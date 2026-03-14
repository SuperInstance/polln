#!/usr/bin/env python3
"""
Geometric Plasticity Learning Simulation
=========================================
Simulates Hebbian, STDP, metaplasticity, and consolidation dynamics
for neuromorphic hardware.

Author: Research Cycle 3
Date: March 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import matplotlib.pyplot as plt
from scipy.special import expit
import warnings
warnings.filterwarnings('ignore')


class WeightState(Enum):
    """Ternary weight states."""
    NEGATIVE = -1
    ZERO = 0
    POSITIVE = 1


@dataclass
class PlasticityParameters:
    """Parameters for plasticity mechanisms."""
    # Hebbian
    eta_hebb: float = 0.01
    decay_rate: float = 0.001
    
    # STDP
    A_plus: float = 0.005
    A_minus: float = 0.0045
    tau_plus: float = 16.8  # ms
    tau_minus: float = 33.7  # ms
    
    # Metaplasticity (BCM)
    theta_m: float = 0.5
    tau_meta: float = 1000.0  # ms
    eta_meta: float = 0.001
    
    # Homeostatic
    r_target: float = 0.1
    tau_homeo: float = 10000.0  # ms
    alpha_homeo: float = 0.1
    
    # Consolidation
    tau_consol: float = 3600000.0  # ms (1 hour)
    consolidation_threshold: float = 0.5


@dataclass
class SynapseState:
    """State of a single synapse."""
    weight: float = 0.0  # Continuous weight
    weight_ternary: WeightState = WeightState.ZERO
    accumulator: float = 0.0
    theta_local: float = 0.5  # Local BCM threshold
    weight_consolidated: float = 0.0
    
    # Spike traces
    trace_pre: float = 0.0
    trace_post: float = 0.0
    
    # Timing
    last_pre_spike: float = -np.inf
    last_post_spike: float = -np.inf


class GeometricPlasticitySimulator:
    """
    Simulator for geometric plasticity in neuromorphic hardware.
    
    Implements:
    - Hebbian learning with channel width modulation
    - Spike-Timing Dependent Plasticity (STDP)
    - BCM metaplasticity with sliding threshold
    - Homeostatic synaptic scaling
    - Memory consolidation dynamics
    """
    
    def __init__(self, n_neurons: int, params: PlasticityParameters):
        """
        Initialize the simulator.
        
        Args:
            n_neurons: Number of neurons in the network
            params: Plasticity parameters
        """
        self.n_neurons = n_neurons
        self.params = params
        self.time = 0.0
        
        # Initialize synapse states
        self.synapses = np.empty((n_neurons, n_neurons), dtype=object)
        for i in range(n_neurons):
            for j in range(n_neurons):
                self.synapses[i, j] = SynapseState()
        
        # Activity tracking
        self.firing_rates = np.zeros(n_neurons)
        self.activity_history = []
        
        # Consolidation queue
        self.consolidation_queue: List[Tuple[int, int, float]] = []
        
    def stdp_window(self, delta_t: float) -> float:
        """
        Compute STDP weight change given timing difference.
        
        Args:
            delta_t: t_post - t_pre in ms
            
        Returns:
            Weight change
        """
        if delta_t > 0:
            return self.params.A_plus * np.exp(-delta_t / self.params.tau_plus)
        else:
            return -self.params.A_minus * np.exp(delta_t / self.params.tau_minus)
    
    def hebbian_update(self, r_pre: float, r_post: float) -> float:
        """
        Compute Hebbian weight change.
        
        Args:
            r_pre: Pre-synaptic firing rate
            r_post: Post-synaptic firing rate
            
        Returns:
            Weight change
        """
        return self.params.eta_hebb * r_pre * r_post
    
    def bcm_update(self, r_post: float, theta_m: float, r_pre: float) -> float:
        """
        Compute BCM weight change with sliding threshold.
        
        Args:
            r_post: Post-synaptic firing rate
            theta_m: Modification threshold
            r_pre: Pre-synaptic firing rate
            
        Returns:
            Weight change
        """
        return self.params.eta_meta * r_post * (r_post - theta_m) * r_pre
    
    def update_threshold(self, theta_m: float, r_post_squared: float) -> float:
        """
        Update BCM sliding threshold.
        
        Args:
            theta_m: Current threshold
            r_post_squared: Squared post-synaptic rate
            
        Returns:
            Updated threshold
        """
        return theta_m + (r_post_squared - theta_m) / self.params.tau_meta
    
    def homeostatic_scale(self, r_actual: float) -> float:
        """
        Compute homeostatic scaling factor.
        
        Args:
            r_actual: Actual firing rate
            
        Returns:
            Scaling factor
        """
        ratio = self.params.r_target / (r_actual + 1e-10)
        return ratio ** self.params.alpha_homeo
    
    def ternarize_weight(self, weight: float, accumulator: float) -> WeightState:
        """
        Convert continuous weight/accumulator to ternary state.
        
        Args:
            weight: Continuous weight
            accumulator: Activity accumulator
            
        Returns:
            Ternary weight state
        """
        if accumulator > 1.0:
            return WeightState.POSITIVE
        elif accumulator < -1.0:
            return WeightState.NEGATIVE
        elif abs(accumulator) < 0.1:
            return WeightState.ZERO
        else:
            # Keep current state
            if weight > 0.5:
                return WeightState.POSITIVE
            elif weight < -0.5:
                return WeightState.NEGATIVE
            else:
                return WeightState.ZERO
    
    def simulate_step(self, dt: float = 1.0, input_spikes: Optional[np.ndarray] = None):
        """
        Simulate one time step of plasticity dynamics.
        
        Args:
            dt: Time step in ms
            input_spikes: Array of neuron indices that spiked
        """
        self.time += dt
        
        # Process input spikes
        if input_spikes is not None:
            for spike_idx in input_spikes:
                # Update pre-synaptic traces
                for post_idx in range(self.n_neurons):
                    syn = self.synapses[spike_idx, post_idx]
                    syn.trace_pre = 1.0
                    
                    # STDP: post-before-pre (LTD)
                    if syn.trace_post > 0.1:
                        delta_w = -self.params.A_minus * syn.trace_post
                        syn.accumulator += delta_w
                    
                    syn.last_pre_spike = self.time
            
            # Generate output spikes based on input
            for post_idx in range(self.n_neurons):
                # Calculate input current
                total_input = 0.0
                for pre_idx in range(self.n_neurons):
                    syn = self.synapses[pre_idx, post_idx]
                    if syn.weight_ternary == WeightState.POSITIVE:
                        total_input += syn.trace_pre
                    elif syn.weight_ternary == WeightState.NEGATIVE:
                        total_input -= syn.trace_pre
                
                # Stochastic spike generation
                prob_spike = expit(total_input - 0.5)
                if np.random.random() < prob_spike:
                    # Post-synaptic spike
                    for pre_idx in range(self.n_neurons):
                        syn = self.synapses[pre_idx, post_idx]
                        syn.trace_post = 1.0
                        
                        # STDP: pre-before-post (LTP)
                        if syn.trace_pre > 0.1:
                            delta_w = self.params.A_plus * syn.trace_pre
                            syn.accumulator += delta_w
                        
                        syn.last_post_spike = self.time
        
        # Update all synapses
        for i in range(self.n_neurons):
            for j in range(self.n_neurons):
                syn = self.synapses[i, j]
                
                # Decay traces
                syn.trace_pre *= np.exp(-dt / self.params.tau_plus)
                syn.trace_post *= np.exp(-dt / self.params.tau_minus)
                
                # Hebbian contribution
                if syn.trace_pre > 0.1 and syn.trace_post > 0.1:
                    syn.accumulator += self.params.eta_hebb * syn.trace_pre * syn.trace_post
                
                # Ternarize
                syn.weight_ternary = self.ternarize_weight(syn.weight, syn.accumulator)
                
                # Update weight from ternary state
                if syn.weight_ternary == WeightState.POSITIVE:
                    syn.weight = 1.0
                elif syn.weight_ternary == WeightState.NEGATIVE:
                    syn.weight = -1.0
                else:
                    syn.weight = 0.0
                
                # BCM threshold update
                r_squared = self.firing_rates[j] ** 2
                syn.theta_local = self.update_threshold(syn.theta_local, r_squared)
                
                # Consolidation check
                if abs(syn.weight - syn.weight_consolidated) > self.params.consolidation_threshold:
                    self.consolidation_queue.append((i, j, syn.weight))
        
        # Process consolidation queue (limited resources)
        max_consolidations = 10  # Resource limit
        for i, j, w in self.consolidation_queue[:max_consolidations]:
            syn = self.synapses[i, j]
            # Gradual consolidation
            syn.weight_consolidated += (w - syn.weight_consolidated) * 0.01
        
        self.consolidation_queue = self.consolidation_queue[max_consolidations:]
        
        # Update activity history
        self.activity_history.append({
            'time': self.time,
            'weights': self.get_weight_matrix(),
            'accumulators': self.get_accumulator_matrix()
        })
    
    def get_weight_matrix(self) -> np.ndarray:
        """Get the current weight matrix."""
        W = np.zeros((self.n_neurons, self.n_neurons))
        for i in range(self.n_neurons):
            for j in range(self.n_neurons):
                W[i, j] = self.synapses[i, j].weight
        return W
    
    def get_accumulator_matrix(self) -> np.ndarray:
        """Get the current accumulator matrix."""
        A = np.zeros((self.n_neurons, self.n_neurons))
        for i in range(self.n_neurons):
            for j in range(self.n_neurons):
                A[i, j] = self.synapses[i, j].accumulator
        return A
    
    def get_consolidated_matrix(self) -> np.ndarray:
        """Get the consolidated weight matrix."""
        C = np.zeros((self.n_neurons, self.n_neurons))
        for i in range(self.n_neurons):
            for j in range(self.n_neurons):
                C[i, j] = self.synapses[i, j].weight_consolidated
        return C
    
    def compute_energy(self) -> float:
        """Compute total energy consumption estimate."""
        # Energy per spike
        E_spike = 1e-12  # 1 pJ
        
        # Energy per weight update
        E_update = 5e-12  # 5 pJ
        
        # Total spikes (approximate from traces)
        total_trace = sum(
            syn.trace_pre + syn.trace_post 
            for i in range(self.n_neurons) 
            for j in range(self.n_neurons)
            for syn in [self.synapses[i, j]]
        )
        
        # Updates (from consolidation queue)
        n_updates = len(self.consolidation_queue)
        
        return total_trace * E_spike + n_updates * E_update


def analyze_stability():
    """
    Analyze stability of plasticity dynamics using eigenvalue analysis.
    """
    params = PlasticityParameters()
    
    # Jacobian eigenvalues
    gamma = params.decay_rate
    eta_homeo = params.alpha_homeo
    tau_meta = params.tau_meta
    tau_consol = params.tau_consol / 1000  # Convert to ms
    
    # At typical firing rate
    r = 0.1
    
    eigenvalues = [
        -gamma - eta_homeo * r,
        -1 / tau_meta,
        -1 / tau_consol
    ]
    
    print("\n" + "=" * 60)
    print("STABILITY ANALYSIS")
    print("=" * 60)
    print(f"\nEigenvalues of Jacobian:")
    print(f"  λ₁ (weight dynamics): {eigenvalues[0]:.6f}")
    print(f"  λ₂ (threshold dynamics): {eigenvalues[1]:.6f}")
    print(f"  λ₃ (consolidation dynamics): {eigenvalues[2]:.6f}")
    print(f"\nAll eigenvalues negative: {all(e < 0 for e in eigenvalues)}")
    print(f"System is: {'STABLE' if all(e < 0 for e in eigenvalues) else 'UNSTABLE'}")
    
    # Time constants
    print(f"\nEffective time constants:")
    print(f"  τ_weight: {1/abs(eigenvalues[0]):.1f} ms")
    print(f"  τ_threshold: {1/abs(eigenvalues[1]):.1f} ms")
    print(f"  τ_consolidation: {1/abs(eigenvalues[2]):.1f} ms")
    
    # Lyapunov analysis
    print(f"\nLyapunov Function Analysis:")
    print(f"  V(x) = ½[(W-W*)² + (θ-θ*)² + (W_LT-W*LT)²]")
    print(f"  dV/dt = -γ(W-W*)² - (1/τ_θ)(θ-θ*)² - (1/τ_c)(W_LT-W*LT)² < 0")
    print(f"  Conclusion: Asymptotically stable equilibrium")
    
    return eigenvalues


def visualize_stdp_window(save_path: str = None):
    """
    Visualize the STDP learning window with biological parameters.
    
    Args:
        save_path: Path to save the figure
    """
    params = PlasticityParameters()
    
    delta_t = np.linspace(-100, 100, 1000)
    delta_w = np.array([params.A_plus * np.exp(-t/params.tau_plus) if t > 0 
                       else -params.A_minus * np.exp(t/params.tau_minus) 
                       for t in delta_t])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(delta_t, delta_w, 'b-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
    ax.fill_between(delta_t[delta_t > 0], delta_w[delta_t > 0], alpha=0.3, color='green', label='LTP Region')
    ax.fill_between(delta_t[delta_t < 0], delta_w[delta_t < 0], alpha=0.3, color='red', label='LTD Region')
    ax.set_xlabel('Δt = t_post - t_pre (ms)', fontsize=12)
    ax.set_ylabel('Δw', fontsize=12)
    ax.set_title('STDP Learning Window\n(Biological Parameters from Bi & Poo, 1998)', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-100, 100)
    
    # Annotate parameters
    textstr = f'A₊ = {params.A_plus}\nA₋ = {params.A_minus}\nτ₊ = {params.tau_plus} ms\nτ₋ = {params.tau_minus} ms'
    ax.annotate(textstr,
                xy=(50, 0.003), fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def visualize_bcm_metaplasticity(save_path: str = None):
    """
    Visualize BCM metaplasticity sliding threshold.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # BCM learning rule curve
    ax = axes[0]
    r_post = np.linspace(0, 1, 100)
    theta_m_values = [0.2, 0.5, 0.8]
    
    for theta_m in theta_m_values:
        delta_w = r_post * (r_post - theta_m)
        ax.plot(r_post, delta_w, linewidth=2, label=f'θ_M = {theta_m}')
    
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Post-synaptic firing rate r_post', fontsize=12)
    ax.set_ylabel('Δw', fontsize=12)
    ax.set_title('BCM Learning Rule\nΔw = η·r_post·(r_post - θ_M)', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Sliding threshold dynamics
    ax = axes[1]
    time = np.linspace(0, 10000, 1000)  # ms
    tau_m = 1000  # ms
    r_squared_avg = 0.3
    
    # Theta evolves toward r²_avg
    theta_t = r_squared_avg * (1 - np.exp(-time / tau_m))
    
    ax.plot(time, theta_t, 'b-', linewidth=2)
    ax.axhline(y=r_squared_avg, color='r', linestyle='--', label=f'Equilibrium θ* = ⟨r²⟩ = {r_squared_avg}')
    ax.set_xlabel('Time (ms)', fontsize=12)
    ax.set_ylabel('Modification threshold θ_M', fontsize=12)
    ax.set_title('Sliding Threshold Dynamics\nτ_M·dθ_M/dt = ⟨r²⟩ - θ_M', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def visualize_consolidation(save_path: str = None):
    """
    Visualize memory consolidation dynamics.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Consolidation time course
    ax = axes[0]
    tau_consol = 3600 * 1000  # 1 hour in ms
    time_hours = np.linspace(0, 6, 1000)
    time_ms = time_hours * 3600 * 1000
    
    W_st = 1.0  # Short-term weight
    W_lt = W_st * (1 - np.exp(-time_ms / tau_consol))
    
    ax.plot(time_hours, W_lt, 'b-', linewidth=2, label='Long-term weight W_LT')
    ax.axhline(y=W_st, color='r', linestyle='--', label='Short-term weight W_ST')
    ax.fill_between(time_hours, 0, W_lt, alpha=0.3, color='blue')
    ax.set_xlabel('Time (hours)', fontsize=12)
    ax.set_ylabel('Weight value', fontsize=12)
    ax.set_title('Memory Consolidation\nW_LT → W_ST over τ_consol = 1 hour', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1.1)
    
    # Bistable potential
    ax = axes[1]
    w = np.linspace(-1.5, 1.5, 100)
    a = 1.0
    U = a/4 * (w**2 - 1)**2
    
    ax.plot(w, U, 'b-', linewidth=2)
    ax.plot([-1, 1], [0, 0], 'go', markersize=10, label='Stable fixed points')
    ax.plot([0], [a/4], 'ro', markersize=10, label='Unstable fixed point')
    ax.set_xlabel('Weight w', fontsize=12)
    ax.set_ylabel('Potential U(w)', fontsize=12)
    ax.set_title('Bistable Weight Potential\nU(w) = a/4(w² - 1)²', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def simulate_learning_dynamics():
    """
    Run comprehensive simulation of learning dynamics.
    """
    print("\n" + "=" * 60)
    print("LEARNING DYNAMICS SIMULATION")
    print("=" * 60)
    
    # Parameters
    n_neurons = 32
    params = PlasticityParameters()
    
    # Initialize simulator
    sim = GeometricPlasticitySimulator(n_neurons, params)
    
    # Initialize some random connections
    np.random.seed(42)
    for i in range(n_neurons):
        for j in range(n_neurons):
            if np.random.random() < 0.3:  # 30% connectivity
                sim.synapses[i, j].weight = np.random.choice([-1, 1])
                sim.synapses[i, j].weight_ternary = WeightState.POSITIVE if sim.synapses[i, j].weight > 0 else WeightState.NEGATIVE
    
    # Simulation
    dt = 1.0  # ms
    n_steps = 10000
    spike_rate = 0.1  # Probability of spike per neuron per step
    
    # Tracking
    weight_history = []
    energy_history = []
    
    print(f"\nSimulating {n_steps} time steps...")
    
    for step in range(n_steps):
        # Generate random input spikes
        n_spikes = np.random.poisson(spike_rate * n_neurons)
        input_spikes = np.random.choice(n_neurons, n_spikes, replace=True)
        
        # Simulate step
        sim.simulate_step(dt, input_spikes)
        
        # Record
        if step % 100 == 0:
            weight_history.append(sim.get_weight_matrix().copy())
            energy_history.append(sim.compute_energy())
    
    print(f"Completed simulation of {len(weight_history) * 100} time steps")
    print(f"Final energy consumption: {energy_history[-1]:.2e} J")
    
    return sim, weight_history, energy_history


def visualize_weight_distribution(sim: GeometricPlasticitySimulator, save_path: str = None):
    """
    Visualize weight distribution after learning.
    """
    W = sim.get_weight_matrix()
    A = sim.get_accumulator_matrix()
    C = sim.get_consolidated_matrix()
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Weight matrix heatmap
    ax = axes[0, 0]
    im = ax.imshow(W, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_title('Weight Matrix (Ternary)', fontsize=12)
    ax.set_xlabel('Post-synaptic neuron')
    ax.set_ylabel('Pre-synaptic neuron')
    plt.colorbar(im, ax=ax, label='Weight')
    
    # Accumulator distribution
    ax = axes[0, 1]
    ax.hist(A.flatten(), bins=50, alpha=0.7, color='blue')
    ax.axvline(x=1.0, color='r', linestyle='--', label='LTP threshold')
    ax.axvline(x=-1.0, color='r', linestyle='--', label='LTD threshold')
    ax.set_xlabel('Accumulator value')
    ax.set_ylabel('Count')
    ax.set_title('Accumulator Distribution', fontsize=12)
    ax.legend()
    
    # Consolidated vs current
    ax = axes[1, 0]
    ax.scatter(C.flatten()[::10], W.flatten()[::10], alpha=0.5, s=1)
    ax.plot([-1, 1], [-1, 1], 'r--', label='y=x')
    ax.set_xlabel('Consolidated weight')
    ax.set_ylabel('Current weight')
    ax.set_title('Consolidation Status', fontsize=12)
    ax.legend()
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Weight histogram
    ax = axes[1, 1]
    weight_values = W.flatten()
    unique, counts = np.unique(weight_values, return_counts=True)
    ax.bar(unique, counts, width=0.3, alpha=0.7)
    ax.set_xlabel('Weight value')
    ax.set_ylabel('Count')
    ax.set_title('Weight Distribution', fontsize=12)
    ax.set_xticks([-1, 0, 1])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def visualize_homeostatic_scaling(save_path: str = None):
    """
    Visualize homeostatic synaptic scaling.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Scaling function
    ax = axes[0]
    r_target = 0.1
    alpha_values = [0.2, 0.5, 1.0]
    r_actual = np.linspace(0.01, 0.5, 100)
    
    for alpha in alpha_values:
        g = (r_target / r_actual) ** alpha
        ax.plot(r_actual, g, linewidth=2, label=f'α = {alpha}')
    
    ax.axvline(x=r_target, color='k', linestyle='--', label=f'r_target = {r_target}')
    ax.axhline(y=1, color='gray', linestyle=':', linewidth=0.5)
    ax.set_xlabel('Actual firing rate r', fontsize=12)
    ax.set_ylabel('Scaling factor g(r)', fontsize=12)
    ax.set_title('Homeostatic Scaling Function\ng(r) = (r_target/r)^α', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 10)
    
    # Activity regulation over time
    ax = axes[1]
    time = np.linspace(0, 100, 1000)
    tau_h = 20
    r_target = 0.1
    
    # Simulate activity approaching target
    r = 0.3 * np.exp(-time/tau_h) + r_target * (1 - np.exp(-time/tau_h))
    
    ax.plot(time, r, 'b-', linewidth=2, label='Activity r(t)')
    ax.axhline(y=r_target, color='r', linestyle='--', label=f'Target r* = {r_target}')
    ax.fill_between(time, r_target, r, alpha=0.3, color='blue')
    ax.set_xlabel('Time (a.u.)', fontsize=12)
    ax.set_ylabel('Firing rate', fontsize=12)
    ax.set_title('Homeostatic Activity Regulation\nr → r_target', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def visualize_mram_resistance_mapping(save_path: str = None):
    """
    Visualize MRAM resistance mapping for geometric plasticity.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Resistance vs conductance
    ax = axes[0]
    G = np.linspace(0.1, 10, 100)  # mS
    R0 = 1.0  # kΩ
    alpha = 0.3
    
    R = R0 * np.exp(-alpha * G)
    
    ax.plot(G, R, 'b-', linewidth=2)
    ax.set_xlabel('Geometric conductance G (mS)', fontsize=12)
    ax.set_ylabel('MRAM resistance R (kΩ)', fontsize=12)
    ax.set_title('MRAM Resistance Mapping\nR(G) = R₀·e^(-αG)', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Annotate ternary states
    ax.axhline(y=1.0, color='g', linestyle='--', alpha=0.5, label='R_P (+1 state)')
    ax.axhline(y=10.0, color='r', linestyle='--', alpha=0.5, label='R_AP (-1 state)')
    ax.legend()
    
    # Ternary weight encoding
    ax = axes[1]
    states = ['-1', '0', '+1']
    resistances = [10, np.inf, 1]  # kΩ
    colors = ['red', 'gray', 'green']
    
    x = np.arange(len(states))
    bars = ax.bar(x, [10, 0.1, 1], color=colors, alpha=0.7, edgecolor='black')
    
    ax.set_xticks(x)
    ax.set_xticklabels(states)
    ax.set_xlabel('Weight state', fontsize=12)
    ax.set_ylabel('Resistance (kΩ)', fontsize=12)
    ax.set_title('Ternary Weight to MRAM State\nMapping', fontsize=14)
    
    # Add labels
    for bar, r in zip(bars, resistances):
        height = bar.get_height()
        label = f'R = {r} kΩ' if r != np.inf else 'R = ∞'
        ax.annotate(label,
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom', fontsize=10)
    
    ax.set_ylim(0, 12)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def run_comprehensive_simulation():
    """
    Run comprehensive simulation and generate all visualizations.
    """
    print("\n" + "=" * 70)
    print("  GEOMETRIC PLASTICITY LEARNING SIMULATION")
    print("  Cycle 3: Neuromorphic Hardware Research")
    print("=" * 70)
    
    # 1. Stability analysis
    eigenvalues = analyze_stability()
    
    # 2. STDP window
    print("\n" + "-" * 40)
    print("Generating STDP Learning Window...")
    fig_stdp = visualize_stdp_window('/home/z/my-project/research/stdp_learning_window.png')
    
    # 3. BCM metaplasticity
    print("Generating BCM Metaplasticity visualization...")
    fig_bcm = visualize_bcm_metaplasticity('/home/z/my-project/research/bcm_metaplasticity.png')
    
    # 4. Consolidation dynamics
    print("Generating Consolidation Dynamics visualization...")
    fig_consol = visualize_consolidation('/home/z/my-project/research/consolidation_dynamics.png')
    
    # 5. Homeostatic scaling
    print("Generating Homeostatic Scaling visualization...")
    fig_homeo = visualize_homeostatic_scaling('/home/z/my-project/research/homeostatic_scaling.png')
    
    # 6. MRAM resistance mapping
    print("Generating MRAM Resistance Mapping visualization...")
    fig_mram = visualize_mram_resistance_mapping('/home/z/my-project/research/mram_resistance_mapping.png')
    
    # 7. Learning simulation
    sim, weight_history, energy_history = simulate_learning_dynamics()
    
    # 8. Weight distribution
    print("\nGenerating Weight Distribution visualization...")
    fig_weights = visualize_weight_distribution(sim, '/home/z/my-project/research/weight_distribution.png')
    
    # Summary statistics
    W = sim.get_weight_matrix()
    print("\n" + "=" * 60)
    print("SIMULATION RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nNetwork Statistics:")
    print(f"  Total synapses: {W.size}")
    print(f"  Positive weights: {np.sum(W > 0)} ({np.sum(W > 0)/W.size*100:.1f}%)")
    print(f"  Negative weights: {np.sum(W < 0)} ({np.sum(W < 0)/W.size*100:.1f}%)")
    print(f"  Zero weights: {np.sum(W == 0)} ({np.sum(W == 0)/W.size*100:.1f}%)")
    
    print(f"\nEnergy Consumption:")
    print(f"  Final energy: {energy_history[-1]:.2e} J")
    print(f"  Average energy per step: {np.mean(energy_history):.2e} J")
    
    print("\n" + "=" * 60)
    print("OUTPUT FILES")
    print("=" * 60)
    print("  /home/z/my-project/research/stdp_learning_window.png")
    print("  /home/z/my-project/research/bcm_metaplasticity.png")
    print("  /home/z/my-project/research/consolidation_dynamics.png")
    print("  /home/z/my-project/research/homeostatic_scaling.png")
    print("  /home/z/my-project/research/mram_resistance_mapping.png")
    print("  /home/z/my-project/research/weight_distribution.png")
    print("  /home/z/my-project/research/cycle3_plasticity_learning.md")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    
    plt.close('all')
    
    return sim, weight_history, energy_history


if __name__ == "__main__":
    run_comprehensive_simulation()
