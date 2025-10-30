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
        s0 = self.addSwitch( 's0'  , stp=True, failMode='standalone')
        s1 = self.addSwitch( 's1'  , stp=True, failMode='standalone')
        s2 = self.addSwitch( 's2'  , stp=True, failMode='standalone')
        s3 = self.addSwitch( 's3'  , stp=True, failMode='standalone')
        s4 = self.addSwitch( 's4'  , stp=True, failMode='standalone')

        # Add hosts
        h0 = self.addHost( 'h0' , ip = "127.0.0.1" )
        h1 = self.addHost( 'h1' , ip = "127.0.1.1" )
        h2 = self.addHost( 'h2' , ip = "127.0.2.1" )
        h3 = self.addHost( 'h3' , ip = "127.0.3.1" )
        h4 = self.addHost( 'h4' , ip = "127.0.4.1" )

        # Add links (host ---  switch)
        self.addLink( h0, s0 )
        self.addLink( h1, s1 )
        self.addLink( h2, s2 )
        self.addLink( h3, s3 )
        self.addLink( h4, s4 )

        # Add links (switch ---  switch)
        self.addLink( s0, s1 )
        self.addLink( s0, s2 )
        self.addLink( s0, s3 )
        self.addLink( s1, s4 )
        self.addLink( s2, s3 )
        self.addLink( s2, s4 )
        self.addLink( s3, s4 )


topos = { 'mytopo': ( lambda: MyTopo() ) }
