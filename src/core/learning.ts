/**
 * POLLN Hebbian Learning Implementation
 * Synaptic plasticity through co-activation
 *
 * Based on Round 2 Research: Resource Allocation & Memory Model
 */

export interface SynapseState {
  sourceAgentId: string;
  targetAgentId: string;
  weight: number;
  coactivationCount: number;
  lastCoactivated: number;
  learningRate: number;
  decayRate: number;
}

export interface LearningConfig {
  // Hebbian parameters
  learningRate: number;
  decayRate: number;
  minWeight: number;
  maxWeight: number;

  // Eligibility trace parameters
  traceLength: number;
  traceDecay: number;

  // Oja's rule normalization
  ojaNormalization: boolean;
}

/**
 * HebbianLearning - Synaptic plasticity for pathway strengthening
 *
 * Key insight: "Memory is stored as synaptic pathway strengths,
 * not in files. The body remembers by BECOMING."
 */
export class HebbianLearning {
  private config: LearningConfig;
  private synapses: Map<string, SynapseState> = new Map();

  constructor(config: Partial<LearningConfig>) {
    this.config = {
      learningRate: 0.01,
      decayRate: 0.001,
      minWeight: 0.01,
      maxWeight: 1.0,
      traceLength: 100,
      traceDecay: 0.95,
      ojaNormalization: true,
      ...config
    };
  }

  /**
   * Update synaptic weight based on co-activation
   *
   * Hebbian rule: Δw = η * pre * post * reward
   * With eligibility traces for delayed credit assignment
   */
  async updateSynapse(
    sourceId: string,
    targetId: string,
    preActivity: number,
    postActivity: number,
    reward: number
  ): Promise<number> {
    const key = `${sourceId}->${targetId}`;

    // Get or create synapse
    let synapse = this.synapses.get(key);
    if (!synapse) {
      synapse = {
        sourceAgentId: sourceId,
        targetAgentId: targetId,
        weight: 0.5,
        coactivationCount: 0,
        lastCoactivated: 0,
        learningRate: this.config.learningRate,
        decayRate: this.config.decayRate,
      };
      this.synapses.set(key, synapse);
    }

    // Apply Hebbian update with eligibility trace
    const oldWeight = synapse.weight;
    let weightDelta: number;

    if (this.config.ojaNormalization) {
      // Oja's rule: Δw = η * x * y - α * w² * x
      // Provides automatic normalization
      weightDelta = this.config.learningRate *
        preActivity *
        postActivity *
        (1 + reward) -
        this.config.learningRate * synapse.weight * preActivity * postActivity;
    } else {
      // Basic Hebbian rule
      weightDelta = this.config.learningRate *
        preActivity *
        postActivity *
        reward;
    }

    // Apply weight change
    const newWeight = Math.max(
      this.config.minWeight,
      Math.min(this.config.maxWeight, oldWeight + weightDelta)
    );

    synapse.weight = newWeight;
    synapse.coactivationCount += 1;
    synapse.lastCoactivated = Date.now();

    // Decay eligibility trace
    const traceAge = Date.now() - synapse.lastCoactivated;
    const traceDecay = Math.pow(this.config.traceDecay, traceAge / 1000);

    // Return effective weight change
    return newWeight - oldWeight;
  }

  /**
   * Get synapse weight between agents
   */
  getWeight(sourceId: string, targetId: string): number {
    const key = `${sourceId}->${targetId}`;
    const synapse = this.synapses.get(key);
    return synapse?.weight ?? 0.5;
  }

  /**
   * Get all synapses for an agent
   */
  getAgentSynapses(agentId: string): SynapseState[] {
    return Array.from(this.synapses.values()).filter(
      s => s.sourceAgentId === agentId || s.targetAgentId === agentId
    );
  }

  /**
   * Decay all synapses (overnight optimization)
   */
  async decayAll(): Promise<void> {
    for (const synapse of this.synapses.values()) {
      // Apply decay
      synapse.weight *= (1 - synapse.decayRate);

      // Enforce minimum
      if (synapse.weight < this.config.minWeight) {
        synapse.weight = this.config.minWeight;
      }
    }
  }

  /**
   * Prune weak synapses
   */
  async pruneWeak(threshold: number = 0.01): Promise<number> {
    let pruned = 0;
    for (const [key, synapse] of this.synapses) {
      if (synapse.weight < threshold) {
        this.synapses.delete(key);
        pruned++;
      }
    }
    return pruned;
  }

  /**
   * Get pathway statistics
   */
  getStats(): {
    totalSynapses: number;
    avgWeight: number;
    maxWeight: number;
    minWeight: number;
  } {
    const synapses = Array.from(this.synapses.values());
    const weights = synapses.map(s => s.weight);

    return {
      totalSynapses: synapses.length,
      avgWeight: weights.length > 0
        ? weights.reduce((a, b) => a + b, 0) / weights.length
        : 0,
      maxWeight: weights.length > 0 ? Math.max(...weights) : 0,
      minWeight: weights.length > 0 ? Math.min(...weights) : 0,
    };
  }
}
