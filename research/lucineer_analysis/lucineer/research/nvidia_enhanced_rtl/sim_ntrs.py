import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Define ternary reservoir parameters
N = 100  # Number of neurons in the reservoir
n_inputs = 1  # Number of input dimensions
n_outputs = 1  # Number of output dimensions
spectral_radius = 0.9  # Spectral radius of the reservoir
leak_rate = 0.1  # Leak rate of the neurons
threshold = 1.0  # Firing threshold of the neurons
ternary_weights = True  # Use ternary weights
input_scaling = 0.1  # Input scaling factor

# Define the ternary reservoir
class TernaryReservoir:
    def __init__(self, N, n_inputs, spectral_radius, leak_rate, threshold, ternary_weights, input_scaling):
        self.N = N
        self.n_inputs = n_inputs
        self.spectral_radius = spectral_radius
        self.leak_rate = leak_rate
        self.threshold = threshold
        self.ternary_weights = ternary_weights
        self.input_scaling = input_scaling
        
        # Initialize the reservoir weights
        self.weights = np.random.rand(N, N) - 0.5
        if ternary_weights:
            self.weights = np.where(self.weights > 0, 1, -1)
        self.weights *= spectral_radius / np.max(np.abs(np.linalg.eigvals(self.weights)))
        
        # Initialize the input weights
        self.input_weights = np.random.rand(N, n_inputs) * input_scaling
        
        # Initialize the state of the reservoir
        self.state = np.zeros(N)
        
    def update(self, input_signal):
        # Update the state of the reservoir
        self.state = (1 - self.leak_rate) * self.state + np.dot(self.weights, np.maximum(self.state - self.threshold, 0)) + np.dot(self.input_weights, input_signal)
        
        # Return the state of the reservoir
        return self.state

# Define the readout layer
class ReadoutLayer:
    def __init__(self, N, n_outputs):
        self.N = N
        self.n_outputs = n_outputs
        
        # Initialize the readout weights
        self.weights = np.random.rand(n_outputs, N)
        
    def update(self, reservoir_state):
        # Update the output of the readout layer
        output = np.dot(self.weights, reservoir_state)
        
        # Return the output of the readout layer
        return output

# Define the training parameters
training_length = 1000
testing_length = 1000
training_signal = np.sin(np.linspace(0, 10, training_length))[:, np.newaxis]
testing_signal = np.sin(np.linspace(10, 20, testing_length))[:, np.newaxis]

# Create the ternary reservoir and readout layer
reservoir = TernaryReservoir(N, n_inputs, spectral_radius, leak_rate, threshold, ternary_weights, input_scaling)
readout_layer = ReadoutLayer(N, n_outputs)

# Train the readout layer
reservoir_states = np.zeros((training_length, N))
for i in range(training_length):
    reservoir_states[i] = reservoir.update(training_signal[i])
readout_layer.weights = np.linalg.lstsq(reservoir_states, training_signal, rcond=None)[0].T

# Test the reservoir and readout layer
testing_outputs = np.zeros((testing_length, n_outputs))
for i in range(testing_length):
    testing_outputs[i] = readout_layer.update(reservoir.update(testing_signal[i]))

# Evaluate the performance of the reservoir and readout layer
mse = mean_squared_error(testing_signal, testing_outputs)
print("Mean squared error: ", mse)

# Visualize the reservoir dynamics
plt.figure(figsize=(10, 6))
plt.plot(reservoir_states[:, 0:10])
plt.title("Reservoir Dynamics")
plt.xlabel("Time")
plt.ylabel("Neuron Activity")
plt.show()

# Visualize the input and output signals
plt.figure(figsize=(10, 6))
plt.plot(training_signal, label="Training Signal")
plt.plot(testing_signal, label="Testing Signal")
plt.plot(testing_outputs, label="Output Signal")
plt.title("Input and Output Signals")
plt.xlabel("Time")
plt.ylabel("Signal Value")
plt.legend()
plt.show()