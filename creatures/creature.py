# good start
# you made a file!
# 288 lines long now. got about ten other files as well
# ok now it's 762 lines
import math
import random
from creatures.genome import Genome, mergeString, modString
from world.map import *
from brain.basics import Action, Stimulus, Brain
import copy
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
            age: int=0,
            mutate: bool=False,
            brain: Brain=None
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
        # self.axonStr=axonStr or mergeString(*[g.axonStr for g in self.genome], chunk=8)
        # self.neuronStr=neuronStr or mergeString(*[g.neuronStr for g in self.genome], chunk=8)
        self.speciesName=speciesName or mergeString(*[g.variant for g in self.genome])

        self.action=Action.rest
        self.hearing: list[Stimulus]=[]
        self.feeling: list[Stimulus]=[]
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
        if not self.brain.axons:
            self.brain.axons=Brain.mergeAxons(*[g.axons for g in self.genome])
            self.brain.biases=Brain.mergeNeurons(*[g.neurons for g in self.genome])
        self.brain.sortAxons()
        
        # self.brain.unpack(self.axonStr, self.neuronStr)

        self.brain.process([Stimulus(self, 'birth', 0)])

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

        self.think()

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
                self.victim.feeling.append(Stimulus(object=self, event='injury'))
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
                        brain=copy.deepcopy(self.brain),
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
            
    def think(self) -> Action:
        # think about what to do
        decision = self.brain.process(
            [Stimulus(self, distance=0)]
            + self.hearing
            + self.feeling
            + self.scanVision()
        )
        self.hearing=[]
        self.feeling=[]
        if decision.act == Action.attack:
            self.attack(decision.object)
        elif decision.act == Action.eat:
            self.seekFood(decision.object)
        elif decision.act == Action.mate:
            self.seekMate(decision.object)
        elif decision.act == Action.flee:
            self.flee(decision.object)
        elif decision.act == Action.rest:
            self.rest()
        elif decision.act == Action.move:
            self.moveForward()
        elif decision.act == Action.wander:
            self.wander()
        elif decision.act == Action.turnLeft:
            self.turnLeft()
        elif decision.act == Action.turnRight:
            self.turnRight()
        elif decision.act == Action.howl:
            self.howl()
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

    def turnLeft(self):
        # works
        self.direction=(self.direction - 1 + len(self.location.neighbors)) % len(self.location.neighbors)
        self.action=Action.turnLeft
        return self

    def turnRight(self):
        self.direction=(self.direction + 1) % len(self.location.neighbors)
        self.action=Action.turnRight
        return self

    def faceDirection(self, direction):
        self.direction=direction
        return self

    def moveForward(self):
        self.path=[self.location.neighbors[self.direction]]
        self.action=Action.move
        return self

    def rest(self):
        self.path=[]
        self.action=Action.rest
        return self

    def howl(self):
        # any creature within 20 tiles in every direction will hear
        earshot=self.location.getVision(0, 20, 6)
        for distance in earshot:
            for node in distance:
                if node.occupant:
                    node.occupant.hearing.append(Stimulus(self, 'howl', distance=distance))
        self.action=Action.howl
        return self

    def die(self):
        self.location.resource=Resource(ResourceType.meat, self.energy + self.size)
        self.location.occupant=None
        self._dead=True
        return self

    # def think(self) -> str:
    #     if self.speciesName == 'killerofdeer':
    #         er=1
    #     if self.uniqueID == debug:
    #         er=1
    #     if self.dead: return "dead'"

    #     self.action=self.brain.process(self.hearing + self.scanVision())

    #     self.clearInputs()
    #     options=[self.processStimulus(target=self)]
    #     options += self.scanVision(self.location.getVision(self.direction, self.sightrange, self.sightfield))
    #     action=max(options, key=lambda option: option.weight)
    #     action.action(self, action.target)

    #     # propagate this action into the net, potentially setting memory neurons
    #     for neuron in self.actionNeurons: neuron.clear()
    #     action.neuron.activate(1)
    #     for axon in self.actionAxons:
    #         axon.fire()

    #     return action.neuron.name

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
                    stimuli.append(Stimulus(object=node.occupant, distance=distance))

                if (node.resource and (not node.occupant or node.occupant == self)):
                    stimuli.append(Stimulus(object=node, distance=distance))

        return stimuli

    def getSimilarity(self, other) -> float:
        similarity=0.0
        commonRange=range(min(len(self.speciesName), len(other.speciesName)))
        increment=1/len(commonRange)
        for c in commonRange:
            if self.speciesName[c] == other.speciesName[c]: similarity += increment
        return similarity

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
        print('brain dna: ', self.brain.toJson())

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
            'brain': self.brain.toJson(),
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
