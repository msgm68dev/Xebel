from evaluation.evaltools import TOPOLOGY, N_FLOWS
from evaluation.TrafficGenerator import TG
from utils import get_env_var
from Topology import Topology

def example():
    examplestr = '''
'''
    print(examplestr)

n_flows = N_FLOWS
topo = Topology(TOPOLOGY)
tg = TG(n_flows, topo.V, rates=(1, 5), durations=(1, 1), arrivedAts=(0, 0))
tg.generate("tr_" + topo.name + "_" + str(n_flows))