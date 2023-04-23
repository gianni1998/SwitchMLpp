from mininet.topo import Topo
from mininet.link import TCLink

from python.config import NUM_WORKERS
from python.sdn_controller import SDNController
from python.config import SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC

class SingleSwitchTopo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        switch = self.addSwitch(name="s0")

        for i in range(1, NUM_WORKERS+1):
            wx = self.addHost(name=f"w{i-1}", ip=f"10.0.0.{i}", mac=f"08:00:00:00:0{i}:{i}{i}", inNamespace=True)
            self.addLink(switch, wx, port1=i, port2=0)

        c0 = self.addHost(name="c0", ip=SDN_CONTROLLER_IP, mac=SDN_CONTROLLER_MAC, inNamespace=True, cls=SDNController)
        self.addLink(switch, c0, port1=0)

        