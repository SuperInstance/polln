# Dreaming Simulations - Proof That Dreaming Improves World Models and Policies

This directory contains Python simulations that prove dream-based optimization improves learning efficiency in reinforcement learning agents.

## Mathematical Foundation

### VAE (Variational Autoencoder)
```
Encoder: z ~ q_φ(z|x) = N(μ_φ(x), σ_φ²(x))
Decoder: x ~ p_θ(x|z) = N(μ_θ(z), σ_θ²(z))
Loss: L = E_q[log p(x|z)] - β·KL(q(z|x) || p(z))
```

### Dream-Based Policy Update
```
Dream: V_dream(s,a) = E[Σ γ^i r_i | model]
Policy: θ ← θ + α∇_θ Σ_t dream_return_t
```

## Simulation Suite

### 1. VAE Training (`vae_training.py`)
- **Purpose**: Train VAE on MDP trajectories
- **Vary**: Latent dimension, β (KL weight)
- **Measure**: Reconstruction loss, KL divergence
- **Prove**: Optimal latent dimensionality for different MDPs

### 2. Dream Rollout Quality (`dream_rollouts.py`)
- **Purpose**: Compare dream vs real trajectories
- **Measure**: Distribution similarity, value estimates
- **Prove**: Dream rollouts approximate real dynamics

### 3. Dream-Based Policy Optimization (`dream_policy.py`)
- **Purpose**: Compare dream-only vs mixed vs real-only learning
- **Vary**: Dream ratio (0-100%)
- **Measure**: Sample efficiency, final performance
- **Prove**: Optimal dream-to-real ratio

### 4. Model-Based RL (`mb_rl.py`)
- **Purpose**: Compare MPC, Dyna, Dreamer, PLANET
- **Measure**: Performance per environment step
- **Prove**: When model-based helps most

## Key Hypotheses

### H1: Latent Sufficiency
If latent dim d ≥ d_critical: V_dream ≈ V_real

### H2: Dream Efficiency
Dream samples cost 0, environment samples cost >0

### H3: Imagination Bonus
Dreaming encourages exploration of unseen states

## Running Simulations

```bash
# Install dependencies
pip install -r requirements.txt

# Run all simulations
python run_all_simulations.py

# Run individual simulations
python vae_training.py
python dream_rollouts.py
python dream_policy.py
python mb_rl.py
```

## Expected Results

1. **VAE Training**: Reconstruction loss decreases with proper β
2. **Dream Quality**: Dream trajectories match real distributions
3. **Policy Learning**: Mixed dream-real learning outperforms either alone
4. **Sample Efficiency**: 2-10x improvement over model-free methods

## Dependencies

- PyTorch >= 2.0
- Gymnasium (Minigrid)
- NumPy, SciPy
- Matplotlib (visualization)
- TensorBoard (logging)
