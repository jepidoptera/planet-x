from enum import Enum
import typing
from creatures.creature import Creature
from world.map import MapNode

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
    sense:typing.Callable
    action:typing.Callable
    type:NeuronType
    name:str
    bias:float
    def __init__(self, index: int, type: NeuronType, name:str='', sense: typing.Callable=None, action: typing.Callable=None, bias: float=0.0):
        self.activation=0.0
        self._sense=sense
        self.action=action
        self.type=type
        self.name=name
        self.bias=bias
        self.index=index
        if not name in netIndex: netIndex[name]=self.index
    def sense(self, *args):
        self.activate(self._sense(*args))
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

class SelfNeuron():
    def __init__(self, index: int, name: str):
        super().__init__(NeuronType.self, index=index, name=name)
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

    @property
    def input2(self):
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


class Stimulus():
    def __init__(self, object: any, distance: float):
        self.object=object
        self.distance=distance

class ActionOption():
    def __init__(self, action: str, target: any, weight: float, relevantNeuron: Neuron):
        self.action=action
        self.target=target
        self.weight=weight
        self.neuron=relevantNeuron

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
    def __init__(self, act: str, object: any):
        self.act=act
        self.object=object

netIndex: dict[str, Neuron]={}

class Brain():
    process: callable[[*Stimulus], Action]
    mutate: callable

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
    def __init__(self, speciesName):
        self.speciesName=speciesName

        self.creatureNeurons=list[Neuron]([
            Neuron(NeuronType.creature, index=0x00, name='creature_deadliness', sense=lambda self, other: min(other.deadliness/self.health, 1) if self.health else 0),
            Neuron(NeuronType.creature, index=0x01, name='creature_age', sense=lambda self, other: other.age/other.longevity),
            Neuron(NeuronType.creature, index=0x02, name='creature_health', sense=lambda self, other: other.health/other.fortitude),
            Neuron(NeuronType.creature, index=0x03, name='creature_similarity', sense=lambda self, other: self.getSimilarity(other)),
            Neuron(NeuronType.creature, index=0x04, name='creature_speed', sense=lambda self, other: sign(other.speed-self.speed)),
            Neuron(NeuronType.creature, index=0x05, name='creature_exists', sense=lambda self, other: True)
        ])

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
            Neuron(NeuronType.environment, index=0x20, name='see_meat', sense=lambda resource: 1 if resource.type=='meat' else 0),
            Neuron(NeuronType.environment, index=0x21, name='see_fruit', sense=lambda resource: 1 if resource.type=='fruit' else 0),
            Neuron(NeuronType.environment, index=0x22, name='see_grass', sense=lambda resource: 1 if resource.type=='grass' else 0),
            Neuron(NeuronType.environment, index=0x23, name='see_tree', sense=lambda resource: 1 if resource.type=='tree' else 0)
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
            # Neuron(NeuronType.action, index=0x4a, name='action_continue', action=Action.continue),
            Neuron(NeuronType.action, index=0x4a, name='action_howl', action=Action.howl)
        ])

        self.memNeurons=list[Neuron]([MemNeuron(False, index=0x50 + n, name=f'memory_{n}') for n in range(8)])

        self.allNeurons={n.index:n for n in (
            self.creatureNeurons + 
            self.selfNeurons + 
            self.envNeurons + 
            self.memNeurons + 
            self.relayNeurons + 
            self.actionNeurons
        )}
