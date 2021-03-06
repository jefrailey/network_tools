# -*- coding: utf-8 -*-
from http_server_mt import HttpServerMT as HttpServer
from http_server_mt import (
    NotGETRequestError,
    NotHTTP1_1Error,
    BadRequestError,
    ResourceNotFound,
    ForbiddenError)
import socket
import pytest
import os
import threading
import Queue
import time


_status_codes = {
    200: b'OK',
    301: b'Moved Permanently',
    304: b'Not Modified',
    400: b'Bad Request',
    403: b'Forbidden',
    404: b'Not Found',
    405: b'Method Not Allowed',
    500: b'Internal Server Error',
    505: b'HTTP version not supported'}


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, target, args):
        super(StoppableThread, self).__init__(target=target, args=args)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


@pytest.fixture(scope="session")
def setup_test_resources(request):
    path = os.getcwd() + "/root/testdir/"
    if not os.path.exists(path):
        os.makedirs(path)
    filename = b"testfile1"
    with open(os.path.join(path, filename), 'wb') as temp_file:
        temp_file.write("")
    filename = b"testfile2"
    with open(os.path.join(path, filename), 'wb') as temp_file:
        temp_file.write("")
    if not os.path.exists(path + "/testsubdirectory"):
        os.makedirs(path + "/testsubdirectory")

    def teardown():
        path = os.getcwd() + "/root/testdir/"
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)
    request.addfinalizer(teardown)


def test_200_ok():
    s = HttpServer()
    assert s._gen_response(200) == "HTTP/1.1 200 OK\r\n"


def test_200_ok_byte():
    s = HttpServer()
    assert isinstance(s._gen_response(200), bytes)


def test_socket_is_socket():
    s = HttpServer()
    s.open_socket()
    assert isinstance(s._socket, socket.socket)


def test_open_socket():
    s = HttpServer()
    s.open_socket()
    assert s._socket.getsockname() == ('127.0.0.1', 50000)


def test_close_socket():
    s = HttpServer()
    s.open_socket()
    s.close_socket()
    assert s._socket is None


def test_parse_one(setup_test_resources):
    testdir = bytes(os.getcwd()) + b'/root/' + b'/testdir/'
    s = HttpServer()
    dirs = []
    files = []
    for item in os.listdir(testdir):
        if os.path.isdir(testdir + item):
            dirs.append("{}/".format(item))
        else:
            files.append(item)
    dirs.sort()
    files.sort()
    resources = dirs + files
    expected_body = []
    expected_body.append("<p>Directory Listing for /testdir/</p><ul>")
    for res in resources:
        expected_body.append('<li><a href="{}">{}</a></li>'.format(res, res))
    expected_body.append("</ul>")
    body, content_type = s._process_request("GET /testdir/ HTTP/1.1")
    assert body == "".join(expected_body)
    assert content_type == "text/html"


def test_parse_2():
    s = HttpServer()
    with pytest.raises(NotGETRequestError):
        s._process_request("POST /uri/ HTTP/1.1")


def test_parse_3():
    s = HttpServer()
    with pytest.raises(NotHTTP1_1Error):
        s._process_request("GET /uri/ HTTP/1.0")


def test_parse_4():
    s = HttpServer()
    with pytest.raises(BadRequestError):
        s._process_request("GET/uri/HTTP/1.0")


def test_gen_response_1():
    s = HttpServer()
    assert s._gen_response(301) == 'HTTP/1.1 301 Moved Permanently\r\n'


def test_retrieve_resource_1():
    test_string = u"Here is text with some unicode in it: ÄÄÄÄÄÄÄÄÄÄ"
    s = HttpServer()
    body, content_type = s._retrieve_resource(b"test.html")
    assert content_type == b"text/html"
    assert body.decode('utf-8') == test_string


def test_retrieve_resources_2():
    s = HttpServer()
    with pytest.raises(ResourceNotFound):
        s._retrieve_resource(b"afilethatdoesntexist.123")


def test_retrieve_resources_3():
    s = HttpServer()
    body, content_type = s._retrieve_resource(b"")
    assert content_type == b"text/html"


def test_forbidden_error1():
    s = HttpServer()
    with pytest.raises(ForbiddenError):
        body, content_type = s._retrieve_resource(b"../../etc/password/")


def test_gen_response2():
    u"""Assert that 403 error response is generated."""
    s = HttpServer()
    assert s._gen_response(403) == b'HTTP/1.1 403 Forbidden\r\n'


def test_gen_all_codes():
    s = HttpServer()
    for code, msg in _status_codes.items():
        assert s._gen_response(code) == b'HTTP/1.1 {} {}\r\n'.format(code, msg)


def test_http_server_mt():
    test_ip = b'127.0.0.1'
    test_port = 50000
    q = Queue.Queue()  # used to know when clients have all gotten responses
    t = StoppableThread(
        target=run_http_server,
        args=(test_ip, test_port))
    t.daemon = True
    t.start()
    time.sleep(0.5)  # let server spin up

    num_clients = 10
    for i in range(num_clients):
        t = StoppableThread(
            target=run_http_testclient,
            args=(q, i, test_ip, test_port))
        t.daemon = True
        t.start()

    num_responses_received = -1
    while num_responses_received < num_clients:
        num_responses_received = q.qsize()

    while not q.empty():
        assert "Here is text with some unicode in it: ÄÄÄÄÄÄÄÄÄÄ" in q.get()
    t.stop()
    while not t.stopped():
        pass


def run_http_server(test_ip, test_port):
    server = HttpServer(test_ip, test_port)
    server.open_socket()
    server.start_listening()


def run_http_testclient(q, i, test_ip, test_port):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
        socket.IPPROTO_IP)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print "Client {}: Connecting...".format(i)
    client_socket.connect((test_ip, test_port))
    print "Client {}: Sendall...".format(i)
    test_request = b"GET /test.html HTTP/1.1"
    client_socket.sendall(test_request)
    response = ["Client {} Response:\r\n"]
    while True:
        response.append(client_socket.recv(4096))
        if len(response[-1]) < 4096:
            break
    print "Client {}: Got Response. Shutting down client...".format(i)
    client_socket.shutdown(socket.SHUT_WR)
    q.put("".join(response))
