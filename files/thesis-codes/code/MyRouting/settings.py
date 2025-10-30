import os
MonitorPORT = 1225
RoutingPORT = 1226 
RYU_IP = "localhost"
LOG_DIR = "/tmp/log/myrouting/"
MAX_SWITCHES = 100000 # In order to kickout ovs node (e.g. id=156142563561286)
# GRAPH ============================================================================
RYU_PORT = 8080
RYU_IP = "localhost"
GRAPH_URL = "http://{}:{}/v1.0/topology/graph".format(RYU_IP, RYU_PORT)
UPDATE_GRAPH_SECS = 60
GRAPH_LOGFILE = LOG_DIR + "graph"
TOPOLOGY_DIR = "/dev/shm/topo"
TOPOLOGY_NODES = TOPOLOGY_DIR + "/nodes"
TOPOLOGY_LINKS = TOPOLOGY_DIR + "/links"
TOPO_PICKLES_DIR = "/root/data/pickles/"
# MONITORING ===========================================================================
MONITOR_DATA_DIR = "/dev/shm/mon"
DELAY_DIR = MONITOR_DATA_DIR + "/delay"
BANDWIDTH_DIR = MONITOR_DATA_DIR + "/bw"
SPEED_DIR = MONITOR_DATA_DIR + "/speed"
MONITORING_LOGFILE = LOG_DIR + "monitoring"

# ROUTING ===========================================================================
ROUTING_DATA_DIR = "/dev/shm/rt"
ROOTDIR = os.environ["THESIS"]
ALL_ROUTES_CSV = "{}/doc/all_routes_nx.txt".format(ROOTDIR)
ROUTING_LOGFILE = LOG_DIR + "routing"
# MYROUTING =============================================================================
ALGORITHM = "spf"
# ALGORITHM = "subal 0.8 3 0"