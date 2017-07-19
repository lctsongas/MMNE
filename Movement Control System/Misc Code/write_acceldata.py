import sys
import time
from Adafruit_BNO055 import BNO055


docName = 'myAccelerationData.txt' #name of text file
fout = open(docName,'wt') #creates file with string in docName, or overwrites existing file
fout.close()

bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
start_time = time.time() #start of program

while True:
    heading, roll, pitch = bno.read_euler()
    sys, gyro, accel, mag = bno.get_calibration_status()
    time_stamp = time.time() - start_time
    print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))

    x,y,z = bno.read_linear_acceleration()
    print(time_stamp,x,y,z)

    fout = open(docName,'a') #reopens file in append mode
    fout.write(str(time_stamp) + ',' + str(x) + ',' + str(y) + ',' + str(z) + '\n')
    fout.close()

    time.sleep(1) #change to whatever
    
