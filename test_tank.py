import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json
import random

config = {
    "host": "localhost",
    "port": 9000
}

# Refer to server.py for inherited class
class TestTank(Server):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.compound_tank = ChemicalTank("glycerin")

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
                    
                    # handles the connection, it should send some metadata including its role, 
                    # e.g. 
                    #       {
                    #           "role": "Process",
                    #           "content" : { "compound_name": 0.75, ... }
                    #       }
                    
                    if (data['role'] == 'Orchestrator'):
                        output = self.compound_tank.serialize()
                        sleep(1)
                        output = json.dumps(output)
                        conn.sendall((bytes(output, encoding='utf-8')))
                    else:
                        print(data)
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = TestTank(config['host'], config['port']).listen()
