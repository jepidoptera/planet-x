from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
from curses import wrapper
import curses

mapWidth: int=32
mapHeight: int=24
viewX: float=0
viewY: float=0
map = Map(mapWidth, mapHeight)
creatures = [Creature(random.choice(map.nodes), randomGenome(), randomGenome(), energy=32) for n in range(10)]

def main(stdscr):
    # Clear screen
    stdscr.clear()
    # stdscr.nodelay(True)
    
    over=False
    steps=0
    creatures: set[Creature] = (
        [templates.herbivore(random.choice(map.nodes)) for n in range(100)] 
        + [templates.carnivore(random.choice(map.nodes)) for n in range(10)]
    )
    thoughtThreshold = 60
    moveThreshold = 60
    while not over:
        random.choice(map.nodes).resource = Resource(ResourceType.grass, 10)
        aliveCreatures: set[Creature] = set()
        steps+=1
        for creature in creatures:
            # worldPad.addstr(int(creature.location.y), int(creature.location.x*4), '.')
            if (creature.location.x*4 < curses.COLS and creature.location.y*2 + creature.location.x%2 < curses.LINES):
                stdscr.addstr(round(creature.location.y*2 + creature.location.x%2), round(creature.location.x * 4), '.')
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
            if (creature.location.x*4 < curses.COLS and creature.location.y*2 + creature.location.x%2 < curses.LINES):
                stdscr.addstr(round(creature.location.y*2 + creature.location.x%2), round(creature.location.x * 4), creature.speciesName[0])
        creatures = aliveCreatures
        # print (f'creature 0 at: {creatures[0].location.x, creatures[0].location.y}')

        stdscr.addstr(0, 0, str(steps))
        stdscr.refresh()
        inKey=stdscr.getkey()
        if inKey=='q': over=True

    # count surviving species
    species={}
    for creature in creatures:
        if not creature.speciesName in species:
            species[creature.speciesName]=0
        species[creature.speciesName] += 1
    
    print (steps)
    print (*[f'{species}: {number}' for i, (species, number) in enumerate(species.items())], sep='\n')
wrapper(main)
