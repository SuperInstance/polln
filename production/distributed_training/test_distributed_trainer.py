#!/usr/bin/env python3
"""
Test Suite for Multi-GPU Distributed Training

Comprehensive tests for:
- Process group initialization
- DDP model wrapping
- Gradient synchronization
- CRDT fast path
- Gradient compression
- Distributed data loading
- Checkpoint saving/loading

Usage:
    # Single GPU test
    pytest test_distributed_trainer.py -v

    # Multi-GPU test
    torchrun --nproc_per_node=2 pytest test_distributed_trainer.py -v
"""

import pytest
import torch
import torch.nn as nn
import torch.optim as optim
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List

from distributed_trainer import (
    DistributedTrainer,
    DistributedConfig,
    CRDTGradientSync,
    GradientCompressor,
    setup_multi_node_training
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_checkpoint_dir():
    """Create temporary checkpoint directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def simple_model():
    """Create simple model for testing."""
    return nn.Sequential(
        nn.Linear(10, 32),
        nn.ReLU(),
        nn.Linear(32, 10)
    )


@pytest.fixture
def dummy_dataset():
    """Create dummy dataset for testing."""
    class DummyDataset(torch.utils.data.Dataset):
        def __init__(self, size=100):
            self.size = size

        def __len__(self):
            return self.size

        def __getitem__(self, idx):
            return torch.randn(10), torch.randint(0, 10, (1,)).item()

    return DummyDataset(size=100)


@pytest.fixture
def distributed_config(temp_checkpoint_dir):
    """Create distributed configuration for testing."""
    return DistributedConfig(
        batch_size=16,
        num_epochs=2,
        learning_rate=0.001,
        checkpoint_dir=temp_checkpoint_dir,
        checkpoint_interval=1,
        use_crdt_sync=True,
        use_amp=False,  # Disable for testing
        num_workers=0,  # Disable for testing
        pin_memory=False
    )


# =============================================================================
# Tests: Gradient Compression
# =============================================================================

class TestGradientCompressor:
    """Test gradient compression functionality."""

    def test_compress_decompress(self):
        """Test basic compression and decompression."""
        compressor = GradientCompressor(compression_ratio=0.1)

        # Create random gradient
        gradient = torch.randn(100, 100)

        # Compress
        compressed, metadata = compressor.compress(gradient)

        # Check shape preserved
        assert compressed.shape == gradient.shape

        # Check metadata
        assert "shape" in metadata
        assert "threshold" in metadata
        assert "nnz" in metadata
        assert metadata["shape"] == gradient.shape

    def test_compression_ratio(self):
        """Test compression ratio effectiveness."""
        compressor = GradientCompressor(compression_ratio=0.1)

        # Create large gradient
        gradient = torch.randn(1000, 1000)

        # Compress
        compressed, metadata = compressor.compress(gradient)

        # Check compression ratio
        actual_ratio = metadata["compression_ratio"]
        assert actual_ratio > 0.8  # Should compress at least 80%

    def test_decompress_identity(self):
        """Test that decompression is identity for sparse gradients."""
        compressor = GradientCompressor(compression_ratio=0.1)

        gradient = torch.randn(100, 100)
        compressed, metadata = compressor.compress(gradient)
        decompressed = compressor.decompress(compressed, metadata)

        # Should be identical (compression is sparse)
        assert torch.equal(compressed, decompressed)

    def test_compression_stats(self):
        """Test compression statistics tracking."""
        compressor = GradientCompressor(compression_ratio=0.1)

        # Compress multiple gradients
        for _ in range(5):
            gradient = torch.randn(100, 100)
            compressor.compress(gradient)

        # Get stats
        stats = compressor.get_compression_stats()

        assert "total_elements" in stats
        assert "compressed_elements" in stats
        assert stats["total_elements"] == 5 * 100 * 100  # 5 gradients


# =============================================================================
# Tests: CRDT Gradient Synchronization
# =============================================================================

class TestCRDTGradientSync:
    """Test CRDT gradient synchronization."""

    def test_initialization(self):
        """Test CRDT sync initialization."""
        crdt_sync = CRDTGradientSync(rank=0, world_size=4, logger=None)

        assert crdt_sync.rank == 0
        assert crdt_sync.world_size == 4
        assert crdt_sync.fast_path_count == 0
        assert crdt_sync.slow_path_count == 0

    def test_version_vector(self):
        """Test version vector tracking."""
        crdt_sync = CRDTGradientSync(rank=0, world_size=4, logger=None)

        # Check initial version vector
        assert torch.equal(crdt_sync.version_vector, torch.zeros(4))

    def test_sync_stats(self):
        """Test synchronization statistics."""
        crdt_sync = CRDTGradientSync(rank=0, world_size=4, logger=None)

        # Increment counters
        crdt_sync.fast_path_count = 80
        crdt_sync.slow_path_count = 20

        # Get stats
        stats = crdt_sync.get_sync_stats()

        assert stats["fast_path_count"] == 80
        assert stats["slow_path_count"] == 20
        assert stats["fast_path_percentage"] == 80.0


# =============================================================================
# Tests: Distributed Config
# =============================================================================

class TestDistributedConfig:
    """Test distributed configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DistributedConfig()

        assert config.backend == "nccl"
        assert config.batch_size == 32
        assert config.num_epochs == 10
        assert config.use_crdt_sync == True
        assert config.use_amp == True

    def test_custom_config(self):
        """Test custom configuration."""
        config = DistributedConfig(
            batch_size=64,
            num_epochs=20,
            learning_rate=0.01,
            use_crdt_sync=False
        )

        assert config.batch_size == 64
        assert config.num_epochs == 20
        assert config.learning_rate == 0.01
        assert config.use_crdt_sync == False


# =============================================================================
# Tests: Distributed Trainer (Single GPU)
# =============================================================================

class TestDistributedTrainer:
    """Test distributed trainer functionality."""

    @pytest.fixture
    def trainer(self, simple_model, distributed_config):
        """Create trainer instance for testing."""
        # Use CPU for testing
        device = torch.device("cpu")

        # Mock distributed setup for single GPU testing
        import os
        os.environ["RANK"] = "0"
        os.environ["WORLD_SIZE"] = "1"
        os.environ["LOCAL_RANK"] = "0"
        os.environ["MASTER_ADDR"] = "localhost"
        os.environ["MASTER_PORT"] = "29500"

        # Create trainer (will skip actual distributed init)
        trainer = DistributedTrainer(
            model=simple_model,
            config=distributed_config,
            rank=0,
            world_size=1,
            device=device
        )

        yield trainer

        # Cleanup
        if torch.distributed.is_initialized():
            trainer.cleanup()

    def test_trainer_initialization(self, trainer):
        """Test trainer initialization."""
        assert trainer.rank == 0
        assert trainer.world_size == 1
        assert trainer.model is not None
        assert trainer.crdt_sync is not None  # Enabled in config

    def test_trainer_compressor(self, trainer):
        """Test gradient compressor setup."""
        assert trainer.compressor is not None
        assert trainer.compressor.compression_ratio == 0.1

    def test_create_dataloader(self, trainer, dummy_dataset):
        """Test distributed dataloader creation."""
        dataloader = trainer._create_dataloader(dummy_dataset, shuffle=True)

        assert dataloader is not None
        assert len(dataloader) > 0

        # Check batch
        batch = next(iter(dataloader))
        assert len(batch) == 2  # inputs, targets

    def test_checkpoint_directory(self, trainer, temp_checkpoint_dir):
        """Test checkpoint directory creation."""
        trainer._save_checkpoint(epoch=0)

        checkpoint_dir = Path(temp_checkpoint_dir)
        assert checkpoint_dir.exists()

        # Check checkpoint file
        checkpoint_files = list(checkpoint_dir.glob("*.pt"))
        assert len(checkpoint_files) > 0


# =============================================================================
# Tests: Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for distributed training."""

    @pytest.mark.skipif(
        not torch.cuda.is_available() or torch.cuda.device_count() < 2,
        reason="Requires at least 2 GPUs"
    )
    def test_multi_gpu_training(self, simple_model, dummy_dataset):
        """Test actual multi-GPU training."""
        if not torch.distributed.is_initialized():
            # Initialize process group
            torch.distributed.init_process_group(
                backend="nccl",
                init_method="tcp://localhost:29500",
                rank=0,
                world_size=torch.cuda.device_count()
            )

        try:
            # Test training on each GPU
            for gpu_id in range(min(2, torch.cuda.device_count())):
                device = torch.device(f"cuda:{gpu_id}")

                # Create model and move to device
                model = simple_model.to(device)

                # Create optimizer and loss
                optimizer = optim.Adam(model.parameters(), lr=0.001)
                criterion = nn.CrossEntropyLoss()

                # Training step
                model.train()
                inputs, targets = dummy_dataset[0]
                inputs = inputs.unsqueeze(0).to(device)
                targets = torch.tensor([targets]).to(device)

                # Forward pass
                outputs = model(inputs)
                loss = criterion(outputs, targets)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Check loss is finite
                assert torch.isfinite(loss)

        finally:
            if torch.distributed.is_initialized():
                torch.distributed.destroy_process_group()

    def test_training_loop(self, simple_model, dummy_dataset, distributed_config):
        """Test complete training loop (single GPU)."""
        # Use CPU for testing
        device = torch.device("cpu")

        # Create trainer
        trainer = DistributedTrainer(
            model=simple_model,
            config=distributed_config,
            rank=0,
            world_size=1,
            device=device
        )

        # Create optimizer and loss
        optimizer = optim.Adam(simple_model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        try:
            # Train for one epoch
            dataloader = trainer._create_dataloader(dummy_dataset, shuffle=True)
            metrics = trainer._train_epoch(dataloader, optimizer, criterion)

            # Check metrics
            assert "loss" in metrics
            assert "accuracy" in metrics
            assert metrics["loss"] > 0
            assert 0 <= metrics["accuracy"] <= 100

        finally:
            trainer.cleanup()


# =============================================================================
# Tests: Performance Tests
# =============================================================================

class TestPerformance:
    """Performance tests for distributed training."""

    def test_compression_performance(self):
        """Test gradient compression performance."""
        import time

        compressor = GradientCompressor(compression_ratio=0.1)

        # Create large gradient
        gradient = torch.randn(10000, 10000)

        # Measure compression time
        start = time.time()
        for _ in range(10):
            compressed, metadata = compressor.compress(gradient)
        compress_time = time.time() - start

        # Should be fast (< 1 second for 10 iterations)
        assert compress_time < 1.0

    def test_crdt_overhead(self):
        """Test CRDT synchronization overhead."""
        import time

        crdt_sync = CRDTGradientSync(rank=0, world_size=4, logger=None)

        # Create dummy model
        model = nn.Linear(1000, 1000)
        dummy_input = torch.randn(32, 1000)
        dummy_target = torch.randint(0, 10, (32,))

        # Setup optimizer and loss
        optimizer = optim.SGD(model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()

        # Measure training time with CRDT
        model.train()
        start = time.time()

        for _ in range(10):
            # Forward pass
            output = model(dummy_input)
            loss = criterion(output, dummy_target)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()

            # CRDT sync (mock - no actual distributed sync)
            # In real scenario, this would involve actual synchronization
            crdt_sync._is_fast_path_safe(model)

            optimizer.step()

        crdt_time = time.time() - start

        # Should complete in reasonable time
        assert crdt_time < 5.0  # 5 seconds for 10 iterations


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
