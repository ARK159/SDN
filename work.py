#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink, Intf
from subprocess import call

def ping_all_hosts(net):
    hosts = net.hosts

    for host in hosts:
        # Extract the first three octets of the IP address
        ip_prefix = ".".join(host.IP().split('.')[:-1])
        target_ip = f'{ip_prefix}.1'

        result = host.cmd(f'ping -c 1 {target_ip}')
        print(result)
        
def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   )

    print( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)
    
    c1=net.addController(name='c1',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)
    
    c2=net.addController(name='c2',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    c3=net.addController(name='c3',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    print( '*** Add switches\n')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    
    r8 = net.addHost('r8', cls=Node, ip='0.0.0.0')
    r8.cmd('sysctl -w net.ipv4.ip_forward=1')
    r7 = net.addHost('r7', cls=Node, ip='0.0.0.0')
    r7.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    s10 = net.addSwitch('s10', cls=OVSKernelSwitch)
    s11 = net.addSwitch('s11', cls=OVSKernelSwitch)
    s12 = net.addSwitch('s12', cls=OVSKernelSwitch)
    
    s13 = net.addSwitch('s13', cls=OVSKernelSwitch)
    s14 = net.addSwitch('s14', cls=OVSKernelSwitch)
    s15 = net.addSwitch('s15', cls=OVSKernelSwitch)
    
    s16 = net.addSwitch('s16', cls=OVSKernelSwitch)
    

    print( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='192.168.0.3/24', defaultRoute='192.168.0.1')
    h2 = net.addHost('h2', cls=Host, ip='192.168.0.4/24', defaultRoute='192.168.0.1')
    h3 = net.addHost('h3', cls=Host, ip='192.168.0.5/24', defaultRoute='192.168.0.1')
    
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4/24', mac='00:00:00:00:00:01',defaultRoute='10.0.0.1')
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5/24', mac='00:00:00:00:00:02',defaultRoute='10.0.0.1')
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6/24', mac='00:00:00:00:00:03',defaultRoute='10.0.0.1')

    h7 = net.addHost('h7', cls=Host, ip='192.168.2.3/24', defaultRoute='192.168.2.1')
    h8 = net.addHost('h8', cls=Host, ip='192.168.2.4/24', defaultRoute='192.168.2.1')
    
    h9 = net.addHost('h9', cls=Host, ip='20.0.0.9/24', mac='00:00:00:00:00:04',defaultRoute='20.0.0.1')
    h10 = net.addHost('h10', cls=Host, ip='20.0.0.10/24', mac='00:00:00:00:00:05',defaultRoute='20.0.0.1')
    h11 = net.addHost('h11', cls=Host, ip='20.0.0.11/24', mac='00:00:00:00:00:06',defaultRoute='20.0.0.1')
    h12 = net.addHost('h12', cls=Host, ip='20.0.0.12/24', mac='00:00:00:00:00:07',defaultRoute='20.0.0.1')
    

    
    
    print( '*** Add links\n')
    
    net.addLink(s5, s4)
    net.addLink(s6, s4)
    net.addLink(s3, s5)
    net.addLink(s3,s6)
    

    
    net.addLink(s11, r8)
    net.addLink(s5, r8)
    net.addLink(s16,r8)
    net.addLink(r7, s6)
    net.addLink(r7, s13)
    
   
    net.addLink(s10, s11)
    net.addLink(s11, s12)
    net.addLink(s10, h4)
    net.addLink(s11, h5)
    net.addLink(s12, h6)
    net.addLink(s4, h10)
    net.addLink(s4, h9)
    net.addLink(h11, s3)
    net.addLink(h12, s3)
    
    net.addLink(h1, s16)
    net.addLink(h2, s16)
    net.addLink(h3, s16)
    
    net.addLink(s14, h8)
    net.addLink(s15, h7)
    
    net.addLink(s13, s15)
    net.addLink(s13, s14)
    net.addLink(s14, s15)


    print( '*** Starting network\n')
    net.build()
    r8.cmd('ip addr add 10.0.0.1/24 dev r8-eth0')
    r8.cmd('ip addr add 20.0.0.1/24 dev r8-eth1')
    r8.cmd('ip addr add 192.168.0.1/24 dev r8-eth2')
    r7.cmd('ip addr add 20.0.0.2/24 dev r7-eth0')
    r7.cmd('ip addr add 192.168.2.1/24 dev r7-eth1')
    
    
    
    h4.cmd('sudo route add default gw 10.0.0.1')
    h5.cmd('sudo route add default gw 10.0.0.1')
    h6.cmd('sudo route add default gw 10.0.0.1')
    
    h9.cmd('sudo route add default gw 20.0.0.1')
    h10.cmd('sudo route add default gw 20.0.0.1')
    h11.cmd('sudo route add default gw 20.0.0.1')
    h12.cmd('sudo route add default gw 20.0.0.1')
    # h9.cmd('sudo ip route add 192.168.2.0/24 via 20.0.0.2')
    # h10.cmd('sudo ip route add 192.168.2.0/24 via 20.0.0.2')
    # h11.cmd('sudo ip route add 192.168.2.0/24 via 20.0.0.2')
    # h12.cmd('sudo ip route add 192.168.2.0/24 via 20.0.0.2')
    
    h1.cmd('sudo route add default gw 192.168.0.1')
    h2.cmd('sudo route add default gw 192.168.0.1')
    h3.cmd('sudo route add default gw 192.168.0.1')
    
    h7.cmd('sudo route add default gw 192.168.2.1')
    h8.cmd('sudo route add default gw 192.168.2.1')
    
    r8.cmd('sudo route add default gw 20.0.0.2')
    r7.cmd('sudo route add default gw 20.0.0.1')
    
    
   
    
    
    print( '*** Starting controllers\n')
    # for controller in net.controllers:
        # controller.start()

    print( '*** Starting switches\n')
    
    
    net.get('s4').start([c3])
    net.get('s5').start([c3])
    net.get('s6').start([c3])
    net.get('s3').start([c3])
    
    net.get('s10').start([c1])
    net.get('s11').start([c1])
    net.get('s12').start([c1])
    
    net.get('s16').start([c0])
    
    net.get('s13').start([c2])
    net.get('s14').start([c2])
    net.get('s15').start([c2])

    print( '*** Post configure switches and hosts\n')
    # net.pingAll(
    ping_all_hosts(net)
   
    CLI(net)
    
    
if __name__=="__main__":
    myNetwork()
