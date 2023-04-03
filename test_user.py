import unittest
import json
from datetime import datetime
from  user import User

class TestUser(unittest.TestCase):

    def setUp(self):
        '''Set up test data'''

        self.user = User()
        self.test_user = {'username': 'test_user', 'password': 'test_password'}
        self.test_admin = {'username': 'test_admin', 'password': 'test_password', 'is_admin': True}

        # Create test data file
        with open('user_info.json', 'w', encoding='utf-8') as file:
            json.dump({}, file)


    def test_register(self):
        '''Test user registration'''

        # Register new user
        self.user.register(self.test_user['username'], self.test_user['password'])

        # Check that user was added to file
        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        self.assertIn(self.test_user['username'], user_data.keys())


    def test_login(self):
        '''Test user login'''

        # Register new user
        self.user.register(self.test_user['username'], self.test_user['password'])

        # Try to login with correct password
        result = self.user.login(self.test_user['username'], self.test_user['password'])
        self.assertEqual(result, json.dumps(f'User {self.test_user["username"]} successfully login', indent=1))

        # Try to login with wrong password
        result = self.user.login(self.test_user['username'], 'wrong_password')
        self.assertEqual(result, json.dumps(f'Wrong password for {self.test_user["username"]} account', indent=1))

        # Try to login with non-existing user
        result = self.user.login('non_existing_user', 'password')
        self.assertEqual(result, json.dumps("User doesn't exist", indent=1))


    def test_users_list(self):
        '''Test users list'''

        # Check that list is not accessible without login
        result = self.user.users_list()
        self.assertEqual(result, json.dumps("You have to be logged to check list of users", indent=1))

        # Register new user and login
        self.user.register(self.test_user['username'], self.test_user['password'])
        self.user.login(self.test_user['username'], self.test_user['password'])

        # Check that list is accessible after login
        result = self.user.users_list()
        self.assertEqual(result, json.dumps([self.test_user['username']], indent=1))


if __name__ == '__main__':
    unittest.main()
