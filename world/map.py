class Node():
    def __init__(self, index, neighbors: list):
        self.index = index
        self.neighbors = neighbors
        self.occupant = None
        self.visionTree = []
    
def calcVisionTree(startingNode: Node, distance: int):
    mergedDict = {n:True for n in startingNode.neighbors + [startingNode]}
    visionTree = [[[node]] + [[] for i in range(distance)] for node in startingNode.neighbors]

    for i in range(distance):
        visionLayer = {}
        for t in range(len(visionTree)):
            nodesThisTree = 0
            for n in visionTree[t][i]:
                # n is a node
                for j in range(len(n.neighbors)):
                    nextNode = n.neighbors[(j + t) % len(n.neighbors)]
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
    for cone in range(len(visionTree)):
        print ("cone {0}".format(cone))
        for sightrange in range(len(visionTree[cone])):
            print ([node.index for node in visionTree[cone][sightrange]])

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
    
    def print(self):
        for y in range(self.mapHeight):
            print (''.join(["{0}    ".format(y + n * self.mapHeight * 2) for n in range(int(self.mapWidth / 2))]))
            print (''.join(["  {0}  ".format(y + self.mapHeight + n * self.mapHeight * 2) for n in range(int(self.mapWidth / 2))]))

# map = Map(16, 10)
# calcVisionTree(map.nodes[45], 3)
