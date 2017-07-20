import multiprocessing as mp

class ProcessManager:

    def __init__(self):
        self.pDict = {}

    def startProcess(self, ID, function, params=()):
        """ID is string to reference the process"""
        self.pDict[ID] = MMNEProcess(function, params)

    def getResult(self, ID, stopTime=0.1):
        """Get result, times out after stopTime seconds"""
        self.checkPID(ID)
        return self.pDict[ID].getResult(stopTime)

    def rerunProcess(self, ID):
        self.checkPID(ID)
        function = self.pDict[ID].getFunction()
        params = self.pDict[ID].getParams()
        self.pDict[ID].close()
        self.pDict[ID] = MMNEProcess(function, params)
        
    def checkPID(self,ID):
        if not ID in self.pDict:
            raise Exception('Process ID does not exist!')
        

class MMNEProcess:

    def __init__(self, function, params=()):
        self.psPool = mp.Pool()
        self.output_q = mp.Queue()
        self.function = function
        self.params = params
        self.process = self.psPool.apply_async(function, args=params)
        
    def getResult(self,stopTime=0.1):
        try:
            result = self.process.get(timeout=stopTime)
            return result
        except mp.TimeoutError:
            return None

    def close(self):
        self.psPool.close()

    def getFunction(self):
        return self.function

    def getParams(self):
        return self.params
        
