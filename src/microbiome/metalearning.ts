/**
 * POLLN Microbiome - Meta-Learning Engine
 *
 * Phase 7: Emergent Intelligence - Milestone 1
 * Implements meta-learning: learning how to learn efficiently.
 *
 * Core capabilities:
 * - Algorithm selection: Choose best learning strategy for context
 * - Learning rate adaptation: Adjust rates based on performance
 * - Transfer learning: Apply knowledge across domains
 * - Strategy evolution: Evolve learning strategies over time
 *
 * @module microbiome/metalearning
 */

import { EventEmitter } from 'events';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  FitnessScore,
  EcosystemSnapshot,
  ResourceType,
} from './types.js';
import { FitnessEvaluator } from './fitness.js';
import { GeneticOperators } from './genetic.js';
import { EvolutionEngine } from './evolution.js';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Learning algorithms available in the system
 */
export enum LearningAlgorithm {
  /** Hebbian learning - neurons that fire together, wire together */
  HEBBIAN = 'hebbian',
  /** Evolutionary optimization - genetic algorithms */
  EVOLUTIONARY = 'evolutionary',
  /** Reinforcement learning - reward-based optimization */
  REINFORCEMENT = 'reinforcement',
  /** Imitation learning - learn from demonstrations */
  IMITATION = 'imitation',
  /** Transfer learning - apply knowledge from other domains */
  TRANSFER = 'transfer',
  /** Meta-learning - learn how to learn */
  META = 'meta',
  /** Ensemble - combine multiple algorithms */
  ENSEMBLE = 'ensemble',
}

/**
 * Context stability assessment
 */
export enum ContextStability {
  /** Highly stable - patterns are consistent */
  STABLE = 'stable',
  /** Moderately stable - some variation */
  MODERATE = 'moderate',
  /** Highly volatile - rapid change */
  VOLATILE = 'volatile',
}

/**
 * Domain knowledge level
 */
export enum DomainKnowledge {
  /** Well-understood domain with proven strategies */
  KNOWN = 'known',
  /** Partially understood with some successful strategies */
  FAMILIAR = 'familiar',
  /** Novel domain with little prior knowledge */
  NOVEL = 'novel',
}

/**
 * Task complexity assessment
 */
export enum TaskComplexity {
  /** Simple task with clear solution */
  SIMPLE = 'simple',
  /** Moderate task with some ambiguity */
  MODERATE = 'moderate',
  /** Complex task with high ambiguity */
  COMPLEX = 'complex',
}

/**
 * Learning strategy configuration
 */
export interface LearningStrategy {
  /** Strategy ID */
  id: string;
  /** Primary learning algorithm */
  algorithm: LearningAlgorithm;
  /** Learning rate (0-1) */
  learningRate: number;
  /** Exploration rate (0-1) */
  explorationRate: number;
  /** Batch size for updates */
  batchSize: number;
  /** Update frequency (ms) */
  updateFrequency: number;
  /** Regularization strength (0-1) */
  regularization: number;
  /** Memory discount factor (0-1) */
  memoryDiscount: number;
  /** Risk tolerance (0-1) */
  riskTolerance: number;
  /** Strategy creation timestamp */
  createdAt: number;
  /** Parent strategy IDs (for evolution) */
  parentIds?: string[];
  /** Generation number */
  generation: number;
}

/**
 * Learning outcome for meta-reward calculation
 */
export interface LearningOutcome {
  /** Agent or colony ID */
  entityId: string;
  /** Strategy used */
  strategy: LearningStrategy;
  /** Context at time of learning */
  context: LearningContext;
  /** Fitness before learning */
  fitnessBefore: FitnessScore;
  /** Fitness after learning */
  fitnessAfter: FitnessScore;
  /** Time taken to learn (ms) */
  learningTime: number;
  /** Resources consumed */
  resourcesConsumed: Map<ResourceType, number>;
  /** Timestamp */
  timestamp: number;
}

/**
 * Learning context for strategy selection
 */
export interface LearningContext {
  /** Context stability */
  stability: ContextStability;
  /** Domain knowledge level */
  domainKnowledge: DomainKnowledge;
  /** Task complexity */
  taskComplexity: TaskComplexity;
  /** Available resources */
  availableResources: Map<ResourceType, number>;
  /** Time pressure (0-1, higher = more pressure) */
  timePressure: number;
  /** Error tolerance (0-1, higher = more tolerance) */
  errorTolerance: number;
  /** Colony size (if applicable) */
  colonySize?: number;
  /** Number of agents in context */
  agentCount: number;
  /** Recent performance trend (-1 to 1) */
  performanceTrend: number;
}

/**
 * Transfer learning source
 */
export interface TransferSource {
  /** Source domain identifier */
  domain: string;
  /** Source agent/colony ID */
  sourceId: string;
  /** Reusable patterns/knowledge */
  knowledge: Map<string, number>;
  /** Transfer confidence (0-1) */
  confidence: number;
  /** Domain similarity to target (0-1) */
  similarity: number;
}

/**
 * Transfer learning result
 */
export interface TransferResult {
  /** Success of transfer (0-1) */
  success: number;
  /** Knowledge transferred */
  transferredKnowledge: Map<string, number>;
  /** Adaptation required (0-1) */
  adaptationRequired: number;
  /** Performance improvement (0-1) */
  performanceImprovement: number;
}

/**
 * Meta-reward components
 */
export interface MetaRewardComponents {
  /** Performance improvement reward */
  performance: number;
  /** Efficiency reward (resources/time) */
  efficiency: number;
  /** Adaptability reward (handled novelty) */
  adaptability: number;
  /** Generalization reward (transfer success) */
  generalization: number;
  /** Safety penalty (if any) */
  safety: number;
  /** Total reward */
  total: number;
}

/**
 * Meta-learning configuration
 */
export interface MetaLearningConfig {
  /** Enable/disable meta-learning */
  enabled: boolean;
  /** Strategy population size */
  populationSize: number;
  /** Strategy evolution interval (ms) */
  evolutionInterval: number;
  /** Learning rate adaptation rate */
  adaptationRate: number;
  /** Transfer learning threshold */
  transferThreshold: number;
  /** Domain similarity threshold */
  similarityThreshold: number;
  /** Meta-reward discount factor */
  metaDiscount: number;
  /** Exploration vs exploitation (0-1) */
  explorationFactor: number;
  /** Safety constraint weight */
  safetyWeight: number;
  /** Minimum learning rate */
  minLearningRate: number;
  /** Maximum learning rate */
  maxLearningRate: number;
  /** Memory capacity (number of outcomes to remember) */
  memoryCapacity: number;
}

/**
 * Meta-learning statistics
 */
export interface MetaLearningStats {
  /** Total strategies evaluated */
  strategiesEvaluated: number;
  /** Current strategy population */
  strategyPopulation: number;
  /** Average meta-reward */
  avgMetaReward: number;
  /** Best strategy ID */
  bestStrategyId: string | null;
  /** Best meta-reward */
  bestMetaReward: number;
  /** Transfer learning success rate */
  transferSuccessRate: number;
  /** Learning rate adaptations */
  adaptationsCount: number;
  /** Last evolution time */
  lastEvolution: number;
}

// ============================================================================
// META-LEARNING ENGINE
// ============================================================================

/**
 * MetaLearningEngine - Learn how to learn efficiently
 *
 * This engine implements meta-learning by:
 * 1. Selecting optimal learning strategies for given contexts
 * 2. Adapting learning rates based on performance
 * 3. Transferring knowledge across domains
 * 4. Evolving strategies through meta-reward optimization
 *
 * Ethical considerations built-in:
 * - Safety constraints always enforced
 * - Transparent decision-making
 * - Accountable strategy evolution
 * - Beneficence-focused reward function
 */
export class MetaLearningEngine extends EventEmitter {
  /** Configuration */
  private config: MetaLearningConfig;

  /** Fitness evaluator for outcome measurement */
  private fitnessEvaluator: FitnessEvaluator;

  /** Evolution engine for strategy evolution */
  private evolutionEngine?: EvolutionEngine;

  /** Current strategy population */
  private strategies: Map<string, LearningStrategy>;

  /** Learning outcome history */
  private outcomeHistory: LearningOutcome[];

  /** Per-entity learning rates */
  private learningRates: Map<string, number>;

  /** Domain knowledge registry */
  private domainKnowledge: Map<string, DomainKnowledge>;

  /** Transfer source registry */
  private transferSources: TransferSource[];

  /** Meta-reward history */
  private metaRewardHistory: Map<string, MetaRewardComponents[]>;

  /** Statistics */
  private stats: MetaLearningStats;

  /** Last evolution time */
  private lastEvolutionTime: number;

  constructor(
    fitnessEvaluator: FitnessEvaluator,
    evolutionEngine?: EvolutionEngine,
    config?: Partial<MetaLearningConfig>
  ) {
    super();

    this.fitnessEvaluator = fitnessEvaluator;
    this.evolutionEngine = evolutionEngine;
    this.strategies = new Map();
    this.outcomeHistory = [];
    this.learningRates = new Map();
    this.domainKnowledge = new Map();
    this.transferSources = [];
    this.metaRewardHistory = new Map();

    this.config = {
      enabled: true,
      populationSize: 20,
      evolutionInterval: 300000, // 5 minutes
      adaptationRate: 0.1,
      transferThreshold: 0.6,
      similarityThreshold: 0.7,
      metaDiscount: 0.95,
      explorationFactor: 0.3,
      safetyWeight: 0.2,
      minLearningRate: 0.001,
      maxLearningRate: 0.5,
      memoryCapacity: 1000,
      ...config,
    };

    this.stats = {
      strategiesEvaluated: 0,
      strategyPopulation: 0,
      avgMetaReward: 0,
      bestStrategyId: null,
      bestMetaReward: -Infinity,
      transferSuccessRate: 0,
      adaptationsCount: 0,
      lastEvolution: Date.now(),
    };

    this.lastEvolutionTime = Date.now();

    // Initialize with default strategies
    this.initializeDefaultStrategies();
  }

  /**
   * Initialize default strategy population
   */
  private initializeDefaultStrategies(): void {
    const defaultStrategies: Omit<LearningStrategy, 'id' | 'createdAt' | 'generation'>[] = [
      {
        algorithm: LearningAlgorithm.HEBBIAN,
        learningRate: 0.1,
        explorationRate: 0.2,
        batchSize: 32,
        updateFrequency: 1000,
        regularization: 0.01,
        memoryDiscount: 0.99,
        riskTolerance: 0.5,
      },
      {
        algorithm: LearningAlgorithm.EVOLUTIONARY,
        learningRate: 0.05,
        explorationRate: 0.5,
        batchSize: 50,
        updateFrequency: 5000,
        regularization: 0.001,
        memoryDiscount: 0.95,
        riskTolerance: 0.7,
      },
      {
        algorithm: LearningAlgorithm.REINFORCEMENT,
        learningRate: 0.15,
        explorationRate: 0.3,
        batchSize: 64,
        updateFrequency: 2000,
        regularization: 0.02,
        memoryDiscount: 0.98,
        riskTolerance: 0.4,
      },
      {
        algorithm: LearningAlgorithm.ENSEMBLE,
        learningRate: 0.08,
        explorationRate: 0.25,
        batchSize: 40,
        updateFrequency: 1500,
        regularization: 0.015,
        memoryDiscount: 0.97,
        riskTolerance: 0.6,
      },
    ];

    for (const strategy of defaultStrategies) {
      this.createStrategy(strategy);
    }
  }

  /**
   * Create a new learning strategy
   */
  private createStrategy(
    base: Omit<LearningStrategy, 'id' | 'createdAt' | 'generation'>,
    parentIds?: string[]
  ): LearningStrategy {
    const generation = parentIds && parentIds.length > 0
      ? Math.max(...parentIds.map(id => this.strategies.get(id)?.generation ?? 0)) + 1
      : 0;

    const strategy: LearningStrategy = {
      ...base,
      id: `strategy-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now(),
      parentIds,
      generation,
    };

    this.strategies.set(strategy.id, strategy);
    this.stats.strategyPopulation = this.strategies.size;

    return strategy;
  }

  // ==========================================================================
  // LEARNING STRATEGY SELECTION
  // ==========================================================================

  /**
   * Select optimal learning strategy for given context
   *
   * Selection logic:
   * - Stable environment → Low learning rate (don't overfit)
   * - Novel situation → High learning rate (adapt quickly)
   * - Known domain → Exploit best algorithm (use proven methods)
   * - Unknown domain → High exploration (find what works)
   */
  public selectStrategy(context: LearningContext): LearningStrategy {
    if (!this.config.enabled) {
      // Return default strategy if meta-learning disabled
      return this.strategies.values().next().value!;
    }

    const now = Date.now();

    // Check if we should evolve strategies
    if (now - this.lastEvolutionTime >= this.config.evolutionInterval) {
      this.evolveStrategies();
      this.lastEvolutionTime = now;
    }

    // Score each strategy based on context
    const scoredStrategies: Array<{ strategy: LearningStrategy; score: number }> = [];

    for (const strategy of this.strategies.values()) {
      const score = this.scoreStrategyForContext(strategy, context);
      scoredStrategies.push({ strategy, score });
    }

    // Sort by score
    scoredStrategies.sort((a, b) => b.score - a.score);

    // Apply exploration (sometimes pick suboptimal strategy)
    if (Math.random() < this.config.explorationFactor) {
      // Pick from top 5 with bias toward best
      const topN = Math.min(5, scoredStrategies.length);
      const candidates = scoredStrategies.slice(0, topN);

      // Weighted random selection
      const totalScore = candidates.reduce((sum, c) => sum + c.score, 0);
      let random = Math.random() * totalScore;

      for (const candidate of candidates) {
        random -= candidate.score;
        if (random <= 0) {
          this.emit('strategy_selected', {
            strategy: candidate.strategy,
            context,
            exploration: true,
          });
          return candidate.strategy;
        }
      }
    }

    // Return best strategy
    const best = scoredStrategies[0].strategy;
    this.emit('strategy_selected', {
      strategy: best,
      context,
      exploration: false,
    });

    return best;
  }

  /**
   * Score a strategy for a given context
   */
  private scoreStrategyForContext(
    strategy: LearningStrategy,
    context: LearningContext
  ): number {
    let score = 0;

    // Stability factor
    switch (context.stability) {
      case ContextStability.STABLE:
        // Prefer lower learning rates to avoid overfitting
        score += (1 - strategy.learningRate) * 0.3;
        break;
      case ContextStability.MODERATE:
        // Balanced learning rate
        const optimalRate = 0.1;
        score += (1 - Math.abs(strategy.learningRate - optimalRate)) * 0.2;
        break;
      case ContextStability.VOLATILE:
        // Prefer higher learning rates for quick adaptation
        score += strategy.learningRate * 0.3;
        break;
    }

    // Domain knowledge factor
    switch (context.domainKnowledge) {
      case DomainKnowledge.KNOWN:
        // Prefer exploitation (low exploration, proven algorithms)
        score += (1 - strategy.explorationRate) * 0.25;
        if (strategy.algorithm === LearningAlgorithm.HEBBIAN ||
            strategy.algorithm === LearningAlgorithm.REINFORCEMENT) {
          score += 0.15;
        }
        break;
      case DomainKnowledge.FAMILIAR:
        // Balanced approach
        score += 0.2;
        break;
      case DomainKnowledge.NOVEL:
        // Prefer exploration and flexible algorithms
        score += strategy.explorationRate * 0.25;
        if (strategy.algorithm === LearningAlgorithm.EVOLUTIONARY ||
            strategy.algorithm === LearningAlgorithm.META) {
          score += 0.15;
        }
        break;
    }

    // Task complexity factor
    switch (context.taskComplexity) {
      case TaskComplexity.SIMPLE:
        // Simple tasks benefit from faster learning
        score += strategy.learningRate * 0.15;
        break;
      case TaskComplexity.MODERATE:
        score += 0.1;
        break;
      case TaskComplexity.COMPLEX:
        // Complex tasks need slower, more careful learning
        score += (1 - strategy.learningRate) * 0.15;
        if (strategy.algorithm === LearningAlgorithm.EVOLUTIONARY ||
            strategy.algorithm === LearningAlgorithm.ENSEMBLE) {
          score += 0.1;
        }
        break;
    }

    // Time pressure factor
    if (context.timePressure > 0.7) {
      // High time pressure: prefer faster algorithms
      score += (1 - strategy.updateFrequency / 10000) * 0.1;
    }

    // Error tolerance factor
    if (context.errorTolerance < 0.3) {
      // Low error tolerance: prefer conservative strategies
      score += (1 - strategy.riskTolerance) * 0.1;
    }

    // Colony size factor
    if (context.colonySize && context.colonySize > 10) {
      // Large colonies benefit from regularization
      score += strategy.regularization * 0.1;
    }

    // Performance trend factor
    if (context.performanceTrend < -0.3) {
      // Declining performance: prefer higher exploration
      score += strategy.explorationRate * 0.15;
    }

    return Math.max(0, Math.min(1, score));
  }

  // ==========================================================================
  // LEARNING RATE ADAPTATION
  // ==========================================================================

  /**
   * Adapt learning rates based on performance
   *
   * Per-agent adaptation:
   * - Improving performance → Decrease learning rate (consolidate)
   * - Declining performance → Increase learning rate (explore)
   * - Stable performance → Maintain current rate
   */
  public adaptLearningRates(performance: Map<string, number>): void {
    if (!this.config.enabled) return;

    const adaptations: Array<{ entityId: string; oldRate: number; newRate: number }> = [];

    for (const [entityId, perf] of performance) {
      const currentRate = this.learningRates.get(entityId) ?? 0.1;

      // Calculate adjustment based on performance
      let adjustment = 0;

      if (perf > 0.7) {
        // Excellent performance: consolidate (decrease rate)
        adjustment = -this.config.adaptationRate * currentRate;
      } else if (perf < 0.3) {
        // Poor performance: explore more (increase rate)
        adjustment = this.config.adaptationRate * (1 - currentRate);
      }
      // Moderate performance: maintain current rate

      // Apply adjustment
      let newRate = currentRate + adjustment;

      // Clamp to valid range
      newRate = Math.max(this.config.minLearningRate,
                        Math.min(this.config.maxLearningRate, newRate));

      if (newRate !== currentRate) {
        this.learningRates.set(entityId, newRate);
        adaptations.push({ entityId, oldRate: currentRate, newRate });
        this.stats.adaptationsCount++;
      }
    }

    if (adaptations.length > 0) {
      this.emit('learning_rates_adapted', { adaptations });
    }
  }

  /**
   * Get learning rate for an entity
   */
  public getLearningRate(entityId: string): number {
    return this.learningRates.get(entityId) ?? 0.1;
  }

  /**
   * Set learning rate for an entity
   */
  public setLearningRate(entityId: string, rate: number): void {
    const clampedRate = Math.max(this.config.minLearningRate,
                                 Math.min(this.config.maxLearningRate, rate));
    this.learningRates.set(entityId, clampedRate);
  }

  // ==========================================================================
  // TRANSFER LEARNING
  // ==========================================================================

  /**
   * Transfer learning from source domain to target
   *
   * Transfer logic:
   * 1. Find similar domains in registry
   * 2. Extract reusable patterns
   * 3. Adapt patterns to target domain
   * 4. Validate transfer effectiveness
   */
  public transferLearning(
    sourceDomain: string,
    targetDomain: string,
    targetContext: LearningContext
  ): TransferResult {
    if (!this.config.enabled) {
      return {
        success: 0,
        transferredKnowledge: new Map(),
        adaptationRequired: 0,
        performanceImprovement: 0,
      };
    }

    // Find transfer sources from similar domains
    const similarSources = this.transferSources.filter(s => {
      const similarity = this.computeDomainSimilarity(sourceDomain, s.domain);
      return similarity >= this.config.similarityThreshold;
    });

    if (similarSources.length === 0) {
      // No similar domains found
      return {
        success: 0,
        transferredKnowledge: new Map(),
        adaptationRequired: 1,
        performanceImprovement: 0,
      };
    }

    // Select best source
    const bestSource = similarSources.reduce((best, current) =>
      current.confidence > best.confidence ? current : best
    );

    // Extract and adapt knowledge
    const transferredKnowledge = this.adaptKnowledge(
      bestSource.knowledge,
      targetContext
    );

    // Calculate adaptation required
    const adaptationRequired = 1 - bestSource.similarity;

    // Estimate performance improvement
    const performanceImprovement = bestSource.confidence * bestSource.similarity;

    // Register successful transfer for future use
    if (performanceImprovement > this.config.transferThreshold) {
      this.registerTransferSource({
        domain: targetDomain,
        sourceId: bestSource.sourceId,
        knowledge: transferredKnowledge,
        confidence: performanceImprovement,
        similarity: bestSource.similarity * 0.9, // Slightly lower for derived
      });
    }

    const result: TransferResult = {
      success: performanceImprovement,
      transferredKnowledge,
      adaptationRequired,
      performanceImprovement,
    };

    this.emit('transfer_learning', {
      sourceDomain,
      targetDomain,
      result,
    });

    return result;
  }

  /**
   * Compute domain similarity
   */
  private computeDomainSimilarity(domain1: string, domain2: string): number {
    // Simple string similarity (can be enhanced with semantic similarity)
    if (domain1 === domain2) return 1;

    const words1 = domain1.toLowerCase().split(/[^a-z0-9]+/);
    const words2 = domain2.toLowerCase().split(/[^a-z0-9]+/);

    const intersection = words1.filter(w => words2.includes(w));
    const union = new Set([...words1, ...words2]);

    return union.size > 0 ? intersection.length / union.size : 0;
  }

  /**
   * Adapt knowledge to target context
   */
  private adaptKnowledge(
    sourceKnowledge: Map<string, number>,
    targetContext: LearningContext
  ): Map<string, number> {
    const adapted = new Map<string, number>();

    for (const [key, value] of sourceKnowledge) {
      // Adjust based on context
      let adaptedValue = value;

      // Scale by task complexity
      if (targetContext.taskComplexity === TaskComplexity.COMPLEX) {
        adaptedValue *= 0.8; // More conservative for complex tasks
      } else if (targetContext.taskComplexity === TaskComplexity.SIMPLE) {
        adaptedValue *= 1.1; // More aggressive for simple tasks
      }

      // Scale by domain knowledge
      if (targetContext.domainKnowledge === DomainKnowledge.NOVEL) {
        adaptedValue *= 0.7; // More cautious for novel domains
      }

      adapted.set(key, adaptedValue);
    }

    return adapted;
  }

  /**
   * Register a transfer source
   */
  public registerTransferSource(source: TransferSource): void {
    // Check if similar source already exists
    const existing = this.transferSources.find(s =>
      s.domain === source.domain && s.sourceId === source.sourceId
    );

    if (existing) {
      // Update existing source
      existing.confidence = Math.max(existing.confidence, source.confidence);
      existing.knowledge = source.knowledge;
    } else {
      // Add new source
      this.transferSources.push(source);
    }

    // Limit registry size
    if (this.transferSources.length > 100) {
      this.transferSources.shift();
    }
  }

  // ==========================================================================
  // STRATEGY EVOLUTION
  // ==========================================================================

  /**
   * Evolve learning strategies based on meta-reward
   *
   * Evolution process:
   * 1. Evaluate all strategies by their meta-reward
   * 2. Select top performers
   * 3. Create new strategies through crossover
   * 4. Apply mutations for exploration
   * 5. Replace worst performers
   */
  public evolveStrategies(): void {
    if (!this.config.enabled) return;
    if (this.strategies.size < 4) return; // Need minimum population

    // Calculate meta-rewards for all strategies
    const strategyRewards = new Map<string, number>();

    for (const [strategyId, rewards] of this.metaRewardHistory) {
      const avgReward = rewards.reduce((sum, r) => sum + r.total, 0) / rewards.length;
      strategyRewards.set(strategyId, avgReward);
    }

    // Sort strategies by reward
    const sortedStrategies = Array.from(this.strategies.entries())
      .sort((a, b) => {
        const rewardA = strategyRewards.get(a[0]) ?? 0;
        const rewardB = strategyRewards.get(b[0]) ?? 0;
        return rewardB - rewardA;
      });

    // Selection: Keep top 50%
    const keepCount = Math.max(2, Math.floor(sortedStrategies.length / 2));
    const survivors = sortedStrategies.slice(0, keepCount);

    // Crossover: Create new strategies from parents
    const offspring: Omit<LearningStrategy, 'id' | 'createdAt' | 'generation'>[] = [];

    for (let i = 0; i < survivors.length - 1; i++) {
      const parent1 = survivors[i][1];
      const parent2 = survivors[i + 1][1];

      const child = this.crossoverStrategies(parent1, parent2);
      offspring.push(child);
    }

    // Mutation: Apply random mutations
    for (const child of offspring) {
      this.mutateStrategy(child);
    }

    // Create new strategies
    for (const child of offspring) {
      const parentIds = [survivors[Math.floor(Math.random() * survivors.length)][0]];
      this.createStrategy(child, parentIds);
    }

    // Replace worst performers
    const replaceCount = offspring.length;
    for (let i = 0; i < replaceCount; i++) {
      const worstId = sortedStrategies[sortedStrategies.length - 1 - i][0];
      this.strategies.delete(worstId);
      this.metaRewardHistory.delete(worstId);
    }

    this.stats.strategyPopulation = this.strategies.size;
    this.stats.lastEvolution = Date.now();

    this.emit('strategies_evolved', {
      survivors: survivors.map(s => s[0]),
      offspringCount: offspring.length,
    });
  }

  /**
   * Crossover two learning strategies
   */
  private crossoverStrategies(
    parent1: LearningStrategy,
    parent2: LearningStrategy
  ): Omit<LearningStrategy, 'id' | 'createdAt' | 'generation'> {
    // Uniform crossover: randomly select from each parent
    const algorithm = Math.random() < 0.5 ? parent1.algorithm : parent2.algorithm;

    // Blend numerical parameters (arithmetic crossover)
    const blend = (v1: number, v2: number, alpha = 0.5): number => {
      return alpha * v1 + (1 - alpha) * v2;
    };

    const alpha = 0.3 + Math.random() * 0.4; // Random blend factor

    return {
      algorithm,
      learningRate: blend(parent1.learningRate, parent2.learningRate, alpha),
      explorationRate: blend(parent1.explorationRate, parent2.explorationRate, alpha),
      batchSize: Math.round(blend(parent1.batchSize, parent2.batchSize, alpha)),
      updateFrequency: Math.round(blend(parent1.updateFrequency, parent2.updateFrequency, alpha)),
      regularization: blend(parent1.regularization, parent2.regularization, alpha),
      memoryDiscount: blend(parent1.memoryDiscount, parent2.memoryDiscount, alpha),
      riskTolerance: blend(parent1.riskTolerance, parent2.riskTolerance, alpha),
    };
  }

  /**
   * Mutate a learning strategy
   */
  private mutateStrategy(strategy: Omit<LearningStrategy, 'id' | 'createdAt' | 'generation'>): void {
    const mutationRate = 0.2; // 20% chance to mutate each parameter

    // Possibly mutate algorithm
    if (Math.random() < mutationRate) {
      const algorithms = Object.values(LearningAlgorithm);
      strategy.algorithm = algorithms[Math.floor(Math.random() * algorithms.length)];
    }

    // Mutate numerical parameters (Gaussian mutation)
    const gaussianMutation = (value: number, min: number, max: number): number => {
      if (Math.random() >= mutationRate) return value;

      const sigma = (max - min) * 0.1;
      const mutated = value + this.randomGaussian() * sigma;
      return Math.max(min, Math.min(max, mutated));
    };

    strategy.learningRate = gaussianMutation(
      strategy.learningRate,
      this.config.minLearningRate,
      this.config.maxLearningRate
    );

    strategy.explorationRate = gaussianMutation(strategy.explorationRate, 0, 1);
    strategy.regularization = gaussianMutation(strategy.regularization, 0, 0.1);
    strategy.memoryDiscount = gaussianMutation(strategy.memoryDiscount, 0.9, 0.999);
    strategy.riskTolerance = gaussianMutation(strategy.riskTolerance, 0, 1);

    // Mutate discrete parameters
    if (Math.random() < mutationRate) {
      strategy.batchSize = Math.max(10, strategy.batchSize + Math.floor(this.randomGaussian() * 10));
    }

    if (Math.random() < mutationRate) {
      strategy.updateFrequency = Math.max(100, strategy.updateFrequency + Math.floor(this.randomGaussian() * 500));
    }
  }

  /**
   * Generate random Gaussian (normal) value
   */
  private randomGaussian(): number {
    let u = 0, v = 0;
    while (u === 0) u = Math.random();
    while (v === 0) v = Math.random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  }

  // ==========================================================================
  // META-REWARD CALCULATION
  // ==========================================================================

  /**
   * Calculate meta-reward for a learning outcome
   *
   * Reward components:
   * - Performance: Did the strategy improve fitness?
   * - Efficiency: Was learning fast and resource-efficient?
   * - Adaptability: Did it handle novelty well?
   * - Generalization: Can the knowledge transfer?
   * - Safety: Were safety constraints maintained?
   */
  public calculateMetaReward(outcome: LearningOutcome): MetaRewardComponents {
    // Performance component
    const fitnessDelta = this.calculateFitnessDelta(
      outcome.fitnessBefore,
      outcome.fitnessAfter
    );
    const performance = Math.max(-1, Math.min(1, fitnessDelta));

    // Efficiency component
    const timeScore = 1 / (1 + outcome.learningTime / 10000); // Normalize to 0-1
    const resourceScore = this.calculateResourceEfficiency(outcome.resourcesConsumed);
    const efficiency = (timeScore + resourceScore) / 2;

    // Adaptability component
    const adaptability = outcome.context.domainKnowledge === DomainKnowledge.NOVEL
      ? performance * 1.5 // Bonus for handling novelty
      : performance;

    // Generalization component
    const generalization = outcome.strategy.algorithm === LearningAlgorithm.TRANSFER
      ? performance * 1.2 // Bonus for successful transfer
      : 0;

    // Safety component (penalty for violations)
    const safety = this.calculateSafetyScore(outcome);

    // Weight and combine
    const weights = {
      performance: 0.4,
      efficiency: 0.2,
      adaptability: 0.2,
      generalization: 0.1,
      safety: this.config.safetyWeight,
    };

    const total =
      performance * weights.performance +
      efficiency * weights.efficiency +
      adaptability * weights.adaptability +
      generalization * weights.generalization +
      safety * weights.safety;

    const components: MetaRewardComponents = {
      performance,
      efficiency,
      adaptability,
      generalization,
      safety,
      total,
    };

    // Store in history
    const history = this.metaRewardHistory.get(outcome.strategy.id) ?? [];
    history.push(components);

    // Limit history size
    if (history.length > 100) {
      history.shift();
    }

    this.metaRewardHistory.set(outcome.strategy.id, history);

    // Update statistics
    this.updateMetaRewardStats(components);

    return components;
  }

  /**
   * Calculate fitness delta
   */
  private calculateFitnessDelta(before: FitnessScore, after: FitnessScore): number {
    // Overall improvement
    const overallDelta = after.overall - before.overall;

    // Consider individual components
    const componentDelta =
      (after.throughput - before.throughput) * 0.25 +
      (after.accuracy - before.accuracy) * 0.35 +
      (after.efficiency - before.efficiency) * 0.25 +
      (after.cooperation - before.cooperation) * 0.15;

    // Weighted combination
    return overallDelta * 0.6 + componentDelta * 0.4;
  }

  /**
   * Calculate resource efficiency
   */
  private calculateResourceEfficiency(resources: Map<ResourceType, number>): number {
    // Lower consumption = higher efficiency
    let totalConsumption = 0;
    for (const amount of resources.values()) {
      totalConsumption += amount;
    }

    // Normalize to 0-1 (assuming reasonable max consumption)
    const maxConsumption = 1000;
    return 1 - Math.min(1, totalConsumption / maxConsumption);
  }

  /**
   * Calculate safety score
   */
  private calculateSafetyScore(outcome: LearningOutcome): number {
    // Check for safety violations
    // This is a placeholder - actual safety checks would be more sophisticated
    let score = 1;

    // Penalize excessive resource consumption
    let totalConsumption = 0;
    for (const amount of outcome.resourcesConsumed.values()) {
      totalConsumption += amount;
    }
    if (totalConsumption > 500) {
      score -= 0.3;
    }

    // Penalize high risk tolerance with low error tolerance
    if (outcome.strategy.riskTolerance > 0.7 && outcome.context.errorTolerance < 0.3) {
      score -= 0.5;
    }

    return Math.max(0, score);
  }

  /**
   * Update meta-reward statistics
   */
  private updateMetaRewardStats(components: MetaRewardComponents): void {
    this.stats.strategiesEvaluated++;

    // Update best
    if (components.total > this.stats.bestMetaReward) {
      this.stats.bestMetaReward = components.total;
    }

    // Update average
    const allRewards: number[] = [];
    for (const rewards of this.metaRewardHistory.values()) {
      for (const r of rewards) {
        allRewards.push(r.total);
      }
    }

    if (allRewards.length > 0) {
      this.stats.avgMetaReward = allRewards.reduce((a, b) => a + b, 0) / allRewards.length;
    }

    // Update transfer success rate
    const transferAttempts = Array.from(this.metaRewardHistory.values())
      .filter(rewards => rewards.some(r => r.generalization > 0)).length;
    this.stats.transferSuccessRate = transferAttempts / Math.max(1, this.stats.strategiesEvaluated);
  }

  // ==========================================================================
  // CONTEXT ASSESSMENT
  // ==========================================================================

  /**
   * Assess learning context from ecosystem state
   */
  public assessContext(
    snapshot: EcosystemSnapshot,
    entityId: string
  ): LearningContext {
    // Assess stability
    const stability = this.assessStability(snapshot);

    // Assess domain knowledge
    const domainKnowledge = this.assessDomainKnowledge(snapshot, entityId);

    // Assess task complexity
    const taskComplexity = this.assessTaskComplexity(snapshot);

    // Available resources
    const availableResources = snapshot.resourceFlows;

    // Time pressure (based on resource scarcity)
    const timePressure = this.calculateTimePressure(snapshot);

    // Error tolerance (from colony state if available)
    const errorTolerance = this.calculateErrorTolerance(snapshot, entityId);

    // Colony size
    const colony = snapshot.colonies.find(c => c.members.includes(entityId));
    const colonySize = colony?.members.length;

    return {
      stability,
      domainKnowledge,
      taskComplexity,
      availableResources,
      timePressure,
      errorTolerance,
      colonySize,
      agentCount: snapshot.agents.size,
      performanceTrend: this.assessPerformanceTrend(entityId),
    };
  }

  /**
   * Assess context stability
   */
  private assessStability(snapshot: EcosystemSnapshot): ContextStability {
    // Calculate variance in resource flows
    const flows = Array.from(snapshot.resourceFlows.values());
    if (flows.length === 0) return ContextStability.STABLE;

    const variances = flows.map(f => {
      const mean = f.available / f.capacity;
      return Math.abs(mean - 0.5);
    });

    const avgVariance = variances.reduce((a, b) => a + b, 0) / variances.length;

    if (avgVariance < 0.2) return ContextStability.STABLE;
    if (avgVariance < 0.5) return ContextStability.MODERATE;
    return ContextStability.VOLATILE;
  }

  /**
   * Assess domain knowledge
   */
  private assessDomainKnowledge(
    snapshot: EcosystemSnapshot,
    entityId: string
  ): DomainKnowledge {
    const agent = snapshot.agents.get(entityId);
    if (!agent) return DomainKnowledge.NOVEL;

    // Check if we have successful history with similar agents
    const similarAgents = Array.from(snapshot.agents.values()).filter(a =>
      a.taxonomy === agent.taxonomy && a.id !== entityId
    );

    if (similarAgents.length > 5) return DomainKnowledge.KNOWN;
    if (similarAgents.length > 2) return DomainKnowledge.FAMILIAR;
    return DomainKnowledge.NOVEL;
  }

  /**
   * Assess task complexity
   */
  private assessTaskComplexity(snapshot: EcosystemSnapshot): TaskComplexity {
    // Based on ecosystem complexity
    const agentCount = snapshot.agents.size;
    const colonyCount = snapshot.colonies.length;
    const symbiosisCount = snapshot.symbioses.length;

    const complexityScore =
      agentCount * 0.3 +
      colonyCount * 0.4 +
      symbiosisCount * 0.3;

    if (complexityScore < 10) return TaskComplexity.SIMPLE;
    if (complexityScore < 30) return TaskComplexity.MODERATE;
    return TaskComplexity.COMPLEX;
  }

  /**
   * Calculate time pressure
   */
  private calculateTimePressure(snapshot: EcosystemSnapshot): number {
    // Based on resource scarcity
    let scarcity = 0;
    for (const flow of snapshot.resourceFlows.values()) {
      const utilization = flow.available / flow.capacity;
      scarcity += 1 - utilization;
    }

    return Math.min(1, scarcity / Math.max(1, snapshot.resourceFlows.size));
  }

  /**
   * Calculate error tolerance
   */
  private calculateErrorTolerance(
    snapshot: EcosystemSnapshot,
    entityId: string
  ): number {
    const agent = snapshot.agents.get(entityId);
    if (!agent) return 0.5;

    // Higher complexity agents have lower error tolerance
    return 1 - agent.complexity * 0.5;
  }

  /**
   * Assess performance trend
   */
  private assessPerformanceTrend(entityId: string): number {
    const outcomes = this.outcomeHistory.filter(o => o.entityId === entityId);

    if (outcomes.length < 2) return 0;

    // Calculate trend from recent outcomes
    const recent = outcomes.slice(-5);
    const improvements = recent.map(o =>
      o.fitnessAfter.overall - o.fitnessBefore.overall
    );

    return improvements.reduce((a, b) => a + b, 0) / improvements.length;
  }

  // ==========================================================================
  // PUBLIC API
  // ==========================================================================

  /**
   * Record a learning outcome
   */
  public recordOutcome(outcome: LearningOutcome): void {
    this.outcomeHistory.push(outcome);

    // Limit history size
    if (this.outcomeHistory.length > this.config.memoryCapacity) {
      this.outcomeHistory.shift();
    }

    // Calculate meta-reward
    this.calculateMetaReward(outcome);
  }

  /**
   * Get current statistics
   */
  public getStats(): MetaLearningStats {
    return { ...this.stats };
  }

  /**
   * Get all strategies
   */
  public getStrategies(): LearningStrategy[] {
    return Array.from(this.strategies.values());
  }

  /**
   * Get strategy by ID
   */
  public getStrategy(id: string): LearningStrategy | undefined {
    return this.strategies.get(id);
  }

  /**
   * Get meta-reward history for a strategy
   */
  public getMetaRewardHistory(strategyId: string): MetaRewardComponents[] {
    return this.metaRewardHistory.get(strategyId) ?? [];
  }

  /**
   * Update configuration
   */
  public updateConfig(config: Partial<MetaLearningConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get configuration
   */
  public getConfig(): MetaLearningConfig {
    return { ...this.config };
  }

  /**
   * Reset learning rates to defaults
   */
  public resetLearningRates(): void {
    this.learningRates.clear();
  }

  /**
   * Clear outcome history
   */
  public clearHistory(): void {
    this.outcomeHistory = [];
    this.metaRewardHistory.clear();
  }

  /**
   * Enable or disable meta-learning
   */
  public setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
    this.emit('enabled_changed', { enabled });
  }

  /**
   * Check if meta-learning is enabled
   */
  public isEnabled(): boolean {
    return this.config.enabled;
  }
}

// ============================================================================
// FACTORY FUNCTION
// ============================================================================

/**
 * Create a meta-learning engine with default configuration
 */
export function createMetaLearningEngine(
  fitnessEvaluator: FitnessEvaluator,
  evolutionEngine?: EvolutionEngine,
  config?: Partial<MetaLearningConfig>
): MetaLearningEngine {
  return new MetaLearningEngine(fitnessEvaluator, evolutionEngine, config);
}
