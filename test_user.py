import unittest
from unittest.mock import patch, mock_open
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

        # Create test data file
        with open('user_info.json', 'w', encoding='utf-8') as file:
            json.dump({}, file)

        self.user.register(self.test_user_one['username'], self.test_user_one['password'])
        self.user.register(self.test_user_two['username'], self.test_user_two['password'])


    def test_register(self):
        '''Test user registration'''

        # Register new user

        # Check that user was added to file
        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        self.assertIn(self.test_user_one['username'], user_data.keys())


    def test_login(self):
        '''Test user login'''

        # Try to login with correct password
        result = self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        self.assertEqual(result, json.dumps(f'User {self.test_user_one["username"]} successfully login', indent=1))

        # Try to login with wrong password
        result = self.user.login(self.test_user_one['username'], 'wrong_password')
        self.assertEqual(result, json.dumps(f'Wrong password for {self.test_user_one["username"]} account', indent=1))

        # Try to login with non-existing user
        result = self.user.login('non_existing_user', 'password')
        self.assertEqual(result, json.dumps("User doesn't exist", indent=1))


    def test_users_list(self):
        '''Test users list'''

        # Check that list is not accessible without login
        result = self.user.users_list()
        self.assertEqual(result, json.dumps("You have to be logged to check list of users", indent=1))

        # Register new user and login
        self.user.login(self.test_user_one['username'], self.test_user_one['password'])

        self.user.login(self.test_user_two['username'], self.test_user_two['password'])

        # Check that list is accessible after login
        result = self.user.users_list()
        self.assertEqual(result, json.dumps([self.test_user_one['username'],self.test_user_two['username']], indent=1))

    def test_send_message_with_missing_username(self):
        '''Test send message with missing username'''

        expected_output = json.dumps("User doesn't exist", indent=1)
        self.assertEqual(self.user.send_message('', self.message), expected_output)
    
    def test_send_message_to_self(self):
        '''Test send message to self'''

        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        
        expected_output = json.dumps("You can't send message to yourself", indent=1)
        self.assertEqual(self.user.send_message(self.test_user_one['username'], self.message), expected_output)

    def test_send_message_with_inactive_user(self):
        '''Test send message to inactive user'''

        expected_output = json.dumps('Command available only for logged users', indent=1)
        self.assertEqual(self.user.send_message(self.test_user_two['username'], self.message), expected_output)

    def test_send_message_with_full_mailbox(self):
        '''Test send message to user with full inbox'''

        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        mailbox = {'unread_messages': {'2023-04-01 12:00:00': 'Test message 1',
                                       '2023-04-01 12:05:00': 'Test message 2',
                                       '2023-04-01 12:10:00': 'Test message 3',
                                       '2023-04-01 12:15:00': 'Test message 4',
                                       '2023-04-01 12:20:00': 'Test message 5'}}
        with open(f'{self.to_user}.json', 'w', encoding='utf-8') as file:
            json.dump(mailbox, file)
        expected_output = json.dumps(f'Message could not be sent, mailbox user {self.to_user} is full', indent=1)
        self.assertEqual(self.user.send_message(self.to_user, self.message), expected_output)
        
    def test_send_message_successfully(self):
        '''Test send message successfully'''

        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        expected_output = json.dumps(f'You successfully send message to user {self.to_user}', indent=1)

        mailbox = {}
        with open(f'{self.to_user}.json', 'w', encoding='utf-8') as file:
            json.dump(mailbox, file)
        self.assertEqual(self.user.send_message(self.to_user, self.message), expected_output)

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_check_inbox(self, mock_file):
        # test when user is not logged in
        expected = '"First you must log in!"'
        self.assertEqual(self.user.check_inbox([]), expected)

        # test when user inbox is empty
        expected = '"Your inbox is empty"'
        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        self.assertEqual(self.user.check_inbox([]), expected)

        # test when user inbox is not empty
        self.user.login(self.test_user_two['username'], self.test_user_two['password'])
        mailbox = {'test_user_two': {'2023-04-01 12:00:00': 'Test message 1',}}
        with open(f'{self.to_user}.json', 'w', encoding='utf-8') as file:
            json.dump(mailbox, file)

        expected = {'test_user_two': {'2023-04-01 12:00:00': 'Test message 1',}}
        self.assertEqual(self.user.check_inbox([]), expected)

        # test when non-admin user tries to check another user's inbox
        self.user.login(self.test_user_one['username'], self.test_user_one['password'])
        expected = '"You do not have permission to check another user mail"'
        self.assertEqual(self.user.check_inbox(['test_admin']), expected)
        
if __name__ == '__main__':
    unittest.main()
