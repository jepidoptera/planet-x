import math
from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
import json
from typing import Callable
import analysis

dirname: str='species/'
defaultMapWidth=240
defaultMapHeight=160

# this is the global metabolic rate, affecting all creatures
# adjust down to make life harder, up to make it easier
metaconstant=400

logAnalysis=True

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
        self.stepFunction=stepFunction

        for creature in creatures:
            creature.moveTimer = random.random() * 60
            creature.thinkTimer = random.random() * 60
            if creature.location.index == -1:
                creature.location=random.choice(self.world.nodes)

        def step():
            cycle(self.creatures)
            self.steps += 1
            if self.stepFunction: self.stepFunction()
            if logAnalysis and self.steps % 50 == 0:
                analysis.analysePop(self.world, self.creatures)

        self.step = step

    def basicWorld():
        return Map(defaultMapWidth,defaultMapHeight).populateGrass(value=20, density=0.2)

    def growGrass(world: Map, number: int=0, value: float=5):
        if not(number): number=int(len(world.nodes)/1200)
        nodes=[random.choice(world.nodes) for _ in range(number)]
        for node in nodes:
            node.resource = Resource(ResourceType.grass, value, node)
 
    def strewMeat(world: Map, number: int=1, value: float=10):
        nodes=[random.choice(world.nodes) for _ in range(ceil(number))]
        for node in nodes:
            if random.random() > number: break
            number -= 1
            node.resource = Resource(ResourceType.meat, value, node)

    def randomAges(creatures: set[Creature]) -> set[Creature]:
        for creature in creatures:
            creature.age = random.random() * creature.longevity
        return creatures

class Scenarios():

    def random_creatures(world: Map=None) -> Scene:
        world=world or Scene.basicWorld()
        return Scene(
            world=world, 
            creatures=set([
                templates.rando() 
                for n in range(300)
            ]),
            stepFunction=lambda: Scene.growGrass(world),
            name='random creatures'
        )

    def herbivores(world: Map=None) -> Scene:
        world=world or Scene.basicWorld()

        creatures=set([
            templates.cross(*[templates.rando(), *[templates.herbivore()]*3]) 
            for n in range(500)
        ])
        for creature in creatures:
            creature.age=random.random() * creature.longevity
            creature.energy=10

        optimalDeer=250
        def maintainPopulations(scene: Scene):
            if scene.steps % 50 == 0:
                deers=list(scene.creatures)
                deers.sort(key=lambda deer: deer.offspringCount * 5000 + deer.age + deer.energy, reverse=True)
                for n in range(optimalDeer - len(deers)):
                    scene.creatures.add(templates.cross(deers[0], deers[1], location=random.choice(world.nodes), mutate=True))
                # for n in range(optimalWolves - len(wolves)):
                #     scene.creatures.add(templates.cross(wolves[0], wolves[1], location=random.choice(world.nodes), mutate=True))
            Scene.growGrass(world)

        scene=Scene(
            world=world, 
            creatures=creatures,
            name='herbivores'
        )
        scene.stepFunction=lambda: maintainPopulations(scene)
        return scene

    def predator_prey(world: Map=None, creatures: set[Creature]=None, steps: int=0) -> Scene: 
        world=world or Scene.basicWorld()
        creatures=creatures or set([
            templates.danrsveej(mutate=True) 
            for n in range(500)
        ] +
        [
            templates.quiltrpolf(mutate=True)
            for n in range(30)
        ])
        return Scene(
            world=world, 
            creatures=creatures,
            stepFunction=lambda: Scene.growGrass(world),
            steps=steps,
            name='predator/prey'
        )

    def immortal_wolves(world: Map=None, creatures: set[Creature]=set(), steps: int=0) -> Scene: 
        world=world or Scene.basicWorld()
        numOfWolves=25
        if len(creatures) == 0:
            wolves=[templates.deerkiller(
                location=random.choice(world.nodes)
            ) for n in range(numOfWolves)]

            deers=[templates.danrsveej(
                location=random.choice(world.nodes),
                mutate=True
            ) for n in range(500)]

            for deer in deers:
                deer.age = random.random() * deer.longevity

            creatures=set(deers + wolves)
        else:
            wolves=set(filter(lambda c: c.meateating == 7, creatures))
            if len(wolves) > numOfWolves:
                wolves=set(list(wolves)[:numOfWolves])

        def maintainStasis():
            for wolf in wolves:
                wolf.energy=10
            Scene.growGrass(world)

        return Scene(
            world=world, 
            creatures=creatures,
            stepFunction=maintainStasis,
            name='immortal wolves',
            steps=steps
        )

    def wolfDen(world: Map=None, creatures: set[Creature]=None, steps: int=0) -> Scene:
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
            Scene.growGrass(world)

        scene=Scene(
            world=world,
            creatures=creatures,
            name='wolfden',
            steps=steps
        )
        scene.stepFunction=lambda: maintainPopulations(scene)
        return scene

    def sacrificial_deer(world: Map=None, creatures: set[Creature]=None, steps: int=0) -> Scene:
        world=world or Scene.basicWorld()

        if not creatures:
            creatures=set([
                    templates.carnivore(mutate=True)
                    for n in range(200)
                ])

        def releaseFood(scene: Scene):
            if scene.steps % 10 == 0:
                scene.creatures.add(templates.herbivore(location=random.choice(world.nodes), energy=100))
            Scene.growGrass(world)

        scene=Scene(
            world=world,
            creatures=creatures,
            name='sacrificial deer',
            steps=steps
        )
        scene.stepFunction=lambda: releaseFood(scene)
        return scene

    def oneonone(world: Map=None, creatures: set[Creature]=None, steps: int=0) -> Scene:
        world=Map(32,20).populateGrass(20, 0.5)
        creatures=set([templates.deerkiller(world.nodes[0]), templates.danrsveej(world.nodes[42])])
        return Scene(world, creatures)

    def free_meat(world: Map=None, creatures: set[Creature]=None, steps: int=0) -> Scene:
        world=world or Map(32,20).populateGrass(20, 0.2)
        creatures=creatures or set([templates.coyotefox(energy=10, mutate=True) for n in range(100)])
        creatures=Scene.randomAges(creatures)
        return Scene(world, creatures, lambda: Scene.strewMeat(world, 0.1, 100), steps=steps, name='free meat')

steps:int = 0
thoughtThreshold:int = 60
moveThreshold:int = 60

def cycle(creatures: set[Creature]):

    aliveCreatures=set(creatures)
    for creature in aliveCreatures:
        
        creature.thinkTimer += creature.intelligence/2
        if creature.thinkTimer > thoughtThreshold:
            creature.thinkTimer -= thoughtThreshold
            creature.think()
            creature.energy -= len(creature.brain)/metaconstant

        creature.moveTimer += creature.speed
        if creature.moveTimer > moveThreshold:
            creature.moveTimer -= moveThreshold
            creature.animate()
            creature.energy -= creature.metabolism/metaconstant

        creature.age += 1
        if creature.age > creature.longevity or creature.energy < 0:
            creature.die()            
            creatures.remove(creature)

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

    topSpecies=[(name, number) for i, (name, number) in enumerate(species.items())]
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
            'step': scene.steps,
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
        steps=data['step'] if 'step' in data else 0
        mapnodes=data['mapnodes']
        world=Map(0,0)
        creatures: set[Creature]=set()
        
        for node in mapnodes:
            newnode=MapNode(int(node['index']), neighbors=node['neighbornodes'], x=node['x'], y=node['y'], z=node['z'])
            newnode.occupant=node['occupant']
            if node['grass']:
                newnode.resource=Resource(ResourceType.grass, node['grass'])
            if node['meat']:
                newnode.resource=Resource(ResourceType.meat, node['meat'])
            world.nodes.append(newnode)
        
        for node in world.nodes:
            node.neighbors=[world.nodes[n] for n in node.neighbors]           
            if node.occupant:
                # will automatically set this node.occupant=Creature
                newCreature=Creature.fromJson(node.occupant, world.nodes[node.occupant['location']])
                creatures.add(newCreature)
        
        for node in world.nodes:
            node.calcVisionTree(10) 

        world.mapWidth=int(max([node.x for node in world.nodes])) + 1
        world.mapHeight=int(max([node.y for node in world.nodes])) + 1

        if scenarioName == 'wolfden':
            return Scenarios.wolfDen(world=world, creatures=creatures, steps=steps)
        elif scenarioName == 'immortal wolves':
            return Scenarios.immortal_wolves(world=world, creatures=creatures, steps=steps)
        elif scenarioName == 'sacrificial deer':
            return Scenarios.sacrificial_deer(world=world, creatures=creatures, steps=steps)
        elif scenarioName == 'free meat':
            return Scenarios.free_meat(world=world, creatures=creatures, steps=steps)
        elif scenarioName == 'predator/prey':
            return Scenarios.predator_prey(world=world, creatures=creatures, steps=steps)
        else:
            return Scene(
                name=scenarioName,
                world=world,
                creatures=creatures,
                stepFunction=lambda: Scene.growGrass(world),
                steps=steps
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
