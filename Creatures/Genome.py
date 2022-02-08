import random
# genome
class Stat():
    def __init__(self, value: int, max: int, metacost: float, growcost: float):
        self.value = value
        self.max = max
        self.metacost = metacost
        self.growcost = growcost

    def __add__(self, n):
        return min(self + n, self.max)
    
    def __sub__(self, n):
        return max(self - n, 0)

mutationRate = 0.5

def __init__(self, energy: float, deadliness: int, speed: int, fortitude: int, intelligence: int, longevity: int, fertility: int, meateating: int, planteating: int):

    self.deadliness = Stat(value = deadliness, max = 4, metacost = 1.0, growcost = 1.0)
    self.speed = Stat(value = speed, max = 12, metacost = 1.0, growcost = 1.0)
    self.fortitude = Stat(value = fortitude, max = 4, metacost = 1.0, growcost = 1.0)
    self.intelligence = Stat(value = intelligence, max = 4, metacost = 1.0, growcost = 1.0)
    self.longevity = Stat(value = longevity, max = 4, metacost = 1.0, growcost = 1.0)
    self.meateating = Stat(value = meateating, max = 4, metacost = 1.0, growcost = 1.0)
    self.planteating = Stat(value = planteating, max = 4, metacost = 1.0, growcost = 1.0)
    self.fertility = Stat(value = fertility, max = 4, metacost = 1.0, growcost = 1.0)

    self.__stats = [deadliness, speed, fortitude, intelligence, longevity, fertility, meateating, planteating]

    self.__size = sum([stat.value for stat in self.__stats])
    self.__metabolism = sum(self.__stats.values().map(lambda stat: stat.value * stat.metacost))

    
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

    return

def mutate(self):
    if random.random() > mutationRate: return 0

    self.__stats[int(random.random * self.__stats.length)] += int(random.random() * 2) * 2 - 1
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
