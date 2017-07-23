
import logging
import sys
import time

from Adafruit_BNO055 import BNO055


# Create and configure the BNO sensor connection.  Make sure only ONE of the
# below 'bno = ...' lines is uncommented:
# Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
# BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
# and RST connected to pin P9_12:
#bno = BNO055.BNO055(rst='P9_12')



# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')






met = False 
while met==False:
    sys,gyro,accel,mag=bno.get_calibration_status()
    print('Sys_cal={0} Gyro_cal={1} Accel_cal={2} Mag_cal={3}'.format(sys, gyro, accel, mag))
    time.sleep(1)
    if sys==3:
        if gyro==3:
            if accel==3:
                if mag==3:
                    print'CALIBRATED!'
                    met=True


while True:
    ask=input('1.save\t2.get calibration status\n')
    if ask==1:
        data=bno.get_calibration()
        dataByteArray = bytearray(data)
        File=open('cal_prof','wb')
        File.write(dataByteArray)
        File.close()
        
        
    if ask==2:
        sys,gyro,accel,mag=bno.get_calibration_status()
        print('Sys_cal={0} Gyro_cal={1} Accel_cal={2} Mag_cal={3}'.format(sys, gyro, accel, mag))
        time.sleep(1)
                    
                    
