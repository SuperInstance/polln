"""
Example Usage of Multiobjective Pareto Optimization

Demonstrates how to use the Pareto optimization system for POLLN configuration.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from recommendation_engine import (
    Scenario,
    UserPriorities,
    RecommendationEngine,
    ConfigurationDatabase
)


def example_1_scenario_based():
    """Example 1: Use predefined scenarios."""
    print("\n" + "=" * 70)
    print("Example 1: Scenario-Based Configuration")
    print("=" * 70)

    engine = RecommendationEngine()

    # Production scenario
    print("\n--- Production Deployment ---")
    config_name, config, score = engine.recommend_by_scenario(Scenario.production())
    print(f"Recommended: {config_name}")
    print(f"Score: {score:.3f}")
    print(f"Expected Availability: {config.get('expected_availability', 'N/A')}")
    print(f"Expected Cost Multiplier: {config.get('expected_cost_multiplier', 'N/A')}")

    # Edge scenario
    print("\n--- Edge Deployment ---")
    config_name, config, score = engine.recommend_by_scenario(Scenario.edge())
    print(f"Recommended: {config_name}")
    print(f"Score: {score:.3f}")
    print(f"Expected Latency: {config.get('expected_latency_ms', 'N/A')}ms")


def example_2_custom_priorities():
    """Example 2: Define custom priorities."""
    print("\n" + "=" * 70)
    print("Example 2: Custom Priorities")
    print("=" * 70)

    engine = RecommendationEngine()

    # Define custom priorities
    priorities = UserPriorities(
        accuracy=0.35,    # High importance
        cost=0.25,        # Medium importance
        latency=0.25,     # Medium importance
        availability=0.10, # Lower importance
        scalability=0.03, # Low importance
        complexity=0.02   # Low importance
    ).normalize()

    print("\nPriorities:")
    print(f"  Accuracy: {priorities.accuracy:.2f}")
    print(f"  Cost: {priorities.cost:.2f}")
    print(f"  Latency: {priorities.latency:.2f}")
    print(f"  Availability: {priorities.availability:.2f}")
    print(f"  Scalability: {priorities.scalability:.2f}")
    print(f"  Complexity: {priorities.complexity:.2f}")

    # Get recommendation
    config_name, config, score = engine.recommend_by_priorities(priorities)

    print(f"\nRecommended: {config_name}")
    print(f"Score: {score:.3f}")
    print(f"Expected Accuracy: {config.get('expected_accuracy', config.get('expected_quality', 'N/A'))}")


def example_3_multiobjective_search():
    """Example 3: Get top-k configurations."""
    print("\n" + "=" * 70)
    print("Example 3: Multi-Objective Search (Top 5)")
    print("=" * 70)

    engine = RecommendationEngine()

    # Define priorities
    priorities = UserPriorities(
        accuracy=0.4,
        cost=0.3,
        latency=0.2,
        availability=0.1,
        scalability=0.0,
        complexity=0.0
    ).normalize()

    # Define constraints
    constraints = {
        'min_availability': 0.99,
        'max_latency_ms': 1000,
        'max_cost_multiplier': 2.0
    }

    print("\nConstraints:")
    print(f"  Min Availability: {constraints['min_availability'] * 100}%")
    print(f"  Max Latency: {constraints['max_latency_ms']}ms")
    print(f"  Max Cost: {constraints['max_cost_multiplier']}x")

    # Get top 5
    top_5 = engine.recommend_multi_objective(
        priorities=priorities,
        constraints=constraints,
        top_k=5
    )

    print("\nTop 5 Configurations:")
    for i, (name, config, score) in enumerate(top_5, 1):
        print(f"\n{i}. {name} (score: {score:.3f})")
        # Show key metrics
        if 'expected_accuracy' in config:
            print(f"   Accuracy: {config['expected_accuracy']:.3f}")
        if 'expected_latency_ms' in config:
            print(f"   Latency: {config['expected_latency_ms']:.1f}ms")
        if 'expected_availability' in config:
            print(f"   Availability: {config['expected_availability']}")


def example_4_configuration_combination():
    """Example 4: Combine configurations from multiple tiers."""
    print("\n" + "=" * 70)
    print("Example 4: Configuration Combination")
    print("=" * 70)

    db = ConfigurationDatabase()

    # Get configurations from different categories
    speed_config = db.get_config('speed_quality', 'REALTIME')
    robustness_config = db.get_config('robustness_efficiency', 'HIGH')

    if speed_config and robustness_config:
        # Combine them (later configs override earlier ones)
        combined = {**speed_config, **robustness_config}

        print("\nCombined Configuration:")
        print("  Speed tier: REALTIME")
        print("  Robustness tier: HIGH")
        print("\n  Key parameters:")
        if 'model_size' in combined:
            print(f"    Model: {combined['model_size']}")
        if 'expected_latency_ms' in combined:
            print(f"    Latency: {combined['expected_latency_ms']}ms")
        if 'expected_availability' in combined:
            print(f"    Availability: {combined['expected_availability']}")
        if 'replication_factor' in combined:
            print(f"    Replication: {combined['replication_factor']}x")


def example_5_constraint_filtering():
    """Example 5: Filter configurations by constraints."""
    print("\n" + "=" * 70)
    print("Example 5: Constraint-Based Filtering")
    print("=" * 70)

    db = ConfigurationDatabase()

    # Define strict constraints
    constraints = {
        'min_availability': 0.999,
        'max_latency_ms': 500,
        'max_cost_multiplier': 1.5
    }

    print("\nConstraints:")
    print(f"  Availability >= {constraints['min_availability'] * 100}%")
    print(f"  Latency <= {constraints['max_latency_ms']}ms")
    print(f"  Cost <= {constraints['max_cost_multiplier']}x")

    # Find matching configurations
    matches = []
    for category in ['speed_quality', 'robustness_efficiency', 'accuracy_cost']:
        for tier in db.all_tiers(category):
            config = db.get_config(category, tier)
            if config and meets_constraints(config, constraints):
                matches.append((f"{category}_{tier}", config))

    print(f"\nFound {len(matches)} matching configurations:")
    for name, config in matches[:5]:  # Show first 5
        print(f"\n  {name}:")
        if 'expected_latency_ms' in config:
            print(f"    Latency: {config['expected_latency_ms']}ms")
        if 'expected_availability' in config:
            print(f"    Availability: {config['expected_availability']}")
        if 'expected_cost_multiplier' in config:
            print(f"    Cost: {config['expected_cost_multiplier']}x")


def meets_constraints(config: dict, constraints: dict) -> bool:
    """Check if configuration meets constraints."""
    # Availability constraint
    if 'min_availability' in constraints:
        avail_str = config.get('expected_availability', '0%')
        if isinstance(avail_str, str):
            availability = float(avail_str.rstrip('%')) / 100
        else:
            availability = avail_str
        if availability < constraints['min_availability']:
            return False

    # Latency constraint
    if 'max_latency_ms' in constraints:
        latency = config.get('expected_latency_ms', float('inf'))
        if latency > constraints['max_latency_ms']:
            return False

    # Cost constraint
    if 'max_cost_multiplier' in constraints:
        cost = config.get('expected_cost_multiplier', float('inf'))
        if cost > constraints['max_cost_multiplier']:
            return False

    return True


def example_6_cost_analysis():
    """Example 6: Analyze cost vs quality tradeoff."""
    print("\n" + "=" * 70)
    print("Example 6: Cost vs Quality Analysis")
    print("=" * 70)

    db = ConfigurationDatabase()

    # Get accuracy/cost tiers
    accuracy_cost_configs = db.configs.get('accuracy_cost', {})

    if not accuracy_cost_configs:
        print("No accuracy/cost configurations found")
        return

    print("\nCost vs Quality Tiers:")
    print(f"{'Tier':<15} {'Accuracy':<12} {'Cost':<12} {'Cost/1% Acc':<15}")
    print("-" * 60)

    for tier_name in ['BUDGET', 'STANDARD', 'PERFORMANCE', 'PREMIUM', 'MAXIMUM']:
        if tier_name not in accuracy_cost_configs:
            continue

        config = accuracy_cost_configs[tier_name]
        accuracy = config.get('expected_accuracy', 0)
        cost = config.get('expected_hourly_cost', 0)
        cost_per_accuracy = cost / (accuracy * 100) if accuracy > 0 else 0

        print(f"{tier_name:<15} {accuracy:<12.3f} ${cost:<11.2f} ${cost_per_accuracy:<14.4f}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("POLLN Multiobjective Pareto Optimization - Examples")
    print("=" * 70)

    try:
        example_1_scenario_based()
        example_2_custom_priorities()
        example_3_multiobjective_search()
        example_4_configuration_combination()
        example_5_constraint_filtering()
        example_6_cost_analysis()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you've run the optimizations first:")
        print("  python run_all.py")


if __name__ == '__main__':
    main()
