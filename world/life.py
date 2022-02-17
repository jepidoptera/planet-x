from world.map import Map
from creatures.creature import *
from creatures.genome import *
import random

map = Map(32, 24)
creatures = [Creature(map, random.choice(map.nodes), randomGenome(), 32) for n in range(10)]
