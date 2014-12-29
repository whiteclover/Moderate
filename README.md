Moderate
==========

A Python Distributed Task System 

Feature
----------

1. Multi-threaded task execution (Leader/Follower variant)
2. Take advantage of zmq push/pull pattern 

How to Use
-------------

```python


from moderate import Server
from moderate import App
from moderate import queue
import threading
import logging

import time 

def say(word):
    print word


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

```