import os

import script
import constants

class Agent:
    '''
    An agent is a script in charge of it's actors
    
    Each agent has a ID, a script, and a dict of actors -> actorData
    '''
    def __init__(self, agentID, scriptName = None, actors = None):
        self.agentID = agentID
        
        if scriptName is None:
            
            self.scriptName = os.path.join(constants.SCRIPT_PATH, '%d.script' % agentID)
            
        if actors is None:
            self.actors = {}
    
    def __str__(self):
        actorIDs = [i.actorID for i in self.actors]
        return '%s: %s\n%s' % (self.agentID, self.scriptName, actorIDs)
    
    def __repr__(self):
        actorRepr = '\n'.join([repr(i) for i in self.actors])
        return '%s: %s\n%s' % (self.agentID, self.scriptName, actorRepr)
        