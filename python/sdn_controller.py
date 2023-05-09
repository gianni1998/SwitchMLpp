import socket
import threading
import networkx as nx

from typing import Dict, List
from mininet.net import Mininet

from python.lib.p4app.src.p4_mininet import P4Host
from python.config import SDN_CONTROLLER_PORT, BUFFER_SIZE

from python.services.graph import build_graph, get_parent_name, get_shortest_path, get_lca
from python.services.network import mac_lookup, port_lookup, ip_lookup
from python.models.switch import SwitchConnectionInfo
from python.models.packet import SubscriptionPacket

from python.controller.state import AbstractState


class SDNController(P4Host):
    """
    Class that simulates a SDN controller for a P4 switch
    """
    g: nx.Graph
    net: Mininet
    conn_infos: Dict[str, SwitchConnectionInfo]
    mac_lookup: Dict[str, Dict[int, str]]
    port_lookup: Dict[str, Dict[str, int]]


    def __init__(self, name, **params):
        """
        Constructor
        """
        P4Host.__init__(self, name, **params)

        self.conn_infos = {}


    def set_net(self, net: Mininet):
        """
        Method to set Mininet object that is used for the switch connections
        """
        self.net = net
        self.g = build_graph(net)
        self.mac_lookup = mac_lookup(net)
        self.ip_lookup = ip_lookup()
        self.port_lookup = port_lookup(net)


    def start(self):
        """
        Method to open a tcp connection and listen for incomming traffic
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #s.setsockopt(socket.SOL_SOCKET, 25, str("eth0" + '\0').encode('utf-8'))

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
    def test3(self, rank: int, mgid: int, sub: bool) -> None:
        """
        Method to update switch control planes accordingly
        """
        # TODO: refactor, clean and optimise this monstrosity of a function
        
        prev = wx = f"w{rank}"
        lca = None
        
        target = next((x for x in self.conn_infos if mgid in self.conn_infos[x].mgids), None)

        # Check if group exists
        if target:
            switches = path = get_shortest_path(graph=self.g, src=wx, dst=target)
            
            if len(switches) > 1:
                lca = get_lca(graph=self.g, src=wx, dst=target)
                switches = switches[:-1] # last switch in list should aready be initialised in this case
        else:
            switches = [get_parent_name(graph=self.g, node=wx)]

        for i, sw in enumerate(switches): 

            if sw not in self.conn_infos.keys():
                self.conn_infos[sw] = SwitchConnectionInfo(connection=self.net.get(sw))

            # If lca then we should check two ports
            if sw == lca:
                l = self.port_lookup[sw][prev]
                r = self.port_lookup[sw][path[i+1]]

                ports = [l, r]
            else:
                ports = [self.port_lookup[sw][prev]]

            for port in ports:
                ip = self.ip_lookup[sw][port]

                if sub:

                    # Create
                    if mgid not in self.conn_infos[sw].mgids:

                        # Multicast group
                        self.conn_infos[sw].mgids.append(mgid)
                        self.conn_infos[sw].mg_ports[mgid] = [port]
                        self.conn_infos[sw].connection.addMulticastGroup(mgid=mgid, ports=self.conn_infos[sw].mg_ports[mgid])

                        # Worker count
                        self.conn_infos[sw].connection.insertTableEntry(
                            table_name="TheIngress.num_workers",
                            match_fields={"hdr.sml.mgid": mgid},
                            action_name="TheIngress.set_num_workers",
                            action_params={
                                "num_workers": len(self.conn_infos[sw].mg_ports[mgid]),
                            },
                        )

                        # SwitchML
                        self.conn_infos[sw].connected_ip.append(ip)
                        self.conn_infos[sw].connection.insertTableEntry(
                            table_name="TheEgress.sml_handler",
                            match_fields={"standard_metadata.egress_port": port},
                            action_name="TheEgress.sml_forward",
                            action_params={
                                "worker_mac": self.mac_lookup[sw][port],
                                "worker_ip": ip,
                            },
                        )
                    
                    # Update
                    elif mgid in self.conn_infos[sw].mgids:

                        if ip not in self.conn_infos[sw].connected_ip:
                            # Multicast group
                            self.conn_infos[sw].mg_ports[mgid].append(port)
                            self.conn_infos[sw].connection.updateMulticastGroup(mgid=mgid, ports=self.conn_infos[sw].mg_ports[mgid])

                            # Worker count
                            self.conn_infos[sw].connection.removeTableEntry(
                                table_name="TheIngress.num_workers",
                                match_fields={"hdr.sml.mgid": mgid},
                                action_name="TheIngress.set_num_workers",
                                action_params={
                                    "num_workers": len(self.conn_infos[sw].mg_ports[mgid]) - 1,
                                },
                            )

                            self.conn_infos[sw].connection.insertTableEntry(
                                table_name="TheIngress.num_workers",
                                match_fields={"hdr.sml.mgid": mgid},
                                action_name="TheIngress.set_num_workers",
                                action_params={
                                    "num_workers": len(self.conn_infos[sw].mg_ports[mgid]),
                                },
                            )

                            # SwitchML
                            self.conn_infos[sw].connected_ip.append(ip)
                            self.conn_infos[sw].connection.insertTableEntry(
                                table_name="TheEgress.sml_handler",
                                match_fields={"standard_metadata.egress_port": port},
                                action_name="TheEgress.sml_forward",
                                action_params={
                                    "worker_mac": self.mac_lookup[sw][port],
                                    "worker_ip": ip,
                                },
                            )
                
                else:

                    # Delete
                    if mgid not in self.conn_infos[sw].mgids or port not in self.conn_infos[sw].mg_ports[mgid]:
                        continue
                    
                    if len(self.conn_infos[sw].mg_ports[mgid]) > 1:
                        # Multicast group
                        self.conn_infos[sw].mg_ports[mgid].remove(port)
                        self.conn_infos[sw].connection.updateMulticastGroup(mgid=mgid, ports=self.conn_infos[sw].mg_ports[mgid])

                        # Worker count
                        self.conn_infos[sw].connection.removeTableEntry(
                            table_name="TheIngress.num_workers",
                            match_fields={"hdr.sml.mgid": mgid},
                            action_name="TheIngress.set_num_workers",
                            action_params={
                                "num_workers": len(self.conn_infos[sw].mg_ports[mgid]) + 1,
                            },
                        )

                        self.conn_infos[sw].connection.insertTableEntry(
                            table_name="TheIngress.num_workers",
                            match_fields={"hdr.sml.mgid": mgid},
                            action_name="TheIngress.set_num_workers",
                            action_params={
                                "num_workers": len(self.conn_infos[sw].mg_ports[mgid]),
                            },
                        )

                    else:
                        # Multicast group
                        self.conn_infos[sw].mgids.remove(mgid)
                        self.conn_infos[sw].connection.deleteMulticastGroup(mgid=mgid, ports=self.conn_infos[sw].mg_ports[mgid])
                        del self.conn_infos[sw].mg_ports[mgid]

                        # Worker count
                        self.conn_infos[sw].connection.removeTableEntry(
                            table_name="TheIngress.num_workers",
                            match_fields={"hdr.sml.mgid": mgid},
                            action_name="TheIngress.set_num_workers",
                            action_params={
                                "num_workers": 1,
                            },
                        )

                    # SwitchML
                    self.conn_infos[sw].connected_ip.remove(ip)
                    self.conn_infos[sw].connection.removeTableEntry(
                        table_name="TheEgress.sml_handler",
                        match_fields={"standard_metadata.egress_port": port},
                        action_name="TheEgress.sml_forward",
                        action_params={
                            "worker_mac": self.mac_lookup[sw][port],
                            "worker_ip": ip,
                        },
                    )
                    
            prev = sw
