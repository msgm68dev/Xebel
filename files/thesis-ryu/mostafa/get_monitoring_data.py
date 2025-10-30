#!/usr/bin/env python3.9

# from __future__ import print_function
import socket
import sys
# import systemd.daemon
# import thread module
from _thread import *
import threading

PORT = 1225 # Get Monitoring Data
HOST = "localhost"

 
def listen_to_port(host, port):
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
# thread function
def receive_data(c):
    while True:
        try:
            data = c.recv(1024)
            if not data:
                break
    
            print("<< {}".format(data))
            args=data.decode("utf-8").split();
            result = process_data(args)
            print(">> {}".format(result))
            c.send(bytes('{}\n'.format(result), 'ascii'))
        except Exception as e:
            print(e)
            c.send(b"Error\n")
    c.close()
def process_data(args):
    return "javab " + str(args)

def Main():
    s = listen_to_port(HOST, MonitorPORT)
    # systemd.daemon.notify('READY=1') # Notify service manager about start-up completion
    while True:
        c, addr = s.accept()
        start_new_thread(receive_data, (c,)) # Start a new thread and return its identifier
    s.close()
  
if __name__ == '__main__':
    Main()
