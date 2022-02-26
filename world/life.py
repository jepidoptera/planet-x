from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
import json

class Scenario():
    world: Map
    creatures: set[Creature]
    steps: int=0
    def __init__(self, world: Map, creatures: set[Creature]):
        self.world=world
        self.creatures=creatures
        for creature in creatures:
            creature.moveTimer = random.random() * 60
            creature.thinkTimer = random.random() * 60
            if creature.location.index == -1:
                creature.location=random.choice(world.nodes)

class Scenarios():
    def random_creatures():
        return Scenario(
                world=Map(80,40).populateGrass(value=20, density=0.2), 
                creatures=set([
                    templates.rando() 
                    for n in range(300)
                ])
            )
    def herbivores_only():
        return Scenario(
                world=Map(80,40).populateGrass(value=20, density=0.2), 
                creatures=set([
                    templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                    for n in range(300)
                ])
            )
    def predator_prey(): 
        return Scenario(
            world=Map(80,40).populateGrass(value=20, density=0.2), 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ] +
            [
                templates.cross(*[templates.rando(), *[templates.carnivore()]*3]) 
                for n in range(30)
            ])
        )
    def superdeer(): 
        return Scenario(
            world=Map(80,40).populateGrass(value=20, density=0.2), 
            creatures=set([
                templates.herbivore(energy=10) 
                for n in range(300)
            ] +
            [
                templates.herbivore_evolved(energy=10)
                for n in range(10)
            ])
        )

steps:int = 0
thoughtThreshold:int = 60
moveThreshold:int = 60

def cycle(world: Map, creatures: set[Creature]):

    random.choice(world.nodes).resource = Resource(ResourceType.grass, 20)
    random.choice(world.nodes).resource = Resource(ResourceType.grass, 20)

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
