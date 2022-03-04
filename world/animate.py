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
            if inKey==ord('k'): viewY = min(viewY+1, mapHeight-viewHeight-1)
            if inKey==ord('j'): viewX = max(viewX-1, 0)
            if inKey==ord('l'): viewX = min(viewX+1, mapWidth-viewWidth//2+2) # 120 - 192 = 27
            if inKey==ord('t'): self.creatures.add(templates.carnivore(random.choice(self.world.nodes), energy=10, mutate=True))
            if inKey==ord('c'): self.creatures.add(templates.scavenger(random.choice(self.world.nodes), energy=10, mutate=True))
            
            for y in range(viewY, viewY + min(mapHeight-1, viewHeight-5)):
                row = [
                    self.world.nodes[x*mapHeight*2 + (y % 2)*mapHeight + y//2] 
                    for x in range(viewX, viewX + viewWidth//5-5)
                ]
                line = '' if y % 2 == 0 else '   '
                for node in row:
                    if node.occupant:
                        line += (
                            node.occupant.speciesName[0].upper() if node.occupant.meateating > node.occupant.planteating 
                            else node.occupant.speciesName[0]
                        )
                    elif node.resource:
                        line += '+' if node.resource.type == ResourceType.meat else '"'
                    else:
                        line += ' '
                    line += '     '
                stdscr.addstr(y-viewY, 0, line)

            # show top existing species
            stdscr.addstr(viewHeight - 5, 0, f'total:{len(self.creatures)}   ')
            stdscr.addstr(viewHeight - 4, 0, f'viewport: {viewX} {viewY} x {viewWidth//5 + viewX} {viewHeight + viewY}')
            for y in range(min(3, len(species))):
                stdscr.addstr(viewHeight-3+y, 0, f'{species[y][0]}: {species[y][1]}   ')
