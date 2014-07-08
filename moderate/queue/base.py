
from moderate.queue.serialization import pack, unpack


class BaseQueue(object):

    def put(self, name, *args, **kw):
        pass

    def get(self):
        pass

    def pack(self, name, args, kw):
        return pack({'name': name, 'args': args, 'kw': kw})

    def unpack(self, msg):
        return unpack(msg)
