"""
POLLN Dialogue Simulation System

Simulates dialogue management and context tracking to optimize POLLN agents
for conversational AI tasks. Tests turn-taking, context management, and
persona consistency across various dialogue scenarios.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
from collections import defaultdict
import random


class DialogueType(Enum):
    """Types of dialogue scenarios to simulate"""
    SHORT_CONTEXT = "short_context"  # Quick exchanges, 5-10 turns
    LONG_CONTEXT = "long_context"    # Extended conversations, 50-100 turns
    MULTI_PARTY = "multi_party"      # 3+ participants
    TASK_ORIENTED = "task_oriented"  # Goal-driven dialogue
    SOCIAL = "social"                # Casual conversation


@dataclass
class DialogueTurn:
    """Represents a single turn in dialogue"""
    speaker: str
    content: str
    turn_number: int
    context_snapshot: Dict[str, any] = field(default_factory=dict)
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class DialogueMetrics:
    """Metrics for dialogue performance"""
    coherence_score: float  # How well responses follow from context
    relevance_score: float  # How relevant responses are to current topic
    engagement_score: float  # How engaging the dialogue is
    consistency_score: float  # Persona and factual consistency
    context_retention: float  # How well context is maintained
    total_turns: int
    topic_transitions: int


class DialogueSimulator:
    """
    Simulates dialogue scenarios to optimize POLLN agent composition
    for conversational AI tasks.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.dialogue_history: List[DialogueTurn] = []
        self.context_state = {}
        self.entity_tracker = defaultdict(list)
        self.topic_history = []

    def _default_config(self) -> Dict:
        """Default simulation configuration"""
        return {
            'max_turns': 100,
            'context_window': 128000,  # tokens
            'summarization_threshold': 10,  # turns
            'entity_tracking': True,
            'persona_consistency': 'high',
            'temperature_range': (0.7, 1.0)
        }

    def simulate_dialogue(
        self,
        dialogue_type: DialogueType,
        num_agents: int = 2,
        seed: Optional[int] = None
    ) -> Tuple[List[DialogueTurn], DialogueMetrics]:
        """
        Simulate a complete dialogue session.

        Args:
            dialogue_type: Type of dialogue to simulate
            num_agents: Number of participant agents
            seed: Random seed for reproducibility

        Returns:
            Tuple of (dialogue turns, metrics)
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.dialogue_history = []
        self.context_state = {}
        self.entity_tracker = defaultdict(list)
        self.topic_history = []

        # Initialize agents with personas
        agents = self._initialize_agents(num_agents)

        # Simulate dialogue based on type
        if dialogue_type == DialogueType.SHORT_CONTEXT:
            max_turns = random.randint(5, 10)
        elif dialogue_type == DialogueType.LONG_CONTEXT:
            max_turns = random.randint(50, 100)
        elif dialogue_type == DialogueType.MULTI_PARTY:
            max_turns = random.randint(20, 40)
            num_agents = max(3, num_agents)
            # Re-initialize agents with new count
            agents = self._initialize_agents(num_agents)
        elif dialogue_type == DialogueType.TASK_ORIENTED:
            max_turns = random.randint(15, 30)
        else:  # SOCIAL
            max_turns = random.randint(20, 50)

        # Simulate turns
        for turn_num in range(max_turns):
            speaker = agents[turn_num % num_agents]
            turn = self._generate_turn(speaker, turn_num, agents)
            self.dialogue_history.append(turn)
            self._update_context(turn)

        # Calculate metrics
        metrics = self._calculate_dialogue_metrics()

        return self.dialogue_history, metrics

    def _initialize_agents(self, num_agents: int) -> List[Dict]:
        """Initialize agents with personas and characteristics"""
        personas = [
            "helpful_assistant",
            "creative_expert",
            "analytical_thinker",
            "casual_conversationalist",
            "domain_expert"
        ]

        agents = []
        for i in range(num_agents):
            temp_range = self.config.get('temperature_range', (0.7, 1.0))
            agent = {
                'id': f'agent_{i}',
                'name': f'Agent_{i}',
                'persona': random.choice(personas),
                'temperature': random.uniform(*temp_range),
                'expertise': random.choice([
                    'general', 'technical', 'creative', 'analytical', 'social'
                ])
            }
            agents.append(agent)

        return agents

    def _generate_turn(
        self,
        speaker: Dict,
        turn_num: int,
        all_agents: List[Dict]
    ) -> DialogueTurn:
        """Generate a single dialogue turn"""
        # Get recent context
        recent_turns = self.dialogue_history[-3:] if self.dialogue_history else []

        # Generate content based on context and persona
        content = self._generate_response(speaker, recent_turns, turn_num)

        # Create turn with context snapshot
        turn = DialogueTurn(
            speaker=speaker['name'],
            content=content,
            turn_number=turn_num,
            context_snapshot={
                'topic': self.topic_history[-1] if self.topic_history else 'initial',
                'entities_mentioned': list(self.entity_tracker.keys())[-5:],
                'recent_speaker': recent_turns[-1].speaker if recent_turns else None
            },
            metadata={
                'persona': speaker['persona'],
                'temperature': speaker['temperature'],
                'expertise': speaker['expertise']
            }
        )

        return turn

    def _generate_response(
        self,
        speaker: Dict,
        recent_turns: List[DialogueTurn],
        turn_num: int
    ) -> str:
        """Generate response content based on context and persona"""
        # Simulated response templates based on persona
        responses = {
            'helpful_assistant': [
                "I'd be happy to help with that.",
                "Let me explain this step by step.",
                "Based on what you've told me, I suggest...",
                "That's a great question. Here's what I think..."
            ],
            'creative_expert': [
                "From a creative perspective, we could...",
                "Let's think outside the box here.",
                "Imagine if we tried a different approach...",
                "Here's an innovative idea..."
            ],
            'analytical_thinker': [
                "Let's analyze this systematically.",
                "Breaking this down, we have several factors.",
                "The data suggests that...",
                "From a logical standpoint..."
            ],
            'casual_conversationalist': [
                "That's interesting! Tell me more.",
                "I see what you mean.",
                "Yeah, I've had similar experiences.",
                "That reminds me of something..."
            ],
            'domain_expert': [
                "In my experience with this domain...",
                "The technical details are important here.",
                "Based on best practices...",
                "Let me share some specialized knowledge..."
            ]
        }

        # Select response based on persona
        persona_responses = responses.get(speaker['persona'], responses['helpful_assistant'])

        # Add context awareness
        if recent_turns:
            previous_speaker = recent_turns[-1].speaker
            if previous_speaker != speaker['name']:
                # Response to another speaker
                base_response = random.choice(persona_responses)
                return f"{base_response} [responding to {previous_speaker}]"
            else:
                # Continuing own thought
                return f"Additionally, {random.choice(['I should mention', 'it\'s worth noting', 'let me add'])}..."

        return random.choice(persona_responses)

    def _update_context(self, turn: DialogueTurn):
        """Update context state after each turn"""
        # Track topic (simplified)
        if turn.turn_number % 5 == 0:
            new_topic = f"topic_{len(self.topic_history) + 1}"
            self.topic_history.append(new_topic)

        # Track entities (simplified - extract nouns)
        entities = self._extract_entities(turn.content)
        for entity in entities:
            self.entity_tracker[entity].append(turn.turn_number)

        # Update context state
        self.context_state['last_speaker'] = turn.speaker
        self.context_state['turn_count'] = turn.turn_number + 1

    def _extract_entities(self, text: str) -> List[str]:
        """Simple entity extraction (placeholder)"""
        # In real simulation, use NLP
        words = text.lower().split()
        # Filter out common words
        stop_words = {'i', 'you', 'the', 'a', 'an', 'is', 'are', 'to', 'for', 'with', 'that', 'this'}
        entities = [w for w in words if len(w) > 3 and w not in stop_words]
        return entities[:3]  # Top 3 entities

    def _calculate_dialogue_metrics(self) -> DialogueMetrics:
        """Calculate comprehensive dialogue metrics"""
        if not self.dialogue_history:
            return DialogueMetrics(0, 0, 0, 0, 0, 0, 0)

        # Coherence: How well responses follow from context
        coherence = self._calculate_coherence()

        # Relevance: How relevant responses are to current topic
        relevance = self._calculate_relevance()

        # Engagement: Based on turn length and variety
        engagement = self._calculate_engagement()

        # Consistency: Persona and factual consistency
        consistency = self._calculate_consistency()

        # Context retention: How well context is maintained
        context_retention = self._calculate_context_retention()

        return DialogueMetrics(
            coherence_score=coherence,
            relevance_score=relevance,
            engagement_score=engagement,
            consistency_score=consistency,
            context_retention=context_retention,
            total_turns=len(self.dialogue_history),
            topic_transitions=len(self.topic_history)
        )

    def _calculate_coherence(self) -> float:
        """Calculate how well responses follow from context"""
        if len(self.dialogue_history) < 2:
            return 1.0

        coherence_scores = []
        for i in range(1, len(self.dialogue_history)):
            current = self.dialogue_history[i]
            previous = self.dialogue_history[i-1]

            # Check if response acknowledges previous
            if 'responding to' in current.content:
                coherence_scores.append(1.0)
            elif current.content.startswith(('Additionally', 'Also', 'Furthermore')):
                coherence_scores.append(0.9)
            else:
                coherence_scores.append(0.7)

        return np.mean(coherence_scores)

    def _calculate_relevance(self) -> float:
        """Calculate relevance to current topic"""
        if not self.topic_history:
            return 1.0

        # Simplified: assume high relevance if entities are tracked
        entity_diversity = len(self.entity_tracker)
        max_diversity = len(self.dialogue_history) * 2
        return min(1.0, entity_diversity / max_diversity)

    def _calculate_engagement(self) -> float:
        """Calculate engagement score"""
        if not self.dialogue_history:
            return 0.0

        # Based on turn variety and length
        speakers = set(turn.speaker for turn in self.dialogue_history)
        speaker_variety = len(speakers) / max(1, len(self.dialogue_history))

        avg_turn_length = np.mean([len(turn.content) for turn in self.dialogue_history])
        length_score = min(1.0, avg_turn_length / 100)

        return (speaker_variety + length_score) / 2

    def _calculate_consistency(self) -> float:
        """Calculate persona and factual consistency"""
        if not self.dialogue_history:
            return 1.0

        # Check if agents maintain their personas
        persona_consistency = 0.0
        for turn in self.dialogue_history:
            expected_persona = turn.metadata.get('persona', '')
            if expected_persona:
                # Simplified check based on content patterns
                if 'helpful' in expected_persona and 'help' in turn.content.lower():
                    persona_consistency += 1
                elif 'creative' in expected_persona and 'creative' in turn.content.lower():
                    persona_consistency += 1
                elif 'analytical' in expected_persona and 'analyze' in turn.content.lower():
                    persona_consistency += 1

        return min(1.0, persona_consistency / len(self.dialogue_history))

    def _calculate_context_retention(self) -> float:
        """Calculate how well context is retained"""
        if not self.dialogue_history:
            return 1.0

        # Check entity tracking
        tracked_entities = len(self.entity_tracker)
        total_turns = len(self.dialogue_history)

        # Good retention if entities are referenced multiple times
        avg_mentions = np.mean([len(mentions) for mentions in self.entity_tracker.values()])
        retention_score = min(1.0, avg_mentions / 3)

        return retention_score

    def optimize_agent_composition(
        self,
        num_trials: int = 50
    ) -> Dict[str, any]:
        """
        Optimize agent composition for dialogue tasks.

        Args:
            num_trials: Number of simulation trials

        Returns:
            Optimal configuration dictionary
        """
        print(f"Running {num_trials} optimization trials...")

        results = []

        for trial in range(num_trials):
            # Random configuration
            config = {
                'num_agents': random.randint(2, 5),
                'temperature': random.uniform(0.5, 1.0),
                'summarization_threshold': random.randint(5, 15),
                'entity_tracking': random.choice([True, False])
            }

            # Run simulation
            sim = DialogueSimulator(config)
            _, metrics = sim.simulate_dialogue(
                dialogue_type=DialogueType.LONG_CONTEXT,
                num_agents=config['num_agents']
            )

            # Calculate overall score
            score = (
                metrics.coherence_score * 0.25 +
                metrics.relevance_score * 0.20 +
                metrics.engagement_score * 0.20 +
                metrics.consistency_score * 0.20 +
                metrics.context_retention * 0.15
            )

            results.append({
                'config': config,
                'metrics': metrics,
                'score': score
            })

        # Find best configuration
        best_result = max(results, key=lambda x: x['score'])

        return {
            'optimal_config': best_result['config'],
            'expected_metrics': {
                'coherence': best_result['metrics'].coherence_score,
                'relevance': best_result['metrics'].relevance_score,
                'engagement': best_result['metrics'].engagement_score,
                'consistency': best_result['metrics'].consistency_score,
                'context_retention': best_result['metrics'].context_retention
            },
            'optimization_score': best_result['score'],
            'all_results': results
        }


class DialogueContextCompressor:
    """
    Simulates context compression strategies for long dialogues.
    Tests different summarization and KV-cache strategies.
    """

    def __init__(self):
        self.compression_strategies = [
            'sliding_window',
            'summarization',
            'hierarchical',
            'kv_cache'
        ]

    def test_compression(
        self,
        dialogue: List[DialogueTurn],
        strategy: str
    ) -> Dict[str, any]:
        """Test a compression strategy on dialogue history"""
        original_size = len(str(dialogue))

        if strategy == 'sliding_window':
            compressed = self._sliding_window(dialogue, window_size=10)
        elif strategy == 'summarization':
            compressed = self._summarization(dialogue, ratio=0.3)
        elif strategy == 'hierarchical':
            compressed = self._hierarchical(dialogue)
        elif strategy == 'kv_cache':
            compressed = self._kv_cache(dialogue)
        else:
            compressed = dialogue

        compressed_size = len(str(compressed))
        compression_ratio = compressed_size / original_size

        return {
            'strategy': strategy,
            'original_turns': len(dialogue),
            'compressed_turns': len(compressed),
            'compression_ratio': compression_ratio,
            'information_retention': self._calculate_retention(dialogue, compressed)
        }

    def _sliding_window(
        self,
        dialogue: List[DialogueTurn],
        window_size: int
    ) -> List[DialogueTurn]:
        """Keep only recent N turns"""
        return dialogue[-window_size:]

    def _summarization(
        self,
        dialogue: List[DialogueTurn],
        ratio: float
    ) -> List[DialogueTurn]:
        """Summarize older turns, keep recent turns verbatim"""
        split_point = int(len(dialogue) * ratio)

        # Keep recent turns verbatim
        recent = dialogue[split_point:]

        # Summarize older turns (placeholder - just keep key turns)
        key_turns = [
            dialogue[i] for i in range(0, split_point, max(1, split_point // 5))
        ]

        return key_turns + recent

    def _hierarchical(
        self,
        dialogue: List[DialogueTurn]
    ) -> List[DialogueTurn]:
        """Hierarchical compression with topic boundaries"""
        # Group by topic (every 10 turns in this simulation)
        topic_groups = []
        for i in range(0, len(dialogue), 10):
            topic_groups.append(dialogue[i:i+10])

        # Keep first and last turn of each topic, plus all recent turns
        compressed = []
        for group in topic_groups[:-1]:
            compressed.append(group[0])
            if len(group) > 1:
                compressed.append(group[-1])

        compressed.extend(topic_groups[-1])

        return compressed

    def _kv_cache(
        self,
        dialogue: List[DialogueTurn]
    ) -> List[DialogueTurn]:
        """Simulate KV-cache based compression"""
        # In real implementation, this would use attention patterns
        # Here we simulate by keeping turns with high entity overlap
        compressed = []

        for i, turn in enumerate(dialogue):
            # Keep if: first turn, last turn, or high entity novelty
            if i == 0 or i == len(dialogue) - 1:
                compressed.append(turn)
            elif i % 3 == 0:  # Keep every 3rd turn
                compressed.append(turn)

        return compressed

    def _calculate_retention(
        self,
        original: List[DialogueTurn],
        compressed: List[DialogueTurn]
    ) -> float:
        """Calculate information retention score"""
        if not original:
            return 1.0

        # Simple metric: percentage of unique entities retained
        original_entities = set()
        for turn in original:
            original_entities.update(self._extract_entities_from_turn(turn))

        compressed_entities = set()
        for turn in compressed:
            compressed_entities.update(self._extract_entities_from_turn(turn))

        if not original_entities:
            return 1.0

        return len(compressed_entities) / len(original_entities)

    def _extract_entities_from_turn(self, turn: DialogueTurn) -> set:
        """Extract entities from a turn"""
        words = turn.content.lower().split()
        return set(w for w in words if len(w) > 3)


def run_dialogue_simulation_suite():
    """Run complete dialogue simulation suite"""
    print("=" * 60)
    print("POLLN Dialogue Simulation Suite")
    print("=" * 60)

    # Test each dialogue type
    results = {}
    for dialogue_type in DialogueType:
        print(f"\nSimulating {dialogue_type.value}...")

        sim = DialogueSimulator()
        turns, metrics = sim.simulate_dialogue(
            dialogue_type=dialogue_type,
            num_agents=2,
            seed=42
        )

        results[dialogue_type.value] = {
            'turns': len(turns),
            'coherence': metrics.coherence_score,
            'relevance': metrics.relevance_score,
            'engagement': metrics.engagement_score,
            'consistency': metrics.consistency_score,
            'context_retention': metrics.context_retention
        }

        print(f"  Turns: {metrics.total_turns}")
        print(f"  Coherence: {metrics.coherence_score:.3f}")
        print(f"  Relevance: {metrics.relevance_score:.3f}")

    # Test compression strategies
    print("\n" + "=" * 60)
    print("Testing Context Compression Strategies")
    print("=" * 60)

    sim = DialogueSimulator()
    long_dialogue, _ = sim.simulate_dialogue(
        DialogueType.LONG_CONTEXT,
        num_agents=2,
        seed=42
    )

    compressor = DialogueContextCompressor()
    compression_results = {}

    for strategy in compressor.compression_strategies:
        result = compressor.test_compression(long_dialogue, strategy)
        compression_results[strategy] = result
        print(f"\n{strategy}:")
        print(f"  Compression ratio: {result['compression_ratio']:.3f}")
        print(f"  Information retention: {result['information_retention']:.3f}")

    # Optimize agent composition
    print("\n" + "=" * 60)
    print("Optimizing Agent Composition")
    print("=" * 60)

    optimal = sim.optimize_agent_composition(num_trials=20)

    print(f"\nOptimal Configuration:")
    print(f"  Num agents: {optimal['optimal_config']['num_agents']}")
    print(f"  Temperature: {optimal['optimal_config']['temperature']:.3f}")
    print(f"  Summarization threshold: {optimal['optimal_config']['summarization_threshold']}")
    print(f"  Optimization score: {optimal['optimization_score']:.3f}")

    # Save results
    output = {
        'dialogue_results': results,
        'compression_results': compression_results,
        'optimal_config': optimal['optimal_config'],
        'expected_metrics': optimal['expected_metrics']
    }

    with open('simulations/domains/reasoning/dialogue_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("Results saved to dialogue_results.json")
    print("=" * 60)

    return output


if __name__ == '__main__':
    run_dialogue_simulation_suite()
