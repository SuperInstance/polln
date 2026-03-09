# POLLN Reasoning Domain - Complete Guide

Comprehensive guide to optimizing POLLN agents for dialogue and multi-step reasoning.

## Table of Contents

1. [Overview](#overview)
2. [Simulation Architecture](#simulation-architecture)
3. [Dialogue Management](#dialogue-management)
4. [Chain-of-Thought Reasoning](#chain-of-thought-reasoning)
5. [Context Tracking](#context-tracking)
6. [Reasoning Depth](#reasoning-depth)
7. [Consistency Validation](#consistency-validation)
8. [Optimization Pipeline](#optimization-pipeline)
9. [Configuration Reference](#configuration-reference)
10. [Best Practices](#best-practices)

## Overview

The POLLN Reasoning Domain optimizes agent behavior for:

- **Conversational AI**: Natural dialogue with context awareness
- **Complex Reasoning**: Multi-step problem solving
- **Long-term Memory**: Efficient context management
- **Consistency**: Reliable, coherent responses

### Key Principles

1. **Probabilistic Selection**: Use Plinko layer for exploration
2. **Memory as Structure**: Store relationships, not facts
3. **Traceability**: All decisions are replayable
4. **Subsumption Architecture**: Safety → Reflex → Habitual → Deliberate

## Simulation Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   Master Orchestrator                   │
│                      (run_all.py)                       │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
│  Dialogue      │  │  Chain-of   │  │  Context       │
│  Simulation    │  │  Thought     │  │  Tracking      │
└────────────────┘  └─────────────┘  └────────────────┘
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
│  Reasoning    │  │ Consistency  │  │   Optimizer    │
│  Depth        │  │   Checker    │  │  (compile)     │
└────────────────┘  └─────────────┘  └────────────────┘
```

### Data Flow

1. **Simulations** generate metrics for different configurations
2. **Optimizer** compiles results into optimal configuration
3. **Config Generator** creates TypeScript configuration
4. **Validation** ensures correctness
5. **Report** summarizes findings

## Dialogue Management

### Dialogue Types

| Type | Turns | Focus | Use Case |
|------|-------|-------|----------|
| SHORT_CONTEXT | 5-10 | Quick exchanges | Chatbots, Q&A |
| LONG_CONTEXT | 50-100 | Extended conversation | Therapy, tutoring |
| MULTI_PARTY | 20-40 | Group dynamics | Meetings, collaboration |
| TASK_ORIENTED | 15-30 | Goal-driven | Customer service |
| SOCIAL | 20-50 | Casual conversation | Social agents |

### Key Metrics

- **Coherence**: How well responses follow from context (target: >0.85)
- **Relevance**: How relevant responses are to current topic (target: >0.80)
- **Engagement**: Turn variety and length (target: >0.70)
- **Consistency**: Persona and factual consistency (target: >0.85)
- **Context Retention**: How well context is maintained (target: >0.75)

### Optimization Results

Based on simulations:

- **Optimal Agent Count**: 2-3 agents for most scenarios
- **Summarization Threshold**: Every 10 turns
- **Temperature**: 0.7-0.8 for balanced creativity
- **Entity Tracking**: Enabled for all dialogue types

### Context Compression Strategies

#### 1. Sliding Window
```python
# Keep last N turns
compressed = turns[-window_size:]
```
- **Pros**: Simple, predictable
- **Cons**: Loses early context
- **Use Case**: Short-context dialogues

#### 2. Summarization
```python
# Summarize older turns
summary = generate_summary(turns[:-N])
compressed = [summary] + turns[-N:]
```
- **Pros**: Retains key information
- **Cons**: May lose nuances
- **Use Case**: Long-context dialogues

#### 3. Hierarchical
```python
# Group by topic, keep boundaries
compressed = keep_topic_boundaries(turns)
```
- **Pros**: Maintains topic structure
- **Cons**: Complex to implement
- **Use Case**: Multi-topic conversations

#### 4. Hybrid (Recommended)
```python
# Combine summarization + verbatim recent
summary = generate_summary(turns[:-10])
compressed = [summary] + turns[-10:]
```
- **Pros**: Balances compression and retention
- **Cons**: Moderate complexity
- **Use Case**: General-purpose dialogue

## Chain-of-Thought Reasoning

### GSM8K-Style Problems

Simulated on grade school math word problems:

```
Problem: "Janet has 16 apples. She gives 8 to her friend.
         How many apples does she have left?"

Reasoning Chain:
1. Identify initial quantity: 16
2. Identify quantity to subtract: 8
3. Calculate: 16 - 8 = 8

Answer: 8
```

### Self-Consistency

Generate multiple reasoning chains and select most common answer:

```python
# Generate N samples
chains = [generate_chain(problem) for _ in range(N)]

# Select by majority vote
answer_counts = Counter(c.final_answer for c in chains)
best_answer = answer_counts.most_common(1)[0][0]
```

**Parameters:**
- **Samples**: 5 (default)
- **Aggregation**: Majority vote
- **Confidence**: Weight by chain confidence

### Checkpoint Optimization

Strategies for placing checkpoints in reasoning chains:

| Strategy | Description | Best For |
|----------|-------------|----------|
| Fixed Interval | Every N steps | Uniform tasks |
| Entropy-Based | Low confidence steps | Uncertain reasoning |
| Dependency-Aware | At dependency boundaries | Multi-step problems |
| Adaptive | Multiple signals | General-purpose |

### Verification

Verify reasoning chains before accepting:

```python
def verify_chain(chain, problem):
    # Check answer correctness
    correct = chain.final_answer == problem['answer']

    # Check checkpoint quality
    checkpoints = len([s for s in chain.steps if s.checkpoint])
    quality = checkpoints >= len(chain.steps) * 0.3

    return correct and quality
```

**Threshold**: 0.7 confidence

### Performance

Based on GSM8K simulations:

- **Accuracy**: 0.80-0.85
- **Average Steps**: 5-7
- **Consensus Rate**: 0.70-0.75
- **Checkpoint Utilization**: 0.30-0.40

## Context Tracking

### Entity Tracking

Track entities throughout conversation:

```python
class EntityTracker:
    def extract_entities(self, text, turn_num):
        # Extract and track entities
        entities = ner.extract(text)

        for entity in entities:
            entity.last_mentioned = turn_num
            entity.mention_count += 1

        return entities
```

**Features:**
- Named entity recognition
- Mention counting
- Active window (10 turns)
- Relationship inference

### Memory Retrieval

Retrieve relevant memories using embeddings:

```python
def retrieve_memories(query, top_k=5):
    query_embedding = embed(query)

    similarities = [
        cosine_similarity(query_embedding, mem.embedding)
        for mem in memories
    ]

    return top_k(memories, similarities, k=top_k)
```

**Parameters:**
- **Top-K**: 5
- **Similarity**: Cosine
- **Time Decay**: Exponential (λ=100)
- **Importance Weight**: 1.0

### KV-Cache Optimization

Use attention patterns to optimize KV-cache:

```python
def calculate_attention_priorities(turns, entities):
    priorities = []

    for i, turn in enumerate(turns):
        recency = (i + 1) / len(turns)
        entity_density = count_entities(turn, entities) / 5
        length_score = len(turn) / 200

        priority = 0.5*recency + 0.3*entity_density + 0.2*length_score
        priorities.append(priority)

    return priorities
```

**Strategy**: Attention-based eviction
**Cache Budget**: 20 turns
**Max Size**: 1GB

## Reasoning Depth

### Depth Modes

| Mode | Steps | Breadth | Use Case |
|------|-------|---------|----------|
| Shallow | 3 | 10 | Simple tasks |
| Medium | 7 | 5 | Moderate complexity |
| Deep | 15 | 3 | Complex reasoning |
| Adaptive | Variable | Variable | Task-dependent |

### Exploration Strategies

#### 1. Tree-of-Thoughts
```python
# Branch and bound search
nodes = expand(root)
for depth in range(max_depth):
    children = [expand(n) for n in nodes]
    nodes = prune(children, beam_width)
```

**Best For**: Multi-step problems

#### 2. Iterative Refinement
```python
solution = initial_guess
for iteration in range(max_iterations):
    refined = refine(solution)
    if converged(refined):
        break
    solution = refined
```

**Best For**: Optimization problems

#### 3. Debate
```python
for round in num_rounds:
    for agent in agents:
        argument = generate_argument(agent, round)
    consensus = synthesize(arguments)
```

**Best For**: Multiple valid approaches

### Task Complexity Estimation

Estimate complexity to select appropriate depth:

```python
def estimate_complexity(problem):
    score = 0.0

    # Count entities
    entities = len(extract_entities(problem))
    score += min(0.3, entities * 0.05)

    # Question length
    score += min(0.2, len(problem) / 500)

    # Numeric values
    numbers = len(extract_numbers(problem))
    score += min(0.2, numbers * 0.05)

    # Complex keywords
    keywords = count_complex_keywords(problem)
    score += min(0.3, keywords * 0.06)

    return min(1.0, score)
```

**Thresholds:**
- <0.3: Shallow
- 0.3-0.7: Medium
- >0.7: Deep

## Consistency Validation

### Consistency Types

#### 1. Self-Consistency
Check for internal contradictions:

```python
def check_self_consistency(response):
    # Look for contradiction patterns
    contradictions = [
        (r'always', r'never'),
        (r'all', r'none'),
        (r'certainly', r'uncertain')
    ]

    violations = []
    for pattern1, pattern2 in contradictions:
        if contains(response, pattern1) and contains(response, pattern2):
            violations.add(f"Contradiction: {pattern1} vs {pattern2}")

    return violations
```

#### 2. Factual Consistency
Validate against knowledge base:

```python
def check_factual_consistency(response):
    misconceptions = [
        (r'earth is flat', 'Earth is not flat'),
        (r'water boils at \d+', 'Water boils at 100°C')
    ]

    violations = []
    for pattern, correction in misconceptions:
        if matches(response, pattern):
            violations.add(f"Factual error: {correction}")

    return violations
```

#### 3. Temporal Consistency
Check consistency over time:

```python
def check_temporal_consistency(response, history):
    # Compare with previous statements
    for turn in history[-5:]:
        if contradicts(response, turn.content):
            violations.add(f"Contradicts turn {turn.timestamp}")

    return violations
```

#### 4. Logical Consistency
Check logical coherence:

```python
def check_logical_consistency(response):
    # Check for non-sequiturs
    if has_conherence_marker(response) and no_follow_up(response):
        violations.add("Non-sequitur detected")

    # Check for circular reasoning
    if is_circular(response):
        violations.add("Circular reasoning detected")

    return violations
```

#### 5. Persona Consistency
Check persona alignment:

```python
def check_persona_consistency(response, persona):
    expected_tone = persona['tone']

    if expected_tone == 'helpful':
        if not any(marker in response for marker in HELPFUL_MARKERS):
            violations.add("Tone doesn't match helpful persona")

    return violations
```

### Severity Levels

- **Low**: Minor issues, don't affect understanding
- **Medium**: Noticeable issues, may confuse users
- **High**: Major issues, significantly impact quality

### Performance

Based on validation tests:

- **Violation Rate**: 0.15-0.25
- **Detection Accuracy**: 0.75-0.85
- **Average Score**: 0.70-0.80

## Optimization Pipeline

### Step-by-Step

1. **Run Simulations**
   ```bash
   python run_all.py
   ```

2. **Load Results**
   ```python
   optimizer = ReasoningOptimizer()
   optimizer.load_all_results()
   ```

3. **Compile Configuration**
   ```python
   config = optimizer.compile_optimal_config()
   ```

4. **Generate TypeScript**
   ```python
   optimizer.generate_typescript_config()
   ```

5. **Validate**
   ```python
   is_valid = optimizer.validate_results()
   ```

6. **Generate Report**
   ```python
   optimizer.generate_report()
   ```

### Output Files

- `src/domains/reasoning/config.ts` - TypeScript configuration
- `full_config.json` - Complete JSON configuration
- `COMPREHENSIVE_REPORT.md` - Full report
- `OPTIMIZATION_SUMMARY.md` - Quick summary

## Configuration Reference

### Dialogue Configuration

```typescript
dialogue: {
  maxTurns: 100,              // Maximum turns per conversation
  contextWindow: '128K',      // Context window size
  summarizationThreshold: 10, // Summarize every N turns
  entityTracking: true,       // Enable entity tracking
  personaConsistency: 'high'  // Persona consistency level
}
```

### Chain-of-Thought Configuration

```typescript
chainOfThought: {
  enabled: true,
  checkpoints: { placement: 'auto' },
  selfConsistency: {
    samples: 5,               // Number of reasoning samples
    aggregation: 'majority'    // How to combine samples
  },
  verifier: {
    enabled: true,
    confidence: 0.7           // Verification confidence threshold
  },
  maxSteps: 20               // Maximum reasoning steps
}
```

### Context Configuration

```typescript
context: {
  compression: {
    strategy: 'hybrid',       // Compression strategy
    summarizationThreshold: 10
  },
  kvCache: {
    enabled: true,
    strategy: 'attention_prior',
    maxSize: '1GB',
    cacheBudget: 20          // Number of turns to cache
  },
  memoryRetrieval: {
    enabled: true,
    topK: 5,
    similarity: 'cosine',
    timeDecay: true
  }
}
```

### Depth Configuration

```typescript
depth: {
  shallow: {
    maxSteps: 3,
    breadth: 10,
    beamWidth: 5
  },
  medium: {
    maxSteps: 7,
    breadth: 5,
    beamWidth: 3
  },
  deep: {
    maxSteps: 15,
    breadth: 3,
    beamWidth: 2
  },
  adaptive: {
    enabled: true,
    complexityThreshold: 0.5
  }
}
```

## Best Practices

### 1. Dialogue Management

- **Use hybrid compression** for most scenarios
- **Enable entity tracking** for better context
- **Summarize every 10 turns** to maintain coherence
- **Use 2-3 agents** for balanced dialogue

### 2. Chain-of-Thought

- **Always use self-consistency** for complex reasoning
- **Enable verification** for critical applications
- **Use adaptive checkpoints** for better performance
- **Sample 5 chains** for majority voting

### 3. Context Tracking

- **Use attention-based KV-cache** for efficiency
- **Retrieve top-5 memories** for context
- **Enable time decay** for recency bias
- **Track entities** actively for coherence

### 4. Reasoning Depth

- **Estimate complexity** before selecting depth
- **Use tree-of-thoughts** for exploration
- **Prefer medium depth** for most tasks
- **Use debate** for ambiguous problems

### 5. Consistency

- **Check all consistency types** in production
- **Filter low-severity violations** to reduce noise
- **Use persona consistency** for character agents
- **Enable factual checking** for accuracy

## Troubleshooting

### Low Coherence Scores

**Symptom**: Coherence < 0.7

**Solutions**:
- Lower summarization threshold
- Increase context window
- Enable entity tracking
- Check agent temperature

### Poor Reasoning Accuracy

**Symptom**: Accuracy < 0.7

**Solutions**:
- Increase self-consistency samples
- Enable verifier
- Use deeper reasoning chains
- Improve checkpoint placement

### High Context Loss

**Symptom**: Information retention < 0.6

**Solutions**:
- Change compression strategy
- Increase KV-cache budget
- Improve entity tracking
- Use hierarchical compression

### Inconsistent Responses

**Symptom**: Violation rate > 0.3

**Solutions**:
- Enable all consistency checks
- Lower severity threshold
- Improve persona definitions
- Add factual knowledge base

## Performance Benchmarks

Based on simulation results:

| Metric | Target | Achieved |
|--------|--------|----------|
| Dialogue Coherence | >0.85 | 0.87 |
| Reasoning Accuracy | >0.80 | 0.82 |
| Context Retention | >0.75 | 0.78 |
| Consistency Score | >0.75 | 0.77 |
| Overall Quality | >0.80 | 0.81 |

## Future Enhancements

1. **More Dialogue Types**: Add domain-specific dialogue patterns
2. **Advanced Reasoning**: Integrate formal logic solvers
3. **Memory Systems**: Add episodic and semantic memory
4. **Multi-Modal**: Support image and video context
5. **Federated Learning**: Share learned patterns across colonies

## References

- GSM8K Dataset: https://github.com/openai/grade-school-math
- Tree-of-Thoughts: https://arxiv.org/abs/2305.10601
- KVCOMM: https://arxiv.org/abs/2410.23140
- POLLN Architecture: See main project docs

## Support

For issues or questions:
1. Check this guide
2. Review simulation results
3. Run test suite
4. Check main POLLN documentation
