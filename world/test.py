from world.map import *
from creatures.creature import *
from creatures.genome import *
from creatures import templates

mapWidth = 30
mapHeight = 20
centerTile = int(mapWidth * mapHeight / 2 + mapHeight / 2)
testmap = Map(mapWidth, mapHeight)
# calcVisionTree(testmap.nodes[146], 8)
for n in range(6):
    testmap.printVisionCone(centerTile, n, 7, 2)
    print()
print()
testmap.printVisionCone(centerTile, 0, 0, 0)

