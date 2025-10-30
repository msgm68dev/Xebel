FROM ubuntu:18.04

USER root
WORKDIR /root

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    ifupdown \
    iproute2 \
    iptables \
    iputils-ping \
    mininet \
    net-tools \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    vim \
    x11-xserver-utils \
    xterm \
    sudo \
    python3.6 python3-dev python3-pip  python3-setuptools
RUN pip3 install requests  
RUN pip3 install networkx 
RUN pip3 install tinyrpc==1.0.4 
RUN pip3 install routes 
RUN pip3 install packaging==20.9 
RUN pip3 install packaging==20.9 
RUN pip3 install ovs==2.6.0 
RUN pip3 install "msgpack>=0.4.0" 
RUN pip3 install oslo.config==2.5.0 
RUN pip3 install netaddr 
RUN pip3 install webob==1.2 
RUN apt install -y build-essential
RUN pip3 install eventlet==0.31.1


RUN rm -rf /var/lib/apt/lists/*  && touch /etc/network/interfaces
RUN apt update && apt install -y nano

ADD files/thesis-ryu/ /root/thesis-ryu/
ADD files/thesis-codes/ /root/thesis-codes/

RUN /root/thesis-codes/scripts/install.sh
RUN cd /root/thesis-ryu/ && python3.6 setup.py install

EXPOSE 6633 6653 6640
# RUN groupadd mostafa \
# && useradd -s /bin/bash -d /home/mostafa -m -p 123 -g mostafa mostafa \
# && usermod -aG sudo mostafa 