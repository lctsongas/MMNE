import sys
from MeshNetworkUtil import MeshNetworkUtil
import time, datetime
#run this from the command module to learn how to use the
#MeshNetworkUtil program. This is not needed to run and to
#run the program, Just use MeshNetworkUtil()

server = MeshNetworkUtil(False)

def getChoice(text):
    choice = raw_input(text)
    if choice == 'y' or choice == 'Y' or choice == 'yes' or choice == 'Yes':
        return True
    else:
        return False

def sendMessage():
    msg = raw_input('  Enter data : ')
    addr = raw_input('  Enter IP : ')
    server.sendPacket(msg, addr)

def getDataFromServer():
    dataOut = server.getData()
    if dataOut == 'None':
        print '  No packets in queue'
        return None
    print '  Msg from network: ' + dataOut
    

def getPacketFromServer():
    packetOut = server.getPacket()
    if packetOut == 'None':
        print '  No packets in queue'
        return None
    print '  Packet from server: '
    print '  Destination IP: ' + packetOut.address()
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
    server.closeSocket()
    print 'bye!'

def main():
    try :
        while True:
            print ''
            options = {1 : ('send packet',sendMessage) ,
                       2 : ('retrieve whole packet',getPacketFromServer),
                       3 : ('retrieve payload only',getDataFromServer),
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
    except Exception as e:
        print(e)
        main()
    
if __name__ == "__main__":
    main()
    
