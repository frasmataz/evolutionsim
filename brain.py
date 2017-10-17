import numpy as np
import math
import random

hidden_layers = 1
layer_size = 8
initial_weight_sigma = 1.0

class Neuron:
    delete_chance = 0.005
    replace_chance = 0.005
    replace_sigma = 1.0
    mutate_chance = 0.1
    mutate_sigma = 1.0
    bias_sigma = 1.0

    def __init__(self, input_size, activate_function):
        self.weights = np.random.normal(
            0.0,
            initial_weight_sigma,
            input_size
        )
        self.activate_function = activate_function
        self.bias = 0.0

    def tick(self, inputs):
        x = (inputs * self.weights).sum() + self.bias

        if self.activate_function == 'sigmoid':
            x = 1 / (1 + math.exp(-x))
        elif self.activate_function == 'tanh':
            x = np.tanh(x)
        elif self.activate_function == 'relu':
            x = max(0.0, x)

        self.value = x

        return x

    def mutate(self):
        for i in range(len(self.weights)):
            if random.uniform(0.0,1.0) < self.mutate_chance:
                self.weights[i] = self.weights[i] + np.random.normal(0.0, self.mutate_sigma)

            if random.uniform(0.0,1.0) < self.delete_chance:
                self.weights[i] = 0.0

            if random.uniform(0.0,1.0) < self.replace_chance:
                self.weights[i] = np.random.normal(0.0, self.replace_sigma)

        if random.uniform(0.0,1.0) < self.mutate_chance:
            self.bias = self.bias + random.uniform(0.0, self.bias_sigma)

class Inputneuron:
    def __init__(self):
        self.weights = [1.0]

    def tick(self, inputs):
        self.value = inputs.sum()
        return self.value

    def mutate(self):
        pass

class Layer:
    def __init__(self, size, input_size, activate_functions):
        self.size = size
        self.neurons = []

        for i in range(self.size):
            self.neurons.append(Neuron(input_size, activate_functions[i]))

    def tick(self, inputs):
        output = []
        for n in self.neurons:
            output.append(n.tick(inputs))

        return output

class InputLayer:
    def __init__(self, size):
        self.neurons = []
        self.size = size
        for i in range(size):
            self.neurons.append(Inputneuron())

    def tick(self, inputs):
        output = []
        for i in range(self.size):
            output.append(self.neurons[i].tick(inputs[i]))

        return output

class Brain:
    def __init__(self, seed):
        self.layers = []
        prevlayersize = 7 # Input layer size

        self.layers.append(InputLayer(prevlayersize))

        for i in range(hidden_layers):
            self.layers.append(Layer(layer_size, prevlayersize, np.full(layer_size, 'relu')))
            prevlayersize = layer_size

        self.layers.append(Layer(5, prevlayersize, np.full(layer_size, 'sigmoid')))

    def tick(self,speed,rspeed,angle,xdiff,ydiff):
        inputs = np.array([
            speed,
            rspeed,
            angle,
            xdiff,
            ydiff,
            0.0,
            1.0
        ], dtype=float)

        for layer in self.layers:
            inputs = layer.tick(inputs)

        return {
            'speed': inputs[0],
            'rspeed': inputs[1],
            'rgb': (inputs[2], inputs[3], inputs[4])
        }

    def mutate(self):
        for l in self.layers:
            for n in l.neurons:
                n.mutate()
