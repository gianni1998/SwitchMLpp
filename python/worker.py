import socket
from scapy.all import raw

import python.lib.config
from python.lib.gen import GenInts, GenMultipleOfInRange
from python.lib.test import CreateTestData, RunIntTest
from python.lib.worker import Log, GetRankOrExit
from python.lib.comm import  unreliable_send, unreliable_receive

from python.services.packet_service import sml_packet_builder, sml_packet_parser
from python.config import NUM_ITER, CHUNK_SIZE, TIMEOUT, SDN_CONTROLLER_IP, SDN_CONTROLLER_PORT
from python.models.packets import SubscriptionPacket


class SMLWorker:
    """
    Class that represents a SwitchML++ worker
    """

    def __init__(self, rank: int, **params):
        """
        Constructor
        """
        self.rank = rank
        self.mgid = params.get("mgid", 1)

        self.sdn_ip = params.get("sdn_ip", SDN_CONTROLLER_IP)
        self.sdn_port = params.get("sdn_port", SDN_CONTROLLER_PORT)


    def start(self, num_iter: int):
        """
        Method to start the work flow of a worker (initialise, all reduce and terminate)
        """
        #self.initialise()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((f'10.0.0.{int(self.rank+1)}', 12345))
        s.settimeout(TIMEOUT) 
        
        Log("Started...")
        for i in range(num_iter):
            num_elem = GenMultipleOfInRange(2, 2048, 2 * CHUNK_SIZE)
            data_out = GenInts(num_elem)
            data_in = GenInts(num_elem, 0)
            CreateTestData("udp-iter-%d" % i, self.rank, data_out)
            self.all_reduce(s, data_out, data_in)
            RunIntTest("udp-iter-%d" % i, self.rank, data_in, True)
        Log("Done")

        #self.terminate()


    def initialise(self):
        """
        Method that sends a subsribe signal to the SDN controller 
        """
        self._send_sub_packet(True)


    def all_reduce(self, soc, data, result):
        """
        Method that preforms the in-network all reduce over UDP
        """
        addr = ("10.0.0.0", 54321)
        ver, idx, offset, packet = 0, 0, 0, 0
        idx = 1

        while offset < len(data):
            packet = sml_packet_builder(self.rank, ver, idx, offset, self.mgid, data[offset:offset+CHUNK_SIZE])
            while(1):
                unreliable_send(soc, packet, addr)
                Log(f"Sending: {idx}, VER: {ver}")

                try:
                    packet, _ = unreliable_receive(soc, 2048)
                    break

                except socket.timeout:
                    Log("Time out")

            offset, idx, ver = sml_packet_parser(packet, result)

        Log(f'final-result: {result}')


    def terminate(self):
        """
        Method that sends a unsubsribe signal to the SDN controller 
        """
        self._send_sub_packet(False)


    def _send_sub_packet(self, subscribe: bool):
        """
        Method to send a subscription packet over TCP
        """
        pkt = raw(SubscriptionPacket(aggregation_id=self.aggregation_id, 
                                     type=int(subscribe)))
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.sdn_ip, self.sdn_port))
            s.send(pkt)


if __name__ == '__main__':
    rank = GetRankOrExit()
    
    worker = SMLWorker(rank=rank)
    worker.start(num_iter=NUM_ITER)