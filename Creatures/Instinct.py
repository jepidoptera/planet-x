import Creature
import Senses
def __init__ (self, ):
    
    return

# behaviors

def callout(self):
    # vocal call which can trigger other creatures

    return

def follow_pack(self):

    return

def imprint(target = Creature(), specificity = 1, slot = 0):

    return

def mate(self, partner = Creature()): #awwwwww

    return

def flee(self, target):
    # run from danger

    return

def attack(self, target):
    # attack other living creatures and attempt to kill them
    return

def eat_meat(self, target):
    return

def eat_grass(self, target):
    return

def eat_fruit(self, target):
    return

def store_fat(self):
    self.energy-=1
    self.fatstore+=1

class Behavior:
    def __init__(self, sense, impulse, action):
        self.sense = sense
        self.impulse = impulse
        self.action = action

    def activation(self):
        return self.sense() * self.impulse
    
    def do(self):
        self.action()