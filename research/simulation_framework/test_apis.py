#!/usr/bin/env python3
"""
Quick test of API connectivity
"""

import asyncio
import sys
from pathlib import Path

# Add apikey folder to path
api_key_dir = Path(__file__).parent.parent.parent / "apikey"
sys.path.insert(0, str(api_key_dir))

from multi_api_orchestrator import MultiAPIOrchestrator, SimulationRequest, ModelCapability


async def test_single_api():
    """Test a single API call"""
    print("Initializing MultiAPI Orchestrator...")
    orchestrator = MultiAPIOrchestrator()

    print(f"\nLoaded models: {list(orchestrator.models.keys())}")

    # Simple test request
    request = SimulationRequest(
        prompt="What is CRDT? Explain in one paragraph.",
        required_capabilities=[ModelCapability.REASONING],
        max_tokens=500
    )

    # Test with one model
    model_name = list(orchestrator.models.keys())[0]
    print(f"\nTesting model: {model_name}")

    result = await orchestrator.call_model(model_name, request)

    print(f"\nResponse from {result.model_name}:")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Cost: ${result.cost:.6f}")
    print(f"Latency: {result.latency_ms:.1f}ms")
    print(f"\nContent:\n{result.response[:500]}...")

    # Print stats
    stats = orchestrator.get_simulation_stats()
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    asyncio.run(test_single_api())
