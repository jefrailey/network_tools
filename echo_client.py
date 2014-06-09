import socket
import sys


class EchoClient(object):
    """A simple echo client that speaks to EcoServer"""

    def __init__(self, ip='127.0.0.1', port=50000):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        self.client_socket.connect((self.ip, self.port))

    def sendMessage(self, msg):
        self.client_socket.sendall(msg)
        self.client_socket.shutdown(socket.SHUT_WR)
        responseMsg = None
        while True:
            responseMsg = self.client_socket.recv(32)
            if responseMsg is not None:
                self.client_socket.close()
                break
        return responseMsg

if __name__ == '__main__':
    client = EchoClient()
    print client.sendMessage(sys.argv[1])
