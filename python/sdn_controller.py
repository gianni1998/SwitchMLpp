import socket
import threading
import networkx as nx
from typing import Dict, List
from mininet.net import Mininet

from python.lib.p4app.src.p4_mininet import P4Host, P4RuntimeSwitch

from python.config import SDN_CONTROLLER_PORT, BUFFER_SIZE
from python.models.tree import Tree
from python.services.network import port_lookup
from python.services.tree import get_mst, find_lca, shortest_path
from python.services.switch import sml_entry, next_step_entry, num_workers_entry


class SDNController(P4Host):
    """
    Class that simulates an SDN controller for a P4 switch
    """
    g: nx.Graph
    net: Mininet
    workers_in_group: Dict[int, List[str]]
    port_lookup: Dict[str, Dict[str, int]]

    mst: Tree
    """Minimal spanning tree of the network"""
    garden_of_eden: Dict[int, Tree]
    """Dictionary holding the Tree's of life"""
    connections: Dict[str, P4RuntimeSwitch]
    """Dictionary holding connections to switches in the network"""

    def __init__(self, name, **params):
        """
        Constructor
        """
        P4Host.__init__(self, name, **params)

        self.ip_lookup = None
        self.mst = None
        self.connections = {}
        self.workers_in_group = {}

        self.garden_of_eden = {}

    def set_net(self, net: Mininet):
        """
        Method to set Mininet object that is used for the switch connections
        """
        self.net = net
        self.mst = get_mst(self.net)
        self.port_lookup = port_lookup(net)

    def start(self):
        """
        Method to open a tcp connection and listen for incomming traffic
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # s.setsockopt(socket.SOL_SOCKET, 25, str("eth0" + '\0').encode('utf-8'))

            s.bind(("", SDN_CONTROLLER_PORT))
            s.listen()

            while 1:
                conn, addr = s.accept()

                print(conn)
                print(addr)

                thread = threading.Thread(target=self._client_thread, args=(conn, addr))
                thread.start()

    def _client_thread(self, conn, addr):
        """
        Method that handles the establised tcp connection with a worker
        """
        data = b''
        while 1:
            chunk = conn.recv(BUFFER_SIZE)

            if not chunk:
                break
            data += chunk

            conn.sendall(data)
        conn.close()

        self._process(data, addr)

    # def _process(data, addr):
    def test5(self, rank: int, mgid: int, sub: bool) -> None:
        wx = f"w{rank}"

        # group = self.workers_in_group.get(mgid, None)
        # if group is not None and wx in group and sub:
        #     return
        #
        # if (group is not None and not sub) or (wx not in group and not sub):
        #     return

        if mgid not in self.garden_of_eden:
            tree = self.garden_of_eden[mgid] = Tree()
            path = [wx, self.mst.get_node(wx).parent.name]

            self.expand_tree(tree=tree, path=path, mgid=mgid)

        else:
            tree = self.garden_of_eden[mgid]
            root = tree.get_root().name

            lca = find_lca(tree=self.mst, src=wx, dst=root)

            if lca != root and sub:
                right = shortest_path(self.mst, src=root, dst=lca)
                print(f"src: {root}, dst: {lca} - {right}")
                self.expand_tree(tree=tree, path=right, mgid=mgid)

            left = shortest_path(self.mst, src=wx, dst=lca)
            print(f"src: {wx}, dst: {lca} - {left}")
            if sub:
                self.expand_tree(tree=tree, path=left, mgid=mgid)
            else:
                self.shrink_tree(tree=tree, path=left, mgid=mgid)
                print("Snap tree")
                self.thanos(tree=tree, mgid=mgid)

        tree.set_root()

    def expand_tree(self, tree: Tree, path: List[str], mgid: int):
        prev = None
        for name in path:
            if not tree.node_exists(name=name):
                node = self.mst.get_node(name=name).copy()
                tree.add_node(node=node)

                if not node.is_wroker():
                    next_step_entry(conn=self.__get_connection(name=name), mgid=mgid, step=0, port=0, insert=True)

            curr = tree.get_node(name=name)

            if prev is not None and prev not in curr.children:
                curr.add_child(child=prev, port=self.port_lookup[name][prev.name])

                conn = self.__get_connection(name=name)
                if len(curr.children) > 1:
                    conn.updateMulticastGroup(mgid=mgid, ports=curr.children.keys())
                    num_workers_entry(conn=conn, mgid=mgid, num=curr.num_children() - 1, insert=False)
                else:
                    conn.addMulticastGroup(mgid=mgid, ports=curr.children.keys())

                num_workers_entry(conn=conn, mgid=mgid, num=curr.num_children(), insert=True)
                port = self.port_lookup[name][prev.name]
                sml_entry(conn=conn, port=port, mac=prev.mac, ip=prev.ip, insert=True)

                if not prev.is_wroker():
                    next_step_entry(conn=self.__get_connection(name=prev.name), mgid=mgid, step=0, port=0, insert=False)
                    next_step_entry(conn=self.__get_connection(name=prev.name), mgid=mgid, step=1, port=self.port_lookup[prev.name][name], insert=True)

            prev = curr

    def shrink_tree(self, tree: Tree, path: List[str], mgid: int) -> None:
        prev = None
        for name in path:
            curr = tree.get_node(name=name)

            if not curr.is_wroker() and prev is not None:
                conn = self.__get_connection(name=curr.name)
                num_workers_entry(conn=conn, mgid=mgid, num=curr.num_children(), insert=False)

                port = self.port_lookup[name][prev.name]
                sml_entry(conn=conn, port=port, mac=prev.mac, ip=prev.ip, insert=False)

                tree.del_node(name=prev.name)

                if curr.num_children() > 0:
                    num_workers_entry(conn=conn, mgid=mgid, num=curr.num_children(), insert=True)
                    conn.updateMulticastGroup(mgid=mgid, ports=curr.children.keys())

                    return
                else:
                    step = 0 if curr.parent is None else 1
                    port = 0 if step == 0 else self.port_lookup[prev.name][name]
                    next_step_entry(conn=conn, mgid=mgid, step=step, port=port, insert=False)
                    conn.deleteMulticastGroup(mgid=mgid, ports=[])

            prev = curr

    def thanos(self, tree: Tree, mgid: int) -> None:
        """
        You couldn't live with you're own failure, so where did it bring you? Back to me!!
        @param tree: Tree to be purged
        @param mgid: Multicast group ID
        """
        curr = tree.root
        prev = None
        while curr.num_children() < 2:

            if prev is not None:
                conn = self.__get_connection(name=prev.name)
                port = self.port_lookup[prev.name][curr.name]
                next_step_entry(conn=conn, mgid=mgid, step=0, port=0, insert=False)
                sml_entry(conn=conn, port=port, mac=curr.mac, ip=curr.ip, insert=False)
                num_workers_entry(conn=conn, mgid=mgid, num=1, insert=False)

                conn = self.__get_connection(name=curr.name)
                next_step_entry(conn=conn, mgid=mgid, step=1, port=self.port_lookup[curr.name][prev.name], insert=False)
                next_step_entry(conn=conn, mgid=mgid, step=0, port=0, insert=True)

                tree.del_node(name=prev.name)

            child = next(iter(curr.children.values()))
            if child.is_wroker():
                break

            prev = curr
            curr = child

        tree.set_root()

    def __get_connection(self, name: str) -> P4RuntimeSwitch:
        """
        Get switch connection by switch name
        @param name: string with the name of the switch
        @return: P4RuntimeSwitch object that represents a switch connection
        """
        if name not in self.connections:
            self.connections[name] = self.net.get(name)

        return self.connections[name]
