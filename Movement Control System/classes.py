import logging
import sys
import time
import math
import atexit







#libraries for IMU
from Adafruit_BNO055 import BNO055
#libraries for MOTORS
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
#libraries for GPS
import gps



class IMU_Operations(object):
    def __init__(self):
        self.bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
        # Initialize the BNO055 and stop if something went wrong.
        if not self.bno.begin():
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
        # Load Calibration profile
        self.load_calibration_profile()
        self.calibration_status()
        
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
        self.heading,self.roll,self.pitch=self.bno.read_euler()
        print(self.heading)
        

    def heading_euler_p(self):
        while True:
            self.heading,self.roll,self.pitch=self.bno.read_euler()
            print(self.heading)
            time.sleep(1)

    def accel_data(self):
        x,y,z = self.bno.read_accelerometer()
        return(x,y,z)
                
    def lin_accel_data(self):
        x, y, z = self.bno.read_linear_acceleration()
        return(x,y,z)

    # save the accel data s:runtime r: point every r second

    def save_accel_data(self):
        start_time = time.time()
        f=open('accel_data','w')
        for i in xrange (100):
            time_stamp = time.time() - start_time
            x,y,z = self.bno.read_linear_acceleration()
            amp=math.sqrt(x**2+y**2+z**2)
            f.write(str(time_stamp) + ',' + str(x) + ',' + str(y) + ',' + str(z) + ',' + str(amp) + '\n')
            time.sleep(0.1)
            
        f.close()

    def get_point(self):
        while True:
            #try:
            x,y,z = self.bno.read_linear_acceleration()
            #time.sleep(0.0001)
            amp = math.sqrt(float(x**2)+float(y**2)+float(z**2))
            return(amp)
            #except:
             #   pass
            
            #print (amp)
            
            
            
    def tpaz(self,p1,p2,dt):
        out = float(p1+p2)*float(dt)*0.5
        return (out)
        
        

class myList(list):
    def append(self,item):
        if len(self) >= 3:
            self[:1]=[]
        list.append(self,item)
        
            
            
            
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
        
    #this is the full speed function
    def setspeed(self,pwm1,pwm2,pwm3,pwm4):
        self.motor1.setSpeed(pwm1)
        self.motor2.setSpeed(pwm2)
        self.motor3.setSpeed(pwm3)
        self.motor4.setSpeed(pwm4)
        
        
    
    def forward(self):
        self.motor1.run(Adafruit_MotorHAT.FORWARD)
        self.motor2.run(Adafruit_MotorHAT.FORWARD)
        self.motor3.run(Adafruit_MotorHAT.FORWARD)
        self.motor4.run(Adafruit_MotorHAT.FORWARD)
        
        
        
    
    def reverse(self):
        self.motor1.run(Adafruit_MotorHAT.BACKWARD)
        self.motor2.run(Adafruit_MotorHAT.BACKWARD)
        self.motor3.run(Adafruit_MotorHAT.BACKWARD)
        self.motor4.run(Adafruit_MotorHAT.BACKWARD)
        
    #t= 0.002 rotates by almost five degrees not calibrated on pavement
    def rotate_CCwise(self,t):
        for i in xrange(1):
            x=5
            y=0
            while x>0:
                self.setspeed(250,0,250,0)
                self.forward()
                time.sleep(float(t))
                x-=1
                y+=1
            while y>0:
                self.setspeed(0,250,0,250)
                self.reverse()
                time.sleep(float(t))
                y-=1
                x+=1
            self.allstop()

    def rotate_Cwise(self,t):
        for i in xrange(1):
            x=5
            y=0
            while x>0:
                self.setspeed(250,0,250,0)
                self.reverse()
                time.sleep(float(t))
                x-=1
                y+=1
            while y>0:
                self.setspeed(0,250,0,250)
                self.forward()
                time.sleep(float(t))
                y-=1
                x+=1
        self.allstop()

    #pass t to control the distance
    def gradstop(self,pwm1, pwm2, pwm3, pwm4,t):

        pwmdict = {'pwm1':pwm1,'pwm2':pwm2,'pwm3':pwm3,'pwm4':pwm4}
        minpwm = min(pwmdict, key=lambda k: pwmdict[k])

        for i in reversed(range(pwmdict[minpwm])):
            self.setspeed(i,i,i,i)
            time.sleep(float(t))
            
           

        

    
    #pass t to control the distance
    def gradgo(self,pwm1,pwm2,pwm3,pwm4,t):
        pwmdict = {'pwm1':pwm1,'pwm2':pwm2,'pwm3':pwm3,'pwm4':pwm4}
        minpwm = min(pwmdict, key=lambda k: pwmdict[k])
                      
        self.forward()
    
        for i in range(pwmdict[minpwm]):
            self.setspeed(i,i,i,i)
            time.sleep(float(t))
            #print(i)
          

        #self.allstop()

    #this functio is for testing purposes only
    def gradmove(self,s):
        
        self.gradgo(s,s,s,s)
        self.gradstop(s,s,s,s)
        self.allstop()

    #pass t to control the distance 
    def gradgoback(self,pwm1, pwm2, pwm3, pwm4,t):
        pwmdict = {'pwm1':pwm1,'pwm2':pwm2,'pwm3':pwm3,'pwm4':pwm4}
        minpwm = min(pwmdict, key=lambda k: pwmdict[k])
                          
        self.reverse()
    
        for i in (range(pwmdict[minpwm])):
            self.setspeed(i,i,i,i)
            time.sleep(float(t))        #increase sleep to increase speed up distance

        self.setspeed(i,i,i,i)

        
        
        


    
imu=IMU_Operations()
motor=Motor_Operations()
alist = myList()
vlist = myList()
dlist = myList()





    
        



















   
    










    





		
   
