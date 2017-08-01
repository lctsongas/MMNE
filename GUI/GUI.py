import sys
sys.path.append("/home/pi/MMNE/Network/NetworkUtils")
from MeshNetworkUtil import *
from Tkinter import *
import tkMessageBox
import time
import APGUI
apnum = 0


class NET_GUI:

    #Priority and packet flags defined below
    PQ_DEFAULT = 10         #Default priority in queue
    PQ_EMERGCY = 1          #Emergency packets get highest priority
    
                            # A2S = Flag sent from AP to Server
                            # S2A = Flag sent from Server to AP
                            # A2A = Flag sent from AP to AP
    FG_NONE      = 0        # Undefined: A2S/S2A/A2A, Flag for general purpose packets
    FG_OKAY      = 1        # OK       : A2S, ready and waiting
    FG_LOWPWR    = 2        # Low Power: A2S, losing client signal, AP running low pwr subroutine
    FG_MOVETO    = 3        # Move to  : S2A, x,y to go to
    FG_MOVING    = 4        # Moving   : A2S, also sends current x,y and dest x,y
    FG_WHEREUAT  = 5        # Poll x,y : S2A, ask AP for his current location
    FG_TOOFAR    = 7        # AP far   : S2A, Stops AP so it doesn't go out of range
    FG_ASKHELP   = 8        # Ask help : A2A & A2S, Asks other nodes for help extending coverage
    FG_YOUSTOP   = 99       # Stop move: S2A, Halts single robot from moving
    FG_ALLSTOP   = 100      # Stop move: S2A, Halts all robots form moving
    
    INTERVAL = 2
    TOTAL = 0
    APDict = {}
    
    def __init__(self,master, winWidth, winHeight):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        #set canvas dimensions
        self.WIDTH=int(winWidth)
        self.HEIGHT=int(winHeight)
        #find canvas origin
        self.xOrigin=self.WIDTH/2
        self.yOrigin=self.HEIGHT/2
        #create canvas
        self.createWidgets()
        self.oldTime = time.time()
        self.newTime = time.time() + 2
        self.network = MeshNetworkUtil(False) # Set to false on release
        self.network.startListening()

        self.status = Frame(self.master)
        

    def createWidgets(self):
	"""Build GUI"""
	self.canvas = Canvas(self.master,
                            width=self.WIDTH,
                            height=self.HEIGHT,
                            bg='white')
        
        self.canvas.pack(side=BOTTOM)
        #create x,y coordinants(moves in pixles)
        self.canvas.create_line(self.WIDTH/2,0,
                                     self.WIDTH/2,
                                     self.HEIGHT,
                                     dash=(1,1))
        self.canvas.create_line(0,self.HEIGHT/2,
                                     self.WIDTH,
                                     self.HEIGHT/2,
                                     dash=(1,1))

        #create GatWay rectangul with half width gw
        gw = 10
        self.canvas.create_rectangle(self.xOrigin-gw,
                                    self.yOrigin-gw,
                                    self.xOrigin+gw,
                                    self.yOrigin+gw,
                                    fill='green')
	
    def monitorAP(self):
        """Listen to network for MeshPackets"""
        while True:
            x = 0
            try:
                x = 1
                #TO DO
            except:
                return
    
    

    def gui_loop(self):
        #Do crap here
        #self.newTime = time.time()
        #elapsedTime = self.newTime - self.oldTime
        #print 'Time: ' + str(elapsedTime)
        #if elapsedTime >= self.INTERVAL:
        #    self.oldTime = time.time()
        #    apStr = 'AP' + str(self.TOTAL)
        #    mac = '00:00:' + str(self.TOTAL)
        #    ip = '10.0.0.' + str(self.TOTAL)
        #    newAP = APGUI.AP(self.canvas, apStr, self.xOrigin, self.yOrigin, mac, ip)
        #    self.APDict[mac] = newAP
        #for keys,value in self.APDict.iteritems():
        #    x,y = value.getCenter()
        #    newCoords = (x+1, y+1)
        #    value.move(newCoords)
        #    print keys + '@:' + str(self.APDict[keys].getCenter())
        packet = self.network.getPacket()
        if not packet == None:
            print "GUI Flags: " + str(packet.flags())
            print "GUI Data : " + packet.getPayload()
            srcIP = packet.srcAddress()
            print "GUI srcIP: " + srcIP
            self.network.sendMoveTo(srcIP, 2, 0)
        self.master.after(32, self.gui_loop) 

    def doStuff(self):
        print 'button pressed!'

    def exitGUI(self):
        """Start teardown"""
        self.master.destroy()
        

    def handler(self):
        """Handler for closing GUI"""
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitGUI()
        else:
            return;

