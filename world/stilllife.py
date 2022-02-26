from creatures.creature import Creature
from world.map import Map
from world import life

class TextWorld():
    def __init__(self,world: Map, creatures: set[Creature]):
        self.world=world
        self.creatures=creatures
    
    def run(self):
        over=False
        steps=0
        while not over:
            steps += 1
            life.cycle(self.world, self.creatures)
            if steps % 50 == 0:
                # count surviving species
                print (f'steps: {steps}')
                species = life.countSpecies(self.creatures)
                print (f'total{len(self.creatures)}')
                for y in range((min(5, len(species)))):
                    print(f'{species[y][0]}: {species[y][1]}')

    # main()

