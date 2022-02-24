from itertools import count
from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
from curses import wrapper
import curses
import json

mapWidth: int=80
mapHeight: int=40
map = Map(mapWidth, mapHeight)
loadfile = ''
loadDir='species/'

thoughtThreshold = 60
moveThreshold = 60

creatures: set[Creature]=set()

def cycle(creatures: set[Creature]):

    random.choice(map.nodes).resource = Resource(ResourceType.grass, 10)
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

        if not creature.dead: aliveCreatures.add(creature)
        if creature.offspring: 
            aliveCreatures.add(creature.offspring)
            creature.offspring=None

    return aliveCreatures

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

def animate(stdscr):
    if loadfile:
        creatures = loadCreatures(loadDir + loadfile)
    else:
        creatures = generateCreatures()
    
    # Clear screen
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.keypad(True)
    
    over=False
    steps=0

    species=[]

    viewX: int=0
    viewY: int=0
    viewWidth: int=80
    viewHeight: int=40

    while not over:

        creatures = cycle(creatures)

        steps+=1
        if steps % 10 == 0:
            species=countSpecies(creatures)

        stdscr.addstr(0, 0, str(steps))
        stdscr.refresh()
        inKey=stdscr.getch()
        if inKey==ord('q'): over=True
        if inKey==ord('s'): save(creatures, f'species/{species[0][0]} {steps}.txt')
        if inKey==curses.KEY_UP: viewY = max(viewY-1, 0)
        if inKey==curses.KEY_DOWN: viewY = min(viewY+1, mapHeight-viewHeight)
        if inKey==curses.KEY_LEFT: viewX = max(viewX-1, 0)
        if inKey==curses.KEY_RIGHT: viewX = min(viewX+1, mapWidth-viewWidth)
        
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
                    line += '.'
                line += '     '
            stdscr.addstr(y, 0, line)

        # show top existing species
        stdscr.addstr(viewHeight, 0, f'total:{len(creatures)}')
        for y in range(min(3, len(species))):
            stdscr.addstr(viewHeight+1+y, 0, f'{species[y][0]}: {species[y][1]}')
    
    # print (steps)
    # print (*[f'{species}: {number}' for i, (species, number) in enumerate(species.items())], sep='\n')

def save(creatures: set[Creature], filename: str):
    with open(filename, 'w') as file:
        json.dump([creature.toJson() for creature in creatures], file, indent=4)

def loadCreatures(filename: str) -> set[Creature]:
    print(f'loading {filename}')
    with open(filename, 'r') as file:
        creaturedata = json.load(file)
        creatures = set([
            Creature.fromJson(c, map.nodes[c['location']])
            for c in creaturedata
        ])
    return creatures

def generateCreatures():
    print(f'generating 300 random creatures...')
    herb = templates.herbivore()
    carn = templates.carnivore()
    # now add some random in the mix
    # 3/4 prefab, 1/4 rando
    creatures: set[Creature] = (
        [templates.cross(herb, templates.cross(herb, templates.rando()), random.choice(map.nodes)) for n in range(200)] 
        + [templates.cross(carn, templates.cross(carn, templates.rando()), random.choice(map.nodes)) for n in range(100)]
    )
    # they have served their purpose
    del(herb)
    del(carn)

    for creature in creatures:
        creature.age = random.random() * 90 * creature.longevity

    return creatures

def run():
    wrapper(animate)
