from Tkinter import *
import tkMessageBox
import time
import math
import APGUI
import random

sys.path.append("/home/pi/MMNE/Network/NetworkUtils")
import MeshNetworkUtil as Mesh
apnum = 0


class NET_GUI:
    INTERVAL = 2
    TOTAL = 1
    APDict = {}
    APIPMap = {}
    
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
        self.newTime = self.oldTime = time.time()

        self.network = Mesh.MeshNetworkUtil()
        self.network.startListening()
        #self.status = Frame(self.master)
        

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
        self.gatewayMAC = '00:00:00:00:00:00'
        self.gatewayIP = '10.0.0.2'
        self.gateway = APGUI.GW(self.canvas,
                                self.xOrigin,
                                self.yOrigin+10,
                                self.gatewayMAC,
                                self.gatewayIP)
        self.APIPMap[self.gatewayIP] = ('gateway', self.gatewayMAC)
        self.APDict['gateway'] = self.gateway
	
    def monitorAP(self):
        """Listen to network for MeshPackets"""
        arpTable = self.network.getArpAndIP()
        #print 'Monitoring'
        for arpIP in arpTable:
            #for IPKeys in self.APIPMap:
            #print 'Checking'
            if not arpIP in self.APIPMap:
                    
                apTAG = 'AP' + str(self.TOTAL)
                print 'New Node: ' + apTAG
                print arpIP + '->' + arpTable[arpIP]
                self.addAP(apTAG, arpTable[arpIP], arpIP)
                self.TOTAL+=1
    
    def addAP(self,TAG, mac, ip):
        newAP = APGUI.AP(self.canvas, self.xOrigin, self.yOrigin, mac, ip)
        self.APIPMap[ip] = (TAG, mac)
        self.APDict[TAG] = newAP

    
    def moveAP(self,ip,xfinal,yfinal):
        if not ip in self.APIPMap:
            print 'No AP found with: ' + ip
            return
        TAG = self.APIPMap[ip][0]
        movingAP = self.APDict[TAG]
        oldCoords  = movingAP.getCenter()
        newCoords = (xfinal, yfinal)
        movingAP.move(newCoords)
        print TAG + ': ' + str(oldCoords) + '->' + str(newCoords) 

    def test_loop(self):
        if(self.newTime == self.oldTime) :
            self.addAP('aptest' + str(self.TOTAL))
            self.TOTAL+=1
            self.addAP('aptest' + str(self.TOTAL))
            self.TOTAL+=1
        self.newTime = time.time()
        elapsed = self.newTime - self.oldTime
        #Move AP1
        x1 = random.uniform(-1.0,1.0)
        y1 = random.uniform(-1.0,1.0)
        xcurr = self.APDict['aptest1'].getCenterMeters()[0]
        ycurr = self.APDict['aptest1'].getCenterMeters()[1]
        self.moveAP('aptest1', xcurr+x1,ycurr+y1)
        #Move AP2
        x2 = random.uniform(-2.0,2.0)
        y2 = random.uniform(-2.0,2.0)
        xcurr = self.APDict['aptest2'].getCenterMeters()[0]
        ycurr = self.APDict['aptest2'].getCenterMeters()[1]
        self.moveAP('aptest2', xcurr+x2,ycurr+y2)
        #self.oldTime = time.time()
        #time.sleep(1)
        self.master.after(32, self.test_loop)
        
    def gui_loop(self):
        #Do crap here
        
        #    self.oldTime = time.time()
        #    mac = '00:00:' + str(self.TOTAL)
        #    ip = '10.0.0.' + str(self.TOTAL)
        #    newAP = APGUI.AP(self.canvas, self.xOrigin, self.yOrigin, mac, ip)
        #    self.APDict[mac] = newAP
        #for keys,value in self.APDict.iteritems():
        #    x,y = value.getCenter()
        #    newCoords = (x+1, y+1)
        #    value.move(newCoords)
        #    print keys + '@:' + str(self.APDict[keys].getCenter())
        self.monitorAP()
        packet = self.network.getPacket()
        if isinstance(packet, Mesh.MeshPacket):
            #Do processing stuff
            flag = packet.flags()
            if flag == Mesh.FG_NONE:
                # Undefined: A2S/S2A/A2A, Flag for general purpose packets
                print 'UNDEFINED PACKET RECIEVED FROM ' + packet.srcAddress()
            elif flag == Mesh.FG_OKAY:
                # OK       : A2S, ready and waiting
                print 'ALL IS GOUDA RECEIVED FROM ' + packet.srcAddress()
            elif flag == Mesh.FG_LOWPWR:
                # Low Power: A2S, losing client signal, AP running low pwr subroutine
                print 'LOW POWER CLIENT RECEIVED FROM ' + packet.srcAddress()
            elif flag == Mesh.FG_MOVING:
                # Moving   : A2S, also sends current x,y and dest x,y
                data = packet.getPayload()
                dataList = data.split(',')
                newX = int(dataList[0])
                newY = int(dataList[1])
                print data + '-> (' + str(newX) + ', ' + str(newY) + ')'
                self.moveAP(packet.srcAddress(), newX, newY)
            else:
                # Packet type not supported
                print self.network.printPacket(packet)

        #for apmac in self.APDict:
            
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

