
import cell
import script

class Actor:
    '''
    An Actor is a "ant"
    
    Each Actor has a ID, a script, and energy, name
    and an instruction pointer (IP)
    '''
    def __init__(self, agentID, cell, direction = None, energy = 100, ip = 0, name = 0, parentID = None):
        # agentID's are unique
        self.agentID = agentID
        self.parentID = parentID
        self.script = script('%d.script' % agentID, ip)
        self.energy = energy
        self.cell = cell
        self.location = cell.location
        self.direction = direction
        self.ip = ip
        self.name = name