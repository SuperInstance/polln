/**
 * POLLN Microbiome - Meta-Learning Engine Tests
 *
 * Comprehensive test suite for meta-learning functionality including:
 * - Learning strategy selection
 * - Learning rate adaptation
 * - Transfer learning
 * - Strategy evolution
 * - Meta-reward calculation
 * - Context assessment
 * - Ethical considerations
 */

import {
  MetaLearningEngine,
  LearningAlgorithm,
  ContextStability,
  DomainKnowledge,
  TaskComplexity,
  LearningStrategy,
  LearningContext,
  LearningOutcome,
  MetaRewardComponents,
  TransferSource,
  TransferResult,
  MetaLearningConfig,
  createMetaLearningEngine,
} from '../metalearning.js';
import { FitnessEvaluator, FitnessEvaluatorConfig } from '../fitness.js';
import { EvolutionEngine } from '../evolution.js';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  FitnessScore,
  EcosystemSnapshot,
  ResourceType,
  LifecycleState,
  MetabolicProfile,
  ColonyStructure,
  Symbiosis,
  SymbiosisType,
} from '../types.js';

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Create a mock agent for testing
 */
function createMockAgent(
  id: string,
  taxonomy: AgentTaxonomy = AgentTaxonomy.BACTERIA
): MicrobiomeAgent {
  const metabolism: MetabolicProfile = {
    inputs: [ResourceType.TEXT],
    outputs: [ResourceType.STRUCTURED],
    processingRate: 100,
    efficiency: 0.8,
  };

  const lifecycle: LifecycleState = {
    health: 1.0,
    age: 0,
    generation: 0,
    isAlive: true,
  };

  return {
    id,
    taxonomy,
    name: `Agent-${id}`,
    metabolism,
    lifecycle,
    size: 1000,
    complexity: 0.5,
    process: jest.fn(),
    reproduce: jest.fn(),
    evaluateFitness: jest.fn(),
    canMetabolize: jest.fn(),
  };
}

/**
 * Create a mock fitness score
 */
function createFitnessScore(overall: number): FitnessScore {
  return {
    overall,
    throughput: overall * 0.9,
    accuracy: overall * 0.95,
    efficiency: overall * 0.85,
    cooperation: overall * 0.8,
  };
}

/**
 * Create a mock ecosystem snapshot
 */
function createMockSnapshot(agents: MicrobiomeAgent[]): EcosystemSnapshot {
  const resourceFlows = new Map<ResourceType, any>([
    [ResourceType.TEXT, { resource: ResourceType.TEXT, flowRate: 100, available: 80, capacity: 100 }],
    [ResourceType.STRUCTURED, { resource: ResourceType.STRUCTURED, flowRate: 50, available: 40, capacity: 100 }],
  ]);

  const agentMap = new Map();
  for (const agent of agents) {
    agentMap.set(agent.id, agent);
  }

  return {
    timestamp: Date.now(),
    agents: agentMap,
    resourceFlows,
    populations: new Map(),
    colonies: [],
    symbioses: [],
  };
}

/**
 * Create a mock fitness evaluator
 */
function createMockFitnessEvaluator(): FitnessEvaluator {
  const config: Partial<FitnessEvaluatorConfig> = {
    weights: {
      throughput: 0.25,
      accuracy: 0.35,
      efficiency: 0.25,
      cooperation: 0.15,
    },
  };

  return new FitnessEvaluator(config);
}

/**
 * Create a mock evolution engine
 */
function createMockEvolutionEngine(): EvolutionEngine | undefined {
  // EvolutionEngine requires specific setup, so we'll return undefined for tests
  // The meta-learning system handles optional evolution engines
  return undefined;
}

/**
 * Create a mock learning context
 */
function createMockContext(
  stability: ContextStability = ContextStability.MODERATE,
  domainKnowledge: DomainKnowledge = DomainKnowledge.FAMILIAR,
  taskComplexity: TaskComplexity = TaskComplexity.MODERATE
): LearningContext {
  return {
    stability,
    domainKnowledge,
    taskComplexity,
    availableResources: new Map([
      [ResourceType.TEXT, 100],
      [ResourceType.STRUCTURED, 50],
    ]),
    timePressure: 0.3,
    errorTolerance: 0.5,
    colonySize: 5,
    agentCount: 10,
    performanceTrend: 0.1,
  };
}

/**
 * Create a mock learning strategy
 */
function createMockStrategy(
  algorithm: LearningAlgorithm = LearningAlgorithm.HEBBIAN
): LearningStrategy {
  return {
    id: `strategy-${Date.now()}`,
    algorithm,
    learningRate: 0.1,
    explorationRate: 0.2,
    batchSize: 32,
    updateFrequency: 1000,
    regularization: 0.01,
    memoryDiscount: 0.99,
    riskTolerance: 0.5,
    createdAt: Date.now(),
    generation: 0,
  };
}

/**
 * Create a mock learning outcome
 */
function createMockOutcome(
  entityId: string,
  strategy: LearningStrategy,
  improvement: number = 0.1
): LearningOutcome {
  const beforeFitness = createFitnessScore(0.5);
  const afterFitness = createFitnessScore(0.5 + improvement);

  return {
    entityId,
    strategy,
    context: createMockContext(),
    fitnessBefore: beforeFitness,
    fitnessAfter: afterFitness,
    learningTime: 1000,
    resourcesConsumed: new Map([[ResourceType.COMPUTE, 100]]),
    timestamp: Date.now(),
  };
}

// ============================================================================
// TEST SUITES
// ============================================================================

describe('MetaLearningEngine', () => {
  let engine: MetaLearningEngine;
  let fitnessEvaluator: FitnessEvaluator;
  let evolutionEngine: EvolutionEngine | undefined;

  beforeEach(() => {
    fitnessEvaluator = createMockFitnessEvaluator();
    evolutionEngine = createMockEvolutionEngine();
    engine = new MetaLearningEngine(fitnessEvaluator, evolutionEngine);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ========================================================================
  // INITIALIZATION TESTS
  // ========================================================================

  describe('Initialization', () => {
    test('should initialize with default strategies', () => {
      const strategies = engine.getStrategies();
      expect(strategies.length).toBeGreaterThan(0);
      expect(strategies.length).toBeLessThanOrEqual(20);
    });

    test('should initialize with default configuration', () => {
      const config = engine.getConfig();
      expect(config.enabled).toBe(true);
      expect(config.populationSize).toBe(20);
      expect(config.minLearningRate).toBe(0.001);
      expect(config.maxLearningRate).toBe(0.5);
    });

    test('should accept custom configuration', () => {
      const customConfig: Partial<MetaLearningConfig> = {
        populationSize: 10,
        minLearningRate: 0.01,
        maxLearningRate: 0.3,
      };

      const customEngine = new MetaLearningEngine(
        fitnessEvaluator,
        evolutionEngine,
        customConfig
      );

      const config = customEngine.getConfig();
      expect(config.populationSize).toBe(10);
      expect(config.minLearningRate).toBe(0.01);
      expect(config.maxLearningRate).toBe(0.3);
    });

    test('should initialize with zero statistics', () => {
      const stats = engine.getStats();
      expect(stats.strategiesEvaluated).toBe(0);
      expect(stats.avgMetaReward).toBe(0);
      expect(stats.bestMetaReward).toBe(-Infinity);
    });
  });

  // ========================================================================
  // STRATEGY SELECTION TESTS
  // ========================================================================

  describe('Learning Strategy Selection', () => {
    test('should select strategy for stable context', () => {
      const context = createMockContext(
        ContextStability.STABLE,
        DomainKnowledge.KNOWN,
        TaskComplexity.SIMPLE
      );

      const strategy = engine.selectStrategy(context);

      expect(strategy).toBeDefined();
      expect(strategy.learningRate).toBeLessThanOrEqual(0.15); // Lower for stable
    });

    test('should select strategy for volatile context', () => {
      const context = createMockContext(
        ContextStability.VOLATILE,
        DomainKnowledge.FAMILIAR,
        TaskComplexity.MODERATE
      );

      const strategy = engine.selectStrategy(context);

      expect(strategy).toBeDefined();
      // Volatile contexts may prefer higher learning rates
    });

    test('should select strategy for novel domain', () => {
      const context = createMockContext(
        ContextStability.MODERATE,
        DomainKnowledge.NOVEL,
        TaskComplexity.COMPLEX
      );

      const strategy = engine.selectStrategy(context);

      expect(strategy).toBeDefined();
      expect(strategy.explorationRate).toBeGreaterThan(0); // Should explore
    });

    test('should select strategy for known domain', () => {
      const context = createMockContext(
        ContextStability.STABLE,
        DomainKnowledge.KNOWN,
        TaskComplexity.SIMPLE
      );

      const strategy = engine.selectStrategy(context);

      expect(strategy).toBeDefined();
      // Known domains may prefer exploitation
    });

    test('should emit strategy_selected event', (done) => {
      const context = createMockContext();

      engine.once('strategy_selected', (data) => {
        expect(data.strategy).toBeDefined();
        expect(data.context).toBe(context);
        expect(data.exploration).toBeDefined();
        done();
      });

      engine.selectStrategy(context);
    });

    test('should return default strategy when disabled', () => {
      engine.setEnabled(false);

      const context = createMockContext();
      const strategy = engine.selectStrategy(context);

      expect(strategy).toBeDefined();
    });
  });

  // ========================================================================
  // LEARNING RATE ADAPTATION TESTS
  // ========================================================================

  describe('Learning Rate Adaptation', () => {
    test('should decrease learning rate for good performance', () => {
      const performance = new Map([
        ['agent-1', 0.8], // Excellent
        ['agent-2', 0.9], // Excellent
      ]);

      engine.adaptLearningRates(performance);

      const rate1 = engine.getLearningRate('agent-1');
      const rate2 = engine.getLearningRate('agent-2');

      expect(rate1).toBeLessThan(0.1); // Should decrease
      expect(rate2).toBeLessThan(0.1); // Should decrease
    });

    test('should increase learning rate for poor performance', () => {
      const performance = new Map([
        ['agent-1', 0.2], // Poor
        ['agent-2', 0.1], // Very poor
      ]);

      engine.adaptLearningRates(performance);

      const rate1 = engine.getLearningRate('agent-1');
      const rate2 = engine.getLearningRate('agent-2');

      expect(rate1).toBeGreaterThan(0.1); // Should increase
      expect(rate2).toBeGreaterThan(0.1); // Should increase
    });

    test('should maintain learning rate for moderate performance', () => {
      engine.setLearningRate('agent-1', 0.1);

      const performance = new Map([
        ['agent-1', 0.5], // Moderate
      ]);

      engine.adaptLearningRates(performance);

      const rate = engine.getLearningRate('agent-1');
      expect(rate).toBeCloseTo(0.1, 1); // Should stay similar
    });

    test('should clamp learning rates to valid range', () => {
      const config = engine.getConfig();
      const minRate = config.minLearningRate;
      const maxRate = config.maxLearningRate;

      const performance = new Map([
        ['agent-1', 0.0], // Worst - would push above max
        ['agent-2', 1.0], // Best - would push below min
      ]);

      engine.adaptLearningRates(performance);

      const rate1 = engine.getLearningRate('agent-1');
      const rate2 = engine.getLearningRate('agent-2');

      expect(rate1).toBeGreaterThanOrEqual(minRate);
      expect(rate1).toBeLessThanOrEqual(maxRate);
      expect(rate2).toBeGreaterThanOrEqual(minRate);
      expect(rate2).toBeLessThanOrEqual(maxRate);
    });

    test('should emit learning_rates_adapted event', (done) => {
      const performance = new Map([
        ['agent-1', 0.8],
        ['agent-2', 0.2],
      ]);

      engine.once('learning_rates_adapted', (data) => {
        expect(data.adaptations).toBeDefined();
        expect(data.adaptations.length).toBeGreaterThan(0);
        done();
      });

      engine.adaptLearningRates(performance);
    });

    test('should track adaptation count in statistics', () => {
      const performance = new Map([
        ['agent-1', 0.8],
        ['agent-2', 0.2],
      ]);

      const statsBefore = engine.getStats();
      engine.adaptLearningRates(performance);
      const statsAfter = engine.getStats();

      expect(statsAfter.adaptationsCount).toBeGreaterThan(statsBefore.adaptationsCount);
    });
  });

  // ========================================================================
  // TRANSFER LEARNING TESTS
  // ========================================================================

  describe('Transfer Learning', () => {
    test('should return zero success when no similar domains', () => {
      const result = engine.transferLearning(
        'unknown-domain',
        'target-domain',
        createMockContext()
      );

      expect(result.success).toBe(0);
      expect(result.transferredKnowledge.size).toBe(0);
    });

    test('should successfully transfer from similar domain', () => {
      const source: TransferSource = {
        domain: 'similar-domain',
        sourceId: 'agent-1',
        knowledge: new Map([
          ['pattern-1', 0.8],
          ['pattern-2', 0.6],
        ]),
        confidence: 0.9,
        similarity: 0.8,
      };

      engine.registerTransferSource(source);

      const result = engine.transferLearning(
        'similar-domain',
        'target-domain',
        createMockContext()
      );

      expect(result.success).toBeGreaterThan(0);
      expect(result.transferredKnowledge.size).toBeGreaterThan(0);
      expect(result.performanceImprovement).toBeGreaterThan(0);
    });

    test('should adapt knowledge based on task complexity', () => {
      const source: TransferSource = {
        domain: 'source-domain',
        sourceId: 'agent-1',
        knowledge: new Map([
          ['pattern-1', 0.8],
        ]),
        confidence: 0.9,
        similarity: 0.8,
      };

      engine.registerTransferSource(source);

      const complexContext = createMockContext(
        ContextStability.MODERATE,
        DomainKnowledge.FAMILIAR,
        TaskComplexity.COMPLEX
      );

      const result = engine.transferLearning(
        'source-domain',
        'target-domain',
        complexContext
      );

      // Complex tasks should have adapted (lower) values
      const adaptedValue = result.transferredKnowledge.get('pattern-1');
      expect(adaptedValue).toBeLessThan(0.8);
    });

    test('should emit transfer_learning event', (done) => {
      const source: TransferSource = {
        domain: 'source-domain',
        sourceId: 'agent-1',
        knowledge: new Map([['pattern-1', 0.8]]),
        confidence: 0.9,
        similarity: 0.8,
      };

      engine.registerTransferSource(source);

      engine.once('transfer_learning', (data) => {
        expect(data.sourceDomain).toBe('source-domain');
        expect(data.targetDomain).toBe('target-domain');
        expect(data.result).toBeDefined();
        done();
      });

      engine.transferLearning('source-domain', 'target-domain', createMockContext());
    });

    test('should register successful transfers as new sources', () => {
      const source: TransferSource = {
        domain: 'source-domain',
        sourceId: 'agent-1',
        knowledge: new Map([['pattern-1', 0.8]]),
        confidence: 0.9,
        similarity: 0.8,
      };

      engine.registerTransferSource(source);

      const result = engine.transferLearning(
        'source-domain',
        'target-domain',
        createMockContext()
      );

      // High success should register new source
      if (result.performanceImprovement > 0.6) {
        // Should be available for future transfers
        const targetResult = engine.transferLearning(
          'target-domain',
          'another-domain',
          createMockContext()
        );
        expect(targetResult.success).toBeGreaterThan(0);
      }
    });
  });

  // ========================================================================
  // STRATEGY EVOLUTION TESTS
  // ========================================================================

  describe('Strategy Evolution', () => {
    test('should evolve strategies based on meta-reward', () => {
      // Record some outcomes to establish meta-rewards
      const strategy = engine.getStrategies()[0];

      for (let i = 0; i < 5; i++) {
        const outcome = createMockOutcome('agent-1', strategy, 0.1);
        engine.recordOutcome(outcome);
      }

      const populationBefore = engine.getStats().strategyPopulation;
      engine.evolveStrategies();
      const populationAfter = engine.getStats().strategyPopulation;

      // Population should be maintained (replace worst with offspring)
      expect(populationAfter).toBeCloseTo(populationBefore, 0);
    });

    test('should create offspring through crossover', () => {
      const strategies = engine.getStrategies();
      const initialCount = strategies.length;

      // Record outcomes to establish meta-rewards
      strategies.forEach((strategy, i) => {
        const outcome = createMockOutcome(`agent-${i}`, strategy, 0.1);
        engine.recordOutcome(outcome);
      });

      engine.evolveStrategies();

      const newStrategies = engine.getStrategies();
      const offspring = newStrategies.filter(s => s.generation > 0);

      expect(offspring.length).toBeGreaterThan(0);
      expect(newStrategies.length).toBe(initialCount);
    });

    test('should apply mutations to offspring', () => {
      // Record outcomes
      const strategies = engine.getStrategies();
      strategies.forEach((strategy, i) => {
        const outcome = createMockOutcome(`agent-${i}`, strategy, 0.1);
        engine.recordOutcome(outcome);
      });

      engine.evolveStrategies();

      const newStrategies = engine.getStrategies();
      const offspring = newStrategies.filter(s => s.generation > 0);

      // Check that some parameters differ from parents
      offspring.forEach(child => {
        if (child.parentIds && child.parentIds.length > 0) {
          const parent = engine.getStrategy(child.parentIds[0]);
          if (parent) {
            // At least one parameter should be different (mutation or crossover)
            const paramsDifferent =
              child.algorithm !== parent.algorithm ||
              child.learningRate !== parent.learningRate ||
              child.explorationRate !== parent.explorationRate;

            expect(paramsDifferent).toBe(true);
          }
        }
      });
    });

    test('should emit strategies_evolved event', (done) => {
      // Record outcomes
      const strategies = engine.getStrategies();
      strategies.forEach((strategy, i) => {
        const outcome = createMockOutcome(`agent-${i}`, strategy, 0.1);
        engine.recordOutcome(outcome);
      });

      engine.once('strategies_evolved', (data) => {
        expect(data.survivors).toBeDefined();
        expect(data.offspringCount).toBeDefined();
        expect(data.offspringCount).toBeGreaterThan(0);
        done();
      });

      engine.evolveStrategies();
    });

    test('should not evolve with insufficient population', () => {
      const smallEngine = new MetaLearningEngine(
        fitnessEvaluator,
        evolutionEngine,
        { populationSize: 2 }
      );

      const statsBefore = smallEngine.getStats();
      smallEngine.evolveStrategies();
      const statsAfter = smallEngine.getStats();

      // Should not evolve with less than 4 strategies
      expect(statsAfter.lastEvolution).toBe(statsBefore.lastEvolution);
    });
  });

  // ========================================================================
  // META-REWARD CALCULATION TESTS
  // ========================================================================

  describe('Meta-Reward Calculation', () => {
    test('should calculate positive reward for improvement', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.2); // 20% improvement

      const reward = engine.calculateMetaReward(outcome);

      expect(reward.performance).toBeGreaterThan(0);
      expect(reward.total).toBeGreaterThan(0);
    });

    test('should calculate negative reward for decline', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, -0.1); // 10% decline

      const reward = engine.calculateMetaReward(outcome);

      expect(reward.performance).toBeLessThan(0);
      expect(reward.total).toBeLessThan(0.5); // May still have positive components
    });

    test('should reward efficiency', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.1);
      outcome.learningTime = 500; // Fast learning

      const reward = engine.calculateMetaReward(outcome);

      expect(reward.efficiency).toBeGreaterThan(0.5);
    });

    test('should penalize excessive resource consumption', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.1);
      outcome.resourcesConsumed = new Map([[ResourceType.COMPUTE, 1000]]);

      const reward = engine.calculateMetaReward(outcome);

      expect(reward.efficiency).toBeLessThan(0.5);
    });

    test('should reward adaptability for novel domains', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.1);
      outcome.context.domainKnowledge = DomainKnowledge.NOVEL;

      const reward = engine.calculateMetaReward(outcome);

      expect(reward.adaptability).toBeGreaterThan(outcome.fitnessAfter.overall - outcome.fitnessBefore.overall);
    });

    test('should apply safety penalty for violations', () => {
      const strategy = createMockStrategy();
      strategy.riskTolerance = 0.9; // High risk

      const outcome = createMockOutcome('agent-1', strategy, 0.1);
      outcome.context.errorTolerance = 0.1; // Low tolerance
      outcome.resourcesConsumed = new Map([[ResourceType.COMPUTE, 1000]]);

      const reward = engine.calculateMetaReward(outcome);

      expect(reward.safety).toBeLessThan(1); // Should be penalized
    });

    test('should update statistics', () => {
      const statsBefore = engine.getStats();

      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.2);
      engine.recordOutcome(outcome);

      const statsAfter = engine.getStats();

      expect(statsAfter.strategiesEvaluated).toBe(statsBefore.strategiesEvaluated + 1);
    });

    test('should track best meta-reward', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.3);

      engine.calculateMetaReward(outcome);

      const stats = engine.getStats();
      expect(stats.bestMetaReward).toBeGreaterThan(0);
    });
  });

  // ========================================================================
  // CONTEXT ASSESSMENT TESTS
  // ========================================================================

  describe('Context Assessment', () => {
    test('should assess stable context', () => {
      const agents = [
        createMockAgent('agent-1'),
        createMockAgent('agent-2'),
      ];

      const snapshot = createMockSnapshot(agents);
      const context = engine.assessContext(snapshot, 'agent-1');

      expect(context).toBeDefined();
      expect(context.stability).toBeDefined();
      expect(context.domainKnowledge).toBeDefined();
      expect(context.taskComplexity).toBeDefined();
    });

    test('should assess domain knowledge based on similar agents', () => {
      const agents = [
        createMockAgent('agent-1', AgentTaxonomy.BACTERIA),
        createMockAgent('agent-2', AgentTaxonomy.BACTERIA),
        createMockAgent('agent-3', AgentTaxonomy.BACTERIA),
        createMockAgent('agent-4', AgentTaxonomy.BACTERIA),
        createMockAgent('agent-5', AgentTaxonomy.BACTERIA),
        createMockAgent('agent-6', AgentTaxonomy.BACTERIA),
      ];

      const snapshot = createMockSnapshot(agents);
      const context = engine.assessContext(snapshot, 'agent-1');

      // Should be at least FAMILIAR with 5+ similar agents
      expect(context.domainKnowledge).toBe(DomainKnowledge.FAMILIAR);
    });

    test('should calculate time pressure from resource scarcity', () => {
      const agents = [createMockAgent('agent-1')];

      const snapshot = createMockSnapshot(agents);
      // Make resources scarce
      snapshot.resourceFlows.get(ResourceType.TEXT)!.available = 10;
      snapshot.resourceFlows.get(ResourceType.TEXT)!.capacity = 100;

      const context = engine.assessContext(snapshot, 'agent-1');

      expect(context.timePressure).toBeGreaterThan(0.5);
    });

    test('should assess task complexity from ecosystem', () => {
      const agents: MicrobiomeAgent[] = [];
      for (let i = 0; i < 50; i++) {
        agents.push(createMockAgent(`agent-${i}`));
      }

      const snapshot = createMockSnapshot(agents);
      snapshot.colonies = [
        { id: 'colony-1', members: agents.map(a => a.id).slice(0, 10), communicationChannels: new Map(), formationTime: Date.now(), stability: 0.8, coEvolutionBonus: 0.2 },
      ];
      snapshot.symbioses = [
        { sourceId: 'agent-1', targetId: 'agent-2', type: SymbiosisType.MUTUALISM, strength: 0.8, benefitToSource: 0.7, benefitToTarget: 0.7 },
      ];

      const context = engine.assessContext(snapshot, 'agent-1');

      // With 50 agents, 1 colony, and 1 symbiosis, complexity score is:
      // 50 * 0.3 + 1 * 0.4 + 1 * 0.3 = 15 + 0.4 + 0.3 = 15.7
      // This falls in the MODERATE range (10-30)
      expect(context.taskComplexity).toBe(TaskComplexity.MODERATE);
    });
  });

  // ========================================================================
  // PUBLIC API TESTS
  // ========================================================================

  describe('Public API', () => {
    test('should get all strategies', () => {
      const strategies = engine.getStrategies();

      expect(Array.isArray(strategies)).toBe(true);
      expect(strategies.length).toBeGreaterThan(0);
    });

    test('should get strategy by ID', () => {
      const strategies = engine.getStrategies();
      const firstStrategy = strategies[0];

      const retrieved = engine.getStrategy(firstStrategy.id);

      expect(retrieved).toEqual(firstStrategy);
    });

    test('should return undefined for non-existent strategy', () => {
      const retrieved = engine.getStrategy('non-existent');

      expect(retrieved).toBeUndefined();
    });

    test('should get meta-reward history', () => {
      const strategy = engine.getStrategies()[0];
      const outcome = createMockOutcome('agent-1', strategy, 0.1);

      engine.recordOutcome(outcome);

      const history = engine.getMetaRewardHistory(strategy.id);

      expect(history.length).toBeGreaterThan(0);
    });

    test('should update configuration', () => {
      const newPopulationSize = 30;

      engine.updateConfig({ populationSize: newPopulationSize });

      const config = engine.getConfig();
      expect(config.populationSize).toBe(newPopulationSize);
    });

    test('should reset learning rates', () => {
      engine.setLearningRate('agent-1', 0.2);
      expect(engine.getLearningRate('agent-1')).toBe(0.2);

      engine.resetLearningRates();
      expect(engine.getLearningRate('agent-1')).toBe(0.1); // Default
    });

    test('should clear history', () => {
      const strategy = engine.getStrategies()[0];
      const outcome = createMockOutcome('agent-1', strategy, 0.1);

      engine.recordOutcome(outcome);
      expect(engine.getMetaRewardHistory(strategy.id).length).toBeGreaterThan(0);

      engine.clearHistory();
      expect(engine.getMetaRewardHistory(strategy.id).length).toBe(0);
    });

    test('should enable and disable meta-learning', () => {
      expect(engine.isEnabled()).toBe(true);

      engine.setEnabled(false);
      expect(engine.isEnabled()).toBe(false);

      engine.setEnabled(true);
      expect(engine.isEnabled()).toBe(true);
    });

    test('should emit enabled_changed event', (done) => {
      engine.once('enabled_changed', (data) => {
        expect(data.enabled).toBe(false);
        done();
      });

      engine.setEnabled(false);
    });
  });

  // ========================================================================
  // ETHICAL CONSIDERATIONS TESTS
  // ========================================================================

  describe('Ethical Considerations', () => {
    test('should enforce safety constraints in meta-reward', () => {
      const riskyStrategy = createMockStrategy();
      riskyStrategy.riskTolerance = 1.0; // Maximum risk

      const outcome = createMockOutcome('agent-1', riskyStrategy, 0.1);
      outcome.context.errorTolerance = 0; // Zero tolerance

      const reward = engine.calculateMetaReward(outcome);

      // Safety penalty should be applied
      expect(reward.safety).toBeLessThanOrEqual(0.5);
      expect(reward.total).toBeLessThan(1.0);
    });

    test('should prefer safe strategies in critical contexts', () => {
      const context = createMockContext(
        ContextStability.STABLE,
        DomainKnowledge.KNOWN,
        TaskComplexity.SIMPLE
      );
      context.errorTolerance = 0; // Critical context

      const strategy = engine.selectStrategy(context);

      // Should prefer conservative strategies (riskTolerance <= 0.7)
      expect(strategy.riskTolerance).toBeLessThanOrEqual(0.7);
    });

    test('should maintain transparency through events', (done) => {
      const events: string[] = [];

      engine.on('strategy_selected', () => events.push('selected'));
      engine.on('learning_rates_adapted', () => events.push('adapted'));
      engine.on('transfer_learning', () => events.push('transfer'));
      engine.on('strategies_evolved', () => events.push('evolved'));

      // Trigger various events
      const context = createMockContext();
      engine.selectStrategy(context);
      engine.adaptLearningRates(new Map([['agent-1', 0.8]]));

      setTimeout(() => {
        expect(events.length).toBeGreaterThan(0);
        done();
      }, 100);
    });

    test('should provide accountability through history', () => {
      const strategy = engine.getStrategies()[0];
      const outcome = createMockOutcome('agent-1', strategy, 0.1);

      engine.recordOutcome(outcome);

      const history = engine.getMetaRewardHistory(strategy.id);

      // Should have complete record
      expect(history[0].performance).toBeDefined();
      expect(history[0].efficiency).toBeDefined();
      expect(history[0].safety).toBeDefined();
      expect(history[0].total).toBeDefined();
    });

    test('should prioritize beneficence in reward function', () => {
      const strategy = createMockStrategy();
      const outcome = createMockOutcome('agent-1', strategy, 0.2);

      const reward = engine.calculateMetaReward(outcome);

      // Performance improvement (beneficence) should have highest weight
      const weights = {
        performance: 0.4,
        efficiency: 0.2,
        adaptability: 0.2,
        generalization: 0.1,
      };

      const expectedTotal =
        reward.performance * weights.performance +
        reward.efficiency * weights.efficiency +
        reward.adaptability * weights.adaptability +
        reward.generalization * weights.generalization +
        reward.safety * 0.2;

      expect(reward.total).toBeCloseTo(expectedTotal, 1);
    });
  });

  // ========================================================================
  // INTEGRATION TESTS
  // ========================================================================

  describe('Integration Tests', () => {
    test('should handle complete learning cycle', () => {
      const agents = [
        createMockAgent('agent-1'),
        createMockAgent('agent-2'),
      ];

      const snapshot = createMockSnapshot(agents);

      // 1. Assess context
      const context = engine.assessContext(snapshot, 'agent-1');

      // 2. Select strategy
      const strategy = engine.selectStrategy(context);

      // 3. Simulate learning outcome
      const outcome = createMockOutcome('agent-1', strategy, 0.15);
      engine.recordOutcome(outcome);

      // 4. Adapt learning rates
      engine.adaptLearningRates(new Map([['agent-1', 0.7]]));

      // 5. Verify state
      const stats = engine.getStats();
      expect(stats.strategiesEvaluated).toBeGreaterThan(0);
      expect(engine.getLearningRate('agent-1')).toBeDefined();
    });

    test('should support transfer learning workflow', () => {
      const sourceContext = createMockContext(
        ContextStability.STABLE,
        DomainKnowledge.KNOWN,
        TaskComplexity.SIMPLE
      );

      // Register source
      const source: TransferSource = {
        domain: 'source-domain',
        sourceId: 'agent-1',
        knowledge: new Map([['pattern-1', 0.9]]),
        confidence: 0.95,
        similarity: 0.85,
      };
      engine.registerTransferSource(source);

      // Transfer to target
      const targetContext = createMockContext(
        ContextStability.MODERATE,
        DomainKnowledge.FAMILIAR,
        TaskComplexity.MODERATE
      );

      const result = engine.transferLearning(
        'source-domain',
        'target-domain',
        targetContext
      );

      expect(result.success).toBeGreaterThan(0.7);
      expect(result.transferredKnowledge.has('pattern-1')).toBe(true);
    });

    test('should evolve strategies over multiple cycles', () => {
      const strategies = engine.getStrategies();

      // Simulate multiple learning cycles
      for (let cycle = 0; cycle < 3; cycle++) {
        strategies.forEach((strategy, i) => {
          const outcome = createMockOutcome(`agent-${i}`, strategy, 0.1 * (1 + cycle * 0.2));
          engine.recordOutcome(outcome);
        });

        engine.evolveStrategies();
      }

      const stats = engine.getStats();
      expect(stats.strategyPopulation).toBeGreaterThan(0);
      expect(stats.avgMetaReward).toBeGreaterThan(0);
    });
  });
});

// ============================================================================
// FACTORY FUNCTION TESTS
// ============================================================================

describe('createMetaLearningEngine', () => {
  test('should create engine with factory function', () => {
    const fitnessEvaluator = createMockFitnessEvaluator();
    const evolutionEngine = createMockEvolutionEngine();

    const engine = createMetaLearningEngine(
      fitnessEvaluator,
      evolutionEngine,
      { populationSize: 15 }
    );

    expect(engine).toBeInstanceOf(MetaLearningEngine);
    expect(engine.getConfig().populationSize).toBe(15);
  });

  test('should create engine with default config', () => {
    const fitnessEvaluator = createMockFitnessEvaluator();
    const evolutionEngine = createMockEvolutionEngine();

    const engine = createMetaLearningEngine(fitnessEvaluator, evolutionEngine);

    expect(engine).toBeInstanceOf(MetaLearningEngine);
    expect(engine.isEnabled()).toBe(true);
  });

  test('should create engine without evolution engine', () => {
    const fitnessEvaluator = createMockFitnessEvaluator();

    const engine = createMetaLearningEngine(fitnessEvaluator);

    expect(engine).toBeInstanceOf(MetaLearningEngine);
    expect(engine.isEnabled()).toBe(true);
  });
});
