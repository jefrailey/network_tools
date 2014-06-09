import socket

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
    socket.IPPROTO_IP)


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


def test_client():
        test_ip = '127.0.0.1'
        test_port = 50000
        test_backlog = 1
        test_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        test_socket.bind((test_ip, test_port))
        test_socket.listen(test_backlog)

        while True:
            connection, addr = test_socket.accept()
            words = connection.recv(32)
            if words:
                connection.sendall("EchoTestSuccess")
                connection.close()
                assert True
                break
