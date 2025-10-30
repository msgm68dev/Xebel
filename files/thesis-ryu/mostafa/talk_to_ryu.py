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
from time import sleep
RYU_IP = "localhost"
RYU_PORT = 8080
GRAPH_URL = "http://{}:{}/v1.0/topology/graph".format(RYU_IP, RYU_PORT)
UPDATE_GRAPH_SECS = 10
graph = None
graph_hash = ""
def ask_graph():
    res = requests.get(GRAPH_URL)
    print(res.json())
    graph_link_data = res.json()
    g = json_graph.node_link_graph(graph_link_data)
    graph_link_data = res.json()
    return json_graph.node_link_graph(graph_link_data)
def update_graph_thread():
    global graph
    global graph_hash
    while True:
        graph = ask_graph()
        hash = nx.weisfeiler_lehman_graph_hash(graph)
        if hash == graph_hash:
            print("salari: nochange {}".format(hash))
        else:
            print("salari: changed {} -> {}".format(graph_hash, hash))
            graph_hash = hash
        print(graph)
        sleep(UPDATE_GRAPH_SECS)
# def listen_to_graph_reports():
#     s = _listen_to_port(HOST, GraphPort)
#     while True:
#         c, addr = s.accept()
#         start_new_thread(_receive_full_graph, (c,)) # Start a new thread and return its identifier
#     s.close()
# def _receive_full_graph(c):
#     while True:
#         try:
#             data = c.recv(4096)
#             if not data:
#                 break
#             # print("<< {}".format(data))
#             graph = loads(data)
#             # graph = ask_graph()
            
#             _process_graph_report(graph)
#             result = "Thank you controller!"
#             print(">> {}".format(result))
#             c.send(bytes('{}\n'.format(result), 'ascii'))
#         except Exception as e:
#             print(e)
#             c.send(b"Error\n")
#     c.close()
# def _process_graph_report(graph):
#     print("Graph report:")
#     print(graph)
#     print("\End of Graph report")

# MONITORING ===========================================================================
MONITOR_DATA_DIR = "/dev/shm/mon"
DELAY_DIR = MONITOR_DATA_DIR + "/delay"
BANDWIDTH_DIR = MONITOR_DATA_DIR + "/bw"
SPEED_DIR = MONITOR_DATA_DIR + "/speed"
def monitoring_init():
    try:
        os.makedirs(DELAY_DIR, exist_ok=True)
        os.makedirs(BANDWIDTH_DIR, exist_ok=True)
        os.makedirs(SPEED_DIR, exist_ok=True)
    except Exception as e:
        print(e) 
        exit(1)
def listen_to_monitoring_events():
    s = _listen_to_port(HOST, MonitorPORT)
    while True:
        c, addr = s.accept()
        start_new_thread(_receive_monotoring_data, (c,)) # Start a new thread and return its identifier
    s.close()
def _receive_monotoring_data(c):
    while True:
        try:
            data = c.recv(1024)
            if not data:
                break
    
            print("in<< {}".format(data))
            args=data.decode("utf-8").split();
            result = _process_monotoring_data(args)
            print("out>> {}".format(result))
            c.send(bytes('{}\n'.format(result), 'ascii'))
        except Exception as e:
            print(e)
            c.send(b"Error\n")
    c.close()
def _process_monotoring_data(args):
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
            src = args[3]
            dst = args[4]
            return "Topochange link {}: {}<--->{} ".format(event, src, dst)
        elif args[1] == "switch":
            event = args[2]
            src = args[3]
            return "Topochange switch {}: {} ".format(event, src)
            
    return "javab " + str(args)

# ROUTING ===========================================================================
ROUTING_DATA_DIR = "/dev/shm/rt"
ROOTDIR = os.environ["THESIS"]
ALL_ROUTES_CSV = "{}/doc/all_routes_nx.txt".format(ROOTDIR)
all_routes_list = None
import csv
def routing_init():
    os.makedirs(ROUTING_DATA_DIR, exist_ok=True)
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
def listen_to_routing_requests():
    s = _listen_to_port(HOST, RoutingPORT)
    while True:
        c, addr = s.accept()
        start_new_thread(_receive_routing_requests, (c,)) # Start a new thread and return its identifier
    s.close()
def _receive_routing_requests(c):
    while True:
        try:
            data = c.recv(1024)
            if not data:
                break
            print("<< {}".format(data))
            args=data.decode("utf-8").split();
            result = _process_routing_request(args)
            print(">> {}".format(result))
            c.send(bytes('{}\n'.format(result), 'ascii'))
        except Exception as e:
            print(e)
            c.send(b"Error\n")
    c.close()
def _process_routing_request(args):
    src = args[2]
    dst = args[4]
    route = get_route(src, dst)
    return "javab " + str(route)

# MAIN ============================================================================
def _listen_to_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    print("socket binded to port ", port)
    #Backlog: In simple words, the backlog parameter specifies the number 
    # of pending connections the queue will hold:
    backlog = 10
    # put the socket into listening mode
    s.listen(backlog) 
    print("socket is listening")
    return s
def Main():
    mon = threading.Thread(target=listen_to_monitoring_events, args=())
    rot = threading.Thread(target=listen_to_routing_requests, args=())
    # gr =  threading.Thread(target=listen_to_graph_reports, args=())
    gr =  threading.Thread(target=update_graph_thread, args=())
    # start_new_thread(listen_to_monitoring_events, ())
    # start_new_thread(listen_to_routing_requests, ())
    monitoring_init()
    mon.start()
    routing_init()
    rot.start()
    gr.start()
    print(" ******** 3 threads started! ********")
if __name__ == '__main__':
    Main()
