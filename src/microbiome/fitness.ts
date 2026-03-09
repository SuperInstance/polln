/**
 * POLLN Microbiome - Fitness System
 *
 * Phase 3: Evolution & Natural Selection
 * Implements sophisticated multi-objective fitness evaluation with
 * Pareto dominance, fitness sharing, and dynamic adaptation.
 *
 * @module microbiome/fitness
 */

import {
  MicrobiomeAgent,
  FitnessScore,
  EcosystemSnapshot,
  AgentTaxonomy,
  Symbiosis,
  ResourceType,
} from './types.js';

/**
 * Fitness objective weights
 */
export interface FitnessWeights {
  /** Weight for throughput score */
  throughput: number;
  /** Weight for accuracy score */
  accuracy: number;
  /** Weight for efficiency score */
  efficiency: number;
  /** Weight for cooperation score */
  cooperation: number;
}

/**
 * Constraint definition
 */
export interface Constraint {
  /** Constraint ID */
  id: string;
  /** Constraint name */
  name: string;
  /** Check if constraint is satisfied */
  isSatisfied: (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot) => boolean;
  /** Penalty weight for violation (0-1) */
  penalty: number;
  /** Constraint description */
  description?: string;
}

/**
 * Pareto front information
 */
export interface ParetoFront {
  /** Front rank (0 = best) */
  rank: number;
  /** Crowding distance (diversity measure) */
  crowdingDistance: number;
  /** Dominated count */
  dominatedCount: number;
  /** Dominates set */
  dominates: Set<string>;
  /** Is dominated by set */
  dominatedBy: Set<string>;
}

/**
 * Fitness sharing configuration
 */
export interface FitnessSharingConfig {
  /** Enable fitness sharing */
  enabled: boolean;
  /** Sharing radius (similarity threshold) */
  sigma: number;
  /** Alpha parameter (1 = linear, 2 = quadratic) */
  alpha: number;
}

/**
 * Dynamic fitness configuration
 */
export interface DynamicFitnessConfig {
  /** Enable dynamic fitness */
  enabled: boolean;
  /** Environment sensitivity (0-1) */
  environmentSensitivity: number;
  /** Seasonal adjustment rate (0-1) */
  seasonalRate: number;
  /** Resource scarcity factor (0-1) */
  resourceScarcityFactor: number;
}

/**
 * Fitness evaluator configuration
 */
export interface FitnessEvaluatorConfig {
  /** Fitness objective weights */
  weights: FitnessWeights;
  /** Fitness sharing configuration */
  sharing: FitnessSharingConfig;
  /** Dynamic fitness configuration */
  dynamic: DynamicFitnessConfig;
  /** Constraints */
  constraints: Constraint[];
  /** Enable Pareto ranking */
  enablePareto: boolean;
  /** Enable constraint penalties */
  enableConstraints: boolean;
}

/**
 * Fitness evaluation result with metadata
 */
export interface FitnessEvaluation {
  /** Agent ID */
  agentId: string;
  /** Raw fitness score */
  rawScore: FitnessScore;
  /** Adjusted fitness (after sharing, penalties) */
  adjustedScore: FitnessScore;
  /** Pareto front information */
  paretoInfo: ParetoFront;
  /** Constraint violations */
  violations: string[];
  /** Environmental factors applied */
  environmentalFactors: number[];
}

/**
 * Population fitness summary
 */
export interface PopulationFitnessSummary {
  /** Best fitness */
  bestFitness: FitnessScore;
  /** Average fitness */
  avgFitness: FitnessScore;
  /** Worst fitness */
  worstFitness: FitnessScore;
  /** Fitness diversity (standard deviation) */
  fitnessDiversity: number;
  /** Pareto front sizes by rank */
  paretoFronts: Map<number, number>;
  /** Constraint violation rate */
  violationRate: number;
}

/**
 * Default fitness weights
 */
const DEFAULT_WEIGHTS: FitnessWeights = {
  throughput: 0.25,
  accuracy: 0.35,
  efficiency: 0.25,
  cooperation: 0.15,
};

/**
 * Default fitness sharing configuration
 */
const DEFAULT_SHARING: FitnessSharingConfig = {
  enabled: true,
  sigma: 0.5,
  alpha: 1.0,
};

/**
 * Default dynamic fitness configuration
 */
const DEFAULT_DYNAMIC: DynamicFitnessConfig = {
  enabled: true,
  environmentSensitivity: 0.3,
  seasonalRate: 0.1,
  resourceScarcityFactor: 0.2,
};

/**
 * Fitness Evaluator
 *
 * Provides sophisticated multi-objective fitness evaluation with
 * Pareto dominance, fitness sharing, dynamic adaptation, and constraint handling.
 */
export class FitnessEvaluator {
  /** Configuration */
  private config: FitnessEvaluatorConfig;
  /** Current ecosystem snapshot */
  private currentSnapshot: EcosystemSnapshot | null;
  /** Seasonal phase (0-1) */
  private seasonalPhase: number;
  /** Fitness history for adaptation */
  private fitnessHistory: Map<string, FitnessScore[]>;

  constructor(config: Partial<FitnessEvaluatorConfig> = {}) {
    this.config = {
      weights: config.weights ?? DEFAULT_WEIGHTS,
      sharing: config.sharing ?? DEFAULT_SHARING,
      dynamic: config.dynamic ?? DEFAULT_DYNAMIC,
      constraints: config.constraints ?? [],
      enablePareto: config.enablePareto ?? true,
      enableConstraints: config.enableConstraints ?? true,
    };

    this.currentSnapshot = null;
    this.seasonalPhase = 0;
    this.fitnessHistory = new Map();
  }

  /**
   * Evaluate fitness for a single agent
   */
  evaluate(agent: MicrobiomeAgent): FitnessScore {
    // Get base fitness from agent
    let score = agent.evaluateFitness();

    // Apply dynamic adjustments
    if (this.config.dynamic.enabled && this.currentSnapshot) {
      score = this.applyDynamicFitness(agent, score);
    }

    // Apply constraint penalties
    if (this.config.enableConstraints && this.config.constraints.length > 0) {
      score = this.applyConstraints(agent, score);
    }

    // Apply weighted combination
    score = this.applyWeights(score);

    return score;
  }

  /**
   * Evaluate fitness for population with Pareto ranking
   */
  evaluatePopulation(agents: MicrobiomeAgent[]): Map<string, FitnessEvaluation> {
    const evaluations = new Map<string, FitnessEvaluation>();
    const rawScores = new Map<string, FitnessScore>();

    // Evaluate each agent
    for (const agent of agents) {
      const rawScore = this.evaluate(agent);
      rawScores.set(agent.id, rawScore);
    }

    // Calculate Pareto fronts if enabled
    const paretoFronts = this.config.enablePareto
      ? this.calculateParetoFronts(agents, Array.from(rawScores.values()))
      : new Map<string, ParetoFront>();

    // Apply fitness sharing if enabled
    const adjustedScores = this.config.sharing.enabled
      ? this.applyFitnessSharing(agents, rawScores)
      : rawScores;

    // Build final evaluations
    for (const agent of agents) {
      const rawScore = rawScores.get(agent.id)!;
      const adjustedScore = adjustedScores.get(agent.id)!;
      const paretoInfo = paretoFronts.get(agent.id) ?? this.getDefaultParetoInfo();

      const violations: string[] = [];
      if (this.config.enableConstraints && this.currentSnapshot) {
        for (const constraint of this.config.constraints) {
          if (!constraint.isSatisfied(agent, this.currentSnapshot)) {
            violations.push(constraint.id);
          }
        }
      }

      evaluations.set(agent.id, {
        agentId: agent.id,
        rawScore,
        adjustedScore,
        paretoInfo,
        violations,
        environmentalFactors: this.config.dynamic.enabled
          ? this.calculateEnvironmentalFactors(agent)
          : [],
      });
    }

    // Update fitness history
    for (const [id, evaluation] of evaluations.entries()) {
      if (!this.fitnessHistory.has(id)) {
        this.fitnessHistory.set(id, []);
      }
      this.fitnessHistory.get(id)!.push(evaluation.adjustedScore);

      // Keep only last 100 evaluations
      const history = this.fitnessHistory.get(id)!;
      if (history.length > 100) {
        history.shift();
      }
    }

    return evaluations;
  }

  /**
   * Check if score1 dominates score2 (Pareto dominance)
   */
  isDominated(score1: FitnessScore, score2: FitnessScore): boolean {
    const objectives = ['throughput', 'accuracy', 'efficiency', 'cooperation'] as const;

    let atLeastOneBetter = false;
    let noneWorse = true;

    for (const obj of objectives) {
      if (score1[obj] > score2[obj]) {
        atLeastOneBetter = true;
      }
      if (score1[obj] < score2[obj]) {
        noneWorse = false;
        break;
      }
    }

    return atLeastOneBetter && noneWorse;
  }

  /**
   * Calculate Pareto fronts using non-dominated sorting
   */
  private calculateParetoFronts(agents: MicrobiomeAgent[], scores: FitnessScore[]): Map<string, ParetoFront> {
    const fronts = new Map<string, ParetoFront>();
    const indexed = agents.map((agent, idx) => ({
      score: scores[idx],
      idx,
      id: agent.id,
    }));

    // Initialize domination sets
    const dominationSets = new Map<string, ParetoFront>();
    for (const { id } of indexed) {
      dominationSets.set(id, {
        rank: 0,
        crowdingDistance: 0,
        dominatedCount: 0,
        dominates: new Set(),
        dominatedBy: new Set(),
      });
    }

    // Calculate domination
    for (let i = 0; i < indexed.length; i++) {
      for (let j = 0; j < indexed.length; j++) {
        if (i === j) continue;

        const { score: score1, id: id1 } = indexed[i];
        const { score: score2, id: id2 } = indexed[j];

        if (this.isDominated(score1, score2)) {
          dominationSets.get(id1)!.dominates.add(id2);
          dominationSets.get(id2)!.dominatedBy.add(id1);
        }
      }
    }

    // Assign ranks using non-dominated sorting
    let currentFront = new Set<string>();
    for (const [id, info] of dominationSets.entries()) {
      if (info.dominatedBy.size === 0) {
        currentFront.add(id);
      }
    }

    let rank = 0;
    while (currentFront.size > 0) {
      // Assign current rank
      for (const id of currentFront) {
        dominationSets.get(id)!.rank = rank;
      }

      // Calculate crowding distance for current front
      this.calculateCrowdingDistance(currentFront, indexed);

      // Build next front
      const nextFront = new Set<string>();
      for (const id of currentFront) {
        const info = dominationSets.get(id)!;
        for (const dominatedId of info.dominates) {
          const dominatedInfo = dominationSets.get(dominatedId)!;
          dominatedInfo.dominatedBy.delete(id);

          if (dominatedInfo.dominatedBy.size === 0) {
            nextFront.add(dominatedId);
          }
        }
      }

      currentFront = nextFront;
      rank++;
    }

    // Map to IDs
    for (const { id } of indexed) {
      fronts.set(id, dominationSets.get(id)!);
    }

    return fronts;
  }

  /**
   * Calculate crowding distance for diversity maintenance
   */
  private calculateCrowdingDistance(front: Set<string>, indexed: Array<{ score: FitnessScore; idx: number; id: string }>): void {
    if (front.size <= 2) {
      // Edge cases: infinite distance for boundaries, 0 for single element
      for (const id of front) {
        const info = indexed.find(i => i.id === id);
        if (info) {
          // Would need to reference the domination set, but we're in a simplified context
          // In practice, boundary points get infinite distance
        }
      }
      return;
    }

    const objectives = ['throughput', 'accuracy', 'efficiency', 'cooperation'] as const;

    // Initialize distances
    const distances = new Map<string, number>();
    for (const id of front) {
      distances.set(id, 0);
    }

    // Calculate crowding distance for each objective
    for (const obj of objectives) {
      // Sort front by this objective
      const sorted = Array.from(front)
        .map(id => ({ id, score: indexed.find(i => i.id === id)?.score }))
        .filter(item => item.score !== undefined)
        .sort((a, b) => b.score![obj] - a.score![obj]);

      const min = sorted[sorted.length - 1].score![obj];
      const max = sorted[0].score![obj];
      const range = max - min;

      if (range === 0) continue;

      // Boundary points get infinite distance
      // (we'll use a large number instead)
      const boundaryDistance = Number.MAX_VALUE / 2;
      distances.set(sorted[0].id, boundaryDistance);
      distances.set(sorted[sorted.length - 1].id, boundaryDistance);

      // Intermediate points
      for (let i = 1; i < sorted.length - 1; i++) {
        const current = distances.get(sorted[i].id) ?? 0;
        const nextObj = sorted[i - 1].score![obj];
        const prevObj = sorted[i + 1].score![obj];
        const distance = current + (nextObj - prevObj) / range;
        distances.set(sorted[i].id, distance);
      }
    }
  }

  /**
   * Apply fitness sharing for diversity maintenance
   */
  private applyFitnessSharing(
    agents: MicrobiomeAgent[],
    scores: Map<string, FitnessScore>
  ): Map<string, FitnessScore> {
    const sharedScores = new Map<string, FitnessScore>();

    for (const agent1 of agents) {
      const score1 = scores.get(agent1.id)!;
      let nicheCount = 0;

      // Calculate sharing function
      for (const agent2 of agents) {
        const distance = this.calculateAgentDistance(agent1, agent2);

        if (distance < this.config.sharing.sigma) {
          const sharingValue = 1 - Math.pow(distance / this.config.sharing.sigma, this.config.sharing.alpha);
          nicheCount += sharingValue;
        }
      }

      // Adjust fitness by niche count
      const sharingFactor = nicheCount > 0 ? 1 / nicheCount : 1;

      sharedScores.set(agent1.id, {
        overall: score1.overall * sharingFactor,
        throughput: score1.throughput * sharingFactor,
        accuracy: score1.accuracy * sharingFactor,
        efficiency: score1.efficiency * sharingFactor,
        cooperation: score1.cooperation * sharingFactor,
      });
    }

    return sharedScores;
  }

  /**
   * Calculate distance between two agents for fitness sharing
   */
  private calculateAgentDistance(agent1: MicrobiomeAgent, agent2: MicrobiomeAgent): number {
    // Use feature space distance
    const metabolismDistance =
      Math.abs(agent1.metabolism.efficiency - agent2.metabolism.efficiency);

    const taxonomyDistance = agent1.taxonomy === agent2.taxonomy ? 0 : 1;

    const complexityDistance = Math.abs(agent1.complexity - agent2.complexity);

    // Weighted combination
    return (
      0.4 * metabolismDistance +
      0.4 * taxonomyDistance +
      0.2 * complexityDistance
    );
  }

  /**
   * Apply dynamic fitness based on environment
   */
  private applyDynamicFitness(agent: MicrobiomeAgent, score: FitnessScore): FitnessScore {
    if (!this.currentSnapshot) return score;

    const factors = this.calculateEnvironmentalFactors(agent);
    const sensitivity = this.config.dynamic.environmentSensitivity;

    // Apply seasonal adjustment
    const seasonalAdjustment = 1 + Math.sin(this.seasonalPhase * 2 * Math.PI) * this.config.dynamic.seasonalRate;

    // Apply resource scarcity factor
    const resourceFactor = this.calculateResourceFactor(agent);

    // Combine adjustments
    const adjustment = seasonalAdjustment * resourceFactor;

    return {
      overall: score.overall * (1 + sensitivity * (adjustment - 1)),
      throughput: score.throughput * adjustment,
      accuracy: score.accuracy * adjustment,
      efficiency: score.efficiency * adjustment,
      cooperation: score.cooperation * adjustment,
    };
  }

  /**
   * Calculate environmental factors for an agent
   */
  private calculateEnvironmentalFactors(agent: MicrobiomeAgent): number[] {
    if (!this.currentSnapshot) return [];

    const factors: number[] = [];

    // Population pressure
    const popDynamics = this.currentSnapshot.populations.get(agent.taxonomy);
    if (popDynamics) {
      const pressure = popDynamics.population / popDynamics.carryingCapacity;
      factors.push(pressure);
    }

    // Resource availability
    for (const input of agent.metabolism.inputs) {
      const flow = this.currentSnapshot.resourceFlows.get(input);
      if (flow) {
        const availability = flow.available / flow.capacity;
        factors.push(availability);
      }
    }

    // Colony stability
    const colony = this.currentSnapshot.colonies.find(c => c.members.includes(agent.id));
    if (colony) {
      factors.push(colony.stability);
      factors.push(colony.coEvolutionBonus);
    }

    return factors;
  }

  /**
   * Calculate resource scarcity factor
   */
  private calculateResourceFactor(agent: MicrobiomeAgent): number {
    if (!this.currentSnapshot) return 1;

    let totalAvailability = 0;
    let resourceCount = 0;

    for (const input of agent.metabolism.inputs) {
      const flow = this.currentSnapshot.resourceFlows.get(input);
      if (flow) {
        const availability = flow.available / flow.capacity;
        totalAvailability += availability;
        resourceCount++;
      }
    }

    if (resourceCount === 0) return 1;

    const avgAvailability = totalAvailability / resourceCount;

    // Lower availability reduces fitness more (scarcity penalty)
    const scarcityFactor = 1 - (1 - avgAvailability) * this.config.dynamic.resourceScarcityFactor;

    return Math.max(0.1, scarcityFactor);
  }

  /**
   * Apply constraint penalties
   */
  private applyConstraints(agent: MicrobiomeAgent, score: FitnessScore): FitnessScore {
    if (!this.currentSnapshot || this.config.constraints.length === 0) {
      return score;
    }

    let totalPenalty = 0;

    for (const constraint of this.config.constraints) {
      if (!constraint.isSatisfied(agent, this.currentSnapshot)) {
        totalPenalty += constraint.penalty;
      }
    }

    // Apply penalty (capped at 0.9 reduction)
    const penaltyFactor = Math.max(0.1, 1 - totalPenalty);

    return {
      overall: score.overall * penaltyFactor,
      throughput: score.throughput * penaltyFactor,
      accuracy: score.accuracy * penaltyFactor,
      efficiency: score.efficiency * penaltyFactor,
      cooperation: score.cooperation * penaltyFactor,
    };
  }

  /**
   * Apply weighted combination to fitness score
   */
  private applyWeights(score: FitnessScore): FitnessScore {
    const overall =
      score.throughput * this.config.weights.throughput +
      score.accuracy * this.config.weights.accuracy +
      score.efficiency * this.config.weights.efficiency +
      score.cooperation * this.config.weights.cooperation;

    return {
      overall: Math.min(1, overall),
      throughput: score.throughput,
      accuracy: score.accuracy,
      efficiency: score.efficiency,
      cooperation: score.cooperation,
    };
  }

  /**
   * Get population fitness summary
   */
  getPopulationSummary(evaluations: Map<string, FitnessEvaluation>): PopulationFitnessSummary {
    const scores = Array.from(evaluations.values()).map(e => e.adjustedScore);

    if (scores.length === 0) {
      return {
        bestFitness: {
          overall: 0,
          throughput: 0,
          accuracy: 0,
          efficiency: 0,
          cooperation: 0,
        },
        avgFitness: {
          overall: 0,
          throughput: 0,
          accuracy: 0,
          efficiency: 0,
          cooperation: 0,
        },
        worstFitness: {
          overall: 0,
          throughput: 0,
          accuracy: 0,
          efficiency: 0,
          cooperation: 0,
        },
        fitnessDiversity: 0,
        paretoFronts: new Map(),
        violationRate: 0,
      };
    }

    // Calculate best, average, worst
    const sum = scores.reduce(
      (acc, score) => ({
        overall: acc.overall + score.overall,
        throughput: acc.throughput + score.throughput,
        accuracy: acc.accuracy + score.accuracy,
        efficiency: acc.efficiency + score.efficiency,
        cooperation: acc.cooperation + score.cooperation,
      }),
      { overall: 0, throughput: 0, accuracy: 0, efficiency: 0, cooperation: 0 }
    );

    const avgFitness: FitnessScore = {
      overall: sum.overall / scores.length,
      throughput: sum.throughput / scores.length,
      accuracy: sum.accuracy / scores.length,
      efficiency: sum.efficiency / scores.length,
      cooperation: sum.cooperation / scores.length,
    };

    const sortedByOverall = [...scores].sort((a, b) => b.overall - a.overall);
    const bestFitness = sortedByOverall[0];
    const worstFitness = sortedByOverall[sortedByOverall.length - 1];

    // Calculate fitness diversity (standard deviation of overall)
    const mean = avgFitness.overall;
    const variance = scores.reduce((acc, score) => acc + Math.pow(score.overall - mean, 2), 0) / scores.length;
    const fitnessDiversity = Math.sqrt(variance);

    // Count Pareto front sizes
    const paretoFronts = new Map<number, number>();
    for (const evaluation of evaluations.values()) {
      const rank = evaluation.paretoInfo.rank;
      paretoFronts.set(rank, (paretoFronts.get(rank) ?? 0) + 1);
    }

    // Calculate violation rate
    const totalViolations = Array.from(evaluations.values()).reduce(
      (acc, e) => acc + e.violations.length,
      0
    );
    const violationRate = totalViolations / evaluations.size;

    return {
      bestFitness,
      avgFitness,
      worstFitness,
      fitnessDiversity,
      paretoFronts,
      violationRate,
    };
  }

  /**
   * Update ecosystem snapshot for dynamic fitness
   */
  updateSnapshot(snapshot: EcosystemSnapshot): void {
    this.currentSnapshot = snapshot;

    // Update seasonal phase
    this.seasonalPhase = (this.seasonalPhase + 0.01) % 1;
  }

  /**
   * Get configuration
   */
  getConfig(): FitnessEvaluatorConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<FitnessEvaluatorConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  /**
   * Reset fitness history
   */
  resetHistory(): void {
    this.fitnessHistory.clear();
  }

  /**
   * Get fitness history for an agent
   */
  getHistory(agentId: string): FitnessScore[] {
    return this.fitnessHistory.get(agentId) ?? [];
  }

  /**
   * Get default Pareto info
   */
  private getDefaultParetoInfo(): ParetoFront {
    return {
      rank: 0,
      crowdingDistance: 0,
      dominatedCount: 0,
      dominates: new Set(),
      dominatedBy: new Set(),
    };
  }
}

/**
 * Create a fitness evaluator with default configuration
 */
export function createFitnessEvaluator(
  config?: Partial<FitnessEvaluatorConfig>
): FitnessEvaluator {
  return new FitnessEvaluator(config);
}

/**
 * Built-in constraints
 */
export const BuiltinConstraints = {
  /**
   * Size constraint - agent must not exceed maximum size
   */
  maxSizeConstraint: (maxSize: number): Constraint => ({
    id: `max_size_${maxSize}`,
    name: 'Maximum Size',
    isSatisfied: (agent: MicrobiomeAgent) => agent.size <= maxSize,
    penalty: 0.5,
    description: `Agent size must not exceed ${maxSize} bytes`,
  }),

  /**
   * Resource constraint - agent must have sufficient resources
   */
  resourceConstraint: (minResources: number): Constraint => ({
    id: `min_resources_${minResources}`,
    name: 'Minimum Resources',
    isSatisfied: (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot) => {
      let totalAvailable = 0;
      for (const input of agent.metabolism.inputs) {
        const flow = snapshot.resourceFlows.get(input);
        if (flow) {
          totalAvailable += flow.available;
        }
      }
      return totalAvailable >= minResources;
    },
    penalty: 0.3,
    description: `Agent must have at least ${minResources} resources available`,
  }),

  /**
   * Complexity constraint - agent must not exceed complexity limit
   */
  complexityConstraint: (maxComplexity: number): Constraint => ({
    id: `max_complexity_${maxComplexity}`,
    name: 'Maximum Complexity',
    isSatisfied: (agent: MicrobiomeAgent) => agent.complexity <= maxComplexity,
    penalty: 0.2,
    description: `Agent complexity must not exceed ${maxComplexity}`,
  }),

  /**
   * Efficiency constraint - agent must meet minimum efficiency
   */
  efficiencyConstraint: (minEfficiency: number): Constraint => ({
    id: `min_efficiency_${minEfficiency}`,
    name: 'Minimum Efficiency',
    isSatisfied: (agent: MicrobiomeAgent) => agent.metabolism.efficiency >= minEfficiency,
    penalty: 0.4,
    description: `Agent metabolic efficiency must be at least ${minEfficiency}`,
  }),

  /**
   * Age constraint - agent must not exceed maximum age
   */
  maxAgeConstraint: (maxAge: number): Constraint => ({
    id: `max_age_${maxAge}`,
    name: 'Maximum Age',
    isSatisfied: (agent: MicrobiomeAgent) => agent.lifecycle.age <= maxAge,
    penalty: 0.6,
    description: `Agent age must not exceed ${maxAge}ms`,
  }),
};
