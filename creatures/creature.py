# good start
# you made a file!
# 288 lines long now. got about ten other files as well
# ok now it's 762 lines
import math
import random
from creatures.genome import Genome, mergeString, modString
from world.map import *
from creatures.brain import Action, Stimulus
debug=-1

class Creature():
    victim: any=None
    fear: any=None
    mate: any=None
    offspring: any=None
    food: Resource=None
    path: list[MapNode]=[]

    def __init__(self, 
            location: MapNode, 
            genomes: list[Genome],
            energy: float=100, 
            speciesName: str='',
            offspringCount: int=0,
            axonStr: str='',
            neuronStr: str='',
            age: int=0,
            mutate: bool=False,
            brain: any=None
        ):

        self.uniqueID=self.__hash__()
        self._dead=False
        self._location=location
        location.occupant=self
        self.path=[]
        self.genome=genomes

        if type(self.genome) != list:
            raise Exception('list[Genome] expected')

        if mutate:
            for g in self.genome:
                g.mutate()

        self.deadliness=sum([g.deadliness for g in self.genome])/len(genomes)
        self._speed=sum([g.speed for g in self.genome])/len(genomes)
        self.fortitude=sum([g.fortitude for g in self.genome])/len(genomes)
        self.fertility=sum([g.fertility for g in self.genome])/len(genomes)
        self._longevity=sum([g.longevity for g in self.genome])/len(genomes)
        self.stamina=sum([g.stamina for g in self.genome])/len(genomes)
        self.intelligence=sum([g.intelligence for g in self.genome])/len(genomes)
        self.meateating=sum([g.meateating for g in self.genome])/len(genomes)
        self.planteating=sum([g.planteating for g in self.genome])/len(genomes)
        self.sightrange=int(sum([g.sightrange for g in self.genome])/len(genomes))
        self.sightfield=int(sum([g.sightfield for g in self.genome])/len(genomes))
        self.size=sum([g.size.value for g in self.genome])/len(genomes)
        self.axonStr=axonStr or mergeString(*[g.axonStr for g in self.genome], chunk=8)
        self.neuronStr=neuronStr or mergeString(*[g.neuronStr for g in self.genome], chunk=8)
        self.speciesName=speciesName or mergeString(*[g.variant for g in self.genome])

        self.action=Action.rest
        self.age=age
        self.justBorn=(self.age==0)
        self.offspringCount=offspringCount
        self._health=self.fortitude
        self.energy=energy
        self.sprints=0
        self.rests=0
        self._metabolism=(
            sum([sum([stat.value * stat.metacost for stat in g.stats.values()]) 
            for g in genomes])
            / len(genomes))

        self.direction=int(random.random() * len(self.location.neighbors))
        self.thinkTimer=int(random.random() * self.intelligence)
        self.moveTimer=int(random.random() * self._speed)

        self.brain = brain
        self.brain.unpack(self.axonStr, self.neuronStr)

        self.brain.process(Stimulus('birth', 0))

    @property
    def longevity(self) -> float:
        return self._longevity*1000 # lifespan in frames

    @longevity.setter
    def longevity(self, value) -> float:
        self._longevity=value*1000
        return self._longevity

    @property 
    def metabolism(self) -> float:
        # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
        return self._metabolism # + self._metabolism*(max(self.sprints, 1))

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

    @property
    def speed(self):
        return self._speed * (2 if self.sprints else 1) * (1-self.age**2/self.longevity**2)

    @speed.setter
    def speed(self, value):
        self._speed=value
        return self.speed

    # def fromHex(self, hexcode) -> Axon:

    #     if len(hexcode) == 8:
    #         input=int(hexcode[:2], 16) % len(self.allNeurons)
    #         output=int(hexcode[2:4], 16) % len(self.allNeurons)
    #         factor=int(hexcode[4:8], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
    #         return Axon(input=self.allNeurons[input], output=self.allNeurons[output], factor=factor)

    #     elif len(hexcode) == 16:
    #         operator=int(hexcode[2:4], 16) % 0xf8
    #         threshold=int(hexcode[4:6], 16)/0xff
    #         input1=int(hexcode[6:8], 16) % len(self.allNeurons)
    #         input2=int(hexcode[8:10], 16) % len(self.allNeurons)
    #         output=int(hexcode[10:12], 16) % len(self.allNeurons)
    #         factor=int(hexcode[12:16], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
    #         return DoubleAxon(
    #             input=[self.allNeurons[n] for n in [input1, input2]], 
    #             output=self.allNeurons[output],
    #             threshold=threshold,
    #             operator=operator,
    #             factor=factor
    #         )

    def animate(self) -> str:
        if self.speciesName == 'tigerwolf':
            er=1

        self.justBorn=False

        if self._dead: return 'dead'

        # heal
        if self.health < self.fortitude:
            self.health += self.fortitude/100
            self.energy -= self.fortitude/100
        if self.energy < 0: 
            self.health += self.energy
            self.energy=0
        # un sprint
        self.sprints = max(self.sprints-1, 0)

        if self.action == Action.eat and self.food:
            if self.location.resource == self.food:
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

        elif self.action == Action.attack and self.victim:
            if self.victim.location in self.location.neighbors:
                self.direction=self.location.neighbors.index(self.victim.location)
                self.victim.health -= self.deadliness
                Creature.processStimulus(self.victim, stimulusType='injury', target=self, magnitude=self.deadliness)
                if self.victim.dead: self.victim=None
            elif Map.getDistance(self.location, self.victim.location) > self.sightrange:
                # lost them
                self.victim=None

        elif self.action == Action.flee and self.fear:
            if self.path == []: self.path=Map.fleePath(self.location, self.fear.location, safeDistance=self.stamina)

        elif self.action == Action.mate and self.mate:
            if self.mate.location in self.location.neighbors:
                if self.energy > self.size + self.size/self.fertility and self.fertility > self.offspringCount:
                    self.energy -= self.size
                    self.energy -= self.size/self.fertility
                    newName=mergeString(self.speciesName, self.mate.speciesName)
                    openLocations=list(filter(lambda n: not n.occupant, self.location.neighbors))
                    if len(openLocations):
                        birthlocation=random.choice(openLocations)
                    else:
                        birthlocation=self.location
                    self.offspring=Creature(
                        birthlocation, 
                        [
                            Genome.merge(*self.genome).mutate(), 
                            Genome.merge(*self.mate.genome).mutate()
                        ], 
                        energy=self.size/self.fertility,
                        speciesName=newName
                        if int(random.random()*10)>0 else
                        modString(newName, random.choice('abcdefghijklmnopqrstuvwxyz'), int(random.random() * len(newName)))
                    )
                    self.offspringCount += 1
                    self.mate=None
            
        # move along
        if (self.path):
            nextMove=self.path.pop(0)
            if nextMove.occupant:
                self.path=[]
            else:
                self.location.occupant=None
                self.direction=self.location.neighbors.index(nextMove)
                self.location=nextMove
                self.location.occupant=self
                self.direction=min(self.direction, len(self.location.neighbors)-1)

        return self.action
            
    def seekFood(self, foodLocation: MapNode):
        self.food=foodLocation.resource
        if self.location == foodLocation:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, foodLocation)
        self.action=Action.eat

    def attack(self, other):
        self.victim=other
        if other.location in self.location.neighbors:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, other.location)
        self.action=Action.attack

    def flee(self, other):
        self.fear=other
        self.path=Map.fleePath(self.location, other.location, safeDistance=10)
        # vvv saved this old code just to compare with the elegance of this ^^^
        # toOther=Map.findPath(self.location, other.location)
        # self.direction=(self.location.neighbors.index(toOther[0])+int(len(self.location.neighbors)/2))%len(self.location.neighbors)
        # self.path=[self.location.neighbors[self.direction]]
        self.action=Action.flee

    def sprint(self, _):
        self.sprints += self.stamina
        self.energy -= 1

    def seekMate(self, other):
        self.mate=other
        if self.mate.location in self.location.neighbors:
            self.path=[]
        else:
            self.path=Map.findPath(self.location, other.location)
        self.action=Action.mate

    def wander(self, _=None):
        # won't allow 'wandering' into someone else's tile
        options=list(filter(lambda n: not n.occupant, self.location.neighbors))
        if len(options) == 0:
            self.path=[]
        else:
            self.path=[random.choice(options)]
        self.action=Action.wander
        return self

    def turnLeft(self, _=None):
        # works
        self.direction=(self.direction - 1 + len(self.location.neighbors)) % len(self.location.neighbors)
        return self

    def turnRight(self, _=None):
        self.direction=(self.direction + 1) % len(self.location.neighbors)
        return self

    def faceDirection(self, direction):
        self.direction=direction
        return self

    def moveForward(self, _=None):
        self.path=[self.location.neighbors[self.direction]]

    def rest(self, _=None):
        self.path=[]
        self.action=Action.rest

    def die(self):
        self.location.resource=Resource(ResourceType.meat, self.energy + self.size)
        self.location.occupant=None
        self._dead=True

    def think(self) -> str:
        if self.speciesName == 'killerofdeer':
            er=1
        if self.uniqueID == debug:
            er=1
        if self.dead: return "dead'"

        self.action=self.brain.process([Stimulus(self, 0)] + self.scanVision())

        self.clearInputs()
        options=[self.processStimulus(target=self)]
        options += self.scanVision(self.location.getVision(self.direction, self.sightrange, self.sightfield))
        action=max(options, key=lambda option: option.weight)
        action.action(self, action.target)

        # propagate this action into the net, potentially setting memory neurons
        for neuron in self.actionNeurons: neuron.clear()
        action.neuron.activate(1)
        for axon in self.actionAxons:
            axon.fire()

        return action.neuron.name

    # def getVisionRanges(self) -> list[list[MapNode]]:
    #     cones=[
    #         self.location.visionTree[(self.direction + n) % len(self.location.neighbors)][:self.sightrange] 
    #         for n in [-int(n / 2) if n % 2 == 0 else int(n / 2) + 1 
    #         for n in range((self.sightfield - 1) * 2 + 1)] 
    #     ]
    #     visionLayers=[
    #         # get a separate array of nodes for each distance from self.location
    #         [node for cone in [[cones[a][b] 
    #         for a in range(len(cones))] for b in range(self.sightrange)][i] 
    #         for node in cone] for i in range(self.sightrange)
    #     ]
    #     return [[self.location]] + visionLayers

    def scanVision(self) -> list[Stimulus]:
        vision=self.location.getVision(self.direction, self.sightrange, self.sightfield)
        stimuli: list[Stimulus]=[]

        for distance, layer in enumerate(vision):
            for node in layer:
                if (node.occupant and node.occupant != self):
                    stimuli.append(Stimulus(target=node.occupant, distance=distance))

                elif (node.resource):
                    stimuli.append(Stimulus(target=node, distance=distance))

        return stimuli

    def printStats(self):
        print('deadliness: ', self.deadliness)
        print('speed: ', self._speed)
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
        obj = {
            'genomes': [self.genome[n].encode() for n in range(len(self.genome))],
            'deadliness': self.deadliness,
            'toughness': self.fortitude,
            'speed': self.speed,
            'stamina': self.stamina,
            'longevity': self.longevity,
            'fertility': self.fertility,
            'vision': f'{self.sightfield} x {self.sightrange}',
            'diet': 'meat' if self.meateating > self.planteating else 'plants',
            'age': self.age,
            'brain': self.brain,
            'energy': self.energy,
            'location': self.location.index,
            'speciesName': self.speciesName,
            'offspring': self.offspringCount
        }
        if self.longevity > 1000000: obj['immortal']=True
        return obj

def fromJson(j:dict, location: MapNode=MapNode()) -> Creature:
    newCreature= Creature(
        location=location,
        genomes=[
            Genome.decode(g)
            for g in j['genomes']
        ], 
        brain=j['brain'] if 'brain' in j else '',
        speciesName=j['speciesName'] if 'speciesName' in j else '',
        offspringCount=j['offspring'] if 'offspring' in j else 0,
        energy=float(j['energy']) if 'energy' in j else 100,
        age=int(j['age']) if 'age' in j else 0
    )
    if 'immortal' in j: newCreature.longevity=math.inf
    return newCreature

Creature.fromJson=staticmethod(fromJson)
