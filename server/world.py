
import agent

class World:
    '''
    This is the world where all of the agents exist at a specific instace in time
    
    Each world is an infinite grid
    '''
    
    def __init__(self, grid = None, agents = None, tick = 0):
        
        # Since the world will be sparse, we use a dict to store only the important locations
        # This is a dict of (x,y) -> Cell
        self.grid = grid
        
        # This is a dict of actortID -> Actor
        self.agents = agents
        
        # Keep track of what tick we are on
        self.tick = tick
        
        # Load a world form a file if we are given one
        if worldFile is not None:
            self.load(worldFile) 
            
    def tick(self):
        '''
        Calculates the next world from this one
        '''
        
        # Create a new grid to store all entities in the next tick
        newGrid = {}
        
        for pos in self.grid:
            
            cell = self.grid[pos]
            
            # Get the current cellEntity
            agent = self.agents[cell.agentID]
            
            # Increase the entity by a tick
            newAgent = agent.tick()
            
            # Store them in the new grid
            oldCell = self.grid[newAgent.pos]
            newGrid[newAgent.pos] = newCellEntity.agentID
            
        # Increase the tick count by 1
        self.tick += 1
        
        # replace the old grid with the new one
        self.grid = newGrid
        
        return self
    

        
        