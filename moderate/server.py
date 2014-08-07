import threading
import Queue

class Server(object):

    def __init__(self, app, queue, min=5, max=50, shine=5):
        app.set_server(self)
        self.app = app
        self.queue = queue
        self.pool = ThreadPool(self, min, max, shine)

    def start(self):
        t = threading.Thread(target = self.claim)
        t.daemon = True
        t.start()
        self.pool.start()

    def claim(self):
        while True:
            job = self.queue.get()
            self.pool.put(job)


class WorkerThread(threading.Thread):

    def __init__(self, server):
        self.ready = False
        self.server = server
        threading.Thread.__init__(self)

    def start(self):
        try:
            self.ready = True
            while self.ready:
                job = self.server.pool.get()
                self.server.app(**job)
        except (KeyboardInterrupt, SystemExit), exc:
            self.server.interrupt = exc


class ThreadPool(object):

    def __init__(self, server, min, max=-1, shine=5):
        self.server = server
        self.min = min
        self.max = max
        self._shine = shine

        self._threads = []
        self._queue = Queue.Queue()

    get = lambda self: self._queue.get()

    def start(self):
        for i in range(self.min):
            self._threads.append(WorkerThread(self.server))
        for worker in self._threads:
            worker.start()

        for worker in self._threads:
            while not worker.ready:
                time.sleep(.1)

    def _get_idle(self):
        return len(t for t in self._threads if t.conn is None)
    idle = property(_get_idle, doc=_get_idle.__doc__)

    def put(self, obj):
        self._queue.put(obj)
        self.shine()

    def grow(self, amount):
        for i in range(amount):
            if self.max > 0 and len(self._threads) >= self.max:
                break
            worker = WorkerThread(self.server)
            self._threads.append(worker)
            worker.start()

    def shine(self):
        if (len(self._threads)  - self._queue.qsize()) >= 20:
            self.grow(5)
        elif (len(self._threads)  - self._queue.qsize()) <= -20:
            self.shrink(5)

    def shrink(self, amount):
        for t in self._threads:
            if not t.isAlive():
                self._threads.remove(t)
                amount -= 1
        if amount > 0:
            for i in range(min(amount, len(self._threads) - self.min)):
                self._queue.put(SHUTDOWN)
