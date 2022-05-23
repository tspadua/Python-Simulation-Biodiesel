import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json
import random

config = {
    "host": "localhost",
    "port": 5003,
    "connection_host": "localhost",
    "connection_port": 5004
}

class Reactor():
    def __init__(self, flow_rate = 1):
        self.content = {
            "NaOH": 0,
            "EtOH": 0,
            "oil": 0,
            "mixed_compound": 0
        }
        self.cycle_count = 0
        self.status = "Waiting"
        self.flow_rate = flow_rate
        self.next_container = None

    @property 
    def volume(self):
        return sum(self.content.values())

    def serialize(self):
        return {
            "content": self.content,
            "status": self.status,
            "cycle_count": self.cycle_count,
            "volume": self.volume
        }

    def connect_to_tank(self, host, port):
        self.next_container = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_container.connect((host, port))
 
    def receive_content(self, data):
        self.content[data["compound"]] += data["volume"]
            

    def process_content(self):
        # condition for reactor activation

        if (self.content["NaOH"] >= 1.25 and self.content["EtOH"] >= 1.25 and self.content["oil"] >= 2.5):

            self.status = "Working"

            self.content["NaOH"] -= 1.25
            self.content["EtOH"] -= 1.25
            self.content["oil"] -= 2.5

            self.content["mixed_compound"] += 5


        else:
            self.status = "Waiting"
    
    def pass_content(self):
        if ( self.content["mixed_compound"] > self.flow_rate ):
            content = {
                "role": "Process",
                "compound": "mixed_compound",
                "volume": self.flow_rate
            }
            self.next_container.sendall(bytes(json.dumps(content), encoding='utf-8'))

            response = self.next_container.recv(1024)
            response = json.loads(response.decode("utf-8"))

            if (response['accepted']):
                self.content["mixed_compound"] -= self.flow_rate
        

    
# Refer to server.py for inherited class
class ReactorSocket(Server):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.reactor = Reactor()

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
                if (data):
                    data = json.loads(data.decode("utf-8"))

                    if (data['role'] == 'Orchestrator'):
                        self.reactor.connect_to_tank(config['connection_host'], config['connection_port'])

                        while True:
                            try:
                                output = self.reactor.serialize()
                                conn.sendall(bytes(json.dumps(output), encoding='utf-8'))
                                self.reactor.process_content()
                                self.reactor.pass_content()
                                sleep(1)
                                
                            except:
                                output = {
                                    "error": "Connection between components is broken, please contact maintenance",
                                    "data": ""
                                    }
                                #conn.sendall((bytes(json.dumps(output), encoding='utf-8')))
                    else:

                        print(data)
                        self.reactor.receive_content(data)
                        output = {
                            "accepted": True
                        }
                        conn.sendall(bytes(json.dumps(output), encoding='utf-8'))

            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = ReactorSocket(config['host'], config['port']).listen()
