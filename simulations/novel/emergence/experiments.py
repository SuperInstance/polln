"""
Experimental Framework for Emergent Phenomena

Provides controlled experimentation framework for testing hypotheses about
emergent phenomena. Includes ablation studies, robustness testing, and
replication protocols.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime
from scipy import stats
from scipy.stats import mannwhitneyu, kruskal
import warnings
warnings.filterwarnings('ignore')


@dataclass
class Experiment:
    """Experimental design"""
    experiment_id: str
    name: str
    hypothesis: str
    independent_variables: Dict[str, Tuple[float, float]]  # var: (min, max)
    dependent_variables: List[str]
    controls: Dict[str, float]
    n_replicates: int
    procedure: str
    expected_outcomes: List[str]


@dataclass
class ExperimentResult:
    """Results from running an experiment"""
    experiment_id: str
    timestamp: str
    parameters: Dict[str, float]
    measurements: Dict[str, float]
    raw_data: Dict[str, Any]
    success: bool
    notes: str = ""


@dataclass
class AblationResult:
    """Results from ablation study"""
    component_ablated: str
    performance_impact: float
    criticality_score: float
    interactions: List[str]
    recommendation: str


class ExperimentalFramework:
    """
    Comprehensive experimental framework for emergence research

    Supports controlled experiments, ablation studies, robustness testing,
    and replication protocols.
    """

    def __init__(self,
                 simulation_fn: Callable,
                 output_dir: str = "./experiment_results"):
        self.simulation_fn = simulation_fn
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.experiments: Dict[str, Experiment] = {}
        self.results: Dict[str, List[ExperimentResult]] = {}
        self.ablation_results: List[AblationResult] = []

    def design_experiment(self,
                         name: str,
                         hypothesis: str,
                         independent_vars: Dict[str, Tuple[float, float]],
                         dependent_vars: List[str],
                         controls: Dict[str, float],
                         n_replicates: int = 10,
                         procedure: str = "") -> Experiment:
        """
        Design a controlled experiment

        Args:
            name: Experiment name
            hypothesis: Hypothesis being tested
            independent_vars: Variables to manipulate
            dependent_vars: Variables to measure
            controls: Control variables
            n_replicates: Number of replicates
            procedure: Experimental procedure

        Returns:
            Experiment object
        """
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            hypothesis=hypothesis,
            independent_variables=independent_vars,
            dependent_variables=dependent_vars,
            controls=controls,
            n_replicates=n_replicates,
            procedure=procedure,
            expected_outcomes=[]
        )

        self.experiments[experiment_id] = experiment

        print(f"🔬 Designed experiment: {name}")
        print(f"   ID: {experiment_id}")
        print(f"   Hypothesis: {hypothesis}")

        self._save_experiment(experiment)

        return experiment

    def run_experiment(self,
                      experiment: Experiment,
                      parameter_values: Optional[Dict[str, float]] = None) -> List[ExperimentResult]:
        """
        Run an experiment

        Args:
            experiment: Experiment to run
            parameter_values: Specific parameter values (if None, sample from range)

        Returns:
            List of results from replicates
        """
        print(f"🧪 Running experiment: {experiment.name}")

        results = []

        for replicate in range(experiment.n_replicates):
            print(f"  Replicate {replicate + 1}/{experiment.n_replicates}")

            # Determine parameter values
            if parameter_values is None:
                # Sample from independent variable ranges
                params = {}
                for var, (min_val, max_val) in experiment.independent_variables.items():
                    params[var] = np.random.uniform(min_val, max_val)
            else:
                params = parameter_values.copy()

            # Add controls
            params.update(experiment.controls)

            # Run simulation
            try:
                sim_result = self.simulation_fn(params)

                # Extract measurements
                measurements = {}
                for dep_var in experiment.dependent_variables:
                    if dep_var in sim_result:
                        measurements[dep_var] = float(sim_result[dep_var])
                    elif "metrics" in sim_result and dep_var in sim_result["metrics"]:
                        measurements[dep_var] = float(sim_result["metrics"][dep_var])
                    else:
                        # Try nested access
                        measurements[dep_var] = self._extract_measurement(sim_result, dep_var)

                result = ExperimentResult(
                    experiment_id=experiment.experiment_id,
                    timestamp=datetime.now().isoformat(),
                    parameters=params,
                    measurements=measurements,
                    raw_data=sim_result,
                    success=True
                )

                results.append(result)
                print(f"    ✅ Success: {measurements}")

            except Exception as e:
                result = ExperimentResult(
                    experiment_id=experiment.experiment_id,
                    timestamp=datetime.now().isoformat(),
                    parameters=params,
                    measurements={},
                    raw_data={},
                    success=False,
                    notes=f"Error: {e}"
                )

                results.append(result)
                print(f"    ❌ Failed: {e}")

        # Store results
        if experiment.experiment_id not in self.results:
            self.results[experiment.experiment_id] = []
        self.results[experiment.experiment_id].extend(results)

        # Save results
        self._save_results(experiment.experiment_id, results)

        return results

    def _extract_measurement(self, data: Dict, key: str) -> float:
        """Extract measurement from nested data structure"""
        keys = key.split('.')
        value = data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, 0.0)
            else:
                return 0.0

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def parameter_sweep(self,
                       experiment: Experiment,
                       sweep_var: str,
                       n_values: int = 20) -> Dict[str, List[ExperimentResult]]:
        """
        Perform parameter sweep

        Args:
            experiment: Experiment to sweep
            sweep_var: Variable to sweep
            n_values: Number of values to test

        Returns:
            Results grouped by parameter value
        """
        print(f"📊 Sweeping parameter: {sweep_var}")

        if sweep_var not in experiment.independent_variables:
            print(f"  ❌ {sweep_var} not in independent variables")
            return {}

        min_val, max_val = experiment.independent_variables[sweep_var]
        values = np.linspace(min_val, max_val, n_values)

        results_by_value = {}

        for value in values:
            print(f"  Testing {sweep_var} = {value:.4f}")

            param_values = {sweep_var: value}
            results = self.run_experiment(experiment, param_values)

            results_by_value[str(value)] = results

        # Analyze sweep results
        self._analyze_sweep(results_by_value, sweep_var)

        return results_by_value

    def _analyze_sweep(self, results_by_value: Dict[str, List[ExperimentResult]],
                      sweep_var: str) -> None:
        """Analyze parameter sweep results"""
        print(f"\n  📈 Analysis of {sweep_var} sweep:")

        values = []
        measurements = {dep_var: [] for dep_var in self.results[list(results_by_value.keys())[0]][0].measurements.keys()}

        for value_str, results in results_by_value.items():
            value = float(value_str)
            values.append(value)

            for result in results:
                for dep_var, meas in result.measurements.items():
                    measurements[dep_var].append(meas)

        # Compute correlations
        for dep_var, meas_values in measurements.items():
            if len(values) == len(meas_values):
                correlation, p_value = stats.pearsonr(values, meas_values)
                print(f"    {dep_var}: r = {correlation:.3f}, p = {p_value:.4f}")

    def ablation_study(self,
                      base_config: Dict[str, float],
                      components: List[str],
                      metric: str) -> List[AblationResult]:
        """
        Perform ablation study to identify critical components

        Args:
            base_config: Base configuration
            components: List of components to ablate
            metric: Metric to measure impact

        Returns:
            List of ablation results
        """
        print(f"🔪 Performing ablation study on {len(components)} components")

        # Run baseline
        print("  Running baseline...")
        try:
            baseline_result = self.simulation_fn(base_config)
            baseline_value = self._extract_measurement(baseline_result, metric)
        except Exception as e:
            print(f"  ❌ Baseline failed: {e}")
            return []

        ablation_results = []

        for component in components:
            print(f"  Ablating: {component}")

            # Create ablated config
            ablated_config = base_config.copy()

            # Ablate component (set to 0 or disable)
            if component in ablated_config:
                ablated_config[component] = 0.0
            else:
                ablated_config[f"enable_{component}"] = 0.0
                ablated_config[f"use_{component}"] = 0.0

            # Run ablated simulation
            try:
                ablated_result = self.simulation_fn(ablated_config)
                ablated_value = self._extract_measurement(ablated_result, metric)

                # Compute impact
                impact = (baseline_value - ablated_value) / (abs(baseline_value) + 1e-6)
                criticality = abs(impact)

                # Identify interactions (simplified)
                interactions = []  # Would need more sophisticated analysis

                # Generate recommendation
                if criticality > 0.5:
                    recommendation = f"CRITICAL: {component} is essential for performance"
                elif criticality > 0.2:
                    recommendation = f"IMPORTANT: {component} contributes significantly"
                else:
                    recommendation = f"OPTIONAL: {component} has minimal impact"

                ablation_result = AblationResult(
                    component_ablated=component,
                    performance_impact=impact,
                    criticality_score=criticality,
                    interactions=interactions,
                    recommendation=recommendation
                )

                ablation_results.append(ablation_result)

                print(f"    Impact: {impact:.3f}, Criticality: {criticality:.3f}")
                print(f"    {recommendation}")

            except Exception as e:
                print(f"    ❌ Ablation failed: {e}")
                continue

        self.ablation_results.extend(ablation_results)

        # Save ablation results
        self._save_ablation_results(ablation_results)

        return ablation_results

    def robustness_test(self,
                       base_config: Dict[str, float],
                       noise_levels: List[float],
                       n_trials: int = 20) -> Dict[str, Any]:
        """
        Test robustness to parameter noise

        Args:
            base_config: Base configuration
            noise_levels: List of noise levels to test
            n_trials: Number of trials per noise level

        Returns:
            Robustness analysis results
        """
        print(f"🛡️  Testing robustness across {len(noise_levels)} noise levels")

        robustness_results = {
            "noise_levels": [],
            "mean_performance": [],
            "std_performance": [],
            "success_rate": []
        }

        # Get baseline metric
        try:
            baseline_result = self.simulation_fn(base_config)
            baseline_metrics = list(baseline_result.get("metrics", {}).keys())
            if baseline_metrics:
                primary_metric = baseline_metrics[0]
            else:
                primary_metric = "performance"
        except:
            primary_metric = "performance"

        for noise_level in noise_levels:
            print(f"  Testing noise level: {noise_level:.3f}")

            performances = []
            successes = 0

            for trial in range(n_trials):
                # Add noise to config
                noisy_config = {}
                for param, value in base_config.items():
                    if isinstance(value, (int, float)):
                        noise = np.random.normal(0, noise_level * abs(value))
                        noisy_config[param] = value + noise
                    else:
                        noisy_config[param] = value

                # Run simulation
                try:
                    result = self.simulation_fn(noisy_config)
                    performance = self._extract_measurement(result, primary_metric)
                    performances.append(performance)
                    successes += 1
                except:
                    continue

            if performances:
                robustness_results["noise_levels"].append(noise_level)
                robustness_results["mean_performance"].append(np.mean(performances))
                robustness_results["std_performance"].append(np.std(performances))
                robustness_results["success_rate"].append(successes / n_trials)

                print(f"    Mean: {np.mean(performances):.3f}, Std: {np.std(performances):.3f}")

        # Analyze robustness
        self._analyze_robustness(robustness_results)

        return robustness_results

    def _analyze_robustness(self, results: Dict[str, Any]) -> None:
        """Analyze robustness test results"""
        print("\n  📊 Robustness Analysis:")

        if len(results["mean_performance"]) < 2:
            return

        # Compute degradation rate
        performance_drop = (results["mean_performance"][0] - results["mean_performance"][-1])
        performance_drop /= (abs(results["mean_performance"][0]) + 1e-6)

        print(f"    Performance drop: {performance_drop:.3f}")

        if performance_drop < 0.1:
            print(f"    ✅ HIGHLY ROBUST: Minimal degradation")
        elif performance_drop < 0.3:
            print(f"    ⚠️  MODERATELY ROBUST: Acceptable degradation")
        else:
            print(f"    ❌ FRAGILE: Significant degradation")

    def replication_study(self,
                         experiment: Experiment,
                         n_replications: int = 5,
                         vary_seed: bool = True) -> Dict[str, Any]:
        """
        Perform replication study

        Args:
            experiment: Experiment to replicate
            n_replications: Number of replications
            vary_seed: Whether to vary random seed

        Returns:
            Replication analysis
        """
        print(f"🔄 Performing replication study ({n_replications} replications)")

        replication_results = []

        for replication in range(n_replications):
            print(f"  Replication {replication + 1}/{n_replications}")

            if vary_seed:
                # Would set random seed here if simulator supports it
                pass

            results = self.run_experiment(experiment)

            # Aggregate results
            for result in results:
                replication_results.append(result)

        # Analyze replication consistency
        consistency = self._analyze_replication_consistency(replication_results, experiment.dependent_variables)

        return {
            "n_replications": n_replications,
            "results": replication_results,
            "consistency": consistency
        }

    def _analyze_replication_consistency(self,
                                        results: List[ExperimentResult],
                                        dependent_vars: List[str]) -> Dict[str, float]:
        """Analyze consistency across replications"""
        print("\n  📊 Replication Consistency:")

        consistency_metrics = {}

        for var in dependent_vars:
            values = [r.measurements.get(var, 0.0) for r in results if var in r.measurements]

            if len(values) > 1:
                mean = np.mean(values)
                std = np.std(values)
                cv = std / (abs(mean) + 1e-6)

                consistency_metrics[f"{var}_cv"] = cv
                print(f"    {var}: CV = {cv:.3f}")

        return consistency_metrics

    def statistical_test(self,
                        results1: List[ExperimentResult],
                        results2: List[ExperimentResult],
                        metric: str,
                        test: str = "mannwhitney") -> Dict[str, Any]:
        """
        Perform statistical test comparing two result sets

        Args:
            results1: First set of results
            results2: Second set of results
            metric: Metric to compare
            test: Statistical test (mannwhitney, kruskal, ttest)

        Returns:
            Statistical test results
        """
        print(f"📊 Performing {test} test on {metric}")

        # Extract measurements
        values1 = [r.measurements.get(metric, 0.0) for r in results1 if metric in r.measurements]
        values2 = [r.measurements.get(metric, 0.0) for r in results2 if metric in r.measurements]

        if len(values1) < 3 or len(values2) < 3:
            print(f"  ❌ Insufficient data for statistical test")
            return {"error": "Insufficient data"}

        # Perform test
        if test == "mannwhitney":
            statistic, p_value = mannwhitneyu(values1, values2, alternative='two-sided')
            test_name = "Mann-Whitney U"
        elif test == "kruskal":
            statistic, p_value = kruskal(values1, values2)
            test_name = "Kruskal-Wallis"
        elif test == "ttest":
            statistic, p_value = stats.ttest_ind(values1, values2)
            test_name = "Independent t-test"
        else:
            print(f"  ❌ Unknown test: {test}")
            return {"error": "Unknown test"}

        results = {
            "test": test_name,
            "statistic": statistic,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "mean1": np.mean(values1),
            "mean2": np.mean(values2),
            "std1": np.std(values1),
            "std2": np.std(values2)
        }

        print(f"  {test_name}: statistic = {statistic:.3f}, p = {p_value:.4f}")

        if results["significant"]:
            print(f"  ✅ SIGNIFICANT difference detected")
        else:
            print(f"  ⚠️  No significant difference")

        return results

    def _save_experiment(self, experiment: Experiment) -> None:
        """Save experiment design"""
        experiments_file = self.output_dir / "experiments.json"

        # Load existing
        if experiments_file.exists():
            with open(experiments_file, 'r') as f:
                experiments_data = json.load(f)
        else:
            experiments_data = {}

        # Add new experiment
        experiments_data[experiment.experiment_id] = {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "hypothesis": experiment.hypothesis,
            "independent_variables": experiment.independent_variables,
            "dependent_variables": experiment.dependent_variables,
            "controls": experiment.controls,
            "n_replicates": experiment.n_replicates,
            "procedure": experiment.procedure,
            "expected_outcomes": experiment.expected_outcomes
        }

        # Save
        with open(experiments_file, 'w') as f:
            json.dump(experiments_data, f, indent=2)

    def _save_results(self, experiment_id: str, results: List[ExperimentResult]) -> None:
        """Save experiment results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"results_{experiment_id}_{timestamp}.json"

        results_data = []
        for result in results:
            results_data.append({
                "experiment_id": result.experiment_id,
                "timestamp": result.timestamp,
                "parameters": result.parameters,
                "measurements": result.measurements,
                "success": result.success,
                "notes": result.notes
            })

        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)

    def _save_ablation_results(self, results: List[AblationResult]) -> None:
        """Save ablation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.output_dir / f"ablation_{timestamp}.json"

        results_data = []
        for result in results:
            results_data.append({
                "component_ablated": result.component_ablated,
                "performance_impact": result.performance_impact,
                "criticality_score": result.criticality_score,
                "interactions": result.interactions,
                "recommendation": result.recommendation
            })

        with open(file_path, 'w') as f:
            json.dump(results_data, f, indent=2)

    def generate_report(self) -> str:
        """Generate comprehensive experimental report"""
        report = []
        report.append("=" * 80)
        report.append("EXPERIMENTAL FRAMEWORK REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total experiments designed: {len(self.experiments)}")
        report.append(f"Total experiments run: {len(self.results)}")
        report.append(f"Ablation studies: {len(self.ablation_results)}")
        report.append("")

        # Experiments by status
        report.append("EXPERIMENTS BY STATUS")
        report.append("-" * 80)

        for exp_id, exp in self.experiments.items():
            if exp_id in self.results:
                status = f"RUN ({len(self.results[exp_id])} results)"
            else:
                status = "DESIGNED"

            report.append(f"{exp.name}: {status}")

        report.append("")

        # Ablation summary
        if self.ablation_results:
            report.append("ABLATION STUDY SUMMARY")
            report.append("-" * 80)

            sorted_ablations = sorted(self.ablation_results,
                                    key=lambda x: x.criticality_score,
                                    reverse=True)

            for result in sorted_ablations:
                report.append(f"{result.component_ablated}:")
                report.append(f"  Criticality: {result.criticality_score:.3f}")
                report.append(f"  Impact: {result.performance_impact:.3f}")
                report.append(f"  {result.recommendation}")

            report.append("")

        return "\n".join(report)


if __name__ == "__main__":
    # Mock simulation function
    def mock_simulation(config):
        return {
            "metrics": {
                "performance": config.get("temperature", 0.5) * config.get("learning_rate", 0.01) * 100,
                "coordination": np.random.random(),
                "synchronization": np.random.random()
            }
        }

    # Create framework
    framework = ExperimentalFramework(mock_simulation, output_dir="./test_experiment_results")

    # Design experiment
    experiment = framework.design_experiment(
        name="Temperature Impact on Performance",
        hypothesis="Higher temperature increases performance up to a point",
        independent_vars={"temperature": (0.1, 2.0)},
        dependent_vars=["performance", "coordination"],
        controls={"learning_rate": 0.01, "n_agents": 100},
        n_replicates=5
    )

    # Run experiment
    results = framework.run_experiment(experiment)

    # Parameter sweep
    sweep_results = framework.parameter_sweep(experiment, "temperature", n_values=10)

    # Ablation study
    base_config = {"temperature": 1.0, "learning_rate": 0.01, "enable_mechanism1": 1.0}
    ablation_results = framework.ablation_study(base_config, ["mechanism1", "mechanism2"], "performance")

    # Generate report
    report = framework.generate_report()
    print("\n" + report)
