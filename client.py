#CLIENT
import socket
import sys

class client:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        print('HOST: ', host)
        print('PORT: ', port)

    def connect(self):
        print('<<<___Connecting to Computer___>>>')
        print('%%% Creating Socket %%%')
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('!!! Failed to Create Socket !!!')
            sys.exit()
        print('%%% SOCKET CREATED %%%')
        print('%%% Connecting %%%')
        try:
            self.s.connect((self.HOST, self.PORT))
        except socket.error:
            print('!!! Connection Failed !!!')
            sys.exit()
        print('%%% Connection Successful %%%')

    def sendMessage(self, message):
        message = message.encode('utf-8')
        done = False
        while done is False:
            self.s.send(message)
            reply = self.s.recv(1024)
            if reply == 'ok':
               done = True
        #For Testing - Comment out when not needed
	#print('Message: ', message, ': was sent')
