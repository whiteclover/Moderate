
import logging
logger = logging.getLogger(__name__)

class App(object):

    def __init__(self):
        self.jobs = dict()
        self.boostrap()

    def set_server(self, server):
        self.server = server

    def bootstrap(self):
        pass

    def add_job(self, name, callback):
        self.jobs[name] = callback

    def __call__(self, name, args, kw):
        try:
            job = self.jobs.get(name)
            if not job:
                logger.warnning('Unknow job: Job<name: %s, args: %s, kw: %s>', name, args, kw)
                return
            job(*arg, **kw)
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