import socket
import threading
from ClientHandler import *


class Server:
    def __init__(self, port=7676):
        print('Server started')
        self.logged_clients = []
        self._cid = 0
        self.serv_sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM,
                                  proto=0)
        self.serv_sock.bind(('', port))
        self.serv_sock.listen()

        while True:
            client_sock = self.accept_client_conn()
            t = threading.Thread(target=self.new_handler,
                                 args=(self, client_sock, self._cid,))
            t.start()
            self._cid += 1

    def accept_client_conn(self):
        """ Waiting connection from user """

        print('Waiting for a client')
        client_sock, client_addr = self.serv_sock.accept()
        print(f'Client #{self._cid} connected {client_addr[0]}:{client_addr[1]}')
        return client_sock

    def new_handler(self, server, client_sock, cid):
        """ Creates own handler for each connection """
        self.handler = ClientHandler(server, client_sock, cid)

if __name__ == '__main__':
    server = Server(port=7676)
