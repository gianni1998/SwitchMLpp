from abc import ABC, abstractmethod

from python.models.switch import SwitchConnectionInfo


class AbstractState(ABC):
    """
    Abstarct class that represents a state for modifying switch table entries
    """
    conn: SwitchConnectionInfo
    mgid: int
    ip: str
    mac: str
    port: str

    def __init__(self, conn: SwitchConnectionInfo, mgid: int, ip: str, mac: str, port: int):
        self.conn = conn
        self.mgid = mgid
        self.ip = ip
        self.mac = mac
        self.port = port

    def handle(self):
        """
        Main logic flow of the states
        """
        self.mg_entry()
        self.num_wokers_entry()
        self.sml_entry()


    @abstractmethod
    def mg_entry(self) -> None:
        """
        Method to handle the multicast group entries
        """
        pass


    @abstractmethod
    def sml_entry(self) -> None:
        """
        Method to handle the SwitchML entries
        """
        pass


    @abstractmethod
    def num_wokers_entry(self) -> None:
        """
        Method to handle the number of workers entries
        """
        pass
    


class CreateState(AbstractState):

    def mg_entry(self) -> None:
        self.conn.mgids.append(self.mgid)
        self.conn.mg_ports[self.mgid] = [self.port]
        self.conn.connection.addMulticastGroup(mgid=self.mgid, ports=self.conn.mg_ports[self.mgid])

    def num_wokers_entry(self) -> None:
        self.conn.connection.insertTableEntry(
            table_name="TheIngress.num_workers",
            match_fields={"hdr.sml.mgid": self.mgid},
            action_name="TheIngress.set_num_workers",
            action_params={
                "num_workers": 1,
            },
        )
    
    def sml_entry(self) -> None:
        self.conn.connected_ip.append(self.ip)

        self.conn.connection.insertTableEntry(
            table_name="TheEgress.smlHandler.handler",
            match_fields={"standard_metadata.egress_port": self.port},
            action_name="TheEgress.smlHandler.forward",
            action_params={
                "worker_mac": self.mac,
                "worker_ip": self.ip,
            },
        )


class UpdateState(AbstractState):
    
    def mg_entry(self) -> None:
        return super().mg_entry()
    
    def num_wokers_entry(self) -> None:
        return super().num_wokers_entry()
    
    def sml_entry(self) -> None:
        
        pass


class DeleteState(AbstractState):

    def handle(self):
        self.num_wokers_entry()
        self.mg_entry()
        self.sml_entry()


    def mg_entry(self) -> None:
        self.conn.connection.deleteMulticastGroup(mgid=self.mgid, ports=self.conn.mg_ports[self.mgid])
        del self.conn.mg_ports[self.mgid]


    def num_wokers_entry(self) -> None:
        self.conn.connection.removeTableEntry(
            table_name="TheIngress.num_workers",
            match_fields={"hdr.sml.mgid": self.mgid},
            action_name="TheIngress.set_num_workers",
            action_params={
                "num_workers": len(self.conn.mg_ports[self.mgid]),
            },
        )


    def sml_entry(self) -> None:
        self.conn.connected_ip.remove(self.ip)

        self.conn.connection.removeTableEntry(
            table_name="TheEgress.smlHandler.handler",
            match_fields={"standard_metadata.egress_port": self.port},
            action_name="TheEgress.smlHandler.forward",
            action_params={
                "worker_mac": self.mac,
                "worker_ip": self.ip,
            },
        )