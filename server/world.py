from collections import defaultdict
import copy
import queue
import threading

from actor import Actor, PastActor
from Vector.vector import Vector
import grid
import cell
import constants
import iterQueue

class World:
    '''
    This is the world where all of the agents exist at a specific instace in time
    
    Each world is an infinite grid
    '''
    
    def __init__(self, initGrid = None, actors = None, tick = 0, worldFile = None):
        
        self.usedActorIDs = set()
        
        self.lastID = 1
        
        self.lock = threading.Lock()
        
        # Load a world form a file if we are given one
        if worldFile is not None:
            self.load(worldFile) 
        else:
        
            # Grid object to store the cells
            self.grid = initGrid
            
            if self.grid is None:
                self.grid = grid.Grid(dimensions=3, cellGenerator=cell.Cell, cleanupMax=10)
            
            # This is a dict of Actors
            self.actors = actors
            
            if self.actors is None:
                self.actors = {}
            
            # Keep track of all actors ever
            self.actorHistory = {}
                
            for actorID in self.actors:
                self.usedActorIDs.add(actorID)
                self.actorHistory[actorID] = self.actors[actorID]
            
            # Keep track of what tick we are on
            self._tick = tick
            
            if self._tick is None:
                self._tick = 0
                
            self.verbose = False
        
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
        
        getReal = lambda loc: self.grid[loc]
        
        if self.verbose:
            print 'Getting Lock'
        with self.lock:
            if self.verbose:
                print 'Locked'
            # Increase the tick count by 1
            self._tick += 1        
            
            # Keep track of the cells that are changed
            newCells = defaultdict(list)
            
            # Keep track of where agents want to move, cells -> agents that want to move there
            newLocs = defaultdict(list)
            
            # Keep track of prefered locations
            prefLocs = defaultdict(list)
            
            actorQueue = iterQueue.IterableQueue(queue.PriorityQueue())
            
            # Iterate over all of the actors
            #numActors = len(self.actors)
            countActors = 0
            for actorID, actor in copy.copy(self.actors).iteritems():
                if self.verbose:
                    print 'Ticking actorID: %s' % actorID
                # Run the actor
                for cell in actor.tick():
                    # Iterate over the modified cells
                    assert self._tick == cell.t
                    newCells[cell.loc].append(cell)
  
            # Merge cells together
            for loc, cells in newCells.iteritems():
                if self.verbose:
                    print 'At loc: %s' % loc
                
                realCell = getReal(loc)
                cells.append(realCell)
                
                defense = 0
                damage = 0
                dfood = 0
                dpher = 0
                for cell in cells:
                    defense += cell.data[constants.DEFENSE]
                    damage += cell.data[constants.DAMAGE]
                    dfood += cell.food - realCell.food
                    dpher += cell.pheromone - realCell.pheromone
                
                realCell.data[constants.DEFENSE] = defense
                realCell.data[constants.DAMAGE] = damage
                realCell.food += dfood
                realCell.pheromone += dpher
                            
                # Apply damage
                actor = realCell.prev.actor
                if actor is not None:
                    if damage > 0:
                        netDamage = min(max(damage - defense, 0), 2*damage)
                        actor.energy -= netDamage
                    
                    # Check if actor died or is dead
                    if not actor:
                        #del self.actors[actor.actorID]
                        #self.usedActorIDs.remove(actor.actorID)
                        if self.verbose:
                            print 'ActorID %s died' % actor.actorID
                            
                        self.deleteActor(actor)
                        #del otherActor.path[self._tick]
                        countActors += 1
                        
            # Request prefered dests and add to queue
            for actorID, actor in self.actors.iteritems():
                # prefDests is a list of prefered destinations.  len == 1 if not moving, len == 2 if moving
                prefDests = actor.path[self._tick]
                
                for dest in prefDests:
                    if dest is not None:
                        newLocs[getReal(dest)].append(actor)
                    
                prefLocs[getReal(prefDests[0])].append(actor)
                    
                actorQueue.put((len(prefDests), actor))            
                        
            def placeActor(actor, cell):
                if cell is None:
                    self.deleteActor(actor)
                    return
                    
                assert self._tick == cell.t
                
                cell.actor = actor
                actor.path[self._tick] = cell
                actor.here = cell
                
                
            for priority, actor in actorQueue:
                if not actor:
                    # Actor died
                    for dest in actor.path[self._tick]:
                        
                        prefLocs[dest].remove(actor)
                        newLocs[dest].remove(actor)
                    continue
                
                prefDests = actor.path[self._tick]
                
                if len(prefDests) == 1:
                    # This actor wants to stay
                    dest = prefDests[0]
                    for otherActor in newLocs[dest]:
                        if otherActor != actor:
                            # Check that other actors have somewhere to move
                            assert len(otherActor.path[self._tick]) > 1
                            otherActor.path[self._tick].remove(dest)
                     
                    if self.verbose:   
                        print 'Placing ActorID: %s\tStaying' % actor.actorID
                    placeActor(actor, dest)
                    countActors += 1
                        
                elif len(prefDests) > 1:
                    # This actor wants to move
                    dest = prefDests[0]
                    backup = prefDests[-1]
                    
                    if len(prefLocs[dest]) == 1:
                        # I am the only one who wants to move here
                        if self.verbose:
                            print 'Placing ActorID: %s\tMoving no collision' % actor.actorID
                        placeActor(actor, dest)
                        countActors += 1
                    elif len(prefLocs[dest]) > 1:
                        allNew = True
                        for otherActor in prefLocs[dest]:
                            if otherActor is not actor and otherActor.path[self._tick][-1] is not None:
                                allNew = False
                                
                        if allNew:
                            # New ants are trying to split here... I have priority
                            if self.verbose:
                                print 'Placing ActorID: %s\tMoving with collision of new actors' % actor.actorID
                            placeActor(actor, dest)
                            countActors += 1                            
                        else:
                            # More than one actor prefers to move here, so I will go to my backup
                            if self.verbose:
                                print 'Placing ActorID: %s\tStaying with collision' % actor.actorID
                            placeActor(actor, backup)
                            countActors += 1
            
            #assert len(self.actors) == countActors
            
            return self
    
    def newActor(self, agent, cell, direction = 'E', energy = 100, ip = None, name = 0, parent = None, actorData = None):
        cell = self.grid[cell]
        if cell.actor is None:
            actor = Actor(self.nextID(), agent, cell, self, direction, energy, ip, name, parent, actorData)
            cell.actor = actor
            self.actors[actor.actorID] = actor
            self.actorHistory[actor.actorID] = actor
            actor.path[self._tick] = [cell, None]
            if self.verbose:
                print 'ActorID %s created' % actor.actorID    
            return actor
        return None
    
    def deleteActor(self, actor):
        if len(actor.path) == 1:
            # Just created, don't add to history
            del self.actorHistory[actor.actorID]
            self.lastID = min(actor.actorID, self.lastID)
        del self.actors[actor.actorID]
        self.usedActorIDs.remove(actor.actorID)
        if self.verbose:
            print 'ActorID %s deleted' % actor.actorID        
        
    
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
    
    import time
    from agent import Agent
    
    def printWorld(world, t, start, end):
        data = w.grid.data
        
        scale = 1
        width  = (end[0] - start[0]+1)
        height = (end[1] - start[1]+1)
        
        
        '''
        6
        5
        4
        3
        2
        1
        0123456789
        
        '''
        #locToVal = lambda loc: [(height-(loc.y-start[1]+1))*(width+1)+((loc.x-start[0]))]
        
        #result = ([' ']*(width) + ['\n'])*(height)
        result = []
        for y in xrange(end[1], start[1]-1, -1):
            for x in xrange(start[0], end[0]+1):
                loc = Vector(x,y,t)
                if loc in data and data[loc].actor is not None:
                    actor = data[loc].actor
                    #for i in locToVal(loc):
                    result += [constants.DIRECTIONS_VEC_SYM[actor.direction]]
                        #result[i] = constants.DIRECTIONS_VEC_SYM[actor.direction]
                    #result += constants.DIRECTIONS_VEC_SYM[actor.direction]
                else:
                    #result += '`'
                    result += [' ']
            #result += '\n'
            
        gridStr = ('+-'*width+'+\n'+'|%s'*width + '|\n')*height + '+-'*width+'+\n'
        
        return gridStr % tuple(result)
                    
    
    agent = Agent(0)
    agent1 = Agent(1)
    
    w = World()
    act1 = w.newActor(agent, (0, 0, 0))
    act2 = w.newActor(agent1, (0, 3, 0))
    
    radius = 7
    
    sumTimePAnt = 0
    
    start = time.time()
    for i in xrange(10):
        tickStart = time.time()
        w.tick()
        tickEnd = time.time()
        print 'Tick: %s' % w._tick
        print 'Ants: %d' % len(w.actors)
        deltaTime = tickEnd - tickStart
        deltaTimePAnt = (deltaTime)/len(w.actors)
        sumTimePAnt += deltaTimePAnt
        print 'Time Taken: %f' % (deltaTime)
        print 'Time Taken per Ant: %f' % (deltaTimePAnt)
        print 'Average Time Taken per Ant: %f' % (sumTimePAnt/w._tick)
        #print w.grid.data
        #print agent.actors
        print printWorld(w, w._tick, (-radius,-radius), (radius, radius))
        
    past1 = PastActor(act1, 2)
    print past1