from Tkinter import *
import tkMessageBox
import time
import APGUI
apnum = 0


class NET_GUI:
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
        print 'Init done'

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
    
    def addAP(self,TAG):
        self.r=5
        ap=self.dsply.create_oval(self.xOrigin-self.r,
                                  self.yOrigin-self.r,
                                  self.xOrigin+self.r,
                                  self.yOrigin+self.r,
                                  fill='red',tags=(TAG))
        return(ap)

    
    def moveAP(self,TAG,xfinal,yfinal):
        x0Current,y0Current,x1Current,y1Current = self.dsply.coords(TAG)
        xcur = x0Current + self.r
        ycur = y0Current + self.r
        xtoorigin = xcur - self.xOrigin
        ytoorigin = ycur - self.yOrigin
        self.dsply.move(TAG,xtoorigin,ytoorigin)
        xtogo = 0 + xfinal
        ytogo = 0 - yfinal
        self.dsply.move(TAG,xtogo,ytogo)

    def gui_loop(self):
        #Do crap here
        self.newTime = time.time()
        elapsedTime = self.newTime - self.oldTime
        print 'Time: ' + str(elapsedTime)
        if elapsedTime >= self.INTERVAL:
            self.oldTime = time.time()
            apStr = 'AP' + str(self.TOTAL)
            mac = '00:00:' + str(self.TOTAL)
            ip = '10.0.0.' + str(self.TOTAL)
            newAP = APGUI.AP(self.canvas, apStr, self.xOrigin, self.yOrigin, mac, ip)
            self.APDict[mac] = newAP
        else:
            for keys,value in self.APDict.iteritems():
                x,y = value.getCenter()
                newCoords = (x+1, y+1)
                value.move(newCoords)
                print keys + '@:' + str(self.APDict[keys].getCenter())
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

