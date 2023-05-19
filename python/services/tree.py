from typing import Dict, List
from collections import deque

from python.models.tree import Tree, TreeNode


def get_mst() -> Tree:
    """
    Get Minimum Spanning Tree (mst) of a network
    @return: Tree which represents the mst
    """
    tree = Tree()

    root = TreeNode(name="s0")
    s1 = TreeNode(name="s1")
    s2 = TreeNode(name="s2")
    w0 = TreeNode(name="w0")
    w1 = TreeNode(name="w1")
    w2 = TreeNode(name="w2")
    w3 = TreeNode(name="w3")

    tree.add_node(root)
    tree.add_node(s1)
    tree.add_node(s2)
    tree.add_node(w0)
    tree.add_node(w1)
    tree.add_node(w2)
    tree.add_node(w3)

    root.add_child(child=s1, port=1)
    root.add_child(child=s2, port=2)

    s1.add_child(child=w0, port=1)
    s1.add_child(child=w1, port=2)

    s2.add_child(child=w2, port=1)
    s2.add_child(child=w3, port=2)

    tree.set_root()

    return tree


def shortest_path(tree: Tree, src: str, dst: str) -> List[str]:
    """
    Gets the shortest path between two nodes
    @param tree: Tree in which to find the shortest path
    @param src: Name of source
    @param dst: Name of destination
    @return: A list with the shortest path
    """
    if src == dst:
        return [src]

    source = tree.get_node(src)

    visited = set()
    queue = deque([(source, [])])

    while queue:
        current, path = queue.popleft()

        print(current.name)

        # Check if we have reached the target node
        if current.name == dst:
            return path + [current.name]

        # Add the children of the current node to the queue
        for child in current.children.values():
            queue.append((child, path + [current.name]))

        parent = current.parent
        if parent is not None and parent not in visited:
            queue.append((parent, path + [current.name]))

    return []


def find_lca(tree: Tree, src: str, dst: str) -> str:
    """
    Gets the Lowest Common Ancestor (lca) of two nodes
    @param tree: Tree in which to find the lca
    @param src: Name of the source
    @param dst: Name of the destination
    @return: Name of the lca
    """
    root = tree.root

    if src == root.name or dst == root.name:
        return root.name

    path = []

    curr = tree.get_node(src)
    while curr != root:
        path.append(curr)
        curr = curr.parent

    curr = tree.get_node(dst)
    while curr != root:
        if curr in path:
            return curr.name
        curr = curr.parent

    return root.name
