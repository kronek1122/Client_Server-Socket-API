import unittest
from unittest.mock import patch
import json
from  user import User


class TestUser(unittest.TestCase):

    def setUp(self):
        '''Set up test data'''

        self.user = User()
        self.test_user_one = {'username': 'test_user', 'password': 'test_password'}
        self.test_user_two = {'username': 'to_user', 'password': 'test_password'}
        self.test_admin = {'username': 'test_admin', 'password': 'test_password', 'is_admin': True}
        self.message = 'Test message'
        self.to_user = 'to_user'


        #Register users
        self.user.register(self.test_user_one['username'],
                           self.test_user_one['password'])
        self.user.register(self.test_user_two['username'],
                           self.test_user_two['password'])
        self.user.register(self.test_admin['username'],
                           self.test_admin['password'],
                           self.test_admin['is_admin'])


    def test_register(self):
        '''Test user registration'''

        # Check that user was added to file
        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        self.assertIn(self.test_user_one['username'], user_data.keys())


    def test_login(self):
        '''Test user login'''

        # Try to login with correct password
        result = self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        self.assertEqual(result, json.dumps(f'User {self.test_user_one["username"]} successfully login',
                                             indent=1))

        # Try to login with wrong password
        result = self.user.login(self.test_user_one['username'], 'wrong_password')
        self.assertEqual(result, json.dumps(f'Wrong password for {self.test_user_one["username"]} account',
                                            indent=1))

        # Try to login with non-existing user
        result = self.user.login('non_existing_user', 'password')
        self.assertEqual(result, json.dumps("User doesn't exist", indent=1))


    def test_users_list(self):
        '''Test users list'''

        # Check that list is not accessible without login
        result = self.user.users_list()
        self.assertEqual(result, json.dumps("You have to be logged to check list of users", indent=1))

        # Login user
        self.user.login(self.test_user_one['username'], self.test_user_one['password'])

        # Check that list is accessible after login
        with patch('builtins.open', create=True) as mocked_file:
            mocked_file.return_value.__enter__.return_value.read.return_value ='{"test_user": {"password": "test_password", "is_admin": false},"to_user": {"password": "test_password", "is_admin": false}, "test_admin": {"password": "test_password", "is_admin": true}}'
            expected_output = json.dumps(["test_user","to_user", "test_admin"],indent=1)
            self.assertEqual(self.user.users_list(), expected_output)


    def test_send_message_with_missing_username(self):
        '''Test send message with missing username'''

        expected_output = json.dumps("User doesn't exist", indent=1)
        self.assertEqual(self.user.send_message('', self.message), expected_output)


    def test_send_message_to_self(self):
        '''Test send message to self'''

        self.user.login(self.test_user_one['username'], self.test_user_one['password'])

        expected_output = json.dumps("You can't send message to yourself", indent=1)
        self.assertEqual(self.user.send_message(self.test_user_one['username'],
                                                self.message), expected_output)


    def test_send_message_with_inactive_user(self):
        '''Test send message to inactive user'''

        expected_output = json.dumps('Command available only for logged users', indent=1)
        self.assertEqual(self.user.send_message(self.test_user_two['username'], self.message),
                        expected_output)


    def test_send_message_with_full_mailbox(self):
        '''Test send message to user with full inbox'''

        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        mailbox = {'unread_messages': {'2023-04-01 12:00:00, test_user': 'Test message 1',
                                       '2023-04-01 12:05:00, test_user': 'Test message 2',
                                       '2023-04-01 12:10:00, test_user': 'Test message 3',
                                       '2023-04-01 12:15:00, test_user': 'Test message 4',
                                       '2023-04-01 12:20:00, test_user': 'Test message 5'},
                    'test_user': {'2023-04-01 12:00:00': 'Test message 1',
                                       '2023-04-01 12:05:00': 'Test message 2',
                                       '2023-04-01 12:10:00': 'Test message 3',
                                       '2023-04-01 12:15:00': 'Test message 4',
                                       '2023-04-01 12:20:00': 'Test message 5'}
                                       }
        with open(f'{self.to_user}.json', 'w', encoding='utf-8') as file:
            json.dump(mailbox, file)
        expected_output = json.dumps(f'Message could not be sent, mailbox user {self.to_user} is full',
                                     indent=1)
        self.assertEqual(self.user.send_message(self.to_user, self.message), expected_output)


    def test_send_message_successfully(self):
        '''Test send message successfully'''

        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        expected_output = json.dumps(f'You successfully send message to user {self.to_user}', indent=1)
        mailbox = {}
        with open(f'{self.to_user}.json', 'w', encoding='utf-8') as file:
            json.dump(mailbox, file)
        self.assertEqual(self.user.send_message(self.to_user, self.message), expected_output)


    def test_check_inbox_success(self):
        '''Test check_inbox successfully'''

        self.user.active_user = 'test_user'
        with patch('builtins.open', create=True) as mocked_file:
            mocked_file.return_value.__enter__.return_value.read.return_value = '{"2023-04-05 10:01:12": "Hello, how are you?"}'
            expected_output = json.dumps({"2023-04-05 10:01:12": "Hello, how are you?"},indent=1)
            self.assertEqual(self.user.check_inbox(['']), expected_output)


    def test_check_inbox_unauthorized_user(self):
        '''Test check inbox by unauthorized user'''

        self.user.active_user = ''
        expected_output = '"First you must log in!"'
        self.assertEqual(self.user.check_inbox([]), expected_output)


    def test_check_inbox_empty(self):
        '''Test check empty inbox'''

        expected_output = '"Your inbox is empty"'
        self.user.active_user = 'test_user'
        self.assertEqual(self.user.check_inbox(['']), expected_output)


    def test_check_inbox_not_admin(self):
        '''Test checking another user's inbox when not being an admin'''

        self.user.active_user = 'test_user'
        expected_output = '"You do not have permission to check another user mail"'
        self.assertEqual(self.user.check_inbox(['inbox','to_user']), expected_output)


    def test_check_inbox_admin_success(self):
        '''Test checking another user's inbox when being an admin'''

        self.user.active_user = "test_admin"

        expected_output = json.dumps({"test_user": {"2023-04-01 12:00:00": "Test message 1",
                                                    "2023-04-01 12:05:00": "Test message 2",
                                                    "2023-04-01 12:10:00": "Test message 3",
                                                    "2023-04-01 12:15:00": "Test message 4",
                                                    "2023-04-01 12:20:00": "Test message 5" 
                                                    }},indent=1)
        self.assertEqual(self.user.check_inbox(['inbox', 'to_user']), expected_output)


    def test_check_unread_messages_logged_out(self):
        '''Test checking unread messages when not logged in'''

        expected_output =  "First you must log in!"
        self.assertEqual(json.loads(self.user.check_unread_messages()), expected_output)


    def test_check_unread_messages_empty_inbox(self):
        '''Test checking empty unread messages inbox'''

        self.user.active_user = "test_user"
        with patch('builtins.open', create=True) as mocked_file:
            mocked_file.return_value.__enter__.return_value.read.return_value = '{}'
            expected_output = "Your unread messages inbox is empty"
            self.assertEqual(json.loads(self.user.check_unread_messages()), expected_output)


    def test_check_unread_messages_existing_unread_messages(self):
        '''Test checking existing unread messages in inbox'''

        self.user.active_user = "test_user"
        with patch('builtins.open', create=True) as mocked_file:
            mocked_file.return_value.__enter__.return_value.read.return_value = '{"unread_messages": {"2023-04-05 09:45:32": "How are you?"}}'
            expected_output = {"2023-04-05 09:45:32": "How are you?"}
            self.assertEqual(json.loads(self.user.check_unread_messages()), expected_output)


    def test_check_unread_messages_file_not_found(self):
        '''Test checking unread messages when user file does not exist'''

        self.user.active_user = "test_user"
        with patch('builtins.open', create=True) as mocked_file:
            mocked_file.side_effect = FileNotFoundError
            expected_output = "Your unread messages inbox is empty"
            self.assertEqual(json.loads(self.user.check_unread_messages()), expected_output)


if __name__ == '__main__':
    unittest.main()
