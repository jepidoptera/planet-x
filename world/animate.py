from curses import wrapper
import curses
from world import life
from world.map import *
from creatures.creature import Creature
from creatures import templates
import random
import os

class Animation():
    scenario: life.Scene
    
    def __init__(self, scenario: life.Scene):
        self.world=scenario.world
        self.creatures=scenario.creatures
        self.scenario=scenario

    def run(self):
        wrapper(self.animate)

    def animate(self, stdscr):

        # Clear screen
        stdscr.clear()
        stdscr.nodelay(True)
        stdscr.keypad(True)

        species=[]

        over=False

        viewX: int=0
        viewY: int=0
        mapHeight: int=self.world.mapHeight
        mapWidth: int=self.world.mapWidth

        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        while not over:
            viewWidth, viewHeight=os.get_terminal_size()
            
            self.scenario.step()
            steps=self.scenario.steps

            if steps % 10 == 0:
                species=life.countSpecies(self.creatures)

            stdscr.addstr(0, 0, str(steps))
            stdscr.refresh()
            inKey=stdscr.getch()
            if inKey==ord('q'): over=True
            if inKey==ord('s'): life.saveWorld(self.scenario, f'{species[0][0]} {species[1][0]} {steps}')
                #life.saveCreatures(self.world, self.creatures, steps, f'species/{species[0][0]} {steps}.txt')
            if inKey==ord('i'): viewY = max(viewY-1, 0)
            if inKey==ord('k'): viewY = min(viewY+1, max(mapHeight-viewHeight-1, 0))
            if inKey==ord('j'): viewX = max(viewX-1, 0)
            if inKey==ord('l'): viewX = min(viewX+1, max(mapWidth-viewWidth//2+2, 0)) # 120 - 192 = 27
            if inKey==ord('t'): self.creatures.add(templates.carnivore(random.choice(self.world.nodes), energy=10, mutate=True))
            if inKey==ord('c'): self.creatures.add(templates.coyotefox(random.choice(self.world.nodes), energy=10, mutate=True))
            
            stdscr.clear()

            for y in range(0, min(mapHeight * 2, viewHeight-5)):
                row = [
                    self.world.nodes[x*mapHeight*2 + ((y + viewY) % 2)*mapHeight + (y + viewY)//2] 
                    for x in range(viewX, min(viewX + viewWidth//6-3, mapWidth//2))
                ]
                # line = '' if y % 2 == 0 else '   '
                # for node in row:
                #     if node.occupant:
                #         line += (
                #             node.occupant.speciesName[0].upper() if node.occupant.meateating > node.occupant.planteating 
                #             else node.occupant.speciesName[0]
                #         )
                #     elif node.resource:
                #         line += '+' if node.resource.type == ResourceType.meat else '"'
                #     else:
                #         line += ' '
                #     line += '     '
                # stdscr.addstr(y-viewY, 0, line)

                for i, node in enumerate(row):
                    x=i*6 + ((y+viewY)%2)*3
                    if node.occupant:
                        stdscr.addstr(y, x, 
                            node.occupant.speciesName[0].upper() 
                            if node.occupant.meateating > node.occupant.planteating 
                            else node.occupant.speciesName[0],
                            curses.color_pair(1) if node.occupant.justBorn else curses.color_pair(7))
                    elif node.resource and node.resource.type == ResourceType.grass:
                        stdscr.addstr(y, x, '"', curses.color_pair(2))
                    elif node.resource and node.resource.type == ResourceType.meat:
                        stdscr.addstr(y, x, '+', curses.color_pair(4))

            # show top existing species
            stdscr.addstr(viewHeight - 5, 0, f'total:{len(self.creatures)}   ')
            stdscr.addstr(viewHeight - 4, 0, f'viewport: {viewX} {viewY} x {viewWidth//5 + viewX} {viewHeight + viewY}')
            for y in range(min(3, len(species))):
                stdscr.addstr(viewHeight-3+y, 0, f'{species[y][0]}: {species[y][1]}   ')
