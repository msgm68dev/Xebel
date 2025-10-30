"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add switches
        s0 = self.addSwitch( 's0'  , stp=True)
        s1 = self.addSwitch( 's1'  , stp=True)
        s2 = self.addSwitch( 's2'  , stp=True)
        s3 = self.addSwitch( 's3'  , stp=True)
        s4 = self.addSwitch( 's4'  , stp=True)

        # Add hosts
        h0 = self.addHost( 'h0' , ip = "10.0.0.1" )
        h1 = self.addHost( 'h1' , ip = "10.0.1.1" )
        h2 = self.addHost( 'h2' , ip = "10.0.2.1" )
        h3 = self.addHost( 'h3' , ip = "10.0.3.1" )
        h4 = self.addHost( 'h4' , ip = "10.0.4.1" )

        # Add links (host ---  switch)
        self.addLink( h0, s0 )
        self.addLink( h1, s1 )
        self.addLink( h2, s2 )
        self.addLink( h3, s3 )
        self.addLink( h4, s4 )

        # Add links (switch ---  switch)
        self.addLink( s0, s1 , bw=2, delay=10000 ) #nano second
        self.addLink( s0, s2 , bw=2, delay=10000 )
        self.addLink( s0, s3 , bw=2, delay=10000 )
        self.addLink( s1, s4 , bw=2, delay=10000 )
        self.addLink( s2, s3 , bw=2, delay=10000 )
        self.addLink( s2, s4 , bw=2, delay=10000 )
        self.addLink( s3, s4 , bw=2, delay=10000 )


topos = { 'mytopo': ( lambda: MyTopo() ) }