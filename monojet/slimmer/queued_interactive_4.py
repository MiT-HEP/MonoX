from Queue import Queue
from threading import Thread 
import time
import os

def do_stuff(q):
  while True:
    #print "Started: ", q.get()
    os.system(q.get())
    q.task_done()
    print "Finished queue",

num_threads = 8
q = Queue()

for line in open('set4.txt', 'r'):
  print "Scheduling:", line
  #q.put(line,True)
  q.put(line)

for i in range(num_threads):
  print q
  worker = Thread(target=do_stuff, args=(q,))
  worker.setDaemon(True)
  worker.start()

q.join() 
