import Queue
import time
import math

class AccessPoint:
    apNum = -1
    x = 0
    y = 0
    speed = 25
    isMoving = False
    numUsers = 0
    users = []
    numAPs = 0
    aps = []
    up = None
    actions = Queue.Queue(5)
    locked = True

    def __init__(self, apNum=-1, up1=None, xPos=0, yPos=0):
        self.apNum = apNum
        up = up1
        self.setPosition(xPos,yPos)

    def updateSS(self):
        for u in users:
            u.ss = self.calcSS(u.x,u.y)

    def calcSS(self, xPos, yPos):
        return 50-self.calcDist(xPos, yPos)

    def calcDist(self, xPos, yPos):
        xDist = xPos - self.x
        yDist = yPos - self.y
        dist = math.sqrt(math.pow(xDist,2) + math.pow(xDist,2))
        return dist

    def setPosition(self, xPos=0, yPos=0):
        time.sleep(self.calcDist(xPos, yPos)/self.speed)
        self.x = xPos
        self.y = yPos

    def addUser(self, xPos, yPos):
        u = 0
        while users[u]!=nil & u<6:
            u+=1
        if u<6:
            users[u] = User(xPos, yPos)
            numUsers+=1

    def alertController():
        tempAPnum
        while tempAPnum!=0:
            tempAPnum = tempAPnum.top
        tempAPnum.actions.put(apNum)

    def mainloop(self):
        while True:
            while self.x!=0 & self.y!=0:
                if (numUsers==0 & numAPs==0):
                    setPosition(0,0)
                elif self.actions.empty:
                    for u in users:
                        u.ss = calcSS(u.x, u.y)
                        if u.ss<10:
                            alertController(apNum)                       
                time.sleep(3)
            time.sleep(3)
            if self.actions.empty:
                print "Position: 0,0        APnum: " + str(self.apNum)


#ap = AccessPoint()
#ap.mainloop()

