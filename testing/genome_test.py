from operator import indexOf
import unittest
from webbrowser import GenericBrowser
from creatures.genome import *

class testGenome(unittest.TestCase):

    def testMutations(self):
        gene1=randomGenome()
        oldAxons=copy.deepcopy(gene1.axons)
        for n in range(32): gene1.mutate(1, 'axon')
        self.assertTrue(len(gene1.axons) == len(oldAxons))
        self.assertTrue(len(list(filter(
            lambda a: (
                gene1.axons[a]._factor != oldAxons[a]._factor
            ),
            list(range(len(gene1.axons)))
        ))))

        oldNeurons=copy.copy(gene1.neurons)
        for n in range(32): gene1.mutate(1, 'neuron')
        self.assertTrue(len(gene1.neurons.keys()) == len(oldNeurons.keys()))
        self.assertTrue(len(list(filter(
            lambda a: (
                gene1.neurons[a] != oldNeurons[a]
            ),
            list(gene1.neurons.keys())
        ))))

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
            variant='11111111',
            axons=[1, 1, 1, 1],
            neurons={1: 1},
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
            variant='99999999',
            axons=[9, 9, 9, 9],
            neurons={9: 9},
            mutations = 9
        )
        gene3=Genome.merge(gene1, gene2)
        gene3.printRawStats()

        [self.assertTrue(char in [1, 9])
            for char in [
                v.value for v in gene3.stats.values()
            ] + 
            [
                int(c) for c in gene3.axons
            ] +
            [
                int(c) for c in gene3.neurons.keys()
            ] +
            [
                int(c) for c in gene3.neurons.values()
            ] +
            [
                int(c) for c in gene3.variant
            ]
        ]
        self.assertTrue(gene3.mutations == 9)

    def testEncoding(self):
        g=randomGenome()
        variant=g.variant
        deadliness=g._deadliness
        stamina=g._stamina
        longevity=g._longevity
        meateating=g._meateating
        
        # this should have zero net result (except for rounding errors)
        g=decode(g.encode())

        axonInputs=[axon.input for axon in g.axons]
        axonOutputs=[axon.output for axon in g.axons]
        axonWeights=[round(axon.factor, 3) for axon in g.axons]
        neuronBiases=[(key, round(value, 3)) for (key, value) in g.neurons.items()]
        # at this point the rounding errors are already baked in so there should really be no result
        # except that for some reason there is occasionally an additional rounding error at the fifth decimal place or so
        # so, we round to three significant digits
        g=decode(g.encode())

        self.assertTrue(axonInputs == [axon.input for axon in g.axons])
        self.assertTrue(axonOutputs == [axon.output for axon in g.axons])
        self.assertTrue(axonWeights == [round(axon.factor, 3) for axon in g.axons])
        self.assertTrue(neuronBiases == [(key, round(value, 3)) for (key, value) in g.neurons.items()])

        self.assertTrue(variant == g.variant)
        self.assertTrue(deadliness == g._deadliness)
        self.assertTrue(stamina == g._stamina)
        self.assertTrue(longevity == g._longevity)
        self.assertTrue(meateating == g._meateating)
