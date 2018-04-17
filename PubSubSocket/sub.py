#sudo fuser -k 8097/tcp 8096/tcp 8095/tcp
import socket
import sys
import json
import threading

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

if NAME == "A1":
    PORT  = 8095
    iPORT = 8093
elif NAME == "A2":
    PORT  = 8096
    iPORT = 8093
elif NAME == "A3":
    PORT  = 8097
    iPORT = 8094
else:
    print bcolors.FAIL,"ERROR: SUBSCRIBER NOT FOUND", bcolors.ENDC
    sys.exit()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(5) # become a server socket, maximum 5 connections

print bcolors.BOLD ,NAME, " is online in HOST=", HOST," PORT=", PORT, bcolors.ENDC

def subscribe(subscription):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sub = json.dumps({'NAME':NAME, 'SUBSCRIPTION':subscription})
    try:
        clientsocket.connect((HOST, iPORT))
        clientsocket.send(sub)
        print bcolors.OKBLUE,"CONNECTION STABLISHED TO INTERMEDIATE NETWORK... WAITING RESPONSE", bcolors.ENDC
        buf = clientsocket.recv(256)
        if len(buf) > 0:
            decodedMessage = json.loads(buf)
            if decodedMessage['ANSWER'] == "SUBSCRIPTION RECEIVED":
                print bcolors.OKGREEN,"SUBSCRIPTION ", subscription, " SENDED SUCCESSFULLY", bcolors.ENDC
    except:
        print bcolors.FAIL,"ERROR: CONNECTION NOT STABLISHED WITH INTERMEDIATE NETWORK", bcolors.ENDC

def waitPublications():
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(256)
        if len(buf) > 0:
            decodedMessage = json.loads(buf)
            print bcolors.OKGREEN,"PUBLICATION", decodedMessage['PUBLICATION'] ,"RECEIVED AND SUBSCRIBED!", bcolors.ENDC

t1 = threading.Thread(target=waitPublications, args=())
t1.start()
while True:
    try:
        print bcolors.HEADER,"What do you want to subscribe?", bcolors.ENDC
        subscription = raw_input()
        subscribe(subscription)
    except KeyboardInterrupt:
        t1.join()
