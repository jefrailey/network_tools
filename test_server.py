import socket

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
    socket.IPPROTO_IP
    )


def test_server_exits():
    client_socket.connect(('127.0.0.1', 50000))
    client_socket.sendall("test string")
    q = ""
    while True:
        print "hung"
        q = client_socket.recv(32)
        if q:
            # client_socket.sendall(q)
            break
    assert q == "test string"
    client_socket.close()
