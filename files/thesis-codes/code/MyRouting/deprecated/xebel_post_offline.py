#!/usr/bin/python3
import os, sys, time, argparse
from utils import *

# class equation:
#     def __init__(self, dag_node_dict):
#         self.left = dag_node_dict
#         self.rights = dag_node_dict["Parent_dicts"]
#         self.left_key = self.left["key"]
#         self.right_keys = [x["key"] for x in self.rights]
#         self.left_tuple = self.left["Tuple"]
#         self.right_tuples = [x["Tuple"] for x in self.rights]
#         self.cost = len(self.rights) - 1

# class xon_prepare:
#     def __init__(self, dag_file, log_file, metrics, edges_directory, n_workers):
#         # Inits:
#         self.dag = load_pkl_json(dag_file)["dag"]
#         self.logfile = log_file
#         self.metrics = metrics
#         self.edges_directory = edges_directory
#         self.n_workers = n_workers
#         self.edges_file_to_key = {} # key = edge file, value = edge memcache key
#         self.nodes = sorted(self.dag.values(), key=lambda x:len(x["Tuple"]))
#         # Checks:
#         assert len(self.nodes) == len(set([n["Tuple"] for n in self.nodes]))
#         self.logdir = os.path.dirname(log_file)
#         os.makedirs(self.logdir, exist_ok=True)
#         open(self.logfile, "w").close()
#         for metric in metrics:
#             oper = metric["operator"]
#             if not oper in Operators:
#                 raise Exception(f"Error in class xon: Function for {oper} is not defined !")
#         # Processes:
#         path_counter = edge_counter = mid_counter = 0
#         for node in self.nodes:
#             # node["mkey"] = bytes(random_hex_32(), "ascii")
#             src = node["Tuple"][0]
#             dst = node["Tuple"][-1]
#             node["digest"] = hex(hash(node["Tuple"]))[-8:]
#             node["key"] = "{}_{}_{}".format(src, dst, node["digest"])
#             # node["mkey1"] = "{}_{}_{}_{}".format(self.metrics[0]["name"], src, dst, node["digest"])
#             # node["mkey2"] = "{}_{}_{}_{}".format(self.metrics[2]["name"], src, dst, node["digest"])
#             if node["is_edge"]:
#                 edge_counter += 1
#                 Tuple = node["Tuple"]
#                 edge_file = os.path.join(self.edges_directory, "{}-{}".format(Tuple[0], Tuple[1]))
#                 if edge_file not in self.edges_file_to_key:
#                     self.edges_file_to_key[edge_file] = node["digest"]
#             elif node["is_path"]:
#                 path_counter += 1
#             elif node["is_mid_only"]:
#                 mid_counter += 1
#         for node in self.nodes:
#             parent_dicts = []
#             for parent in node["Parents"]:
#                 parent_dicts.append(self.dag[parent])
#             node["Parent_dicts"] = parent_dicts
#         self.Equations = [equation(node) for node in self.nodes if not node["is_edge"] and not node["is_root"]]
#         self.Cost = sum(e.cost for e in self.Equations)
#         self.Workers = []
#         cost_threshold = self.Cost / self.n_workers
#         self.sublists = defaultdict(list)
#         sublist_idx = 0
#         sublist_cost = 0
#         for eq in self.Equations:
#             if sublist_cost < cost_threshold or sublist_idx == self.n_workers - 1:
#                 self.sublists[sublist_idx].append(eq)
#                 sublist_cost += eq.cost
#             else:
#                 sublist_cost = 0
#                 sublist_idx += 1
#         # for i in range(len(self.sublists)):
#         #     sublist = self.sublists[i]
#         #     # logfile = os.path.join(self.logdir, f"{name}.log")

#         # Reports:
#         self.logger(f"dag file loaded: {dag_file}")
#         self.logger(f"    {edge_counter} edges, {mid_counter} midonlys, {path_counter} paths")
#         self.logger(f"    total cost: {self.Cost}")
#         self.logger(f"    {self.n_workers} workers:")
#     def export_ways(self, ways_file):
#         def is_edge(n):
#             if n["is_edge"]:
#                 return 1
#             return 0
#         def is_path(n):
#             if n["is_path"]:
#                 return 1
#             return 0
#         def is_mid(n):
#             if n["is_mid"]:
#                 return 1
#             return 0
#         def is_mid_only(n):
#             if n["is_mid_only"]:
#                 return 1
#             return 0
#         start = time.time()
#         f = open(ways_file, "w+t")
#         # key|tuple-dashed|edge?|path?|mid?|midonly?
#         # key = <src>_<dst>_<digest>
#         f.write("#key|tuple-dashed|edge?|path?|mid?|midonly?")
#         counter = 0
#         for n in self.nodes:
#             f.write("{}|{}|{}|{}|{}|{}\n".format(n["key"], tuple_to_dashedstr(n["Tuple"]), 
#                                                  is_edge(n), is_path(n), is_mid(n), is_mid_only(n)))
#             counter += 1
#             # write = False
#             # role = ""
#             # if n["is_edge"]:
#             #     role = "edge"
#             #     write = True
#             # elif n["is_mid_only"]:
#             #     if export_mid_onlys:
#             #         role = "mido"
#             #         write = True
#             # elif n["is_path"]:
#             #     role = "path"
#             #     write = True
#             # else:
#             #     continue
#             # if write:
#             #     f.write("{}|{}|{}\n".format(role, tuple_to_dashedstr(n["Tuple"]), n["mkey"].decode("ascii")))
#             #     counter += 1
#         f.close()
#         self.logger(f"Total {counter} nodes saved in {elapsed_time(start)} seconds into {ways_file}")
#     def export_equations(self, equations_file):
#         start = time.time()
#         f = open(equations_file, "w+t")
#         # id|worker|cost|left_key|right_key_1#right_key_2#...
#         f.write("#id|worker|cost|left_key|right_key_1#right_key_2#...")
#         counter = 0
#         for w in range(len(self.sublists)):
#             sublist = self.sublists[w]
#             for eq in sublist:
#                 # rkeys = "#".join([r["key"] for r in eq.rights])
#                 rkeys = "#".join(eq.right_keys)
#                 f.write("{}|{}|{}|{}|{}\n".format(counter, w, eq.cost, eq.left["key"], rkeys)) 
#                 counter += 1
#         self.logger(f"Total {counter} equations for {len(self.sublists)} workers saved in {elapsed_time(start)} seconds into {equations_file}")

#     def logger(self, logstr, print_also = True, log_date = False):
#         date_str = ""
#         if log_date:
#             date_str = f"{datetime.datetime.now()} |"
#         with open(self.logfile, "a+") as f:
#             f.write(f"{date_str} {logstr}\n")
#             if print_also:
#                 print(f"{logstr}")
#             f.close()

# def prepare_for_online_phases(CONF = None):
#     offline_conf = CONF['offline']
#     online_conf = CONF['online']
#     # dag_file = offline_conf['stage2_dagfile_pkl']
#     dag_file = online_conf['dag_file']
#     log_file = online_conf['log_file']
#     edges_directory = online_conf['edges_directory']

#     metric1 = online_conf['metric1']
#     metric1_optimum = online_conf['metric1_optimum']
#     metric1_operator = online_conf['metric1_operator']
#     metric2 = online_conf['metric2']
#     metric2_optimum = online_conf['metric2_optimum']
#     metric2_operator = online_conf['metric2_operator']
#     n_workers = int(online_conf['workers'])
#     ways_file = online_conf['ways_file']
#     equations_file = online_conf['equations_file']
#     metrics = [
#         {
#             "name" : metric1,
#             "operator" : metric1_operator,
#             "optimum" : metric1_optimum
#         },
#         {
#             "name" : metric2,
#             "operator" : metric2_operator,
#             "optimum" : metric2_optimum
#         }
#     ]
#     X = xon_prepare(dag_file=dag_file, log_file=log_file, metrics=metrics, edges_directory=edges_directory, n_workers = n_workers)
#     X.export_ways(ways_file)
#     X.export_equations(equations_file)

def offline_post_process(dag):
    cost_0 = sum([len(n["Tuple"]) for n in dag.values() if n["is_path"]])
    for n in dag.values():
        n["cost"] = len(n["Parents"]) - 1
    nodes = sorted(dag.values(), key=lambda x:x["cost"])
    cost_1 = sum([n["cost"] for n in dag.values() if not n["is_root"]])
    cost_reduction = 0
    cost_remain = 0
    n_ok = 0
    n_nok = 0
    for n in nodes:
        if n["cost"] == 1:
            continue
        ok = False
        for i in range(2, len(n["Tuple"])):
            T1 = n["Tuple"][:i]
            T2 = n["Tuple"][i-1:]
            if T1 in dag and T2 in dag:
                cost_reduction += n["cost"] - 1
                n_ok += 1
                n["Parents"] = [T1, T2]
                # print("Way {} - OldParents {} - NewParents {}".format(
                #     n["Tuple"], tuples_list_to_str(n["Parents"]), tuples_list_to_str([T1, T2])
                # ))
                n["cost"] = 1
                ok = True
        if not ok:
            cost_remain += n["cost"] - 1
            n_nok += 1
    cost_2 = cost_1 - cost_reduction
    print(f" cost reduction {cost_reduction} by #ways {n_ok}")
    print(f" cost remained {cost_remain} by #ways {n_nok}")
    cost_min = len([n for n in nodes if n["is_path"]])
    print(f"cost_base = {cost_0}, before = {cost_1} ({float(cost_0 - cost_1) / cost_0}%), after = {cost_2} ({float(cost_0 - cost_2) / cost_0}%)")
    print(f"theoric_min_cost (#of paths) = {cost_min}, UTILITY (min_cost / cost) = {100 * (cost_min / cost_2)}%")


    

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
    CONF = load_configs(CONFIG_FILE)
    dag = load_pkl_json(CONF['offline']['stage2_dagfile_pkl'])["dag"]
    offline_post_process(dag)