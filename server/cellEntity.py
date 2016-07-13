
class CellEntity:
    '''
    An abstract entity that resides in a cell in the world
    
    May be an agent, resouce, pheromone, etc...
    '''
    
    def __init__(self, pos):
        self._pos = pos
        
    def tick(self):
        pass
    
    def getPos(self):
        return self._pos
    
    def getName(self):
        return ''
    
    