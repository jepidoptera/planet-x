from creatures.creature import Creature, netIndex
from creatures.genome import *

basicBrain = (
    # 00 = othercreature.deadliness - self.deadliness
    # 01 = othercreature.age/lifespan
    # 02 = other.health
    # 03 = self.similarity(other)
    # 04 = other.speed - self.speed
    # 05 = other.size
    # 06 = self.energy
    # 07 = self.health
    # 08 = self.age
    # 09 = self.sprintmoves
    # 0a = resource.meat (0/1)
    # 0b = resource.fruit
    # 0c = resource.grass
    # 0d = resource.tree
    # 2d = fight
    # 2e = flee
    # 2f = "mate"
    # 30 = eat
    '002effff' + # flee! if other.deadliness is higher
    '032fffff' + # mate if other is similar to self
    '06300000' + # don't eat if you're not hungry
    '0c30ffff' + # eat grass if you see grass
    '' # don't mate if energy is low
)