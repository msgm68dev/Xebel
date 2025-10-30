import socket
from datetime import datetime
import sys
import resource # To limit memory
#=============== SOCKET ==============================
def _listen_to_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    print("socket binded to port ", port)
    #Backlog: In simple words, the backlog parameter specifies the number 
    # of pending connections the queue will hold:
    backlog = 10
    # put the socket into listening mode
    s.listen(backlog) 
    print("socket is listening")
    return s

# def _receive_and_process_data_always(c, logfile, process_function):
#     while True:
#         try:
#             data = c.recv(1024)
#             if not data:
#                 break
    
#             log_into("in<< {}".format(data), logfile)
#             args=data.decode("utf-8").split();
#             result = process_function(args)
#             log_into("out>> {}".format(result), logfile)
#             c.send(bytes('{}\n'.format(result), 'ascii'))
#         except Exception as e:
#             print(e)
#             c.send(b"Error\n")
#     c.close()

#=============== FILE ================================
def now_str():
    return datetime.now().strftime("%B %d %I:%M:%S")
def log_into(log_str, logfile, timestamp = True, print_it = False):
    string_to_write = log_str
    try:
        f = open(logfile, "a+")
        if timestamp:
            timestr = now_str()
            string_to_write = timestr + "|" + string_to_write
        f.write(string_to_write + "\n")
        f.close()
        if (print_it):
            print(string_to_write)
    except Exception as e:
        print("Logging error: {}. log={}".format(str(e), string_to_write))    

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

import configparser
def read_config_as_dict (config_file):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8-sig')
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            value = config.get(section, option)
            config_dict[section][option] = value
    return config_dict
def load_configs(config_file):
    conf = read_config_as_dict(config_file)
    return conf
def save_configs(config_dict, file_path):
    config = configparser.ConfigParser()
    for section, key_values in config_dict.items():
        config.add_section(section)
        for key, value in key_values.items():
            config.set(section, key, str(value))
    with open(file_path, 'w') as configfile:
        config.write(configfile)
        configfile.close()
    # os.system(f"sudo chmod a+r {file_path}")


# ================================================================
# ================================================================
# ================================================================
# ================================================================
# =======================                      ===================
# =======================                      ===================
# =======================      OLD UTILS       ===================
# =======================                      ===================
# =======================                      ===================
# ================================================================
# ================================================================
# ================================================================
# ================================================================
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
def create_file_with_path(filepath, clear_it = True):
    logdir = os.path.dirname(filepath)
    os.makedirs(logdir, exist_ok=True)
    if clear_it:
        open(filepath, "w").close()
    else:
        open(filepath, "a").close()

# thesis_dir  = get_env_var('THESIS')
# topology_dir = os.path.join(thesis_dir, "data/topology/")
# TOPOLOGY = os.path.join(topology_dir, get_env_var('DATASET'))
# check_file_exist(TOPOLOGY)

def apply_function_on_file_content(text_file_path, Function):
    with open(text_file_path, 'r') as f:
        content = f.read()
        f.close()
    processed_content = Function(content)
    with open(text_file_path, 'w') as f:
        f.write(f"{processed_content}")
        f.close()
    return (content, processed_content)
def init_file_content_float(metric_file:str, value:float):
    create_file_with_path(metric_file)
    with open(metric_file, 'w') as f:
        f.write(f"{value}")
        f.close()
    return value
def update_file_content_float_plus(metric_file:str, plus_by:float):
    def add_func(content):
        return float(content) + plus_by
    return apply_function_on_file_content(metric_file, add_func)
def update_file_content_float_grow(metric_file:str, grow_percent:int):
    def enlarge_func(content):
        val = float(content)
        new_val = val * (1 + (grow_percent / 100))
        return new_val
    return apply_function_on_file_content(metric_file, enlarge_func)
def get_file_content_float(file, get_if_error):
    try:
        with open(file, 'r') as f:
            content = f.read()
            f.close()
            return float(content)
    except:
        return get_if_error


def file_to_table(filename, separator = ',', apply_on_each_element = lambda x: x):
    output = []
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    i = 0
    for line in lines:
        s = line.strip()
        if not s or s == [''] or s[0] == '#':
            continue
        i += 1
        words = line.split(separator)
        record = [apply_on_each_element(x.strip()) for x in words]
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
        # if output_file.split('.')[-1].lower() != "json":
        #     raise Exception("File format must be .json")
        _save_obj(obj_to_save, output_file, True)
    except Exception as e:
        print("save_as_json FAILED !!! \nobj type: {}\nfile: {}\nerror: {}\n     try save_as_pkl".format(type(obj_to_save), output_file, str(e)))
def load_pkl_json(filename):
    loaded_dict = _load_obj(filename)
    return loaded_dict

def dataset_pkl_dir(dataset):
    dataset
    dsdir = os.path.dirname(dataset)
    return os.path.join(dsdir, "pickles")
def dataset_dag_dir(dataset):
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

    
def partition_list(L, N:int):
    """
    partitions list L into N [semi]equal pieces
    """
    if not isinstance(N, int) or N < 1:
        raise ValueError("N must be a positive integer")
    if len(L) == 0:
        raise ValueError("L must be a non-empty list")
    # calculate the length of each sublist
    quotient, remainder = divmod(len(L), N)
    lengths = [quotient + 1] * remainder + [quotient] * (N - remainder)
    result = []
    index = 0
    for length in lengths:
        sublist = L[index:index + length]
        result.append(sublist)
        index += length
    return result

def timeit(function_to_time, *args, **kwargs):
    import time
    start_time = time.time()
    result = function_to_time(*args, **kwargs)
    time = round((time.time() - start_time),2)
        # print("+++ _make_all_pathlets : {} seconds, {} Paths, {} Pathlets, {} Edges ".format(round((time.time() - start_time),2), len(self.Paths), len(self.Pathlets), len(self.Edges) ))
    print(f" function {function_to_time} ended in {time} seconds")
    return result
def elapsed_time(start_time, prefix_str = ""):
    import time
    return round((time.time() - start_time),2)
def piece_is_part_of_other(piece:tuple, other:tuple):
        if piece[0] in other:
            start = other.index(piece[0]) 
            end = start + len(piece)
            if len(other) < end:
                return False
            if other[start:end] == piece:
                return True
        return False
def tuple_in_tple(small:tuple, big:tuple):
    return piece_is_part_of_other(small, big)
def random_string_of_length(length:int):
    import string
    import random
    return ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=length))
def random_hex_32():
    return format(random.getrandbits(128), '032x')
def random_hex_16():
    return format(random.getrandbits(64), '016x')
def random_hex_8():
    return format(random.getrandbits(32), '08x')
def str_to_int_tuple(int_tuple_str:str):
    mystr = int_tuple_str.strip()
    if int_tuple_str[0] == '(':
        mystr = mystr[1:]
    if mystr[-1] == ')':
        mystr = mystr[:-1]
    return tuple([int(b.strip()) for b in  mystr.split(",")])
    
def tuples_list_to_str(list_of_tuples, delimeter="/"):
    return delimeter.join([str(t) for t in list_of_tuples])
def tuple_to_dashedstr(Tuple):
    tuple_str = str(Tuple)
    return tuple_str.strip().replace(" ","").replace("(", "").replace(")", "").replace(",", "-")
def str_to_inttuple_list(list_str, delimeter="/"):
    try:
        # return [] if list_str == "" else [eval(s) for s in list_str.split(delimeter)]
        return [] if list_str == "" else [str_to_int_tuple(s) for s in list_str.split(delimeter)]
    except Exception as e:
        xxx = "Error) {}\nlist_str = {}".format(str(e), list_str)
        raise Exception(xxx)
def tuple_formed_by_joining_tuples(main_tuple: tuple, parts: list):
    if len(main_tuple) == 0:
        if len(parts) == 0:
            return True
        else:
            return False
    elif len(main_tuple) == 1:
        if len(parts) == 1 and parts[0] == main_tuple:
            return True
        else:
            return False
    else:
        if sum([len(x) for x in parts]) - len(parts) + 1 != len(main_tuple):
            return False
        else:
            result = True
            i = 0
            while i < len(main_tuple) - 1:
                old_i = i
                for p in parts:
                    if main_tuple[i] == p[0]:
                        j = 1
                        while j < len(p):
                            if main_tuple[i+j] != p[j]:
                                result = False
                                break
                            j += 1
                        i += j - 1
                if old_i == i:
                    result = False
                    break
            return result
#tuple_formed_by_joining_tuples((1,2,3,4,5,6,7,8,9), [(1,2), (2,3,4,5), (5,6,7,8,9)])

import subprocess
def run_shell_command_simple(command):
    print(f"command = {command}")
    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

def comma_separated_str_to_int_tuple(comma_separated_str):
    vals = comma_separated_str.replace(" ", "").replace(",", " ").strip().split(" ")
    try:
        return tuple([int(v) for v in vals])
    except:
        raise Exception(f"Error in comma_separated_str_to_int_tuple: non valid string: {comma_separated_str}")
        return None
def comma_separated_str_to_float_tuple(comma_separated_str):
    vals = comma_separated_str.replace(" ", "").replace(",", " ").strip().split(" ")
    try:
        return tuple([float(v) for v in vals])
    except:
        raise Exception(f"Error in comma_separated_str_to_int_tuple: non valid string: {comma_separated_str}")
        return None
def comma_separated_str_to_str_tuple(comma_separated_str):
    vals = comma_separated_str.replace(" ", "").replace(",", " ").strip().split(" ")
    try:
        return tuple([str(v) for v in vals])
    except:
        raise Exception(f"Error in comma_separated_str_to_str_tuple: non valid string: {comma_separated_str}")
        return None
def find_largest_less_than(num, sorted_list):
    left, right = 0, len(sorted_list) - 1
    result = None
    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] < num:
            result = sorted_list[mid]
            left = mid + 1
        else:
            right = mid - 1
    return result

def set_memory_limit_B(max_size_bytes):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (max_size_bytes, hard))
def set_memory_limit_GB(max_size_gigabytes):
    print(f"Limiting program memoty to: {max_size_gigabytes} GiB")
    set_memory_limit_B(max_size_gigabytes * 1024 * 1024 * 1024)
def find_nearest_number_in_list(numbers, number):
    lowest_diff = 100000000
    nearest = None
    for n in numbers:
        diff = abs(n - number)
        if diff < lowest_diff:
            lowest_diff = diff
            nearest = n
    return nearest

def is_yes(answer:str):
    return answer.lower() in ("yes", "y", "true")
def dict_to_ymlstr(D:dict, prefix = "", print_header = True):
    outstr = ""
    if print_header:
        outstr += f"{prefix}Dict: \n"
    for k in D:
        if type(D[k]) != dict:
            outstr += f"{prefix}  - {k}: {D[k]}\n"
        else:
            outstr += f"{prefix}  - {k}: \n{dict_to_ymlstr(D[k], prefix='  ', print_header= False)}\n"
    return outstr
def print_dict_yml(D: dict):
    print(dict_to_ymlstr(D))
def normalize(numbers):
        Min = min(numbers)
        diff = max(numbers) - Min
        normals = [(x - Min)/diff for x in numbers]
        return normals
def dict_to_1line_str(d:dict):
    s = ""
    for k in d:
        s += f"{k}:{d[k]}, "
    return s