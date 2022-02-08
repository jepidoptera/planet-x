class Node():
    def __init__(self, index, neighbors: list):
        self.index = index
        self.neighbors = neighbors
        self.occupant = None
        self.visionTree = []
    
def calcVisionTree(startingNode: Node, distance: int):
    mergedDict = {n:True for n in startingNode.neighbors}
    visionTree = [[startingNode]]

    class VisionBranch():
        base: Node
        neighbors: list

    for i in range(distance):
        visionLayer = {}
        for t in range(len(visionTree)):
            for n in visionTree[t][i]:
                # n is a node
                for j, nextNode in enumerate(n.neighbors):
                    if nextNode not in mergedDict.keys():
                        if nextNode not in visionLayer.keys():
                            visionLayer[nextNode] = (t, j)
                        else:
                            if visionLayer[nextNode][1] > j:
                                # replace
                                visionLayer[nextNode] = (t, j)
        print ([key.index for key in visionLayer.keys()])
        for node in visionLayer.keys():
            nodeTuple = visionLayer[node]
            visionTree[nodeTuple[0]][i+1].append(node)
            mergedDict[node] = True
