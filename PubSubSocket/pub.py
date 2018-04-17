import socket
import sys
import json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


NAME = sys.argv[1]
HOST = 'localhost'
iPORT = 0

if NAME == "P1":
    PORT  = 8090
    iPORT = 8092
elif NAME == "P2":
    PORT  = 8091
    iPORT = 8094
else:
    print bcolors.FAIL +"ERROR: PUBLISHER NOT FOUND" + bcolors.ENDC
    sys.exit()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(5) # become a server socket, maximum 5 connections

print bcolors.BOLD,  NAME, " is online in HOST=", HOST," PORT=", PORT, bcolors.ENDC

def publish(publication):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pub = json.dumps({'NAME':NAME, 'PUBLICATION':publication, 'TYPE':'PUBLICATION'})
    try:
        clientsocket.connect((HOST, iPORT))
        clientsocket.send(pub)
        print bcolors.OKBLUE +"CONNECTION STABLISHED WITH INTERMEDIATE NETWORK... WAITING RESPONSE"+ bcolors.ENDC
        buf = clientsocket.recv(256)
        if len(buf) > 0:
            decodedMessage = json.loads(buf)
            if decodedMessage['ANSWER'] == "NO SUBMITERS":
                print bcolors.FAIL + "NO SUBMITERS FOUND TO ", publication, bcolors.ENDC
            else:
                print bcolors.OKGREEN +"PUBLICATION SUBMITED!"+ bcolors.ENDC
                print decodedMessage['ANSWER']
    except:
        print bcolors.FAIL + "ERROR: CONNECTION NOT STABLISHED WITH INTERMEDIATE NETWORK"+ bcolors.ENDC


while True:
    print bcolors.HEADER + "What do you want to publish?" + bcolors.ENDC
    publication = raw_input()
    publish(publication)
