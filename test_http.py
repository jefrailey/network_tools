from http_server import HttpServer
import socket


def test_200_ok():
    s = HttpServer()
    assert s.gen_response() == "HTTP/1.1 200 OK"


def test_200_ok_byte():
    s = HttpServer()
    assert isinstance(s.gen_response(), bytes)


def test_socket_is_socket():
    s = HttpServer()
    s.open_socket()
    assert isinstance(s._socket, socket.socket)


def test_open_socket():
    s = HttpServer(ip=u'127.0.0.1', port=50000, backlog=5)
    s.open_socket()
    assert s._socket.getsockname() == ('127.0.0.1', 50000)


def test_close_socket():
    s = HttpServer(ip=u'127.0.0.1', port=50000, backlog=5)
    s.open_socket()
    s.close_socket()
    assert s._socket is None