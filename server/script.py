from os import path
from collections import deque
import string
import io

from constants import SCRIPT_PATH
import opcodes

class Script:
    '''
    A script is code to be run by each agent
    
    It has code
    '''
    def __init__(self, scripName):
        self.ip = ip
        self.data = []
        self.keys = {}
        self.keysBack = {}
        with open(path.join(SCRIPT_PATH, scripName), 'rb') as f:
            tok = ''
            lastIndex = None
            for byte in f.read():
                byte = byte.upper()
                
                # Skip non-letter bytes
                if byte not in string.uppercase:
                    continue
                
                # Add letter to tok
                tok += byte
                
                # Check if tok is an opcode
                if tok in opcodes.OP_CODES:
                    
                    # Check if tok is the 'literal' opcode
                    if tok == opcodes.LITERAL_CODE:
                        
                        # Parse literal number
                        num = ''
                        for digit in f.read():
                            if d not in (string.digits + '-bx' + string.uppercase[:6] + '+*/()' + '<>^~&|%'):
                                break
                            num += digit
                        f.seek(-1, io.SEEK_CUR)
                        
                        try:
                            # Add literal to data
                            self.data.append(int(eval(num)))
                        except:
                            pass
                    else:
                        
                        # Add opcode to data
                        self.data.append(tok)
                        
                        if tok in opcodes.TICK_CODES:
                            if lastIndex is not None:
                                index = len(self.data)
                                self.keys[lastIndex] = index
                                self.keysBack[index] = lastIndex
                            lastIndex = index
                            
                    # Reset tok
                    tok = ''
                        
    def nextOps(self):
        '''
        Gets the next list of op codes to be evaluated
        '''
        nextKey = self.keys[self.ip]
        opStr = self.data[self.ip:nextKey-1]
        self.ip = nextKey
        return opStr
    
    def execute(self, opStr):
        '''
        Executes a list of evaluated op codes
        
        @return - The command to be executed in a tuple ('opcode', value)
        '''
        
        # JG MA 25 50 MA 2 0 -1
        
        opstack = deque(opStr)
        
        argStack = deque()
        
        while len(opstack) > 0:
            p = opstack.pop()
            if p in opcodes.OP_CODES:
                arity = opcodes.OP_CODES[p]
                if len(argStack) > arity:
                    args = [argStack.pop() for i in range(arity)]
                    result = self.applyOpCode(p, args)
                    if result is not None:
                        argStack.append(result)
            else:
                argStack.append(p)
                
    # opstack  = JG MA 25 50 MA 2 0 -1
    # argStack =
    
    # opstack  = JG MA 25 50 MA 2 0
    # argStack = -1
    
    # opstack  = JG MA 25 50 MA 2
    # argStack = -1 0    
    
    # opstack  = JG MA 25 50 MA
    # argStack = -1 0 2    
    
    # MA 2 0 = 2
    
    # opstack  = JG MA 25 50
    # argStack = -1 2     
    
    # opstack  = JG MA 25
    # argStack = -1 2 50  
    
    # opstack  = JG MA
    # argStack = -1 2 50 25    
    
    # MA 50 25 = 75
    
    # opstack  = JG
    # argStack = -1 2 75
    
    # JG 75 2 -1 = None  (sets ip to ip-1)
    
    # opstack  =
    # argStack =  
        
        
    def applyOpCode(self, opcode, args):
        pass     
