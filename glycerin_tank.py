import socket
from _thread import *
from time import sleep
from server import Server
import json

config = {
    "host": "localhost",
    "port": 5006
}

class GlycerinTank():
    def __init__(self):
        self.volume = 0
    
    def serialize(self):
        return {
            "glycerin": self.volume
        }

    def pour_content(self, volume):
        self.volume = round(self.volume + volume,2)




# Refer to server.py for inherited class
class EtanolTankSocket():
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.glycerin_tank = GlycerinTank()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevents "Address already in use"
        self.s.bind((self.host, self.port))

    def listen(self):
        self.s.listen()
        print("Listening on %s:%d" %(self.host, self.port))
        while True:
            conn, addr = self.s.accept()
            start_new_thread(self.handle_client_thread, (conn, addr))
    
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

                        try:

                            while True:
                                output = self.glycerin_tank.serialize()
                                output = json.dumps(output)

                                conn.sendall((bytes(output, encoding='utf-8')))
                                sleep(1)
                                
                        except Exception as e:
                            output = {
                                "error": "Connection between components is broken, please contact maintenance",
                                "data": ""
                                }
                            conn.sendall((bytes(json.dumps(output), encoding='utf-8')))
                    else:
                        self.glycerin_tank.pour_content(data["volume"])
                        output = json.dumps({"accepted": True})
                        conn.sendall((bytes(output, encoding='utf-8')))
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = EtanolTankSocket(config['host'], config['port']).listen()
