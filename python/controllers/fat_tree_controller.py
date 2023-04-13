from python.config import NUM_PORTS


class FattreeController:
    def __init__(self):
        self.servers = int(pow(NUM_PORTS, 3) / 4)
        self.cores = int(pow((NUM_PORTS / 2), 2))
        self.edges = int((self.servers) / (NUM_PORTS / 2))
    
    def run_workers(self, net):
        """
        Starts the workers and waits for their completion.
        Redirects output to logs/<worker_name>.log (see lib/worker.py, Log())
        This function assumes worker i is named 'w<i>'. Feel free to modify it
        if your naming scheme is different
        """
        worker = lambda rank: "w%i" % rank
        log_file = lambda rank: os.path.join(os.environ['APP_LOGS'], "%s.log" % worker(rank))
        for i in range(self.servers):
            net.get(worker(i)).sendCmd('python worker/worker.py %d > %s' % (i, log_file(i)))
        for i in range(self.servers):
            net.get(worker(i)).waitOutput()
    
    def run_control_plane(self, net):
        """
        One-time control plane configuration
        """
        pass