
import cell
import script

from Vector.vector import Vector

class Actor:
    '''
    An agent is a script
    
    Each agent has a ID, a script, and energy
    '''
    def __init__(self, agentID, here, there, direction = Vector(1,0), energy = 100, ip = 0):
        self.agentID = agentID
        self.script = script('%d.script' % agentID, ip)
        self.energy = energy
        self.here = here
        self.there = there
        self.location = cell.location
        self.direction = direction
        