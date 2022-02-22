from creatures import templates
from world.map import *
from creatures.creature import *
from creatures.genome import *
import random
from curses import wrapper
import curses


map = Map(32, 24)
creatures = [Creature(map, random.choice(map.nodes), randomGenome(), 32) for n in range(10)]

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # This raises ZeroDivisionError when i == 10.
    for i in range(0, 11):
        v = i-10
        stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))
    
    width = curses.LINES
    height = curses.LINES
    over = False
    creatures: list[Creature] = [templates.herbivore for n in range(100)] + [templates.carnivore for n in range(10)]
    thoughtThreshold = 60
    moveThreshold = 60
    while not over:
        random.choice(map.nodes).resource = Resource(ResourceType.grass, 1)
        aliveCreatures: list[Creature] = []

        for creature in creatures:
            creature.thinkTimer += creature.intelligence
            if creature.thinkTimer > thoughtThreshold:
                creature.thinkTimer -= thoughtThreshold
                creature.think()

            creature.moveTimer += creature.speed
            if creature.moveTimer > moveThreshold:
                creature.moveTimer -= moveThreshold
                creature.animate()

            if not creature.dead: aliveCreatures.append(creature)
            if creature.offspring: aliveCreatures.append(creature.offspring)

        creatures = aliveCreatures

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)
