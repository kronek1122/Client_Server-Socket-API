'''Client socket API'''

import socket as s

HOST = '127.0.0.1'
PORT = 65432

client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
client_socket.connect((HOST,PORT))

while True:
    user_command = input('Enter the command! (Type help for command list):  ').encode('utf8')
    client_socket.sendall(user_command)
    data = client_socket.recv(1024).decode('utf8')
    if data == 'server closed':
        print(data)
        break
    else:
        print(data)