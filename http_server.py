class HttpServer(object):
    """docstring for HttpServer"""
    def __init__(self, ip=u'127.0.0.1', port=50000, backlog=5):
        self.ip = ip
        self.port = port
        self.backlog = backlog
        self.socket = None