"""
TernaryAir Demo

Run with:
    python -c "from ternaryair import demo; demo.run()"
    
Or:
    python -m ternaryair.demo
"""

import time


def run():
    """Run the TernaryAir demonstration"""
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           TernaryAir Simulator Demo                          ║")
    print("║           Open-Source Ternary Inference                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Import simulator
    print(">>> Loading simulator...")
    from .simulator import Simulator
    print(">>> ✓ Simulator loaded")
    print()
    
    # Initialize
    print(">>> Initializing model...")
    sim = Simulator(model="tiny")
    print(f">>> ✓ Model: {sim.config.name} ({sim.config.params} parameters)")
    print(f">>> ✓ Layers: {sim.config.layers}")
    print(f">>> ✓ Dimension: {sim.config.dim}")
    print()
    
    # Run inference examples
    print("─" * 64)
    print("  Inference Examples")
    print("─" * 64)
    print()
    
    prompts = [
        "Hello, TernaryAir",
        "The ternary architecture uses weights",
        "Edge AI inference requires",
    ]
    
    for prompt in prompts:
        print(f">>> Input: \"{prompt}\"")
        start = time.time()
        response = sim.generate(prompt, max_tokens=15)
        elapsed = (time.time() - start) * 1000
        print(f"    ({elapsed:.0f}ms)")
        print(f"    Output: \"{response}\"")
        print()
    
    # Show stats
    print("─" * 64)
    print("  Performance Statistics")
    print("─" * 64)
    print()
    
    stats = sim.stats()
    print(f"  Tokens generated: {stats['tokens_generated']}")
    print(f"  Inference time: {stats['inference_time_ms']:.0f}ms")
    print(f"  Avg speed: {stats['avg_tokens_per_second']:.1f} tok/s")
    print(f"  Weight sparsity: {stats['weight_sparsity']*100:.1f}%")
    print()
    
    # Explain what's happening
    print("─" * 64)
    print("  How It Works")
    print("─" * 64)
    print("""
  Ternary weights use just three values: {-1, 0, +1}

  Traditional multiplication:
      result = input × weight
      (requires expensive multiplier circuits)

  Ternary rotation:
      +1: result = input (pass through)
       0: result = 0 (skip)
      -1: result = -input (negate)
      (requires only sign manipulation)

  This eliminates multipliers:
  • ~90% reduction in arithmetic gates
  • ~85% reduction in power consumption
  • Simpler hardware design

  In real TernaryAir hardware:
  • Weights are mask-locked in metal layers
  • Zero memory access latency
  • Zero access energy
  • Cannot be modified by software

  This simulator demonstrates the behavior on CPU.
  Target hardware would run 100+ tok/s at 3-5 watts.
    """)
    
    print("─" * 64)
    print()
    print(">>> Demo complete!")
    print(">>> Learn more: https://github.com/superinstance/ternaryair")
    print()


if __name__ == "__main__":
    run()
