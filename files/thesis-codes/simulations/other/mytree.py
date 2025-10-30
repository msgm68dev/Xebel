"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""
#stp_mode = True;
stp_mode = False;

from mininet.topo import Topo

class MyTree( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        s1 = self.addSwitch ( 's1' , stp=stp_mode, failMode='standalone')
        s2 = self.addSwitch ( 's2' , stp=stp_mode, failMode='standalone')
        s3 = self.addSwitch ( 's3' , stp=stp_mode, failMode='standalone')
        h1 = self.addHost   ( 'h1' , ip = "12.1.0.1/24" )
        h2 = self.addHost   ( 'h2' , ip = "12.2.0.2/24" )
        h3 = self.addHost   ( 'h3' , ip = "12.3.0.3/24" )
        h4 = self.addHost   ( 'h4' , ip = "12.4.0.4/24" )

        # Add links
        self.addLink( s1, s2 )
        self.addLink( s1, s3 )
        self.addLink( s2, h1 )
        self.addLink( s2, h2 )
        self.addLink( s3, h3 )
        self.addLink( s3, h4 )

        # self.addLink( h1, h4 )

topos = { 'mytopo': ( lambda: MyTree() ) }
