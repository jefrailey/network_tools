from http_server import HttpServer
import socket


def test_200_ok():
    s = HttpServer()
    assert s.ok() == "HTTP/1.1 200 OK"


def test_200_ok_byte():
    s = HttpServer()
    assert isinstance(s.ok(), bytes)


def test_socket_is_socket():
    s = HttpServer()
    s.open_socket()
    assert isinstance(s._socket, socket)


def test_open_socket():
    s = HttpServer(ip=u'127.0.0.1', port=50000, backlog=5)
    s.open_socket()
    assert s.getsockname() == ('127.0.0.1', 50000)