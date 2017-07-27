from time import time
import math
import sys
import atexit
from Queue import Queue
import threading

from gps import * #imports "everything" from gps
from Adafruit_BNO055 import BNO055
#import our libraries
sys.path.append("/home/pi/MMNE/Movement Control System")
import positioning_calc
import motor_op
from classes import *
sys.path.append("/home/pi/MMNE/Network/NetworkUtils")
from MeshNetworkUtil import *
from APListener import *

imu=IMU_Operations()
motor=Motor_Operations()
alist = myList()
vlist = myList()
dlist = myList()
accel_total_distance = 0

def distance():
    global accel_total_distance
    # dt: the sampling time must be greater than
    # alist,vlist,dlist must be initilized if classes not imported
    alist.append(imu.get_point())
    if len(alist) == 3 :
        vlist.append(imu.tpaz(alist[0],alist[1],0.03))
    if len(vlist) == 3:
        dlist.append(imu.tpaz(vlist[0],vlist[1],0.03))
    if len(dlist) == 3:
        accel_total_distance = accel_total_distance + dlist[0]

def distanceWrapper():
    while True:
        distance()




monitorInQ = Queue() # Not used
monitorOutQ = Queue() # Used to get AP data
connectionMonitor = APListener(monitorInQ,monitorOutQ)
connectionMonitor.start()
commandReceiver = MeshNetworkUtil()
commandReceiver.startListening()


distThread = threading.Thread(target = distanceWrapper,args=())
#loop variable initializations
loops = 0
xcurrent = ycurrent = 0.0
xdestination = ydestination = 0.0

ismoving = False
ismovingforward = False
isturning = False
isdestination = False

distThread.start()
###### Main Event Loop ##########
while True:
    

     ########## MODIFY HERE #######
    #get destination info
    #currently console input (need to set up port)
    #Get potential packet from networkUtil
    packet = commandReceiver.getPacket()
    #check if its a MeshPacket Object
    if isinstance(packet, MeshPacket):

        timestamp = packet.timestamp()
        data = packet.getPayload()
        pflag = packet.flags()
        if pflag == 2: # Bad connection, start moving
            print 'TRYING TO MOVE'
            motor.setspeed(200,195,200,195)
            print 'Speed Set'
            motor.forward()
            print "[M]Distance: " + str(accel_total_distance)
        elif pflag == 1: # Connection okay, stop
            motor.allstop()
            accel_total_distance = 0
            print "[S]Distance: " + str(accel_total_distance)
            
        
            
    ##############################
    #Networking stuff: sends data TO whomever sent the packet
    replyData = "Dist: " + str(accel_total_distance) + " | " + str(connectionMonitor.getLowestSignal())
    address = '10.0.0.2'
    if connectionMonitor.getLowestSignal() >= 70:
        pflag = 2
    else:
        pflag = 1
    commandReceiver.sendPacket(replyData, address, flags=pflag)
    packet = None
    #compensator section
    #currently only full top or slight turn options
    #slight turn is fixed but could add a proportional controller to increase PWM if angle is increased
        




        

