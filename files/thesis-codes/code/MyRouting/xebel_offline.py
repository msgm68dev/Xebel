#!/usr/bin/python3
# import sys
import os, sys, gc, time, argparse
from multiprocessing import Pool
from utils import *
from Topology import Topology
from allpaths_w_xebel import Graph
from dag_xebel import dag, dagnode
from dag_xebel import nodes as NODES
from xebel_onre_prepare import prepare_for_onre

def pathlist_calc_statistics(pathlist_to_export:list, graph:Graph):
    class linkak:
        def __init__(self, link_tuple, weight = 1) -> None:
            self.id = link_tuple
            self.weight = weight
            self.usage = 0
        def cross(self, pseudo_flow_size:float):
            self.usage += pseudo_flow_size
    Links = {}
    def get_new_linkak(l_tuple):
        if l_tuple not in  Links:
            l = linkak(l_tuple)
            Links[l_tuple] = l
            return l
        else:
            return Links[l_tuple]
    class pathak:
        def __init__(self, path_tuple) -> None:
            self.src = path_tuple[0]
            self.dst = path_tuple[-1]
            self.Tuple = path_tuple
            self.links = []
            for i in range(len(path_tuple) - 1):
                link_id = (path_tuple[i], path_tuple[i+1])
                # get_new_linkak(link_id)
                self.links.append(get_new_linkak(link_id))
        def cross(self, pseudo_flow_size:float):
            for l in self.links:
                l.cross(pseudo_flow_size)
        def usage(self):
            return sum([l.usage for l in self.links])
    Paths_all = {}
    V = graph.V
    i2j_n_paths = [ [ 0 for j in range(V)] for i in range(V) ]
    i2j_cross_size = [ [ 0 for j in range(V)] for i in range(V) ]
    for i in range(V):
        for j in range(V):
            i_to_j_paths = pathlist_to_export[i][j].Paths
            i2j_n_paths[i][j] = len(i_to_j_paths)
            for path_tuple in i_to_j_paths:
                path_tuple = tuple(path_tuple)
                Paths_all[path_tuple] = pathak(path_tuple)
    max_i2j_n_path = max(max(i2j_n_paths))
    for i in range(V):
        for j in range(V):
            i2j_cross_size[i][j] = max_i2j_n_path / i2j_n_paths[i][j]
    for ptk in Paths_all.values():
        ptk.cross(i2j_cross_size[ptk.src][ptk.dst])

    from statistics import stdev as std, mean as avg
    crosses = [l.usage for l in Links.values()]
    avg_i2j_n_path = 0
    for i2_n_path in i2j_n_paths:
        for i2j_n_path in i2_n_path:
            avg_i2j_n_path += i2j_n_path
    avg_i2j_n_path /= (V*V)

    std_link_usage_norm = std(normalize(crosses))
    std_link_usage = std(crosses)
    avg_link_usage = avg(crosses)
    # input(f"LB = {LB}")
    return {
        "std_lnk_usag_norm" : std_link_usage_norm,
        "std_lnk_usag" : std_link_usage,
        "avg_lnk_usag" : avg_link_usage,
        "n_paths" : len(Paths_all), 
        "avg_i2j_n_path" : avg_i2j_n_path,
    }

def xoff1_worker (param:dict):
    PICKLE_PARTS_DIR = param['PICKLE_PARTS_DIR']
    g = param['graph']
    sources = param['sources']
    dests = param['dests']
    stage1_logfile = param['stage1_logfile']
    logger = lambda log_str : log_into(log_str, stage1_logfile, timestamp = False, print_it = True)
    topo = g.topology
    dataset_name = g.topology_name
    acep = param['acep']
    aps = param['aps']
    worker_id = param['worker_id']
    save_at = param['save_at']
    filename = f"worker_{worker_id}.pkl"
    w_start_time = time.time()
    pathlist = g.get_paths_from_to(acep, aps,  dir_to_save = PICKLE_PARTS_DIR, 
                                    save_at = save_at, sources = sources, dests = dests, 
                                    dont_load = False, filename = filename)
    logger(f"\tworker_{worker_id}_time: {elapsed_time(w_start_time)}")
    logger(f"\tworker_{worker_id}_sources: {sources}")
    logger(f"\tworker_{worker_id}_gc: {gc.collect()}")
    return pathlist
def Xoff_1(Offline_CONF = None):
    stage1_start_time = time.time()
    acep = float(Offline_CONF['acep'])
    aps = float(Offline_CONF['aps'])
    first_node_id = int(Offline_CONF['first_node_id'])
    links_file = Offline_CONF['links_file']
    dataset_name = Offline_CONF['dataset_name']
    stage1_logfile = Offline_CONF['stage1_logfile']
    stage1_pathlist_pkl = Offline_CONF['stage1_pathlist_pkl']
    offline_data_dir = Offline_CONF['offline_data_dir']
    stage1_dir = Offline_CONF['stage1_dir']
    stage_1_workers = int(Offline_CONF['stage_1_workers'])
    stage_1_saveat = int(Offline_CONF['stage_1_saveat'])
    stage1_print_result = False if "y" not in Offline_CONF['stage1_print_result'].lower() else True
    # DATADIR = offline_data_dir + "/" + dataset_name
    params = f"{acep}-{aps}"
    stage1_dir_param = os.path.join(stage1_dir, params)
    create_file_with_path(stage1_logfile, clear_it=False)
    logger = lambda log_str, ts = False : log_into(log_str, stage1_logfile, timestamp = ts, print_it = True)
    logger(f"xoff-1: ", True)
    topo = Topology(topology_file=links_file, name = dataset_name, first_node_id=first_node_id)
    g = Graph(topo, topology_name=dataset_name, prints=stage1_print_result)
    topo = g.topology
    Paths_pickle_cache = os.path.join(stage1_dir_param, "paths_cache")
    # os.makedirs(DATADIR, exist_ok=True)
    os.makedirs(Paths_pickle_cache, exist_ok=True)
    all_nodes = list(range(topo.V))
    sources_lists = partition_list(all_nodes, stage_1_workers)
    pool_param_dicts = []
    g.prints = False
    for i in range(stage_1_workers):
        pool_param_dict = {
            'PICKLE_PARTS_DIR' : Paths_pickle_cache,
            'graph' : g,
            'sources' : sources_lists[i],
            'dests' : all_nodes,
            'acep' : acep,
            'aps' : aps,
            'worker_id' : i,
            'save_at': stage_1_saveat, 
            'stage1_logfile' : stage1_logfile
        }
        pool_param_dicts.append(pool_param_dict)
    pool_start_time = time.time()
    pool = Pool(processes=stage_1_workers)
    results = pool.map(xoff1_worker, pool_param_dicts)
    logger(f"\tpaths_fetch_time: {elapsed_time(pool_start_time)}")
    if stage1_print_result:
        for result in results:
            for from_source_list in result:
                for to_dest_ijpaths in from_source_list:
                    to_dest_ijpaths.print_stats(acep, aps)
    results_merged = []
    for result in results:
        for from_source_list in result:
            results_merged.append(from_source_list)
    export_addr = os.path.join(stage1_dir_param, stage1_pathlist_pkl)
    pathlist_export(results_merged, export_addr, e = False, as_json = False)
    g.killme()
    plstats = pathlist_calc_statistics(results_merged, g)
    plstats_str = dict_to_1line_str(plstats)
    
    logger(f"\tparams: {params}, {plstats_str}")
    logger(f"\ttotal_time: {elapsed_time(stage1_start_time)}")
    logger(f"\tparams: {params}")

def Xoff_2(Offline_CONF = None):
    dataset_name = Offline_CONF['dataset_name']
    first_node_id = int(Offline_CONF['first_node_id'])
    acep = float(Offline_CONF['acep'])
    aps = float(Offline_CONF['aps'])
    stage1_dir = Offline_CONF['stage1_dir']
    stage1_pathlist_pkl_name = Offline_CONF['stage1_pathlist_pkl']
    stage2_logfile = Offline_CONF['stage2_logfile']
    stage2_dir = Offline_CONF['stage2_dir']
    make_method = Offline_CONF['make_method']
    # stage2_dagfile_pkl = CONF['stage2_dagfile_pkl']
    # stage2_dagfile_text = CONF['stage2_dagfile_text']
    # stage2_save_dag_as_txt = True if "y" in CONF['stage2_save_dag_as_txt'].lower() else False
    params = f"{acep}-{aps}"
    stage1_dir_param = os.path.join(stage1_dir, params)
    Pathlist_file = os.path.join(stage1_dir_param, stage1_pathlist_pkl_name)
    d = dag(pathlist_file_to_import = Pathlist_file, logfile=stage2_logfile, make_method=make_method)
    dag_dict = d.make()
    verified = dag_dict["verified"]
    make_duration = dag_dict["make_duration"]
    make_method = dag_dict["make_method"]
    base_dag_cost = dag_dict["base_dag_cost"]
    dag_cost = dag_dict["dag_cost"]
    improvement_percentage = dag_dict["improvement_percentage"]
    operations_per_path = dag_dict["operations_per_path"]
    number_of_paths = dag_dict["number_of_paths"]
    number_of_leaf_paths = dag_dict["number_of_leaf_paths"] = number_of_paths
    number_of_path_midways = number_of_paths - number_of_leaf_paths
    number_of_nonpath_midways = dag_dict["number_of_nonpath_dagnodes"]
    dag_dict["acep"] = acep
    dag_dict["aps"] = aps
    dag_dict["dataset_name"] = dataset_name
    if first_node_id == 1:
        # In dag class, first_node is always 0
        # so here we convert it to node_id from 1 if necessary:
        def plus_one(x):
            if x == "ROOT":
                return x
            return tuple([y+1 for y in x])
        nodes_dict = dag_dict["dag"]
        new_dict = {}
        for Tuple in nodes_dict.keys():
            node = nodes_dict[Tuple]
            parents = node["Parents"]
            childs = node["Childs"]
            new_parents = [plus_one(p) for p in parents]
            new_childs = [plus_one(ch) for ch in childs]
            new_Tuple = plus_one(Tuple)
            node["Tuple"] = new_Tuple
            node["Parents"] = new_parents
            node["Childs"] = new_childs
            new_dict[new_Tuple] = node
        dag_dict["dag"] = new_dict
    elif first_node_id != 0:
        raise Exception(f"first_node_id must be 0 or 1 ...")
    # d.logger(f"\tcost_reduction: from {base_dag_cost} to {dag_cost} improved {improvement_percentage}%") 
    # d.logger(f"\tbase_cost: {base_dag_cost}") 
    # d.logger(f"\tdag_cost: {dag_cost}") 
    # d.logger(f"\timprove%: {improvement_percentage}") 
    # d.logger(f"\tavg_ops/path: {operations_per_path}") 
    # d.logger(f"\t#mid/paths: {number_of_path_midways}/{number_of_paths}, #midonlys: {number_of_nonpath_midways}") 
    logstr = now_str() + ", "   
    logstr += f"params:{params}, "   
    logstr += f"make_method:{make_method}, "   
    logstr += f"make_time:{make_duration}, "   
    logstr += f"base_dag_cost:{base_dag_cost}, "   
    logstr += f"dag_cost:{dag_cost}, "   
    logstr += f"improvement_percentage:{improvement_percentage}, "   
    logstr += f"avg_ops/path:{operations_per_path}, "   
    logstr += f"mid_paths:{number_of_path_midways}, "   
    logstr += f"paths:{number_of_paths}, "   
    logstr += f"midonlys:{number_of_nonpath_midways}, "   
    logstr += f"dag_verified:{verified}, "   

    print("Saving ", end="")
    start_time = time.time()
    dag_pkl_name = "dag.pkl"
    Dagfile_pkl = os.path.abspath(os.path.join(stage2_dir, params, dag_pkl_name))
    d.save(Dagfile_pkl)
    # if stage2_save_dag_as_txt:
    #     stage2_dagfile_text = os.path.abspath(stage2_dagfile_text)
    #     dag_nodes = dag_dict["dag"]
    #     other_info = {}
    #     for key in dag_dict:
    #         if key != "dag":
    #             other_info[key] = dag_dict[key]
    #     with open(stage2_dagfile_text, "w+") as f:
    #         f.write("DAG Manifest:\n")
    #         for key in other_info.keys():
    #             f.write("  {}: {}\n".format(key, other_info[key]))
    #         f.write("DAG Nodes:\n")
    #         spaces = " " * (3 + len(str(len(dag_nodes))))
    #         def write_1_node_in_file(idx, key, dict_record:dict):
    #             f.write("{} Tuple: {}\n{}Parents: {}\n{}Childs: {}\n{}path:{}, edge?{}, mid?{}, midonly?{}\n".format(
    #                 idx, key, 
    #                 spaces, tuples_list_to_str(dict_record["Parents"]), 
    #                 spaces, tuples_list_to_str(dict_record["Childs"]), 
    #                 spaces, 
    #                     "yes" if dict_record["is_path"] else "no", 
    #                     "yes" if dict_record["is_edge"] else "no", 
    #                     "yes" if dict_record["is_mid"] else "no", 
    #                     "yes" if dict_record["is_mid_only"] else "no"
    #             ))
    #         i = 1
    #         for key in dag_nodes.keys():
    #             write_1_node_in_file(i, key, dag_nodes[key])
    #             i += 1
    #         f.close()

    print("done")
    logstr += f"save_dag_time:{elapsed_time(start_time)}, "   
    logstr += f"Dag_file:{os.path.abspath(Dagfile_pkl)}, "   
    # if stage2_save_dag_as_txt:
    #     d.logger(f"Dag text: {stage2_dagfile_text}")
    
    d.logger(logstr)
    print("see:\n {}".format(os.path.abspath(d.logfile)))

def Xoff_3(CONF = None):
    prepare_for_onre(CONF)

def Batch_Xoff(CONF = None):
    raise Exception("Sorry. DONT USE BATCH MODE: this way results in OUT OF MEMORY problem \nuse xebel-offline-batch instead")
    Offline_conf = CONF['offline']
    batch_acep = Offline_conf['batch_acep']
    batch_aps = Offline_conf['batch_aps']
    batch_logfile = Offline_conf['batch_logfile']
    logger = lambda log_str, ts = False : log_into(log_str, batch_logfile, timestamp = ts, print_it = True)
    aceps = comma_separated_str_to_str_tuple(batch_acep)
    apss = comma_separated_str_to_str_tuple(batch_aps)
    n_modes = len(aceps) * len(apss)
    create_file_with_path(batch_logfile, clear_it=False)
    logger(f"xoff-batch: ", True)
    logger(f" n_acep: {len(aceps)}")
    logger(f" n_aps: {len(apss)}")
    logger(f" n_modes: {n_modes}")
    m = 0
    for acep in aceps:
        for aps in apss:
            m += 1
            logger(" ################################################################")
            logger(f" mode: {m}")
            params = f"{acep}-{aps}"
            logger(f"\tparams: {params}")
            main_conf = CONF
            main_conf['offline'].update({"acep" : acep, "aps" : aps})
            off_conf = main_conf['offline']
            # logger(f"\toff_conf: {off_conf}")
            # input()
            Xoff_1(off_conf)
            # time.sleep(3)
            print(f"XEBEL BATCH MODE {m} STAGE 1 DONE : {gc.collect()} garbages collected")

            

def main():
    argc = len(sys.argv)
    argv = sys.argv
    # Define command-line switches:
    parser = argparse.ArgumentParser()
    # Define the --config-file switch
    parser.add_argument("--config-file", help="specify the configuration file")
    parser.add_argument("--stage", help="specify the stage of offline phase (default is 0 to run all stages in order)")
    parser.add_argument("--acep", type=float, help="specify ACEP parameter to be used (instead of the value in config file)")
    parser.add_argument("--aps", type=float, help="specify APS parameter to be used (instead of the value in config file)")
    parser.add_argument("--maker", type=str, help="specify DAG maker method to be used (instead of the value in config file)")
    parser.add_argument("batch", nargs="?", help="run batch mode (generate outputs for several aceps and aps)")
    # parser.add_argument("args", nargs="*", help="any arguments without switches")
    args = parser.parse_args()
    Stage = args.stage or "0"
    Batch = args.batch or False
    Acep = args.acep or -1
    Aps = args.aps or -1
    Maker = args.maker or ""
    current_dir = os.getcwd()
    print(f"Here: {current_dir}")
    Config_file = args.config_file
    if not Config_file:
        if os.path.exists(current_dir + "/xebel.conf"):
            Config_file = os.path.join(current_dir, "xebel.conf")
        elif os.path.exists("/root/configs/xebel.conf"):
            Config_file = "/root/configs/xebel.conf"
        else:
            print("No config file (xebel.conf) found!")
    print(f"Using config file: {Config_file}")
    CONF = load_configs(Config_file)
    if Acep > 0:
        CONF['offline'].update({"acep" : Acep})
    if Aps > 0:
        CONF['offline'].update({"aps" : Aps})
    if Maker != "":
        CONF['offline'].update({"make_method" : Maker})
    # set_memory_limit_GB(allowed_memory_gb)
    if Batch:
        if Stage !=  "0":
            raise Exception(f"You can not enter stage in batch mode")
        if Batch != "batch":
            raise Exception(f"Unknown argument {Batch}")
        Batch_Xoff(CONF)
        return
    if Stage == "0":
        Xoff_1(CONF['offline'])
        Xoff_2(CONF['offline'])
        Xoff_3(CONF)
    elif Stage == "1":
        Xoff_1(CONF['offline'])
    elif Stage == "2":
        Xoff_2(CONF['offline'])
    elif Stage == "3":
        Xoff_3(CONF)
    else:
        print(f"invalid inputs: {argv[1:]}")

if __name__ == "__main__":
    main()