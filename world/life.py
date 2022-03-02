from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
import json
from typing import Callable

dirname: str='species/'

class Scene():
    world: Map
    creatures: set[Creature]
    steps: int=0
    info: str=''

    def __init__(self, 
        world: Map, 
        creatures: set[Creature], 
        stepFunction: Callable[[any], None]=None, 
        steps: int=0,
        name: str=''
    ):
        self.world=world or Scene.basicWorld()
        self.creatures=creatures
        self.steps=steps
        self.name=name
        if stepFunction: self.stepFunction=stepFunction

        for creature in creatures:
            creature.moveTimer = random.random() * 60
            creature.thinkTimer = random.random() * 60
            if creature.location.index == -1:
                creature.location=random.choice(self.world.nodes)

        def step():
            cycle(self.world, self.creatures)
            self.steps += 1
            if self.stepFunction: self.stepFunction()
        self.step = step

    def basicWorld():
        return Map(80,40).populateGrass(value=20, density=0.2)

class Scenarios():

    def _growGrass(world: Map, number: int=1, value: float=10):
        for _ in range(number):
            random.choice(world.nodes).resource = Resource(ResourceType.grass, value)
 
    def _strewMeat(world: Map, number: int=1, value: float=10):
        for _ in range(number):
            random.choice(world.nodes).resource = Resource(ResourceType.meat, value)

    def random_creatures(world: Map=None) -> Scene:
        world=world or Scene.basicWorld()
        return Scene(
            world=world, 
            creatures=set([
                templates.rando() 
                for n in range(300)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20),
            name='random creatures'
        )

    def herbivores(world: Map=None) -> Scene:
        world=world or Scene.basicWorld()
        return Scene(
            world=world, 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20),
            name='herbivores'
        )

    def scavengers(world: Map=None) -> Scene:
        world=world or Scene.basicWorld()
        return Scene(
            world=world, 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20),
            name='scavengers'
        )
    def predator_prey(world: Map=None) -> Scene: 
        world=world or Scene.basicWorld()
        return Scene(
            world=world, 
            creatures=set([
                templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
                for n in range(300)
            ] +
            [
                templates.cross(*[templates.rando(), *[templates.carnivore()]*3]) 
                for n in range(30)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20),
            name='predators and prey'
        )

    def superdeer(world: Map=None) -> Scene: 
        world=world or Scene.basicWorld()
        return Scene(
            world=world, 
            creatures=set([
                templates.herbivore(energy=10) 
                for n in range(300)
            ] +
            [
                templates.herbivore_evolved(energy=10)
                for n in range(10)
            ]),
            stepFunction=lambda: Scenarios._growGrass(world, 2, 20),
            name='superdeer'
        )

    def wolfDen(world: Map=None, creatures: set[Creature]=None) -> Scene:
        world=world or Map(120, 60).populateGrass(20, 0.2)
        optimalWolves: int=40
        optimalDeer: int=400

        if not creatures:
            wolves=[
                    templates.carnivore(mutate=True)
                    for n in range(optimalWolves)
                ]
            deers=[
                    templates.herbivore(mutate=True)
                    for n in range(optimalDeer)
                ]
            creatures = set(wolves + deers)

        def maintainPopulations(scene: Scene):
            if scene.steps % 50 == 0:
                deers=list(filter(lambda deer: deer.meateating < deer.planteating, scene.creatures))
                wolves=list(filter(lambda wolf: wolf.meateating > wolf.planteating, scene.creatures))
                deers.sort(key=lambda deer: deer.offspringCount * 5000 + deer.age + deer.energy, reverse=True)
                wolves.sort(key=lambda wolf: wolf.offspringCount * 5000 + wolf.age + wolf.energy, reverse=True)
                for n in range(optimalDeer - len(deers)):
                    scene.creatures.add(templates.cross(deers[0], deers[1], location=random.choice(world.nodes), mutate=True))
                # for n in range(optimalWolves - len(wolves)):
                #     scene.creatures.add(templates.cross(wolves[0], wolves[1], location=random.choice(world.nodes), mutate=True))
            Scenarios._growGrass(world, 2, 20)

        scene=Scene(
            world=world,
            creatures=creatures,
            name='wolfden'
        )
        scene.stepFunction=lambda: maintainPopulations(scene)
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

def saveCreatures(world: Map, creatures: set[Creature], steps:int, filename: str):
    with open(dirname + filename, 'w') as file:
        json.dump({
            'steps':steps, 
            'mapwidth':world.mapWidth,
            'mapheight':world.mapHeight,
            'creatures':[creature.toJson() for creature in creatures]}, 
        file, indent=4)

def saveWorld(scene: Scene, filename: str):
    with open(dirname + filename + '.world', 'w') as file:
        json.dump({
            'scenario': scene.name,
            'mapnodes': [{
                'index': node.index,
                'neighbornodes': [n.index for n in node.neighbors],
                'x': node.x,
                'y': node.y,
                'z': node.z,
                'grass': node.resource.value if node.resource and node.resource.type == ResourceType.grass else 0,
                'meat': node.resource.value if node.resource and node.resource.type == ResourceType.meat else 0,
                'occupant': (
                    Creature.toJson(node.occupant) if type(node.occupant) == Creature
                        else None
                )
            } for node in scene.world.nodes]
        },
        file, indent=4)

def loadWorld(filename: str) -> Scene:
    if filename[-6:] != '.world':
        filename += '.world'

    with open(dirname + filename) as file:
        data=json.load(file)
        scenarioName=data['scenario']
        mapnodes=data['mapnodes']
        world=Map(0,0)
        creatures: set[Creature]=set()
        
        for node in mapnodes:
            newnode=MapNode(int(node['index']), neighbors=node['neighbornodes'], x=node['x'], y=node['y'], z=node['z'])
            newnode.occupant=node['occupant']
            world.nodes.append(newnode)
        
        for node in world.nodes:
            node.neighbors=[world.nodes[n] for n in node.neighbors]           
            if node.occupant:
                # will automatically set this node.occupant=Creature
                creatures.add(Creature.fromJson(node.occupant, world.nodes[node.occupant['location']]))
        
        for node in world.nodes:
            node.calcVisionTree(10) 

        world.mapWidth=int(max([node.x for node in world.nodes]))
        world.mapHeight=int(max([node.y for node in world.nodes]))

        if scenarioName == 'wolfden':
            return Scenarios.wolfDen(world=world)
        else:
            return Scene(
                name=scenarioName,
                world=world,
                creatures=creatures
            )

def loadCreatures(filename: str) -> Scene:
    print(f'loading {filename}')
    with open(dirname + filename, 'r') as file:
        data = json.load(file)
        steps=int(data['steps'])
        mapHeight=data['mapheight']
        mapWidth=data['mapwidth']
        world=Map(mapWidth=mapWidth, mapHeight=mapHeight).populateGrass(20, 0.1)
        creatures = set([
            Creature.fromJson(c, world.nodes[c['location']])
            for c in data['creatures']
        ])
    scenario=Scene(world, creatures)
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
