from Tkinter import *
from PIL import Image, ImageTk
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
    APDict = {} #AP_TAG : AP OBJECT
    APIPMap = {} # AP_IP : (AP_TAG, AP_MAP)
    
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
        self.network.startArping()
        #self.status = Frame(self.master)
        

    def createWidgets(self):
        """Build GUI"""
        self.canvas = Canvas(self.master,
                             width=self.WIDTH,
                             height=self.HEIGHT,
                             bg='white')
        self.canvas.pack(expand=YES)
        self.image = ImageTk.PhotoImage(file='background.png')
        self.canvas.create_image(0,0, anchor = NW, image = self.image)
        
        #create x,y coordinants(moves in pixles)
        self.canvas.create_line(self.WIDTH/2,0,
                                self.WIDTH/2,
                                self.HEIGHT,
                                fill='white',
                                dash=(5,1))
        self.canvas.create_line(0,self.HEIGHT/2,
                                self.WIDTH,
                                self.HEIGHT/2,
                                fill='white',
                                dash=(5,1))

        #create GatWay rectangul with half width gw
        self.gatewayMAC = '20:0c:c8:01:c5:37'
        self.gatewayIP = '10.0.0.1'
        self.gatewayTAG = 'GW'
        gateway = APGUI.GW(self.canvas,
                           self.xOrigin,
                           self.yOrigin+10,
                           self.gatewayMAC,
                           self.gatewayIP,
                           self.gatewayTAG)
        
        self.APIPMap[self.gatewayIP] = (self.gatewayTAG, self.gatewayMAC)
        self.APDict[self.gatewayTAG] = gateway
        #Create Select Button
        self.selectBtn = Button(self.master,
                                text='1: Refresh',
                                command=self.refresh)
        self.selectBtn.pack(side=LEFT)
        #Create Dropdown List
        self.apTags = StringVar(self.master)
        self.apTags.trace('w', self.getInfo)
        self.apDropdownMenu = OptionMenu(self.master, self.apTags, ())
        self.apDropdownMenu.config(width=5)
        self.apDropdownMenu.pack(side=LEFT)
        #Create Test information display
        self.apTextInfo = self.canvas.create_text(5,5,anchor='nw')
        #Create AP Options Dropdown List
        self.apOptions = StringVar(self.master)
        self.apOptionMenu = OptionMenu(self.master,
                                       self.apOptions,
                                       'AP Move to:',
                                       'Where are you?',
                                       'Stop Moving',
                                       'ALL STOP')
        self.apOptionMenu.config(width=12)
        self.apOptionMenu.pack(side=LEFT)
        #Create x and y textbox
        self.apXCoord = StringVar(self.master)
        self.apYCoord = StringVar(self.master)
        self.apXCoord.set('0')
        self.apYCoord.set('0')
        self.apXText = Entry(self.master, textvariable=self.apXCoord)
        self.apYText = Entry(self.master, textvariable=self.apYCoord)
        self.apXText.config(width=5)
        self.apYText.config(width=5)
        self.apXText.pack(side=LEFT)
        self.apYText.pack(side=LEFT)
        #Create Send Button
        self.sendButton = Button(self.master,
                                 text='2: Send!',
                                 command=self.sendCommand)
        self.sendButton.pack(side=LEFT)
	
    def monitorAP(self):
        """Listen to network for MeshPackets"""
        #print 'network called'
        arpTable = self.network.getArpDict()
        if arpTable == None:
            return
        #print 'network returned'
        for arpIP in arpTable:
            #print 'for loop iteration'
            if not arpIP in self.APIPMap:
                splitIP = arpIP.split('.')
                apTAG = 'AP' + str(splitIP[3])
                print 'New Node: ' + apTAG
                print arpIP + '->' + arpTable[arpIP]
                self.addAP(apTAG, arpTable[arpIP], arpIP)
                self.TOTAL+=1
        #print 'monitorAP done'
    
    def addAP(self,TAG, mac, ip):
        newAP = APGUI.AP(self.canvas, self.xOrigin, self.yOrigin, mac, ip, TAG)
        self.APIPMap[ip] = (TAG, mac)
        self.APDict[TAG] = newAP

    
    def moveAP(self,ip,xfinal,yfinal):
        if not ip in self.APIPMap:
            print 'No AP found with: ' + ip
            return
        TAG = self.APIPMap[ip][0]
        #print 'TAG: ' + TAG
        movingAP = self.APDict[TAG]
        #print 'APIP: ' + movingAP.getIP()
        oldCoords  = movingAP.getCenter()
        newCoords = (xfinal, yfinal)
        movingAP.move(newCoords)
        #print TAG + ': ' + str(oldCoords) + '->' + str(newCoords) 

    def test_loop(self):
        if(self.newTime == self.oldTime) :
            self.addAP('ap1', '00:01:01:01:01:01', '10.01.1.1')
            self.TOTAL+=1
            self.addAP('ap2', '00:02:02:02:02:02', '10.02.2.2')
            self.TOTAL+=1
        self.newTime = time.time()
        elapsed = self.newTime - self.oldTime
        self.master.after(32, self.test_loop)
        
    def gui_loop(self):
        self.monitorAP()
        #self.newTime = time.time()
        #elapsed = self.newTime - self.oldTime
        #if elapsed > 5:
            #self.monitorAP()
            #self.oldTime = time.time()
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
                apTag = self.APIPMap[packet.srcAddress()]
                self.APDict[apTag[0]].setOK()
                self.APDict[apTag[0]].update()
            elif flag == Mesh.FG_LOWPWR:
                # Low Power: A2S, losing client signal, AP running low pwr subroutine
                print 'LOW POWER CLIENT RECEIVED FROM ' + packet.srcAddress()
            elif flag == Mesh.FG_MOVING:
                apTag = self.APIPMap[packet.srcAddress()]
                self.APDict[apTag[0]].setOK()
                self.APDict[apTag[0]].update()
                print 'CLIENT MOVING ' + packet.srcAddress()
                # Moving   : A2S, also sends current x,y and dest x,y
                data = packet.getPayload()
                #print 'DATA: ' + data
                dataList = data.split(',')
                newX = int(round(float(dataList[0])))
                newY = int(round(float(dataList[1])))
                #print 'X,Y: ' + str(newX) + ', ' + str(newY)
                #print data + '-> (' + str(newX) + ', ' + str(newY) + ')'
                self.moveAP(packet.srcAddress(), newX, newY)
            else:
                # Packet type not supported
                print self.network.printPacket(packet)

        #for apmac in self.APDict:
            
        self.master.after(32, self.gui_loop) 

    def refresh(self):
        menu = self.apDropdownMenu['menu']
        menu.delete(0,'end')
        for apTag in self.APDict.keys():
            menu.add_command(label=apTag,
                             command = lambda value=apTag: self.apTags.set(value))
            self.apTags.set('')

    def sendCommand(self):
        apName = self.apTags.get()                
        if apName == '':
            return
        ap = self.APDict[apName]
        xCoord = self.apXCoord.get()
        yCoord = self.apYCoord.get()
        option = self.apOptions.get()
        ip = ap.getIP()
        if option == 'AP Move to:':
            if xCoord == '' or yCoord == '':
                return
            try:
                x = int(xCoord)
                y = int(yCoord)
                if apName == self.gatewayTAG:
                    self.moveAP(self.gatewayIP, x, y)
                else:
                    self.network.sendMoveTo(ip,x,y)
            except ValueError:
                return 
        elif option == 'Where are you?':
            self.network.pollCoords(ip)
        elif option == 'Stop Moving':
            self.network.stopAPNow(ip)
        elif option == 'ALL STOP':
            self.network.stopAPAll()
        else:
            return

    def getInfo(self, *args):
        tag = self.apTags.get()
        if tag == '':
            return
        self.canvas.delete(self.apTextInfo)
        self.apTextBg = self.canvas.create_rectangle(3,3,150,50, fill='white')
        self.apTextInfo = self.canvas.create_text(5,5,anchor='nw')
        for otherApTags in self.APDict.keys():
            if otherApTags == tag:
                continue
            self.APDict[otherApTags].setBad()
            self.APDict[otherApTags].draw()
        apObject = self.APDict[tag]
        apObject.setSelected()
        apObject.update()
        apInfoString = tag + ' Info:\n'
        apInfoString+= 'IP  ' + apObject.getIP() + '\n'
        apInfoString+= 'MAC ' + apObject.getMAC()
        self.canvas.itemconfig(self.apTextInfo, text=apInfoString)
        

    def exitGUI(self):
        """Start teardown"""
        self.master.destroy()
        

    def handler(self):
        """Handler for closing GUI"""
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitGUI()
        else:
            return;

