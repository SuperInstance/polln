# P32: Dreaming - Validation Criteria

**Paper:** P32 - Overnight Optimization Through Dreaming
**Created:** 2026-03-13
**Status:** Research Phase - Claims to Validate
**Hardware:** RTX 4050 GPU (CUDA 13.1.1, CuPy 14.0.1)

---

## Core Claims to Validate

### Claim 1: Dreaming Improves Next-Day Performance
**Statement:** Overnight dream rollouts improve next-day task performance by >15%.

**Validation Criteria:**
- [ ] Run tasks with dreaming phase (offline rollouts from replay buffer)
- [ ] Run tasks without dreaming (standard training only)
- [ ] Measure performance improvement: `(post_dream - pre_dream) / pre_dream * 100`
- [ ] Validate: improvement > 15%

**Falsification Criteria:**
- If improvement < 10% across multiple runs
- If dreaming degrades performance (negative improvement)
- If improvement is not statistically significant (p > 0.05)

**Data Required:**
```python
{
    "pre_dream_performance": float,  # Win rate before dreaming
    "post_dream_performance": float,  # Win rate after dreaming
    "improvement_percent": float,
    "dream_rollouts": int,  # Number of rollouts performed
    "replay_buffer_size": int,
    "statistical_significance": float  # p-value
}
```

---

### Claim 2: Dream Rollouts Converge Faster
**Statement:** Dream rollouts converge to optimal policies faster than standard experience replay.

**Validation Criteria:**
- [ ] Track learning curves with dreaming vs standard replay
- [ ] Measure timesteps to reach 90% of optimal performance
- [ ] Compare convergence rates
- [ ] Validate: dreaming converges >20% faster

**Data Required:**
```python
{
    "dreaming_convergence_timesteps": int,
    "standard_convergence_timesteps": int,
    "convergence_speedup": float,  # percentage faster
    "final_performance_dreaming": float,
    "final_performance_standard": float
}
```

---

### Claim 3: Replay Buffer Quality Matters
**Statement:** Dream quality correlates with replay buffer diversity (Shannon entropy > 2.5).

**Validation Criteria:**
- [ ] Calculate Shannon entropy of replay buffer states
- [ ] Measure dream quality (improvement from dreams)
- [ ] Calculate correlation between entropy and improvement
- [ ] Validate: correlation > 0.6

**Data Required:**
```python
{
    "replay_buffer_entropy": float,  # Shannon entropy
    "dream_quality_score": float,  # Measured improvement
    "entropy_improvement_correlation": float,
    "buffer_states_sampled": int,
    "entropy_distribution": List[float]  # Over time
}
```

---

### Claim 4: Sparse Rewards Benefit Most
**Statement:** Dreaming provides >30% improvement for sparse reward tasks vs <15% for dense rewards.

**Validation Criteria:**
- [ ] Run dreaming on sparse reward tasks (reward < 0.1 per step)
- [ ] Run dreaming on dense reward tasks (reward > 0.5 per step)
- [ ] Compare improvement percentages
- [ ] Validate: sparse_improvement > 2 * dense_improvement

**Data Required:**
```python
{
    "sparse_reward_improvement": float,
    "dense_reward_improvement": float,
    "improvement_ratio": float,  # sparse / dense
    "sparse_task_density": float,
    "dense_task_density": float
}
```

---

## Mathematical Formulation

### Dream Rollout Algorithm
```python
def dream_rollout(replay_buffer, value_network, num_rollouts=100):
    """
    Perform offline rollouts from replay buffer states.

    Args:
        replay_buffer: List of (state, action, reward, next_state)
        value_network: Trained value function V(s)
        num_rollouts: Number of dream trajectories

    Returns:
        Updated value network from dream experience
    """
    for _ in range(num_rollouts):
        # Sample random state from buffer
        state = sample(replay_buffer).state

        # Simulate trajectory using current policy
        trajectory = simulate_trajectory(state, value_network)

        # Update value network using TD learning
        update_value_network(trajectory, value_network)

    return value_network
```

### TD(λ) Dream Update
```
V(s) <- V(s) + α[δ + γ*λ*V(s') - V(s)]
where δ = r_dream + γ*V(s') - V(s)
```

**Key difference:** Dreams use simulated rewards `r_dream` from value network predictions.

---

## Simulation Parameters

### Dream Configuration
| Parameter | Value | Description |
|-----------|-------|-------------|
| dream_rollouts | 100 | Rollouts per overnight cycle |
| rollout_depth | 10 | Steps per rollout trajectory |
| replay_buffer_size | 10000 | Maximum buffer size |
| buffer_sample_size | 1000 | States sampled for dreaming |
| td_lambda | 0.9 | TD(λ) eligibility trace |
| learning_rate | 0.001 | Value network learning rate |

### Task Configuration
| Parameter | Sparse | Dense |
|-----------|--------|-------|
| Reward Probability | 0.05 | 0.5 |
| Reward Magnitude | 10.0 | 1.0 |
| Expected Reward/Step | 0.5 | 0.5 |
| Task Difficulty | Hard | Easy |

### Hardware Optimization
```python
# GPU-accelerated dream rollouts
import cupy as cp

# Vectorized rollout simulation
states_gpu = cp.asarray(sampled_states)
values_gpu = value_network.predict_batch(states_gpu)

# Parallel TD updates
deltas_gpu = reward_gpu + gamma * next_values_gpu - values_gpu
updates_gpu = alpha * deltas_gpu
```

**Memory Management:**
- Batch size: 32-64 rollouts per GPU batch
- State dimension: 64-128
- Replay buffer: Store in CPU, transfer batches to GPU

---

## Experimental Controls

### Control Groups
1. **No Dreaming:** Standard experience replay only
2. **Random Dreams:** Rollouts from random states (not from buffer)
3. **Shallow Dreams:** Rollout depth = 1 (no multi-step dreams)

### Experimental Groups
1. **Full Dreaming:** Replay buffer sampling with deep rollouts
2. **High-Entropy Dreams:** Buffer sampling with entropy threshold
3. **Adaptive Dreams:** Dynamic rollout depth based on uncertainty

### Baseline Comparisons
- Standard DQN without replay buffer
- Prioritized Experience Replay (PER)
- Hindsight Experience Replay (HER)

---

## Success Thresholds

| Metric | Minimum Success | Target Success |
|--------|----------------|----------------|
| Performance Improvement | >10% | >15% |
| Convergence Speedup | >15% | >20% |
| Entropy-Improvement Correlation | r > 0.5 | r > 0.6 |
| Sparse-Dense Improvement Ratio | >1.5x | >2.0x |
| Dream Quality Score | >0.1 | >0.15 |
| Statistical Significance | p < 0.05 | p < 0.01 |

---

## Failure Modes to Test

### 1. Catastrophic Forgetting in Dreams
**Scenario:** Dreams overwrite valuable experience
**Detection:** Performance on old tasks degrades >20%

### 2. Dream Hallucination
**Scenario:** Value network overfits to unrealistic dream states
**Detection:** Dream states diverge from real state distribution

### 3. Low Entropy Buffer
**Scenario:** Replay buffer lacks diversity
**Detection:** Shannon entropy < 2.0, minimal improvement

### 4. Sparse Reward Exploitation
**Scenario:** Agent finds ways to trigger rewards without solving task
**Detection:** High reward rate without task completion

---

## Cross-Paper Connections

### FOR Other Papers
- **P26 (Value Networks):** Dreams require accurate value functions
- **P24 (Self-Play):** Dream rollouts can simulate opponent strategies
- **P31 (Health Prediction):** Dreams can predict system health scenarios

### FROM Other Papers
- **P21 (Stochastic):** Stochastic dream exploration
- **P27 (Emergence):** Dreams can accelerate emergent capability discovery
- **P13 (Agent Networks):** Multi-agent dream coordination

### Synergies to Explore
- **P26 + P32:** Value networks enable high-quality dream rollouts
- **P24 + P32:** Self-play agents dream about adversarial strategies
- **P31 + P32:** Health prediction combined with failure scenario dreams

---

## GPU Performance Targets

### RTX 4050 (6GB VRAM) Optimization
- **Dream Rollout Batch:** 64 trajectories per batch
- **Memory per Batch:** ~500MB (states + values + gradients)
- **Throughput:** 1000 rollouts in <1 second
- **Value Network Inference:** <0.1ms per state

### CuPy Implementation
```python
# Efficient dream rollout with CuPy
def gpu_dream_rollout(states, value_net, depth=10):
    states_gpu = cp.asarray(states)

    for _ in range(depth):
        # Vectorized action selection
        actions_gpu = value_net.predict_batch(states_gpu)

        # Vectorized next states (simulated)
        next_states_gpu = simulate_batch(states_gpu, actions_gpu)

        # Update values
        values_gpu = value_net.forward(states_gpu)

    return cp.asnumpy(values_gpu)
```

---

## Validation Status

| Claim | Theoretical | Simulation | GPU-Accelerated | Status |
|-------|-------------|------------|-----------------|--------|
| C1: >15% improvement | ✓ | 🔲 Needed | Pending | Pending |
| C2: >20% faster convergence | ✓ | 🔲 Needed | Pending | Pending |
| C3: Entropy correlation >0.6 | ✓ | 🔲 Needed | Pending | Pending |
| C4: Sparse >2x dense | ✓ | 🔲 Needed | Pending | Pending |

---

## Next Steps

1. Implement dream rollout simulation
2. Create sparse and dense reward environments
3. Run dreaming vs standard replay comparisons
4. Measure replay buffer entropy over time
5. Document cross-paper findings with P26 (Value Networks)
6. Update NEXT_PHASE_PAPERS.md with results

---

*Schema Version: 1.0*
*GPU Optimized: RTX 4050*
*Last Updated: 2026-03-13*
