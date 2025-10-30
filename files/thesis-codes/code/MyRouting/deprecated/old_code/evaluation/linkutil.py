from evaluation.evaltools import ALGORITHM, FLOWSET, TOPOLOGY
from evaluation.TrafficGenerator import TG
from Topology import Topology, Switch, Link
from Traffic import Traffic, Flow
from Network import Network
from Router import Router


def example():
    examplestr = '''
net = Network(TOPOLOGY, FLOWSET)
router = Router(net, ALGORITHM)
path = router.route(src_id, dst_id)
path.show_oneline()	
router.route('2', '20').show_oneline()
pw = router.alg.sid_path_weight

# SUBAL:
router.alg.GPATHs[2][21].groups[0]
[s.id for s in router.alg.GPATHs[2][21].groups[1][0]]

# Traffic Generator:
n_flows = 500
tg = TG(n_flows, net.topology.V, rates=(1, 5), durations=(1, 1), arrivedAts=(0, 0))
tg.generate("tr_" + net.topology.name + "_" + str(n_flows))

net.topology.Links[(0, 3)].capacity
net.topology.Links[(0, 3)].OPTS['free']

f=net.traffic.flows[0]
'''
    print(examplestr)

net = Network(TOPOLOGY, FLOWSET)
router = Router(net, ALGORITHM)


# def Route(src_id, dst_id):
#     path = router.route(str(src_id), str(dst_id))
#     path.show_oneline()

# def RouteF(flow: Flow):
#     path = Route(flow.src_id, flow.dst_id)
#     path.show_oneline()

#     path = self.routeF(flow)
#     path.show_oneline()
#     for i in range(1, len(path)):
#         v1 = int(path[i-1].id)
#         v2 = int(path[i].id)
#         l = self.net.topology.Links[(v1, v2)]
#         l.OPTS['free'] -= flow.rate
    # Route(str(flow.src_swch_id), str(flow.dst_swch_id))
def ResetLinksTo(free_capacity):
    for link in net.topology.Links.values():
        link.OPTS['free'] = free_capacity
        




print("-------TOPOLOGY:---------------")
# net.topology.show_switches_out()
print("--------TRAFFIC:--------------")
# net.traffic.show()
print("--------ROUTING:--------------")
# src_id = input('Source: ')
# dst_id = input('Destination: ')

def go(show=False):
    import statistics
    import time
    import os
    from evaluation.evaltools import flowset_dir

    start = time.time()
    for f in net.traffic.flows:
        # f.show()
        router.Route(f, show)
    time = round(time.time() - start, 2)

    utils = [ (1-(l.OPTS['free'] / l.capacity))*100.0 \
        for l in  net.topology.Links.values()]
    caps = [l.capacity for l in  net.topology.Links.values()]
    avg_cap = statistics.mean(caps)
    avg = round(statistics.mean(utils), 2)
    std = round(statistics.stdev(utils), 2)
    nrej = len(net.rejected_flows)
    rej_rate = (100.0 * nrej) / len(net.traffic.flows)

    first_rej = -1
    if nrej > 0:
        first_rej = net.traffic.flows.index(net.rejected_flows[0])
    
    # try:
    results_file = os.path.join(flowset_dir, "../results/Results.txt")
    with open(results_file, mode='a') as f:
        # f.write("* {}\n".format(TOPOLOGY))
        # f.write("* {}\n".format(FLOWSET))
        f.write("{0:<20}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}{7:<10}{8:<10}\n".format( \
                "Alg", "avg_cap", "avg_%util", "std_%util", "%reject", "1stRej", "time", "topo", "traffic"))
        f.write("{0:<20}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}{7:<10}{8:<10}\n".format( \
                ALGORITHM, avg_cap, avg,  
                std, rej_rate, first_rej, time, 
                net.topology.name, net.traffic.name))

        f.close()
    print("Results appended to " + results_file)
    # except Exception as e:
        # print(str(e))

    # print("Method = {}".format(ALGORITHM))
    # print("Time = {}".format(round(time, 2)))
    # print("avg = {}".format( avg))
    # print("avg capacities = {}".format( avg_cap))
    # print("std = {}".format( std))
    # print("rejected flows = {}".format(len(net.rejected_flows)))


go()
