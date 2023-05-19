from typing import Dict
from mininet.net import Mininet

from python.config import SDN_CONTROLLER_IP


def mac_lookup(net: Mininet) -> Dict[str, Dict[int, str]]:
    """
    Method to generate a lookup dictionary for mac addresses
    """
    lookup = {}

    for sw in net.switches:
        if sw.name not in lookup:
            lookup[sw.name] = {}

        for k, v in sw.intfs.items():
            if sw.name != "s0" and k == 0:
                lookup[sw.name][k] = v.link.intf1.node.MAC()
            else:
                lookup[sw.name][k] = v.link.intf2.node.MAC() # for controller
    
    return lookup


def ip_lookup() -> Dict[str, Dict[int, str]]:

    lookup = {
        "s0": {0: SDN_CONTROLLER_IP, 1: "10.0.0.1", 2: "10.0.1.1"},
        "s1": {0: "10.0.2.1", 1: "10.0.0.2", 2: "10.0.0.3"},
        "s2": {0: "10.0.2.1", 1: "10.0.1.2", 2: "10.0.1.3"},
        "w0": {0: "10.0.0.1"},
        "w1": {0: "10.0.0.1"},
        "w2": {0: "10.0.0.2"},
        "w3": {0: "10.0.0.2"}
    }

    return lookup


def port_lookup(net: Mininet) -> Dict[str, Dict[str, int]]:
    """
    Method to generate a lookup dictionary for port numbers
    """
    lookup = {}

    nodes = net.switches
    nodes.extend(net.hosts)

    for node in nodes:
        if node.name not in lookup:
            lookup[node.name] = {}

        for k, v in node.intfs.items():
            if k == 0 and node.name != "s0":
                lookup[node.name][v.link.intf1.node.name] = k
            else:
                lookup[node.name][v.link.intf2.node.name] = k

    return lookup