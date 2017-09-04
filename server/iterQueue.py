import Queue

class IterableQueue(object):
    def __init__(self, queue = None):
        self.queue = queue
        if self.queue is None:
            self.queue = Queue.Queue()
        
    def __iter__(self):
        while not self.queue.empty():
            yield self.queue.get()
            
    def __getattr__(self, name):
        return getattr(self.queue, name)
