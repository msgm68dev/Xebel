from Network import Network
# from Traffic import Flow
from routing.simple_mcp import Simple_mcp
from routing.xebel_mcp import *




class MC_Router:
    def __init__(self, network, Routing_alg):
        self.net = network
        self.alg = None
        words = Routing_alg.split()
        routing_alg = words[0]
        if words[0] == "simple_mcp":
            self.alg = Simple_mcp(self.net, name=routing_alg)
        elif words[0] == "xebel_mcp":
            try:
                ip  = words[1]
                port  = int(words[2])
            except Exception as e:
                raise Exception("Ip/Port are not provided sufficiently!")
                exit(1)
            xebel_server=(ip, port)
            self.alg = Xebel_mcp(self.net, name=routing_alg, xebel_server=xebel_server)
        else:
            raise Exception("Unknown Routing Algorithm: " + routing_alg)
            exit(1)
        self.route = self.alg.route
        self.route_delay_bw = self.alg.route_delay_bw
    def Route(self, src_sid:int, dst_sid:int, show = True):
        # print("salam router")
        path = self.route(src_sid, dst_sid)
        # self.net.update_status(flow, path)
        if show:
            if path:
                path.show(prefix="Route: ")
                # path.show_links(prefix  ='      ')
            else:
                print(f"Rejected: {src_sid} > {dst_sid}")
            # input('Press Enter ...')
        return path
    # def Route(self, flow: Flow, show = True):
    def Route_delay_bw(self, src_sid:int, dst_sid:int, max_delay, min_bandwidth, show = True):
        path = self.route_delay_bw(src_sid, dst_sid, max_delay, min_bandwidth)
        if show:
            if path:
                path.show(prefix="Route: ")
            else:
                print(f"Rejected: {src_sid} > {dst_sid}")
        return path
        