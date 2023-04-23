from dataclasses import dataclass
from typing import List, Dict

from python.lib.p4app.src.p4_mininet import P4RuntimeSwitch

@dataclass
class SwitchConnection:

    connection: P4RuntimeSwitch
    """Connection to the switch"""

    mgids: List[int]
    """List of aggregation/multicast ids present on the switch"""

    mg_ports: Dict[int, List[int]]
    """Dictionary containing all ports of a multicast group"""
    