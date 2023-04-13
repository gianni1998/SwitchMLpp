from mininet.topo import Topo

from python.config import NUM_PORTS
from python.models.fat_tree import FatTree


class FatTreeTopo(Topo):
    """
	Create a fat-tree network in Mininet
	"""

    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        ft_topo = FatTree(NUM_PORTS)

        servers = {server.id: self.addHost(name=f"w{i-1}", ip=server.id, mac=f"08:00:00:00:0{i}:{i}{i}") for i, server in enumerate(ft_topo.servers)}
        switches = {switch.id: self.addSwitch(name=f"s{i+1}") for i, switch in enumerate(ft_topo.switches)}

        items = servers
        items.update(switches)

        exists = []

        for switch in ft_topo.switches:
            for edge in switch.edges:
                pair = (items[edge.lnode.id], items[edge.rnode.id])
                if pair not in exists:
                    exists.append(pair)
                    self.addLink(pair[0], pair[1], bw=15, delay='5ms')