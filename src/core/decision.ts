/**
 * POLLN Plinko Decision Layer
 * Stochastic decision making using Gumbel-Softmax
 *
 * Based on Round 2 Research: Stochastic Selection Superiority
 */

import { v4 } from 'uuid';

export interface AgentProposal {
  agentId: string;
  confidence: number;
  bid: number;
}

export interface PlinkoConfig {
  temperature: number;
  minTemperature: number;
  decayRate: number;
}

export interface PlinkoResult {
  id: string;
  proposals: AgentProposal[];
  selectedAgentId: string;
  temperature: number;
  entropy: number;
  discriminatorResults: Record<string, boolean>;
  explanation?: string;
  wasOverridden: boolean;
  overrideReason?: string;
}

/**
 * PlinkoLayer - Stochastic selection with discriminators
 *
 * Key insight from research:
 * Stochastic selection maintains diversity and adapts better to changing environments
 */
export class PlinkoLayer {
  private config: PlinkoConfig;
  private discriminators: Map<string, (proposal: AgentProposal) => boolean> = new Map();

  private results: PlinkoResult[] = [];

  constructor(config: PlinkoConfig) {
    this.config = {
      temperature: 1.0,
      minTemperature: 0.1,
      decayRate: 0.001,
      ...config
    };
  }

  /**
   * Register a discriminator for safety/quality checks
   */
  registerDiscriminator(
    name: string,
    check: (proposal: AgentProposal) => boolean
  ): void {
    this.discriminators.set(name, check);
  }

  /**
   * Process proposals and stochastic selection
   */
  async process(proposals: AgentProposal[]): Promise<PlinkoResult> {
    const id = uuidv4();

    // Calculate entropy for exploration decision
    const entropy = this.calculateEntropy(proposals);

    // Apply temperature (annealing)
    const effectiveTemp = Math.max(
      this.config.minTemperature,
      this.config.temperature
    );

    // Run discriminator checks
    const discriminatorResults: Record<string, boolean> = {};
    for (const [name, check] of this.discriminators) {
      discriminatorResults[name] = proposals.every(p => check(p));
    }

    // Check for safety override
    const safetyPassed = discriminatorResults['safety'] !== false;
    let wasOverridden = false;
    let overrideReason: string | undefined;

    if (!safetyPassed) {
      wasOverridden = true;
      overrideReason = 'Safety constraint violation';
    }

    // Apply Gumbel-Softmax selection
    let selectedAgentId: string;
    let explanation: string | undefined;

    if (wasOverridden) {
      // Select safest agent instead
      selectedAgentId = this.selectSafestAgent(proposals);
      explanation = 'Selected safest agent due to safety override';
    } else {
      selectedAgentId = this.gumbelSoftmax(proposals, effectiveTemp);
      explanation = `Selected via stochastic selection (temp=${effectiveTemp.toFixed(2)})`;
    }

    const result: PlinkoResult = {
      id,
      proposals,
      selectedAgentId,
      temperature: effectiveTemp,
      entropy,
      discriminatorResults,
      explanation,
      wasOverridden,
      overrideReason,
    };

    this.results.push(result);

    // Anneal temperature
    this.config.temperature = Math.max(
      this.config.minTemperature,
      this.config.temperature * (1 - this.config.decayRate)
    );

    return result;
  }

  /**
   * Gumbel-Softmax selection
   *
   * Adds Gumbel noise to logits for stochastic exploration
   */
  private gumbelSoftmax(proposals: AgentProposal[], temperature: number): string {
    // Extract confidence scores
    const logits = proposals.map(p => p.confidence);

    // Add Gumbel noise: G = -log(-log(U)) where U ~ Uniform(0, 1)
    const gumbelNoise = logits.map(() =>
      -Math.log(-Math.random())
    );

    // Compute perturbed scores
    const perturbedScores = logits.map((logit, i) =>
      (logit + temperature * gumbelNoise[i]) / temperature
    );

    // Select argmax of perturbed scores
    const selectedIndex = perturbedScores.indexOf(Math.max(...perturbedScores));
    return proposals[selectedIndex].agentId;
  }

  /**
   * Calculate entropy (diversity measure)
   */
  private calculateEntropy(proposals: AgentProposal[]): number {
    const confidences = proposals.map(p => p.confidence);
    const max = Math.max(...confidences);
    const sum = confidences.reduce((a, b) => a + Math.exp(b / max), 0);
    return -Math.log(sum);
  }

  /**
   * Select safest agent when safety override
   */
  private selectSafestAgent(proposals: AgentProposal[]): string {
    // For now, just select the one with highest confidence
    // In a full implementation, this would consider safety scores
    const safest = proposals.reduce((best, current) =>
      current.confidence > best.confidence ? current : best
    );
    return safest.agentId;
  }

  /**
   * Get decision history for analysis
   */
  getHistory(limit: number = 10): PlinkoResult[] {
    return this.results.slice(-limit);
  }
}
