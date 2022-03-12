from creatures.creature import *
from creatures.genome import *
from brain.basics import netIndex
from brain import brain

# def axonsToHex(axons: list[Axon]):
#     return ''.join([str(axon) for axon in axons])

def randomAxon(): 
    return ''.join(random.choice('abcdef1234567890') for n in range(8))

def Axon(input: int, output: int, factor: float):
    return (hex(input)[:2].zfill(2) 
        + hex(output)[:2].zfill(2) 
        + hex(min(int((factor + 1)*0x8000), 0xffff))[2:].zfill(4)
    )

def DoubleAxon(input: list[int], output: int, operator: int, threshold: float, factor: float):
        return (
            'FF' + 
            hex(operator)[2:].zfill(2) + 
            hex(int(threshold * 0xff))[2:].zfill(2) + 
            hex(input[0].index)[2:].zfill(2) + 
            hex(input[1].index)[2:].zfill(2) + 
            hex(output.index)[2:].zfill(2) +
            hex(min(int((factor + 1)*0x8000), 0xffff))[2:].zfill(4)
        )

def herbivore(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    herbivore_mind: brain.V1=brain.V1.unpack(
        axons=''.join([
            Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
            Axon(netIndex['action_flee'], netIndex['memory_0'], 1.0),
            Axon(netIndex['creature_similarity'], netIndex['action_mate'], 0.5),
            Axon(netIndex['see_grass'], netIndex['action_eat'], 1.0),

            Axon(netIndex['self_energy'], netIndex['action_mate'], 0.5),
            DoubleAxon(
                input=[netIndex['self_energy'], netIndex['creature_similarity']],
                output=netIndex['action_mate'],
                operator=DoubleAxon.operators['and'],
                threshold=0.9,
                factor=1.0
            ),
            Axon(netIndex['self_energy'], netIndex['action_mate'], 0.5),

            Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
            Axon(netIndex['memory_7'], netIndex['relay_7'], 0.5),
            Axon(netIndex['self_energy'], netIndex['action_eat'], -0.1),
            Axon(netIndex['relay_7'], netIndex['action_mate'], -1.0),
            Axon(netIndex['self_energy'], netIndex['relay_7'], -1.0),
            Axon(netIndex['self_sprints'], netIndex['action_rest'], 1.0),
            Axon(netIndex['self_injury'], netIndex['memory_5'], 1.0),
            Axon(netIndex['self_injury'], netIndex['action_flee'], 1.0),
            Axon(netIndex['memory_5'], netIndex['action_rest'], -0.4),
            Axon(netIndex['action_rest'], netIndex['memory_5'], 1.0),

            Axon(netIndex['memory_0'], netIndex['action_sprint'], 1.0),
            Axon(netIndex['memory_0'], netIndex['action_sprint'], 1.0),
            Axon(netIndex['action_sprint'], netIndex['memory_0'], -1.0),
            Axon(netIndex['self_sprints'], netIndex['action_rest'], -1.0),
        ])
    )
    neurons=[0 for _ in range(len(brain))]
    neurons[netIndex['action_wander']]=0.1
    herbivore_mind.loadBiases(neurons)

    return Creature(
        location=location,
        genomes=[Genome(
            deadliness=0, 
            speed=4, 
            stamina=4, 
            fortitude=2, 
            intelligence=20, 
            longevity=4, 
            fertility=9, 
            meateating=0, 
            planteating=7, 
            sightrange=4, 
            sightfield=3, 
            brain=herbivore_mind,
            variant='deersheep'
        )], 
        speciesName='deersheep',
        energy=100,
        mutate=mutate
    )

def danrsveej(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    deerbrain=''.join([
        DoubleAxon(
            input=[netIndex['creature_similarity'], netIndex['self_energy']],
            output=netIndex['action_mate'],
            threshold=0.9,
            operator=DoubleAxon.operators['and'],
            factor=0.5
        ),
        Axon(netIndex['see_grass'], netIndex['action_eat'], 0.7),
        Axon(netIndex['creature_deadliness'], netIndex['memory_0'], 1.0),
        Axon(netIndex['creature_deadliness'], netIndex['memory_1'], 1.0),
        Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
        Axon(netIndex['memory_1'], netIndex['action_sprint'], 0.6),
        Axon(netIndex['action_sprint'], netIndex['memory_1'], -1.0),
        Axon(netIndex['memory_0'], netIndex['action_mate'], -1.0),
        Axon(netIndex['memory_0'], netIndex['action_eat'], -1.0),
        Axon(netIndex['self_sprints'], netIndex['action_continue'], 1.0),
        Axon(netIndex['self_rarely'], netIndex['memory_1'], -1.0),
        DoubleAxon(
            input=[netIndex['memory_0'], netIndex['memory_1']],
            output=netIndex['action_turnleft'],
            threshold=1.0,
            operator=DoubleAxon.operators['and not'],
            factor=0.9
        ),
        Axon(netIndex['action_turnleft'], netIndex['memory_0'], -0.9),
    ])

    return Creature(
        location=location,
        genomes=[Genome(
            deadliness=0, 
            speed=7, 
            stamina=12, 
            fortitude=2, 
            intelligence=13, 
            longevity=4, 
            fertility=9, 
            meateating=0, 
            planteating=7, 
            sightrange=4, 
            sightfield=3, 
            axonStr=deerbrain,
            variant='danrsveej'
        )], 

        speciesName='danrsveej',
        energy=100,
        mutate=mutate
    )

def coyotefox(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    scavenger_mind = [
        Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
        DoubleAxon(
            input=[netIndex['creature_similarity'], netIndex['self_energy']],
            output=netIndex['action_mate'],
            threshold=0.9,
            operator=DoubleAxon.operators['and'],
            factor=0.5
        ),
        Axon(netIndex['creature_similarity'], netIndex['action_turnleft'], 0.5),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 0.9)
    ]
    return Creature(
        location=location, 
        genomes=[Genome(
            deadliness=1, 
            speed=6, 
            stamina=6, 
            fortitude=2, 
            intelligence=13, 
            longevity=5, 
            fertility=9, 
            meateating=7, 
            planteating=0, 
            sightrange=7, 
            sightfield=2, 
            axonStr=axonsToHex(scavenger_mind),
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
        genomes=[Genome(
            deadliness=4, 
            speed=8, 
            stamina=8, 
            fortitude=3, 
            intelligence=30, 
            longevity=4, 
            fertility=6, 
            meateating=7, 
            planteating=0, 
            sightrange=7, 
            sightfield=2, 
            axonStr=axonsToHex(carnivore_mind),
            variant='tigerwolf'
        )], 
        speciesName='tigerwolf',
        energy=energy,
        mutate=mutate
    )
def quiltrpolf(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    # designed with the help of evolution
    brain=[
        DoubleAxon(
            input=[netIndex['creature_similarity'], netIndex['self_energy']],
            output=netIndex['action_mate'],
            threshold=0.9,
            operator=DoubleAxon.operators['and'],
            factor=0.5
        ),
        Axon(netIndex['creature_exists'], netIndex['action_attack'], 0.77),
        Axon(netIndex['creature_similarity'], netIndex['action_attack'], -1.0),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 0.88),
        Axon(netIndex['self_energy'], netIndex['action_howl'], 1.0),
        # Axon(netIndex['creature_deadliness'], netIndex['action_attack'], -0.88),
        # Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        # Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
        # Axon(netIndex['creature_similarity'], netIndex['action_turnleft'], 1.0),
        # Axon(netIndex['self_energy'], netIndex['action_mate'], 0.1),
        # Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        # Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
        # Axon(netIndex['creature_similarity'], netIndex['action_continue'], 0.69),
        # Axon(netIndex['action_attack'], netIndex['memory_0'], 0.69),
        # Axon(netIndex['memory_0'], netIndex['action_sprint'], 0.69),
        # Axon(netIndex['action_eat'], netIndex['memory_0'], -1.0),
    ]
    return Creature(
        location=location,  
        genomes=[Genome(
            deadliness=4, 
            speed=8, 
            stamina=8, 
            fortitude=3, 
            intelligence=30, 
            longevity=4, 
            fertility=6, 
            meateating=7, 
            planteating=0, 
            sightrange=7, 
            sightfield=2, 
            axonStr=axonsToHex(brain),
            variant='qiltrpolf'
        )], 
        speciesName='qiltrpolf',
        energy=energy,
        mutate=mutate
    )

def deerkiller(location: MapNode=MapNode(), energy: float=100, mutate: bool=False) -> Creature:
    # this thing just kills deer
    brain=[
        Axon(netIndex['creature_health'], netIndex['action_attack'], 1.0),
        Axon(netIndex['creature_similarity'], netIndex['action_attack'], -1.0),
        Axon(netIndex['see_meat'], netIndex['action_eat'], 1.0),
    ]
    killer=Creature(
        location=location,  
        genomes=[Genome(
            deadliness=4, 
            speed=10, 
            stamina=8, 
            fortitude=3, 
            intelligence=13, 
            longevity=math.inf, 
            fertility=0, 
            meateating=7, 
            planteating=0, 
            sightrange=7, 
            sightfield=2, 
            axonStr=axonsToHex(brain),
            variant='deerkiller'
        )], 
        speciesName='killerofdeer',
        energy=energy,
        mutate=mutate
    )
    killer._metabolism=0
    return killer

def empty(location: MapNode=MapNode(), energy: float=100, mutate: bool=False, brain: str='') -> Creature:
    return Creature(
        location=location,
        genomes=[Genome(
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
            axonStr=brain,
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
        genomes=[merge(*creature.genome) for creature in creatures], 
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

