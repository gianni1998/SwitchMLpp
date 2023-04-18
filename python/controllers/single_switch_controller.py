import os

from python.config import NUM_WORKERS


class SingleSwitchController:
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
            net.get(worker(i)).sendCmd('python python/worker.py %d > %s' % (i, log_file(i)))
        for i in range(NUM_WORKERS):
            net.get(worker(i)).waitOutput()


    def run_control_plane(self, net):
        """
        One-time control plane configuration
        """
        # Config switch
        sw = net.get('s0')
        sw_mac = "08:10:00:00:00:00"
        sw.config(mac = sw_mac)

        sw.cmd('ifconfig s1 10.0.0.1')

        # ARP
        sw.insertTableEntry(
            table_name="TheIngress.arpHandler.handler",
            match_fields={"hdr.arp.oper": 1},
            action_name="TheIngress.arpHandler.forward",
            action_params={"switch_mac": sw_mac}
        )
