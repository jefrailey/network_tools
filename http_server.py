class HttpServer(object):
    """docstring for HttpServer"""
    def __init__(self, ip=u'127.0.0.1', port=50000, backlog=5):
        self._ip = ip
        self._port = port
        self._backlog = backlog
        self._socket = None