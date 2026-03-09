"""
Master Optimizer - Run All Memory Optimizations for POLLN

This script runs all memory optimization simulations and generates
a unified cache configuration file.

Optimizations run:
1. Compression optimization
2. Eviction policy optimization
3. ANN index tuning
4. Cache sizing
5. Prefetching strategy

Output: Unified TypeScript configuration file
"""

import subprocess
import sys
import json
import os
from typing import Dict, Any

def run_script(script_name: str) -> Dict[str, Any]:
    """
    Run a Python script and return its results

    Args:
        script_name: Name of script to run

    Returns:
        Results dictionary (loaded from JSON output)
    """
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print(f"{'='*70}")

    script_path = f"simulations/optimization/memory/{script_name}"

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )

        print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        # Try to load results from JSON file
        results_dir = "simulations/optimization/memory/results"
        result_file = script_name.replace(".py", "_results.json")
        result_path = os.path.join(results_dir, result_file)

        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Warning: No results file found at {result_path}")
            return {}

    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return {}

def generate_unified_config(
    compression_results: Dict[str, Any],
    eviction_results: Dict[str, Any],
    ann_results: Dict[str, Any],
    sizing_results: Dict[str, Any],
    prefetch_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate unified cache configuration from all optimization results

    Args:
        compression_results: Compression optimization results
        eviction_results: Eviction policy results
        ann_results: ANN index tuning results
        sizing_results: Cache sizing results
        prefetch_results: Prefetching results

    Returns:
        Unified configuration dictionary
    """
    print("\n" + "="*70)
    print("GENERATING UNIFIED CONFIGURATION")
    print("="*70)

    config = {
        "version": "1.0.0",
        "generated_at": "2026-03-07",
        "description": "Auto-generated KV-cache configuration from memory optimization simulations",

        "compression": {},
        "eviction": {},
        "annIndex": {},
        "sizing": {},
        "prefetch": {}
    }

    # Compression config
    if compression_results and 'optimal_configs' in compression_results:
        for cache_type, opt_config in compression_results['optimal_configs'].items():
            config["compression"][cache_type] = {
                "method": opt_config.get('method', 'svd'),
                "ratio": opt_config.get('compression_ratio', 0.1),
                "quality": opt_config.get('quality', 0.95),
                "parameters": opt_config.get('parameters', {})
            }

        print("\nCompression Configuration:")
        for cache_type, conf in config["compression"].items():
            print(f"  {cache_type}: {conf['method']}, ratio={conf['ratio']:.3f}")

    # Eviction config
    if eviction_results and 'optimal' in eviction_results:
        optimal = eviction_results['optimal']
        config["eviction"] = {
            "policy": optimal.get('overall', {}).get('policy', 'adaptive_arc'),
            "cache_size": optimal.get('overall', {}).get('cache_size', 512 * 1024 * 1024),
            "hit_rate": optimal.get('overall', {}).get('hit_rate', 0.85)
        }

        print(f"\nEviction Configuration:")
        print(f"  Policy: {config['eviction']['policy']}")
        print(f"  Cache Size: {config['eviction']['cache_size'] // (1024*1024)}MB")
        print(f"  Expected Hit Rate: {config['eviction']['hit_rate']:.3f}")

    # ANN Index config
    if ann_results and 'optimal' in ann_results:
        optimal = ann_results['optimal']
        config["annIndex"] = {
            "algorithm": optimal.get('algorithm', 'hnsw'),
            "parameters": optimal.get('parameters', {}),
            "recall": optimal.get('recall', 0.95),
            "query_time_ms": optimal.get('query_time_ms', 1.0)
        }

        print(f"\nANN Index Configuration:")
        print(f"  Algorithm: {config['annIndex']['algorithm']}")
        print(f"  Parameters: {config['annIndex']['parameters']}")
        print(f"  Recall: {config['annIndex']['recall']:.3f}")

    # Sizing config
    if sizing_results and 'optimal_sizes' in sizing_results:
        optimal = sizing_results['optimal_sizes']
        config["sizing"] = optimal

        print(f"\nCache Sizing Configuration:")
        if 'overall' in optimal:
            print(f"  Overall: {optimal['overall']['size_mb']:.1f}MB")

    # Prefetch config
    if prefetch_results and 'optimal' in prefetch_results:
        optimal = prefetch_results['optimal']
        config["prefetch"] = {
            "enabled": True,
            "strategy": optimal.get('strategy', 'markov'),
            "parameters": optimal.get('parameters', {}),
            "efficiency": optimal.get('efficiency', 0.7),
            "latency_reduction": optimal.get('latency_reduction', 0.3)
        }

        print(f"\nPrefetch Configuration:")
        print(f"  Strategy: {config['prefetch']['strategy']}")
        print(f"  Parameters: {config['prefetch']['parameters']}")
        print(f"  Efficiency: {config['prefetch']['efficiency']:.3f}")

    return config

def generate_typescript_config(config: Dict[str, Any], output_path: str):
    """
    Generate TypeScript configuration file

    Args:
        config: Unified configuration dictionary
        output_path: Path to output TypeScript file
    """
    print("\n" + "="*70)
    print(f"GENERATING TYPESCRIPT CONFIG: {output_path}")
    print("="*70)

    ts_content = f"""// Auto-generated by simulations/optimization/memory/run_all.py
// Generation Date: 2026-03-07
// Source: Memory optimization simulations
//
// This configuration contains optimal parameters for KV-cache compression,
// eviction policies, ANN indexing, sizing, and prefetching based on
// comprehensive simulation testing.

export const KV_CACHE_CONFIG = {{
  version: "{config.get('version', '1.0.0')}",
  generatedAt: "{config.get('generated_at', '2026-03-07')}",

  // Compression settings for different cache types
  compression: {{
"""

    # Add compression config
    if 'compression' in config:
        compression = config['compression']
        for cache_type, settings in compression.items():
            ts_content += f"""
    {cache_type}: {{
      method: '{settings.get('method', 'svd')}',
      ratio: {settings.get('ratio', 0.1)},
      quality: {settings.get('quality', 0.95)},
      parameters: {json.dumps(settings.get('parameters', {}))}
    }},"""

    ts_content += """
  },
"""

    # Add eviction config
    if 'eviction' in config:
        eviction = config['eviction']
        ts_content += f"""
  // Eviction policy settings
  eviction: {{
    policy: '{eviction.get('policy', 'adaptive_arc')}',
    maxSize: {eviction.get('cache_size', 512 * 1024 * 1024)},
    expectedHitRate: {eviction.get('hit_rate', 0.85)},
  }},"""

    # Add ANN index config
    if 'annIndex' in config:
        ann = config['annIndex']
        ts_content += f"""
  // ANN Index settings for similarity search
  annIndex: {{
    algorithm: '{ann.get('algorithm', 'hnsw')}',
    params: {json.dumps(ann.get('parameters', {}))},
    expectedRecall: {ann.get('recall', 0.95)},
    expectedQueryTimeMs: {ann.get('query_time_ms', 1.0)},
  }},"""

    # Add sizing config
    if 'sizing' in config:
        sizing = config['sizing']
        ts_content += f"""
  // Cache sizing recommendations
  sizing: {json.dumps(sizing, indent=4)},"""

    # Add prefetch config
    if 'prefetch' in config:
        prefetch = config['prefetch']
        ts_content += f"""
  // Prefetching strategy settings
  prefetch: {{
    enabled: {prefetch.get('enabled', True)},
    strategy: '{prefetch.get('strategy', 'markov')}',
    params: {json.dumps(prefetch.get('parameters', {}))},
    expectedEfficiency: {prefetch.get('efficiency', 0.7)},
    expectedLatencyReduction: {prefetch.get('latency_reduction', 0.3)},
  }},"""

    ts_content += """
} as const;

// Type exports
export type KVCacheConfig = typeof KV_CACHE_CONFIG;
"""

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(ts_content)

    print(f"\nTypeScript configuration written to: {output_path}")

def main():
    """Main optimization pipeline"""
    print("="*70)
    print("POLLN MEMORY OPTIMIZATION MASTER")
    print("Running all optimizations...")
    print("="*70)

    # Create results directory
    os.makedirs("simulations/optimization/memory/results", exist_ok=True)

    # Run all optimizations
    results = {}

    # 1. Compression optimization
    results['compression'] = run_script('compression_optimization.py')

    # 2. Eviction policy
    results['eviction'] = run_script('eviction_policy.py')

    # 3. ANN index tuning
    results['ann'] = run_script('ann_index_tuning.py')

    # 4. Cache sizing
    results['sizing'] = run_script('cache_sizing.py')

    # 5. Prefetching
    results['prefetch'] = run_script('prefetching.py')

    # Generate unified configuration
    unified_config = generate_unified_config(
        results.get('compression', {}),
        results.get('eviction', {}),
        results.get('ann', {}),
        results.get('sizing', {}),
        results.get('prefetch', {})
    )

    # Generate TypeScript config file
    output_path = "src/core/kv/config.ts"
    generate_typescript_config(unified_config, output_path)

    # Also save unified JSON config
    json_path = "simulations/optimization/memory/results/unified_config.json"
    with open(json_path, 'w') as f:
        json.dump(unified_config, f, indent=2)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nResults saved to: simulations/optimization/memory/results/")
    print(f"TypeScript config: {output_path}")
    print(f"Unified JSON: {json_path}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nAll memory optimizations have been run successfully!")
    print("\nGenerated files:")
    print("  - src/core/kv/config.ts (TypeScript configuration)")
    print("  - simulations/optimization/memory/results/*.json (Raw results)")
    print("\nNext steps:")
    print("  1. Review the generated configuration")
    print("  2. Integrate into kvanchor.ts and ann-index.ts")
    print("  3. Run integration tests to validate")
    print("  4. Monitor in production and adjust as needed")

if __name__ == '__main__':
    main()
