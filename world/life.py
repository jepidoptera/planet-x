from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
import json

# comment these out to debug in vs code #
from curses import wrapper
import curses
#########################################

class Scenario():
    def __int__(self, map: Map, creatures: set[Creature]):
        for creature in creatures:
            creature.moveTimer = random.random() * Life.moveThreshold
            creature.thinkTimer = random.random() * Life.thoughtThreshold
        self.map=map
        self.creatures=creatures

class Scenarios(Enum[Scenario]):
    herbivores_only = Scenario(
        Map(80,40), 
        set([templates.cross([templates.random] + [templates.herbivore*3]) for n in range(300)]))

class Life():
    steps:int = 0
    creatures: set[Creature]=set()

    thoughtThreshold:int = 60
    moveThreshold:int = 60

    loadDir='species/'

    def __init__(self, loadfile: str='', scnenario: Scenario=Scenarios.herbivores_only):
        if loadfile:
            world = loadWorld(self.loadDir + loadfile)
            map = Map(80, 40)
            self.steps = world['steps']
            self.creatures = world['creatures']
        else:
            self.steps=0
            self.map=Scenario.map
            self.creatures=Scenario.creatures
        
        # seed some grass to start
        for node in map.nodes:
            if(random.random() < 0.2): node.resource=Resource(ResourceType.grass, 20)


    def run(self):
        wrapper(self.animate)

    @staticmethod
    def cycle(creatures: set[Creature]):

        moveThreshold=Life.moveThreshold
        thoughtThreshold=Life.thoughtThreshold

        random.choice(map.nodes).resource = Resource(ResourceType.grass, 20)
        random.choice(map.nodes).resource = Resource(ResourceType.grass, 20)

        aliveCreatures: set[Creature] = set()
        for creature in creatures:
            
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
            if creature.age > creature.longevity * 100 or creature.energy < 0:
                creature.die()            

            if not creature._dead: aliveCreatures.add(creature)
            if creature.offspring: 
                aliveCreatures.add(creature.offspring)
                creature.offspring=None

        return aliveCreatures

    @staticmethod
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

    def animate(self, stdscr):

        # Clear screen
        stdscr.clear()
        stdscr.nodelay(True)
        stdscr.keypad(True)

        species=[]

        over=False

        viewX: int=0
        viewY: int=0
        viewWidth: int=80
        viewHeight: int=40
        mapHeight: int=self.mapHeight
        mapWidth: int=self.mapWidth

        while not over:

            creatures = Life.cycle(creatures)

            steps+=1
            if steps % 10 == 0:
                species=Life.countSpecies(creatures)

            stdscr.addstr(0, 0, str(steps))
            stdscr.refresh()
            inKey=stdscr.getch()
            if inKey==ord('q'): over=True
            if inKey==ord('s'): saveWorld(creatures, steps, f'species/{species[0][0]} {steps}.txt')
            if inKey==curses.KEY_UP: viewY = max(viewY-1, 0)
            if inKey==curses.KEY_DOWN: viewY = min(viewY+1, mapHeight-viewHeight)
            if inKey==curses.KEY_LEFT: viewX = max(viewX-1, 0)
            if inKey==curses.KEY_RIGHT: viewX = min(viewX+1, mapWidth-viewWidth)
            if inKey==ord('t'): creatures.add(templates.carnivore(random.choice(map.nodes)))
            if inKey==ord('c'): creatures.add(templates.scavenger(random.choice(map.nodes)))
            
            for y in range(viewY, viewY + min(curses.LINES, mapHeight-1)):
                row = [
                    map.nodes[x*mapHeight*2 + (y % 2)*mapHeight + y//2] 
                    for x in range(viewX, viewX + min(curses.COLS//5 - 2, viewWidth//2-1))
                ]
                line = '' if y % 2 == 0 else '   '
                for node in row:
                    if node.occupant:
                        line += (
                            node.occupant.speciesName[0].upper() if node.occupant.meateating > node.occupant.planteating 
                            else node.occupant.speciesName[0]
                        )
                    elif node.resource:
                        line += '+' if node.resource.type == ResourceType.meat else '"'
                    else:
                        line += ' '
                    line += '     '
                stdscr.addstr(y, 0, line)

            # show top existing species
            stdscr.addstr(viewHeight, 0, f'total:{len(creatures)}   ')
            stdscr.addstr(viewHeight + 1, 0, f'viewport: {viewX} {viewY}')
            for y in range(min(3, len(species))):
                stdscr.addstr(viewHeight+2+y, 0, f'{species[y][0]}: {species[y][1]}   ')
        
        # print (steps)
        # print (*[f'{species}: {number}' for i, (species, number) in enumerate(species.items())], sep='\n')

    def saveWorld(self, creatures: set[Creature], world: Map, steps:int, filename: str):
        with open(filename, 'w') as file:
            json.dump({
                'steps':steps, 
                'mapwidth':world.mapWidth,
                'mapheight':world.mapHeight,
                'creatures':[creature.toJson() for creature in creatures]}, 
            file, indent=4)

    def loadWorld(self, filename: str) -> dict[str: int, str: int, str: int, str: set[Creature]]:
        print(f'loading {filename}')
        with open(filename, 'r') as file:
            data = json.load(file)
            self.steps=int(data['steps'])
            self.mapHeight=data['mapheight']
            self.mapWidth=data['mapwidth']
            self.creatures = set([
                Creature.fromJson(c, map.nodes[c['location']])
                for c in data['creatures']
            ])
        self.map = Map(mapWidth=self.mapWidth, mapHeight=self.mapHeight)
        return {
            'steps': self.steps,
            'map': self.map,
            'creatures': self.creatures
        }

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
