import sys
from mininet.cli import CLI

from python.lib import config
from p4app import P4Mininet
from python.controllers.fat_tree_controller import FattreeController
from python.controllers.sml_controller import SMLController
from python.topologies.fat_tree_topo import FatTreeTopo
from python.topologies.sml_topo import SMLTopo


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
        topo = FatTreeTopo()
        build_mini_net(FattreeController())
    else:
        topo = SMLTopo()
        build_mini_net(SMLController())