
from moderate import Server
from moderate import App
from moderate import queue
import unittest
import threading
import logging

import time 


def say(word):
    print word

class ServerTest(unittest.TestCase):

    def test_run(self):
        app = App()
        app.add_job('say',  say)

        def put():
            q = queue.queue('zmq', pull=False)
            time.sleep(1)
            for i in range(200):
                q.put('say', 'test  say app')

        q = queue.queue('zmq')
        s = Server(app, q)

        st = threading.Thread(target=s.run)
        wt = threading.Thread(target=put)
        wt.start()
        st.start()


if __name__ == '__main__':
    unittest.main()