import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from lib import config
from p4app import P4Mininet
from mininet.cli import CLI

from fat_tree import FattreeNet, FattreeController
from sml_topo import SMLTopo, SMLController


def build_mini_net(controller):
    net = P4Mininet(program="p4/main.p4", topo=topo)
    net.run_control_plane = lambda: controller.run_control_plane(net)
    net.run_workers = lambda: controller.run_workers(net)
    net.start()
    net.run_control_plane()
    CLI(net)
    net.stop()


if __name__ == '__main__': 
    selected_topo = sys.argv[1]

    if selected_topo == "Fattree":
        topo = FattreeNet()
        build_mini_net(FattreeController())
    else:
        topo = SMLTopo()
        build_mini_net(SMLController())

    