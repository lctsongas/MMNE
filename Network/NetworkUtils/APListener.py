import sys
from time import sleep, time
sys.path.append("/home/pi/MMNE/Threading")
from WorkerThread import WorkerThread
import subprocess
from Queue import Queue
from MeshNetworkUtil import *

class APListener(WorkerThread):


    MAX_QUEUE = 2
    SIGNAL_THRESHOLD = -70 #When to send low client signal packet
    TX_FAILED_THRESHHOLD = 1000 #When to send help packet

    
    def __init__(self, dataIn, dataOut):
        """dataIn will never be used"""
        super(APListener, self).__init__()
        self.dataOut = dataOut
        self.clients = {}
        self.txPrev = 0
        self.txCurr = 0
        self.meshUtil = MeshNetworkUtil()
        self.meshUtil.startListening()
        self.time1 = time()
        self.time2 = time() + 5
        
        
        
    def __str__(self):
        """return the name of this class"""
        return type(self).__name__
    
    def run(self):
        """Main loop thread"""
        while True :
            try:
                if self.dataOut.qsize() > self.MAX_QUEUE :
                    #clear queue if too much data
                    self.dataOut.empty()
                    for i in range(self.MAX_QUEUE):
                        self.dataOut.get()
                arpShell = subprocess.Popen(["arp","-a"],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
        
                iwShell = subprocess.Popen(["iw","dev", "wlan1", "station", "dump"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                arpOut = arpShell.communicate()[0]
                iwOut = iwShell.communicate()[0]
                sleep(1)

                self.checkSignals(iwOut)
                self.dataOut.put([iwOut,arpOut])
                arpShell.wait()
                iwShell.wait()
            except Exception as e:
                self.dataOut.put(e.message,e.__doc__)

    def checkSignals(self, iwData):
        """Only called every 5 seconds"""
        self.time2 = time()
        elapsed = self.time2 - self.time1
        if elapsed < 2:
            return
        
        iwList = iwData.split()
        if len(iwList) == 0:
            return
        mac = iwList[0] # Get MAC address (used to ID client)
        signal = int(iwList[27]) # Get client signal strength
        self.clients[mac] = signal
        data = "(" + mac + ", " + str(signal) + ")"
        if signal <= self.SIGNAL_THRESHOLD:
            #Flags == 2 means client is losing signal!
            #print "Client losing signal! " + str(signal) 
            self.meshUtil.sendPacket(data, '10.0.0.2', flags=2)
        elif signal > self.SIGNAL_THRESHOLD:
            #Flags == 1 means everything is okay
            #print "Everything is ok! " + str(signal)
            self.meshUtil.sendPacket(data, '10.0.0.2', flags=1)
        self.time1 = time()
        
            



        

        
