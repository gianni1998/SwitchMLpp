import networkx as nx
from typing import Dict, List
from collections import deque
from mininet.net import Mininet

from python.services.network import port_lookup
from python.models.tree import Tree, Node


def get_mst(net: Mininet) -> Tree:
    """
    Get Minimum Spanning Tree (mst) of a network
    @return: Tree which represents the mst
    """
    ports = port_lookup(net=net)

    tree = Tree()

    g = nx.Graph()
    g.add_nodes_from([node.name for node in net.nameToNode.values()], key=list)
    g.add_edges_from([(link.intf1.node.name, link.intf2.node.name) for link in net.links], weight=1, key=list)

    mst = nx.algorithms.approximation.steiner_tree(G=g, terminal_nodes=[f"w{i}" for i in range(16)])

    for node in mst.nodes():
        mn_node = net.get(node)
        tree.add_node(node=Node(name=node,
                                ip=mn_node.IP() if node[0] == 'w' else mn_node.ip,
                                mac=mn_node.MAC()))

    for link in mst.edges():
        node1 = tree.get_node(name=link[0])
        node2 = tree.get_node(name=link[1])

        if node1.is_worker():
            node2.add_child(child=node1, portc=ports[node2.name][node1.name], portp=ports[node1.name][node2.name])
        else:
            node1.add_child(child=node2, portc=ports[node1.name][node2.name], portp=ports[node2.name][node1.name])

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
        for child in current.children:
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
