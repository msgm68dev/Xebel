#!/usr/bin/python3

# Import the socket module
import socket

import sys
# Create a TCP socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port as a tuple
server_addr = ("127.0.0.1", 12345)

# Connect to the server socket
client.connect(server_addr)

# Define the message to be sent as bytes
if len(sys.argv) > 1:
    message = bytes(sys.argv[1], "ascii")
else:
    message = b"Myname"

# Send the message to the server socket
client.send(message)

# Receive the response from the server socket
response = client.recv(1024)

# Print the response as a string
print(response.decode())

# Close the socket
client.close()
