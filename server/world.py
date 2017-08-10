from collections import defaultdict

import queue

from actor import Actor
from Vector.vector import Vector
import grid
import cell

class World:
    '''
    This is the world where all of the agents exist at a specific instace in time
    
    Each world is an infinite grid
    '''
    
    def __init__(self, initGrid = None, actors = None, tick = 0, worldFile = None):
        
        self.usedActorIDs = set()
        
        self.lastID = 0
        
        # Load a world form a file if we are given one
        if worldFile is not None:
            self.load(worldFile) 
        else:
        
            # Grid object to store the cells
            self.grid = initGrid
            
            if self.grid is None:
                self.grid = grid.Grid(dimensions=3, cellGenerator=cell.Cell, cleanupMax=10)
            
            # This is a set of Actors
            self.actors = actors
            
            if self.actors is None:
                self.actors = set()
                
            for actor in self.actors:
                self.usedActorIDs.add(actor.actorID)
            
            # Keep track of what tick we are on
            self._tick = tick
            
            if self._tick is None:
                self._tick = 0
        
    def nextID(self):
        # TODO: Maybe make random IDs and allow reuse?
        while self.lastID in self.usedActorIDs:
            self.lastID += 1
            
        self.usedActorIDs.add(self.lastID)
        
        return self.lastID
            
    def tick(self):
        '''
        Calculates the next world from this one
        '''
        # Increase the tick count by 1
        self._tick += 1        
        
        # Keep track of the cells that are changed
        newCells = defaultdict(list)
        
        # Keep track of where agents want to move, cells -> agents that want to move there
        newLocs = defaultdict(list)
        actorQueue = queue.PriorityQueue()
        
        # Iterate over all of the actors
        for actor in self.actors:
            # Run the actor
            for cell in actor.tick():
                # Iterate over the modified cells
                newCells[cell.loc].append(cell)
                    
            # prefDests is a list of prefered destinations.  len == 1 if not moving, len == 2 if moving
            prefDests = actor.cells[self._tick]
            
            for dest in prefDests:
                newLocs[dest].append(actor)
                
            actorQueue.put((len(prefDests), actor, 0))
            
        for loc, cells in newCells.iteritems():
            realCell = self.grid[loc]
            cells.appand(realCell)
            
            defense = 0
            damage = 0
            for cell in cells:
                defense += cell.data[constants.DEFENSE]
                damage += cell.data[constants.DAMAGE]
                        
            # Apply damage
            actor = realCell.actor
            if actor is not None:
                netDamage = max(damage - defense, 0)
                actor.energy -= netDamage
                
                # Check if actor died
                if not actor:
                    self.actors.remove(actor)
                    self.usedActorIDs.remove(actor.actorID)
                    
        stack = queue.LifoQueue()
        placedActors = {}
        
        # Figure out where to move actors
        # Iterate over all of the actors again
        while not actorQueue.empty():
            priority, actor, attempts = actorQueue.get()
            dests = actor.cells[self._tick]
            
            if dests[0] not in placedActors:
                # Try to place actor in prefered dest
                stack.put((actor, 0, dests))
                placedActors[dests[0]] = (actor, 0, dests)
            elif attempts >= 1:
                # Go to backup dest
                stack.put((actor, 1, dests))
                placedActors[dests[1]] = (actor, 1, dests)                
            else:
                # There's an actor already there
                otherActor, preference, otherDests = placedActors[dests[0]]
                if len(otherDests) == 1:
                    # They have no other options
                    # Go to backup dest
                    stack.put((actor, 1, dests))
                    placedActors[dests[1]] = (actor, 1, dests)
                else:
                    # They have another option
                    # Rewind and set it so noone can take this location
                    while not stack.empty():
                        tmpActor, tmpPref, tmpDests = stack.get()
                        del placedActors[tmpDests[tmpPref]]
                        actorQueue.put((len(tmpDests), tmpActor, tmpPref))
                        if tmpActor == otherActor:
                            break
                    placedActors[dests[0]] = (None, 0, [dests[0]])
                    
                    # Go to backup dest
                    stack.put((actor, 1, dests))
                    placedActors[dests[1]] = (actor, 1, dests)
                    
        # Actually move actors
        for cell, actor in placedActors.iteritems():
            nextCell = self.grid[cell].next
            actor.cells[self._tick] = nextCell
            nextCell.actor = actor
        
        return self
    
    def newActor(self, agent, cell, direction = 'E', energy = 100, ip = None, name = 0, parent = None, actorData = None):
        cell = self.grid[cell]
        actor = Actor(self.nextID(), agent, cell, self, direction, energy, ip, name, parent, actorData)
        cell.actor = actor
        return actor
    
    def load(self, stream):
        '''
        Load a world from a stream
        
        :param stream: A byte stream with the .read(.) attribute
        '''
        pass
    
    def save(self, stream):
        '''
        Save the world to a stream
        
        :param stream: A byte stream with the .write(.) attribute
        '''
        pass        
    
    
if __name__ == '__main__':  
    from agent import Agent
    
    agent = Agent(0)
    
    w = World()
    w.newActor(agent, (0, 0, 0))
    w.tick()
    
    print agent.actors