
from mininet.topo import Topo

L = 8
class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )
        
	
        switches = []
        hosts = []
        # Add switches
        # dummy_switch = self.addSwitch( 's0' ) #Get rid of large dpid
        # dummy_host = self.addHost( 'h0' )
        for i in range(1,L+1):
            switches.append(self.addSwitch( 's{}'.format(i) ))
            print(switches)
        # Add hosts
        for i in range(1,L+1):
            print(hosts)
            hosts.append(self.addHost( 'h{}'.format(i) ))
        # Add links (host ---  switch)
        for i in range(0,L):
            self.addLink( hosts[i], switches[i] )
            print('link ' + str(i))
        print("h <-->s DONE")
        # Add links (switch ---  switch)
        for i in range(0,L-1):
            print('Link ' + str(i))
            self.addLink( switches[i], switches[i+1] )
        print("s <-->s DONE")
        self.addLink( switches[-1], switches[0] ) #CIRCLE
        self.addLink( switches[0], switches[len(switches)/2] ) #Ghotr

topos = { 'mytopo': ( lambda: MyTopo() ) }
