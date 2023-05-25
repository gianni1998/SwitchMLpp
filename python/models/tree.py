from typing import Dict, List

from python.lib.p4app.src.p4_mininet import P4RuntimeSwitch


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

    @parent.setter
    def parent(self, value: 'Node') -> None:
        self._parent = value

    @property
    def children(self):
        return self._children.values()

    @property
    def ports(self):
        return self._children.keys()

    def add_child(self, child: 'Node', port: int):
        """
        Adds a child to the Node
        @param child: Child node to add
        @param port: Port number to which the child is connected
        """
        child.parent = self
        self._children[port] = child
        self._name_to_port[child.name] = port

    def delete_child(self, name: str):
        """
        Deletes a Node from its children by name
        @param name: Name of the child that needs to be removed
        """
        del self._children[self._name_to_port[name]]
        del self._name_to_port[name]

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

    def __init__(self, name: str, conn: P4RuntimeSwitch, **params):
        """
        Constructor
        @param name:
        @param conn:
        @param params:
        """
        Node.__init__(name, **params)
        self._conn = conn

    def add_child(self, child: 'Node', port: int):
        Node.add_child(child, port)

        # ToDo: add control plane logic

    def delete_child(self, name: str):
        Node.delete_child(name)

        # ToDo: add control plane logic



class TreeNode:
    """
    Class that represents a Node in a tree
    """
    name: str
    ip: str
    mac: str
    parent: 'TreeNode'
    children: Dict[int, 'TreeNode']

    def __init__(self, name: str, **params):
        """
        Constructor
        @param name: Name of the node
        @param params: Params
        """
        self.name = name
        self.ip = params.get("ip", '')
        self.mac = params.get("mac", '')
        self.parent = None
        self.children = {}

    def add_parent(self, parent: 'TreeNode') -> None:
        """
        Sets the parent node
        @param parent: The parent of this node
        """
        self.parent = parent

    def add_child(self, child: 'TreeNode', port: int) -> None:
        """
        Adds a child to this node
        @param child: The child which needs to be added
        @param port: Port number to which the child is connected
        """
        self.children[port] = child
        child.add_parent(self)

    def get_parents(self) -> 'TreeNode':
        """
        Gets the parent node of this node
        @return: The parent of this node
        """
        return self.parent

    def get_children(self) -> List['TreeNode']:
        """
        Gets all child nodes of this node
        @return: List with all children
        """
        return self.children.values()

    def num_children(self) -> int:
        """
        Get the number of children
        @return: The number of children
        """
        return len(self.children)
    
    def is_leaf(self) -> bool:
        """
        Checks if this node is a leaf
        @return: Boolean result of this check
        """
        return len(self.children) == 0
    
    def is_wroker(self) -> bool:
        """
        Checks if this node is a worker
        @return: Boolean result of this check
        """
        return self.name[0] == 'w'
    
    def copy(self) -> 'TreeNode':
        """
        Copies the information (ip, mac) of this node into a new node
        @return: TreeNode with info
        """
        return TreeNode(name=self.name, ip=self.ip, mac=self.mac)
    
    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f"{self.name}: p {None if self.parent is None else self.parent.name}, c {self.children}"
    

class Tree:
    """
    Class that represents a tree
    """
    root: TreeNode
    nodes: Dict[str, TreeNode]

    def __init__(self):
        """
        Constructor
        """
        self.root = None
        self.nodes = {}

    def node_exists(self, name: str) -> None:
        """
        Checks if node exists in the tree
        @param name: Name of the node
        @return: Boolean result of this check
        """
        return name in self.nodes

    def add_node(self, node: TreeNode) -> None:
        """
        Adds a node to the tree
        @param node: Node to add
        """
        self.nodes[node.name] = node

    def get_node(self, name: str) -> TreeNode:
        """
        Get a node by name
        @param name: Name of the node
        @return: The node
        """
        return self.nodes.get(name, None)

    def del_node(self, name: str) -> None:
        """
        Deletes a node from the tree when it has no children
        @param name: Name of the node
        """
        node = self.get_node(name=name)

        if node.parent is not None:
            for k, v in node.parent.children.items():
                if v.name is node.name:
                    del node.parent.children[k]
                    break

        for child in node.children.values():
            child.parent = None

        node.children = None

        del self.nodes[node.name]

    def set_root(self) -> None:
        """
        Traverses the tree to set the root
        """
        if len(self.nodes) > 0:
            
            node = next(iter(self.nodes.values()))
            while node.parent is not None:
                node = node.parent

            self.root = node

    def get_root(self) -> TreeNode:
        """
        Get the root node of the tree
        @return: Root node
        """
        return self.root
    
    def __str__(self) -> str:
        result = f"Root: {self.root.name}\n"

        for v in self.nodes.values():
            result += v.__str__() + '\n'

        return result
    