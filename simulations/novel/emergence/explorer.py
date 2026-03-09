"""
Parameter Space Explorer for Emergent Phenomena Discovery

Performs systematic exploration of POLLN's parameter space to identify
regions exhibiting novel emergent behaviors. Uses multiple exploration
strategies including adaptive sampling and rare event detection.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
import warnings
warnings.filterwarnings('ignore')


class ExplorationStrategy(Enum):
    """Exploration strategies"""
    GRID = "grid"  # Systematic grid search
    RANDOM = "random"  # Random sampling
    BAYESIAN = "bayesian"  # Bayesian optimization
    ADAPTIVE = "adaptive"  # Adaptive sampling based on results
    RARE_EVENT = "rare_event"  # Importance sampling for rare events
    MULTI_OBJECTIVE = "multi_objective"  # Pareto frontier exploration
    GRADIENT_ASCENT = "gradient_ascent"  # Follow emergence gradients
    ENTROPY_MAX = "entropy_max"  # Maximize information gain


@dataclass
class ParameterSpace:
    """Definition of parameter space to explore"""
    name: str
    dimensions: Dict[str, Tuple[float, float]]  # param_name: (min, max)
    log_scale: List[str] = field(default_factory=list)  # params to sample in log space
    constraints: Optional[List[Callable[[Dict[str, float]], bool]]] = None

    def sample(self, n_samples: int, strategy: ExplorationStrategy = ExplorationStrategy.RANDOM,
               seed: Optional[int] = None) -> List[Dict[str, float]]:
        """Sample parameter configurations"""
        if seed is not None:
            np.random.seed(seed)

        samples = []

        if strategy == ExplorationStrategy.GRID:
            samples = self._grid_sample(n_samples)
        elif strategy == ExplorationStrategy.RANDOM:
            samples = self._random_sample(n_samples)
        elif strategy == ExplorationStrategy.BAYESIAN:
            samples = self._bayesian_sample(n_samples)
        else:
            samples = self._random_sample(n_samples)

        # Filter by constraints
        if self.constraints:
            samples = [s for s in samples
                      if all(constraint(s) for constraint in self.constraints)]

        return samples

    def _grid_sample(self, n_samples: int) -> List[Dict[str, float]]:
        """Uniform grid sampling"""
        samples = []
        samples_per_dim = max(2, int(n_samples ** (1 / len(self.dimensions))))

        # Create grid for each dimension
        grids = {}
        for param, (min_val, max_val) in self.dimensions.items():
            if param in self.log_scale:
                grids[param] = np.logspace(np.log10(min_val), np.log10(max_val), samples_per_dim)
            else:
                grids[param] = np.linspace(min_val, max_val, samples_per_dim)

        # Generate all combinations
        import itertools
        for combo in itertools.product(*grids.values()):
            sample = dict(zip(self.dimensions.keys(), combo))
            samples.append(sample)
            if len(samples) >= n_samples:
                break

        return samples[:n_samples]

    def _random_sample(self, n_samples: int) -> List[Dict[str, float]]:
        """Random uniform sampling"""
        samples = []
        for _ in range(n_samples):
            sample = {}
            for param, (min_val, max_val) in self.dimensions.items():
                if param in self.log_scale:
                    sample[param] = 10 ** np.random.uniform(np.log10(min_val), np.log10(max_val))
                else:
                    sample[param] = np.random.uniform(min_val, max_val)
            samples.append(sample)
        return samples

    def _bayesian_sample(self, n_samples: int) -> List[Dict[str, float]]:
        """Bayesian optimization sampling (requires objective function)"""
        # Initial random sample
        n_initial = min(20, n_samples // 2)
        samples = self._random_sample(n_initial)

        # Would need objective function to continue
        # Return initial samples for now
        return samples


@dataclass
class EmergenceMetric:
    """Metric for quantifying emergence"""
    name: str
    description: str
    compute: Callable[[Any], float]
    higher_is_better: bool = True
    target_range: Optional[Tuple[float, float]] = None


class EmergenceExplorer:
    """
    Advanced parameter space explorer for emergent phenomena

    Explores POLLN parameter space to discover configurations exhibiting
    novel emergent behaviors. Uses multiple strategies and adaptive sampling.
    """

    def __init__(self, parameter_space: ParameterSpace,
                 emergence_metrics: List[EmergenceMetric],
                 output_dir: str = "./exploration_results"):
        self.parameter_space = parameter_space
        self.emergence_metrics = emergence_metrics
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.exploration_history = []
        self.best_configurations = {metric.name: [] for metric in emergence_metrics}

    def explore(self,
                n_iterations: int = 100,
                strategy: ExplorationStrategy = ExplorationStrategy.ADAPTIVE,
                simulation_fn: Optional[Callable] = None,
                batch_size: int = 10) -> Dict[str, Any]:
        """
        Run exploration expedition

        Args:
            n_iterations: Number of exploration iterations
            strategy: Exploration strategy to use
            simulation_fn: Function to run POLLN simulation with given params
            batch_size: Number of configs to test per batch

        Returns:
            Exploration results with discovered phenomena
        """
        print(f"🔬 Starting emergence exploration with {strategy.value} strategy")
        print(f"   Parameters: {len(self.parameter_space.dimensions)} dimensions")
        print(f"   Metrics: {[m.name for m in self.emergence_metrics]}")
        print(f"   Iterations: {n_iterations}")

        results = {
            "strategy": strategy.value,
            "iterations": n_iterations,
            "discoveries": [],
            "parameter_space": self.parameter_space.name,
            "best_by_metric": {metric.name: None for metric in self.emergence_metrics}
        }

        # Adaptive sampling strategy
        if strategy == ExplorationStrategy.ADAPTIVE:
            results = self._adaptive_explore(n_iterations, simulation_fn, batch_size)
        elif strategy == ExplorationStrategy.RARE_EVENT:
            results = self._rare_event_explore(n_iterations, simulation_fn, batch_size)
        elif strategy == ExplorationStrategy.MULTI_OBJECTIVE:
            results = self._multi_objective_explore(n_iterations, simulation_fn, batch_size)
        elif strategy == ExplorationStrategy.ENTROPY_MAX:
            results = self._entropy_explore(n_iterations, simulation_fn, batch_size)
        else:
            results = self._standard_explore(n_iterations, strategy, simulation_fn, batch_size)

        # Save results
        self._save_results(results)

        return results

    def _standard_explore(self, n_iterations: int, strategy: ExplorationStrategy,
                         simulation_fn: Optional[Callable], batch_size: int) -> Dict[str, Any]:
        """Standard exploration (grid, random, or bayesian)"""
        results = {
            "strategy": strategy.value,
            "iterations": n_iterations,
            "discoveries": [],
            "all_evaluations": []
        }

        # Sample configurations
        configs = self.parameter_space.sample(n_iterations, strategy)

        # Evaluate configurations
        for i, config in enumerate(configs):
            print(f"  Evaluating configuration {i+1}/{len(configs)}")

            # Run simulation if provided
            if simulation_fn:
                sim_result = simulation_fn(config)
            else:
                sim_result = self._mock_simulation(config)

            # Compute emergence metrics
            metrics = {}
            for metric in self.emergence_metrics:
                try:
                    metrics[metric.name] = metric.compute(sim_result)
                except Exception as e:
                    metrics[metric.name] = 0.0

            # Record results
            evaluation = {
                "config": config,
                "metrics": metrics,
                "raw_result": sim_result
            }
            results["all_evaluations"].append(evaluation)

            # Check for discoveries (high metric values)
            for metric in self.emergence_metrics:
                value = metrics[metric.name]
                if metric.target_range:
                    min_val, max_val = metric.target_range
                    if min_val <= value <= max_val:
                        discovery = {
                            "type": "target_range",
                            "metric": metric.name,
                            "value": value,
                            "config": config,
                            "iteration": i
                        }
                        results["discoveries"].append(discovery)
                        print(f"    ✨ Discovery: {metric.name} = {value:.4f}")
                elif metric.higher_is_better and value > 0.8:  # Threshold for discovery
                    discovery = {
                        "type": "high_value",
                        "metric": metric.name,
                        "value": value,
                        "config": config,
                        "iteration": i
                    }
                    results["discoveries"].append(discovery)
                    print(f"    ✨ Discovery: {metric.name} = {value:.4f}")

        return results

    def _adaptive_explore(self, n_iterations: int, simulation_fn: Optional[Callable],
                         batch_size: int) -> Dict[str, Any]:
        """
        Adaptive exploration that focuses on promising regions

        Uses information gain and surprise to direct exploration
        """
        results = {
            "strategy": "adaptive",
            "iterations": n_iterations,
            "discoveries": [],
            "all_evaluations": [],
            "adaptation_history": []
        }

        # Initial random sample
        initial_configs = self.parameter_space.sample(batch_size, ExplorationStrategy.RANDOM)
        evaluated_configs = []
        metric_values = {metric.name: [] for metric in self.emergence_metrics}

        # Evaluate initial batch
        for config in initial_configs:
            sim_result = simulation_fn(config) if simulation_fn else self._mock_simulation(config)
            metrics = {m.name: m.compute(sim_result) for m in self.emergence_metrics}

            evaluated_configs.append((config, metrics, sim_result))
            for metric_name, value in metrics.items():
                metric_values[metric_name].append(value)

        # Iterative adaptive sampling
        for iteration in range(batch_size, n_iterations, batch_size):
            print(f"  Adaptive iteration {iteration}/{n_iterations}")

            # Analyze current results to identify promising regions
            adaptation = self._analyze_and_adapt(evaluated_configs, metric_values)
            results["adaptation_history"].append(adaptation)

            # Generate new samples based on adaptation
            new_configs = self._generate_adaptive_samples(
                evaluated_configs, metric_values, batch_size, adaptation
            )

            # Evaluate new samples
            for config in new_configs:
                sim_result = simulation_fn(config) if simulation_fn else self._mock_simulation(config)
                metrics = {m.name: m.compute(sim_result) for m in self.emergence_metrics}

                evaluated_configs.append((config, metrics, sim_result))
                for metric_name, value in metrics.items():
                    metric_values[metric_name].append(value)

                # Check for discoveries
                for metric in self.emergence_metrics:
                    value = metrics[metric.name]
                    if value > np.percentile(metric_values[metric.name], 95):
                        discovery = {
                            "type": "adaptive_outlier",
                            "metric": metric.name,
                            "value": value,
                            "config": config,
                            "percentile": 100 * (np.sum(np.array(metric_values[metric.name]) <= value) / len(metric_values[metric.name])),
                            "iteration": iteration
                        }
                        results["discoveries"].append(discovery)
                        print(f"    ✨ Discovery: {metric.name} = {value:.4f} (percentile: {discovery['percentile']:.1f})")

        results["all_evaluations"] = [
            {"config": c, "metrics": m, "raw_result": r}
            for c, m, r in evaluated_configs
        ]

        return results

    def _rare_event_explore(self, n_iterations: int, simulation_fn: Optional[Callable],
                           batch_size: int) -> Dict[str, Any]:
        """
        Rare event exploration using importance sampling

        Focuses on parameter regions that produce unusual behaviors
        """
        results = {
            "strategy": "rare_event",
            "iterations": n_iterations,
            "discoveries": [],
            "all_evaluations": [],
            "rare_events": []
        }

        # Standard sampling to establish baseline
        baseline_configs = self.parameter_space.sample(batch_size * 2, ExplorationStrategy.RANDOM)
        baseline_metrics = {metric.name: [] for metric in self.emergence_metrics}

        for config in baseline_configs:
            sim_result = simulation_fn(config) if simulation_fn else self._mock_simulation(config)
            metrics = {m.name: m.compute(sim_result) for m in self.emergence_metrics}
            for metric_name, value in metrics.items():
                baseline_metrics[metric_name].append(value)

        # Identify rare regions (tail events)
        from scipy import stats
        rare_regions = {}
        for metric_name, values in baseline_metrics.items():
            # Define rare as top 5% or bottom 5%
            threshold_high = np.percentile(values, 95)
            threshold_low = np.percentile(values, 5)
            rare_regions[metric_name] = {
                "high": threshold_high,
                "low": threshold_low
            }

        # Importance sampling towards rare regions
        for iteration in range(0, n_iterations, batch_size):
            print(f"  Rare event iteration {iteration}/{n_iterations}")

            # Sample biased towards rare regions
            rare_configs = self._sample_rare_regions(rare_regions, batch_size // 2)
            normal_configs = self.parameter_space.sample(batch_size // 2, ExplorationStrategy.RANDOM)
            configs = rare_configs + normal_configs

            for config in configs:
                sim_result = simulation_fn(config) if simulation_fn else self._mock_simulation(config)
                metrics = {m.name: m.compute(sim_result) for m in self.emergence_metrics}

                results["all_evaluations"].append({
                    "config": config,
                    "metrics": metrics,
                    "raw_result": sim_result
                })

                # Check if we found rare events
                for metric_name, value in metrics.items():
                    is_rare = False
                    rarity_type = None

                    if value >= rare_regions[metric_name]["high"]:
                        is_rare = True
                        rarity_type = "high"
                    elif value <= rare_regions[metric_name]["low"]:
                        is_rare = True
                        rarity_type = "low"

                    if is_rare:
                        rare_event = {
                            "metric": metric_name,
                            "value": value,
                            "config": config,
                            "rarity_type": rarity_type,
                            "iteration": iteration
                        }
                        results["rare_events"].append(rare_event)
                        print(f"    🎲 Rare event: {metric_name} = {value:.4f} ({rarity_type})")

                        # Also mark as discovery
                        discovery = {
                            "type": "rare_event",
                            "metric": metric_name,
                            "value": value,
                            "config": config,
                            "rarity_type": rarity_type,
                            "iteration": iteration
                        }
                        results["discoveries"].append(discovery)

        return results

    def _multi_objective_explore(self, n_iterations: int, simulation_fn: Optional[Callable],
                                batch_size: int) -> Dict[str, Any]:
        """
        Multi-objective exploration for Pareto frontier

        Finds configurations that optimize multiple emergence metrics simultaneously
        """
        results = {
            "strategy": "multi_objective",
            "iterations": n_iterations,
            "discoveries": [],
            "all_evaluations": [],
            "pareto_frontier": []
        }

        evaluated_configs = []

        for iteration in range(0, n_iterations, batch_size):
            print(f"  Multi-objective iteration {iteration}/{n_iterations}")

            # Sample configurations
            configs = self.parameter_space.sample(batch_size, ExplorationStrategy.RANDOM)

            for config in configs:
                sim_result = simulation_fn(config) if simulation_fn else self._mock_simulation(config)
                metrics = {m.name: m.compute(sim_result) for m in self.emergence_metrics}

                evaluated_configs.append({
                    "config": config,
                    "metrics": metrics,
                    "raw_result": sim_result
                })

                results["all_evaluations"].append({
                    "config": config,
                    "metrics": metrics,
                    "raw_result": sim_result
                })

            # Update Pareto frontier
            current_pareto = self._compute_pareto_frontier(evaluated_configs)
            if len(current_pareto) > len(results["pareto_frontier"]):
                new_points = len(current_pareto) - len(results["pareto_frontier"])
                results["pareto_frontier"] = current_pareto
                print(f"    📈 Pareto frontier expanded: +{new_points} points")

                # New Pareto points are discoveries
                for point in current_pareto[-new_points:]:
                    discovery = {
                        "type": "pareto_optimal",
                        "metrics": point["metrics"],
                        "config": point["config"],
                        "iteration": iteration
                    }
                    results["discoveries"].append(discovery)

        return results

    def _entropy_explore(self, n_iterations: int, simulation_fn: Optional[Callable],
                        batch_size: int) -> Dict[str, Any]:
        """
        Entropy maximization exploration

        Samples to maximize information gain about the parameter space
        """
        results = {
            "strategy": "entropy_max",
            "iterations": n_iterations,
            "discoveries": [],
            "all_evaluations": [],
            "entropy_history": []
        }

        evaluated_configs = []

        for iteration in range(0, n_iterations, batch_size):
            print(f"  Entropy iteration {iteration}/{n_iterations}")

            if iteration == 0:
                # Initial random sample
                configs = self.parameter_space.sample(batch_size, ExplorationStrategy.RANDOM)
            else:
                # Sample to maximize entropy (diversity)
                configs = self._max_entropy_sample(evaluated_configs, batch_size)

            for config in configs:
                sim_result = simulation_fn(config) if simulation_fn else self._mock_simulation(config)
                metrics = {m.name: m.compute(sim_result) for m in self.emergence_metrics}

                evaluated_configs.append({
                    "config": config,
                    "metrics": metrics,
                    "raw_result": sim_result
                })

                results["all_evaluations"].append({
                    "config": config,
                    "metrics": metrics,
                    "raw_result": sim_result
                })

            # Compute entropy of current samples
            entropy = self._compute_entropy(evaluated_configs)
            results["entropy_history"].append(entropy)
            print(f"    🎲 Current entropy: {entropy:.4f}")

            # Check for discoveries (unusual metric combinations)
            if len(evaluated_configs) > batch_size:
                for metric in self.emergence_metrics:
                    recent_values = [e["metrics"][metric.name]
                                    for e in evaluated_configs[-batch_size:]]
                    all_values = [e["metrics"][metric.name]
                                for e in evaluated_configs[:-batch_size]]

                    # Check if recent samples are in unexplored region
                    for i, (config, metrics) in enumerate([(e["config"], e["metrics"])
                                                          for e in evaluated_configs[-batch_size:]]):
                        value = metrics[metric.name]
                        # Check if value is in sparse region
                        if len(all_values) > 0:
                            distances = [abs(value - v) for v in all_values]
                            min_distance = min(distances)
                            if min_distance > np.percentile(distances, 90):
                                discovery = {
                                    "type": "novel_region",
                                    "metric": metric.name,
                                    "value": value,
                                    "config": config,
                                    "min_distance": min_distance,
                                    "iteration": iteration
                                }
                                results["discoveries"].append(discovery)
                                print(f"    ✨ Novel region: {metric.name} = {value:.4f}")

        return results

    def _analyze_and_adapt(self, evaluated_configs: List, metric_values: Dict) -> Dict[str, Any]:
        """Analyze current results and determine adaptation strategy"""
        adaptation = {
            "strategy": None,
            "focus_metrics": [],
            "parameter_adjustments": {}
        }

        # Find metrics with high variance (promising for exploration)
        for metric_name, values in metric_values.items():
            if len(values) > 0:
                cv = np.std(values) / (np.mean(values) + 1e-6)
                if cv > 0.3:  # High coefficient of variation
                    adaptation["focus_metrics"].append(metric_name)

        # Determine adaptation strategy
        if len(adaptation["focus_metrics"]) > 0:
            adaptation["strategy"] = "focus"
            # Suggest parameter adjustments
            for param in self.parameter_space.dimensions.keys():
                # Would analyze correlation between param and focus metrics
                adaptation["parameter_adjustments"][param] = "maintain"
        else:
            adaptation["strategy"] = "explore"

        return adaptation

    def _generate_adaptive_samples(self, evaluated_configs: List, metric_values: Dict,
                                   n_samples: int, adaptation: Dict) -> List[Dict]:
        """Generate new samples based on adaptation strategy"""
        if adaptation["strategy"] == "focus":
            # Sample around high-performing configs
            top_configs = sorted(evaluated_configs,
                               key=lambda x: sum(x[1].values()),
                               reverse=True)[:5]

            new_samples = []
            for _ in range(n_samples):
                # Select a top config
                base_config = top_configs[np.random.randint(len(top_configs))][0]

                # Add noise to parameters
                noisy_config = {}
                for param, (min_val, max_val) in self.parameter_space.dimensions.items():
                    base_value = base_config[param]
                    noise_level = 0.1 * (max_val - min_val)
                    new_value = base_value + np.random.normal(0, noise_level)
                    noisy_config[param] = np.clip(new_value, min_val, max_val)

                new_samples.append(noisy_config)

            return new_samples
        else:
            # Random exploration
            return self.parameter_space.sample(n_samples, ExplorationStrategy.RANDOM)

    def _sample_rare_regions(self, rare_regions: Dict, n_samples: int) -> List[Dict]:
        """Sample configurations biased towards rare event regions"""
        # This is a simplified version
        # In practice, would use more sophisticated importance sampling
        return self.parameter_space.sample(n_samples, ExplorationStrategy.RANDOM)

    def _compute_pareto_frontier(self, evaluated_configs: List) -> List[Dict]:
        """Compute Pareto frontier from evaluated configurations"""
        if not evaluated_configs:
            return []

        # Extract metric values
        metric_names = list(evaluated_configs[0]["metrics"].keys())

        def dominates(config1, config2):
            """Check if config1 dominates config2"""
            m1 = config1["metrics"]
            m2 = config2["metrics"]

            at_least_one_better = False
            all_at_least_as_good = True

            for metric_name in metric_names:
                metric = next(m for m in self.emergence_metrics if m.name == metric_name)
                if metric.higher_is_better:
                    if m1[metric_name] < m2[metric_name]:
                        all_at_least_as_good = False
                        break
                    elif m1[metric_name] > m2[metric_name]:
                        at_least_one_better = True
                else:
                    if m1[metric_name] > m2[metric_name]:
                        all_at_least_as_good = False
                        break
                    elif m1[metric_name] < m2[metric_name]:
                        at_least_one_better = True

            return all_at_least_as_good and at_least_one_better

        # Find non-dominated configs
        pareto = []
        for config in evaluated_configs:
            is_dominated = False
            for other in evaluated_configs:
                if other is not config and dominates(other, config):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto.append(config)

        return pareto

    def _max_entropy_sample(self, evaluated_configs: List, n_samples: int) -> List[Dict]:
        """Generate samples to maximize entropy (diversity)"""
        # Simple version: sample uniformly
        # Advanced version would use Gaussian Process to model uncertainty
        return self.parameter_space.sample(n_samples, ExplorationStrategy.RANDOM)

    def _compute_entropy(self, evaluated_configs: List) -> float:
        """Compute entropy of current sample distribution"""
        if len(evaluated_configs) == 0:
            return 0.0

        # Estimate entropy using k-nearest neighbors
        metric_names = list(evaluated_configs[0]["metrics"].keys())
        metric_matrix = np.array([[e["metrics"][m] for m in metric_names]
                                  for e in evaluated_configs])

        # Normalize
        metric_matrix = (metric_matrix - metric_matrix.mean(axis=0)) / (metric_matrix.std(axis=0) + 1e-6)

        # Compute pairwise distances
        from scipy.spatial.distance import pdist
        distances = pdist(metric_matrix)

        # Entropy proxy: mean distance
        return float(np.mean(distances))

    def _mock_simulation(self, config: Dict[str, float]) -> Dict[str, Any]:
        """Mock simulation for testing without actual POLLN"""
        # Generate mock results based on config
        np.random.seed(hash(str(sorted(config.items()))) % 2**32)

        result = {
            "agent_behavior": {
                "coordination": np.random.random(),
                "specialization": np.random.random(),
                "emergence": np.random.random()
            },
            "collective_dynamics": {
                "synchronization": np.random.random(),
                "phase_transitions": np.random.random(),
                "criticality": np.random.random()
            },
            "information_flow": {
                "entropy": np.random.random(),
                "mutual_information": np.random.random(),
                "transfer_entropy": np.random.random()
            },
            "config": config
        }

        # Make some metrics depend on parameters
        if "temperature" in config:
            result["agent_behavior"]["coordination"] *= config["temperature"]
        if "learning_rate" in config:
            result["collective_dynamics"]["synchronization"] *= config["learning_rate"]

        return result

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save exploration results to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"exploration_{results['strategy']}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"  💾 Results saved to {filename}")

    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze exploration results to identify patterns"""
        analysis = {
            "summary": {
                "total_evaluations": len(results.get("all_evaluations", [])),
                "discoveries": len(results.get("discoveries", [])),
                "metrics_analyzed": len(self.emergence_metrics)
            },
            "discovery_types": {},
            "parameter_importance": {},
            "recommendations": []
        }

        # Analyze discovery types
        for discovery in results.get("discoveries", []):
            dtype = discovery.get("type", "unknown")
            analysis["discovery_types"][dtype] = analysis["discovery_types"].get(dtype, 0) + 1

        # Parameter importance (simplified)
        # In practice, would use more sophisticated analysis

        # Generate recommendations
        if len(results.get("discoveries", [])) > 0:
            analysis["recommendations"].append("Promising parameter regions discovered")
            analysis["recommendations"].append("Consider targeted refinement")

        return analysis


# Utility functions

def create_polln_parameter_space() -> ParameterSpace:
    """Create standard POLLN parameter space for exploration"""
    return ParameterSpace(
        name="polln_standard",
        dimensions={
            # Agent parameters
            "n_agents": (10, 1000),
            "temperature": (0.1, 2.0),
            "learning_rate": (0.001, 0.1),

            # Network parameters
            "connectivity": (0.01, 1.0),
            "synapse_strength": (0.1, 10.0),
            "decay_rate": (0.0, 0.5),

            # Collective parameters
            "coordination_strength": (0.0, 1.0),
            "exploration_bias": (0.0, 1.0),
            "memory_length": (1, 100),

            # Meta parameters
            "meta_differentiation": (0.0, 1.0),
            "value_uncertainty": (0.0, 1.0)
        },
        log_scale=["n_agents", "memory_length"],
        constraints=[
            # Example constraint: connectivity * n_agents >= 10
            lambda params: params["connectivity"] * params["n_agents"] >= 10
        ]
    )


def create_standard_emergence_metrics() -> List[EmergenceMetric]:
    """Create standard emergence metrics for POLLN"""
    return [
        EmergenceMetric(
            name="collective_intelligence",
            description="Emergent problem-solving capability beyond individual agents",
            compute=lambda result: result.get("agent_behavior", {}).get("emergence", 0.0),
            higher_is_better=True,
            target_range=(0.7, 1.0)
        ),
        EmergenceMetric(
            name="criticality",
            description="System operates near critical point (phase transition)",
            compute=lambda result: result.get("collective_dynamics", {}).get("criticality", 0.0),
            higher_is_better=True,
            target_range=(0.8, 0.95)
        ),
        EmergenceMetric(
            name="information_integration",
            description="Integration of information across agents",
            compute=lambda result: result.get("information_flow", {}).get("mutual_information", 0.0),
            higher_is_better=True
        ),
        EmergenceMetric(
            name="adaptive_complexity",
            description="Balance between stability and adaptability",
            compute=lambda result: (
                result.get("collective_dynamics", {}).get("synchronization", 0.5) *
                result.get("agent_behavior", {}).get("specialization", 0.5)
            ),
            higher_is_better=True
        ),
        EmergenceMetric(
            name="self_organization",
            description="Spontaneous pattern formation",
            compute=lambda result: result.get("agent_behavior", {}).get("coordination", 0.0),
            higher_is_better=True
        )
    ]


if __name__ == "__main__":
    from datetime import datetime

    # Create explorer
    param_space = create_polln_parameter_space()
    metrics = create_standard_emergence_metrics()

    explorer = EmergenceExplorer(
        parameter_space=param_space,
        emergence_metrics=metrics,
        output_dir="./exploration_results"
    )

    # Run different exploration strategies
    strategies = [
        ExplorationStrategy.RANDOM,
        ExplorationStrategy.ADAPTIVE,
        ExplorationStrategy.ENTROPY_MAX
    ]

    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Running {strategy.value} exploration")
        print(f"{'='*60}\n")

        results = explorer.explore(
            n_iterations=50,
            strategy=strategy,
            simulation_fn=None,  # Use mock simulation
            batch_size=10
        )

        analysis = explorer.analyze_results(results)
        print(f"\n📊 Analysis: {analysis}")
