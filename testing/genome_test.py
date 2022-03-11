from operator import indexOf
import unittest
from webbrowser import GenericBrowser
from creatures.genome import *

class testGenome(unittest.TestCase):

    def testMutations(self):
        gene1=randomGenome()
        old=gene1.axonStr
        self.assertTrue(len(gene1.axonStr) % 8 == 0)
        self.assertTrue(len(gene1.neuronStr) % 4 == 0)
        gene1.mutate(32, 'axon')
        self.assertTrue(gene1.axonStr != old)
        self.assertTrue(len(gene1.axonStr) == len(old))
        old=gene1.neuronStr
        gene1.mutate(32, 'neuron')
        self.assertTrue(gene1.neuronStr != old)
        self.assertTrue(len(gene1.neuronStr) == len(old))

    def testMerging(self):
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
            axonStr='11111111111111111111111111111111111111',
            variant='11111111',
            mutations=1
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
            axonStr='99999999999999999999999999999999999999',
            variant='99999999',
            mutations = 9
        )
        gene3=Genome.merge(gene1, gene2)
        gene3.printRawStats()
        print(gene3.brain)

        [self.assertTrue(char in [1, 9])
            for char in [
                v.value for v in gene3.stats.values()
            ] + 
            [
                int(c) for c in gene3.brain
            ] +
            [
                int(c) for c in gene3.variant
            ]
        ]
        self.assertTrue(gene3.mutations == 9)

        newBrain=mergeBrains ('1111111100000000bbbbbbbb', '555555557777777700000000bbbbbbbb')
        self.assertTrue(newBrain.count('0') < 9)

    def testEncoding(self):
        g=randomGenome()
        variant=g.variant
        deadliness=g._deadliness
        stamina=g._stamina
        longevity=g._longevity
        meateating=g._meateating
        
        # this should have zero net result
        g=decode(g.encode())

        self.assertTrue(variant == g.variant)
        self.assertTrue(deadliness == g._deadliness)
        self.assertTrue(stamina == g._stamina)
        self.assertTrue(longevity == g._longevity)
        self.assertTrue(meateating == g._meateating)
