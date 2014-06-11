from http_server import (
    HttpServer,
    NotGETRequestError,
    NotHTTP1_1Error,
    BadRequestError
    )
import socket
import pytest


def test_200_ok():
    s = HttpServer()
    assert s.gen_response(200) == "HTTP/1.1 200 OK"


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


def test_parse_one():
    s = HttpServer()
    assert s.parse_request("GET /uri/ HTTP/1.1") == "/uri/"


def test_parse_2():
    s = HttpServer()
    with pytest.raises(NotGETRequestError):
        s.parse_request("POST /uri/ HTTP/1.1")


def test_parse_3():
    s = HttpServer()
    with pytest.raises(NotHTTP1_1Error):
        s.parse_request("GET /uri/ HTTP/1.0")


def test_parse_4():
    s = HttpServer()
    with pytest.raises(BadRequestError):
        s.parse_request("GET/uri/HTTP/1.0")


def test_gen_response_1():
    s = HttpServer()
    assert s.gen_response(301) == 'HTTP/1.1 301 Moved Permanently'
