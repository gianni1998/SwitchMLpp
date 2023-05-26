from typing import Dict, List

from python.lib.p4app.src.p4_mininet import P4RuntimeSwitch

from python.services.switch import sml_entry, next_step_entry, num_workers_entry


class Node:
    """
    Class that represents a node in a tree
    """

    _name: str
    "Name of the Node"
    _ip: str
    "IP address of the Node in the network"
    _mac: str
    "MAC address of the Node"
    _parent: 'Node'
    "Parent of the Node"
    _parent_port: int
    "Port to which parent is connected"
    _children: Dict[int, 'Node']
    "Children connected on a port of the Node"
    _name_to_port: Dict[str, int]
    "Lookup for name of child to connected port"

    def __init__(self, name: str, **params):
        """
        Constructor
        @param name: Name of the node
        @param params: Params
        """
        self._name = name
        self._ip = params.get("ip", '')
        self._mac = params.get("mac", '')
        self._parent = None
        self._children = {}
        self._name_to_port = {}

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def ip(self) -> str:
        return self._ip

    @property
    def mac(self) -> str:
        return self._mac

    @property
    def parent(self) -> 'Node':
        return self._parent

    @property
    def children(self) -> List['Node']:
        return list(self._children.values())

    @property
    def ports(self) -> List[int]:
        return list(self._children.keys())
    
    @property
    def num_children(self) -> int:
        return len(self._children)

    def add_child(self, child: 'Node', portc: int, portp: int):
        """
        Adds a child to the Node
        @param child: Child node to add
        @param portc: Port number to which the parent is connected to the child
        @param portp: Port number to which the child is connected to the parent
        """
        if child.name not in self._name_to_port:
            self._children[portc] = child
            self._name_to_port[child.name] = portc

            child.add_parent(parent=self, portc=portc, portp=portp)

    def delete_child(self, name: str):
        """
        Deletes a Node from its children by name
        @param name: Name of the child that needs to be removed
        """
        if name in self._name_to_port:
            del self._children[self._name_to_port[name]]
            del self._name_to_port[name]

    def add_parent(self, parent: 'Node', portc: int, portp: int) -> None:
        """
        Add the parent Node
        @param parent: The parent that needs to be added
        @param portc: Port number to which the parent is connected to the child
        @param portp: Port number to which the child is connected to the parent
        """
        if self._parent is None:
            self._parent = parent
            self._parent_port = portp

            parent.add_child(child=self, portc=portc, portp=portp)

    def delete_parent(self) -> None:
        """
        Delete the parent Node
        """
        if self.parent is not None:
            self._parent = None
            self._parent_port = 0

    def is_worker(self) -> bool:
        """
        Checks if Node is a worker
        @return: Boolean result of this check
        """
        return self.name[0] == 'w'
    
    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f"{self.name}: p {None if self.parent is None else self.parent.name}, c {self._children}"
    

class SMLNode(Node):
    """
    Class that represents a SwitchML node in a tree
    """

    _conn: P4RuntimeSwitch
    "Connection to the in-network P4 switch"
    _mgid: int
    "Multicat group ID"

    def __init__(self, name: str, conn: P4RuntimeSwitch, mgid: int, **params):
        """
        Constructor
        @param name: Name of the Node
        @param conn: Connection to the switch
        @param mgid: Multicast group id
        @param params: Additional parameters
        """
        Node.__init__(self, name=name, **params)
        self._conn = conn
        self._mgid = mgid

        if not self.is_worker():
            next_step_entry(conn=conn, mgid=mgid, step=0, port=0, insert=True)

    def add_child(self, child: 'Node', portc: int, portp: int):
        if child.name in self._name_to_port:
            return

        self._children[portc] = child
        self._name_to_port[child.name] = portc

        if self.is_worker():
            return

        if self.num_children == 1:
            self._conn.addMulticastGroup(mgid=self._mgid, ports=self.ports)
        else:
            self._conn.updateMulticastGroup(mgid=self._mgid, ports=self.ports)
            num_workers_entry(conn=self._conn, mgid=self._mgid, num=self.num_children - 1, insert=False)

        num_workers_entry(conn=self._conn, mgid=self._mgid, num=self.num_children, insert=True)
        sml_entry(conn=self._conn, port=portc, mac=child.mac, ip=child.ip, insert=True)

        child.add_parent(parent=self, portc=portc, portp=portp)

    def delete_child(self, name: str) -> None:
        if name not in self._name_to_port:
            return

        port = self._name_to_port[name]
        child = self._children[port]

        del self._children[port]
        del self._name_to_port[name]

        num_workers_entry(conn=self._conn, mgid=self._mgid, num=self.num_children + 1, insert=False)
        sml_entry(conn=self._conn, port=port, mac=child.mac, ip=child.ip, insert=False)

        if self.num_children == 0:
            self._conn.deleteMulticastGroup(mgid=self._mgid, ports=[])
            next_step_entry(conn=self._conn, mgid=self._mgid, step=0, port=0, insert=False)
        else:
            self._conn.updateMulticastGroup(mgid=self._mgid, ports=self.ports)
            num_workers_entry(conn=self._conn, mgid=self._mgid, num=self.num_children, insert=True)

    def add_parent(self, parent: 'Node', portc: int, portp: int) -> None:
        if self._parent is not None:
            return

        self._parent = parent
        self._parent_port = portp

        if not self.is_worker():
            next_step_entry(conn=self._conn, mgid=self._mgid, step=0, port=0, insert=False)
            next_step_entry(conn=self._conn, mgid=self._mgid, step=1, port=portp, insert=True)

        parent.add_child(child=self, portc=portc, portp=portp)

    def delete_parent(self) -> None:
        if self.parent is None or self.is_worker():
            return

        self.parent.delete_child(name=self.name)
        next_step_entry(conn=self._conn, mgid=self._mgid, step=1, port=self._parent_port, insert=False)

        if self.num_children > 0:
            next_step_entry(conn=self._conn, mgid=self._mgid, step=0, port=0, insert=True)

        self._parent = None
        self._parent_port = 0

class Tree:
    """
    Class that represents a tree
    """

    _root: Node
    "Root Node of the tree"
    _nodes: Dict[str, Node]
    "Dictionary of Nodes in the tree"

    def __init__(self):
        """
        Constructor
        """
        self._root = None
        self._nodes = {}

    @property
    def root(self) -> Node:
        return self._root
    
    @property
    def num_nodes(self) -> int:
        return len(self._nodes)

    def node_exists(self, name: str) -> bool:
        """
        Checks if node exists in the tree
        @param name: Name of the node
        @return: Boolean result of this check
        """
        return name in self._nodes

    def add_node(self, node: Node) -> None:
        """
        Adds a node to the tree
        @param node: Node to add
        """
        self._nodes[node.name] = node

    def get_node(self, name: str) -> Node:
        """
        Get a node by name
        @param name: Name of the node
        @return: The node
        """
        return self._nodes.get(name, None)

    def del_node(self, name: str) -> None:
        """
        Deletes a Node from the tree
        @param name: Name of the node
        """
        node = self.get_node(name=name)

        if node.parent is not None:
            node.parent.delete_child(name=node.name)

        for child in node.children:
            child.delete_parent()

        del self._nodes[node.name]

    def set_root(self) -> None:
        """
        Traverses the tree to set the root
        """
        if len(self._nodes) > 0:
            
            node = next(iter(self._nodes.values()))
            while node.parent is not None:
                node = node.parent

            self._root = node
        else:
            self._root = None

    def shrink_tree(self, path: List[str]) -> None:
        """
        Removes a given path from the tree
        @param path: Path that needs to be removed
        """
        for hop in path:
            node = self.get_node(name=hop)

            if node.num_children >= 1:
                return

            self.del_node(name=node.name)

    def top_tree(self) -> None:
        """
        Removes unwanted tops from the tree
        """
        node = self.root

        while node.num_children == 1:
            print(node.name)
            child = next(iter(node.children))
            if child.is_worker():
                break

            self.del_node(node.name)
            node = child
    
    def __str__(self) -> str:
        result = f"Root: {self.root.name if self.root is not None else None}\n"

        for v in self._nodes.values():
            result += v.__str__() + '\n'

        return result
    