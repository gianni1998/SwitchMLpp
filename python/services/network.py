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
            if v.link.intf1.node.name is sw.name:
                lookup[sw.name][k] = v.link.intf2.node.MAC()
            else:
                lookup[sw.name][k] = v.link.intf1.node.MAC()
    
    return lookup


def port_lookup(net: Mininet) -> Dict[str, Dict[str, int]]:
    """
    Method to generate a lookup dictionary for port numbers
    """
    lookup = {}

    nodes = net.nameToNode.values()

    for node in nodes:
        if node.name not in lookup:
            lookup[node.name] = {}

        for k, v in node.intfs.items():
            if k == 0 and node.name != "s0":
                lookup[node.name][v.link.intf1.node.name] = k
            else:
                lookup[node.name][v.link.intf2.node.name] = k

    return lookup
