import sys
sys.path.append("/home/pi/MMNE/Threading")
from WorkerThread import WorkerThread
from ThreadManager import ThreadManager
from APListener import APListener
import subprocess
from Queue import Queue
import time

if __name__ == '__main__':
    queueIn = Queue()
    queueOut = Queue()
    queueTuple = (queueIn, queueOut)
    ListenerID = "AP_Status"
    qDict =  {ListenerID : queueTuple}
    APdict = {ListenerID : APListener}

    threadMgr = ThreadManager(APdict, qDict)

    threadMgr.startThread(ListenerID)

    while True:
        time.sleep(1)
        iwData, arpData = threadMgr.getFrom(ListenerID)
        print 'iw Data: '
        print iwData
        print 'arp Data: '
        print arpData
        
