import os
import subprocess
import time
import mininet
import mininet.clean
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.link import TCLink
from mininet.node import Node, OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.util import waitListening, custom

from models.topo import Fattree
from config import NUM_PORTS


class FattreeNet(Topo):
    """
	Create a fat-tree network in Mininet
	"""

    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        ft_topo = Fattree(NUM_PORTS)

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


class FattreeController:
    def __init__(self):
        self.servers = int(pow(NUM_PORTS, 3) / 4)
        self.cores = int(pow((NUM_PORTS / 2), 2))
        self.edges = int((self.servers) / (NUM_PORTS / 2))
    
    def run_workers(self, net):
        """
        Starts the workers and waits for their completion.
        Redirects output to logs/<worker_name>.log (see lib/worker.py, Log())
        This function assumes worker i is named 'w<i>'. Feel free to modify it
        if your naming scheme is different
        """
        worker = lambda rank: "w%i" % rank
        log_file = lambda rank: os.path.join(os.environ['APP_LOGS'], "%s.log" % worker(rank))
        for i in range(self.servers):
            net.get(worker(i)).sendCmd('python worker/worker.py %d > %s' % (i, log_file(i)))
        for i in range(self.servers):
            net.get(worker(i)).waitOutput()
    
    def run_control_plane(self, net):
        """
        One-time control plane configuration
        """
        pass