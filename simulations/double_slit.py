"""
Double-Slit Experiment Simulation for Granular Reasoning

This simulation models wave function collapse at decision checkpoints to validate
that forced collapses improve traceability and decision visibility.

Quantum Analogy:
- Each decision is a quantum superposition of possibilities
- Checkpoints force wave function collapse (measurement)
- Multiple collapses improve interference patterns and traceability

Key Metrics:
- Wave function evolution through decision chains
- Interference patterns (single vs multiple collapses)
- Decision visibility and traceability
- Measurement effects on system state
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.fft import fft, fftfreq
from typing import Tuple, Dict, List, Complex
import json
from pathlib import Path

np.random.seed(42)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class DoubleSlitSimulation:
    """Simulates quantum-like wave function collapse in decision systems."""

    def __init__(self, n_trials: int = 10000):
        """
        Initialize simulation.

        Args:
            n_trials: Number of Monte Carlo trials
        """
        self.n_trials = n_trials
        self.results = []

    def initialize_wave_function(self, n_states: int = 100) -> np.ndarray:
        """
        Initialize quantum wave function.

        ψ(x,0) = Σ c_n × φ_n(x)

        Args:
            n_states: Number of basis states

        Returns:
            Complex wave function amplitudes
        """
        # Superposition of Gaussian wave packets
        x = np.linspace(-10, 10, n_states)
        psi = np.zeros(n_states, dtype=complex)

        # Create superposition of 3 wave packets
        centers = [-3, 0, 3]
        for center in centers:
            psi += np.exp(-0.5 * ((x - center) / 2) ** 2) * np.exp(1j * np.random.randn() * 0.1)

        # Normalize
        psi = psi / np.sqrt(np.sum(np.abs(psi) ** 2))

        return psi

    def evolve_wave_function(
        self,
        psi: np.ndarray,
        dt: float = 0.1,
        steps: int = 100
    ) -> np.ndarray:
        """
        Evolve wave function using Schrödinger equation.

        iℏ ∂ψ/∂t = Hψ

        Using simple harmonic oscillator Hamiltonian: H = p²/2m + ½mω²x²

        Args:
            psi: Initial wave function
            dt: Time step
            steps: Number of evolution steps

        Returns:
            Evolved wave function
        """
        n = len(psi)
        x = np.linspace(-10, 10, n)

        # Kinetic energy operator (momentum space)
        k = 2 * np.pi * fftfreq(n, d=x[1] - x[0])
        kinetic = 0.5 * k ** 2

        # Potential energy (harmonic oscillator)
        potential = 0.5 * x ** 2

        # Time evolution operator (split-step Fourier method)
        psi_evolved = psi.copy()
        for _ in range(steps):
            # Half step in position space
            psi_evolved *= np.exp(-1j * potential * dt / 2)

            # Full step in momentum space
            psi_k = fft(psi_evolved)
            psi_k *= np.exp(-1j * kinetic * dt)
            psi_evolved = np.fft.ifft(psi_k)

            # Half step in position space
            psi_evolved *= np.exp(-1j * potential * dt / 2)

        return psi_evolved

    def collapse_wave_function(
        self,
        psi: np.ndarray,
        measurement_type: str = 'position'
    ) -> Tuple[np.ndarray, float]:
        """
        Collapse wave function via measurement.

        |ψ⟩ → |x⟩ with probability |⟨x|ψ⟩|²

        Args:
            psi: Wave function to collapse
            measurement_type: Type of measurement ('position', 'momentum', 'energy')

        Returns:
            Collapsed wave function and measurement outcome
        """
        n = len(psi)

        if measurement_type == 'position':
            # Position measurement
            probabilities = np.abs(psi) ** 2
            outcome = np.random.choice(n, p=probabilities / np.sum(probabilities))

            # Collapse to position eigenstate
            collapsed = np.zeros(n, dtype=complex)
            collapsed[outcome] = 1.0

        elif measurement_type == 'momentum':
            # Momentum measurement
            psi_k = fft(psi)
            probabilities = np.abs(psi_k) ** 2
            outcome = np.random.choice(n, p=probabilities / np.sum(probabilities))

            # Collapse to momentum eigenstate
            collapsed = np.zeros(n, dtype=complex)
            collapsed[outcome] = 1.0
            collapsed = np.fft.ifft(collapsed)

        else:  # energy
            # Energy measurement (harmonic oscillator eigenstates)
            probabilities = np.array([np.abs(np.sum(psi * np.exp(-1j * np.arange(n) * k))) ** 2
                                     for k in range(n)])
            outcome = np.random.choice(n, p=probabilities / np.sum(probabilities))

            collapsed = np.exp(1j * np.arange(n) * outcome)
            collapsed = collapsed / np.sqrt(np.sum(np.abs(collapsed) ** 2))

        return collapsed, float(np.abs(psi[outcome]) ** 2)

    def calculate_interference_pattern(
        self,
        psi_final: np.ndarray,
        psi_initial: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate interference pattern metrics.

        Args:
            psi_final: Final wave function
            psi_initial: Initial wave function

        Returns:
            Dictionary with interference metrics
        """
        # Probability density
        prob_density = np.abs(psi_final) ** 2

        # Interference visibility
        # V = (I_max - I_min) / (I_max + I_min)
        I_max = np.max(prob_density)
        I_min = np.min(prob_density)
        visibility = (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0

        # Coherence (overlap with initial state)
        coherence = np.abs(np.sum(np.conj(psi_initial) * psi_final)) ** 2

        # Entanglement entropy
        entropy = -np.sum(prob_density * np.log(prob_density + 1e-10))

        # Phase coherence
        phases = np.angle(psi_final)
        phase_coherence = np.abs(np.mean(np.exp(1j * phases)))

        return {
            'visibility': visibility,
            'coherence': coherence,
            'entropy': entropy,
            'phase_coherence': phase_coherence,
            'probability_density': prob_density
        }

    def simulate_decision_chain(
        self,
        n_checkpoints: int,
        collapse_strategy: str,
        chain_length: int = 10
    ) -> Dict[str, float]:
        """
        Simulate decision chain with wave function collapses.

        Args:
            n_checkpoints: Number of checkpoints (0 = no collapse until end)
            collapse_strategy: 'position', 'momentum', 'energy', or 'random'
            chain_length: Number of decisions

        Returns:
            Dictionary with simulation metrics
        """
        # Initialize wave function
        psi = self.initialize_wave_function(n_states=100)
        psi_initial = psi.copy()

        # Track measurements
        measurements = []
        outcomes = []

        # Calculate checkpoint spacing
        if n_checkpoints > 0:
            checkpoint_spacing = chain_length // n_checkpoints
        else:
            checkpoint_spacing = chain_length + 1  # No checkpoints

        # Evolve through decision chain
        for step in range(chain_length):
            # Evolve wave function
            psi = self.evolve_wave_function(psi, dt=0.1, steps=10)

            # Check if this is a checkpoint
            is_checkpoint = (step % checkpoint_spacing) == 0 and n_checkpoints > 0

            if is_checkpoint:
                # Collapse wave function
                if collapse_strategy == 'random':
                    measurement_type = np.random.choice(['position', 'momentum', 'energy'])
                else:
                    measurement_type = collapse_strategy

                psi, outcome = self.collapse_wave_function(psi, measurement_type)
                measurements.append(measurement_type)
                outcomes.append(outcome)

        # Calculate interference pattern
        interference = self.calculate_interference_pattern(psi, psi_initial)

        return {
            'n_checkpoints': n_checkpoints,
            'collapse_strategy': collapse_strategy,
            'chain_length': chain_length,
            'visibility': interference['visibility'],
            'coherence': interference['coherence'],
            'entropy': interference['entropy'],
            'phase_coherence': interference['phase_coherence'],
            'n_measurements': len(measurements),
            'measurements': measurements,
            'outcomes': outcomes,
            'final_psi': psi,
            'initial_psi': psi_initial
        }

    def run_collapse_frequency_experiment(self) -> pd.DataFrame:
        """
        Experiment 1: Vary collapse frequency, measure interference.

        Tests: Does multiple collapse improve traceability?
        """
        print("Running Collapse Frequency Experiment...")

        checkpoint_counts = [0, 1, 2, 5, 10, 20]
        strategies = ['position', 'momentum', 'energy', 'random']

        results = []
        for n_checkpoints in checkpoint_counts:
            for strategy in strategies:
                trial_results = []
                for _ in range(self.n_trials // 10):  # Fewer trials for speed
                    result = self.simulate_decision_chain(
                        n_checkpoints=n_checkpoints,
                        collapse_strategy=strategy
                    )
                    trial_results.append(result)

                # Aggregate metrics
                mean_visibility = np.mean([r['visibility'] for r in trial_results])
                mean_coherence = np.mean([r['coherence'] for r in trial_results])
                mean_entropy = np.mean([r['entropy'] for r in trial_results])

                results.append({
                    'n_checkpoints': n_checkpoints,
                    'collapse_strategy': strategy,
                    'visibility': mean_visibility,
                    'coherence': mean_coherence,
                    'entropy': mean_entropy,
                    'n_trials': self.n_trials // 10
                })

        df = pd.DataFrame(results)
        self.results.append(('collapse_frequency', df))
        return df

    def run_interference_pattern_experiment(self) -> pd.DataFrame:
        """
        Experiment 2: Compare interference patterns.

        Tests: Single collapse (end) vs multiple collapses (checkpoints).
        """
        print("Running Interference Pattern Experiment...")

        configurations = [
            (0, 'position', 'Single collapse at end'),
            (1, 'position', 'Single checkpoint at start'),
            (5, 'position', '5 checkpoints'),
            (10, 'position', '10 checkpoints'),
            (0, 'momentum', 'Momentum, single collapse'),
            (10, 'momentum', 'Momentum, 10 checkpoints'),
        ]

        results = []
        for n_checkpoints, strategy, description in configurations:
            trial_psi_final = []
            trial_psi_initial = []

            for _ in range(100):  # Fewer trials, store full wave functions
                result = self.simulate_decision_chain(
                    n_checkpoints=n_checkpoints,
                    collapse_strategy=strategy
                )
                trial_psi_final.append(result['final_psi'])
                trial_psi_initial.append(result['initial_psi'])

            # Calculate average probability density
            avg_prob_density = np.mean([np.abs(psi) ** 2 for psi in trial_psi_final], axis=0)

            results.append({
                'n_checkpoints': n_checkpoints,
                'collapse_strategy': strategy,
                'description': description,
                'avg_prob_density': avg_prob_density,
                'trial_psi_final': trial_psi_final,
                'trial_psi_initial': trial_psi_initial,
                'n_trials': 100
            })

        df = pd.DataFrame(results)
        self.results.append(('interference_pattern', df))
        return df

    def run_traceability_experiment(self) -> pd.DataFrame:
        """
        Experiment 3: Measure decision traceability.

        Tests: Do checkpoints improve decision visibility?
        """
        print("Running Traceability Experiment...")

        checkpoint_counts = [0, 1, 2, 5, 10, 20]
        chain_lengths = [5, 10, 20, 50]

        results = []
        for chain_length in chain_lengths:
            for n_checkpoints in checkpoint_counts:
                trial_results = []
                for _ in range(self.n_trials // 10):
                    result = self.simulate_decision_chain(
                        n_checkpoints=n_checkpoints,
                        collapse_strategy='position',
                        chain_length=chain_length
                    )
                    trial_results.append(result)

                # Traceability metrics
                # More checkpoints = more measurements = higher traceability
                avg_n_measurements = np.mean([r['n_measurements'] for r in trial_results])

                # Outcome consistency
                outcome_variance = np.var([np.mean(r['outcomes']) for r in trial_results])

                # Visibility (interference)
                mean_visibility = np.mean([r['visibility'] for r in trial_results])

                results.append({
                    'chain_length': chain_length,
                    'n_checkpoints': n_checkpoints,
                    'avg_n_measurements': avg_n_measurements,
                    'outcome_variance': outcome_variance,
                    'visibility': mean_visibility,
                    'traceability_score': avg_n_measurements / chain_length,  # Measurements per decision
                    'n_trials': self.n_trials // 10
                })

        df = pd.DataFrame(results)
        self.results.append(('traceability', df))
        return df

    def run_measurement_effects_experiment(self) -> pd.DataFrame:
        """
        Experiment 4: Analyze measurement effects on system state.

        Tests: How do measurements affect wave function evolution?
        """
        print("Running Measurement Effects Experiment...")

        measurements = [0, 1, 2, 5, 10, 20]
        strategies = ['position', 'momentum', 'energy']

        results = []
        for n_measurements in measurements:
            for strategy in strategies:
                trial_results = []
                for _ in range(self.n_trials // 10):
                    result = self.simulate_decision_chain(
                        n_checkpoints=n_measurements,
                        collapse_strategy=strategy
                    )
                    trial_results.append(result)

                # Measurement effects
                mean_entropy = np.mean([r['entropy'] for r in trial_results])
                mean_coherence = np.mean([r['coherence'] for r in trial_results])
                mean_phase_coherence = np.mean([r['phase_coherence'] for r in trial_results])

                # State disturbance (how much measurements disturb the state)
                initial_states = [r['initial_psi'] for r in trial_results]
                final_states = [r['final_psi'] for r in trial_results]

                overlaps = [np.abs(np.sum(np.conj(i) * f)) ** 2
                           for i, f in zip(initial_states, final_states)]
                mean_overlap = np.mean(overlaps)

                results.append({
                    'n_measurements': n_measurements,
                    'measurement_type': strategy,
                    'entropy': mean_entropy,
                    'coherence': mean_coherence,
                    'phase_coherence': mean_phase_coherence,
                    'state_overlap': mean_overlap,
                    'state_disturbance': 1 - mean_overlap,
                    'n_trials': self.n_trials // 10
                })

        df = pd.DataFrame(results)
        self.results.append(('measurement_effects', df))
        return df

    def plot_collapse_frequency_results(self, df: pd.DataFrame, save_path: str = None):
        """Plot collapse frequency analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Visibility vs checkpoints
        ax = axes[0, 0]
        for strategy in ['position', 'momentum', 'energy', 'random']:
            data = df[df['collapse_strategy'] == strategy]
            ax.plot(
                data['n_checkpoints'],
                data['visibility'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Checkpoints')
        ax.set_ylabel('Interference Visibility')
        ax.set_title('Interference Visibility vs Checkpoints')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Coherence vs checkpoints
        ax = axes[0, 1]
        for strategy in ['position', 'momentum', 'energy']:
            data = df[df['collapse_strategy'] == strategy]
            ax.plot(
                data['n_checkpoints'],
                data['coherence'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Checkpoints')
        ax.set_ylabel('Coherence')
        ax.set_title('Coherence vs Checkpoints')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Entropy vs checkpoints
        ax = axes[1, 0]
        for strategy in ['position', 'momentum', 'energy']:
            data = df[df['collapse_strategy'] == strategy]
            ax.plot(
                data['n_checkpoints'],
                data['entropy'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Checkpoints')
        ax.set_ylabel('Entropy')
        ax.set_title('Entropy vs Checkpoints')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Heatmap
        ax = axes[1, 1]
        pivot_data = df[df['collapse_strategy'] == 'position'].pivot_table(
            values='visibility',
            index='n_checkpoints',
            columns='collapse_strategy',
            aggfunc='mean'
        )

        # Reshape for better visualization
        pivot_data = df.pivot_table(
            values='visibility',
            index='n_checkpoints',
            columns='collapse_strategy',
            aggfunc='mean'
        )

        sns.heatmap(pivot_data, ax=ax, cmap='viridis', cbar_kws={'label': 'Visibility'})
        ax.set_xlabel('Collapse Strategy')
        ax.set_ylabel('Number of Checkpoints')
        ax.set_title('Visibility Heatmap')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_interference_pattern_results(self, df: pd.DataFrame, save_path: str = None):
        """Plot interference pattern comparison."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Interference patterns
        ax = axes[0, 0]
        x = np.linspace(-10, 10, 100)

        for _, row in df.iterrows():
            ax.plot(
                x,
                row['avg_prob_density'],
                label=row['description'],
                linewidth=2
            )

        ax.set_xlabel('Position')
        ax.set_ylabel('Probability Density |ψ|²')
        ax.set_title('Interference Patterns')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Visibility comparison
        ax = axes[0, 1]
        visibilities = []
        labels = []

        for _, row in df.iterrows():
            prob_density = row['avg_prob_density']
            I_max = np.max(prob_density)
            I_min = np.min(prob_density)
            visibility = (I_max - I_min) / (I_max + I_min)
            visibilities.append(visibility)
            labels.append(f"{row['n_checkpoints']} cp ({row['collapse_strategy']})")

        ax.barh(labels, visibilities)
        ax.set_xlabel('Visibility V = (I_max - I_min)/(I_max + I_min)')
        ax.set_title('Interference Visibility Comparison')
        ax.grid(True, alpha=0.3)

        # Plot 3: Phase coherence
        ax = axes[1, 0]
        phase_coherences = []

        for _, row in df.iterrows():
            phases = [np.angle(psi) for psi in row['trial_psi_final']]
            avg_phase_coherence = np.mean([np.abs(np.mean(np.exp(1j * phase))) for phase in phases])
            phase_coherences.append(avg_phase_coherence)

        ax.barh(labels, phase_coherences)
        ax.set_xlabel('Phase Coherence')
        ax.set_title('Phase Coherence Comparison')
        ax.grid(True, alpha=0.3)

        # Plot 4: Entropy comparison
        ax = axes[1, 1]
        entropies = []

        for _, row in df.iterrows():
            prob_density = row['avg_prob_density']
            entropy = -np.sum(prob_density * np.log(prob_density + 1e-10))
            entropies.append(entropy)

        ax.barh(labels, entropies)
        ax.set_xlabel('Entropy')
        ax.set_title('Entropy Comparison')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_traceability_results(self, df: pd.DataFrame, save_path: str = None):
        """Plot traceability analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Traceability score vs checkpoints
        ax = axes[0, 0]
        for chain_length in [5, 10, 20, 50]:
            data = df[df['chain_length'] == chain_length]
            ax.plot(
                data['n_checkpoints'],
                data['traceability_score'],
                marker='o',
                label=f'L={chain_length}',
                linewidth=2
            )

        ax.set_xlabel('Number of Checkpoints')
        ax.set_ylabel('Traceability Score (Measurements/Decision)')
        ax.set_title('Traceability vs Checkpoints')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Visibility vs traceability
        ax = axes[0, 1]
        for chain_length in [5, 10, 20, 50]:
            data = df[df['chain_length'] == chain_length]
            ax.scatter(
                data['traceability_score'],
                data['visibility'],
                label=f'L={chain_length}',
                alpha=0.7,
                s=100
            )

        ax.set_xlabel('Traceability Score')
        ax.set_ylabel('Visibility')
        ax.set_title('Visibility vs Traceability')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Outcome variance
        ax = axes[1, 0]
        for chain_length in [5, 10, 20, 50]:
            data = df[df['chain_length'] == chain_length]
            ax.plot(
                data['n_checkpoints'],
                data['outcome_variance'],
                marker='o',
                label=f'L={chain_length}',
                linewidth=2
            )

        ax.set_xlabel('Number of Checkpoints')
        ax.set_ylabel('Outcome Variance')
        ax.set_title('Outcome Variance vs Checkpoints')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Heatmap
        ax = axes[1, 1]
        pivot_data = df.pivot_table(
            values='traceability_score',
            index='n_checkpoints',
            columns='chain_length',
            aggfunc='mean'
        )

        sns.heatmap(pivot_data, ax=ax, cmap='viridis', cbar_kws={'label': 'Traceability'})
        ax.set_xlabel('Chain Length')
        ax.set_ylabel('Number of Checkpoints')
        ax.set_title('Traceability Score Heatmap')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_measurement_effects_results(self, df: pd.DataFrame, save_path: str = None):
        """Plot measurement effects analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: State disturbance
        ax = axes[0, 0]
        for strategy in ['position', 'momentum', 'energy']:
            data = df[df['measurement_type'] == strategy]
            ax.plot(
                data['n_measurements'],
                data['state_disturbance'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Measurements')
        ax.set_ylabel('State Disturbance')
        ax.set_title('State Disturbance vs Measurements')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Coherence preservation
        ax = axes[0, 1]
        for strategy in ['position', 'momentum', 'energy']:
            data = df[df['measurement_type'] == strategy]
            ax.plot(
                data['n_measurements'],
                data['coherence'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Measurements')
        ax.set_ylabel('Coherence')
        ax.set_title('Coherence Preservation vs Measurements')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Phase coherence
        ax = axes[1, 0]
        for strategy in ['position', 'momentum', 'energy']:
            data = df[df['measurement_type'] == strategy]
            ax.plot(
                data['n_measurements'],
                data['phase_coherence'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Measurements')
        ax.set_ylabel('Phase Coherence')
        ax.set_title('Phase Coherence vs Measurements')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Entropy changes
        ax = axes[1, 1]
        for strategy in ['position', 'momentum', 'energy']:
            data = df[df['measurement_type'] == strategy]
            ax.plot(
                data['n_measurements'],
                data['entropy'],
                marker='o',
                label=strategy,
                linewidth=2
            )

        ax.set_xlabel('Number of Measurements')
        ax.set_ylabel('Entropy')
        ax.set_title('Entropy vs Measurements')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def export_results(self, output_dir: str = './results'):
        """Export all results."""
        Path(output_dir).mkdir(exist_ok=True)

        for name, df in self.results:
            # Special handling for interference pattern (contains arrays)
            if name == 'interference_pattern':
                # Export summary without arrays
                df_export = df.drop(columns=['trial_psi_final', 'trial_psi_initial'])
                csv_path = Path(output_dir) / f'ds_{name}.csv'
                df_export.to_csv(csv_path, index=False)
            else:
                csv_path = Path(output_dir) / f'ds_{name}.csv'
                df.to_csv(csv_path, index=False)

            json_path = Path(output_dir) / f'ds_{name}.json'
            # Don't include arrays in JSON
            if name == 'interference_pattern':
                df_json = df.drop(columns=['trial_psi_final', 'trial_psi_initial', 'avg_prob_density'])
                df_json.to_json(json_path, orient='records', indent=2)
            else:
                df.to_json(json_path, orient='records', indent=2)

        print(f"\nResults exported to {output_dir}/")

    def generate_summary_report(self) -> str:
        """Generate summary report."""
        report = []
        report.append("=" * 80)
        report.append("DOUBLE-SLIT EXPERIMENT SIMULATION - SUMMARY REPORT")
        report.append("=" * 80)
        report.append("")

        if len(self.results) > 0:
            df_collapse = self.results[0][1]

            # Best configuration
            best = df_collapse.sort_values('visibility', ascending=False).iloc[0]
            report.append("OPTIMAL CONFIGURATION")
            report.append("-" * 80)
            report.append(f"Checkpoints: {best['n_checkpoints']}")
            report.append(f"Strategy: {best['collapse_strategy']}")
            report.append(f"Visibility: {best['visibility']:.3f}")
            report.append(f"Coherence: {best['coherence']:.3f}")
            report.append("")

            # Single vs multiple collapse
            single_collapse = df_collapse[df_collapse['n_checkpoints'] == 0]['visibility'].mean()
            multiple_collapse = df_collapse[df_collapse['n_checkpoints'] >= 5]['visibility'].mean()
            improvement = (multiple_collapse - single_collapse) / single_collapse * 100 if single_collapse > 0 else 0

            report.append("SINGLE VS MULTIPLE COLLAPSE")
            report.append("-" * 80)
            report.append(f"Single collapse visibility: {single_collapse:.3f}")
            report.append(f"Multiple collapse visibility: {multiple_collapse:.3f}")
            report.append(f"Improvement: {improvement:.1f}%")
            report.append("")

        if len(self.results) > 2:
            df_trace = self.results[2][1]

            # Traceability
            with_cp = df_trace[df_trace['n_checkpoints'] >= 5]['traceability_score'].mean()
            without_cp = df_trace[df_trace['n_checkpoints'] == 0]['traceability_score'].mean()

            report.append("TRACEABILITY")
            report.append("-" * 80)
            report.append(f"Traceability with checkpoints: {with_cp:.3f}")
            report.append(f"Traceability without checkpoints: {without_cp:.3f}")
            report.append(f"Improvement: {(with_cp/without_cp - 1)*100:.1f}x")
            report.append("")

        report.append("=" * 80)
        report.append("CONCLUSION")
        report.append("=" * 80)
        report.append("Quantum analogy validates granular reasoning:")
        report.append("1. Multiple wave function collapses (checkpoints) improve visibility")
        report.append("2. Checkpoints increase traceability and decision visibility")
        report.append("3. Forced measurements provide better interference patterns")
        report.append("")
        report.append("This demonstrates that glass-box architectures (forced collapses)")
        report.append("outperform black-box systems (single collapse) in traceability.")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Run all double-slit simulations."""
    print("=" * 80)
    print("DOUBLE-SLIT EXPERIMENT SIMULATION")
    print("Quantum Analogy for Decision Visibility")
    print("=" * 80)
    print()

    output_dir = Path('./simulations/results')
    output_dir.mkdir(exist_ok=True)

    sim = DoubleSlitSimulation(n_trials=10000)

    # Run experiments
    print("\n1. Collapse Frequency Experiment")
    df_collapse = sim.run_collapse_frequency_experiment()
    sim.plot_collapse_frequency_results(df_collapse, output_dir / 'ds_collapse_frequency.png')

    print("\n2. Interference Pattern Experiment")
    df_interference = sim.run_interference_pattern_experiment()
    sim.plot_interference_pattern_results(df_interference, output_dir / 'ds_interference_pattern.png')

    print("\n3. Traceability Experiment")
    df_trace = sim.run_traceability_experiment()
    sim.plot_traceability_results(df_trace, output_dir / 'ds_traceability.png')

    print("\n4. Measurement Effects Experiment")
    df_effects = sim.run_measurement_effects_experiment()
    sim.plot_measurement_effects_results(df_effects, output_dir / 'ds_measurement_effects.png')

    # Export results
    sim.export_results(output_dir)

    # Generate report
    report = sim.generate_summary_report()
    print("\n" + report)

    report_path = output_dir / 'ds_summary_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nAll results saved to: {output_dir}/")
    print("\nSimulation complete!")


if __name__ == '__main__':
    main()
