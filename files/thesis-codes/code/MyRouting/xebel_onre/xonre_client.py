#!/usr/bin/python3
# client.py
# import os,  gc, time, argparse
import sys, argparse
import socket
import pydoc

default_ip = "127.0.0.1"
default_port = 1369

Commands = """
    help
    healthcheck
    stats
    paths 
    ways
    nodes
    edges
    metrics
    equations
    way <dashed-tuple>
    path <dashed-tuple>
    edge <dashed-tuple>
    verify <dashed-tuple>
    traverse <src> <dst> <delay-idx> <bw-idx>
    traverse1 <src> <dst> <delay-idx> <bw-idx>
    route <src> <dst> <delay> <bw>
    route_show <src> <dst> <delay> <bw>
    routes <src> <dst>
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Define the --config-file switch
    parser.add_argument("--ip", help="specify the IP of xebel-onre server")
    parser.add_argument("--port", help="specify the Port of xebel-onre server")
    parser.add_argument("positional_args", nargs="*", help="any arguments without switches")
    args = parser.parse_args()
    host = args.ip or default_ip
    PORT = int(args.port) or default_port
    # print(f"* * * * * * ** {args.positional_args}")


    def errrr():
        hstr = """
{} [--ip XEBEL_SERVER_IP] [--port XEBEL_SERVER_PORT] CMD
    default ip: {}
    default port: {}
CMD::{}
""".format(sys.argv[0], default_ip, default_port, Commands)
        print(f"{hstr}")
        exit(1)
    def verify_command(command_words):
        # verified = True
        def verify_command_length(l:int):
            if len(command_words) != l:
                errrr()
        def is_a_dashed_tuple(tuple_str):
            if not tuple_str:  
                errrr()
                # verified = False
                # return
            parts = tuple_str.split("-")  # Split the string by dashes
            if all(part.isdigit() for part in parts):  # Check if all parts are digits
                # verified = True
                pass
            else:
                errrr()
                # verified = False
        def is_a_positive_integer(num_str: str):
            if not num_str.isdigit():
                errrr()
            elif int(num_str) < 0:
                errrr()
        def is_a_positive_float(float_str):
            try:
                value = float(float_str)
                if value < 0:
                    errrr()
            except ValueError:
                errrr()
        if command_words[0] in ("help", "-h", "--help"):
            errrr()
        elif command_words[0] in (
                                "healthcheck",
                                "stats",
                                "paths",
                                "ways",
                                "nodes",
                                "edges",
                                "metrics",
                                "equations"
                                ):
            verify_command_length(1)
        if command_words[0] == "way":
            verify_command_length(2)
            is_a_dashed_tuple(command_words[1])
        if command_words[0] == "path":
            verify_command_length(2)
            is_a_dashed_tuple(command_words[1])
        if command_words[0] == "edge":
            verify_command_length(2)
            is_a_dashed_tuple(command_words[1])
        if command_words[0] == "equation":
            verify_command_length(2)
            is_a_positive_integer(command_words[1])
        if command_words[0] == "verify":
            verify_command_length(2)
            is_a_dashed_tuple(command_words[1])
        if command_words[0] in ("traverse", "traverse1"):
            verify_command_length(5)
            is_a_positive_integer(command_words[1])
            is_a_positive_integer(command_words[2])
            is_a_positive_integer(command_words[3])
            is_a_positive_integer(command_words[4])
        if command_words[0] in ("route", "route_show"):
            verify_command_length(5)
            is_a_positive_integer(command_words[1])
            is_a_positive_integer(command_words[2])
            is_a_positive_float(command_words[3])
            is_a_positive_float(command_words[4])
        if command_words[0] == "routes":
            verify_command_length(3)
            is_a_positive_integer(command_words[1])
            is_a_positive_integer(command_words[2])
    def send_command(request):
        # print(f"sent: {request}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, PORT))
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
    if len(sys.argv) > 1:
        words = [x.lower() for x in args.positional_args]
    else:
        words = ["help"]
    verify_command(words)
    response = send_command(" ".join(words))
    # pydoc.pager(f"Received: \n{response}")
    print(f"Received: \n{response}")