import unittest

from moderate import queue
import time

import threading
from thread import get_ident

class ZmqQueueTest(object):

    def setUp(self):
        
        self.q = queue.queue('zmq')
        self.pull_q = queue.queue('zmq', push=False)
        

    def tearDown(self):
        self.q.close()


    def test_in_and_out(self):

        def get(q):
            time.sleep(10)
            while True:
                msg = q.get()
                print 'thread:', get_ident(), 'id: ' + msg['name']
                #self.assertIn('name_', msg['name'])
        #get(self.pull_q)
        def get2(q):
            for i in range(20):
                msg = q.get()
                print 'q2 r thread:', get_ident(), 'id: ' + msg['name']
            q.close()

            q2 = queue.queue('zmq', push=False)
            for i in range(20):
                msg = q2.get()
                print 'q2 thread:', get_ident(), 'id: ' + msg['name']

        threading.Thread(target=get2, args=(self.pull_q,)).start()
        t = threading.Thread(target=get, args=(self.q,))
        t.start()

        #threading.Thread(target=get, args=(self.q,)).start()
        

        for i in range(200):
        
            self.q.put('name_' + str(i) )


if __name__ == '__main__':

    x = ZmqQueueTest()
    x.setUp()
    x.test_in_and_out()