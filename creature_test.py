from pstats import Stats
import unittest
from creatures.genome import *

class testGenome(unittest.TestCase):
    gene = Genome(energy=1, deadliness=1, speed=1, stamina=4, fortitude=4, intelligence=13, longevity=6, fertility=9, meateating=1, planteating=7, sightrange=5, sightfield=3,mindStr='345979023qr79fa70450b0734ec3098e90283b')
    def test(self):
        print (self.gene.stamina)
        self.assertTrue(self.gene.stamina == 3 + 2/3)
        print ('raw')
        print ()
        print(*[f'{key}: {value.value}' for i, (key, value) in enumerate(self.gene.stats.items())], sep='\n')
        print ()
        print ('computed')
        print ()
        print(*[
            f'energy: {self.gene.energy}', 
            f'deadliness: {self.gene.deadliness}', 
            f'speed: {self.gene.speed}', 
            f'stamina: {self.gene.stamina}', 
            f'fortitude: {self.gene.fortitude}', 
            f'intelligence: {self.gene.intelligence}', 
            f'longevity: {self.gene.longevity}', 
            f'fertility: {self.gene.fertility}', 
            f'sight range: {self.gene.sightRange}', 
            f'field of view: {self.gene.sightField}', 
            f'meat eating: {self.gene.meatEating}', 
            f'plant eating: {self.gene.plantEating}'
        ], sep='\n')

testGenome().test()