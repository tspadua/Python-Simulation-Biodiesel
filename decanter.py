import socket
from _thread import *
from time import sleep
from server import Server
from chemical_tank import ChemicalTank
import json
import random

config = {
    "host": "localhost",
    "port": 6001,
    "connection_host": "localhost",
    "connection_port": 9000
}

class Decanter():
    def __init__(self):
        pass
    
    def serialize(self):
        return {
            "decanter": self.volume
        }