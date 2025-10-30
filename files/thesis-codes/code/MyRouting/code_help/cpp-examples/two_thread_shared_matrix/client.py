#!/usr/bin/python3
# client.py
import socket
import sys

host = "127.0.0.1"
PORT = 1369
# sock = socket.socket (socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.sendto (b"GET NUMBER 3 2", ("127.0.0.1", 1226))
# response = sock.recv (1024)
# response = response.decode ()
# print ("Received response:", response)
# exit(0)

# Check the number of arguments
if len (sys.argv) != 3:
    print ("Usage: python client.py row col")
    sys.exit (1)

# Get the arguments
# host = sys.argv [1]
# port = int (sys.argv [2])
row = sys.argv [1]
col = sys.argv [2]

# Create a raw socket
# sock = socket.socket (socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, PORT))

# Format the request
request = "GET NUMBER {} {}".format (col, row)
print(f"sent: {request}")
r = request.encode()
# print("host {} port {} row {} col {} r {}".format(host,port, row, col, r))
# Send the request to the host and port
# print(sock.sendto.__doc__)
sock.send(r)


# Receive the response from the socket
response = sock.recv (1024)

# Convert the response to a string
response = response.decode ()

# Print the response
print (f"Received: {response}")
sock.close()
