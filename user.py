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
                msg = f'User {username} successfully log in'
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

        if username in user_data:
            if self.active_user != '':
                if self.active_user != username:
                    try:
                        with open(username + '.json', 'r', encoding='utf-8') as file:
                            mailbox_content = json.load(file)
                    except (FileNotFoundError, json.decoder.JSONDecodeError):
                        mailbox_content = {}

                    if 'unread_messages' in mailbox_content:
                        if len(mailbox_content['unread_messages'])<5 or user_data[self.active_user]['is_admin'] is True :
                            mailbox_content['unread_messages'][datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' , ' + self.active_user] = ' '.join(message)
                            if self.active_user in mailbox_content:
                                mailbox_content[self.active_user][datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = ' '.join(message)
                            else:
                                mailbox_content[self.active_user] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S") : ' '.join(message)}

                            with open(username + '.json', 'w', encoding='utf-8') as file:
                                json.dump(mailbox_content,file)
                            msg = f'You successfully send message to user {username}'

                        else:
                            msg = f'Message could not be sent, mailbox user {username} is full'
                    else:
                        mailbox_content['unread_messages'] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' , ' + self.active_user : ' '.join(message)}
                        if self.active_user in mailbox_content:
                            mailbox_content[self.active_user][datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = ' '.join(message)
                        else:
                            mailbox_content[self.active_user] = {datetime.now().strftime("%Y-%m-%d %H:%M:%S") : ' '.join(message)}

                        with open(username + '.json', 'w', encoding='utf-8') as file:
                            json.dump(mailbox_content,file)
                        msg = f'You successfully send message to user {username}'

                else:
                    msg = "You can't send message to yourself"
            else:
                msg = 'Command available only for logged users'
        else:
            msg = "User doesn't exist"

        return json.dumps(msg, indent=1)


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
