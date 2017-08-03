from Tkinter import *

                    # 1 meter = 10 px 
PX2M = 1.0/10.0         # Pixels to meters scalar
M2PX = 1.0/PX2M       # Meters to pixels scalar

def meters2pixels(coordsInMeters):
        return (int(coordsInMeters[0]*M2PX), int(coordsInMeters[1]*M2PX))

def pixels2meters(coordsInPixels):
        return (float(coordsInPixels[0])*PX2M, float(coordsInPixels[1])*PX2M)
    

class AP:
    RADIUS = 5          # Circle radius
    apSelected = 'yellow'
    apActive = 'green'
    apBad = 'red'
    apColor = apBad
    apOutline = 'white'
    
    def __init__(self,canvas,xOrigin,yOrigin,mac,ip,tag):
        """Init AP to (0,0)"""
        self.canvas = canvas
        self.xPos = 0   # In pixels
        self.yPos = 0   # In pixels
        self.drawXPos = xOrigin
        self.drawYPos = yOrigin
        self.xOrigin = xOrigin
        self.yOrigin = yOrigin
        self.macAddr = mac
        self.IP = ip
        self.TAG = tag
        self.draw()

    def draw(self):
        self.apCircle = self.canvas.create_oval(self.drawXPos-self.RADIUS,
                                                self.drawYPos-self.RADIUS,
                                                self.drawXPos+self.RADIUS,
                                                self.drawYPos+self.RADIUS,
                                                fill=self.apColor,
                                                outline=self.apOutline,
                                                tags=(self.TAG,))
        
        self.apText = self.canvas.create_text(self.drawXPos-(2*self.RADIUS),
                                              self.drawYPos-(3*self.RADIUS),
                                              text = self.TAG,
                                              fill='white',
                                              anchor = 'nw',
                                              tags=(self.TAG,))


    def getCenter(self):
        """Get relative x,y coords"""
        #print 'Xp: ' + str(self.xPos) + ' Yp: ' + str(self.yPos)
        coords = (self.xPos, self.yPos)
        xR, yR = pixels2meters(coords)
        #print 'Xr: ' + str(xR) + ' Yr: ' + str(yR)
        return self.xPos,self.yPos

    def getCenterMeters(self):
        """Get real x,y coords"""
        #print 'Xp: ' + str(self.xPos) + ' Yp: ' + str(self.yPos)
        coords = (self.xPos, self.yPos)
        xR, yR = pixels2meters(coords)
        #print 'Xr: ' + str(xR) + ' Yr: ' + str(yR)
        return xR,yR

    def getdrawCenter(self):
        """Get x,y based on top left corner"""
        return (self.drawXPos,self.drawYPos)

    def move(self, coordsInMeters):
        """update x,y stuff with new coords in meters"""
        print 'AP.Move called: ' + str(coordsInMeters)
        xInPixels,yInPixels = meters2pixels(coordsInMeters)
        yInPixels = -yInPixels # Flip horizontally
        deltaX = xInPixels - self.xPos
        deltaY = yInPixels - self.yPos
        
        self.xPos = self.xPos + deltaX
        self.yPos = self.yPos + deltaY
        
        self.drawXPos = self.drawXPos + deltaX
        self.drawYPos = self.drawYPos + deltaY
        self.canvas.move(self.TAG, deltaX, deltaY)
        self.canvas.delete(self.apText)
        self.apText = self.canvas.create_text(self.drawXPos-(2*self.RADIUS),
                                              self.drawYPos-(3*self.RADIUS),
                                              text = self.TAG,
                                              fill='white',
                                              anchor = 'nw',
                                              tags=(self.TAG,))

    def update(self):
        self.canvas.delete(self.apCircle)
        self.canvas.delete(self.apText)
        self.draw()
        
    def getIP(self):
        return self.IP

    def getMAC(self):
        return self.macAddr

    def setOK(self):
        self.apColor = self.apActive

    def setSelected(self):
        self.apColor = self.apSelected

    def setBad(self):
        self.apColor = self.apBad

class GW(AP):
    
    LENGTH = 5
    gwColor = 'green'
    


    def draw(self):
        self.gwRect = self.canvas.create_rectangle(self.drawXPos-self.LENGTH,
                                                   self.drawYPos-self.LENGTH,
                                                   self.drawXPos+self.LENGTH,
                                                   self.drawYPos+self.LENGTH,
                                                   fill=self.gwColor,
                                                   tags=(self.TAG,))

    def move(self, coordsInMeters):
        """update x,y stuff with new coords in meters"""
        print 'GW.Move called: ' + str(coordsInMeters)
        xInPixels,yInPixels = meters2pixels(coordsInMeters)
        yInPixels = -yInPixels # Flip horizontally
        deltaX = xInPixels - self.xPos
        deltaY = yInPixels - self.yPos
        
        self.xPos = self.xPos + deltaX
        self.yPos = self.yPos + deltaY
        
        self.drawXPos = self.drawXPos + deltaX
        self.drawYPos = self.drawYPos + deltaY
        self.canvas.move(self.TAG, deltaX, deltaY)

    def update(self):
        self.canvas.delete(self.gwRect)
        self.draw()


        
                                                   
        
        
        

    
        
        
        
                                                
