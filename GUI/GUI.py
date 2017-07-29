from Tkinter import *
import time
apnum = 0


class NET_GUI:
    def __init__(self,master):
    
        self.master = master
        self.master.title(' NETWORK GRAPHICAL INTERFACE')
        #set canvas dimensions
        self.w=500
        self.h=500
        #find canvas origin
        self.xOrigin=self.w/2
        self.yOrigin=self.h/2
        #create canvas
        self.dsply = Canvas(self.master, width=self.w, height=self.h,bg='white')
        self.dsply.pack(side=BOTTOM)
        #create x,y coordinants(moves in pixles)
        self.dsply.create_line(self.w/2,0,self.w/2,self.h,dash=(1,1))
        self.dsply.create_line(0,self.h/2,self.w,self.h/2,dash=(1,1))
        #create GatWay rectangul with half width gw
        gw = 10
        self.dsply.create_rectangle(self.xOrigin-gw,self.yOrigin-gw,self.xOrigin+gw,self.yOrigin+gw,fill='green')

        self.status = Frame(self.master)
        
    
    def Add_APS(self,TAG):
        self.r=5
        ap=self.dsply.create_oval(self.xOrigin-self.r,self.yOrigin-self.r,self.xOrigin+self.r,self.yOrigin+self.r,fill='red',tags=(TAG))
        
        return(ap)
    def Move_APS(self,TAG,xfinal,yfinal):
        x0Current,y0Current,x1Current,y1Current = self.dsply.coords(TAG)
        xcur = x0Current + self.r
        ycur = y0Current + self.r
        xtoorigin = xcur - self.xOrigin
        ytoorigin = ycur - self.yOrigin
        self.dsply.move(TAG,xtoorigin,ytoorigin)
        xtogo = 0 + xfinal
        ytogo = 0 - yfinal
        self.dsply.move(TAG,xtogo,ytogo)
        

root = Tk()
root.config(height = 1000, width = 1000)
gui = NET_GUI(root)
gui.Add_APS('ap0')
gui.Move_APS('ap0',10,10)
gui.Add_APS('ap1')
gui.Move_APS('ap1',30,-20)


root.mainloop()
