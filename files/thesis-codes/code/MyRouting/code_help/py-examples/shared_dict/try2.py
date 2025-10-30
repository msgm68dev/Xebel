#!/usr/bin/python3
from collections import defaultdict
from threading import Lock
from time import sleep as sleep
import multiprocessing

Values = defaultdict(float) # create a defaultdict with float as the default value
lock = Lock() # create a lock object
def show_and_increase():
    global Values
    while True:
        value = Values["key"] # get the value
        print("T1: {}".format(value) )
        Values["key"] += 1 # get the value
        sleep(1)
def jump_10():
    global Values
    while True:
        Values["key"] = 0 # get the value
        print("T2")
        sleep(3)

            
  
# In one thread, set a key-value pair
Values["key"] = 15 # set the value
# release the lock automatically

# In another thread, get the value of the same key
# release the lock automatically
processes = []
p = multiprocessing.Process(target=show_and_increase, args=( ))
processes.append(p)
p.start()
p = multiprocessing.Process(target=jump_10, args=( ))
processes.append(p)
p.start()
for p in processes:
    p.join()
