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


class ForbiddenError(Exception):
    u"""An exception to raise when a URI points to forbidden resource"""
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
            403: b'Forbidden',
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
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._ip, self._port))
        self._socket.listen(self._backlog)

    def close_socket(self):
        u"""Shutdown and close the socket."""
        self._socket.close()
        self._socket = None

    def _gen_response(self, code, body=None, headers={}):
        u"""Generate response for the given HTTP status code."""
        # Would like to use **kwargs instead of headers, but
        # given that some of the headers are dash seperated,
        # like Content-Type, some headers could not be passed
        # in as simple keyword arguments.  Perhaps we should
        # include headers={} for all headers with dashes but
        # still handle any **kwargs as headers.
        response = []
        try:
            response.append("HTTP/1.1 {} {}".format(
                code, self._statusCodes[code]))
        except KeyError:
            raise InvalidHttpCodeError(
                u'{} is not a valid HTTP code'.format(code))
        for header, msg in headers.items():
                response.append("{}: {}".format(
                    header,
                    msg))
        response.append("")  # blank line between headers and body
        if body:
            response.append(body)
        return "\r\n".join(response)

    def start_listening(self):
        u"""Accept a request from a client and return appropriate response."""
        buffersize = 4096
        while True:
            request = []
            connection, addr = self._socket.accept()
            while True:
                buffer_ = connection.recv(buffersize)
                request.append(buffer_)
                if len(buffer_) < buffersize:
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

    def _process_request(self, request):
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
        self._check_uri(uri)
        p = self._root + uri
        if isdir(p):
            body = ["<p>Directory Listing for "]
            body.append(uri)
            body.append("</p><ul>")
            dirs = []
            files = []
            for res in listdir(p):
                if isdir(p + res):
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
            with open(self._root + uri, 'rb') as resource:
                body = resource.read()
                content_type, content_encoding = mimetypes.guess_type(uri)
            return (body, content_type)
        else:
            raise ResourceNotFound

    def _check_uri(self, uri):
        u"""Raise ForbiddenError if URI contains potentially malicous chars."""
        if b".." in uri:
            raise ForbiddenError


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
