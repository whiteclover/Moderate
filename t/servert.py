
from moderate.server import Server
from moderate.app import App
from moderate import queue
import unittest
import threading
import logging

import time 



class ServerTest(unittest.TestCase):

    def test_run(self):
        app = App()
        app.add_job('say',  say)

        def put():
            q = queue.queue('zmq', pull=False)
            time.sleep(1)
            for i in range(200):
                q.put('say', 'test  say app')
        def say(word):
            print word
        q = queue.queue('zmq', push=False)
        s = Server(app, q)

        st = threading.Thread(target=s.start)
        wt = threading.Thread(target=put)
        wt.start()
        st.start()


if __name__ == '__main__':
    unittest.main()