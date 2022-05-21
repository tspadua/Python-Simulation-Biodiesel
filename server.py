import socket
from _thread import *

class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevents "Address already in use"
        self.s.bind((self.host, self.port))

    def listen(self):
        self.s.listen()
        print("Listening on %s:%d" %(self.host, self.port))
        while True:
            conn, addr = self.s.accept()
            conn.settimeout(30)
            start_new_thread(self.handle_client_thread, (conn, addr))

    def handle_client_thread(self, conn, addr):
        print(f"Connected: {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if data:
                    response = data
                    print(response)
                    conn.send('response')
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False