import socket
from _thread import *
import json
from time import sleep
import os
import configparser

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

config = configparser.ConfigParser()
config.read('config.ini')

output = {
    "reactor": None,
    "oil": None,
    "NaOH": None,
    "EtOH": None,
    "decanter": None,
    "etanol_dryer": None,
    "glycerin_tank": None,
    "1st_washing_tank": None,
    "test1": None,
}

def connectToServer(host, port, message, type):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))

    while (True):
        s.sendall(bytes(json.dumps(message), encoding='utf-8'))
        dados = s.recv(1024)
        if (dados):
            #print(f"\nResposta do servidor: {dados.decode()}")
            output[type] = dados.decode()
            sleep(1*float(config['globals']['timescale']))

try:

    start_new_thread(connectToServer, (
        config['connection']['decanter_host'],
        config['connection']['decanter_port'],
        {"role": "Orchestrator"}, "decanter"))

    start_new_thread(connectToServer, (
        config['connection']['reactor_host'],
        config['connection']['reactor_port'],
        {"role": "Orchestrator"}, "reactor"))

    start_new_thread(connectToServer, (
        config['connection']['oil_tank_host'],
        config['connection']['oil_tank_port'],
        {"role": "Orchestrator"}, "oil"))
    
    start_new_thread(connectToServer, (
        config['connection']['caustic_soda_tank_host'],
        config['connection']['caustic_soda_tank_port'],
        {"role": "Orchestrator"}, "NaOH"))

    start_new_thread(connectToServer, (
        config['connection']['ethanol_tank_host'],
        config['connection']['ethanol_tank_port'],
        {"role": "Orchestrator"}, "EtOH"))

    start_new_thread(connectToServer, (
        config['connection']['ethanol_dryer_host'],
        config['connection']['ethanol_dryer_port'],
        {"role": "Orchestrator"}, "etanol_dryer"))

    start_new_thread(connectToServer, (
        config['connection']['glycerin_tank_host'],
        config['connection']['glycerin_tank_port'],
        {"role": "Orchestrator"}, "glycerin_tank"))

    start_new_thread(connectToServer, (
        config['connection']['washing_tank1_host'],
        config['connection']['washing_tank1_port'],
        {"role": "Orchestrator"}, "1st_washing_tank"))
       
    start_new_thread(connectToServer, (
        config['testing_servers']['test1_host'],
        config['testing_servers']['test1_port'],
        {"role": "Orchestrator"}, "test1"))

    while True:
        clearConsole()
        print("Oil Tank:")
        print(output["oil"])
        print("\n")

        print("Caustic Soda Tank:")
        print(output["NaOH"])
        print("\n")

        print("Ethanol Tank:")
        print(output["EtOH"])
        print("\n")

        print("Reactor:")
        print(output["reactor"])
        print("\n")

        print("Decanter:")
        print(output["decanter"])
        print("\n")

        print("Ethanol Dryer:")
        print(output["etanol_dryer"])
        print("\n")

        print("Glycerin Tank:")
        print(output["glycerin_tank"])
        print("\n")

        print("First Washing Tank:")
        print(output["1st_washing_tank"])
        print("\n")

        print("Test Output:")
        print(output["test1"])
        print("\n")

        sleep(1*float(config['globals']['timescale']))
except Exception as e:
    print("Err: " + str(e))
    pass


while True:
   pass