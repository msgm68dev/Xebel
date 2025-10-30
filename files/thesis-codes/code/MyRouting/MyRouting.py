#!/usr/bin/env python3

# from __future__ import print_function
from ast import arg
import socket
import sys
# import systemd.daemon
# import thread module
from _thread import *
import threading
import os
from pickle import loads
from unittest import result

from Router import Router
from Network import Network, Path
from Topology import Topology, MAX_CAPACITY
from settings import *
from utils import _listen_to_port, log_into

GraphPort = 1224
MonitorPORT = 1225
RoutingPORT = 1226 
HOST = "localhost"

# GRAPH ============================================================================
import requests
import copy
import networkx as nx
from networkx.algorithms.shortest_paths.generic import shortest_path
from networkx.readwrite import json_graph
import json
from time import sleep
# RYU_IP = "localhost"
# RYU_PORT = 8080
# GRAPH_URL = "http://{}:{}/v1.0/topology/graph".format(RYU_IP, RYU_PORT)
# UPDATE_GRAPH_SECS = 5
graph = None
graph_hash = ""
def graph_init():
    os.makedirs(TOPOLOGY_DIR, exist_ok=True)
    if (os.path.exists(TOPOLOGY_NODES) == False):
            f = open(TOPOLOGY_NODES, "w")
            f.close()
    if (os.path.exists(TOPOLOGY_LINKS) == False):
            f = open(TOPOLOGY_LINKS, "w")
            f.close()
    if (os.path.exists(GRAPH_LOGFILE) == False):
            f = open(GRAPH_LOGFILE, "w")
            f.close()
    
def ask_graph():
    res = requests.get(GRAPH_URL)
    result_json = res.json()
    log_into("ASKED GRAPH: \n\t{}".format(result_json), GRAPH_LOGFILE)
    g = json_graph.node_link_graph(result_json)
    return g
def save_topology_as_text_file(topo: Topology):
    # USE topo.links_changed and topo.switches_changed  HERE
    nodes = sorted([s for s in topo.Switches])
    links = sorted([l for l in topo.Links])
    with open(TOPOLOGY_NODES, "w") as f:
        for node in nodes:
            f.write(str(node)+"\n")
        f.close()
    with open(TOPOLOGY_LINKS, "w") as f:
        f.write("# from, to, capacity, weight\n")
        for link in links:
            u, v = link
            L = topo.Links[(u, v)]
            f.write("{}, {}, {}, {}\n".format(u, v, L.capacity, L.weight))
        f.close()
def update_graph_thread(args:Topology):
    topology = args
    global graph
    global graph_hash
    while True:
        try:
            graph = ask_graph() # graph is of type nx.DiGraph
            for node in graph.nodes:
                if node < MAX_SWITCHES:
                    topology.get_or_add_switch(node)
            for u, v, weight in graph.edges(data="weight"):
                if u!=v:
                    topology.get_or_add_link(u, v, capacity=MAX_CAPACITY, weight=weight )
            
            # hash = nx.weisfeiler_lehman_graph_hash(graph)
            # if hash == graph_hash:
                # log_into("graph hash NOT changed {}".format(hash), GRAPH_LOGFILE)
            # else:
                # log_into("graph hash CHanged {} -> {}".format(graph_hash, hash), GRAPH_LOGFILE)
                # graph_hash = hash
            # log_into("*** UPDATED GRAPH: \n{}".format(graph), GRAPH_LOGFILE)
        except Exception as e:
            print("Exception: ask_graph failed!\n\t{} ".format(str(e)))
            sleep(UPDATE_GRAPH_SECS)
            continue
        
        # DECIDE FOR TOPOLOGY CHANGE HERE
        save_topology_as_text_file(topology)
        sleep(UPDATE_GRAPH_SECS)
# def listen_to_graph_reports():
"""
    s = _listen_to_port(HOST, GraphPort)
    while True:
        c, addr = s.accept()
        start_new_thread(_receive_full_graph, (c,)) # Start a new thread and return its identifier
    s.close()
def _receive_full_graph(c):
    while True:
        try:
            data = c.recv(4096)
            if not data:
                break
            # print("<< {}".format(data))
            graph = loads(data)
            # graph = ask_graph()
            
            _process_graph_report(graph)
            result = "Thank you controller!"
            print(">> {}".format(result))
            c.send(bytes('{}\n'.format(result), 'ascii'))
        except Exception as e:
            print(e)
            c.send(b"Error\n")
    c.close()
def _process_graph_report(graph):
    print("Graph report:")
    print(graph)
    print("\End of Graph report")
"""

# MONITORING ===========================================================================
# MONITOR_DATA_DIR = "/dev/shm/mon"
# DELAY_DIR = MONITOR_DATA_DIR + "/delay"
# BANDWIDTH_DIR = MONITOR_DATA_DIR + "/bw"
# SPEED_DIR = MONITOR_DATA_DIR + "/speed"
def monitoring_init():
    try:
        os.makedirs(DELAY_DIR, exist_ok=True)
        os.makedirs(BANDWIDTH_DIR, exist_ok=True)
        os.makedirs(SPEED_DIR, exist_ok=True)
        if (os.path.exists(MONITORING_LOGFILE) == False):
            f = open(MONITORING_LOGFILE, "w")
            f.close()
    except Exception as e:
        print(e) 
        exit(1)
def listen_to_monitoring_events(args):
    topology = args
    log_into("monitoring thread started", MONITORING_LOGFILE)
    s = _listen_to_port(HOST, MonitorPORT)
    while True:
        c, addr = s.accept()
        start_new_thread(_receive_monotoring_data, (c,topology,)) # Start a new thread and return its identifier
    s.close()
def _receive_monotoring_data(c, topology):
    while True:
        try:
            data = c.recv(1024)
            if not data:
                break
            log_into("in<< {}".format(data), MONITORING_LOGFILE)
            args=data.decode("utf-8").split()
            result = _process_monotoring_data(topology, args)
            c.send(bytes('{}\n'.format(result), 'ascii'))
            # DECIDE FOR TOPOLOGY CHANGE HERE
            save_topology_as_text_file(topology)


        except Exception as e:
            print(e)
            c.send(bytes("Error _receive_monotoring_data: {}\n".format(str(e))))
    c.close()
def _process_monotoring_data(topology:Topology, args):
    if args[0] == "metric":
        src = args[1]
        dst = args[2]
        metric = args[3]
        old_val = args[4]
        new_val = args[5]
        f = open("{}/{}/{}-{}".format(MONITOR_DATA_DIR, metric, src, dst), "w")
        f.write(new_val)
        f.close()
    elif args[0] == "topo":
        if args[1] == "link":
            event = args[2]  
            src = int(args[3])
            dst = int(args[4])
            if event == "add":
                if src != dst:
                    #USE TOPOLOGY OBJECT HERE
                    topology.get_or_add_link(src, dst, capacity=876543210000, weight=1)
            elif event == "del":
                # pass 
                #USE TOPOLOGY OBJECT HERE
                topology.delete_link(src, dst)
            return "Topochange link {}: {}<--->{} ".format(event, src, dst)
        elif args[1] == "switch":
            event = args[2]
            src = int(args[3])
            if event == "add":
                if src < MAX_SWITCHES:
                    # pass #USE TOPOLOGY OBJECT HERE
                    topology.get_or_add_switch(src)
            elif event == "del":
                # pass #USE TOPOLOGY OBJECT HERE
                topology.delete_switch(src)
            return "Topochange switch {}: {} ".format(event, src)
            
    return "javab " + str(args)

# ROUTING ===========================================================================
# ROUTING_DATA_DIR = "/dev/shm/rt"
# ROOTDIR = os.environ["THESIS"]
# ALL_ROUTES_CSV = "{}/doc/all_routes_nx.txt".format(ROOTDIR)
all_routes_list = None
import csv
def routing_init():
    os.makedirs(ROUTING_DATA_DIR, exist_ok=True)
    if (os.path.exists(ROUTING_LOGFILE) == False):
            f = open(ROUTING_LOGFILE, "w")
            f.close()
    f = open(ALL_ROUTES_CSV, newline='')
    reader = csv.reader(f)
    all_routes_list = list(reader)
    f.close()
    for path in all_routes_list:
        src = path[0]
        dst = path[-1]
        f = open("{}/{}-{}".format(ROUTING_DATA_DIR, src,dst), "w")
        f.write(",".join(path))
def get_route(src, dst):
    f = open("{}/{}-{}".format(ROUTING_DATA_DIR, src, dst), newline='')
    path = csv.reader(f)
    print("{}".format(path))
    return path
def listen_to_routing_requests(args):
    router = args
    log_into("routing thread started", ROUTING_LOGFILE)
    s = _listen_to_port(HOST, RoutingPORT)
    while True:
        c, addr = s.accept()
        start_new_thread(_receive_routing_requests, (c,router)) # Start a new thread and return its identifier
    s.close()
def _receive_routing_requests(c, router):
    while True:
        try:
            data = c.recv(1024)
            if not data:
                break
            log_into("<< {}".format(data), ROUTING_LOGFILE)
            args=data.decode("utf-8").split();
            result = _process_routing_request(router, args)
            log_into(">> {}".format(result), ROUTING_LOGFILE)
            c.send(bytes('{}'.format(result), 'ascii'))
        except Exception as e:
            print(e)
            # c.send(bytes("Error _receive_routing_requests: {}\n".format(str(e))))

    c.close()
def _process_routing_request(router:Router, args):
    src = int(args[2])
    dst = int(args[4])
    #USE ROUTER OBJECT HERE:
    path = router.route(src, dst).switches
    path = [s.id for s in path]
    path_str = str(path).replace(" ","").replace("'","")[1:-1]
    # path = [s.id for s in switches]
    #\USE ROUTER OBJECT HERE
    result = "PATH {} {} {}".format(src, dst, str(path_str))
    # log_into("{}".format(result) \
    #          , ROUTING_LOGFILE, print_it=True)
    return result

# MAIN ============================================================================
def init():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception as e:
        print(e) 
        exit(1)
def Main():
    init()
    topo = Topology()
    net = Network(topo)
    router = Router(net, ALGORITHM)

    mon = threading.Thread(target=listen_to_monitoring_events, args=([topo]))
    rot = threading.Thread(target=listen_to_routing_requests, args=([router]))
    # gr =  threading.Thread(target=listen_to_graph_reports, args=())
    gr =  threading.Thread(target=update_graph_thread, args=([topo]))
    # start_new_thread(listen_to_monitoring_events, ())
    # start_new_thread(listen_to_routing_requests, ())
    monitoring_init()
    mon.start()
    routing_init()
    rot.start()
    graph_init()
    gr.start()
    print(" ******** 3 threads started! ********")
    print(" See logs:")
    print("   tail -f {}".format(MONITORING_LOGFILE))
    print("   tail -f {}".format(ROUTING_LOGFILE))
    print("   tail -f {}".format(GRAPH_LOGFILE))
if __name__ == '__main__':
    Main()
