from os import path
from collections import deque
import string
import struct
import io
from StringIO import StringIO

from constants import SCRIPT_PATH
import opcodes


decimal = string.digits
binary = string.digits[:2] + 'b'
basicMath = '+-*/()'
advancedMath = '<>^~&|%'   

# TODO: Implement hex.  May conflict with opcodes e.g. MA0xABCAHX could either be MA 0xABCA HX or MA 0xABC AHX
hexadecimal = string.digits + 'x' + string.uppercase[:6]

literalChars = ''.join(set(decimal + binary + basicMath + advancedMath))
startChars = ''.join(set(string.uppercase + literalChars))

fmt = '>I'
fmtSize = struct.calcsize(fmt)

def packAt(f, loc, num):
    init = f.tell()
    f.seek(loc, io.SEEK_SET)
    f.write(struct.pack(fmt, num))
    f.seek(init, io.SEEK_SET)
    
def unpackAt(f, loc):
    init = f.tell()
    f.seek(loc, io.SEEK_SET)
    num = struct.unpack(fmt, f.read(fmtSize))
    f.seek(init, io.SEEK_SET)
    return num[0]

def parseLiteral(stream):

    # Parse literal number
    num = ''
    while True:
        digit = stream.read(1)
        if digit not in (literalChars) or digit == '':
            break
        num += digit
        
    if digit != '':
        # Went too far
        stream.seek(-1, io.SEEK_CUR)
    
    return int(eval(num))

def parseSentence(stream):
    '''
    Given a stream
    '''
    
    # TODO: better check for optimized stream
    byte = stream.read(1)
    if byte not in startChars:
        lenData = unpackAt(stream, 0)
        headerSize = fmtSize * (lenData+1)
        stream.seek(headerSize, io.SEEK_SET)
        optimized = True
        
        
    elif byte != '':
        stream.seek(-1, io.SEEK_CUR)
        optimized = False
        
    sen = None
    tok = ''
    while True:
        
        # Convert to uppercase for case insensitivity
        byte = stream.read(1).upper()
        
        if byte == '':
            break
        
        # Skip non-letter non-number bytes
        if byte not in startChars:
            continue
        
        # Add letter to tok
        tok += byte
        
        # Check if tok is an opcode
        if tok in opcodes.OP_CODES:
            
            op = opcodes.OP_CODES[tok]
            
            # Check to see if this is a tick code
            if op.tick:
                # If it is then start a new sentence
                if sen is not None:
                    yield sen
                sen = []
                
            # Add opcode to sentence
            sen.append(tok)                
                    
            # Reset tok
            tok = ''
        elif tok in literalChars:
            # Tok is a number
            
            # Go back
            stream.seek(-1, io.SEEK_CUR)
            
            # Parse literal, add to sentence
            sen.append(parseLiteral(stream))
            
            # Reset tok
            tok = ''   
    if sen is not None:
        yield sen
    
    if tok != '':
        raise ParseException('Ended in middle of opcode')

def parseFile(fileName):
    '''
    Convert a user written script into a more manageable format
    '''
        
    # Data is a list of sentences
    # A sentence is a list of opcodes staring with a tick
    data = []
    sen = []
    
    with open(fileName, 'rb+') as f:
        try:
            lenData = struct.unpack(fmt, f.read(fmtSize))[0]
            # It is optimized if the first line
            if lenData > 0:
                optimized = True
                tickPoints = [struct.unpack(fmt, f.read(fmtSize))[0] for i in xrange(lenData)]
                ''' tickPoints = []
                for i in xrange(lenData):
                    chars = f.read(fmtSize)
                    value = struct.unpack(fmt, chars)
                    tickPoints.append(value)'''
                    
                for tickPoint in tickPoints:
                    f.seek(tickPoint-1, io.SEEK_SET)
                    startOfLine = f.read(2)
                    if startOfLine[0] != '\n' or startOfLine[1] not in startChars:
                        optimized = False
                        break
                if optimized:
                    return tickPoints
            
        except struct.error:
            optimized = False
            
        f.seek(0, io.SEEK_SET)
        for sen in parseSentence(f):
            data.append(sen)
        
        headerSize = fmtSize * (len(data)+1)
        
        packAt(f, 0, len(data))
        
        # Jump to after the header
        f.seek(headerSize, io.SEEK_SET)
        
        tickPoints = []
        for n, sen in enumerate(data):
            
            # Pack the location of the n'th tick
            loc = int(f.tell()+1)
            tickPoints.append(loc)
            packAt(f, (n+1)*fmtSize, loc)
            
            # Construct the sentence
            sentence = '\n' +  ' '.join(map(str, sen))
            
            # Write the sentence to the file
            f.write(sentence)
            
        f.truncate()
        
        return tickPoints
            

class Script:
    '''
    A script is code to be run by each agent
    
    It has code
    '''
    def __init__(self, scriptName = None, ip = None, cacheSize = None):
        if ip is None:
            self.ip = 0
        else:
            self.ip = ip
        
        self.scriptName = scriptName
        
        if cacheSize is None:
            self.defaultCacheSize = 128
        else:
            self.defaultCacheSize = cacheSize
        self.cacheSize = 0
        self.maxCacheSize = 2 * self.defaultCacheSize
        self.cacheStart = 0
        self.cache = StringIO()
        
        self.sentenceCache = {}

        if self.scriptName is not None:
            self.tickPoints = parseFile(self.scriptName)
            self.getCache()
            
        self.maxIP = len(self.tickPoints)
    
    @property
    def rawip(self):
        try:
            return self.tickPoints[self.ip]
        except IndexError:
            self.ip = 0
            return self.tickPoints[0]
        
    def __copy__(self):
        clone = type(self)()
        clone.scriptName = self.scriptName
        clone.ip = self.ip
        clone.tickPoints = self.tickPoints
        clone.defaultCacheSize = self.defaultCacheSize
        clone.getCache()
        
        return clone
    
    def next(self, tick = True):
        if self.ip in self.sentenceCache:
            sen = self.sentenceCache[self.ip]
            if tick:
                self.ip = (self.ip + 1) % self.maxIP
            return sen
            
        try:
            if self.rawip < self.cacheStart or self.rawip >= self.cacheStart + self.cacheSize or self.cacheSize > self.maxCacheSize:
                self.getCache()
                if self.rawip >= self.cacheStart + self.cacheSize:
                    return
        except IndexError:
            return
        
        while True:
            try:
                self.cache.seek(self.rawip - self.cacheStart)
                
                sen = parseSentence(self.cache).next()
                self.sentenceCache[self.ip] = sen
                if tick:
                    self.ip = (self.ip + 1) % self.maxIP
                return sen
            
            except ParseException:
                try:
                    self.addCache()
                except EOFError:
                    return        
    
    def __iter__(self):
        sen = self.next()
        while sen is not None:
            yield sen
            sen = self.next()
            
    def __getitem__(self, key):
        if key <= -len(self.tickPoints) or key >= len(self.tickPoints):
            raise IndexError('Index out of bounds')
        
        try:
            return self.sentenceCache[key]
        except KeyError:
            pass
        rawKey = self.tickPoints[key]
        if rawKey >= self.cacheStart and rawKey < self.cacheStart + self.cacheSize:
            try:
                self.cache.seek(rawKey - self.cacheStart)
                sen = parseSentence(self.cache).next()
                self.sentenceCache[key] = sen
                return sen
            
            except ParseException:
                pass
        with open(self.scriptName, 'rb') as f:
            f.seek(rawKey, io.SEEK_SET)
            sen = parseSentence(f).next()
            self.sentenceCache[key] = sen
            return sen            
    
    def getCache(self, amount = None):
        if amount is None:
            amount = self.defaultCacheSize
        self.cacheStart = max(self.rawip - amount/3, 0)
        with open(self.scriptName, 'rb') as f:
            f.seek(self.cacheStart)
            data = f.read(amount)
            self.cache = StringIO(data) 
            self.cacheSize = len(data)
            
    def addCache(self, amount = None):
        cacheLength = self.cacheSize
        
        if amount is None:
            amount = cacheLength

        with open(self.scriptName, 'rb') as f:
            f.seek(self.cacheStart + cacheLength)
            data = f.read(amount)
            if data == '':
                raise EOFError('Reached EOF')
            self.cache.write(data)
            self.cacheSize += len(data)
    
    def execute(self, actor, sentence):
        '''
        Executes a list of evaluated op codes
        
        '''
        
        # JG MA 25 50 MA 2 0 -1
        
        #actor.status = sentence[0]
        
        opstack = deque(sentence)
        
        argStack = deque()
        
        while len(opstack) > 0:
            p = opstack.pop()
            if p in opcodes.OP_CODES:
                op = opcodes.OP_CODES[p]
                if len(argStack) >= op.arity:
                    args = tuple([argStack.pop() for i in range(op.arity)])
                else:
                    raise ParseException('Not enough arguments, OP:%s requires %d arguments got %d' % (p, op.arity, len(argStack)))
                result = op(actor, *args)
                if not op.tick:
                    argStack.append(result)
                else:
                    actor.status = (p,) + args
            else:
                argStack.append(p)
        
        if result is not None:
            return result
        
        # No modified cells
        return set([actor.here.next])
                
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
    
    def tick(self, actor):
        return self.execute(actor, self.next())

class ParseException(Exception):
    pass

if __name__ == '__main__':  
    
    test = 'test.op'
    testCode = 'C C C JL EH 100 -3 TL JG ET 0 -5 S MD EH 2 JU -7'
    
    with open(test, 'w') as f:
        f.write(testCode)
        
    parseFile(test)
    
    with open(test) as f:
        print f.read()
        
    
    print [i for i in parseSentence(StringIO('C C C JL'))]
    print parseSentence(StringIO('C C C JL')).next()
    
    s = Script(test)
    print 
    print s.next()
    for sen in s:
        print sen
        
    
    
    