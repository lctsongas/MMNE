import sys
from Tkinter import Tk
from GUI import *

if __name__ == '__main__':

    root = Tk()
    #WIDTH=int(sys.argv[1])
    #HEIGHT=int(sys.argv[2])
    WIDTH = 500
    HEIGHT = 500
    root.config(height = HEIGHT, width = WIDTH)
    app = NET_GUI(root, WIDTH, HEIGHT)
    #app = GUI(root, sys.argv[1], sys.argv[2])
    app.master.title('NETWORK GRAPHICAL INTERFACE')
    app.master.after(0, app.test_loop) #Run ~30FPS (Wich we could do 60... PCMR)
    root.mainloop()
    
