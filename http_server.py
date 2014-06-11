import socket


class InvalidHttpCodeError(Exception):
    """docstring for InvalidHttpCodeError"""
    pass


class NotGETRequestError(Exception):
    """docstring for InvalidHttpCodeError"""
    pass


class NotHTTP1_1Error(Exception):
    """docstring for InvalidHttpCodeError"""
    pass


class BadRequestError(Exception):
    """docstring for InvalidHttpCodeError"""
    pass


class HttpServer(object):
    """docstring for HttpServer"""
    def __init__(self, ip=u'127.0.0.1', port=50000, backlog=5):
        self._ip = ip
        self._port = port
        self._backlog = backlog
        self._socket = None
        self._statusCodes = {
            200: 'OK',
            301: 'Moved Permanently',
            304: 'Not Modified',
            400: 'Bad Request',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error',
            505: 'HTTP version not supported'
            }

    def open_socket(self):
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        self._socket.bind((self._ip, self._port))
        self._socket.listen(self._backlog)

    def close_socket(self):
        self._socket.shutdown(socket.SHUT_WR)
        self._socket.close()
        self._socket = None

    def gen_response(self, code, msg=None):
        try:
            if msg is None:
                msg = self._statusCodes[code]
            response = "HTTP/1.1 {} {}".format(code, msg)
            return response
        except KeyError:
            raise InvalidHttpCodeError(
                u'{} is not a valid HTTP code'.format(code))

    def start_listening(self):
        while True:
            request = []
            connection, addr = self._socket.accept()

            while True:
                buffer_ = connection.recv(32)
                if buffer_:
                    request.append(buffer_)
                else:
                    break
            try:
                self.parse_request(" ".join(request))
            except NotGETRequestError:
                connection.sendall(self.gen_response(405))
            except BadRequestError:
                connection.sendall(self.gen_response(400))
            except NotHTTP1_1Error:
                connection.sendall(self.gen_response(505))
            else:
                connection.sendall(self.gen_response(200))
            finally:
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()

    def parse_request(self, request):
        list_ = request.split("\r\n")
        status_line = list_[0].split(" ")
        if len(status_line) != 3:
            raise BadRequestError
        if status_line[0] != "GET":
            raise NotGETRequestError
        if status_line[2] != "HTTP/1.1":
            raise NotHTTP1_1Error
        return status_line[1]


if __name__ == "__main__":
    try:
        s = HttpServer()
        s.open_socket()
        s.start_listening()
    except KeyboardInterrupt:
        s.close_socket()
    finally:
        s.close_socket()
