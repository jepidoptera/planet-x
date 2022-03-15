from brain.basics import *
# from enum import Enum
# import typing
from creatures.creature import Creature
from world.map import MapNode
import copy

sign=lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

class V1(Brain):
    def process(self, stimuli: list[Stimulus]) -> tuple[str, any]:
        options: list[Action]=[]
        selfCreature=stimuli[0].object
        for stimulus in stimuli:
            object=stimulus.object
            event=stimulus.event
            self.clear()
            if type(object) == Creature and stimulus.distance == 0:
                # self
                for sensor in self.selfNeurons:
                    sensor.sense(object)
                if event == "birth":
                    self.neurons[netIndex['self_birth']].activate(1.0)

            elif type(object) == Creature:
                for sensor in self.creatureNeurons:
                    sensor.sense(selfCreature, object)
                for axon in self.creatureAxons:
                    axon.fire()
                
                if event == 'injury':
                    self.neurons[netIndex['self_injury']].activate(1.0)

            elif type(object) == MapNode:
                # food, probably
                for sensor in self.envNeurons:
                    sensor.sense(object)
                for axon in self.envAxons:
                    axon.fire()

            for axon in self.selfAxons + self.actionAxons + self.memoryAxons + self.relayAxons:
                axon.fire()

            if type(object) == MapNode or object == selfCreature:
                self.neurons[netIndex['action_attack']].clear()
                self.neurons[netIndex['action_mate']].clear()
                self.neurons[netIndex['action_flee']].clear()
            if type(object) == Creature:
                self.neurons[netIndex['action_attack']].activate(
                    self.neurons[netIndex['action_eat']].activation
                )
                self.neurons[netIndex['action_eat']].clear()
                if selfCreature.getSimilarity(object) < 0.5:
                    self.neurons[netIndex['action_mate']].clear()
                

            impulse=max(self.actionNeurons, key=lambda n: n.activation)
            options.append(Action(
                act=impulse.action,
                object=object,
                weight=impulse.activation
            ))
        return max(options, key=lambda option: option.weight)
    
    def merge(self, *others: Brain):
        newBrain=copy.deepcopy(self)
        newBrain.axons=Brain.mergeAxons(self.axons, *[other.axons for other in others])
        newBrain.biases=Brain.mergeNeurons(self.biases, *[other.biases for other in others])
        return newBrain

    def clear(self):
        for neuron in self.creatureNeurons + self.envNeurons + self.actionNeurons:
            neuron.clear()


# initialize=V1()