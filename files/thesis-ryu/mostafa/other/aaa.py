#!/usr/bin/env python

#do authorize username service cmd cmdargs
#do accounting username service cmd cmdargs
#do set-authorization-type type
#do set-tacacs-server host port secret
#do set-accounting-type type
from __future__ import print_function

from tacacs_plus.client import TACACSClient
from tacacs_plus.flags import TAC_PLUS_ACCT_FLAG_START, TAC_PLUS_ACCT_FLAG_WATCHDOG, TAC_PLUS_ACCT_FLAG_STOP
from expiringdict import ExpiringDict
import socket
import sys
import systemd.daemon

# import thread module
from _thread import *
import threading

TRUE_RESPONSE=1
FALSE_RESPONSE=0
ERROR_RESPONSE=-1

cache = ExpiringDict(max_len=100, max_age_seconds=10, items=None)

authorization_type_file="/opt/Rahyab/files/authorization_type";
tacacs_server_info_file="/opt/Rahyab/files/tacacs_server";
accounting_type_file="/opt/Rahyab/files/accounting_type";

init_commands=[('warm-restart',''),('enable',''),('configure','terminal'),('service','integrated-vtysh-config'),('[no]','terminal paginate'),('end',''),('disable',''),('enable',''),('log','syslog'),('exit',''),('autocomplete','TYPE')]

#args start from 1.
def do_command(args):
    print(args)
    command=args[1]
    try:
        if command=="authorize":
            try:

                username=args[2]
                service=args[3]
                cmd=args[4]
                if(len(args)>5):
                    cmdargs=args[5]
                else:
                    cmdargs=""

                if (cmd,cmdargs) in init_commands:
                     print("init_commands")
                     return TRUE_RESPONSE   
                f=open(authorization_type_file,"r")
                authorization_type=f.read();
                f.close()
#                print(authorization_type)
                if authorization_type=="tacacs+":
                   f=open(tacacs_server_info_file,"r")
                   t=f.read().split()
                   host=t[0]
                   port=int(t[1])
                   secret=t[2]


                   cache_key=username+"_"+service+"_"+cmd+"_"+cmdargs
#                   print(cache_key)
                   if cache_key in cache:
                       return cache[cache_key];
                       
                   # For IPv6, use `family=socket.AF_INET6`
                   cli = TACACSClient(host, port, secret, timeout=10, family=socket.AF_INET)

                   # authorize user and command
                   author = cli.authorize(username, arguments=[bytes("service="+service,"utf8"), bytes("cmd="+cmd,"utf8"), bytes("cmdargs="+cmdargs, "utf8")])
                   #author = cli.authorize(username, arguments=[b"service=shell", bytes("cmd="+cmd,"utf8"), b"cmdargs=salam"])
                   #author = cli.authorize(username, arguments=[b"service=shell", b"cmd=show", b"cmdargs=version"])
                   #author = cli.authorize(username, arguments=[bytes("service="+service, "utf8"), bytes("cmd="+cmd, "utf8"), )
                   if author.valid:
                       cache[cache_key]=TRUE_RESPONSE
                       return cache[cache_key]
                   else:
                       cache[cache_key]=FALSE_RESPONSE
                       return cache[cache_key]
                else:
                    return TRUE_RESPONSE
                        #print("PASS!" if author.valid else "FAIL!")
            except  FileNotFoundError as e:
                return TRUE_RESPONSE
            except OSError as e:
                print(e)
                return ERROR_RESPONSE
            except Exception as e:
                print(e)
                return ERROR_RESPONSE
        if command=="accounting":
            try:

                username=args[2]
                service=args[3]
                cmd=args[4]
                if(len(args)>5):
                    cmdargs=args[5]
                else:
                    cmdargs=""


                f=open(accounting_type_file,"r")
                accounting_type=f.read();
                f.close()
                if accounting_type=="tacacs+":
                        f=open(tacacs_server_info_file,"r")
                        t=f.read().split()
                        host=t[0]
                        port=int(t[1])
                        secret=t[2]


                        # For IPv6, use `family=socket.AF_INET6`
                        cli = TACACSClient(host, port, secret, timeout=10, family=socket.AF_INET)

                        # authorize user and command
                        acct = cli.account(username, TAC_PLUS_ACCT_FLAG_START+TAC_PLUS_ACCT_FLAG_STOP ,arguments=[bytes("service="+service,"utf8"), bytes("cmd="+cmd,"utf8"), bytes("cmdargs="+cmdargs, "utf8")])
                        if acct.valid:
                            return TRUE_RESPONSE
                        else:
                            return FALSE_RESPONSE
            except OSError as e:
                return ERROR_RESPONSE
            except Exception as e:
                return ERROR_RESPONSE
        elif command=="set-authorization-type":
            authorization_type=args[2];
            f =open(authorization_type_file, "w")
            f.write(authorization_type)
            f.close()
            return TRUE_RESPONSE
        elif command=="set-accounting-type":
            accounting_type=args[2];
            f =open(accounting_type_file, "w")
            f.write(accounting_type)
            f.close()
            return TRUE_RESPONSE
        elif command=="set-tacacs-server":
            host=args[2]
            port=args[3]
            secret=args[4]
            f=open(tacacs_server_info_file,"w")
            f.write(host+" "+port+" "+secret)
            f.close()
            return TRUE_RESPONSE
    except IndexError as e:
        print(e)
        return ERROR_RESPONSE

# thread function
def threaded(c):
    while True:
        try:
            # data received from client
            data = c.recv(1024)
            if not data:
                break
    
            # reverse the given string from client
            #data = data[::-1]
            print(data)
            args=data.decode("utf-8").split();
            if do_command(args)==TRUE_RESPONSE:
                print("True")
                c.send(b'True\n')
            elif do_command(args)==FALSE_RESPONSE:
                print("False")
                c.send(b'False\n')
            else: 
                print("Error")
                c.send(b'Error\n')
        except Exception as e:
            print(e)
            c.send(b"Error\n")
    # connection closed
    c.close()
  
  
def Main():
    host = "localhost"
  
    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 13425
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    print("socket binded to port", port)
  
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")
    systemd.daemon.notify('READY=1')
    # a forever loop until client wants to exit
    while True:
        #print("1")
        # establish connection with client
        c, addr = s.accept()
  
        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
        #print("2")
    s.close()
  
if __name__ == '__main__':
    Main()
