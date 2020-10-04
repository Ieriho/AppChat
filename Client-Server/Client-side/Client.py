import socket
import json
import datetime
import threading
from Checker import *
from EasyEncrypt import encrypt_json


class Client:

    def __init__(self):
        self.address_to_server = ('localhost', 7676)
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect(self.address_to_server)
        self._lock = threading.Lock()

        self.id_user = None
        self.user_name = None
        self.checker = Checker()

        print('-----------Welcome to the chat!-------------')
        runned = True
        while runned:
            ending = self.run()

            if not ending:
                print('=====You have finished working with chat=====')
                again = input('if you want to start working again, input "/start":')
                if not again == '/start':
                    self.client_sock.close()
                    runned = False
            else:
                print('Whooops, something went wrong')


    def run(self):
        """
        Main method. Accepts commands from the user. Runs other methods
        """

        while True:
            command = input('"/login" for login, '
                        '"/reg" for registration,'
                        '"/escape" for escape: ')
            while True:

                if command == "/login":
                    self.id_user, self.user_name = self.login()

                    recv_thread = threading.Thread(target=self.recv_from_chat)
                    recv_thread.start()
                    self.send_in_chat()
                    return False

                elif command == "/reg":
                    self.id_user, self.user_name = self.registration()
                    command = '/login'

                elif command == '/escape':
                    return self.escape()

                else:
                    print('Unknown command')
                    break

    def login(self):
        while True:
            email = self.checker.check_email()
            password = input('Input password: ')

            # Hereinafter: Encrypt values in the dictionary and dumps to json
            json_dict = {'flag': 'login',
                        'email': email,
                        'password': password}

            json_log = json.dumps(encrypt_json(json_dict))
            self.client_sock.send(bytes(json_log, encoding='UTF-8'))

            received = self.client_sock.recv(1024)
            received = json.loads(received)
            received = encrypt_json(received)

            if bool(received['answer']):
                print('You have entered the chat!')
                print('------------Go Chat--------------')
                id_user = received['id_user']
                user_name = received['name']
                return id_user, user_name
            else:
                print('Not logged in, please, check email and password and try again')
                msg = input('Command or "Enter" -->: ')
                if msg == '/escape':
                    self.client_sock.close()
                    return False

    def registration(self):
        while True:
            email = self.checker.check_email()
            user_name = self.checker.check_name()
            password = self.checker.check_password()
            json_dict = {'flag': 'reg',
                        'email': email,
                        'name': user_name,
                        'password': password}

            json_log = json.dumps(encrypt_json(json_dict))
            self.client_sock.send(bytes(json_log, encoding='UTF-8'))

            received = self.client_sock.recv(1024)

            received = json.loads(received)
            received = encrypt_json(received)
            id_user = received['id_user']

            if bool(received['answer']):
                print('New user registration completed')
                return id_user, user_name
            else:
                print('Such mail or name already exist')

    def send_in_chat(self):
        while True:
            msg = input('-->: ')

            if msg == '/escape':
                self.escape(logged=True)
                break
            now = datetime.datetime.utcnow()
            now = str(now)

            json_dict = {'flag': 'to_chat',
                         'id_user': str(self.id_user),
                         'name': self.user_name,
                         'msg': msg,
                         'datetime': now[:-7]}
            json_msg = json.dumps(encrypt_json(json_dict))
            self.client_sock.send(bytes(json_msg, encoding='UTF-8'))

    def recv_from_chat(self, delimiter=b'}'):
        request = bytearray()
        try:
            while True:
                chunk = self.client_sock.recv(20)
                if not chunk:
                    print('###---Connection with the server is lost---###')
                    return None

                request += chunk
                if delimiter in request:
                    request = json.loads(request)
                    request = encrypt_json(request)
                    with self._lock:
                        msg = f'[{request["from_user"]}]-> {request["msg"]}'
                        print(msg)

        except (ConnectionResetError, ConnectionAbortedError):
            print('###---Connection with the server is lost---###')
            return None

    def escape(self, logged=False):

        if logged:
            now = datetime.datetime.utcnow()
            now = str(now)
            json_dict = {'flag': 'escape',
                        'id_user': str(self.id_user),
                        'name': self.user_name,
                        'datetime': now[:-7]}

            json_esc = json.dumps(encrypt_json(json_dict))
            self.client_sock.send(bytes(json_esc, encoding='UTF-8'))
