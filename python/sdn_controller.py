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


    def start(self):
        """
        Method to open a tcp connection and listen for incomming traffic
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", SDN_CONTROLLER_PORT))

            print("Test 1")
            s.listen()

            while 1:
                print("Test 2")
                conn, addr = s.accept()
                print(conn)
                thread = threading.Thread(target=self._client_thread, args=(conn, addr))
                thread.start()      
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
        """
        Method to process the subscription packet
        """
        sw_name = "s0"

        if sw_name not in self.sw_conns.keys():
            self.sw_conns[sw_name] = SwitchConnection()

        self._mg_entry(conn=self.sw_conns[sw_name], mgid=addr, subscribe=addr)

        # ToDo: increment counter



    def _mg_entry(self, conn: SwitchConnection, mgid: int, subscribe: bool):
        """
        Method to Create, Update or Delete multicast entry
        """

        # ToDo: calculate port
        port = 1

        if subscribe:
            if mgid not in conn.mgids:
                conn.mgids.append(mgid)
                conn.mg_ports[mgid] = [port]
                conn.connection.addMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
            else:
                conn.mg_ports[mgid].append(port)
                conn.connection.updateMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])

        elif mgid in conn.mgids:
            if conn.mg_ports[mgid].count() > 1:
                conn.mg_ports[mgid].remove(port)
                conn.connection.updateMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
            else:
                conn.connection.deleteMulticastGroup(mgid=mgid, ports=conn.mg_ports[mgid])
                del conn.mg_ports[mgid]


    def _sml_entry(self):
        """
        Method to Create, Update or Delete SwitchML entry
        """
        pass

        