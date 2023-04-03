import unittest
import socket
from server import Server
from user import User
import json
from datetime import datetime


class TestServer(unittest.TestCase):

    def setUp(self):
        self.host = '127.0.0.1'
        self.port = 5000
        self.info = 'test server'
        self.server = Server(self.host, self.port, self.info)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.user = User()

    def tearDown(self):
        self.server.server_socket.close()
        self.client_socket.close()

    def test_available_commands(self):
        expected_output = json.dumps({
            'uptime': "returns the lifetime of the server",
            'info': "returns the version of the server, the date of its creation",
            'help': "returns a list of available commands",
            'stop': "stops server and client",
            'register <user name> <password>': 'create new user',
            'login <user name> <password>': 'log in user',
            'users': 'return all user list',
            'send <user name> <massage>': 'send a message to the selected user',
            'inbox': 'check messages in your inbox',
            'unread': 'check only unread messages'
        }, indent=1)

        self.assertEqual(self.server.available_commands(), expected_output)

    def test_uptime(self):
        self.assertIsInstance(json.loads(self.server.uptime()), str)

    def test_json_unpacking(self):
        data = "command info"
        expected_output = data.split(' ')
        self.assertEqual(self.server.json_unpacking(data), expected_output)


if __name__ == '__main__':
    unittest.main()

