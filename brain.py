import random
import math
from pprint import pprint

def getiter(obj):
    pprint(obj)
    return obj.values() if isinstance(obj, dict) else obj

class Neuron:
    threshold = 0.5
    mutate_chance = 0.1
    max_mutate = 2.0

    def __init__(self, inputs):
        self.inputs = inputs
        self.weights = []
        self.value = 0.0

        for i in range(0, len(self.inputs)):
            self.weights.append(random.uniform(-0.1,0.1))

    def decide(self):
        n = 0.0
        for i in range(0,len(self.inputs)):
            n = n + (self.inputs[i].value * self.weights[i])
            # print('Input {}, weight {}, value {}'.format(self.inputs[i].value,self.weights[i],1 / (1 + math.exp(-n))))

        self.value = 1 / (1 + math.exp(-n))

    def mutate(self):
        for i in range(len(self.weights)):
            if random.uniform(0.0,1.0) < self.mutate_chance:
                print('MUTATE')
                self.weights[i] = self.weights[i] + random.uniform(-self.max_mutate,self.max_mutate)

    def set_inputs(self, value): # For input layer only
        for input in self.inputs:
            input = value

class Input:
    def __init__(self):
        self.value = 0.0

    def update(self, value):
        self.value = value

class Brain:
    def __init__(self,seed):
        self.hiddenlayersize = 5
        self.layers = []

        random.seed(seed)

        # Input layer - x, y, speed, angle, rspeed, xdiff, ydiff
        inputlayer = []
        inputlayer.append(Neuron([Input()]))
        inputlayer.append(Neuron([Input()]))
        inputlayer.append(Neuron([Input()]))
        inputlayer.append(Neuron([Input()]))
        inputlayer.append(Neuron([Input()]))

        self.layers.append(inputlayer)

        # Hidden layer
        hiddenlayer = []
        for i in range(0,self.hiddenlayersize):
            hiddenlayer.append(Neuron(list(self.layers[0])))

        self.layers.append(hiddenlayer)

        # Output layer - speed, rspeed
        outputlayer = []
        outputlayer.append(Neuron(self.layers[1]))
        outputlayer.append(Neuron(self.layers[1]))

        self.layers.append(outputlayer)

    def tick(self,speed,angle,rspeed,xdiff,ydiff):
        self.layers[0][0].set_inputs(speed)
        self.layers[0][1].set_inputs(angle)
        self.layers[0][2].set_inputs(rspeed)
        self.layers[0][3].set_inputs(xdiff)
        self.layers[0][4].set_inputs(ydiff)

        for n in self.layers[0]:
            pprint(self.layers[0])
            n.decide()

        for n in self.layers[1]:
            n.decide()

        for n in self.layers[2]:
            n.decide()

        return {
            'speed': self.layers[2][0].value,
            'rspeed': self.layers[2][1].value
        }

    def mutate(self):
        for l in self.layers:
            for n in getiter(l):
                n.mutate()
