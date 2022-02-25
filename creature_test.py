import unittest
from creatures.genome import *
from creatures.creature import *
from creatures import templates
from world.map import *


class testCreature(unittest.TestCase):
    def test(self):
        self.map = Map(20, 10)
        self.scenario_predation()
        self.scenario_herbivory()
        self.scenario_courtship()

    def scenario_predation(self):
        self.map.clear()
        herbivore = templates.herbivore(self.map.nodes[74])
        herbivore.direction=2
        carnivore = templates.carnivore(self.map.nodes[114], energy=100)
        carnivore.direction=4
        herbivore_action=herbivore.think()
        carnivore_action=carnivore.think()
        self.assertTrue(herbivore_action == 'action_flee')
        self.assertTrue(carnivore_action == 'action_attack')
        for n in range(5):
            herbivore_action=herbivore.animate()
        self.assertTrue(Map.getDistance(herbivore.location, carnivore.location) > 5)
        
        herbivore.location=self.map.nodes[74]

        for n in range(5):
            carnivore.animate()

        self.assertTrue(herbivore._dead)

        carnivore.think()
        carnivore.animate()
        carnivore.animate()

        self.assertTrue(carnivore.energy > 100)

    def scenario_herbivory(self):
        self.map.clear()
        herbivore = templates.herbivore(self.map.nodes[74], energy=100)
        herbivore.direction = 2
        self.map.nodes[114].resource=Resource(ResourceType.grass, 100) 
        herbivore_action=herbivore.think()
        self.assertTrue(herbivore_action == 'action_eat')
        for n in range(5):
            herbivore.animate()
        self.assertTrue (herbivore.energy > 100)

    def scenario_courtship(self):
        self.map.clear()
        creature1 = templates.herbivore(self.map.nodes[21])
        creature1.direction = 3
        creature2 = templates.herbivore(self.map.nodes[24])
        creature2.direction = 0
        creature1_action=creature1.think()
        creature2_action=creature2.think()
        self.assertTrue(creature1_action == 'action_mate')
        self.assertTrue(creature2_action == 'action_mate')
        for n in range(5):
            creature1.animate()
        self.assertTrue(type(creature1.offspring)==Creature)

        for creature in [creature1, creature2, creature1.offspring]:
            creature.die()
            creature.location.resource=None

        creature1=templates.carnivore(self.map.nodes[21],energy=120)
        creature2=templates.carnivore(self.map.nodes[24],energy=120)
        creature1.direction = 3
        creature2.direction = 0
        creature1_action=creature1.think()
        creature2_action=creature2.think()
        self.assertTrue(creature1_action == 'action_mate')
        self.assertTrue(creature2_action == 'action_mate')
        for n in range(5):
            creature1.animate()
        self.assertTrue(type(creature1.offspring)==Creature)

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

testCreature().test()