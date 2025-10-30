#!/bin/bash

cd ~/thesis-ryu/
sudo python3.6 setup.py install
ryu-manager --observe-links ryu/app/network_awareness/shortest_forwarding.py
