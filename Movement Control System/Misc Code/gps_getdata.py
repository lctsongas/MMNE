#working
#gives latitude and longitude in a while loop

from gps import *
import time

i=0
lat=lon=0.0
session = gps(mode=WATCH_ENABLE)
try:
    while True:
        start_time = time.time()
        report = session.next()
        if report['class'] == 'DEVICE':
            session.close()
            session = gps(mode=WATCH_ENABLE)
        if report[u'class'] == u'TPV':
            lon = report[u'lon']
            lat = report[u'lat']
        i+=1
        end_time = time.time() - start_time
        print('loop: %d, time: %.3f |lat: %f|lon: %f' % (i,end_time,lat,lon))
        #time.sleep(.25)
except StopIteration:
    print("GPSD has terminated")
