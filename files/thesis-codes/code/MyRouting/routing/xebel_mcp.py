# from routing.base import base_routing as BaseRouting
from Network import Path, Network
# from allpaths_w import Graph, ijPaths
from utils import *
import os
import socket


def send_command(request, address):
    # print(f"sent: {request}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    r = request.encode()
    sock.send(r)
    full_response = b""  
    while True:
        response = sock.recv(5000)  # Receive up to 5000 bytes
        if not response:
            break
        full_response += response
        if b"\r\n\r\n" in full_response:
            break
    sock.close()
    return full_response.decode()
            
class Xebel_mcp:
    def __init__(self, network, xebel_server, *args, **kwargs):
        self.net = network
        self.name = "Xebel_routing"
        self.current = 0
        self.topo = self.net.topology
        self.xebel_server = xebel_server
            
    def route(self, src_id, dst_id):
        return self.route_bw_delay(src_id, dst_id, max_delay=1000, min_bandwidth=0)
    def route_delay_bw(self, src_id, dst_id, max_delay, min_bandwidth):
        response = send_command(f"route {src_id} {dst_id} {max_delay} {min_bandwidth}", self.xebel_server)
        # print(f"xebel.py route response = {response}")
        try:
            if response == "":
                return None
            sid_s = [int(x) for x in response.split("-")]
            return Path(self.net, id_list_to_switch_list(sid_s, self.net.topology.Switches))
        except Exception as e:
            print(f"xebel_mcp.py route error) response: \"{response}\"")
            return None
    



