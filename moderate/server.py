#!/usr/bin/env python
import logging
import time
import threading
import sys
import Queue


try:
    from thread import get_ident
except ImportError:
    from _thread import get_ident
 
LOGGER = logging.getLogger(__name__)
 
_SHUTDOWNTASK = object()

class  Server(object):
 
    # the total time for worker thread to cleanly exit
    SHOTDOWN_TIMEOUT = 5
 
    def __init__(self, app, queue, minthreads=10, maxthreads=50):
        minthreads = minthreads or 1
        minthreads = 1 if minthreads <=0 else minthreads
        maxthreads = maxthreads or 500
        maxthreads = 500 if maxthreads > 500 else maxthreads
        if maxthreads <= minthreads:
            raise TypeError('maxthreads:%d must be greater than minthreads:%d', maxthreads, minthreads)
 
        app.set_server(self)
        self.app = app
        self.queue = queue
        self._idel_tasks = Queue.Queue()
        self.heartbeat = HeartBeat(self._periodic_action)
        self.threadpool = ThreadPool(self, minthreads, maxthreads)

    def _periodic_action(self):
        # clear idle tasks 
        idel_queue_size = self._idel_tasks.qsize()
        for _ in range(idel_queue_size):
            task = self.get()
            self.execute(task, True)
 
    get = lambda self: self._idel_tasks.get()
 
    put = lambda self, task: self._idel_tasks.put(task)
 
    def run(self):
        LOGGER.debug('Starting server ....')
        LOGGER.debug('Master thread : %d', get_ident())
        self.ready = True
        self.threadpool.start()
        self.heartbeat.start()
        
        while self.ready:
            try:
                task = self.claim()
  
                LOGGER.debug('current_task: %s', task)
                self.execute(task)
           
            except Exception as e:
                cls, e, tb = sys.exc_info()
                LOGGER.exception('Unhandled Error %s', e)
 
 
        LOGGER.debug('Stoping server...')
        self.stop()
 
    def stop(self):
        self.heartbeat.stop()
        idel_queue_size = self._idel_tasks.qsize()
        for _ in range(idel_queue_size):
            task = self.get()
            self.queue.put(task)
 
        self.threadpool.stop(self.SHOTDOWN_TIMEOUT)
 
    def execute(self, task, retry=False):
        try:
            done = False
            thread = self.threadpool.pop()
            if thread:
                LOGGER.debug('Execute in thread: %s', thread)
                thread.current_task = task
                thread.resume()
                done = True
            elif not retry:
                self.put(task)
                time.sleep(1)
            else:
                self.queue.put(task)
 
        except (KeyboardInterrupt, SystemExit):
                self.ready = False
                if not done and thread:
                    thread.current_task = _SHUTDOWNTASK
                    thread.resume()
        except Exception as e:
            LOGGER.error('Execute error : %s', e)
            self.queue.put(task)
 
    def claim(self):
        return self.queue.get()

 
class HeartBeat(threading.Thread):
 
    def __init__(self, callback, interval=5):
        self.callback = callback
        self.interval = interval
        self.ready = False
        threading.Thread.__init__(self)
 
    def run(self):
        self.ready = True
        while self.ready:
            time.sleep(self.interval)
            self.callback()
 
    def stop(self):
        self.ready = False
        if self.isAlive():
            self.join()
            
class ThreadPool(object):
 
    def __init__(self, server, min, max):
        self.server = server
        self.min = min
        self.max = max
        self._created = 0
        self._lock = threading.Lock()
        self._in_use_threads = {}
        self._idel_threads = []
 
    def start(self):
        for i in range(self.min):
            with self._lock:
                self._created += 1
                thread = self._new_thread()
                self._idel_threads.append(thread)
 
    def push(self, thread):
        with self._lock:
            if thread in self._in_use_threads:
                del self._in_use_threads[thread]
            self._idel_threads.append(thread)
 
    def pop(self):
        """Non-block pop an idle thread, if not get returns None"""
        thread = None
        self._lock.acquire()
        if self._idel_threads:
            thread = self._idel_threads.pop(0)
            self._in_use_threads[thread] = True
        elif self._created < self.max:
            self._created += 1
            thread = self._new_thread()
            self._in_use_threads[thread] = True
        self._lock.release()
        return thread
 
    def _new_thread(self):
        return WorkerThread(self.server, self)
 
    def stop(self, timeout=5):
        # Must shut down threads here so the code that calls
        # this method can know when all threads are stopped.

        while True:
            time.sleep(1)
            with self._lock:
                if self._in_use_threads or self._idel_threads:
                    LOGGER.info('_idel_threads')
                    while self._idel_threads:
                        worker = self._idel_threads.pop(0)
                        worker.current_task = _SHUTDOWNTASK
                        worker.resume()
                        #worker.event.clear()
                else: 
                    break
 
class WorkerThread(threading.Thread):
 
    def __init__(self, server, pool):
        self.ready = False
        self.event = threading.Event()
        self.server = server
        self.current_task = None
        self.pool = pool
        threading.Thread.__init__(self)
        self.start()
 
    def suspend(self):
        self.event.clear()
        self.event.wait()
 
    def resume(self):
        self.event.set()
 
    def run(self):
        self.ready = True
        LOGGER.debug('Starting thread %d', get_ident())
        while self.ready:
            self.suspend()
            if self.current_task == _SHUTDOWNTASK:
                # shutdown the worker thread
                self.ready = False
                break
            try:
                if self.current_task:
                    self.server.app(self.current_task)
            except Exception as e:
                cls, e, tb = sys.exc_info()
                LOGGER.exception('Unhandled Error in thread:%s %s', get_ident(),e)
                self.server.queue.put(self.current_task)
            finally:
                self.current_task = None
                self.pool.push(self)
        self.event.clear()