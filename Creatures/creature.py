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
    def __init__(self, type: NeuronType, sense: function = None, action: function = None, state = True):
        self.activation = 0.0
        self.sense = sense
        self.action = action
        self.type = type
        self.memState = state

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

    creatureNeurons = [
        Neuron(NeuronType.creature, sense=lambda self, other: other.deadliness - self.deadliness),
        Neuron(NeuronType.creature, sense=lambda _, other: other.age / other.longevity),
        Neuron(NeuronType.creature, sense=lambda _, other: other.health),
        Neuron(NeuronType.creature, sense=lambda self, other: other.similarity(self)),
        Neuron(NeuronType.creature, sense=lambda self, other: other.speed - self.speed),
        Neuron(NeuronType.creature, sense=lambda _, other: other.size)
    ]
    selfNeurons = [
        Neuron(NeuronType.self) * 5
    ]
    envNeurons = [
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.meat),
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.fruit),
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.grass),
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.tree)
    ]
    hiddenNeurons = [
        Neuron(NeuronType.hidden) * 12
    ]
    actionNeurons = [
        Neuron(NeuronType.action)
    ]

    def __init__(self, world:Map, location:MapNode, genome:Genome, energy: float):
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
        self.energy = energy

        self.location = location
        self.direction = int(random.random() * len(self.location.neighbors))
        # *age
        # *wisdom
        # *hunger
        # *health
        # *stamina

        self.memNeurons = [
            Neuron(NeuronType.memory, state = False) * 8
        ]
        self.brain = Brain(
            neurons=[
                *self.creatureNeurons,
                *self.selfNeurons,
                *self.envNeurons,
                *self.hiddenNeurons,
                *self.actionNeurons,
                *self.memNeurons
            ],
            axons=[
                genome.mindStr
            ]
        )
        return 

    def processEnvironment(self):
        vision = self.getVisionRanges()

        for layer, distance in enumerate(vision):
            for node in layer:
                self.processMapNode(node, distance)

    def processMapNode(self, node: MapNode, distance: int):
        for neuron in self.brain.neurons:
            if neuron.type != NeuronType.memory:
                neuron.activation = 0.0

        if (node.occupant):
            other = node.occupant

            for sensor in self.creatureNeurons:
                sensor.sense(self, other)
                # oh that's quite beautiful 👍

        if (node.resource):
            for sensor in self.envNeurons:
                sensor.sense(node.resource)

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

    def getSimilarity(self, other):
        similarity = 0.0
        commonRange = range(min(len(self.mindStr), len(other.mindStr)))
        for c in range(min(len(self.mindStr), len(other.mindStr))):
            similarity
        return 1.0
