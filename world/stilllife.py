from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
import json
# from curses import wrapper
# import curses


# import pstats
# from pstats import SortKey
# p = pstats.Stats('restats')
# p.strip_dirs().sort_stats(-1).print_stats()

# p.sort_stats(SortKey.CUMULATIVE).print_stats(25)

mapWidth: int=32
mapHeight: int=24
viewX: float=0
viewY: float=0
map = Map(mapWidth, mapHeight)
# creatures = [Creature(random.choice(map.nodes), randomGenome(), randomGenome(), energy=32) for n in range(10)]

# def main(stdscr):
def main():
    # Clear screen
    # stdscr.clear()
    
    over=False
    steps=0
    # creatures: set[Creature] = (
    #     [templates.herbivore(random.choice(map.nodes)) for n in range(100)] 
    #     + [templates.carnivore(random.choice(map.nodes)) for n in range(10)]
    # )
    herb = templates.herbivore()
    carn = templates.carnivore()
    # now add some random in the mix
    # 3/4 prefab, 1/4 rando
    creatures: set[Creature] = (
        [templates.cross(herb, templates.cross(herb, templates.rando()), random.choice(map.nodes)) for n in range(100)] 
        + [templates.cross(carn, templates.cross(carn, templates.rando()), random.choice(map.nodes)) for n in range(100)]
    )
    # they have served their purpose
    del(herb)
    del(carn)

    for creature in creatures:
        creature.age = random.random() * 100 * creature.longevity

    # creatures = [Creature(random.choice(map.nodes), randomGenome(), randomGenome(), energy=100) for n in range(100)]
    thoughtThreshold = 60
    moveThreshold = 60
    while not over:
        random.choice(map.nodes).resource = Resource(ResourceType.grass, 1)
        aliveCreatures: set[Creature] = set()
        steps+=1
        for creature in creatures:
            # worldPad.addstr(int(creature.location.y), int(creature.location.x*4), '.')
            # if (creature.location.x*4 < curses.COLS and creature.location.y*2 + creature.location.x%2 < curses.LINES):
            #     stdscr.addstr(int(creature.location.y*2 + creature.location.x%2), int(creature.location.x * 4), '.')
            creature.thinkTimer += creature.intelligence/2
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
                creature.offSpring=None
            # worldPad.addstr(int(creature.location.y), int(creature.location.x*4), creature.speciesName[0])
            # if (creature.location.x*4 < curses.COLS and creature.location.y*2 + creature.location.x%2 < curses.LINES):
            #     stdscr.addstr(int(creature.location.y*2 + creature.location.x%2), int(creature.location.x * 4), creature.speciesName[0])
        creatures = aliveCreatures
        # print (f'creature 0 at: {creatures[0].location.x, creatures[0].location.y}')


        # stdscr.addstr(0, 0, str(steps))
        # stdscr.refresh()
        # inKey=stdscr.getkey()
        # if inKey=='q': over=True

        if steps % 10 == 0:
            # count surviving species
            print (f'steps: {steps}')
            species={}
            for creature in creatures:
                if not creature.speciesName in species:
                    species[creature.speciesName]=0
                species[creature.speciesName] += 1

            topSpecies = [(name, number) for i, (name, number) in enumerate(species.items())]
            topSpecies.sort(key=lambda x: -x[1])
            for y in range(3):
                print(f'{topSpecies[y][0]}: {topSpecies[y][1]}')
            # print()
            # print (*[f'{species}: {number}' for i, (species, number) in enumerate(species.items())], sep='\n')
# wrapper(main)

def save(creatures: set[Creature], filename: str):
    with open(filename, 'w') as file:
        json.dump([creature.toJson() for creature in creatures], file, indent=4)

main()

