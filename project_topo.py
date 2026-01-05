from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def secure_infra_ha():
    net = Mininet( controller=Controller, switch=OVSKernelSwitch, link=TCLink )
    net.addController( 'c0' )

    info( '*** Adding Switches\n' )
    s_wan = net.addSwitch( 's1' )
    s_dmz = net.addSwitch( 's2' )
    s_lan = net.addSwitch( 's3' )

    info( '*** Adding Routers (Cluster HA)\n' )
    # R1 (Master) - IP Physique .252
    r1 = net.addHost( 'r1', ip='192.168.100.252/24' )
    # R2 (Backup) - IP Physique .253
    r2 = net.addHost( 'r2', ip='192.168.100.253/24' )

    info( '*** Adding Hosts\n' )
    # Les hôtes pointent vers la VIP (.254) comme passerelle par défaut
    h_ext = net.addHost( 'h_ext', ip='192.168.100.1/24', defaultRoute='via 192.168.100.254' )
    h_web = net.addHost( 'h_web1', ip='10.0.1.1/24', defaultRoute='via 10.0.1.254' )
    h_admin = net.addHost( 'h_admin', ip='10.0.2.1/24', defaultRoute='via 10.0.2.254' )

    info( '*** Creating Links\n' )
    # WAN
    net.addLink( h_ext, s_wan )
    net.addLink( s_wan, r1, intfName2='r1-eth0', params2={'ip':'192.168.100.252/24'} )
    net.addLink( s_wan, r2, intfName2='r2-eth0', params2={'ip':'192.168.100.253/24'} )

    # DMZ
    net.addLink( h_web, s_dmz )
    net.addLink( s_dmz, r1, intfName2='r1-eth1', params2={'ip':'10.0.1.252/24'} )
    net.addLink( s_dmz, r2, intfName2='r2-eth1', params2={'ip':'10.0.1.253/24'} )

    # LAN
    net.addLink( h_admin, s_lan )
    net.addLink( s_lan, r1, intfName2='r1-eth2', params2={'ip':'10.0.2.252/24'} )
    net.addLink( s_lan, r2, intfName2='r2-eth2', params2={'ip':'10.0.2.253/24'} )

    info( '*** Starting network\n' )
    net.start()
    
    # Activation du routage
    r1.cmd("sysctl -w net.ipv4.ip_forward=1")
    r2.cmd("sysctl -w net.ipv4.ip_forward=1")

    # --- SETUP INITIAL (VIP sur R1) ---
    info( '*** Starting Heartbeat (Simulated VIP on R1)\n' )
    # On ajoute l'IP Virtuelle (.254) sur R1 pour commencer
    r1.cmd("ip addr add 192.168.100.254/24 dev r1-eth0")
    r1.cmd("ip addr add 10.0.2.254/24 dev r1-eth2")
    
    # On lance une fausse invite pour garder le terminal ouvert
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    secure_infra_ha()
