
import cell
import script

class Actor:
    '''
    An agent is a script
    
    Each agent has a ID, a script, and energy
    '''
    def __init__(self, agentID, cell, direction = -1, energy = 100, ip = 0):
        self.agentID = agentID
        self.script = script('%d.script' % agentID, ip)
        self.energy = energy
        self.cell = cell
        self.location = cell.location
        self.direction = direction