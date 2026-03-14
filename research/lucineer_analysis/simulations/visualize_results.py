"""
Lucineer Throughput Visualization
==================================

Generate plots and visualizations from throughput simulation results.

Author: Throughput Benchmark Specialist
Date: 2026-03-13
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from typing import List, Dict, Tuple

# Set style
rcParams['figure.figsize'] = (14, 8)
rcParams['font.size'] = 10
sns.set_style("whitegrid")


def plot_throughput_vs_sequence(
    results: Dict[str, List[float]],
    memory_types: List[str],
    batch_sizes: List[int],
    seq_lengths: List[int],
    save_path: str = None
):
    """Plot throughput vs sequence length for different batch sizes"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for idx, mem_type in enumerate(memory_types):
        ax = axes[idx]

        # Organize results by batch size
        for batch_size in batch_sizes:
            throughputs = []
            for seq_len in seq_lengths:
                # Find corresponding result
                result_idx = batch_sizes.index(batch_size) * len(seq_lengths) + seq_lengths.index(seq_len)
                if result_idx < len(results[mem_type]):
                    throughputs.append(results[mem_type][result_idx].tokens_per_second)

            ax.plot(seq_lengths, throughputs, marker='o', label=f'Batch={batch_size}', linewidth=2)

        # Target range
        ax.axhspan(80, 150, alpha=0.2, color='green', label='Target Range (80-150)')

        ax.set_xlabel('Sequence Length', fontsize=12)
        ax.set_ylabel('Throughput (tokens/second)', fontsize=12)
        ax.set_title(f'{mem_type} - Throughput vs Sequence Length', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_bottleneck_distribution(
    bottleneck_stats: Dict[str, Dict],
    save_path: str = None
):
    """Plot bottleneck distribution pie chart"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for idx, (mem_type, stats) in enumerate(bottleneck_stats.items()):
        ax = axes[idx]

        labels = list(stats.keys())
        sizes = [s['count'] for s in stats.values()]
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24']

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            colors=colors, startangle=90,
            textprops={'fontsize': 11}
        )

        ax.set_title(f'{mem_type} - Bottleneck Distribution', fontsize=14, fontweight='bold')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_efficiency_comparison(
    fpga_results: Dict[str, float],
    gpu_results: Dict[str, float],
    save_path: str = None
):
    """Plot FPGA vs GPU efficiency comparison"""
    fig, ax = plt.subplots(figsize=(12, 6))

    configs = list(fpga_results.keys())
    fpga_efficiency = list(fpga_results.values())
    gpu_efficiency = list(gpu_results.values())

    x = np.arange(len(configs))
    width = 0.35

    bars1 = ax.bar(x - width/2, fpga_efficiency, width, label='FPGA (HBM2)', color='#4ecdc4')
    bars2 = ax.bar(x + width/2, gpu_efficiency, width, label='GPU (A100)', color='#ff6b6b')

    ax.set_xlabel('Configuration', fontsize=12)
    ax.set_ylabel('Efficiency (tokens/second/Watt)', fontsize=12)
    ax.set_title('FPGA vs GPU - Power Efficiency Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def create_summary_table(
    results: Dict[str, List],
    save_path: str = None
):
    """Create summary statistics table as visualization"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')

    # Prepare data
    table_data = []
    for mem_type, mem_results in results.items():
        throughputs = [r.tokens_per_second for r in mem_results]

        row = [
            mem_type,
            f"{np.mean(throughputs):.1f}",
            f"{np.median(throughputs):.1f}",
            f"{np.std(throughputs):.1f}",
            f"{np.min(throughputs):.1f}",
            f"{np.max(throughputs):.1f}",
            f"{100*np.mean([t>80 for t in throughputs]):.1f}%",
            f"{100*np.mean([t>150 for t in throughputs]):.1f}%"
        ]
        table_data.append(row)

    columns = [
        'Memory Type',
        'Mean (tok/s)',
        'Median (tok/s)',
        'Std Dev (tok/s)',
        'Min (tok/s)',
        'Max (tok/s)',
        '% ≥ 80 tok/s',
        '% ≥ 150 tok/s'
    ]

    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        cellLoc='center',
        loc='center',
        colWidths=[0.15, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style header row
    for i in range(len(columns)):
        table[(0, i)].set_facecolor('#4ecdc4')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style data rows
    for i in range(1, len(table_data) + 1):
        for j in range(len(columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    plt.title('Throughput Simulation Summary Statistics',
              fontsize=16, fontweight='bold', pad=20)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # Import results from main simulation
    from throughput_simulation import (
        HardwareConfig, ModelConfig, TLMMSimulator,
        MemoryType, BottleneckAnalyzer
    )

    print("Generating visualizations...")

    # Run simulation
    hardware = HardwareConfig(
        luts_available=900_000,
        memory_type=MemoryType.HBM2,
        memory_channels=2
    )

    model = ModelConfig()

    simulator = TLMMSimulator(hardware, model)

    batch_sizes = [1, 2, 4, 8, 16]
    seq_lengths = [128, 512, 1024, 2048, 4096]
    memory_types = [MemoryType.HBM2, MemoryType.DDR4_3200]

    results = simulator.run_sweep(batch_sizes, seq_lengths, memory_types)

    # Generate plots
    print("\n1. Throughput vs Sequence Length...")
    plot_throughput_vs_sequence(
        results,
        [m.value for m in memory_types],
        batch_sizes,
        seq_lengths,
        save_path=r"C:\Users\casey\polln\research\lucineer_analysis\simulations\throughput_vs_sequence.png"
    )

    print("\n2. Summary Table...")
    create_summary_table(
        results,
        save_path=r"C:\Users\casey\polln\research\lucineer_analysis\simulations\summary_table.png"
    )

    print("\n3. Bottleneck Analysis...")
    analyzer = BottleneckAnalyzer()

    bottleneck_stats = {}
    for mem_type in [m.value for m in memory_types]:
        bottleneck_stats[mem_type] = analyzer.analyze(results[mem_type])

    plot_bottleneck_distribution(
        bottleneck_stats,
        save_path=r"C:\Users\casey\polln\research\lucineer_analysis\simulations\bottleneck_distribution.png"
    )

    print("\n4. Efficiency Comparison...")
    # Simulated efficiency data
    fpga_efficiency = {
        'Short Context (128)': 28.0,
        'Medium Context (1024)': 24.5,
        'Long Context (4096)': 10.2
    }

    gpu_efficiency = {
        'Short Context (128)': 0.4,
        'Medium Context (1024)': 0.35,
        'Long Context (4096)': 0.27
    }

    plot_efficiency_comparison(
        fpga_efficiency,
        gpu_efficiency,
        save_path=r"C:\Users\casey\polln\research\lucineer_analysis\simulations\efficiency_comparison.png"
    )

    print("\nAll visualizations complete!")
    print("\nSaved files:")
    print("  - throughput_vs_sequence.png")
    print("  - summary_table.png")
    print("  - bottleneck_distribution.png")
    print("  - efficiency_comparison.png")
