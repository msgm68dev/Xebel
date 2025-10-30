"""Custom topology example

"""

from mininet.topo import Topo
import sys

existing_topos = { 
    1 : 'ring',
    2 : 'wheel',
    3 : 'geant' 
}
def input_topo():
    for k in existing_topos:
        print("{} {}".format(k, existing_topos[k]))
    try:
        t=int(input("Enter topology: "))
        if t not in existing_topos:
            raise
    except:
        print("wrong topology number!")
        print("exeiting...")
        exit(1)
    topo_name = existing_topos[t]
    if topo_name == 'geant':
        V = 23
    else:
        v = input("Enter number of switches: ")
        try:
            V = int(v)
            assert V > 1
        except:
            print("Wrong number!")
            print("exiting...")
            exit(1)
    return V, topo_name
V, topo_name = input_topo()
class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self  ):
        "Create custom topo."
        print("\n *** V={} ***\n\n".format(V))
        # Initialize topology
        Topo.__init__( self )
        switches = []
        hosts = []
        # Add switches
        for i in range(V+1):
            switches.append(self.addSwitch( 's{}'.format(i)  ))
        print(switches)
        # Add hosts
        for i in range(V+1):
            nam = 'h{}'.format(i) 
            # ip = '10.{}.{}.2/24'.format(str(i/100), str(i%100))
            # mac = '00:00:00:00:{}:{}'.format(str(i/100).zfill(2), str(i%100).zfill(2))
            # host = self.addHost( nam, ip = ip, mac = mac)
            host = self.addHost( nam )
            hosts.append(host)
        print("Hosts created!: {}".format(hosts))
        # Add links (host ---  switch)
        for i in range(V+1):
            if i == 0:
                continue
            self.addLink( hosts[i], switches[i] )
        print("links to hosts added :)")
        # Add links (switch ---  switch)
        topo2func = {
            "ring" : self.ring,
            "wheel" : self.wheel,
            "geant" : self.geant
        }
        func = topo2func[topo_name]
        func(switches)
    def ring(self, switches, siz=V):
        print(" *** Adding links of topology: ring-{}".format(siz))
        # self.addLink( switches[0],   switches[1] ) # Alaki
        for i in range(1,siz):
            self.addLink( switches[i],   switches[i+1] ) 
        self.addLink( switches[siz],   switches[1] ) 
    def wheel(self, switches, siz=V):
        print(" *** Adding links of topology: wheel-{}".format(siz))
        # self.addLink( switches[0],   switches[1] ) # Alaki
        for i in range(1,siz):
            self.addLink( switches[i],   switches[siz] ) 
        for i in range(1,siz-1):
            self.addLink( switches[i],   switches[i+1] ) 
        self.addLink( switches[siz-1],   switches[1] ) 
    def geant(self, switches):
        print(" *** Adding links of topology: geant")
        # self.addLink( switches[0],   switches[1] ) # Alaki
        self.addLink( switches[1],   switches[3] )
        self.addLink( switches[1],   switches[4] )
        self.addLink( switches[2],   switches[6] )
        self.addLink( switches[2],   switches[12] )
        self.addLink( switches[3],   switches[7] )
        self.addLink( switches[3],   switches[12] )
        self.addLink( switches[4],   switches[6] )
        self.addLink( switches[4],   switches[11] )
        self.addLink( switches[5],   switches[6] )
        self.addLink( switches[5],   switches[8] )
        self.addLink( switches[5],   switches[12] )
        self.addLink( switches[5],   switches[23] )
        self.addLink( switches[6],   switches[13] )
        self.addLink( switches[6],   switches[16] )
        self.addLink( switches[6],   switches[22] )
        self.addLink( switches[7],   switches[9] )
        self.addLink( switches[8],   switches[10] )
        self.addLink( switches[8],   switches[13] )
        self.addLink( switches[9],   switches[14] )
        self.addLink( switches[9],   switches[18] )
        self.addLink( switches[10],  switches[13] )
        self.addLink( switches[11],  switches[12] )
        self.addLink( switches[11],  switches[18] )
        self.addLink( switches[11],  switches[19] )
        self.addLink( switches[11],  switches[20] )
        self.addLink( switches[12],  switches[13] )
        self.addLink( switches[13],  switches[15] )
        self.addLink( switches[13],  switches[21] )
        self.addLink( switches[14],  switches[17] )
        self.addLink( switches[15],  switches[16] )
        self.addLink( switches[15],  switches[20] )
        self.addLink( switches[17],  switches[18] )
        self.addLink( switches[18],  switches[21] )
        self.addLink( switches[18],  switches[22] )
        self.addLink( switches[19],  switches[20] )
        self.addLink( switches[20],  switches[21] )
        self.addLink( switches[20],  switches[23] )
topos = { 'mytopo': ( lambda: MyTopo() ) }
