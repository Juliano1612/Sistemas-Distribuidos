import socket
import sys
import json, copy, random
from random import randint
from operator import itemgetter

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
ID = int(sys.argv[1])
HOST = 'localhost'
PORT = OFFSET+int(sys.argv[1])
QTDD_POR_UNIDADE_TEMPO = int(sys.argv[2])
VIZINHOS = 0
ERASE_AFTER = 0
TIME = 0
ONLINE = True

HEARTBEAT_TABLE = []

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(10) # become a server socket, maximum 10 connections

def atualizeMyHeartbeat():
    global TIME, ID, HEARTBEAT_TABLE
    i = map(itemgetter('ID'), HEARTBEAT_TABLE).index(ID)
    HEARTBEAT_TABLE[i]['HEARTBEAT'] += 1
    HEARTBEAT_TABLE[i]['ATUALIZADO'] = 0
    HEARTBEAT_TABLE[i]['TIMESTAMP_LOCAL'] = TIME

def atualizeLastUpdateTime():
    global HEARTBEAT_TABLE, ID
    for i in range(0, len(HEARTBEAT_TABLE)):
        if HEARTBEAT_TABLE[i]['ID'] != ID:
            HEARTBEAT_TABLE[i]['ATUALIZADO'] += 1

def verifyFailNodes():
    global HEARTBEAT_TABLE, ERASE_AFTER
    for i in range(0, len(HEARTBEAT_TABLE)):
        if HEARTBEAT_TABLE[i]['ATUALIZADO'] > 2*ERASE_AFTER:
            print bcolors.WARNING, 'NODE ', HEARTBEAT_TABLE[i]['ID'], ' FAILED', bcolors.ENDC
            HEARTBEAT_TABLE.pop(i)

def gossip():
    global HEARTBEAT_TABLE, ID, HOST, VIZINHOS
    AUX_TABLE = []
    for i in range(0,len(HEARTBEAT_TABLE)):
        if HEARTBEAT_TABLE[i]['ATUALIZADO'] == 0:
            AUX_TABLE.append(HEARTBEAT_TABLE[i])
    if VIZINHOS > 1:
        destination = object()
        if len(HEARTBEAT_TABLE) > 1:
            destination = random.choice(HEARTBEAT_TABLE)
            while destination['ID'] == ID:
                destination = random.choice(HEARTBEAT_TABLE)
        else:
            index = randint(0, VIZINHOS-1)
            while index == ID:
                index = randint(0, VIZINHOS-1)
            destination = {'ID':index, 'ENDERECO': OFFSET+index}
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientsocket.connect((HOST, destination['ENDERECO']))
            clientsocket.send(json.dumps(AUX_TABLE))
            print bcolors.OKGREEN, "HEARTBEAT TABLE SENDED TO NODE ", destination['ID'] ,bcolors.ENDC
        except:
            print bcolors.FAIL, "ERROR: CONNECTION NOT ESTABLISHED WITH ", destination['ID'], bcolors.ENDC

def receiveGossip(message):
    global HEARTBEAT_TABLE, ID, TIME
    for i in range(0, len(message)):
        if message[i]['ID'] != ID:
            try:
                index = map(itemgetter('ID'), HEARTBEAT_TABLE).index(message[i]['ID'])
                HEARTBEAT_TABLE[index]['HEARTBEAT'] = message[i]['HEARTBEAT']
                HEARTBEAT_TABLE[index]['ATUALIZADO'] = 0
                HEARTBEAT_TABLE[index]['TIMESTAMP_LOCAL'] = TIME
            except:
                HEARTBEAT_TABLE.append(message[i])
                HEARTBEAT_TABLE[-1]['ATUALIZADO'] = 0
                HEARTBEAT_TABLE[-1]['TIMESTAMP_LOCAL'] = TIME

def showTable():
    global HEARTBEAT_TABLE
    print   bcolors.BOLD,bcolors.OKBLUE,'ID\tHEARTBEAT\tLOCAL TIMESTAMP\t\tLAST UPDATE', bcolors.ENDC
    for i in range(0, len(HEARTBEAT_TABLE)):
        print  bcolors.OKBLUE,' ',HEARTBEAT_TABLE[i]['ID'],'\t  ',HEARTBEAT_TABLE[i]['HEARTBEAT'],'\t\t    ',HEARTBEAT_TABLE[i]['TIMESTAMP_LOCAL'],'\t\t',HEARTBEAT_TABLE[i]['ATUALIZADO'],' units ago',  bcolors.ENDC

connection, address = serversocket.accept()
mensagem = json.loads(connection.recv(256))
buf = mensagem.split(' ')
ERASE_AFTER = int(buf[0])
VIZINHOS = int(buf[1])
print bcolors.HEADER, 'TEMPO ATE EXCLUIR NO FALHO = ', ERASE_AFTER, bcolors.ENDC
print bcolors.HEADER, 'QUANTIDADE DE NOS NA REDE  = ', VIZINHOS, bcolors.ENDC

HEARTBEAT_TABLE.append({'ID':ID,'ENDERECO':OFFSET+ID, 'HEARTBEAT':0, 'TIMESTAMP_LOCAL':TIME, 'ATUALIZADO':0}) 
showTable()

while True:
    connection, address = serversocket.accept()
    buf = connection.recv(256)
    if len(buf) > 0:
        decodedMessage = json.loads(buf)
        if decodedMessage == 'NEXT' and ONLINE:
            TIME += QTDD_POR_UNIDADE_TEMPO
            atualizeMyHeartbeat()
            gossip()
            atualizeLastUpdateTime()
            verifyFailNodes()
            showTable()
        elif decodedMessage == 'TOGGLE':
            ONLINE = not ONLINE
            if ONLINE:
                HEARTBEAT_TABLE.append({'ID':ID,'ENDERECO':OFFSET+ID, 'HEARTBEAT':0, 'TIMESTAMP_LOCAL':TIME, 'ATUALIZADO':0}) 
                print bcolors.OKGREEN,'NODE ' + str(ID) + " ONLINE", bcolors.ENDC
            else:
                TIME = 0
                HEARTBEAT_TABLE = []
                print bcolors.FAIL, 'NODE ' + str(ID) + " OFFLINE", bcolors.ENDC
        elif ONLINE:
            receiveGossip(decodedMessage)