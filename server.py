'''Server socket API'''

import socket as s
import json
from datetime import datetime

HOST = '127.0.0.1'
PORT = 65432
INFO = 'version: 0.2.0; creation date: 12.03.2023r'
START_TIME = datetime.now()

data_list = []

def available_commands():
    '''Return json file with list of available commands'''

    msg = {
        'uptime': "returns the lifetime of the server",
        'info': "returns the version of the server, the date of its creation",
        'help': "returns a list of available commands",
        'stop': "stops server and client",
        'register <user name> <password>' : 'create new user'
    }
    return json.dumps(msg, indent=1)


def uptime():
    '''Return json file with lifetime of the server'''

    return json.dumps(str(datetime.now() - START_TIME))

def sign_up_new_user(data_list):
    '''Adding a new user'''
    user_information = {
        data_list[1]:data_list[2]
    }

    with open('user.json', 'r', encoding='utf8') as file:
        user_data = json.load(file)

    user_data[data_list[1]] = {
        data_list[1]:data_list[2]
    }

    with open('user.json', 'w', encoding='utf8') as file:
        json.dump(user_data, file)

    msg = f'User {data_list[1]} succesfully registered'
    return json.dumps(msg, indent=1)


def json_unpaking(data):
    '''Unpaking jsonfile'''
    global data_list
    data_list = data.split(' ')
    return data_list
        

server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

connection, address = server_socket.accept()

with connection:
    print(f'Connected by {address}')

    while True:
        data = connection.recv(1024).decode('utf8')

        if not data:
            break
        
        json_unpaking(data)
        if data_list[0] == 'uptime':
            connection.send(uptime().encode('utf8'))
        elif data_list[0] == 'info':
            connection.send(INFO.encode('utf8'))
        elif data_list[0] == 'help':
            connection.send(available_commands().encode('utf8'))
        elif data_list[0] == 'register':
            connection.send(sign_up_new_user(data_list).encode('utf8'))
        elif data_list[0] == 'stop':
            connection.send(('server closed').encode('utf8'))
            server_socket.close()
            break
        else:
            connection.send(('nieznana komenda').encode('utf8'))

