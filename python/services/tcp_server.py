import socket

from python.config import SDN_CONTROLLER_IP, SDN_CONTROLLER_PORT

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SDN_CONTROLLER_IP, SDN_CONTROLLER_PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        data = conn.recv(1024)

    print(data)