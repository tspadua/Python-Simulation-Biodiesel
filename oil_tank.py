import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json
import random

config = {
    "host": "localhost",
    "port": 5000,
    "connection_host": "localhost",
    "connection_port": 5002
}

# Refer to server.py for inherited class
class OilTankServer(Server):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.oil_tank = ChemicalTank("oil", 0.75)

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
                    
                    if (data['role'] == 'Observe'):
                        output = self.oil_tank.serialize()
                        sleep(1)
                        output = json.dumps(output)
                        conn.sendall((bytes(output, encoding='utf-8')))
                    else:
                        try:
                            self.oil_tank.connect_to_tank(config['connection_host'], config['connection_port'])

                            second_cnt = 0
                            while True:
                                # This triggers each time 10 seconds have passed
                                if (int(second_cnt)%10 == 0):
                                    # pour between 1 to 2 liters of oil
                                    self.oil_tank.pour_content(random.randint(10, 20)/10)

                                self.oil_tank.pass_content()
                                sleep(1) # process tick rate is 1 second because the flow rate is L/s
                                second_cnt += 1
                                
                        except:
                            output = {
                                "error": "Connection between components is broken, please contact maintenance",
                                "data": ""
                                }
                            conn.sendall((bytes(json.dumps(output), encoding='utf-8')))
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = OilTankServer(config['host'], config['port']).listen()
