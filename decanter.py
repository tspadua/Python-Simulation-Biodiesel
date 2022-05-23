import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json
import random

config = {
    "host": "localhost",
    "port": 5004,

    "connection_host_dryer": "localhost",
    "connection_port_dryer": 9000,

    "connection_host_glycerin": "localhost",
    "connection_port_glycerin": 9001,

    "connection_host_washing_tank": "localhost",
    "connection_port_washing_tank": 9000,
}

class Decanter():
    def __init__(self, capacity = 10, rest_time = 5):
        self.capacity = capacity
        self.rest_time = rest_time
        self.status = "Waiting"
        self.volume = 0
        self.next_containers = {}
        self.cycle_count = 0

    @property
    def shouldRest(self):
        if (self.volume == self.capacity):
            return True
        else:
            return False
    
    def serialize(self):
        return {
            "decanter": self.volume
        }

    # EtOH, Glycerin, wash_solution
    def connect_to_tank(self, host, port, nickname):
        self.next_containers[nickname] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_containers[nickname].connect((host, port))

    def receive_content(self, data):
        if (self.volume + data["volume"] <= self.capacity):
            self.volume += data["volume"]
            return {"accepted": True}
        else:
            return {"accepted": False}
    
    def pass_content(self):
        # 96% -> lavagem, 3%->etOH, 1% -> Glycerin

        EtOH_output = {"role": "Process", "compound": "EtOH", "volume": 0}
        EtOH_output['volume'] = self.volume*0.03

        glycerin_output = {"role": "Process", "compound": "glycerin", "volume": 0}
        glycerin_output['volume'] = self.volume*0.01

        washing_solution_output = {"role": "Process", "compound": "washing_solution", "volume": 0}
        washing_solution_output['volume'] = self.volume*0.96

        print()
        print(EtOH_output)
        self.next_containers["EtOH_dryer"].sendall(bytes(json.dumps(EtOH_output), encoding='utf-8'))
        #self.next_containers["Glycerin_tank"].sendall(bytes(json.dumps(glycerin_output), encoding='utf-8'))
        #self.next_containers["Washing_tank"].sendall(bytes(json.dumps(washing_solution_output), encoding='utf-8'))

    def decant(self):
        print("Entrou no decant")
        self.cycle_count += 1
        self.status = "Working"
        sleep(self.decanter.rest_time)
        self.status = "Waiting"
        self.decanter.pass_content()



    
    


 
# Refer to server.py for inherited class
class DecanterSocket(Server):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.decanter = Decanter()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevents "Address already in use"
        self.s.bind((self.host, self.port))

    def listen(self):
        self.s.listen()
        print("Listening on %s:%d" %(self.host, self.port))
        while True:
            conn, addr = self.s.accept()
            #conn.settimeout(30)
            start_new_thread(self.handle_client_thread, (conn, addr))

    
    def handle_client_thread(self, conn, addr):
        print(f"Connected: {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if (data):
                    data = json.loads(data.decode("utf-8"))

                    if (data['role'] == 'Orchestrator'):

                        self.decanter.connect_to_tank(config['connection_host_dryer'], config['connection_port_dryer'], "EtOH_dryer")
                        #self.decanter.connect_to_tank(config['connection_host_glycerin'], config['connection_port_glycerin'], "Glycerin_tank")
                        #self.decanter.connect_to_tank(config['connection_host_washing_tank'], config['connection_port_washing_tank'], "Washing_tank")
                        while True:
                            try:
                                output = self.decanter.serialize()

                                conn.sendall(bytes(json.dumps(output), encoding='utf-8'))
                                print(self.decanter.shouldRest)
                                if (self.decanter.shouldRest):
                                    self.decanter.decant()
                                else:
                                    sleep(1)
                                
                            except:
                                output = {
                                    "error": "Connection between components is broken, please contact maintenance",
                                    "data": ""
                                    }
                                #conn.sendall((bytes(json.dumps(output), encoding='utf-8')))
                    else:

                        output = self.decanter.receive_content(data)
                        conn.sendall(bytes(json.dumps(output), encoding='utf-8'))

            except Exception as e:
                print(e)
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = DecanterSocket(config['host'], config['port']).listen()
   