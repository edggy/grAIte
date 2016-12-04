import math as m
import copy
import operator

class Vector:
    def __init__(self, *vec):
        self._val = list(vec)
        
    def __str__(self):
        return str(self._val)
    
    def __repr__(self):
        return repr(self._val)   
    
    def __hash__(self):
        return hash(tuple(self._val))
        
    def __op__(self, op, *other):
        return Vector(*[op(*i) for i in zip(self._val, *other)])
    
    def __rop__(self, op, *other):
        l = other + (self._val,)
        return Vector(*[op(*i) for i in zip(*l)])
    
    def __iop__(self, op, *other):
        self = Vector(*[op(*i) for i in zip(self._val, *other)])
        return self
        
    def __add__(self, other):
        return self.__op__(operator.add, other)
    
    def __radd__(self, other):
        return self.__rop__(operator.add, other)
    
    def __iadd__(self, other):
        return self.__iop__(operator.add, other)
    
    def __mul__(self, other):
        try:
            return sum(self.__op__(operator.mul, other))
        except TypeError:
            pass
        
        return self.__op__(operator.mul, (other,) * len(self))
    
    def __rmul__(self, other):
        try:
            return sum(self.__rop__(operator.mul, other))
        except TypeError:
            pass
        
        return self.__op__(operator.mul, (other,) * len(self))
    
    def __imul__(self, other):
        return self.__iop__(operator.mul, (other,) * len(self))    
    
    def __floordiv__(self, other):
        return self.__op__(operator.floordiv, other)
    
    def __mod__(self, other):
        return self.__op__(operator.mod, other)
        
    def __abs__(self):
        return m.sqrt(self*self)
    
    def __divmod__(self, other): return self.__op__(operator.divmod, other)
    def __pow__(self, other, modulo = None): return self.__op__(operator.pow, other, modulo)
    def __lshift__(self, other): 
        pass 
    def __rshift__(self, other):
        pass
    def __and__(self, other): return self._op_(operator.and_, other)
    def __xor__(self, other): return self._op_(operator.xor_, other)
    def __or__(self, other): return self._op_(operator.or_, other)     
    
    def __div__(self, other): return self._op_(operator.div, other)
    def __truediv__(self, other): return self._op_(operator.truediv, other)
    
    '''object.__radd__(self, other)
object.__rsub__(self, other)
object.__rmul__(self, other)
object.__rdiv__(self, other)
object.__rtruediv__(self, other)
object.__rfloordiv__(self, other)
object.__rmod__(self, other)
object.__rdivmod__(self, other)
object.__rpow__(self, other)
object.__rlshift__(self, other)
object.__rrshift__(self, other)¶
object.__rand__(self, other)
object.__rxor__(self, other)
object.__ror__(self, other)
    '''
    
    def __eq__(self, other):
        for (i,j) in zip(self._val, other):
            if i != j: return False
        return True
    
    def __ne__(self, other):
        for (i,j) in zip(self._val, other):
            if i != j: return True
        return False   
    
    def __gt__(self, other):
        return self.length2() > Vector(other).length2()
    
    def __ge__(self, other):
        return self.length2() >= Vector(other).length2()    
    
    def __lt__(self, other):
        return self.length2() < Vector(other).length2()
    
    def __le__(self, other):
        return self.length2() <= Vector(other).length2()    
    
    def __len__(self):
        return len(self._val)
    
    def __getitem__(self, key):
        return self._val[key]
    
    def __missing__(self, key):
        raise IndexError()
    
    def __setitem__(self, key, value):
        self._val[key] = value
        
    def __iter__(self):
        return Static_Iter(self._val)
    
    def __reversed__(self):
        return Static_Iter(self._val, step = -1)
    
    def length2(self):
        return self*self
        

class Static_Iter:
    def __init__(self, tup, start = 0, end = None, step = 1):
        if end is None:
            end = len(tup)
        self.i = 0
        self.n = tuple([tup[i] for i in range(start, end, step)])
    
    def __iter__(self):
        return self

    def next(self):
        if self.i < len(self.n):
            i = self.n[self.i]
            self.i += 1
            return i
        else:
            raise StopIteration()    


if __name__ == '__main__':  
    v1 = Vector(1,2)
    v2 = Vector(3,4)
    
    print v1 + v2
    print v1 + (5,1)
    print (5,1) + v2
    
    print v1 * v2
    print v1 * (5,1)
    print (5,1) * v2  
    
    print v1 * 2
    
    v1 *= 3
    print v1
    
    print abs(v1)
    print abs(v2)
    
    
    