#!/usr/bin/env python3
"""
Example: Training CIFAR-10 with Distributed SuperInstance

This example demonstrates how to train a simple CNN on CIFAR-10
using the multi-GPU distributed training system.

Usage:
    # Single node, 4 GPUs
    torchrun --nproc_per_node=4 example_cifar10.py

    # Multi-node, 4 GPUs per node
    torchrun --nproc_per_node=4 --nnodes=2 --node_rank=0 --master_addr="192.168.1.1" example_cifar10.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from distributed_trainer import (
    DistributedTrainer,
    DistributedConfig,
    setup_multi_node_training
)


class CIFAR10CNN(nn.Module):
    """Simple CNN for CIFAR-10 classification."""

    def __init__(self, num_classes=10):
        super(CIFAR10CNN, self).__init__()

        self.features = nn.Sequential(
            # Conv block 1
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Conv block 2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Conv block 3
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256 * 4 * 4, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def main():
    """Main training function."""

    # Setup distributed training
    rank, world_size, device = setup_multi_node_training()

    # Configuration
    config = DistributedConfig(
        batch_size=128,  # Per GPU
        num_epochs=100,
        learning_rate=0.001,
        gradient_clip_value=1.0,
        compression_ratio=0.1,  # Top 10% gradients
        use_crdt_sync=True,
        crdt_sync_interval=5,
        use_amp=True,
        checkpoint_dir="./checkpoints/cifar10",
        checkpoint_interval=10,
        num_workers=4,
        pin_memory=True
    )

    # Print configuration (rank 0 only)
    if rank == 0:
        print("=" * 80)
        print("CIFAR-10 Distributed Training")
        print("=" * 80)
        print(f"World Size: {world_size}")
        print(f"Effective Batch Size: {config.batch_size * world_size}")
        print(f"Epochs: {config.num_epochs}")
        print(f"Learning Rate: {config.learning_rate}")
        print(f"CRDT Sync: {config.use_crdt_sync}")
        print(f"AMP: {config.use_amp}")
        print(f"Compression Ratio: {config.compression_ratio}")
        print("=" * 80)

    # Create model
    model = CIFAR10CNN(num_classes=10).to(device)

    if rank == 0:
        print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Data transforms
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    # Load datasets
    if rank == 0:
        print("Loading datasets...")

    train_dataset = torchvision.datasets.CIFAR10(
        root="./data",
        train=True,
        download=True,  # Only rank 0 downloads
        transform=transform_train
    )

    test_dataset = torchvision.datasets.CIFAR10(
        root="./data",
        train=False,
        download=True,
        transform=transform_test
    )

    if rank == 0:
        print(f"Train samples: {len(train_dataset):,}")
        print(f"Test samples: {len(test_dataset):,}")

    # Create trainer
    trainer = DistributedTrainer(
        model=model,
        config=config,
        rank=rank,
        world_size=world_size,
        device=device
    )

    # Create optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config.num_epochs
    )
    criterion = nn.CrossEntropyLoss()

    # Training loop with learning rate scheduling
    for epoch in range(config.num_epochs):
        # Train for one epoch
        train_loader = trainer._create_dataloader(train_dataset, shuffle=True)
        test_loader = trainer._create_dataloader(test_dataset, shuffle=False)

        # Train epoch
        train_metrics = trainer._train_epoch(train_loader, optimizer, criterion)

        # Validation
        val_metrics = trainer._validate(test_loader, criterion)

        # Update learning rate
        scheduler.step()

        # Log metrics
        if rank == 0:
            print(
                f"Epoch {epoch}/{config.num_epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.2f}% | "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Acc: {val_metrics['accuracy']:.2f}% | "
                f"LR: {scheduler.get_last_lr()[0]:.6f}"
            )

            # Save checkpoint
            if epoch % config.checkpoint_interval == 0:
                trainer._save_checkpoint(epoch, is_best=(val_metrics['loss'] < trainer.best_loss))

        # Sync CRDT state periodically
        if config.use_crdt_sync and epoch % config.crdt_sync_interval == 0:
            trainer._sync_crdt_state()

    # Print final metrics
    if rank == 0:
        print("=" * 80)
        print("Training completed!")
        print(f"Best validation loss: {trainer.best_loss:.4f}")

        # Print CRDT stats
        if config.use_crdt_sync and trainer.crdt_sync:
            stats = trainer.crdt_sync.get_sync_stats()
            print(f"CRDT Fast Path: {stats['fast_path_percentage']:.1f}%")
            print(f"Fast Path Count: {stats['fast_path_count']}")
            print(f"Slow Path Count: {stats['slow_path_count']}")

        # Print compression stats
        if trainer.compressor:
            stats = trainer.compressor.get_compression_stats()
            print(f"Compression Ratio: {stats['actual_compression_ratio']:.1%}")
        print("=" * 80)

    # Cleanup
    trainer.cleanup()


if __name__ == "__main__":
    main()
