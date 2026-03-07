# Resource Allocation Integration Guide

**Connecting the Blood Flow Mechanism to POLLN Architecture**

---

## Overview

This document shows how to integrate the Resource Allocation System with existing POLLN components defined in `ARCHITECTURE.md`.

---

## Integration Map

```
┌─────────────────────────────────────────────────────────────┐
│                 RESOURCE ALLOCATION IN POLLN                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RESOURCE ALLOCATION SYSTEM                                 │
│  (This Research)                                            │
│         │                                                   │
│         ├──► PLINKO LAYER (Existing)                        │
│         │    • Resource-aware stochastic selection           │
│         │    • Budget-adjusted confidence scores             │
│         │                                                    │
│         ├──► AGENT COLONY (Existing)                        │
│         │    • Per-agent resource budgets                    │
│         │    • Load-aware task acceptance                   │
│         │    • Pathway strength tracking                    │
│         │                                                    │
│         ├──► SPORE PROTOCOL (Existing)                      │
│         │    • Shared pathway strength topics               │
│         │    • Eligibility trace broadcasting               │
│         │    • Resource allocation events                   │
│         │                                                    │
│         ├──► EXECUTORS (Existing)                           │
│         │    • Outcome reporting for credit assignment      │
│         │    • Resource-constrained execution               │
│         │                                                    │
│         └──► OVERNIGHT OPTIMIZATION (Existing)              │
│              • Synaptic downscaling                         │
│              • Pattern extraction via dreaming              │
│              • Memory consolidation                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component-Level Integration

### 1. Integration with Plinko Layer

**Current Plinko Flow** (from ARCHITECTURE.md):
```
Proposals → Filter → Gumbel Noise → Softmax → Selection
```

**Enhanced with Resource Awareness**:
```python
class ResourceAwarePlinko(PlinkoLayer):
    def select_proposal(self, proposals, context):
        # Standard Plinko filtering
        filtered = self.safety_filter(proposals)
        filtered = self.coherence_filter(filtered)

        # RESOURCE AWARENESS: Adjust scores based on resources
        resource_adjusted = []
        for proposal in filtered:
            agent = proposal.proposing_agent
            resources = self.resource_system.get_allocation(agent)

            # Boost if agent has good resource allocation
            resource_multiplier = 1.0 + (resources * 0.2)

            adjusted_score = proposal.confidence * resource_multiplier
            resource_adjusted.append((proposal, adjusted_score))

        # Standard Plinko selection on adjusted scores
        return self.stochastic_select(resource_adjusted)
```

**Why**: Ensures Plinko doesn't select proposals from resource-starved agents.

---

### 2. Integration with Agent Colony

**Agent Enhancement**:
```python
class ResourceAwareAgent(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id)
        self.resource_budget = 0.0
        self.current_load = 0.0
        self.pathway_strengths = {}

    def should_accept_task(self, task):
        """Local load balancing decision."""
        load_pressure = self.current_load / self.capacity

        # Probabilistic acceptance
        acceptance_prob = 1.0 - sigmoid(load_pressure - 0.7)

        # High priority more likely to accept
        if task.priority > HIGH_PRIORITY:
            acceptance_prob *= 1.5

        return random() < acceptance_prob

    def execute(self, task, resources):
        """Execute within resource budget."""
        self.current_load += resources

        try:
            result = self.do_execute(task)
            return result
        finally:
            self.current_load -= resources
```

**SPORE Topics for Resource Sharing**:
- `agent/{id}/pathway_strengths` - Publish pathway strengths
- `agent/{id}/resource_budget` - Publish current allocation
- `agent/{id}/load_metrics` - Publish load for balancing

---

### 3. Integration with SPORE Protocol

**New SPORE Topics**:
```
resource/allocation/global     - Global budget announcements
resource/allocation/{agent_id} - Per-agent allocations
pathway/update/{pathway_id}    - Pathway strength updates
eligibility/trace/{agent_id}   - Eligibility trace broadcasts
consolidation/overnight/start  - Nightly consolidation trigger
consolidation/overnight/complete - Consolidation done
```

**Message Schemas**:
```python
# Resource allocation announcement
{
    "type": "resource_allocation",
    "agent_id": "vision_processor_1",
    "budget": {
        "compute": 0.25,
        "memory": 0.30,
        "network": 0.20
    },
    "pathway_strengths": {
        "object_detection": 0.85,
        "segmentation": 0.72,
        "tracking": 0.65
    }
}

# Pathway update
{
    "type": "pathway_update",
    "pathway_id": "vision_processor_1->object_detection",
    "old_strength": 0.85,
    "new_strength": 0.87,
    "reward": 0.5,
    "timestamp": 1678123456.789
}
```

---

### 4. Integration with Executors

**Executor Enhancement**:
```python
class ResourceAwareExecutor(Executor):
    async def execute(self, action, resources):
        """Execute action within resource constraints."""

        # Check if we have enough resources
        if not self.check_resources(resources):
            raise ResourceLimitError("Insufficient resources")

        # Mark pathways as active (for eligibility trace)
        self.mark_pathways_active(action.pathways)

        try:
            # Execute with timeout based on resources
            timeout = self.compute_timeout(resources)
            result = await asyncio.wait_for(
                self.do_execute(action),
                timeout=timeout
            )

            # Report outcome for credit assignment
            self.report_outcome(action, result)

            return result

        except asyncio.TimeoutError:
            # Penalty for timeout
            self.report_outcome(action, Outcome(success=False, penalty=0.5))
            raise
```

---

### 5. Integration with Overnight Optimization

**Enhanced Dreaming**:
```python
async def overnight_dreaming():
    """Run during idle periods."""

    # Phase 1: Synaptic downscaling
    pathways = await load_all_pathways()
    synaptic_downscaling(pathways, factor=0.8)

    # Phase 2: Pattern extraction (existing dreaming)
    mutations = generate_mutations(pathways)
    for mutation in mutations:
        score = await evaluate_simulation(mutation)
        if score > baseline + IMPROVEMENT_THRESHOLD:
            await save_discovered_pattern(mutation, score)

    # Phase 3: Memory consolidation
    pollen = await load_pollen_grains()
    consolidated = consolidate_memories(pollen)
    await save_pollen_grains(consolidated)

    # Phase 4: Pruning
    prune_weak_pathways(pathways)

    # Announce completion
    await publish("consolidation/overnight/complete", {
        "pathways_pruned": count_pruned(pathways),
        "patterns_discovered": len(consolidated),
        "timestamp": time.time()
    })
```

---

## Data Flow Examples

### Example 1: Resource-Aware Action Selection

```
1. Context arrives (user request)
2. Sensors publish to SPORE
3. Agent colonies receive context
4. Agents propose actions (with confidence scores)
5. Proposals arrive at Plinko layer
6. Resource system queried for each proposing agent's resources
7. Proposal scores adjusted based on resources
8. Gumbel noise added
9. Softmax selection
10. Selected executor receives action + resource budget
11. Executor checks budget, executes
12. Outcome reported
13. Pathway strengths updated (Hebbian)
14. Eligibility trace updated
15. Resource allocation updated for next cycle
```

### Example 2: Overnight Consolidation

```
1. System detects idle period (low load for 30 min)
2. Consolidation trigger published
3. All agents stop learning (freeze pathway updates)
4. Load all pathway strengths
5. Apply synaptic downscaling (factor=0.8)
6. Load pollen grains (memories)
7. Consolidate based on importance
8. Run dreaming simulations (1000 mutations)
9. Save discovered patterns
10. Prune pathways below threshold
11. Rebuild vector index
12. Publish completion
13. System resumes normal operation
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Implement `ResourceAllocationSystem` class
- [ ] Create SPORE topics for resource sharing
- [ ] Build eligibility trace system
- [ ] Implement basic Hebbian updates

### Phase 2: Plinko Integration
- [ ] Extend `PlinkoLayer` for resource awareness
- [ ] Add resource adjustment to proposal scoring
- [ ] Integrate with Gumbel-softmax selection

### Phase 3: Agent Integration
- [ ] Add resource budget tracking to agents
- [ ] Implement load-aware task acceptance
- [ ] Add pathway strength publishing

### Phase 4: Executor Integration
- [ ] Add resource constraints to execution
- [ ] Implement outcome reporting
- [ ] Connect to eligibility traces

### Phase 5: Overnight Consolidation
- [ ] Implement synaptic downscaling
- [ ] Build memory consolidation
- [ ] Connect to existing dreaming system
- [ ] Add pruning logic

### Phase 6: Monitoring
- [ ] Add resource allocation metrics
- [ ] Track pathway strength evolution
- [ ] Monitor consolidation effectiveness
- [ ] Alert on resource exhaustion

---

## Configuration

```python
# Resource allocation config
RESOURCE_CONFIG = {
    "total_budget": 1.0,
    "min_budget_share": 0.05,  # 5% minimum per agent
    "max_budget_share": 0.5,   # 50% maximum per agent
    "learning_rate": 0.01,
    "decay_rate": 0.001,
    "prune_threshold": 0.1,
    "downscale_factor": 0.8,
    "attention_temperature": 1.0,
    "consolidation_interval": 86400,  # 24 hours
}
```

---

## Testing

### Unit Tests
- [ ] Hebbian update rule correctness
- [ ] Attention mechanism selection probabilities
- [ ] Budget allocation fairness
- [ ] Synaptic downscaling preserves ratios

### Integration Tests
- [ ] Plinko selection with resource awareness
- [ ] Agent task acceptance under load
- [ ] Executor outcome feedback
- [ ] Overnight consolidation end-to-end

### Load Tests
- [ ] 1000 agents with resource allocation
- [ ] Overnight consolidation with 1M pathways
- [ ] High-load graceful degradation

---

## Monitoring Metrics

```python
# Key metrics to track
METRICS = {
    # Resource utilization
    "resource_utilization": gauge,
    "agent_load_distribution": histogram,
    "budget_allocation_efficiency": gauge,

    # Learning
    "pathway_strength_mean": gauge,
    "pathway_strength_variance": gauge,
    "pathways_pruned_count": counter,
    "learning_convergence_rate": gauge,

    # Consolidation
    "consolidation_duration": histogram,
    "patterns_discovered": counter,
    "signal_to_noise_ratio": gauge,
}
```

---

**Document Status**: Integration Ready
**Dependencies**: All core POLLN components
**Next Step**: Begin Phase 1 implementation

---

*Integration Guide for Resource Allocation System*
*POLLN Round 2 Research*
*Last Updated: 2026-03-06*
