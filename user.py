import json
from datetime import datetime

class User:
    '''Represents a user in the system with methods for user registration, login, 
    show all existing users, sending message, check inbox and chech only unread messages.'''

    def __init__(self):
        self.active_user = ''


    def register(self, username, password):
        '''Adding a new user'''

        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        user_data[(username)] = {'password':password, 'is_admin': False}

        with open('user_info.json', 'w', encoding='utf-8') as file:
            json.dump(user_data, file)
        msg = f'User {username} succesfully registered'

        return json.dumps(msg, indent=1)


    def login(self, username, password):
        '''Login user function'''

        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        if username in user_data:
            if user_data[username]['password'] == password:
                msg = f'User {username} successfully login'
                self.active_user = username
            else:
                msg = f'Wrong password for {username} account'
        else:
            msg = "User doesn't exist"

        return json.dumps(msg, indent=1)


    def users_list(self):
        '''return list of existing users'''

        if self.active_user != '':
            list_of_user = []
            with open('user_info.json', 'r', encoding='utf-8') as file:
                user_data = json.load(file)

            for user in user_data:
                list_of_user.append(user)

            return json.dumps(list_of_user, indent=1)

        else:
            return json.dumps("You have to be logged to check list of users", indent=1)


    def send_message(self, username, message):
        '''sending message to other users'''

        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        if username not in user_data:
            return json.dumps("User doesn't exist", indent=1)

        if not self.active_user:
            return json.dumps('Command available only for logged users', indent=1)

        if self.active_user == username:
            return json.dumps("You can't send message to yourself", indent=1)

        try:
            with open(username + '.json', 'r', encoding='utf-8') as file:
                mailbox = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            mailbox = {}

        if 'unread_messages' in mailbox:
            if len(mailbox['unread_messages']) >= 5 and not user_data[self.active_user]['is_admin']:
                return json.dumps(f'Message could not be sent, mailbox user {username} is full', indent=1)

        mailbox['unread_messages'] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' , ' + self.active_user : ' '.join(message)}

        if self.active_user in mailbox:
            mailbox[self.active_user][datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = ' '.join(message)
        else:
            mailbox[self.active_user] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S") : ' '.join(message)}

        with open(username + '.json', 'w', encoding='utf-8') as file:
            json.dump(mailbox, file)

        return json.dumps(f'You successfully send message to user {username}', indent=1)


    def check_inbox(self, query):
        '''return messages in user inbox'''

        with open('user_info.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        if self.active_user != '':
            if len(query)>1 and user_data[self.active_user]['is_admin'] is True:
                try:
                    with open(query[1] + '.json', 'r', encoding='utf-8') as file:
                        user_messages = json.load(file)
                        try:
                            del user_messages['unread_messages']
                        except KeyError:
                            pass
                    return json.dumps(user_messages, indent=1)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    msg = 'Your inbox is empty'

            elif len(query)>1 and user_data[self.active_user]['is_admin'] is False:
                msg = 'Uou do not have permission to check another user mail' 

            else:
                try:
                    with open(self.active_user + '.json', 'r', encoding='utf-8') as file:
                        user_messages = json.load(file)
                        try:
                            del user_messages['unread_messages']
                        except KeyError:
                            pass
                    return json.dumps(user_messages, indent=1)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    msg = 'Your inbox is empty'

        else: msg = 'First you must log in!'
        return json.dumps(msg, indent=1)


    def check_unread_messages(self):
        '''return only unread messages in user inbox'''

        if self.active_user != '':
            try:
                with open(self.active_user + '.json', 'r', encoding='utf-8') as file:
                    user_messages = json.load(file)
                    if 'unread_messages' in user_messages:
                        msg = user_messages['unread_messages']
                        del user_messages['unread_messages']
                        with open(self.active_user + '.json', 'w', encoding='utf-8') as file:
                            json.dump(user_messages, file)
                    else: msg = 'Your unread messages inbox is empty'
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                msg = 'Your unread messages inbox is empty'
        else:
            msg = 'First you must log in!'
        return json.dumps(msg, indent=1)
