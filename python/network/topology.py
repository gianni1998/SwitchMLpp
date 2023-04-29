from mininet.topo import Topo
from mininet.util import macColonHex

from python.sdn_controller import SDNController
from python.config import NUM_WORKERS, SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC


class Lab5Topo(Topo):

    def __init__(self, **params):
        Topo.__init__(self, **params)

        n = params.get("n", NUM_WORKERS)

        switch = self.addSwitch(name="s0")

        for i in range(1, n+1):
            wx = self.addHost(name=f"w{i-1}", ip=f"10.0.1.{i+1}", mac=f"08:00:00:00:0{i}:{i}{i}")
            self.addLink(switch, wx, port1=i, port2=0)


class SingleSwitchTopo(Topo):

    def __init__(self, **params):
        Topo.__init__(self, **params)

        n = params.get("n", NUM_WORKERS)

        switch = self.addSwitch(name="s0")

        for i in range(1, n+1):
            wx = self.addHost(name=f"w{i-1}", ip=f"10.0.1.{i+1}", mac=f"08:00:00:00:0{i}:{i}{i}")
            self.addLink(switch, wx, port1=i, port2=0)

        c0 = self.addHost(name="c0", ip=SDN_CONTROLLER_IP, mac=SDN_CONTROLLER_MAC, cls=SDNController)
        self.addLink(switch, c0, port1=0)


class TreeTopo(Topo):
    
    def __init__(self, **params):
        Topo.__init__(self, **params)

        depth = params.get("depth", 1)

        if depth > 3 or depth < 1:
            raise ValueError("Depth not supported")

        fanout = 2
        s = 1

        s0 = self.addSwitch(name="s0")
        c0 = self.addHost(name="c0", ip=SDN_CONTROLLER_IP, mac=SDN_CONTROLLER_MAC, cls=SDNController)
        self.addLink(s0, c0, port1=0)
        
        switches = [s0]
        for i in range(0, depth):
            top = switches.pop(0)
            for j in range(1, fanout+1):
                leaf = self.addSwitch(name=f"s{s}")
                s += 1

                switches.append(leaf)
                self.addLink(top, leaf, port1=j, port2=0)

        w = 0
        in_pod = 1
        pod = 0
        i = 0
        while len(switches) > 0:
            sw = switches.pop(0)

            if (in_pod >= fanout**2):
                pod += 1
                in_pod = 1
                i = 0

            for j in range(1, fanout+1):
                mac = macColonHex(w+1)
                wx = self.addHost(name=f"w{w}", ip=f"10.{pod}.{i}.{j+1}", mac=mac)
                w += 1
                in_pod += 1

                self.addLink(sw, wx, port1=j, port2=0)

            i += 1
                
