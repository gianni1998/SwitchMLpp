from abc import ABC, abstractmethod
from mininet.util import macColonHex

from python.lib.p4app.src.p4app import P4Mininet

from python.config import NUM_WORKERS, SDN_CONTROLLER_IP, SDN_CONTROLLER_MAC, TREE_DEPTH, TREE_FANOUT
from python.services.network import mac_lookup


class TopoConfig(ABC):

    @abstractmethod
    def run_control_plane(self, net: P4Mininet):
        """
        One-time control plane configuration
        """
        pass

    @staticmethod
    def arp_entry(sw, ip, mac=None):
        """"
        Method to add ARP entry to the contol plane
        """
        if mac is None:
            mac = sw.MAC()

        sw.insertTableEntry(
            table_name="TheIngress.arpHandler.handler",
            match_fields={"hdr.arp.tpa": ip},
            action_name="TheIngress.arpHandler.forward",
            action_params={"switch_mac": mac}
        )

    @staticmethod
    def switch_entry(sw, ip):
        """
        Mathod to add switch information to the control plane
        """
        sw.ip = ip

        sw.insertTableEntry(
            table_name="TheIngress.switch_mac_and_ip",
            default_action="TheIngress.set_switch_mac_and_ip",
            action_name="TheIngress.set_switch_mac_and_ip",
            action_params= {
                "switch_mac": sw.MAC(),
                "switch_ip": ip,
            }
        )

        sw.insertTableEntry(
            table_name="TheIngress.switch_rank",
            default_action="TheIngress.set_switch_rank",
            action_name="TheIngress.set_switch_rank",
            action_params= {
                "rank": int(sw.name[-1]),
            }
        )

    @staticmethod
    def ipv4_entry(sw, ip, mac, port):
        """
        Mathod to add ipv4 forwarding entry to the control plane
        """
        sw.insertTableEntry(
            table_name="TheIngress.ipv4Handler.handler",
            match_fields={"hdr.ipv4.destinationAddress": ip},
            action_name="TheIngress.ipv4Handler.forward",
            action_params= {
                "destinationAddress": mac,
                "port": port
            }
        )


class Lab5Config(TopoConfig):

    def run_control_plane(self, net: P4Mininet):
    # Config switch
        sw = net.get('s0')
        sw_mac = "08:10:00:00:00:00"
        sw_ip = "10.0.1.1"
        sw.config(mac = sw_mac)

        lookup = mac_lookup(net)

        # ARP
        self.arp_entry(sw=sw, ip="10.0.0.0")

        # Multicast
        multicast_group_id = 1
        ports = [i for i in range(1, NUM_WORKERS+1)]
        sw.addMulticastGroup(multicast_group_id, ports)

        # Switch source details
        self.switch_entry(sw=sw, ip=sw_ip)

        for i in range(1, NUM_WORKERS+1):

            # Normal traffic
            self.ipv4_entry(sw=sw, ip=[f"10.0.1.{i+1}", 32], mac=lookup[sw.name][i], port=i)

            # SML reply
            sw.insertTableEntry(
                table_name="TheEgress.sml_handler",
                match_fields={"standard_metadata.egress_port": i},
                action_name="TheEgress.sml_forward",
                action_params={
                    "worker_mac": f"08:00:00:00:0{i}:{i}{i}",
                    "worker_ip": f"10.0.1.{i+1}",
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


class SingleSwitchConfig(TopoConfig):
    
    def run_control_plane(self, net: P4Mininet):
        # Config switch
        sw = net.get('s0')
        sw_mac = "08:10:00:00:00:00"
        sw.config(mac = sw_mac)
        sw_ip = "10.0.1.1"

        lookup = mac_lookup(net)

        # ARP
        self.arp_entry(sw=sw, ip="10.0.0.0")

        # Switch source details
        self.switch_entry(sw=sw, ip=sw_ip)

        # Controller
        self.ipv4_entry(sw=sw, ip=[SDN_CONTROLLER_IP, 32], mac=SDN_CONTROLLER_MAC, port=0)

        # Workers
        for i in range(1, NUM_WORKERS+1):
            self.ipv4_entry(sw=sw, ip=[f"10.0.1.{i+1}", 32], mac=lookup[sw.name][i], port=i)

        
class TreeTopoConfig(TopoConfig):

    def __init__(self, **params):
        self.depth = params.get("depth", TREE_DEPTH)
        self.fanout = params.get("fanout", TREE_FANOUT)
        
    def run_control_plane(self, net: P4Mininet):
        # Set mac
        n = 1000
        for sw in net.switches:
            mac = macColonHex(n)
            sw.config(mac = mac)
            n += 1

        lookup = mac_lookup(net)

        s0 = net.get("s0")

        # ARP 
        self.arp_entry(sw=s0, ip="10.0.0.0")

        # Switch details
        self.switch_entry(sw=s0, ip="10.0.2.1")

        # IPv4 for controller
        self.ipv4_entry(sw=s0, ip=[SDN_CONTROLLER_IP, 32], mac=SDN_CONTROLLER_MAC, port=0)

        # IPv4 for workers
        for i in range(1, self.fanout+1):
            self.ipv4_entry(sw=s0, ip=[f"10.0.{i-1}.0", 24], mac=lookup[s0.name][i], port=i)

        for i in range(0, self.fanout):
            sw = net.get(f"s{i+1}")

            # ARP
            self.arp_entry(sw=sw, ip="10.0.0.0")

            # Switch details
            self.switch_entry(sw=sw, ip=f"10.0.{i}.1")
            
            # IPv4 Traffic up
            self.ipv4_entry(sw=sw, ip=["10.0.0.0", 8], mac=lookup[sw.name][0], port=0)

            for j in range(2, self.fanout+2):
                port = j-1
                # IPv4 traffic to workers
                self.ipv4_entry(sw=sw, ip=[f"10.0.{i}.{j}", 32], mac=lookup[sw.name][port], port=port)


class FatTreeConfig(TopoConfig):
    def __init__(self, k=4):
        self.k = k

    def run_control_plane(self, net: P4Mininet):
        k = self.k
        k2 = int(k/2)

        # Set mac
        n = 1000
        for sw in net.switches:
            mac = macColonHex(n)
            sw.config(mac=mac)
            n += 1

            # ARP
            self.arp_entry(sw=sw, ip="10.0.0.0")

        lookup = mac_lookup(net)

        # 10.k.x.y          - Core
        # 10.pod.switch.1   - Aggregation
        # 10.pod.switch.ID  - Edge and Workers

        # Core switches
        for core in range(self.k):
            sw = net.get(f"s{core}")

            # Switch details
            self.switch_entry(sw=sw, ip=f"10.{k}.{int(core / k2 + 1)}.{int(core % k2 + 1)}")

            # IPv4 Traffic
            for pod in range(k):
                # print(f"ipv4 10.{pod}.0.0 {lookup[sw.name][pod]} {pod}")
                self.ipv4_entry(sw=sw, ip=[f"10.{pod}.0.0", 16], mac=lookup[sw.name][pod], port=pod)

        for pod in range(k):
            # Aggregation switches
            for agg in range(k2):
                sw = net.get(f"s{pod*k2+k+agg}")
                # print(f"Agg: s{pod*k2+k+agg}")

                # Switch details
                self.switch_entry(sw=sw, ip=f"10.{pod}.{agg + k2}.1")

                # IPv4 up
                self.ipv4_entry(sw=sw, ip=[f"10.0.0.0", 8], mac=lookup[sw.name][agg], port=agg)

                # IPv4 Traffic
                for edge in range(k2):
                    port = edge + k2
                    # print(f"ipv4 10.{pod}.{edge}.0 {lookup[sw.name][port]} {port}")
                    self.ipv4_entry(sw=sw, ip=[f"10.{pod}.{edge}.0", 24], mac=lookup[sw.name][port], port=port)

            # Edge switches
            for edge in range(k2):
                sw = net.get(f"s{pod*k2+(k*k2+k+edge)}")
                # print(f"Edge: s{pod*k2+(k*k2+k+edge)}")

                # Switch details
                self.switch_entry(sw=sw, ip=f"10.{pod}.{edge}.1")

                # IPv4 up
                self.ipv4_entry(sw=sw, ip=[f"10.0.0.0", 8], mac=lookup[sw.name][edge], port=edge)

                # IPv4 Traffic
                for worker in range(k2):
                    port = worker+k2
                    # print(f"ipv4 10.{pod}.{edge}.{worker+2} {lookup[sw.name][port]} {port}")
                    self.ipv4_entry(sw=sw, ip=[f"10.{pod}.{edge}.{worker+2}", 32], mac=lookup[sw.name][port], port=port)

        # Controller
        sw = net.get(f"s{int(3*k**2/4)}")
        self.ipv4_entry(sw=sw, ip=[SDN_CONTROLLER_IP, 32], mac=SDN_CONTROLLER_MAC, port=k)