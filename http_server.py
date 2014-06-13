import socket
import mimetypes
from os import getcwd
from os.path import isdir
from os.path import isfile
from os import listdir


class InvalidHttpCodeError(Exception):
    u"""Create InvalidHttpCodeError Exception"""
    pass


class NotGETRequestError(Exception):
    u"""Create InvalidHttpCodeError Exception"""
    pass


class NotHTTP1_1Error(Exception):
    u"""Create InvalidHttpCodeError Exception"""
    pass


class BadRequestError(Exception):
    u"""Create InvalidHttpCodeError Exception"""
    pass


class ResourceNotFound(Exception):
    u"""An exception that is raised when a resources cannot be located
          for the provided URI"""
    pass


class HttpServer(object):
    u"""Create an HTTP Server with the given endpoint."""
    def __init__(self, ip=b'127.0.0.1', port=50000, backlog=5):
        self._ip = ip
        self._port = port
        self._backlog = backlog
        self._socket = None
        self._root = getcwd() + b"/root/"
        self._statusCodes = {
            200: b'OK',
            301: b'Moved Permanently',
            304: b'Not Modified',
            400: b'Bad Request',
            404: b'Not Found',
            405: b'Method Not Allowed',
            500: b'Internal Server Error',
            505: b'HTTP version not supported'}

    def open_socket(self):
        u"""Open a socket, bind it, and listen."""
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        self._socket.bind((self._ip, self._port))
        self._socket.listen(self._backlog)

    def close_socket(self):
        u"""Shutdown and close the socket."""
        self._socket.close()
        self._socket = None

    def gen_response(self, code, body=None, kwargs={}):
        u"""Generate response for the given HTTP status code."""
        response = []
        try:
            response.append("HTTP/1.1 {} {}\r\n".format(
                code, self._statusCodes[code]))
        except KeyError:
            raise InvalidHttpCodeError(
                u'{} is not a valid HTTP code'.format(code))
        headers = kwargs.keys()
        for header in headers:
                response.append("{}: {}\r\n".format(
                    header,
                    kwargs[header]))
        response.append("\r\n")  # blank line between headers and body
        if body:
            response.append(body)
        return "".join(response)

    def start_listening(self):
        u"""Accept a request from a client and return appropriate response."""
        buffersize = 32
        while True:
            request = []
            connection, addr = self._socket.accept()
            while True:
                buffer_ = connection.recv(buffersize)
                request.append(buffer_)
                if len(buffer_) < buffersize:
                    break
            try:
                body, content_type = self.process_request("".join(request))
            except NotGETRequestError:
                connection.sendall(self.gen_response(405))
            except BadRequestError:
                connection.sendall(self.gen_response(400))
            except NotHTTP1_1Error:
                connection.sendall(self.gen_response(505))
            except ResourceNotFound:
                connection.sendall(self.gen_response(404))
            else:
                response = self.gen_response(
                    200,
                    body,
                    {'Content-Type': content_type,
                     'Content-Length': len(body)})
                connection.sendall(response)
                print response
            finally:
                connection.close()

    def process_request(self, request):
        u"""Split status line into verb, URI, and protocol."""
        list_ = request.split("\r\n")
        status_line = list_[0].split()
        if len(status_line) != 3:
            raise BadRequestError
        if status_line[0] != "GET":
            raise NotGETRequestError
        if status_line[2] != "HTTP/1.1":
            raise NotHTTP1_1Error
        body, content_type = self._retrieve_resource(status_line[1])
        return body, content_type

    def _retrieve_resource(self, uri):
        u"""
        Get the resource specified by the uri if it exist.
        Otherwise, raise a Exception
        """
        p = self._root + uri
        if isdir(p):
            body = ["<p>Directory Listing for "]
            body.append(uri)
            body.append("</p><ul>")
            dirs = []
            files = []
            for res in listdir(p):
                if isdir(p+res):
                    dirs.append(res + b'/')
                else:
                    files.append(res)
            dirs.sort()
            files.sort()
            resources = dirs + files
            for res in resources:
                body.append('<li><a href="{}">{}</a></li>'.format(res, res))
            body.append("</ul>")
            return ("".join(body), "text/html")
        elif isfile(p):
            with open(self._root + uri, 'r') as resource:
                body = resource.read()
                content_type, content_encoding = mimetypes.guess_type(uri)
            return (body, content_type)
        else:
            raise ResourceNotFound


if __name__ == "__main__":
    s = HttpServer()
    try:
        s.open_socket()
        s.start_listening()
    except KeyboardInterrupt:
        s.close_socket()
    finally:
        if s is not None and s._socket is not None:
            s.close_socket()
