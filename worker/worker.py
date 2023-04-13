import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from lib.gen import GenInts, GenMultipleOfInRange
from lib.test import CreateTestData, RunIntTest
from lib.worker import *
from lib.comm import  unreliable_send, unreliable_receive
import socket

from util.utils import packet_builder, packet_parser
from util.constants import NUM_ITER, CHUNK_SIZE, TIMEOUT


def AllReduce(soc, rank, data, result):
    """
    Perform in-network all-reduce over UDP

    :param str    soc: the socket used for all-reduce
    :param int   rank: the worker's rank
    :param [int] data: the input vector for this worker
    :param [int]  res: the output vector

    This function is blocking, i.e. only returns with a result or error
    """

    soc.settimeout(TIMEOUT)

    addr = ("10.0.0.0", 54321)
    ver, idx, offset, packet = 0, 0, 0, 0
    idx = 1

    while offset < len(data):
        packet = packet_builder(rank, ver, idx, offset, data[offset:offset+CHUNK_SIZE])
        while(1):
            unreliable_send(soc, packet, addr)
            Log(f"Sending: {idx}, VER: {ver}")

            try:
                packet, _ = unreliable_receive(soc, 2048)
                break

            except socket.timeout:
                Log("Time out")

        offset, idx, ver = packet_parser(packet, result)

    Log(f'final-result: {result}')


def main():
    rank = GetRankOrExit()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((f'10.0.0.{int(rank+1)}', 12345))

    Log("Started...")
    for i in range(NUM_ITER):
        num_elem = GenMultipleOfInRange(2, 2048, 2 * CHUNK_SIZE)
        data_out = GenInts(num_elem)
        data_in = GenInts(num_elem, 0)
        CreateTestData("udp-iter-%d" % i, rank, data_out)
        AllReduce(s, rank, data_out, data_in)
        RunIntTest("udp-iter-%d" % i, rank, data_in, True)
    Log("Done")

if __name__ == '__main__':
    main()