import socket, threading, sys
import traceback, os
import time, math
from Queue import Queue
#from MeshUDPPacket import MeshPacket

class MeshNetworkUtil:
    HOST = ''   # Listen to all 
    PORT = 7331 # Random port
    DONE = False
    isServer = True
    debug = False
    clientPorts = {'127.0.0.1' : 7331 }
    
    # Datagram (udp) socket
    def __init__(self, debugOn = False):
        """Open socket for listening"""
        if debugOn: #Turn on debugging, off by default
            self.debug = True
        self.mbox = Queue()
        try :
            self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.clientPorts[socket.gethostbyname(socket.gethostname())] = self.PORT
        except socket.error, msg :
            print 'Ignore error if this is the 2nd instance'
            print '[' + str(msg[0]) + '] : ' + msg[1]
        # Bind socket to local host and port
        try:
            self.socketUDP.bind((self.HOST, self.PORT))
            if self.debug:
                print 'Socket bind complete'
        except socket.error , msg:
            print '[' + str(msg[0]) + '] : ' + msg[1]
            self.isServer = False
        if self.isServer:
            self.startListening()
 
    #now keep listening with the client
    def startListening(self):
        """Create new thread for UDP"""
        threading.Thread(target=self.listenUDP).start()
        self.queueEvent = threading.Event()
        self.queueEvent.clear()

    def listenUDP(self):
        """Listen for UDP traffic"""
        while True:
            # receive data from client (data, addr)
            d = self.socketUDP.recvfrom(20480)
            data = d[0]
            addr = d[1]
            if not data: 
                break
     
            #reply = 'OK...' + data
     
            #self.socketUDP.sendto(reply , addr)
            if data == 'STOP':
                self.closeSocket()
            if self.debug:
                print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
            self.clientPorts[addr[0]] = addr[1]
            self.mbox.put(data)

    def closeSocket(self):
        self.DONE = True
        self.socketUDP.close()

    def sendData(self, data, host):
        if self.debug:
            print 'sendData( data = ' + data + ', host = ' + host + ' )' 
        try :
            #Set the whole string
            self.socketUDP.sendto(data, (host, self.PORT))
            self.startListening()
            #d = self.socketUDP.recvfrom(20480)
            #reply = d[0]
            #addr = d[1]
        except socket.error, msg:
            print '[' + str(msg[0]) + '] : ' + msg[1]
            self.closeSocket()

    def getData(self):
        try :
            data = self.mbox.get(False)
            if self.debug:
                print 'getData() -> ' + data
            return data
        except :
            print 'Queue empty'
            return 'None'
