import logging
import sys
import time
import math
import atexit
from threading import Thread


from Adafruit_BNO055 import BNO055
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor


class IMU_Operations(object):
    def __init__(self):
        self.bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
        # Initialize the BNO055 and stop if something went wrong.
        if not self.bno.begin():
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
        # Load Calibration profile
        self.load_calibration_profile()
        self.heading_euler()
        
        
    def load_calibration_profile(self):
        self.infile= open('cal_prof','rb')
        self.data=self.infile.read()
        self.infile.close()
        self.newdata=bytearray(self.data)
        self.bno.set_calibration(self.newdata)

    def calibration_status(self):
        self.sys,self.gyro,self.accel,self.mag=self.bno.get_calibration_status()
        print('Sys_cal={0} Gyro_cal={1} Accel_cal={2} Mag_cal={3}'.format(self.sys, self.gyro, self.accel, self.mag))

    def zero_north(self):
        self.x,self.y,self.z=self.bno.read_magnetometer()
        self._North_=math.atan2(self.y,self.x)
        self.degree=math.degrees(self._North_)
        return (self.degree)

    def heading_euler(self):
        while True:
            self.heading,self.roll,self.pitch=self.bno.read_euler()
            return(self.heading)

    def heading_euler_p(self):
        while True:
            self.heading,self.roll,self.pitch=self.bno.read_euler()
            print(self.heading)
            time.sleep(1)
        


class Motor_Operations(object):
    def __init__(self):
        # create a default object, no changes to I2C address or frequenc
        self.mh = Adafruit_MotorHAT(addr=0x60)
        # 
        self.motor1 = self.mh.getMotor(1) #Front Right
        self.motor2 = self.mh.getMotor(2) #Front Left
        self.motor3 = self.mh.getMotor(3) #Back Right
        self.motor4 = self.mh.getMotor(4) #Back Left

    def allstop(self):
        self.motor1.run(Adafruit_MotorHAT.RELEASE)
        self.motor2.run(Adafruit_MotorHAT.RELEASE)
        self.motor3.run(Adafruit_MotorHAT.RELEASE)
        self.motor4.run(Adafruit_MotorHAT.RELEASE)
        
    
    def setspeed(self,pwm1,pwm2,pwm3,pwm4):
        self.motor1.setSpeed(pwm1)
        self.motor2.setSpeed(pwm2)
        self.motor3.setSpeed(pwm3)
        self.motor4.setSpeed(pwm4)
        
    
    def forward(self,pwm1,pwm2,pwm3,pwm4):
        self.setspeed(pwm1,pwm2,pwm3,pwm4)
        self.motor1.run(Adafruit_MotorHAT.FORWARD)
        self.motor2.run(Adafruit_MotorHAT.FORWARD)
        self.motor3.run(Adafruit_MotorHAT.FORWARD)
        self.motor4.run(Adafruit_MotorHAT.FORWARD)
        
        
    
    def reverse(self,pwm1,pwm2,pwm3,pwm4):
        self.setspeed(pwm1,pwm2,pwm3,pwm4)
        self.motor1.run(Adafruit_MotorHAT.BACKWARD)
        self.motor2.run(Adafruit_MotorHAT.BACKWARD)
        self.motor3.run(Adafruit_MotorHAT.BACKWARD)
        self.motor4.run(Adafruit_MotorHAT.BACKWARD)

    def rotate_CCwise(self):
        for i in xrange(1):
            x=5
            y=0
            while x>0:
                self.forward(250,0,250,0)
                time.sleep(0.002)
                x-=1
                y+=1
            while y>0:
                self.reverse(0,250,0,250)
                time.sleep(0.002)
                y-=1
                x+=1
            self.allstop()

    def rotate_Cwise(self):
        for i in xrange(1):
            x=5
            y=0
            while x>0:
                self.reverse(250,0,250,0)
                time.sleep(0.002)
                x-=1
                y+=1
            while y>0:
                self.forward(0,250,0,250)
                time.sleep(0.002)
                y-=1
                x+=1
        self.allstop()

    
imu=IMU_Operations()
motor=Motor_Operations()









   
    










    





		
   
