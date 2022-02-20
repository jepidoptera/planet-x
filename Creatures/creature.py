# good start
# you made a file!
# 288 lines long now. got about ten other files as well
from enum import Enum
import random
from creatures.genome import Genome
from world.map import *
import typing

class NeuronType(Enum):
    self = 0
    creature = 1
    environment = 2
    memory = 3
    relay = 4
    action = 5

netIndex={}
    
class Neuron():
    activation:float
    sense:typing.Callable
    action:typing.Callable
    type:NeuronType
    name:str
    def __init__(self, type: NeuronType, name:str='', sense: typing.Callable=None, action: typing.Callable=None):
        self.activation = 0.0
        self.__sense = sense
        self.action = action
        self.type = type
        netIndex[name]=self
    def sense(self, *args):
        self.activate(self.__sense(*args))
    def activate(self, amount):
        self.activation = amount
    def clear(self):
        self.activation = 0
# 🙌🏾

class MemNeuron(Neuron):
    sense=None
    action=None
    type=NeuronType.memory

    def __init__(self, memstate:bool=True, threshold:float=1.0, strength:float=1.0, name:str=''):
        super().__init__(NeuronType.memory, name=name)
        self.memState = memstate
        self.strength = strength
    def activate(self, amount):
        if abs(amount) > self.threshold: self.memState = (sign(amount)+1) / 2
    def clear(self):
        self.activation = self.memState * self.strength

class Axon():
    def __init__(self, input: Neuron, output: Neuron, factor: float):
        self.input = input
        self.output = output
        self.factor = factor

class ActionOption():
    def __init__(self, action: typing.Callable, target: any, weight: float, relevantNeuron: Neuron):
        self.action = action
        self.target = target
        self.weight = weight
        self.neuron = relevantNeuron

# class Brain():

class Creature():    
    attackTarget: any
    fleeTarget: any
    mateTarget: any
    moveTarget: MapNode
    path: list[MapNode]

    creatureNeurons = [ # 00 - 05
        Neuron(NeuronType.creature, name='creature_deadliness', sense=lambda self, other: other.deadliness - self.deadliness),
        Neuron(NeuronType.creature, name='creature_age', sense=lambda self, other: other.age / other.longevity),
        Neuron(NeuronType.creature, name='creature_health', sense=lambda self, other: other.health),
        Neuron(NeuronType.creature, name='creature_similarity', sense=lambda self, other: self.getSimilarity(other)),
        Neuron(NeuronType.creature, name='creature_speed', sense=lambda self, other: other.speed - self.speed),
        Neuron(NeuronType.creature, name='creature_size', sense=lambda self, other: other.size)
    ]

    selfNeurons = [ # 06 - 09
        Neuron(NeuronType.self, name='energy', sense=lambda self: self.energy),
        Neuron(NeuronType.self, name='health', sense=lambda self: self.health),
        Neuron(NeuronType.self, name='age', sense=lambda self: self.age),
        Neuron(NeuronType.self, name='birth', sense=lambda self: 0), # just born
        Neuron(NeuronType.self, name='injury', sense=lambda self: 0), # under attack 
    ]
    
    envNeurons = [ # 0a - 0d
        Neuron(NeuronType.environment, name='meat', sense=lambda resource: 1 if resource.type==ResourceType.meat else 0),
        Neuron(NeuronType.environment, name='fruit', sense=lambda resource: 1 if resource.type==ResourceType.fruit else 0),
        Neuron(NeuronType.environment, name='grass', sense=lambda resource: 1 if resource.type==ResourceType.grass else 0),
        Neuron(NeuronType.environment, name='tree', sense=lambda resource: 1 if resource.type==ResourceType.tree else 0)
    ]

    relayNeurons = [Neuron(NeuronType.relay, name=f'relay{n}') for n in range(8)]

    actionNeurons = [
        Neuron(NeuronType.action, action=lambda self, other: self.attack(other)),
        Neuron(NeuronType.action, action=lambda self, other: self.flee(other)),
        Neuron(NeuronType.action, action=lambda self, other: self.mate(other)),
        Neuron(NeuronType.action, action=lambda self, resource: self.eat(resource)) 
    ]

    senseAxons: list[Axon]
    memoryAxons: list[Axon]
    relayAxons: list[Axon]
    actionAxons: list[Axon]

    def __init__(self, world:Map, location:MapNode, genome:Genome, energy: float):
        self.world = world
        self.location = location
        self.location.occupant = self
        
        self.genome = genome
        self.deadliness = genome.deadliness
        self.speed = genome.speed
        self.fortitude = genome.fortitude
        self.fertility = genome.fertility
        self.longevity = genome.longevity
        self.stamina = genome.stamina
        self.intelligence = genome.intelligence
        self.meatEating = genome.meatEating
        self.plantEating = genome.plantEating
        self.sightRange = genome.sightRange
        self.sightField = genome.sightField
        self.size = genome.size.value
        self.mindStr = genome.mindStr

        self.age = 0
        self.health = self.fortitude
        self.energy = energy
        self.sprintMoves = 0
        self.__metabolism = sum([stat.value * stat.metacost for stat in genome.stats.values()])

        self.direction = int(random.random() * len(self.location.neighbors))
        # *age
        # *wisdom
        # *hunger
        # *health
        # *stamina

        self.memNeurons = [MemNeuron(False, strength=n, name=f'memory{n}') for n in range(8)]
        self.allNeurons = self.creatureNeurons + self.envNeurons + self.selfNeurons + self.memNeurons + self.relayNeurons + self.actionNeurons
        self.unpackGenome(self.mindStr)

        return

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
            if n >= self.intelligence: break
            
            axon = genome[n * 8: (n + 1) * 8]
            input = int(axon[:2], 16) % len(self.allNeurons)
            output = int(axon[2:4], 16) % len(self.allNeurons)
            factor = int(axon[4:8], 16) / 32768 - 1 # either positive or negative, 8000 being zero
            axon = Axon(input=self.allNeurons[input], output=self.allNeurons[output], factor=factor)
            if axon.input.type in [NeuronType.creature, NeuronType.environment, NeuronType.self]:
                self.senseAxons.append(axon)
            elif axon.input.type == NeuronType.memory:
                self.memoryAxons.append(axon)
            elif axon.input.type == NeuronType.relay:
                self.relayAxons.append(axon)
            elif axon.input.type == NeuronType.action:
                self.actionAxons.append(axon)

        return self.senseAxons + self.memoryAxons + self.relayAxons + self.actionAxons

    def animate(self):
        options = self.processEnvironment(self.getVisionRanges())
        options.append(ActionOption(self.rest, None, self.sprintMoves))
        options.append(ActionOption(self.wander, None, 0.5))
        action = max(*options, key=lambda option: option.weight)
        if action.target:
            action.action(self, action.target)
        else:
            action.action()
        # propagate this action into the net, potentially setting memory neurons or smth
        for neuron in self.actionNeurons: neuron.clear()
        action.neuron.activate(1)
        for axon in self.actionAxons:
            axon.output.activate(axon.input.activation * axon.factor)

    def attack(self, other):
        self.attackTarget = other

    def flee(self, other):
        self.fleeTarget = other

    def mate(self, other):
        self.mateTarget = other

    def wander(self):
        self.moveTarget = random.choice(self.location.neighbors)

    def rest(self):
        self.sprintMoves -= 1

    @property 
    def metabolism(self) -> float:
        # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
        return self.__metabolism + self.sprintMoves / self.stamina

    def getVisionRanges(self) -> list[list[MapNode]]:
        cones = [
            self.location.visionTree[(self.direction + n) % len(self.location.neighbors)][:self.sightRange] 
            for n in [-int(n / 2) if n % 2 == 0 else int(n / 2) + 1 
            for n in range((self.sightField - 1) * 2 + 1)] 
        ]
        visionLayers = [
            # get a separate array of nodes for each distance from self.location
            [node for cone in [[cones[a][b] 
            for a in range(len(cones))] for b in range(self.sightRange)][i] 
            for node in cone] for i in range(self.sightRange)
        ]
        return visionLayers

    def getSimilarity(self, other) -> float:
        similarity = 0.0
        commonRange = range(min(len(self.genome.mindStr), len(other.genome.mindStr)))
        increment = 1/len(commonRange)
        for c in commonRange:
            if self.genome.mindStr[c] == other.genome.mindStr[c]: similarity += increment
        return similarity

    def clearInputs(self):
        for neuron in self.allNeurons:
            neuron.clear()

    def processEnvironment(self, vision:list[list[MapNode]]) -> list[ActionOption]:
        actionOptions: list[ActionOption] = []

        for sensor in self.selfNeurons:
            sensor.sense(self)
        actionOptions.append(self.processStimulus(self, 'self', 1))

        for distance, layer in enumerate(vision):
            for node in layer:
                if (node.occupant):
                    other = node.occupant
                    actionOptions.append(self.processStimulus(other, 'creature', distance + 1))

                if (node.resource):
                    actionOptions.append(self.processStimulus(node.resource, 'resource', distance + 1))

        return actionOptions

    def processStimulus(self, target:any, type:str, distance:float):
        self.clearInputs()
        if type == 'resource':
            for sensor in self.envNeurons:
                sensor.sense(target)
        elif type == 'creature':
            for sensor in self.creatureNeurons:
                sensor.sense(self, target)
                # oh that's quite beautiful 👍

        # the order is important here vvv
        for axon in self.senseAxons + self.memoryAxons + self.relayAxons:
            axon.output.activation += axon.input.activation * axon.factor

        out = max(*[self.actionNeurons], key=lambda n: n.activation)
        return ActionOption(out.action, target, out.activation * 1/distance, out)

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