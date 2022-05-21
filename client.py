import socket
from _thread import *
import json

code = "10000000"
n = "6000"

message = code + "&" + n

def connectToServer(host, port, message):
    print("test2")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print(s)

    while (True):
        s.sendall(bytes(json.dumps(message), encoding='utf-8'))
        dados = s.recv(1024)
        if (dados):
            print(f"Resposta do servidor: {dados.decode()}")

try:
    start_new_thread(connectToServer, ('localhost', 5000, {"role": "Observer"}))
    #start_new_thread(connectToServer, ('localhost', 5001, {"role": "observer"}))
except:
    pass


while True:
   pass