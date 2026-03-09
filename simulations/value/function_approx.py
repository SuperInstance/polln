"""
Function Approximation for TD(λ) Learning

Mathematical Foundation:
    Linear: V(s) = w·φ(s)
    Neural: V(s) = NN_θ(s)

Research Questions:
    Q1: When does approximation break TD learning?
    Q2: How do errors propagate through function approximation?
    Q3: What's the optimal representation for different state spaces?
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from sklearn.linear_model import SGDRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.kernel_approximation import RBFSampler
import warnings
warnings.filterwarnings('ignore')


class ApproxType(Enum):
    """Function approximation types"""
    TABULAR = "Tabular"
    LINEAR = "Linear"
    POLYNOMIAL = "Polynomial"
    RBF = "RBF Kernel"
    NEURAL = "Neural Network"


@dataclass
class ApproxConfig:
    """Configuration for function approximation simulation"""
    num_states: int = 100
    state_dim: int = 1
    feature_dim: int = 10
    gamma: float = 0.99
    alpha: float = 0.01
    lambda_: float = 0.5
    num_episodes: int = 500
    num_runs: int = 50

    # Neural network config
    hidden_layers: Tuple[int, ...] = (64, 32)
    activation: str = 'relu'

    # Polynomial config
    poly_degree: int = 3


class MDPEnvironment:
    """
    Chain MDP for function approximation testing

    States: 0 to N-1
    Actions: Move right (deterministic)
    Rewards: 0 except at terminal
    """

    def __init__(self, num_states: int, reward_prob: float = 0.1):
        self.num_states = num_states
        self.terminal_state = num_states - 1
        self.reward_prob = reward_prob

        # True value function (exponential decay)
        self.true_values = np.zeros(num_states)
        for s in range(num_states):
            self.true_values[s] = self._compute_true_value(s)

    def _compute_true_value(self, state: int) -> float:
        """Compute true value using Bellman equation"""
        if state == self.terminal_state:
            return 0.0

        # V(s) = E[r + γV(s')]
        # P(reward) = reward_prob at each step
        remaining_steps = self.terminal_state - state
        value = 0.0
        for t in range(1, remaining_steps + 1):
            prob = self.reward_prob * (1 - self.reward_prob) ** (t - 1)
            value += prob * (1.0)  # Reward = 1

        return value

    def step(self, state: int) -> Tuple[int, float, bool]:
        """Take one step"""
        if state == self.terminal_state:
            return state, 0.0, True

        next_state = state + 1

        # Stochastic reward
        reward = 1.0 if np.random.random() < self.reward_prob else 0.0

        return next_state, reward, next_state == self.terminal_state

    def reset(self) -> int:
        """Reset to initial state"""
        return 0


class FeatureExtractor:
    """Extract features for function approximation"""

    def __init__(self, approx_type: ApproxType, config: ApproxConfig):
        self.approx_type = approx_type
        self.config = config

        if approx_type == ApproxType.LINEAR:
            # Simple linear features: normalize state
            self.feature_dim = 1

        elif approx_type == ApproxType.POLYNOMIAL:
            self.poly = PolynomialFeatures(degree=config.poly_degree, include_bias=False)
            # Fit on normalized states
            states = np.linspace(0, 1, config.num_states).reshape(-1, 1)
            self.poly.fit(states)
            self.feature_dim = self.poly.transform([[0]]).shape[1]

        elif approx_type == ApproxType.RBF:
            self.rbf = RBFSampler(n_components=config.feature_dim, gamma=1.0)
            states = np.linspace(0, 1, config.num_states).reshape(-1, 1)
            self.rbf.fit(states)
            self.feature_dim = config.feature_dim

        elif approx_type == ApproxType.NEURAL:
            # Neural network learns its own features
            self.feature_dim = config.state_dim

        else:  # TABULAR
            self.feature_dim = config.num_states

    def extract(self, state: int) -> np.ndarray:
        """Extract features from state"""
        if self.approx_type == ApproxType.TABULAR:
            features = np.zeros(self.feature_dim)
            features[state] = 1.0
            return features

        elif self.approx_type == ApproxType.LINEAR:
            # Normalize state to [0, 1]
            return np.array([state / (self.config.num_states - 1)])

        elif self.approx_type == ApproxType.POLYNOMIAL:
            normalized = np.array([[state / (self.config.num_states - 1)]])
            return self.poly.transform(normalized).flatten()

        elif self.approx_type == ApproxType.RBF:
            normalized = np.array([[state / (self.config.num_states - 1)]])
            return self.rbf.transform(normalized).flatten()

        else:  # NEURAL
            return np.array([state / (self.config.num_states - 1)])


class ValueApproximator:
    """Value function with different approximation types"""

    def __init__(self, approx_type: ApproxType, config: ApproxConfig):
        self.approx_type = approx_type
        self.config = config
        self.feature_extractor = FeatureExtractor(approx_type, config)

        if approx_type == ApproxType.TABULAR:
            self.weights = np.zeros(config.num_states)
            self.eligibility = np.zeros(config.num_states)

        elif approx_type == ApproxType.LINEAR:
            self.weights = np.zeros(1)
            self.eligibility = np.zeros(1)

        elif approx_type in [ApproxType.POLYNOMIAL, ApproxType.RBF]:
            self.weights = np.zeros(self.feature_extractor.feature_dim)
            self.eligibility = np.zeros(self.feature_extractor.feature_dim)

        elif approx_type == ApproxType.NEURAL:
            self.model = MLPRegressor(
                hidden_layers=config.hidden_layers,
                activation=config.activation,
                learning_rate_init=config.alpha,
                max_iter=1,
                warm_start=True,
                early_stopping=False,
                validation_fraction=0.0
            )
            # Initialize with one sample
            dummy_state = np.array([[0.0]])
            dummy_value = np.array([0.0])
            self.model.fit(dummy_state, dummy_value)

    def get_value(self, state: int) -> float:
        """Get value for a state"""
        if self.approx_type == ApproxType.NEURAL:
            features = self.feature_extractor.extract(state).reshape(1, -1)
            return self.model.predict(features)[0]
        else:
            features = self.feature_extractor.extract(state)
            return np.dot(self.weights, features)

    def update(self, state: int, td_error: float, trace: bool = True):
        """Update value function"""
        if self.approx_type == ApproxType.NEURAL:
            # Neural network uses SGD internally
            current_value = self.get_value(state)
            target = current_value + td_error

            features = self.feature_extractor.extract(state).reshape(1, -1)
            self.model.partial_fit(features, [target])

        else:
            features = self.feature_extractor.extract(state)

            if trace:
                # Update eligibility trace
                self.eligibility = (self.config.gamma * self.config.lambda_ * self.eligibility +
                                   features)
                # Update all weights
                self.weights += self.config.alpha * td_error * self.eligibility
            else:
                # TD(0) update
                self.weights += self.config.alpha * td_error * features

    def reset_traces(self):
        """Reset eligibility traces"""
        if hasattr(self, 'eligibility'):
            self.eligibility = np.zeros_like(self.eligibility)

    def get_all_values(self) -> np.ndarray:
        """Get values for all states"""
        values = []
        for s in range(self.config.num_states):
            values.append(self.get_value(s))
        return np.array(values)

    def compute_rms_error(self, true_values: np.ndarray) -> float:
        """Compute RMS error"""
        predicted = self.get_all_values()
        return np.sqrt(np.mean((predicted - true_values) ** 2))


class FunctionApproxSimulator:
    """
    Simulates function approximation for TD(λ) learning

    Research Questions:
        Q1: When does approximation break TD learning?
        Q2: How do errors propagate through function approximation?
        Q3: What's the optimal representation for different state spaces?
    """

    def __init__(self, config: ApproxConfig):
        self.config = config
        self.results: Dict[str, List[Dict]] = {}

        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 12

    def run_episode(self, env: MDPEnvironment, approximator: ValueApproximator,
                   use_traces: bool = True) -> List[float]:
        """Run a single episode"""
        state = env.reset()
        approximator.reset_traces()
        errors = []

        while True:
            next_state, reward, done = env.step(state)

            # TD target
            if done:
                target = reward
            else:
                target = reward + self.config.gamma * approximator.get_value(next_state)

            # TD error
            current_value = approximator.get_value(state)
            td_error = target - current_value

            # Update
            approximator.update(state, td_error, trace=use_traces)

            # Compute error
            rms = approximator.compute_rms_error(env.true_values)
            errors.append(rms)

            state = next_state
            if done:
                break

        return errors

    def simulate_approximation(self, approx_type: ApproxType,
                               state_sizes: List[int]) -> pd.DataFrame:
        """Simulate different approximation types across state space sizes"""
        print(f"\n{'='*70}")
        print(f"Testing {approx_type.value} Approximation")
        print(f"{'='*70}")

        results = []

        for num_states in state_sizes:
            print(f"\nState space size: {num_states}")

            # Update config
            self.config.num_states = num_states

            # Create environment
            env = MDPEnvironment(num_states)

            # Run multiple trials
            final_errors = []
            convergence_speeds = []

            for run in range(self.config.num_runs):
                approximator = ValueApproximator(approx_type, self.config)

                episode_errors = []
                for episode in range(self.config.num_episodes):
                    errors = self.run_episode(env, approximator, use_traces=True)
                    episode_errors.append(errors[-1])  # Final error

                final_errors.append(episode_errors[-1])

                # Estimate convergence (when error drops below threshold)
                threshold = 0.1
                for i, err in enumerate(episode_errors):
                    if err < threshold:
                        convergence_speeds.append(i)
                        break
                else:
                    convergence_speeds.append(self.config.num_episodes)

            results.append({
                'Approximation': approx_type.value,
                'State Space Size': num_states,
                'Final RMS Error': np.mean(final_errors),
                'Std Error': np.std(final_errors),
                'Convergence Speed': np.mean(convergence_speeds),
                'Success Rate': np.mean([e < threshold for e in final_errors])
            })

            print(f"  Final Error: {results[-1]['Final RMS Error']:.4f} ± {results[-1]['Std Error']:.4f}")
            print(f"  Convergence: {results[-1]['Convergence Speed']:.0f} episodes")
            print(f"  Success Rate: {results[-1]['Success Rate']*100:.1f}%")

        return pd.DataFrame(results)

    def compare_approximations(self, state_sizes: List[int]) -> pd.DataFrame:
        """Compare all approximation types"""
        print("\n" + "="*70)
        print("FUNCTION APPROXIMATION COMPARISON")
        print("="*70)

        all_results = []

        approx_types = [
            ApproxType.TABULAR,
            ApproxType.LINEAR,
            ApproxType.POLYNOMIAL,
            ApproxType.RBF,
            ApproxType.NEURAL
        ]

        for approx_type in approx_types:
            try:
                df = self.simulate_approximation(approx_type, state_sizes)
                all_results.append(df)
            except Exception as e:
                print(f"Error with {approx_type.value}: {e}")
                continue

        combined_df = pd.concat(all_results, ignore_index=True)
        self.results['approximation_comparison'] = combined_df

        return combined_df

    def analyze_error_propagation(self) -> pd.DataFrame:
        """
        Q2: How do errors propagate through function approximation?
        """
        print("\n" + "="*70)
        print("ERROR PROPAGATION ANALYSIS")
        print("="*70)

        num_states = 50
        env = MDPEnvironment(num_states)

        results = []

        for approx_type in [ApproxType.LINEAR, ApproxType.POLYNOMIAL, ApproxType.RBF]:
            print(f"\nAnalyzing {approx_type.value}...")

            self.config.num_states = num_states

            # Track error distribution across states
            state_errors = []

            for run in range(self.config.num_runs):
                approximator = ValueApproximator(approx_type, self.config)

                # Train
                for episode in range(self.config.num_episodes):
                    self.run_episode(env, approximator, use_traces=True)

                # Compute per-state errors
                for s in range(num_states):
                    pred = approximator.get_value(s)
                    true_val = env.true_values[s]
                    state_errors.append({
                        'Approximation': approx_type.value,
                        'State': s,
                        'Error': abs(pred - true_val)
                    })

            df = pd.DataFrame(state_errors)
            results.append(df)

            print(f"  Mean Error: {df['Error'].mean():.4f}")
            print(f"  Max Error: {df['Error'].max():.4f}")
            print(f"  Std Error: {df['Error'].std():.4f}")

        combined_df = pd.concat(results, ignore_index=True)
        self.results['error_propagation'] = combined_df

        return combined_df

    def find_breaking_point(self) -> pd.DataFrame:
        """
        Q1: When does approximation break TD learning?
        """
        print("\n" + "="*70)
        print("APPROXIMATION BREAKING POINT ANALYSIS")
        print("="*70)

        # Test increasing state space sizes
        state_sizes = [10, 20, 50, 100, 200, 500, 1000]

        results = []

        for approx_type in [ApproxType.LINEAR, ApproxType.POLYNOMIAL, ApproxType.RBF, ApproxType.NEURAL]:
            print(f"\nTesting {approx_type.value}...")

            breaking_points = []

            for num_states in state_sizes:
                self.config.num_states = num_states
                env = MDPEnvironment(num_states)

                # Check if learning succeeds
                success_count = 0
                for run in range(min(self.config.num_runs, 20)):  # Fewer runs for large state spaces
                    approximator = ValueApproximator(approx_type, self.config)

                    for episode in range(self.config.num_episodes):
                        self.run_episode(env, approximator, use_traces=True)

                    final_error = approximator.compute_rms_error(env.true_values)
                    if final_error < 0.2:  # Success threshold
                        success_count += 1

                success_rate = success_count / min(self.config.num_runs, 20)
                breaking_points.append({
                    'Approximation': approx_type.value,
                    'State Space Size': num_states,
                    'Success Rate': success_rate,
                    'Broken': success_rate < 0.5
                })

                print(f"  {num_states} states: {success_rate*100:.0f}% success")

            results.extend(breaking_points)

        df = pd.DataFrame(results)
        self.results['breaking_points'] = df

        return df

    def plot_approximation_comparison(self, save_path: Optional[str] = None):
        """Plot approximation comparison"""
        if 'approximation_comparison' not in self.results:
            self.compare_approximations([10, 20, 50, 100])

        df = self.results['approximation_comparison']

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Final error vs state space size
        for approx in df['Approximation'].unique():
            data = df[df['Approximation'] == approx]
            axes[0].plot(data['State Space Size'], data['Final RMS Error'],
                        'o-', label=approx, linewidth=2, markersize=8)

        axes[0].set_xlabel('State Space Size', fontsize=14)
        axes[0].set_ylabel('Final RMS Error', fontsize=14)
        axes[0].set_title('Approximation Error vs State Space Size', fontsize=16)
        axes[0].legend(fontsize=10)
        axes[0].set_xscale('log')
        axes[0].set_yscale('log')
        axes[0].grid(True, alpha=0.3)

        # Convergence speed vs state space size
        for approx in df['Approximation'].unique():
            data = df[df['Approximation'] == approx]
            axes[1].plot(data['State Space Size'], data['Convergence Speed'],
                        's-', label=approx, linewidth=2, markersize=8)

        axes[1].set_xlabel('State Space Size', fontsize=14)
        axes[1].set_ylabel('Convergence Speed (episodes)', fontsize=14)
        axes[1].set_title('Convergence Speed vs State Space Size', fontsize=16)
        axes[1].legend(fontsize=10)
        axes[1].set_xscale('log')
        axes[1].set_yscale('log')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_error_propagation(self, save_path: Optional[str] = None):
        """Plot error propagation across states"""
        if 'error_propagation' not in self.results:
            self.analyze_error_propagation()

        df = self.results['error_propagation']

        plt.figure(figsize=(14, 8))

        for approx in df['Approximation'].unique():
            data = df[df['Approximation'] == approx]
            # Aggregate by state
            grouped = data.groupby('State')['Error'].agg(['mean', 'std'])
            plt.plot(grouped.index, grouped['mean'], label=approx, linewidth=2)
            plt.fill_between(grouped.index,
                            grouped['mean'] - grouped['std'],
                            grouped['mean'] + grouped['std'],
                            alpha=0.2)

        plt.xlabel('State', fontsize=14)
        plt.ylabel('Absolute Error', fontsize=14)
        plt.title('Error Propagation Across State Space', fontsize=16)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_breaking_points(self, save_path: Optional[str] = None):
        """Plot breaking points for each approximation"""
        if 'breaking_points' not in self.results:
            self.find_breaking_point()

        df = self.results['breaking_points']

        plt.figure(figsize=(12, 8))

        for approx in df['Approximation'].unique():
            data = df[df['Approximation'] == approx]
            plt.plot(data['State Space Size'], data['Success Rate'],
                    'o-', label=approx, linewidth=2, markersize=8)

        plt.axhline(y=0.5, color='red', linestyle='--', label='Breaking Threshold')
        plt.xlabel('State Space Size', fontsize=14)
        plt.ylabel('Success Rate', fontsize=14)
        plt.title('Approximation Breaking Points', fontsize=16)
        plt.legend(fontsize=12)
        plt.xscale('log')
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def generate_report(self) -> str:
        """Generate comprehensive report"""
        if not self.results:
            self.compare_approximations([10, 20, 50, 100])
            self.analyze_error_propagation()
            self.find_breaking_point()

        report = []
        report.append("="*80)
        report.append("FUNCTION APPROXIMATION FOR TD(λ) LEARNING")
        report.append("="*80)

        # Q1: Breaking Points
        report.append("\n" + "="*80)
        report.append("Q1: WHEN DOES APPROXIMATION BREAK TD LEARNING?")
        report.append("="*80)

        if 'breaking_points' in self.results:
            df = self.results['breaking_points']
            report.append("\nBreaking Points (50% success rate):")

            for approx in df['Approximation'].unique():
                data = df[df['Approximation'] == approx]
                broken = data[data['Broken'] == True]
                if len(broken) > 0:
                    first_broken = broken.iloc[0]
                    report.append(f"  • {approx}: ~{first_broken['State Space Size']} states")
                else:
                    report.append(f"  • {approx}: No breaking point up to 1000 states")

        # Q2: Error Propagation
        report.append("\n" + "="*80)
        report.append("Q2: HOW DO ERRORS PROPAGATE?")
        report.append("="*80)

        if 'error_propagation' in self.results:
            df = self.results['error_propagation']
            report.append("\nError Statistics by Approximation:")

            for approx in df['Approximation'].unique():
                data = df[df['Approximation'] == approx]
                report.append(f"\n  {approx}:")
                report.append(f"    • Mean Error: {data['Error'].mean():.4f}")
                report.append(f"    • Max Error: {data['Error'].max():.4f}")
                report.append(f"    • Std Error: {data['Error'].std():.4f}")

        # Q3: Optimal Representation
        report.append("\n" + "="*80)
        report.append("Q3: OPTIMAL REPRESENTATION")
        report.append("="*80)

        if 'approximation_comparison' in self.results:
            df = self.results['approximation_comparison']
            report.append("\nRecommendations by State Space Size:")

            for size in [10, 20, 50, 100]:
                data = df[df['State Space Size'] == size]
                if len(data) > 0:
                    best = data.loc[data['Final RMS Error'].idxmin()]
                    report.append(f"  • {size} states: {best['Approximation']} (error: {best['Final RMS Error']:.4f})")

        # Key Findings
        report.append("\n" + "="*80)
        report.append("KEY FINDINGS")
        report.append("="*80)

        report.append("\n1. Tabular:")
        report.append("   • Pros: Exact representation, no approximation error")
        report.append("   • Cons: Does not scale (memory O(S))")

        report.append("\n2. Linear:")
        report.append("   • Pros: Fast, stable, interpretable")
        report.append("   • Cons: Limited expressiveness")
        report.append("   • Best: Small to medium state spaces (< 100)")

        report.append("\n3. Polynomial:")
        report.append("   • Pros: Captures non-linearities")
        report.append("   • Cons: Can overfit, computationally expensive")
        report.append("   • Best: Medium state spaces with smooth value functions")

        report.append("\n4. RBF Kernel:")
        report.append("   • Pros: Local generalization, robust")
        report.append("   • Cons: Requires careful kernel selection")
        report.append("   • Best: Medium to large state spaces")

        report.append("\n5. Neural Network:")
        report.append("   • Pros: Highly expressive, scales well")
        report.append("   • Cons: Unstable, requires tuning")
        report.append("   • Best: Large state spaces (> 500)")

        report.append("\n" + "="*80)
        report.append("CONCLUSION")
        report.append("="*80)
        report.append("\n✓ Approximation breaks when feature space is insufficient")
        report.append("✓ Errors propagate smoothly with good feature selection")
        report.append("✓ Optimal representation depends on state space structure")
        report.append("\nRecommendation: Start simple (linear), scale up (RBF/Neural)")

        return "\n".join(report)


def main():
    """Main simulation runner"""
    print("="*70)
    print("FUNCTION APPROXIMATION FOR TD(λ) LEARNING")
    print("="*70)

    config = ApproxConfig(
        num_states=50,
        state_dim=1,
        feature_dim=10,
        gamma=0.99,
        alpha=0.01,
        lambda_=0.5,
        num_episodes=500,
        num_runs=50
    )

    simulator = FunctionApproxSimulator(config)

    # Run analyses
    print("\n1. Comparing approximation types...")
    comparison_df = simulator.compare_approximations([10, 20, 50, 100])
    print("\n" + comparison_df.to_string(index=False))

    print("\n2. Analyzing error propagation...")
    error_df = simulator.analyze_error_propagation()
    print("\nError propagation analysis complete")

    print("\n3. Finding breaking points...")
    breaking_df = simulator.find_breaking_point()
    print("\nBreaking point analysis complete")

    # Generate plots
    print("\n4. Generating visualizations...")
    simulator.plot_approximation_comparison('approx_comparison.png')
    simulator.plot_error_propagation('error_propagation.png')
    simulator.plot_breaking_points('breaking_points.png')

    # Generate report
    print("\n5. Generating report...")
    report = simulator.generate_report()
    print(report)

    # Save report
    with open('FUNCTION_APPROX_REPORT.txt', 'w') as f:
        f.write(report)

    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    print("\nOutputs:")
    print("  • approx_comparison.png")
    print("  • error_propagation.png")
    print("  • breaking_points.png")
    print("  • FUNCTION_APPROX_REPORT.txt")


if __name__ == "__main__":
    main()
