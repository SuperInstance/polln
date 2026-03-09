"""
Pareto-Based Configuration Recommendation Engine

Recommends optimal POLLN configurations based on user priorities
and scenario requirements using Pareto-optimal solution sets.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class UserPriorities:
    """User priorities for configuration recommendation."""
    accuracy: float  # 0-1, importance of accuracy
    cost: float  # 0-1, importance of low cost
    latency: float  # 0-1, importance of low latency
    availability: float  # 0-1, importance of high availability
    scalability: float  # 0-1, importance of throughput
    complexity: float  # 0-1, importance of low complexity (inverse)

    def normalize(self) -> 'UserPriorities':
        """Normalize priorities to sum to 1."""
        total = sum([self.accuracy, self.cost, self.latency,
                    self.availability, self.scalability, self.complexity])
        if total == 0:
            return self
        return UserPriorities(
            accuracy=self.accuracy / total,
            cost=self.cost / total,
            latency=self.latency / total,
            availability=self.availability / total,
            scalability=self.scalability / total,
            complexity=self.complexity / total
        )


@dataclass
class Scenario:
    """Predefined scenario with priorities."""
    name: str
    description: str
    priorities: UserPriorities
    constraints: Dict[str, Any]

    @classmethod
    def production(cls) -> 'Scenario':
        """Production scenario: high availability, balanced cost."""
        return Scenario(
            name="PRODUCTION",
            description="High-availability production deployment",
            priorities=UserPriorities(
                accuracy=0.2,
                cost=0.2,
                latency=0.15,
                availability=0.3,
                scalability=0.1,
                complexity=0.05
            ).normalize(),
            constraints={
                'min_availability': 0.999,
                'max_latency_ms': 1000,
                'max_cost_multiplier': 2.0
            }
        )

    @classmethod
    def development(cls) -> 'Scenario':
        """Development scenario: low cost, high flexibility."""
        return Scenario(
            name="DEVELOPMENT",
            description="Development and testing environment",
            priorities=UserPriorities(
                accuracy=0.1,
                cost=0.4,
                latency=0.1,
                availability=0.1,
                scalability=0.1,
                complexity=0.2
            ).normalize(),
            constraints={
                'min_availability': 0.95,
                'max_latency_ms': 5000,
                'max_cost_multiplier': 1.5
            }
        )

    @classmethod
    def edge(cls) -> 'Scenario':
        """Edge scenario: low latency, low cost."""
        return Scenario(
            name="EDGE",
            description="Edge deployment with limited resources",
            priorities=UserPriorities(
                accuracy=0.15,
                cost=0.3,
                latency=0.35,
                availability=0.1,
                scalability=0.05,
                complexity=0.05
            ).normalize(),
            constraints={
                'min_availability': 0.99,
                'max_latency_ms': 200,
                'max_cost_multiplier': 1.2,
                'max_model_size': 100
            }
        )

    @classmethod
    def research(cls) -> 'Scenario':
        """Research scenario: maximum quality, ignore cost."""
        return Scenario(
            name="RESEARCH",
            description="Research experimentation with maximum quality",
            priorities=UserPriorities(
                accuracy=0.5,
                cost=0.05,
                latency=0.1,
                availability=0.15,
                scalability=0.1,
                complexity=0.1
            ).normalize(),
            constraints={
                'min_availability': 0.95,
                'max_latency_ms': 10000,
                'max_cost_multiplier': 5.0
            }
        )

    @classmethod
    def real_time(cls) -> 'Scenario':
        """Real-time scenario: minimum latency."""
        return Scenario(
            name="REALTIME",
            description="Real-time applications with strict latency requirements",
            priorities=UserPriorities(
                accuracy=0.15,
                cost=0.15,
                latency=0.5,
                availability=0.15,
                scalability=0.03,
                complexity=0.02
            ).normalize(),
            constraints={
                'min_availability': 0.99,
                'max_latency_ms': 100,
                'max_cost_multiplier': 3.0
            }
        )

    @classmethod
    def batch(cls) -> 'Scenario':
        """Batch scenario: maximum throughput, low cost."""
        return Scenario(
            name="BATCH",
            description="Batch processing with high throughput requirements",
            priorities=UserPriorities(
                accuracy=0.2,
                cost=0.3,
                latency=0.05,
                availability=0.15,
                scalability=0.25,
                complexity=0.05
            ).normalize(),
            constraints={
                'min_availability': 0.98,
                'max_latency_ms': 10000,
                'max_cost_multiplier': 1.5
            }
        )


class ConfigurationDatabase:
    """Database of Pareto-optimal configurations from all frontiers."""

    def __init__(self, data_dir: str = None):
        """Load configurations from JSON files."""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'
        self.configs = {}
        self.load_all()

    def load_all(self):
        """Load all tier configurations."""
        json_files = {
            'accuracy_cost': 'accuracy_cost_tiers.json',
            'speed_quality': 'speed_quality_tiers.json',
            'robustness_efficiency': 'robustness_efficiency_tiers.json',
            'scalability_complexity': 'scalability_complexity_tiers.json'
        }

        for category, filename in json_files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    self.configs[category] = json.load(f)
                print(f"Loaded {len(self.configs[category])} configs from {category}")
            else:
                print(f"Warning: {filepath} not found, using defaults")
                self.configs[category] = self._get_default_configs(category)

    def _get_default_configs(self, category: str) -> Dict:
        """Generate default configs if file not found."""
        if category == 'accuracy_cost':
            return {
                'BUDGET': {'model_size': '10M', 'expected_accuracy': 0.85, 'expected_hourly_cost': 0.5},
                'STANDARD': {'model_size': '100M', 'expected_accuracy': 0.90, 'expected_hourly_cost': 1.0},
                'PERFORMANCE': {'model_size': '500M', 'expected_accuracy': 0.93, 'expected_hourly_cost': 2.0}
            }
        # Add default configs for other categories as needed
        return {}

    def get_config(self, category: str, tier: str) -> Optional[Dict]:
        """Get specific configuration."""
        return self.configs.get(category, {}).get(tier)

    def all_tiers(self, category: str) -> List[str]:
        """Get all available tiers for a category."""
        return list(self.configs.get(category, {}).keys())


class RecommendationEngine:
    """Engine for recommending optimal configurations."""

    def __init__(self, config_db: ConfigurationDatabase = None):
        self.config_db = config_db or ConfigurationDatabase()

    def score_configuration(self, config: Dict, priorities: UserPriorities) -> float:
        """Score a configuration based on user priorities (higher is better)."""
        score = 0.0

        # Accuracy score (normalize to 0-1)
        accuracy = config.get('expected_accuracy', config.get('expected_quality', 0.85))
        score += priorities.accuracy * accuracy

        # Cost score (invert, lower is better)
        cost = config.get('expected_hourly_cost', config.get('expected_cost_multiplier', 1.0))
        # Normalize cost: assume 0.1-10 range
        normalized_cost = 1 - min(1, (cost - 0.1) / 9.9)
        score += priorities.cost * normalized_cost

        # Latency score (invert, lower is better)
        latency_ms = config.get('expected_latency_ms', 1000)
        # Normalize latency: assume 10-10000ms range
        normalized_latency = 1 - min(1, (latency_ms - 10) / 9990)
        score += priorities.latency * normalized_latency

        # Availability score
        availability_str = config.get('expected_availability', '99.0%')
        if isinstance(availability_str, str):
            availability = float(availability_str.rstrip('%')) / 100
        else:
            availability = availability_str
        score += priorities.availability * availability

        # Throughput score
        throughput = config.get('expected_throughput', 100)
        # Normalize throughput: assume 10-10000 range
        normalized_throughput = min(1, (throughput - 10) / 9990)
        score += priorities.scalability * normalized_throughput

        # Complexity score (invert, lower is better)
        complexity = config.get('expected_complexity', 0.5)
        normalized_complexity = 1 - complexity
        score += priorities.complexity * normalized_complexity

        return score

    def recommend_by_scenario(self, scenario: Scenario) -> Tuple[str, Dict, float]:
        """Recommend best configuration for a scenario."""
        best_score = -1
        best_category = None
        best_tier = None
        best_config = None

        # Search all configurations
        for category in self.config_db.configs.keys():
            for tier, config in self.config_db.configs[category].items():
                # Check constraints
                if not self._check_constraints(config, scenario.constraints):
                    continue

                # Score configuration
                score = self.score_configuration(config, scenario.priorities)

                if score > best_score:
                    best_score = score
                    best_category = category
                    best_tier = tier
                    best_config = config

        if best_config is None:
            # Fallback: return best scoring without constraints
            return self.recommend_by_priorities(scenario.priorities)

        return f"{best_category}_{best_tier}", best_config, best_score

    def recommend_by_priorities(self, priorities: UserPriorities) -> Tuple[str, Dict, float]:
        """Recommend best configuration by priorities only (no constraints)."""
        best_score = -1
        best_category = None
        best_tier = None
        best_config = None

        for category in self.config_db.configs.keys():
            for tier, config in self.config_db.configs[category].items():
                score = self.score_configuration(config, priorities)

                if score > best_score:
                    best_score = score
                    best_category = category
                    best_tier = tier
                    best_config = config

        return f"{best_category}_{best_tier}", best_config, best_score

    def recommend_multi_objective(self,
                                 priorities: UserPriorities,
                                 constraints: Dict[str, Any] = None,
                                 top_k: int = 5) -> List[Tuple[str, Dict, float]]:
        """Recommend top-k configurations across all categories."""
        results = []

        for category in self.config_db.configs.keys():
            for tier, config in self.config_db.configs[category].items():
                # Check constraints
                if constraints and not self._check_constraints(config, constraints):
                    continue

                # Score configuration
                score = self.score_configuration(config, priorities)
                results.append((f"{category}_{tier}", config, score))

        # Sort by score
        results.sort(key=lambda x: x[2], reverse=True)

        return results[:top_k]

    def _check_constraints(self, config: Dict, constraints: Dict[str, Any]) -> bool:
        """Check if configuration meets constraints."""
        # Availability constraint
        if 'min_availability' in constraints:
            availability_str = config.get('expected_availability', '99.0%')
            if isinstance(availability_str, str):
                availability = float(availability_str.rstrip('%')) / 100
            else:
                availability = availability_str
            if availability < constraints['min_availability']:
                return False

        # Latency constraint
        if 'max_latency_ms' in constraints:
            latency = config.get('expected_latency_ms', 1000)
            if latency > constraints['max_latency_ms']:
                return False

        # Cost constraint
        if 'max_cost_multiplier' in constraints:
            cost = config.get('expected_cost_multiplier', config.get('expected_hourly_cost', 1.0))
            if cost > constraints['max_cost_multiplier']:
                return False

        # Model size constraint
        if 'max_model_size' in constraints:
            model_size_str = config.get('model_size', '100M')
            model_size = int(model_size_str.rstrip('M'))
            if model_size > constraints['max_model_size']:
                return False

        return True

    def explain_recommendation(self,
                              config_name: str,
                              config: Dict,
                              priorities: UserPriorities) -> str:
        """Generate explanation for recommendation."""
        explanation = f"\nRecommended Configuration: {config_name}\n"
        explanation += "=" * 60 + "\n\n"

        # Key metrics
        explanation += "Key Metrics:\n"
        for key in ['expected_accuracy', 'expected_quality', 'expected_latency_ms',
                   'expected_availability', 'expected_throughput', 'expected_hourly_cost',
                   'expected_cost_multiplier', 'expected_complexity']:
            if key in config:
                explanation += f"  {key}: {config[key]}\n"

        explanation += "\nConfiguration Details:\n"
        for key, value in config.items():
            if not key.startswith('expected_'):
                explanation += f"  {key}: {value}\n"

        explanation += "\nPriority Match:\n"
        explanation += f"  Accuracy: {priorities.accuracy:.2f}\n"
        explanation += f"  Cost: {priorities.cost:.2f}\n"
        explanation += f"  Latency: {priorities.latency:.2f}\n"
        explanation += f"  Availability: {priorities.availability:.2f}\n"
        explanation += f"  Scalability: {priorities.scalability:.2f}\n"
        explanation += f"  Complexity: {priorities.complexity:.2f}\n"

        return explanation


def interactive_recommendation():
    """Interactive recommendation CLI."""
    print("\n" + "=" * 60)
    print("POLLN Configuration Recommendation Engine")
    print("=" * 60)

    engine = RecommendationEngine()

    # Select scenario or custom priorities
    print("\nSelect a scenario:")
    scenarios = {
        '1': Scenario.production(),
        '2': Scenario.development(),
        '3': Scenario.edge(),
        '4': Scenario.research(),
        '5': Scenario.real_time(),
        '6': Scenario.batch(),
        '7': None  # Custom
    }

    for key, scenario in scenarios.items():
        if scenario:
            print(f"  {key}. {scenario.name}: {scenario.description}")
        else:
            print(f"  {key}. Custom priorities")

    choice = input("\nEnter choice (1-7): ").strip()

    if choice == '7' or choice not in scenarios:
        # Custom priorities
        print("\nEnter priority weights (0-1):")
        priorities = UserPriorities(
            accuracy=float(input("  Accuracy: ").strip() or "0.2"),
            cost=float(input("  Cost: ").strip() or "0.2"),
            latency=float(input("  Latency: ").strip() or "0.2"),
            availability=float(input("  Availability: ").strip() or "0.2"),
            scalability=float(input("  Scalability: ").strip() or "0.1"),
            complexity=float(input("  Complexity (inverse): ").strip() or "0.1")
        ).normalize()

        scenario = Scenario("CUSTOM", "Custom configuration", priorities, {})

    else:
        scenario = scenarios[choice]

    # Get recommendation
    config_name, config, score = engine.recommend_by_scenario(scenario)

    # Display recommendation
    print(engine.explain_recommendation(config_name, config, scenario.priorities))

    # Show top 5 alternatives
    print("\nTop 5 Alternative Configurations:")
    print("-" * 60)
    top_5 = engine.recommend_multi_objective(
        scenario.priorities,
        scenario.constraints,
        top_k=5
    )

    for i, (name, cfg, score) in enumerate(top_5, 1):
        print(f"\n{i}. {name} (score: {score:.3f})")
        # Show key metrics only
        for key in ['expected_accuracy', 'expected_latency_ms', 'expected_availability']:
            if key in cfg:
                print(f"    {key}: {cfg[key]}")

    return config_name, config


def generate_recommendation_report(output_dir: str):
    """Generate comprehensive recommendation report."""
    engine = RecommendationEngine()
    output_path = Path(output_dir) / 'recommendation_report.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = []
    report.append("# POLLN Configuration Recommendation Report\n")
    report.append("*Generated by Pareto-based recommendation engine*\n\n")

    # Predefined scenarios
    scenarios = [
        Scenario.production(),
        Scenario.development(),
        Scenario.edge(),
        Scenario.research(),
        Scenario.real_time(),
        Scenario.batch()
    ]

    for scenario in scenarios:
        config_name, config, score = engine.recommend_by_scenario(scenario)

        report.append(f"## {scenario.name}\n")
        report.append(f"{scenario.description}\n\n")
        report.append(f"**Recommended:** {config_name}\n\n")

        # Key metrics
        report.append("### Key Metrics\n")
        for key in ['expected_accuracy', 'expected_latency_ms', 'expected_availability',
                   'expected_throughput', 'expected_hourly_cost']:
            if key in config:
                report.append(f"- **{key}:** {config[key]}\n")

        report.append("\n### Configuration\n")
        for key, value in config.items():
            if not key.startswith('expected_'):
                report.append(f"- **{key}:** {value}\n")

        report.append("\n---\n\n")

    # Write report
    with open(output_path, 'w') as f:
        f.write(''.join(report))

    print(f"Recommendation report saved to {output_path}")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--report':
        # Generate report
        output_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).parent.parent.parent / 'outputs')
        generate_recommendation_report(output_dir)
    else:
        # Interactive mode
        interactive_recommendation()


if __name__ == '__main__':
    main()
