import socket


class EchoServer(object):
    """a simple EchoServer"""
    def __init__(self, ip=u'127.0.0.1', port=50000, backlog=5):
        self.ip = ip
        self.port = port
        self.backlog = backlog
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.backlog)

    def start_listening(self):
        while True:
            request = []
            self.connection, self.addr = self.socket.accept()

            while True:
                buffer_ = self.connection.recv(32)
                if buffer_:
                    request.append(buffer_)
                else:
                    break
            self.connection.sendall(" ".join(request))
            self.connection.close()


if __name__ == "__main__":
    server = EchoServer()
    server.start_listening()
