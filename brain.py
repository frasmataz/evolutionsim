import random
import math
from pprint import pprint

class Neuron:
    threshold = 0.5
    mutate_chance = 0.1
    max_mutate = 2.0

    def __init__(self, inputs):
        self.inputs = []
        self.weights = []
        self.value = 0.0

        for i in range(0, len(self.inputs)):
            self.weights.append(random.uniform(-2.0,2.0))

    def decide(self):
        n = 0.0
        for i in range(0,len(self.inputs)):
            n = n + (self.inputs[i].value * self.weights[i])

        self.value = 1 / (1 + math.exp(-n))

    def mutate(self):
        for weight in self.weights:
            if random.uniform(0.0,1.0) < mutate_chance:
                weight = weight + random.uniform(-max_mutate,max_mutate)

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
        self.layers = {}

        random.seed(seed)

        # Input layer - x, y, speed, angle, rspeed, xdiff, ydiff
        inputlayer = {}
        inputlayer['speed'] = Neuron([Input()])
        inputlayer['angle'] = Neuron([Input()])
        inputlayer['rspeed'] = Neuron([Input()])
        inputlayer['xdiff'] = Neuron([Input()])
        inputlayer['ydiff'] = Neuron([Input()])

        self.layers['input'] = inputlayer

        # Hidden layer
        hiddenlayer = []
        for i in range(0,self.hiddenlayersize):
            hiddenlayer.append(Neuron(self.layers['input']))

        self.layers['hidden'] = hiddenlayer

        # Output layer - speed, rspeed
        outputlayer = {}
        outputlayer['speed'] = Neuron(self.layers['hidden'])
        outputlayer['rspeed'] = Neuron(self.layers['hidden'])

        self.layers['output'] = outputlayer

    def tick(self,speed,angle,rspeed,xdiff,ydiff):
        self.layers['input']['speed'].set_inputs(speed)
        self.layers['input']['angle'].set_inputs(angle)
        self.layers['input']['rspeed'].set_inputs(rspeed)
        self.layers['input']['xdiff'].set_inputs(xdiff)
        self.layers['input']['ydiff'].set_inputs(ydiff)

        for k,v in self.layers['input'].items():
            v.decide()

        for n in self.layers['hidden']:
            n.decide()

        for k,v in self.layers['output'].items():
            v.decide()

        return {
            'speed': self.layers['output']['speed'].value,
            'rspeed': self.layers['output']['rspeed'].value
        }

    def mutate(self):
        for l in self.layers:
            for n in l:
                n.mutate()
