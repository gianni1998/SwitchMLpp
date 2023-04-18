from mininet.cli import CLI
from mininet.node import Controller

from python.lib import config
from p4app import P4Mininet

from python.controllers.single_switch_controller import SingleSwitchController
from python.topologies.single_switch_topo import SingleSwitchTopo
from python.sdn_controller import SDNController

def build_mini_net(controller, topo):
    net = P4Mininet(program="p4/main.p4", topo=topo)
    net.run_control_plane = lambda: controller.run_control_plane(net)

    c0 = net.addController(SDNController(name='c0', net=net))

    net.start()
    net.run_control_plane()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    build_mini_net(controller=SingleSwitchController(), topo=SingleSwitchTopo())