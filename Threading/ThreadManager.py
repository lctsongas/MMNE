from WorkerThread import WorkerThread
import Queue, threading
from time import sleep
from MyThreads import *

#You will need an instance of this object in your top
#program otherwise it will make everything harder
#YOU SHOULD NOT MODIFY THIS ONLY THE THREAD OBJECTS
class ThreadManager:
    
    TOTAL_THREADS = 0  #total number of threads
    threadPool = {}    #dictionary that holds all threads
                       #(each is referenced via strings)
    queuePool = {}     #dictionary that hold all queues between
                       #threads (each referenced with same string as threadPool
    linkPool = {}      #maintains the list of linked thread in/out queues
    #give ThreadManager AT LEAST 1 thread to run to initialize it
    def __init__(self,threads, queues): 
        """Initializer for ThreadManager"""
        for threadName in threads:
            #Add data in/out queues to queue dict
            self.queuePool[threadName] = queues[threadName]
            #call __init__ function of the thread class
            #and add thread to thread dict
            self.threadPool[threadName] = threads[threadName](self.queuePool[threadName][0],self.queuePool[threadName][1])
            #Increment number of threads
            self.TOTAL_THREADS+=1

    def printThreads(self):
        """print threadMgr contents"""
        print 'Total Threads: ' + str(self.TOTAL_THREADS)
        for threadStr in self.threadPool:
            print threadStr + ' thread is a ' +  str(self.threadPool[threadStr]) + ' thread class.'
            
    def getThreads(self):
        return self.TOTAL_THREADS

    def stopThread(self,name):
        """Stop thread with mathcing name"""
        try:
            self.threadPool[name].join()
            self.TOTAL_THREADS-=1
            return True
        except KeyError:
            return False
        
    def startThread(self,name):
        """Start thread with matching name"""
        try:
            self.threadPool[name].start()
            return True
        except KeyError:
            return False

    def startAll(self):
        """Start all threads if running"""
        for threadName in self.threadPool:
            thread = self.threadPool[threadName]
            try:
                thread.start()
            except RuntimeError:
                continue

    def stopAll(self):
        """Stop all threads if running"""
        for threadName in self.threadPool:
            thread = self.threadPool[threadName]
            if thread.running.isSet():
                thread.join()
                self.TOTAL_THREADS-=1

                
    def addThread(threads, queues):
        """Add a 1 or more threads to the pool"""
        for threadName in threads:
            self.queuePool[threadName] = queues[threadName]
            self.threadPool[threadName] = threads[threadName](self.queuePool[threadName][0],self.queuePool[threadName][1])
            self.TOTAL_THREADS+=1

    def getFrom(self,name):
        """Get the data from the queue of a thread"""
        try:
            #the second queue at index 1 will be the output
            dataOut = self.queuePool[name][1].get(True, 1.0)
            #print 'getFrom: ' + name + ' -> ' + dataOut
            return dataOut
        except Queue.Empty:
            #print 'getFrom: ' + name + ' -> None'
            return None

    def sendTo(self,name, data):
         """Send the data to the queue of a thread"""
         try:
             self.queuePool[name][0].put(data)
             return True
         except:
            return False

    def linkThreads(self,nameOutput, nameInput):
        """Link the output of first thread to output of
            second thread arg"""
        threadOut = self.threadPool[nameOutput]
        threadIn  = self.threadPool[nameInput]
        #create unique name ID
        linkName = nameOutput + ':' + nameInput
        self.linkPool[linkName] = threading.Thread(target=self.autoQueue)
        self.linkPool[linkName].start()

    def autoQueue(self):
        """Queue threading. Use linkThreads"""
        while True:
            for linkName in self.linkPool.keys():
                try:
                    threadNames = linkName.split(':')
                    dataToSend = self.getFrom(threadNames[0])
                    if dataToSend != None:
                        #print str(self.threadPool[threadNames[0]]) + ' sent ' + dataToSend + ' to ' + str(self.threadPool[threadNames[1]])
                        self.sendTo(threadNames[1], dataToSend)
                    #print str(self.threadPool[threadNames[0]]) + ' sent nothing to ' + str(self.threadPool[threadNames[1]])
                except Exception as e:
                    #print str(self.threadPool[threadNames[0]]) + ' error to ' + str(self.threadPool[threadNames[1]])
                    continue


        
        
        
