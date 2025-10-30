#!/usr/bin/python3
import os, sys, gc, time, argparse
from utils import *
from utils import _listen_to_port as listen_to_port 
from collections import defaultdict
from functools import reduce
import pymemcache, struct
from time import sleep as sleep
import datetime

def memcache_set_bytes_float(client_set, key_bytes, value_float):
    result = client_set.set(key_bytes, struct.pack("<f", value_float))
    if not result:
        raise Exception(f"failed to save key-value {str(key_bytes)} -> {str(value_float)} ")
def memcache_get_bytes_float(client_get, key_bytes):
    ff = client_get.get(key_bytes, b'-999')
    return struct.unpack("<f", ff)[0] if ff else None

Metric_function = {
    "delay" : lambda numbers: reduce(lambda x, y: x + y, numbers),
    "bw" : lambda numbers: reduce(lambda x, y: min(x,y), numbers),
    "ploss" : lambda numbers: reduce(lambda x, y: x * y, numbers)
}
class equation:
    def __init__(self, dag_node_dict):
        self.left = dag_node_dict
        self.rights = dag_node_dict["Parent_dicts"]
        self.left_mkey = self.left["mkey"]
        self.right_mkeys = [x["mkey"] for x in self.rights]
        self.left_tuple = self.left["Tuple"]
        self.right_tuples = [x["Tuple"] for x in self.rights]
        self.cost = len(self.rights) - 1
class xono:
    def __init__(self, name, equations_list, metric, memcache_addr, logfile = None):
        self.name = name
        self.equations = equations_list
        self.metric = metric
        self.memcached_ip = memcache_addr[0]
        self.memcached_port = memcache_addr[1]
        self.logfile = logfile
        self.logger = lambda logstr: log_into(logstr, self.logfile, timestamp=False, print_it=False)
        self.function = Metric_function[self.metric]
        self.client_get = pymemcache.Client(memcache_addr)
        self.client_set = pymemcache.Client(memcache_addr)
        self.Cost = sum([eq.cost for eq in self.equations])
        self.logger(f"Hello: {now_str()}")
    def _go_equation(self, equation:equation):
        right_keys = equation.right_mkeys
        left_key = equation.left_mkey
        right_values = [memcache_get_bytes_float(self.client_get, key) for key in right_keys]
        left_value = self.function(right_values)
        memcache_set_bytes_float(self.client_set, left_key, left_value)  
    def run(self, xono_run_sleep_ms = -1, xono_run_iterations_limit  = -1):
        run_start = time.time()
        sleeper = lambda: sleep(xono_run_sleep_ms / 1000) if xono_run_sleep_ms > 0 else lambda: None
        i = 1
        sum_dur = 0
        self.logger(f"{self.name} run start at {now_str()}")
        while i != xono_run_iterations_limit:
            start_time = time.time()
            for eq in self.equations:
                self._go_equation(eq)
            dur = elapsed_time(start_time)
            sum_dur += dur
            avg_dur = round(sum_dur/i, 2)
            self.logger(f"  iter {i}  \t{self.name} \taverage {avg_dur} sec")
            sleeper()
            i += 1
        run_dur = elapsed_time(run_start)
        self.logger(f"{self.name} run end in {run_dur} seconds")
class xon:
    def __init__(self, dag_file, log_file, metric, n_workers, edges_directory, memcache, 
                 xono_run_sleep_ms = -1, xono_run_iterations_limit  = -1, edge_updater_sleep_ms = -1):
        # Inits:
        self.name = f"XON_{metric}"
        self.dag = load_pkl_json(dag_file)["dag"]
        self.logfile = log_file
        self.metric = metric
        self.n_workers = n_workers
        self.edges_directory = edges_directory
        self.edges_file_to_key = {} # key = edge file, value = edge memcache key
        self.memcache = memcache
        self.xono_run_sleep_ms = xono_run_sleep_ms
        self.xono_run_iterations_limit = xono_run_iterations_limit
        self.edge_updater_sleep_ms = edge_updater_sleep_ms
        self.client_get = pymemcache.Client(self.memcache)
        self.client_set = pymemcache.Client(self.memcache)
        self.nodes = sorted(self.dag.values(), key=lambda x:len(x["Tuple"]))
        # Checks:
        assert len(self.nodes) == len(set([n["Tuple"] for n in self.nodes]))
        self.logdir = os.path.dirname(log_file)
        os.makedirs(self.logdir, exist_ok=True)
        open(self.logfile, "w").close()
        self.client_get.version() # Check memcached server is up:
        self.client_set.version() # Check memcached server is up:
        if not metric in Metric_function:
            raise Exception(f"Error in class xon: Function for {metric} is not defined !")
        # Processes:
        path_counter = edge_counter = mid_counter = 0
        for node in self.nodes:
            # node["mkey"] = bytes(random_hex_32(), "ascii")
            src = node["Tuple"][0]
            dst = node["Tuple"][-1]
            digest = hex(hash(node["Tuple"]))[-8:]
            mkey = "{}_{}_{}_{}".format(self.metric, src, dst, digest)
            node["mkey"] = bytes(mkey, "ascii")
            if node["is_edge"]:
                edge_counter += 1
                Tuple = node["Tuple"]
                edge_file = os.path.join(self.edges_directory, "{}-{}".format(Tuple[0], Tuple[1]))
                if edge_file not in self.edges_file_to_key:
                    self.edges_file_to_key[edge_file] = node["mkey"]
            elif node["is_path"]:
                path_counter += 1
            elif node["is_mid_only"]:
                mid_counter += 1
        for node in self.nodes:
            parent_dicts = []
            for parent in node["Parents"]:
                parent_dicts.append(self.dag[parent])
            node["Parent_dicts"] = parent_dicts
        self.Equations = [equation(node) for node in self.nodes if not node["is_edge"] and not node["is_root"]]
        self.Cost = sum(e.cost for e in self.Equations)
        self.zero_worker = xono("xono_0", self.Equations, self.metric, self.memcache)
        # # define workers ( = xebel online operator = xono)
        self.Workers = []
        cost_threshold = self.Cost / self.n_workers
        sublists = defaultdict(list)
        sublist_idx = 0
        sublist_cost = 0
        for eq in self.Equations:
            if sublist_cost < cost_threshold or sublist_idx == self.n_workers - 1:
                sublists[sublist_idx].append(eq)
                sublist_cost += eq.cost
            else:
                sublist_cost = 0
                sublist_idx += 1
        for i in range(len(sublists)):
            sublist = sublists[i]
            name = f"xono_{self.metric}_{i}"
            logfile = os.path.join(self.logdir, f"{name}.log")
            worker = xono(name, sublist, self.metric, self.memcache, logfile)
            self.Workers.append(worker)
        # Reports:
        self.logger(f"dag file loaded: {dag_file}")
        self.logger(f"    {edge_counter} edges, {mid_counter} midonlys, {path_counter} paths")
        self.logger(f"    total cost: {self.Cost}")
        self.logger(f"    {self.n_workers} workers:")
        for w in self.Workers:
            self.logger(f"      {w.name}: #equations {len(w.equations)}, cost {w.Cost}, log {w.logfile}")
    def edges_value_updater(self):
        sleeper = lambda: sleep(self.edge_updater_sleep_ms / 1000) if self.edge_updater_sleep_ms > 0 else lambda: None
        while(True):
            val = 0.0
            for edge_file in self.edges_file_to_key:
                with open(edge_file, "r") as f:
                    line = f.readline()
                    try:
                        val = float(line.strip())
                    except:
                        self.logger("Error in edges_value_updater) file {} : value \"{}\" cannot converted to float".format(edge_file, line))
                        continue
                    f.close()
                try:
                    memcache_set_bytes_float(self.client_set, self.edges_file_to_key[edge_file], val)
                except Exception as e:
                    self.logger(f"edge updater failed to set edge {edge_file} ")

            # xono_object.logger(f"{xono_object.name}: all edges updated", log_date= True)
            sleeper()
    def watch_server(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        backlog = 10
        s.listen(backlog) 
        while True:
            # print("before accept ")
            c, addr = s.accept()
            try:
                data = c.recv(1024)
                print(f"received data = {data}")
                if not data:
                    continue
                args=data.decode("utf-8").split("|")
                if len(args) < 1:
                    c.send(bytes("Invalid command or parameter: \"{}\"".format(args), 'ascii'))
                    continue
                # Single arg commands
                cmd = args[0].strip()
                if cmd == "stats":
                    rsp = []
                    rsp.append(f"# nodes: {len(self.nodes)}")
                    rsp.append(f"# workers: {len(self.Workers)}")
                    response = "\n".join(rsp)
                    c.send(bytes('{}'.format(response), 'ascii'))
                elif cmd == "keys":
                    rsp = ["{} : {}".format(n["Tuple"], n["mkey"]) for n in self.nodes]
                    response = "\n".join(rsp)
                    c.send(bytes('{}'.format(response), 'ascii'))
                # Double arg commands
                elif cmd in ("get", "verify", "key"):
                    if len(args) < 2:
                        c.send(bytes("Invalid command or parameter: \"{}\"".format(args), 'ascii'))
                        continue
                    parameter = args[1].strip()
                    try:
                        Tup = eval(parameter)
                    except Exception as e:
                        c.send(bytes("Parameter can not be converted into tuple: \"{}\". Error: {}".format(parameter, str(e)), 'ascii'))
                        continue
                    if cmd == "get":
                        # print(" ** * * * * * * ** get {}".format(Tup))
                        mkey = self.dag[Tup]["mkey"]
                        val = memcache_get_bytes_float(self.client_get, mkey)
                        response = "{} : {} = {}".format(Tup, self.metric, val)
                        c.send(bytes('{}'.format(response), 'ascii'))
                    elif cmd == "verify":
                        rsp = []
                        mkey = self.dag[Tup]["mkey"]
                        val0 = memcache_get_bytes_float(self.client_get, mkey)
                        rsp.append("{} : {} = {}".format(Tup, self.metric, val0))
                        vals = []
                        for i in range(len(Tup) - 1):
                            edge_tuple = Tup[i:i+2]
                            edge_node = self.dag[edge_tuple]
                            edge_key = edge_node["mkey"]
                            val = memcache_get_bytes_float(self.client_get, edge_key)
                            vals.append(val)
                            rsp.append(" * {} : {} = {}".format(edge_tuple, self.metric, val))
                        func = Metric_function[self.metric]
                        vals_total= func(vals)
                        err = round(100 * (val0 - vals_total)/vals_total, 5)
                        rsp.append("* total = {}".format(vals_total))
                        rsp.append("* error = %{}".format(err))
                        response = "\n".join(rsp)
                        c.send(bytes('{}'.format(response), 'ascii'))
                    elif cmd == "key":
                        mkey = self.dag[Tup]["mkey"]
                        response = "{} : {}\n".format(Tup, mkey.decode("ascii"))
                        c.send(bytes('{}'.format(response), 'ascii'))
                    
                else:
                        c.send(bytes("Unknown command: \"{}\"".format(cmd), 'ascii'))

            except Exception as e:
                print(e)
                c.send(bytes("Error in xon server: {}\n".format(str(e))))
    def export(self, filename, append = False, export_mid_onlys = False):
        print("Export paths keys:")
        start = time.time()
        if append:
            f = open(filename, "a+t")
        else:
            f = open(filename, "w+t")
        f.write("{}|{}|{}\n".format("#Role", "Tuple", "MKey"))
        counter = 0
        for n in self.nodes:
            write = False
            role = ""
            if n["is_edge"]:
                role = "edge"
                write = True
            elif n["is_mid_only"]:
                if export_mid_onlys:
                    role = "mido"
                    write = True
            elif n["is_path"]:
                role = "path"
                write = True
            else:
                continue
            if write:
                f.write("{}|{}|{}\n".format(role, tuple_to_dashedstr(n["Tuple"]), n["mkey"].decode("ascii")))
                counter += 1
        f.close()
        self.logger(f"Total {counter} nodes saved in {elapsed_time(start)} seconds into {filename}")
    def logger(self, logstr, print_also = True, log_date = False):
        date_str = ""
        if log_date:
            date_str = f"{datetime.datetime.now()} |"
        with open(self.logfile, "a+") as f:
            f.write(f"{date_str} {logstr}\n")
            if print_also:
                print(f"{logstr}")
            f.close()
    # def Run(self, watch_host = "127.0.0.1", watch_port = 11311):
    #     def run_worker(worker: xono):
    #         worker.run(xono_run_sleep_ms = self.xono_run_sleep_ms, 
    #                    xono_run_iterations_limit = self.xono_run_iterations_limit)
    #     processes = []
    #     import multiprocessing
    #     start_time = time.time()
    #     print(f" Xon Run start {now_str()}")
    #     print("  Starting edge updater thread: ", end="")
    #     p = multiprocessing.Process(target=self.edges_value_updater, args=())
    #     processes.append(p)
    #     p.start()
    #     print("  Starting watch server thread: ", end="")
    #     p = multiprocessing.Process(target=self.watch_server, args=(watch_host, watch_port))
    #     processes.append(p)
    #     p.start()
    #     print(" done")
    #     print("  Starting DAG updater threads: ", end="")
    #     for worker in self.Workers:
    #         p = multiprocessing.Process(target=run_worker, args=(worker,))
    #         processes.append(p)
    #         p.start()
    #     print(" done")
    #     for p in processes:
    #         p.join()
def xebel_online(CONF = None):
    metrics = [s.strip() for s in  CONF['metrics'].split(",")]
    watch_ports = [int(s.strip()) for s in  CONF['watch_ports'].split(",")]
    edges_directory = CONF['edges_directory']
    memcached_ip = CONF['memcached_ip'] or "localhost"
    memcached_port = int(CONF['memcached_port']) or 11211
    n_workers = int(CONF['workers'])
    dag_file = CONF['dag_file']
    log_file = CONF['log_file']
    nodes_cache_keys_file = CONF['nodes_cache_keys_file']
    memcached_addr = (memcached_ip, memcached_port)
    xono_run_sleep_ms = int(CONF['xono_run_sleep_ms']) if 'xono_run_sleep_ms' in CONF else -1
    xono_run_iterations_limit  = int(CONF['xono_run_iterations_limit '])  if 'xono_run_iterations_limit ' in CONF else -1
    edge_updater_sleep_ms = int(CONF['edge_updater_sleep_ms']) if 'edge_updater_sleep_ms' in CONF else -1
    export_mid_onlys = True if CONF['export_mid_onlys'].lower in {"true", "yes", "y"} else False
    Xons = []
    for i in range(len(metrics)):
        metric = metrics[i]
        Xon = xon(
                    dag_file=dag_file, 
                    log_file = log_file, 
                    metric=metric, 
                    n_workers = n_workers,
                    edges_directory=edges_directory, 
                    memcache = memcached_addr ,
                    xono_run_sleep_ms = xono_run_sleep_ms,
                    xono_run_iterations_limit = xono_run_iterations_limit,
                    edge_updater_sleep_ms = edge_updater_sleep_ms
                )
        Xons.append(Xon)
        Xon.export(nodes_cache_keys_file, append=i > 0, export_mid_onlys = export_mid_onlys)
    def run_worker(context: xon, worker: xono):
        print(f"    * Starting {context.name} worker {worker.name} ")
        worker.run(xono_run_sleep_ms = context.xono_run_sleep_ms, 
                    xono_run_iterations_limit = context.xono_run_iterations_limit)
    import multiprocessing
    processes = []
    for i in range(len(Xons)):
        X = Xons[i]
        watch_port = watch_ports[i]
        start_time = time.time()
        print(f"+ {X.name} start {now_str()}")
        print(f"    {X.name}: Starting edge updater thread: ")
        p = multiprocessing.Process(target=X.edges_value_updater, args=())
        processes.append(p)
        p.start()
        print(f"    {X.name}: Starting watch server on port {watch_port}: ")
        p = multiprocessing.Process(target=X.watch_server, args=("127.0.0.1", watch_port))
        processes.append(p)
        p.start()
        print(f"    {X.name}: Starting DAG updater threads: ")
        for worker in X.Workers:
            p = multiprocessing.Process(target=run_worker, args=(X, worker,))
            processes.append(p)
            p.start()
    for p in processes:
        p.join()
if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    # Define command-line switches:
    parser = argparse.ArgumentParser()
    # Define the --config-file switch
    parser.add_argument("--config-file", help="specify the configuration file")
    parser.add_argument("--stage", help="specify the stage of online phase (default is 0 to run all stages in order)")
    parser.add_argument("args", nargs="*", help="any arguments without switches")
    args = parser.parse_args()
    current_dir = os.getcwd()
    print(f"Here: {current_dir}")
    CONFIG_FILE = args.config_file
    if not CONFIG_FILE:
        if os.path.exists(current_dir + "/xebel.conf"):
            CONFIG_FILE = os.path.join(current_dir, "xebel.conf")
        elif os.path.exists("/root/configs/xebel.conf"):
            CONFIG_FILE = "/root/configs/xebel.conf"
        else:
            print("No config file (xebel.conf) found!")
    print(f"Using config file: {CONFIG_FILE}")
    STAGE = args.stage or "0"
    CONF = load_configs(CONFIG_FILE)['online']
    xebel_online(CONF)