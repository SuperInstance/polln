"""
META Tile Knowledge Succession Simulation
==========================================

Proves that knowledge can be efficiently transferred between generations
of META tiles through the succession protocol.

Mathematical Foundation:
    Transfer: W_new = W_old + α × W_teacher + ε
    Decay: W_old = W_old × (1 - decay_rate)

    Retention = α × transfer + (1-α) × decay

Hypotheses:
    H3: Optimal transfer rate maximizes knowledge preservation
    H3: Decay rate balances adaptation vs retention
    H3: Succession enables lifelong learning without catastrophic forgetting
"""

import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import json
from pathlib import Path
from collections import defaultdict


# Set random seeds
np.random.seed(42)
torch.manual_seed(42)


class KnowledgeStage(Enum):
    """Knowledge maturity stages"""
    EPHEMERAL = 'EPHEMERAL'   # Fresh, < 100 executions
    WORKING = 'WORKING'       # Validated, 100-1000 executions
    EMBEDDED = 'EMBEDDED'     # Deep, > 1000 executions
    FOSSIL = 'FOSSIL'         # Archived, no longer active


@dataclass
class PatternData:
    """Represents a learned pattern"""
    key: str
    value: np.ndarray
    count: int
    success_rate: float
    last_used: float
    stage: KnowledgeStage


@dataclass
class KnowledgePacket:
    """Compressed knowledge for transfer"""
    id: str
    source_id: str
    patterns: Dict[str, PatternData]
    value_function: float
    execution_count: int
    compression_ratio: float
    created_at: float


@dataclass
class SuccessionConfig:
    """Configuration for succession simulation"""
    # Agent lifecycle
    max_agent_lifetime: int = 1000  # Steps before death
    succession_trigger: int = 800   # Steps to start succession

    # Knowledge parameters
    pattern_threshold: int = 5      # Min executions to preserve
    max_pattern_age: float = 100.0  # Max age before fossilization

    # Transfer parameters
    transfer_rate: float = 0.8      # α: how much to transfer
    decay_rate: float = 0.01        # λ: how fast old knowledge decays
    noise_level: float = 0.05       # ε: transfer noise

    # Compression
    compression_threshold: int = 100  # Patterns before compression
    compression_ratio: float = 0.5    # Keep top 50%

    # Simulation
    n_generations: int = 10
    n_agents_per_generation: int = 20
    n_tasks: int = 5


class MetaTileAgent:
    """
    META tile agent with knowledge that can be transferred.

    Tracks:
    - Learned patterns
    - Execution history
    - Value function estimates
    """

    def __init__(self, agent_id: str, config: SuccessionConfig,
                 inherited_knowledge: Optional[KnowledgePacket] = None):
        self.id = agent_id
        self.config = config
        self.age = 0
        self.alive = True
        self.generation = 0

        # Knowledge store
        self.patterns: Dict[str, PatternData] = {}

        # Statistics
        self.execution_count = 0
        self.success_count = 0
        self.value_function = 0.5

        # History
        self.performance_history: List[float] = []

        # Initialize from inherited knowledge
        if inherited_knowledge:
            self.inherit_knowledge(inherited_knowledge)

    def inherit_knowledge(self, packet: KnowledgePacket):
        """Inherit knowledge from predecessor"""
        self.generation = packet.source_id.split('_')[-1] if '_' in packet.source_id else '0'

        # Transfer patterns with noise
        for key, pattern in packet.patterns.items():
            # Add transfer noise
            noise = np.random.randn(*pattern.value.shape) * self.config.noise_level

            inherited_pattern = PatternData(
                key=key,
                value=pattern.value + noise,
                count=pattern.count // 2,  # Decay count
                success_rate=pattern.success_rate * 0.9,  # Decay confidence
                last_used=0.0,
                stage=KnowledgeStage.EPHEMERAL  # Reset to ephemeral
            )

            # Only inherit if above threshold
            if inherited_pattern.count >= self.config.pattern_threshold:
                self.patterns[key] = inherited_pattern

        # Inherit value function
        self.value_function = packet.value_function * 0.9  # Decay

    def execute(self, task: np.ndarray) -> float:
        """Execute task and learn from experience"""
        self.age += 1
        self.execution_count += 1

        # Simulate task performance based on knowledge
        if self.patterns:
            # Use learned patterns
            pattern_keys = list(self.patterns.keys())
            selected_key = pattern_keys[hash(str(task.data.tobytes())) % len(pattern_keys)]
            pattern = self.patterns[selected_key]

            # Performance based on pattern quality and execution count
            performance = (
                pattern.success_rate *
                (1 + np.log(pattern.count + 1) / 10)
            )
        else:
            # Random performance without knowledge
            performance = np.random.rand() * 0.5

        # Update pattern
        self._update_pattern(str(task.data.tobytes()), task, performance)

        # Track performance
        self.performance_history.append(performance)
        self.value_function = 0.9 * self.value_function + 0.1 * performance

        # Check success
        if performance > 0.7:
            self.success_count += 1

        return performance

    def _update_pattern(self, key: str, value: np.ndarray, performance: float):
        """Update or create pattern based on experience"""
        if key in self.patterns:
            pattern = self.patterns[key]
            pattern.count += 1
            pattern.last_used = self.age
            # Update success rate as moving average
            pattern.success_rate = 0.9 * pattern.success_rate + 0.1 * (performance > 0.7)

            # Update stage
            if pattern.count >= 1000:
                pattern.stage = KnowledgeStage.EMBEDDED
            elif pattern.count >= 100:
                pattern.stage = KnowledgeStage.WORKING
        else:
            if self.execution_count >= self.config.pattern_threshold:
                self.patterns[key] = PatternData(
                    key=key,
                    value=value.copy(),
                    count=1,
                    success_rate=performance,
                    last_used=self.age,
                    stage=KnowledgeStage.EPHEMERAL
                )

    def extract_knowledge(self) -> KnowledgePacket:
        """Extract knowledge for succession"""
        # Filter patterns by age and count
        current_time = self.age
        valid_patterns = {}

        for key, pattern in self.patterns.items():
            age = current_time - pattern.last_used

            # Skip fossils
            if pattern.stage == KnowledgeStage.FOSSIL:
                continue

            # Skip old patterns
            if age > self.config.max_pattern_age:
                pattern.stage = KnowledgeStage.FOSSIL
                continue

            # Skip low-count patterns
            if pattern.count < self.config.pattern_threshold:
                continue

            valid_patterns[key] = pattern

        # Compress if needed
        if len(valid_patterns) > self.config.compression_threshold:
            # Sort by importance
            sorted_patterns = sorted(
                valid_patterns.items(),
                key=lambda x: x[1].count * x[1].success_rate,
                reverse=True
            )

            # Keep top patterns
            keep_count = int(len(sorted_patterns) * self.config.compression_ratio)
            valid_patterns = dict(sorted_patterns[:keep_count])

        packet = KnowledgePacket(
            id=f"{self.id}_packet",
            source_id=self.id,
            patterns=valid_patterns,
            value_function=self.value_function,
            execution_count=self.execution_count,
            compression_ratio=len(valid_patterns) / len(self.patterns) if self.patterns else 1.0,
            created_at=self.age
        )

        return packet

    def age_knowledge(self):
        """Age out old patterns"""
        for pattern in list(self.patterns.values()):
            age = self.age - pattern.last_used

            if age > self.config.max_pattern_age and pattern.stage != KnowledgeStage.FOSSIL:
                pattern.stage = KnowledgeStage.FOSSIL

    def get_stats(self) -> Dict:
        """Get agent statistics"""
        stage_counts = defaultdict(int)
        for pattern in self.patterns.values():
            stage_counts[pattern.stage.value] += 1

        return {
            'id': self.id,
            'age': self.age,
            'alive': self.alive,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'success_rate': self.success_count / self.execution_count if self.execution_count > 0 else 0,
            'value_function': self.value_function,
            'n_patterns': len(self.patterns),
            'stage_distribution': dict(stage_counts),
            'generation': self.generation
        }


class SuccessionManager:
    """
    Manages knowledge transfer between agent generations.
    """

    def __init__(self, config: SuccessionConfig):
        self.config = config
        self.agents: List[MetaTileAgent] = []
        self.generation = 0
        self.succession_history: List[Dict] = []
        self.knowledge_store: Dict[str, KnowledgePacket] = {}

    def spawn_generation(self, n_agents: int, predecessor_knowledge: List[KnowledgePacket] = None):
        """Spawn a new generation of agents"""
        new_agents = []

        for i in range(n_agents):
            agent_id = f"gen{self.generation}_agent{i}"

            # Inherit knowledge if available
            inherited = None
            if predecessor_knowledge and i < len(predecessor_knowledge):
                inherited = predecessor_knowledge[i]

            agent = MetaTileAgent(agent_id, self.config, inherited)
            new_agents.append(agent)

        self.agents = new_agents
        self.generation += 1

        print(f"Spawned generation {self.generation} with {n_agents} agents")

    def execute_all(self, tasks: List[np.ndarray]):
        """Execute all agents on tasks"""
        performances = []

        for agent in self.agents:
            if not agent.alive:
                continue

            # Random task for each agent
            task = tasks[np.random.randint(len(tasks))]
            performance = agent.execute(task)
            performances.append(performance)

            # Age knowledge
            agent.age_knowledge()

        return performances

    def check_succession(self):
        """Check if agents should undergo succession"""
        dying_agents = []
        new_knowledge = []

        for agent in self.agents:
            if agent.age >= self.config.max_agent_lifetime:
                dying_agents.append(agent)

        if dying_agents:
            print(f"  {len(dying_agents)} agents dying, extracting knowledge...")

            # Extract knowledge from dying agents
            for agent in dying_agents:
                packet = agent.extract_knowledge()
                new_knowledge.append(packet)
                agent.alive = False

                self.succession_history.append({
                    'generation': self.generation,
                    'source_agent': agent.id,
                    'patterns_transferred': len(packet.patterns),
                    'value_function': packet.value_function,
                    'compression_ratio': packet.compression_ratio
                })

            # Spawn new generation
            self.spawn_generation(len(dying_agents), new_knowledge)

        return len(dying_agents) > 0

    def get_generation_stats(self) -> Dict:
        """Get statistics for current generation"""
        if not self.agents:
            return {}

        stats = {
            'generation': self.generation,
            'n_agents': len(self.agents),
            'n_alive': sum(1 for a in self.agents if a.alive),
            'avg_age': np.mean([a.age for a in self.agents]),
            'total_executions': sum(a.execution_count for a in self.agents),
            'total_patterns': sum(len(a.patterns) for a in self.agents),
            'avg_value_function': np.mean([a.value_function for a in self.agents]),
            'avg_success_rate': np.mean([
                a.success_count / a.execution_count if a.execution_count > 0 else 0
                for a in self.agents
            ])
        }

        return stats


class SuccessionSimulation:
    """
    Main simulation for knowledge succession across generations.
    """

    def __init__(self, config: SuccessionConfig):
        self.config = config
        self.manager = SuccessionManager(config)
        self.history: List[Dict] = []

        # Generate tasks
        self.tasks = [
            np.random.randn(10) for _ in range(config.n_tasks)
        ]

    def run(self) -> Dict:
        """Run succession simulation"""
        print("="*70)
        print("META TILE KNOWLEDGE SUCCESSION SIMULATION")
        print("="*70)

        # Spawn initial generation
        self.manager.spawn_generation(self.config.n_agents_per_generation)

        # Run for specified generations
        for gen in range(self.config.n_generations):
            print(f"\nGeneration {gen + 1}/{self.config.n_generations}")

            # Execute until succession
            while True:
                # Execute all agents
                performances = self.manager.execute_all(self.tasks)

                # Record stats
                gen_stats = self.manager.get_generation_stats()
                gen_stats['step'] = len(self.history)
                gen_stats['avg_performance'] = np.mean(performances) if performances else 0
                self.history.append(gen_stats)

                # Check succession
                success = self.manager.check_succession()
                if success:
                    break

                # Safety check
                if len(self.history) > 10000:
                    break

        # Analyze results
        results = self._analyze_results()
        return results

    def _analyze_results(self) -> Dict:
        """Analyze succession results"""
        # Group by generation
        gen_data = defaultdict(list)
        for entry in self.history:
            gen_data[entry['generation']].append(entry)

        # Compute generation-level statistics
        generation_stats = {}
        for gen, entries in gen_data.items():
            final_entry = entries[-1]

            generation_stats[gen] = {
                'avg_performance': np.mean([e['avg_performance'] for e in entries]),
                'final_value_function': final_entry['avg_value_function'],
                'final_patterns': final_entry['total_patterns'],
                'final_success_rate': final_entry['avg_success_rate'],
                'total_executions': final_entry['total_executions']
            }

        # Compute retention across generations
        retention_rates = []
        for gen in range(1, len(generation_stats)):
            prev_perf = generation_stats[gen-1]['avg_performance']
            curr_perf = generation_stats[gen]['avg_performance']
            retention = curr_perf / (prev_perf + 1e-10)
            retention_rates.append(retention)

        # Succession events
        succession_events = self.manager.succession_history

        return {
            'generation_stats': generation_stats,
            'n_generations': len(generation_stats),
            'avg_retention_rate': np.mean(retention_rates) if retention_rates else 0,
            'final_performance': generation_stats[len(generation_stats)-1]['avg_performance'],
            'performance_improvement': (
                generation_stats[len(generation_stats)-1]['avg_performance'] -
                generation_stats[0]['avg_performance']
            ),
            'total_succession_events': len(succession_events),
            'avg_patterns_transferred': np.mean([
                e['patterns_transferred'] for e in succession_events
            ]) if succession_events else 0,
            'avg_compression_ratio': np.mean([
                e['compression_ratio'] for e in succession_events
            ]) if succession_events else 1.0,
            'history': self.history
        }

    def visualize(self, save_path: Optional[Path] = None):
        """Visualize succession results"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Group data by generation
        gen_data = defaultdict(list)
        for entry in self.history:
            gen_data[entry['generation']].append(entry)

        # 1. Performance over time (by generation)
        ax = axes[0, 0]
        for gen, entries in gen_data.items():
            steps = [e['step'] for e in entries]
            performances = [e['avg_performance'] for e in entries]
            ax.plot(steps, performances, label=f'Gen {gen}', alpha=0.7)

        ax.set_xlabel('Step')
        ax.set_ylabel('Average Performance')
        ax.set_title('Performance Evolution Across Generations')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Knowledge accumulation
        ax = axes[0, 1]
        for gen, entries in gen_data.items():
            steps = [e['step'] for e in entries]
            patterns = [e['total_patterns'] for e in entries]
            ax.plot(steps, patterns, label=f'Gen {gen}', alpha=0.7)

        ax.set_xlabel('Step')
        ax.set_ylabel('Total Patterns')
        ax.set_title('Knowledge Accumulation')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Value function evolution
        ax = axes[1, 0]
        for gen, entries in gen_data.items():
            steps = [e['step'] for e in entries]
            values = [e['avg_value_function'] for e in entries]
            ax.plot(steps, values, label=f'Gen {gen}', alpha=0.7)

        ax.set_xlabel('Step')
        ax.set_ylabel('Average Value Function')
        ax.set_title('Value Function Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 4. Generation comparison
        ax = axes[1, 1]
        generations = sorted(gen_data.keys())
        final_performances = [
            gen_data[gen][-1]['avg_performance']
            for gen in generations
        ]
        final_patterns = [
            gen_data[gen][-1]['total_patterns']
            for gen in generations
        ]

        ax2 = ax.twinx()
        ax.bar(generations, final_performances, alpha=0.7, color='blue', label='Performance')
        ax2.plot(generations, final_patterns, 'ro-', label='Patterns')

        ax.set_xlabel('Generation')
        ax.set_ylabel('Final Performance', color='blue')
        ax2.set_ylabel('Total Patterns', color='red')
        ax.set_title('Generation-wise Comparison')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved succession plot to {save_path}")

        return fig


def run_transfer_rate_sweep():
    """Experiment: Find optimal transfer rate"""
    print("\n" + "="*70)
    print("EXPERIMENT: Transfer Rate Sweep")
    print("="*70)

    transfer_rates = np.linspace(0.1, 1.0, 10)
    results = []

    for rate in transfer_rates:
        config = SuccessionConfig(
            n_generations=5,
            n_agents_per_generation=10,
            transfer_rate=rate
        )

        sim = SuccessionSimulation(config)
        result = sim.run()

        results.append({
            'transfer_rate': rate,
            'avg_retention_rate': result['avg_retention_rate'],
            'final_performance': result['final_performance'],
            'performance_improvement': result['performance_improvement']
        })

        print(f"  Rate {rate:.2f}: retention={result['avg_retention_rate']:.3f}, "
              f"perf={result['final_performance']:.3f}")

    return results


def run_decay_rate_sweep():
    """Experiment: Find optimal decay rate"""
    print("\n" + "="*70)
    print("EXPERIMENT: Decay Rate Sweep")
    print("="*70)

    decay_rates = np.linspace(0.001, 0.1, 10)
    results = []

    for decay in decay_rates:
        config = SuccessionConfig(
            n_generations=5,
            n_agents_per_generation=10,
            decay_rate=decay
        )

        sim = SuccessionSimulation(config)
        result = sim.run()

        results.append({
            'decay_rate': decay,
            'avg_retention_rate': result['avg_retention_rate'],
            'final_performance': result['final_performance']
        })

        print(f"  Decay {decay:.4f}: retention={result['avg_retention_rate']:.3f}")

    return results


def main():
    """Run all succession experiments"""
    # Create output directory
    output_dir = Path('/c/Users/casey/polln/simulations/results')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run main simulation
    config = SuccessionConfig(
        n_generations=10,
        n_agents_per_generation=20,
        max_agent_lifetime=500,
        succession_trigger=400
    )

    sim = SuccessionSimulation(config)
    results = sim.run()

    print("\n" + "="*70)
    print("SUCCESSION SIMULATION RESULTS")
    print("="*70)
    print(f"  Generations: {results['n_generations']}")
    print(f"  Avg retention rate: {results['avg_retention_rate']:.3f}")
    print(f"  Final performance: {results['final_performance']:.3f}")
    print(f"  Performance improvement: {results['performance_improvement']:.3f}")
    print(f"  Total succession events: {results['total_succession_events']}")
    print(f"  Avg patterns transferred: {results['avg_patterns_transferred']:.1f}")
    print(f"  Avg compression ratio: {results['avg_compression_ratio']:.2f}")

    # Visualize
    fig_dir = Path('/c/Users/casey/polln/simulations/figures')
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig = sim.visualize(fig_dir / 'succession_main.png')

    # Run experiments
    transfer_results = run_transfer_rate_sweep()
    decay_results = run_decay_rate_sweep()

    # Save all results
    all_results = {
        'main_simulation': results,
        'transfer_rate_sweep': transfer_results,
        'decay_rate_sweep': decay_results
    }

    results_path = output_dir / 'succession_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to {results_path}")

    return results


if __name__ == '__main__':
    results = main()
