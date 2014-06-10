import socket


class HttpServer(object):
    """docstring for HttpServer"""
    def __init__(self, ip=u'127.0.0.1', port=50000, backlog=5):
        self._ip = ip
        self._port = port
        self._backlog = backlog
        self._socket = None

    def open_socket(self):
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        self._socket.bind((self._ip, self._port))
        self._socket.listen(self._backlog)