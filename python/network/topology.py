from mininet.topo import Topo
from mininet.util import macColonHex

from python.sdn_controller import SDNController
from python.config import NUM_WORKERS, SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC, TREE_DEPTH, TREE_FANOUT


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

        self.s = 0
        self.leafs = []

        depth = params.get("depth", TREE_DEPTH)
        fanout = params.get("fanout", TREE_FANOUT)

        if depth > 3 or depth < 1:
            raise ValueError("Depth not supported")
        
        self.__add_tree(depth=depth-1, fanout=fanout)

        s0 = self.addSwitch(name="s0")
        c0 = self.addHost(name="c0", ip=SDN_CONTROLLER_IP, mac=SDN_CONTROLLER_MAC, cls=SDNController)
        self.addLink(s0, c0, port1=0)

        w, i, pod, in_pod = 0, 0, 0, 1 

        while len(self.leafs) > 0:
            sw = self.leafs.pop(0)

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
    

    def __add_tree(self, depth, fanout):
        node = self.addSwitch(name=f"s{self.s}")
        self.s += 1

        if depth > 0:
            for i in range(1, fanout+1):
                leaf = self.__add_tree( depth - 1, fanout )
                self.addLink(node, leaf, port1=i, port2=0)
        else:
            self.leafs.append(node)

        return node
                
