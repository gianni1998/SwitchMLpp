import socket
import threading
from mininet.net import Mininet

from python.lib.p4app.src.p4_mininet import P4Host
from python.config import SDN_CONTROLLER_PORT, BUFFER_SIZE

from python.services.graph import build_graph, get_parent_name
from python.services.network import generate_mac_lookup
from python.models.switch import SwitchConnection
from python.models.packet import SubscriptionPacket


class SDNController(P4Host):
    """
    Class that simulates a SDN controller for a P4 switch
    """

    def __init__(self, name, **params):
        """
        Constructor
        """
        P4Host.__init__(self, name, **params)

        self.sw_conns = {}
        self.net = None
        self.g = None
        self.ip_to_mac = {}


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

                thread = threading.Thread(target=self._client_thread, args=(conn, addr))
                thread.start()    


    def set_net(self, net: Mininet):
        self.net = net
        self.g = build_graph(net)
        self.mac_look_up = generate_mac_lookup(net)


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

        # if not subscribtion packet then skip


    # def _process(self, data, addr) -> None:
    def test(self, ip, rank, mgid, sub):
        """
        Method to process the subscription packet
        """
        # pkt = SubscriptionPacket(data)
        # rank = pkt[SubscriptionPacket].rank
        # mgid = pkt[SubscriptionPacket].mgid
        # sub = pkt[SubscriptionPacket].type

        #ip = "10.0.1.2"

        wx = f"w{rank}"
        port = int(ip.split('.')[-1]) - 1

        sw_name = get_parent_name(self.g, wx)

        if sw_name not in self.sw_conns.keys():
            self._init_sml_switch(sw_name=sw_name, mgid=mgid)
        
        conn = self.sw_conns[sw_name]

        old_count = len(conn.mg_ports.get(mgid, []))
        self._mg_entry(conn=conn, mgid=mgid, port=port, subscribe=sub)

        new_count = len(conn.mg_ports.get(mgid, []))
        self._num_workers_entry(conn=conn, mgid=mgid, old=old_count, new=new_count)

        self._sml_entry(sw_name=sw_name,conn=conn, ip=ip, port=port, subscribe=sub)


    def _init_sml_switch(self, sw_name: str, mgid: int) -> None:
        """
        Method to initialise a new SML switch
        """
        self.sw_conns[sw_name] = SwitchConnection(connection=self.net.get(sw_name))
        self.sw_conns[sw_name].connection.insertTableEntry(
            table_name="TheIngress.num_workers",
            match_fields={"hdr.sml.mgid": mgid},
            action_name="TheIngress.set_num_workers",
            action_params={
                "num_workers": 0,
            },
        )


    def _mg_entry(self, conn: SwitchConnection, mgid: int, port: int, subscribe: bool) -> None:
        """
        Method to Create, Update or Delete multicast entry
        """
        if subscribe:
            if mgid not in conn.mgids:
                conn.mgids.append(mgid)
                conn.mg_ports[mgid] = [port]
                conn.connection.addMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
            elif port not in conn.mg_ports[mgid]:
                conn.mg_ports[mgid].append(port)
                conn.connection.updateMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])

        elif mgid in conn.mgids and port in conn.mg_ports[mgid]:
            if len(conn.mg_ports.get(mgid, [])):
                conn.mg_ports[mgid].remove(port)
                conn.connection.updateMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
            else:
                conn.connection.deleteMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
                del conn.mg_ports[mgid]


    def _num_workers_entry(self, conn: SwitchConnection, mgid: int, old: int, new: int) -> None:
        """
        Method to update the number of workers entry
        """
        if old == new:
            return
        
        conn.connection.removeTableEntry(
            table_name="TheIngress.num_workers",
            match_fields={"hdr.sml.mgid": mgid},
            action_name="TheIngress.set_num_workers",
            action_params={
                "num_workers": old,
            },
        )

        conn.connection.insertTableEntry(
            table_name="TheIngress.num_workers",
            match_fields={"hdr.sml.mgid": mgid},
            action_name="TheIngress.set_num_workers",
            action_params={
                "num_workers": new,
            },
        )


    def _sml_entry(self, sw_name: str, conn: SwitchConnection, ip: str, port: int, subscribe: bool) -> None:
        """
        Method to Create or Delete SwitchML entry
        """
        if subscribe and ip not in conn.connected_ip:
            conn.connected_ip.append(ip)

            conn.connection.insertTableEntry(
                table_name="TheEgress.smlHandler.handler",
                match_fields={"standard_metadata.egress_port": port},
                action_name="TheEgress.smlHandler.forward",
                action_params={
                    "worker_mac": self.mac_look_up[sw_name][port],
                    "worker_ip": ip,
                },
            )
        elif not subscribe and ip in conn.connected_ip:
            conn.connected_ip.remove(ip)

            conn.connection.removeTableEntry(
                table_name="TheEgress.smlHandler.handler",
                match_fields={"standard_metadata.egress_port": port},
                action_name="TheEgress.smlHandler.forward",
                action_params={
                    "worker_mac": self.mac_look_up[sw_name][port],
                    "worker_ip": ip,
                },
            )

        