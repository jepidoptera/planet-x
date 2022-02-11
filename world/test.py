from map import *
mapWidth = 50
mapHeight = 25
centerTile = int(mapWidth * mapHeight / 2 + mapHeight / 2)
testmap = Map(mapWidth, mapHeight)
testmap.print()
print()
# calcVisionTree(testmap.nodes[146], 8)
for n in range(6):
    testmap.printVisionCone(centerTile, n)
    print()