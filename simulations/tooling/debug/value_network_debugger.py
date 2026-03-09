#!/usr/bin/env python3
"""
Value Network Debugger - Debug and analyze TD(λ) value networks in POLLN.

This tool inspects TD(λ) updates, value predictions, eligibility traces,
and helps debug convergence issues, oscillation, and divergence.
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import numpy as np
import time


@dataclass
class ValueUpdateEvent:
    """A single value function update event."""
    agent_id: str
    timestamp: float
    old_value: float
    new_value: float
    reward: float
    td_error: float
    eligibility_trace: float
    learning_rate: float
    lambda_param: float  # TD(λ) parameter

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EligibilityTraceState:
    """State of eligibility traces for an agent."""
    agent_id: str
    traces: Dict[str, float]  # action_id -> trace value
    last_updated: float
    total_trace_mass: float
    active_trace_count: int
    decay_rate: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ConvergenceAnalysis:
    """Analysis of value network convergence."""
    agent_id: str
    converged: bool
    convergence_rate: float
    stability_score: float
    oscillation_detected: bool
    oscillation_frequency: float
    divergence_detected: bool
    trend: str  # 'increasing', 'decreasing', 'stable'
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ValueDistribution:
    """Statistical distribution of value predictions."""
    agent_id: str
    mean: float
    std: float
    min: float
    max: float
    median: float
    percentile_25: float
    percentile_75: float
    histogram: List[Tuple[float, int]]  # (bin_center, count)

    def to_dict(self) -> Dict:
        return asdict(self)


class ValueNetworkDebugger:
    """
    Comprehensive TD(λ) value network debugging.

    Features:
    - Track value updates over time
    - Analyze eligibility traces
    - Detect convergence issues
    - Identify oscillation patterns
    - Detect divergence
    - Visualize learning curves
    - Analyze value distributions
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Update tracking
        self.update_events: Dict[str, List[ValueUpdateEvent]] = defaultdict(list)
        self.value_history: Dict[str, List[float]] = defaultdict(list)
        self.reward_history: Dict[str, List[float]] = defaultdict(list)

        # Eligibility traces
        self.eligibility_traces: Dict[str, EligibilityTraceState] = {}

        # Analysis cache
        self.convergence_cache: Dict[str, ConvergenceAnalysis] = {}
        self.distribution_cache: Dict[str, ValueDistribution] = {}

        # Learning parameters
        self.learning_params: Dict[str, Dict[str, float]] = {}

    def record_update(self, agent_id: str, old_value: float, new_value: float,
                     reward: float, td_error: float, eligibility_trace: float,
                     learning_rate: float, lambda_param: float) -> None:
        """
        Record a value function update.

        Args:
            agent_id: Agent ID
            old_value: Previous value
            new_value: Updated value
            reward: Reward received
            td_error: Temporal difference error
            eligibility_trace: Current eligibility trace value
            learning_rate: Learning rate (α)
            lambda_param: TD(λ) parameter
        """
        event = ValueUpdateEvent(
            agent_id=agent_id,
            timestamp=time.time(),
            old_value=old_value,
            new_value=new_value,
            reward=reward,
            td_error=td_error,
            eligibility_trace=eligibility_trace,
            learning_rate=learning_rate,
            lambda_param=lambda_param
        )

        self.update_events[agent_id].append(event)
        self.value_history[agent_id].append(new_value)
        self.reward_history[agent_id].append(reward)

        # Store learning parameters
        self.learning_params[agent_id] = {
            'learning_rate': learning_rate,
            'lambda': lambda_param
        }

    def record_eligibility_traces(self, agent_id: str, traces: Dict[str, float],
                                  decay_rate: float = 0.99) -> None:
        """
        Record eligibility trace state.

        Args:
            agent_id: Agent ID
            traces: Dictionary of action_id -> trace value
            decay_rate: Trace decay rate
        """
        state = EligibilityTraceState(
            agent_id=agent_id,
            traces=traces,
            last_updated=time.time(),
            total_trace_mass=sum(traces.values()),
            active_trace_count=sum(1 for v in traces.values() if v > 0.01),
            decay_rate=decay_rate
        )

        self.eligibility_traces[agent_id] = state

    def get_update_history(self, agent_id: str,
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None) -> List[ValueUpdateEvent]:
        """
        Get update history for an agent.

        Args:
            agent_id: Agent ID
            start_time: Optional start timestamp
            end_time: Optional end timestamp

        Returns:
            List of update events
        """
        events = self.update_events.get(agent_id, [])

        if start_time is not None:
            events = [e for e in events if e.timestamp >= start_time]

        if end_time is not None:
            events = [e for e in events if e.timestamp <= end_time]

        return events

    def analyze_convergence(self, agent_id: str,
                          window_size: int = 100) -> ConvergenceAnalysis:
        """
        Analyze convergence of an agent's value network.

        Args:
            agent_id: Agent ID
            window_size: Size of the rolling window for analysis

        Returns:
            ConvergenceAnalysis: Convergence analysis results
        """
        if agent_id in self.convergence_cache:
            return self.convergence_cache[agent_id]

        values = self.value_history.get(agent_id, [])

        if len(values) < window_size:
            return ConvergenceAnalysis(
                agent_id=agent_id,
                converged=False,
                convergence_rate=0.0,
                stability_score=0.0,
                oscillation_detected=False,
                oscillation_frequency=0.0,
                divergence_detected=False,
                trend='stable',
                recommendations=["Insufficient data for convergence analysis"]
            )

        # Calculate stability score (inverse of variance)
        recent_values = values[-window_size:]
        variance = np.var(recent_values)
        stability_score = 1.0 / (1.0 + variance)

        # Detect oscillation
        oscillation_detected, oscillation_freq = self._detect_oscillation(recent_values)

        # Detect divergence
        divergence_detected = self._detect_divergence(recent_values)

        # Determine trend
        trend = self._calculate_trend(recent_values)

        # Calculate convergence rate
        if len(values) >= window_size * 2:
            old_variance = np.var(values[-window_size*2:-window_size])
            convergence_rate = (old_variance - variance) / (old_variance + 1e-10)
        else:
            convergence_rate = 0.0

        # Determine if converged
        converged = (stability_score > 0.95 and
                    not oscillation_detected and
                    not divergence_detected and
                    convergence_rate > 0)

        # Generate recommendations
        recommendations = []
        if oscillation_detected:
            recommendations.append("Reduce learning rate to dampen oscillation")
        if divergence_detected:
            recommendations.append("CRITICAL: Value network diverging. Reduce learning rate immediately")
        if trend == 'decreasing' and not divergence_detected:
            recommendations.append("Value function declining - check reward function")
        if not converged and convergence_rate < 0.001:
            recommendations.append("Slow convergence - consider increasing learning rate slightly")

        analysis = ConvergenceAnalysis(
            agent_id=agent_id,
            converged=converged,
            convergence_rate=convergence_rate,
            stability_score=stability_score,
            oscillation_detected=oscillation_detected,
            oscillation_frequency=oscillation_freq,
            divergence_detected=divergence_detected,
            trend=trend,
            recommendations=recommendations
        )

        self.convergence_cache[agent_id] = analysis
        return analysis

    def compute_value_distribution(self, agent_id: str,
                                   num_bins: int = 50) -> ValueDistribution:
        """
        Compute the distribution of value predictions.

        Args:
            agent_id: Agent ID
            num_bins: Number of histogram bins

        Returns:
            ValueDistribution: Distribution statistics
        """
        if agent_id in self.distribution_cache:
            return self.distribution_cache[agent_id]

        values = self.value_history.get(agent_id, [])

        if not values:
            return ValueDistribution(
                agent_id=agent_id,
                mean=0.0,
                std=0.0,
                min=0.0,
                max=0.0,
                median=0.0,
                percentile_25=0.0,
                percentile_75=0.0,
                histogram=[]
            )

        values_array = np.array(values)

        # Compute statistics
        mean = float(np.mean(values_array))
        std = float(np.std(values_array))
        min_val = float(np.min(values_array))
        max_val = float(np.max(values_array))
        median = float(np.median(values_array))
        percentile_25 = float(np.percentile(values_array, 25))
        percentile_75 = float(np.percentile(values_array, 75))

        # Create histogram
        hist, bin_edges = np.histogram(values_array, bins=num_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        histogram = list(zip(bin_centers.tolist(), hist.tolist()))

        distribution = ValueDistribution(
            agent_id=agent_id,
            mean=mean,
            std=std,
            min=min_val,
            max=max_val,
            median=median,
            percentile_25=percentile_25,
            percentile_75=percentile_75,
            histogram=histogram
        )

        self.distribution_cache[agent_id] = distribution
        return distribution

    def _detect_oscillation(self, values: List[float],
                          threshold: float = 0.05) -> Tuple[bool, float]:
        """Detect oscillation in value sequence."""
        if len(values) < 10:
            return False, 0.0

        # Calculate autocorrelation at various lags
        values_array = np.array(values)
        normalized = (values_array - np.mean(values_array)) / (np.std(values_array) + 1e-10)

        # Check for periodic patterns
        max_autocorr = 0
        max_lag = 0

        for lag in range(1, min(20, len(values) // 2)):
            autocorr = np.corrcoef(normalized[:-lag], normalized[lag:])[0, 1]
            if abs(autocorr) > abs(max_autocorr):
                max_autocorr = autocorr
                max_lag = lag

        # Oscillation detected if strong negative autocorrelation
        oscillating = max_autocorr < -threshold

        # Estimate frequency
        frequency = 1.0 / max_lag if max_lag > 0 else 0.0

        return oscillating, frequency

    def _detect_divergence(self, values: List[float],
                          threshold: float = 0.5) -> bool:
        """Detect divergence in value sequence."""
        if len(values) < 10:
            return False

        # Check if values are growing unbounded
        recent_values = values[-10:]
        avg_change = np.mean(np.diff(recent_values))

        # Divergence if values are increasing rapidly
        if avg_change > threshold:
            return True

        # Check for NaN or Inf
        if any(not np.isfinite(v) for v in values):
            return True

        return False

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend of value sequence."""
        if len(values) < 3:
            return 'stable'

        # Linear regression to find trend
        x = np.arange(len(values))
        y = np.array(values)

        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]

        if abs(slope) < 0.001:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'

    def generate_debug_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive debug report.

        Returns:
            Dictionary containing all debug data and analysis
        """
        # Analyze all agents
        convergence_analyses = {}
        for agent_id in self.value_history:
            convergence_analyses[agent_id] = self.analyze_convergence(agent_id).to_dict()

        # Compute distributions
        distributions = {}
        for agent_id in self.value_history:
            distributions[agent_id] = self.compute_value_distribution(agent_id).to_dict()

        # Summary statistics
        total_updates = sum(len(events) for events in self.update_events.values())
        total_agents = len(self.value_history)

        converged_count = sum(1 for a in convergence_analyses.values() if a['converged'])
        oscillating_count = sum(1 for a in convergence_analyses.values() if a['oscillation_detected'])
        diverging_count = sum(1 for a in convergence_analyses.values() if a['divergence_detected'])

        report = {
            'colony_id': self.colony_id,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_agents': total_agents,
                'total_updates': total_updates,
                'converged_agents': converged_count,
                'oscillating_agents': oscillating_count,
                'diverging_agents': diverging_count
            },
            'update_events': {
                agent_id: [e.to_dict() for e in events]
                for agent_id, events in self.update_events.items()
            },
            'value_history': dict(self.value_history),
            'reward_history': dict(self.reward_history),
            'eligibility_traces': {
                agent_id: state.to_dict()
                for agent_id, state in self.eligibility_traces.items()
            },
            'convergence_analyses': convergence_analyses,
            'value_distributions': distributions,
            'learning_parameters': self.learning_params,
            'issues': self._identify_issues()
        }

        return report

    def _identify_issues(self) -> List[Dict[str, Any]]:
        """Identify common value network issues."""
        issues = []

        for agent_id in self.value_history:
            analysis = self.analyze_convergence(agent_id)

            if analysis.divergence_detected:
                issues.append({
                    'type': 'divergence',
                    'severity': 'critical',
                    'agent_id': agent_id,
                    'message': f'Agent {agent_id} value network is diverging',
                    'recommendation': 'Immediately reduce learning rate and check reward function'
                })

            if analysis.oscillation_detected:
                issues.append({
                    'type': 'oscillation',
                    'severity': 'warning',
                    'agent_id': agent_id,
                    'message': f'Agent {agent_id} value network is oscillating (freq: {analysis.oscillation_frequency:.2f})',
                    'recommendation': 'Reduce learning rate to dampen oscillation'
                })

            if analysis.trend == 'decreasing' and not analysis.divergence_detected:
                issues.append({
                    'type': 'declining_value',
                    'severity': 'warning',
                    'agent_id': agent_id,
                    'message': f'Agent {agent_id} value function is declining',
                    'recommendation': 'Review reward function and agent performance'
                })

        return issues

    def save_debug_report(self, filename: str = "value_network_debug.json") -> str:
        """
        Save debug report to file.

        Args:
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        report = self.generate_debug_report()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Debug report saved to: {output_path}")
        return str(output_path)

    def print_agent_summary(self, agent_id: str) -> None:
        """Print a summary of an agent's value network state."""
        if agent_id not in self.value_history:
            print(f"Agent {agent_id} not found")
            return

        analysis = self.analyze_convergence(agent_id)
        distribution = self.compute_value_distribution(agent_id)

        print(f"\n{'=' * 80}")
        print(f"Value Network Summary: {agent_id}")
        print(f"{'=' * 80}")
        print(f"Current Value: {self.value_history[agent_id][-1]:.4f}")
        print(f"Total Updates: {len(self.value_history[agent_id])}")
        print(f"Converged: {analysis.converged}")
        print(f"Stability Score: {analysis.stability_score:.3f}")
        print(f"Trend: {analysis.trend}")

        if analysis.oscillation_detected:
            print(f"⚠️  OSCILLATION DETECTED (freq: {analysis.oscillation_frequency:.2f})")
        if analysis.divergence_detected:
            print(f"⚠️  DIVERGENCE DETECTED - CRITICAL")

        print(f"\nValue Distribution:")
        print(f"  Mean: {distribution.mean:.4f}")
        print(f"  Std: {distribution.std:.4f}")
        print(f"  Range: [{distribution.min:.4f}, {distribution.max:.4f}]")

        if analysis.recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(analysis.recommendations, 1):
                print(f"  {i}. {rec}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python value_network_debugger.py <colony_id> [command]")
        print("\nCommands:")
        print("  load <file>               - Load value update data from file")
        print("  report                    - Generate debug report")
        print("  summary <agent_id>        - Print agent summary")
        print("  converge <agent_id>       - Analyze convergence")
        sys.exit(1)

    colony_id = sys.argv[1]
    debugger = ValueNetworkDebugger(colony_id)

    if len(sys.argv) < 3:
        print("No command specified")
        sys.exit(1)

    command = sys.argv[2]

    if command == "load" and len(sys.argv) >= 4:
        # Load value update data from file
        data_file = sys.argv[3]
        with open(data_file, 'r') as f:
            data = json.load(f)

        if 'updates' in data:
            for update in data['updates']:
                debugger.record_update(
                    update['agentId'],
                    update['oldValue'],
                    update['newValue'],
                    update['reward'],
                    update['tdError'],
                    update.get('eligibilityTrace', 0),
                    update.get('learningRate', 0.1),
                    update.get('lambda', 0.9)
                )

        if 'eligibilityTraces' in data:
            for agent_id, traces in data['eligibilityTraces'].items():
                debugger.record_eligibility_traces(agent_id, traces)

        print(f"Loaded data for {len(debugger.value_history)} agents")

    elif command == "report":
        debugger.save_debug_report()

    elif command == "summary" and len(sys.argv) >= 4:
        debugger.print_agent_summary(sys.argv[3])

    elif command == "converge" and len(sys.argv) >= 4:
        analysis = debugger.analyze_convergence(sys.argv[3])
        print(f"Convergence Analysis for {sys.argv[3]}:")
        print(f"  Converged: {analysis.converged}")
        print(f"  Stability: {analysis.stability_score:.3f}")
        print(f"  Trend: {analysis.trend}")
        print(f"  Oscillation: {analysis.oscillation_detected}")
        print(f"  Divergence: {analysis.divergence_detected}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
