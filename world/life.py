from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
import json
from typing import Callable

class Scenario():
    world: Map
    creatures: set[Creature]
    steps: int=0
    info: str=''

    def __init__(self, 
        world: Map, 
        creatures: set[Creature], 
        stepFunction: Callable[[any], None]=None, 
        steps: int=0
    ):
        self.world=world
        self.creatures=creatures
        self.steps=steps

        for creature in creatures:
            creature.moveTimer = random.random() * 60
            creature.thinkTimer = random.random() * 60
            if creature.location.index == -1:
                creature.location=random.choice(world.nodes)

        def step():
            cycle(self.world, self.creatures)
            self.steps += 1
            if stepFunction: stepFunction()
        self.step = step

class Scenarios():
    def _growGrass(world: Map, number: int=1, value: float=10):
        for _ in range(number):
            random.choice(world.nodes).resource = Resource(ResourceType.grass, value)
    def _strewMeat(world: Map, number: int=1, value: float=10):
        for _ in range(number):
            random.choice(world.nodes).resource = Resource(ResourceType.meat, value)
    def _basicWorld():
        return Map(80,40).populateGrass(value=20, density=0.2)

    def random_creatures() -> Scenario:
        world=Scenarios._basicWorld()
        return Scenario(
            world=world, 
            creatures=set([
                templates.rando() 
                for n in range(300)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20)
        )

    def herbivores() -> Scenario:
        world=Scenarios._basicWorld()
        return Scenario(
            world=world, 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20)
        )

    def scavengers() -> Scenario:
        world=Scenarios._basicWorld()
        return Scenario(
            world=world, 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20)
        )
    def predator_prey() -> Scenario: 
        world=Scenarios._basicWorld()
        return Scenario(
            world=world, 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ] +
            [
                templates.cross(*[templates.rando(), *[templates.carnivore()]*3]) 
                for n in range(30)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20)
        )

    def superdeer() -> Scenario: 
        world=Scenarios._basicWorld(), 
        return Scenario(
            world=world, 
            creatures=set([
                templates.herbivore(energy=10) 
                for n in range(300)
            ] +
            [
                templates.herbivore_evolved(energy=10)
                for n in range(10)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20)
        )

    def wolfDen() -> Scenario:
        world=Scenarios._basicWorld()
        optimalWolves: int=20
        optimalDeer: int=200

        wolves=[
                templates.carnivore(mutate=True)
                for n in range(optimalWolves)
            ]
        deers=[
                templates.herbivore(mutate=True)
                for n in range(optimalDeer)
            ]

        def maintainPopulations(scene: Scenario, deers: list[Creature], wolves: list[Creature]):
            if scene.steps % 100 == 0:
                deers=filter(lambda deer: not deer.dead, deers)
                wolves=filter(lambda wolf: not wolf.dead, wolves)
                deers.sort(key=lambda deer: deer.offspringCount * 5000 + deer.age + deer.energy, reverse=True)
                wolves.sort(key=lambda wolf: wolf.offspringCount * 5000 + wolf.age + wolf.energy, reverse=True)
                while len(deers) < optimalDeer:
                    deers.append(templates.cross(deers[0], deers[1], location=random.choice(world.nodes)))
                while len(wolves) < optimalWolves:
                    wolves.append(templates.cross(wolves[0], wolves[1], location=random.choice(world.nodes)))

        scene=Scenario(
            world=world,
            creatures=set(wolves+deers)
        )
        scene.stepFunction=lambda: maintainPopulations(scene, deers, wolves)
        return scene


steps:int = 0
thoughtThreshold:int = 60
moveThreshold:int = 60

def cycle(world: Map, creatures: set[Creature]):

    aliveCreatures: set[Creature] = set(creatures)
    for creature in aliveCreatures:
        
        creature.thinkTimer += creature.intelligence/2
        if creature.thinkTimer > thoughtThreshold:
            creature.thinkTimer -= thoughtThreshold
            creature.think()

        creature.moveTimer += creature.speed
        if creature.moveTimer > moveThreshold:
            creature.moveTimer -= moveThreshold
            creature.animate()

        creature.age += 1
        creature.energy -= creature.metabolism
        if creature.age > creature.longevity or creature.energy < 0:
            creature.die()            

        if creature._dead: creatures.remove(creature)
        if creature.offspring: 
            creatures.add(creature.offspring)
            creature.offspring=None

def countSpecies(creatures):
    species={}
    for creature in creatures:
        # count surviving species
        if not creature.speciesName in species:
            species[creature.speciesName]=0
        species[creature.speciesName] += 1

    topSpecies = [(name, number) for i, (name, number) in enumerate(species.items())]
    topSpecies.sort(key=lambda x: -x[1])
    return topSpecies
    
    # print (steps)
    # print (*[f'{species}: {number}' for i, (species, number) in enumerate(species.items())], sep='\n')

def saveWorld(world: Map, creatures: set[Creature], steps:int, filename: str):
    with open(filename, 'w') as file:
        json.dump({
            'steps':steps, 
            'mapwidth':world.mapWidth,
            'mapheight':world.mapHeight,
            'creatures':[creature.toJson() for creature in creatures]}, 
        file, indent=4)

def loadWorld(filename: str) -> Scenario:
    print(f'loading {filename}')
    with open(filename, 'r') as file:
        data = json.load(file)
        steps=int(data['steps'])
        mapHeight=data['mapheight']
        mapWidth=data['mapwidth']
        world=Map(mapWidth=mapWidth, mapHeight=mapHeight).populateGrass(20, 0.1)
        creatures = set([
            Creature.fromJson(c, world.nodes[c['location']])
            for c in data['creatures']
        ])
    scenario=Scenario(world, creatures)
    scenario.steps=steps
    return scenario

# def generateCreatures():
#     if scenario == 'random':
#         print(f'generating 300 random creatures...')
#         creatures = set([templates.rando(random.choice(map.nodes)) for n in range(300)])

#     else:
#         herb = templates.herbivore()
#         carn = templates.carnivore()
#         # now add some random in the mix
#         herbs = [templates.cross(herb, templates.cross(herb, templates.rando()), random.choice(map.nodes)) for n in range(300)] 
#         for creature in herbs: 
#             creature.speciesName = 'deersheep'
#             creature.genome[0].speciesName = 'deersheep'
#             creature.genome[1].speciesName = 'deersheep'
#         carns = [templates.cross(carn, templates.rando(), random.choice(map.nodes)) for n in range(0)]
#         for creature in carns: 
#             creature.speciesName = 'tigerwolf'
#             creature.genome[0].speciesName = 'tigerwolf'
#             creature.genome[1].speciesName = 'tigerwolf'
#         creatures: set[Creature] = (
#             herbs + carns
#             # + [templates.cross(carn, templates.cross(carn, templates.rando()), random.choice(map.nodes)) for n in range(100)]
#         )
#         # creatures = (
#         #     [templates.herbivore(random.choice(map.nodes)) for n in range(200)]
#         #     + [templates.carnivore(random.choice(map.nodes)) for n in range(20)]
#         # )
#         # they have served their purpose
#         del(herb)
#         del(carn)


#     return creatures
