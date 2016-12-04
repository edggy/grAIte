from constants import NUM_IDS
from constants import NUM_FOOD
from constants import NUM_PHEROMONES

class Cell:
    '''
    A cell is a entity at a gridpoint
    
    Cells have agent's id, food amount and pheromone amount
    
    An agent's id is a number between 0 to 2^32-1
    A cell can hold between 0 to 2^32-1 food and pheromones
    '''
    
    def __init__(self, location, actorID = None, numFood = None, numPheromone = None):
        self.actorID = int(actorID)
        self.food = int(numFood)
        self.pheromone = int(numPheromone)
        self.location = location
        
        if self.actorID >= NUM_IDS: self.actorID = NUM_IDS-1
        elif self.actorID < 0: self.actorID = 0      
        
        if self.food >= NUM_FOOD: self.food = NUM_FOOD-1
        elif self.food < 0: self.food = 0
        
        if self.pheromone >= NUM_PHEROMONES: self.pheromone = NUM_PHEROMONES-1
        elif self.pheromone < 0: self.pheromone = 0
        
    def __str__(self):
        return '(%d,%d,%d)' % (self.actorID, self.food, self.pheromone)
    
    def __repr__(self):
        return '(%d,%d,%d)' % (self.actorID, self.food, self.pheromone)