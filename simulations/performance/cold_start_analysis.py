"""
POLLN Cold Start Analysis - META Tile Optimization

Validates H2: META tiles cold start < 100ms with signal-based differentiation

This simulation models:
- T_cold = T_init + T_differentiation (cold start time equation)
- Signal-based caching impact on cold start
- Pre-differentiation strategies
- Statistical validation of sub-100ms target
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import time
from datetime import datetime
from pathlib import Path

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# Cold start SLA target
COLD_START_TARGET_MS = 100  # Target cold start time in milliseconds

# META tile differentiation costs (based on TypeScript implementation)
T_INIT_BASE_MS = 20  # Base initialization time
T_DIFFERENTIATION_BASE_MS = 50  # Base differentiation time

# Agent type complexity multipliers
AGENT_COMPLEXITY = {
    'task': 1.0,      # Simplest
    'role': 1.5,      # Medium
    'core': 2.0,      # Most complex
}

# Signal cache effectiveness
CACHE_HIT_RATE = 0.85  # 85% cache hit with signal-based caching
CACHE_SPEEDUP = 0.6     # 60% faster with cache hit

# Simulation parameters
NUM_TRIALS = 1000
CONFIDENCE_LEVEL = 0.95
SEED = 42

# ============================================================================
# MATHEMATICAL MODELS
# ============================================================================

def cold_start_time(
    agent_type: str,
    has_cache: bool,
    is_pre_differentiated: bool,
    signal_strength: float = 0.7,
    complexity: float = 1.0
) -> float:
    """
    Compute cold start time using T_cold = T_init + T_differentiation.

    Args:
        agent_type: Type of agent ('task', 'role', 'core')
        has_cache: Whether signal cache is available
        is_pre_differentiated: Whether agent is pre-differentiated
        signal_strength: Signal strength (0-1)
        complexity: Request complexity multiplier

    Returns:
        Cold start time in milliseconds
    """
    # T_init: Base initialization
    t_init = T_INIT_BASE_MS * complexity

    # T_differentiation: Time to differentiate
    if is_pre_differentiated:
        # Already differentiated, no differentiation cost
        t_differentiation = 0
    else:
        # Base differentiation cost
        base_diff = T_DIFFERENTIATION_BASE_MS * AGENT_COMPLEXITY[agent_type]

        # Signal strength reduces differentiation time
        # Stronger signal = faster differentiation
        signal_bonus = (1 - signal_strength) * base_diff

        t_differentiation = base_diff + signal_bonus

        # Cache hit speeds up differentiation
        if has_cache and np.random.random() < CACHE_HIT_RATE:
            t_differentiation *= (1 - CACHE_SPEEDUP)

    return t_init + t_differentiation


def compute_confidence_interval(
    data: np.ndarray,
    confidence: float = 0.95
) -> Tuple[float, float, float]:
    """Compute confidence interval for sample mean."""
    n = len(data)
    if n < 2:
        return (np.mean(data), np.mean(data), np.mean(data))

    mean = np.mean(data)
    std_err = stats.sem(data)
    h = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)

    return (mean, mean - h, mean + h)


# ============================================================================
# META TILE STATE MODEL
# ============================================================================

class MetaTileState(Enum):
    """META tile differentiation states."""
    UNDIFFERENTIATED = "undifferentiated"
    DIFFERENTIATING = "differentiating"
    DIFFERENTIATED = "differentiated"


@dataclass
class MetaTile:
    """Represents a META tile with cold start tracking."""
    id: str
    state: MetaTileState = MetaTileState.UNDIFFERENTIATED
    agent_type: Optional[str] = None
    has_cache: bool = False
    signal_strength: float = 0.0
    cold_start_time_ms: float = 0.0

    def differentiate(
        self,
        target_type: str,
        signal_strength: float,
        use_cache: bool
    ) -> float:
        """
        Differentiate META tile.

        Returns:
            Time taken in milliseconds
        """
        start_time = time.time()

        # Update state
        self.state = MetaTileState.DIFFERENTIATING
        self.agent_type = target_type
        self.signal_strength = signal_strength
        self.has_cache = use_cache

        # Compute cold start time
        self.cold_start_time_ms = cold_start_time(
            agent_type=target_type,
            has_cache=use_cache,
            is_pre_differentiated=False,
            signal_strength=signal_strength
        )

        self.state = MetaTileState.DIFFERENTIATED

        return self.cold_start_time_ms


@dataclass
class SignalCache:
    """Signal-based cache for META tiles."""
    cache_size: int = 100
    entries: Dict[str, Dict] = field(default_factory=dict)

    def lookup(self, signal_pattern: str) -> Optional[Dict]:
        """Lookup signal pattern in cache."""
        return self.entries.get(signal_pattern)

    def store(self, signal_pattern: str, agent_type: str, metadata: Dict):
        """Store signal pattern in cache."""
        if len(self.entries) >= self.cache_size:
            # Evict oldest entry
            oldest_key = next(iter(self.entries))
            del self.entries[oldest_key]

        self.entries[signal_pattern] = {
            'agent_type': agent_type,
            'timestamp': time.time(),
            **metadata
        }


# ============================================================================
# CACHING STRATEGIES
# ============================================================================

class CachingStrategy(Enum):
    """Different caching strategies for comparison."""
    NO_CACHE = "no_cache"
    SIGNAL_CACHE = "signal_cache"
    PRE_DIFFERENTIATED = "pre_differentiated"


def apply_caching_strategy(
    strategy: CachingStrategy,
    signal_pattern: str,
    cache: SignalCache
) -> Tuple[bool, bool]:
    """
    Apply caching strategy.

    Returns:
        (has_cache, is_pre_differentiated)
    """
    if strategy == CachingStrategy.NO_CACHE:
        return (False, False)

    elif strategy == CachingStrategy.SIGNAL_CACHE:
        # Check cache
        cached = cache.lookup(signal_pattern)
        return (cached is not None, False)

    elif strategy == CachingStrategy.PRE_DIFFERENTIATED:
        # Assume pre-differentiated
        return (False, True)

    return (False, False)


# ============================================================================
# SIMULATION ENGINE
# ============================================================================

class ColdStartSimulation:
    """
    Simulates META tile cold start performance.

    Models:
    - Different agent types (task, role, core)
    - Signal-based caching
    - Pre-differentiation
    - Various signal strengths
    """

    def __init__(
        self,
        num_tiles: int = 20,
        cache_size: int = 100,
        seed: int = SEED
    ):
        self.num_tiles = num_tiles
        self.cache = SignalCache(cache_size=cache_size)
        self.seed = seed
        np.random.seed(seed)

        # Initialize META tiles
        self.meta_tiles: List[MetaTile] = [
            MetaTile(id=f"meta-{i}") for i in range(num_tiles)
        ]

    def simulate_cold_start(
        self,
        agent_type: str,
        signal_strength: float,
        strategy: CachingStrategy,
        num_requests: int = 1000
    ) -> Dict[str, np.ndarray]:
        """
        Simulate cold start for multiple requests.

        Returns:
            Dictionary with latency arrays and metadata
        """
        cold_start_times = []
        cache_hits = []
        pre_differentiated = []

        for i in range(num_requests):
            # Generate signal pattern
            signal_pattern = f"{agent_type}-{signal_strength:.2f}"

            # Apply caching strategy
            has_cache, is_pre_diff = apply_caching_strategy(
                strategy, signal_pattern, self.cache
            )

            # Get undifferentiated tile
            tile = next(
                (t for t in self.meta_tiles
                 if t.state == MetaTileState.UNDIFFERENTIATED),
                None
            )

            if tile is None:
                # Reset a tile
                tile = self.meta_tiles[0]
                tile.state = MetaTileState.UNDIFFERENTIATED

            # Differentiate
            start = time.time()
            cold_start_ms = tile.differentiate(
                target_type=agent_type,
                signal_strength=signal_strength,
                use_cache=has_cache
            )
            end = time.time()

            # Store in cache if applicable
            if strategy == CachingStrategy.SIGNAL_CACHE and not has_cache:
                self.cache.store(
                    signal_pattern,
                    agent_type,
                    {'cold_start_time_ms': cold_start_ms}
                )

            cold_start_times.append(cold_start_ms)
            cache_hits.append(1 if has_cache else 0)
            pre_differentiated.append(1 if is_pre_diff else 0)

        return {
            'cold_start_times': np.array(cold_start_times),
            'cache_hits': np.array(cache_hits),
            'pre_differentiated': np.array(pre_differentiated),
        }


def run_cold_start_experiment(
    strategies: List[CachingStrategy] = None,
    agent_types: List[str] = None,
    signal_strengths: List[float] = None,
    num_trials: int = NUM_TRIALS,
    seed: int = SEED
) -> pd.DataFrame:
    """
    Run comprehensive cold start experiment.

    Returns:
        DataFrame with all results
    """
    if strategies is None:
        strategies = list(CachingStrategy)
    if agent_types is None:
        agent_types = ['task', 'role', 'core']
    if signal_strengths is None:
        signal_strengths = [0.3, 0.5, 0.7, 0.9]

    results = []

    for strategy in strategies:
        for agent_type in agent_types:
            for signal_strength in signal_strengths:
                for trial in range(num_trials):
                    trial_seed = seed + trial

                    # Run simulation
                    sim = ColdStartSimulation(num_tiles=20, seed=trial_seed)
                    data = sim.simulate_cold_start(
                        agent_type=agent_type,
                        signal_strength=signal_strength,
                        strategy=strategy,
                        num_requests=100
                    )

                    # Compute statistics
                    cold_starts = data['cold_start_times']

                    results.append({
                        'trial': trial,
                        'strategy': strategy.value,
                        'agent_type': agent_type,
                        'signal_strength': signal_strength,
                        'mean_cold_start_ms': np.mean(cold_starts),
                        'std_cold_start_ms': np.std(cold_starts),
                        'p50_cold_start_ms': np.percentile(cold_starts, 50),
                        'p95_cold_start_ms': np.percentile(cold_starts, 95),
                        'p99_cold_start_ms': np.percentile(cold_starts, 99),
                        'cache_hit_rate': np.mean(data['cache_hits']),
                        'compliant': np.mean(cold_starts) < COLD_START_TARGET_MS,
                    })

    return pd.DataFrame(results)


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_hypothesis_h2(results: pd.DataFrame) -> Dict:
    """
    Analyze H2: META tiles cold start < 100ms with signal-based differentiation.

    Returns:
        Dictionary with hypothesis validation results
    """
    # Filter for signal cache strategy (most realistic)
    signal_cache_results = results[results['strategy'] == 'signal_cache']

    # Overall compliance
    overall_compliant = signal_cache_results['compliant'].all()

    # By agent type
    by_agent_type = {}
    for agent_type in ['task', 'role', 'core']:
        agent_results = signal_cache_results[
            signal_cache_results['agent_type'] == agent_type
        ]
        by_agent_type[agent_type] = {
            'compliant': agent_results['compliant'].all(),
            'mean_cold_start_ms': float(agent_results['mean_cold_start_ms'].mean()),
            'p95_cold_start_ms': float(agent_results['p95_cold_start_ms'].mean()),
        }

    # By signal strength
    by_signal_strength = {}
    for strength in sorted(signal_cache_results['signal_strength'].unique()):
        strength_results = signal_cache_results[
            signal_cache_results['signal_strength'] == strength
        ]
        by_signal_strength[float(strength)] = {
            'compliant': strength_results['compliant'].all(),
            'mean_cold_start_ms': float(strength_results['mean_cold_start_ms'].mean()),
            'p95_cold_start_ms': float(strength_results['p95_cold_start_ms'].mean()),
        }

    # Strategy comparison
    strategy_comparison = {}
    for strategy in results['strategy'].unique():
        strategy_results = results[results['strategy'] == strategy]
        strategy_comparison[strategy] = {
            'mean_cold_start_ms': float(strategy_results['mean_cold_start_ms'].mean()),
            'p95_cold_start_ms': float(strategy_results['p95_cold_start_ms'].mean()),
            'compliant': strategy_results['compliant'].all(),
        }

    return {
        'hypothesis': 'H2: META tiles cold start < 100ms with signal-based differentiation',
        'target_ms': COLD_START_TARGET_MS,
        'overall_compliant': overall_compliant,
        'by_agent_type': by_agent_type,
        'by_signal_strength': by_signal_strength,
        'strategy_comparison': strategy_comparison,
    }


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_cold_start_results(
    results: pd.DataFrame,
    analysis: Dict,
    output_dir: Path
):
    """Generate publication-quality plots for cold start results."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Cold start time by strategy
    fig, ax = plt.subplots(figsize=(12, 6))

    strategies = results['strategy'].unique()
    x = np.arange(len(strategies))
    width = 0.35

    means = [results[results['strategy'] == s]['mean_cold_start_ms'].mean()
             for s in strategies]
    stds = [results[results['strategy'] == s]['std_cold_start_ms'].mean()
            for s in strategies]

    bars = ax.bar(x, means, width, yerr=stds, capsize=5, alpha=0.7)

    # Color bars by compliance
    for i, bar in enumerate(bars):
        if means[i] < COLD_START_TARGET_MS:
            bar.set_color('green')
        else:
            bar.set_color('red')

    ax.axhline(y=COLD_START_TARGET_MS, color='red', linestyle='--',
               label=f'SLA Target ({COLD_START_TARGET_MS}ms)')

    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies],
                       rotation=45, ha='right')
    ax.set_ylabel('Cold Start Time (ms)')
    ax.set_title('META Tile Cold Start Time by Caching Strategy')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'cold_start_by_strategy.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Cold start by agent type (signal cache only)
    fig, ax = plt.subplots(figsize=(12, 6))

    signal_cache = results[results['strategy'] == 'signal_cache']

    agent_types = ['task', 'role', 'core']
    x = np.arange(len(agent_types))

    means = [signal_cache[signal_cache['agent_type'] == t]['mean_cold_start_ms'].mean()
             for t in agent_types]
    stds = [signal_cache[signal_cache['agent_type'] == t]['std_cold_start_ms'].mean()
            for t in agent_types]

    bars = ax.bar(x, means, width, yerr=stds, capsize=5, alpha=0.7)

    # Color bars by compliance
    for i, bar in enumerate(bars):
        if means[i] < COLD_START_TARGET_MS:
            bar.set_color('green')
        else:
            bar.set_color('red')

    ax.axhline(y=COLD_START_TARGET_MS, color='red', linestyle='--',
               label=f'SLA Target ({COLD_START_TARGET_MS}ms)')

    ax.set_xticks(x)
    ax.set_xticklabels([t.title() for t in agent_types])
    ax.set_ylabel('Cold Start Time (ms)')
    ax.set_title('META Tile Cold Start Time by Agent Type (Signal Cache)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'cold_start_by_agent_type.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Cold start vs signal strength
    fig, ax = plt.subplots(figsize=(12, 6))

    signal_cache = results[results['strategy'] == 'signal_cache']

    for agent_type in agent_types:
        agent_data = signal_cache[signal_cache['agent_type'] == agent_type]
        strengths = sorted(agent_data['signal_strength'].unique())
        means = [agent_data[agent_data['signal_strength'] == s]['mean_cold_start_ms'].mean()
                 for s in strengths]
        stds = [agent_data[agent_data['signal_strength'] == s]['std_cold_start_ms'].mean()
                for s in strengths]

        ax.errorbar(strengths, means, yerr=stds, marker='o',
                   label=agent_type.title(), capsize=5, linewidth=2)

    ax.axhline(y=COLD_START_TARGET_MS, color='red', linestyle='--',
               label=f'SLA Target ({COLD_START_TARGET_MS}ms)')

    ax.set_xlabel('Signal Strength')
    ax.set_ylabel('Cold Start Time (ms)')
    ax.set_title('META Tile Cold Start Time vs Signal Strength')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'cold_start_vs_signal.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Strategy comparison heatmap
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create pivot table
    pivot_data = results.pivot_table(
        values='mean_cold_start_ms',
        index='strategy',
        columns='agent_type',
        aggfunc='mean'
    )

    sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Cold Start Time (ms)'},
                ax=ax, vmin=0, vmax=COLD_START_TARGET_MS * 1.5)

    ax.set_title('META Tile Cold Start Time by Strategy and Agent Type')
    ax.set_xlabel('Agent Type')
    ax.set_ylabel('Caching Strategy')

    plt.tight_layout()
    plt.savefig(output_dir / 'cold_start_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. CDF of cold start times
    fig, ax = plt.subplots(figsize=(12, 6))

    for strategy in strategies:
        strategy_data = results[results['strategy'] == strategy.value]
        all_times = []

        for _, row in strategy_data.iterrows():
            # Generate sample times based on mean and std
            times = np.random.normal(
                loc=row['mean_cold_start_ms'],
                scale=row['std_cold_start_ms'],
                size=100
            )
            all_times.extend(times)

        # Compute CDF
        sorted_times = np.sort(all_times)
        cdf = np.arange(1, len(sorted_times) + 1) / len(sorted_times)

        ax.plot(sorted_times, cdf, label=strategy.value.replace('_', ' ').title(),
               linewidth=2)

    ax.axvline(x=COLD_START_TARGET_MS, color='red', linestyle='--',
               label=f'SLA Target ({COLD_START_TARGET_MS}ms)')

    ax.set_xlabel('Cold Start Time (ms)')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('CDF of META Tile Cold Start Times')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'cold_start_cdf.png', dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    """Run comprehensive cold start analysis experiment."""

    print("=" * 80)
    print("POLLN Cold Start Analysis - META Tile Optimization")
    print("=" * 80)

    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run experiment
    print("\nRunning cold start simulations...")
    results = run_cold_start_experiment(
        strategies=list(CachingStrategy),
        agent_types=['task', 'role', 'core'],
        signal_strengths=[0.3, 0.5, 0.7, 0.9],
        num_trials=100,
        seed=SEED
    )

    # Save results
    results.to_csv(output_dir / 'cold_start_results.csv', index=False)

    # Analyze H2
    print("\nAnalyzing H2...")
    analysis = analyze_hypothesis_h2(results)

    # Save analysis
    with open(output_dir / 'cold_start_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    # Generate plots
    print("\nGenerating plots...")
    plot_cold_start_results(results, analysis, output_dir)

    # Generate summary report
    report_path = output_dir / 'cold_start_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("POLLN COLD START ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"SLA Target: < {COLD_START_TARGET_MS}ms\n\n")

        f.write("HYPOTHESIS H2\n")
        f.write("-" * 80 + "\n")
        f.write(f"{analysis['hypothesis']}\n")
        f.write(f"Target: {analysis['target_ms']}ms\n")
        f.write(f"Overall Compliant: {analysis['overall_compliant']}\n\n")

        f.write("BY AGENT TYPE\n")
        f.write("-" * 80 + "\n")
        for agent_type, data in analysis['by_agent_type'].items():
            f.write(f"\n{agent_type.upper()}\n")
            f.write(f"  Compliant: {data['compliant']}\n")
            f.write(f"  Mean Cold Start: {data['mean_cold_start_ms']:.2f}ms\n")
            f.write(f"  p95 Cold Start: {data['p95_cold_start_ms']:.2f}ms\n")

        f.write("\nSTRATEGY COMPARISON\n")
        f.write("-" * 80 + "\n")
        for strategy, data in analysis['strategy_comparison'].items():
            f.write(f"\n{strategy.upper().replace('_', ' ')}\n")
            f.write(f"  Mean Cold Start: {data['mean_cold_start_ms']:.2f}ms\n")
            f.write(f"  p95 Cold Start: {data['p95_cold_start_ms']:.2f}ms\n")
            f.write(f"  Compliant: {data['compliant']}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("-" * 80 + "\n")

        if analysis['overall_compliant']:
            f.write("✓ H2 VALIDATED: META tiles cold start < 100ms with signal-based caching\n")
            f.write(f"  - Signal cache achieves {analysis['strategy_comparison']['signal_cache']['mean_cold_start_ms']:.2f}ms "
                   f"mean cold start\n")
            f.write(f"  - This represents a {(1 - analysis['strategy_comparison']['signal_cache']['mean_cold_start_ms'] / analysis['strategy_comparison']['no_cache']['mean_cold_start_ms']) * 100:.1f}% "
                   f"improvement over no cache\n")
        else:
            f.write("✗ H2 NOT VALIDATED: META tiles do not meet 100ms cold start target\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nResults saved to {output_dir}")
    print(f"Summary report: {report_path}")

    return results, analysis


if __name__ == '__main__':
    main()
