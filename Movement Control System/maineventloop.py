from gps import * #imports "everything" from gps
from Adafruit_BNO055 import BNO055
import motor_op
import positioning_calc

import time
import math
import sys
import atexit

# Create and configure the BNO sensor connection
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)

#start GPS session
session = gps(mode=WATCH_ENABLE)


#loop variable initializations
loops = 0
lat = lon = 0.0
run_time = 0.0
xcurrent = ycurrent = 0.0

isGPSusedmovement = True
ismoving = False
ismovingforward = False
isturning = False
isdestination = False
isgetGPSorigin = False

#calibrations for individual robot ***WRITE CALIBRATION FILE LATER
isheadingoffset = True
heading_offset = -90 #(degrees) offset to compensate for imu mounting direction and robot's front direction
pwm1 = 235 #max speed of each motor, change for offsets if needed
pwm2 = 240
pwm3 = 235
pwm4 = 240

#performance options
fullstopturn = 10 #(degrees) full stop turn if angle difference between heading and bearing is greater than amount
slow_turnoffset = 3 #(PWM) offset supplied to motors during a slow turn
rotation_speed = 70 #speed to rotate at full stop (value PWM between 0 and 255)
min_angle_correction = 2 #minimum angle between heading and bearing at which robot returns to straight trajectory
min_distance_correction = 1 #minimum meters when rover stops and has hit the target destination

###### Main Event Loop ##########
atexit.register(motor_op.allstop)
while True:
    #loop timing and counting
    start_time = time.time()
    loops += 1

    ########## MODIFY HERE #######
    #get destination info
    #currently console input (need to set up port)
    if not isdestination and run_time > 5:
        xdestination = float(raw_input('xcoord: '))
        ydestination = float(raw_input('ycoord: '))
        isdestination = True        
    ##############################


    ########### SENSOR ACQUISITION ###########
    #lat, lon, heading

    #get gps data and set gps origin
    report = session.next()
    if report['class'] == 'DEVICE':
        session.close()
        session = gps(mode=WATCH_ENABLE)
    if report[u'class'] == u'TPV':
        lon = report[u'lon']
        lat = report[u'lat']
    loop_time = time.time() - start_time
    print('loop: %d, time: %.3f |lat: %f|lon: %f' % (loops,loop_time,lat,lon))
    if not isgetGPSorigin and (lon > 0 and lat > 0):
        lon_origin = lon
        lat_origin = lat
        isgetGPSorigin = True
            

    #get imu data
    heading, roll, pitch = bno.read_euler()
    if isheadingoffset:
        if heading_offset < 0 and heading < math.fabs(heading_offset):
            heading = 360 + heading + heading_offset
        else:
            heading = (heading + heading_offset) % 360
        
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()
    # Print everything out.
    #print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
    #      heading, roll, pitch, sys, gyro, accel, mag))
    print("heading", heading)
    loop_time = time.time() - start_time
    ##################################


    #gps movement section
    if isgetGPSorigin:
        gpsdistance_origin = positioning_calc.haversine(lat_origin, lon_origin, lat, lon)
        gpsbearing_north = positioning_calc.gpsbearing(lat_origin, lon_origin, lat, lon)
        xcurrent, ycurrent = positioning_calc.xy_getpoint(gpsbearing_north, gpsdistance_origin)
        print("xycurrent",xcurrent, ycurrent)

    #heading test and correction information
    if isdestination:
        dist_togo = positioning_calc.distance_togo(xcurrent, ycurrent, xdestination, ydestination)
        bearing = positioning_calc.bearing_deg(xcurrent, ycurrent, xdestination, ydestination)
        angle_diff = positioning_calc.angle_diff(heading, bearing)
        isclockwise = positioning_calc.rotation_dir(heading, bearing)
        print("travel distance: %.2f|bearing: %.2f|angle to close: %.2f|go CW?: %r" % \
              (dist_togo, bearing, angle_diff, isclockwise))

    #compensator section
    #currently only full top or slight turn options
    #slight turn is fixed but could add a proportional controller to increase PWM if angle is increased
    if isdestination and dist_togo > min_distance_correction:
        ismoving = True
        #print('moving',ismoving,'forward',ismovingforward,'turning',isturning)

        if angle_diff >= fullstopturn:
            if ismovingforward:
                ismovingforward = motor_op.gradstop(pwm1, pwm2, pwm3, pwm4)
                isturning = motor_op.allrotate(isclockwise, rotation_speed)
                print('1')
            elif not isturning:
                isturning = motor_op.allrotate(isclockwise, rotation_speed)
                print('2')
        else:
            if angle_diff < min_angle_correction:
                if ismovingforward and isturning:
                    isturning = not(motor_op.fullspeed(pwm1, pwm2, pwm3, pwm4))
                    print('3')
                if not ismovingforward:
                    ismovingforward = motor_op.gradgo(pwm1, pwm2, pwm3, pwm4)
                    print('4')
            else:
                if ismovingforward and not isturning:
                    isturning = motor_op.gradual_correction(isclockwise, slow_turnoffset, pwm1, pwm2, pwm3, pwm4)
                    print('5')
                if not ismovingforward:
                    ismovingforward = motor_op.gradgo(pwm1, pwm2, pwm3, pwm4)
                    isturning = motor_op.gradual_correction(isclockwise, slow_turnoffset, pwm1, pwm2, pwm3, pwm4)
                    print('6')
    
    else:
        ismoving = False
        isturning = False
        ismovingforward = motor_op.gradstop(pwm1, pwm2, pwm3, pwm4)
        isdestination = False
        
    #loop timing
    time.sleep(1)
    end_time = time.time() - start_time
    run_time += end_time
