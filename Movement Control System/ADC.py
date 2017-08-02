import Adafruit_ADS1x15
import time
import threading
from Queue import Queue, LifoQueue



wheel_size = .205 #wheel circumference in meters (meters/rotation)
#wheel_size = .6726 #wheel circumference in feet (feet/rotation)

def adcGetData(adc0q,adc1q,adc2q,adc3q,adcGetDataFlag):
    #print 'ADC STARTED'
    sample_time = 0 #sample roughly every 25 msec
    run_time = 0.0
    values = [0]*4
    GAIN = 1
    adc = Adafruit_ADS1x15.ADS1015()
    while True:
        try:
            #adcGetDataFlag.isSet():
                #break
            adcGetDataFlag.wait()
                
            start_time = time.time()
            for i in range(4):
                # Read the specified ADC channel using the previously set gain value.
                values[i] = adc.read_adc(i, gain=GAIN)

            end_time = time.time() - start_time
            run_time += end_time
            # Put adc values into queues at the sample_time
            if run_time > sample_time:
                adc0q.put(values[0])
                adc1q.put(values[1])
                adc2q.put(values[2])
                adc3q.put(values[3])

                run_time = 0.0 #reset run_time
      
            end_time = time.time() - start_time
            run_time += end_time
        except Exception as e:
            print e

#def getADC():
 #   values = [0]*4
  #  while True:
   #     print 'NOT USED'
    #    values[0] = adc0q.get()
     #   values[1] = adc1q.get()
      #  values[2] = adc2q.get()
       # values[3] = adc3q.get()
        #print(values[0],values[1],values[2],values[3])
        #time.sleep(1)
    

#Dependency: adcGetData() - puts adc values into a queue and TickAdd_AvgDistance() gets them
#calculates average distance by combining all wheel data
def TickAdd_AvgDistance(distanceQ,adc0q,adc1q,adc2q,adc3q,TickAdd_AvgDistanceFlag):
    values = [0]*4
    count = [0]*4
    tick = [0]*4
    totaltick = [0]*4
    wheel_distance = [0]*4
    while True:
        #print('................distance running')
        try:
            if TickAdd_AvgDistanceFlag.isSet():
            #    break
                values = [0]*4
                count = [0]*4
                tick = [0]*4
                totaltick = [0]*4
                wheel_distance = [0]*4

            if not adc0q.empty() and not adc1q.empty() and not adc2q.empty() and not adc3q.empty():
                values[0] = adc0q.get()
                values[1] = adc1q.get()
                values[2] = adc2q.get()
                values[3] = adc3q.get()
            #print  '2running'
                for i in range(4):
                # Basic spoke counter based on a threshold value
                # change values to 0 if above 1000 and to 1 if below 1000
                # above 1000 indicates a gap and below 1000 is a spoke
                # Count is set to 1 to show a transition from spoke to gap
                    if values[i] > 20000:
                        values[i] = 0
                        if count[i] == 1:
                            count[i] = 0
                            tick[i] += 1
                    else:
                        values[i] = 1
                        count [i] = 1
                #print('i',i,'values',values[i], 'count', count[i],'tick', tick[i])
                    totaltick[i] += tick[i]
                    tick[i] = 0
                
                    wheel_distance[i] = (totaltick[i] / 6) * wheel_size
                total_distance = (sum(wheel_distance) / len(wheel_distance))

                distanceQ.put(total_distance)
            #print  '3running'
        except Exception as e:
            print e
            return
    print 'DEAD'

###Internal testing purposes####
#headingQ = LifoQueue()
#distanceQ = LifoQueue()
#xcurrentQ = LifoQueue()
#ycurrentQ = LifoQueue()
#adc0q = Queue()
#adc1q = Queue()
#adc2q = Queue()
#adc3q = Queue()
#TickAdd_AvgDistanceFlag = threading.Event()
#adcGetDataFlag = threading.Event()

#adcGetDataThread = threading.Thread(target = adcGetData,args=(adc0q,adc1q,adc2q,adc3q,adcGetDataFlag)).start()
#TickAdd_AvgDistanceThread = threading.Thread(target = TickAdd_AvgDistance,args=(distanceQ,adc0q,adc1q,adc2q,adc3q,TickAdd_AvgDistanceFlag)).start()
#getADCThread = threading.Thread(target = getADC,args=()).start()

#testing use of Queues
#loop = 0
#while True:
#    loop += 1
#    print('que size adc',adc0q.qsize())
#    print('que size',distanceQ.qsize())
#    distance = distanceQ.get()
#    print('distance',distance)
#    time.sleep(1)
#    if loop > 10:
#        adc0q.queue.clear()
#        loop = 0
    
