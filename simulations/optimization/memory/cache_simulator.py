"""
Realistic KV-Cache Simulator for POLLN

This script provides a realistic cache simulator that models production
KV-cache access patterns for transformers and LLMs.

Patterns modeled:
- Attention key/value reuse
- Context window patterns
- Multi-turn conversation patterns
- Agent preference patterns
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import random

class CacheAccessType(Enum):
    """Types of cache accesses"""
    ATTENTION_KEY = "attention_key"
    ATTENTION_VALUE = "attention_value"
    MLP_ACTIVATION = "mlp_activation"
    EMBEDDING = "embedding"
    FFN_STATE = "ffn_state"

class AccessPattern(Enum):
    """High-level access patterns"""
    SEQUENTIAL_DECODE = "sequential_decode"  # Autoregressive generation
    CONTEXT_REUSE = "context_reuse"          # Reuse cached context
    MULTI_TURN = "multi_turn"                # Multi-turn conversation
    LONG_CONTEXT = "long_context"            # Long documents
    BRANCHING = "branching"                  # Tree-based exploration

@dataclass
class CacheAccess:
    """A single cache access"""
    timestamp: float
    access_type: CacheAccessType
    key: str
    size: int
    layer: int
    token_id: int
    context_id: str

@dataclass
class SimulatorConfig:
    """Configuration for cache simulator"""
    num_layers: int = 32
    hidden_dim: int = 4096
    num_heads: int = 32
    head_dim: int = 128
    vocab_size: int = 50000
    max_context_length: int = 8192

class KVCacheSimulator:
    """
    Realistic KV-cache simulator for transformer models

    Models the actual access patterns seen in production LLM systems
    """

    def __init__(self, config: SimulatorConfig = None):
        """Initialize simulator"""
        self.config = config or SimulatorConfig()

        # State
        self.current_time = 0.0
        self.contexts = {}  # context_id -> context state
        self.active_context = None

        # Statistics
        self.stats = {
            'total_accesses': 0,
            'by_type': defaultdict(int),
            'by_layer': defaultdict(int),
            'reuse_distance': [],
            'access_intervals': []
        }

    def generate_attention_kv(
        self,
        token_id: int,
        layer: int,
        context_id: str
    ) -> Tuple[str, int, str]:
        """
        Generate attention K/V cache access

        Args:
            token_id: Token position
            layer: Layer number
            context_id: Conversation context

        Returns:
            (key, size, access_type)
        """
        # Key: {context}_layer{layer}_token{token_id}
        key = f"{context_id}_l{layer}_t{token_id}"

        # Size: hidden_dim * num_heads * head_dim (simplified)
        size = self.config.hidden_dim * 4  # 4 bytes per float32

        access_type = CacheAccessType.ATTENTION_KEY

        return key, size, access_type

    def generate_mlp_activation(
        self,
        token_id: int,
        layer: int,
        context_id: str
    ) -> Tuple[str, int, str]:
        """
        Generate MLP activation cache access

        Args:
            token_id: Token position
            layer: Layer number
            context_id: Conversation context

        Returns:
            (key, size, access_type)
        """
        key = f"{context_id}_mlp_l{layer}_t{token_id}"
        size = self.config.hidden_dim * 4
        access_type = CacheAccessType.MLP_ACTIVATION

        return key, size, access_type

    def simulate_sequential_decode(
        self,
        context_id: str,
        num_tokens: int = 100,
        start_token: int = 0
    ) -> List[CacheAccess]:
        """
        Simulate autoregressive sequential decoding

        This is the most common pattern: each new token attends to all
        previous tokens, creating O(n^2) access pattern.

        Args:
            context_id: Context identifier
            num_tokens: Number of tokens to generate
            start_token: Starting token position

        Returns:
            List of cache accesses
        """
        accesses = []

        for new_token in range(start_token, start_token + num_tokens):
            # New token attends to all previous tokens
            for layer in range(self.config.num_layers):
                # Access previous tokens' K/V (these should be cached)
                for prev_token in range(0, new_token):
                    key, size, access_type = self.generate_attention_kv(
                        prev_token, layer, context_id
                    )

                    access = CacheAccess(
                        timestamp=self.current_time,
                        access_type=access_type,
                        key=key,
                        size=size,
                        layer=layer,
                        token_id=prev_token,
                        context_id=context_id
                    )
                    accesses.append(access)
                    self.current_time += 0.001

                # Compute and store new token's K/V
                key, size, access_type = self.generate_attention_kv(
                    new_token, layer, context_id
                )

                access = CacheAccess(
                    timestamp=self.current_time,
                    access_type=access_type,
                    key=key,
                    size=size,
                    layer=layer,
                    token_id=new_token,
                    context_id=context_id
                )
                accesses.append(access)
                self.current_time += 0.001

                # MLP activation
                key, size, access_type = self.generate_mlp_activation(
                    new_token, layer, context_id
                )

                access = CacheAccess(
                    timestamp=self.current_time,
                    access_type=access_type,
                    key=key,
                    size=size,
                    layer=layer,
                    token_id=new_token,
                    context_id=context_id
                )
                accesses.append(access)
                self.current_time += 0.001

        return accesses

    def simulate_context_reuse(
        self,
        base_context: str,
        num_turns: int = 5,
        tokens_per_turn: int = 50
    ) -> List[CacheAccess]:
        """
        Simulate context reuse across multiple turns

        In multi-turn conversations, we reuse the shared context prefix
        and only compute new tokens.

        Args:
            base_context: Base context ID
            num_turns: Number of conversation turns
            tokens_per_turn: Tokens generated per turn

        Returns:
            List of cache accesses
        """
        accesses = []

        # First turn: generate initial context
        accesses.extend(
            self.simulate_sequential_decode(base_context, tokens_per_turn)
        )

        # Subsequent turns: reuse context
        for turn in range(1, num_turns):
            turn_context = f"{base_context}_turn{turn}"
            start_token = turn * tokens_per_turn

            # Reuse: access existing context (should be in cache)
            for layer in range(self.config.num_layers):
                for prev_token in range(0, start_token):
                    key, size, access_type = self.generate_attention_kv(
                        prev_token, layer, base_context
                    )

                    access = CacheAccess(
                        timestamp=self.current_time,
                        access_type=access_type,
                        key=key,
                        size=size,
                        layer=layer,
                        token_id=prev_token,
                        context_id=base_context
                    )
                    accesses.append(access)
                    self.current_time += 0.001

            # Generate new tokens for this turn
            accesses.extend(
                self.simulate_sequential_decode(
                    turn_context, tokens_per_turn, start_token
                )
            )

        return accesses

    def simulate_long_context(
        self,
        context_id: str,
        num_tokens: int = 10000
    ) -> List[CacheAccess]:
        """
        Simulate long context processing

        For long documents, we see interesting patterns:
- Recent tokens accessed frequently
- Periodic "re-attention" to older tokens
- Compression of middle tokens

        Args:
            context_id: Context identifier
            num_tokens: Total tokens in document

        Returns:
            List of cache accesses
        """
        accesses = []

        # Process in chunks
        chunk_size = 512

        for chunk_start in range(0, num_tokens, chunk_size):
            chunk_end = min(chunk_start + chunk_size, num_tokens)

            # Generate tokens in this chunk
            for new_token in range(chunk_start, chunk_end):
                for layer in range(self.config.num_layers):
                    # Access pattern for long context:
                    # - Always access recent 512 tokens
                    # - Sample from older tokens (re-attention)

                    # Recent tokens
                    for prev_token in range(max(0, new_token - 512), new_token):
                        key, size, access_type = self.generate_attention_kv(
                            prev_token, layer, context_id
                        )

                        access = CacheAccess(
                            timestamp=self.current_time,
                            access_type=access_type,
                            key=key,
                            size=size,
                            layer=layer,
                            token_id=prev_token,
                            context_id=context_id
                        )
                        accesses.append(access)
                        self.current_time += 0.001

                    # Re-attention to older tokens (sample)
                    if new_token > 512:
                        num_reattention = min(64, new_token - 512)
                        reattention_tokens = random.sample(
                            range(0, new_token - 512),
                            num_reattention
                        )

                        for prev_token in reattention_tokens:
                            key, size, access_type = self.generate_attention_kv(
                                prev_token, layer, context_id
                            )

                            access = CacheAccess(
                                timestamp=self.current_time,
                                access_type=access_type,
                                key=key,
                                size=size,
                                layer=layer,
                                token_id=prev_token,
                                context_id=context_id
                            )
                            accesses.append(access)
                            self.current_time += 0.001

                    # Store new token
                    key, size, access_type = self.generate_attention_kv(
                        new_token, layer, context_id
                    )

                    access = CacheAccess(
                        timestamp=self.current_time,
                        access_type=access_type,
                        key=key,
                        size=size,
                        layer=layer,
                        token_id=new_token,
                        context_id=context_id
                    )
                    accesses.append(access)
                    self.current_time += 0.001

        return accesses

    def simulate_branching(
        self,
        base_context: str,
        num_branches: int = 5,
        tokens_per_branch: int = 20
    ) -> List[CacheAccess]:
        """
        Simulate tree-based branching (e.g., for search/generation)

        Branching creates interesting cache patterns where multiple
        branches share a common prefix.

        Args:
            base_context: Base context before branching
            num_branches: Number of branches to explore
            tokens_per_branch: Tokens generated per branch

        Returns:
            List of cache accesses
        """
        accesses = []

        # Generate base context (shared by all branches)
        base_tokens = 50
        accesses.extend(
            self.simulate_sequential_decode(base_context, base_tokens)
        )

        # Generate branches
        for branch_id in range(num_branches):
            branch_context = f"{base_context}_branch{branch_id}"

            # Each branch reuses base context
            for layer in range(self.config.num_layers):
                for prev_token in range(0, base_tokens):
                    key, size, access_type = self.generate_attention_kv(
                        prev_token, layer, base_context
                    )

                    access = CacheAccess(
                        timestamp=self.current_time,
                        access_type=access_type,
                        key=key,
                        size=size,
                        layer=layer,
                        token_id=prev_token,
                        context_id=base_context
                    )
                    accesses.append(access)
                    self.current_time += 0.001

            # Generate branch-specific tokens
            accesses.extend(
                self.simulate_sequential_decode(
                    branch_context, tokens_per_branch, base_tokens
                )
            )

        return accesses

    def generate_trace(
        self,
        pattern: AccessPattern,
        duration: float = 100.0
    ) -> List[CacheAccess]:
        """
        Generate a complete access trace

        Args:
            pattern: Access pattern to simulate
            duration: Duration in seconds

        Returns:
            List of cache accesses
        """
        self.current_time = 0.0

        if pattern == AccessPattern.SEQUENTIAL_DECODE:
            return self.simulate_sequential_decode(
                context_id="seq",
                num_tokens=1000
            )

        elif pattern == AccessPattern.CONTEXT_REUSE:
            return self.simulate_context_reuse(
                base_context="reuse",
                num_turns=10,
                tokens_per_turn=100
            )

        elif pattern == AccessPattern.MULTI_TURN:
            return self.simulate_context_reuse(
                base_context="multi_turn",
                num_turns=20,
                tokens_per_turn=50
            )

        elif pattern == AccessPattern.LONG_CONTEXT:
            return self.simulate_long_context(
                context_id="long",
                num_tokens=5000
            )

        elif pattern == AccessPattern.BRANCHING:
            return self.simulate_branching(
                base_context="branch",
                num_branches=10,
                tokens_per_branch=30
            )

        else:
            # Mixed pattern
            all_accesses = []
            all_accesses.extend(self.simulate_sequential_decode("mixed_seq", 200))
            all_accesses.extend(self.simulate_context_reuse("mixed_reuse", 5, 100))
            all_accesses.extend(self.simulate_long_context("mixed_long", 1000))
            return all_accesses

    def analyze_access_pattern(
        self,
        accesses: List[CacheAccess]
    ) -> Dict[str, Any]:
        """
        Analyze access pattern for statistics

        Args:
            accesses: List of cache accesses

        Returns:
            Statistics dictionary
        """
        total_accesses = len(accesses)

        # Count by type
        by_type = defaultdict(int)
        for access in accesses:
            by_type[access.access_type] += 1

        # Count by layer
        by_layer = defaultdict(int)
        for access in accesses:
            by_layer[access.layer] += 1

        # Reuse distance analysis
        key_last_access = {}
        reuse_distances = []

        for access in accesses:
            if access.key in key_last_access:
                distance = len([a for a in accesses
                              if key_last_access[access.key] < a.timestamp <= access.timestamp])
                reuse_distances.append(distance)
            key_last_access[access.key] = access.timestamp

        # Access intervals
        timestamps = [a.timestamp for a in accesses]
        intervals = np.diff(timestamps).tolist()

        # Working set size over time
        working_sets = []
        seen_keys = set()

        for access in accesses:
            seen_keys.add(access.key)
            working_sets.append(len(seen_keys))

        return {
            'total_accesses': total_accesses,
            'unique_keys': len(key_last_access),
            'by_type': {k.value: v for k, v in by_type.items()},
            'by_layer': dict(by_layer),
            'avg_reuse_distance': np.mean(reuse_distances) if reuse_distances else 0,
            'median_reuse_distance': np.median(reuse_distances) if reuse_distances else 0,
            'avg_access_interval': np.mean(intervals) if intervals else 0,
            'peak_working_set': max(working_sets) if working_sets else 0,
            'final_working_set': working_sets[-1] if working_sets else 0
        }

def main():
    """Generate example traces and analyze patterns"""
    print("="*70)
    print("KV-CACHE SIMULATOR")
    print("="*70)

    config = SimulatorConfig(
        num_layers=32,
        hidden_dim=4096,
        num_heads=32
    )

    simulator = KVCacheSimulator(config)

    patterns = [
        AccessPattern.SEQUENTIAL_DECODE,
        AccessPattern.CONTEXT_REUSE,
        AccessPattern.MULTI_TURN,
        AccessPattern.LONG_CONTEXT,
        AccessPattern.BRANCHING
    ]

    results = {}

    for pattern in patterns:
        print(f"\n{'='*70}")
        print(f"Pattern: {pattern.value.upper()}")
        print(f"{'='*70}")

        # Generate trace
        trace = simulator.generate_trace(pattern)

        # Analyze
        stats = simulator.analyze_access_pattern(trace)

        results[pattern.value] = stats

        print(f"Total Accesses: {stats['total_accesses']}")
        print(f"Unique Keys: {stats['unique_keys']}")
        print(f"Peak Working Set: {stats['peak_working_set']}")
        print(f"Avg Reuse Distance: {stats['avg_reuse_distance']:.1f}")
        print(f"\nAccess Types:")
        for access_type, count in stats['by_type'].items():
            print(f"  {access_type}: {count}")

    # Save results
    os.makedirs('simulations/optimization/memory/results', exist_ok=True)

    with open('simulations/optimization/memory/results/trace_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*70)
    print("Trace analysis saved to: simulations/optimization/memory/results/trace_analysis.json")
    print("="*70)

    return results

if __name__ == '__main__':
    import os
    main()
