from creatures.creature import *
from creatures.genome import *

def axonsToHex(axons: list[Axon]):
    return ''.join([str(axon) for axon in axons])

def randomAxon(): 
    return ''.join(random.choice('abcdef1234567890') for n in range(8))

def herbivore(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    herbivore_mind = [
        Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
        Axon(netIndex['action_flee'], netIndex['memory_0'], 1.0),
        # Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
        Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        # DoubleAxon(
        #     input=[netIndex['self_energy'], netIndex['creature_similarity']],
        #     output=netIndex['action_mate'],
        #     operator=DoubleAxon.operators['and'],
        #     threshold=0.9,
        #     factor=1.0
        # ),
        # Axon(netIndex['self_energy'], netIndex['action_mate'], 0.5),
        Axon(netIndex['see_grass'], netIndex['action_eat'], 1.0),
        # Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
        # Axon(netIndex['memory_7'], netIndex['relay_7'], 0.5),
        # Axon(netIndex['self_energy'], netIndex['action_eat'], -0.1),
        # Axon(netIndex['relay_7'], netIndex['action_mate'], -1.0),
        # Axon(netIndex['self_energy'], netIndex['relay_7'], -1.0),
        # Axon(netIndex['self_sprints'], netIndex['action_rest'], 1.0),
        # Axon(netIndex['self_injury'], netIndex['memory_5'], 1.0),
        # Axon(netIndex['self_injury'], netIndex['action_flee'], 1.0),
        # Axon(netIndex['memory_5'], netIndex['action_rest'], -0.4),
        # Axon(netIndex['action_rest'], netIndex['memory_5'], 1.0),
        Axon(netIndex['memory_0'], netIndex['action_sprint'], 1.0),
        Axon(netIndex['memory_0'], netIndex['action_sprint'], 1.0),
        Axon(netIndex['action_sprint'], netIndex['memory_0'], -1.0),
        Axon(netIndex['self_sprints'], netIndex['action_rest'], -1.0),
    ]
    return Creature(
        location=location,
        genome=[Genome(
            deadliness=0, 
            speed=4, 
            stamina=4, 
            fortitude=2, 
            intelligence=20, 
            longevity=20, 
            fertility=9, 
            meateating=0, 
            planteating=7, 
            sightrange=4, 
            sightfield=3, 
            brain=axonsToHex(herbivore_mind),
            variant='deersheep'
        )], 
        speciesName='deersheep',
        energy=100,
        mutate=mutate
    )

def herbivore_evolved(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    return Creature(
        location=location,
        genome=[Genome(
            deadliness=0, 
            speed=12, 
            stamina=3, 
            fortitude=2, 
            intelligence=13, 
            longevity=42, 
            fertility=9, 
            meateating=0, 
            planteating=7, 
            sightrange=4, 
            sightfield=4, 
            # brai'faecd86fcc85cb780605854211269566f857727c852876a4aba33057cad8b2b34ce3ffc48f193c143fce1315a975ce3a1514d7bed1ac9d96241fed48',
            brain='574d4678677f91020625851e112695665857727c2997a7d22a225054038ef7f39bccb51a8f199c24fe4e96480be24284b445bc2154b344f7dc920cf4',
            variant='superdeer'
        )], 
        speciesName='superdeer',
        energy=100,
        mutate=mutate
    )

def scavenger(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    scavenger_mind = [
        Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
        Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        Axon(netIndex['self_energy'], netIndex['action_mate'], 0.5),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
        Axon(netIndex['memory_7'], netIndex['relay_7'], 1.0),
        Axon(netIndex['self_energy'], netIndex['action_eat'], -0.1),
        Axon(netIndex['relay_7'], netIndex['action_mate'], -0.5),
        Axon(netIndex['self_energy'], netIndex['relay_7'], -0.01),
        Axon(netIndex['self_always'], netIndex['action_turnleft'], 0.5),
    ]
    return Creature(
        location=location, 
        genome=[Genome(
            deadliness=0, 
            speed=3, 
            stamina=3, 
            fortitude=2, 
            intelligence=20, 
            longevity=20, 
            fertility=9, 
            meateating=7, 
            planteating=0, 
            sightrange=7, 
            sightfield=2, 
            brain=axonsToHex(scavenger_mind),
            variant='coyotefox'
        )],
        speciesName='coyotefox',
        energy=energy,
        mutate=mutate
    )

def carnivore(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    carnivore_mind = [
        # attack creatures less deadly than self
        Axon(netIndex['creature_deadliness'], netIndex['action_attack'], -1.0),
        # mate with creatures similar to self
        Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        # don't attack creatures similar to self
        Axon(netIndex['self_energy'], netIndex['action_mate'], 0.1),
        # mate with deadly creatures, to sire deadly progeny
        Axon(netIndex['creature_deadliness'], netIndex['action_mate'], 0.1),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        Axon(netIndex['self_sometimes'], netIndex['action_turnleft'], 0.5),
        # Axon(netIndex['creature_size'], netIndex['action_attack'], 0.05)
        # Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
        # Axon(netIndex['self_birth'], netIndex['memory_6'], 1.0),
        # Axon(netIndex['memory_6'], netIndex['memory_7'], 0.55),
        # Axon(netIndex['memory_7'], netIndex['action_eat'], 0.5),
        # Axon(netIndex['memory_7'], netIndex['action_attack'], 0.1),
        # Axon(netIndex['memory_7'], netIndex['action_wander'], 0.05),
        # Axon(netIndex['memory_7'], netIndex['action_mate'], -1.0),
        # Axon(netIndex['self_energy'], netIndex['memory_7'], -0.05),
        # Axon(netIndex['self_sprints'], netIndex['action_rest'], 0.2),
    ]
    return Creature(
        location=location,  
        genome=[Genome(
            deadliness=4, 
            speed=8, 
            stamina=8, 
            fortitude=3, 
            intelligence=30, 
            longevity=40, 
            fertility=6, 
            meateating=7, 
            planteating=0, 
            sightrange=7, 
            sightfield=2, 
            brain=axonsToHex(carnivore_mind),
            variant='tigerwolf'
        )], 
        speciesName='tigerwolf',
        energy=energy,
        mutate=mutate
    )

def empty(location: MapNode=MapNode(), energy: float=100, mutate: bool=False, brain: str='') -> Creature:
    return Creature(
        location=location,
        genome=[Genome(
            deadliness=1, 
            speed=1, 
            stamina=1, 
            fortitude=1, 
            intelligence=1, 
            longevity=1, 
            fertility=1, 
            meateating=1, 
            planteating=1, 
            sightrange=4, 
            sightfield=4, 
            # brai'faecd86fcc85cb780605854211269566f857727c852876a4aba33057cad8b2b34ce3ffc48f193c143fce1315a975ce3a1514d7bed1ac9d96241fed48',
            brain=brain,
            variant='emptymind'
        )], 
        speciesName='?nothing?',
        energy=100,
        mutate=mutate
    )

def rando(location: MapNode=MapNode(), energy: float=100) -> Creature:
    return Creature(location, [randomGenome(), randomGenome()], energy, speciesName=''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for n in range(9)]))

def cross(*creatures, location: MapNode=MapNode(), mutate: bool=False):
    return Creature(
        location=location, 
        genome=[merge(*creature.genome) for creature in creatures], 
        speciesName=mergeString(*[creature.speciesName for creature in creatures]),
        mutate=mutate
    )

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

