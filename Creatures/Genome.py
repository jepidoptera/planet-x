# genome
def __init__(self, size, strength, speed, fortitude, intelligence, longevity, fertility, metabolism):

    self.__size = size
    self.__strength = strength
    self.__speed = speed
    self.__fortitude = fortitude
    self.__intelligence = intelligence
    self.__longevity = longevity
    self.__fertility = fertility
    self.__metabolism = metabolism
    # *size
    # *strength
    # *speed
    # *fortitude
    # *intelligence
    # *longevity
    # *fertility
    # *metabolism

    return

@property 
def metabolism(self):
    return self.__metabolism + (self.__intelligence + self.__strength + self.__speed + self.__size) / 4

@property
def size(self):
    return self.__strength - self.__fertility / 4

@property
def fertility(self):
    return self.__longevity / 3

@property
def metabolism(self):
    return (self.__intelligence + self.__strength + self.__speed + self.__size) / 4

@property
def strength(self):
    strength = self.__strength - self.__speed / 3 - fertility / 4
    strength += size / 2
    return strength

@property
def speed(self):
    return (self.__speed - self.__strength / 2) * 1.5

@property
def longevity(self):
    longevity = self.__longevity / min(self.__size / self.__strength, 1)
    return longevity
    # // longevity declines when strength < size
    # weakness = size / strength
    # longevity /= weakness
    # // higher stats, needs more food
    # metabolism += (intelligence + strength + speed + size) / 4
    # // trade-off between strength and speed
    # strength -= speed / 3
    # speed = (speed - strength / 2) * 1.5
    # // size adds to strength, but only after weakness is subtracted from longevity
    # strength += size / 2
