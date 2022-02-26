from creatures.creature import Creature
from world.life import *

def run(loadfile: str=''):
    
    creatures: set[Creature]
    if loadfile:
        scenario=Life.loadWorld(loadfile)

    else:
        scenario=Scenarios.herbivores_only

    creatures=scenario.creatures
    world=scenario.world

    over=False
    steps=0
    while not over:
        steps += 1
        Life.cycle(creatures, world)
        if steps % 10 == 0:
            # count surviving species
            print (f'steps: {steps}')
            species = Life.countSpecies(creatures)
            print (f'total{len(creatures)}')
            for y in range((min(5, len(species)))):
                print(f'{species[y][0]}: {species[y][1]}')

# main()

