# Polln — Pattern-Organized Large Language Network

**Polln** is a distributed intelligence framework that models agent decision-making as a pollen-based ecosystem: autonomous agents produce *pollen grains* (behavioral embeddings), share them through a **Behavioral Embedding Space (BES)**, and make stochastic decisions via a **Plinko Layer** that uses Gumbel-Softmax sampling to maintain exploration diversity. The system augments these mechanisms with a **VAE-based World Model** for dreaming/future simulation, a **Confidence Cascade** for multi-level signal propagation, and GPU-accelerated WGSL shaders for tensor algebra and rate-based change detection.

## Why It Matters

Most multi-agent systems suffer from mode collapse — agents converge on the same strategy and stop exploring. Polln solves this by treating agent selection as a stochastic sampling problem (Gumbel-Softmax) rather than a greedy argmax, ensuring persistent behavioral diversity. Its behavioral embedding space with differential privacy guarantees (via privacy tiers and budget accounting) makes it suitable for federated learning across untrusted nodes. The addition of a VAE world model enables *offline policy optimization through dream episodes* — agents simulate future trajectories in latent space and update their policies without real-world interaction, sample-efficiently. GPU acceleration via WebGPU/WGSL shaders makes the confidence cascade and tile algebra computations practical at scale.

## How It Works

### Stochastic Selection (Plinko Layer)

Instead of deterministically selecting the highest-confidence agent, Polln samples from the proposal distribution using the **Gumbel-Softmax trick**. Given agent proposals with confidence scores $c_i$, the selection probability is:

$$p_i = \frac{\exp(\log(c_i) / \tau)}{\sum_j \exp(\log(c_j) / \tau)}$$

where $\tau$ is a temperature parameter that anneals over time ($\tau_{t+1} = \max(\tau_{\min},\; \tau_t \cdot (1 - \text{decay}))$). Higher $\tau$ produces uniform exploration; lower $\tau$ approaches greedy selection. **Discriminators** (safety/quality predicates) act as hard gates before sampling — any proposal failing a discriminator is excluded from the softmax. The entropy of the resulting distribution $H = -\sum_i p_i \log p_i$ is tracked to detect collapse.

### VAE World Model & Dreaming

The world model follows the DreamerV2-style architecture: a **Variational Autoencoder (VAE)** encodes observations into a latent space parameterized by mean $\mu$ and log-variance $\log\sigma^2$, a **GRU recurrent network** models state transitions $s_{t+1} = f(s_t, a_t)$, and an **MLP reward predictor** estimates $r(s_t, a_t)$. Training minimizes:

$$\mathcal{L} = \mathcal{L}_{\text{recon}} + \beta \cdot D_{KL}(q(z|x) \;\|\; \mathcal{N}(0, I)) + \mathcal{L}_{\text{transition}} + \mathcal{L}_{\text{reward}}$$

The KL divergence term is weighted by $\beta$ (β-VAE formulation). During *dreaming*, the model rolls out trajectories for $H$ steps (the dream horizon) in latent space, computes TD($\lambda$) returns, and backpropagates policy gradients — all without environment interaction.

### Confidence Cascade

The confidence cascade is a hierarchical multi-level signal processor. Each level maintains a `ConfidenceLevel` struct (value, uncertainty, stability, trend) and up to 8 `DeadbandTrigger` instances. A **deadband** is a hysteresis region $[r_{\min}, r_{\max}]$ where no state change occurs — this prevents oscillation near thresholds. When a trigger fires, confidence propagates to parent levels via `propagation_weight`, enabling multi-scale anomaly detection. This is implemented as parallel WGSL compute shaders on GPU.

### Rate-Based Change Mechanics

Rate-based change tracks derivatives of observations rather than absolute values. The fundamental equation: $x(t) = x_0 + \int_0^t r(\tau)\,d\tau$, approximated discretely as $x_{n+1} = x_n + r_n \Delta t + O(\Delta t^2)$. Higher-order rates (acceleration, jerk, snap) are computed for anomaly detection. Deadbands on rates $[r_{\min}, r_{\max}]$ filter noise — only rate changes outside the deadband trigger updates.

### Tile Algebra

Tiles are self-contained behavioral units with position, confidence, and zone membership. The composition operators $\otimes$ (combine) and $\oplus$ (merge) use weight matrices to fuse tiles spatially. Zones group tiles into spatial regions with neighbor relationships, enabling localized confidence propagation. Tiles are categorized by lifespan: **EPHEMERAL** (minutes), **ROLE** (days), **CORE** (infrastructure).

### Complexity

| Operation | Complexity |
|-----------|-----------|
| Plinko selection (n proposals) | $O(n)$ |
| VAE forward pass (latent dim $d$) | $O(d^2)$ |
| Confidence cascade ($L$ levels, $T$ triggers) | $O(L \cdot T)$ |
| Tile composition ($n$ tiles) | $O(n^2)$ spatial check |
| BES similarity search ($k$ neighbors, $N$ grains) | $O(N \cdot d)$ per query; $O(\log N \cdot d)$ with index |

## Quick Start

```bash
# Clone and install
git clone https://github.com/SuperInstance/Polln.git
cd Polln
npm install

# Build
npm run build

# Run the SDK
import { PollnSDK } from 'polln';

const sdk = new PollnSDK({
  worldModel: { latentDim: 64, hiddenDim: 256, beta: 0.5 },
  plinko: { temperature: 1.0, minTemperature: 0.1, decayRate: 0.001 },
});

// Register agents and process proposals
const result = await sdk.plinko.process([
  { agentId: 'explorer-1', confidence: 0.82, bid: 10 },
  { agentId: 'diplomat-2', confidence: 0.91, bid: 15 },
]);
console.log(`Selected: ${result.selectedAgentId} at T=${result.temperature}`);

// Generate dream episodes for offline policy optimization
const dreams = sdk.worldModel.dream({
  startState: latentState,
  horizon: 50,
  batchSize: 16,
});
```

## API

### Core Types

```typescript
class PlinkoLayer {
  constructor(config: PlinkoConfig);
  registerDiscriminator(name: string, check: (p: AgentProposal) => boolean): void;
  async process(proposals: AgentProposal[]): Promise<PlinkoResult>;
}

class WorldModel {
  constructor(config: WorldModelConfig);
  encode(observation: number[]): LatentState;        // VAE encoder
  transition(state: LatentState, action: number): TransitionResult;
  dream(config: { startState, horizon, batchSize }): DreamEpisode[];
}

class GPUEngine {
  static getInstance(): GPUEngine;
  async init(): Promise<GPUDeviceInfo>;
  executeCompute(shader: string, buffers: GPUBufferInfo[]): GPUExecutionResult;
}

class SafetyLayer {
  addConstraint(c: ConstitutionalConstraint): void;
  check(action: unknown): SafetyCheckResult;
  triggerKillSwitch(): void;
  checkpoint(): string;  // rollback point
}

interface Tile<TInput, TOutput> {
  execute(input: TInput, ctx: TileContext): Promise<TileResult<TOutput>>;
  observe(outcome: TileOutcome): void;
  serialize(): PollenGrain;
}
```

### WGSL Shader Libraries

- `confidence_cascade.wgsl` — Deadband triggers, cascade propagation, activation functions
- `rate_based_change.wgsl` — Rate/acceleration calculation, anomaly detection, state reconstruction
- `geometric_tensors.wgsl` — Pythagorean tensors, Wigner-D harmonics
- `tile_algebra.wgsl` — Tile composition (⊗, ⊕), zone computation, confidence flow

## Architecture Notes

Polln serves as the **cognitive engine** in the SuperInstance fleet architecture. Within the γ + η = C framework (where γ is the conservation ratio of ternary actions and η is Shannon entropy), Polln's Plinko layer directly controls γ by tuning exploration temperature — high τ increases η (diversity), low τ concentrates γ toward exploitation. The VAE world model provides the forward simulation capacity needed to evaluate policy variants without disturbing the live ecosystem. Polln's BES (Behavioral Embedding Space) federates knowledge across fleet nodes via pollen grain exchange, with privacy tiers enforcing differential privacy budgets.

See the full architecture: [SuperInstance Architecture](https://github.com/SuperInstance/SuperInstance/blob/main/ARCHITECTURE.md)

## References

1. Ha, D. & Schmidhuber, J. (2018). "World Models." *arXiv:1803.10122* — VAE + RNN + Controller architecture for model-based RL.
2. Jang, E., Gu, S., & Poole, B. (2017). "Categorical Reparameterization with Gumbel-Softmax." *ICLR 2017* — The differentiable sampling trick used by the Plinko layer.
3. Hafner, D. et al. (2020). "DreamerV2: Mastering Atari with Discrete World Models." *arXiv:2010.02193* — Dream episode generation for offline policy improvement.

## License

MIT
