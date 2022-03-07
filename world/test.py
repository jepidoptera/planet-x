from map import *

mapWidth = 30
mapHeight = 20
testmap = Map(mapWidth, mapHeight)
centerTile = testmap.nodes[int(mapWidth * mapHeight / 2 + mapHeight / 2)]
# calcVisionTree(testmap.nodes[146], 8)
for n in range(0, 12):
    # testmap.printVisionCone(centerTile, n, 7, 2)
    vision=centerTile.getVision(5, int(12-n/2), n/2)
    for node in testmap.nodes:
        node.index='.'
    for d, layer in enumerate(vision):
        for node in layer:
            node.index=d
    testmap.print()
    print()
print()

