from abc import ABC, abstractmethod

from python.lib.p4app.src.p4app import P4Mininet

from python.config import NUM_WORKERS, SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC


class TopoController(ABC):

    @abstractmethod
    def run_control_plane(self, net: P4Mininet):
        """
        One-time control plane configuration
        """
        pass


class Lab5Controller(TopoController):

    def run_control_plane(self, net: P4Mininet):
    # Config switch
        sw = net.get('s0')
        sw_mac = "08:10:00:00:00:00"
        sw_ip = "10.0.1.1"
        sw.config(mac = sw_mac)

        # ARP
        sw.insertTableEntry(
            table_name="TheIngress.arpHandler.handler",
            match_fields={"hdr.arp.oper": 1},
            action_name="TheIngress.arpHandler.forward",
            action_params={"switch_mac": sw_mac}
        )

        # Multicast
        multicast_group_id = 1
        ports = [i for i in range(1, NUM_WORKERS+1)]
        sw.addMulticastGroup(multicast_group_id, ports)

        # Switch source details
        sw.insertTableEntry(
            table_name="TheIngress.switch_mac_and_ip",
            default_action="TheIngress.set_switch_mac_and_ip",
            action_name="TheIngress.set_switch_mac_and_ip",
            action_params= {
                "switch_mac": sw_mac,
                "switch_ip": sw_ip,
            }
        )

        for i in range(1, NUM_WORKERS+1):

            # Normal traffic
            sw.insertTableEntry(
                table_name="TheIngress.ipv4Handler.handler",
                match_fields={"hdr.ipv4.destinationAddress": [f"10.0.0.{i}", 32]},
                action_name="TheIngress.ipv4Handler.forward",
                action_params= {
                    "destinationAddress": f"08:00:00:00:0{i}:{i}{i}",
                    "port": i
                }
            )

            # SML reply
            sw.insertTableEntry(
                table_name="TheEgress.smlHandler.handler",
                match_fields={"standard_metadata.egress_port": i},
                action_name="TheEgress.smlHandler.forward",
                action_params={
                    "worker_mac": f"08:00:00:00:0{i}:{i}{i}",
                    "worker_ip": f"10.0.0.{i}",
                },
            )

        # worker count
        sw.insertTableEntry(
            table_name="TheIngress.num_workers",
            match_fields={"hdr.sml.mgid": multicast_group_id},
            action_name="TheIngress.set_num_workers",
            action_params={
                "num_workers": NUM_WORKERS,
            },
        )


class SingleSwitchController(TopoController):
    
    def run_control_plane(self, net: P4Mininet):
        # Config switch
        sw = net.get('s0')
        sw_mac = "08:10:00:00:00:00"
        sw.config(mac = sw_mac)

        # ARP
        sw.insertTableEntry(
            table_name="TheIngress.arpHandler.handler",
            match_fields={"hdr.arp.oper": 1},
            action_name="TheIngress.arpHandler.forward",
            action_params={"switch_mac": sw_mac}
        )

        # Controller
        sw.insertTableEntry(
            table_name="TheIngress.ipv4Handler.handler",
            match_fields={"hdr.ipv4.destinationAddress": [SDN_CONTROLLER_IP, 32]},
            action_name="TheIngress.ipv4Handler.forward",
            action_params= {
                "destinationAddress": SDN_CONTROLLER_MAC,
                "port": 0
            }
        )

        # Workers
        for i in range(1, NUM_WORKERS+1):
            sw.insertTableEntry(
                table_name="TheIngress.ipv4Handler.handler",
                match_fields={"hdr.ipv4.destinationAddress": [f"10.0.0.{i}", 32]},
                action_name="TheIngress.ipv4Handler.forward",
                action_params= {
                    "destinationAddress": f"08:00:00:00:0{i}:{i}{i}",
                    "port": i
                }
            )

