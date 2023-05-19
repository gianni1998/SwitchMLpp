from typing import Dict, List


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

    def node_exists(self, name: str):
        """
        Checks if node exists in the tree
        @param name: Name of the node
        @return: Boolean result of this check
        """
        return name in self.nodes

    def add_node(self, node: TreeNode):
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

    def set_root(self):
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
    
    def __str__(self):
        result = f"Root: {self.root.name}\n"

        for v in self.nodes.values():
            result += v.__str__() + '\n'

        return result
    