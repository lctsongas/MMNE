import os, time
import threading, Queue

class WorkerThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self):
        super(WorkerThread, self).__init__()
        self.stopRequest = threading.Event()

    def run(self):
        """overwrite this"""
        #does nothing except tell you to overwrtie this
        #run function
        print 'I DO NOTHING'
        return None

    def join(self, timeout=None):
        self.stoprequest.set()
        super(WorkerThread, self).join(timeout)
