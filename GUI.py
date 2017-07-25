import Tkinter
from Tkinter import *
import thread
import time
#import User

class GUI:

    def setupGUI(self):
        global top
        top = Tk()
        global C
        C = Canvas(top, width=600, height=400, bg='white smoke')
        C.place(x=50, y=100)

        global E1
        E1 = Entry(top, bd=5)
        E1.place(x=40, y=10)
        global L1
        L1 = Label(top, text="X:")
        L1.place(x=10, y=10)
        global L2
        L2 = Label(top, text="Y:")
        L2.place(x=250, y=10)
        global E2
        E2 = Entry(top, bd=5)
        E2.place(x=290, y=10)
        global B1
        B1 = Button(top, text="Add User", command=self.addUser)
        B1.place(x=500, y=10)

        global L3
        L3 = Label(top, text="#:")
        L3.place(x=10, y=60)
        global E3
        E3 = Entry(top, bd=5, width=10)
        E3.place(x=40, y=60)
        global L4
        L4 = Label(top, text="X:")
        L4.place(x=150, y=60)
        global E4
        E4 = Entry(top, bd=5, width=10)
        E4.place(x=190, y=60)
        global L5
        L5 = Label(top, text="Y:")
        L5.place(x=300, y=60)
        global E5
        E5 = Entry(top, bd=5, width=10)
        E5.place(x=340, y=60)
        global B2
        B2 = Button(top, text="Move User", command=self.moveUser)
        B2.place(x=500, y=60)

        global apTableLabel
        apTableLabel = Label(top, text="Access Points:")
        apTableLabel.place(x=700, y=100)
        global userTableLabel
        userTableLabel = Label(top, text="Users:")
        userTableLabel.place(x=825, y=100)
        top.mainloop()
        
    def addUser(self):
        self.drawUser(int(E1.get()),int(E2.get()))
        #x = int(E1.get())
        #y = int(E2.get())
        #User.User(xPos=x,yPos=y,contr=controller)
        
    def moveUser(self):
        self.addUser()
        #userNum = int(E3.get())
        #x = int(E4.get())
        #y = int(E5.get())
        #contr.findUser(uNum=userNum,contr.aps).setPosition(xPos=x,yPos=y)

    def drawUser(self, xPos=0, yPos=0):
        x = xPos+300
        y = 200-yPos
        C.create_oval(x-5, y-5, x+5, y+5, fill='red')

    def drawUsers(self, ap=None):
        for curAP in ap.aps:
            if curAP.numAPs>0:
                drawUsers(ap=curAP)
        for u in ap.users:
            self.drawUser(xPos=u.x, yPos=u.y)

    def drawRange(self, xPos=0, yPos=0):
        xPos += 300
        yPos = 200-yPos
        C.create_oval(xPos-50, yPos-50, xPos+50, yPos+50, fill='blue')
        C.create_oval(xPos-40, yPos-40, xPos+40, yPos+40, fill='green')

    def drawRanges(self, ap=None):
        for curAP in ap.aps:
            if curAP.numAPs>0:
                drawRanges(ap=curAP)
        self.drawRange(xPos=ap.x, yPos=ap.y)

    def drawAP(self, xPos=0, yPos=0):
        xPos += 300
        yPos = 200-yPos
        C.create_oval(xPos-5, yPos-5, xPos+5, yPos+5, fill='red')

    def drawAPs(self, ap=None):
        for curAP in ap.aps:
            if curAP.numAPs>0:
                drawAPs(ap=curAP)
        self.drawAP(xPos=ap.x, yPos=ap.y)

    def tableEntry(self, ap=None):
        tempLabel = Label(top, text='AP'+str(ap.apNum)+'- X:'+str(ap.x)+' Y:'+str(ap.y))
        tempLabel.place(x=700, y=120)

    def updateTable(self, ap=None):
        for curAP in ap.aps:
            if curAP.numAPs>0:
                updateTable(ap=curAP)
        self.tableEntry(ap=ap)

    def update(self, ap=None):
        time.sleep(4)
        global controller
        controller = ap
        while True:
            self.drawRanges(ap=ap)
            self.drawAPs(ap=ap)
            self.drawUsers(ap=ap)
            self.updateTable(ap=ap)
            time.sleep(3)

#gui = GUI()
#gui.mainloop()

