#!/usr/bin/env python3
"""
Run all NVIDIA-generated simulations and save results
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# ============================================================
# 1. MEMRISTOR SWARM SIMULATION
# ============================================================
print("Running Memristor Swarm Simulation...")

class MemristorAgent:
    def __init__(self, state):
        self.state = state  # -1, 0, or +1
        self.neighbors = []
        self.memristance = np.random.uniform(0.8, 1.2)  # Memristive variability
        self.activity = 0
    
    def interact(self, other_agent):
        """Ternary interaction rules with memristive dynamics"""
        noise = np.random.normal(0, 0.1) * self.memristance
        
        if self.state == other_agent.state:
            return  # Same state, no change
        elif self.state == -1 and other_agent.state == 1:
            if np.random.random() < 0.7 + noise:
                self.state = 0
                self.activity += 1
        elif self.state == 1 and other_agent.state == -1:
            if np.random.random() < 0.7 + noise:
                self.state = 0
                self.activity += 1
        elif self.state == 0:
            if other_agent.state != 0:
                if np.random.random() < 0.5 + noise:
                    self.state = other_agent.state
                    self.activity += 1
    
    def update(self):
        for neighbor in self.neighbors:
            self.interact(neighbor)

class MemristorSwarm:
    def __init__(self, num_agents, topology='ring'):
        self.agents = [MemristorAgent(np.random.choice([-1, 0, 1])) 
                       for _ in range(num_agents)]
        
        if topology == 'ring':
            for i in range(num_agents):
                self.agents[i].neighbors = [
                    self.agents[(i-1) % num_agents],
                    self.agents[(i+1) % num_agents]
                ]
        elif topology == 'grid':
            # 2D grid topology
            size = int(np.sqrt(num_agents))
            for i in range(num_agents):
                row, col = i // size, i % size
                neighbors = []
                if row > 0:
                    neighbors.append(self.agents[(row-1)*size + col])
                if row < size-1:
                    neighbors.append(self.agents[(row+1)*size + col])
                if col > 0:
                    neighbors.append(self.agents[row*size + (col-1)])
                if col < size-1:
                    neighbors.append(self.agents[row*size + (col+1)])
                self.agents[i].neighbors = neighbors
    
    def update(self):
        np.random.shuffle(self.agents)  # Random update order
        for agent in self.agents:
            agent.update()
    
    def get_states(self):
        return [agent.state for agent in self.agents]
    
    def get_activities(self):
        return [agent.activity for agent in self.agents]

# Run simulation
num_agents = 100
num_iterations = 200

swarm = MemristorSwarm(num_agents, topology='ring')
states_over_time = np.zeros((num_iterations, num_agents))
activities = []

for i in range(num_iterations):
    swarm.update()
    states_over_time[i] = swarm.get_states()
    activities.append(np.mean(swarm.get_activities()))

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# State evolution
ax1 = axes[0, 0]
im = ax1.imshow(states_over_time, cmap='bwr', interpolation='nearest', aspect='auto')
ax1.set_title('Memristor Swarm State Evolution')
ax1.set_xlabel('Agent Index')
ax1.set_ylabel('Iteration')
plt.colorbar(im, ax=ax1, label='State')

# State distribution over time
ax2 = axes[0, 1]
neg_counts = np.sum(states_over_time == -1, axis=1)
zero_counts = np.sum(states_over_time == 0, axis=1)
pos_counts = np.sum(states_over_time == 1, axis=1)
ax2.stackplot(range(num_iterations), neg_counts, zero_counts, pos_counts,
              labels=['-1', '0', '+1'], colors=['blue', 'gray', 'red'])
ax2.set_title('State Distribution Evolution')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Count')
ax2.legend()

# Activity histogram
ax3 = axes[1, 0]
ax3.hist(activities, bins=30, color='green', alpha=0.7)
ax3.set_title('Agent Activity Distribution')
ax3.set_xlabel('Activity Count')
ax3.set_ylabel('Frequency')

# Convergence metric
ax4 = axes[1, 1]
state_variance = np.var(states_over_time, axis=1)
ax4.plot(state_variance, color='purple')
ax4.set_title('State Variance (Convergence Metric)')
ax4.set_xlabel('Iteration')
ax4.set_ylabel('Variance')

plt.tight_layout()
plt.savefig('/home/z/my-project/research/nvidia_enhanced_rtl/results_memristor_swarm.png', dpi=150)
print("  Saved results_memristor_swarm.png")

# ============================================================
# 2. QUANTUM-INSPIRED ANNEALER
# ============================================================
print("Running Quantum-Inspired Annealer...")

class QuantumTernaryAnnealer:
    def __init__(self, num_vars, J_matrix, h_vector):
        self.n = num_vars
        self.J = J_matrix  # Coupling matrix
        self.h = h_vector   # External fields
        self.states = np.random.choice([-1, 0, 1], size=num_vars)
        self.temperature = 2.0
        self.tunneling_rate = 0.1
        self.history = []
    
    def energy(self, states=None):
        """Calculate Ising energy for ternary states"""
        if states is None:
            states = self.states
        
        # Map ternary to continuous for energy calculation
        continuous = states.astype(float)
        
        # Ising energy: -sum(J_ij * s_i * s_j) - sum(h_i * s_i)
        energy = -np.sum(self.J * np.outer(continuous, continuous))
        energy -= np.sum(self.h * continuous)
        return energy
    
    def quantum_tunnel(self):
        """Simulated quantum tunneling - large state jumps"""
        if np.random.random() < self.tunneling_rate:
            # Select random variable and flip to opposite extreme
            idx = np.random.randint(self.n)
            if self.states[idx] == -1:
                self.states[idx] = 1
            elif self.states[idx] == 1:
                self.states[idx] = -1
            else:
                self.states[idx] = np.random.choice([-1, 1])
    
    def anneal_step(self):
        """Single annealing step with Metropolis acceptance"""
        idx = np.random.randint(self.n)
        old_state = self.states[idx]
        old_energy = self.energy()
        
        # Propose new state
        new_state = np.random.choice([-1, 0, 1])
        self.states[idx] = new_state
        new_energy = self.energy()
        
        # Metropolis criterion
        delta_E = new_energy - old_energy
        if delta_E > 0:
            if np.random.random() > np.exp(-delta_E / self.temperature):
                self.states[idx] = old_state  # Reject
        
        # Quantum tunneling
        self.quantum_tunnel()
        
        # Cool down
        self.temperature *= 0.9995
        self.tunneling_rate *= 0.999
    
    def run(self, num_steps):
        for _ in range(num_steps):
            self.anneal_step()
            self.history.append(self.energy())
        return self.history

# Create random problem instance
n = 50
np.random.seed(42)
J = np.random.randn(n, n) * 0.1
J = (J + J.T) / 2  # Symmetric
np.fill_diagonal(J, 0)
h = np.random.randn(n) * 0.1

annealer = QuantumTernaryAnnealer(n, J, h)
energy_history = annealer.run(5000)

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
ax1.plot(energy_history, color='blue', alpha=0.7)
ax1.set_title('Energy Landscape During Annealing')
ax1.set_xlabel('Step')
ax1.set_ylabel('Energy')
ax1.axhline(y=min(energy_history), color='r', linestyle='--', label='Minimum')
ax1.legend()

ax2 = axes[1]
final_states = annealer.states
ax2.bar(range(n), final_states, color=['blue' if s < 0 else 'gray' if s == 0 else 'red' for s in final_states])
ax2.set_title('Final Ternary State Configuration')
ax2.set_xlabel('Variable Index')
ax2.set_ylabel('State')

plt.tight_layout()
plt.savefig('/home/z/my-project/research/nvidia_enhanced_rtl/results_quantum_annealer.png', dpi=150)
print("  Saved results_quantum_annealer.png")

# ============================================================
# 3. THERMODYNAMIC COMPUTING SIMULATION
# ============================================================
print("Running Thermodynamic Computing Simulation...")

kT = 4.11e-21  # Boltzmann constant * 300K (room temperature)
log2_3 = np.log2(3)  # ~1.585 bits per ternary symbol

class ThermodynamicPE:
    def __init__(self):
        self.state = 0
        self.temperature = 300  # Kelvin
        self.entropy = 0
        self.heat_dissipated = 0
    
    def compute(self, input_state, weight):
        """Ternary computation with thermodynamic tracking"""
        # Landauer's limit for ternary: kT * ln(3) per bit erase
        landauer_limit = kT * np.log(3)
        
        # Computation
        if weight == 0:
            output = 0  # Zero weight bypass
            heat = 0
        else:
            output = input_state * weight
            # Energy cost proportional to state change
            if output != self.state:
                heat = landauer_limit * np.random.uniform(1, 10)  # Practical limit
                self.heat_dissipated += heat
            else:
                heat = 0
        
        self.state = output
        self.entropy += np.log(3) if output != 0 else np.log(2)
        
        return output, heat

class ThermodynamicArray:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.PEs = [[ThermodynamicPE() for _ in range(cols)] for _ in range(rows)]
    
    def forward(self, inputs, weights):
        """Systolic forward pass with thermodynamic tracking"""
        total_heat = 0
        total_entropy = 0
        
        for i in range(self.rows):
            for j in range(self.cols):
                output, heat = self.PEs[i][j].compute(
                    inputs[i] if j == 0 else self.PEs[i][j-1].state,
                    weights[i][j]
                )
                total_heat += heat
                total_entropy += self.PEs[i][j].entropy
        
        return total_heat, total_entropy

# Simulate thermodynamic efficiency
array = ThermodynamicArray(32, 32)
weights = np.random.choice([-1, 0, 1], size=(32, 32))

heat_history = []
entropy_history = []
landauer_theoretical = []

for step in range(100):
    inputs = np.random.choice([-1, 0, 1], size=32)
    heat, entropy = array.forward(inputs, weights)
    heat_history.append(heat)
    entropy_history.append(entropy)
    landauer_theoretical.append(kT * np.log(3) * 32 * 32)

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
ax1.plot(np.array(heat_history) * 1e21, label='Actual Heat', color='red')
ax1.plot(np.array(landauer_theoretical) * 1e21, label='Landauer Limit', color='blue', linestyle='--')
ax1.set_title('Thermodynamic Efficiency')
ax1.set_xlabel('Inference Step')
ax1.set_ylabel('Heat (×10⁻²¹ J)')
ax1.legend()
ax1.set_yscale('log')

ax2 = axes[1]
ax2.plot(entropy_history, color='green')
ax2.set_title('Entropy Production')
ax2.set_xlabel('Inference Step')
ax2.set_ylabel('Entropy (nats)')

plt.tight_layout()
plt.savefig('/home/z/my-project/research/nvidia_enhanced_rtl/results_thermodynamic.png', dpi=150)
print("  Saved results_thermodynamic.png")

# ============================================================
# 4. DEFECT TOLERANCE SIMULATION
# ============================================================
print("Running Defect Tolerance Simulation...")

class DefectAwarePE:
    def __init__(self, id):
        self.id = id
        self.defective = False
        self.defect_type = None  # 'stuck_at_neg', 'stuck_at_zero', 'stuck_at_pos', 'random'
        self.state = 0
    
    def inject_defect(self, defect_rate=0.01):
        if np.random.random() < defect_rate:
            self.defective = True
            self.defect_type = np.random.choice(['stuck_at_neg', 'stuck_at_zero', 'stuck_at_pos', 'random'])
    
    def compute(self, activation, weight):
        if self.defective:
            if self.defect_type == 'stuck_at_neg':
                return -1
            elif self.defect_type == 'stuck_at_zero':
                return 0
            elif self.defect_type == 'stuck_at_pos':
                return 1
            elif self.defect_type == 'random':
                return np.random.choice([-1, 0, 1])
        
        # Normal computation
        return activation * weight

class SelfHealingArray:
    def __init__(self, size):
        self.size = size
        self.PEs = [[DefectAwarePE(i*size + j) for j in range(size)] for i in range(size)]
        self.defect_map = np.zeros((size, size))
        self.redundancy_map = {}
    
    def inject_defects(self, defect_rate):
        for i in range(self.size):
            for j in range(self.size):
                self.PEs[i][j].inject_defect(defect_rate)
                if self.PEs[i][j].defective:
                    self.defect_map[i, j] = 1
    
    def diagnose(self):
        """Built-in self-test to identify defects"""
        detected = np.zeros((self.size, self.size))
        for i in range(self.size):
            for j in range(self.size):
                # Test patterns
                results = []
                for test in [-1, 0, 1]:
                    result = self.PEs[i][j].compute(test, 1)
                    results.append(result)
                
                # Check if output matches expected
                if results != [-1, 0, 1]:
                    detected[i, j] = 1
        return detected
    
    def reconfigure(self, detected_defects):
        """Reconfigure to bypass defective PEs"""
        for i in range(self.size):
            for j in range(self.size):
                if detected_defects[i, j]:
                    # Route around defective PE
                    self.redundancy_map[(i, j)] = 'bypass'
    
    def compute_with_redundancy(self, inputs, weights):
        """Compute using majority voting for defective PEs"""
        outputs = np.zeros(self.size)
        
        for j in range(self.size):
            votes = []
            for i in range(self.size):
                if (i, j) not in self.redundancy_map:
                    result = self.PEs[i][j].compute(inputs[i], weights[i][j])
                    votes.append(result)
                else:
                    # Bypass - use neighbor's result
                    if i > 0:
                        votes.append(outputs[j])
            
            # Majority voting
            if votes:
                outputs[j] = max(set(votes), key=votes.count)
        
        return outputs

# Simulate defect tolerance
array_size = 32
defect_rates = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
accuracies = []
detected_rates = []

for rate in defect_rates:
    test_array = SelfHealingArray(array_size)
    test_array.inject_defects(rate)
    
    # Diagnose
    detected = test_array.diagnose()
    detection_rate = np.sum(detected) / np.sum(test_array.defect_map) if np.sum(test_array.defect_map) > 0 else 1.0
    detected_rates.append(detection_rate)
    
    # Test accuracy
    test_array.reconfigure(detected)
    correct = 0
    total = 100
    
    for _ in range(total):
        inputs = np.random.choice([-1, 0, 1], size=array_size)
        weights = np.random.choice([-1, 0, 1], size=(array_size, array_size))
        
        expected = np.sum(inputs.reshape(-1, 1) * weights, axis=0)
        actual = test_array.compute_with_redundancy(inputs, weights)
        
        if np.allclose(expected, actual, atol=0.1):
            correct += 1
    
    accuracies.append(correct / total)

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
ax1.plot(defect_rates, accuracies, 'o-', color='green', markersize=8)
ax1.axhline(y=0.9, color='red', linestyle='--', label='90% Target')
ax1.set_title('Accuracy vs Defect Rate (with Self-Healing)')
ax1.set_xlabel('Defect Rate')
ax1.set_ylabel('Accuracy')
ax1.set_xscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(defect_rates, detected_rates, 'o-', color='blue', markersize=8)
ax2.set_title('Defect Detection Rate')
ax2.set_xlabel('Defect Rate')
ax2.set_ylabel('Detection Rate')
ax2.set_xscale('log')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/z/my-project/research/nvidia_enhanced_rtl/results_defect_tolerance.png', dpi=150)
print("  Saved results_defect_tolerance.png")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 50)
print("All simulations complete!")
print("=" * 50)

# Save summary
summary = {
    "memristor_swarm": {
        "num_agents": num_agents,
        "num_iterations": num_iterations,
        "final_variance": float(state_variance[-1])
    },
    "quantum_annealer": {
        "num_variables": n,
        "initial_energy": float(energy_history[0]),
        "final_energy": float(energy_history[-1]),
        "min_energy": float(min(energy_history))
    },
    "thermodynamic": {
        "array_size": "32x32",
        "total_heat_dissipated_j": float(sum(heat_history)),
        "landauer_efficiency": float(sum(landauer_theoretical) / sum(heat_history)) if sum(heat_history) > 0 else 0
    },
    "defect_tolerance": {
        "array_size": array_size,
        "defect_rates_tested": defect_rates,
        "accuracies": accuracies
    }
}

with open('/home/z/my-project/research/nvidia_enhanced_rtl/simulation_results.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("Saved simulation_results.json")
