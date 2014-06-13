from http_server import HttpServer
from http_server import InvalidHttpCodeError
from http_server import NotGETRequestError
from http_server import NotHTTP1_1Error
from http_server import BadRequestError
from http_server import ResourceNotFound
from http_server import ForbiddenError
import threading


class HttpServerMT(HttpServer):

    def __init__(self, ip=b'127.0.0.1', port=50000, backlog=5):
        super(HttpServerMT, self).__init__(ip, port, backlog)
        self._bufferSize = 4096

    def _handle_connection(self, connection):
        #print "_handle_connection thread started"
        request = []
        while True:
            buffer_ = connection.recv(self._bufferSize)
            request.append(buffer_)
            if len(buffer_) < self._bufferSize:
                break
        print "\nRequest: {}".format("".join(request))
        body = b""
        headers = {}
        try:
            body, content_type = self._process_request("".join(request))
        except ForbiddenError:
            code = 403
        except NotGETRequestError:
            code = 405
        except BadRequestError:
            code = 400
        except NotHTTP1_1Error:
            code = 505
        except ResourceNotFound:
            code = 404
        else:
            code = 200
            headers = {
                'Content-Type': content_type,
                'Content-Length': len(body)}
        try:
            if not body:
                body = self._statusCodes[code]
            response = self._gen_response(code, body, headers)
            print response
        except InvalidHttpCodeError:
            response = self._gen_response(
                500,
                self._statusCodes[code],
                headers)
            # Is this the right HTTP code?
        finally:
            connection.sendall(response)
            connection.close()
        #print "_handle_connection thread ended"

    def start_listening(self):
        u"""Accept a request from a client and return appropriate response."""
        while True:
            connection, addr = self._socket.accept()
            t = threading.Thread(
                target=self._handle_connection,
                args=(connection,))
            t.daemon = True
            t.start()

if __name__ == "__main__":
    s = HttpServerMT()
    try:
        s.open_socket()
        s.start_listening()
    except KeyboardInterrupt:
        s.close_socket()
    finally:
        if s is not None and s._socket is not None:
            s.close_socket()
