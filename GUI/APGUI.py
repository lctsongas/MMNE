from Tkinter import *

                    # 1 meter = 2 
PX2M = 0.5          # Pixels to meters scalar
M2PX = 1/PX2M       # Meters to pixels scalar

def meters2pixels(coordsInMeters):
        return (int(coordsInMeters[0]*M2PX), int(coordsInMeters[1]*M2PX))

def pixels2meters(coordsInPixels):
        return (float(coordsInPixels[0])*PX2M, float(coordsInPixels[1])*PX2M)
    

class AP:
    RADIUS = 5          # Circle radius
    apColor = 'red'
    
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
                                                tags=(self.TAG,))
        
        self.apText = self.canvas.create_text(self.drawXPos-(2*self.RADIUS),
                                              self.drawYPos-(3*self.RADIUS),
                                              text = self.TAG,
                                              anchor = 'nw')


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
                                              anchor = 'nw')
        
    def getIP(self):
        return self.IP

    def getMAC(self):
        return self.macAddr


class GW(AP):
    
    LENGTH = 5
    gwColor = 'green'
    


    def draw(self):
        self.gwRect = self.canvas.create_rectangle(self.drawXPos-self.LENGTH,
                                                   self.drawYPos-self.LENGTH,
                                                   self.drawXPos+self.LENGTH,
                                                   self.drawYPos+self.LENGTH,
                                                   fill=self.gwColor)
                                                   
        
        
        

    
        
        
        
                                                
