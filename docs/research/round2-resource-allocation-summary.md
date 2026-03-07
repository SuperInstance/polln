# Resource Allocation Algorithms - Quick Reference

**Extracted from**: `round2-resource-allocation.md`

---

## Core Algorithms

### 1. Hebbian Pathway Update

```python
def hebbian_update(synapse, pre_activity, post_activity, reward):
    """
    Update synaptic weight: neurons that fire together wire together.

    Δw = η · pre · post · tanh(reward)
    """
    delta = LEARNING_RATE * pre_activity * post_activity * tanh(reward)
    synapse.weight += delta
    synapse.weight *= (1 - DECAY_RATE)  # Forgetting
    return clamp(synapse.weight, MIN, MAX)
```

### 2. Agent Selection via Attention

```python
def select_agent(context, agents, temperature=1.0):
    """
    Select agent using transformer-style attention.

    Q = context embedding
    K = agent specialization embedding
    Score = cosine(Q, K)
    P = softmax(Scores / temperature)
    Selected = sample(P)
    """
    scores = [cosine_sim(context.embedding, agent.key) for agent in agents]
    probs = softmax(scores / temperature)
    return agents[sample_categorical(probs)]
```

### 3. Resource Budget Allocation

```python
def allocate_budget(pathway_strengths, total_budget):
    """
    Distribute budget based on pathway strengths.

    allocation_i = base_i + (remaining) * (strength_i / total_strength)
    """
    # Ensure minimum allocations
    allocations = {agent: MIN_BUDGET for agent in pathway_strengths}

    # Distribute remaining proportionally
    remaining = total_budget - sum(allocations.values())
    total_strength = sum(pathway_strengths.values())

    for agent, strength in pathway_strengths.items():
        discretionary = (strength / total_strength) * remaining
        allocations[agent] += discretionary

    return allocations
```

### 4. Overnight Synaptic Downscaling

```python
def overnight_consolidation(pathways, factor=0.8):
    """
    Proportionally reduce all weights (prevent saturation).

    All weights *= factor
    Weights < threshold → prune
    """
    for pathway in pathways:
        pathway.strength *= factor

        if pathway.strength < PRUNE_THRESHOLD:
            pathway.active = False  # Prune weak pathways
```

### 5. Eligibility Trace (Credit Assignment)

```python
def mark_active(trace, pathway_id):
    """Mark pathway as recently active."""
    trace[pathway_id] = trace.get(pathway_id, 0) + 1.0

def decay_traces(trace, rate=0.95):
    """Age out old traces."""
    for id in trace:
        trace[id] *= rate

def update_with_reward(trace, pathways, reward):
    """Update pathways proportional to eligibility."""
    for pathway in pathways:
        eligibility = trace.get(pathway.id, 0)
        pathway.strength += eligibility * reward * LEARNING_RATE
```

---

## Key Constants

```python
LEARNING_RATE = 0.01          # Hebbian learning rate
DECAY_RATE = 0.001            # Weight decay (forgetting)
MIN_BUDGET = 0.05             # Minimum resource share (5%)
PRUNE_THRESHOLD = 0.1         # Strength below which to prune
DOWNSCALE_FACTOR = 0.8        # Overnight consolidation
TEMPERATURE = 1.0             # Attention exploration (higher = more exploration)
```

---

## Design Principles

1. **Resource = Learning**: Where compute flows, system grows
2. **Local Autonomy**: Agents make local decisions
3. **Subsumption**: Safety gets resources first
4. **Forgetting**: Decay is essential
5. **Probabilistic**: Strength → probability, not certainty
6. **Fairness**: Prevent monopolization
7. **Consolidation**: Overnight optimization required

---

## Integration Points

- **Plinko Layer**: Resource-aware stochastic selection
- **SPORE Protocol**: Shared memory for pathway strengths
- **Executor Agents**: Report outcomes for credit assignment
- **Coordinator**: Load metrics for budget adjustment

---

*Quick Reference for Implementation*
*See full document for details*
