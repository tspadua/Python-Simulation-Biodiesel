import socket
from _thread import *
from time import sleep
import json

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Refer to server.py for inherited class
class TestTank():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

        self.content = {}

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevents "Address already in use"
        self.s.bind((self.host, int(self.port)))
    
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
                        sleep(1*float(config['globals']['timescale']))
                        output = json.dumps(self.content)
                        conn.sendall((bytes(output, encoding='utf-8')))
                    else:
                        print(data)
                        if (data['compound'] not in self.content):
                            self.content[data['compound']] = 0
                        self.content[data['compound']] += data['volume']
                        #self.content[data['compound']] += data['volume']
                        output = json.dumps({"accepted": True})
                        conn.sendall((bytes(output, encoding='utf-8')))
            except:
                conn.close()
                print(f"Disconnected: {addr}")
                return False

server = TestTank(config['testing_servers']['test1_host'], config['testing_servers']['test1_port']).listen()
