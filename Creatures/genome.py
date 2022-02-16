from json.encoder import INFINITY
from operator import mod
from random import random

# genome
class Stat():
    def __init__(self, value: int, max: int=INFINITY, metacost: float=0.0, growcost: float=0.0):
        self.value = min(value, max)
        self.max = max
        self.metacost = metacost
        self.growcost = growcost

    def __add__(self, n):
        self.value = min(self.value + n, self.max)
        return self.value
    
    def __sub__(self, n):
        self.value = max(self.value - n, 0)
        return self.value

class Fortitude(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=1.0, growcost=1.5)

class Deadliness(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=2.0, growcost=1.0)

class Speed(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=12, metacost=1.5, growcost=1.0)

class Longevity(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=20, metacost=1.0, growcost=1.0)

class Intelligence(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=128, metacost=0.5, growcost=0.2)

class MeatEating(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=1.0, growcost=0.0)

class PlantEating(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=1.0, growcost=0.0)

class Fertility(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=1.5, growcost=0)

class SightRange(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=1.0, growcost=0.4)

class PeripheralVision(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=4, metacost=1.0, growcost=0.4)

class Stamina(Stat):
    def __init__(self, value):
        super().__init__(value=value, max=7, metacost=1.0, growcost=1.0)

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
            "sight field": PeripheralVision(value=sightfield)
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
        if random.random() > self.mutationRate: return 0

        brainMutation = int(random() * 2)

        def modString(string, char, position):
            return string[:position] + char + string[position+1:]

        if (brainMutation):
            self.mindStr = modString(self.mindStr, random.choice('1234567890abcdef'), int(random() * len(self.mindStr)))
        else:
            self.__stats[int(random.random() * len(self.__stats))] += int(random.random() * 2) * 2 - 1
        return self

    @property 
    def metabolism(self):
        # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
        return self.__metabolism + self.sprintMoves / self.stamina.value

    @property
    def size(self):
        # return self.__deadliness - self.__fertility / 4
        # size is just the sum of all stats
        return self.__size

    @property
    def fertility(self):
        return self.__fertility - self.__longevity / 3

    @property
    def meatEating(self):
        return self.__meateating - self.__planteating / 2

    @property
    def plantEating(self):
        return self.__planteating - self.__meateating / 2

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
        return self.__stamina - self.speed / 3

    @property
    def fortitude(self):
        return self.__fortitude

    @property
    def intelligence(self):
        return self.__intelligence - self.__sightrange * self.__sightfield

    @property
    def longevity(self):
        return self.__longevity

