import random
import math
from pprint import pprint

class Neuron:
    saturation = 255
    mutate_chance = 0.1
    max_mutate = 2.0

    def __init__(self, inputs, sigmoid, random_w):
        self.inputs = inputs
        self.weights = []
        self.value = 0.0
        self.sigmoid = sigmoid
        self.random_w = random_w

        for i in range(0, len(self.inputs)):
            if self.random_w:
                self.weights.append(random.uniform(-2.0,2.0))
            else:
                self.weights.append(1.0)


    def decide(self):
        n = 0.0
        for i in range(0,len(self.inputs)):
            n = n + (self.inputs[i].value * self.weights[i])
            # print('Input {}, weight {}, value {}'.format(self.inputs[i].value,self.weights[i],1 / (1 + math.exp(-n))))

        n = min(n,self.saturation)
        n = max(n,-self.saturation)
        if self.sigmoid:
            self.value = 1 / (1 + math.exp(-n))
            self.value = (self.value * 2) - 1.0
        else:
            self.value = (n / len(self.inputs))

    def mutate(self):
        for i in range(len(self.weights)):
            if random.uniform(0.0,1.0) < self.mutate_chance:
                self.weights[i] = self.weights[i] + random.uniform(-self.max_mutate,self.max_mutate)

    def set_inputs(self, value): # For input layer only
        for input in self.inputs:
            input.value = float(value)

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
        inputlayer.append(Neuron([Input()], False, False))
        inputlayer.append(Neuron([Input()], False, False))
        inputlayer.append(Neuron([Input()], False, False))
        inputlayer.append(Neuron([Input()], False, False))
        inputlayer.append(Neuron([Input()], False, False))

        self.layers.append(inputlayer)

        # Hidden layer
        hiddenlayer = []
        for i in range(0,self.hiddenlayersize):
            hiddenlayer.append(Neuron(list(self.layers[0]), True, True))

        self.layers.append(hiddenlayer)

        # Output layer - speed, rspeed
        outputlayer = []
        outputlayer.append(Neuron(self.layers[1], True, True))
        outputlayer.append(Neuron(self.layers[1], True, True))

        self.layers.append(outputlayer)

    def tick(self,speed,angle,rspeed,xdiff,ydiff):
        self.layers[0][0].set_inputs(speed)
        self.layers[0][1].set_inputs(angle)
        self.layers[0][2].set_inputs(rspeed)
        self.layers[0][3].set_inputs(xdiff)
        self.layers[0][4].set_inputs(ydiff)

        for n in self.layers[0]:
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
            for n in l:
                n.mutate()
