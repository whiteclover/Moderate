
import zmq

from moderate.queue.base import BaseQueue

context = zmq.Context(1)

class ZmqQueue(BaseQueue):

    def __init__(self, host='127.0.0.1', port=5555, push=True, pull=True):
        self.push = push
        self.pull = pull
        self.proto = 'tcp'
        self.host = host
        self.port = port
        if push:
            self.init_push_socket()
        if pull:
            self.init_pull_socket()

    def init_push_socket(self, ):
        self.push_socket = context.socket(zmq.PUSH)
        url = self.proto + '://*:' + str(self.port) 
        self.push_socket.bind(url)

    def init_pull_socket(self):

        self.pull_socket = context.socket(zmq.PULL)
        url = self.proto + '://' + self.host + ':' + str(self.port) 
        self.pull_socket.connect(url)

    def put(self, name, *args, **kw):
        msg = self.pack(name, args, kw)
        self._put(msg)

    def _put(self, msg):
        self.push_socket.send(msg)

    def get(self):
        return self._get()

    def _get(self):
        return self.unpack(self.pull_socket.recv())

    def close(self):
        if self.pull:
            self.pull_socket.close()
        if self.push:
            self.push_socket.close()