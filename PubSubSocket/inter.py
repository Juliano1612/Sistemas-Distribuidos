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

subscriberList = []

NAME = sys.argv[1]
HOST = 'localhost'
iPORT = 0
iPORT1 = 0

portList = [("P1",8090),("P2",8091),\
            ("I1",8092),("I2",8093),("I3",8094),\
            ("A1",8095),("A2",8096),("A3",8097),]

if NAME == "I1":
    PORT  = 8092
    iPORT = 8093
elif NAME == "I2":
    PORT  = 8093
    iPORT, iPORT1 = 8092,8094
    aPORT = [8095, 8096]
elif NAME == "I3":
    PORT  = 8094
    iPORT = 8093
    aPORT = 8097
else:
    print bcolors.FAIL, "ERROR: INTERMEDIATER NOT FOUND", bcolors.ENDC
    sys.exit()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(5) # become a server socket, maximum 5 connections

print bcolors.BOLD, NAME, " is online in HOST=", HOST," PORT=", PORT, bcolors.ENDC

def publicationReceived(connection, message):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    matches = [x for x in subscriberList if x['SUBSCRIPTION']==message['PUBLICATION']]
    if len(matches) > 0:
        answer = json.dumps({'NAME': NAME, 'ANSWER': 'SUBMITER FOUND'})
        print bcolors.FAIL, "SUBMITER FOUND TO", matches[0]['SUBSCRIPTION'], "... SENDING PUBLICATION", bcolors.ENDC
        try:
            portSend = [x for x in portList if x[0]==matches[0]['NAME']]
            clientsocket.connect((HOST, portSend[0][1]))
            clientsocket.send(json.dumps(message))
            print bcolors.OKGREEN, "PUBLICATION SENDED TO ", matches[0]['NAME'], bcolors.ENDC
        except:
            print bcolors.FAIL, "ERROR: CONNECTION NOT STABLISHED WITH ", matches[0]['NAME'], bcolors.ENDC
    else:
        answer = json.dumps({'NAME': NAME, 'ANSWER': 'NO SUBMITERS'})
        print bcolors.FAIL, "NO SUBMITERS FOUND TO ", message['PUBLICATION'], bcolors.ENDC
    connection.send(answer)

def messageReceived(connection, message):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if message['TYPE'] == "SUBSCRIPTION":
        answer = json.dumps({'NAME': NAME, 'ANSWER': 'SUBSCRIPTION RECEIVED'})
        connection.send(answer)
        print bcolors.OKGREEN,"SUBSCRIPTION MESSAGE RECEIVED FROM ", message['NAME'], " -> ", message['SUBSCRIPTION'], "SAVED", bcolors.ENDC
        if NAME == "I2":
            subscriberList.append(message)
            message1 = copy.deepcopy(message)
            message1['NAME'] = NAME;
            try:
                clientsocket.connect((HOST, iPORT))
                clientsocket.send(json.dumps(message1))
                print bcolors.OKBLUE,"SUBSCRIPTION SENDED TO I1... WAITING CONFIRMATION", bcolors.ENDC
                buf = clientsocket.recv(256)
                if len(buf) > 0:
                    decodedMessage = json.loads(buf)
                    if decodedMessage['ANSWER'] == "SUBSCRIPTION RECEIVED":
                        print bcolors.OKGREEN,"SUBSCRIPTION RECEIVED BY I1", bcolors.ENDC
            except:
                print bcolors.FAIL,"ERROR: CONNECTION NOT STABLISHED WITH I1", bcolors.ENDC
        else:
            subscriberList.append(message)
            print bcolors.OKGREEN,"SUBSCRIPTION SAVED", bcolors.ENDC
    elif message['TYPE'] == "PUBLICATION":
        print bcolors.OKBLUE, "PUBLICATION RECEIVED... FORWARDING", bcolors.ENDC
        publicationReceived(connection, message)



def subscriptionReceived(connection, message):
    answer = json.dumps({'NAME': NAME, 'ANSWER': 'SUBSCRIPTION RECEIVED'})
    subscriberList.append(message)
    print bcolors.OKGREEN, "SUBSCRIPTION RECEIVED AND ADDED TO LIST: ", message, bcolors.ENDC
    connection.send(answer)
    print bcolors.OKBLUE, "SENDING SUBSCRIPTION TO NEIGHBORS", bcolors.ENDC
    send = json.dumps({'NAME': NAME, 'SUBSCRIPTION': message['SUBSCRIPTION'], 'TYPE':'SUBSCRIPTION'})
    advertiseNeighbors(send)


def advertiseNeighbors(message):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if NAME == "I2":
        try:
            clientsocket.connect((HOST, iPORT))
            clientsocket.send(message)
            print bcolors.OKBLUE, "SUBSCRIPTION SENDED TO I1... WAITING CONFIRMATION", bcolors.ENDC
            buf = clientsocket.recv(256)
            if len(buf) > 0:
                decodedMessage = json.loads(buf)
                if decodedMessage['ANSWER'] == "SUBSCRIPTION RECEIVED":
                    print bcolors.OKGREEN, "SUBSCRIPTION RECEIVED BY I1", bcolors.ENDC
            try:
                clientsocket1.connect((HOST, iPORT1))
                clientsocket1.send(message)
                print bcolors.OKBLUE, "SUBSCRIPTION SENDED TO I3... WAITING CONFIRMATION", bcolors.ENDC
                buf = clientsocket1.recv(256)
                if len(buf) > 0:
                    decodedMessage = json.loads(buf)
                    if decodedMessage['ANSWER'] == "SUBSCRIPTION RECEIVED":
                        print bcolors.OKGREEN,"SUBSCRIPTION RECEIVED BY I3 ", bcolors.ENDC
            except:
                print bcolors.FAIL,"ERROR: CONNECTION NOT STABLISHED WITH I3", bcolors.ENDC
        except:
            print bcolors.FAIL,"ERROR: CONNECTION NOT STABLISHED WITH I1", bcolors.ENDC



    elif NAME == "I3":
        try:
            clientsocket.connect((HOST, iPORT))
            clientsocket.send(message)
            print bcolors.OKBLUE, "SUBSCRIPTION SENDED TO I2... WAITING CONFIRMATION", bcolors.ENDC
            buf = clientsocket.recv(256)
            if len(buf) > 0:
                decodedMessage = json.loads(buf)
                if decodedMessage['ANSWER'] == "SUBSCRIPTION RECEIVED":
                    print bcolors.OKGREEN, "SUBSCRIPTION RECEIVED BY I2 ", bcolors.ENDC
        except:
            print bcolors.FAIL, "ERROR: CONNECTION NOT STABLISHED WITH I2", bcolors.ENDC


while True:
    connection, address = serversocket.accept()
    buf = connection.recv(256)
    if len(buf) > 0:
        decodedMessage = json.loads(buf)
        if decodedMessage['NAME'].startswith('P'):
            publicationReceived(connection, decodedMessage)
        elif decodedMessage['NAME'].startswith('I'):
            messageReceived(connection, decodedMessage)
            # print subscriberList
        elif decodedMessage['NAME'].startswith('A'):
            subscriptionReceived(connection, decodedMessage)
            # print subscriberList
