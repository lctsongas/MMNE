import sys
from MeshNetworkUtil import MeshNetworkUtil
import time, datetime
#run this from the command module to learn how to use the
#MeshNetworkUtil program. This is not needed to run and to
#run the program, Just use MeshNetworkUtil()

server = MeshNetworkUtil()
server.startListening()
#server.startAPMonitor()
def getChoice(text):
    choice = raw_input(text)
    if choice == 'y' or choice == 'Y' or choice == 'yes' or choice == 'Yes':
        return True
    else:
        return False

def sendMessage():
    print ''
    options = {1 : ('Generic',server.sendGeneric) ,
               2 : ('AP is all Okay',server.sendOK),
               3 : ('Low Power client AP',server.sendLowPower),
               4 : ('Move AP to x, y',server.sendMoveTo),
               5 : ('Send server my x, y',server.sendCoords),
               6 : ('Ask AP for x, y',server.pollCoords),
               7 : ('Stop AP from extending coverage',server.stopAPTooFar) ,
               8 : ('AP needs help going farther',server.askHelp),
               9 : ('Stop AP',server.stopAPNow),
               10: ('Stop ALL APs',server.stopAPAll),
               11: ('Arp' , server.arpTable)
    }
    for option in options:
        print str(option) + ' = ' + options[option][0]
    num = input('Select option: ')
    if num == 1: # Generic
        options[num][1]()
    elif num == 2: # OK
        options[num][1]()
    elif num == 3: # Low Power
        options[num][1]()
    elif num == 4: # MoveTo
        ip = raw_input('Enter IP : ')
        x = raw_input('  Enter x : ')
        y = raw_input('  Enter y : ')
        options[num][1](ip,x,y)
    elif num == 5: # Send Coords
        xcurr = raw_input('  Enter current x : ')
        ycurr = raw_input('  Enter current y : ')
        xdest = raw_input('  Enter destination x : ')
        ydest = raw_input('  Enter destination y : ')
        options[num][1](xcurr, ycurr, xdest, ydest)
    elif num == 6: # Poll coords
        ip = raw_input('Enter IP : ')
        options[num][1](ip)
    elif num == 7: # stop AP from moving too far
        ip = raw_input('Enter IP : ')
        options[num][1](ip)
    elif num == 8: # Ask others for help
        options[num][1]()
    elif num == 9: # Stop single AP
        ip = raw_input('Enter IP : ')
        options[num][1](ip)
    elif num == 10: # Stop all APs
        print str(options[num][1]())
    else:
        print 'Unknown option'
    

def getInfo():
    print ''
    options = {1 : ('Arp Table',server.arpTable),
               2 : ('Who is (arp)',server.arpIP),
               3 : ('Arp and IP map', server.getArpAndIP),
               4 : ('Get lowest signal', server.getLowestSignal)
    }
    for option in options:
        print str(option) + ' = ' + options[option][0]
    num = input('Select option: ')
    if num == 1: # Return whole arp table
        print options[num][1]()
    elif num == 2: # Get mac of ip
        ip = raw_input('Enter IP : ')
        print options[num][1](ip)
    elif num == 3: # map ip to mac
        print options[num][1]()
    elif num == 4: # Lowest AP signal
        print options[num][1]()
    else:
        print 'Unknown option'

def getPacketFromServer():
    packetOut = server.getPacket()
    if packetOut == None:
        print '  No packets in queue'
        return None
    print '  Packet from server: '
    print '  Destination IP: ' + packetOut.address()
    print '  Source IP: ' + packetOut.srcAddress()
    print '  Message Type: ' + str(packetOut.messageType())
    print '  Flags: ' + str(packetOut.flags())
    print '  Timestamp: ' + datetime.datetime.fromtimestamp(packetOut.timestamp()).strftime('%Y-%m-%d %H:%M:%S')
    print '  Payload size: ' + str(packetOut.payloadLength())
    print '  Payload: ' + packetOut.getPayload()

def debugOnOff():
    if server.debug:
        print '  Debug is On'
    else:
        print '  Debug is Off'
    if getChoice('  Toggle debugging? (Y/N): '):
        server.toggleDebug()
        
def portMap():
    print '  log of devices that sent packets to this device'
    print '  {IP Address : Port Num}'
    server.meshPortMap()

def close():
    server.close()
    print 'bye!'

def main():
    try :
        while True:
            print 'MAIN: LOWEST SIGNAL = ' + str(server.getLowestSignal())
            print ''
            options = {1 : ('send packet',sendMessage) ,
                       2 : ('retrieve whole packet',getPacketFromServer),
                       3 : ('get network info',getInfo),
                       4 : ('toggleDebug',debugOnOff),
                       5 : ('print port map',portMap),
                       6 : ('exit', close)
            }
            for option in options:
                print str(option) + ' = ' + options[option][0]
            num = input('Select option: ')
            options[num][1]()
            time.sleep(0.5)
            if options[num][0] == 'exit':
                exit()
            print 'MAIN: END OF LOOP'
    except Exception as e:
        print(e)
        main()
    
if __name__ == "__main__":
    main()
