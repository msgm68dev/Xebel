import sys
import heapq
from Network import Network,  Path
from Topology import Topology, Switch, Link
from Traffic import Flow, Traffic
from queue import PriorityQueue 
# def sid_list_to_Path(path_as_sid_list):

MaxDistance = sys.maxsize


class Simple_mcp:
    def __init__(self, network, *args, **kwargs):
        self.net = network
        self.name = "SimpleMCP_routing"
        self.topo = self.net.topology
    def dijkstra(self, src_id):
        topo = self.net.topology
        switches = topo.Switches.values()
        for s in switches:
            s.OPTS['distance'] = MaxDistance
            s.OPTS['visited'] = False
            s.OPTS['prev'] = None
        src_switch = topo.Switches[src_id]
        # print ('''Dijkstra's shortest path''')
        # Set the distance for the src_switch node to zero 
        src_switch.OPTS['distance'] = 0
        # Put tuple pair into the priority queue
        unvisited_queue = [(s.OPTS['distance'] ,s.id) for s in switches]
        heapq.heapify(unvisited_queue)

        while len(unvisited_queue):
            # Pops a vertex with the smallest distance 
            uv = heapq.heappop(unvisited_queue)
            idx = uv[1]
            current = topo.Switches[idx]
            current.OPTS['visited'] = True

            #for next in v.adjacent:
            for lnk_to in current.links_out:
                #SATURATION
                if lnk_to.OPTS['saturated']: 
                    continue

                next = lnk_to.To
                if next.OPTS['visited']:
                    continue
                new_dist = current.OPTS['distance'] + lnk_to.weight
                
                if new_dist < next.OPTS['distance']:
                    next.OPTS['distance'] = new_dist
                    next.OPTS['prev'] = current

            # Rebuild heap
            # 1. Pop every item
            while len(unvisited_queue):
                heapq.heappop(unvisited_queue)
            # 2. Put all vertices not visited into the queue
            unvisited_queue = [(s.OPTS['distance'] ,s.id) for s in switches if not s.OPTS['visited'] ]
            heapq.heapify(unvisited_queue)
    def shortest(self, dst, path):
        #     print('myError: dst_id = {} ({})'.format(dst_id, type(dst_id)))
        prev = dst.OPTS['prev']
        if prev:
            path.append(prev)
            self.shortest(prev, path)
        return
    def route(self, src_id, dst_id):
        print("dijkstra start")
        self.dijkstra(src_id)
        dst = self.net.topology.Switches[dst_id]
        path = [dst]
        self.shortest(dst, path)
        print("dijkstra end: {}".format(path))
        if path[0].id == dst_id and path[-1].id == src_id:
            path.reverse()
            return Path(self.net, path)
        else:
            return None
    def route_delay_bw(self, src_id, dst_id, max_delay, min_bandwidth):
        import random
        # A priority queue to hold the paths to be explored next, ordered by total delay
        priority_queue = PriorityQueue()
        source = self.topo.Switches[src_id]
        destination = self.topo.Switches[dst_id]
        # priority_queue.put((0, source.id, (source, [])))  
        # sid is added after delay just because in priority queue,
        # the items are of type like (priority_value, data) and when 
        # priority_values are equal, it tries to compare data parts.
        # however, Switch instances are not comparable. to avoid error
        # we add a fake  comparable field.
        priority_queue.put((0, random.random(), (source, [source])))  
        while not priority_queue.empty():
            current_delay, _, (current_node, path) = priority_queue.get()
            if current_node == destination and current_delay <= max_delay:
                return Path(self.net, path)
            for link_out in current_node.links_out:
                if link_out.OPTS['free'] >= min_bandwidth:
                    new_delay = current_delay + link_out.OPTS['delay']
                    if new_delay <= max_delay:
                        priority_queue.put((new_delay, random.random(), (link_out.To, path + [link_out.To])))
        return None

def bing_pseudo_code_delay_bw(graph, source, destination, max_delay, min_bandwidth):
    # This function uses a priority queue to explore paths in order 
    # of increasing total delay. When the destination is reached, 
    # it checks if the path satisfies the delay and bandwidth constraints. 
    # If it does, the path is returned; otherwise, the search continues. 
    # If no valid path is found, an empty list is returned. 
    # Remember to replace graph.neighbors and graph.get_edge_data with 
    # your actual graph's methods for accessing neighbors and edge data.

    # A priority queue to hold the paths to be explored next, ordered by total delay
    priority_queue = PriorityQueue()
    priority_queue.put((0, source, []))  # (total_delay, current_node, path_taken)

    while not priority_queue.empty():
        current_delay, current_node, path = priority_queue.get()

        # If the destination is reached and the conditions are satisfied, return the path
        if current_node == destination and current_delay <= max_delay:
            return path

        # Explore the neighbors of the current node
        for neighbor in graph.neighbors(current_node):
            edge_data = graph.get_edge_data(current_node, neighbor)

            # Check if the edge satisfies the bandwidth condition
            if edge_data['bandwidth'] >= min_bandwidth:
                # Calculate new total delay
                new_delay = current_delay + edge_data['delay']
                # If the new total delay is within the limit, add the neighbor to the queue
                if new_delay <= max_delay:
                    priority_queue.put((new_delay, neighbor, path + [neighbor]))

    # If no path is found, return an empty list
    return []

