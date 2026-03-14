#!/usr/bin/env python3
"""
Integration Test: End-to-End Distributed Training

This script performs a complete integration test of the distributed training
system, including:
- Multi-GPU initialization
- Model training with all optimizations
- Checkpoint saving/loading
- Metrics collection
- Resource cleanup

Usage:
    # Single GPU test
    python integration_test.py

    # Multi-GPU test
    torchrun --nproc_per_node=2 integration_test.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Import distributed training components
from distributed_trainer import (
    DistributedTrainer,
    DistributedConfig,
    CRDTGradientSync,
    GradientCompressor,
    setup_multi_node_training,
    setup_logging
)


class TestModel(nn.Module):
    """Simple test model for integration testing."""

    def __init__(self, input_dim=784, hidden_dim=256, output_dim=10):
        super(TestModel, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        features = self.encoder(x)
        logits = self.classifier(features)
        return logits


class TestDataset(torch.utils.data.Dataset):
    """Synthetic dataset for integration testing."""

    def __init__(self, size=1000, input_dim=784, num_classes=10):
        self.size = size
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Generate fixed random data for reproducibility
        torch.manual_seed(42)
        self.data = torch.randn(size, input_dim)
        self.targets = torch.randint(0, num_classes, (size,))

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.data[idx], self.targets[idx]


class IntegrationTest:
    """Complete integration test suite."""

    def __init__(self):
        self.rank = 0
        self.world_size = 1
        self.device = torch.device("cpu")
        self.logger = setup_logging(0)
        self.results: Dict[str, Any] = {}

        # Check if distributed
        if torch.distributed.is_available():
            try:
                # Try to get environment variables
                self.rank = int(sys.environ.get("RANK", 0))
                self.world_size = int(sys.environ.get("WORLD_SIZE", 1))

                if self.world_size > 1:
                    self.rank, self.world_size, self.device = setup_multi_node_training()
                    self.logger = setup_logging(self.rank)
            except Exception as e:
                self.logger.warning(f"Could not initialize distributed: {e}")

    def test_gradient_compression(self) -> bool:
        """Test gradient compression functionality."""
        self.logger.info("Testing gradient compression...")

        try:
            compressor = GradientCompressor(compression_ratio=0.1)

            # Create test gradient
            gradient = torch.randn(1000, 1000)

            # Compress and decompress
            compressed, metadata = compressor.compress(gradient)
            decompressed = compressor.decompress(compressed, metadata)

            # Verify
            assert compressed.shape == gradient.shape, "Shape mismatch"
            assert metadata["nnz"] < gradient.numel(), "No compression applied"

            self.logger.info(f"  Compression ratio: {metadata['compression_ratio']:.1%}")
            self.logger.info("  Gradient compression: PASSED")
            return True

        except Exception as e:
            self.logger.error(f"  Gradient compression: FAILED ({e})")
            return False

    def test_crdt_synchronization(self) -> bool:
        """Test CRDT gradient synchronization."""
        self.logger.info("Testing CRDT synchronization...")

        try:
            crdt_sync = CRDTGradientSync(
                rank=self.rank,
                world_size=self.world_size,
                logger=self.logger
            )

            # Create test model
            model = TestModel()

            # Test fast path safety check
            is_safe = crdt_sync._is_fast_path_safe(model)

            # Get stats
            stats = crdt_sync.get_sync_stats()

            self.logger.info(f"  Fast path safe: {is_safe}")
            self.logger.info("  CRDT synchronization: PASSED")
            return True

        except Exception as e:
            self.logger.error(f"  CRDT synchronization: FAILED ({e})")
            return False

    def test_distributed_training(self) -> bool:
        """Test complete distributed training loop."""
        self.logger.info("Testing distributed training loop...")

        try:
            # Create temporary checkpoint directory
            import tempfile
            import shutil
            checkpoint_dir = tempfile.mkdtemp()

            try:
                # Configuration
                config = DistributedConfig(
                    batch_size=64,
                    num_epochs=2,  # Short test
                    learning_rate=0.001,
                    use_crdt_sync=True,
                    use_amp=False,  # Disable for CPU testing
                    checkpoint_dir=checkpoint_dir,
                    checkpoint_interval=1,
                    num_workers=0,
                    pin_memory=False
                )

                # Create model
                model = TestModel().to(self.device)

                # Create trainer
                trainer = DistributedTrainer(
                    model=model,
                    config=config,
                    rank=self.rank,
                    world_size=self.world_size,
                    device=self.device
                )

                # Create datasets
                train_dataset = TestDataset(size=1000)
                val_dataset = TestDataset(size=200)

                # Create optimizer and loss
                optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
                criterion = nn.CrossEntropyLoss()

                # Train
                start_time = time.time()
                metrics = trainer.train(
                    dataset=train_dataset,
                    optimizer=optimizer,
                    criterion=criterion,
                    validation_dataset=val_dataset
                )
                training_time = time.time() - start_time

                # Verify results
                assert "training_metrics" in metrics, "No training metrics"
                assert "best_loss" in metrics, "No best loss"

                self.logger.info(f"  Training time: {training_time:.2f}s")
                self.logger.info(f"  Best loss: {metrics['best_loss']:.4f}")

                if config.use_crdt_sync and "crdt_stats" in metrics:
                    crdt_stats = metrics["crdt_stats"]
                    self.logger.info(
                        f"  CRDT fast path: {crdt_stats['fast_path_percentage']:.1f}%"
                    )

                # Cleanup
                trainer.cleanup()

                self.logger.info("  Distributed training: PASSED")
                self.results["training_time"] = training_time
                self.results["best_loss"] = metrics["best_loss"]
                return True

            finally:
                # Cleanup checkpoint directory
                shutil.rmtree(checkpoint_dir)

        except Exception as e:
            self.logger.error(f"  Distributed training: FAILED ({e})")
            import traceback
            traceback.print_exc()
            return False

    def test_checkpoint_save_load(self) -> bool:
        """Test checkpoint saving and loading."""
        self.logger.info("Testing checkpoint save/load...")

        try:
            import tempfile
            import shutil

            checkpoint_dir = tempfile.mkdtemp()

            try:
                # Create model
                model = TestModel()

                # Create config
                config = DistributedConfig(checkpoint_dir=checkpoint_dir)

                # Create trainer
                trainer = DistributedTrainer(
                    model=model,
                    config=config,
                    rank=self.rank,
                    world_size=self.world_size,
                    device=self.device
                )

                # Save checkpoint
                trainer._save_checkpoint(epoch=0)

                # Check checkpoint file exists
                checkpoint_path = Path(checkpoint_dir) / "checkpoint_epoch_0.pt"
                assert checkpoint_path.exists(), "Checkpoint file not created"

                # Load checkpoint
                checkpoint = torch.load(checkpoint_path)

                # Verify checkpoint contents
                assert "epoch" in checkpoint, "No epoch in checkpoint"
                assert "model_state_dict" in checkpoint, "No model state in checkpoint"
                assert checkpoint["epoch"] == 0, "Wrong epoch in checkpoint"

                self.logger.info("  Checkpoint save/load: PASSED")
                return True

            finally:
                shutil.rmtree(checkpoint_dir)

        except Exception as e:
            self.logger.error(f"  Checkpoint save/load: FAILED ({e})")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests."""
        self.logger.info("=" * 80)
        self.logger.info("Starting Integration Tests")
        self.logger.info("=" * 80)
        self.logger.info(f"Rank: {self.rank}/{self.world_size}")
        self.logger.info(f"Device: {self.device}")
        self.logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        self.logger.info("=" * 80)

        results = {}

        # Run tests
        results["gradient_compression"] = self.test_gradient_compression()
        results["crdt_synchronization"] = self.test_crdt_synchronization()
        results["checkpoint_save_load"] = self.test_checkpoint_save_load()
        results["distributed_training"] = self.test_distributed_training()

        # Print summary
        self.logger.info("=" * 80)
        self.logger.info("Integration Test Summary")
        self.logger.info("=" * 80)

        for test_name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            symbol = "✓" if passed else "✗"
            self.logger.info(f"  {symbol} {test_name}: {status}")

        # Overall result
        all_passed = all(results.values())
        self.logger.info("=" * 80)

        if all_passed:
            self.logger.info("✓ ALL TESTS PASSED")
        else:
            self.logger.error("✗ SOME TESTS FAILED")

        self.logger.info("=" * 80)

        # Store results
        self.results.update(results)
        self.results["all_passed"] = all_passed

        return results


def main():
    """Main entry point."""
    # Create test suite
    test_suite = IntegrationTest()

    # Run all tests
    results = test_suite.run_all_tests()

    # Exit with appropriate code
    if results.get("all_passed", False):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
