from mininet.topo import Topo

from python.sdn_controller import SDNController
from python.config import NUM_WORKERS, SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC


class Lab5Topo(Topo):

    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        n = opts.get("n", NUM_WORKERS)

        switch = self.addSwitch(name="s0")

        for i in range(1, n+1):
            wx = self.addHost(name=f"w{i-1}", ip=f"10.0.1.{i+1}", mac=f"08:00:00:00:0{i}:{i}{i}")
            self.addLink(switch, wx, port1=i, port2=0)


class SingleSwitchTopo(Topo):

    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        n = opts.get("n", NUM_WORKERS)

        switch = self.addSwitch(name="s0")

        for i in range(1, n+1):
            wx = self.addHost(name=f"w{i-1}", ip=f"10.0.1.{i+1}", mac=f"08:00:00:00:0{i}:{i}{i}")
            self.addLink(switch, wx, port1=i, port2=0)

        c0 = self.addHost(name="c0", ip=SDN_CONTROLLER_IP, mac=SDN_CONTROLLER_MAC, cls=SDNController)
        self.addLink(switch, c0, port1=0)
