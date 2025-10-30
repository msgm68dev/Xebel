from utils import *
import time

from collections import defaultdict

nodes = {} # defaultdict(tuple)
e_base = 0  # Are paths stated by edges?

class dagnode:
    def __init__(self, Tuple, \
                is_edge = False, is_path = False \
                , target = False, added = False \
                , part_of = [] \
                , childs = [] \
                , parents = []):
        self.gain = -1000
        if Tuple not in nodes.keys():
            self.is_edge = is_edge
            self.Tuple = Tuple
            self.is_path = is_path
            self.target = target
            self.added = added
            self.part_of = []
            self.childs = [] 
            self.parents = []
            union_lists(self.part_of, part_of)
            union_lists(self.childs, childs)
            union_lists(self.parents, parents)
            nodes[Tuple] = self
            
        else:
            nodes[Tuple].is_path = is_path or nodes[Tuple].is_path
            nodes[Tuple].is_edge = is_edge or nodes[Tuple].is_edge
            nodes[Tuple].target = target or nodes[Tuple].target
            nodes[Tuple].added = added or nodes[Tuple].added
            union_lists(nodes[Tuple].part_of, part_of)
            union_lists(nodes[Tuple].childs, childs)
            union_lists(nodes[Tuple].parents, parents)
    def update_gain(self):
        l = len(self.Tuple)
        n = len([d for d in self.part_of if not d.added])
        self.gain = (l*n) - (l+n)
def _sub_tuples(pathlet_tuple: tuple):
    maxl = len(pathlet_tuple)
    for L in reversed(range(2, maxl)):
        for i in range(maxl-L+1):
            sub = tuple(pathlet_tuple[i:i+L])
            yield sub
def get_all_subways_of(dnode: dagnode):
    Part_of = [dnode]  if dnode.is_path else []
    for sub in _sub_tuples(dnode.Tuple):
        edg = len(sub) == (2 - e_base)
        dagnode(sub, \
            is_edge = edg, \
            part_of = Part_of
        ) 
        d = nodes[sub]
        yield d
def disjoint_ways(way1: tuple, way2: tuple):
    for i in range(len(way1)-1):
        step1 = (way1[i], way1[i+1])
        for j in range(len(way2)-1):
            step2 = (way2[j], way2[j+1])
            if step1 == step2:
                return False
    return True
def _get_rest_of_tuple(super: tuple, sub:tuple):
    # Note: we sure that sub exists in super!
    if len(super) < len(sub):
        raise Exception("super bayad bozorgtar az sub bashe!")
    if len(sub) == 0:
        return super, None
    if len(super) == len(sub):
        return None, None
    SUP = len(super)
    left_end_idx = 0
    right_begin_idx = SUP-1
    while left_end_idx < len(super):
        if super[left_end_idx] != sub[0]:
            left_end_idx += 1
        else:
             break
    while right_begin_idx > 0:
        if super[right_begin_idx] != sub[-1]:
            right_begin_idx -= 1 
        else:
            break
    left = super[0:left_end_idx +1 ] if left_end_idx > 0 else None
    right = super[right_begin_idx:] if right_begin_idx < SUP-1 else None
    return left , right
def _get_left_right_dnodes(super_way: dagnode, sub_way: dagnode):
    left, right = _get_rest_of_tuple(super_way.Tuple, sub_way.Tuple)
    left_dnode = nodes[left]
    right_dnode = nodes[right]
    return left_dnode, right_dnode
class dag:
    def __init__(self, pathlist_file_to_import = None):
        self.Edges = [] # Single edges used
        self.Pathlets = []  # Multi-edge pathlets that are part of other path (Maybe it is also a path)
        self.Paths = []
        self.gens = defaultdict(int) # Key: gen tuple, Value: gen score
        if pathlist_file_to_import:
            print("loading {} ".format(pathlist_file_to_import), end="")
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
            print("sorting paths ... ", end="")
            self._sortpaths()
            print("  done")
            if str(sample).__contains__("-"):
                e_base = 1
            else:
                e_base = 0
    def _sortpaths(self):
        # From Shortest to longest paths
        sortkey = lambda x: len(x.Tuple)
        self.Paths = sorted(self.Paths, key=sortkey)
    def _sort_pathlets_by_gain(self):
        for pl in self.Pathlets:
            pl.update_gain()
        sortkey = lambda x: x.gain
        # Most gain first
        self.Pathlets = sorted(self.Pathlets, key=sortkey, reverse = True)
    def _make_all_pathlets(self):
        report_each = 500
        c = 0
        pno = len(self.Paths)
        for dnode in self.Paths:
            subs = []
            for d in get_all_subways_of(dnode):
                subs.append(d)
                if d.is_edge:
                    self.Edges.append(d)
                else:
                    self.Pathlets.append(d)
            c= c+1
            if c % report_each == 0:
                print("\tPath {}/{} processed".format(c, pno))
        print("\tAll {} Paths  processed".format(c))
        self.Edges = list(set(self.Edges))
        self.Pathlets = list(set(self.Pathlets))
        print( "\tSorting {} pathlets by length ...".format(len(self.Pathlets)))
        self.Pathlets.sort(key = lambda pl: (len(pl.Tuple), pl.Tuple))
        print( "\t\tdone")

    def make(self):
        targets = []
        addeds = []
        # ========== Mark all final Paths as target =================
        for dnode in self.Paths:
            targets.append[dnode]
            dnode.target = True
        # ========== Calculate all partial paths (Pathlets) =========
        start_time = time.time()
        self._make_all_pathlets()
        print("+++ _make_all_pathlets : {} seconds, {} Paths, {} Pathlets, {} Edges ".format(round((time.time() - start_time),2), len(self.Paths), len(self.Pathlets), len(self.Edges) ))
        # ========== Core functions =================================
        def _accept_pathlet(candidate: dagnode):
            candidate.added = True
            addeds.append(candidate)
            targets.remove(candidate)
            if not candidate.is_path:
                self.Pathlets.remove(candidate)
            for child in candidate.part_of:
                candidate.childs.append(child)
                child.parents.append(candidate)
                if not child.added:
                    child.added = True
                    addeds.append(child)
                    targets.remove(child)
                    left_dnode, right_dnode = _get_left_right_dnodes(super_way=child, sub_way=candidate)
                    targets.append(left_dnode)
                    targets.append(right_dnode)
                    self.Pathlets.remove(left_dnode)
                    self.Pathlets.remove(right_dnode)
                    for d in get_all_subways_of(left_dnode):
                        pass
                    for d in get_all_subways_of(right_dnode):
                        pass
        # ========== Main while =====================================
        while len(targets) > 0:
            selected_pls = []
            self._sort_pathlets_by_gain()
            for i in range(len(self.Pathlets)):
                candidate = self.Pathlets[i]
                if candidate.gain <= 0:
                    self.Pathlets.remove(candidate)
                else:
                    disjoint = True
                    for pl in selected_pls:
                        if not disjoint_ways(candidate.Tuple, pl.Tuple):
                            disjoint = False
                            break
                    if disjoint:
                        selected_pls.append(pl)
            for pl in selected_pls:
                _accept_pathlet(pl)






        # print("***\t1. Paths' sublets")
        # self._make1()

        # print("***\t2. Remove non-common pathlets")
        # start_time = time.time()
        # self._remove_1time_pathlets()
        # print("+++ _remove_1time_pathlets : {} seconds ".format(round((time.time() - start_time),2)))

        # print("***\t3. Pathlets' sublets")
        # start_time = time.time()
        # self._make2()
        # print("+++ _make2 : {} seconds ".format(round((time.time() - start_time),2)))
    