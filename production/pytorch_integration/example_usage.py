#!/usr/bin/env python3
"""
Example usage of PyTorch Real Integration Tracer

Demonstrates various tracing scenarios and analysis techniques
"""

import torch
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict

from pytorch_tracer import (
    PyTorchTracer,
    TraceExporter,
    LayerTrace,
    ModelTrace
)


def example_1_basic_tracing():
    """Example 1: Basic model tracing."""
    print("\n" + "="*80)
    print("Example 1: Basic Model Tracing")
    print("="*80 + "\n")

    # Create tracer for ResNet50
    tracer = PyTorchTracer("resnet50", device="cuda")

    # Create input data
    input_data = torch.randn(1, 3, 224, 224).cuda()

    # Trace inference
    trace = tracer.trace(input_data)

    # Print summary
    TraceExporter.print_summary(trace)

    # Export trace
    output_dir = Path("C:/Users/casey/polln/production/pytorch_integration/traces")
    output_dir.mkdir(parents=True, exist_ok=True)

    TraceExporter.to_json(trace, output_dir / "example1_resnet50.json")

    return trace


def example_2_layer_analysis():
    """Example 2: Analyze layer-by-layer metrics."""
    print("\n" + "="*80)
    print("Example 2: Layer-by-Layer Analysis")
    print("="*80 + "\n")

    # Trace BERT model
    tracer = PyTorchTracer("bert-base", device="cuda")

    # Create BERT input
    input_data = {
        "input_ids": torch.randint(0, 30000, (1, 128)).cuda(),
        "attention_mask": torch.ones(1, 128).cuda()
    }

    # Trace
    trace = tracer.trace(input_data)

    # Analyze layers
    print("\nTop 10 Layers by FLOPs:")
    print("-" * 80)
    sorted_by_flops = sorted(trace.layers, key=lambda l: l.flops, reverse=True)
    for layer in sorted_by_flops[:10]:
        print(f"{layer.layer_name:<40} {layer.layer_type:<15} "
              f"FLOPs={layer.flops:>12,} Time={layer.compute_time_ms:>7.2f}ms")

    print("\nTop 10 Layers by CRDT-Friendly Score:")
    print("-" * 80)
    sorted_by_crdt = sorted(trace.layers, key=lambda l: l.crdt_friendly_score, reverse=True)
    for layer in sorted_by_crdt[:10]:
        print(f"{layer.layer_name:<40} {layer.layer_type:<15} "
              f"CRDT={layer.crdt_friendly_score:>6.3f} Params={layer.parameters:>10,}")

    # Export
    output_dir = Path("C:/Users/casey/polln/production/pytorch_integration/traces")
    TraceExporter.to_json(trace, output_dir / "example2_bert.json")

    return trace


def example_3_memory_analysis():
    """Example 3: Memory access pattern analysis."""
    print("\n" + "="*80)
    print("Example 3: Memory Access Pattern Analysis")
    print("="*80 + "\n")

    # Trace GPT-2 model
    tracer = PyTorchTracer("gpt2", device="cuda")

    # Create GPT-2 input
    input_data = torch.randint(0, 50257, (1, 128)).cuda()

    # Trace
    trace = tracer.trace(input_data)

    # Memory analysis
    total_read = sum(l.memory_reads_mb for l in trace.layers)
    total_write = sum(l.memory_writes_mb for l in trace.layers)

    print(f"\nTotal Memory Read: {total_read:.2f} MB")
    print(f"Total Memory Write: {total_write:.2f} MB")
    print(f"Total Memory: {total_read + total_write:.2f} MB")

    print("\nTop 10 Memory-Hungry Layers:")
    print("-" * 80)
    sorted_by_memory = sorted(trace.layers,
                             key=lambda l: l.memory_reads_mb + l.memory_writes_mb,
                             reverse=True)
    for layer in sorted_by_memory[:10]:
        total_mem = layer.memory_reads_mb + layer.memory_writes_mb
        print(f"{layer.layer_name:<40} {layer.layer_type:<15} "
              f"Read={layer.memory_reads_mb:>7.2f}MB "
              f"Write={layer.memory_writes_mb:>7.2f}MB "
              f"Total={total_mem:>7.2f}MB")

    # Cache line analysis
    print("\nCache Line Access Statistics:")
    print("-" * 80)
    cache_line_counts = [len(l.cache_line_accesses) for l in trace.layers]
    print(f"Total Cache Lines Accessed: {sum(cache_line_counts):,}")
    print(f"Average Cache Lines per Layer: {np.mean(cache_line_counts):.1f}")
    print(f"Max Cache Lines in Layer: {max(cache_line_counts):,}")
    print(f"Min Cache Lines in Layer: {min(cache_line_counts):,}")

    # Export
    output_dir = Path("C:/Users/casey/polln/production/pytorch_integration/traces")
    TraceExporter.to_json(trace, output_dir / "example3_gpt2.json")

    return trace


def example_4_crdt_optimization():
    """Example 4: CRDT optimization analysis."""
    print("\n" + "="*80)
    print("Example 4: CRDT Optimization Analysis")
    print("="*80 + "\n")

    # Trace ResNet50
    tracer = PyTorchTracer("resnet50", device="cuda")
    input_data = torch.randn(1, 3, 224, 224).cuda()
    trace = tracer.trace(input_data)

    # CRDT distribution analysis
    high_crdt = [l for l in trace.layers if l.crdt_friendly_score >= 0.8]
    medium_crdt = [l for l in trace.layers if 0.6 <= l.crdt_friendly_score < 0.8]
    low_crdt = [l for l in trace.layers if l.crdt_friendly_score < 0.6]

    print(f"\nCRDT-Friendly Layer Distribution:")
    print(f"  High (>=0.8):   {len(high_crdt)} layers ({len(high_crdt)/len(trace.layers)*100:.1f}%)")
    print(f"  Medium (0.6-0.8): {len(medium_crdt)} layers ({len(medium_crdt)/len(trace.layers)*100:.1f}%)")
    print(f"  Low (<0.6):     {len(low_crdt)} layers ({len(low_crdt)/len(trace.layers)*100:.1f}%)")

    # FLOP distribution by CRDT score
    high_flops = sum(l.flops for l in high_crdt)
    medium_flops = sum(l.flops for l in medium_crdt)
    low_flops = sum(l.flops for l in low_crdt)
    total_flops = trace.total_flops

    print(f"\nFLOP Distribution by CRDT Score:")
    print(f"  High:   {high_flops:,} ({high_flops/total_flops*100:.1f}%)")
    print(f"  Medium: {medium_flops:,} ({medium_flops/total_flops*100:.1f}%)")
    print(f"  Low:    {low_flops:,} ({low_flops/total_flops*100:.1f}%)")

    # Optimization recommendations
    print(f"\nOptimization Recommendations:")
    print("-" * 80)

    # Find bottlenecks
    bottlenecks = [l for l in trace.layers
                  if l.crdt_friendly_score < 0.6 and l.flops > 1e6]
    if bottlenecks:
        print("Low-CRDT Bottlenecks (consider optimization):")
        for layer in sorted(bottlenecks, key=lambda l: l.flops, reverse=True)[:5]:
            print(f"  - {layer.layer_name}: {layer.flops:,} FLOPs "
                  f"(score={layer.crdt_friendly_score:.3f})")

    # Find easy wins
    easy_wins = [l for l in trace.layers
                if l.crdt_friendly_score >= 0.9 and l.flops > 1e5]
    if easy_wins:
        print("\nEasy Distribution Wins (highly parallelizable):")
        for layer in sorted(easy_wins, key=lambda l: l.flops, reverse=True)[:5]:
            print(f"  - {layer.layer_name}: {layer.flops:,} FLOPs "
                  f"(score={layer.crdt_friendly_score:.3f})")

    # Export
    output_dir = Path("C:/Users/casey/polln/production/pytorch_integration/traces")
    TraceExporter.to_json(trace, output_dir / "example4_crdt_analysis.json")

    return trace


def example_5_comparison():
    """Example 5: Compare multiple models."""
    print("\n" + "="*80)
    print("Example 5: Model Comparison")
    print("="*80 + "\n")

    models = ["resnet50", "bert-base", "gpt2"]
    traces = []

    for model_name in models:
        print(f"\nTracing {model_name}...")
        try:
            tracer = PyTorchTracer(model_name, device="cuda")

            # Create appropriate input
            if "resnet" in model_name:
                input_data = torch.randn(1, 3, 224, 224).cuda()
            elif "bert" in model_name:
                input_data = {
                    "input_ids": torch.randint(0, 30000, (1, 128)).cuda(),
                    "attention_mask": torch.ones(1, 128).cuda()
                }
            else:  # gpt2
                input_data = torch.randint(0, 50257, (1, 128)).cuda()

            trace = tracer.trace(input_data)
            traces.append((model_name, trace))

        except Exception as e:
            print(f"Error tracing {model_name}: {e}")

    # Comparison
    print("\n" + "="*80)
    print("Model Comparison Summary")
    print("="*80)
    print(f"{'Model':<15} {'Layers':>8} {'FLOPs':>15} {'Memory (MB)':>12} "
          f"{'Time (ms)':>10} {'Avg CRDT':>10}")
    print("-" * 80)

    for model_name, trace in traces:
        avg_crdt = np.mean([l.crdt_friendly_score for l in trace.layers])
        print(f"{model_name:<15} {len(trace.layers):>8} {trace.total_flops:>15,} "
              f"{trace.total_memory_mb:>12.2f} {trace.total_time_ms:>10.2f} "
              f"{avg_crdt:>10.3f}")

    # Efficiency metrics
    print("\nEfficiency Metrics:")
    print("-" * 80)
    for model_name, trace in traces:
        flops_per_ms = trace.total_flops / trace.total_time_ms
        mb_per_ms = trace.total_memory_mb / trace.total_time_ms
        print(f"{model_name}:")
        print(f"  {flops_per_ms:>12,.0f} FLOPs/ms")
        print(f"  {mb_per_ms:>12.3f} MB/ms")

    return traces


def example_6_visualize():
    """Example 6: Visualize trace data."""
    print("\n" + "="*80)
    print("Example 6: Trace Visualization")
    print("="*80 + "\n")

    # Trace ResNet50
    tracer = PyTorchTracer("resnet50", device="cuda")
    input_data = torch.randn(1, 3, 224, 224).cuda()
    trace = tracer.trace(input_data)

    # Create output directory
    output_dir = Path("C:/Users/casey/polln/production/pytorch_integration/traces/plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Plot 1: FLOPs by layer type
    layer_types = {}
    for layer in trace.layers:
        if layer.layer_type not in layer_types:
            layer_types[layer.layer_type] = []
        layer_types[layer.layer_type].append(layer.flops)

    plt.figure(figsize=(12, 6))
    plt.bar(layer_types.keys(), [sum(v) for v in layer_types.values()])
    plt.xlabel('Layer Type')
    plt.ylabel('Total FLOPs')
    plt.title('FLOPs Distribution by Layer Type')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_dir / "flops_by_layer_type.png", dpi=150)
    print(f"Saved: {output_dir / 'flops_by_layer_type.png'}")

    # Plot 2: CRDT score distribution
    crdt_scores = [l.crdt_friendly_score for l in trace.layers]

    plt.figure(figsize=(10, 6))
    plt.hist(crdt_scores, bins=20, edgecolor='black')
    plt.xlabel('CRDT-Friendly Score')
    plt.ylabel('Count')
    plt.title('Distribution of CRDT-Friendly Scores')
    plt.axvline(x=0.8, color='r', linestyle='--', label='High threshold')
    plt.axvline(x=0.6, color='orange', linestyle='--', label='Medium threshold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "crdt_score_distribution.png", dpi=150)
    print(f"Saved: {output_dir / 'crdt_score_distribution.png'}")

    # Plot 3: Memory access pattern
    memory_reads = [l.memory_reads_mb for l in trace.layers]
    memory_writes = [l.memory_writes_mb for l in trace.layers]

    plt.figure(figsize=(14, 6))
    x = range(len(trace.layers))
    plt.bar(x, memory_reads, label='Read', alpha=0.7)
    plt.bar(x, memory_writes, bottom=memory_reads, label='Write', alpha=0.7)
    plt.xlabel('Layer Index')
    plt.ylabel('Memory (MB)')
    plt.title('Memory Access Pattern by Layer')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "memory_access_pattern.png", dpi=150)
    print(f"Saved: {output_dir / 'memory_access_pattern.png'}")

    # Plot 4: Compute time vs FLOPs
    flops = [l.flops for l in trace.layers]
    times = [l.compute_time_ms for l in trace.layers]

    plt.figure(figsize=(10, 6))
    plt.scatter(flops, times, alpha=0.6)
    plt.xlabel('FLOPs')
    plt.ylabel('Compute Time (ms)')
    plt.title('Compute Time vs FLOPs')
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(output_dir / "compute_time_vs_flops.png", dpi=150)
    print(f"Saved: {output_dir / 'compute_time_vs_flops.png'}")

    print(f"\nAll plots saved to: {output_dir}")

    return trace


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("PyTorch Real Integration - Example Usage")
    print("="*80)

    # Check CUDA availability
    if not torch.cuda.is_available():
        print("\nWarning: CUDA not available, using CPU")
        print("For GPU acceleration, ensure PyTorch is installed with CUDA support")

    # Run examples
    examples = [
        ("Basic Tracing", example_1_basic_tracing),
        ("Layer Analysis", example_2_layer_analysis),
        ("Memory Analysis", example_3_memory_analysis),
        ("CRDT Optimization", example_4_crdt_optimization),
        ("Model Comparison", example_5_comparison),
        ("Visualization", example_6_visualize),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            print(f"\n{'#' * 80}")
            print(f"# Example {i}: {name}")
            print(f"{'#' * 80}")
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
