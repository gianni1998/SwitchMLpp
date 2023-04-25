from mininet.cli import CLI
from mininet.topo import Topo

import python.lib.config
from python.lib.p4app.src.p4app import P4Mininet
from python.network.topology import Lab5Topo, SingleSwitchTopo
from python.network.controller import TopoController, Lab5Controller, SingleSwitchController


def build_mini_net(controller: TopoController, topo: Topo):
    net = P4Mininet(program="p4/main.p4", topo=topo)
    net.run_control_plane = lambda: controller.run_control_plane(net)

    # c0 = net.get("c0")
    # c0.net = net

    net.start()
    net.run_control_plane()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    #build_mini_net(controller=SingleSwitchController(), topo=SingleSwitchTopo())
    build_mini_net(controller=Lab5Controller(), topo=Lab5Topo())