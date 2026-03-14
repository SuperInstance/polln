#!/usr/bin/env python3
"""
Mini Research Ideation Test - Quick validation
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add apikey folder to path
api_key_dir = Path(__file__).parent.parent.parent / "apikey"
sys.path.insert(0, str(api_key_dir))

from multi_api_orchestrator import (
    MultiAPIOrchestrator,
    SimulationRequest,
    ModelCapability
)


async def quick_test():
    """Quick test of multiple APIs"""
    print(">>> Starting Multi-API Research Ideation Test\n")
    print("="*60)

    orchestrator = MultiAPIOrchestrator()

    # Test prompt for research ideation
    test_prompt = """Generate 3 novel, testable research hypotheses about CRDT-Enhanced SuperInstance coordination.

For each hypothesis provide:
1. A clear claim
2. The theoretical basis
3. A validation method

Format as a numbered list."""

    print(f"\n>>> Test Prompt:\n{test_prompt}\n")
    print("="*60)

    request = SimulationRequest(
        prompt=test_prompt,
        required_capabilities=[
            ModelCapability.CREATIVE,
            ModelCapability.REASONING
        ],
        max_tokens=2000,
        ensemble=True
    )

    print("\n>>> Running ensemble simulation across multiple models...\n")

    result = await orchestrator.simulate_ensemble(request)

    print("\n" + "="*60)
    print(">>> ENSEMBLE RESULTS")
    print("="*60)

    print(f"\n>>> Models used: {len(result.results)}")
    for r in result.results:
        print(f"  - {r.model_name}: {r.tokens_used} tokens, ${r.cost:.6f}")

    print(f"\n>>> Consensus confidence: {result.confidence:.2f}")
    print(f">>> Disagreement score: {result.disagreement_score:.2f}")

    print("\n" + "="*60)
    print(">>> SYNTHESIZED HYPOTHESES")
    print("="*60)
    print(result.consensus)

    # Save results
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = results_dir / f"mini_test_{timestamp}.json"

    output_data = {
        "timestamp": timestamp,
        "prompt": test_prompt,
        "models_used": [r.model_name for r in result.results],
        "total_tokens": sum(r.tokens_used for r in result.results),
        "total_cost": sum(r.cost for r in result.results),
        "consensus": result.consensus
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n>>> Results saved to: {output_file}")

    # Print stats
    stats = orchestrator.get_simulation_stats()
    print(f"\n>>> Session Statistics:")
    print(f"  - Total API calls: {stats.get('total_simulations', 0)}")
    print(f"  - Total tokens: {stats.get('total_tokens', 0):,}")
    print(f"  - Total cost: ${stats.get('total_cost_usd', 0):.6f}")

    print("\n" + "="*60)
    print(">>> Mini test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(quick_test())
