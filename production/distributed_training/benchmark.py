#!/usr/bin/env python3
"""
Distributed Training Benchmark Tool

Measures and compares performance of different distributed training configurations:
- Single GPU vs Multi-GPU
- CRDT sync vs AllReduce
- With/without gradient compression
- With/without AMP

Usage:
    torchrun --nproc_per_node=4 benchmark.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
import time
from typing import Dict, List
from dataclasses import dataclass
from distributed_trainer import (
    DistributedTrainer,
    DistributedConfig,
    setup_multi_node_training,
    GradientCompressor,
    CRDTGradientSync
)


class BenchmarkModel(nn.Module):
    """Simple model for benchmarking."""

    def __init__(self, input_dim=784, hidden_dim=1024, output_dim=10):
        super(BenchmarkModel, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.net(x)


class BenchmarkDataset(torch.utils.data.Dataset):
    """Synthetic dataset for benchmarking."""

    def __init__(self, size=10000, input_dim=784, num_classes=10):
        self.size = size
        self.input_dim = input_dim
        self.num_classes = num_classes

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        x = torch.randn(self.input_dim)
        y = torch.randint(0, self.num_classes, (1,)).item()
        return x, y


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""

    config_name: str
    world_size: int
    batch_size: int
    use_crdt: bool
    use_compression: bool
    use_amp: bool
    throughput: float  # samples/second
    avg_loss: float
    epoch_time: float
    sync_method: str
    memory_usage: float  # GB


class DistributedBenchmark:
    """Distributed training benchmark suite."""

    def __init__(self, rank: int, world_size: int, device: torch.device):
        """
        Initialize benchmark suite.

        Args:
            rank: Process rank
            world_size: Total number of processes
            device: Device to run on
        """
        self.rank = rank
        self.world_size = world_size
        self.device = device
        self.results: List[BenchmarkResult] = []

    def run_benchmark_suite(self):
        """Run complete benchmark suite."""
        if self.rank != 0:
            return

        print("=" * 80)
        print("Distributed Training Benchmark Suite")
        print("=" * 80)
        print(f"World Size: {self.world_size}")
        print(f"Device: {self.device}")
        print("=" * 80)

        # Benchmark configurations
        configs = [
            # Baseline
            {
                "name": "Baseline (AllReduce, No Compression, No AMP)",
                "use_crdt": False,
                "use_compression": False,
                "use_amp": False,
                "compression_ratio": 0.1
            },
            # CRDT only
            {
                "name": "CRDT Sync Only",
                "use_crdt": True,
                "use_compression": False,
                "use_amp": False,
                "compression_ratio": 0.1
            },
            # Compression only
            {
                "name": "Compression Only",
                "use_crdt": False,
                "use_compression": True,
                "use_amp": False,
                "compression_ratio": 0.1
            },
            # CRDT + Compression
            {
                "name": "CRDT + Compression",
                "use_crdt": True,
                "use_compression": True,
                "use_amp": False,
                "compression_ratio": 0.1
            },
            # AMP only
            {
                "name": "AMP Only",
                "use_crdt": False,
                "use_compression": False,
                "use_amp": True,
                "compression_ratio": 0.1
            },
            # Full optimization
            {
                "name": "Full Optimization (CRDT + Compression + AMP)",
                "use_crdt": True,
                "use_compression": True,
                "use_amp": True,
                "compression_ratio": 0.1
            },
        ]

        # Run benchmarks
        for config in configs:
            result = self._run_single_benchmark(**config)
            self.results.append(result)

        # Print summary
        self._print_summary()

    def _run_single_benchmark(self,
                             name: str,
                             use_crdt: bool,
                             use_compression: bool,
                             use_amp: bool,
                             compression_ratio: float) -> BenchmarkResult:
        """
        Run a single benchmark configuration.

        Args:
            name: Configuration name
            use_crdt: Enable CRDT sync
            use_compression: Enable gradient compression
            use_amp: Enable AMP
            compression_ratio: Compression ratio

        Returns:
            Benchmark result
        """
        if self.rank == 0:
            print(f"\nBenchmarking: {name}")
            print("-" * 80)

        # Configuration
        config = DistributedConfig(
            batch_size=128,
            num_epochs=5,  # Short benchmark
            learning_rate=0.001,
            use_crdt_sync=use_crdt,
            compression_ratio=compression_ratio,
            use_amp=use_amp,
            num_workers=2,  # Reduce for benchmark
            pin_memory=True
        )

        # Create model
        model = BenchmarkModel().to(self.device)

        # Create trainer
        trainer = DistributedTrainer(
            model=model,
            config=config,
            rank=self.rank,
            world_size=self.world_size,
            device=self.device
        )

        # Create optimizer and loss
        optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
        criterion = nn.CrossEntropyLoss()

        # Create dataset
        dataset = BenchmarkDataset(size=10000)

        # Benchmark training
        start_time = time.time()
        total_samples = 0

        for epoch in range(config.num_epochs):
            epoch_start = time.time()

            # Create dataloader
            dataloader = trainer._create_dataloader(dataset, shuffle=True)

            # Train epoch
            model.train()
            epoch_loss = 0.0
            batches = 0

            for inputs, targets in dataloader:
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                # Forward pass
                if use_amp:
                    with torch.cuda.amp.autocast():
                        outputs = model(inputs)
                        loss = criterion(outputs, targets)

                    # Backward pass
                    optimizer.zero_grad()
                    trainer.scaler.scale(loss).backward()
                    trainer.scaler.unscale_(optimizer)
                    trainer._sync_gradients(optimizer)
                    trainer.scaler.step(optimizer)
                    trainer.scaler.update()
                else:
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)

                    # Backward pass
                    optimizer.zero_grad()
                    loss.backward()
                    trainer._sync_gradients(optimizer)
                    optimizer.step()

                epoch_loss += loss.item()
                batches += 1
                total_samples += inputs.size(0) * self.world_size

            epoch_time = time.time() - epoch_start
            avg_loss = epoch_loss / batches

            if self.rank == 0:
                print(f"  Epoch {epoch}: {epoch_time:.2f}s, Loss: {avg_loss:.4f}")

        total_time = time.time() - start_time

        # Compute metrics
        throughput = total_samples / total_time
        epoch_time_avg = total_time / config.num_epochs

        # Get sync method
        if use_crdt and trainer.crdt_sync:
            stats = trainer.crdt_sync.get_sync_stats()
            sync_method = f"CRDT ({stats['fast_path_percentage']:.1f}% fast path)"
        else:
            sync_method = "AllReduce"

        # Get memory usage
        memory_allocated = torch.cuda.max_memory_allocated() / 1e9  # GB

        # Create result
        result = BenchmarkResult(
            config_name=name,
            world_size=self.world_size,
            batch_size=config.batch_size,
            use_crdt=use_crdt,
            use_compression=use_compression,
            use_amp=use_amp,
            throughput=throughput,
            avg_loss=avg_loss,
            epoch_time=epoch_time_avg,
            sync_method=sync_method,
            memory_usage=memory_allocated
        )

        if self.rank == 0:
            print(f"  Throughput: {throughput:.1f} samples/sec")
            print(f"  Epoch Time: {epoch_time_avg:.2f}s")
            print(f"  Sync Method: {sync_method}")
            print(f"  Memory: {memory_usage:.2f} GB")

        # Cleanup
        trainer.cleanup()

        return result

    def _print_summary(self):
        """Print benchmark summary table."""
        if self.rank != 0:
            return

        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)

        # Find baseline for speedup calculation
        baseline = None
        for result in self.results:
            if result.config_name == "Baseline (AllReduce, No Compression, No AMP)":
                baseline = result
                break

        # Print table
        print(f"{'Configuration':<40} {'Throughput':<15} {'Speedup':<10} {'Memory':<10}")
        print("-" * 80)

        for result in self.results:
            speedup = result.throughput / baseline.throughput if baseline else 1.0

            print(f"{result.config_name:<40} "
                  f"{result.throughput:<15.1f} "
                  f"{speedup:<10.2f}x "
                  f"{result.memory_usage:<10.2f} GB")

        print("=" * 80)

        # Print recommendations
        print("\nRECOMMENDATIONS:")
        print("-" * 80)

        # Find best configuration
        best = max(self.results, key=lambda r: r.throughput)
        print(f"Best Throughput: {best.config_name}")
        print(f"  - {best.throughput:.1f} samples/sec ({best.throughput / baseline.throughput:.2f}x speedup)")

        # Find most memory efficient
        most_memory_efficient = min(self.results, key=lambda r: r.memory_usage)
        print(f"\nMost Memory Efficient: {most_memory_efficient.config_name}")
        print(f"  - {most_memory_efficient.memory_usage:.2f} GB")

        # Print best configuration for different scenarios
        print("\nBest Configuration by Scenario:")
        print("-" * 80)

        # Maximum throughput
        max_throughput = max(self.results, key=lambda r: r.throughput)
        print(f"Maximum Throughput: {max_throughput.config_name}")

        # Best CRDT performance
        crdt_results = [r for r in self.results if r.use_crdt]
        if crdt_results:
            best_crdt = max(crdt_results, key=lambda r: r.throughput)
            print(f"Best CRDT Configuration: {best_crdt.config_name}")

        # Best compression
        compression_results = [r for r in self.results if r.use_compression]
        if compression_results:
            best_compression = max(compression_results, key=lambda r: r.throughput)
            print(f"Best Compression Configuration: {best_compression.config_name}")

        print("=" * 80)


def main():
    """Main benchmark function."""

    # Setup distributed training
    rank, world_size, device = setup_multi_node_training()

    # Create benchmark suite
    benchmark = DistributedBenchmark(rank, world_size, device)

    # Run benchmarks
    benchmark.run_benchmark_suite()


if __name__ == "__main__":
    main()
