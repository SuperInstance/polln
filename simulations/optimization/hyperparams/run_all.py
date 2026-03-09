"""
Master Optimization Runner

Runs all POLLN hyperparameter optimizations in parallel and generates
a unified configuration file with optimal parameters.

Usage:
    python run_all.py [--parallel] [--quick]

Options:
    --parallel: Run optimizations in parallel (faster)
    --quick: Run with reduced iterations for testing (faster but less accurate)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
import time
from datetime import datetime


# Optimization modules
OPTIMIZATIONS = [
    'plinko_temperature',
    'td_lambda_optimization',
    'vae_architecture',
    'graph_evolution_params',
    'meta_differentiation'
]


def run_optimization(name: str, quick: bool = False) -> Dict:
    """
    Run a single optimization script.

    Args:
        name: Name of optimization module (without .py)
        quick: Use reduced iterations for faster execution

    Returns:
        Dictionary with optimization results
    """
    print(f"\n{'='*60}")
    print(f"Running {name} optimization...")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        # Run the optimization script
        cmd = [sys.executable, f"{name}.py"]

        # Add quick flag if needed (modifies iterations internally)
        if quick:
            # Set environment variable to signal quick mode
            import os
            os.environ['OPTIMIZATION_QUICK_MODE'] = '1'

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        elapsed = time.time() - start_time
        print(f"✓ {name} completed in {elapsed:.1f}s")

        # Load results
        results_file = Path(__file__).parent / 'results' / f'{name}_results.json'

        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
            return results
        else:
            print(f"⚠ Warning: Results file not found for {name}")
            return {}

    except subprocess.CalledProcessError as e:
        print(f"✗ {name} failed with error:")
        print(e.stderr)
        return {}
    except Exception as e:
        print(f"✗ {name} failed with exception: {e}")
        return {}


def run_parallel(quick: bool = False) -> Dict[str, Dict]:
    """
    Run all optimizations in parallel.

    Args:
        quick: Use reduced iterations

    Returns:
        Dictionary mapping optimization names to results
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print(f"\n{'='*60}")
    print(f"Running {len(OPTIMIZATIONS)} optimizations in parallel...")
    print(f"{'='*60}\n")

    results = {}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=len(OPTIMIZATIONS)) as executor:
        # Submit all optimizations
        futures = {
            executor.submit(run_optimization, name, quick): name
            for name in OPTIMIZATIONS
        }

        # Collect results as they complete
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                results[name] = result
            except Exception as e:
                print(f"✗ {name} failed: {e}")
                results[name] = {}

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"All parallel optimizations completed in {elapsed:.1f}s")
    print(f"{'='*60}\n")

    return results


def run_sequential(quick: bool = False) -> Dict[str, Dict]:
    """
    Run all optimizations sequentially.

    Args:
        quick: Use reduced iterations

    Returns:
        Dictionary mapping optimization names to results
    """
    print(f"\n{'='*60}")
    print(f"Running {len(OPTIMIZATIONS)} optimizations sequentially...")
    print(f"{'='*60}\n")

    results = {}
    start_time = time.time()

    for name in OPTIMIZATIONS:
        result = run_optimization(name, quick)
        results[name] = result

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"All sequential optimizations completed in {elapsed:.1f}s")
    print(f"{'='*60}\n")

    return results


def generate_unified_config(results: Dict[str, Dict]) -> Dict:
    """
    Generate unified configuration from all optimization results.

    Args:
        results: Dictionary of optimization results

    Returns:
        Unified configuration dictionary
    """
    config = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0.0'
        },
        'optimizations': {}
    }

    # Extract best parameters from each optimization
    for name, result in results.items():
        if result and 'best_parameters' in result:
            config['optimizations'][name] = {
                'best_parameters': result['best_parameters'],
                'objective_value': result.get('optimization_objective', None),
                'validation_stats': result.get('validation_statistics', {})
            }

    return config


def save_results(unified_config: Dict):
    """Save unified configuration to files"""

    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Save JSON
    json_path = results_dir / 'unified_config.json'
    with open(json_path, 'w') as f:
        json.dump(unified_config, f, indent=2)
    print(f"✓ Saved unified config to {json_path}")

    # Save human-readable report
    report_path = results_dir / 'OPTIMIZATION_REPORT.md'
    generate_report(unified_config, report_path)
    print(f"✓ Saved optimization report to {report_path}")


def generate_report(config: Dict, output_path: Path):
    """Generate Markdown optimization report"""

    with open(output_path, 'w') as f:
        f.write("# POLLN Hyperparameter Optimization Report\n\n")
        f.write(f"**Generated**: {config['metadata']['generated_at']}\n\n")
        f.write(f"**Version**: {config['metadata']['version']}\n\n")

        f.write("## Overview\n\n")
        f.write("This report summarizes the results of hyperparameter optimization ")
        f.write("for all POLLN components using Bayesian optimization and grid search.\n\n")

        f.write("## Optimized Components\n\n")

        for name, data in config['optimizations'].items():
            f.write(f"### {name.replace('_', ' ').title()}\n\n")

            params = data['best_parameters']
            f.write("**Best Parameters:**\n\n")
            f.write("```typescript\n")
            f.write(f"{name}: {{\n")
            for key, value in params.items():
                if isinstance(value, float):
                    f.write(f"  {key}: {value:.6f},\n")
                elif isinstance(value, str):
                    f.write(f"  {key}: '{value}',\n")
                else:
                    f.write(f"  {key}: {value},\n")
            f.write("}\n")
            f.write("```\n\n")

            if 'objective_value' in data:
                f.write(f"**Objective Value**: {data['objective_value']:.6f}\n\n")

            if 'validation_stats' in data and data['validation_stats']:
                f.write("**Validation Statistics:**\n\n")
                stats = data['validation_stats']
                f.write("| Metric | Mean | Std | Min | Max |\n")
                f.write("|--------|------|-----|-----|-----|\n")
                for metric, values in stats.items():
                    f.write(f"| {metric} | {values['mean']:.4f} | {values['std']:.4f} | ")
                    f.write(f"{values['min']:.4f} | {values['max']:.4f} |\n")
                f.write("\n")

        f.write("## Usage\n\n")
        f.write("To use these optimized parameters in your POLLN implementation:\n\n")
        f.write("```typescript\n")
        f.write("import { OPTIMIZED_CONFIG } from './config/optimized';\n\n")
        f.write("// Use in your code\n")
        f.write("const temperature = OPTIMIZED_CONFIG.plinko.initialTemperature;\n")
        f.write("const lambda = OPTIMIZED_CONFIG.tdLambda.lambda;\n")
        f.write("```\n\n")

        f.write("## Regeneration\n\n")
        f.write("To regenerate this configuration:\n\n")
        f.write("```bash\n")
        f.write("cd simulations/optimization/hyperparams\n")
        f.write("python run_all.py\n")
        f.write("```\n\n")


def print_summary(unified_config: Dict):
    """Print summary of optimization results"""

    print(f"\n{'='*60}")
    print("OPTIMIZATION SUMMARY")
    print(f"{'='*60}\n")

    for name, data in unified_config['optimizations'].items():
        print(f"{name.replace('_', ' ').title()}")
        print("-" * 40)

        params = data['best_parameters']
        for key, value in params.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.6f}")
            else:
                print(f"  {key}: {value}")

        if 'objective_value' in data:
            print(f"  objective: {data['objective_value']:.6f}")

        print()

    print(f"{'='*60}\n")


def main():
    """Main execution"""

    parser = argparse.ArgumentParser(
        description='Run all POLLN hyperparameter optimizations'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run optimizations in parallel'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run with reduced iterations (faster but less accurate)'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("POLLN HYPERPARAMETER OPTIMIZATION")
    print("="*60)
    print(f"Mode: {'Parallel' if args.parallel else 'Sequential'}")
    print(f"Iterations: {'Reduced (quick)' if args.quick else 'Full'}")
    print("="*60)

    # Change to script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)

    # Run optimizations
    if args.parallel:
        results = run_parallel(quick=args.quick)
    else:
        results = run_sequential(quick=args.quick)

    # Generate unified config
    unified_config = generate_unified_config(results)

    # Save results
    save_results(unified_config)

    # Print summary
    print_summary(unified_config)

    # Generate TypeScript config
    print("Generating TypeScript configuration...")
    subprocess.run(
        [sys.executable, 'generate_config.py'],
        check=True,
        cwd=script_dir
    )

    print("\n" + "="*60)
    print("OPTIMIZATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review results in results/OPTIMIZATION_REPORT.md")
    print("2. Check visualizations in results/*.png")
    print("3. Use optimized config: src/core/config/optimized.ts")
    print("\n")


if __name__ == '__main__':
    main()
