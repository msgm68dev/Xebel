from Network import Network
from Traffic import Flow
from routing.spf_dijkstra import SPF_dijkstra 
from routing.subal import Subal 

class Router:
    def __init__(self, network, Routing_alg):
        self.net = network
        self.alg = None
        words = Routing_alg.split()
        routing_alg = words[0]
        if words[0] == "spf":
            self.alg = SPF_dijkstra(self.net, name=routing_alg)
        elif words[0] == "subal":
            try:
                acep = float(words[1])
                aps = float(words[2])
                overlap = float(words[3])
            except Exception as e:
                raise Exception("Acep/Aps/Overlap are not provided sufficiently!")
                exit(1)
            self.alg = Subal(self.net, name=routing_alg, acep=acep, aps=aps, overlap=overlap)
        else:
            raise Exception("Unknown Routing Algorithm: " + routing_alg)
            exit(1)
        self.route = self.alg.route
    def Route(self, flow: Flow, show = True):
        path = self.route(flow.src_id, flow.dst_id)
        self.net.update_status(flow, path)
        if show:
            flow.show()
            if path:
                path.show(prefix        ="Route: ")
                path.show_links(prefix  ='      ')
            else:
                print(" Rejected ")
                # path.show_links()
            input('Press Enter ...')
        