from Topology import Topology, Switch
from Traffic import Traffic, Flow
# from routing.spf_dijkstra import SPF_dijkstra
# from routing.subal import Subal
class Path:
    def __init__(self, network, list_of_switches):
        self.net = network
        self.src_id = list_of_switches[0].id
        self.dst_id = list_of_switches[-1].id
        self.switches = list_of_switches
        self.links = [self.net.topology.Links[(self.switches[i-1].id, self.switches[i].id)] for i in range(1, len(self.switches))]
        self.sids = [sw.id for sw in list_of_switches]
        self.weight = 0
        if len(list_of_switches) > 1:
            for i in range(1, len(self.switches )):
                frm_sid = list_of_switches[i-1].id
                to_sid = list_of_switches[i].id
                self.weight += self.net.topology.Links[(frm_sid, to_sid)].weight
    def show_oneline(self, prefix=''):
        print("{}{} > {} w={}: {}".format(prefix, self.src_id, self.dst_id, self.weight, self.sids))
    # def links(self):
    #     return [self.net.topology.Links[(self.switches[i-1].id, self.switches[i].id)] for i in range(1, len(self.switches))]
    def is_saturated(self):
        for l in self.links:
            if l.OPTS['saturated']:
                return True
        return False
    

    def show(self, prefix=''):
        self.show_oneline(prefix=prefix)
    def show_links(self, prefix=''):
        for l in self.links:
            l.show(prefix=prefix)

    
class Network:
    def __init__(self, topology_file, traffic_csv_file):
        self.topology = Topology(topology_file)
        self.traffic = Traffic(traffic_csv_file)
        self.lifespan = max(f.arrive_at + f.duration for f in self.traffic.flows)
        self.rejected_flows = []
    def update_status(self, flow: Flow, path: Path):
        if path:
            for l in path.links:
                l.decrease_free(flow.rate)
                l.check_saturation() # Change link's OPTS['saturation'] to true if free capacity < 0
        else:
            self.reject(flow)
    def reject(self, flow: Flow):
        self.rejected_flows.append(flow)
    