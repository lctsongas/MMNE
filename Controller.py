import thread
import GUI
import time
import Queue
import AccessPoint

class Controller:
    global gui
    gui = GUI.GUI()
    apNum = 0
    x = 0
    y = 0
    speed = 25
    isMoving = False
    numUsers = 0
    users = []
    numAPs = 0
    aps = []
    up = None
    totalAPs = 0
    reserveAPs = []
    alerts = Queue.Queue(10)

    def __init__(self):
        print('Starting Controller')

    def updateSS(self):
        for u in users:
            u.ss = calcSS(u.x,u.y)

    def calcSS(self, xPos, yPos):
        return calcDist(xPos, yPos)

    def calcDist(self, xPos, yPos):
        xDist = xPos - x
        yDist = yPos - y
        dist = Math.sqrt(Math.pow(xDist,2) + Math.pow(xDist,2))
        return dist

    def setPosition(self, xPos=0, yPos=0):
        totalAPs += 1
        if len(aps)<3:
            aps.append(AccessPoint(totalAPs).setPosition(xPos=xPos,yPos=yPos))
            numAPs += 1

    def addUser(self, xPos, yPos):
        u = 0
        while users[u]!=nil & u<6:
            u+=1
        if u<6:
            users[u] = User(xPos, yPos)
            numUsers+=1


    def findAP(self, apNum=-1, aps1=aps):
        for ap in aps1:
            if ap.apNum == apNum:
                return ap
            else:
                if ap.numUsers>0:
                    findAP(apNum, ap)

    def findUser(self, uNum=-1, aps1=aps):
        for ap in aps1:
            for u in ap.users:
                if u.x == xPos & u.y == yPos:
                    return u
            else:
                if ap.numUsers>0:
                    findUser(uNum, ap)

    def mainloop(self):
        global gui
        thread.start_new_thread(gui.update, (self,))
        while True:
            if self.alerts.empty:
                print "No Alerts"
                time.sleep(3)

    def startThreads(self):
        global gui
        print "Creating AccessPoints"
        for x in range(3):
            print str(x+1)
            tempAP = AccessPoint.AccessPoint(apNum=x+1)
            self.reserveAPs.append(tempAP)
            thread.start_new_thread(tempAP.mainloop, ())
        thread.start_new_thread(self.mainloop, ())
        gui.setupGUI()

c = Controller()
c.startThreads()

