# good start
# you made a file!
# 288 lines long now. got about ten other files as well
from cgi import MiniFieldStorage
from enum import Enum
import random
from creatures.genome import Genome, mergeString
from world.map import *
import typing

class NeuronType(Enum):
    self=0
    creature=1
    environment=2
    memory=3
    relay=4
    action=5

class Neuron():
    activation:float
    sense:typing.Callable
    action:typing.Callable
    type:NeuronType
    name:str
    bias:float
    def __init__(self, type: NeuronType, name:str='', sense: typing.Callable=None, action: typing.Callable=None, bias: float=0.0):
        self.activation=0.0
        self._sense=sense
        self.action=action
        self.type=type
        self.name=name
        self.bias=bias
        if not name in netIndex: netIndex[name]=self
    def sense(self, *args):
        self.activate(self._sense(*args))
    def activate(self, amount):
        self.activation += amount
    def clear(self):
        self.activation=self.bias
# 🙌🏾

class MemNeuron(Neuron):
    sense=None
    action=None
    type=NeuronType.memory
    threshold=0.5
    strength=1.0

    def __init__(self, memstate:bool=True, name:str=''):
        super().__init__(NeuronType.memory, name=name)
        self.memState=memstate
    def activate(self, amount):
        if abs(amount) > self.threshold: self.memState=1 if amount > 0 else 0
        self.clear()
    def clear(self):
        self.activation=self.memState * self.strength

class Axon():
    def __init__(self, input: Neuron, output: Neuron, factor: float):
        self.input=input
        self.output=output
        self.factor=factor


    def fire(self):
        self.output.activate(self.input.activation * self.factor)

    def __str__(self) -> str:
        return (
            hex(Creature.allNeurons.index(self.input))[2:].zfill(2) + 
            hex(Creature.allNeurons.index(self.output))[2:].zfill(2) +
            hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
        )

class DoubleAxon(Axon):
    operators={
        'and': 0,
        'or': 1,
        'nor': 2,
        'xor': 3
    }
    def __init__(self, input: list[Neuron], output: Neuron, threshold: float, operator: int, factor: float):
        
        self._input=input
        self.output: Neuron=output
        self.threshold=threshold
        self.factor=factor
        self.operator=operator

    def fire(self):
        # there is room for up to 256 different operators
        # just probably gonna use 8
        if self.operator == 0:
            # AND
            if (self._input[0].activation > self.threshold and self._input[1].activation > self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 1:
            # OR
            if (self._input[0].activation > self.threshold or self._input[1].activation > self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 2:
            # NOR 
            if (self._input[0].activation < self.threshold and self._input[1].activation < self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 3:
            # XOR
            if (self._input[0].activation > self.threshold ^ self._input[1].activation > self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)

    @property
    def input(self):
        return self._input[0]

    @property
    def input2(self):
        return self._input[1]

    def __str__(self) -> str:
        return (
            'FF' + 
            hex(self.operator)[2:].zfill(2) + 
            hex(int(self.threshold * 0xff))[2:].zfill(2) + 
            hex(Creature.allNeurons.index(self._input[0]))[2:].zfill(2) + 
            hex(Creature.allNeurons.index(self._input[1]))[2:].zfill(2) + 
            hex(Creature.allNeurons.index(self.output))[2:].zfill(2) +
            hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
        )


class ActionOption():
    def __init__(self, action: typing.Callable, target: any, weight: float, relevantNeuron: Neuron):
        self.action=action
        self.target=target
        self.weight=weight
        self.neuron=relevantNeuron

# class Brain():

netIndex: dict[str, Neuron]={}
    
class Creature():
    victim: any=None
    fear: any=None
    mate: any=None
    offspring: any=None
    food: Resource=None
    path: list[MapNode]=[]

    selfNeurons: list[Neuron]
    creatureNeurons: list[Neuron]
    envNeurons: list[Neuron]
    relayNeurons: list[Neuron]
    actionNeurons: list[Neuron]

    selfAxons: set[Axon]
    creatureAxons: set[Axon]
    envAxons: set[Axon]
    memoryAxons: set[Axon]
    relayAxons: set[Axon]
    actionAxons: set[Axon]

    def __init__(self, 
            location: MapNode, 
            genome: list[Genome],
            energy: float=100, 
            speciesName: str='',
            offspringCount: int=0,
            brain: str='',
            age: int=0,
            mutate: bool=False
        ):

        self._dead=False
        self._location=location
        location.occupant=self
        self.path=[]
        
        self.genome=genome
        if type(self.genome) != list:
            raise Exception('list[Genome] expected')

        if mutate:
            for g in self.genome:
                g.mutate()

        genome=self.genome
        self.deadliness=sum([g.deadliness for g in genome])/len(genome)
        self.speed=sum([g.speed for g in genome])/len(genome)
        self.fortitude=sum([g.fortitude for g in genome])/len(genome)
        self.fertility=sum([g.fertility for g in genome])/len(genome)
        self._longevity=sum([g.longevity for g in genome])/len(genome)
        self.stamina=sum([g.stamina for g in genome])/len(genome)
        self.intelligence=sum([g.intelligence for g in genome])/len(genome)
        self.meateating=sum([g.meateating for g in genome])/len(genome)
        self.planteating=sum([g.planteating for g in genome])/len(genome)
        self.sightrange=int(sum([g.sightrange for g in genome])/len(genome))
        self.sightfield=int(sum([g.sightfield for g in genome])/len(genome))
        self.size=sum([g.size.value for g in genome])/len(genome)
        self.brain=brain or mergeString(*[g.brain for g in genome], chunk=8)
        self.speciesName=speciesName or mergeString(*[g.variant for g in genome])

        self.age=age
        self.offspringCount=offspringCount
        self._health=self.fortitude
        self.energy=energy
        self.sprintMoves=0
        self._metabolism=(sum([sum([stat.value * stat.metacost for stat in g.stats.values()]) for g in genome])) / (3500 * len(genome))

        self.direction=int(random.random() * len(self.location.neighbors))
        self.thinkTimer=int(random.random() * self.intelligence)
        self.moveTimer=int(random.random() * self.speed)

        # instantiate memory neurons specific to this creature 
        # the rest are shared across all creatures to save space
        # memory needs to be specific to each creature, though
        self.memNeurons:list[Neuron]=[MemNeuron(False, name=f'memory_{n}') for n in range(8)]
        self.allNeurons:list[Neuron]=self.creatureNeurons + self.selfNeurons + self.envNeurons + self.memNeurons + self.relayNeurons + self.actionNeurons
        self.unpackGenome(self.brain)

        self.clearInputs()
        self.processStimulus('birth')
        return

    @property
    def longevity(self) -> float:
        return self._longevity * 100 # lifespan in frames

    @property 
    def metabolism(self) -> float:
        # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
        return self._metabolism*(max(self.sprintMoves, 1)/self.stamina)

    @property
    def location(self) -> MapNode:
        return self._location

    @location.setter
    def location(self, newlocation: MapNode):
        self._location.occupant=None
        self._location=newlocation
        newlocation.occupant=self
        return self.location

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value):
        self._health=min(value, self.fortitude)
        if self.health <= 0:
            self.die()

    @property
    def dead(self) -> bool:
        return self._dead

    @dead.setter
    def dead(self, value):
        if value:
            self.die()
            return True
        return False

    def fromHex(self, hexcode) -> Axon:

        if len(hexcode) == 8:
            input=int(hexcode[:2], 16) % len(self.allNeurons)
            output=int(hexcode[2:4], 16) % len(self.allNeurons)
            factor=int(hexcode[4:8], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
            return Axon(input=self.allNeurons[input], output=self.allNeurons[output], factor=factor)

        elif len(hexcode) == 16:
            operator=int(hexcode[2:4], 16)//0xf8
            threshold=int(hexcode[4:6], 16)/0xff
            input1=int(hexcode[6:8], 16) % len(self.allNeurons)
            input2=int(hexcode[8:10], 16) % len(self.allNeurons)
            output=int(hexcode[10:12], 16) % len(self.allNeurons)
            factor=int(hexcode[12:16], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
            return DoubleAxon(
                input=[self.allNeurons[n] for n in [input1, input2]], 
                output=self.allNeurons[output],
                threshold=threshold,
                operator=operator,
                factor=factor
            )

        else:
            raise Exception(f"invalid hex code length ({len(hexcode)}), can't generate axon")

    def unpackGenome(self, genome) -> list[Axon]:
        # first two digits are input neuron
        # second two are output
        # what are possible outputs?
        # attack, mate, eat, flee, wander, think (which), remember (which)
        doubleAxon=False
        self.actionAxons=[]
        self.relayAxons=[]
        self.memoryAxons=[]
        self.creatureAxons=[]
        self.envAxons=[]
        self.selfAxons=[]
        for n in range(int(len(genome)/8)):
            # if n >= self.intelligence: break
            if doubleAxon:
                doubleAxon=False
                continue
            
            if int(genome[n*8: n*8 + 2], 16) != 0xff:
                axon=self.fromHex(genome[n * 8: (n + 1) * 8])
            else:
                axon=self.fromHex(genome[n*8: (n+2)*8])
                doubleAxon=True

            if (axon.input.type == NeuronType.action
                or type(axon) == DoubleAxon 
                and axon.input2.type == NeuronType.action
            ):
                self.actionAxons.append(axon)

            elif (axon.input.type == NeuronType.relay
                or type(axon) == DoubleAxon 
                and axon.input2.type == NeuronType.relay
            ):
                self.relayAxons.append(axon)

            elif (axon.input.type == NeuronType.creature
                or type(axon) == DoubleAxon 
                and axon.input2.type == NeuronType.creature
            ):
                self.creatureAxons.append(axon)

            elif (axon.input.type == NeuronType.environment
                or type(axon) == DoubleAxon 
                and axon.input2.type == NeuronType.environment
            ):
                self.envAxons.append(axon)

            elif (axon.input.type == NeuronType.self
                or type(axon) == DoubleAxon 
                and axon.input2.type == NeuronType.self
            ):
                self.selfAxons.append(axon)

            elif (axon.input.type == NeuronType.memory
                or type(axon) == DoubleAxon 
                and axon.input2.type == NeuronType.memory
            ):
                self.memoryAxons.append(axon)

        return self.creatureAxons + self.envAxons + self.selfAxons + self.memoryAxons + self.relayAxons + self.actionAxons

    def animate(self) -> str:
        if self.speciesName == 'tigerwolf':
            er=1

        if self._dead: return 'dead'

        # heal
        if self.health < self.fortitude:
            self.health += self.fortitude/100
            self.energy -= self.fortitude/100
        if self.energy < 0: 
            self.health += self.energy
            self.energy=0

        if self.food and self.location.resource == self.food:
            bitesize=1
            energyValue=0
            if self.food.type == ResourceType.meat:
                bitesize=min(self.meateating, self.food.value)
                energyValue=self.meateating*bitesize/7
            elif self.food.type == ResourceType.grass:
                bitesize=min(self.planteating, self.food.value)
                energyValue=self.planteating*bitesize/7
            elif self.food.type == ResourceType.fruit:
                bitesize=min(self.planteating, self.food.value)
                energyValue=self.planteating*bitesize/7
            self.food.value -= bitesize
            self.energy += energyValue
            # all gone
            if self.food.value <= 0: self.location.resource=None
            return 'action_eat'

        elif self.victim and self.victim.location in self.location.neighbors:
            self.direction=self.location.neighbors.index(self.victim.location)
            self.victim.health -= self.deadliness
            Creature.processStimulus(self.victim, stimulusType='injury', target=self, magnitude=self.deadliness)
            if self.victim.dead: self.victim=None 
            return 'action_attack'

        elif self.mate and self.mate.location in self.location.neighbors:
            if self.energy > self.size:
                self.energy -= self.size
                self.energy /= 2
                self.fertility -= 1
                self.offspring=Creature(
                    self.location, 
                    [
                        Genome.merge(*self.genome).mutate(), 
                        Genome.merge(*self.mate.genome).mutate()
                    ], 
                    energy=self.energy,
                    speciesName=mergeString(self.speciesName, self.mate.speciesName)
                )
                self.offspringCount += 1
            return 'action_mate'
            
        # move along the path
        elif (self.path):
            nextMove=self.path.pop(0)
            if nextMove.occupant:
                self.path=[]
                return 'action_blocked'
            else:
                self.location.occupant=None
                self.direction=self.location.neighbors.index(nextMove)
                self.location=nextMove
                self.location.occupant=self
                self.direction=min(self.direction, len(self.location.neighbors)-1)
                self.sprintMoves += 1
            return 'action_move'
        else:
            self.sprintMoves=min(self.sprintMoves - 1, 0)
            return 'action_rest'
            
    def seekFood(self, foodLocation: MapNode):
        self.food=foodLocation.resource
        if self.location == foodLocation:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, foodLocation)

    def attack(self, other):
        self.victim=other
        if other.location in self.location.neighbors:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, other.location)

    def flee(self, other):
        self.fear=other
        self.path=Map.fleePath(self.location, other.location, safeDistance=9)
        # vvv saved this old code just to compare with the elegance of this ^^^
        # toOther=Map.findPath(self.location, other.location)
        # self.direction=(self.location.neighbors.index(toOther[0])+int(len(self.location.neighbors)/2))%len(self.location.neighbors)
        # self.path=[self.location.neighbors[self.direction]]

    def seekMate(self, other):
        self.mate=other
        if self.mate.location in self.location.neighbors:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, other.location)

    def wander(self, _=None):
        # works
        self.path=[random.choice(self.location.neighbors)]

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
        self._dead=True

    def think(self) -> str:
        self.clearInputs()
        options=[self.processStimulus(target=self)]

        options += self.processVision(self.getVisionRanges())
        # exhaustion
        options.append(ActionOption(Creature.rest, self, self.sprintMoves / self.stamina, netIndex['action_rest']))

        action=max(*options, key=lambda option: option.weight)
        # if action.target:
        action.action(self, action.target)
        # else:
        #     action.action()
        # propagate this action into the net, potentially setting memory neurons or smth
        for neuron in self.actionNeurons: neuron.clear()
        action.neuron.activate(1)
        for axon in self.actionAxons:
            axon.fire()

        return action.neuron.name

    def getVisionRanges(self) -> list[list[MapNode]]:
        cones=[
            self.location.visionTree[(self.direction + n) % len(self.location.neighbors)][:self.sightrange] 
            for n in [-int(n / 2) if n % 2 == 0 else int(n / 2) + 1 
            for n in range((self.sightfield - 1) * 2 + 1)] 
        ]
        visionLayers=[
            # get a separate array of nodes for each distance from self.location
            [node for cone in [[cones[a][b] 
            for a in range(len(cones))] for b in range(self.sightrange)][i] 
            for node in cone] for i in range(self.sightrange)
        ]
        return [[self.location]] + visionLayers

    def getSimilarity(self, other) -> float:
        similarity=0.0
        commonRange=range(min(len(self.speciesName), len(other.speciesName)))
        increment=1/len(commonRange)
        for c in commonRange:
            if self.speciesName[c] == other.speciesName[c]: similarity += increment
        return similarity

    def clearInputs(self):
        for neuron in self.allNeurons:
            neuron.clear()

    def processVision(self, vision:list[list[MapNode]]) -> list[ActionOption]:
        actionOptions: list[ActionOption]=[]

        for distance, layer in enumerate(vision):
            for node in layer:
                if (node.occupant and node.occupant != self):
                    other=node.occupant
                    actionOptions.append(self.processStimulus(stimulusType='creature', target=other, magnitude=1))

                if (node.resource):
                    if node.resource.type == ResourceType.grass and netIndex['see_grass'].activation: continue
                    if node.resource.type == ResourceType.meat and netIndex['see_meat'].activation: continue
                    actionOptions.append(self.processStimulus(stimulusType='food', target=node, magnitude=min(node.resource.value, 10.0/(distance+1))))

        return actionOptions

    def processStimulus(self, stimulusType:str='', target:any=None,  magnitude:float=1.0):
        if not target: target=self
        for neuron in self.creatureNeurons + self.relayNeurons + self.actionNeurons:
            neuron.clear()

        if stimulusType == 'birth':
            netIndex['self_birth'].activate(1)
        elif stimulusType == 'injury':
            netIndex['self_injury'].activate(magnitude)

        # if target == self:
        for sensor in self.selfNeurons:
            sensor.sense(self)
        for axon in self.selfAxons:
            axon.fire()
        
        if type(target) == MapNode:
            for sensor in self.envNeurons:
                sensor.sense(target.resource)
            for axon in self.envAxons:
                axon.fire()
        elif type(target) == Creature:
            for sensor in self.creatureNeurons:
                sensor.sense(self, target)
                # oh that's quite beautiful 👍
            for axon in self.creatureAxons:
                axon.fire()

        # the order is important here vvv
        for axon in self.memoryAxons + self.relayAxons:
            axon.fire()

        if target == self:
            netIndex['action_attack'].clear()
            netIndex['action_eat'].clear()
            netIndex['action_mate'].clear()
        if stimulusType == 'food':
            netIndex['action_attack'].clear()
            netIndex['action_flee'].clear()
            netIndex['action_mate'].clear()
        if stimulusType == 'creature':
            netIndex['action_attack'].activation += netIndex['action_eat'].activation
            netIndex['action_eat'].clear()
            if self.energy < self.size: netIndex['action_mate'].clear()
            if netIndex['creature_similarity'].activation < 0.5: 
                netIndex['action_mate'].clear()
                # self.energy -= 1

        out=max(*[self.actionNeurons], key=lambda n: n.activation)
        return ActionOption(out.action, target, out.activation * magnitude, out)

    def printStats(self):
        print('deadliness: ', self.deadliness)
        print('speed: ', self.speed)
        print('fortitude: ', self.fortitude)
        print('stamina: ', self.stamina)
        print('meat eating: ', self.meateating)
        print('plant eating: ', self.planteating)
        print('intelligence: ', self.intelligence)
        print('sight range: ', self.sightrange)
        print('field of view: ', self.sightfield)
        print('brain dna: ', self.brain)

        print('age: ', self.age)
        print('health: ', self.health)
        print('energy: ', self.energy)
        print(f'location x:{self.location.x}, y:{self.location.y}')

    def toJson(self) -> dict:
        return {
            'genomes': [self.genome[n].encode() for n in range(len(self.genome))],
            # {
            #     'mutations': self.genome[n].mutations,
            #     'deadliness': self.genome[n]._deadliness,
            #     'speed': self.genome[n]._speed,
            #     'stamina': self.genome[n]._stamina,
            #     'fortitude': self.genome[n]._fortitude,
            #     'intelligence': self.genome[n]._intelligence,
            #     'longevity': self.genome[n]._longevity,
            #     'fertility': self.genome[n]._fertility,
            #     'meateating': self.genome[n]._meateating,
            #     'planteating': self.genome[n]._planteating,
            #     'sightrange': self.genome[n]._sightrange,
            #     'sightfield': self.genome[n]._sightfield,
            #     'brain': self.genome[n].brain,
            # } 
            'age': self.age,
            'brain': self.brain,
            'energy': self.energy,
            'location': self.location.index,
            'speciesName': self.speciesName,
            'offspring': self.offspringCount
        }

def fromJson(j:dict, location: MapNode=MapNode()) -> Creature:
    return Creature(
        location=location,
        genome=[
            Genome.decode(g)
            # (
            #     mutations=genome['mutations'],
            #     deadliness=genome['deadliness'],
            #     speed=genome['speed'],
            #     stamina=genome['stamina'],
            #     fortitude=genome['fortitude'],
            #     intelligence=genome['intelligence'],
            #     longevity=genome['longevity'],
            #     fertility=genome['fertility'],
            #     meateating=genome['meateating'],
            #     planteating=genome['planteating'],
            #     sightrange=genome['sightrange'],
            #     sightfield=genome['sightfield'],
            #     brain=genome['brain'],
            # ) 
            for g in j['genomes']
        ], 
        brain=j['brain'] if 'brain' in j else '',
        speciesName=j['speciesName'] if 'speciesName' in j else '',
        offspringCount=j['offspring'] if 'offspring' in j else 0,
        energy=float(j['energy']) if 'energy' in j else 100,
        age=int(j['age']) if 'age' in j else 0
    )

Creature.fromJson=staticmethod(fromJson)

Creature.creatureNeurons=list[Neuron]([
    Neuron(NeuronType.creature, name='creature_deadliness', sense=lambda self, other: other.deadliness - self.deadliness),
    Neuron(NeuronType.creature, name='creature_age', sense=lambda self, other: other.age/other.longevity),
    Neuron(NeuronType.creature, name='creature_health', sense=lambda self, other: other.health),
    Neuron(NeuronType.creature, name='creature_similarity', sense=lambda self, other: self.getSimilarity(other)),
    Neuron(NeuronType.creature, name='creature_speed', sense=lambda self, other: other.speed - self.speed),
    Neuron(NeuronType.creature, name='creature_size', sense=lambda self, other: other.size)
])

Creature.selfNeurons=list[Neuron]([
    Neuron(NeuronType.self, name='self_energy', sense=lambda self: self.energy * 0.01),
    Neuron(NeuronType.self, name='self_health', sense=lambda self: self.health),
    Neuron(NeuronType.self, name='self_age', sense=lambda self: self.age/self.longevity),
    Neuron(NeuronType.self, name='self_sprints', sense=lambda self: self.sprintMoves),
    Neuron(NeuronType.self, name='self_birth', sense=lambda self: 0), # just born
    Neuron(NeuronType.self, name='self_injury', sense=lambda self: 0), # under attack
    Neuron(NeuronType.self, name='self_always', sense=lambda self: True),
    Neuron(NeuronType.self, name='self_sometimes', sense=lambda self: int(self.age % 7) == 0), 
    Neuron(NeuronType.self, name='self_rarely', sense=lambda self: int(self.age % 77) == 0) 
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
    Neuron(NeuronType.action, name='action_rest', action=Creature.rest, bias=0.1),
    Neuron(NeuronType.action, name='action_wander', action=Creature.wander, bias=0.1) 
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
