import Queue
import random
import threading

import time

q = Queue.Queue(10)

class Producer(threading.Thread):
    def run(self):
        while True:
            elem = random.randrange(100)
            q.put(elem)
            print "Producer a elem {}, Now size is {}".format(elem,q.qsize())
            time.sleep(random.random())

class Consumer(threading.Thread):
    def run(self):
        while True:
            elem = q.get()
            q.task_done()
            print "Consumer a elem {}, Now size is {}".format(elem,q.qsize())
            time.sleep(random.random())

if __name__=="__main__":
    for i in range(3):
        Producer().start()
    for i in range(3):
        Consumer().start()