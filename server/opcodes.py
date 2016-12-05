import random

# dict of opcodes to arity
OP_CODES = {'AHX':0,'ATX':0,'AHY':0,'ATY':0,'AK':0,'CHG':0,'CLN':1,'DE':0,'DH':0,
            'DT':0,'EH':0,'ET':0,'FDH':1,'FDT':1,'FEH':1,'FET':1,'FH':0,'FT':0,
            'FMT':1,'FMH':1,'JE':3,'JG':3,'JL':3,'JN':3,'JU':1,'MA':2,'MBA':2,
            'MBO':2,'MBN':1,'MBX':2,'MD':2,'MM':2,'MR':2,'MS':2,'MX':2,'NH':0,
            'NT':0,'NOP':0,'NS':1,'PAH':1,'PAT':1,'PH':0,'PT':0,'PRH':1,'PRT':1,
            'Q':0, 'TL':0,'TR':0,'TT':1,'X':0}

LITERAL_CODE = 'Q'

TICK_CODES = set(['AK','CHG','CLN','DE','FDH','FDT','FEH','FET',
                  'FMT','FMH','JE','JG','JL','JN','JU','NOP','NS',
                  'PAH','PAT','PRH','PRT','TL','TR','TT','X' ])

OP_FUNCTIONS = {'AHX':AHX,'ATX':ATX,'AHY':AHY,'ATY':ATY,'AK':AK,'CHG':CHG,'CLN':CLN,'DE':DE,'DH':DH,
                'DT':DT,'EH':EH,'ET':ET,'FDH':FDH,'FDT':FDT,'FEH':FEH,'FET':FET,'FH':FET,'FT':FT,
                'FMT':FMT,'FMH':FMH,'JE':JE,'JG':JG,'JL':JL,'JN':JN,'JU':JU,'MA':MA,'MBA':MBA,
                'MBO':MBO,'MBN':MBN,'MBX':MBX,'MD':MD,'MM':MM,'MR':MR,'MS':MS,'MX':MX,'NH':NH,
                'NT':NT,'NOP':NOP,'NS':NS,'PAH':PAH,'PAT':PAT,'PH':PH,'PT':PT,'PRH':PRH,'PRT':PRT,
                'Q':None, 'TL':TL,'TR':TR,'TT':TT,'X':X}

def AHX(actor):
    return actor.location[0]

def ATX(actor):
    pass

def AHY(actor):
    return actor.location[1]

def ATY(actor):
    pass

def AK(actor):
    pass

def CHG(actor):
    pass

def CLN(actor, amount):
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

def MA(num1, num2):
    return num1 + num2

def MBA(num1, num2):
    return num1 & num2

def MBO(num1, num2):
    return num1 | num2

def MBN(num):
    return ~num

def MBX(num1, num2):
    return num1 ^ num2

def MD(num1, num2):
    return num1 / num2

def MM(num1, num2):
    return num1 * num2

def MR(num1, num2):
    return num1 % num2

def MS(num1, num2):
    return num1 - num2

def MX(num1, num2):
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
    pass

def PT(actor):
    pass

def PRH(actor, amount):
    pass

def PRT(actor, amount):
    pass

def Q(actor):
    return None

def TL(actor):
    pass

def TR(actor):
    pass

def TT(actor, amount):
    pass

def X(actor):
    pass