#Motor Operations

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# function to shut off motors when .py run in console
#def turnOffMotors():
#    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
#    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
#    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
#    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
#
#atexit.register(turnOffMotors)

#Set individual motors here or rewire terminals
#current convention is: motor1 = right front
#                       motor2 = left front
#                       motor3 = right back
#                       motor4 = left back
motor1 = mh.getMotor(1)
motor2 = mh.getMotor(2)
motor3 = mh.getMotor(3)
motor4 = mh.getMotor(4)

#all stop
def allstop():
    motor1.run(Adafruit_MotorHAT.RELEASE)
    motor2.run(Adafruit_MotorHAT.RELEASE)
    motor3.run(Adafruit_MotorHAT.RELEASE)
    motor4.run(Adafruit_MotorHAT.RELEASE)
    return False

def fullspeed(pwm1, pwm2, pwm3, pwm4):
    motor1.setSpeed(pwm1)
    motor2.setSpeed(pwm2)
    motor3.setSpeed(pwm3)
    motor4.setSpeed(pwm4)
    return True

def forward():
    motor1.run(Adafruit_MotorHAT.FORWARD)
    motor2.run(Adafruit_MotorHAT.FORWARD)
    motor3.run(Adafruit_MotorHAT.FORWARD)
    motor4.run(Adafruit_MotorHAT.FORWARD)
    return 0

def reverse():
    motor1.run(Adafruit_MotorHAT.BACKWARD)
    motor2.run(Adafruit_MotorHAT.BACKWARD)
    motor3.run(Adafruit_MotorHAT.BACKWARD)
    motor4.run(Adafruit_MotorHAT.BACKWARD)
    return 0

#gradually slow down to stop, arrived at destination
def gradstop(pwm1, pwm2, pwm3, pwm4):
    pwmdict = {'pwm1':pwm1,'pwm2':pwm2,'pwm3':pwm3,'pwm4':pwm4}
    minpwm = min(pwmdict, key=lambda k: pwmdict[k])
    for i in reversed(range(pwmdict[minpwm])):
        motor1.setSpeed(i)
        motor2.setSpeed(i)
        motor3.setSpeed(i)
        motor4.setSpeed(i)
        time.sleep(0.005)        #increase sleep to increase stop distance

    motor1.run(Adafruit_MotorHAT.RELEASE)
    motor2.run(Adafruit_MotorHAT.RELEASE)
    motor3.run(Adafruit_MotorHAT.RELEASE)
    motor4.run(Adafruit_MotorHAT.RELEASE)
    return False


#gradually speed up to move from a full stop
def gradgo(pwm1, pwm2, pwm3, pwm4):
    pwmdict = {'pwm1':pwm1,'pwm2':pwm2,'pwm3':pwm3,'pwm4':pwm4}
    minpwm = min(pwmdict, key=lambda k: pwmdict[k])
                      
    forward()
    
    for i in (range(pwmdict[minpwm])):
        motor1.setSpeed(i)
        motor2.setSpeed(i)
        motor3.setSpeed(i)
        motor4.setSpeed(i)
        time.sleep(0.001)        #increase sleep to increase speed up distance

    motor1.setSpeed(pwm1)    #use pwm calibrated values
    motor2.setSpeed(pwm2)
    motor3.setSpeed(pwm3)
    motor4.setSpeed(pwm4)

    return True

def gradgoback(pwm1, pwm2, pwm3, pwm4):
    pwmdict = {'pwm1':pwm1,'pwm2':pwm2,'pwm3':pwm3,'pwm4':pwm4}
    minpwm = min(pwmdict, key=lambda k: pwmdict[k])
                      
    reverse()
    
    for i in (range(pwmdict[minpwm])):
        motor1.setSpeed(i)
        motor2.setSpeed(i)
        motor3.setSpeed(i)
        motor4.setSpeed(i)
        time.sleep(0.001)        #increase sleep to increase speed up distance

    motor1.setSpeed(pwm1)    #use pwm calibrated values
    motor2.setSpeed(pwm2)
    motor3.setSpeed(pwm3)
    motor4.setSpeed(pwm4)

    return True

#all stop rotation (doesn't work well with distant axle separation)
def allrotate(clockwise, rot_speed): #if clockwise is true rotate clockwise, otherwise rotate counterCW
    motor1.setSpeed(rot_speed)
    motor2.setSpeed(rot_speed)
    motor3.setSpeed(rot_speed)
    motor4.setSpeed(rot_speed)

    #rotate clockwise
    if clockwise:
        motor1.run(Adafruit_MotorHAT.BACKWARD)
        motor2.run(Adafruit_MotorHAT.FORWARD)
        motor3.run(Adafruit_MotorHAT.BACKWARD)
        motor4.run(Adafruit_MotorHAT.FORWARD)
    else:
    #rotate counterclockwise
        motor1.run(Adafruit_MotorHAT.FORWARD)
        motor2.run(Adafruit_MotorHAT.BACKWARD)
        motor3.run(Adafruit_MotorHAT.FORWARD)
        motor4.run(Adafruit_MotorHAT.BACKWARD)
    return True

#seesaw turning rotation (results in about a 10 degree turn)
def seesaw_turn(clockwise): #if back_turn True then arc while backing
    pwm = 255
    turn_offset = 90
    gotime = 1
    
    pwm_o = pwm - turn_offset
    if clockwise:
        for i in xrange(1):
            x=5
            y=0
            while x>0:
                reverse()
                fullspeed(250,50,250,50)
                time.sleep(0.02)
                x-=1
                y+=1
            while y>0:
                forward()
                fullspeed(50,250,50,250)
                time.sleep(0.02)
                y-=1
                x+=1
    else:
        for i in xrange(1):
            x=5
            y=0
            while x>0:
                forward()
                fullspeed(250,50,250,50)
                time.sleep(0.02)
                x-=1
                y+=1
            while y>0:
                reverse()
                fullspeed(50,250,50,250)
                time.sleep(0.02)
                y-=1
                x+=1
    return False

#gradual correction while traveling straight
def gradual_correction(clockwise, pwm_offset, pwm1, pwm2, pwm3, pwm4):
    if clockwise:
        motor1.setSpeed(pwm1-pwm_offset)
        motor2.setSpeed(pwm2)
        motor3.setSpeed(pwm3-pwm_offset)
        motor4.setSpeed(pwm4)
    else:
        motor1.setSpeed(pwm1)
        motor2.setSpeed(pwm2-pwm_offset)
        motor3.setSpeed(pwm3)
        motor4.setSpeed(pwm4-pwm_offset)
    return True
