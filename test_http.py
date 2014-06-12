# -*- coding: utf-8 -*-
from http_server import (
    HttpServer,
    NotGETRequestError,
    NotHTTP1_1Error,
    BadRequestError,
    ResourceNotFound)
import socket
import pytest
import os


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
        if not os.path.exists(path):
            import shutil.rmtree
            shutil.rmtree(path)
    request.addfinalizer(teardown)


def test_200_ok():
    s = HttpServer()
    assert s.gen_response(200) == "HTTP/1.1 200 OK\r\n\r\n"


def test_200_ok_byte():
    s = HttpServer()
    assert isinstance(s.gen_response(200), bytes)


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
    s = HttpServer()
    body, content_type = s.process_request("GET /testdir/ HTTP/1.1")
    expected_body = []
    expected_body.append("<p>Directory Listing for /testdir/</p><ul>")
    expected_body.append("<li> testfile1 </li>")
    expected_body.append("<li> testfile2 </li>")
    expected_body.append("<li> testsubdirectory </li></ul>")
    #  Consider creating this on the fly with a call to os.listdir()
    assert body == "".join(expected_body)
    assert content_type == "text/html"


def test_parse_2():
    s = HttpServer()
    with pytest.raises(NotGETRequestError):
        s.process_request("POST /uri/ HTTP/1.1")


def test_parse_3():
    s = HttpServer()
    with pytest.raises(NotHTTP1_1Error):
        s.process_request("GET /uri/ HTTP/1.0")


def test_parse_4():
    s = HttpServer()
    with pytest.raises(BadRequestError):
        s.process_request("GET/uri/HTTP/1.0")


def test_gen_response_1():
    s = HttpServer()
    assert s.gen_response(301) == 'HTTP/1.1 301 Moved Permanently\r\n\r\n'


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
