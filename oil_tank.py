import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json

config = {
    "connection_host": "localhost",
    "connection_port": "5002"
}

class OilTankServer(Server):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.oil_tank = ChemicalTank(0.75, None, oil=0)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevents "Address already in use"
        self.s.bind((self.host, self.port))
    
    def handle_client_thread(self, conn, addr):
        print(f"Connected: {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if (data):
                    data = json.loads(data.decode("utf-8"))
                    if (data['role'] == 'Observer'):
                        output = self.oil_tank.serialize()
                        sleep(1)
                        output = json.dumps(output)
                        conn.sendall((bytes(output, encoding='utf-8')))
                    else:
                        self.status = 'Working'
                        try:
                            self.oil_tank.connect_to_tank(config['connection_host'], config['connection_port'])
                        except:
                            conn.sendall((bytes('{"error":""Connection between tanks is broken, please contact maintenance"","data": ""}', encoding='utf-8')))
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

test = ChemicalTank(0.75, None, oil=0)
print(test.serialize())
server = OilTankServer('localhost', 5000).listen()