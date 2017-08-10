
import copy
import hashlib

import cell
import script
import constants
from Vector.vector import Vector

sha256 = lambda x: int(hashlib.new('sha256', x).digest(), 16)

class Actor:
    '''
    An Actor is a "ant"
    
    Each Actor has a ID, a script, and energy, name
    and an instruction pointer (IP)
    '''
    def __init__(self, actorID, agent, cell, world, direction = 'E', energy = 100, ip = None, name = 0, parent = None, actorData = None):
        # actorID's are unique
        self.actorID = actorID
        
        # Actor that created this actor
        self.parent = parent
        
        # The controlling agent
        self.agent = agent
        
        # Add to agent's list
        self.agent.actors[self] = actorData
        
        # The script to run
        self.script = script.Script(self.agent.scriptName, ip, constants.CACHE_SIZE)
            
        # Amount of energy
        self.energy = energy
        
        # Current location
        self.here = cell
        
        self.world = world
        
        # Current direction
        if direction in tuple('NSEW'):
            direction = constants.DIRECTIONS_VEC_CHAR[direction]
        elif direction in (0,1,2,3):
            direction = constants.DIRECTIONS_VEC_NUM[direction]
        self.direction = Vector(*direction)
        
        # This agent's name
        self.name = name
        
        self.status = None
        
        self.cells = {}
        
    @property
    def ip(self):
        return self.script.ip
    
    @property
    def there(self):
        self.there = self.here + self.direction
        
    def __repr__(self):
        return '%s: %s' % (self.actorID, self.name)
    
    def __str__(self):
        return 'ID = %s\nName = %s\nAgent = %s\nParent = %s\nip = %s\nEnergy = %s\nHere = %s\nThere = %s' \
         % (self.actorID, self.name, self.agent.agentID, self.parent, self.ip, self.energy, self.here, self.there)
        
    def __hash__(self):
        return self.actorID     
    
    def __eq__(self, other):
        return self.actorID == other.actorID
    
    def __nonzero__(self):
        '''
        Returns True iff actor is alive
        '''
        return self.energy > 0
    
    def randint(num1, num2):
        '''
        Deterministically get an x s.t. num1 <= x < num2
        '''
        stuff = (self.actorID, self.parent.actorID, self.agent.agentID, self.energy, self.direction, self.name, self.here.food, self.here.pheromone)
        string = ('%s' * len(stuff)) % stuff
        higher = max(num1, num2)
        lower = min(num1, num2)
        return (sha256(string) % (higher - lower)) + lower
        
    def tick(self):
        '''
        Run the next line of the script
        
        Return a set of modified cells
        '''
        
        # return (newHere, newThere)
        return self.script.tick()