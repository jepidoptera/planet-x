from json.encoder import INFINITY
from operator import mod
from random import random
import random

# genome
class Stat():
    min = 0
    max = INFINITY
    metacost = 0.0
    growcost = 0.0
    def __init__(self, value, min:int = 0, max:int = 0, metacost:float = 0.0, growcost:float = 0.0):
        if max: self.max = max
        if min: self.min = min
        if metacost: self.metacost = metacost
        if growcost: self.growcost = growcost
        self.value = value

    def __add__(self, n):
        self.value = max(min(self.value + n, self.max), self.min)
        return self
    
    def __sub__(self, n):
        self.value = min(max(self.value - n, self.min), self.max)
        return self

class Fortitude(Stat):
    min = 1
    max = 7
    metacost = 1.0
    growcost = 1.5

class Deadliness(Stat):
    max = 7
    metacost = 2.0
    growcost = 1.0

class Speed(Stat):
    max = 12
    metacost = 2.0
    growcost = 1.0

class Longevity(Stat):
    min = 1
    max = 20
    metacost = 1.0
    growcost = 1.0

class Intelligence(Stat):
    min = 10
    max = 128
    metacost = 0.5
    growcost = 0.1

class MeatEating(Stat):
    max = 7
    metacost = 1.0
    growcost = 0.0

class PlantEating(Stat):
    max = 7
    metacost = 1.0
    growcost = 0.0

class Fertility(Stat):
    max = 7
    metacost = 1.5
    growcost = 0.0

class SightRange(Stat):
    max = 7
    metacost = 1.0
    growcost = 0.4

class SightField(Stat):
    min = 1
    max = 4
    metacost = 1.0
    growcost = 0.4

class Stamina(Stat):
    min = 1
    max = 7
    metacost = 1.0
    growcost = 1.0

class Genome():
    mutationRate = 0.5
    def __init__(self, energy: float, deadliness: int, speed: int, stamina:int, fortitude: int, intelligence: int, longevity: int, fertility: int, meateating: int, planteating: int, sightrange: int, sightfield: int, mindStr: str):

        # gene = Genome(energy=1, deadliness=1, speed=1, stamina=4, fortitude=4, intelligence=13, longevity=6, fertility=9, meateating=1, planteating=7, sightrange=5, sightfield=3,mindStr='345979023qr79fa70450b0734ec3098e90283b')

        self.stats = {
            "deadliness": Deadliness(value=deadliness),
            "speed": Speed(value=speed), 
            "stamina": Stamina(value=stamina),
            "fortitude": Fortitude(value=fortitude), 
            "intelligence": Intelligence(value=intelligence), 
            "longevity": Longevity(value=longevity), 
            "fertility": Fertility(value=fertility), 
            "meat eating": MeatEating(value=meateating), 
            "plant eating": PlantEating(value=planteating), 
            "sight range": SightRange(value=sightrange),
            "sight field": SightField(value=sightfield)
        }

        # phenome
        self.__deadliness = self.stats["deadliness"].value
        self.__speed = self.stats["speed"].value
        self.__stamina = self.stats["stamina"].value
        self.__fortitude = self.stats["fortitude"].value
        self.__intelligence = self.stats["intelligence"].value
        self.__longevity = self.stats["longevity"].value
        self.__fertility = self.stats["fertility"].value
        self.__meateating = self.stats["meat eating"].value
        self.__planteating = self.stats["plant eating"].value
        self.__sightrange = self.stats["sight range"].value
        self.__sightfield = self.stats["sight field"].value

        self.__size = Stat(value=sum([stat.value for stat in self.stats.values()]), max=99, metacost=1.0, growcost=0)
        self.__metabolism = Stat(value=sum([stat.value * stat.metacost for stat in self.stats.values()]))
        
        self.mindStr = mindStr
        
        self.sprintMoves = 0
        self.energy = energy
        self.age = 0
        # *size
        # *deadliness
        # *speed
        # *fortitude
        # *intelligence
        # *longevity
        # *fertility
        # *metabolism
        # *meateating
        # *planteating
        # *sightrange
        # *peripheralvision

        return

    def mutate(self):
        # if random.random() > self.mutationRate: return 0

        brainMutation = int(random.random() * 2)

        def modString(string, char, position):
            return string[:position] + char + string[position+1:]

        if (brainMutation):
            self.mindStr = modString(self.mindStr, random.choice('1234567890abcdef'), int(random.random() * len(self.mindStr)))
        else:
            self.stats[random.choice(list(self.stats.keys()))] += int(random.random() * 2) * 2 - 1

    @property 
    def metabolism(self):
        # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
        return self.__metabolism + self.sprintMoves / self.stamina

    @property
    def size(self):
        # return self.__deadliness - self.__fertility / 4
        # size is just the sum of all stats
        return self.__size

    @property
    def fertility(self):
        return self.__fertility ** 2 / (self.__fertility + self.__longevity / 3)

    @property
    def meatEating(self):
        return (self.__meateating + 1) ** 2 / (1 + self.__meateating + self.__planteating / 2)

    @property
    def plantEating(self):
        return (self.__planteating + 1) ** 2 / (1 + self.__meateating / 2 + self.__planteating)

    @property
    def sightRange(self):
        return self.__sightrange

    @property
    def sightField(self):
        return self.__sightfield

    @property
    def deadliness(self):
        return self.__deadliness

    @property
    def speed(self):
        return self.__speed

    @property
    def stamina(self):
        return self.__stamina ** 2 / (self.__stamina + self.__speed / 3 + 1)

    @property
    def fortitude(self):
        return self.__fortitude

    @property
    def intelligence(self):
        return int(self.__intelligence ** 2 / (self.__intelligence + self.__sightrange * self.__sightfield))

    @property
    def longevity(self):
        return self.__longevity

    def printStats(self):
        print(*[
            f'energy: {self.energy}', 
            f'deadliness: {self.deadliness}', 
            f'speed: {self.speed}', 
            f'stamina: {self.stamina}', 
            f'fortitude: {self.fortitude}', 
            f'intelligence: {self.intelligence}', 
            f'longevity: {self.longevity}', 
            f'fertility: {self.fertility}', 
            f'sight range: {self.sightRange}', 
            f'field of view: {self.sightField}', 
            f'meat eating: {self.meatEating}', 
            f'plant eating: {self.plantEating}'
        ], sep='\n')

    def printRawStats(self):
        print(*[f'{key}: {value.value}' for i, (key, value) in enumerate(self.stats.items())], sep='\n')


def randomGenome():
    return Genome(
        energy = random.random() * 32, 
        deadliness = int(random.random() * (Deadliness.max + 1)),
        speed = int(random.random() * (Speed.max + 1)),
        stamina = int(random.random() * (Stamina.max) + 1),
        fortitude = int(random.random() * (Fortitude.max) + 1),
        intelligence = int(random.random() * (Intelligence.max - Intelligence.min + 1) + Intelligence.min),
        longevity =int(random.random() * (Longevity.max) + 1),
        fertility = int(random.random() * (Fertility.max + 1)),
        meateating = int(random.random() * (MeatEating.max + 1)),
        planteating = int(random.random() * (PlantEating.max + 1)),
        sightrange = int(random.random() * (SightRange.max + 1)),
        sightfield = int(random.random() * (SightField.max) + 1),
        mindStr = "".join(random.choice('abcdef1234567890') for i in range(32))
    )

c = randomGenome()
while c.mutate() == 0: pass
