import json
import threading
import datetime
from SQLighter import *
from EasyEncrypt import encrypt_json


class ClientHandler:
    """
    Process messages and events from users on server.
    Sends data to chat database
    """

    def __init__(self, server, client_sock, cid):
        self.server = server
        self.client_sock = client_sock
        self.cid = cid

        self.sqlighter = SQLighter()
        self._lock = threading.Lock()

        self.serve_client()


    def serve_client(self):
        """ Main method. Controls other functions """

        while True:
            self.request = self.read_request()

            if self.request is None:
                print(f'Client #{self.cid} unexpectedly disconnected')
                self.handle_escape(logged=False)
                break

            elif self.request['flag'] == 'login':
                with self._lock:
                    self.handle_login()

            elif self.request['flag'] == 'reg':
                with self._lock:
                    self.handle_reg()

            elif self.request['flag'] == 'to_chat':
                with self._lock:
                    self.handle_chat_msg()

            elif self.request['flag'] == 'escape':
                with self._lock:
                    self.handle_escape()
                    break

            else:
                print(f'Unknown command from client {self.cid}')


    def read_request(self, delimiter=b'}'):
        """ Reads jsons from users in parts. Returns json-dictionary """

        request = bytearray()
        
        try:
            while True:
                chunk = self.client_sock.recv(10)
                
                if not chunk:
                    return None
                
                request += chunk
                if delimiter in request:
                    request = json.loads(request)
                    request = encrypt_json(request)
                    return request
                
        except ConnectionResetError:
            return None


    def handle_login(self):
        """
        Handles user login: checks email and password from databases,
        sends the message (json) about results
        """

        sqanswer = self.sqlighter.check_uniqueness(self.request, 'email', 'password')
        
        if sqanswer is None:
            serv_ans = False
            self.id_user, self.name = '', ''
        else:
            serv_ans = True
            self.server.logged_clients.append(self.client_sock)
            self.id_user, self.name = sqanswer[0], sqanswer[1]

        json_dict = {'flag': 'to_client',
                    'answer': str(serv_ans),
                    'id_user': str(self.id_user),
                    'name': self.name,
                    'email': self.request['email'],
                    'password': self.request['password']}

        # Hereinafter: Encrypt values in the dictionary and dumps to json
        json_resp = json.dumps(encrypt_json(json_dict))
        self.client_sock.sendall(bytes(json_resp, encoding='UTF-8'))

    def handle_reg(self):
        """
        Handles user registration: checks email and password from databases,
        sends the message (json) about results
        """

        sqanswer = self.sqlighter.check_uniqueness(self.request, 'email', 'name')
        
        if sqanswer is None:
            serv_ans = True
            self.sqlighter.add_new_user((self.request['name'],
                                        self.request['password'],
                                        self.request['email']))
            sqanswer = self.sqlighter.check_uniqueness(self.request, 'email', 'name')
            id_user = sqanswer[0]
        else:
            serv_ans = False
            id_user, name = '', ''

        json_dict = {'flag': 'to_client',
                    'answer': str(serv_ans),
                    'id_user': str(id_user),
                    'name': self.request['name'],
                    'email': self.request['email'],
                    'password': self.request['password']}

        json_resp = json.dumps(encrypt_json(json_dict))
        self.client_sock.sendall(bytes(json_resp, encoding='UTF-8'))

    def handle_chat_msg(self):
        """
        Handles chat messages: sends a message to the database
        and to logged in users
        """

        dtime = datetime.datetime.strptime(self.request["datetime"], '%Y-%m-%d %H:%M:%S')
        self.sqlighter.add_new_message((int(self.request['id_user']),
                                        self.request["msg"],
                                        dtime))
        
        for client_socket in self.server.logged_clients:
            if client_socket == self.client_sock:
                continue

            json_dict = {'flag': 'to_client',
                        'from_user': str(self.request['id_user']),
                        'msg': self.request["msg"]}

            json_resp = json.dumps(encrypt_json(json_dict))
            client_socket.sendall(bytes(json_resp, encoding='UTF-8'))

    def handle_escape(self, msg='left the chat', logged=True):
        """
        Handles escape of user: sends a logout message to the database
        and to logged in users.
        """

        if logged:
            dtime = datetime.datetime.strptime(self.request["datetime"], '%Y-%m-%d %H:%M:%S')
            self.sqlighter.add_new_message((int(self.id_user),
                                            msg,
                                            dtime))

            for client_socket in self.server.logged_clients:
                if client_socket == self.client_sock:
                    self.server.logged_clients.remove(self.client_sock)
                else:
                    json_dict = {'flag': 'to_client',
                                'from_user': self.name,
                                'msg': 'left the chat'}
                    json_resp = json.dumps(encrypt_json(json_dict))
                    client_socket.sendall(bytes(json_resp, encoding='UTF-8'))

