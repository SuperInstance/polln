#!/usr/bin/env python
"""
Quick Start Script for POLLN Meta-Learning

Run this to quickly set up and test the meta-learning system.
"""

import sys
import subprocess
from pathlib import Path


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          POLLN Meta-Learning System - Quick Start           ║
║                                                              ║
║  Model-Agnostic Meta-Learning for Rapid Adaptation          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    required = [
        ('numpy', 'numpy'),
        ('torch', 'torch'),
        ('matplotlib', 'matplotlib'),
        ('sklearn', 'scikit-learn'),
        ('scipy', 'scipy')
    ]

    missing = []

    for module, package in required:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False

    print("\n✅ All dependencies installed!")
    return True


def create_directories():
    """Create required directories"""
    print("\nCreating directories...")

    dirs = [
        'simulations/advanced/metalearning',
        'src/core/meta'
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

    print("\n✅ Directories created!")


def run_quick_test():
    """Run quick meta-learning test"""
    print("\n" + "="*60)
    print("Running Quick Meta-Learning Test")
    print("="*60)

    # Quick MAML test
    print("\n1. Testing MAML...")
    test_maml()

    # Quick Reptile test
    print("\n2. Testing Reptile...")
    test_reptile()

    # Quick config generation
    print("\n3. Generating configuration...")
    generate_config()

    print("\n" + "="*60)
    print("✅ Quick test complete!")
    print("="*60)


def test_maml():
    """Quick MAML test"""
    import torch
    import torch.nn as nn

    # Simple model
    model = nn.Sequential(
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Linear(256, 1)
    )

    # Mock task
    task = {
        'support_x': torch.randn(10, 128),
        'support_y': torch.randn(10),
        'query_x': torch.randn(5, 128),
        'query_y': torch.randn(5)
    }

    # Inner loop (adaptation)
    adapted = nn.Sequential(
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Linear(256, 1)
    )
    adapted.load_state_dict(model.state_dict())

    optimizer = torch.optim.SGD(adapted.parameters(), lr=0.01)

    for _ in range(5):  # 5 gradient steps
        optimizer.zero_grad()
        loss = nn.functional.mse_loss(
            adapted(task['support_x']).squeeze(),
            task['support_y']
        )
        loss.backward()
        optimizer.step()

    # Evaluate
    with torch.no_grad():
        query_loss = nn.functional.mse_loss(
            adapted(task['query_x']).squeeze(),
            task['query_y']
        )

    print(f"  ✓ MAML adaptation complete")
    print(f"    Query loss: {query_loss.item():.4f}")


def test_reptile():
    """Quick Reptile test"""
    import torch
    import torch.nn as nn

    # Simple model
    model = nn.Sequential(
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Linear(256, 1)
    )

    # Mock task
    task = {
        'support_x': torch.randn(10, 128),
        'support_y': torch.randn(10)
    }

    # Store original params
    original_params = {name: param.clone()
                      for name, param in model.named_parameters()}

    # Adapt
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    for _ in range(10):  # 10 gradient steps
        optimizer.zero_grad()
        loss = nn.functional.mse_loss(
            model(task['support_x']).squeeze(),
            task['support_y']
        )
        loss.backward()
        optimizer.step()

    # Compute gradient difference
    with torch.no_grad():
        for name, param in model.named_parameters():
            grad_diff = param.data - original_params[name]
            print(f"  ✓ {name}: diff norm = {grad_diff.norm().item():.4f}")


def generate_config():
    """Generate meta-learning configuration"""
    import json

    config = {
        'enabled': True,
        'preferredMethod': 'maml',
        'maml': {
            'innerLoop': {
                'learningRate': 0.01,
                'steps': 5
            },
            'outerLoop': {
                'learningRate': 0.001,
                'metaBatchSize': 32
            }
        },
        'reptile': {
            'metaLearningRate': 0.1,
          'innerSteps': 10,
          'metaBatchSize': 32
        },
        'fewShot': {
            'k': 5,
            'ways': 5
        },
        'adaptation': {
            'strategy': 'lora',
            'lora': {
                'rank': 16,
                'alpha': 32
            }
        }
    }

    # Save JSON config
    config_path = 'simulations/advanced/metalearning/quick_config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  ✓ Configuration saved to {config_path}")


def print_next_steps():
    """Print next steps"""
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)

    print("""
1. Run full simulations:
   python simulations/advanced/metalearning/run_all.py

2. Run specific component:
   python simulations/advanced/metalearning/maml_implementation.py
   python simulations/advanced/metalearning/reptile_implementation.py

3. Run tests:
   python simulations/advanced/metalearning/test_metalearning.py

4. View generated files:
   - TypeScript config: src/core/meta/learning.ts
   - Documentation: simulations/advanced/metalearning/README.md
   - Guide: simulations/advanced/metalearning/META_LEARNING_GUIDE.md

5. Use in your code:
   import {{ META_LEARNING_CONFIG }} from './core/meta/learning'
    """)


def main():
    """Main entry point"""
    print_banner()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Create directories
    create_directories()

    # Run quick test
    run_quick_test()

    # Print next steps
    print_next_steps()

    print("\n" + "="*60)
    print("Quick start complete! 🎉")
    print("="*60)
    print("\nFor full implementation, run:")
    print("  python simulations/advanced/metalearning/run_all.py")
    print()


if __name__ == '__main__':
    main()
