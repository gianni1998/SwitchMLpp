import networkx as nx

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

    return g


def lca(graph: nx.Graph, src: str, dst: str) -> str:
    """
    Find the lowest common ancestor between two nodes
    """
    path = nx.dijkstra_path_length(G=graph, source=src, target=dst)
    n = len(path)

    return path[int(n/2)]


def get_parent_name(graph: nx.Graph, node: str) -> str:
    """
    Get the name of the switch that is directly above a worker
    """
    for edge in graph.edges:
        if node in edge:
            return edge[1] if edge[0] == node else edge[0]
        
    return ""
