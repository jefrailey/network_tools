import socket
import Queue
import threading
from echo_server import EchoServer
from echo_client import EchoClient
import time


def next_port():
    x = 50000
    while True:
        yield x
        x += 1
        if x > 60000:
            x -= 10000

port_gen = next_port()


def test_for_EchoServer():
    test_ip = '127.0.0.1'
    test_port = port_gen.next()
    q = Queue.Queue()
    t = threading.Thread(
        target=run_EcoServer,
        args=(q, test_ip, test_port))
    t.daemon = True
    t.start()
    time.sleep(1)  # give the echo server a chance to spin up

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
        socket.IPPROTO_IP)

    client_socket.connect((test_ip, test_port))

    test_string = "Hello, EchoServer"
    client_socket.sendall(test_string)
    client_socket.shutdown(socket.SHUT_WR)

    time.sleep(1)  # give the echo server a chance to respond
    response = client_socket.recv(32)  # grab the echo response
    client_socket.close()
    assert response == test_string


def run_EcoServer(q, test_ip, test_port):
    es = EchoServer(test_ip, test_port)
    es.start_listening()
    q.put(True)


def test_for_EchoClient():
    test_ip = '127.0.0.1'
    test_port = port_gen.next()
    test_client = EchoClient(test_ip, test_port)
    q = Queue.Queue()
    t = threading.Thread(
        target=run_test_server,
        args=(q, test_ip, test_port))
    t.daemon = True
    t.start()
    time.sleep(1)  # give the test server a chance to spin up
    test_msg = "Hello, Test Server"
    assert test_client.sendMessage(test_msg) == test_msg


def run_test_server(q, test_ip, test_port):
    test_backlog = 5
    test_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
        socket.IPPROTO_IP)
    test_socket.bind((test_ip, test_port))
    test_socket.listen(test_backlog)

    while True:
        connection, addr = test_socket.accept()
        incomingMsg = connection.recv(32)
        if incomingMsg:
            connection.sendall(incomingMsg)
            connection.close()
            test_socket.close()
            q.put(True)
            break
