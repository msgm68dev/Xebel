#!/usr/bin/python3
# client.py
import socket
import sys
import pydoc

host = "127.0.0.1"
PORT = 1369
if len (sys.argv) != 2:
    print ("Usage: python client.py \"command\"")
    sys.exit (1)
cmd = sys.argv [1]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, PORT))
request = cmd
print(f"sent: {request}")
r = request.encode()
sock.send(r)
response = sock.recv (50000)
response = response.decode ()
pydoc.pager(f"Received: {response}")
sock.close()