from collections import defaultdict
import copy

from constants import NUM_IDS
from constants import NUM_FOOD
from constants import NUM_PHEROMONES

from grid import Cell3Dt
import Vector.vector as vector

def setInBound(value, lower, upper):
    if value is None or value < lower:
        return lower            
    if value >= upper:
        return upper-1
    return value

class Cell(Cell3Dt):
    '''
    A cell is a entity at a gridpoint
    
    Cells have agent's id, food amount and pheromone amount
    
    An agent's id is a number between 0 to 2^32-1
    A cell can hold between 0 to 2^32-1 food and pheromones
    '''
    
    def __init__(self, location, grid, actor = None, numFood = None, numPheromone = None):
        super(Cell, self).__init__(location, grid)
        
        self.actor = actor
        self.data = defaultdict(int)
        
        try:
            self.food = setInBound(int(numFood), 0, NUM_FOOD)
        except TypeError:
            self.food = 0
            
        try:
            self.pheromone = setInBound(int(numPheromone), 0, NUM_PHEROMONES)
        except TypeError:
            self.pheromone = 0            
        
        # Get the cell below ours's food and pheromones
        if self.loc[2] > 0 and (numFood is None or numPheromone is None):
            below = self.grid[self.loc - vector.I(2, 3, 1)]
            if numFood is None:
                self.food = below.food
            if numPheromone is None:
                self.pheromone = below.pheromone 
            #if actor is None:
            #    self.actor = below.actor
        
    def __str__(self):
        return '%s: (%s, %s, %s)' % (self.loc, self.food, self.pheromone, self.actor)
        
    def __repr__(self):
        return ''.join(('loc=%r,food=%r,pheromone=%r,actor=(%s)' % (self.loc, self.food, self.pheromone, self.actor)).split())
    
    def __nonzero__(self):
        return self.actor is not None or self.food > 0 or self.pheromone > 0

    def __copy__(self):
        return type(self)(self.loc, self.grid, self.actor, self.food, self.pheromone)
    
    def __deepcopy__(self, memo):  
        return type(self)(copy.deepcopy(self.loc), self.grid, copy.deepcopy(self.actor), copy.deepcopy(self.food), copy.deepcopy(self.pheromone))