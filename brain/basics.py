from enum import Enum
from tokenize import Double
from typing import Callable
import random
import copy
# from creatures.creature import Creature
# from world.map import MapNode

sign=lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

class NeuronType(Enum):
    self=0
    creature=1
    environment=2
    memory=3
    relay=4
    action=5

class Neuron():
    activation:float
    sense:Callable
    action:Callable
    type:NeuronType
    name:str
    bias:float
    def __init__(self, type: NeuronType, index: int, name:str='', sense: Callable=None, action: Callable=None, bias: float=0.0):
        self.activation=0.0
        self._sense=sense
        self.action=action
        self.type=type
        self.name=name
        self.bias=bias
        self.index=index
        if not name in netIndex: netIndex[name]=self.index
        if not self.index in netKey: netKey[self.index]=name
    def sense(self, *args):
        self.activation=(self._sense(*args))
    def activate(self, amount):
        self.activation += amount
    def clear(self):
        self.activation=self.bias
# 🙌🏾

class MemNeuron(Neuron):
    sense=None
    action=None
    type=NeuronType.memory
    threshold=0.5
    strength=1.0

    def __init__(self, memstate:bool, index: int, name:str=''):
        super().__init__(NeuronType.memory, index=index, name=name)
        self.memState=memstate
    def activate(self, amount):
        if abs(amount) > self.threshold: self.memState=1 if amount > 0 else 0
        self.clear()
    def clear(self):
        self.activation=self.memState * self.strength

class SelfNeuron(Neuron):
    def __init__(self, index: int, name: str, sense: Callable):
        super().__init__(NeuronType.self, index=index, name=name, sense=sense)
    def clear(self):
        # don't
        return

class Axon():
    def __init__(self, input: Neuron, output: Neuron, factor: float):
        self.input=input
        self.output=output
        self.factor=factor

    def fire(self):
        self.output.activate(self.input.activation * self.factor)

    def __str__(self) -> str:
        return (
            hex(self.input.index)[2:].zfill(2) + 
            hex(self.output.index)[2:].zfill(2) +
            hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
        )
    def toJson(self):
        return {
            'type': 'single',
            'input': self.input.name,
            'output': self.output.name,
            'factor': self._factor
        }
    @property 
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, value):
        self._factor=max(min(value, 1), -1)
        return self._factor

class DoubleAxon(Axon):
    operators={
        'and': 0,
        'or': 1,
        'nor': 2,
        'xor': 3,
        'and not': 4
    }

    def __init__(self, input: list[Neuron], output: Neuron, threshold: float, operator: int, factor: float):
        
        self._input=input
        self.output: Neuron=output
        self.threshold=threshold
        self.factor=factor
        self.operator=operator

    def fire(self):
        # there is room for up to 256 different operators
        # just probably gonna use 8
        if self.operator == 0:
            # AND
            if (self._input[0].activation >= self.threshold and self._input[1].activation >= self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 1:
            # OR
            if (self._input[0].activation >= self.threshold or self._input[1].activation >= self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 2:
            # NOR 
            if (self._input[0].activation < self.threshold and self._input[1].activation < self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 3:
            # XOR
            if ((self._input[0].activation >= self.threshold) ^ (self._input[1].activation >= self.threshold)):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)
        elif self.operator == 4:
            # and not
            if (self._input[0].activation >= self.threshold and not self._input[1].activation >= self.threshold):
                self.output.activate(max(self._input[0].activation, self._input[1].activation) * self.factor)

    @property
    def input(self):
        return self._input[0]

    @input.setter
    def input(self, value):
        self._input[0]=value
        return self._input[0]

    @property
    def input2(self):
        return self._input[1]

    @input2.setter
    def input2(self, value):
        self._input[1]=value
        return self._input[1]

    def __str__(self) -> str:
        return (
            'FF' + 
            hex(self.operator)[2:].zfill(2) + 
            hex(int(self.threshold * 0xff))[2:].zfill(2) + 
            hex(self._input[0].index)[2:].zfill(2) + 
            hex(self._input[1].index)[2:].zfill(2) + 
            hex(self.output.index)[2:].zfill(2) +
            hex(min(int((self.factor + 1)*0x8000), 0xffff))[2:].zfill(4)
        )

    def toJson(self):
        return {
            'type': 'double',
            'input1': self.input.name,
            'input2': self.input2.name,
            'output': self.output.name,
            'factor': self.factor,
            'threshold': self.threshold,
            'operator': list(DoubleAxon.operators.keys())[list(DoubleAxon.operators.values()).index(self.operator)]
        }

class Stimulus():
    def __init__(self, object: any=None, event: str='', distance: float=1.0):
        self.object=object
        self.distance=distance
        self.event=event

class Action():
    attack='attack'
    flee='flee'
    mate='mate'
    eat='eat'
    wander='wander'
    rest='rest'
    turnLeft='turn left'
    turnRight='turn right'
    sprint='sprint'
    move='move'
    howl='howl'
    def __init__(self, act: str, object: any, weight: float):
        self.act=act
        self.object=object
        self.weight=weight

netIndex: dict[str, int]={}
netKey: dict[int: str]={}

class Brain():
    process: Callable[[list[Stimulus]], Action]
    mutate: Callable

    selfNeurons: list[Neuron]
    creatureNeurons: list[Neuron]
    envNeurons: list[Neuron]
    relayNeurons: list[Neuron]
    actionNeurons: list[Neuron]

    selfAxons: set[Axon]
    creatureAxons: set[Axon]
    envAxons: set[Axon]
    memoryAxons: set[Axon]
    relayAxons: set[Axon]
    actionAxons: set[Axon]
    allAxons: list[Axon]

    def __init__(self, axons: list[Axon]=[], neurons: dict[int: float]={}):

        self.creatureNeurons=list[Neuron]([
            Neuron(NeuronType.creature, index=0x00, name='creature_deadliness', sense=lambda self, other: min(other.deadliness/self.health, 1) if self.health else 0),
            Neuron(NeuronType.creature, index=0x01, name='creature_age', sense=lambda self, other: other.age/other.longevity),
            Neuron(NeuronType.creature, index=0x02, name='creature_health', sense=lambda self, other: other.health/other.fortitude),
            Neuron(NeuronType.creature, index=0x03, name='creature_similarity', sense=lambda self, other: self.getSimilarity(other)),
            Neuron(NeuronType.creature, index=0x04, name='creature_speed', sense=lambda self, other: sign(other.speed-self.speed)),
            Neuron(NeuronType.creature, index=0x05, name='creature_exists', sense=lambda self, other: True)
        ])

        self.memNeurons=list[Neuron]([MemNeuron(False, index=0x50 + n, name=f'memory_{n}') for n in range(8)])

        self.selfNeurons=list[Neuron]([
            SelfNeuron(index=0x10, name='self_energy', sense=lambda self: self.energy/self.size if self.size else 0),
            SelfNeuron(index=0x11, name='self_health', sense=lambda self: self.health/self.fortitude if self.health else 0),
            SelfNeuron(index=0x12, name='self_age', sense=lambda self: self.age/self.longevity if self.longevity else 0),
            SelfNeuron(index=0x13, name='self_sprints', sense=lambda self: 1 if self.sprints else 0),
            SelfNeuron(index=0x14, name='self_birth', sense=lambda self: 0), # just born
            SelfNeuron(index=0x15, name='self_injury', sense=lambda self: 0), # under attack
            SelfNeuron(index=0x16, name='is_self', sense=lambda self: True),
            SelfNeuron(index=0x17, name='self_sometimes', sense=lambda self: int(self.age % 7 == 0)), 
            SelfNeuron(index=0x18, name='self_rarely', sense=lambda self: int(self.age % 77 == 0)) 
        ])

        self.envNeurons=list[Neuron]([
            Neuron(NeuronType.environment, index=0x20, name='see_meat', sense=lambda node: 1 if node.resource.type=='meat' else 0),
            Neuron(NeuronType.environment, index=0x21, name='see_fruit', sense=lambda node: 1 if node.resource.type=='fruit' else 0),
            Neuron(NeuronType.environment, index=0x22, name='see_grass', sense=lambda node: 1 if node.resource.type=='grass' else 0),
            Neuron(NeuronType.environment, index=0x23, name='see_tree', sense=lambda node: 1 if node.resource.type=='tree' else 0)
        ])

        self.relayNeurons=list[Neuron]([Neuron(NeuronType.relay, index=0x30 + n, name=f'relay_{n}') for n in range(8)])

        self.actionNeurons=list[Neuron]([
            Neuron(NeuronType.action, index=0x40, name='action_attack', action=Action.attack),
            Neuron(NeuronType.action, index=0x41, name='action_flee', action=Action.flee),
            Neuron(NeuronType.action, index=0x42, name='action_mate', action=Action.mate),
            Neuron(NeuronType.action, index=0x43, name='action_eat', action=Action.eat),
            Neuron(NeuronType.action, index=0x44, name='action_turnleft', action=Action.turnLeft),
            Neuron(NeuronType.action, index=0x45, name='action_turnright', action=Action.turnRight),
            Neuron(NeuronType.action, index=0x46, name='action_move', action=Action.move),
            Neuron(NeuronType.action, index=0x47, name='action_sprint', action=Action.sprint),
            Neuron(NeuronType.action, index=0x48, name='action_rest', action=Action.rest),
            Neuron(NeuronType.action, index=0x49, name='action_wander', action=Action.wander),
            Neuron(NeuronType.action, index=0x4a, name='action_howl', action=Action.howl),
            Neuron(NeuronType.action, index=0x4b, name='action_continue', action=None)            
        ])


        self.neurons={n.index:n for n in (
            self.creatureNeurons + 
            self.selfNeurons + 
            self.envNeurons + 
            self.memNeurons + 
            self.relayNeurons + 
            self.actionNeurons
        )}

        self.axons=axons
        self.biases=neurons
        for index in neurons:
            self.neurons[index].bias=neurons[index]
        self.sortAxons()

    def sortAxons(self):
        self.actionAxons=[]
        self.relayAxons=[]
        self.memoryAxons=[]
        self.creatureAxons=[]
        self.envAxons=[]
        self.selfAxons=[]

        for axon in self.axons:
            if type(axon.input) == int:
                axon.input=self.neurons[axon.input]
            if type(axon) == DoubleAxon and type(axon.input2) == int:
                axon.input2=self.neurons[axon.input2]
            if type(axon.output) == int:
                axon.output=self.neurons[axon.output]

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

        self.axons=self.creatureAxons + self.envAxons + self.selfAxons + self.memoryAxons + self.relayAxons + self.actionAxons

    def toJson(self):
        axons=[axon.toJson() for axon in self.axons]
        neurons={
            netKeys[index]: neuron.bias
            for _, (index, neuron) in 
            enumerate(filter(lambda x: x[1].bias > 0, self.neurons.items()))
        }
        return {
            'axons': axons,
            'neurons': neurons
        }

    def mergeAxons(*args: list[Axon]):
        # def similarity(s1: str, s2: str):
        #     sim=0
        #     for n in range(min(len(s1), len(s2))):
        #         if s1[n] == s2[n]:
        #             sim += 1
        #     return sim/min(len(s1), len(s2))

        class Mergeable:
            def __init__(self, axons: list[Axon]):
                self.axons=axons
                self._mergePos=0
                self.finished=False
            @property
            def currentAxon(self):
                return self.axons[self._mergePos]
            def next(self):
                self._mergePos += 1
                if self._mergePos == len(self.axons): self.finished=True

        parsedOut=0
        brains=[Mergeable(brain) for brain in args]
        newBrain=[]
        while parsedOut < len(brains):
            remainingBrains=list(filter(lambda brain: not brain.finished, brains))
            if len(remainingBrains) == 0: break
            newAxon=random.choice(
                [brain.currentAxon
                for brain in remainingBrains]
            )
            newBrain.append(newAxon)
            for brain in brains:
                brain.next()
                if brain.finished: 
                    continue
                if (hasattr(brain.currentAxon, 'input')
                    and brain.currentAxon.input == newAxon.input 
                    and brain.currentAxon.output == newAxon.output
                    and type(brain.currentAxon) == type(newAxon)
                ):
                    brain.next()

        return newBrain

    def mergeNeurons(*args: dict[int: float]):
        newBrain={}
        for n in netIndex.values():
            new=random.choice([neuronset[n] if n in neuronset else 0 for neuronset in args])
            if new: newBrain[n]=new
        return newBrain

    def merge(self, other):
        new=copy.deepcopy(self)
        new.axons=self.mergeAxons(self.axons, other.axons)
        new.neurons=self.mergeNeurons(self.neurons, other.neurons)
        return new

    @staticmethod
    def encodeAxons(axons: list[Axon]) -> str:
        axonStr=''
        for axon in axons:
            if type(axon) == Axon:
                axonStr += hex(axon.input.index if isinstance(axon.input, Neuron) else axon.input)[2:].zfill(2)
                axonStr += hex(axon.output.index if isinstance(axon.output, Neuron) else axon.output)[2:].zfill(2)
                axonStr += hex(int((axon.factor * 0xffff + 0xffff) / 2))[2:].zfill(4)

            elif type(axon) == DoubleAxon:
                axonStr += "FF"
                axonStr += hex(axon.input.index if isinstance(axon.input, Neuron) else axon.input)[2:].zfill(2)
                axonStr += hex(axon.input2.index if isinstance(axon.input2, Neuron) else axon.input2)[2:].zfill(2)
                axonStr += hex(axon.output.index if isinstance(axon.output, Neuron) else axon.output)[2:].zfill(2)
                axonStr += hex(axon.operator)[2:].zfill(2)
                axonStr += hex(int(axon.threshold * 0xff))[2:].zfill(2)
                axonStr += hex(int((axon.factor * 0xffff + 0xffff) / 2))[2:].zfill(4)
        
        return axonStr

    @staticmethod
    def encodeNeurons(neurons: dict[int: float]) -> str:
        neuronStr=''
        for k in neurons.keys():
            neuronStr += hex(k)[2:].zfill(2)
            neuronStr += hex(int((neurons[k] * 0xffff + 0xffff) / 2))[2:].zfill(4)

        return neuronStr

    @staticmethod
    def decodeAxons(axonStr: str) -> list[Axon]:
        axons: list[Axon]=[]
        def fromHex(hexcode):
            if len(hexcode) == 8:
                input=int(hexcode[:2], 16) % 0x60
                output=int(hexcode[2:4], 16) % 0x60
                factor=((int(hexcode[4:8], 16) / 0xffff) - 0.5) * 2 # either positive or negative, 8000 being zero
                
                return Axon(
                    input=input,
                    output=output, 
                    factor=factor
                )

            elif len(hexcode) == 16:
                operator=int(hexcode[2:4], 16) % 0xf8
                threshold=int(hexcode[4:6], 16)/0xff
                input1=int(hexcode[6:8], 16) % 0x60
                input2=int(hexcode[8:10], 16) % 0x60
                output=int(hexcode[10:12], 16) % 0x60
                factor=((int(hexcode[12:16], 16) / 0xffff) - 0.5) * 2 # either positive or negative, 8000 being zero

                return DoubleAxon(
                    input=[input1, input2],
                    output=output,
                    threshold=threshold,
                    operator=operator,
                    factor=factor
                )
            else:
                raise Exception(f"invalid hex code length ({len(hexcode)}), can't generate axon")

        doubleAxon=False
        for n in range(int(len(axonStr)/8)):
            if doubleAxon:
                doubleAxon=False
                continue
            
            if int(axonStr[n*8: n*8 + 2], 16) != 0xff:
                axon=fromHex(axonStr[n * 8: (n + 1) * 8])
            else:
                axon=fromHex(axonStr[n*8: (n+2)*8])
                doubleAxon=True
            axons.append(axon)

        return axons

    @staticmethod
    def decodeNeurons(neuronStr: str) -> dict[int: float]:
        neurons={}
        for n in range(int(len(neuronStr)/6)):
            neurons[int(neuronStr[n*6: n*6 + 2], 16)]=((int(neuronStr[n*6 + 2: n*6 + 6], 16) / 0xffff) - 0.5) * 2
        
        return neurons

# set up the netIndex
netKeys={
    **{0x30 + n: f'relay_{n}' for n in range(8)},
    **{0x50 + n: f'memory_{n}' for n in range(8)},
    **{
        0x00:'creature_deadliness',
        0x01:'creature_age',
        0x02:'creature_health',
        0x03:'creature_similarity',
        0x04:'creature_speed',
        0x05:'creature_exists',

        0x10:'self_energy',
        0x11:'self_health',
        0x12:'self_age',
        0x13:'self_sprints',
        0x14:'self_birth',
        0x15:'self_injury',
        0x16:'is_self',
        0x17:'self_sometimes',
        0x18:'self_rarely',

        0x20:'see_meat',
        0x21:'see_fruit',
        0x22:'see_grass',
        0x23:'see_tree',

        0x40:'action_attack',
        0x41:'action_flee',
        0x42:'action_mate',
        0x43:'action_eat',
        0x44:'action_turnleft',
        0x45:'action_turnright',
        0x46:'action_move',
        0x47:'action_sprint',
        0x48:'action_rest',
        0x49:'action_wander',
        0x4a:'action_howl',
        0x4b:'action_continue'
    }
}
netIndex={value: key for _, (key, value) in enumerate(netKeys.items())}
