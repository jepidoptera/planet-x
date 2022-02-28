from creatures.creature import Creature
from world.map import Map
from world import life

class TextWorld():
    def __init__(self, scenario: life.Scene):
        self.world=scenario.world
        self.creatures=scenario.creatures
        self.scenario=scenario
    
    def run(self):
        over=False
        steps=0
        while not over:
            self.scenario.step()
            steps=self.scenario.steps
            if steps % 50 == 0:
                # count surviving species
                print (f'steps: {steps}')
                species = life.countSpecies(self.creatures)
                print (f'total{len(self.creatures)}')
                for y in range((min(5, len(species)))):
                    print(f'{species[y][0]}: {species[y][1]}')

    # main()

