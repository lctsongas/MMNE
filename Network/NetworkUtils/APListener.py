import sys
sys.path.append("/home/pi/MMNE/Threading")
from WorkerThread import WorkerThread
import subprocess
from Queue import Queue
from time import sleep

class APListener(WorkerThread):


    MAX_QUEUE = 2
    
    def __init__(self, dataIn, dataOut):
        """dataIn will never be used"""
        super(APListener, self).__init__()
        self.dataOut = dataOut
        
        
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
        
                iwShell = subprocess.Popen(["iwconfig","wlan1"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                arpOut = arpShell.communicate()[0]
                iwOut = iwShell.communicate()[0]
                sleep(1)

                self.dataOut.put([iwOut,arpOut])
                arpShell.wait()
                iwShell.wait()
            except Exception as e:
                self.dataOut.put(e.message,e.__doc__)



        

        
