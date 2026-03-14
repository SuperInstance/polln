import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Constants
k_B = 1.38064852e-23  # Boltzmann constant in J/K
T = 300  # Temperature in K
log2_3 = np.log2(3)  # Log2(3) for Landauer's limit

# Ternary operation mapping to thermodynamic processes
def ternary_operation(x, y, op):
    if op == 'AND':
        return x * y
    elif op == 'OR':
        return x + y - x * y
    elif op == 'NOT':
        return 1 - x
    else:
        raise ValueError('Invalid ternary operation')

# Landauer's limit for ternary bits
def landauer_limit(E):
    return log2_3 * k_B * T * E

# Thermal noise and fluctuation-dissipation
def thermal_noise(sigma):
    return np.random.normal(0, sigma)

# Simulate TTCE inference
def simulate_ttce(x, y, op, E, sigma):
    # Ternary operation
    z = ternary_operation(x, y, op)
    
    # Landauer's limit
    E_L = landauer_limit(E)
    
    # Thermal noise
    noise = thermal_noise(sigma)
    
    # Entropy production
    delta_S = E_L / T
    
    # Energy efficiency
    eta = E_L / E
    
    # Thermodynamic reversibility
    r = 1 - delta_S / E
    
    return z, E_L, delta_S, eta, r

# Parameters
x = 0.5  # Input 1
y = 0.7  # Input 2
op = 'AND'  # Ternary operation
E = 1e-12  # Energy in J
sigma = 1e-6  # Thermal noise standard deviation

# Simulate TTCE inference
z, E_L, delta_S, eta, r = simulate_ttce(x, y, op, E, sigma)

print(f'Ternary operation result: {z:.4f}')
print(f'Landauer limit: {E_L:.4e} J')
print(f'Entropy production: {delta_S:.4e} J/K')
print(f'Energy efficiency: {eta:.4f}')
print(f'Thermodynamic reversibility: {r:.4f}')

# Thermodynamic visualizations
plt.figure(figsize=(8, 6))

# Energy-entropy diagram
plt.subplot(2, 2, 1)
plt.plot(E, delta_S, 'bo-')
plt.xlabel('Energy (J)')
plt.ylabel('Entropy (J/K)')
plt.title('Energy-Entropy Diagram')

# Ternary operation diagram
plt.subplot(2, 2, 2)
plt.plot(x, y, 'ro-')
plt.plot(x, z, 'bo-')
plt.xlabel('Input 1')
plt.ylabel('Input 2')
plt.title('Ternary Operation Diagram')

# Thermal noise histogram
plt.subplot(2, 2, 3)
plt.hist(thermal_noise(sigma), bins=50, density=True)
plt.xlabel('Thermal Noise')
plt.ylabel('Probability Density')
plt.title('Thermal Noise Histogram')

# Landauer's limit diagram
plt.subplot(2, 2, 4)
plt.plot(E, E_L, 'go-')
plt.xlabel('Energy (J)')
plt.ylabel('Landauer Limit (J)')
plt.title("Landauer's Limit Diagram")

plt.tight_layout()
plt.show()