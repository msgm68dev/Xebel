#!/usr/bin/python3
from collections import defaultdict
from threading import RLock
from time import sleep as sleep
import multiprocessing

Values = defaultdict(float) # create a defaultdict with float as the default value
lock = RLock() # create a lock object
def show_and_increase():
    while True:
        with lock: # acquire the lock
            value = Values["key"] # get the value
        print("T1: {}".format(value) )
        with lock: # acquire the lock
            Values["key"] += 1 # get the value
        sleep(1)
def jump_10():
    # with lock: # acquire the lock
    #     value = Values["key"] # get the value
    while True:
        value = 0
        with lock: # acquire the lock
            Values["key"] = value # get the value
        print("T2: {}".format(value) )
        sleep(3)

            
  
# In one thread, set a key-value pair
with lock: # acquire the lock
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
