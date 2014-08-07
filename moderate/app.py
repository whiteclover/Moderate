
import logging
logger = logging.getLogger(__name__)

class App(object):

    def __init__(self):
        self.jobs = {}
        self.bootstrap()

    def set_server(self, server):
        self.server = server

    def bootstrap(self):
        pass

    def add_job(self, name, callback):
        self.jobs[name] = callback
        print self.jobs[name]

    def __call__(self, name, args, kw=None):
        job = self.jobs.get(name)
        try:
            if not job:
                logger.warnning('Unknow job: Job<name: %s, args: %s, kw: %s>', name, args, kw)
                return
            if kw:
                job(*args, **kw)
            else:
                job(*args)
        except APPError as e:
            if isinstance(e, ReQueue):
                self.server.queue.put(name, *args, **kw)
            logger.error('Handle job failed Job<name: %s, args: %s, kw: %s>', name, args, kw)
        except Exception as e:
            logger.error('Unhandle error:%s', e)


class APPError(Exception):
    pass

class ReQueue(APPError):
    pass

class UnknowJob(APPError):
    pass