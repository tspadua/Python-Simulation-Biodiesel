import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json
import random

config = {
    "host": "localhost",
    "port": 9001
}

# Refer to server.py for inherited class
class TestTank(Server):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.content = {
            "glycerin": 0,
            "EtOH": 0,
            "washing_solution": 0,
            "mixed_compound": 0
        }

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
                        sleep(1)
                        output = json.dumps(self.content)
                        conn.sendall((bytes(output, encoding='utf-8')))
                    else:
                        self.content[data['compound']] += data['volume']
                        output = json.dumps({"accepted": True})
                        conn.sendall((bytes(output, encoding='utf-8')))
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = TestTank(config['host'], config['port']).listen()