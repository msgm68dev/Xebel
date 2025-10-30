from Network import Network, Path
from Topology import Topology, Link, Switch
from Traffic import Flow
class base_routing(object):
    def __init__(self, network: Network, name='sOmEroutingalg'):
        self.net = network
        self.name = name
    # Returns a list of switch_ids
    def route(self, src_id, dst_id):
        print("self.route method is NOT implemented yet!")
    def routeF(self, flow):
        self.route(str(flow.src_id), str(flow.dst_id))
    # Returns list of switche_ids, print it and decreases links free space
    def Route(self, flow: Flow):
        path = self.routeF(flow)
        path.show_oneline()
        for i in range(1, len(path)):
            v1 = int(path[i-1].id)
            v2 = int(path[i].id)
            l = self.net.topology.Links[(v1, v2)]
            l.OPTS['free'] -= flow.rate