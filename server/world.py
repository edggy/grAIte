
import agent

class World:
    '''
    This is the world where all of the agents exist at a specific instace in time
    '''
    
    def __init__(self, worldFile = None):
        
        # Since the world will be sparse, we use a dict to store only the important locations
        # This is a dict of positions: name of entity
        self._grid = {}
        
        # This is a dict of the name of the entities to their coorosponding objects
        self._entities = {}
        
        # Keep track of what tick we are on
        self._tick = 0
        
        # Load a world form a file if we are given one
        if worldFile is not None:
            self.load(worldFile)
            
    def getTick(self):
        '''
        Gets the current tick of the world
        
        @return - The current tick of this world
        '''
        return self._tick
        
    def save(self, worldFile):
        '''
        Saves the world to a file
        
        @param - worldFile, the name of the file to save to
        '''
        with open(worldFile, 'w') as f:
            # First write the tick we are on
            f.write('%d' % self._tick)
            
            # Then write each nonempty cell on its own line
            for pos in self._grid:
                f.write('%s\t%s\t%s\n' % (pos[0], pos[1], repr(self._grid[pos])))
    
    def load(self, worldFile):
        '''
        Loads a world from a file
        
        @param - worldFile, the name of the file to save to
        '''        
        with open(worldFile, 'r') as f:
            
            # The first line is the tick number
            self._tick = int(f.readline())
            
            # Each other line contains a position and an agent
            for line in f:
                
                # Seperate the line into xPos, yPos and agent
                toks = line.split('\t', 2)
                pos = (int(toks[0]), int(toks[1]))
                self._grid[pos] = agent.Agent(toks[2])
                
    def tick(self):
        '''
        Calculates the next world from this one
        '''
        
        # Create a new grid to store all entities in the next tick
        newGrid = {}
        
        for pos in self._grid:
            
            # Get the current cellEntity
            curCellEntity = self._entities[self._grid[pos]]
            
            # Increase the entity by a tick
            curCellEntity.tick()
            
            # Store them in the new grid
            newGrid[curCellEntity.getPos()] = curCellEntity.getName()
            
        # Increase the tick count by 1
        self._tick += 1
        
        # replace the old grid with the new one
        self._grid = newGrid
    

        
        