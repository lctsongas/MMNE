import multiprocessing as mp
from ProcessManager import MMNEProcess, ProcessManager
import time
def spam(myDouble, myList, spamQ):
    myList.append(myDouble)
    spamQ.put(myList)

def eggs(eggsQ):
    time.sleep(5)
    eggsQ.put('I\'m done cooking eggs!')

def bacon(myString, baconQ):
    x = len(myString)
    baconQ.put(myString + ' is ' + str(x) + ' chars long!')

if __name__ == '__main__':
    #Create ProcessManager object
    pManager = ProcessManager()
    #Create Process string IDs
    spamID = 'SPAM'
    eggsID = 'EGGS'
    baconID = 'tasty'
    spamOut=mp.Queue()
    eggsOut=mp.Queue()
    stringyOut=mp.Queue()
    #Start processes
    groceryList = ['milk', 'cheese', 'and for dessert:']
    #Create spam process
    pSpam = mp.Process(target=spam, args = (3.14, groceryList, spamOut))
    pSpam.start()
    #pManager.startProcess(spamID, spam, (3.14, groceryList), (spamOut,))
    #Create eggs process
    pEggs = mp.Process(target=eggs, args=(eggsOut,))
    pEggs.start()
    #pManager.startProcess(eggsID, eggs, (), (eggsOut,))
    #Create bacon process
    pBacon = mp.Process(target=bacon, args=('my stringy string',stringyOut))
    pBacon.start()
    #pManager.startProcess(baconID, bacon, ('my stringy string',), (stringyOut,))
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
            try:
                spamResult = spamOut.get(True, 0.1)
            except Exception as e:
                continue
            
        #Check if eggs is done
        if eggsResult != None and not eggsDone:
            processesDone+=1
            print 'Eggs done! Returned: ' + str(eggsResult)
            eggsDone = True
        elif not eggsDone:
            try:
                eggsResult = eggsOut.get(True, 0.1)
            except Exception as e:
                continue
            
        #Check if bacon is done
        if baconResult != None and not baconDone:
            processesDone+=1
            print 'Bacon done! Returned: ' + str(baconResult)
            baconDone = True
        elif not baconDone:
            try:
                baconResult = stringyOut.get(True, 0.1)
            except Exception as e:
                continue
            #print pManager.getProcess(baconID).is_alive()

        print 'waiting...'
        time.sleep(1)


