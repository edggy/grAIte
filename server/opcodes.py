import random
import copy

import constants
#from actor import Actor

class opcode(object):
    def __init__(self, function, arity = 0, tick = False, cost = None):
        self.function = function
        self.arity = arity
        self.tick = tick
        
        if cost is None:
            if self.tick:
                self.cost = constants.DEFAULT_TICK_COST
            else:
                self.cost = constants.DEFAULT_NONTICK_COST
        else:
            self.cost = cost
        
    def __call__(self, actor, *args, **kargs):
        kargs['cost'] = self.cost
        if self.tick:
            setupMove(actor)
        return self.function(actor, *args, **kargs)
    
def setupMove(actor):
    actor.cells[nextCell.t+1] = [actor.here.next]
    '''cellData = actor.here.next.data
    if constants.OCCUPIED not in cellData:
        cellData[constants.OCCUPIED] = {actor:0}
    else:
        cellData[constants.OCCUPIED][actor] = 0'''

def setAmount(deltaAmount, costPerItem, curAmount, maxNetCost = None, maxAmount = None):

    newAmount = curAmount + deltaAmount
    
    if maxAmount is not None and newAmount > maxAmount:
        # Can't add to more than max
        deltaAmount = maxAmount - curAmount
    elif newAmount < 0:
        # Can't remove to less than 0
        deltaAmount = -curAmount
    
    if maxNetCost is not None:
        netCost = abs(deltaAmount) * costPerItem
        
        if netCost > maxNetCost:
            # Paying more than we have
            if deltaAmount > 0:
                deltaAmount = maxNetCost / costPerItem
            else:
                deltaAmount = -maxNetCost / costPerItem
        
    return deltaAmount

LITERAL_CODE = '0123456789b-'


def normalCost(f):
    def wrapper(actor, *args, **kargs):
        actor.energy -= kargs['cost']     
        del kargs['cost']
        return f(actor, *args, **kargs)
    return wrapper  

def hereThere(f):
    def wrapper(actor, *args, **kargs):
        return f(actor, actor.here, actor.there, *args, **kargs)
    return wrapper

def hereThereCopy(f):
    def wrapper(actor, *args, **kargs):
        return f(actor, copy.copy(actor.here), copy.copy(actor.there), *args, **kargs)
    return wrapper
        
@normalCost
@hereThere
def AHX(actor, here, there):
    '''
    Get Abs Position X Here
    '''
    return here.x

@normalCost
@hereThere
def ATX(actor, here, there):
    '''
    Get Abs Position X There
    '''
    return there.x

@normalCost
@hereThere
def AHY(actor, here, there):
    '''
    Get Abs Position Y Here
    '''
    return here.y

@normalCost
@hereThere
def ATY(actor, here, there):
    '''
    Get Abs Position Y There
    '''
    return there.y

@normalCost
@hereThereCopy
def AK(actor, here, there):
    '''
    Attack
    '''

    # Put damage on There to be applied later
    there.data[constants.DAMAGE] += constants.ATTACK_DAMAGE
    
    # Raise (or lower) the defense of Here to calculate damage later
    here.data[constants.DEFENSE] += constants.ATTACK_DEFENSE
    
    return set([here, there])
    
@normalCost
@hereThereCopy
def CHG(actor, here, there):
    '''
    Charge
    '''
    # Energy will be added from negative 'cost'
    
    # Raise (or lower) the defense of Here to calculate damage later
    here.data[constants.DEFENSE] += constants.CHARGE_DEFENSE
    
    return set([here])

@normalCost
@hereThereCopy
def DE(actor, here, there):
    '''
    Defend
    '''
    # Raise (or lower) the defense of Here to calculate damage later
    here.data[constants.DEFENSE] += constants.DEFEND_DEFENSE
    
    return set([here])

@normalCost
def DH(actor):
    '''
    Get Direction Here
    '''
    return constants.DIRECTIONS_VEC_NUM[actor.direction]

@normalCost
@hereThere
def DT(actor, here, there):
    '''
    Get Direction There
    '''
    return constants.DIRECTIONS_VEC_NUM[there.actor.direction]

@normalCost
def EH(actor):
    '''
    Get Energy Here
    '''
    return actor.energy

@normalCost
@hereThere
def ET(actor, here, there):
    '''
    Get Energy There
    '''
    return there.actor.energy

@hereThereCopy
def FDH(actor, here, there, amount, cost = 1):
    '''
    Drop Food Here
    '''
    amount = setAmount(amount, cost, here.food, agent.energy, constants.NUM_FOOD)
    actor.energy -= amount*cost
    
    here.food += amount
    
    return set([here])

@hereThereCopy
def FDT(actor, here, there, amount, cost = 1):
    '''
    Drop Food There
    '''
    amount = setAmount(amount, cost, there.food, agent.energy, constants.NUM_FOOD)
    actor.energy -= amount*cost
    
    there.food += amount
    
    return set([here, there])

@hereThereCopy
def FEH(actor, here, there, amount, cost = -1):
    '''
    Eat Food Here
    '''
    amount = setAmount(-amount, cost, here.food, agent.energy, constants.NUM_FOOD)
    actor.energy -= amount*cost
    
    here.food -= amount
    
    return set([here])

@hereThereCopy
def FET(actor, here, there, amount, cost = -1):
    '''
    Eat Food There
    '''
    amount = setAmount(-amount, cost, there.food, agent.energy, constants.NUM_FOOD)
    actor.energy -= amount*cost
    
    there.food -= amount
    
    return set([here, there])

@normalCost
@hereThere
def FH(actor, here, there):
    '''
    Get Food Here
    '''
    return actor.here.food

@normalCost
@hereThere
def FT(actor, here, there):
    '''
    Get Food There
    '''
    return actor.there.food

@hereThereCopy
def FMH(actor, here, there, amount, cost = 1):
    '''
    Move Food Here
    '''
    amount = min(setAmount(-amount, cost, here.food, agent.energy, constants.NUM_FOOD), setAmount(amount, cost, there.food, agent.energy, constants.NUM_FOOD))
    actor.energy -= amount*cost
    
    here.food += amount
    there.food -= amount
    
    return set([here, there])

@hereThereCopy
def FMT(actor, here, there, amount, cost = 1):
    '''
    Move Food There
    '''
    amount = min(setAmount(amount, cost, here.food, agent.energy, constants.NUM_FOOD), setAmount(-amount, cost, there.food, agent.energy, constants.NUM_FOOD))
    actor.energy -= amount*cost
    
    here.food -= amount
    there.food += amount
    
    return set([here, there])

@normalCost
def JE(actor, num1, num2, offset):
    '''
    Jump Equal	
    '''
    if num1 == num2:
        actor.script.ip += offset

@normalCost
def JG(actor, num1, num2, offset):
    '''
    Jump Greater
    '''
    if num1 > num2:
        actor.script.ip += offset

@normalCost
def JL(actor, num1, num2, offset):
    '''
    Jump Less
    '''
    if num1 < num2:
        actor.script.ip += offset

@normalCost
def JN(actor, num1, num2, offset):
    '''
    Jump Not Equal
    '''
    if num1 != num2:
        actor.script.ip += offset

@normalCost
def JU(actor, offset):
    '''
    Jump Unconditionally
    '''
    actor.script.ip += offset

@normalCost
def MA(actor, num1, num2):
    '''
    Math Add
    '''
    return num1 + num2

@normalCost
def MBA(actor, num1, num2):
    '''
    Bitwise And
    '''
    return num1 & num2

@normalCost
def MBO(actor, num1, num2):
    '''
    Bitwise Or
    '''
    return num1 | num2

@normalCost
def MBN(actor, num):
    '''
    Bitwise Not
    '''
    return ~num

@normalCost
def MBX(actor, num1, num2):
    '''
    Bitwise Xor
    '''
    return num1 ^ num2

@normalCost
def MD(actor, num1, num2):
    '''
    Math Divide
    '''
    return num1 / num2

@normalCost
def MM(actor, num1, num2):
    '''
    Math Multiply
    '''
    return num1 * num2

@normalCost
def MR(actor, num1, num2):
    '''
    Math Remainder
    '''
    return num1 % num2

@normalCost
def MS(actor, num1, num2):
    '''
    Math Subtract
    '''
    return num1 - num2

@normalCost
def MX(actor, num1, num2):
    '''
    Math Random
    '''
    return actor.randint(num1, num2)

@normalCost
def NH(actor):
    '''
    Get Actor Name Here
    '''
    return actor.name

@normalCost
@hereThere
def NT(actor, here, there):
    '''
    Get Actor Name There
    '''
    return there.actor.name

@normalCost
@hereThereCopy
def NOP(actor, here, there):
    '''
    No Op	
    '''
    return set([here])

@normalCost
@hereThereCopy
def NS(actor, here, there, name):
    '''
    Set Actor Name
    '''
    actor.name = name
    return set([here])

@hereThereCopy
def PAH(actor, here, there, amount, cost = 1):
    '''
    Add Pheromones Here
    '''
    amount = setAmount(amount, cost, here.pheromone, agent.energy, constants.NUM_PHEROMONES)
    actor.energy -= amount*cost
    
    here.pheromone += amount
        
    return set([here])       

@hereThereCopy
def PAT(actor, here, there, amount, cost = 1):
    '''
    Add Pheromones There
    '''
    amount = setAmount(amount, cost, there.pheromone, agent.energy, constants.NUM_PHEROMONES)
    actor.energy -= amount*cost
    
    there.pheromone += amount
    
    return set([here, there])    

@normalCost
@hereThere
def PH(actor, here, there):
    '''
    Pheromones Here
    '''
    return here.pheromone

@normalCost
@hereThere
def PT(actor, here, there):
    '''
    Pheromones There
    '''
    return there.pheromone

@hereThereCopy
def PRH(actor, here, there, amount, cost = 1):
    '''
    Remove Pheromones Here
    '''
    amount = setAmount(-amount, cost, here.pheromone, agent.energy, constants.NUM_PHEROMONES)
    actor.energy -= amount*cost
    
    here.pheromone -= amount
    
    return set([here])

@hereThereCopy
def PRT(actor, here, there, amount, cost = 1):
    '''
    Remove Pheromones There
    '''
    amount = setAmount(-amount, cost, there.pheromone, agent.energy, constants.NUM_PHEROMONES)
    actor.energy -= amount*cost
    
    there.pheromone -= amount
    
    return set([here, there])

@hereThereCopy
def S(actor, here, there, amount, cost = 1):
    '''
    Split
    '''
    amount = setAmount(amount, cost, 0, agent.energy)
    actor.energy -= amount*cost
    
    newActor = actor.world.newActor(actor.agent, there, actor.direction, amount, actor.ip, 0, actor)
    
    return set([here, there])

@normalCost
@hereThere
def TL(actor, here, there):
    '''
    Turn Left
    '''
    actor.direction = constants.DIRECTIONS_LEFT[actor.direction]
    
    return set([here])

@normalCost
@hereThere
def TR(actor, here, there):
    '''
    Turn Right
    '''
    actor.direction = constants.DIRECTIONS_RIGHT[actor.direction]
    
    return set([here])

def TT(actor, amount, cost = 1):
    '''
    Time Travel
    '''
    # TODO
    actor.energy -= cost*2**amount

@normalCost
@hereThereCopy
def X(actor, here, there):
    '''
    Move Forward
    '''
    
    actor.cells[nextCell.t+1].insert(0, actor.there.next)
    
    #there.data[constants.OCCUPIED][actor] = 1
    #here.data[constants.OCCUPIED][actor] = 2
    
    return set([here, there])


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
    'S':opcode(S, 1, True),
    'TL':opcode(TL, 0, True),
    'TR':opcode(TR, 0, True),
    'TT':opcode(TT, 1, True),
    'X':opcode(X, 0, True)
    }