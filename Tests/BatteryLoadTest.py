import datetime
from time import time
import sys
sys.path.append("/home/pi/MMNE/Movement Control System")
from classes import *
from multiprocessing import Pool, Queue
from multiprocessing import cpu_count
        
def dummy(x):
    while True:
        x*x    

if __name__ == '__main__':
    #processes = cpu_count()
    
    #pool = Pool(processes)
    #pool.map_async(dummy, range(processes))
    motor = Motor_Operations()
    motor.setspeed(250,250,250,250)
    motor.forward()
    ctime = datetime.datetime.now()
    x = 2
    #with open('batterylog.txt' , 'a') as log:
        #log.write('Start ' + str(ctime) + '\n')
        #print 'started'
    while True:
        #with open('batterylog.txt' , 'a') as log:
            #log.write(str(ctime) + '\n')
        print 'recorded'
        x=x*x
        time.sleep(1)
        
