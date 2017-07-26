from gps import * #imports "everything" from gps
from Adafruit_BNO055 import BNO055
import positioning_calc
import motor_op
sys.path.append("/home/pi/MMNE/Network/NetworkUtils")
from MeshNetworkUtil import *

import time
import math
import sys
import atexit


# Create and configure the BNO sensor connection
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

#start GPS session
#session = gps(mode=WATCH_ENABLE)

#Init the listener util BEFORE
#starting the main event loop
commandReceiver = MeshNetworkUtil()
commandReceiver.startListening()

#loop variable initializations
loops = 0
lat = lon = lat_origin = lon_origin = 0.0
run_time = 0.0
xcurrent = ycurrent = 0.0
xdestination = ydestination = 0.0
gpsdistance_origin=heading= 0.0

isGPSusedmovement = True
ismoving = False
ismovingforward = False
isturning = False
isdestination = False
isgetGPSorigin = False
isNetworkingEnabled = True

#calibrations for individual robot ***WRITE CALIBRATION FILE LATER
isheadingoffset = True
heading_offset = -90 #(degrees) offset to compensate for imu mounting direction and robot's front direction
pwm1 = 235 #max speed of each motor, change for offsets if needed
pwm2 = 240
pwm3 = 235
pwm4 = 240

#performance options
fullstopturn = 15 #(degrees) full stop turn if angle difference between heading and bearing is greater than amount
slow_turnoffset = 20 #(PWM) offset supplied to motors during a slow turn
#BROKEN#rotation_speed = 250 #speed to rotate at full stop (value PWM between 0 and 255)
min_angle_correction = 2 #minimum angle between heading and bearing at which robot returns to straight trajectory
min_distance_correction = 1 #minimum meters when rover stops and has hit the target destination

###### Main Event Loop ##########
while True:
    print '**********'
    #loop timing and counting
    start_time = time.time()
    loops += 1


     ########## MODIFY HERE #######
    #get destination info
    #currently console input (need to set up port)
    #Get potential packet from networkUtil
    if isNetworkingEnabled:
        packet = commandReceiver.getPacket()
        #check if its a MeshPacket Object
        print 'Listening for packet'
        if isinstance(packet, MeshPacket):
            print 'Got a packet!'
            print packet.getPayload()
            #check if its current command is completed
            #if it is completed, then run the new command
            #otherwise ignore it and keep going
            if not isdestination and run_time > 5:
                #timestamp will have the time th epacket is
                #sent if needed later
                timestamp = packet.timestamp()
                coordinates = packet.getPayload()
                #coordinates will be in the form of:
                #1.234, 5.678 so we can split by ', '
                coordList = coordinates.split(', ')
                xdestination = float(coordList[0])
                ydestination = float(coordList[1])
                isdestination = True
    else :
        if not isdestination and run_time > 5:
            xdestination = float(raw_input('xcoord: '))
            ydestination = float(raw_input('ycoord: '))
            isdestination = True        
    ##############################
    #Networking stuff: sends data TO whomever sent the packet
    #if isNetworkingEnabled:
    #    replyData = str(xcurrent) + ', ' + str(ycurrent) + ', ' + str(heading)
    #    address = '10.0.0.2'
    #    commandReceiver.sendPacket(replyData, address)
    #    packet = None


    ########### SENSOR ACQUISITION ###########
    #lat, lon, heading

    #get GPS data
    fin = open('gpslog', 'rt')
    gpslog = fin.read()
    fin.close()
    if gpslog:
        gpsdata = gpslog.split(' ')
        lat = float(gpsdata[0])
        lon = float(gpsdata[1])
    print('loop: %d, time: %.3f |lat: %f|lon: %f' % (loops,run_time,lat,lon))
    if not isgetGPSorigin and (lon != 0 and lat != 0):
        lon_origin = lon
        lat_origin = lat
        isgetGPSorigin = True
        #print('setting gps to origin')

    #print('isdestination set', isdestination, 'xydestination', xdestination, ydestination)
    #print('isgetGPSorigin set', isgetGPSorigin)
    print('gps origin', lat_origin, lon_origin)
    #print('gps distance from origin', gpsdistance_origin)

    #get imu data
    heading, roll, pitch = bno.read_euler()
    #correct for 90 degree placement on robot
    #if isheadingoffset:
    #    if heading_offset < 0 and heading < math.fabs(heading_offset):
    #        heading = 360 + heading + heading_offset
    #    else:
    #        heading = (heading + heading_offset) % 360
    #
    #correct for unit circle (counter clockwise) degrees
    heading = 360 - heading
    
        
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()
    # Print everything out.
    print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))
    #print("heading", heading)
    loop_time = time.time() - start_time
    ##################################


    #gps movement section
    if isgetGPSorigin:
        gpsdistance_origin = positioning_calc.haversine(lat_origin, lon_origin, lat, lon)
        gpsbearing_north = positioning_calc.gpsbearing(lat_origin, lon_origin, lat, lon)
        xcurrent, ycurrent = positioning_calc.xy_getpoint(gpsbearing_north, gpsdistance_origin)
    print("xycurrent",xcurrent, ycurrent)
    print('gps distance from origin', gpsdistance_origin, 'to feet', (gpsdistance_origin * 3.28))

    
    #heading test and correction information
    if isdestination:
        dist_togo = positioning_calc.distance_togo(xcurrent, ycurrent, xdestination, ydestination)
        bearing = positioning_calc.bearing_deg(xcurrent, ycurrent, xdestination, ydestination)
        angle_diff = positioning_calc.angle_diff(heading, bearing)
        isclockwise = positioning_calc.rotation_dir(heading, bearing)
        print("travel distance: %.2f|bearing: %.2f|angle to close: %.2f|go CW?: %r" % \
              (dist_togo, bearing, angle_diff, isclockwise))
    print('destination xy',xdestination,ydestination)
    #compensator section
    #currently only full top or slight turn options
    #slight turn is fixed but could add a proportional controller to increase PWM if angle is increased
    if isdestination and dist_togo > min_distance_correction:
        ismoving = True
        #print('moving',ismoving,'forward',ismovingforward,'turning',isturning)

        if angle_diff >= fullstopturn:
            if ismovingforward:
                ismovingforward = motor_op.gradstop(pwm1, pwm2, pwm3, pwm4)
                isturning = motor_op.seesaw_turn(isclockwise)
                print('**branch 1', 'ismovingforward',ismovingforward,'isturning',isturning)
            elif not isturning:
                isturning = motor_op.seesaw_turn(isclockwise)
                print('**branch 2', 'isturning', isturning)
        else:
            if angle_diff < min_angle_correction:
                if ismovingforward and isturning:
                    isturning = not(motor_op.fullspeed(pwm1, pwm2, pwm3, pwm4))
                    print('**branch 3','isturning',isturning)
                if not ismovingforward:
                    ismovingforward = motor_op.gradgo(pwm1, pwm2, pwm3, pwm4)
                    print('**branch 4','ismovingforward',ismovingforward)
            else:
                if ismovingforward and not isturning:
                    isturning = motor_op.gradual_correction(isclockwise, slow_turnoffset, pwm1, pwm2, pwm3, pwm4)
                    print('**branch 5')
                if not ismovingforward:
                    ismovingforward = motor_op.gradgo(pwm1, pwm2, pwm3, pwm4)
                    isturning = motor_op.gradual_correction(isclockwise, slow_turnoffset, pwm1, pwm2, pwm3, pwm4)
                    print('**branch 6')
    
    else:
        ismoving = False
        isturning = False
        ismovingforward = motor_op.gradstop(pwm1, pwm2, pwm3, pwm4)
        isdestination = False
        
    #loop timing
    time.sleep(1)
    #print('ismoving',ismoving)
    end_time = time.time() - start_time
    run_time += end_time
