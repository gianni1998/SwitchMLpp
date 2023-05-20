import networkx as nx

from typing import List, Tuple

from mininet.net import Mininet


def build_graph(net: Mininet) -> nx.Graph:
    """
    Method to build a networkx graph from a given Mininet object
    """
    g = nx.Graph()

    edges = []

    for node in net.switches: 
        g.add_node(node)

    for node in net.hosts:
        if node.name[0] != 'c':
            g.add_node(node)
    
    for link in net.links:
        if link.intf1.node.name[0] != 'c' and link.intf2.node.name[0] != 'c':
            edges.append((link.intf1.node.name, link.intf2.node.name, 1))

    g.add_weighted_edges_from(edges)

    mst = nx.algorithms.tree.mst.minimum_spanning_tree(g)

    root_node = [node for node, degree in mst.degree() if degree >= 2][0]
    nodes = [node for node, degree in mst.degree()]
    print("Root node of the spanning tree:", root_node)
    print("Spanning tree:", nodes)

    return mst


def get_lca(graph: nx.Graph, src: str, dst: str) -> str:
    """
    Find the lowest common ancestor between two nodes
    """
    return nx.algorithms.lowest_common_ancestors.lowest_common_ancestor(G=graph, node1=src, node2=dst)


def get_shortest_path(graph: nx.Graph, src: str, dst: str) -> Tuple[List[str], int]:
    """
    Method to get the shortest path between two nodes
    """
    path = nx.dijkstra_path(G=graph, source=src, target=dst)

    return path, len(path)


def get_parent_name(graph: nx.Graph, node: str) -> str:
    """
    Get the name of the switch that is directly above a worker
    """
    for edge in graph.edges:
        if node in edge:
            return edge[1] if edge[0] == node else edge[0]
        
    raise ValueError(f"Unable to find parrent for node: {node}")
