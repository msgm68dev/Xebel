import sys
import heapq
from routing.base import base_routing as BaseRouting
from Network import Network,  Path
from Topology import Topology, Switch, Link
from Traffic import Flow, Traffic
MaxDistance = sys.maxsize

# Source: https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php

class SPF_dijkstra(BaseRouting):
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
        self.dijkstra(src_id)
        dst = self.net.topology.Switches[dst_id]
        path = [dst]
        self.shortest(dst, path)
        if path[0].id == dst_id and path[-1].id == src_id:
            path.reverse()
            return Path(self.net, path)
        else:
            
            return None