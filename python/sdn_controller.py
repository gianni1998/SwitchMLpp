import socket
import struct
import threading

from mininet.util import quietRun
from mininet.node import Controller

from python.lib.p4app.src.p4_mininet import P4Host
from python.config import SDN_CONTROLLER_PORT, BUFFER_SIZE

from python.models.switch import SwitchConnection



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

        self.ip_to_mac = {}


    def start(self):
        """
        Method to open a tcp connection and listen for incomming traffic
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, 25, str("lo" + '\0').encode('utf-8'))
            s.bind(("", SDN_CONTROLLER_PORT))

            print(self.cmd("ifconfig"))
            s.listen()

            while 1:
                print("Test 2")
                conn, addr = s.accept()
                print(conn + " " + addr)

                conn.sendall("Tjupapi")
                conn.close()
                break
                # thread = threading.Thread(target=self._client_thread, args=(conn, addr))
                # thread.start()      
        # print(self.cmd("nc -l 5005"))  


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


    def _process(self, data, addr):
        pass

    def test(self):
        """
        Method to process the subscription packet
        """
        
        # ToDo: get from packet
        sw_name = "s0"
        sub = True
        mgid = 1

        if sw_name not in self.sw_conns.keys():
            self.sw_conns[sw_name] = SwitchConnection(connection=self.net.get(sw_name))

        port = 1
        ip = "10.0.0.1"

        conn = self.sw_conns[sw_name]

        self._mg_entry(conn=conn, mgid=mgid, port=port, subscribe=sub)
        self._sml_entry(conn=conn, ip=ip, port=port, subscribe=sub)

        # ToDo: increment counter
        



    def _mg_entry(self, conn: SwitchConnection, mgid: int, port: int, subscribe: bool):
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
            if conn.mg_ports[mgid].count() > 1:
                conn.mg_ports[mgid].remove(port)
                conn.connection.updateMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
            else:
                conn.connection.deleteMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
                del conn.mg_ports[mgid]


    def _sml_entry(self, conn: SwitchConnection, ip: str, port: int, subscribe: bool):
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
                    "worker_mac": self.ip_to_mac.get(ip, "08:00:00:00:00:00"),
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
                    "worker_mac": self.ip_to_mac.get(ip, "08:00:00:00:00:00"),
                    "worker_ip": ip,
                },
            )

        