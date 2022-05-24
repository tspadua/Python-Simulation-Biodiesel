import socket
from _thread import *
from time import sleep
import json

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class WashingTank():

    def __init__(self, flow_rate = 1.5, waste_factor = 0.025):
        self.next_container = None
        self.flow_rate = flow_rate
        self.waste_factor = waste_factor
        self.solution = 0
        self.emulsion = 0

    def serialize(self):
        return {
            "solution": self.solution,
            "emulsion": self.emulsion,
        }

    def connect_to_tank(self, host, port):
        self.next_container = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_container.connect((host, int(port)))
 
    def receive_and_clean_content(self, data):

        emulsion = round(data["volume"]*self.waste_factor,2)

        self.solution = round(self.solution + (data["volume"] - emulsion), 2)
        self.emulsion = round(self.emulsion + emulsion, 2)
        
        return {"accepted": True}
    
    def pass_content(self):
        if (self.solution > 0):
            volume = self.solution
            if (self.solution >= self.flow_rate):
                volume = self.flow_rate
            
            self.solution -= volume

            content = {
                "role": "Process",
                "compound": "solution",
                "volume": volume
            }
        
            self.next_container.sendall(bytes(json.dumps(content), encoding='utf-8'))
            
        

class WashingTankSocket():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

        self.washing_tank = WashingTank()

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
                        self.washing_tank.connect_to_tank(config['testing_servers']['test1_host'], config['testing_servers']['test1_port'])

                        while True:
                            try:
                                # send current information to client
                                conn.sendall(bytes(json.dumps(self.washing_tank.serialize()), encoding='utf-8'))
                                self.washing_tank.pass_content()
                                sleep(1*float(config['globals']['timescale']))
                                
                            except:
                                output = {
                                    "error": "Connection between components is broken, please contact maintenance",
                                    "data": ""
                                    }
                                #conn.sendall((bytes(json.dumps(output), encoding='utf-8')))
                    else:
                        output = self.washing_tank.receive_and_clean_content(data)
                        conn.sendall(bytes(json.dumps(output), encoding='utf-8'))

            except Exception as e:
                print(e)
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = WashingTankSocket(config['connection']['washing_tank1_host'], config['connection']['washing_tank1_port']).listen()
