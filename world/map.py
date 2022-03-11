from enum import Enum
from math import *
import random

sign=lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

class ResourceType(Enum):
    grass='grass'
    fruit='fruit'
    meat='meat'
    tree='tree'

class Resource():
    type: ResourceType
    value: int
    def __init__(self, type: ResourceType, value: int, location=None):
        self.type=type
        self.value=value
        self.location=location

class MapNode():
    def __init__(self, index: int=-1, neighbors: list=[], x: float=0.0, y: float=0.0, z: float=0.0):
        self.index=index
        self.neighbors=neighbors
        self.occupant: any=None
        self.resource: Resource=None
        self.obstruction: any=None
        self.visionTree=[]
        self.x=x
        self.y=y
        self.z=z

    def getVision(self, lookDirection: int, distance: int, viewAngle: int):
        visionRanges: list[set[MapNode]]=[set() for n in range(distance + 1)]
        visionRanges[0].add(self)

        def rotateLeft(origin: MapNode, direction: int, amount: int):
            return (direction - amount) % len(origin.neighbors)

        def rotateRight(origin: MapNode, direction: int, amount: int):
            return (direction + amount) % len(origin.neighbors)

        forwardNode: MapNode=self
        for d in range(1, distance + 1):
            nodesInRange=int(min(d*viewAngle + 2, d*6))
            forwardNode=forwardNode.neighbors[lookDirection]
            visionRanges[d].add(forwardNode)
            
            for rotation in [rotateRight, rotateLeft]:
                scanDirection=rotation(forwardNode, lookDirection, 2)
                scanningNode: MapNode=forwardNode
                for n in range(nodesInRange//2):
                    if n > 0 and n % d == 0:
                        scanDirection=rotation(scanningNode, scanDirection, 1)
                    scanningNode=scanningNode.neighbors[scanDirection]
                    visionRanges[d].add(scanningNode)

        return visionRanges

    def calcVisionTree(self, distance: int):
        return
        mergedDict={n:True for n in self.neighbors + [self]}
        visionTree=[[[node]] + [[] for i in range(distance - 1)] for node in self.neighbors]

        for i in range(distance - 1):
            visionLayer={}
            for t in range(len(visionTree)):
                nodesThisTree=0
                for n in visionTree[t][i]:
                    # n is a node
                    for j in range(len(n.neighbors)):
                        nextNode=n.neighbors[(j + t + 3 * (t % 2)) % len(n.neighbors)]
                        if nextNode not in mergedDict.keys():
                            if nextNode not in visionLayer.keys():
                                visionLayer[nextNode]=t
                                # print (nextNode.index, t, j)
                                nodesThisTree += 1
                        if nodesThisTree > i + 1:
                            break
            # print (["{0}, {1}".format(key.index, visionLayer[key]) for key in visionLayer.keys()])
            for node in visionLayer.keys():
                cone=visionLayer[node]
                visionTree[cone][i+1].append(node)
                mergedDict[node]=True
        # for cone in range(len(visionTree)):
        #     print ("cone {0}".format(cone))
        #     for sightrange in range(len(visionTree[cone])):
        #         visionTree[cone][sightrange].sort(key=lambda node: node.index)
        #         print ([node.index for node in visionTree[cone][sightrange]])
        
        self.visionTree=visionTree


class Map():
    def __init__(self, mapWidth, mapHeight):
        mapHeight=mapHeight//2*2
        mapWidth=mapWidth//2*2
        self.mapWidth, self.mapHeight=mapWidth, mapHeight
        self.totalNodes=mapWidth * mapHeight
        self.nodes=[MapNode(n, []) for n in range(self.totalNodes)]
        
        for i, node in enumerate(self.nodes):
            node.x=i//mapHeight
            node.y=i % mapHeight + (i//mapHeight % 2)/2
            node.z=0

        for i, node in enumerate(self.nodes):
            neighborIndexes=[]
            if int(i / mapHeight) % 2 == 1:
                # odd row
                neighborIndexes=[-1, mapHeight, mapHeight + 1, 1, -mapHeight + 1, -mapHeight]
            else:
                # even row
                neighborIndexes=[-1, mapHeight - 1, mapHeight, 1, -mapHeight, -mapHeight - 1]
            
            # corrections to wrap around at the edge of the map
            if node.x == 0:
                neighborIndexes[4] += mapHeight * mapWidth
                neighborIndexes[5] += mapHeight * mapWidth
            elif node.x == mapWidth-1:
                neighborIndexes[1] -= mapHeight * mapWidth
                neighborIndexes[2] -= mapHeight * mapWidth
            
            if node.y == 0:
                neighborIndexes[0] += mapHeight
                neighborIndexes[1] += mapHeight
                neighborIndexes[5] += mapHeight
            elif node.y == 0.5:
                neighborIndexes[0] += mapHeight
            elif node.y == mapHeight-1:
                neighborIndexes[3] -= mapHeight
            elif node.y == mapHeight-0.5:
                neighborIndexes[2] -= mapHeight
                neighborIndexes[3] -= mapHeight
                neighborIndexes[4] -= mapHeight
            for _, n in enumerate(neighborIndexes):
                # if (i + n) >= 0 and (i + n) < len(self.nodes):
                    newNeighbor=self.nodes[(i + n) % self.totalNodes]
                    # if (abs(newNeighbor.x-node.x <= 1) 
                    #     and abs(newNeighbor.y-node.y <= 1) 
                    #     and abs(newNeighbor.z - node.z <= 1)
                    # ):
                    node.neighbors.append(newNeighbor)

        for node in self.nodes:
            node.calcVisionTree(7)
    
    def populateGrass(self, value: int=10, density: float=0.1):
        for node in self.nodes:
            if random.random() < density:
                node.resource=Resource(ResourceType.grass, value, node)
        return self

    def parseVisionTree(self, startIndex: int, direction: int, distance: int, coneWidth: int):
        cones=[
            # layer[a] for a in range[distance]
            self.nodes[startIndex].visionTree[(direction + n) % len(self.nodes[startIndex].neighbors)][:distance] 
            for n in [-int(n/2) if n % 2== 0 else int(n/2) + 1 
            for n in range((coneWidth - 1) * 2 + 1)] 
        ]
        visionLayers=[
            # don't worry about it, it works fine
            [node.index for cone in [[cones[a][b] 
            for a in range(len(cones))] for b in range(distance)][i] 
            for node in cone] for i in range(distance)
        ]
        nodeList=[node for cone in visionLayers for node in cone]
        
    def print(self, highlights: set[MapNode]=set()):

        # visionCone=self.nodes[startIndex].visionTree[direction]
        # nodeList=[node.index for layer in visionCone[:distance] for node in layer]

        def highlight(index) -> str:
            if not highlights: return str(index)
            if self.nodes[index] in highlights: return "█"*(len(str(index)))
            return str(index) 

        for y in range(self.mapHeight):
            oddRow=[self.nodes[y + n * self.mapHeight * 2] for n in range(int(self.mapWidth / 2))]
            evenRow=[self.nodes[y + self.mapHeight + n * self.mapHeight * 2] for n in range(int(self.mapWidth / 2))]
            print(''.join(["{0}   ".format(highlight(' ' * (3-len(str(node.index))) + str(node.index))) for node in oddRow]))
            print(''.join(["   {0}".format(highlight(' ' * (3-len(str(node.index))) + str(node.index))) for node in evenRow]))

    @staticmethod
    def fleePath(startNode: MapNode, fleeFrom:MapNode, safeDistance:int=5):
        # modified A*
        maxout=150 # if openlist exceeds this length, return path to currentNode
        class nodeOption():
            def __init__(self, node: MapNode, previous: MapNode, pathLength: int=0, distanceTraveled: int=0, distFrom: int=0):
                self.node=node
                self.previous=previous
                self.pathLength=pathLength # estimated total path length
                self.distFrom=distFrom
                self.distanceTraveled=distanceTraveled # distance traveled so far

        openList=set([nodeOption(startNode, 0)])
        closedList=set()
        while openList:
            currentNode=min(openList, key=lambda node: node.pathLength)
            openList.remove(currentNode)
            closedList.add(currentNode.node.index)

            for neighbor in currentNode.node.neighbors:
                dist=Map.getDistance(fleeFrom, neighbor)
                if dist >= safeDistance:
                    # that'll do
                    path=[neighbor]
                    while True:
                        if currentNode.node == startNode: break
                        path=[currentNode.node] + path
                        currentNode=currentNode.previous
                    return path

                if neighbor.index in closedList or neighbor.obstruction or neighbor.occupant:
                    continue

                remainingDistance=safeDistance-dist
                distanceTraveled=currentNode.distanceTraveled + 1
                pathLength=distanceTraveled + remainingDistance
                for i, option in enumerate(openList):
                    if option.node == neighbor:
                        if option.distanceTraveled > distanceTraveled:
                            openList.remove(option)
                            openList.add(nodeOption(neighbor, currentNode, pathLength, distanceTraveled, dist))
                        break
                openList.add(nodeOption(neighbor, currentNode, pathLength, distanceTraveled))
                if len(openList) > maxout:
                    # return the best we've found so far
                    currentNode=max(openList, key=lambda node: node.distFrom)
                    path=[]
                    while True:
                        if currentNode.node == startNode: break
                        path=[currentNode.node] + path
                        currentNode=currentNode.previous
                    return path

    @staticmethod
    def findPath(startNode: MapNode, endNode: MapNode) -> list[MapNode]:
        # good ol' A* algorithm
        maxout=100
        class nodeOption():
            def __init__(self, node: MapNode, previous: MapNode=None, pathLength: int=0, distanceTraveled: int=0):
                self.node=node
                self.previous=previous
                self.pathLength=pathLength # estimated total path length
                self.distanceTraveled=distanceTraveled # distance traveled so far

        openList=set([nodeOption(startNode, 0)])
        closedList=set()
        while openList:
            currentNode=min(openList, key=lambda node: node.pathLength)
            openList.remove(currentNode)
            closedList.add(currentNode.node.index)

            for neighbor in currentNode.node.neighbors:
                if neighbor == endNode:
                    path=[neighbor]
                    while True:
                        if currentNode.node == startNode: break
                        path=[currentNode.node] + path
                        currentNode=currentNode.previous
                    return path

                if neighbor.index in closedList or neighbor.obstruction or neighbor.occupant:
                    continue

                remainingDistance=Map.getDistance(neighbor, endNode)
                distanceTraveled=currentNode.distanceTraveled + 1
                pathLength=distanceTraveled + remainingDistance
                for option in openList:
                    if option.node == neighbor:
                        if option.distanceTraveled > distanceTraveled:
                            openList.remove(option)
                            openList.add(nodeOption(neighbor, currentNode, pathLength, distanceTraveled))
                        break
                openList.add(nodeOption(neighbor, currentNode, pathLength, distanceTraveled))
                if len(openList) > maxout: 
                    return []

    @staticmethod
    def getDistance(a: MapNode, b: MapNode):
        # x0=a.x-a.y
        # y0=a.y
        # x1=b.x-b.y
        # y1=b.y
        # dx=x1 - x0
        # dy=y1 - y0
        dx=abs(a.x - b.x)
        dy=int(max(abs(a.y - b.y) - dx/2, 0))
        return dx + dy # max(abs(dx), abs(dy), abs(dx+dy))     

    def clear(self):
        for node in self.nodes:
            node.obstruction=None
            node.occupant=None
            node.resource=None

# map=Map(16, 10)
# calcVisionTree(map.nodes[45], 3)
