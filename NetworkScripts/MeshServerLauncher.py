import sys
from MeshNetworkUtil import MeshNetworkUtil

#run this from the command module to learn how to use the
#MeshNetworkUtil program. This is not needed to run and to
#run the program, Just 

if __name__ == "__main__":
    server = MeshNetworkUtil()
    while True:
        msg = raw_input('Enter message : ')
        addr = raw_input('Enter IP : ')
        server.sendData(msg, addr)
        
        
