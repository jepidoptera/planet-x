# good start
# you made a file
from enum import Enum
from random import random
from genome import Genome
from world.map import *

class NeuronType(Enum):
    creature = 0
    self = 1
    memory = 2
    environment = 3
    hidden = 4
    action = 5
    
class Neuron():
    def __init__(self, type: NeuronType ):
        self.activation = 0.0
        self.sense = None
        self.action = None
        self.type = type

class Axon():
    def __init__(self, input: Neuron, output: Neuron, factor: float):
        self.input = input
        self.output = output
        self.factor = factor

class Brain():
    def __init__(self, axons: list[Axon], neurons: list[Neuron]):
        self.axons = axons
        self.neurons = neurons

class Creature():    
    def __init__(self, world:Map, location:MapNode, genome:Genome):
        self.world = world
        
        self.genome = genome
        self.deadliness = genome.deadliness
        self.speed = genome.speed
        self.fortitude = genome.fortitude
        self.stamina = genome.stamina
        self.meatEating = genome.meatEating
        self.plantEating = genome.plantEating
        self.intelligence = genome.intelligence
        self.sightRange = genome.sightRange
        self.peripheralVision = genome.peripheralVision

        self.age = 0
        self.health = self.fortitude

        self.location = location
        self.direction = int(random.random() * len(self.location.neighbors))
        # *age
        # *wisdom
        # *hunger
        # *health
        # *stamina

        self.creatureNeurons = [
            Neuron(NeuronType.creature) * 10
        ]
        self.selfNeurons = [
            Neuron(NeuronType.self) * 5
        ]
        self.envNeurons = [
            Neuron(NeuronType.environment) * 6
        ]
        self.memNeurons = [
            Neuron(NeuronType.memory) * 8
        ]
        self.hiddenNeurons = [
            Neuron(NeuronType.hidden) * 12
        ]
        self.actionNeurons = [
            Neuron(NeuronType.action)
        ]
        self.brain = Brain(
            neurons=[
                *self.creatureNeurons,
                *self.selfNeurons,
                *self.envNeurons,
                *self.memNeurons,
                *self.hiddenNeurons,
                *self.actionNeurons
            ],
            axons=[

            ]
        )
        return 

    def processEnvironment(self):
        vision = self.getVisionRanges()

        for layer, distance in enumerate(vision):
            for node in layer:
                self.processMapNode(node)

    def processMapNode(self, node: MapNode):
        for neuron in self.brain.neurons:
            neuron.activation = 0.0

        if type(node.occupant) == Creature:
            other = node.occupant

            for axon in self.brain.axons:
                if axon.input.type == NeuronType.creature:
                    axon.output.activation += axon.input.activation * axon.factor


    def getVisionRanges(self):
        cones = [
            self.nodes[self.location].visionTree[(self.direction + n) % len(self.location.neighbors)][:self.sightRange] 
            for n in [-int(n / 2) if n % 2 == 0 else int(n / 2) + 1 
            for n in range((self.peripheralVision - 1) * 2 + 1)] 
        ]
        visionLayers = [
            # get a separate array of nodes for each distance from self.location
            [node.index for cone in [[cones[a][b] 
            for a in range(len(cones))] for b in range(self.sightRange)][i] 
            for node in cone] for i in range(self.sightRange)
        ]
        return visionLayers

    def unpackBrainGenome(self):
        return []
