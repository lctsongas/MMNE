from ThreadManager import *
import Queue, threading
from time import sleep
#Run this file to start the demo!
#Example run of ThreadManager
if __name__ == '__main__':
    #create unique strings for each thread
    strA = 'dawood'  #BE SURE TO NEVER USE THE SAME STRING TWICE
    strB = 'ryan'    #YOU WILL OVERWRITE A THREAD IF YOU DO THIS
    strC = 'unicorn'
    #create queue tuples (aka list with 2 objects)
    queueList = [ Queue.Queue() for i in xrange(6) ]
    #create a tuple of queue objects
    #for each thread. the first queue
    #for data TO the worker thread,
    #the second is for outputted data from the worker
    dataFlowA = (queueList[0] , queueList[1]) 
    dataFlowB = (queueList[2] , queueList[3]) 
    dataFlowC = (queueList[4] , queueList[5])
    #put queues in dictionary structure for ThreadManager
    dataFlows = {strA : dataFlowA,
                 strB : dataFlowB,
                 strC : dataFlowC
                 }
    #create thread dictionary that maps the unique strings
    #to the thread worker class names
    threadDict = {strA : ThreadA, # Note the 2nd arg is the actual name of the class
                  strB : ThreadB,
                  strC : ThreadC
                  }
    #pass dictionarys to init our ThreadManager
    bossMan = ThreadManager(threadDict, dataFlows)

    #ThreadB OUTPUT queue -> ThreadA INPUT queue
    #ThreadA OUTPUT queue -> ThreadC INPUT queue
    #ThreadC OUTPUT queue -> print in __main__
    #
    #ThreadB INPUT = unused

    #Link the thread queues
    bossMan.linkThreads(strB, strA)
    bossMan.linkThreads(strA, strC)
    #start all threads
    bossMan.startAll()
    
    while True:
        finalData = bossMan.getFrom(strC)
        print 'From C: ' + str(finalData)
