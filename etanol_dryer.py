import socket
from _thread import *
from time import sleep
import json

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class EtanolDryer():

    def __init__(self, waste_factor = 0.05, time_per_liter = 5, threshold = 1):
        self.status = "Waiting"
        self.next_container = None
        self.threshold = threshold
        self.time_per_liter = time_per_liter
        self.waste_factor = waste_factor
        self.volume = 0
        self.waste = 0
    
    @property
    def should_start_process(self):
        if ((self.status == "Waiting") and (self.volume >= self.threshold)):
            return True
        else:
            return False

    def serialize(self):
        return {
            "EtOH": self.volume,
            "waste": self.waste,
            "status": self.status
        }
    
    def calculate_drying_time(self):
        drying_time = self.volume*self.time_per_liter 
        return drying_time

    def connect_to_tank(self, host, port):
        self.next_container = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_container.connect((host, int(port)))
 
    def receive_content(self, data):
        if (self.status == "Waiting"):
            self.volume += data["volume"]

            return {"accepted": True}
        else:
            return {"accepted": False}

    def dry(self):
            sleep(self.calculate_drying_time()*float(config['globals']['timescale']))

            amount_lost = self.volume*self.waste_factor
            self.waste += amount_lost
            self.volume -= amount_lost

            self.pass_content()

    
    def pass_content(self):
            content = {
                "role": "Process",
                "compound": "EtOH",
                "volume": self.volume
            }
            self.next_container.sendall(bytes(json.dumps(content), encoding='utf-8'))

            self.volume = 0
        

class EtanolDryerSocket():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

        self.dryer = EtanolDryer()

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
                        self.dryer.connect_to_tank(config['connection']['washing_tank1_host'], config['connection']['washing_tank1_port'])

                        while True:
                            try:

                                if (self.dryer.should_start_process):

                                    self.dryer.status = "Working"
                                    # Update client about working status
                                    conn.sendall(bytes(json.dumps(self.dryer.serialize()), encoding='utf-8'))
                                    self.dryer.dry()
                                    self.dryer.status = "Waiting"

                                # send current information to client
                                conn.sendall(bytes(json.dumps(self.dryer.serialize()), encoding='utf-8'))

                                sleep(1*float(config['globals']['timescale']))
                                
                            except:
                                output = {
                                    "error": "Connection between components is broken, please contact maintenance",
                                    "data": ""
                                    }
                                #conn.sendall((bytes(json.dumps(output), encoding='utf-8')))
                    else:
                        output = self.dryer.receive_content(data)
                        conn.sendall(bytes(json.dumps(output), encoding='utf-8'))

            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = EtanolDryerSocket(config['connection']['ethanol_dryer_host'], config['connection']['ethanol_dryer_port']).listen()
