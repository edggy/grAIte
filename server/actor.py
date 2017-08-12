
import copy
import hashlib

import cell
import script
import constants
from Vector.vector import Vector

sha256 = lambda x: int(hashlib.new('sha256', x).hexdigest(), 16)

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
        
        self.path = {}
        
    @property
    def ip(self):
        return self.script.ip
    
    @property
    def there(self):
        return self.here + self.direction
        
    def __str__(self):
        return '%s: %s' % (self.actorID, self.name)
    
    def __repr__(self):
        try:
            parID = self.parent.actorID
        except AttributeError:
            parID = None

        return 'ID=%s,Name=%s,Agent=%s,Parent=%s,ip=%s,Energy=%s,Here=%s,There=%s' \
         % (self.actorID, 
            self.name, 
            self.agent.agentID, 
            parID, 
            self.ip, 
            self.energy, 
            self.here.loc, 
            self.there.loc)
        
    def __hash__(self):
        return self.actorID     
    
    def __eq__(self, other):
        try:
            return self.actorID == other.actorID
        except AttributeError:
            return False
    
    def __nonzero__(self):
        '''
        Returns True iff actor is alive
        '''
        return self.energy > 0
    
    def randint(self, num1, num2):
        '''
        Deterministically get an x s.t. num1 <= x <= num2
        '''
        pid = None
        try:
            pid = self.parent.actorID
        except AttributeError:
            pass
        
        otherStuff = ()
        try:
            otherActor = self.there.actor
            otherStuff = (otherActor.actorID, otherActor.energy, otherActor.direction, otherActor.name)
        except AttributeError:
            pass        
        
        stuff = (self.actorID, pid, self.agent.agentID, self.energy, self.direction, self.name, self.here.food, self.here.pheromone, self.there.food, self.there.pheromone) + otherStuff
        string = ('%s' * len(stuff)) % stuff
        higher = max(num1, num2)
        lower = min(num1, num2)
        return int((sha256(string) % (higher - lower + 1)) + lower)
        
    def tick(self):
        '''
        Run the next line of the script
        
        Return a set of modified cells
        '''

        return self.script.tick(self)