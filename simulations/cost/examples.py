"""
Example Usage of POLLN Cost Simulations

This file demonstrates how to use the cost simulations programmatically.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def example_1_basic_cost_comparison():
    """Example 1: Basic cost comparison between POLLN and GPT-4"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Cost Comparison")
    print("=" * 80)

    from token_cost_analysis import TokenCostAnalyzer, TokenProfile

    analyzer = TokenCostAnalyzer()

    # Define your workload
    profile = TokenProfile(
        input_tokens=2000,  # Average input tokens
        output_tokens=800,   # Average output tokens
    )

    # Calculate costs for 1000 requests
    gpt4_cost = analyzer.calculate_monolithic_cost('gpt-4', profile, 1000)
    polln_cost = analyzer.calculate_polln_cost(profile, 1000)

    # Print results
    print(f"\nGPT-4 Cost:")
    print(f"  Total: ${gpt4_cost['total_cost']:.2f}")
    print(f"  Per request: ${gpt4_cost['cost_per_request']:.4f}")

    print(f"\nPOLLN Cost:")
    print(f"  Total: ${polln_cost['total_cost']:.2f}")
    print(f"  Per request: ${polln_cost['cost_per_request']:.4f}")

    savings = ((gpt4_cost['total_cost'] - polln_cost['total_cost']) /
               gpt4_cost['total_cost']) * 100
    print(f"\nSavings: {savings:.1f}%")


def example_2_compute_efficiency():
    """Example 2: Analyze compute efficiency"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Compute Efficiency Analysis")
    print("=" * 80)

    from compute_efficiency import ComputeEfficiencyAnalyzer, ModelSize

    analyzer = ComputeEfficiencyAnalyzer()

    # Compare monolithic vs POLLN
    comparison = analyzer.compare_approaches()

    print(f"\nMonolithic (1B model):")
    print(f"  Quality: {comparison['monolithic']['quality']*100:.1f}%")
    print(f"  Cost: ${comparison['monolithic']['cost'].cost_usd:.2f}")

    print(f"\nPOLLN (100 × 10M agents):")
    print(f"  Quality: {comparison['polln']['quality']*100:.1f}%")
    print(f"  Cost: ${comparison['polln']['cost'].cost_usd:.2f}")

    print(f"\nComparison:")
    print(f"  Quality ratio: {comparison['comparison']['quality_ratio']*100:.1f}%")
    print(f"  Cost ratio: {comparison['comparison']['cost_ratio']*100:.1f}%")


def example_3_find_break_even():
    """Example 3: Find break-even point"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Break-Even Analysis")
    print("=" * 80)

    from break_even_analysis import BreakEvenAnalyzer

    analyzer = BreakEvenAnalyzer()

    # Test different request volumes
    print("\nBreak-even analysis for different request volumes:")
    print(f"{'Requests/Day':<15} {'Break-Even':<15} {'90-Day ROI':<15}")
    print("-" * 45)

    for requests in [50, 100, 200, 500, 1000]:
        bre_days, _ = analyzer.find_break_even_point(requests)
        roi = analyzer.calculate_roi(requests, 90)

        bre_str = f"Day {bre_days}" if bre_days else ">365 days"
        print(f"{requests:<15} {bre_str:<15} {roi:>14.1f}%")


def example_4_scaling_analysis():
    """Example 4: Dynamic scaling analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Dynamic Scaling Analysis")
    print("=" * 80)

    from dynamic_scaling import DynamicScalingAnalyzer, WorkloadPattern

    analyzer = DynamicScalingAnalyzer()

    # Compare scaling strategies for spiky workload
    workload = analyzer.generate_workload(WorkloadPattern.SPIKY, hours=168)

    # Static scaling
    peak_load = int(workload.max())
    from dynamic_scaling import ResourceConfig
    static_config = ResourceConfig(
        'Static',
        num_agents=int(peak_load // 50),
        hourly_cost=int(peak_load // 50) / 10 * 1.0,
        max_requests_per_hour=peak_load,
    )
    static_result = analyzer.simulate_static_scaling(workload, static_config)

    # Auto-scaling
    autoscaling_result = analyzer.simulate_autoscaling(
        workload, analyzer.autoscaling_policy
    )

    print(f"\nStatic Scaling:")
    print(f"  Cost: ${static_result.total_cost:.2f}/week")
    print(f"  Utilization: {static_result.avg_utilization*100:.1f}%")

    print(f"\nAuto-scaling:")
    print(f"  Cost: ${autoscaling_result.total_cost:.2f}/week")
    print(f"  Utilization: {autoscaling_result.avg_utilization*100:.1f}%")

    savings = ((static_result.total_cost - autoscaling_result.total_cost) /
               static_result.total_cost) * 100
    print(f"\nSavings: {savings:.1f}%")


def example_5_custom_scenario():
    """Example 5: Custom scenario analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom Scenario Analysis")
    print("=" * 80)

    from token_cost_analysis import TokenCostAnalyzer, TokenProfile
    from break_even_analysis import BreakEvenAnalyzer

    # Define your custom scenario
    daily_requests = 250
    duration_days = 180
    input_tokens = 3500
    output_tokens = 1200

    print(f"\nScenario Parameters:")
    print(f"  Daily requests: {daily_requests}")
    print(f"  Duration: {duration_days} days")
    print(f"  Input tokens: {input_tokens}")
    print(f"  Output tokens: {output_tokens}")

    # Token cost analysis
    token_analyzer = TokenCostAnalyzer()
    profile = TokenProfile(input_tokens, output_tokens)

    gpt4_cost = token_analyzer.calculate_monolithic_cost(
        'gpt-4', profile, daily_requests * duration_days
    )
    polln_cost = token_analyzer.calculate_polln_cost(
        profile, daily_requests * duration_days
    )

    print(f"\nCost Analysis:")
    print(f"  GPT-4 total: ${gpt4_cost['total_cost']:.2f}")
    print(f"  POLLN total: ${polln_cost['total_cost']:.2f}")
    print(f"  Savings: ${gpt4_cost['total_cost'] - polln_cost['total_cost']:.2f}")

    # Break-even analysis
    bre_analyzer = BreakEvenAnalyzer()
    bre_days, _ = bre_analyzer.find_break_even_point(daily_requests)

    print(f"\nBreak-even:")
    print(f"  Break-even at: Day {bre_days if bre_days else '>365'}")
    print(f"  Duration: {duration_days} days")

    if bre_days and bre_days <= duration_days:
        days_in_profit = duration_days - bre_days
        daily_savings = (gpt4_cost['total_cost'] - polln_cost['total_cost']) / duration_days
        profit_savings = days_in_profit * daily_savings
        print(f"  Days in profit: {days_in_profit}")
        print(f"  Profit period savings: ${profit_savings:.2f}")


def example_6_batch_analysis():
    """Example 6: Batch analysis for multiple scenarios"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Batch Scenario Analysis")
    print("=" * 80)

    from token_cost_analysis import TokenCostAnalyzer, TokenProfile

    analyzer = TokenCostAnalyzer()

    # Define scenarios
    scenarios = [
        ("Simple", TokenProfile(500, 200)),
        ("Medium", TokenProfile(2000, 800)),
        ("Complex", TokenProfile(5000, 2000)),
        ("Very Complex", TokenProfile(10000, 4000)),
    ]

    print(f"\n{'Complexity':<15} {'GPT-4':<12} {'POLLN':<12} {'Savings':<10}")
    print("-" * 50)

    for name, profile in scenarios:
        gpt4 = analyzer.calculate_monolithic_cost('gpt-4', profile, 1000)
        polln = analyzer.calculate_polln_cost(profile, 1000)

        savings = ((gpt4['total_cost'] - polln['total_cost']) /
                   gpt4['total_cost']) * 100

        print(f"{name:<15} ${gpt4['total_cost']:>10.2f} ${polln['total_cost']:>10.2f} {savings:>9.1f}%")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("POLLN COST SIMULATION EXAMPLES")
    print("=" * 80)

    examples = [
        example_1_basic_cost_comparison,
        example_2_compute_efficiency,
        example_3_find_break_even,
        example_4_scaling_analysis,
        example_5_custom_scenario,
        example_6_batch_analysis,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError running example: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
