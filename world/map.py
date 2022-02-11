from math import *
sign = lambda x: copysign(1, x)

class Node():
    def __init__(self, index, neighbors: list):
        self.index = index
        self.neighbors = neighbors
        self.occupant = None
        self.visionTree = []
    
def calcVisionTree(startingNode: Node, distance: int):
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
                        # todo: prune the right one
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
        self.nodes = [Node(n, []) for n in range(self.totalNodes)]
        
        for i, node in enumerate(self.nodes):
            neighborIndexes = []
            if int(i / mapHeight) % 2 == 1:
                neighborIndexes = [-1, mapHeight, mapHeight + 1, 1, -mapHeight + 1, -mapHeight]
            else:
                neighborIndexes = [-1, mapHeight - 1, mapHeight, 1, -mapHeight, -mapHeight - 1]
            for _, n in enumerate(neighborIndexes):
                node.neighbors.append(self.nodes[(i + n) % self.totalNodes])

            # rotate the list
            # node.neighbors = node.neighbors[i * 11 % 6:] + node.neighbors[:i * 11 % 6]
        # print ("node {0} neighbors: {1}".format(int(self.totalNodes / 2), [n.index for n in self.nodes[int(self.totalNodes / 2)].neighbors]))

        for node in self.nodes:
            node.visionTree = calcVisionTree(node, 10)
    
    def print(self):
        for y in range(self.mapHeight):
            print (''.join(["{0}    ".format(y + n * self.mapHeight * 2) for n in range(int(self.mapWidth / 2))]))
            print (''.join(["  {0}  ".format(y + self.mapHeight + n * self.mapHeight * 2) for n in range(int(self.mapWidth / 2))]))

    def printVisionCone(self, startIndex: int, direction: int):
        visionCone = self.nodes[startIndex].visionTree[direction]
        nodeList = [node.index for layer in visionCone for node in layer]

        def showVision(index):
            if index == startIndex: return "#"* len(str(index))
            return index if index not in nodeList else "█"*(len(str(index)))

        for y in range(self.mapHeight):
            print(''.join(["{0}    ".format(showVision(y + n * self.mapHeight * 2)) for n in range(int(self.mapWidth / 2))]))
            print(''.join(["  {0}  ".format(showVision(y + self.mapHeight + n * self.mapHeight * 2)) for n in range(int(self.mapWidth / 2))]))


# map = Map(16, 10)
# calcVisionTree(map.nodes[45], 3)
