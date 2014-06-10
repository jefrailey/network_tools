from http_server import HttpServer


def test_200_ok():
    s = HttpServer()
    assert s.ok() == "HTTP/1.1 200 OK"


def test_200_ok_byte():
    s = HttpServer()
    assert isinstance(s.ok(), bytes)