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
        self.next_containers = {}
        self.cycle_count = 0

        self.content = {
            "mixed_compound": 0,
            "EtOH": 0,
            "glycerin": 0,
            "washing_solution": 0
        }

    @property 
    def volume(self):
        return sum(self.content.values())

    @property
    def should_rest(self):
        if (self.volume == self.capacity):
            return True
        else:
            return False
    
    def serialize(self):
        return {
            "status": self.status,
            "cycle_count": self.cycle_count,
            "mixed_compound": self.content["mixed_compound"],
            "EtOH": self.content["EtOH"],
            "glycerin": self.content["glycerin"],
            "washing_solution": self.content["washing_solution"]
        }

    # EtOH, Glycerin, wash_solution
    def connect_to_tank(self, host, port, nickname):
        self.next_containers[nickname] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_containers[nickname].connect((host, port))

    def receive_content(self, data):
        if (self.volume + data["volume"] <= self.capacity):

            self.content["mixed_compound"] += data["volume"]
            return {"accepted": True}
        else:
            return {"accepted": False}

    def attempt_to_send(self, destination, compound, volume):

        output = {"role": "Process", "compound": compound, "volume": volume}
        self.next_containers[destination].sendall(bytes(json.dumps(output), encoding='utf-8'))

        response = self.next_containers[destination].recv(1024)
        response = json.loads(response.decode("utf-8"))

        if (response["accepted"]):
            print("sent content")
            self.content[compound] = 0
    
    def pass_content(self):
        # 96% -> lavagem, 3%->etOH, 1% -> Glycerin


        self.attempt_to_send("EtOH_dryer", "EtOH", self.content["EtOH"])
        self.attempt_to_send("Glycerin_tank", "glycerin", self.content["glycerin"])
        #self.attempt_to_send("Washing_tank", "EtOH", self.content["washing_solution"])

        self.content["washing_solution"] = 0 ## TODO: CHANGE WHEN WASHING TANK IS CREATED
        #self.next_containers["EtOH_dryer"].sendall(bytes(json.dumps(EtOH_output), encoding='utf-8'))
        #self.next_containers["Glycerin_tank"].sendall(bytes(json.dumps(glycerin_output), encoding='utf-8'))
        #self.next_containers["Washing_tank"].sendall(bytes(json.dumps(washing_solution_output), encoding='utf-8'))

        self.volume = 0

    def attempt_decant(self, conn):
        if (self.content["mixed_compound"] == 0):
            self.pass_content()
        else:
            self.status = "Working"
            
            # ensure that client is updated
            conn.sendall(bytes(json.dumps(self.serialize()), encoding='utf-8'))

            sleep(5)
            
            self.content["EtOH"] = round(self.content["mixed_compound"]*0.03, 2)
            self.content["glycerin"] = round(self.content["mixed_compound"]*0.01, 2)
            self.content["washing_solution"] = round(self.content["mixed_compound"]*0.96, 2)
            
            self.content["mixed_compound"] = 0

            self.status = "Waiting"

            # ensure that client is updated
            conn.sendall(bytes(json.dumps(self.serialize()), encoding='utf-8'))
            self.pass_content()
            self.cycle_count += 1




    
    


 
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
                        self.decanter.connect_to_tank(config['connection_host_glycerin'], config['connection_port_glycerin'], "Glycerin_tank")
                        #self.decanter.connect_to_tank(config['connection_host_washing_tank'], config['connection_port_washing_tank'], "Washing_tank")
                        while True:
                            try:
                                output = self.decanter.serialize()
                                if (self.decanter.should_rest):
                                    self.decanter.attempt_decant(conn)
                                conn.sendall(bytes(json.dumps(output), encoding='utf-8'))
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