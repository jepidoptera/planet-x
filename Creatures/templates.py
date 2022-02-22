from creatures.creature import *
from creatures.genome import *

def axonsToHex(axons: list[Axon]):
    return ''.join([str(axon) for axon in axons])

def randomAxon(): 
    return ''.join(random.choice('abcdef1234567890') for n in range(8))

def herbivore(location: MapNode, energy: float=100) -> Creature:
    herbivore_mind = [
        Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
        Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        Axon(netIndex['see_grass'], netIndex['action_eat'], 1.0),
        Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
        Axon(netIndex['memory_7'], netIndex['relay_7'], 1.0),
        Axon(netIndex['self_energy'], netIndex['action_eat'], -0.005),
        Axon(netIndex['relay_7'], netIndex['action_mate'], -1.0),
        Axon(netIndex['self_energy'], netIndex['relay_7'], -0.02),
        Axon(netIndex['self_sprints'], netIndex['action_rest'], 0.5),
        Axon(netIndex['self_injury'], netIndex['memory_5'], 1.0),
        Axon(netIndex['memory_5'], netIndex['action_rest'], -0.4),
        Axon(netIndex['action_rest'], netIndex['memory_5'], 1.0),
    ]
    return Creature(location, Genome(
        deadliness=0, 
        speed=3, 
        stamina=3, 
        fortitude=2, 
        intelligence=60, 
        longevity=9, 
        fertility=9, 
        meateating=0, 
        planteating=7, 
        sightrange=4, 
        sightfield=3, 
        mindStr=axonsToHex(herbivore_mind)
    ), energy=100)

def carnivore(location: MapNode, energy: float=100) -> Creature:
    carnivore_mind = [
        # attack creatures less deadly than self
        Axon(netIndex['creature_deadliness'], netIndex['action_attack'], -0.5),
        # mate with creatures similar to self
        Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        # don't attack creatures similar to self
        Axon(netIndex['creature_similarity'], netIndex['action_attack'], -1.0),
        # mate with deadly creatures, to sire deadly progeny
        Axon(netIndex['creature_deadliness'], netIndex['action_mate'], 0.1),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
        Axon(netIndex['self_birth'], netIndex['memory_6'], 1.0),
        Axon(netIndex['memory_6'], netIndex['memory_7'], 0.55),
        Axon(netIndex['memory_7'], netIndex['action_eat'], 0.5),
        Axon(netIndex['memory_7'], netIndex['action_attack'], 0.1),
        Axon(netIndex['memory_7'], netIndex['action_wander'], 0.05),
        Axon(netIndex['self_energy'], netIndex['memory_7'], -0.05),
        Axon(netIndex['self_sprints'], netIndex['action_rest'], 0.2),
    ]
    return Creature(location,  Genome(
        deadliness=4, 
        speed=4, 
        stamina=8, 
        fortitude=3, 
        intelligence=60, 
        longevity=9, 
        fertility=6, 
        meateating=7, 
        planteating=0, 
        sightrange=7, 
        sightfield=2, 
        mindStr=axonsToHex(carnivore_mind)
    ), energy=100)


# 0    20    40    60    80    100    120    140    160    180
#   10    30    50    70    90    110    130    150    170    190
# 1    21    41    61    81    101    121    141    161    181
#   11    31    51    71    91    111    131    151    171    191
# 2    22    42    62    82    102    122    142    162    182
#   12    32    52    72    92    112    132    152    172    192
# 3    23    43    63    83    103    123    143    163    183
#   13    33    53    73    93    113    133    153    173    193
# 4    24    44    64    84    104    124    144    164    184
#   14    34    54    74    94    114    134    154    174    194
# 5    25    45    65    85    105    125    145    165    185
#   15    35    55    75    95    115    135    155    175    195
# 6    26    46    66    86    106    126    146    166    186
#   16    36    56    76    96    116    136    156    176    196
# 7    27    47    67    87    107    127    147    167    187
#   17    37    57    77    97    117    137    157    177    197
# 8    28    48    68    88    108    128    148    168    188
#   18    38    58    78    98    118    138    158    178    198
# 9    29    49    69    89    109    129    149    169    189
#   19    39    59    79    99    119    139    159    179    199

