import socket
from _thread import *
from time import sleep
import json

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class Decanter():
    def __init__(self, capacity = 5, rest_time = 5):
        self.capacity = capacity
        self.rest_time = rest_time
        self.status = "Waiting"
        self.next_containers = {}
        self.cycle_count = 0

        self.content = {
            "mixed_compound": 0,
            "EtOH": 0,
            "glycerin": 0,
            "solution": 0
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
            "solution": self.content["solution"],
            "volume": self.volume
        }

    # EtOH, Glycerin, wash_solution
    def connect_to_tank(self, host, port, nickname):
        self.next_containers[nickname] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_containers[nickname].connect((host, int(port)))

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
            self.content[compound] = 0
    
    def pass_content(self):
        # 96% -> lavagem, 3%->etOH, 1% -> Glycerin


        self.attempt_to_send("EtOH_dryer", "EtOH", self.content["EtOH"])
        self.attempt_to_send("Glycerin_tank", "glycerin", self.content["glycerin"])
        self.attempt_to_send("Washing_tank", "solution", self.content["solution"])

        self.volume = 0

    def attempt_decant(self, conn):
        if (self.content["mixed_compound"] == 0):
            self.pass_content()
        else:
            self.status = "Working"
            
            # ensure that client is updated
            conn.sendall(bytes(json.dumps(self.serialize()), encoding='utf-8'))

            sleep(5*float(config['globals']['timescale']))
            
            self.content["EtOH"] = self.content["mixed_compound"]*0.03
            self.content["glycerin"] = self.content["mixed_compound"]*0.01
            self.content["solution"] = self.content["mixed_compound"]*0.96
            
            self.content["mixed_compound"] = 0
            self.cycle_count += 1
            self.status = "Waiting"

            # ensure that client is updated
            conn.sendall(bytes(json.dumps(self.serialize()), encoding='utf-8'))
            self.pass_content()
            self.cycle_count += 1


class DecanterSocket():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

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

                        self.decanter.connect_to_tank(config['connection']['ethanol_dryer_host'], config['connection']['ethanol_dryer_port'], "EtOH_dryer")
                        self.decanter.connect_to_tank(config['connection']['glycerin_tank_host'], config['connection']['glycerin_tank_port'], "Glycerin_tank")
                        self.decanter.connect_to_tank(config['connection']['washing_tank1_host'], config['connection']['washing_tank1_port'], "Washing_tank")
                        while True:
                            try:
                                if (self.decanter.should_rest):
                                    self.decanter.attempt_decant(conn)

                                conn.sendall(bytes(json.dumps(self.decanter.serialize()), encoding='utf-8'))
                                sleep(1*float(config['globals']['timescale']))
                                
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

server = DecanterSocket(config['connection']['decanter_host'], config['connection']['decanter_port']).listen()