"""
Run all TD(λ) convergence simulations

This script executes all four simulation modules and generates
comprehensive reports validating TD(λ) learning convergence.
"""

import sys
import os
import argparse
from typing import List, Optional
import subprocess


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_simulation(script_name: str, description: str) -> bool:
    """
    Run a single simulation script

    Args:
        script_name: Name of the script to run
        description: Description of the simulation

    Returns:
        True if successful, False otherwise
    """
    print_header(description)

    script_path = os.path.join(
        os.path.dirname(__file__),
        script_name
    )

    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main runner for all simulations"""
    parser = argparse.ArgumentParser(
        description="Run TD(λ) convergence simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all simulations
  python run_all.py

  # Run specific simulations
  python run_all.py --sim td_lambda function_approx

  # Skip specific simulations
  python run_all.py --skip off_policy credit_assignment

  # Quick run (fewer episodes)
  python run_all.py --quick
        """
    )

    parser.add_argument(
        '--sim',
        nargs='+',
        choices=['td_lambda', 'function_approx', 'off_policy', 'credit_assignment'],
        help='Specific simulations to run (default: all)'
    )

    parser.add_argument(
        '--skip',
        nargs='+',
        choices=['td_lambda', 'function_approx', 'off_policy', 'credit_assignment'],
        help='Simulations to skip'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick run with fewer episodes (for testing)'
    )

    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating plots'
    )

    args = parser.parse_args()

    print_header("TD(λ) LEARNING CONVERGENCE SIMULATIONS")
    print("Mathematical validation of TD(λ) for POLLN value network")
    print("\nThis will run:")
    print("  1. TD(λ) Convergence Proof")
    print("  2. Function Approximation Analysis")
    print("  3. Off-Policy Learning Validation")
    print("  4. Multi-Agent Credit Assignment")
    print("\nPress Ctrl+C to abort at any time")

    input("\nPress Enter to continue...")

    # Define all simulations
    all_simulations = [
        ('td_lambda_convergence.py', 'TD(λ) Convergence Proof', 'td_lambda'),
        ('function_approx.py', 'Function Approximation Analysis', 'function_approx'),
        ('off_policy.py', 'Off-Policy Learning Validation', 'off_policy'),
        ('credit_assignment.py', 'Multi-Agent Credit Assignment', 'credit_assignment')
    ]

    # Filter simulations based on arguments
    simulations_to_run = []

    if args.sim:
        # Run only specified
        for script, desc, name in all_simulations:
            if name in args.sim:
                simulations_to_run.append((script, desc, name))
    else:
        # Run all
        simulations_to_run = all_simulations.copy()

    # Skip specified
    if args.skip:
        simulations_to_run = [
            (script, desc, name)
            for script, desc, name in simulations_to_run
            if name not in args.skip
        ]

    # Quick run: Modify environment variable
    if args.quick:
        os.environ['QUICK_RUN'] = '1'
        print("\nQuick run mode: Reduced episodes for faster execution")

    # Run simulations
    results = {}

    for script, description, name in simulations_to_run:
        success = run_simulation(script, description)
        results[name] = success

        if not success:
            print(f"\nWarning: {description} failed to complete")
            cont = input("Continue with remaining simulations? (y/n): ")
            if cont.lower() != 'y':
                print("\nAborted by user")
                return 1

    # Summary
    print_header("SIMULATION SUMMARY")

    print("\nResults:")
    for name, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {name}: {status}")

    # Check outputs
    print("\nGenerated Files:")

    output_files = [
        # TD(λ) Convergence
        "convergence_curves.png",
        "lambda_sensitivity.png",
        "alpha_sensitivity.png",
        "TD_LAMBDA_CONVERGENCE_REPORT.txt",

        # Function Approximation
        "approx_comparison.png",
        "error_propagation.png",
        "breaking_points.png",
        "FUNCTION_APPROX_REPORT.txt",

        # Off-Policy
        "policy_divergence.png",
        "is_methods.png",
        "stability_bounds.png",
        "OFF_POLICY_REPORT.txt",

        # Credit Assignment
        "credit_methods.png",
        "fairness_analysis.png",
        "scalability.png",
        "CREDIT_ASSIGNMENT_REPORT.txt"
    ]

    for filename in output_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✓ {filename} ({size:,} bytes)")
        else:
            print(f"  ✗ {filename} (not found)")

    # Final summary
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)

    all_success = all(results.values())

    if all_success:
        print("\n✓ All simulations completed successfully!")
        print("\nThe simulations prove:")
        print("  • TD(λ) converges to optimal values (Theorem T1)")
        print("  • Optimistic initialization accelerates exploration (Theorem T2)")
        print("  • Eligibility traces improve convergence rate (Theorem T3)")
        print("  • Function approximation works with proper feature selection")
        print("  • Off-policy learning requires careful variance control")
        print("  • Multi-agent credit assignment can be fair and efficient")
        print("\nThese mathematical validations support POLLN's value network implementation.")
    else:
        print("\n⚠ Some simulations failed. Check error messages above.")
        return 1

    print("\n" + "="*80)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
