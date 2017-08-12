from Vector.vector import I,O

SCRIPT_PATH    = 'scripts'
NUM_IDS        = 2**32
NUM_FOOD       = 2**32
NUM_PHEROMONES = 2**32
CACHE_SIZE     = 128

DIRECTIONS_NUM_CHAR = {'E':0, 'N':1, 'W':2, 'S':3, 0:'E', 1:'N', 2:'W', 3:'S', None:-1, -1:None}
DIRECTIONS_VEC_CHAR = {'E':I(0,3,1), 'N':I(1,3,1), 'W':I(0,3,-1), 'S':I(1,3,-1), I(0,3,1):'E', I(1,3,1):'N', I(0,3,-1):'W', I(1,3,-1):'S', O(3):None, O(2):None, None:O(3)}
DIRECTIONS_VEC_NUM = {0:I(0,3,1), 1:I(1,3,1), 2:I(0,3,-1), 3:I(1,3,-1), I(0,3,1):0, I(1,3,1):1, I(0,3,-1):2, I(1,3,-1):3, O(3):-1, O(2):-1, -1:O(3), None:-1}
DIRECTIONS_VEC_SYM = {'>':I(0,3,1), '^':I(1,3,1), '<':I(0,3,-1), 'v':I(1,3,-1), I(0,3,1):'>', I(1,3,1):'^', I(0,3,-1):'<', I(1,3,-1):'v', O(3):' ', O(2):' ', ' ':O(3)}

DIRECTIONS_LEFT = {I(0,3,1):I(1,3,1), I(1,3,1):I(0,3,-1), I(0,3,-1):I(1,3,-1), I(1,3,-1):I(0,3,1), 'E':'N', 'N':'W', 'W':'S', 'S':'E', 0:1, 1:2, 2:3, 3:0}
DIRECTIONS_RIGHT = {I(0,3,1):I(1,3,-1), I(1,3,-1):I(0,3,-1), I(0,3,-1):I(1,3,1), I(1,3,1):I(0,3,1), 'E':'S', 'S':'W', 'W':'N', 'N':'E', 0:3, 3:2, 2:1, 1:0}

DEFAULT_TICK_COST = 1
DEFAULT_NONTICK_COST = 0

ATTACK_DAMAGE     = 10
ATTACK_DEFENSE    = -10
DEFEND_DEFENSE    = 9
CHARGE_DEFENSE    = -5

DAMAGE = 'DAMAGE'
DEFENSE = 'DEFENSE'
OCCUPIED = 'OCCUPIED'