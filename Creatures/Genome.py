# genome
class Stat():
    def __init__(self, value: int, max: int, metacost: float, growcost: float):
        self.value = value
        self.max = max
        self.metacost = metacost
        self.growcost = growcost

def __init__(self, deadliness, speed, fortitude, intelligence, longevity, fertility):

    self.__stats = {
        deadliness: Stat(value = deadliness, max = 4, metacost = 1.0, growcost = 1.0),
        speed: Stat(value = speed, max = 4, metacost = 1.0, growcost = 1.0),
        fortitude: Stat(value = fortitude, max = 4, metacost = 1.0, growcost = 1.0),
        intelligence: Stat(value = intelligence, max = 4, metacost = 1.0, growcost = 1.0),
        longevity: Stat(value = longevity, max = 4, metacost = 1.0, growcost = 1.0),
        fertility: Stat(value = deadliness, max = 4, metacost = 1.0, growcost = 1.0),
    }
    self.__size = sum([stat.value for stat in self.__stats])
    self.__metabolism = sum(self.__stats.values().map(lambda stat: stat.value * stat.metacost))
    self.sprintMoves = 0
    # *size
    # *deadliness
    # *speed
    # *fortitude
    # *intelligence
    # *longevity
    # *fertility
    # *metabolism

    return

@property 
def metabolism(self):
    # return self.__metabolism + (self.__intelligence + self.__deadliness + self.__speed + self.__size) / 4
    return self.__metabolism + self.sprintMoves * self.size

@property
def size(self):
    # return self.__deadliness - self.__fertility / 4
    # size is just the sum of all stats
    return self.__size

@property
def fertility(self):
    return self.__fertility - self.__longevity / 3

@property
def deadliness(self):
    deadliness = self.__deadliness - self.__speed / 3 - fertility / 4
    deadliness += size / 2
    return deadliness

@property
def speed(self):
    return (self.__speed - self.__deadliness / 2) * 1.5

@property
def longevity(self):
    longevity = self.__longevity / min(self.__size / self.__deadliness, 1)
    return longevity
    # // longevity declines when deadliness < size
    # weakness = size / deadliness
    # longevity /= weakness
    # // higher stats, needs more food
    # metabolism += (intelligence + deadliness + speed + size) / 4
    # // trade-off between deadliness and speed
    # deadliness -= speed / 3
    # speed = (speed - deadliness / 2) * 1.5
    # // size adds to deadliness, but only after weakness is subtracted from longevity
    # deadliness += size / 2
