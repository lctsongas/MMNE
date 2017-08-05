

class ClientInfo:

    def __init__(self, mac, ip, signal = -1, status = False):
        self.MAC = mac
        self.IP = ip
        self.signal = signal
        self.status = status

    def getIP(self):
        return self.IP

    def getMAC(self):
        return self.MAC

    def getSignal(self):
        return self.signal

    def getStatus(self):
        return self.status

    
