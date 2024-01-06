#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   )

    info( '*** Adding controller\n' )
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

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    r7 = net.addHost('r7', cls=Node, ip='0.0.0.0')
    r7.cmd('sysctl -w net.ipv4.ip_forward=1')
    r8 = net.addHost('r8', cls=Node, ip='0.0.0.0')
    r8.cmd('sysctl -w net.ipv4.ip_forward=1')
    s10 = net.addSwitch('s10', cls=OVSKernelSwitch)
    s11 = net.addSwitch('s11', cls=OVSKernelSwitch)
    s12 = net.addSwitch('s12', cls=OVSKernelSwitch)
    s13 = net.addSwitch('s13', cls=OVSKernelSwitch)
    s14 = net.addSwitch('s14', cls=OVSKernelSwitch)
    s15 = net.addSwitch('s15', cls=OVSKernelSwitch)
    s16 = net.addSwitch('s16', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='192.168.0.3', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='192.168.0.4', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='192.168.0.5', defaultRoute=None)
    
    h4 = net.addHost('h4', cls=Host, ip='192.168.1.3/24', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='192.168.1.9/24', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='192.168.1.13/24', defaultRoute=None)
    
    h7 = net.addHost('h7', cls=Host, ip='192.168.1.3', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='192.168.2.3', defaultRoute=None)
    
    h9 = net.addHost('h9', cls=Host, ip='10.0.0.9/24', defaultRoute=None)
    h10 = net.addHost('h10', cls=Host, ip='10.0.0.10/24', defaultRoute=None)
    h11 = net.addHost('h11', cls=Host, ip='10.0.0.11/24', defaultRoute=None)
    h12 = net.addHost('h12', cls=Host, ip='10.0.0.12/24', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s5, s1)
    net.addLink(s5, s2)
    net.addLink(s1, s3)
    net.addLink(s3, s6)
    net.addLink(s6, s4)
    net.addLink(s2, s4)
    net.addLink(s1, s4)
    net.addLink(s3, s2)
    net.addLink(r8, s5)
    net.addLink(r7, s6)
    net.addLink(r8, s11)
    net.addLink(s10, s11)
    net.addLink(s11, s12)
    net.addLink(s13, s15)
    net.addLink(s13, s14)
    net.addLink(s14, s15)
    net.addLink(r7, s13)
    net.addLink(h1, s16)
    net.addLink(h2, s16)
    net.addLink(h3, s16)
    net.addLink(s16, r8)
    net.addLink(s10, h4)
    net.addLink(s11, h5)
    net.addLink(s12, h6)
    net.addLink(s14, h8)
    net.addLink(s15, h7)
    net.addLink(s4, h10)
    net.addLink(s4, h9)
    net.addLink(h11, s1)
    net.addLink(h12, s3)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    # for controller in net.controllers:
    #     controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c3])
    net.get('s2').start([c3])
    net.get('s3').start([c3])
    net.get('s4').start([c3])
    net.get('s5').start([c3])
    net.get('s6').start([c3])
    net.get('s10').start([c1])
    net.get('s11').start([c1])
    net.get('s12').start([c1])
    net.get('s13').start([c2])
    net.get('s14').start([c2])
    net.get('s15').start([c2])
    net.get('s16').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)

if __name__=="__main__":
    myNetwork()
