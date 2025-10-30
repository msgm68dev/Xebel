from utils import file_to_table, apply_function_on_file_content
import os

MAX_CAPACITY = 800000000000 # 100 Gbps
DEFAULT_W = 1

class Switch:
    def __init__(self, id):
        # self.id = len(Switches)
        # self.name = name #if name != '' else "s" + str(self.id)
        self.id = id
        self.links_out = []
        self.links_in = []
        self.OPTS = {} # A dictionary in which you can add any more properties in the future!
        self.OPTS['enabled'] = True
        # Set distance to infinity for all nodes
        # self.OPTS['distance'] = sys.maxint
        # Mark all nodes unvisited        
        # self.OPTS['visited'] = False
        # Predecessor
        # self.OPTS['previous'] = None

    def show_out(self, prefix=' '):
        for l_out in self.links_out:
            print("{}{} --> {} W={} C={}".format(prefix, self.id, l_out.To.id, l_out.weight, l_out.capacity))
            # print(prefix + str(self.id) + " --> " + str(l_out.To.id))
    def show_in(self, prefix=' '):
        for l_in in self.links_in:
            print(prefix + str(l_in.From.id) + " --> " + str(self.id))

class Link:
    def __init__(self, frm_switch, to_switch, capacity=MAX_CAPACITY, weight=1):
        self.id = (frm_switch.id, to_switch.id)
        self.From = frm_switch 
        self.To = to_switch
        # self.name = name #if name != '' else "e"+str(self.id)
        self.weight = weight
        self.capacity = capacity
        self.OPTS = {}
        self.OPTS['up'] = True
        self.OPTS['saturated'] = False
        self.OPTS['free'] = capacity
    def show(self, prefix=''):
        print("{}l{} : W={}, C={} Free={}".format(prefix, self.id, self.weight, self.capacity, self.OPTS['free']))
    def decrease_free(self, value):
        self.OPTS['free'] -= value
    def check_saturation(self):
        if self.OPTS['free'] <= 0:
            self.OPTS['saturated'] = True
    # def __lt__(self, other):
    #     return self.OPTS['delay'] < other.OPTS['delay']
class Topology:
    switches_changed = False
    links_changed = False
    def __init__(self, topology_file = None, name = None, first_node_id = 0, prints = False):
        if not topology_file:
            self.Switches = {} # Key = Switch_ID: 0, 1, 2, ... | Value = Switch object
            self.Links = {}     # Key = Link_ID: (0, 1), (1, 4), (4, 1), ... | Value = Link object
            self.V = len(self.Switches)
            self.E = len(self.Links)
            self.W = []
            self.OPTS = {}
        else:
            if prints:
                print(f"Loading topology from {topology_file}")

            self.filename = topology_file
            self.name = name or os.path.basename(topology_file)
            self.Switches = {} # Key = Switch_ID: 0, 1, 2, ... | Value = Switch object
            self.Links = {}     # Key = Link_ID: (0, 1), (1, 4), (4, 1), ... | Value = Link object
            links = file_to_table(topology_file, separator=',')
            for l in links:
                if first_node_id > 0:
                    l[0] = str(int(l[0]) - 1)
                    l[1] = str(int(l[1]) - 1)
                if len(l) < 2:
                    raise Exception("myError: bad edge record !!!!!*")
                from_sid = int(l[0])
                to_sid = int(l[1])
                capacity = MAX_CAPACITY
                weight = DEFAULT_W 
                if len(l) >= 3:
                    capacity = int(l[2] or MAX_CAPACITY)
                if len(l) >= 4:
                    weight = int(l[3] or DEFAULT_W)
                Lnk = self.get_or_add_link(from_sid, to_sid, capacity=capacity, weight=weight)
            # for sw in self.Switches.values():
            #     sw.OPTS['topology'] = self
            # for lnk in self.Links.values():
            #     lnk.OPTS['topology'] = self
            self.V = len(self.Switches)
            self.E = len(self.Links)
            # self.W = [[DEFAULT_W] * self.V] * self.V # --> NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO <--
            self.W = []
            for i in range(self.V + 1):
                self.W.append([])
                for j in range(self.V+1):
                    self.W[i].append(DEFAULT_W)
            for i in range(self.V + 1):
                self.W[i][i] = 0
            # self.show_W()
            for l in self.Links.values():
                self.W [l.id[0]] [l.id[1]] = l.weight
                if prints:
                    l.show()
                # print("W[{}][{}] = {}".format(l.id[0], l.id[1], l.weight))
            # Weight matrix
            # self.W = W
            if prints:
                self.show_W()


    def show_W(self):
        header = "\t".join(list(str(i) for i in range(self.V)))
        header = " \t" + header
        print(header)
        print("______________________________________________")
        for i in range(self.V):
            row = str(i).ljust(3,' ') + "|\t"
            row += "\t".join(str(x) for x in self.W[i])
            # for j in range(self.V):
            print(row)
        print("")

    def sid_path_weight(self, path):
        # path: a list of Switch.id
        weight = 0.0
        for i in range(len(path)-1):
            weight += self.W[path[i]][path[i+1]]
        return weight
    def switch_path_weight(self, path):
        # path: a list of Switch 
        weight = 0.0
        for i in range(len(path)-1):
            weight += self.W[path[i].id][path[i+1].id]
        return weight
    def switch_exist(self, sid:int):
        return sid in self.Switches.keys()
    def link_exist(self, lid):
        return lid in self.Links.keys()

    def get_or_add_switch(self, sid:int):
    # Create a new one if switch not exist
        if self.switch_exist(sid):
            return self.Switches[sid]
        else:
            new = Switch(sid)
            self.Switches[sid] = new
            self.switches_changed = True
            return new
    def delete_switch(self, sid:int):
        if self.link_exist(sid):
            self.Switches.pop(sid)
            self.switches_changed = True
    def get_or_add_link(self, from_sid:int, to_sid:int, capacity:int = MAX_CAPACITY, weight:int = 1):
    # Create a new one if link not exist
        lid = (from_sid, to_sid)
        if self.link_exist(lid):
            return self.Links[lid]
        else:
            frm_switch = self.get_or_add_switch(from_sid)
            to_switch = self.get_or_add_switch(to_sid)
            new = Link(frm_switch, to_switch, capacity=capacity, weight=weight)
            frm_switch.links_out.append(new)
            to_switch.links_in.append(new)
            self.Links[lid] = new
            self.links_changed = True
            return new
    def delete_link(self, from_sid:int, to_sid:int):
        lid = (from_sid, to_sid)
        if self.link_exist(lid):
            self.Links.pop(lid)
            self.links_changed = True

    def show_switches_out(self):
        print("topology: " + self.name)
        for s in sorted(self.Switches.values(), key=lambda x: x.id):
            s.show_out(prefix='  ')
    def show_links(self):
        print("topology: " + self.name)
        for l in sorted(self.Links.values()):
            l.show(prefix='  ')