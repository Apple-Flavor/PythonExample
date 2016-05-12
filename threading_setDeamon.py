import random
import threading
import time

class MyThread(threading.Thread):
    def run(self):
        wait_time = random.randrange(1,10)
        print "{} will wait {}s".format(self.name,wait_time)
        time.sleep(wait_time)
        print "{} finished".format(self.name)

def main():
    print "Start main threading"
    for i in range(5):
        t = MyThread()
        t.setDaemon(True)
        t.start()
    print "End main threading"
main()
