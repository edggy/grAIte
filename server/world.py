
class World:
    '''
    This is the world where all of the agents exist at a specific instace in time
    
    Each world is an infinite grid
    '''
    
    def __init__(self, grid = None, actors = None, tick = 0):
        
        # Since the world will be sparse, we use a dict to store only the important locations
        # This is a dict of (x,y) -> Cell
        self.grid = grid
        
        if self.grid is None:
            self.grid = {}
        
        # This is a dict of actorID -> Actor
        self.actors = actors
        
        if self.actors is None:
            self.actors = {}
        
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
        
        # Iterate over all of the actors
        for actor in self.actors:
            
            # Run the actor
            newHere, newThere = actor.tick()
            
            # Agent will return modifications
            newGrid[newHere.location] = newHere
            newGrid[newThere.location] = newThere
            
            # TODO: deal with conflicts
            
        # Increase the tick count by 1
        self.tick += 1
        
        # replace the old grid with the new one
        self.grid = newGrid
        
        return self
    

        
        