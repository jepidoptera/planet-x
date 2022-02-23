# good start
# you made a file!
# 288 lines long now. got about ten other files as well
from cgi import MiniFieldStorage
from enum import Enum
import random
from xml.dom import minidom
from creatures.genome import Genome, mergeString
from world.map import *
import typing

class NeuronType(Enum):
    self = 0
    creature = 1
    environment = 2
    memory = 3
    relay = 4
    action = 5

netIndex={'lock': False}
    
class Neuron():
    activation:float
    sense:typing.Callable
    action:typing.Callable
    type:NeuronType
    name:str
    def __init__(self, type: NeuronType, name:str='', sense: typing.Callable=None, action: typing.Callable=None):
        self.activation = 0.0
        self._sense = sense
        self.action = action
        self.type = type
        self.name = name
        if not netIndex['lock']: netIndex[name]=self
    def sense(self, *args):
        self.activate(self._sense(*args))
    def activate(self, amount):
        self.activation += amount
    def clear(self):
        self.activation = 0
# 🙌🏾

class MemNeuron(Neuron):
    sense=None
    action=None
    type=NeuronType.memory
    threshold=0.5
    strength=2.0

    def __init__(self, memstate:bool=True, name:str=''):
        super().__init__(NeuronType.memory, name=name)
        self.memState = memstate
    def activate(self, amount):
        if abs(amount) > self.threshold: self.memState = (sign(amount)+1) / 2
    def clear(self):
        self.activation = self.memState * self.strength

class Axon():
    def __init__(self, input: Neuron, output: Neuron, factor: float):
        self.input = input
        self.output = output
        self.factor = factor

    def __str__(self) -> str:
        return (
            hex(Creature.allNeurons.index(self.input))[2:].zfill(2) + 
            hex(Creature.allNeurons.index(self.output))[2:].zfill(2) +
            hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
        )

class ActionOption():
    def __init__(self, action: typing.Callable, target: any, weight: float, relevantNeuron: Neuron):
        self.action = action
        self.target = target
        self.weight = weight
        self.neuron = relevantNeuron

# class Brain():

class Creature():
    victim: any = None
    fear: any = None
    mate: any = None
    offspring: any = None
    food: Resource = None
    path: list[MapNode] = []

    selfNeurons: list[Neuron]
    creatureNeurons: list[Neuron]
    envNeurons: list[Neuron]
    relayNeurons: list[Neuron]
    actionNeurons: list[Neuron]

    senseAxons: set[Axon]
    memoryAxons: set[Axon]
    relayAxons: set[Axon]
    actionAxons: set[Axon]

    def __init__(self, location:MapNode, genome1:Genome, genome2:Genome=None, energy: float=100):
        if not genome2: genome2=genome1
        self.dead=False
        self._location = location
        location.occupant = self
        self.path=[]
        
        self.genome=[genome1, genome2]
        self.deadliness = (genome1.deadliness + genome2.deadliness)/2
        self.speed = (genome1.speed + genome2.speed)/2
        self.fortitude = (genome1.fortitude + genome2.fortitude)/2
        self.fertility = (genome1.fertility + genome2.fertility)/2
        self.longevity = (genome1.longevity + genome2.longevity)/2
        self.stamina = (genome1.stamina + genome2.stamina)/2
        self.intelligence = (genome1.intelligence + genome2.intelligence)/2
        self.meatEating = (genome1.meatEating + genome2.meatEating)/2
        self.plantEating = (genome1.plantEating + genome2.plantEating)/2
        self.sightRange = int((genome1.sightRange + genome2.sightRange)/2)
        self.sightField = int((genome1.sightField + genome2.sightField)/2)
        self.size = (genome1.size.value + genome2.size.value)/2
        self.mindStr = mergeString(genome1.mindStr, genome2.mindStr, chunk=8)
        self.speciesName=mergeString(*[g.speciesName for g in self.genome])

        self.age = 0
        self._health = self.fortitude
        self.energy = energy
        self.sprintMoves = 0
        self._metabolism = (sum([stat.value * stat.metacost for stat in genome1.stats.values()]) +
            sum([stat.value * stat.metacost for stat in genome2.stats.values()])) / 2000

        self.direction=int(random.random() * len(self.location.neighbors))
        self.thinkTimer=int(random.random() * self.intelligence)
        self.moveTimer=int(random.random() * self.speed)

        # instantiate memory neurons specific to this creature 
        # the rest are shared across all creatures to save space
        # memory needs to be specific to each creature, though
        self.memNeurons:list[Neuron] = [MemNeuron(False, name=f'memory_{n}') for n in range(8)]
        self.allNeurons:list[Neuron] = self.creatureNeurons + self.selfNeurons + self.envNeurons + self.memNeurons + self.relayNeurons + self.actionNeurons
        self.unpackGenome(self.mindStr)

        self.processStimulus('birth')
        return

    @property 
    def metabolism(self) -> float:
        # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
        return self._metabolism + self.sprintMoves / self.stamina

    @property
    def location(self) -> MapNode:
        return self._location

    @location.setter
    def location(self, newlocation: MapNode):
        self._location.occupant = None
        self._location = newlocation
        newlocation.occupant = self
        return self.location

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value):
        self._health = min(value, self.fortitude)
        if self.health <= 0:
            self.die()

    def fromHex(self, hexcode) -> Axon:
        input = int(hexcode[:2], 16) % len(self.allNeurons)
        output = int(hexcode[2:4], 16) % len(self.allNeurons)
        factor = int(hexcode[4:8], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
        return Axon(input=self.allNeurons[input], output=self.allNeurons[output], factor=factor)

    def unpackGenome(self, genome) -> list[Axon]:
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
            
            axon = self.fromHex(genome[n * 8: (n + 1) * 8])
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
        if self.dead: return 'dead'

        if self.health < self.fortitude:
            self.health += self.fortitude/1000
            self.energy -= self.fortitude/1000
        self.energy -= self.metabolism
        if self.energy < 0: 
            self.health += self.energy
            self.energy = 0
        self.age += .01

        if self.age > self.longevity * 100:
            self.die()
            return 'action_die'

        if self.food and self.location.resource == self.food:
            bitesize=1
            energyValue=0
            if self.food.type == ResourceType.meat:
                bitesize=min(self.meatEating, self.food.value)
                energyValue=self.meatEating*bitesize/7
            elif self.food.type == ResourceType.grass:
                bitesize=min(self.plantEating, self.food.value)
                energyValue=self.plantEating*bitesize/7
            elif self.food.type == ResourceType.fruit:
                bitesize=min(self.plantEating, self.food.value)
                energyValue=self.plantEating*bitesize/7
            self.food.value -= bitesize
            self.energy += energyValue
            # all gone
            if self.food.value <= 0: self.location.resource = None
            return 'action_eat'

        elif self.victim and self.victim.location in self.location.neighbors:
            self.direction=self.location.neighbors.index(self.victim.location)
            self.victim.health -= self.deadliness
            Creature.processStimulus(self.victim, type='injury', magnitude=self.deadliness)
            if self.victim.dead: self.victim = None 
            return 'action_attack'

        elif self.mate and self.mate.location in self.location.neighbors:
            if self.energy > self.size:
                self.energy /= 2
                self.fertility -= 1
                self.offspring=Creature(
                    self.location, 
                    Genome.merge(*self.genome).mutate(), 
                    Genome.merge(*self.mate.genome).mutate(), 
                    energy=self.energy
                )
            
        # move along the path
        elif (self.path):
            nextMove=self.path.pop(0)
            if nextMove.occupant:
                self.path = []
            else:
                self.location.occupant = None
                self.direction=self.location.neighbors.index(nextMove)
                self.location=nextMove
                self.location.occupant = self
                self.direction=min(self.direction, len(self.location.neighbors)-1)
                self.sprintMoves += 1

        else:
            self.sprintMoves -= 1
            
    def seekFood(self, foodLocation: MapNode):
        self.food = foodLocation.resource
        if self.location == foodLocation:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, foodLocation)

    def attack(self, other):
        self.victim = other
        if other.location in self.location.neighbors:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, other.location)

    def flee(self, other):
        self.fear = other
        away=max([n for n in self.location.neighbors], key=lambda n: Map.getDistance(n, other.location))
        self.path=[away]
        # vvv saved this old code just to compare with the elegance of this ^^^
        # toOther=Map.findPath(self.location, other.location)
        # self.direction=(self.location.neighbors.index(toOther[0])+int(len(self.location.neighbors)/2))%len(self.location.neighbors)
        # self.path=[self.location.neighbors[self.direction]]

    def seekMate(self, other):
        self.mate = other
        if self.mate.location in self.location.neighbors:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, other.location)

    def wander(self, _=None):
        # works
        self.path = [random.choice(self.location.neighbors)]

    def turnLeft(self, _=None):
        # works
        self.direction=(self.direction - 1 + len(self.location.neighbors)) % len(self.location.neighbors)

    def turnRight(self, _=None):
        self.direction=(self.direction + 1) % len(self.location.neighbors)

    def moveForward(self, _=None):
        self.path=[self.location.neighbors[self.direction]]

    def rest(self, _=None):
        self.path=[]

    def die(self):
        self.location.resource=Resource(ResourceType.meat, self.energy + self.size)
        self.location.occupant=None
        self.dead=True

    def think(self) -> str:
        options = self.processEnvironment(self.getVisionRanges())
        # exhaustion
        options.append(ActionOption(self.rest, None, self.sprintMoves / self.stamina, netIndex['action_rest']))
        # wandering
        options.append(ActionOption(self.wander, None, 0.1, netIndex['action_wander']))
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

        return action.neuron.name

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
        return [[self.location]] + visionLayers

    def getSimilarity(self, other) -> float:
        similarity = 0.0
        commonRange = range(min(len(self.speciesName), len(other.speciesName)))
        increment = 1/len(commonRange)
        for c in commonRange:
            if self.mindStr[c] == other.mindStr[c]: similarity += increment
        return similarity

    def clearInputs(self):
        for neuron in self.allNeurons:
            neuron.clear()

    def processEnvironment(self, vision:list[list[MapNode]]) -> list[ActionOption]:
        actionOptions: list[ActionOption] = []

        for distance, layer in enumerate(vision):
            for node in layer:
                if (node.occupant==self):
                    actionOptions.append(self.processStimulus(target=self, type='self', magnitude=1))
            
                elif (node.occupant):
                    other = node.occupant
                    actionOptions.append(self.processStimulus(type='creature', target=other, magnitude=1))

                if (node.resource):
                    actionOptions.append(self.processStimulus(type='food', target=node, magnitude=min(node.resource.value, 10.0/(distance+1))))

        return actionOptions

    def processStimulus(self, type:str, target:any=None,  magnitude:float=1.0):
        self.clearInputs()
        for sensor in self.selfNeurons:
            sensor.sense(self)
        if type == 'food':
            for sensor in self.envNeurons:
                sensor.sense(target.resource)
        elif type == 'creature':
            for sensor in self.creatureNeurons:
                sensor.sense(self, target)
                # oh that's quite beautiful 👍
        elif type == 'birth':
            netIndex['self_birth'].activate(7)
        elif type == 'injury':
            netIndex['self_injury'].activate(magnitude)

        # the order is important here vvv
        for axon in self.senseAxons + self.memoryAxons + self.relayAxons:
            axon.output.activate(axon.input.activation * axon.factor)

        if target == self or target == None:
            netIndex['action_attack'].clear()
            netIndex['action_eat'].clear()
            netIndex['action_mate'].clear()
        if type == 'food':
            netIndex['action_attack'].clear()
            netIndex['action_flee'].clear()
            netIndex['action_mate'].clear()
        if type == 'creature':
            netIndex['action_attack'].activation += netIndex['action_eat'].activation
            netIndex['action_eat'].clear()

        out = max(*[self.actionNeurons], key=lambda n: n.activation)
        return ActionOption(out.action, target, out.activation * magnitude, out)

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

Creature.creatureNeurons=list[Neuron]([
    Neuron(NeuronType.creature, name='creature_deadliness', sense=lambda self, other: other.deadliness - self.deadliness),
    Neuron(NeuronType.creature, name='creature_age', sense=lambda self, other: other.age / other.longevity),
    Neuron(NeuronType.creature, name='creature_health', sense=lambda self, other: other.health),
    Neuron(NeuronType.creature, name='creature_similarity', sense=lambda self, other: self.getSimilarity(other)),
    Neuron(NeuronType.creature, name='creature_speed', sense=lambda self, other: other.speed - self.speed),
    Neuron(NeuronType.creature, name='creature_size', sense=lambda self, other: other.size)
])

Creature.selfNeurons=list[Neuron]([
    Neuron(NeuronType.self, name='self_energy', sense=lambda self: self.energy),
    Neuron(NeuronType.self, name='self_health', sense=lambda self: self.health),
    Neuron(NeuronType.self, name='self_age', sense=lambda self: self.age),
    Neuron(NeuronType.self, name='self_sprints', sense=lambda self: self.sprintMoves),
    Neuron(NeuronType.self, name='self_birth', sense=lambda self: 0), # just born
    Neuron(NeuronType.self, name='self_injury', sense=lambda self: 0), # under attack 
])

Creature.envNeurons=list[Neuron]([
    Neuron(NeuronType.environment, name='see_meat', sense=lambda resource: 1 if resource.type==ResourceType.meat else 0),
    Neuron(NeuronType.environment, name='see_fruit', sense=lambda resource: 1 if resource.type==ResourceType.fruit else 0),
    Neuron(NeuronType.environment, name='see_grass', sense=lambda resource: 1 if resource.type==ResourceType.grass else 0),
    Neuron(NeuronType.environment, name='see_tree', sense=lambda resource: 1 if resource.type==ResourceType.tree else 0)
])

Creature.relayNeurons=list[Neuron]([Neuron(NeuronType.relay, name=f'relay_{n}') for n in range(8)])

Creature.actionNeurons=list[Neuron]([
    Neuron(NeuronType.action, name='action_attack', action=Creature.attack),
    Neuron(NeuronType.action, name='action_flee', action=Creature.flee),
    Neuron(NeuronType.action, name='action_mate', action=Creature.seekMate),
    Neuron(NeuronType.action, name='action_eat', action=Creature.seekFood),
    Neuron(NeuronType.action, name='action_turnleft', action=Creature.turnLeft),
    Neuron(NeuronType.action, name='action_turnright', action=Creature.turnRight),
    Neuron(NeuronType.action, name='action_move', action=Creature.moveForward),
    Neuron(NeuronType.action, name='action_rest', action=Creature.rest),
    Neuron(NeuronType.action, name='action_wander', action=Creature.wander) 
])

# these are class level placeholders
Creature.memNeurons=list[Neuron]([MemNeuron(False, name=f'memory_{n}') for n in range(8)])

# leave in place. this one too
Creature.allNeurons=list[Neuron](
    Creature.creatureNeurons + 
    Creature.selfNeurons + 
    Creature.envNeurons + 
    Creature.memNeurons + 
    Creature.relayNeurons + 
    Creature.actionNeurons
)
netIndex['lock']=True

if __name__ == "__main__":
    print("creature.py is main file")
#     map = Map(20, 14)
#     c = Creature(map, map.nodes[150], randomGenome(), 100.0)