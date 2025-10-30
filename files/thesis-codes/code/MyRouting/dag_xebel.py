from utils import *
import time, gc
import datetime
from collections import defaultdict
import sys

nodes = {} # defaultdict(tuple)
e_base = 0  # Are paths stated by edges?

def opens_i_str(i:int):
    return f"opens_{i}"
def openofs_str_i(i:int):
    return f"open_ofs_{i}"
def piece_inside_tuple(inner:tuple, larger:tuple):
    for i in range(len(larger)):
        if inner[0] == larger[i]:
            end = i + len(inner)
            if len(larger) < end:
                return False
            if larger[i:end] == inner:
                return True
    return False
def dagnode_list_to_str(list_of_dagnodes, delimeter="/"):
    return delimeter.join([str(t.Tuple) for t in list_of_dagnodes])
def get_uncovered_parts_of_tuple(big:tuple, smalls:list):
    # try:
        uncovereds = []
        smalls_sorted = sorted(smalls, key=lambda x:big.index(x[0]), reverse=False)
        start_idx = 0
        # from start of big to end of smalls_sorted
        for small in smalls_sorted:
            idx = big.index(small[0])
            if idx > start_idx :
                uncovereds.append(big[start_idx:idx+1])
                start_idx = idx + len(small) - 1
            else:
                start_idx = idx + len(small) - 1
        # from end of smalls_sorted to end of big
        if start_idx < len(big) - 1:
            uncovereds.append(big[start_idx:])
        return uncovereds
    # except:
        # raise Exception(f"Error in get_uncovered_parts_of_tuple: \n\tbig: {str(big)}\n\tsmalls: {tuples_list_to_str(smalls)}\n:|")


class dagnode:
    def __init__(self, Tuple, \
                is_edge = False, is_path = False \
                , childs = [] \
                , parents = [] ):
        self.gain = -1000
        self.gain_function = self._gain1
        if Tuple not in nodes.keys():
            self.OPTS = defaultdict(lambda : None)
            self.LISTS = defaultdict(lambda : [])
            self.is_edge = is_edge
            self.Tuple = Tuple
            self.is_path = is_path
            self.childs = [] 
            self.parents = []
            union_lists(self.childs, childs)
            union_lists(self.parents, parents)
            nodes[Tuple] = self
        else:
            nodes[Tuple].is_path = is_path or nodes[Tuple].is_path
            nodes[Tuple].is_edge = is_edge or nodes[Tuple].is_edge
            union_lists(nodes[Tuple].childs, childs)
            union_lists(nodes[Tuple].parents, parents)
            # for key in LISTS:
            #     if key in nodes[Tuple].LISTS:
            #         union_lists(nodes[Tuple].LISTS[key], LISTS[key])
            #     else:
            #         nodes[Tuple].LISTS[key] = LISTS[key]
    def add_parent(self, parent, check_parents = False):
        if parent not in self.parents:
            if check_parents and parent != ROOT  and not piece_inside_tuple(parent.Tuple, self.Tuple):
                raise Exception(f" Owh {parent.Tuple} can not be parent of {self.Tuple}")
            self.parents.append(parent)
            parent.childs.append(self)
        
    def scan_open_parts(self, i:int):
        big = self.Tuple
        smalls = [parent.Tuple for parent in self.parents]
        try:
            opens_tuple = get_uncovered_parts_of_tuple(big, smalls)
        except:
            raise Exception(f"Error in scan_open_parts of {str(self.Tuple)}\n\tparents: {dagnode_list_to_str(self.parents)}\n:|")

        open_parts_all = [nodes[d] for d in opens_tuple]
        open_parts = []
        for open_part in open_parts_all:
            if open_part.is_an_edge():
                self.add_parent(open_part)
            else:
                open_parts.append(open_part)
        self._set_opens_i(i, open_parts)
        for open_part in open_parts:
            open_part.add_1_openofs_i(i, self)
        return self.get_opens_i(i)
    def get_opens_i(self, i:int):
        opens_str = opens_i_str(i)
        if opens_str in self.LISTS:
            return list(set(self.LISTS[opens_str]))
        else:
            # print(f"{self.Tuple} has no list {keystr}")
            return []
    def _set_opens_i(self, i:int, opens:list):
        opens_str = opens_i_str(i)
        self.LISTS[opens_str] = opens
    def get_openofs_i(self, i:int):
        openofs_str = openofs_str_i(i)
        if openofs_str in self.LISTS:
            return list(set(self.LISTS[openofs_str]))
        else:
            # print(f"{self.Tuple} has no list {keystr}")
            return []
    def add_1_openofs_i(self, i:int, open_of_dnode):
        openofs_str = openofs_str_i(i)
        if self.LISTS[openofs_str] :
            if open_of_dnode not in self.LISTS[openofs_str]:
                self.LISTS[openofs_str].append(open_of_dnode)
        else:
            self.LISTS[openofs_str] = [open_of_dnode]
    def add_n_openofs_i(self, i:int, open_ofs_list):
        openofs_str = openofs_str_i(i)
        for open_of_dnode in open_ofs_list:
            self.add_1_openofs_i(i, open_of_dnode)
    def update_gain(self, iteration = -1):
        self.gain = self.gain_function(iteration)
    def _gain1(self, iteration:int):
        l = len(self.Tuple) - 1
        openofs = self.get_openofs_i(iteration)
        n = len(openofs)
        gain = (l*n) - (l+n)
        if self in openofs and len(openofs) > 1:
            # If this piece is also a target:
            gain += l
        return gain
    def gain_for_openofs(self, iteration:int, openofs:list):
        l = len(self.Tuple)
        n = len(openofs)
        gain = (l*n) - (l+n)
        if self in openofs:
            # If this piece is also a target:
            gain += l
        return gain
    def parents_str(self):
        return "/".join([str(p.Tuple) for p in self.parents])
    def childs_str(self):
        return "/".join([str(p.Tuple) for p in self.childs])
    def is_an_edge(self):
        return len(self.Tuple) == 2 - e_base
    def summary_str(self):
        return f"node {str(self.Tuple)}\n   | + + parents: {dagnode_list_to_str(self.parents)}\n   | + + childs: {dagnode_list_to_str(self.childs)}\n   | + + Done: {self.OPTS['done']}"
    def summary_str_i(self, iteration:int):
        return f"node {str(self.Tuple)}\n   | + + parents: {dagnode_list_to_str(self.parents)}\n   | + + childs: {dagnode_list_to_str(self.childs)}\n   | + + + opens: {dagnode_list_to_str(self.get_opens_i(iteration))}\n   | + + Done: {self.OPTS['done']}"
    def full_str_i(self, iteration:int, prefix = "   | + + "):
        return f"node {str(self.Tuple)}\n{prefix}openofs_{iteration}: {dagnode_list_to_str(self.get_openofs_i(iteration))}\n{prefix}opens_{iteration}: {dagnode_list_to_str(self.get_opens_i(iteration))}\n{prefix}parents: {dagnode_list_to_str(self.parents)}\n{prefix}childs: {dagnode_list_to_str(self.childs)}\n{prefix}opens: {dagnode_list_to_str(self.get_opens_i(iteration))}\n{prefix}Done: {self.OPTS['done']}"
    def verify_parents(self):
        if self.is_an_edge() and self.parents == [ROOT]:
            return True
        parents = [p.Tuple for p in self.parents]
        return tuple_formed_by_joining_tuples(self.Tuple, parents)
    def sort_parents(self):
        if self.is_an_edge() and self.parents == [ROOT]:
            return True
        result = False
        parents_old = self.parents
        parents_old_str = '/'.join([str(p.Tuple) for p in parents_old])
        parents_new = []
        if len(self.Tuple) == 1 and len(self.parents) == 0:
            result =  True
        if len(self.Tuple) == 2 - e_base and len(self.parents) == 1 and self.parents[0].Tuple == (0,):
            result =  True
        if len(self.Tuple) > 2 - e_base:
            i = 0
            while i < len(self.Tuple) - 1:
                old_i = i
                for p in parents_old:
                    if self.Tuple[i] == p.Tuple[0]:
                        j = 1
                        while j < len(p.Tuple):
                            if self.Tuple[i+j] != p.Tuple[j]:
                                # print(f"NOT VERIFIED: {p.Tuple} NOT IN {self.Tuple} ")
                                result = False
                                break
                            j += 1
                        i += j - 1
                        parents_old.remove(p)
                        parents_new.append(p)
                if old_i == i:
                    result = False
                    break
            self.parents = parents_new
            result = True
        return result
    def sort_and_verify_parents(self):
        if not self.sort_parents():
            return False
        if self.is_an_edge() and len(self.parents) == 1 and self.parents[0] == ROOT:
            return True
        joined = ()
        def join_tuples(t1:tuple, t2:tuple):
            if len(t1) == 0:
                return t2
            if len(t2) == 0:
                return t1
            if t1[-1] == t2[0]:
                return t1[:-1] + t2
            if t2[-1] == t1[0]:
                return t2[:-1] + t1
            return None
        for p in self.parents:
            joined = join_tuples(joined, p.Tuple)
        return joined == self.Tuple
def yield_sub_tuples(pathlet_tuple: tuple):
    maxl = len(pathlet_tuple)
    for L in reversed(range(2, maxl)):
        for i in range(maxl-L+1):
            sub = tuple(pathlet_tuple[i:i+L])
            yield sub
def get_all_subways_of(dnode: dagnode, iteration:int):
    openofs_str = openofs_str_i(iteration)
    open_ofs = dnode.get_openofs_i(iteration)
    yy = "no"
    for sub in yield_sub_tuples(dnode.Tuple):
        edg = len(sub) == (2 - e_base)
        dagnode(sub, \
            is_edge = edg, \
        )
        d = nodes[sub]
            # LISTS = {openofs_str: open_ofs}
        d.add_n_openofs_i(iteration, open_ofs)
        yield d
def disjoint_ways(way1: tuple, way2: tuple):
    for i in range(len(way1)-1):
        step1 = (way1[i], way1[i+1])
        for j in range(len(way2)-1):
            step2 = (way2[j], way2[j+1])
            if step1 == step2:
                return False
    return True
def process_pieces_4_not_work(pieces: list, iteration:int):
    accepteds = []
    count = 0
    in1000accept = 0
    x_time = time.time()
    openofs_changed = False
    for piece in pieces:
        count += 1
        rejected_cause = None
        ok = True
        piece_openofs_set = set(piece.get_openofs_i(iteration))
        for acpt in accepteds:
            if not disjoint_ways(piece.Tuple, acpt.Tuple):
                acpt_openofs_set = set(acpt.get_openofs_i(iteration))
                common_openofs = acpt_openofs_set & piece_openofs_set
                if len(common_openofs) > 0:
                    piece_openofs_set -= common_openofs
                    openofs_changed = True
                    new_gain = piece.gain_for_openofs(iteration, piece_openofs_set)
                    if new_gain <= 0:
                        ok = False
                        rejected_cause = acpt
                        break
        if ok:
            piece.LISTS[openofs_str_i(iteration)] = list(piece_openofs_set)
            # if openofs_changed:
                # input(f" x x openofs_changed for {str(piece.Tuple)} to {dagnode_list_to_str(piece.LISTS[openofs_str_i(iteration)])}")
            piece.update_gain(iteration)
            accepteds.append(piece)
            in1000accept += 1
        if count % 1000 == 0:
            print(f"        {count} pieces processed: accepted({in1000accept} ): {round(time.time() - x_time, 1)}")
            in1000accept = 0
            x_time = time.time()
    return accepteds
def process_pieces_00(pieces: list, iteration:int):
    accepteds = []
    return accepteds
ROOT = dagnode(("ROOT"))
def dag_explore_bfs( dag_root = ROOT, flag_str = None, each_node_function = lambda x : None, report_each = -1):
    from  collections import deque
    if not flag_str:
        flag_str = "bfs_" + random_string_of_length(4)
    for node in nodes.values():
        node.OPTS[flag_str] = False
    # result = {}
    root = dag_root
    # q = []
    q = deque()
    node_counter = 0
    t = time.time()
    q.append(root)
    while len(q) > 0:
        # subject = q.pop(0)
        subject = q.pop()
        if not subject.OPTS[flag_str]:
            each_node_function(subject)
            node_counter += 1
            if node_counter % report_each == 0 and report_each > 0:
                print(f"bfs processed {node_counter} nodes in {elapsed_time(t)} secs.")
                t = time.time()
            subject.OPTS[flag_str] = True
        for ch in subject.childs:
            q.append(ch)
def create_childs(logger = None):
    t = time.time()
    for key in nodes:
        node = nodes[key]
        if node == ROOT:
            continue
        node.childs = []
    for key in nodes:
        node = nodes[key]
        if node.is_an_edge() or node == ROOT:
            continue
        for parent in node.parents:
            parent.childs.append(node)
    # logger(f"childs created in {elapsed_time(t)} secs")
class dag:
    def __init__(self, pathlist_file_to_import = None, logfile = None, make_method = None):
        self.Edges = [] # Single edges used
        self.Paths = []
        self.make_method = make_method
        self.Dag_dict = None # It will be created after make()
        if pathlist_file_to_import:
            print("loading PATHS pickle file: {} ".format(pathlist_file_to_import), end="")
            self.Paths_dict = load_pkl_json(pathlist_file_to_import)
            # print("  done")
            for src in self.Paths_dict:
                print("  load paths from {} ... ".format(src), end="")
                for dst in self.Paths_dict[src]:
                    for path in self.Paths_dict[src][dst]:
                        Tuple = tuple(path)
                        dnode = dagnode(Tuple, is_path=True)
                        nodes[Tuple] = dnode
                        self.Paths.append(dnode)
                print("    done")
            sample = self.Paths[-1].Tuple[-1]
            print(" sorting paths from longest to smallest:", end="")
            self.Paths = sorted(self.Paths, key=lambda x: len(x.Tuple), reverse=True)
            print(f"done\n total {len(self.Paths)} paths imported")
            if str(sample).__contains__("-"):
                e_base = 1
            else:
                e_base = 0
        if logfile:
            if not os.path.exists(logfile):
                logdir = os.path.dirname(logfile)
                os.makedirs(logdir, exist_ok=True)
            with open(logfile, "a") as f:
                f.close()
            self.logfile = logfile
            self.logger("xoff-2:", log_date=False)
        else:
            self.logfile = "/dev/null"
    def logger(self, logstr, print_also = True, log_date = False):
        date_str = ""
        if log_date:
            date_str = f"{datetime.datetime.now()} |"
        with open(self.logfile, "a+") as f:
            f.write(f"{date_str} {logstr}\n")
            if print_also:
                print(f"{logstr}")
            f.close()
    def make(self, **kwargs):
        Make_func_object = None
        make_function_name = ""
        Parameters = {}
        try:
            if "/" in self.make_method:
                words = self.make_method.split("/")
                make_function_name = words[0]
                if len(words) == 2:
                    options_raw = words[1]
                    if ":" in options_raw:
                        options_list = options_raw.split("-")
                        for option in options_list:
                            opts = str(option).split(":")
                            Parameters[opts[0]] = opts[1]
                # self.logger("MAKE: {}\n\tOptions: {}".format(make_function_name, Parameters))
            else:
                make_function_name = self.make_method
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            raise Exception("Error 01) invalid make_method value \"{}\"\nexc_type = {}\nerror = {}\nfile = {}\nline = {}".format( \
                                                        self.make_method, \
                                                        str(e) , exc_type, fname, exc_tb.tb_lineno))
        Make_func_object = getattr(self, make_function_name)
        start_time = time.time()
        # self.logger(f"make_method: {self.make_method}")
        # MAKE START *************************************************
        Make_func_object(Parameters)
        # MAKE END ***************************************************
        make_duration = elapsed_time(start_time)
        if not self.Dag_dict:
            raise Exception(f"ERROR. Dag_dict is not created by make function {self.make_method}")
        verified = self.verify()
        # self.logger(f"\tmake_time: {make_duration}")
        # self.logger(f"\tverified: {verified}")
        if verified:
            cost, n_mids, n_paths, n_midonlys = self.cost()
            def base_cost():
                cost = 0
                for path in self.Paths:
                    # cose = Number of operations = Number of edges - 1
                    # Number of edges = len(Tuple) - 1 if not edge_based representation (e_base == 0)
                    cost += len(path.Tuple) - (1 - e_base) -1
                return cost
            cost0 = base_cost()
            improv = round(100 * (cost0 - cost) / cost0, 2)
            ops_per_path = round(cost / len([p for p in self.Paths if len(p.Tuple) > (2-e_base) ]), 2)
            self.Dag_dict["verified"] = True
            self.Dag_dict["make_duration"] = make_duration
            self.Dag_dict["make_method"] = self.make_method
            self.Dag_dict["base_dag_cost"] = cost0
            self.Dag_dict["dag_cost"] = cost
            self.Dag_dict["improvement_percentage"] = improv
            self.Dag_dict["operations_per_path"] = ops_per_path
            self.Dag_dict["number_of_paths"] = n_paths
            self.Dag_dict["number_of_leaf_paths"] = n_paths - n_mids
            self.Dag_dict["number_of_nonpath_dagnodes"] = n_midonlys
        else:
            self.Dag_dict["verified"] = False
        return self.Dag_dict
    def make_00(self, options):
        root = ROOT
        indags = []
        dones = []
        print(f"make_00 start  ")
        for path in self.Paths :
            if len(path.Tuple) == 1 - e_base:
                # Skip sngle nodes like (0,)!
                continue
            elif len(path.Tuple) == 2 - e_base:
                # Edge paths are already done!
                path.is_edge = True
                path.OPTS["Indag"] = False
                path.OPTS["Done"] = True
                dones.append(path)
                path.add_parent(root)
            else:
                path.OPTS["Indag"] = True
                indags.append(path)
        remainings = indags
        print(f"@  {len(remainings)} paths")
        for undone in remainings:
            ucs = get_uncovered_parts_of_tuple(undone.Tuple, [parent.Tuple for parent in undone.parents])
            # Yaal haye tuple ha ro vasl kon be baalaa. tekrari nadare
            for uc in ucs:
                for i in range(len(uc) - 1):
                    dnode = nodes[uc[i:i+2]]
                    undone.add_parent(dnode)
            parents = [str(p.Tuple) for p in undone.parents]
        print(f"make_00 end --- ")
        if('dont_save' not in options or options['dont_save'] == False):
            self.Dag_dict = self._create_dag_dict()
    def make_buttom_up(self, options):
        indags = []
        dones = []
        root = ROOT
        all_accepted_candidates = []
        gc.collect()
        def AM1_disjoint_OR_no_common_child(pieces: list, iteration:int):
            accepteds = []
            count = 0
            in1000accept = 0
            x_time = time.time()
            openofs_changed = False
            for piece in pieces:
                count += 1
                rejected_cause = None
                ok = True
                piece_openofs_set = set(piece.get_openofs_i(iteration))
                for acpt in accepteds:
                    if not disjoint_ways(piece.Tuple, acpt.Tuple):
                        acpt_openofs_set = set(acpt.get_openofs_i(iteration))
                        common_openofs = acpt_openofs_set & piece_openofs_set
                        if len(common_openofs) > 0:
                            # piece_openofs_set -= common_openofs
                            # openofs_changed = True
                            # new_gain = piece.gain_for_openofs(iteration, piece_openofs_set)
                            # if new_gain <= 0:
                                ok = False
                                rejected_cause = acpt
                                break
                if ok:
                    # openofs_str = openofs_str_i(iteration)
                    # piece.LISTS[openofs_str] = list(piece_openofs_set)
                    # piece.update_gain(iteration)
                    accepteds.append(piece)
                    in1000accept += 1
                if count % 1000 == 0:
                    print(f"processed {count} pieces ({in1000accept} accepted): {round(time.time() - x_time, 1)}")
                    in1000accept = 0
                    x_time = time.time()
            return accepteds
        def AM1_disjoint(pieces: list, iteration:int):
            accepteds = []
            count = 0
            in1000accept = 0
            x_time = time.time()
            openofs_changed = False
            for piece in pieces:
                count += 1
                rejected_cause = None
                ok = True
                piece_openofs_set = set(piece.get_openofs_i(iteration))
                for acpt in accepteds:
                    if not disjoint_ways(piece.Tuple, acpt.Tuple):
                        ok = False
                        rejected_cause = acpt
                        break
                if ok:
                    # openofs_str = openofs_str_i(iteration)
                    # piece.LISTS[openofs_str] = list(piece_openofs_set)
                    # piece.update_gain(iteration)
                    accepteds.append(piece)
                    in1000accept += 1
                if count % 1000 == 0:
                    print(f"processed {count} pieces ({in1000accept} accepted): {round(time.time() - x_time, 1)}")
                    in1000accept = 0
                    x_time = time.time()
            return accepteds
        def AM2_disjoint_remove_common_child(pieces: list, iteration:int):
            accepteds = []
            count = 0
            in1000accept = 0
            x_time = time.time()
            openofs_changed = False
            for piece in pieces:
                count += 1
                rejected_cause = None
                ok = True
                piece_openofs_set = set(piece.get_openofs_i(iteration))
                for acpt in accepteds:
                    if not disjoint_ways(piece.Tuple, acpt.Tuple):
                        acpt_openofs_set = set(acpt.get_openofs_i(iteration))
                        common_openofs = acpt_openofs_set & piece_openofs_set
                        if len(common_openofs) > 0:
                            piece_openofs_set -= common_openofs
                            openofs_changed = True
                            new_gain = piece.gain_for_openofs(iteration, piece_openofs_set)
                            if new_gain <= 0:
                                ok = False
                                rejected_cause = acpt
                                break
                if ok:
                    piece.LISTS[openofs_str_i(iteration)] = list(piece_openofs_set)
                    # if openofs_changed:
                        # input(f" x x openofs_changed for {str(piece.Tuple)} to {dagnode_list_to_str(piece.LISTS[openofs_str_i(iteration)])}")
                    piece.update_gain(iteration)
                    accepteds.append(piece)
                    in1000accept += 1
                if count % 1000 == 0:
                    print(f"processed {count} pieces ({in1000accept} accepted): {round(time.time() - x_time, 1)}")
                    in1000accept = 0
                    x_time = time.time()
            return accepteds
        def insert_to_dag(accepted: dagnode, iteration:int):
            all_accepted_candidates.append(accepted)
            if accepted not in indags:
                accepted.OPTS["Indag"] = True
                indags.append(accepted)
            for child in accepted.get_openofs_i(iteration):
                if child != accepted:
                    child.add_parent(accepted)
        def grinder(to_grind: list, iteration:int):
            count = 0
            subs = []
            for dnode in to_grind:
                if dnode.is_edge:
                    self.logger("This happened! a target is edge")
                    continue
                else:
                    subs.append(dnode) # Add a piece iteslt
                    for d in get_all_subways_of(dnode, iteration): # Shamele khode tuple nist!
                        if not d.is_edge:
                            subs.append(d)
                count += 1
                if count % 1000 == 0:
                    print(f"        grinded {count} nodes")
            pieces = sorted(list(set(subs)), key=lambda x:x.Tuple)        
            return pieces
        print(f" MAKE start : {self.make_method} --------------------- ")
        for path in self.Paths :
            if len(path.Tuple) == 1 - e_base:
                # Skip sngle nodes like (0,)!
                continue
            elif len(path.Tuple) == 2 - e_base:
                # Edge paths are already done!
                path.is_edge = True
                path.OPTS["Indag"] = False
                path.OPTS["Done"] = True
                dones.append(path)
                path.add_parent(root)
            else:
                path.OPTS["Indag"] = True
                indags.append(path)
        iteration = 0
        acception_method = locals().get(options["acception_method"])
        if not acception_method:
            raise Exception("Invalid acception method name: \"{options['acception_method']}\"")
        print("  While START ----------------- ")
        while True:
            iteration += 1
            print(f"  While iteration {iteration} ---------- ")
            to_grind = []
            print(f"    * scan open parts of {len(indags)} indags ")
            to_be_dones = []
            for indag in indags:
                open_parts = indag.scan_open_parts(iteration)
                if len(open_parts) == 0:
                    to_be_dones.append(indag)
                for part in open_parts:
                    if part not in to_grind:
                        to_grind.append(part)
            print(f"    * remove {len(to_be_dones)} dones from indags")
            for to_be_done in to_be_dones:
                to_be_done.OPTS["Done"] = True
                to_be_done.OPTS["Indag"] = False
                indags.remove(to_be_done)
                dones.append(to_be_done)
            print(f"    * grind {len(to_grind)} open parts ")
            pieces = grinder(to_grind, iteration)
            print(f"    * update gains of {len(pieces)} pieces & sort ")
            for piece in pieces:
                piece.update_gain(iteration)
            gc.collect()
            positive_pieces = [ p for p in pieces if p.gain > 0]
            positive_pieces.sort(key = lambda x:x.gain, reverse=True)
            print(f"    * process {len(positive_pieces)} positive pieces ")
            accepted_pieces = acception_method(positive_pieces, iteration)
            print(f"    #pieces: {len(pieces)}, #positives: {len(positive_pieces)}, #accepteds: {len(accepted_pieces)}")
            for accepted in accepted_pieces:
                insert_to_dag(accepted, iteration)
            # ---------- DONE ----------
            n_done_paths = len([p for p in self.Paths if p.OPTS["Done"]])
            n_remaining_paths = len(self.Paths) - n_done_paths
            print(f"    * endof {iteration}, to_grind: {len(to_grind)}, indags: {len(indags)}, \
                        dones: {len(dones)}, accepted_cands: {len(all_accepted_candidates)}, \
                        done_paths: {n_done_paths}, remaining_paths: {n_remaining_paths}")
            # input()
            if len(accepted_pieces) == 0:
                    print(f"No more benefit!, breaking...")
                    break
        print("  While END ----------------- ")
        iteration = 999999
        to_grind = []
        print(f"  * scan open parts of remaining {len(indags)} indags ")
        for indag in indags:
            open_parts = indag.scan_open_parts(iteration)
            union_lists(to_grind, open_parts)
        remainings = sorted(list(set(to_grind)), key=lambda x:x.Tuple)
        print(f"  * process {len(remainings)} remaining open parts")
        for undone in remainings:
            ucs = get_uncovered_parts_of_tuple(undone.Tuple, [parent.Tuple for parent in undone.parents])
            # Yaal haye tuple ha ro vasl kon be baalaa. tekrari nadare
            prnt_str='/'.join([str(p.Tuple) for p in undone.parents])
            ucs_str = '/'.join([str(t) for t in ucs])
            for uc in ucs:
                for i in range(len(uc) - 1):
                    dnode = nodes[uc[i:i+2]]
                    undone.add_parent(dnode)
            parents = [str(p.Tuple) for p in undone.parents]
            prnt_str='/'.join(parents)
        print(f" MAKE end : {self.make_method} --------------------- ")
        self.Dag_dict = self._create_dag_dict()
    def make_post_joiner(self, options):
        def join_ways(way1: dagnode, way2:dagnode):
            t1 = way1.Tuple
            t2 = way2.Tuple
            if t1[-1] == t2[0]:
                t = t1[:-1] + t2
                dagnode(Tuple=t)
                return nodes[t]
            else:
                return None
        make_func_name = options["base_make"]
        base_make = getattr(self, make_func_name)
        st = time.time()
        self.logger(f"{self.make_method} -> base_make start...")
        base_make(options)
        self.logger(f"{self.make_method} -> base_make done in {elapsed_time(st)} secs")
        Nodes_to_process = []
        for p in self.Paths:
            if len(p.Tuple) > 2 - e_base:
                Nodes_to_process.append(p)
        start_time = time.time()
        has_benefit = True
        iteration = 0
        self.logger(f"  {self.make_method} WHILE! start ----------------")
        while has_benefit:
            added_nodes = []
            if self.verify():
                duration = elapsed_time(start_time)
                print(f"  dag of {make_func_name} verified in {duration} seconds")
            else:
                raise Exception(f" Owh! dag NOT verified! make: {make_func_name}")
            iteration += 1
            make_func_name = f"make_joiner:iter {iteration}"
            self.logger("    iteration {}::::: ".format(iteration))
            check_str = f"make_joiner_{iteration}_checked"
            total_util = 0
            path_count = 0
            n_joinings_in_1000 = 0
            n_joinings_total = 0
            # self.logger(f"*s*s*s**s*s*")
            start_time = time.time()
            self.logger(f"gc.collect() : ")
            x = gc.collect()
            self.logger(f" {x} :)))")
            for path in Nodes_to_process:
                news = []
                news_for = []
                news_parts = []
                path_count += 1
                for i in range( len(path.parents) - 1):
                    way1 = path.parents[i]
                    way2 = path.parents[i+1]
                    way = join_ways(way1, way2)
                    # if not way:
                    #     print("path {} parents {}".format(path.Tuple, dagnode_list_to_str(path.parents)))
                    #     raise Exception(f"ajab! {str(way1.Tuple)} and {str(way2.Tuple)} are not sequential!!!")
                    if way == path or way.OPTS[check_str]:
                        continue
                    way.OPTS[check_str] = True
                    paths_has_way = [path]
                    for other in Nodes_to_process:
                        if way1 in other.parents and way2 in other.parents:
                            if other != path:
                                paths_has_way.append(other)
                    if len(paths_has_way) > 1:
                        news.append(way)
                        news_for.append(paths_has_way)
                        news_parts.append([way1, way2])
                j  = 0
                for i in range(len(news)):
                    way = news[i]
                    paths_contain_way = news_for[i]
                    way1 = news_parts[i][0]
                    way2 = news_parts[i][1]
                    for ch in paths_contain_way:
                        if ch == way:
                            continue
                        if way1 in ch.parents and way2 in ch.parents:
                            j += 1
                            idx = ch.parents.index(way1)
                            ch.parents = ch.parents[:idx] + [way] + ch.parents[idx+2:]
                            way1.childs.remove(ch)
                            way2.childs.remove(ch)
                            if ch not in way.childs:
                                way.childs.append(ch)
                            way.parents = [way1, way2]
                            if way not in way1.childs:
                                way1.childs.append(way)
                            if way not in way2.childs:
                                way2.childs.append(way)
                n_joinings_in_1000 += j
                n_joinings_total += j
                if path_count % 1000 == 0:
                    duration = elapsed_time(start_time)
                    print(f"      {path_count}/{len(Nodes_to_process)} nodes processed in {duration} seconds. {n_joinings_in_1000} joinings performed. total {n_joinings_total}")
                    start_time = time.time()
                    n_joinings_in_1000 = 0            
            if n_joinings_total == 0:
                has_benefit = False
        print(f"  {self.make_method} WHILE! end ----------------")
        self.Dag_dict = self._create_dag_dict()
    def make_partial_sticks(self, options):
        options.update({'dont_save' : True})
        self.make_00(options)
        ignore_flag = options['ignore_flag']
        root = ROOT
        # indags = []
        # dones = []
        print(f"{self.make_method} start  ")
        for path in self.Paths :
            if len(path.Tuple) == 1 - e_base:
                continue
            elif len(path.Tuple) == 2 - e_base:
                # Edge paths are already done!
                path.is_edge = True
                # path.OPTS["Indag"] = False
                # path.OPTS["Done"] = True
                # dones.append(path)
                path.add_parent(root)
            # else:
                # path.OPTS["Indag"] = True
                # indags.append(path)
            
        # remainings = indags
        def Mid(tup):
            return int(len(tup)/2)
        def alt_range(X):
            counter = 0
            for i in range(X):
                if counter == 0:
                    yield X
                else:
                    yield X - i
                    yield X + i
                counter += 1
                counter += 1
        def yield_subs(Tup):
            m = Mid(Tup)
            for i in alt_range(m):
                yield [Tup[:i+1], Tup[i:]]
        paths_tuples = sorted([p.Tuple for p in self.Paths], key = lambda x: len(x))
        path_dict_temp = dict([(p.Tuple, p) for p in self.Paths])
        remainings_tuples = []
        counter = 0
        dones = 0
        for path_tuple in paths_tuples:
            if len(path_tuple) == 2 - e_base:
                continue
            done = False
            for subs in yield_subs(path_tuple):
                half1_tup = subs[0]
                half2_tup = subs[1]
                if len(half1_tup) == 1 or len(half2_tup) == 1:
                    continue
                if half1_tup in path_dict_temp and half2_tup in path_dict_temp:
                    half1 = nodes[half1_tup]
                    half2 = nodes[half2_tup]
                    path = nodes[path_tuple]
                    path.parents = [half1, half2]
                    done = True
                    path.OPTS[ignore_flag] = True
                    break
            if not done:
                remainings_tuples.append(path_tuple)
            else:
                dones += 1
            counter += 1
            # if path_tuple == (6, 8, 13, 16, 17, 10, 3, 0, 2, 11, 1, 5, 12, 9, 7, 4, 22, 19, 14, 15):
            #     input(f"tupl = {nodes[path_tuple].Tuple}\ndone = {done}, {dagnode_list_to_str(nodes[path_tuple].parents)}")
            if counter % 1000 == 0:
                print(f"  {counter} paths processed: {dones} done!")
        create_childs(self.logger)
        self.Dag_dict = self._create_dag_dict()
    def make_post_joiner_faster(self, options):
        def join_ways(way1: dagnode, way2:dagnode):
            t1 = way1.Tuple
            t2 = way2.Tuple
            if t1[-1] == t2[0]:
                t = t1[:-1] + t2
                dagnode(Tuple=t)
                return nodes[t]
            else:
                return None
        make_func_name = options["base_make"]
        ignore_flag = random_string_of_length(4)
        options.update({'ignore_flag' : ignore_flag})
        base_make = getattr(self, make_func_name)
        base_make(options)
        Nodes_to_process = []
        for p in self.Paths:
            if len(p.Tuple) > 2 - e_base:
                if len(p.parents) > 2 or len(p.Tuple) == 2:
                    Nodes_to_process.append(p)
        start_time = time.time()
        has_benefit = True
        iteration = 0
        print("  joiner WHILE! start ----------------")
        gc.collect()
        # for n in nodes.values():
        #     if n == ROOT:
        #         continue
        #     if n.is_an_edge():
        #         continue
        #     n.OPTS["parents_dict"] = dict([(p.Tuple, p) for p in n.parents])
        while has_benefit:
            added_nodes = []
            if self.verify():
                duration = elapsed_time(start_time)
                print(f"  dag of {make_func_name} verified in {duration} seconds")
            else:
                raise Exception(f" Owh! dag NOT verified! make: {make_func_name}")
            iteration += 1
            make_func_name = f"make_joiner:iter {iteration}"
            check_str = f"make_joiner_{iteration}_checked"
            total_util = 0
            path_count = 0
            n_joinings_in_1000 = 0
            n_joinings_total = 0
            start_time = time.time()
            gc.collect()

            print("    iteration {}::::: processing {} paths ".format(iteration, len(Nodes_to_process)))
            for path in Nodes_to_process:
                # if len(path.parents) == 2:
                #     self.logger(f"path {path.Tuple} ignored")
                #     continue
                # gc.collect()
                news = []
                news_for = []
                news_parts = []
                path_count += 1
                # print(f"for path {path_count} : {path.Tuple}")
                for i in range( len(path.parents) - 1):
                    way1 = path.parents[i]
                    way2 = path.parents[i+1]
                    way = join_ways(way1, way2)
                    # print(f"  for joint parents {way}")
                    # if not way:
                    #     print("path {} parents {}".format(path.Tuple, dagnode_list_to_str(path.parents)))
                    #     raise Exception(f"ajab! {str(way1.Tuple)} and {str(way2.Tuple)} are not sequential!!!")
                    if way == path or way.OPTS[check_str]:
                        continue
                    way.OPTS[check_str] = True
                    paths_has_way = [path]
                    for other in Nodes_to_process:
                        # if way1.Tuple in other.OPTS["parents_dict"] and way2.Tuple in other.OPTS["parents_dict"]:
                        if way1 in other.parents and way2 in other.parents:
                            if other != path:
                                paths_has_way.append(other)
                    if len(paths_has_way) > 1:
                        news.append(way)
                        news_for.append(paths_has_way)
                        news_parts.append([way1, way2])
                j  = 0
                for i in range(len(news)):
                    way = news[i]
                    paths_contain_way = news_for[i]
                    way1 = news_parts[i][0]
                    way2 = news_parts[i][1]
                    for ch in paths_contain_way:
                        if ch == way:
                            continue
                        if way1 in ch.parents and way2 in ch.parents:
                            j += 1
                            idx = ch.parents.index(way1)
                            ch.parents = ch.parents[:idx] + [way] + ch.parents[idx+2:]
                            # way1.childs.remove(ch)
                            # way2.childs.remove(ch)
                            # if ch not in way.childs:
                                # way.childs.append(ch)
                            way.parents = [way1, way2]
                            # if way not in way1.childs:
                                # way1.childs.append(way)
                            # if way not in way2.childs:
                                # way2.childs.append(way)
                n_joinings_in_1000 += j
                n_joinings_total += j
                if path_count % 1000 == 0:
                    duration = elapsed_time(start_time)
                    print(f"      {path_count}/{len(Nodes_to_process)} nodes processed in {duration} seconds. {n_joinings_in_1000} joinings performed. total {n_joinings_total}")
                    start_time = time.time()
                    n_joinings_in_1000 = 0            
            if n_joinings_total == 0:
                has_benefit = False
        print("  joiner WHILE! end ----------------")
        print("  joiner creating childs ...")
        create_childs(self.logger)
        self.Dag_dict = self._create_dag_dict()
    def make_full_pathlist(self, options):
        t = time.time()
        start = time.time()
        root = ROOT
        for dnode in self.Paths:
            if dnode.is_an_edge():
                dnode.add_parent(root)
                continue
            Mid = int(len(dnode.Tuple)/2)
            half1_tup = dnode.Tuple[:Mid+1]
            half2_tup = dnode.Tuple[Mid:]
            half1 = nodes[half1_tup]
            half2 = nodes[half2_tup]
            dnode.parents = [half1, half2]
        duration = elapsed_time(t)
        self.logger(f" {self.make_method} parents of all paths has been chosen: {duration} secs.")
        self.logger(f" {self.make_method} creating childs ...")
        create_childs(self.logger)
        duration = elapsed_time(start_time=start)
        self.Dag_dict = self._create_dag_dict()
        t = time.time()
        if self.verify():
            duration = elapsed_time(t)
            print(f"  dag verified in {duration} seconds")
        else:
            raise Exception(f" Owh! dag NOT verified! make: {self.make_method}")
        self.logger(f" {self.make_method} done: {duration} secs")

    def _create_dag_dict(self):
        print("_create_dag_dict start")
        dag_as_dict_of_nodes = {}
        def add_1_dagnode(d:dagnode):
            is_root = d  == ROOT
            is_path = d.is_path
            is_edge = d.is_an_edge()
            is_mid = not is_root and len(d.childs) > 0
            rec_dict = {
                "Tuple" : d.Tuple,
                "is_root" : is_root,
                "is_edge" : is_edge,
                "is_path" : is_path,
                "is_mid" : is_mid,
                "is_mid_only" : is_mid and not is_path and not is_edge,
                "Parents" : [p.Tuple for p in d.parents], 
                "Childs" : [ch.Tuple for ch in d.childs]
            }
            dag_as_dict_of_nodes[d.Tuple] = rec_dict
        dag_explore_bfs(dag_root=ROOT, each_node_function=add_1_dagnode, report_each=100000)
        print("---- create_dag_dict end ----")
        return {
                    "dag" : dag_as_dict_of_nodes, 
                    "make_method" : self.make_method
                }
    def verify(self,):
        nodes_dict = self.Dag_dict["dag"]
        print("  Verify that all Paths are covered in dag:", end="")
        for path in self.Paths:
            if len(path.Tuple) == 1:
                continue
            if path.Tuple not in nodes_dict.keys():
                self.logger(f"FAILED! dag NOT VERIFIED: path {str(path.Tuple)} does not exist in dag!")
                return False
        print(" Done!")
        print("  Verify that each node of dag has correct parents:")
        for Tuple in nodes_dict.keys():
            d = nodes[Tuple]
            if d != ROOT :
                if not d.sort_and_verify_parents():
                    self.logger(f"dag NOT VERIFIED: node {str(d.Tuple)} parents are not correct: {dagnode_list_to_str(d.parents)}!")
                    return False
        return True
    def cost(self):
            nodes_dict = self.Dag_dict["dag"]
            cost = 0
            n_paths = 0
            n_mids = 0
            n_midonlys = 0
            for node in nodes_dict.values():
                if not node["is_edge"] and not node["is_root"]:
                    cost += len(node["Parents"]) - 1  
                if node["is_path"]:
                    n_paths += 1
                if node["is_mid"]:
                    n_mids += 1
                if node["is_mid_only"]:
                    n_midonlys += 1
            return (cost, n_mids, n_paths, n_midonlys) 
    def save(self, pkl_filename):
        Dict = self.Dag_dict
        save_as_pkl(Dict, pkl_filename)
        

