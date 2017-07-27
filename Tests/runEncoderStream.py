# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time
import csv

# Import the ADS1x15 module.
import Adafruit_ADS1x15


# Create an ADS1115 ADC (16-bit) instance.
#adc = Adafruit_ADS1x15.ADS1115()

# Or create an ADS1015 ADC (12-bit) instance.
adc = Adafruit_ADS1x15.ADS1015()

# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1

print('Writing ADS1x15 values, press Ctrl-C to quit...')
# Print nice channel column headers.
#print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
#print('-' * 37)
# Main loop.

sample = 1 #specify number of seconds to sample speed data
#wheel_size = .205 #wheel circumference in meters (meters/rotation)
wheel_size = .6726 #wheel circumference in feet (feet/rotation)
start_time = end_time = loop_time = loop_counter = 0
count = [0]*4
tick = [0]*4
avgtick = [0]*4
speed = [0]*4
reports = 0
total_distance = distance_time = 0
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    start_time=time.time()
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = adc.read_adc(i, gain=GAIN)
        # change values to 0 if above 1000 and to 1 if below 1000
        # above 1000 indicates a gap and below 1000 is a spoke
        # Count is set to 1 to show a transition from spoke to gap
        if values[i] > 1000:
            values[i] = 0
            if count[i] == 1:
                count[i] = 0
                tick[i] += 1
        else:
            values[i] = 1
            count [i] = 1
        #print('i',i,'values',values[i], 'count', count[i],'tick', tick[i])

        
        # Note you can also pass in an optional data_rate parameter that controls
        # the ADC conversion time (in samples/second). Each chip has a different
        # set of allowed data rate values, see datasheet Table 9 config register
        # DR bit values.
        #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        # Each value will be a 12 or 16 bit signed integer value depending on the
        # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    # Print the ADC values.
    #print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
    
    loop_counter += 1
    total_time = time.time() - start_time + loop_time
    if total_time > sample:
        print(tick[0],tick[1],tick[2],tick[3])
        for i in range(4):
            avgtick[i] = tick[i] / (6 * total_time)
            speed[i] = avgtick[i] * wheel_size
            tick[i] = 0
        print_output='rotat|%.2f|%.2f|%.2f|%.2f|   loop number=%d   runtime=%.4f' % \
                (avgtick[0],avgtick[1],avgtick[2],avgtick[3],loop_counter, total_time)
        print_speed='speed|%.2f|%.2f|%.2f|%.2f|' % (speed[0],speed[1],speed[2],speed[3])
        loop_time = loop_counter = 0
        reports += 1
        distance_time += total_time
        total_distance = (sum(speed) / len(speed)) * distance_time
        #text_output='%.4f,%.4f,%.4f,%.4f,%.4f' % (avgtick0,avgtick1,avgtick2,avgtick3,total_time)
        #csv_output=[avgtick0,avgtick1,avgtick2,avgtick3,total_time]
        print(print_output)
        print(print_speed)
        print(reports, distance_time, total_distance)
        #print(text_output)
        #with open('wheelspeed.txt', 'a') as fout:
         #   fout.write(text_output + '\n')
          #  fout.close
        #with open('csv_output', 'wt') as fout:
         #   csvout=csv.writer(fout)
          #  csvout.writerows(csv_output)
        #print(avgtick0,avgtick1,avgtick2,avgtick3,'loop=',loopcount,'time=',time.time() - start_time + loop_time)
        
    
    #show values of adc for each channel (0 is notch and 1 is spoke)    
    #print(values[0],values[1],values[2],values[3])
    #print(tick0,tick1,tick2,tick3)

    #print(avgtick0,avgtick1,avgtick2,avgtick3,loopcount)
    
    # Pause for half a second.
    #time.sleep(0.1)
    end_time=time.time()
    loop_time+=(end_time-start_time)
