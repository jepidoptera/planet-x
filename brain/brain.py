from brain.basics import *
# from enum import Enum
# import typing
from creatures.creature import Creature
from world.map import MapNode

# sign=lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

# class NeuronType(Enum):
#     self=0
#     creature=1
#     environment=2
#     memory=3
#     relay=4
#     action=5

# class Neuron():
#     activation:float
#     sense:typing.Callable
#     action:typing.Callable
#     type:NeuronType
#     name:str
#     bias:float
#     def __init__(self, index: int, type: NeuronType, name:str='', sense: typing.Callable=None, action: typing.Callable=None, bias: float=0.0):
#         self.activation=0.0
#         self._sense=sense
#         self.action=action
#         self.type=type
#         self.name=name
#         self.bias=bias
#         self.index=index
#         if not name in netIndex: netIndex[name]=self.index
#     def sense(self, *args):
#         self.activate(self._sense(*args))
#     def activate(self, amount):
#         self.activation += amount
#     def clear(self):
#         self.activation=self.bias
# # 🙌🏾

# class MemNeuron(Neuron):
#     sense=None
#     action=None
#     type=NeuronType.memory
#     threshold=0.5
#     strength=1.0

#     def __init__(self, memstate:bool=True, name:str=''):
#         super().__init__(NeuronType.memory, name=name)
#         self.memState=memstate
#     def activate(self, amount):
#         if abs(amount) > self.threshold: self.memState=1 if amount > 0 else 0
#         self.clear()
#     def clear(self):
#         self.activation=self.memState * self.strength

# class Axon():
#     def __init__(self, input: Neuron, output: Neuron, factor: float):
#         self.input=input
#         self.output=output
#         self.factor=factor


#     def fire(self):
#         self.output.activate(self.input.activation * self.factor)

#     def __str__(self) -> str:
#         return (
#             hex(self.input.index)[2:].zfill(2) + 
#             hex(self.output.index)[2:].zfill(2) +
#             hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
#         )

# class DoubleAxon(Axon):
#     operators={
#         'and': 0,
#         'or': 1,
#         'nor': 2,
#         'xor': 3,
#         'and not': 4
#     }
#     def __init__(self, input: list[Neuron], output: Neuron, threshold: float, operator: int, factor: float):
        
#         self._input=input
#         self.output: Neuron=output
#         self.threshold=threshold
#         self.factor=factor
#         self.operator=operator

#     def fire(self):
#         # there is room for up to 256 different operators
#         # just probably gonna use 8
#         if self.operator == 0:
#             # AND
#             if (self._input[0].activation >= self.threshold and self._input[1].activation >= self.threshold):
#                 self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
#         elif self.operator == 1:
#             # OR
#             if (self._input[0].activation >= self.threshold or self._input[1].activation >= self.threshold):
#                 self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
#         elif self.operator == 2:
#             # NOR 
#             if (self._input[0].activation < self.threshold and self._input[1].activation < self.threshold):
#                 self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
#         elif self.operator == 3:
#             # XOR
#             if ((self._input[0].activation >= self.threshold) ^ (self._input[1].activation >= self.threshold)):
#                 self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
#         elif self.operator == 4:
#             # and not
#             if (self._input[0].activation >= self.threshold and not self._input[1].activation >= self.threshold):
#                 self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)

#     @property
#     def input(self):
#         return self._input[0]

#     @property
#     def input2(self):
#         return self._input[1]

#     def __str__(self) -> str:
#         return (
#             'FF' + 
#             hex(self.operator)[2:].zfill(2) + 
#             hex(int(self.threshold * 0xff))[2:].zfill(2) + 
#             hex(self._input[0].index)[2:].zfill(2) + 
#             hex(self._input[1].index)[2:].zfill(2) + 
#             hex(self.output.index)[2:].zfill(2) +
#             hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
#         )


# class Stimulus():
#     def __init__(self, object: any, distance: float):
#         self.object=object
#         self.distance=distance

# class ActionOption():
#     def __init__(self, action: str, target: any, weight: float, relevantNeuron: Neuron):
#         self.action=action
#         self.target=target
#         self.weight=weight
#         self.neuron=relevantNeuron

# class Action():
#     attack='attack'
#     flee='flee'
#     mate='mate'
#     eat='eat'
#     wander='wander'
#     rest='rest'
#     turnLeft='turn left'
#     turnRight='turn right'
#     sprint='sprint'
#     move='move'
#     howl='howl'

# netIndex: dict[str, Neuron]={}

class V1(Brain):
        # list[Neuron](
        # )
    def __init__(self, speciesName: str, axons: list[Axon], neurons: list[Neuron]):
        super().__init__(speciesName=speciesName)
        if axons: self.axons

    def process(self, *stimuli: Stimulus) -> tuple[str, any]:
        for stimulus in stimuli:
            object=stimulus.object
            self.clear()
            if type(object) == Creature and stimulus.distance <= 0:
                # self
                for sensor in self.selfNeurons:
                    sensor.sense(object)

            elif type(object) == Creature:
                for sensor in self.creatureNeurons:
                    sensor.sense(object)
                for axon in self.creatureAxons:
                    axon.fire()

            elif type(object) == MapNode:
                # food, probably
                for sensor in self.envNeurons:
                    sensor.sense(object)
                for axon in self.envAxons:
                    axon.fire()

            for axon in self.selfAxons + self.relayAxons + self.memoryAxons + self.actionAxons:
                axon.fire()


    
    def unpack(self, axonStr: str='', neuronStr: str=''):
        # def get_key(val, dict: dict):
        #     for key, value in dict.items():
        #         if val == value:
        #             return key
        if axonStr:
            def fromHex(hexcode):
                if len(hexcode) == 8:
                    input = int(hexcode[:2], 16) % 0x60
                    output = int(hexcode[2:4], 16) % 0x60
                    factor = int(hexcode[4:8], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
                    
                    if not input in self.allNeurons or not output in self.allNeurons:
                        return None

                    return Axon(
                        input=self.allNeurons[input],
                        output=self.allNeurons[output], 
                        factor=factor
                    )
                elif len(hexcode) == 16:
                    operator=int(hexcode[2:4], 16) % 0xf8
                    threshold=int(hexcode[4:6], 16)/0xff
                    input1=int(hexcode[6:8], 16) % 0x60
                    input2=int(hexcode[8:10], 16) % 0x60
                    output=int(hexcode[10:12], 16) % 0x60
                    factor=int(hexcode[12:16], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero

                    if not input1 in self.allNeurons or not input2 in self.allNeurons or not output in self.allNeurons:
                        return None

                    return DoubleAxon(
                        input=[self.allNeurons[n] for n in [input1, input2]],
                        output=self.allNeurons[output],
                        threshold=threshold,
                        operator=operator,
                        factor=factor
                    )
                else:
                    raise Exception(f"invalid hex code length ({len(hexcode)}), can't generate axon")

            doubleAxon=False
            self.actionAxons=[]
            self.relayAxons=[]
            self.memoryAxons=[]
            self.creatureAxons=[]
            self.envAxons=[]
            self.selfAxons=[]
            for n in range(int(len(axonStr)/8)):
                if doubleAxon:
                    doubleAxon=False
                    continue
                
                if int(axonStr[n*8: n*8 + 2], 16) != 0xff:
                    axon=fromHex(axonStr[n * 8: (n + 1) * 8])
                else:
                    axon=fromHex(axonStr[n*8: (n+2)*8])
                    doubleAxon=True

                if (axon.input.type == NeuronType.action
                    or type(axon) == DoubleAxon 
                    and axon.input2.type == NeuronType.action
                ):
                    self.actionAxons.append(axon)

                elif (axon.input.type == NeuronType.relay
                    or type(axon) == DoubleAxon 
                    and axon.input2.type == NeuronType.relay
                ):
                    self.relayAxons.append(axon)

                elif (axon.input.type == NeuronType.creature
                    or type(axon) == DoubleAxon 
                    and axon.input2.type == NeuronType.creature
                ):
                    self.creatureAxons.append(axon)

                elif (axon.input.type == NeuronType.environment
                    or type(axon) == DoubleAxon 
                    and axon.input2.type == NeuronType.environment
                ):
                    self.envAxons.append(axon)

                elif (axon.input.type == NeuronType.self
                    or type(axon) == DoubleAxon 
                    and axon.input2.type == NeuronType.self
                ):
                    self.selfAxons.append(axon)

                elif (axon.input.type == NeuronType.memory
                    or type(axon) == DoubleAxon 
                    and axon.input2.type == NeuronType.memory
                ):
                    self.memoryAxons.append(axon)

            self.allAxons=self.creatureAxons + self.envAxons + self.selfAxons + self.memoryAxons + self.relayAxons + self.actionAxons
        
        if neuronStr:
            for n in range(len(neuronStr)//4):
                self.allNeurons[int(n[:2], 16)].bias=(int(n[2:], 16) / 0xff -0.5)*2

        return self

    def loadBiases(self, biases: list[float]):
        for n, b in enumerate(biases):
            self.allNeurons[n]=b
        return self

    def getSimilarity(self, other: Creature) -> float:
        similarity=0.0
        commonRange=range(min(len(self.speciesName), len(other.speciesName)))
        increment=1/len(commonRange)
        for c in commonRange:
            if self.speciesName[c] == other.speciesName[c]: similarity += increment
        return similarity

    def clear(self):
        for neuron in self.allNeurons:
            neuron.clear()
