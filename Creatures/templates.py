from creatures.creature import *
from creatures.genome import *

basicBrain = [
    Axon(netIndex['creature_deadliness'], netIndex['action_flee'], 1.0),
    Axon(netIndex['creature_similarity'], netIndex['action_mate'], 1.0),
    Axon(netIndex['grass'], netIndex['action_eat'], 1.0),
    Axon(netIndex['self_birth'], netIndex['memory_7'], 1.0),
    Axon(netIndex['memory_7'], netIndex['relay_7'], 1.0),
    Axon(netIndex['self_energy'], netIndex['action_eat'], -0.2),
    Axon(netIndex['relay_7'], netIndex['action_mate'], -1.0),
    Axon(netIndex['self_energy'], netIndex['relay_7'], -1.0),
    Axon(netIndex['self_sprints'], netIndex['action_rest'], 0.5),
    Axon(netIndex['self_injury'], netIndex['memory_5'], 1.0),
    Axon(netIndex['memory_5'], netIndex['action_rest'], -0.4),
    Axon(netIndex['action_rest'], netIndex['memory_5'], 1.0),
]
brainStr = ''.join([str(axon) for axon in basicBrain])
# '002effff' + # flee! if other.deadliness is higher
# '032fffff' + # mate if other is similar to self
# '06300000' + # don't eat if you're not hungry
# '0c30ffff' + # eat grass if you see grass
# '' # don't mate if energy is low
