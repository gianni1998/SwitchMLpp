from dataclasses import dataclass
from typing import List, Dict

from python.lib.p4app.src.p4_mininet import P4RuntimeSwitch

@dataclass
class SwitchConnectionInfo:

    connection: P4RuntimeSwitch
    """Connection to the switch"""

    mgids: List[int]
    """List of aggregation/multicast ids present on the switch"""

    mg_ports: Dict[int, List[int]]
    """Dictionary containing all ports of a multicast group"""

    connected_ip: List[str]
    """IP list of connected SML workers"""

    next_step: Dict[int, int]
    """Dictrionaty containing the next step of a switch"""

    def __init__(self, connection):
        self.connection = connection
        self.mgids = []
        self.mg_ports = {}
        self.connected_ip = []
        self.next_step = {}



@dataclass
class SwitchMLInfo:
    parents: Dict[str, int]
    """Connected parent nodes Dict[Name, port]"""

    children: Dict[str, int]
    """Connected child nodes Dict[Name, port]"""