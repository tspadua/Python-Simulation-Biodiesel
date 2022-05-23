import socket
from _thread import *
import json
from time import sleep
import os

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

code = "10000000"
n = "6000"

message = code + "&" + n

output = {
    "reactor": None,
    "oil": None,
    "NaOH": None,
    "EtOH": None,
    "decanter": None,
    "test_output": None,
    "test_2": None
}

def connectToServer(host, port, message, type):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    while (True):
        s.sendall(bytes(json.dumps(message), encoding='utf-8'))
        dados = s.recv(1024)
        if (dados):
            #print(f"\nResposta do servidor: {dados.decode()}")
            output[type] = dados.decode()
            sleep(1)

try:
    start_new_thread(connectToServer, ('localhost', 9001, {"role": "Orchestrator"}, "test_2"))
    start_new_thread(connectToServer, ('localhost', 9000, {"role": "Orchestrator"}, "test_output"))
    start_new_thread(connectToServer, ('localhost', 5004, {"role": "Orchestrator"}, "decanter"))
    start_new_thread(connectToServer, ('localhost', 5003, {"role": "Orchestrator"}, "reactor"))
    start_new_thread(connectToServer, ('localhost', 5000, {"role": "Orchestrator"}, "oil"))
    start_new_thread(connectToServer, ('localhost', 5001, {"role": "Orchestrator"}, "NaOH"))
    start_new_thread(connectToServer, ('localhost', 5002, {"role": "Orchestrator"}, "EtOH"))
    
    while True:
        #print(output["reactor"])
        #print(output["test_output"])
        #print(output["test_2"])
        print(output["decanter"])
        print("\n\n")
        #print(output["oil"])
        #print(output["NaOH"])
        #print(output["EtOH"])
        sleep(1)
        clearConsole()
except:
    pass


while True:
   pass