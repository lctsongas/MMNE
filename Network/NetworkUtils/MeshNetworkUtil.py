import socket, sys
import threading as tr
import traceback, os, math, re
from time import time
from Queue import *
import subprocess

#Priority and packet flags defined below
PQ_DEFAULT = 10         #Default priority in queue
PQ_EMERGCY = 1          #Emergency packets get highest priority

                        # A2S = Flag sent from AP to Server
                        # S2A = Flag sent from Server to AP
                        # A2A = Flag sent from AP to AP
FG_NONE      = 0        # Undefined: A2S/S2A/A2A, Flag for general purpose packets
FG_OKAY      = 1        # OK       : A2S, ready and waiting
FG_LOWPWR    = 2        # Low Power: A2S, losing client signal, AP running low pwr subroutine
FG_MOVETO    = 3        # Move to  : S2A, x,y to go to
FG_MOVING    = 4        # Moving   : A2S, also sends current x,y and dest x,y
FG_WHEREUAT  = 5        # Poll x,y : S2A, ask AP for his current location
FG_TOOFAR    = 7        # AP far   : S2A, Stops AP so it doesn't go out of range
FG_ASKHELP   = 8        # Ask help : A2A & A2S, Asks other nodes for help extending coverage
FG_YOUSTOP   = 99       # Stop move: S2A, Halts single robot from moving
FG_ALLSTOP   = 100      # Stop move: S2A, Halts all robots form moving

class MeshNetworkUtil:
    
    #Module flags and fields defined below
    HOST         = ''       # Listen to all 
    PORT         = 7331     # Random port
    debug        = False    # Debugging off (default) / on
    stopRx = tr.Event()     # Stops/resets packet receiving thread if set
    stopAP = tr.Event()     # Stops/resets AP listening thread if set
    stopArp= tr.Event()     # Stops/resets AP
    clientPorts  = {'127.0.0.1' : 7331 }
    
    clients      = {}       # Maps client to power level
    arpDict = None
    lowestSignal = 0
    lowestSignalOld = -1
    
    # Datagram (udp) socket
    def __init__(self, debugOn = False):
        """Initialize MeshUtil object"""
        if debugOn: #Turn on debugging, off by default
            self.debug = True
            
        self.mbox = PriorityQueue()
        
        # Create socket on local host
        try :
            self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socketUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.clientPorts[socket.gethostbyname(socket.gethostname())] = self.PORT
        except socket.error, msg :
            print 'ERROR: 2 MeshNetworkUtil modules running!'
            print 'Only 1 allowed per device'
            print '[' + str(msg[0]) + '] : ' + msg[1]
            exit 
        # Bind socket to local host and port
        try:
            self.socketUDP.bind((self.HOST, self.PORT))
            if self.debug:
                print  '    Socket bind complete'
        except socket.error , msg:
            print '[' + str(msg[0]) + '] : ' + msg[1]

        # Create threading objects
        self.rxThread = tr.Thread(target=self.listenUDP)
        self.apThread = tr.Thread(target=self.monitorAP)
        self.arpThread= tr.Thread(target=self.getArpAndIP)
 
    #now keep listening with the client
    def startListening(self):
        """Create new thread for UDP"""
        if not self.rxThread.isAlive():
            self.stopRx.clear()
            self.rxThread.start()

    def startAPMonitor(self):
        """Starts thread for motoring client power"""
        if not self.apThread.isAlive():
            self.stopAP.clear()
            self.apThread.start()

    def startArping(self):
        if not self.arpThread.isAlive():
            self.stopArp.clear()
            self.arpThread.start()
            
    def close(self):
        """Stop the MeshUtil"""
        self.socketUDP.close()
        if not self.stopAP.isSet():
            self.stopAP.set()
            self.apThread = tr.Thread(target=self.startAPMonitor)
        if not self.stopRx.isSet():
            self.stopRx.set()
            self.rxThread = tr.Thread(target=self.listenUDP)

    def sendPacket(self, data, dest, msgType = 1, flags = FG_NONE, server = False):
        """sends UDP packet to broadcast"""
        if self.debug:
            print  '    sendData( data = ' + data + ', host = ' + dest + ' )'
        # Setup UDP packet contents
        packet = MeshPacket()
        packet.encode(dest, data, msgType, flags)
        if server:
            packet.setSrcAddress('10.0.0.1')
        try :
            #Set the whole string
            self.socketUDP.sendto(packet.getPacket(), (dest, self.PORT))
            #self.startListening()
        except socket.error, msg:
            print '[' + str(msg[0]) + '] : ' + msg[1]
            self.close()


    def listenUDP(self):
        """Listen for UDP traffic"""
        while True:
            # receive data from client (data, addr)
            d = self.socketUDP.recvfrom(20480)
            packet = MeshPacket()
            packet.decode(d[0])
            #print 'MeshUtil: got something!'
            if self.debug:
                print  '    time: ' + str(packet.timestamp())
                print  '    address: ' + packet.address()
                print  '    payload: ' + packet.getPayload()
            self.clientPorts[packet.address()] = d[1][1]
            
            #Set priority of packet in queue here
            priority = PQ_DEFAULT # Set default priority
            if packet.flags() == FG_YOUSTOP or packet.flags() == FG_ALLSTOP:
                #Emergency stop priority set
                priority = PQ_EMERGCY
            self.mbox.put((priority , packet.getPacket()))

    def monitorAP(self):
        pollRate = 5
        signalThreshold = 70
        oldTime = time()
        while True:
            #Poll client poer every pollRate seconds
            newTime = time()
            elapsed = newTime - oldTime
            if elapsed < pollRate:
                #continue
                oldTime = time()
            #Grab iwTable shell command output
            iwDump = self.iwTable()
            iwList = iwDump.split()
            #Move previous lowest signal to old
            self.lowestSignalOld = self.lowestSignal
            if len(iwList) == 0:
                #No clients connected, no signal then
                self.lowestSignal = 0
                #continue
            #Regex for MAC addresses
            macRegEx = '..:..:..:..:..:..'
            #Get all instances of MAC on AP
            macList = re.findall(macRegEx,iwDump)
            index = 1
            
            for mac in macList:
                
                signal = abs(int(iwList[27*index]))
                self.clients[mac] = signal
                if signal > self.lowestSignal:
                    tmpValue = self.lowestSignal
                    self.lowestSignal = signal
                    self.lowestSignalOld = tmpValue

    def getLowestSignal(self):
        return self.lowestSignal

    
    def getData(self):
        """Dequeues the next element sent to host"""
        #try :
        dequeued = self.mbox.get(False)
        packet = MeshPacket()
        packet.decode(dequeued[1])
        data = packet.getPayload()
        if self.debug:
            print  '    getData() -> ' + data
        return data


    def getPacket(self):
        """Dequeues a packet object if it exists"""
        try :
            dequeued = self.mbox.get(False)
            packet = MeshPacket()
            packet.decode(dequeued[1])
            if self.debug:
                print  '    getPacket() -> ' + str(packet.payloadLength()) + ' bytes'
            return packet
        except :
            if self.debug:
                print  '    Queue empty'
            return None

    def arpTable(self):
        return subprocess.check_output(["arp","-a"])

    def iwTable(self):
        return subprocess.check_output(['iw', 'dev', 'wlan1', 'station', 'dump'])

    def arpIP(self, ipaddr):
        arptable = self.arpTable()
        arplist = arptable.split('\n')
        #print 'seraching for: ' + ipaddr
        for line in arplist:
            if line == None:
                continue
            foundip = re.search('\d+\.\d+\.\d+\.\d+', line).group(0)
            if foundip == ipaddr:
                #print 'found: ' + foundip
                mac = re.search('..:..:..:..:..:..',line)
                if mac != None:
                    return mac.group(0)
                else:
                    break
 
        return None

    def getArpAndIP(self):
        while True:
            arptable = self.arpTable()
            arplist = arptable.split('\n')
            retDict = {}
            for line in arplist:
                #print 'arp table iteration'
                if line == None:
                    continue
                #print 'arp searching'
                foundip = re.search('\d+\.\d+\.\d+\.\d+', line)
                foundmac = re.search('..:..:..:..:..:..',line)
                #print 'arp search done'
                if foundmac != None and foundip != None:
                        retDict[foundip.group(0)] = foundmac.group(0)
            #print 'arp done'
            self.arpDict = retDict

    def getArpDict(self):
        return self.arpDict

    def meshPortMap(self):
        for key in self.clientPorts:
            print '  ' + key + ' : '  + str(self.clientPorts[key])

    def printPacket(self, packet):
        retval  = 'Source IP: ' + packet.srcAddress() + '\n'
        retval += '  Dest IP: ' + packet.address() + '\n'
        retval += '  MsgType: ' + packet.messageType() + '\n'
        retval += '    Flags: ' + packet.flags() + '\n'
        retval += 'Timestamp: ' + packet.timestamp() + '\n'
        retval += '     Data: ' + packet.getPayload()
        return retval

    def toggleDebug(self):
        self.debug = not self.debug
        print 'debug = ' + str(self.debug)

    # A2S = Flag sent from AP to Server
    # S2A = Flag sent from Server to AP
    # A2A = Flag sent from AP to AP
    #See top of class for info
    # Undefined: A2S/S2A/A2A, Flag for general purpose packets
    def sendGeneric(self, dest='<broadcast>', data='Test'):
        self.sendPacket(data, dest, flags=FG_NONE)
                        
    #See top of class for info
    # OK       : A2S, ready and waiting
    def sendOK(self, dest='10.0.0.2'):
        self.sendPacket('', dest, flags=FG_OKAY)

    #See top of class for info
    # Low Power: A2S, losing client signal, AP running low pwr subroutine
    def sendLowPower(self, dest='10.0.0.2'):
        self.sendPacket('', dest, flags=FG_LOWPWR)

    #See top of class for info
    # Move to  : S2A, x,y to go to
    def sendMoveTo(self, dest, x, y):
        data = str(x) + ', ' + str(y)
        self.sendPacket(data, dest, flags=FG_MOVETO, server=True)
        
    #See top of class for info
    # Moving   : A2S, also sends current x,y and dest x,y
    def sendCoords(self, x_current, y_current, x_destination, y_destination, dest='10.0.0.2'):
        data_current = str(x_current) + ', ' + str(y_current)
        data_destination = str(x_destination) + ', ' + str(y_destination)
        data = data_current + ', ' + data_destination
        self.sendPacket(data, dest, flags=FG_MOVING)

    #See top of class for info
    # Poll x,y : S2A, ask AP for his current location
    def pollCoords(self, dest):
        self.sendPacket('', dest, flags=FG_WHEREUAT, server=True)
        
    #See top of class for info
    # AP far   : S2A, Stops AP so it doesn't go out of range
    def stopAPTooFar(self, dest):
        self.sendPacket('',dest,flags=FG_TOOFAR, server=True)

    #See top of class for info
    # Ask help : A2A & A2S, Asks other nodes for help extending coverage
    def askHelp(self):
        self.sendPacket('','<broadcast>',flags=FG_ALLSTOP)
        
    #See top of class for info
    # Stop move: S2A, Halts single robot from moving
    def stopAPNow(self, dest):
        self.sendPacket('',dest,flags=FG_YOUSTOP, server=True)
        
    #See top of class for info
    # Stop move: S2A, Halts all robots form moving
    def stopAPAll(self):
        self.sendPacket('','<broadcast>',flags=FG_ALLSTOP, server=True)

    

    
        
    
HEADER_SIZE = 20

class MeshPacket:   
    header = bytearray(HEADER_SIZE)
    
    def __init__(self):
        pass
        
    def encode(self, destIP, payload, msgType, flags):
        """Encode the RTP packet with header fields and payload."""
        timestamp = int(time())
        header = bytearray(HEADER_SIZE)
        #########HEADER FORMAT###############
        #0          1          2          3 #
        #01234567 89012345 67890123 45678901#
        #            Src IP Address         #
        #           Dest. IP Address        #
        #MsgType #   Padding       #  Flags #
        #             Timestamp             #
        #    DataLen      #    Padding      #
        #####################################
        dIP1,dIP2,dIP3,dIP4 = destIP.split('.')
        try:
            
            macShell = subprocess.check_output(["cat","/sys/class/net/eth0/address"])
            macBytes = macShell.split(':')
            header[0] = 10
            header[1] = int(macBytes[3],16)
            header[2] = int(macBytes[4],16)
            header[3] = int(macBytes[5],16)
        except Exception as e:
            header[0] = 10
            header[1] = 0
            header[2] = 0
            header[3] = 2
        
        header[4] = int(dIP1)
        header[5] = int(dIP2)
        header[6] = int(dIP3)
        header[7] = int(dIP4)

        header[8] = msgType
        
        header[9] = 0
        header[10] = 0
        
        header[11] = flags
        
        header[12] = ((timestamp >> 24) & 255)
        header[13] = ((timestamp >> 16) & 255)
        header[14] = ((timestamp >> 8) & 255)
        header[15] = (timestamp & 255)

        header[16] = ((len(payload) >> 8) & 255)
        header[17] = (len(payload) & 255)
        
        header[18] = 0
        header[19] = 0
        
        self.header = header
        self.payload = payload

    def decode(self, byteStream):
        """Decode the UDP packet."""
        self.header = bytearray(byteStream[:HEADER_SIZE])
        self.payload = byteStream[HEADER_SIZE:]
    def srcAddress(self):
        """Return who sent the packet"""
        ipAddr = ''
        ipAddr += str(self.header[0])
        ipAddr += "."
        ipAddr += str(self.header[1])
        ipAddr += "."
        ipAddr += str(self.header[2])
        ipAddr += "."
        ipAddr += str(self.header[3])
        return ipAddr

    def setSrcAddress(self,ip):
        ipBytes = ip.split('.')
        self.header[0] = int(ipBytes[0])
        self.header[1] = int(ipBytes[1])
        self.header[2] = int(ipBytes[2])
        self.header[3] = int(ipBytes[3])
    
    def address(self):
        """Return UDP dest. address."""
        ipAddr = ''
        ipAddr += str(self.header[4])
        ipAddr += "."
        ipAddr += str(self.header[5])
        ipAddr += "."
        ipAddr += str(self.header[6])
        ipAddr += "."
        ipAddr += str(self.header[7])
        return ipAddr
    
    def messageType(self):
        """Return UDP type"""
        #msgType == 1 : Generic UDP Packet
        return int(self.header[8])

    def flags(self):
        """Return UDP flags"""
        return int(self.header[11])

    def payloadLength(self):
        """Return payload size (in bytes)"""
        return (self.header[16] << 8) | self.header[17]
    
    def timestamp(self):
        """Return timestamp."""
        timestamp = self.header[12] << 24 | self.header[13] << 16 | self.header[14] << 8 | self.header[15]
        return int(timestamp)
    
    def getPayload(self):
        """Return payload."""
        return self.payload
        
    def getPacket(self):
        """Return RTP packet."""
        return self.header + self.payload


