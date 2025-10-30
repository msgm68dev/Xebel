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
        s00 = self.addSwitch( 's00'  , stp=True, failMode='standalone')
        s01 = self.addSwitch( 's01'  , stp=True, failMode='standalone')
        s02 = self.addSwitch( 's02'  , stp=True, failMode='standalone')
        s03 = self.addSwitch( 's03'  , stp=True, failMode='standalone')
        s04 = self.addSwitch( 's04'  , stp=True, failMode='standalone')
        s05 = self.addSwitch( 's05'  , stp=True, failMode='standalone')
        s06 = self.addSwitch( 's06'  , stp=True, failMode='standalone')
        s07 = self.addSwitch( 's07'  , stp=True, failMode='standalone')
        s08 = self.addSwitch( 's08'  , stp=True, failMode='standalone')
        s09 = self.addSwitch( 's09'  , stp=True, failMode='standalone')
        s10 = self.addSwitch( 's10'  , stp=True, failMode='standalone')
        s11 = self.addSwitch( 's11'  , stp=True, failMode='standalone')
        s12 = self.addSwitch( 's12'  , stp=True, failMode='standalone')
        s13 = self.addSwitch( 's13'  , stp=True, failMode='standalone')
        s14 = self.addSwitch( 's14'  , stp=True, failMode='standalone')
        s15 = self.addSwitch( 's15'  , stp=True, failMode='standalone')
        s16 = self.addSwitch( 's16'  , stp=True, failMode='standalone')
        s17 = self.addSwitch( 's17'  , stp=True, failMode='standalone')
        s18 = self.addSwitch( 's18'  , stp=True, failMode='standalone')
        s19 = self.addSwitch( 's19'  , stp=True, failMode='standalone')
        s20 = self.addSwitch( 's20'  , stp=True, failMode='standalone')
        s21 = self.addSwitch( 's21'  , stp=True, failMode='standalone')
        s22 = self.addSwitch( 's22'  , stp=True, failMode='standalone')

        # Add hosts
        h00 = self.addHost( 'h00' , ip = "127.0.0.1" )
        h01 = self.addHost( 'h01' , ip = "127.0.1.1" )
        h02 = self.addHost( 'h02' , ip = "127.0.2.2" )
        h03 = self.addHost( 'h03' , ip = "127.0.3.3" )
        h04 = self.addHost( 'h04' , ip = "127.0.4.4" )
        h05 = self.addHost( 'h05' , ip = "127.0.5.5" )
        h06 = self.addHost( 'h06' , ip = "127.0.6.6" )
        h07 = self.addHost( 'h07' , ip = "127.0.7.7" )
        h08 = self.addHost( 'h08' , ip = "127.0.8.8" )
        h09 = self.addHost( 'h09' , ip = "127.0.9.9" )
        h10 = self.addHost( 'h10' , ip = "127.0.10.10" )
        h11 = self.addHost( 'h11' , ip = "127.0.11.11" )
        h12 = self.addHost( 'h12' , ip = "127.0.12.12" )
        h13 = self.addHost( 'h13' , ip = "127.0.13.13" )
        h14 = self.addHost( 'h14' , ip = "127.0.14.14" )
        h15 = self.addHost( 'h15' , ip = "127.0.15.15" )
        h16 = self.addHost( 'h16' , ip = "127.0.16.16" )
        h17 = self.addHost( 'h17' , ip = "127.0.17.17" )
        h18 = self.addHost( 'h18' , ip = "127.0.18.18" )
        h19 = self.addHost( 'h19' , ip = "127.0.19.19" )
        h20 = self.addHost( 'h20' , ip = "127.0.20.20" )
        h21 = self.addHost( 'h21' , ip = "127.0.21.21" )
        h22 = self.addHost( 'h22' , ip = "127.0.22.22" )

        # Add links (host ---  switch)
        self.addLink( h00, s00 )
        self.addLink( h01, s01 )
        self.addLink( h02, s02 )
        self.addLink( h03, s03 )
        self.addLink( h04, s04 )
        self.addLink( h05, s05 )
        self.addLink( h06, s06 )
        self.addLink( h07, s07 )
        self.addLink( h08, s08 )
        self.addLink( h09, s09 )
        self.addLink( h10, s10 )
        self.addLink( h11, s11 )
        self.addLink( h12, s12 )
        self.addLink( h13, s13 )
        self.addLink( h14, s14 )
        self.addLink( h15, s15 )
        self.addLink( h16, s16 )
        self.addLink( h17, s17 )
        self.addLink( h18, s18 )
        self.addLink( h19, s19 )
        self.addLink( h20, s20 )
        self.addLink( h21, s21 )
        self.addLink( h22, s22 )

        # Add links (switch ---  switch)
        self.addLink( s00, s03 )
        self.addLink( s00, s02 )
        self.addLink( s01, s05 )
        self.addLink( s01, s11 )
        self.addLink( s02, s11 )
        self.addLink( s02, s06 )
        self.addLink( s03, s05 )
        self.addLink( s03, s10 )
        self.addLink( s04, s11 )
        self.addLink( s04, s22 )
        self.addLink( s04, s05 )
        self.addLink( s04, s07 )
        self.addLink( s05, s21 )
        self.addLink( s05, s15 )
        self.addLink( s05, s12 )
        self.addLink( s06, s08 )
        self.addLink( s07, s09 )
        self.addLink( s07, s12 )
        self.addLink( s08, s17 )
        self.addLink( s08, s13 )
        self.addLink( s09, s12 )
        self.addLink( s10, s18 )
        self.addLink( s10, s11 )
        self.addLink( s10, s19 )
        self.addLink( s10, s17 )
        self.addLink( s11, s12 )
        self.addLink( s12, s14 )
        self.addLink( s12, s20 )
        self.addLink( s13, s16 )
        self.addLink( s14, s15 )
        self.addLink( s14, s19 )
        self.addLink( s16, s17 )
        self.addLink( s17, s20 )
        self.addLink( s17, s21 )
        self.addLink( s18, s19 )
        self.addLink( s19, s20 )
        self.addLink( s19, s22 )


topos = { 'mytopo': ( lambda: MyTopo() ) }
