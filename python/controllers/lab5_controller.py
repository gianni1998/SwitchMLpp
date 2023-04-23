import os

from python.config import NUM_WORKERS


class Lab5Controller:
    def __init__(self):
        pass

    def run_workers(self, net):
        """
        Starts the workers and waits for their completion.
        Redirects output to logs/<worker_name>.log (see lib/worker.py, Log())
        This function assumes worker i is named 'w<i>'. Feel free to modify it
        if your naming scheme is different
        """
        worker = lambda rank: "w%i" % rank
        log_file = lambda rank: os.path.join(os.environ['APP_LOGS'], "%s.log" % worker(rank))
        for i in range(NUM_WORKERS):
            net.get(worker(i)).sendCmd('python worker/worker.py %d > %s' % (i, log_file(i)))
        for i in range(NUM_WORKERS):
            net.get(worker(i)).waitOutput()


    def run_control_plane(self, net):
        """
        One-time control plane configuration
        """
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
