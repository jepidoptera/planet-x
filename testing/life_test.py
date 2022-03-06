import unittest
from world.map import *
from creatures import templates
from world import life
class testLife(unittest.TestCase):
    def test_flee(self):
        world=Map(20, 10).populateGrass(10, 1.0)
        danrsveej=templates.danrsveej(world.nodes[42]).faceDirection(4)
        deerkiller=templates.deerkiller(world.nodes[22]).faceDirection(2)
        # slowdanr=templates.danrsveej(world.nodes[43]).faceDirection(4)
        danrsveej.speed=9
        danrsveej.stamina=9
        # slowdanr.speed=4
        creatures=[danrsveej, deerkiller]
        scene=life.Scene(world, creatures)
        preyLocation=danrsveej.location.index
        predatorLocaion=deerkiller.location.index
        print (f'danrsveej metabolism={danrsveej.metabolism}')
        print (f'deerkiller metabolism={deerkiller.metabolism}')
        # give the poor danrsveej a head start
        deerkiller.thinkTimer=0
        for n in range(200):
            scene.step()
            if preyLocation != danrsveej.location.index:
                preyLocation=danrsveej.location.index
                print (f'danrsveej at {preyLocation} (action {danrsveej.action})')
            if predatorLocaion != deerkiller.location.index:
                predatorLocaion=deerkiller.location.index
                print (f'deerkiller at {predatorLocaion} (action {deerkiller.action})')
            # if slowdanr.dead:
            #     print (f'slow one died at {n}')
            #     slowdanr._dead=False
            if danrsveej.dead:
                print (f'died at step {n}')
                break
        self.assertTrue(not danrsveej.dead)
