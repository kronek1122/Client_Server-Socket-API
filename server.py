'''Server socket API'''

import socket as s
import json
from datetime import datetime
from user import User

HOST = '127.0.0.1'
PORT = 65432
INFO = 'version: 0.2.0; creation date: 12.03.2023r'
START_TIME = datetime.now()



def available_commands():
    '''Return json file with list of available commands'''

    msg = {
        'uptime': "returns the lifetime of the server",
        'info': "returns the version of the server, the date of its creation",
        'help': "returns a list of available commands",
        'stop': "stops server and client",
        'register <user name> <password>' : 'create new user',
        'login <user name> <password>' : 'log in user',
        'users' : 'return all user list',
        'send <user name> <massage>': 'send a message to the selected user',
        'inbox' : 'check messages in your inbox',
        'unread' : 'check only unread messages'
    }
    return json.dumps(msg, indent=1)


def uptime():
    '''Return json file with lifetime of the server'''

    return json.dumps(str(datetime.now() - START_TIME))


def json_unpacking(data):
    '''Unpacking jsonfile'''
    unpacking_data = []
    unpacking_data = data.split(' ')
    return unpacking_data


server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

connection, address = server_socket.accept()

with connection:
    print(f'Connected by {address}')
    user = User()

    while True:
        query = connection.recv(1024).decode('utf8')

        if not query:
            break

        query_list = json_unpacking(query)

        if query_list[0] == 'uptime':
            connection.send(uptime().encode('utf8'))

        elif query_list[0] == 'info':
            connection.send(INFO.encode('utf8'))

        elif query_list[0] == 'help':
            connection.send(available_commands().encode('utf8'))

        elif query_list[0] == 'register':
            connection.send(user.register(query_list[1],query_list[2]).encode('utf8'))

        elif query_list[0] == 'login':
            connection.send(user.login(query_list[1],query_list[2]).encode('utf8'))

        elif query_list[0] == 'users':
            connection.send(user.users_list().encode('utf8'))

        elif query_list[0] == 'send':
            connection.send(user.send_message(query_list[1],query_list[2:]).encode('utf8'))

        elif query_list[0] == 'inbox':
            connection.send(user.check_inbox(query_list).encode('utf8'))

        elif query_list[0] == 'unread':
            connection.send(user.check_unread_messages().encode('utf8'))

        elif query_list[0] == 'stop':
            connection.send(('server closed').encode('utf8'))
            server_socket.close()
            break

        else:
            connection.send(('Unknown command').encode('utf8'))
            