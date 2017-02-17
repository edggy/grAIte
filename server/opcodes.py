import random

class opcode:
    def __init__(self, function, arity = 0, tick = False, cost = 0):
        self.function = function
        self.arity = arity
        self.tick = tick
        
    def __call__(self, *args, **kargs):
        return self.function(*args, **kargs)
    
OP_CODES = {
    'AHX':opcode(AHX), 
    'ATX':opcode(ATX), 
    'AHY':opcode(AHY), 
    'ATY':opcode(ATY),
    'AK':opcode(AK, 0, True),
    'C':opcode(CHG, 0, True, -10),
    'DE':opcode(DE, 0, True),
    'DH':opcode(DH), 
    'DT':opcode(DT),
    'EH':opcode(EH), 
    'ET':opcode(ET),
    'FDH':opcode(FDH, 1, True), 
    'FDT':opcode(FDT, 1, True), 
    'FEH':opcode(FEH, 1, True), 
    'FET':opcode(FET, 1, True), 
    'FH':opcode(FH), 
    'FT':opcode(FT),
    'FMT':opcode(FMT, 1, True), 
    'FMH':opcode(FMH, 1, True),
    'JE':opcode(JE, 3, True),
    'JG':opcode(JG, 3, True),
    'JL':opcode(JL, 3, True),
    'JN':opcode(JN, 3, True),
    'JU':opcode(JU, 1, True),
    'MBA':opcode(MBA, 2),
    'MBO':opcode(MBO, 2),
    'MBN':opcode(MBN, 1),
    'MBX':opcode(MBX, 2),
    'MA':opcode(MA, 2),
    'MD':opcode(MD, 2),
    'MM':opcode(MM, 2),
    'MR':opcode(MR, 2),
    'MS':opcode(MS, 2),
    'MX':opcode(MX, 2),
    'NH':opcode(NH),
    'NT':opcode(NT),
    'NOP':opcode(NOP, 0, True),
    'NS':opcode(NS, 1, True),
    'PAH':opcode(PAH, 1, True),
    'PAT':opcode(PAT, 1, True),
    'PH':opcode(PH),
    'PT':opcode(PT),
    'PRH':opcode(PRH, 1, True),
    'PRT':opcode(PRT, 1, True),
    'Q':None,
    'TL':opcode(TL, 0, True),
    'TR':opcode(TR, 0, True),
    'TT':opcode(TT, 1, True),
    'X':opcode(X, 0, True)
    }

# dict of opcodes to arity

'''
OP_ARITY = {'AHX':0,'ATX':0,'AHY':0,'ATY':0,'AK':0,'CHG':0,'CLN':1,'DE':0,'DH':0,
            'DT':0,'EH':0,'ET':0,'FDH':1,'FDT':1,'FEH':1,'FET':1,'FH':0,'FT':0,
            'FMT':1,'FMH':1,'JE':3,'JG':3,'JL':3,'JN':3,'JU':1,'MA':2,'MBA':2,
            'MBO':2,'MBN':1,'MBX':2,'MD':2,'MM':2,'MR':2,'MS':2,'MX':2,'NH':0,
            'NT':0,'NOP':0,'NS':1,'PAH':1,'PAT':1,'PH':0,'PT':0,'PRH':1,'PRT':1,
            'Q':0, 'TL':0,'TR':0,'TT':1,'X':0}
'''

LITERAL_CODE = 'Q'

'''
TICK_CODES = set(['AK','CHG','CLN','DE','FDH','FDT','FEH','FET',
                  'FMT','FMH','JE','JG','JL','JN','JU','NOP','NS',
                  'PAH','PAT','PRH','PRT','TL','TR','TT','X' ])
'''
'''
OP_FUNCTIONS = {'AHX':AHX,'ATX':ATX,'AHY':AHY,'ATY':ATY,'AK':AK,'CHG':CHG,'CLN':CLN,'DE':DE,'DH':DH,
                'DT':DT,'EH':EH,'ET':ET,'FDH':FDH,'FDT':FDT,'FEH':FEH,'FET':FET,'FH':FET,'FT':FT,
                'FMT':FMT,'FMH':FMH,'JE':JE,'JG':JG,'JL':JL,'JN':JN,'JU':JU,'MA':MA,'MBA':MBA,
                'MBO':MBO,'MBN':MBN,'MBX':MBX,'MD':MD,'MM':MM,'MR':MR,'MS':MS,'MX':MX,'NH':NH,
                'NT':NT,'NOP':NOP,'NS':NS,'PAH':PAH,'PAT':PAT,'PH':PH,'PT':PT,'PRH':PRH,'PRT':PRT,
                'Q':None, 'TL':TL,'TR':TR,'TT':TT,'X':X}
'''

def AHX(actor):
    return actor.here.location[0]

def ATX(actor):
    return actor.there.location[0]

def AHY(actor):
    return actor.here.location[1]

def ATY(actor):
    return actor.there.location[1]

def AK(actor):
    pass

def CHG(actor):
    pass

def DE(actor):
    pass

def DH(actor):
    pass

def DT(actor):
    pass

def EH(actor):
    pass

def ET(actor):
    pass

def FDH(actor, amount):
    pass

def FDT(actor, amount):
    pass

def FEH(actor, amount):
    pass

def FET(actor, amount):
    pass

def FH(actor):
    pass

def FT(actor):
    pass

def FMT(actor, amount):
    pass

def FMH(actor, amount):
    pass

def JE(actor, num1, num2, offset):
    pass

def JG(actor, num1, num2, offset):
    pass

def JL(actor, num1, num2, offset):
    pass

def JN(actor, num1, num2, offset):
    pass

def JU(actor, offset):
    pass

def MA(actor, num1, num2):
    return num1 + num2

def MBA(actor, num1, num2):
    return num1 & num2

def MBO(actor, num1, num2):
    return num1 | num2

def MBN(actor, num):
    return ~num

def MBX(actor, num1, num2):
    return num1 ^ num2

def MD(actor, num1, num2):
    return num1 / num2

def MM(actor, num1, num2):
    return num1 * num2

def MR(actor, num1, num2):
    return num1 % num2

def MS(actor, num1, num2):
    return num1 - num2

def MX(actor, num1, num2):
    return random.randint(num1, num2)

def NH(actor):
    return actor.name

def NT(actor):
    pass

def NOP(actor):
    return None

def NS(actor, name):
    actor.name = name
    return None

def PAH(actor, amount):
    pass

def PAT(actor, amount):
    pass

def PH(actor):
    '''
    Pheromones Here
    '''
    return actor.here.pheromone

def PT(actor):
    '''
    Pheromones There
    '''
    return actor.there.pheromone

def PRH(actor, amount):
    '''
    Remove Pheromones Here
    '''
    pass

def PRT(actor, amount):
    '''
    Remove Pheromones There
    '''
    pass

def Q(actor):
    return None

def TL(actor):
    '''
    Turn Left
    '''
    pass

def TR(actor):
    '''
    Turn Right
    '''
    pass

def TT(actor, amount):
    '''
    Time Travel
    '''
    pass

def X(actor):
    '''
    Move Forward
    '''
    pass