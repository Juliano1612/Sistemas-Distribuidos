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
ID = int(sys.argv[1])
HOST = 'localhost'
PORT = OFFSET+int(sys.argv[1])
QTDD_POR_UNIDADE_TEMPO = int(sys.argv[2])
VIZINHOS = 0
ERASE_AFTER = 0
TIME = 0
ONLINE = True

HEARTBEAT_TABLE = []

def sendHeartbeat(id):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientsocket.connect((HOST, PORT))
        clientsocket.send(json.dumps(HEARTBEAT_TABLE))
        print bcolors.OKGREEN, "HEARTBEAT SENDED TO NODE ", id ,bcolors.ENDC
    except:
        print bcolors.FAIL, "ERROR: CONNECTION NOT STABLISHED WITH ", id, bcolors.ENDC

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(10) # become a server socket, maximum 10 connections

'''node = raw_input("Digite o id do no para iniciar o Heartbeating...")
if node != '': #Nao digitou enter... nao e no inicial
    sendHeartbeat(node)'''

connection, address = serversocket.accept()
mensagem = json.loads(connection.recv(256))
buf = mensagem.split(' ')
ERASE_AFTER = int(buf[0])
VIZINHOS = int(buf[1])
print 'TEMPO ATE EXCLUIR NO FALHO = ', ERASE_AFTER
print 'QUANTIDADE DE NOS NA REDE  = ', VIZINHOS

for i in range(0, VIZINHOS):
    HEARTBEAT_TABLE.append({'ENDERECO':OFFSET+i, 'HEARTBEAT':0, 'TIMESTAMP_LOCAL':TIME, 'ATUALIZADO':0})        

print HEARTBEAT_TABLE

while True:
    connection, address = serversocket.accept()
    buf = connection.recv(256)
    if len(buf) > 0:
        print 'RECEBI MENSAGEM ', json.loads(buf) , ' TIME -> ', TIME
        decodedMessage = json.loads(buf)
        if decodedMessage == 'NEXT':
            TIME += QTDD_POR_UNIDADE_TEMPO
            HEARTBEAT_TABLE[ID]['HEARTBEAT'] += 1
            HEARTBEAT_TABLE[ID]['ATUALIZADO'] = 1
            HEARTBEAT_TABLE[ID]['TIMESTAMP_LOCAL'] += TIME
            print HEARTBEAT_TABLE
        elif decodedMessage == 'TOGGLE':
            ONLINE = not ONLINE
        elif ONLINE:
            print 'TO ONLINE'
        '''if decodedMessage['NAME'].startswith('P'):
            publicationReceived(connection, decodedMessage)
        elif decodedMessage['NAME'].startswith('I'):
            messageReceived(connection, decodedMessage)
        elif decodedMessage['NAME'].startswith('A'):
            subscriptionReceived(connection, decodedMessage)'''