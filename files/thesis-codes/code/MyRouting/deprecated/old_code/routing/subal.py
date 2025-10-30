from routing.base import base_routing as BaseRouting
from Network import Path, Network
from allpaths_w import Graph, ijPaths
from utils import dataset_pkl_dir, pathlist_export, id_list_to_switch_list
import os

class ijGrouppedPaths:
    def __init__(self, ijpaths: ijPaths, net: Network, overlap):
        self.net = net
        self.Overlap = overlap
        self.topo = self.net.topology
        self.Switches = self.net.topology.Switches
        self.counter = 0
        self.cur_group = 0
        self.ijpaths = ijpaths
        self.src = ijpaths.src
        self.dst = ijpaths.dst
        # self.paths_all = [ id_list_to_switch_list(p, self.Switches) for p in self.ijpaths.Paths ]
        self.paths_all = [ Path(self.net, id_list_to_switch_list(p, self.Switches)) for p in self.ijpaths.Paths ]
        self.n_paths=len(self.paths_all)
        self.groups = []
        self.groups.append( [ self.paths_all[0] ] )
        for i in range(1, self.n_paths):
            #OVERLAPPING
            # last_path = self.groups[-1][-1]
            last_path = self.groups[-1][0]

            last_w = last_path.weight
            next_path = self.paths_all[i]
            next_w = next_path.weight
            
            #OVERLAPPING
            overlap_factor = (1.0 + self.Overlap)
            # if last_w == next_w:
            #     self.groups[-1].append(next_path)
            # elif last_w < next_w:
            #     self.groups.append( [next_path] )
            # else:
            #     print("*-*-* last_path {}, last_w {}, next_path {}, next_w {}".format(last_path.sids, last_w, next_path.sids, next_w))
            #     raise Exception("myError in Groupped_ijPaths --> Not sorted ijPaths")
            if next_w <= last_w * overlap_factor:
                self.groups[-1].append(next_path)
            else:
                self.groups.append( [next_path] )
    
    def Next_path(self):
        self.counter += 1
        # idx = self.counter
        # G = self.groups[self.cur_group]

        while True:
            if self.cur_group == len(self.groups):
                # print(" XXX Rejected: {} > {}".format(self.src, self.dst))
                return None
            else:
                G = self.groups[self.cur_group]
                group_len = len(G)
                for i in range(group_len):
                    idx = self.counter % group_len 
                    path = G[idx]
                    candid = "G{} r{}: {}".format(self.cur_group, idx, path.sids)
                    # path = Path(self.net, p)
                    if not path.is_saturated():
                        # print("SELected: " + candid)
                        return path
                    else:
                        # print("- Skipped: " + candid)
                        self.counter += 1

                self.cur_group += 1
        # return None

class Subal(BaseRouting):
    def __init__(self, network, acep = 1.0, aps = 999.0, overlap = 0.0, *args, **kwargs):
        super(Subal, self).__init__(network)
        # self.counter = 0
        self.current = 0
        self.topo = self.net.topology
        self.sid_path_weight = self.topo.sid_path_weight
        self.V = self.net.topology.V
        
        # Usage: 
        # pathlist=self.PathGroups[src_id][dst_id][0]
        # path=self.choose
        
        self.graph = Graph(self.net.topology)
        # self.PATHs = self.graph._PATHs
        self.acep = acep
        self.aps = aps
        self.overlap = overlap
        self.pstr = self.graph._param_to_str(self.acep, self.aps)
        print("Subal init: acep = {}, aps = {}, net.topo = {}".format(self.acep, self.aps, self.graph.dataset))
        sources = [s.id for s in self.net.topology.Switches.values()]
        # print(sources)
        self.pathlist = self.graph.get_paths_from_to(self.acep, self.aps, sources)
        # pathlist_stats(pathlist, verbosity = 2)
        DIR = os.path.join(dataset_pkl_dir(), self.net.topology.name+"_pathlist.json")
        pathlist_export(self.pathlist, DIR, e = False, as_json = True)
        self.PATHs = self.graph._PATHs[self.pstr]
        # self.PathGroups = [[None] * self.V] * self.V
        # for i in range(self.V):
        #     for j in range(self.V):
        #         self.PathGroups[i][j] = ijGrouppedPaths(self.PATHs[i][j])
        self.GPATHs = [[ijGrouppedPaths(ijpaths, self.net, self.overlap) for ijpaths in row] for row in self.PATHs] 


    def show_paths(self, src_id, dst_id):
        gij_paths = self.GPATHs[src_id][dst_id]
        ng = len(gij_paths.groups)
        for i in range(ng):
            group = gij_paths.groups[i]
            glen = len(group)
            for j in range(glen):
                # path = Path(self.net, gij_paths.groups[i][j])
                path = gij_paths.groups[i][j]
                print("g{} r{} {}".format(i, j, path.sids))
                # path.show_oneline()
            
    def route(self, src_id, dst_id):
        # print("Routing of SUBAL {} > {}".format(src_id, dst_id))
        # self.counter += 1
        # self.show_paths(src_id, dst_id)
        path = self.GPATHs[src_id][dst_id].Next_path()
        return path
        # if path:
        #     return Path(self.net, path)
        # else:
        #     return None

