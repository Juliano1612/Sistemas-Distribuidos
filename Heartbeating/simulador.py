import socket
import sys
import json, copy

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

OFFSET = 9000
HOST = 'localhost'
PORT = OFFSET-1
TIME = 0

NODE_LIST = []

for i in range(0, int(sys.argv[1])):
    NODE_LIST.append(OFFSET+i)
    print NODE_LIST[i]
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientsocket.connect((HOST, NODE_LIST[i]))
        clientsocket.send(json.dumps(sys.argv[2] +  ' ' + sys.argv[1]))
        print bcolors.OKGREEN, "CONFIGURATION SENT TO ", i ,bcolors.ENDC
    except:
        print bcolors.FAIL, "ERROR: CONNECTION NOT ESTABLISHED WITH ", i, bcolors.ENDC

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(10) # become a server socket, maximum 10 connections

while True:
    print "\nINSTANTE DE TEMPO ATUAL -> ", TIME
    option = raw_input("Enter : proximo instante de tempo\nID : conectar/desconectar noh\n")
    if option == '': #Proximo instante de tempo
        for i in range(0, len(NODE_LIST)):
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                clientsocket.connect((HOST, NODE_LIST[i]))
                clientsocket.send(json.dumps('NEXT'))
                print bcolors.OKGREEN, "NEXT INSTANT SENT TO NODE ", i ,bcolors.ENDC
            except:
                print bcolors.FAIL, "ERROR: CONNECTION NOT ESTABLISHED WITH ", i, bcolors.ENDC
    else: #Enviar mensagem de ativacao/desativacao
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientsocket.connect((HOST, NODE_LIST[int(option)]))
            clientsocket.send(json.dumps('TOGGLE'))
            print bcolors.OKGREEN, "TOGGLE TO NODE ", option ,bcolors.ENDC
        except:
            print bcolors.FAIL, "ERROR: CONNECTION NOT ESTABLISHED WITH ", i, bcolors.ENDC
    TIME += 1