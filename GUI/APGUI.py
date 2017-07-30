from Tkinter import *

class AP:
    RADIUS = 5          # Circle radius
    PX2M = 0.5          # Pixels to meters scalar
    M2PX = 1/PX2M       # Meters to pixels scalar
    
    def __init__(self,canvas,tag,xOrigin,yOrigin,mac,ip):
        """Init AP to (0,0)"""
        self.canvas = canvas
        self.name = tag
        self.xPos = 0   # In pixels
        self.yPos = 0   # In pixels
        self.drawXPos = xOrigin
        self.drawYPos = yOrigin
        self.xOrigin = xOrigin
        self.yOrigin = yOrigin
        self.macAddr = mac
        self.IP = ip
        self.draw()

    def draw(self):
        self.apCircle = self.canvas.create_oval(self.drawXPos-self.RADIUS,
                                                self.drawYPos-self.RADIUS,
                                                self.drawXPos+self.RADIUS,
                                                self.drawYPos+self.RADIUS,
                                                fill='red',
                                                tags=(self.macAddr,))


    def getCenter(self):
        """Get relative x,y coords"""
        print 'X: ' + str(self.xPos) + ' Y: ' + str(self.yPos)
        return self.xPos,self.yPos
        

    def getdrawCenter(self):
        """Get x,y based on top left corner"""
        return (self.drawXPos,self.drawYPos)

    def move(self, coordsInMeters):
        """update x,y stuff with new coords in meters"""
        xInPixels,yInPixels = self.meters2pixels(coordsInMeters)
        
        deltaX = xInPixels - self.xPos
        deltaY = yInPixels - self.yPos
        
        self.xPos = self.xPos + deltaX
        self.yPos = self.yPos + deltaY
        
        self.drawXPos = self.drawXPos + deltaX
        self.drawYPos = self.drawYPos + deltaY
        self.canvas.move(self.macAddr, deltaX, deltaY)
        

    def meters2pixels(self, coordsInMeters):
        return (coordsInMeters[0]*self.M2PX, coordsInMeters[1]*self.M2PX)

    def pixels2meters(self, coordsInPixels):
        return (coordsInPixels[0]*self.PX2M, coordsInPixels[1]*self.PX2M)
        
        
        

    
        
        
        
                                                
