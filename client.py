import socket
from _thread import *
import json
from time import sleep
import os
import configparser

import tkinter as tk
from tkinter import ttk

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

config = configparser.ConfigParser()
config.read('config.ini')

second_cnt = 0

output = {
    "reactor": {"EtOH": 0, "NaOH": 0, "oil": 0, "mixed_compound": 0,"status": "Waiting", "cycle_count": 0, "volume": 0},
    "oil_tank": {"oil": 0},
    "NaOH_tank": {"NaOH": 0},
    "EtOH_tank": {"EtOH": 0},
    "decanter": {"status": "Waiting", "cycle_count": 0, "mixed_compound": 0, "EtOH": 0, "glycerin": 0, "solution": 0, "volume": 0},
    "etanol_dryer": None,
    "glycerin_tank": None,
    "1st_washing_tank": None,
    "2nd_washing_tank": None,
    "3rd_washing_tank": None,
    "biodiesel_dryer": None,
    "biodiesel_tank": None
    #"test1": None,
}

root = None

def connectToServer(host, port, message, type):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))

    while (True):
        s.sendall(bytes(json.dumps(message), encoding='utf-8'))
        data = s.recv(1024)
        if (data):
            try:
                #print(f"\nResposta do servidor: {dados.decode()}")
                output[type] = json.loads(data.decode("utf-8"))
                sleep(1*float(config['globals']['timescale']))
            except:
                pass

def start_gui():
    # root window
    root = tk.Tk()
    root.geometry("1500x1000")
    root.title('Login')
    root.resizable(0, 0)

    # configure the grid
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=1)

    oil_tank_lbl = ttk.Label(root, text="Oil Tank")
    oil_tank_lbl.grid(column=0, row=0, sticky=tk.N, padx=0, pady=0)

    oil_tank_vol_lbl = ttk.Label(root, text="Volume:")
    oil_tank_vol_lbl.grid(column=0, row=1, sticky=tk.W, padx=0, pady=0)

    oil_tank_vol_entry = ttk.Entry(root)
    oil_tank_vol_entry.grid(column=0, row=1, sticky=tk.N, padx=0, pady=5)

    #############################################################################

    NaOH_tank_lbl = ttk.Label(root, text="NaOH Tank")
    NaOH_tank_lbl.grid(column=1, row=0, sticky=tk.N, padx=0, pady=0)

    NaOH_tank_vol_lbl = ttk.Label(root, text="Volume:")
    NaOH_tank_vol_lbl.grid(column=1, row=1, sticky=tk.W, padx=0, pady=0)

    NaOH_tank_vol_entry = ttk.Entry(root)
    NaOH_tank_vol_entry.grid(column=1, row=1, sticky=tk.N, padx=0, pady=5)   

    #############################################################################

    EtOH_tank_lbl = ttk.Label(root, text="EtOH Tank")
    EtOH_tank_lbl.grid(column=2, row=0, sticky=tk.N, padx=0, pady=0)

    EtOH_tank_vol_lbl = ttk.Label(root, text="Volume:")
    EtOH_tank_vol_lbl.grid(column=2, row=1, sticky=tk.W, padx=0, pady=0)

    EtOH_tank_vol_entry = ttk.Entry(root)
    EtOH_tank_vol_entry.grid(column=2, row=1, sticky=tk.N, padx=0, pady=5)   

    #############################################################################

    reactor_lbl = ttk.Label(root, text="Reactor")
    reactor_lbl.grid(column=3, row=0, sticky=tk.N, padx=0, pady=0)

    reactor_vol_lbl = ttk.Label(root, text="Volume:")
    reactor_vol_lbl.grid(column=3, row=1, sticky=tk.W, padx=0, pady=0)
    reactor_vol_entry = ttk.Entry(root)
    reactor_vol_entry.grid(column=3, row=1, sticky=tk.N, padx=0, pady=5)

    reactor_status_lbl = ttk.Label(root, text="Status:")
    reactor_status_lbl.grid(column=3, row=3, sticky=tk.W, padx=0, pady=0)
    reactor_status_entry = ttk.Entry(root)
    reactor_status_entry.grid(column=3, row=3, sticky=tk.N, padx=0, pady=5)

    reactor_cycle_lbl = ttk.Label(root, text="Cycle no.:")
    reactor_cycle_lbl.grid(column=3, row=4, sticky=tk.W, padx=0, pady=0)
    reactor_cycle_entry = ttk.Entry(root)
    reactor_cycle_entry.grid(column=3, row=4, sticky=tk.N, padx=0, pady=5) 

    reactor_compound_lbl = ttk.Label(root, text="Reactor Prod:")
    reactor_compound_lbl.grid(column=3, row=5, sticky=tk.W, padx=0, pady=0)
    reactor_compound_entry = ttk.Entry(root)
    reactor_compound_entry.grid(column=3, row=5, sticky=tk.N, padx=0, pady=5) 

    reactor_oil_lbl = ttk.Label(root, text="Oil:")
    reactor_oil_lbl.grid(column=3, row=6, sticky=tk.W, padx=0, pady=0)
    reactor_oil_entry = ttk.Entry(root)
    reactor_oil_entry.grid(column=3, row=6, sticky=tk.N, padx=0, pady=5)   

    reactor_etoh_lbl = ttk.Label(root, text="EtOH:")
    reactor_etoh_lbl.grid(column=3, row=7, sticky=tk.W, padx=0, pady=0)
    reactor_etoh_entry = ttk.Entry(root)
    reactor_etoh_entry.grid(column=3, row=7, sticky=tk.N, padx=0, pady=5)   

    reactor_naoh_lbl = ttk.Label(root, text="NaOH:")
    reactor_naoh_lbl.grid(column=3, row=8, sticky=tk.W, padx=0, pady=0)
    reactor_naoh_entry = ttk.Entry(root)
    reactor_naoh_entry.grid(column=3, row=8, sticky=tk.N, padx=0, pady=5) 

    #############################################################################

    decanter_lbl = ttk.Label(root, text="Decanter")
    decanter_lbl.grid(column=3, row=9, sticky=tk.N, padx=0, pady=5)

    decanter_vol_lbl = ttk.Label(root, text="Volume:")
    decanter_vol_lbl.grid(column=3, row=10, sticky=tk.W, padx=0, pady=0)
    decanter_vol_entry = ttk.Entry(root)
    decanter_vol_entry.grid(column=3, row=10, sticky=tk.N, padx=0, pady=5)

    decanter_status_lbl = ttk.Label(root, text="Status:")
    decanter_status_lbl.grid(column=3, row=11, sticky=tk.W, padx=0, pady=0)
    decanter_status_entry = ttk.Entry(root)
    decanter_status_entry.grid(column=3, row=11, sticky=tk.N, padx=0, pady=5)

    decanter_cycle_lbl = ttk.Label(root, text="Cycle no.:")
    decanter_cycle_lbl.grid(column=3, row=12, sticky=tk.W, padx=0, pady=0)
    decanter_cycle_entry = ttk.Entry(root)
    decanter_cycle_entry.grid(column=3, row=12, sticky=tk.N, padx=0, pady=5) 

    decanter_compound_lbl = ttk.Label(root, text="Reactor cmp:")
    decanter_compound_lbl.grid(column=3, row=13, sticky=tk.W, padx=0, pady=0)
    decanter_compound_entry = ttk.Entry(root)
    decanter_compound_entry.grid(column=3, row=13, sticky=tk.N, padx=0, pady=5) 

    decanter_etoh_lbl = ttk.Label(root, text="EtOH:")
    decanter_etoh_lbl.grid(column=3, row=14, sticky=tk.W, padx=0, pady=0)
    decanter_etoh_entry = ttk.Entry(root)
    decanter_etoh_entry.grid(column=3, row=14, sticky=tk.N, padx=0, pady=5)   

    decanter_glycerin_lbl = ttk.Label(root, text="Glycerin:")
    decanter_glycerin_lbl.grid(column=3, row=15, sticky=tk.W, padx=0, pady=0)
    decanter_glycerin_entry = ttk.Entry(root)
    decanter_glycerin_entry.grid(column=3, row=15, sticky=tk.N, padx=0, pady=5)   

    decanter_solution_lbl = ttk.Label(root, text="Solution:")
    decanter_solution_lbl.grid(column=3, row=16, sticky=tk.W, padx=0, pady=0)
    decanter_solution_entry = ttk.Entry(root)
    decanter_solution_entry.grid(column=3, row=16, sticky=tk.N, padx=0, pady=5) 

    def update_gui():
        if (second_cnt < int(config["globals"]["end_time"])):
            print("hm")
            oil_tank_vol_entry.delete(0, 'end')
            oil_tank_vol_entry.insert(0, str(round(output["oil_tank"]["oil"], 3)) + "L")

            ###############################################################################
            NaOH_tank_vol_entry.delete(0, 'end')
            NaOH_tank_vol_entry.insert(0, str(round(output["NaOH_tank"]["NaOH"], 3)) + "L")

            ###############################################################################
            EtOH_tank_vol_entry.delete(0, 'end')
            EtOH_tank_vol_entry.insert(0, str(round(output["EtOH_tank"]["EtOH"], 3)) + "L")

            ################################ Reactor ##################################
            reactor_vol_entry.delete(0, 'end')
            reactor_vol_entry.insert(0, str(round(output["reactor"]["volume"], 3)) + "L")

            reactor_status_entry.delete(0, 'end')
            reactor_status_entry.insert(0, output["reactor"]["status"])

            reactor_cycle_entry.delete(0, 'end')
            reactor_cycle_entry.insert(0, str(output["reactor"]["cycle_count"]))

            reactor_compound_entry.delete(0, 'end')
            reactor_compound_entry.insert(0, str(round(output["reactor"]["mixed_compound"], 3)) + "L")

            reactor_oil_entry.delete(0, 'end')
            reactor_oil_entry.insert(0, str(round(output["reactor"]["oil"], 3)) + "L")

            reactor_etoh_entry.delete(0, 'end')
            reactor_etoh_entry.insert(0, str(round(output["reactor"]["EtOH"], 3)) + "L")

            reactor_naoh_entry.delete(0, 'end')
            reactor_naoh_entry.insert(0, str(round(output["reactor"]["NaOH"], 3)) + "L")

            ###############################  Decanter ####################################
            decanter_vol_entry.delete(0, 'end')
            decanter_vol_entry.insert(0, str(round(output["decanter"]["volume"], 3)) + "L")

            decanter_status_entry.delete(0, 'end')
            decanter_status_entry.insert(0, output["decanter"]["status"])

            decanter_cycle_entry.delete(0, 'end')
            decanter_cycle_entry.insert(0, str(output["decanter"]["cycle_count"]))

            decanter_compound_entry.delete(0, 'end')
            decanter_compound_entry.insert(0, str(round(output["decanter"]["mixed_compound"], 3)) + "L")

            decanter_etoh_entry.delete(0, 'end')
            decanter_etoh_entry.insert(0, str(round(output["decanter"]["EtOH"], 3)) + "L")

            decanter_glycerin_entry.delete(0, 'end')
            decanter_glycerin_entry.insert(0, str(round(output["decanter"]["glycerin"], 3)) + "L")

            decanter_solution_entry.delete(0, 'end')
            decanter_solution_entry.insert(0, str(round(output["decanter"]["solution"], 3)) + "L")
            
            root.after(int(1000*float(config['globals']['timescale'])), update_gui)  # run again after 1000ms (1s)
        else:
            pass
    root.after(int(1000*float(config['globals']['timescale'])), update_gui)

    root.mainloop()

try:
    
    start_new_thread(start_gui, ())

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
        {"role": "Orchestrator"}, "oil_tank"))
    
    start_new_thread(connectToServer, (
        config['connection']['caustic_soda_tank_host'],
        config['connection']['caustic_soda_tank_port'],
        {"role": "Orchestrator"}, "NaOH_tank"))

    start_new_thread(connectToServer, (
        config['connection']['ethanol_tank_host'],
        config['connection']['ethanol_tank_port'],
        {"role": "Orchestrator"}, "EtOH_tank"))

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
        config['connection']['washing_tank2_host'],
        config['connection']['washing_tank2_port'],
        {"role": "Orchestrator"}, "2nd_washing_tank"))

    start_new_thread(connectToServer, (
        config['connection']['washing_tank3_host'],
        config['connection']['washing_tank3_port'],
        {"role": "Orchestrator"}, "3rd_washing_tank"))
    
    start_new_thread(connectToServer, (
        config['connection']['biodiesel_dryer_host'],
        config['connection']['biodiesel_dryer_port'],
        {"role": "Orchestrator"}, "biodiesel_dryer"))

    start_new_thread(connectToServer, (
        config['connection']['biodiesel_tank_host'],
        config['connection']['biodiesel_tank_port'],
        {"role": "Orchestrator"}, "biodiesel_tank"))

    #start_new_thread(connectToServer, (
    #    config['testing_servers']['test1_host'],
    #    config['testing_servers']['test1_port'],
    #    {"role": "Orchestrator"}, "test1"))
    
    for second_cnt in range (1, int(config["globals"]["end_time"])+1):#3600):
        clearConsole()
        print("Oil Tank:")
        print(output["oil_tank"])
        print("\n")

        print("Caustic Soda Tank:")
        print(output["NaOH_tank"])
        print("\n")

        print("Ethanol Tank:")
        print(output["EtOH_tank"])
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

        print("Second Washing Tank:")
        print(output["2nd_washing_tank"])
        print("\n")

        print("Third Washing Tank:")
        print(output["3rd_washing_tank"])
        print("\n")

        print("Biodiesel Dryer:")
        print(output["biodiesel_dryer"])
        print("\n")

        print("Biodiesel Tank:")
        print(output["biodiesel_tank"])
        print("\n")

        #print("Test Output:")
        #print(output["test1"])
        #print("\n")
        sleep(1*float(config['globals']['timescale']))


except Exception as e:
    print("Err: " + str(e))
    pass


while True:
   pass