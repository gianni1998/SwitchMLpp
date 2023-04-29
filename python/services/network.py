from typing import Dict
from mininet.net import Mininet


def generate_mac_lookup(net: Mininet) -> Dict[str, Dict[int, str]]:
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