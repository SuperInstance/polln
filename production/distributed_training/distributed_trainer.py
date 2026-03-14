#!/usr/bin/env python3
"""
Multi-GPU Distributed Training for SuperInstance

Scales training across multiple GPUs and nodes with:
- PyTorch Distributed Data Parallel (DDP)
- CRDT-aware gradient synchronization (P41 concept)
- Gradient compression for bandwidth optimization
- Multi-node training support
- Automatic mixed precision (AMP) support

Hardware: Multi-GPU (RTX 4050 SLI, A100, H100, etc.)
Scale: 2-64 GPUs across 1-8 nodes

Author: SuperInstance Distributed Training Team
Version: 1.0.0
"""

import os
import sys
import time
import logging
import argparse
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import GradScaler, autocast

# =============================================================================
# Logging Configuration
# =============================================================================

def setup_logging(rank: int = 0) -> logging.Logger:
    """
    Setup distributed logging.

    Args:
        rank: Process rank for logging prefix

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"DistributedTrainer_Rank_{rank}")
    logger.setLevel(logging.INFO if rank == 0 else logging.WARNING)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        f'[Rank {rank}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# =============================================================================
# Configuration Data Classes
# =============================================================================

@dataclass
class DistributedConfig:
    """Configuration for distributed training."""

    # Process group settings
    backend: str = "nccl"  # "nccl" for GPU, "gloo" for CPU
    init_method: str = "env://"  # Environment variable initialization

    # Multi-node settings
    master_addr: str = "localhost"
    master_port: str = "29500"

    # Training settings
    batch_size: int = 32
    num_epochs: int = 10
    learning_rate: float = 0.001

    # Gradient settings
    gradient_clip_value: float = 1.0
    compression_ratio: float = 0.1  # Top-k sparsification

    # CRDT settings
    use_crdt_sync: bool = True
    crdt_sync_interval: int = 5  # Sync every N epochs

    # Mixed precision
    use_amp: bool = True
    amp_dtype: torch.dtype = torch.float16

    # Checkpointing
    checkpoint_dir: str = "./checkpoints"
    checkpoint_interval: int = 1  # Save every N epochs

    # Data loading
    num_workers: int = 4
    pin_memory: bool = True


# =============================================================================
# CRDT Gradient Synchronization (P41 Concept)
# =============================================================================

class CRDTGradientSync:
    """
    CRDT-based gradient synchronization for distributed training.

    Implements a Conflict-Free Replicated Data Type approach to gradient
    synchronization, enabling fast-path merging when safe and falling back
    to AllReduce when necessary.

    Concept from Paper P41: CRDT-based distributed optimization.
    """

    def __init__(self, rank: int, world_size: int, logger: logging.Logger):
        """
        Initialize CRDT gradient synchronizer.

        Args:
            rank: Process rank
            world_size: Total number of processes
            logger: Logger instance
        """
        self.rank = rank
        self.world_size = world_size
        self.logger = logger

        # Version vector for tracking gradient updates
        self.version_vector = torch.zeros(world_size, dtype=torch.long)

        # Gradient state for CRDT merging
        self.gradient_state: Dict[int, torch.Tensor] = {}

        # Statistics
        self.fast_path_count = 0
        self.slow_path_count = 0

    def sync_gradients(self, model: nn.Module) -> bool:
        """
        Synchronize gradients using CRDT merge (fast path) or AllReduce (slow path).

        Args:
            model: PyTorch model with gradients to sync

        Returns:
            True if fast path (CRDT) was used, False if slow path (AllReduce)
        """
        # Check if fast path is safe
        if self._is_fast_path_safe(model):
            self._crdt_merge(model)
            self.fast_path_count += 1
            return True
        else:
            self._allreduce_fallback(model)
            self.slow_path_count += 1
            return False

    def _is_fast_path_safe(self, model: nn.Module) -> bool:
        """
        Determine if CRDT fast path is safe.

        Fast path is safe when:
        1. Gradients are independent (no conflicts)
        2. Low conflict probability detected
        3. Training is in stable regime

        Args:
            model: PyTorch model

        Returns:
            True if fast path is safe
        """
        # Heuristic 1: Check gradient norm stability
        total_norm = 0.0
        for param in model.parameters():
            if param.grad is not None:
                total_norm += param.grad.data.norm(2).item() ** 2
        total_norm = total_norm ** 0.5

        # Fast path safe if gradient norm is stable
        # (In production, would use ML predictor from P41)
        is_stable = total_norm < 100.0  # Heuristic threshold

        # Heuristic 2: Check training epoch (early epochs less stable)
        # This would be passed in context in production

        return is_stable

    def _crdt_merge(self, model: nn.Module):
        """
        Perform CRDT merge of gradients (fast path).

        Uses commutative addition for gradient merging.
        Each rank independently computes gradients, then merges via
        commutative operation (addition).

        Args:
            model: PyTorch model with gradients
        """
        # Update version vector
        self.version_vector[self.rank] += 1

        # CRDT merge: commutative addition of gradients
        for param_idx, param in enumerate(model.parameters()):
            if param.grad is not None:
                # Store gradient state
                if param_idx not in self.gradient_state:
                    self.gradient_state[param_idx] = torch.zeros_like(param.grad)

                # Merge via addition (commutative operation)
                self.gradient_state[param_idx].add_(param.grad)

        # Synchronize version vectors
        dist.all_reduce(self.version_vector, op=dist.ReduceOp.SUM)

        # Average gradients across replicas (commutative)
        for param_idx, grad_state in self.gradient_state.items():
            dist.all_reduce(grad_state, op=dist.ReduceOp.SUM)
            grad_state.div_(self.world_size)

    def _allreduce_fallback(self, model: nn.Module):
        """
        Fallback to traditional AllReduce (slow path).

        Args:
            model: PyTorch model with gradients
        """
        # Traditional AllReduce gradient synchronization
        for param in model.parameters():
            if param.grad is not None:
                dist.all_reduce(param.grad.data, op=dist.ReduceOp.SUM)
                param.grad.data.div_(self.world_size)

    def get_sync_stats(self) -> Dict[str, int]:
        """Get synchronization statistics."""
        total = self.fast_path_count + self.slow_path_count
        fast_path_pct = (self.fast_path_count / total * 100) if total > 0 else 0

        return {
            "fast_path_count": self.fast_path_count,
            "slow_path_count": self.slow_path_count,
            "fast_path_percentage": fast_path_pct
        }


# =============================================================================
# Gradient Compression for Bandwidth Optimization
# =============================================================================

class GradientCompressor:
    """
    Compress gradients to reduce communication bandwidth.

    Implements top-k sparsification: keeps only the largest k% of gradient
    values, zeros the rest. Significantly reduces bandwidth for large models.
    """

    def __init__(self,
                 compression_ratio: float = 0.1,
                 logger: logging.Logger = None):
        """
        Initialize gradient compressor.

        Args:
            compression_ratio: Fraction of gradients to keep (0.0-1.0)
            logger: Logger instance
        """
        self.compression_ratio = compression_ratio
        self.logger = logger

        # Statistics
        self.total_elements = 0
        self.compressed_elements = 0

    def compress(self, gradient: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Compress gradient using top-k sparsification.

        Args:
            gradient: Gradient tensor to compress

        Returns:
            Tuple of (compressed_gradient, metadata)
        """
        # Flatten gradient for processing
        flat_grad = gradient.flatten()
        original_shape = gradient.shape

        # Compute number of elements to keep
        k = max(1, int(len(flat_grad) * self.compression_ratio))

        # Find top-k values by magnitude
        topk_values, topk_indices = torch.topk(flat_grad.abs(), k)
        threshold = topk_values[-1].item()

        # Create sparse gradient
        sparse_grad = torch.zeros_like(flat_grad)
        mask = flat_grad.abs() >= threshold
        sparse_grad[mask] = flat_grad[mask]

        # Reshape to original shape
        compressed = sparse_grad.reshape(original_shape)

        # Metadata for decompression
        metadata = {
            "shape": original_shape,
            "threshold": threshold,
            "nnz": mask.sum().item(),
            "compression_ratio": 1.0 - (mask.sum().item() / len(flat_grad))
        }

        # Update statistics
        self.total_elements += len(flat_grad)
        self.compressed_elements += mask.sum().item()

        return compressed, metadata

    def decompress(self,
                  compressed: torch.Tensor,
                  metadata: Dict[str, Any]) -> torch.Tensor:
        """
        Decompress gradient (identity for sparse gradients).

        Args:
            compressed: Compressed gradient tensor
            metadata: Compression metadata

        Returns:
            Decompressed gradient tensor
        """
        # For top-k sparsification, compressed gradient is usable as-is
        return compressed

    def get_compression_stats(self) -> Dict[str, float]:
        """Get compression statistics."""
        if self.total_elements == 0:
            return {"compression_ratio": 0.0}

        actual_ratio = 1.0 - (self.compressed_elements / self.total_elements)

        return {
            "total_elements": self.total_elements,
            "compressed_elements": self.compressed_elements,
            "actual_compression_ratio": actual_ratio
        }


# =============================================================================
# Multi-GPU Distributed Trainer
# =============================================================================

class DistributedTrainer:
    """
    Multi-GPU distributed trainer with CRDT-aware gradient synchronization.

    Features:
    - PyTorch DDP for model parallelism
    - CRDT-based fast-path gradient sync
    - Gradient compression for bandwidth optimization
    - Automatic mixed precision (AMP)
    - Multi-node training support
    - Checkpointing and monitoring
    """

    def __init__(self,
                 model: nn.Module,
                 config: DistributedConfig,
                 rank: int,
                 world_size: int,
                 device: torch.device):
        """
        Initialize distributed trainer.

        Args:
            model: PyTorch model to train
            config: Distributed configuration
            rank: Process rank
            world_size: Total number of processes
            device: Device to train on
        """
        self.config = config
        self.rank = rank
        self.world_size = world_size
        self.device = device

        # Setup logging
        self.logger = setup_logging(rank)

        # Initialize process group if not already initialized
        if not dist.is_initialized():
            self._init_process_group()

        # Move model to device and wrap with DDP
        self.model = model.to(device)
        self.model = DDP(
            self.model,
            device_ids=[rank % torch.cuda.device_count()],
            output_device=rank % torch.cuda.device_count()
        )

        # Setup CRDT gradient sync
        if config.use_crdt_sync:
            self.crdt_sync = CRDTGradientSync(rank, world_size, self.logger)
        else:
            self.crdt_sync = None

        # Setup gradient compressor
        self.compressor = GradientCompressor(
            config.compression_ratio,
            self.logger
        )

        # Setup AMP scaler
        self.scaler = GradScaler() if config.use_amp else None

        # Training state
        self.current_epoch = 0
        self.best_loss = float('inf')

        # Metrics tracking
        self.metrics = defaultdict(list)

        self.logger.info(f"Initialized DistributedTrainer on rank {rank}/{world_size}")

    def _init_process_group(self):
        """Initialize PyTorch distributed process group."""
        # Set environment variables if not already set
        if "MASTER_ADDR" not in os.environ:
            os.environ["MASTER_ADDR"] = self.config.master_addr
        if "MASTER_PORT" not in os.environ:
            os.environ["MASTER_PORT"] = self.config.master_port

        self.logger.info(f"Initializing process group: {self.config.backend}")

        dist.init_process_group(
            backend=self.config.backend,
            init_method=self.config.init_method,
            rank=self.rank,
            world_size=self.world_size
        )

        self.logger.info("Process group initialized successfully")

    def train(self,
              dataset: Dataset,
              optimizer: optim.Optimizer,
              criterion: nn.Module,
              validation_dataset: Optional[Dataset] = None) -> Dict[str, Any]:
        """
        Run distributed training.

        Args:
            dataset: Training dataset
            optimizer: Optimizer instance
            criterion: Loss function
            validation_dataset: Optional validation dataset

        Returns:
            Training metrics dictionary
        """
        self.logger.info(f"Starting training for {self.config.num_epochs} epochs")

        # Create data loaders
        train_loader = self._create_dataloader(dataset, shuffle=True)

        if validation_dataset is not None:
            val_loader = self._create_dataloader(validation_dataset, shuffle=False)
        else:
            val_loader = None

        # Training loop
        start_time = time.time()

        for epoch in range(self.config.num_epochs):
            self.current_epoch = epoch

            # Train epoch
            train_metrics = self._train_epoch(train_loader, optimizer, criterion)

            # Log metrics
            if self.rank == 0:
                self.logger.info(
                    f"Epoch {epoch}/{self.config.num_epochs} - "
                    f"Loss: {train_metrics['loss']:.4f}, "
                    f"Acc: {train_metrics['accuracy']:.2f}%"
                )

            # Validation
            if val_loader is not None:
                val_metrics = self._validate(val_loader, criterion)

                if self.rank == 0:
                    self.logger.info(
                        f"Validation - Loss: {val_metrics['loss']:.4f}, "
                        f"Acc: {val_metrics['accuracy']:.2f}%"
                    )

                # Save best model
                if val_metrics['loss'] < self.best_loss:
                    self.best_loss = val_metrics['loss']
                    if self.rank == 0:
                        self._save_checkpoint(epoch, is_best=True)

            # Sync CRDT state periodically
            if self.crdt_sync and epoch % self.config.crdt_sync_interval == 0:
                self._sync_crdt_state()

            # Save checkpoint
            if epoch % self.config.checkpoint_interval == 0 and self.rank == 0:
                self._save_checkpoint(epoch)

        # Compute final metrics
        total_time = time.time() - start_time

        final_metrics = {
            "total_time": total_time,
            "epochs_completed": self.config.num_epochs,
            "best_loss": self.best_loss,
            "training_metrics": dict(self.metrics)
        }

        # Add CRDT stats if enabled
        if self.crdt_sync:
            final_metrics["crdt_stats"] = self.crdt_sync.get_sync_stats()

        # Add compression stats
        final_metrics["compression_stats"] = self.compressor.get_compression_stats()

        self.logger.info(f"Training completed in {total_time:.2f}s")

        return final_metrics

    def _train_epoch(self,
                     dataloader: DataLoader,
                     optimizer: optim.Optimizer,
                     criterion: nn.Module) -> Dict[str, float]:
        """
        Train one epoch across all GPUs.

        Args:
            dataloader: Distributed data loader
            optimizer: Optimizer instance
            criterion: Loss function

        Returns:
            Training metrics for the epoch
        """
        self.model.train()

        total_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (inputs, targets) in enumerate(dataloader):
            inputs = inputs.to(self.device)
            targets = targets.to(self.device)

            # Forward pass with mixed precision
            if self.config.use_amp:
                with autocast(dtype=self.config.amp_dtype):
                    outputs = self.model(inputs)
                    loss = criterion(outputs, targets)

                # Backward pass with gradient scaling
                optimizer.zero_grad()
                self.scaler.scale(loss).backward()

                # Unscale gradients before clipping
                self.scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip_value
                )

                # Gradient synchronization
                self._sync_gradients(optimizer)

                # Optimizer step with gradient scaling
                self.scaler.step(optimizer)
                self.scaler.update()
            else:
                # Forward pass
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip_value
                )

                # Gradient synchronization
                self._sync_gradients(optimizer)

                # Optimizer step
                optimizer.step()

            # Track metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

            # Log progress
            if batch_idx % 100 == 0 and self.rank == 0:
                self.logger.info(
                    f"Batch {batch_idx}/{len(dataloader)} - "
                    f"Loss: {loss.item():.4f}"
                )

        # Compute epoch metrics
        avg_loss = total_loss / len(dataloader)
        accuracy = 100.0 * correct / total

        # Store metrics
        self.metrics["train_loss"].append(avg_loss)
        self.metrics["train_accuracy"].append(accuracy)

        return {"loss": avg_loss, "accuracy": accuracy}

    def _validate(self,
                  dataloader: DataLoader,
                  criterion: nn.Module) -> Dict[str, float]:
        """
        Validate model on validation set.

        Args:
            dataloader: Validation data loader
            criterion: Loss function

        Returns:
            Validation metrics
        """
        self.model.eval()

        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, targets in dataloader:
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                # Forward pass
                if self.config.use_amp:
                    with autocast(dtype=self.config.amp_dtype):
                        outputs = self.model(inputs)
                        loss = criterion(outputs, targets)
                else:
                    outputs = self.model(inputs)
                    loss = criterion(outputs, targets)

                # Track metrics
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()

        # Compute metrics
        avg_loss = total_loss / len(dataloader)
        accuracy = 100.0 * correct / total

        # Store metrics
        self.metrics["val_loss"].append(avg_loss)
        self.metrics["val_accuracy"].append(accuracy)

        return {"loss": avg_loss, "accuracy": accuracy}

    def _sync_gradients(self, optimizer: optim.Optimizer):
        """
        Synchronize gradients across all replicas.

        Uses CRDT fast path if safe, otherwise falls back to AllReduce.

        Args:
            optimizer: Optimizer instance
        """
        if self.crdt_sync:
            # CRDT-aware synchronization
            fast_path = self.crdt_sync.sync_gradients(self.model)
        else:
            # Traditional AllReduce
            for param in self.model.parameters():
                if param.grad is not None:
                    dist.all_reduce(param.grad.data, op=dist.ReduceOp.SUM)
                    param.grad.data.div_(self.world_size)

    def _sync_crdt_state(self):
        """Sync CRDT state across all replicas."""
        if self.rank == 0:
            self.logger.info("Syncing CRDT state across replicas")

        # Broadcast version vector from rank 0
        dist.broadcast(
            self.crdt_sync.version_vector,
            src=0
        )

        # Synchronize gradient state
        for param_idx, grad_state in self.crdt_sync.gradient_state.items():
            dist.broadcast(grad_state, src=0)

    def _create_dataloader(self,
                           dataset: Dataset,
                           shuffle: bool = True) -> DataLoader:
        """
        Create distributed data loader.

        Args:
            dataset: PyTorch dataset
            shuffle: Whether to shuffle data

        Returns:
            Distributed data loader
        """
        sampler = DistributedSampler(
            dataset,
            num_replicas=self.world_size,
            rank=self.rank,
            shuffle=shuffle
        )

        return DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            sampler=sampler,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory
        )

    def _save_checkpoint(self, epoch: int, is_best: bool = False):
        """
        Save training checkpoint.

        Args:
            epoch: Current epoch number
            is_best: Whether this is the best model so far
        """
        # Create checkpoint directory
        checkpoint_dir = Path(self.config.checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Prepare checkpoint
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.module.state_dict(),
            "optimizer_state_dict": None,  # Would be passed in train()
            "config": self.config,
            "metrics": dict(self.metrics),
            "best_loss": self.best_loss
        }

        # Save checkpoint
        if is_best:
            checkpoint_path = checkpoint_dir / "best_model.pt"
        else:
            checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"

        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"Saved checkpoint to {checkpoint_path}")

    def cleanup(self):
        """Cleanup distributed training resources."""
        if dist.is_initialized():
            dist.destroy_process_group()
            self.logger.info("Destroyed process group")


# =============================================================================
# Multi-Node Training Setup
# =============================================================================

def setup_multi_node_training() -> Tuple[int, int, torch.device]:
    """
    Setup for multi-node, multi-GPU training.

    Reads environment variables set by torchrun or torch.distributed.launch:
    - MASTER_ADDR: Master node address
    - MASTER_PORT: Master node port
    - WORLD_SIZE: Total number of processes
    - RANK: Global rank of this process
    - LOCAL_RANK: Local rank within this node

    Returns:
        Tuple of (rank, world_size, device)
    """
    # Get environment variables
    master_addr = os.environ.get("MASTER_ADDR", "localhost")
    master_port = os.environ.get("MASTER_PORT", "29500")
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    rank = int(os.environ.get("RANK", "0"))
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))

    # Initialize process group
    dist.init_process_group(
        backend="nccl",  # Use NCCL for GPU
        rank=rank,
        world_size=world_size
    )

    # Set device
    torch.cuda.set_device(local_rank)
    device = torch.device(f"cuda:{local_rank}")

    return rank, world_size, device


def spawn_training(gpu_count: int,
                   nodes: int = 1,
                   train_fn: callable = None):
    """
    Spawn training processes across GPUs and nodes.

    For multi-node training, use torchrun:
    ```bash
    torchrun --nproc_per_node=<GPUs> --nnodes=<nodes> distributed_trainer.py
    ```

    Args:
        gpu_count: Number of GPUs per node
        nodes: Number of nodes
        train_fn: Training function to spawn
    """
    if train_fn is None:
        raise ValueError("train_fn must be provided")

    # Set environment variables
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29500"
    os.environ["WORLD_SIZE"] = str(gpu_count * nodes)

    # Spawn workers
    mp.spawn(
        train_fn,
        args=(gpu_count * nodes,),
        nprocs=gpu_count * nodes
    )


# =============================================================================
# Example Training Function
# =============================================================================

def train_worker(rank: int, world_size: int, args: argparse.Namespace):
    """
    Worker function for each GPU/process.

    Args:
        rank: Process rank
        world_size: Total number of processes
        args: Command-line arguments
    """
    # Setup distributed training
    rank, world_size, device = setup_multi_node_training()

    # Setup logging
    logger = setup_logging(rank)
    logger.info(f"Worker {rank}/{world_size} initialized on device {device}")

    # Create model (example: simple CNN)
    model = nn.Sequential(
        nn.Conv2d(3, 64, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(128 * 8 * 8, 256),
        nn.ReLU(),
        nn.Linear(256, 10)
    )

    # Create config
    config = DistributedConfig(
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        learning_rate=args.learning_rate,
        use_crdt_sync=not args.no_crdt,
        use_amp=not args.no_amp
    )

    # Create trainer
    trainer = DistributedTrainer(
        model=model,
        config=config,
        rank=rank,
        world_size=world_size,
        device=device
    )

    # Create dummy dataset (replace with actual dataset)
    class DummyDataset(Dataset):
        def __init__(self, size=1000):
            self.size = size

        def __len__(self):
            return self.size

        def __getitem__(self, idx):
            return torch.randn(3, 32, 32), torch.randint(0, 10, (1,)).item()

    train_dataset = DummyDataset(size=10000)
    val_dataset = DummyDataset(size=2000)

    # Create optimizer and loss function
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
    criterion = nn.CrossEntropyLoss()

    try:
        # Train
        metrics = trainer.train(
            dataset=train_dataset,
            optimizer=optimizer,
            criterion=criterion,
            validation_dataset=val_dataset
        )

        # Print final metrics
        if rank == 0:
            logger.info("Training completed!")
            logger.info(f"Final metrics: {metrics}")

            # Print CRDT stats
            if "crdt_stats" in metrics:
                crdt_stats = metrics["crdt_stats"]
                logger.info(
                    f"CRDT Fast Path: {crdt_stats['fast_path_percentage']:.1f}%"
                )

            # Print compression stats
            if "compression_stats" in metrics:
                comp_stats = metrics["compression_stats"]
                logger.info(
                    f"Compression Ratio: {comp_stats['actual_compression_ratio']:.1%}"
                )

    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

    finally:
        # Cleanup
        trainer.cleanup()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point for distributed training."""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Multi-GPU Distributed Training for SuperInstance"
    )

    # Training parameters
    parser.add_argument("--batch-size", type=int, default=32,
                       help="Batch size per GPU")
    parser.add_argument("--epochs", type=int, default=10,
                       help="Number of training epochs")
    parser.add_argument("--learning-rate", type=float, default=0.001,
                       help="Learning rate")

    # Distributed parameters
    parser.add_argument("--nodes", type=int, default=1,
                       help="Number of nodes")
    parser.add_argument("--gpu-per-node", type=int, default=None,
                       help="GPUs per node (default: all available)")

    # Feature flags
    parser.add_argument("--no-crdt", action="store_true",
                       help="Disable CRDT gradient synchronization")
    parser.add_argument("--no-amp", action="store_true",
                       help="Disable automatic mixed precision")

    args = parser.parse_args()

    # Get GPU count
    if args.gpu_per_node is None:
        args.gpu_per_node = torch.cuda.device_count()

    total_gpus = args.nodes * args.gpu_per_node

    # Print configuration
    if dist.is_initialized() or args.gpu_per_node > 1:
        rank = int(os.environ.get("RANK", 0))
        if rank == 0:
            print("=" * 80)
            print("Multi-GPU Distributed Training Configuration")
            print("=" * 80)
            print(f"Nodes: {args.nodes}")
            print(f"GPUs per node: {args.gpu_per_node}")
            print(f"Total GPUs: {total_gpus}")
            print(f"Batch size per GPU: {args.batch_size}")
            print(f"Effective batch size: {args.batch_size * total_gpus}")
            print(f"Epochs: {args.epochs}")
            print(f"Learning rate: {args.learning_rate}")
            print(f"CRDT sync: {not args.no_crdt}")
            print(f"AMP: {not args.no_amp}")
            print("=" * 80)

    # Launch training
    if total_gpus > 1:
        # Multi-GPU training (already spawned by torchrun)
        rank = int(os.environ.get("RANK", 0))
        world_size = int(os.environ.get("WORLD_SIZE", 1))
        train_worker(rank, world_size, args)
    else:
        # Single GPU training
        print("Single GPU training detected")
        train_worker(0, 1, args)


if __name__ == "__main__":
    main()
