from enum import Enum
from math import *
sign = lambda x: copysign(1, x)

class ResourceType(Enum):
    grass = 0
    fruit = 1
    meat = 2
    tree = 3

class Resource():
    type: ResourceType
    value: int

class MapNode():
    def __init__(self, index: int, neighbors: list, x: float=0.0, y: float=0.0, z: float=0.0):
        self.index = index
        self.neighbors = neighbors
        self.occupant: any
        self.resource: Resource
        self.visionTree = []

def calcVisionTree(startingNode: MapNode, distance: int):
    mergedDict = {n:True for n in startingNode.neighbors + [startingNode]}
    visionTree = [[[node]] + [[] for i in range(distance - 1)] for node in startingNode.neighbors]

    for i in range(distance - 1):
        visionLayer = {}
        for t in range(len(visionTree)):
            nodesThisTree = 0
            for n in visionTree[t][i]:
                # n is a node
                for j in range(len(n.neighbors)):
                    nextNode = n.neighbors[(j + t + 3 * (t % 2)) % len(n.neighbors)]
                    if nextNode not in mergedDict.keys():
                        if nextNode not in visionLayer.keys():
                            visionLayer[nextNode] = t
                            # print (nextNode.index, t, j)
                            nodesThisTree += 1
                    if nodesThisTree > i + 1:
                        break
        # print (["{0}, {1}".format(key.index, visionLayer[key]) for key in visionLayer.keys()])
        for node in visionLayer.keys():
            cone = visionLayer[node]
            visionTree[cone][i+1].append(node)
            mergedDict[node] = True
    # for cone in range(len(visionTree)):
    #     print ("cone {0}".format(cone))
    #     for sightrange in range(len(visionTree[cone])):
    #         visionTree[cone][sightrange].sort(key = lambda node: node.index)
    #         print ([node.index for node in visionTree[cone][sightrange]])
    
    return visionTree

class Map():
    def __init__(self, mapWidth, mapHeight):
        self.mapHeight = mapHeight
        self.mapWidth = mapWidth
        self.totalNodes = mapWidth * mapHeight
        self.nodes = [MapNode(n, []) for n in range(self.totalNodes)]
        
        for i, node in enumerate(self.nodes):
            neighborIndexes = []
            if int(i / mapHeight) % 2 == 1:
                # odd row
                neighborIndexes = [-1, mapHeight, mapHeight + 1, 1, -mapHeight + 1, -mapHeight]
            else:
                # even row
                neighborIndexes = [-1, mapHeight - 1, mapHeight, 1, -mapHeight, -mapHeight - 1]
            node.x = int(i / mapHeight)
            node.y = i % mapHeight * .866 + (i/mapHeight % 2) / 2
            node.z = 0
            for _, n in enumerate(neighborIndexes):
                node.neighbors.append(self.nodes[(i + n) % self.totalNodes])

        for node in self.nodes:
            node.visionTree = calcVisionTree(node, 7)
    
    def print(self):
        for y in range(self.mapHeight):
            print (''.join(["{0}    ".format(y + n * self.mapHeight * 2) for n in range(int(self.mapWidth / 2))]))
            print (''.join(["  {0}  ".format(y + self.mapHeight + n * self.mapHeight * 2) for n in range(int(self.mapWidth / 2))]))

    def printVisionCone(self, startIndex: int, direction: int, distance: int, coneWidth: int):
        cones = [
            # layer[a] for a in range[distance]
            self.nodes[startIndex].visionTree[(direction + n) % len(self.nodes[startIndex].neighbors)][:distance] 
            for n in [-int(n/2) if n % 2== 0 else int(n/2) + 1 
            for n in range((coneWidth - 1) * 2 + 1)] 
        ]
        visionLayers = [
            # don't worry about it, it works fine
            [node.index for cone in [[cones[a][b] 
            for a in range(len(cones))] for b in range(distance)][i] 
            for node in cone] for i in range(distance)
        ]
        nodeList = [node for cone in visionLayers for node in cone]
        # visionCone = self.nodes[startIndex].visionTree[direction]
        # nodeList = [node.index for layer in visionCone[:distance] for node in layer]

        def showVision(index):
            if index == startIndex: return "▓"* len(str(index))
            return index if index not in nodeList else "█"*(len(str(index)))

        for y in range(self.mapHeight):
            print(''.join(["{0}    ".format(showVision(y + n * self.mapHeight * 2)) for n in range(int(self.mapWidth / 2))]))
            print(''.join(["  {0}  ".format(showVision(y + self.mapHeight + n * self.mapHeight * 2)) for n in range(int(self.mapWidth / 2))]))


# map = Map(16, 10)
# calcVisionTree(map.nodes[45], 3)
