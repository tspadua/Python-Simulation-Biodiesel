import socket
from _thread import *
from server import Server
from time import sleep
import json

class ChemicalTank():
    def __init__(self, compound, flow_rate = 0):
        self.next_container = None
        self.flow_rate = flow_rate
        self.compound = compound # e.g. "oil"
        self.volume = 0
    
    def serialize(self):        
        return {
            self.compound: self.volume
        }

    def connect_to_tank(self, host, port):
        self.next_container = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_container.connect((host, port))

    def pour_content(self, volume):
        self.volume = round(self.volume + volume,2)

    # pass content from this container to another
    def pass_content(self):
        content_output = {"role": "Process", "content": {}}
        if (self.volume > self.flow_rate):
            content_output["content"][self.compound] = self.flow_rate
            self.volume = round(self.volume - self.flow_rate, 2)
        else:
            content_output["content"][self.compound] = 0
        
        self.next_container.sendall(bytes(json.dumps(content_output), encoding='utf-8'))





