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
viewX: int=0
viewY: int=0
map = Map(mapWidth, mapHeight)
# creatures = [Creature(random.choice(map.nodes), randomGenome(), randomGenome(), energy=32) for n in range(10)]

def main(stdscr):
    # Clear screen
    stdscr.clear()
    # stdscr.nodelay(True)
    
    over=False
    steps=0
    # the progenitors of all life
    herb = templates.herbivore()
    carn = templates.carnivore()
    # now add some random in the mix
    creatures: set[Creature] = (
        [templates.cross(herb, templates.rando(), random.choice(map.nodes)) for n in range(100)] 
        + [templates.cross(carn, templates.rando(), random.choice(map.nodes)) for n in range(20)]
    )
    # they have served their purpose
    del(herb)
    del(carn)

    for creature in creatures:
        creature.age = random.random() * 90 * creature.longevity

    thoughtThreshold = 60
    moveThreshold = 60
    
    while not over:
        random.choice(map.nodes).resource = Resource(ResourceType.grass, 10)
        aliveCreatures: set[Creature] = set()
        species={}
        topspecies=[]
        steps+=1
        for creature in creatures:
            # count surviving species
            if not creature.speciesName in species:
                species[creature.speciesName]=0
            species[creature.speciesName] += 1
            
            # worldPad.addstr(int(creature.location.y), int(creature.location.x*4), '.')
            # if (creature.location.x*4 < curses.COLS and creature.location.y*2 + creature.location.x%2 < curses.LINES):
            #     stdscr.addstr(round(creature.location.y*2 + creature.location.x%2), round(creature.location.x * 4), '.')
            creature.thinkTimer += creature.intelligence
            if creature.thinkTimer > thoughtThreshold:
                creature.thinkTimer -= thoughtThreshold
                creature.think()

            creature.moveTimer += creature.speed
            if creature.moveTimer > moveThreshold:
                creature.moveTimer -= moveThreshold
                creature.animate()

            if not creature.dead: aliveCreatures.add(creature)
            if creature.offspring: 
                aliveCreatures.add(creature.offspring)
                creature.offspring=None
            # worldPad.addstr(int(creature.location.y), int(creature.location.x*4), creature.speciesName[0])
            # if (creature.location.x*4 < curses.COLS and creature.location.y*2 + creature.location.x%2 < curses.LINES):
            #     stdscr.addstr(round(creature.location.y*2 + creature.location.x%2), round(creature.location.x * 4), creature.speciesName[0])
        creatures = aliveCreatures
        # print (f'creature 0 at: {creatures[0].location.x, creatures[0].location.y}')

        stdscr.addstr(0, 0, str(steps))
        stdscr.refresh()
        inKey=stdscr.getch()
        if inKey==ord('q'): over=True
        for y in range(viewY, min(curses.LINES, mapHeight-1)):
            row = [map.nodes[x*mapHeight*2 + (y % 2)*mapHeight + y//2] 
                for x in range(viewX, min(curses.COLS//5 - 2, mapWidth//2-1))]
            line = '' if y % 2 == 0 else '   '
            for node in row:
                if node.occupant:
                    line += node.occupant.speciesName[0].upper() if node.occupant.victim else node.occupant.speciesName[0]
                elif node.resource:
                    line += '+' if node.resource.type == ResourceType.meat else '"'
                else:
                    line += '.'
                line += '     '
            stdscr.addstr(y, 0, line)
        topSpecies = [(name, number) for i, (name, number) in enumerate(species.items())].sort(key=lambda x: x[1])
        for y in range(3):
            stdscr.addstr(40+y, 0, f'{topSpecies[0]}: {topSpecies[1]}')
    
    print (steps)
    print (*[f'{species}: {number}' for i, (species, number) in enumerate(species.items())], sep='\n')
wrapper(main)

def save(creatures: set[Creature], filename: str):
    with open(filename, 'w') as file:
        file.write(json.dumps(creatures))