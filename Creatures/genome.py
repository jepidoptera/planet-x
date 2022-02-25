from json.encoder import INFINITY
from operator import mod
from random import random
import random

# genome
class Stat():
    min = 0
    max = INFINITY
    metacost:float=0.0
    growcost:float=0.0
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
    metacost = 4.0
    growcost = 1.0

class Speed(Stat):
    max = 12
    metacost = 4.0
    growcost = 1.0

class Longevity(Stat):
    min = 1
    max = INFINITY # imortality would require infinite energy tho
    metacost = 0.8
    growcost = 1.0

class Intelligence(Stat):
    min = 10
    max = 60
    metacost = 0.3
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
    max = 10
    metacost = 4.0
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
    mutationRate=2
    mutations=0
    def __init__(self, deadliness: int, speed: int, stamina:int, fortitude: int, intelligence: int, longevity: int, fertility: int, meateating: int, planteating: int, sightrange: int, sightfield: int, brain: str, speciesName: str='', mutations: int=0):

        # gene = Genome(energy=1, deadliness=1, speed=1, stamina=4, fortitude=4, intelligence=13, longevity=6, fertility=9, meateating=1, planteating=7, sightrange=5, sightfield=3,brain='345979023qr79fa70450b0734ec3098e90283b')

        self.stats:dict[str: Stat] = {
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
        self._deadliness = self.stats["deadliness"].value
        self._speed = self.stats["speed"].value
        self._stamina = self.stats["stamina"].value
        self._fortitude = self.stats["fortitude"].value
        self._intelligence = self.stats["intelligence"].value
        self._longevity = self.stats["longevity"].value
        self._fertility = self.stats["fertility"].value
        self._meateating = self.stats["meat eating"].value
        self._planteating = self.stats["plant eating"].value
        self._sightrange = self.stats["sight range"].value
        self._sightfield = self.stats["sight field"].value
        self.stats["sight field"].metacost=self._sightrange/4

        self._size = Stat(value=sum([stat.value for stat in self.stats.values()]), max=99, metacost=1.0, growcost=0)
        
        self.brain=brain
        self.mutations=mutations
        self.age=0
        self.speciesName=speciesName
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

    @property
    def size(self):
        # return self.__deadliness - self.__fertility / 4
        # size is just the sum of all stats
        return self._size

    @property
    def fertility(self):
        return self._fertility

    @property
    def meatEating(self) -> float:
        return (self._meateating + 1) ** 2 / (1 + self._meateating + self._planteating / 2)

    @property
    def plantEating(self) -> float:
        return (self._planteating + 1) ** 2 / (1 + self._meateating / 2 + self._planteating)

    @property
    def sightRange(self) -> int:
        return self._sightrange

    @property
    def sightField(self) -> int:
        return self._sightfield

    @property
    def deadliness(self) -> float:
        return self._deadliness

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def stamina(self) -> float:
        return self._stamina ** 2 / (self._stamina + self._speed / 3 + 1)

    @property
    def fortitude(self) -> float:
        return self._fortitude

    @property
    def intelligence(self) -> int:
        return self._intelligence

    @property
    def longevity(self):
        return self._longevity

    def mutate(self):
        def modString(string: str, char: chr, position: int) -> str:
            return string[:position] + char + string[position+1:]

        newMutations=0
        # this will give something pretty close to averaging mutationRate mutations
        # while still having some chance of zero. it was the best I could come up with
        while random.random()*self.mutationRate**1.4*1.4 > random.random()*(newMutations + 1):
            self.mutations += 1
            if self.mutations % 10 == 0:
                self.speciesName=modString(self.speciesName, random.choice('abcdefghijklmnopqrstuvwxyz'), int(random.random()*len(self.speciesName)))

            brainMutation = int(random.random() * 2)

            if (brainMutation):
                self.brain = modString(self.brain, random.choice('1234567890abcdef'), int(random.random() * len(self.brain)))
            else:
                self.stats[random.choice(list(self.stats.keys()))] += int(random.random() * 2) * 2 - 1

        return self

    def printStats(self):
        print(*[
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
        deadliness = int(random.random() * (Deadliness.max + 1)),
        speed = int(random.random() * (Speed.max + 1)),
        stamina = int(random.random() * (Stamina.max) + 1),
        fortitude = int(random.random() * (Fortitude.max) + 1),
        intelligence = int(random.random() * (Intelligence.max - Intelligence.min + 1) + Intelligence.min),
        longevity =int(random.random() * (50) + 1),
        fertility = int(random.random() * (Fertility.max + 1)),
        meateating = int(random.random() * (MeatEating.max + 1)),
        planteating = int(random.random() * (PlantEating.max + 1)),
        sightrange = int(random.random() * (SightRange.max + 1)),
        sightfield = int(random.random() * (SightField.max) + 1),
        brain = "".join(random.choice('abcdef1234567890') for i in range(128)),
        speciesName=''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for n in range(10)])
    )

def merge(*args: Genome) -> Genome:
    if len(args) == 1: return args[0]
    merged = Genome(
        mutations=max(*[g.mutations for g in args]),
        deadliness=random.choice([g.deadliness for g in args]),
        speed=random.choice([g._speed for g in args]),
        stamina=random.choice([g._stamina for g in args]),
        fortitude=random.choice([g._fortitude for g in args]),
        intelligence=random.choice([g._intelligence for g in args]),
        longevity=random.choice([g._longevity for g in args]),
        fertility=random.choice([g._fertility for g in args]),
        meateating=random.choice([g._meateating for g in args]),
        planteating=random.choice([g._planteating for g in args]),
        sightrange=random.choice([g._sightrange for g in args]),
        sightfield=random.choice([g._sightfield for g in args]),
        brain=mergeString(*[g.brain for g in args], chunk=8),
        speciesName=mergeString(*[g.speciesName for g in args], chunk=1)
    )
    return merged
def mergeString(*args: str, chunk: int=1) -> str:
    if len(args) == 1: return args[0]
    mergeStr=''
    for n in range(int(max(*[len(arg) for arg in args])/chunk)):
        genes=[arg[n*chunk:(n+1)*chunk] if len(arg) >= n*chunk else '' for arg in args]
        mergeStr += random.choice(genes)
    return mergeStr

Genome.merge=staticmethod(merge)
Genome.randomGenome=staticmethod(randomGenome)
Genome.mergeString=staticmethod(mergeString)

# in search of a function that will repeat an average of x times,
# but always has a chance of repeating 0 times.

candidates=[
    lambda rate, mutations: random.random()*rate*2 > random.random()*(mutations + 1),
    lambda rate, mutations: random.random()*(mutations + 1) < rate,
    lambda rate, mutations: rate**(mutations+1) > random.random()*(rate+1)**(mutations + 1)*(1 + (mutations*rate) / (mutations * rate + 1)),
    lambda rate, mutations: rate * random.random() > random.random()*(mutations + 1),
    lambda rate, mutations: random.random()*rate**1.4*1.4 > random.random()*(mutations + 1)
    # 2/3, 4/9, 8/27
]
def avgMutations(rate, f):
    avg=0
    f=candidates[f]
    for _ in range(1000):
        mutations=0
        while f(rate, mutations):
            mutations += 1
        avg += mutations
    return avg / 1000

def convergence(x):
    s = 0
    y = 1
    for _ in range(1000):
        y *= x/(x+1)
        s += y
    return s

def headToHead():
    for n in range(len(candidates)):
        print(f'function {n + 1}: {[avgMutations(i+1, n) for i in range(10)]}')