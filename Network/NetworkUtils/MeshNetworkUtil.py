import socket, threading, sys
import traceback, os, math
from time import time
from Queue import Queue

class MeshNetworkUtil:
    HOST = ''   # Listen to all 
    PORT = 7331 # Random port
    DONE = False # Closes socket when done
    isServer = True # Keeps multiple Utils from using same socket
    debug = False # Debugging off (default) / on
    isListening = False # Determines if listening thread is already running
    clientPorts = {'127.0.0.1' : 7331 }
    
    # Datagram (udp) socket
    def __init__(self, debugOn = False):
        """Open socket for listening"""
        if debugOn: #Turn on debugging, off by default
            self.debug = True
        self.mbox = Queue()
        # Create socket on local host
        try :
            self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socketUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.clientPorts[socket.gethostbyname(socket.gethostname())] = self.PORT
        except socket.error, msg :
            print 'Ignore error if this is the 2nd instance'
            print '[' + str(msg[0]) + '] : ' + msg[1]
        # Bind socket to local host and port
        try:
            self.socketUDP.bind((self.HOST, self.PORT))
            if self.debug:
                print  '    Socket bind complete'
        except socket.error , msg:
            print '[' + str(msg[0]) + '] : ' + msg[1]
            self.isServer = False
        if self.isServer:
            self.startListening()
 
    #now keep listening with the client
    def startListening(self):
        """Create new thread for UDP"""
        if not self.isListening:
            self.isListening = True
            threading.Thread(target=self.listenUDP).start()
            self.queueEvent = threading.Event()
            self.queueEvent.clear()

    def listenUDP(self):
        """Listen for UDP traffic"""
        while True:
            # receive data from client (data, addr)
            d = self.socketUDP.recvfrom(20480)
            packet = MeshPacket()
            packet.decode(d[0])
            if not packet.getPayload():
                self.isListening = False
                break
            if self.debug:
                print  '    time: ' + str(packet.timestamp())
                print  '    address: ' + packet.address()
                print  '    payload: ' + packet.getPayload()
            self.clientPorts[packet.address()] = d[1][1]
            self.mbox.put(packet.getPacket())

    def closeSocket(self):
        self.DONE = True
        self.socketUDP.close()

    def sendPacket(self, data, host, msgType = 1, flags = 0):
        """sends UDP packet to broadcast"""
        if self.debug:
            print  '    sendData( data = ' + data + ', host = ' + host + ' )'
        # Setup UDP packet contents
        packet = MeshPacket()
        packet.encode(host, data, msgType, flags)
        try :
            #Set the whole string
            self.socketUDP.sendto(packet.getPacket(), ('<broadcast>', self.PORT))
            self.startListening()
        except socket.error, msg:
            print '[' + str(msg[0]) + '] : ' + msg[1]
            self.closeSocket()
            
    def getData(self):
        """Dequeues the next element sent to host"""
        try :
            dequeued = self.mbox.get(False)
            packet = MeshPacket()
            packet.decode(dequeued)
            data = packet.getPayload()
            if self.debug:
                print  '    getData() -> ' + data
            return data
        except :
            if self.debug:
                print  '    Queue empty'
            return 'None'

    def getPacket(self):
        """Dequeues a packet object if it exists"""
        try :
            dequeued = self.mbox.get(False)
            packet = MeshPacket()
            packet.decode(dequeued)
            if self.debug:
                print  '    getPacket() -> ' + str(packet.payloadLength()) + ' bytes'
            return packet
        except :
            if self.debug:
                print  '    Queue empty'
            return 'None'

    def meshPortMap(self):
        for key in self.clientPorts:
            print '  ' + key + ' : '  + str(self.clientPorts[key])
            
    def getIP(ifname='wlan0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])

    def toggleDebug(self):
        self.debug = not self.debug
        print 'debug = ' + str(self.debug)
        


HEADER_SIZE = 16

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
        #           Dest. IP Address        #
        #MsgType #   Padding       #  Flags #
        #             Timestamp             #
        #    DataLen      #    Padding      #
        #####################################
        ip1,ip2,ip3,ip4 = destIP.split('.')
        header[0] = int(ip1)
        header[1] = int(ip2)
        header[2] = int(ip3)
        header[3] = int(ip4)

        header[4] = msgType
        
        header[5] = 0
        header[6] = 0
        
        header[7] = flags
        
        header[8] = ((timestamp >> 24) & 255)
        header[9] = ((timestamp >> 16) & 255)
        header[10] = ((timestamp >> 8) & 255)
        header[11] = (timestamp & 255)

        header[12] = ((len(payload) >> 8) & 255)
        header[13] = (len(payload) & 255)
        
        header[14] = 0
        header[15] = 0
        
        self.header = header
        self.payload = payload

    def decode(self, byteStream):
        """Decode the UDP packet."""
        self.header = bytearray(byteStream[:HEADER_SIZE])
        self.payload = byteStream[HEADER_SIZE:]
    
    def address(self):
        """Return UDP dest. address."""
        ipAddr = ''
        ipAddr += str(self.header[0])
        ipAddr += "."
        ipAddr += str(self.header[1])
        ipAddr += "."
        ipAddr += str(self.header[2])
        ipAddr += "."
        ipAddr += str(self.header[3])
        return ipAddr
    
    def messageType(self):
        """Return UDP type"""
        #msgType == 1 : Generic UDP Packet
        return int(self.header[4])

    def flags(self):
        """Return UDP flags"""
        return int(self.header[7])

    def payloadLength(self):
        """Return payload size (in bytes)"""
        return (self.header[12] << 8) | self.header[13]
    
    def timestamp(self):
        """Return timestamp."""
        timestamp = self.header[8] << 24 | self.header[9] << 16 | self.header[10] << 8 | self.header[11]
        return int(timestamp)
    
    def payloadLength(self):
        """Return payload type."""
        dataLen = int((self.header[12] << 8))
        dataLen |= int(self.header[13])
        return dataLen
    
    def getPayload(self):
        """Return payload."""
        return self.payload
        
    def getPacket(self):
        """Return RTP packet."""
        return self.header + self.payload

