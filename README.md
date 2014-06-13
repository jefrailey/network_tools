network_tools
=============

A repository for network tools in Python

###Descriptions
####HttpServer
This simple HTTP Server is single threaded and only accepts basic GET requests. It only supports protocol HTTP/1.1. If the HTTP method or protocol are any different then an appropriate HTTP Response will be return to the client. Malformed requests will also result in an appropriate response to the client.

The server is a class. To use it, instantiate the server class, call open_socket() to bind the server's socket, and then call start_listening() to wait for a client connection. start_listening() will block the UI thread.

_parse_request() is responsible for parsing a given request. If certain failure cases are encountered, it uses exceptions to communicate to its parent context.

_gen_response() is used to actually construct a response that can be send to a client based on a given HTTP response code.

start_listening() contains the actual server loop that waits for client connections, accumulates a request, and ultimately sends responses to clients.

####HttpServerMT
This simple HTTP Server uses threads to handle multiple, simultaneous requests. The server still blocks the main thread, but spawns seperate threads for each client connection. The functionality and operation are otherwise unchanged.

###Inspirations:
* [A Simple Echo Server](http://ilab.cs.byu.edu/python/socket/echoserver.html)
* [Understanding the HTTP Protocol](http://codefellows.github.io/python-dev-accelerator/lectures/day07/http.html)
* [Socket Communications](http://cewing.github.io/training.codefellows/assignments/day06/socket_exercise.html)
* [Section 6 Response - Hypertext Transfer Protocol -- HTTP/1.1](http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html)
* [Is there any way to kill a Thread in Python? - Stack Overflow](http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python)

####Travis says:
[![Travis](https://travis-ci.org/jefrailey/network_tools.svg?branch=master)](https://travis-ci.org/jefrailey/network_tools.svg?branch=master)
