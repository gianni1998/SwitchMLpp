import socket

from python.config import SDN_CONTROLLER_IP, SDN_CONTROLLER_PORT


if __name__ == "__main__":
    MESSAGE = b'Hello, World!'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect(("0.0.0.0", SDN_CONTROLLER_PORT))
    s.send(MESSAGE)
    s.close()