from Adafruit_BNO055 import BNO055
import positioning_calc
import motor_op
import classes
#from eventloop_Functions import *

import threading
import ADC
from Queue import Queue, LifoQueue
import time
import math
import sys
import atexit

#imu = classes.IMU_Operations()
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
#if not bno.begin():
#    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
motor = classes.Motor_Operations()

isSave = True #save position data to text file
isdestination = False #currently no destination set, reads True if destination set
isEncoderused = True #Is the encoder used to track distance while the robot is moving
ismovingforward = False #Is the robot moving forward? at start of loop it is not moving at all
ismoving = False #The robot is not moving at all (including turning) when the program starts
isclockwise = False #Just an initialization here.  Value is not evaulated until after isdestination = True during runtime
isGPSused = True #Record GPS measurements
isgetGPSorigin = False #no GPS origin stored when program starts.  Origin is saved then set to True
isIMUaccelused = False #collect data with IMU

saveName = 'RobotMovementData.txt' #name of file to save movement data to
min_distance_correction = 3 #stop robot if within 2 (encoderData.py sets distance measurement type: feet, meters)
fullstopturn = 6 #how many degrees away from bearing will a full stop turn be performed. Smaller than this transitions to new turn
min_angle_correction = 2 #how many degrees away from bearing to use a gradual turn.  Smaller than this and go straight
pwm1 = 240 #set pulse width modulation for each motor
pwm2 = 240
pwm3 = 240
pwm4 = 240
slow_turnoffset = 20 #subtract pwm by this amount for a slow turn

#loop and time info
loops = 0 #counts number of loops
start_time = end_time = run_time = 0.0 #used for finding loop time in seconds
write_time = 0.0 #used to determine when to write a file
time_stamp = 0.0 #time stamp each of the recordings
read_time = 0.0 #read GPS data delay
report_time = 0.0 #used in debuging to report various items to console

#initialize gps variables
lat = lon = lat_origin = lon_origin = xgps = ygps = 0.0

#initialize position variables
xcurrent = ycurrent = xtranslation = ytranslation = 0.0
xdestination = ydestination = 0.0
dist_togo = bearing = angle_diff = 0.0

#initialize encoder variables
xallincrements = yallincrements = 0.0 #used for encoder incremental distance calculation
pastdistance = 0.0 #used for encoder incremental distance calculation

#create Events
adcGetDataFlag = threading.Event()
TickAdd_AvgDistanceFlag = threading.Event()
xypositionFlag = threading.Event()
savedataFlag = threading.Event()
acceldistanceFlag = threading.Event()
getAcceldataFlag = threading.Event()


#create Queues
headingQ = LifoQueue()
distanceQ = LifoQueue()
xcurrentQ = LifoQueue()
ycurrentQ = LifoQueue()
latQ = LifoQueue()
lonQ = LifoQueue()
sysQ = LifoQueue()
gyroQ = LifoQueue()
accelQ = LifoQueue()
magQ = LifoQueue()
acceldistanceQ = LifoQueue()
adc0q = Queue()
adc1q = Queue()
adc2q = Queue()
adc3q = Queue()
xQ = Queue()
yQ = Queue()
zQ = Queue()
accelTimeQ = Queue()

#create threads
if isEncoderused:
    adcGetDataThread = threading.Thread(target = ADC.adcGetData,args=(adc0q,adc1q,adc2q,adc3q,adcGetDataFlag)).start()
    TickAdd_AvgDistanceThread = threading.Thread(target = ADC.TickAdd_AvgDistance,args=(distanceQ,adc0q,adc1q,adc2q,adc3q,TickAdd_AvgDistanceFlag)).start()
    print 'isEncoderUsed: ' + str(TickAdd_AvgDistanceThread)



def distanceAccel():
    # dt: the sampling time must be greater than
    # alist,vlist,dlist must be initilized if classes not imported
    #print('(0): inside distanceAccel function')
    alist = classes.myList()
    vlist = classes.myList()
    dlist = classes.myList()
    tlist = classes.myList()
    total_distance = 0
    while True:
        #print('(1): start while loop')
        if acceldistanceFlag.isSet():
            alist = classes.myList()
            vlist = classes.myList()
            dlist = classes.myList()
            tlist = classes.myList()
            t2list = classes.myList()
            total_distance = 0
            #print('(2): reset variables')
        if not xQ.empty() and not yQ.empty() and not zQ.empty() and not accelTimeQ.empty():
            mag = math.sqrt(xQ.get()**2 + yQ.get()**2 + zQ.get()**2)
            alist.append(mag)
            tlist.append(accelTimeQ.get())
            #print('(3): get queue data')
        if len(alist) == 3 and len(tlist) == 3:
            dt = tlist[1] - tlist[0]
            t2list.append(dt)
            #print('t1 and t0: ' + str(tlist[1]) + ', ' + str(tlist[0]))
            #print('dt: ' + str(dt))
            out = float(alist[0]+alist[1])*float(dt)*0.5
            vlist.append(out)
            #print('(4): calc vlist')
            #print('alist' + str(alist))
        if len(vlist) == 3 and len(t2list) == 3:
            dt2 = t2list[1] - t2list[0]
            out = float(vlist[0]+vlist[1])*float(dt2)*0.5
            dlist.append(out)
            #print('(5): calc dlist')
            #print('vlist' + str(vlist))
        if len(dlist) == 3:
            total_distance = total_distance + dlist[0]
            #acceldistanceQ.put(total_distance)
            #print('(6): ********Accel Distance',total_distance)
            #print('dlist' + str(dlist))
            distanceQ.put(total_distance)

def getheading():
    record_time = 0.0
    end_time = 0.0
    while True:
        start_time = time.time()
        heading, roll, pitch = bno.read_euler()
        heading = 360 - heading

        record_time += end_time + time.time() - start_time
        if getAcceldataFlag.isSet() and record_time > .5:
            #print('record time: ' + str(record_time))
            x, y, z = bno.read_linear_acceleration()
            sample_time = time.time()
            accelTimeQ.put(sample_time)
            xQ.put(x)
            yQ.put(y)
            zQ.put(z)
            record_time = 0.0
        sys, gyro, accel, mag = bno.get_calibration_status()
        headingQ.put(heading)
        sysQ.put(sys)
        gyroQ.put(gyro)
        accelQ.put(accel)
        magQ.put(mag)
        end_time = time.time() - start_time
    #time.sleep(1)

def xyposition(xcurrentQ, ycurrentQ, distanceQ, headingQ,xypositionFlag):
    #global xtranslation
    #global ytranslation
    pastdistance = 0.0 #zero distance traveled at start
    xallincrements = yallincrements = 0.0
    while True:
        #print 'XYPOSITION: Event= ' + str(xypositionFlag) + str(xypositionFlag.isSet())
        if xypositionFlag.isSet():
            pastdistance = 0.0 #zero distance traveled at start
            xallincrements = yallincrements = 0.0
            #heading = LifoQueue()
            #distance = LifoQueue()

        if not distanceQ.empty() and not headingQ.empty():   
            distance = distanceQ.get()
            heading = headingQ.get()

            distincrement = distance - pastdistance #pastdistance is encoderdistance the last time it was imported, pastdistance reset fully stopped at destination
            pastdistance = distance #recycle current distance data into pastdistance to be used in next loop

            xincrement, yincrement = positioning_calc.xy_getpoint(heading, distincrement)
            xallincrements += xincrement  #these guys get reset when fully stopped at destination
            yallincrements += yincrement

            xcurrentQ.put(xallincrements)
            ycurrentQ.put(yallincrements)

#def gpsdata(latQ, lonQ):
#    gpsd = gps(mode=WATCH_ENABLE)
#    while True:
#        gpsd.next()
#        latQ.put(gpsd.fix.latitude)
#        lonQ.put(gpsd.fix.longitude)

#        time.sleep(.1) #GPS updates at 10Hz, no reason to sample faster

#def savedata(savestring):
#    fout = open(saveName, 'wt')
#    fout.close()
    
if isIMUaccelused:
    distanceAccelThread = threading.Thread(target = distanceAccel,args=()).start()
    #print('start distanceIMU thread: ' + str(distanceAccelThread))
    
        
getheadingThread = threading.Thread(target = getheading,args=()).start()
xypositionThread = threading.Thread(target = xyposition,args = (xcurrentQ, ycurrentQ, distanceQ, headingQ, xypositionFlag)).start()
#print('start xyposition thread: ' + str(xypositionThread))
#gpsdataThread = threading.Thread(target = gpsdata,args = (latQ, lonQ)).start()
#if isSave:
#    savedataThread = threading.Thread(target = writedata,args = (savestring)).start()

#save text file data
#encodersave = 'encodersave1.txt'
#fout = open(encodersave, 'wt')
#fout.close()

while True:
    #print('********************************** beginning of loop ****************************')
    #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)
    #loop timing and counting
    start_time = time.time()
    run_time += end_time
    loops += 1

    #print('Queue Sizes')
    #print(xQ.qsize())
    #print(yQ.qsize())
    #print(zQ.qsize())
    #print(accelTimeQ.qsize())
    #print(distanceQ.qsize())
    
    report_time += end_time + time.time() - start_time
    if run_time < 30:
        heading = headingQ.get()
        heading = 360 - heading
        sys = sysQ.get()
        gyro = gyroQ.get()
        accel = accelQ.get()
        mag = magQ.get()
        # Print everything out.
        if report_time > 5:
            print('Heading={0:0.2F}\tSys_cal={1} Gyro_cal={2} Accel_cal={3} Mag_cal={4}'.format(
              heading, sys, gyro, accel, mag))
            report_time = 0.0
        

    #if isdestination = false then get a destination from user
    if not isdestination and run_time > 20:
        print('****** Get Destination *******')
        xypositionFlag.set() #reset distance calculations
        while not distanceQ.empty():
            junk = distanceQ.get()
        while not headingQ.empty():
            junk = headingQ.get()
        while not xcurrentQ.empty():
            junk = xcurrentQ.get()
        while not ycurrentQ.empty():
            junk = ycurrentQ.get()
        while not latQ.empty():
            junk = latQ.get()
        while not lonQ.empty():
            junk = lonQ.get()
        #print(headingQ.qsize())
        #print(distanceQ.qsize())
        #print(xcurrentQ.qsize())
        #print(ycurrentQ.qsize())
        #print(adc0q.qsize())
        TickAdd_AvgDistanceFlag.set()
        acceldistanceFlag.set()
        time.sleep(1)
        ############
        heading = headingQ.get()
        heading = 360 - heading
        sys = sysQ.get()
        gyro = gyroQ.get()
        accel = accelQ.get()
        mag = magQ.get()
        # Print everything out.
        print('Heading={0:0.2F}\tSys_cal={1} Gyro_cal={2} Accel_cal={3} Mag_cal={4}'.format(
          heading, sys, gyro, accel, mag))
        
        #################
        xdestination = float(raw_input('xcoord: '))
        ydestination = float(raw_input('ycoord: '))
        isdestination = True
        #print('xy position flag status: ' + str(xypositionFlag.isSet()))
        xypositionFlag.clear() #ready for calculation
        acceldistanceFlag.clear()
        #print('xy position flag status: ' + str(xypositionFlag.isSet()))
        TickAdd_AvgDistanceFlag.clear()
        #xcurrentQ = LifoQueue()
        #ycurrentQ = LifoQueue()
        #store xy past position into translation for finding current xy position for subsequent destinations
        #info used in the xyposition function
        xtranslation += xcurrent
        ytranslation += ycurrent
        xdestination -= xtranslation
        ydestination -= ytranslation
        xcurrent = 0.0
        ycurrent = 0.0
        #xcurrent = ycurrent = 0.0
    #print('___top loop info')
    #print('xydestination translated',xdestination,ydestination)
    #print('xytranslation',xtranslation,ytranslation)
    #print('xycurrent translated',xcurrent,ycurrent)

    #if ismovingforward:
        #read_time += end_time + time.time() - start_time
        #if read_time > .5:
            #if isGPSused:
                #fin = open('gpslog.txt', 'rt')
                #gpslog = fin.read()
                #fin.close()
                #if gpslog:
                    #gpsdata = gpslog.split(' ')
                    #lat = float(gpsdata[0])
                    #lon = float(gpsdata[1])
                #print('loop: %d, time: %.3f |lat: %f|lon: %f' % (loops,run_time,lat,lon))
                #if not isgetGPSorigin and (lon != 0 and lat != 0):
                    #lon_origin = lon
                    #lat_origin = lat
                    #isgetGPSorigin = True
            #read_time = 0
    #print('lat and lon',lat,lon)
    #print('gps origin',lon_origin,lat_origin)

    #if isGPSused:
        #gpsdistance_origin = positioning_calc.haversine(lat_origin, lon_origin, lat, lon)
        #gpsbearing_north = positioning_calc.gpsbearing(lat_origin, lon_origin, lat, lon)
        #xgps, ygps = positioning_calc.xy_getpoint(gpsbearing_north, gpsdistance_origin)

    #print('gpsdistance_origin',gpsdistance_origin)
    #print('gpsbearing_north',gpsbearing_north)
    #print('xygps',xgps,ygps)

    #Use encoder distance data to calculate current xy position
    #thread is started when a destination is set and constantly takes live data to get most up to date xy position
    #xycurrent is stored in Lifoqueue named xcurrentQ and ycurrentQ
    #if isEncoderused:
        #find total encoder distance traveled and only run when there is a destination set.  stops thread when destination reached
        #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)
        #if isdestination and not TickAdd_AvgDistanceThread.ident == None:
            #print 'Call START DISTANCE'
            #TickAdd_AvgDistanceThread = threading.Thread(target = ADC.TickAdd_AvgDistance,args=(distanceQ,adc0q,adc1q,adc2q,adc3q,TickAdd_AvgDistanceFlag)).start() 
        #print('after isAlive()')
        #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)
        #collect ticks on encoder if moving forward and stop recording if not moving forward (stationary turn or just immobile)
        #if ismovingforward and not adcGetDataThread.ident == None:
          #  print 'Call START ADC'
         #   adcGetDataThread = threading.Thread(target = ADC.adcGetData,args=(adc0q,adc1q,adc2q,adc3q,adcGetDataFlag)).start()
        #calculates most recent xy position based on distance traveled and puts it into a Lifo queue
        #if isdestination and not xypositionThread.ident == None:
            #xypositionThread = threading.Thread(target = eventloop_Functions.xyposition,args = (xtranslation, ytranslation, xcurrentQ, ycurrentQ, distanceQ, headingQ, xypositionFlag)).start()
        #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)
        #print '!!!!!!xypositionThread' + str(xypositionThread)
                   
    #print('after encoder line')
    #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)

    #sys, gyro, accel, mag = bno.get_calibration_status()
    #print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
    #      heading, roll, pitch, sys, gyro, accel, mag))

    if not xcurrentQ.empty() and not ycurrentQ.empty():
        xcurrent = xcurrentQ.get()
        ycurrent = ycurrentQ.get()
        #xcurrentQ = LifoQueue()
        #ycurrentQ = LifoQueue()
        #print('getting xycurrent from queue',xcurrent,ycurrent)
    #xcurrent += xtranslation
    #ycurrent += ytranslation

    #write_time += end_time + time.time() - start_time
    #if time_stamp == 0:
        #time_stamp = time.time()
    #if write_time > 1:
        #print('xycurrent: queue',xcurrent,ycurrent)
        #fout = open(encodersave, 'a')
        #fout.write(str(time.time() - time_stamp) + ',' + str(xcurrent) + ',' + str(ycurrent) + ',' \
        #                   + str(heading) + ',' + str(xgps) + ',' + str(ygps) + ',' + '\n')
        #fout.close()
        #write_time = 0.0

    if not headingQ.empty():
        heading = headingQ.get()
    #headingQ.queue.clear()
    #print('after get xycurrent,heading')
    #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)

    if isdestination:
        dist_togo = positioning_calc.distance_togo(xcurrent, ycurrent, xdestination, ydestination)
        bearing = positioning_calc.bearing_deg(xdestination, ydestination)
        angle_diff = positioning_calc.angle_diff(heading, bearing)
        isclockwise = positioning_calc.rotation_dir(heading, bearing)
        print("dist_togo: %.2f|bearing: %.2f|angle_diff: %.2f|go CW?: %r" % \
              (dist_togo, bearing, angle_diff, isclockwise))

    #print('after distance calculations')
    #print 'isDestination: ' + str(TickAdd_AvgDistanceThread) 
    #print('isdestination',isdestination,'dist_togo',dist_togo,'min_distance_correction',min_distance_correction)
    #print('first if',isdestination and dist_togo > min_distance_correction)
    if isdestination and dist_togo > min_distance_correction:
        ismoving = True
        print('1')
        #print('moving',ismoving,'forward',ismovingforward,'turning',isturning)
    
        if angle_diff >= fullstopturn:
            print('2')
            if isclockwise:
                motor.rotate_Cwise(.002)
            else:
                motor.rotate_CCwise(.002)
            print('3')
            #motor_op.seesaw_turn(isclockwise)
            isturning = True
            ismovingforward = False
        elif angle_diff < fullstopturn and angle_diff > min_angle_correction:
            print('4')
            motor_op.forward()
            motor_op.gradual_correction(isclockwise, slow_turnoffset, pwm1, pwm2, pwm3, pwm4)
            print('5')
            isturning = True
            ismovingforward = True
        else:
            print('6')
            motor_op.forward()
            motor_op.fullspeed(pwm1, pwm2, pwm3, pwm4)
            print('7')
            isturning = False
            ismovingforward = True
    
    elif isdestination and dist_togo <= min_distance_correction:
        print('8')
        ismoving = False
        isturning = False
        isdestination = False
        ismovingforward = False
        print('9')
        motor_op.gradstop(pwm1, pwm2, pwm3, pwm4)
        print('10')
        #### tell encoderData.py to reset encoder
        #fout = open('runencoderstatus.txt', 'wt')
        print('12')
        #fout.write(str(ismovingforward) + ' ' + str(isdestination))
        #fout.close()
        #### reset encoder variables for maineventloop.py calculations
        xallincrements = 0.0
        yallincrements = 0.0
        pastdistance = 0.0

    #print('after motor control')
    #print 'isDestination: ' + str(TickAdd_AvgDistanceThread)

    #kill threads
    #if isEncoderused:
    #    print(not ismovingforward and adcGetDataThread.isAlive())
    #    if not ismovingforward and adcGetDataThread.isAlive():
    #        adcGetDataFlag.set()
    #    print(not isdestination and TickAdd_AvgDistanceThread.isAlive())
    #    if not isdestination and TickAdd_AvgDistanceThread.isAlive():
    #        TickAdd_AvgDistanceFlag.set()
    #    print(not isdestination and xypositionThread.isAlive())
    #    if not isdestination and xypositionThread.isAlive():
    #        xypositionFlag.set()

    #Flag threads
    if ismovingforward:
        adcGetDataFlag.set()
        getAcceldataFlag.set()
    else:
        adcGetDataFlag.clear()
        getAcceldataFlag.clear()

   # time.sleep(1)
    end_time = time.time() - start_time
    


        
