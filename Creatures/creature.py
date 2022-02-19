# good start
# you made a file
from argparse import Action
from enum import Enum
import random
from creatures.genome import randomGenome
from creatures.genome import Genome
from world.map import *
import typing

class NeuronType(Enum):
    creature = 0
    self = 1
    memory = 2
    environment = 3
    relay = 4
    action = 5
    
class Neuron():
    activation:float
    sense:typing.Callable
    action:typing.Callable
    type:NeuronType
    name:str
    memState:bool
    connects:list
    def __init__(self, type: NeuronType, name:str='', sense: typing.Callable=None, action: typing.Callable=None, memState=True):
        self.activation = 0.0
        self.sense = sense
        self.action = action
        self.type = type
        self.memState = memState

# 🙌🏾

class Axon():
    def __init__(self, input: Neuron, output: Neuron, factor: float):
        self.input = input
        self.output = output
        self.factor = factor

class ActionOption():
    action: typing.Callable
    target: any
    weight: float
    def __int__(self, action: typing.Callable, target: any, weight: float):
        self.action = action
        self.target = target
        self.weight = weight        

class Brain():
    creatureNeurons = [
        Neuron(NeuronType.creature, sense=lambda self, other: other.deadliness - self.deadliness),
        Neuron(NeuronType.creature, sense=lambda _, other: other.age / other.longevity),
        Neuron(NeuronType.creature, sense=lambda _, other: other.health),
        Neuron(NeuronType.creature, sense=lambda self, other: other.similarity(self)),
        Neuron(NeuronType.creature, sense=lambda self, other: other.speed - self.speed),
        Neuron(NeuronType.creature, sense=lambda _, other: other.size)
    ]

    selfNeurons = [
        Neuron(NeuronType.self, sense=lambda self: self.energy),
        Neuron(NeuronType.self, sense=lambda self: self.health),
        Neuron(NeuronType.self, sense=lambda self: self.age),
        Neuron(NeuronType.self, sense=lambda self: self.sprintMoves),
    ]
    
    envNeurons = [
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.meat),
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.fruit),
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.grass),
        Neuron(NeuronType.environment, sense=lambda resource: resource.type==ResourceType.tree)
    ]

    relayNeurons = [Neuron(NeuronType.relay)] * 16

    actionNeurons = [
        Neuron(NeuronType.action, action=lambda creature, _: creature)
    ]

    senseAxons: list[Axon]
    memoryAxons: list[Axon]
    relayAxons: list[Axon]
    actionAxons: list[Axon]

    def __init__(self,genome:str):
        self.memNeurons = [Neuron(NeuronType.memory, memState = False)] * 16
        self.unpackGenome(genome)

    def unpackGenome(self, genome):
        # first two digits are input neuron
        # second two are output
        # what are possible outputs?
        # attack, mate, eat, flee, wander, think (which), remember (which)
        self.actionAxons = []
        self.relayAxons = []
        self.memoryAxons = []
        self.senseAxons = []
        for n in range(int(len(genome)/8)):
            axon = genome[n * 8: (n + 1) * 8]
            input = int(axon[:2], 16) % len(self.neurons)
            output = int(axon[2:4], 16) % len(self.neurons)
            factor = int(axon[4:8], 16) / 65535
            axon = Axon(input=self.neurons[input], output=self.neurons[output], factor=factor)
            if axon.input.type in [NeuronType.creature, NeuronType.environment, NeuronType.self]:
                self.senseAxons.append(axon)
            elif axon.input.type == NeuronType.memory:
                self.memoryAxons.append(axon)
            elif axon.input.type == NeuronType.relay:
                self.relayAxons.append(axon)
            elif axon.input.type == NeuronType.action:
                self.actionAxons.append(axon)

        return self.senseAxons + self.memoryAxons + self.relayAxons + self.actionAxons

    def processEnvironment(self, vision:list[list[MapNode]]):
        actionOptions: list[ActionOption] = []

        for layer, distance in enumerate(vision):
            for node in layer:
                if (node.occupant):
                    self.clearInputs()
                    other = node.occupant

                    for sensor in self.creatureNeurons:
                        sensor.sense(self, other)
                        # oh that's quite beautiful 👍
                    actionOptions.append(self.processStimulus(other, distance))

                if (node.resource):
                    self.clearInputs()
                    for sensor in self.envNeurons:
                        sensor.sense(node.resource)
                    actionOptions.append(self.processStimulus(other, distance))

        return actionOptions

    def clearInputs(self):
        for neuron in self.selfNeurons + self.envNeurons + self.creatureNeurons + self.memNeurons + self.relayNeurons + self.actionNeurons:
            neuron.activation = 0.0

    def processStimulus(self, target, distance):
        # the order is very important here vvv
        for axon in self.senseAxons + self.memoryAxons + self.relayAxons + self.actionAxons:
            axon.output.activation += axon.input.activation * axon.factor

        out = max(*[self.actionNeurons], key=lambda n: n.activation)
        return ActionOption(out.action, target, out.activation * 1/distance)

class Creature():    
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
        self.sightField = genome.sightField
        self.mindStr = genome.mindStr

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

        self.memNeurons = [Neuron(NeuronType.memory, memState = False)] * 16

        self.brain = Brain(self.mindStr)
        return

    def animate(self):
        options = self.brain.processEnvironment(self.getVisionRanges)
        action = max(*options, key=lambda option: option.weight)
        action.action()

    def getVisionRanges(self):
        cones = [
            self.nodes[self.location].visionTree[(self.direction + n) % len(self.location.neighbors)][:self.sightRange] 
            for n in [-int(n / 2) if n % 2 == 0 else int(n / 2) + 1 
            for n in range((self.sightField - 1) * 2 + 1)] 
        ]
        visionLayers = [
            # get a separate array of nodes for each distance from self.location
            [node.index for cone in [[cones[a][b] 
            for a in range(len(cones))] for b in range(self.sightRange)][i] 
            for node in cone] for i in range(self.sightRange)
        ]
        return visionLayers

    def getSimilarity(self, other):
        similarity = 0.0
        commonRange = range(min(len(self.genome.mindStr), len(other.genome.mindStr)))
        increment = 1/len(commonRange)
        for c in commonRange:
            if self.genome.mindStr[c] == other.genome.mindStr[c]: similarity += increment
        return similarity

    def printStats(self):
        print('deadliness: ', self.deadliness)
        print('speed: ', self.speed)
        print('fortitude: ', self.fortitude)
        print('stamina: ', self.stamina)
        print('meat eating: ', self.meatEating)
        print('plant eating: ', self.plantEating)
        print('intelligence: ', self.intelligence)
        print('sight range: ', self.sightRange)
        print('field of view: ', self.sightField)
        print('brain dna: ', self.mindStr)

        print('age: ', self.age)
        print('health: ', self.health)
        print('energy: ', self.energy)
        print(f'location x:{self.location.x}, y:{self.location.y}')

if __name__ == "__main__":
    print("creature.py is main file")
#     map = Map(20, 14)
#     c = Creature(map, map.nodes[150], randomGenome(), 100.0)