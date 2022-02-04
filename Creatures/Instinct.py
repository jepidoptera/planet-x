from ast import Mod
from enum import Enum
import Creature
import Senses
class Modes(Enum):
    resting = 0
    eating = 1
    fleeing = 2
    fighting = 3
    mating = 4
    migrating = 5
    chasing = 6

def __init__ (self, ):
    self.mode = Modes.resting
    return

# behaviors

def callout(self):
    # vocal call which can trigger other creatures
    return

def follow_pack(self):
    self.mode = Modes.migrating
    return

def mate(self, partner = Creature()): #awwwwww
    self.mode = Modes.mating
    return

def flee(self, target):
    # run from danger
    self.mode = Modes.fleeing
    return

def attack(self, target):
    # attack other living creatures and attempt to kill them
    self.mode = Modes.fighting
    return

def eat_meat(self, target):
    self.mode = Modes.eating
    return

def eat_grass(self, target):
    self.mode = Modes.eating
    return

def eat_fruit(self, target):
    self.mode = Modes.eating
    return

def store_fat(self):
    self.energy-=1
    self.fatstore+=1

def ponder(self, impulse, register):
    self.braincell[register].activation += impulse

class Behavior:
    def __init__(self, sense, impulse, action):
        self.sense = sense
        self.impulse = impulse
        self.action = action

    def activation(self):
        return self.sense() * self.impulse
    
    def do(self):
        self.action()