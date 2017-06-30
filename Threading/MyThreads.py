from WorkerThread import WorkerThread
import Queue, threading
from time import sleep
#Look at class ThreadA for in-depth comments
#Look at class ThreadB for how to properly make your own
#Look at class ThreadC because you want to
#Ask me any question you have!
#This is the basic framework for creating a threaded module
#Change the class name to the appropritae name you want
#the (WorkerThread) means that this thread class will
#extend the parent class WorkerThread
class ThreadA(WorkerThread):
    #define whatever vars you want for this class
    dataA = 2 # specific var for the ThreadA class

    #You can add parameter after the dataOut
    #if needed, dont remove these params
    def __init__(self,dataIn,dataOut):  
        """Only add stuff to this function"""
        #Always start __init__ like this as this
        #builds the thread stuffs. Add all other
        #initilization stuff after the lines below
        super(ThreadA, self).__init__()
        self.dataIn  = dataIn
        self.dataOut = dataOut
                                        
    #this defines what to return when you call
    #print'{}'.format(<ThreadA object>) or
    #print str(<ThreadA object>)
    def __str__(self):
        """returns class name"""
        return type(self).__name__

    #This will be called when you are ready to start the thread
    #this is where you should put your while loop
    def run(self):
        # As long as we weren't asked to stop,
        # try to take new tasks from the queue
        while not self.stopRequest.isSet():
            #ThreadA sends data when it recieves something
            dataReceived = self.getData()
            if dataReceived != None:
                self.sendData(dataReceived)

    #This is an example of how to use the queues
    #to move data from one thread to another
    def sendData(self,toSend=''):
        #put adds to the queue
        self.dataOut.put(' A sent: ' + str(self.dataA)+ '\n')
        self.dataA+=1

    #this is an example of how to use the queues
    #to get data from another thread to this one
    def getData(self):
        #get tries to retrieve data
        #the true means it is blocking, so no other
        #thread can call get on the queue until this one is done
        #this could be a problem if the get is called and it waits
        #for data but never receives anything. The thread would
        #be stuck at the get command. So to fix this, the 0.05
        #tells the thread to timeout and continue after 0.05 seconds
        #the try loop keeps the exception thrown by a timeout from
        #messing everything up
        try:
            dataOther = self.dataIn.get(True, 1.0)
            #DEBUG uncomment if needed
            #print ' A got: '+ dataOther + '\n' 
            return dataOther #you can return nothing or anyhting else if you want
        except Exception as e:
            print(e)
            return None
    
#Each line will have a comment with a letter.
#The letter tells you if the line is needed for making your own
#threaded class. Each line will one of the following: 
#R = REQUIRED - COPY THIS EXACTLY
#O = OPTIONAL - Not necessary, but makes life easier
#M = MODIFY - This is my example code, replace it with your
#               code to do real work
class ThreadB(WorkerThread):  #O - change the name 'ThreadB' NOTHING ELSE
    dataB = 3.14  #M

    def __init__(self,dataIn,dataOut):  #R
        super(ThreadB, self).__init__()  #R
        self.dataIn  = dataIn  #R
        self.dataOut = dataOut  #R
        #Add all other init stuff below here
        
    def __str__(self):  #O
        """returns class name"""  #O
        return type(self).__name__  #O

    def run(self):  #R
        """Main loop of the thread"""
        #ThreadB only send data, never recieves  #M
        while not self.stopRequest.isSet():  #R
            self.sendData()  #M - this is the infinte loop where
            sleep(1.0)  #M        you do stuff n' things
            

    def sendData(self,toSend=''):  #R
        """Sends processed data to output queue"""
        self.dataOut.put(' B sent: ' + str(self.dataB) + '\n')  #O - Keep the self.dataOut.put(...)
        self.dataB+=2  #M                                          but in the  (...) put your stuff
                                                                #you want to send

    def getData(self):  #R
        """Gets data from input queue"""
        try:  #R
            dataOther = self.dataIn.get(True, 0.05)  #O change left side ONLY
            #DEBUG uncomment if needed  #M
            #print ' B got: '+ dataOther + '\n'   #M - uncomment if stuff is being weird
            return dataOther  #M
        except Queue.Empty:  #R
            return None  #R
    
class ThreadC(WorkerThread):
    dataC = 'mystrData'

    def __init__(self,dataIn,dataOut):
        super(ThreadC, self).__init__()
        self.dataIn  = dataIn
        self.dataOut = dataOut
        #self.stopRequest = threading.Event()
                                        
    def __str__(self):
        """returns class name"""
        return type(self).__name__

    def run(self):
        #ThreadC returns whatever it was sent
        while not self.stopRequest.isSet():
            stuff = self.getData()
            if stuff != None:
                self.sendData(stuff)

    def sendData(self,toSend=''):
        #this function takes one parameter
        self.dataOut.put(' C sent: ' + self.dataC + '\n')

    def getData(self):
        try:
            dataOther = self.dataIn.get(True, 0.05)
            #DEBUG uncomment if needed
            #print ' C got: '+ dataOther + '\n' 
            return dataOther
        except Queue.Empty:
            return None
