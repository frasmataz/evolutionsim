import random
import math
import time
from pprint import pprint

class Neuron:
    saturation = 255
    delete_chance = 0.02
    replace_chance = 0.01
    max_replace = 2.0
    mutate_chance = 0.05
    max_mutate = 0.5
    max_bias_mutate = 0.2

    def __init__(self, inputs, activate_function, random_w):
        self.inputs = inputs
        self.weights = []
        self.value = 0.0
        self.activate_function = activate_function
        self.random_w = random_w

        if self.random_w:
            self.bias = random.uniform(-1.0,1.0)
        else:
            self.bias = 0.0

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

        n = n + self.bias
        
        if self.activate_function == 'sigmoid':
            self.value = 1 / (1 + math.exp(-n))
            self.value = (self.value * 2) - 1.0
        elif self.activate_function == 'relu':
            self.value = max(0,n)
        else:
            self.value = (n / len(self.inputs))

    def mutate(self):
        for i in range(len(self.weights)):
            if random.uniform(0.0,1.0) < self.mutate_chance:
                self.weights[i] = self.weights[i] + random.uniform(-self.max_mutate,self.max_mutate)

            if random.uniform(0.0,1.0) < self.delete_chance:
                self.weights[i] = 0.0

            if random.uniform(0.0,1.0) < self.replace_chance:
                self.weights[i] = random.uniform(-self.max_replace,self.max_replace)

        if random.uniform(0.0,1.0) < self.mutate_chance:
            self.bias = self.bias + random.uniform(-self.max_bias_mutate,self.max_bias_mutate)

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
        self.hiddenlayersize = 6
        self.hiddenlayers = 2
        self.layers = []

        random.seed(seed)

        # Input layer - speed, sin(a), cos(a), rspeed, xdiff, ydiff, 0, 1
        inputlayer = []
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))
        inputlayer.append(Neuron([Input()], 'none', False))

        self.layers.append(inputlayer)

        for i in range(0,self.hiddenlayers):
            # Hidden layer
            hiddenlayer = []
            for j in range(0,self.hiddenlayersize):
                hiddenlayer.append(Neuron(list(self.layers[len(self.layers)-1]), 'relu', True))

            self.layers.append(hiddenlayer)

        # Output layer - speed, rspeed, r, g, b
        outputlayer = []
        outputlayer.append(Neuron(self.layers[len(self.layers)-1], 'sigmoid', True))
        outputlayer.append(Neuron(self.layers[len(self.layers)-1], 'sigmoid', True))
        outputlayer.append(Neuron(self.layers[len(self.layers)-1], 'sigmoid', True))
        outputlayer.append(Neuron(self.layers[len(self.layers)-1], 'sigmoid', True))
        outputlayer.append(Neuron(self.layers[len(self.layers)-1], 'sigmoid', True))

        self.layers.append(outputlayer)

    def tick(self,speed,sina,cosa,rspeed,xdiff,ydiff):
        self.layers[0][0].set_inputs(speed)
        self.layers[0][1].set_inputs(sina)
        self.layers[0][2].set_inputs(cosa)
        self.layers[0][3].set_inputs(rspeed)
        self.layers[0][4].set_inputs(xdiff)
        self.layers[0][5].set_inputs(ydiff)
        self.layers[0][6].set_inputs(0.0)
        self.layers[0][7].set_inputs(1.0)

        for l in self.layers:
            for n in l:
                n.decide()

        return {
            'speed': self.layers[len(self.layers)-1][0].value,
            'rspeed': self.layers[len(self.layers)-1][1].value,
            'rgb': (self.layers[len(self.layers)-1][2].value,
                  self.layers[len(self.layers)-1][3].value,
                  self.layers[len(self.layers)-1][4].value)
        }

    def mutate(self):
        i = 0
        for l in self.layers:
            for n in l:
                if i > 0:
                    n.mutate()
            i = i + 1
