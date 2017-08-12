from collections import defaultdict
import copy
import queue

from actor import Actor
from Vector.vector import Vector
import grid
import cell
import constants

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
        numActors = len(self.actors)
        countActors = 0
        for actor in copy.copy(self.actors):
            # Run the actor
            for cell in actor.tick():
                # Iterate over the modified cells
                assert self._tick == cell.t
                newCells[cell.loc].append(cell)
                    
            # prefDests is a list of prefered destinations.  len == 1 if not moving, len == 2 if moving
            prefDests = actor.path[self._tick]
            
            for dest in prefDests:
                newLocs[dest].append(actor)
                
            actorQueue.put((len(prefDests), actor, 0))
            
        for loc, cells in newCells.iteritems():
            realCell = self.grid[loc]
            cells.append(realCell)
            
            defense = 0
            damage = 0
            for cell in cells:
                defense += cell.data[constants.DEFENSE]
                damage += cell.data[constants.DAMAGE]
                        
            # Apply damage
            actor = realCell.actor
            if actor is not None and damage > 0:
                netDamage = min(max(damage - defense, 0), 2*damage)
                actor.energy -= netDamage
                
                # Check if actor died
                if not actor:
                    self.actors.remove(actor)
                    self.usedActorIDs.remove(actor.actorID)
                    del otherActor.path[self._tick]
                    countActors += 1
                    
            def placeActor(actor, cell):
                assert self._tick == cell.t
                if cell.actor is not None:
                    self.actors.remove(cell.actor)
                cell.actor = actor
                actor.path[self._tick] = cell
                actor.here = cell
            
            if constants.OCCUPIED in realCell.data:
                if len(realCell.data[constants.OCCUPIED]) == 1:
                    for newActor, backupLoc in realCell.data[constants.OCCUPIED].iteritems():
                        placeActor(newActor, realCell)
                        countActors += 1
                        
                elif len(realCell.data[constants.OCCUPIED]) > 1:
                    for newActor, backupLoc in realCell.data[constants.OCCUPIED].iteritems():
                        if backupLoc is None:
                            placeActor(newActor, realCell)
                            countActors += 1
                        else:
                            placeActor(newActor, backupLoc)
                            countActors += 1
                    
        """stack = queue.LifoQueue()
        placedActors = {}
        
        def rewind(actor):
            '''
            Rewind the stack to remove actor
            '''
            while not stack.empty():
                tmpActor, tmpPref, tmpDests = stack.get()
                if tmpActor is not None:
                    del placedActors[tmpDests[tmpPref]]
                    actorQueue.put((len(tmpDests), tmpActor, tmpPref))
                if tmpActor == actor:
                    break  
                
        def setMove(actor, preference, dests):
            stack.put((actor, preference, dests))
            placedActors[dests[preference]] = (actor, preference, dests)            
        
        # Figure out where to move actors
        # Iterate over all of the actors again
        while not actorQueue.empty():
            priority, actor, attempts = actorQueue.get()
            dests = actor.path[self._tick]
            
            '''print len(dests)
            for cell, placedActor in placedActors.iteritems():
                if placedActor[0] is not None:
                    print '%s:%s' % (cell.loc, placedActor[0].actorID),
                else:
                    print '%s:%s' % (cell.loc, None),
            print'''
            
            if dests[0] not in placedActors:
                # Try to place actor in prefered dest
                setMove(actor, 0, dests)
            #elif attempts >= 1:
            #    # Go to backup dest
            #    stack.put((actor, 1, dests))
            #    placedActors[dests[1]] = (actor, 1, dests)                
            else:
                # There's an actor already there
                otherActor, preference, otherDests = placedActors[dests[0]]
                
                # Case 1:  I didn't move
                '''if len(dests) == 1:
                    otherActor, preference, otherDests = placedActors[dests[-1]]
                    
                    # Assert that they have another move
                    assert len(otherDests) > 1
                    
                    # rewind and take spot
                    rewind(otherActor)
                    setMove(actor, -1, dests)  '''                  
                
                # Case 2:  I moved, they didn't
                #   Try to go to my backup spot
                
                if len(otherDests) == 1 or len(dests) == 1:
                    if dests[-1] not in placedActors:
                        # Backup is not taken
                        setMove(actor, -1, dests)
                    else:
                        # Backup is taken
                        otherActor, preference, otherDests = placedActors[dests[-1]]
                        
                        # Check if it is a no-move cell
                        if otherActor is None:
                            # Two other actors tried to move here
                            setMove(actor, -1, dests)
                        
                        else:
                            # Rewind to remove other actor
                            # Assert that they have another move
                            assert len(otherDests) > 1
                            rewind(otherActor)
                            setMove(actor, -1, dests)
                        
                # Case 3:  We both moved
                else:
                    # Rewind
                    rewind(otherActor)
                    
                    # set it so noone can take this location
                    setMove(None, 0, [dests[0]])
                    setMove(actor, -1, dests)
                    
        assert numActors == len(placedActors)
        # Actually move actors
        for cell, placedActor in placedActors.iteritems():
            actor = placedActor[0]
            nextCell = self.grid[cell]
            actor.path[self._tick] = nextCell
            actor.here = nextCell
            if nextCell.actor is not None:
                # Someone was here who was not supposed to
                # Maybe somebody walked into a split
                self.actors.remove(nextCell.actor)
            nextCell.actor = actor"""
        
        assert numActors == countActors
        
        return self
    
    def newActor(self, agent, cell, direction = 'E', energy = 100, ip = None, name = 0, parent = None, actorData = None):
        cell = self.grid[cell]
        if cell.actor is None:
            actor = Actor(self.nextID(), agent, cell, self, direction, energy, ip, name, parent, actorData)
            cell.actor = actor
            self.actors.add(actor)
            return actor
        return None
    
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
    w.newActor(agent, (0, 0, 0))
    w.newActor(agent1, (0, 3, 0))
    
    radius = 7
    
    sumTimePAnt = 0
    
    start = time.time()
    for i in xrange(1000):
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
        