import multiprocessing as mp
from ProcessManager import MMNEProcess, ProcessManager
import time
def spam(myDouble, myList):
    myList.append(myDouble)
    return myList

def eggs():
    time.sleep(5)
    return 'I\'m done cooking eggs!'

def bacon(myString):
    x = len(myString)
    return myString + ' is ' + str(x) + ' chars long!'

if __name__ == '__main__':
    #Create ProcessManager object
    pManager = ProcessManager()
    #Create Process string IDs
    spamID = 'SPAM'
    eggsID = 'EGGS'
    baconID = 'tasty'
    #Start processes
    groceryList = ['milk', 'cheese', 'and for dessert:']
    #Create spam process
    pManager.startProcess(spamID, spam, (3.14, groceryList))
    #Create eggs process
    pManager.startProcess(eggsID, eggs)
    #Create bacon process
    pManager.startProcess(baconID, bacon, ('my stringy string',))
    #While loop control vars
    spamResult = None
    eggsResult = None
    baconResult = None
    baconDone=eggsDone=spamDone = False
    processesDone = 0
    while processesDone != 3:
        #Check if spam is done
        if spamResult != None and not spamDone:
            processesDone+=1
            print 'Spam done! Returned: ' + str(spamResult)
            spamDone = True
        elif not spamDone:
            spamResult = pManager.getResult(spamID)
            
        #Check if eggs is done
        if eggsResult != None and not eggsDone:
            processesDone+=1
            print 'Eggs done! Returned: ' + str(eggsResult)
            eggsDone = True
        elif not eggsDone:
            eggsResult = pManager.getResult(eggsID)
            
        #Check if bacon is done
        if baconResult != None and not baconDone:
            processesDone+=1
            print 'Bacon done! Returned: ' + str(baconResult)
            baconDone = True
        elif not baconDone:
            baconResult = pManager.getResult(baconID)

        print 'waiting...'


