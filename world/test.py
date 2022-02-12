from map import *
mapWidth = 30
mapHeight = 20
centerTile = int(mapWidth * mapHeight / 2 + mapHeight / 2)
testmap = Map(mapWidth, mapHeight)
testmap.printVisionCone(centerTile, 0, 0, 0)
print()
# calcVisionTree(testmap.nodes[146], 8)
for n in range(6):
    testmap.printVisionCone(centerTile, n, 7, 2)
    print()
