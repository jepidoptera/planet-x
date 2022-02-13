from operator import mod
from random import random

# genome
class Stat():
    def __init__(self, value: int, max: int, metacost: float, growcost: float):
        self.value = min(value, max)
        self.max = max
        self.metacost = metacost
        self.growcost = growcost

    def __add__(self, n):
        return min(self + n, self.max)
    
    def __sub__(self, n):
        return max(self - n, 0)

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

def modString(string, char, position):
    return string[:position] + char + string[position+1:]

class Genome():
    mutationRate = 0.5
    def __init__(self, energy: float, deadliness: int, speed: int, stamina:int, fortitude: int, intelligence: int, longevity: int, fertility: int, meateating: int, planteating: int, sightrange: int, peripheralvision: int, axons: str):

        self.__deadliness = Deadliness(value=deadliness)
        self.__speed = Speed(value=speed)
        self.__stamina = Stamina(value=stamina)
        self.__fortitude = Fortitude(value=fortitude)
        self.__intelligence = Intelligence(value=intelligence)
        self.__longevity = Longevity(value=longevity)
        self.__meateating = MeatEating(value=meateating)
        self.__planteating = PlantEating(value=planteating)
        self.__fertility = Fertility(value=fertility)
        self.__sightrange = SightRange(value=sightrange)
        self.__peripheralvision = PeripheralVision(value=peripheralvision)

        self.__stats = [deadliness, speed, fortitude, intelligence, longevity, fertility, meateating, planteating]

        self.__size = sum([stat.value for stat in self.__stats])
        self.__metabolism = sum(self.__stats.values().map(lambda stat: stat.value * stat.metacost))
        
        self.axons = axons
        
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

        if (brainMutation):
            self.axons = modString(self.axons, random.choice('1234567890abcdef'), int(random() * len(self.axons)))
        else:
            self.__stats[int(random.random() * len(self.__stats))] += int(random.random() * 2) * 2 - 1
        return self

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
    def peripheralVision(self):
        return self.__peripheralvision

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
        return self.__intelligence - self.__sightrange * self.__peripheralvision

    @property
    def longevity(self):
        return self.__longevity

