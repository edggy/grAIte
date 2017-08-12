import Vector.vector as vector
from ast import literal_eval
import copy

class Cell(object):
    '''
    A cell in a grid, has references to it's neighbors
    '''
    def __init__(self, loc, grid, data = None):
        self.data = data
        self.loc = vector.Vector(*loc)
        self.grid = grid
        
    def __str__(self):
        return '%s: %s' % (self.loc, self.data)
        
    def __repr__(self):
        return '%r:%r' % (self.loc, self.data)    
    
    def __hash__(self):
        return hash(self.loc)
    
    def __eq__(self, other):
        try:
            return self.loc == other.loc
        except AttributeError:
            return self.loc == other
    
    def __nonzero__(self):
        return self.data is not None  
    
    def __add__(self, vec):
        vec = vector.Vector(*vec)
        return self.grid[self.loc + vec]  
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __getattr__(self, attr):
        return getattr(self.data, attr)
    
    def __iter__(self):
        # Used to unpack cells into vectors for keys in grid[key]
        index = 0
        for i in self.loc:
            yield i
    
    def __copy__(self):
        return type(self)(self.loc, self.grid, self.data)
    
    def __deepcopy__(self, memo):  
        return type(self)(copy.deepcopy(self.loc), self.grid, copy.deepcopy(self.data))
    
    def move(self, vec):
        '''
        Returns the cell in the location here + vec
        '''
        return self + vec

class Cell2D(Cell):
    
    @property
    def east(self):
        return self + vector.I(0, self.grid.dim)
    
    @property
    def west(self):
        return self + vector.I(0, self.grid.dim, -1)   
    
    @property
    def north(self):
        return self + vector.I(1, self.grid.dim)
    
    @property
    def south(self):
        return self + vector.I(1, self.grid.dim, -1)    
    
    @property
    def x(self):
        return self.loc[0]
    
    @property
    def y(self):
        return self.loc[1]    
    
    @property
    def xy(self):
        return vector.Vector(self.loc[0], self.loc[1])
    

class Cell3D(Cell2D):
    @property
    def up(self):
        return self + vector.I(2, self.grid.dim)
    
    @property
    def down(self):
        return self + vector.I(2, self.grid.dim, -1)   
    
    @property
    def z(self):
        return self.loc[2]    
    
class Cell3Dt(Cell2D):
    @property
    def next(self):
        return self + vector.I(2, self.grid.dim)
    
    @property
    def prev(self):
        return self + vector.I(2, self.grid.dim, -1)   
    
    @property
    def t(self):
        return self.loc[2]    

class Grid(object):
    '''
    A grid class that given a location returns a cell for that location
    '''
    def __init__(self, dimensions = 2, cellGenerator = Cell, cleanupMax = 10):
        self.dim = dimensions
        self.data = {}
        self.cellGenerator = cellGenerator
        self.cleanupMax = cleanupMax
        self.cleanupData = 0
    
    def __getitem__(self, key):
        '''
        key should be a tuple or vector
        '''
        
        key = vector.Vector(*key)
        
        if len(key) != self.dim:
            raise KeyError('Key is of wrong dimension')
        
        try:
            return self.data[key]
        except KeyError:
            newCell = self.cellGenerator(key, self)
            self.data[key] = newCell
            return newCell
    
    def __setitem__(self, key, value):
        if len(key) != self.dim:
            raise KeyError('Key is of wrong dimension')
        
        key = vector.Vector(*key)
        
        try:
            self.data[key].data = value
        except KeyError:
            self.data[key] = self.cellGenerator(key, self, value)
            
        self.cleanup()
            
    def __delitem__(self, key):
        key = vector.Vector(*key)
        del self.data[key]
        self.cleanup()
            
    def __iter__(self):
        self.cleanup(True)
        for key in self.data:
            yield self.data[key]
            
    def __copy__(self):
        self.cleanup(True)
        clone = type(self)(self.dim, self.cellGenerator)
        for key, cell in self.data.iteritems():
            cellClone = copy.copy(cell)
            cellClone.grid = clone
            clone.data[key] = cellClone
            
        return clone
    
    def __deepcopy__(self, memo):
        self.cleanup(True)
        clone = type(self)(self.dim, self.cellGenerator)
        for key, cell in self.data.iteritems():
            cellClone = copy.deepcopy(cell)
            cellClone.grid = clone
            clone.data[key] = cellClone
            
        return clone
            
    def cleanup(self, force = False, isEmpty = None):
        if empty is None:
            empty = lambda x: not bool(x)
            
        self.cleanupData += 1
        if force or self.cleanupData > self.cleanupMax:
            self.cleanupData = 0
            for cell in self:
                if empty(cell):
                    del self[cell.loc]
    
    def load(self, stream, cellGenerator = None):
        if cellGenerator is not None:
            self.cellGenerator = cellGenerator
        
        def readtochar(stream, endchar = '\n'):
            line = ''
            char = ' '
            while char not in endchar:
                char = stream.read(1)
                line += char
            return line
            
        # Get the dimensions and number of elements off of the first line
        count, self.dim = map(int, readtochar(stream).split())
        
        for i in xrange(count):
            # Get the key, value pair off of each line
            key, value = readtochar(stream)[-1].split(':')
            key = map(int, key[1:-1].split(','))
            value = literal_eval(value)
            self.data[key] = self.cellGenerator(key, self, value)
        
    
    def save(self, stream):
        self.cleanup(True)
        stream.write('%d %d\n' % (len(self.data)), self.dim)
        for key in self.data:
            stream.write('%r\n' % (self.data[key],))
    
if __name__ == '__main__':
    g = Grid(3)
    g[1,2,3] = 15
    
    print g[1,2,3]
    
    g3d = Grid(3, Cell3D)
    
    print g3d[1,1,1]
    print g3d[1,1,1].up
    print g3d[1,1,1] is g3d[1,1,1].up.down
    print g3d[1,1,1] is g3d[1,1,1].up.up.down.down.west.east.west.east
    
    print repr(g3d[1,1,1])
    
    g3d[1,1,1] = 'apples'
    
    print g3d[1,1,1][1:4]
    
    