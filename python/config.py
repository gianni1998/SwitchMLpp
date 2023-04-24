import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Topo
NUM_PORTS = 4
NUM_WORKERS = 2

# Worker
NUM_ITER   = 1
CHUNK_SIZE = 32  
SWITCH_ML_PACKET_SIZE = 20
TIMEOUT = .1
MAX_CHUNKS = 1

# Controller
SDN_CONTROLLER_IP = "10.1.2.3"
SDN_CONTROLLER_MAC = "00:00:00:00:00:02"  
SDN_CONTROLLER_PORT = 12345
BUFFER_SIZE = 1024