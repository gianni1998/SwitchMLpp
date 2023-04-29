from mininet.cli import CLI
from mininet.topo import Topo

import python.lib.config
from python.lib.p4app.src.p4app import P4Mininet
from python.network.topology import Lab5Topo, SingleSwitchTopo, TreeTopo
from python.network.configuration import TopoConfig, Lab5Config, SingleSwitchConfig, TreeTopoConfig


def build_mini_net(config: TopoConfig, topo: Topo, use_sdn: bool):
    net = P4Mininet(program="p4/main.p4", topo=topo)
    net.run_control_plane = lambda: config.run_control_plane(net)

    if use_sdn:
        c0 = net.get("c0")
        c0.set_net(net)

    net.start()
    net.run_control_plane()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    build_mini_net(config=TreeTopoConfig(), topo=TreeTopo(), use_sdn=True)
    #build_mini_net(config=SingleSwitchConfig(), topo=SingleSwitchTopo(), use_sdn=True)
    #build_mini_net(config=Lab5Config(), topo=Lab5Topo(), use_sdn=False)