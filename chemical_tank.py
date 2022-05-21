import socket
from _thread import *
from server import Server
import json

class ChemicalTank():
    def __init__(self, flow_rate = None, capacity = None, **kwargs):
        self.next_container = None
        self.flow_rate = flow_rate
        self.capacity = capacity
        self.content = kwargs # receives a dictionary e.g. {sodium: 12.3, iron: 3.0}
        self.status = "Waiting"
    
    def serialize(self):
        return {
            "status": self.status,
            "content": self.content, 
            "volume": str(sum(self.content.values())) + 'L'
        }

    def connect_to_tank(self, host, port):
        self.next_container = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_container.connect((host, port))

    def pour_content(self, **kwargs):
        for key, value in kwargs.iteritems():
            self.content[key] = self.content.get(key, 0) + value
    
    # TODO: CREATE FUNCTION FOR ADDING CONTENT
