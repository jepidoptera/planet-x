import unittest
from creatures.genome import *

class testGenome(unittest.TestCase):

    def test(self):
        gene1 = Genome(
            deadliness=1, 
            speed=1, 
            stamina=1, 
            fortitude=1, 
            intelligence=1, 
            longevity=1, 
            fertility=1, 
            meateating=1, 
            planteating=1, 
            sightrange=1, 
            sightfield=1,
            mindStr='11111111111111111111111111111111111111'
                    
        )
        gene2 = Genome(
            deadliness=9, 
            speed=9, 
            stamina=9, 
            fortitude=9, 
            intelligence=9, 
            longevity=9, 
            fertility=9, 
            meateating=9, 
            planteating=9, 
            sightrange=9, 
            sightfield=9,
            mindStr='99999999999999999999999999999999999999'
        )
        gene3=Genome.merge(gene1, gene2)
        gene3.printRawStats()
        print(gene3.mindStr)

        [self.assertTrue(char in [1, 9])
            for char in [
                v.value for v in gene3.stats.values()
            ] + 
            [
                int(c) for c in gene3.mindStr
            ]
        ]

testGenome().test()