import socket
import threading
import ast
from typing import Dict, List
from mininet.net import Mininet

from python.lib.p4app.src.p4_mininet import P4Host, P4RuntimeSwitch

from python.config import SDN_CONTROLLER_PORT, BUFFER_SIZE
from python.models.tree import Tree, SMLNode
from python.models.packet import SubscriptionPacket
from python.services.network import port_lookup
from python.services.tree import get_mst, find_lca, shortest_path


class SDNController(P4Host):
    """
    Class that simulates an SDN controller for a P4 switch
    """

    port_lookup: Dict[str, Dict[str, int]]
    "Look up dictionary for port numbers"
    net: Mininet
    "Mininet object of the network"
    mst: Tree
    "Minimal spanning tree of the network"
    garden_of_eden: Dict[int, Tree]
    "Dictionary holding the Tree's of life"
    connections: Dict[str, P4RuntimeSwitch]
    "Dictionary holding connections to switches in the network"

    def __init__(self, name, **params):
        """
        Constructor
        """
        P4Host.__init__(self, name, **params)

        self.mst = None
        self.connections = {}

        self.garden_of_eden = {}

    def set_net(self, net: Mininet):
        """
        Method to set Mininet object that is used for the switch connections
        """
        self.net = net
        self.mst = get_mst(self.net)
        self.port_lookup = port_lookup(net)

    def start(self) -> None:
        """
        Method to start the controller
        """
        while 1:
            out = self.cmd("python -m python.services.tcp_server")
            #out = self.cmd("nc -l -p 5005")
            #print("Tjupapi: " + out)

            thread = threading.Thread(target=self._client_thread, args=(out,))
            thread.start()

    def _client_thread(self, data) -> None:
        """
        Method that handles the establised tcp connection with a worker
        """
        pkt = SubscriptionPacket(ast.literal_eval(data))
        rank = pkt[SubscriptionPacket].rank
        mgid = pkt[SubscriptionPacket].mgid
        sub = pkt[SubscriptionPacket].type

    #def test5(self, rank: int, mgid: int, sub: bool) -> None:
        wx = f"w{rank}"

        tree = self.garden_of_eden.get(mgid, None)
        if not sub and (tree is None or not tree.node_exists(wx)):
            return

        if sub and tree is not None and tree.node_exists(wx):
            return

        if mgid not in self.garden_of_eden or self.garden_of_eden[mgid].num_nodes == 0:
            tree = self.garden_of_eden[mgid] = Tree()
            path = [wx, self.mst.get_node(wx).parent.name]

            self.expand_tree(tree=tree, path=path, mgid=mgid)

        else:
            tree = self.garden_of_eden[mgid]
            root = tree.root.name

            lca = find_lca(tree=self.mst, src=wx, dst=root)

            if lca != root and sub:
                right = shortest_path(self.mst, src=root, dst=lca)
                self.expand_tree(tree=tree, path=right, mgid=mgid)

            left = shortest_path(self.mst, src=wx, dst=lca)
            if sub:
                self.expand_tree(tree=tree, path=left, mgid=mgid)
            else:
                tree.shrink_tree(path=left)
                tree.top_tree()

        tree.set_root()

    def expand_tree(self, tree: Tree, path: List[str], mgid: int) -> None:
        """
        Method that expands a based on a given path
        @param tree: Tree that needs to be expended
        @param path: The given path
        @param mgid: Multicast group ID
        """
        prev = None

        for hop in path:
            if not tree.node_exists(name=hop):
                node = self.mst.get_node(name=hop)
                tree.add_node(node=SMLNode(name=hop,
                                           conn=None if node.is_worker() else self.__get_connection(name=hop),
                                           mgid=mgid,
                                           ip=node.ip,
                                           mac=node.mac))

            node = tree.get_node(name=hop)

            if prev is not None:
                node.add_child(child=prev, portc=self.port_lookup[node.name][prev.name],
                               portp=self.port_lookup[prev.name][node.name])

            prev = node

    def __get_connection(self, name: str) -> P4RuntimeSwitch:
        """
        Get switch connection by switch name
        @param name: string with the name of the switch
        @return: P4RuntimeSwitch object that represents a switch connection
        """
        if name not in self.connections:
            self.connections[name] = self.net.get(name)

        return self.connections[name]
