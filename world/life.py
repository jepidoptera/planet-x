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
    while not over:
        random.choice(map.nodes).resource = Resource(ResourceType.grass, 1)

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)
