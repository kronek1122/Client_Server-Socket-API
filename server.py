'''Server socket API'''

import socket as s
import json
from datetime import datetime

HOST = '127.0.0.1'
PORT = 65432

INFO = 'version: 0.1.0; creation date: 12.03.2023r'
START_TIME = datetime.now()


def available_commands():
    '''Return json file with list of available commands'''

    msg = {
        'uptime': "returns the lifetime of the server",
        'info': "returns the version of the server, the date of its creation",
        'help': "returns a list of available commands",
        'stop': "stops server and client"
    }
    return json.dumps(msg, indent=1)


def uptime():
    '''Return json file with lifetime of the server'''

    return json.dumps(str(datetime.now() - START_TIME))


server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

connection, address = server_socket.accept()

with connection:
    print(f'Connected by {address}')

    while True:
        data = connection.recv(1024).decode('utf8')

        if data == 'uptime':
            connection.send(uptime().encode('utf8'))
        if data == 'info':
            connection.send(INFO.encode('utf8'))
        if data == 'help':
            connection.send(available_commands().encode('utf8'))
        if data == 'stop':
            connection.send(('server closed').encode('utf8'))
            server_socket.close()
            break
