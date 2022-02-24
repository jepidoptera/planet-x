from creatures.creature import Creature
from world import life

def main():
    
    creatures: set[Creature]
    loadfile = 'species/deetsheep.txt'
    if loadfile:
        creatures = life.loadCreatures(loadfile)
    else:
        creatures = life.generateCreatures()

    over=False
    steps=0
    while not over:
        steps += 1
        creatures = life.cycle(creatures)
        if steps % 10 == 0:
            # count surviving species
            print (f'steps: {steps}')
            species = life.countSpecies(creatures)
            for y in range(5):
                print(f'{species[y][0]}: {species[y][1]}')

main()

