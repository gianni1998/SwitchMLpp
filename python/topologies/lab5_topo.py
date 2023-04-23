from mininet.topo import Topo

from python.config import NUM_WORKERS
from python.sdn_controller import SDNController
from python.config import SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC

class Lab5Topo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        switch = self.addSwitch(name="s0")

        for i in range(1, NUM_WORKERS+1):
            wx = self.addHost(name=f"w{i-1}", ip=f"10.0.0.{i}", mac=f"08:00:00:00:0{i}:{i}{i}")
            self.addLink(switch, wx, port1=i, port2=0)
        