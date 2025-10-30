import os
from collections import defaultdict 
import random
try: #for save/load dictionary to/from file
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle
import json

def get_env_var(VAR_STR):
    str = ""
    try:
        str = os.environ[VAR_STR] 
    except Exception as e:
        print("Error: {}\nThere is no envisonment variable ${}".format(str(e), VAR_STR))
        exit(1)
    return str
def check_file_exist(filename):
    exist = os.path.isfile(filename)
    if not exist:
        print(" *** FILE NOT FOUND: {}\n".format(filename))
        exit(1)

thesis_dir  = get_env_var('THESIS')
topology_dir = os.path.join(thesis_dir, "data/topology/")
DATASET = get_env_var('DATASET')
TOPOLOGY = os.path.join(topology_dir, DATASET)
check_file_exist(TOPOLOGY)

def file_to_table(filename, separator = ','):
    output = []
    f = open(filename, 'r')
    lines = f.readlines()
    i = 0
    for line in lines:
        s = line.strip()
        if not s or s == [''] or s[0] == '#':
            continue
        i += 1
        words = line.split(separator)
        record = [x.strip() for x in words]
        output.append(record)
    return output

def id_list_to_switch_list(sid_list, switches_dict):
    return [switches_dict[sid] for sid in sid_list]

def change_pcnt(name, value1, value2):
    msg = "{}: {} -> {} ({}%)".format(name, \
                value1, value2,  \
                    str(-1 * round(100.0 * (value1-value2)/value1 , 1)))
    return msg

# You can set filename as fullpath and directory as None or set them separately.
def _save_obj(obj_to_save, output_file, as_json = False):
    _directory = os.path.dirname(output_file)
    # _filename = "".join(os.path.basename(output_file).split(".")[:-1])
    _filename = os.path.basename(output_file)
    ext = os.path.basename(output_file).split(".")[-1]
    if ext == "json" or ext == "pkl":
        _filename = _filename[:-len(ext)-1]
    ext = "json" if as_json else "pkl"
    if not os.path.exists(_directory):
        os.makedirs(_directory)
    pkl_file = os.path.join(_directory, _filename + "." + ext)
    with open(pkl_file, 'wb') as fp:
        if as_json:
            json.dump(obj_to_save, fp)
        else:
            pickle.dump(obj_to_save, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("{} SAVED: {}".format(ext, pkl_file))
def _load_obj(filename):
    _directory = os.path.dirname(filename)
    _filename = os.path.basename(filename)
    ext = ""
    tmp = _filename.split(".")
    if len(tmp) > 1:
        ext = tmp[-1]
    as_json = ext.lower() == "json"
    file_to_load = os.path.join(filename)
    if not os.path.exists(file_to_load):
        print("Load FAILED: Not exist: " + file_to_load)
        return
    output = None
    try:
        with open(file_to_load, 'rb') as fp:
            if as_json:
                output = json.load(fp)
            else:
                output = pickle.load(fp)
        print("Load {} SUCCESS: {}".format(ext, file_to_load))
    except Exception as e:
        print("Load {} FAILED: Unknown error: {}".format(ext, str(e)))
    return output
def save_as_pkl(obj_to_save, output_file):
    _save_obj(obj_to_save, output_file)
def save_as_json(obj_to_save, output_file):
    try:
        _save_obj(obj_to_save, output_file, True)
    except:
        print("save_as_json FAILED !!! \nobj type: {}\nfile: {}\n     try save_as_pkl".format(type(obj_to_save), output_file))
def load_pkl_json(filename):
    loaded_dict = _load_obj(filename)
    return loaded_dict

def dataset_pkl_dir(dataset = TOPOLOGY):
    dataset
    dsdir = os.path.dirname(dataset)
    return os.path.join(dsdir, "pickles")
def dataset_dag_dir(dataset = TOPOLOGY):
    dataset
    dsdir = os.path.dirname(dataset)
    return os.path.join(dataset_pkl_dir(), "dag")
def dataset_dir(dataset):
    return os.path.dirname(dataset)
def addr_as_json(filename):
    fname = filename
    ss = filename.split(".")
    if ss[-1] != "json":
        fname = ".".join(ss) + ".json"
    return os.path.join(dataset_pkl_dir(), fname)
def addr_as_pkl(filename):
    fname = filename
    ss = filename.split(".")
    if ss[-1] != "pkl":
        fname = ".".join(ss) + ".pkl"
    return os.path.join(dataset_pkl_dir(), fname)
def addr_as_dag_pkl(filename):
    fname = filename
    ss = filename.split(".")
    if ss[-1] != "pkl":
        fname = ".".join(ss) + ".pkl"
    return os.path.join(dataset_dag_dir(), fname)
def addr_as_dag_json(filename):
    fname = filename
    ss = filename.split(".")
    if ss[-1] != "json":
        fname = ".".join(ss) + ".json"
    return os.path.join(dataset_dag_dir(), fname)

def union_lists(base, second = []):
    for elem in second:
        if not elem in base:
            base.append(elem)
def flatten_pathlist(pathlist, e = False):
    if e:
        list_of_paths = [path for p in pathlist for q in p for path in q.EPaths]
    else:
        list_of_paths = [path for p in pathlist for q in p for path in q.Paths]
    return list_of_paths
def order_dict_as_tuple(dictionary, reverse = False):
    return sorted(dictionary.items(), key=lambda kv: kv[1], reverse=reverse)
def order_dict_as_dict(dictionary, reverse = False):
    t = order_dict_as_tuple(dictionary, reverse=reverse)
    from collections import OrderedDict
    return OrderedDict(t)

def sum_pathlet_dicts(base_pl, second_pl):
    for key in second_pl:
        if key in base_pl:
            base_pl[key] += second_pl[key]
        else:
            base_pl[key] = second_pl[key]
def get_pathlets0(path):
    pathlets = {}
    maxl = len(path)
    for L in range(1, maxl+1):
        for i in range(maxl-L+1):
            sub = tuple(path[i:i+L])
            pathlets[sub] = 1
    return pathlets
def paths_to_pathlets(paths):
    pathlets = {}
    for path in paths:
        pl = path_to_pathlets(path)
        sum_pathlet_dicts(pathlets, pl)
    return pathlets


def pathlist_stats(pathlist, verbosity = 2):
    #verbosity = 0: Print path stats from all sources to all destinations (100% aggregated)
    #verbosity = 1: Print path stats from each source to all destinations (50% aggregated)
    #verbosity = 2: Print path stats from each source to each destinations (Not aggregated)
    sum_ = 0.0
    max_ = 0
    min_ = 100000
    num_ = 0
    counter = 0
    srcs = []
    dsts = []
    for paths_from in pathlist:
        from_sum = 0.0
        from_counter = 0
        from_max = 0
        from_min = 100000
        from_num = 0
        if len(paths_from) == 0:
            continue
        src = paths_from[0].Paths[0][0]
        srcs.append(src)
        dsts = []
        for paths_from_to in paths_from:
            from_to_num = len(paths_from_to.Paths)
            from_num += from_to_num
            num_ += from_to_num
            if from_to_num == 0:
                continue
            dst = paths_from_to.Paths[0][-1]
            dsts.append(dst)
            from_to_sum = 0.0
            from_to_counter = 0
            from_to_max = 0
            from_to_min = 100000
            for path in paths_from_to.Paths:
                l = len(path)
                from_to_sum += l
                from_to_counter += 1
                from_to_max = max(from_to_max, l)
                from_to_min = min(from_to_min, l)
            if verbosity >= 2:
                print("       {} > {}:: num {}, max {}, avg {}, min {}".format(src, dst, from_to_num, from_to_max, round(from_to_sum/from_to_counter, 2), from_to_min))
            from_sum += from_to_sum
            from_counter += from_to_counter
            from_max = max(from_max, from_to_max)
            from_min = min(from_min, from_to_min)
        if verbosity >= 1:
            print("\n    {} > {} ::\n    num {} (avg {}), max {}, avg {}, min {}\n".format(src, dsts, from_num, round((from_num + 0.0)/len(dsts), 1), from_max,  round(from_sum/from_counter, 2), from_min))
        sum_ += from_sum
        counter += from_counter
        max_ = max(from_max, max_)
        min_ = min(from_min, min_)
    if verbosity >= 0:
        print("\n  {} > {} ::\n  num {} (avg {}), max {}, avg {}, min {}\n".format(srcs, dsts, num_, round((num_ + 0.0)/(len(srcs) * len(dsts)), 1),  max_,  round(sum_/counter, 2), min_))
        print("---------\n")

def pathlist_export(pathlist, output_file, e = False, as_json = False):
    ex = defaultdict(dict) # Element keys = srcs
    for paths_from in pathlist:
        if len(paths_from) == 0:
            continue
        src = paths_from[0].Paths[0][0]
        ex[src] = defaultdict(list)
        dsts = []
        for paths_from_to in paths_from:
            if len(paths_from_to.Paths[0]) == 0:
                continue
            dst = paths_from_to.Paths[0][-1]
            if e:
                ex[src][dst] = paths_from_to.EPaths
            else:
                ex[src][dst] = paths_from_to.Paths
    if as_json:
        save_as_json(ex, output_file)
    else:
        save_as_pkl(ex, output_file)

def bits2bools(bits, n_bits):
    return tuple([bool(bits & (1<<n)) for n in range(n_bits)])
def bools2bits(bools):
    return sum(2**i for i in range(len(bools)) if bools[i])