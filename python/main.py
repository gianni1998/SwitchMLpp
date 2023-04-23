from mininet.cli import CLI

import python.lib.config
from python.lib.p4app.src.p4app import P4Mininet
from python.controllers.single_switch_controller import SingleSwitchController
from python.controllers.lab5_controller import Lab5Controller
from python.topologies.single_switch_topo import SingleSwitchTopo


def build_mini_net(controller, topo):
    net = P4Mininet(program="p4/main.p4", topo=topo)
    net.run_control_plane = lambda: controller.run_control_plane(net)

    c0 = net.get("c0")
    c0.net = net

    net.start()
    net.run_control_plane()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    build_mini_net(controller=SingleSwitchController(), topo=SingleSwitchTopo())
    #build_mini_net(controller=Lab5Controller(), topo=SingleSwitchTopo())