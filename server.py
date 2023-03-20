'''Server socket API'''

import socket as s
import json
from datetime import datetime

HOST = '127.0.0.1'
PORT = 65432
INFO = 'version: 0.2.0; creation date: 12.03.2023r'
START_TIME = datetime.now()

data_list = []
active_user = ''
msg = ''


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


def register_user(data_list):
    '''Adding a new user'''

    with open('user_info.json', 'r', encoding='utf-8') as file:
        user_data = json.load(file)
    user_data[data_list[1]] = {'password':data_list[2], 'is_admin': False}

    with open('user_info.json', 'w', encoding='utf-8') as file:
        json.dump(user_data, file)
    msg = f'User {data_list[1]} succesfully registered'

    return json.dumps(msg, indent=1)


def login_user(data_list):
    '''Login user function'''

    global active_user
    with open('user_info.json', 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    user = data_list[1]
    password = data_list[2]

    if user in user_data:
        if user_data[user]['password'] == password:
            msg = f'User {user} successfully log in'
            active_user = user
        else:
            msg = f'Wrong password for {user} account'
    else:
        msg = "User doesn't exist"

    return json.dumps(msg, indent=1)


def users_list():
    '''return list of existing users'''

    global active_user
    if active_user != '':

        list_of_user = []
        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        for user in user_data:
            list_of_user.append(user)

        return json.dumps(list_of_user, indent=1)

    else:
        return json.dumps("You have to be logged to check list of users", indent=1)


def send_message(data_list):
    '''sending message to other users'''

    global active_user
    with open('user_info.json', 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    user = data_list[1]
    if user in user_data:
        if active_user != '':
            if active_user != user:
                try:
                    with open(user + '.json', 'r', encoding='utf-8') as file:
                        mailbox_content = json.load(file)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    mailbox_content = {}

                if 'unread_messages' in mailbox_content:
                    if len(mailbox_content['unread_messages'])<5 or user_data[active_user]['is_admin'] is True :
                        mailbox_content['unread_messages'][datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' , ' + active_user] = ' '.join(data_list[2:])
                        if active_user in mailbox_content:
                            mailbox_content[active_user][datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = ' '.join(data_list[2:])
                        else:  
                            mailbox_content[active_user] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S") : ' '.join(data_list[2:])}

                        with open(user + '.json', 'w', encoding='utf-8') as file:
                            json.dump(mailbox_content,file)
                        msg = f'You successfully send message to user {user}'

                    else:
                        msg = f'Message could not be sent, mailbox user {user} is full'
                else:
                    mailbox_content['unread_messages'] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' , ' + active_user : ' '.join(data_list[2:])}
                    if active_user in mailbox_content:
                        mailbox_content[active_user][datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = ' '.join(data_list[2:])
                    else:  
                        mailbox_content[active_user] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S") : ' '.join(data_list[2:])}

                    with open(user + '.json', 'w', encoding='utf-8') as file:
                        json.dump(mailbox_content,file)
                    msg = f'You successfully send message to user {user}'

            else:
                msg = "You can't send message to yourself"
        else:
            msg = 'Command available only for logged users'
    else:
        msg = "User doesn't exist"

    return json.dumps(msg, indent=1)


def check_inbox(data_list):
    '''return messages in user inbox'''

    global active_user
    with open('user_info.json', 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    if active_user != '':
        if user_data[active_user]['is_admin'] is True:
            try:
                with open(data_list[1] + '.json', 'r', encoding='utf-8') as file:
                    user_messages = json.load(file)
                return json.dumps(user_messages, indent=1)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                msg = 'Your inbox is empty'

        else:
            try:
                with open(active_user + '.json', 'r', encoding='utf-8') as file:
                    user_messages = json.load(file)
                    del user_messages['unread_messages']
                return json.dumps(user_messages, indent=1)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                msg = 'Your inbox is empty'

    else: msg = 'First you must log in!'
    return json.dumps(msg, indent=1)


def check_unread_messages():
    '''return only unread messages in user inbox'''

    global active_user
    if active_user != '':
        try:
            with open(active_user + '.json', 'r', encoding='utf-8') as file:
                user_messages = json.load(file)
                if 'unread_messages' in user_messages:
                    msg = user_messages['unread_messages']
                    del user_messages['unread_messages']
                    with open(active_user + '.json', 'w', encoding='utf-8') as file:
                        json.dump(user_messages, file)
                else: msg = 'Your unread messages inbox is empty'
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            msg = 'Your unread messages inbox is empty'
    else:
        msg = 'First you must log in!'
    return json.dumps(msg, indent=1)


def json_unpacking(data):
    '''Unpacking jsonfile'''
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

        json_unpacking(data)

        if data_list[0] == 'uptime':
            connection.send(uptime().encode('utf8'))

        elif data_list[0] == 'info':
            connection.send(INFO.encode('utf8'))

        elif data_list[0] == 'help':
            connection.send(available_commands().encode('utf8'))

        elif data_list[0] == 'register':
            connection.send(register_user(data_list).encode('utf8'))

        elif data_list[0] == 'login':
            connection.send(login_user(data_list).encode('utf8'))

        elif data_list[0] == 'users':
            connection.send(users_list().encode('utf8'))

        elif data_list[0] == 'send':
            connection.send(send_message(data_list).encode('utf8'))

        elif data_list[0] == 'inbox':
            connection.send(check_inbox(data_list).encode('utf8'))

        elif data_list[0] == 'unread':
            connection.send(check_unread_messages().encode('utf8'))

        elif data_list[0] == 'stop':
            connection.send(('server closed').encode('utf8'))
            server_socket.close()
            break

        else:
            connection.send(('Unknown command').encode('utf8'))
            