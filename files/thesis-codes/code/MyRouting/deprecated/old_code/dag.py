from utils import *
import time

from collections import defaultdict

nodes = {} # defaultdict(tuple)
e_base = 0  # Are paths stated by edges?

class dagnode:
    def __init__(self, Tuple, \
                is_edge = False, is_path = False, enable = False \
                , part_of = [] \
                , sublets_all = [] \
                , sublets_enable = []):
        if Tuple not in nodes.keys():
            self.is_edge = is_edge
            self.Tuple = Tuple
            self.is_path = is_path
            self.enable = enable
            self.sublets_all = [] 
            self.part_of = []
            self.sublets_enable = []
            union_lists(self.sublets_all, sublets_all)
            union_lists(self.sublets_enable, sublets_enable)
            union_lists(self.part_of, part_of)
            nodes[Tuple] = self
            
        else:
            nodes[Tuple].is_path = is_path or nodes[Tuple].is_path
            nodes[Tuple].is_edge = is_edge or nodes[Tuple].is_edge
            nodes[Tuple].enable = enable or nodes[Tuple].enable
            union_lists(nodes[Tuple].sublets_all, sublets_all)
            union_lists(nodes[Tuple].sublets_enable, sublets_enable)
            union_lists(nodes[Tuple].part_of, part_of)

    def _add_sublet(self, dnode):
        union_lists(self.sublets_all, [dnode])

    def _to_str(self):
        enable = "-"
        edg = " "
        pth = " "
        if self.enable:
            enable = "+"
        if self.is_edge:
            edg = "E"
        if self.is_path:
            pth = "P"
        return "{} {}{}, Subs {}({}), part_of {}\t{}".format(enable, pth, edg, len(self.sublets_all), len(self.sublets_enable), len(self.part_of), self.Tuple)
    def Print(self, prefix = "", part_of = False, subs_all = False, subs_enable = False):
        print( "{}{}".format(prefix, self._to_str()))
        if subs_all:
            j = 0
            for x in self.sublets_all:
                x.Print(prefix = "  ba {}) ".format(str(j)))
                j = j+1
        if subs_enable:
            j = 0
            for x in self.sublets_enable:
                x.Print(prefix = "  be {}) ".format(str(j)))
                j = j+1
        if part_of:
            j = 0
            for x in self.part_of:
                x.Print(prefix = "  pa {}) ".format(str(j)))
                j = j+1
    def impact(self):
        return 0 if self.enable else (len(self.part_of) * len(self.Tuple))
        # return 0 if self.enable else (len(self.part_of) )

def _sub_tuples(pathlet):
    maxl = len(pathlet)
    for L in reversed(range(2, maxl)):
        for i in range(maxl-L+1):
            sub = tuple(pathlet[i:i+L])
            yield sub
def _sublets(dnode):
    Part_of = [dnode]  if dnode.is_path else []
    for sub in _sub_tuples(dnode.Tuple):
        edg = len(sub) == 2 - e_base
        dagnode(sub, \
            is_edge = edg, \
            is_path = False, \
            enable = edg, \
            #An edge is always enable, else it would "or" with current value \  
            sublets_all = [], \
            part_of = Part_of, \
            sublets_enable = [], \
        ) 
        d = nodes[sub]
        yield d

def check_subs(target, enables):
    concat = subs[0]
    for sub in subs[1:]:
        if concat[-1] == sub[0]:
            concat += sub[1:]
        else:
            break

def min_subs_alg2(target, subs, current = None):
    def recursive(prefix, target, subs, visited):
        # print(prefix + "> target = {}, subs = {}".format(target, subs))
        l = len(target)
        if l <= 2:
            if l < 2:
                return 0, []
            elif not target in subs:
                raise Exception(prefix + "ERROR target {} subs {}".format(target, subs))
        elif target in subs:
            visited.append(target)
            # print(prefix + "RET 1")
            return 1, [target]
        non_visited = [sub for sub in subs if sub not in visited]
        non_visited.sort(key=len, reverse=True)
        best_score = 99999
        best_select = []
        if current:
            best_score = len(current)
            best_select = [x.Tuple for x in current]

        for Sub in non_visited:
            if len(Sub) < 3:
                continue
            # print(prefix + "# candid = {}".format(Sub))
            maxL = target[0:target.index(Sub[1])]
            maxR = target[target.index(Sub[-1]):]
            # print(prefix + "* maxL = {}, maxR = {}".format(maxL, maxR))
            maxLsubs = [sub for sub in subs if not sub in visited and all(x in maxL for x in sub)]
            maxRsubs = [sub for sub in subs if not sub in visited and all(x in maxR for x in sub)]
            newprefix = " " + prefix
            scoreL, selectL = recursive(newprefix , maxL, maxLsubs, [Sub])
            scoreR, selectR = recursive(newprefix , maxR, maxRsubs, [Sub])
            score = 1 + scoreL + scoreR
            select = selectL + [Sub] + selectR
            if score < best_score:
                best_score = score
                best_select = select
        return best_score, best_select

    _ , selected = recursive(" ", target, subs, [])
    ret = [nodes[s] for s in selected]
    return ret
def min_subs_alg3_DELETEME(target, subs):
    from itertools import compress, chain
    k = len(subs)
    targt = tuple(sorted(target))
    min_len = 99999
    best_selection = None
    for i in range(2**k):
        l = bin(i).count("1")
        if l > min_len or l < 2: 
            continue
        selection = [bool(i & (1<<n)) for n in range(k)]
        selecteds = list(compress(subs, selection))
        # selecteds = [subs[bool(i & (1<<n))] for n in range(k)]
        # l = len(selecteds)

        concat = selecteds[0]
        for sub in selecteds[1:]:
            if concat[-1] == sub[0]:
                concat += sub[1:]
            else:
                break

        if concat == target:
            if len(selecteds) < min_len:
                min_len = len(selecteds)
                best_selection = selecteds
    return [nodes[x] for x in best_selection]
def min_subs_alg4(target, subs, current = None):
    from itertools import compress, chain
    k = len(subs)
    targt = tuple(sorted(target))
    min_len = 99999
    best_selection = None
    if current:
        min_len = len(current)
        best_selection = [x.Tuple for x in current]
    for i in range(2**k):
        l = bin(i).count("1")
        if l > min_len or l < 2: 
            continue
        selection = [bool(i & (1<<n)) for n in range(k)]
        selecteds = list(compress(subs, selection))

        concat = selecteds[0]
        for sub in selecteds[1:]:
            if concat[-1] == sub[0]:
                concat += sub[1:]
            else:
                break

        if concat == target:
            if len(selecteds) < min_len:
                min_len = len(selecteds)
                best_selection = selecteds

        del(concat)
        del(selection)
        del(selecteds)
    if best_selection:
        # print(best_selection)
        return [nodes[x] for x in best_selection]
    else:
        return current
def appxmin_subs_alg1(target, subs, current = []):
    # print("target = {}\nsubs= {}".format(target, subs))
    def recursive(prefix, target, subs, visited):
        # print("{}target = {}\n{}subs= {}".format(prefix, target, prefix, subs))
        l = len(target)
        if l <= 2:
            if l < 2:
                return 0, []
            elif not target in subs:
                raise Exception(prefix + "ERROR target {} subs {}".format(target, subs))
        elif target in subs:
            visited.append(target)
            return 1, [target]
        if target in subs:
            visited.append(target)
            return 1, [target]
        # Sub = max(sub for sub in subs, key=len) 
        try:       
            Sub = max([sub for sub in subs if sub not in visited], key=len)        
        except:
            print(target)
            print(subs)
            return []
        maxL = target[0:target.index(Sub[1])]
        maxR = target[target.index(Sub[-1]):]
        # print(prefix + "* maxL = {}, maxR = {}".format(maxL, maxR))
        maxLsubs = [sub for sub in subs if not sub in visited and all(x in maxL for x in sub)]
        maxRsubs = [sub for sub in subs if not sub in visited and all(x in maxR for x in sub)]
        newprefix = " " + prefix
        # scoreL, selectL = recursive(newprefix , maxL, maxLsubs, [Sub])
        scoreL, selectL = recursive(newprefix , maxL, maxLsubs, [])
        # scoreR, selectR = recursive(newprefix , maxR, maxRsubs, [Sub])
        scoreR, selectR = recursive(newprefix , maxR, maxRsubs, [])
        score = 1 + scoreL + scoreR
        select =  selectL + [Sub] + selectR
        return score, select

    scor0 , select0 = recursive(" ", target, subs, [])
    if current:
        if len(select0) >= len(current):
            return current
    ret = [nodes[s] for s in select0]
    return ret
def update_statefull(dnode):
    # statefull: using min_subs_alg4 that tries to find sublets_enable better than current ones!
    # Good for single pathlet enabling
    enables = [sl.Tuple for sl in dnode.sublets_all if sl.enable ]
    selecteds = min_subs_alg4(dnode.Tuple, enables, dnode.sublets_enable)
    dnode.sublets_enable = selecteds
def update_statefull_approx(dnode):
    enables = [sl.Tuple for sl in dnode.sublets_all if sl.enable ]
    selecteds = appxmin_subs_alg1(dnode.Tuple, enables)
    dnode.sublets_enable = selecteds
def update_statefull_initapx(dnode):
    enables = [sl.Tuple for sl in dnode.sublets_all if sl.enable ]
    selecteds = appxmin_subs_alg1(dnode.Tuple, enables)
    dnode.sublets_enable = selecteds
    selecteds = min_subs_alg2(dnode.Tuple, enables, dnode.sublets_enable)
    dnode.sublets_enable = selecteds
    
def update_stateless(dnode):
    # stateless: Tries to find sublets_enable, ignoring current ones!
    # Good for randim gen enabling
    enables = [sl.Tuple for sl in dnode.sublets_all if sl.enable ]
    start_time = time.time()
    selecteds = min_subs_alg4(dnode.Tuple, enables)
    print("min_subs_alg4 ({}, {}) : {} seconds".format(len(dnode.Tuple), len(enables),round((time.time() - start_time),2)))
    dnode.sublets_enable = selecteds
    return len(selecteds)
updater = None

class dag:
    Edges = [] # Single edges used
    Pathlets = []  # Multi-edge pathlets that are part of other path (Maybe it is also a path)
    Paths = []
    gens = defaultdict(int) # Key: gen tuple, Value: gen score
    def __init__(self, pathlist_file_to_import = None):
        if pathlist_file_to_import:
            print("loading {} ".format(pathlist_file_to_import), end="")
            self.Paths_dict = load_pkl_json(pathlist_file_to_import)
            # print("  done")
            for src in self.Paths_dict:
                print("  load paths from {} ... ".format(src), end="")
                for dst in self.Paths_dict[src]:
                    for path in self.Paths_dict[src][dst]:
                        Tuple = tuple(path)
                        dnode = dagnode(Tuple, is_path=True, enable=False)
                        nodes[Tuple] = dnode
                        self.Paths.append(dnode)
                print("    done")
            sample = self.Paths[-1].Tuple[-1]
            print("sorting paths ... ", end="")
            self.sortpaths()
            print("  done")
            if str(sample).__contains__("-"):
                e_base = 1
            else:
                e_base = 0
        else:
            self.Paths = []
            self.Edges = []
            self.Pathlets = []

    def sortedpathlets(self):
        # sortkey = lambda x: len(x.Tuple)
        # self.Pathlets = sorted(self.Pathlets, key=sortkey)
        # keys = lambda x: (x.enable, len(x.part_of) * len(x.Tuple) )
        # self.Pathl/ets.sort(key=keys, reverse=True)
        return sorted(self.Pathlets, key=lambda pl: pl.impact(), reverse=True)

    def sortpaths(self):
        sortkey = lambda x: len(x.Tuple)
        self.Paths = sorted(self.Paths, key=sortkey)
    def _make1(self):
        c = 0
        pno = len(self.Paths)
        for pnode in self.Paths:
            subs = []
            for d in _sublets(pnode):
                subs.append(d)
                if d.is_edge:
                    self.Edges.append(d)
                    pnode.sublets_enable.append(d)
                else:
                    self.Pathlets.append(d)
            pnode.sublets_all = subs
            c= c+1
            if c % 100 == 0:
                print("Path {}/{} done".format(c, pno))
        print("Path {}/{} done".format(c, pno))

        self.Edges = list(set(self.Edges))
        self.Pathlets = list(set(self.Pathlets))
        self.Pathlets.sort(key = lambda pl: (len(pl.Tuple), pl.Tuple))
    def _remove_1time_pathlets(self):
        remove_list = []
        c1 = len(self.Pathlets)
        for pl in self.Pathlets:
            if len(pl.part_of) < 2:
                remove_list.append(pl)
        self.Pathlets = [pl for pl in self.Pathlets if not pl in remove_list]
        c2 = len(self.Pathlets)
        print("One-time pathlets removed ({} -> {})".format(c1, c2))
    def _make2(self):
        c = 0
        pno = len(self.Pathlets)
        for node in self.Pathlets:
            node.sublets_all = [d for d in _sublets(node)]
            c= c+1
            if c % 100 == 0:
                print("Pathlet {}/{} done".format(c, pno))
        print("Pathlet {}/{} done".format(c, pno))
    def make(self):

        print("***\t1. Paths' sublets")
        start_time = time.time()
        self._make1()
        print("+++ _make1 : {} seconds, {} Paths, {} Pathlets, {} Edges ".format(round((time.time() - start_time),2), len(self.Paths), len(self.Pathlets), len(self.Edges) ))

        print("***\t2. Remove non-common pathlets")
        start_time = time.time()
        self._remove_1time_pathlets()
        print("+++ _remove_1time_pathlets : {} seconds ".format(round((time.time() - start_time),2)))

        print("***\t3. Pathlets' sublets")
        start_time = time.time()
        self._make2()
        print("+++ _make2 : {} seconds ".format(round((time.time() - start_time),2)))
    
    def _change_pl(self, pathlet, set_true):
        def err():
            print("Wrong input. Enter pathlet's dagnode OR tuple OR index b.w {}, {}".format(0, len(self.Pathlets)))
            return
        pl = None
        if isinstance(pathlet, dagnode):
            if pathlet in self.Pathlets:
                pl = pathlet
            else:
                err()
        if type(pathlet) == tuple:
            if nodes[pathlet] in self.Pathlets:
                pl = nodes[pathlet]
            else:
                err()
        elif type(pathlet) == int:
            if  0 <= pathlet < len(self.Pathlets):
                pl = self.Pathlets[pathlet]
            else:
                err()

        # s0 = self.score() * 1.0
        start_time = time.time()
        counter = 0
        pl.enable = set_true
        if set_true:
            updater(pl)
            counter += 1
        elif not pl.is_path:
            pl.sublets_enable = []
        for path in pl.part_of:
            updater(path)
            counter += 1
        # print("  > enablepl : {} seconds ({} * {}) ".format(round((time.time() - start_time),2), counter, updater.__name__))
        # s1 = self.score() * 1.0

        # action = "Enable" if set_true else "Disable"
        # msg = "{} {}\n{}".format(action, pl.Tuple, change_pcnt("Score", s0, s1))
        # print(msg)
        return #s1 - s0
    def _reset_node(self, pathlet, is_path):
        p = None
        plist = self.Paths if is_path else self.Pathlets
        def err():
            print("Wrong input. Enter dagnode OR tuple OR index b.w {}, {}".format(0, len(plist)))
            return
        if type(pathlet) == tuple:
            if nodes[pathlet] in plist:
                p = nodes[pathlet]
            else:
                err()
        elif type(pathlet) == int:
            if  0 <= pathlet < len(plist):
                p = plist[pathlet]
            else:
                err()
        elif type(pathlet) == dagnode:
            if pathlet in plist:
                p = pathlet
            else:
                err()
        s0 = self.score() * 1.0
        p.sublets_enable = [s for s in p.sublets_all if s.is_edge]
        s1 = self.score() * 1.0
        msg = "Reseting {}\n{}".format(p.Tuple, change_pcnt("Score", s0, s1))
        print(msg)

    def enablepl(self, pathlet):
        if not updater:
            raise Exception("Error: updater is None")
            return
        return self._change_pl(pathlet, True)
    def disablepl(self, pathlet):
        if not updater:
            raise Exception("Error: updater is None")
            return
        return self._change_pl(pathlet, False)
    def resetpath(self, path = -1):
        self._reset_node(self, path, True)
    def resetpathlet(self, pathlet = -1):
        self._reset_node(self, pathlet, False)

    def score(self):
        used1 = 1.0 * sum(len(node.sublets_enable) for node in nodes.values() if node.enable or node.is_path)
        return used1
        
    def run(self, diff_wanted = 0, save_at = -1, clean_at = 500, upd_func = None):
        global updater
        updater =  upd_func if upd_func else update_statefull_approx
        pls = self.sortedpathlets()
        sumdiff = 0
        wanted = -1 * diff_wanted if diff_wanted else -1 * self.score()
        save_threshold = save_at if save_at > 0 else 99999
        start_time = time.time()
        save_counter = -save_threshold
        count = 0
        score0 = self.score()
        for candidate_pl in pls:
            if candidate_pl.enable:
                print("No more improvement is possible")
                return 
            diff = self.enablepl(candidate_pl)
            score1 = self.score()
            diff = score1 - score0
            print("{} > {} ({}): ENABLE {}".format(score0, score1, diff, candidate_pl.Tuple))            
            score0 = score1
            sumdiff += diff
            if diff > 0:
                self.disablepl(candidate_pl)
                score1 = self.score()
                diff = score1 - score0
                print("{} > {} ({}): DISABLE {}".format(score0, score1, diff, candidate_pl.Tuple))            
                score0 = score1

            count += 1
            if count == clean_at:
                self.clean()
                score1 = self.score()
                count = 0
            if sumdiff <= save_counter:
                print("Saving ...")
                self.save()
                save_counter -= save_threshold
            if sumdiff <= wanted:
                break
        print("RUN : {}sec ({})----------".format(round((time.time() - start_time),2), updater.__name__))
    def run2(self, diff_wanted = 0, save_at = -1, clean_at = 500):
        self.run(diff_wanted = diff_wanted, save_at = save_at, \
            clean_at = clean_at, upd_func = update_statefull_initapx)

    def go(self, niters): 
        # Choose a random enable map, If it is better, keep it, else, ignore it!
        global updater
        updater = update_statefull_approx
        l = len(self.Pathlets)
        score0 = self.score()
        map0 = tuple([x.enable for x in self.Pathlets])
        gen0 = bools2bits(map0)
        self.gens[gen0] = score0
        # main loop ........................................................
        for itr in range(niters):
            start_time = time.time()
            gen1 = random.getrandbits(l)
            map1 = bits2bools(gen1, l)
            for i in range(l):
                self.Pathlets[i].enable = map1[i]
            j = 0
            pl_en = [x for x in self.Pathlets if x.enable]
            for pathlet in pl_en:
                if pathlet.enable:
                    updater(pathlet)
                    j += 1
                    # print("Pathlet {}/{},\t{}".format(j,len(pl_en), updater.__name__))
            j = 0
            paths = [p for p in self.Paths if not p.is_edge]
            for path in paths:
                updater(path)
                j += 1
                # print("Path {}/{},\t{}".format(j,len(self.Paths), updater.__name__))

            score1 = self.score()
            self.gens[map1] = score1
            print("Iter {} ({} secs) score {} ".format(itr, round((time.time() - start_time),2), score1))
        print("__________________best: {}______________________".format(min(self.gens.values())))

    def clean(self):
        '''Disables unused pathlets, makes score() == validate().
        Because, run() may change sublets_enable of paths, so, leave some previously 
        enabled pathlets unused!
        Thus, the result of score() will be more than real score!'''
        print("Cleaning ...")
        Q = [p for p in self.Paths]
        v = defaultdict(bool)
        if len(Q) == 0:
            return 0
        score = 0
        i = 0
        while i < len(Q):
            n = Q[i]
            se = n.sublets_enable
            if not v[n.Tuple]:
                v[n.Tuple] = True
                score += len(se)
            Q = Q + se
            i += 1
        diff = []
        for n in nodes.values():
            if n.enable and n.Tuple not in v:
                diff.append(n)
        for n in diff:
            n.enable = False
    def validate(self):
        validated = True
        Q = [p for p in self.Paths]
        visited = []
        score = 0
        # input("len(Q) = {}".format(len(Q)))
        i = -1
        while i < len(Q) -1:
            i += 1
            test = Q[i]
            subs = [s.Tuple for s in test.sublets_enable]
            if test.Tuple not in visited:
                visited.append(test.Tuple)
                score += len(subs)
            # print("i = {},{} // {}".format(i, test.Tuple, subs))
            if len(test.Tuple) in (1, 2):
                if len(subs) == 0:
                    # print("z OK {} ---> {}".format(test.Tuple, subs))
                    continue
                else:
                    print("zero violation {} -/-> {}".format(test.Tuple, subs))
                    validated = False
                    return validated, -1

            for s in test.sublets_enable:
                Q.append(s)
            try:
                concat = subs[0]
                for sub in subs[1:]:
                    if concat[-1] == sub[0]:
                        concat += sub[1:]
                    else:
                        break
            except Exception as e:
                print("ERR {} // {} >> {}".format(test.Tuple, subs, str(e)))
            if concat != test.Tuple:
                print("violation {} -/-> {}".format(test.Tuple, subs))
                validated = False
                return validated, -1
            # else:
                # print("OK {} ---> {}".format(test.Tuple, subs))
        # for n in nodes.values():
        #     viol = []
        #     viol2 = []
        #     if n.enable and n.Tuple not in visited:
        #         n.Print()
        #         viol.append(n)
        #         for m in nodes.values():
        #             if 
        return validated, score
    def validate2(self):
        validated = True
        Q = [p for p in self.Paths]
        visited = []
        score = 0
        # input("len(Q) = {}".format(len(Q)))
        i = -1
        while len(Q) > 0:
            i += 1
            test = Q.pop(0)
            subs = [s.Tuple for s in test.sublets_enable]
            if test.Tuple not in visited:
                visited.append(test.Tuple)
                score += len(subs)
            # print("i = {},{} // {}".format(i, test.Tuple, subs))
            if len(test.Tuple) in (1, 2):
                if len(subs) == 0:
                    # print("z OK {} ---> {}".format(test.Tuple, subs))
                    continue
                else:
                    print("zero violation {} -/-> {}".format(test.Tuple, subs))
                    validated = False
                    return validated, -1

            for s in test.sublets_enable:
                Q.append(s)
            try:
                concat = subs[0]
                for sub in subs[1:]:
                    if concat[-1] == sub[0]:
                        concat += sub[1:]
                    else:
                        break
            except Exception as e:
                print("ERR {} // {} >> {}".format(test.Tuple, subs, str(e)))
            if concat != test.Tuple:
                print("violation {} -/-> {}".format(test.Tuple, subs))
                validated = False
                return validated, -1
            # else:
                # print("OK {} ---> {}".format(test.Tuple, subs))
        # for n in nodes.values():
        #     viol = []
        #     viol2 = []
        #     if n.enable and n.Tuple not in visited:
        #         n.Print()
        #         viol.append(n)
        #         for m in nodes.values():
        #             if 
        return validated, score
    def save(self, name = "dag"):
        def dagnode_to_dict(dnode):
            outobj = defaultdict(str)
            outobj['Tuple'] = dnode.Tuple
            outobj['is_edge'] = dnode.is_edge
            outobj['is_path'] = dnode.is_path
            outobj['enable'] = dnode.enable
            outobj['part_of'] = [s.Tuple for s in dnode.part_of]
            outobj['sublets_all'] = [s.Tuple for s in dnode.sublets_all]
            outobj['sublets_enable'] = [s.Tuple for s in dnode.sublets_enable]
            return outobj
        edges = [dagnode_to_dict(n) for n in self.Edges]
        paths = [dagnode_to_dict(n) for n in self.Paths]
        pathlets = [dagnode_to_dict(n) for n in self.Pathlets]
        obj = {
            'edges'     : edges,
            'paths'     : paths,
            'pathlets'  : pathlets
        }
        output = addr_as_dag_pkl(name)
        save_as_pkl(obj, output)

    def print_pnode(self, pnode_idx = -1, part_of = True, subs_all = True, subs_enable = True):
        if pnode_idx > len(self.Paths) -1 or pnode_idx == -1 :
            print ("Enter index between 0, {}".format(len(self.Paths) -1))
            return
        pn = self.Paths[pnode_idx]
        pn.Print("", part_of, subs_all, subs_enable)
    def export(self, outputfile = "Output"):
        self.clean()
        print("Adding nodes ...")
        used = []
        for edg in self.Edges:
            used.append(edg)
        for pl in self.Pathlets:
            if pl.enable and not pl.is_path:
                used.append(pl)
        for p in self.Paths:
            used.append(p)
        L = len(used)
        print("Extract tuples ...")
        tuples = [n.Tuple for n in used]
        def tuple2idx(tupl):
            return tuples.index(tupl)
        def subs2idxs(subs):
            return tuple([tuple2idx(sub.Tuple) for sub in subs])
        parents = [subs2idxs(n.sublets_enable) for n in used]
        output = [] # list of (idx, tuple, (subs))        
        for i in range(L):
            output.append((i, tuples[i], parents[i]))
        fname = addr_as_dag_json(outputfile)
        save_as_pkl(output, fname)
        print("Done!")

def load(name = "dag"):
    start_time = time.time()
    #1
    print("Loading ...")
    Input = addr_as_dag_pkl(name)
    obj = load_pkl_json(Input)
    #2
    print("Init nodes ...")
    _edges = obj['edges'] 
    edges = []
    _paths = obj['paths'] 
    paths = []
    _pathlets = obj['pathlets']
    pathlets = []
    for _node in _edges:
        dagnode(_node['Tuple'], is_edge=_node['is_edge'], is_path=_node['is_path'], enable=_node['enable'])
        edges.append(nodes[_node['Tuple']])
    print("edges ok")
    for _node in _paths:
        dagnode(_node['Tuple'], is_edge=_node['is_edge'], is_path=_node['is_path'], enable=_node['enable'])
        paths.append(nodes[_node['Tuple']])
    print("paths ok")
    for _node in _pathlets:
        dagnode(_node['Tuple'], is_edge=_node['is_edge'], is_path=_node['is_path'], enable=_node['enable'])
        pathlets.append(nodes[_node['Tuple']])
    print("pathlets ok")
    #3
    print("Extracting sublets_* & part_of ...")
    for _node in _edges:
        node = nodes[_node['Tuple']]
        for tup in _node['part_of']:
            node.part_of.append(nodes[tup])
    print("edges ok")
    n = None
    for _node in _paths:
        node = nodes[_node['Tuple']]
        for tup in _node['part_of']:
            try:
                n = nodes[tup]
            except:
                dagnode(tup)
                n = nodes[tup]
            node.part_of.append(n)
        for tup in _node['sublets_all']:
            try:
                n = nodes[tup]
            except:
                dagnode(tup)
                n = nodes[tup]
            node.sublets_all.append(n)
        for tup in _node['sublets_enable']:
            try:
                n = nodes[tup]
            except:
                dagnode(tup)
                n = nodes[tup]
            node.sublets_enable.append(n)
    print("paths ok")
    for _node in _pathlets:
        node = nodes[_node['Tuple']]
        if node.is_path:
            continue
        for tup in _node['part_of']:
            try:
                n = nodes[tup]
            except:
                dagnode(tup)
                n = nodes[tup]
            node.part_of.append(n)
        for tup in _node['sublets_all']:
            try:
                n = nodes[tup]
            except:
                dagnode(tup)
                n = nodes[tup]
            node.sublets_all.append(n)
        for tup in _node['sublets_enable']:
            try:
                n = nodes[tup]
            except:
                dagnode(tup)
                n = nodes[tup]
            node.sublets_enable.append(n)
    print("pathlets ok")
    #4
    d = dag()
    d.Edges = edges
    d.Pathlets = pathlets
    d.Paths = paths
    print("  load_dag : {} seconds, {} Paths, {} Pathlets, {} Edges ".format(round((time.time() - start_time),2), len(d.Paths), len(d.Pathlets), len(d.Edges) ))
    return d
def load_output(outputfile = "Output"):
    fname = addr_as_dag_pkl(outputfile)
    out  = load_pkl_json(fname)
    for o in out:
        print("{}. {} = {}".format(o[0], o[1], o[2]))
    print("Total connections = {}".format(sum(len(o[2]) for o in out)))
    return out
def example():
    str='''
    # DIR = addr_as_json(TOPOLOGY+"_pathlist") #ghalat
    DIR = os.path.join(dataset_pkl_dir(), DATASET+"_pathlist.json")
    d = dag(DIR)
    d.make()
    d=load()
    d=load('temp')
    d.validate()
    # d.run()
    # d.run(2000, save_at = 100)
    # pls = d.sortedpathlets()
    # d.sortpaths()
    # d.resetpath(930)
    # d.enablepl((4, 5, 6))
    # d.enablepl(2)
    Example 1:
    d=load('2582-5990')
    d.export()
    o = load_output()
    '''
    print(str.replace("    ",""))
example()
print("\nexample()")

def load_dag_DELETEME(name = "dag"):
    # nodes
    start_time = time.time()
    print("Loading ...")
    Input = addr_as_dag_pkl(name)
    obj = load_pkl_json(Input)

    _edges = obj['edges'] 
    _paths = obj['paths'] 
    _pathlets = obj['pathlets']
    print("Extracting ...")
    edges = [dict_to_dagnode_DELETEME(x) for x in _edges]
    print("Edges done! ...")
    paths = [dict_to_dagnode_DELETEME(x) for x in _paths]
    print("Paths done! ...")
    pathlets = [dict_to_dagnode_DELETEME(x) for x in _pathlets]
    print("Pathlets done! ...")
    d = dag()
    d.Edges = edges
    d.Pathlets = pathlets
    d.Paths = paths
    print("  load_dag : {} seconds, {} Paths, {} Pathlets, {} Edges ".format(round((time.time() - start_time),2), len(d.Paths), len(d.Pathlets), len(d.Edges) ))
    return d

