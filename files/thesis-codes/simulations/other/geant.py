"""Custom topology example

"""

from mininet.topo import Topo

V=23
class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

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
            hosts.append(self.addHost( 'h{}'.format(i) ))
        print(hosts)
        # Add links (host ---  switch)
        for i in range(V+1):
            if i == 0:
                continue
            self.addLink( hosts[i], switches[i] )
        print("links to hosts added :)")

        # Add links (switch ---  switch)
        self.geant(switches)
        # self.ringstar(switches)
        # self.six_zeli(switches)
        # self.ring15(switches)

    def ring15(self, switches):
        print("Adding links of topology: ring15 :)")
        for i in range(1,15):
            self.addLink( switches[i],  switches[i+1] )
        self.addLink( switches[15],  switches[1] )
    def six_zeli(self, switches):
        print("Adding links of topology: six zeli")
        self.addLink( switches[1], switches[2] )
        self.addLink( switches[1], switches[6] )
        self.addLink( switches[1], switches[7] )
        self.addLink( switches[2], switches[3] )
        self.addLink( switches[3], switches[4] )
        self.addLink( switches[3], switches[7] )
        self.addLink( switches[4], switches[5] )
        self.addLink( switches[5], switches[6] )
        self.addLink( switches[6], switches[7] )
    def geant(self, switches):
        print("Adding links of topology: geant")
        self.addLink( switches[0],   switches[1] ) # Alaki
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


    def ringstar(self, switches, siz=V):
        self.addLink( switches[0],   switches[1] ) # Alaki
        for i in range(1,siz):
            self.addLink( switches[i],   switches[siz] ) 
        for i in range(1,siz-1):
            self.addLink( switches[i],   switches[i+1] ) 
        self.addLink( switches[siz-1],   switches[1] ) 
        


topos = { 'mytopo': ( lambda: MyTopo() ) }
