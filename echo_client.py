# -*- coding: utf-8 -*-
import socket
import sys


class EchoClient(object):
    """A simple echo client that speaks to an echo server"""
    def __init__(self, ip=u'127.0.0.1', port=50000):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)

    def sendMessage(self, msg):
        if not isinstance(msg, str):
            msg = msg.encode('utf-8')
        self.client_socket.connect((self.ip, self.port))
        self.client_socket.sendall(msg)
        self.client_socket.shutdown(socket.SHUT_WR)
        responseMsg = None
        while True:
            responseMsg = self.client_socket.recv(32).decode('utf-8')
            if responseMsg is not None:
                self.client_socket.close()
                break
        self.client_socket.close()
        return responseMsg

if __name__ == '__main__':
    client = EchoClient()
    print client.sendMessage(sys.argv[1])
