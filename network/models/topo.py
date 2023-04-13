from models.node import Node


class Fattree:
    def __init__(self, num_ports):
        self.servers = []
        self.switches = []
        self.free_switches = []
        self.generate(num_ports)

    def generate(self, num_ports):
        if (num_ports >= 256):
            raise ValueError("num_ports cannot be bigger or equal to 256")

        # Calculate amount of servers, switches and pods
        servers = int(pow(num_ports, 3) / 4)
        cores = int(pow((num_ports / 2), 2))
        edges = int((servers) / (num_ports / 2))
        pods = num_ports
        servers_per_pod = int(servers / pods)
        edges_per_pod = int(edges / pods)  # doubles as aggregations per pod
        servers_per_edge = int(servers_per_pod / edges_per_pod)

        # Create topology
        core_switches = []
        aggregation_switches = []
        edge_switches = []
        server_hosts = []
        for i in range(servers):
            server_hosts.append(Node(
                f"10.{str(int(i / servers_per_pod))}.{str(int((i / (num_ports / 2)) % (num_ports / 2)))}.{str(int(i % (num_ports / 2) + 2))}",
                "Server"))

        for i in range(edges):
            edge_switches.append(Node(f"10.{str(int(i / edges_per_pod))}.{str(int(i % (num_ports / 2)))}.1", "Edge"))
            aggregation_switches.append(
                Node(f"10.{str(int(i / edges_per_pod))}.{str(int(i % (num_ports / 2) + num_ports / 2))}.1",
                     "Aggregation"))

        for i in range(cores):
            core_switches.append(Node(
                f"10.{str(int(num_ports))}.{str(int(i / (num_ports / 2) + 1))}.{str(int(i % (num_ports / 2) + 1))}",
                "Core"))

        for idx, node in enumerate(edge_switches):
            for i in range(servers_per_edge):
                node.add_edge(server_hosts[i + (idx * servers_per_edge)])

        for idx, node in enumerate(aggregation_switches):
            for i in range(edges_per_pod):
                node.add_edge(edge_switches[i + (int(idx / edges_per_pod) * edges_per_pod)])

        for idx, node in enumerate(core_switches):
            for i in range(pods):
                node.add_edge(aggregation_switches[int(idx / edges_per_pod) + (i * edges_per_pod)])

        self.switches = core_switches + aggregation_switches + edge_switches
        self.servers = server_hosts
