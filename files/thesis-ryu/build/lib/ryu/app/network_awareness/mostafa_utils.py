from collections import defaultdict
from email.policy import default
import socket
from types import new_class

MonitorPORT = 1225
RoutingPORT = 1226
# GraphPort = 1224 
HOST = '127.0.0.1'

DELAY_PRECISION = 3
LINK_DELIMETER = ' '
class OutSource_Routing():
    def __init__(self):
        self.link_speed = defaultdict(int)
        self.link_delay = defaultdict(float)
        self.link_bw = defaultdict(int)
    def _get_link_name(self, src, dst):
        return '{}{}{}'.format( src, LINK_DELIMETER, dst)
    def _send_string_on_socket(self, data_str, port):
        data = None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, port))
                s.sendall(bytes(data_str, 'ascii'))
                data = s.recv(1024)
        return  repr(data)
    def _send_bytes_on_socket(self, data_bytes, port):
        data = None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, port))
                s.sendall(data_bytes)
                data = s.recv(1024)
        return  repr(data)
    def _send_link_metric(self, link, metric, old_value, new_value):
        """
        str_to_send : metric <link> <metric-name> <old-value> <new-value>
            example (DELIM= ) :  metric 11 3 delay 0.05 0.72
        """
        # if old_value != new_value:
        str_to_send = "metric {} {} {} {}".format(link, metric, old_value, new_value)
        javab = self._send_string_on_socket(str_to_send, MonitorPORT)
        return javab
        # return None
    def send_link_speed(self, src, dst, speed):
        link = self._get_link_name(src, dst)
        new_speed = int(speed)
        old_speed = self.link_speed[link]
        self.link_speed[link] = new_speed
        return self._send_link_metric(link, 'speed', old_speed, new_speed)
    def send_link_bw(self, src, dst, bw):
        link = self._get_link_name(src, dst)
        new_bw = int(bw)
        old_bw = self.link_bw[link]
        self.link_bw[link] = new_bw
        return self._send_link_metric(link, 'bw', old_bw, new_bw)
    def send_link_delay(self, src, dst, delay):
        link = self._get_link_name(src, dst)
        new_delay = round(delay, DELAY_PRECISION)
        old_delay = self.link_delay[link]
        self.link_delay[link] = new_delay
        return self._send_link_metric(link, 'delay', old_delay, new_delay)
    def send_routing_request(self, src, dst):
        str_to_send = "route from {} to {}".format(src, dst)
        return  self._send_string_on_socket(str_to_send, RoutingPORT)
    def send_topology_change(self, entity, event, msg):
        """
        str_to_send : topo <entity> <event> <name> 
            example :   topo link add 1 8
                        topo switch add 4
        """
        name = ""
        if entity == "link":
            src = int(msg['src']['dpid'], base=16)
            dst = int(msg['dst']['dpid'], base=16)
            name = self._get_link_name(src, dst)
        elif entity == "switch":
            name = int(msg['dpid'], base=16)
        str_to_send = "topo {} {} {}".format(entity, event, name)
        return self._send_string_on_socket(str_to_send, MonitorPORT)

# Useless
    def send_graph(self, graph_as_bytes):
        GraphPort = 1224 
        self._send_bytes_on_socket(graph_as_bytes, GraphPort)
