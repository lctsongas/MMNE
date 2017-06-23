import sys
from MeshNetworkUtil import MeshNetworkUtil

#run this from the command module to learn how to use the
#MeshNetworkUtil program. This is not needed to run and to
#run the program, Just use MeshNetworkUtil()

if __name__ == "__main__":
    server = MeshNetworkUtil(True)
    while True:
        msg = raw_input('Enter message : ')
        addr = raw_input('Enter IP : ')
        server.sendData(msg, addr)
        choice = raw_input('get data from queue? (Y/N)')
        if choice == 'y' or choice == 'Y' or choice == 'yes' or choice == 'Yes':
            dataOut = server.getData()
            print 'Msg from network: ' + dataOut
        
