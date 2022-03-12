from brain.basics import *
# from enum import Enum
# import typing
from creatures.creature import Creature
from world.map import MapNode

sign=lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

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
