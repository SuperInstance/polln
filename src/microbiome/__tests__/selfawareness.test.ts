/**
 * POLLN Microbiome - Self-Awareness Engine Tests
 *
 * Comprehensive test suite for self-awareness functionality including:
 * - Self-modeling capabilities
 * - Self-prediction accuracy
 * - Performance monitoring
 * - Blind spot detection
 * - Theory of mind modeling
 * - Reflective reasoning
 * - Ethical considerations
 */

import {
  SelfAwarenessEngine,
  AwarenessLevel,
  Capability,
  Limitation,
  BehavioralPattern,
  PerformanceEntry,
  SelfModel,
  Goal,
  GoalStatus,
  ValueSystem,
  SelfPrediction,
  Situation,
  PerformanceReport,
  BlindSpot,
  OptimizationPlan,
  OptimizationStrategy,
  MentalState,
  Experience,
  Insight,
  InsightType,
  SelfAwarenessConfig,
  SelfAwarenessStats,
  createSelfAwarenessEngine,
} from '../selfawareness.js';
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
import { MetaLearningEngine, LearningContext, ContextStability, DomainKnowledge, TaskComplexity } from '../metalearning.js';

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Create a mock agent for testing
 */
function createMockAgent(
  id: string,
  taxonomy: AgentTaxonomy = AgentTaxonomy.BACTERIA,
  health: number = 1.0,
  complexity: number = 0.5
): MicrobiomeAgent {
  const metabolism: MetabolicProfile = {
    inputs: [ResourceType.TEXT],
    outputs: [ResourceType.STRUCTURED],
    processingRate: 100,
    efficiency: 0.8,
  };

  const lifecycle: LifecycleState = {
    health,
    age: 1000,
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
    complexity,
    process: jest.fn(),
    reproduce: jest.fn(),
    evaluateFitness: jest.fn(() => createFitnessScore(health)),
    canMetabolize: jest.fn(() => true),
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
  const colonies: ColonyStructure[] = [];
  const symbioses: Symbiosis[] = [];

  // Create a colony if we have multiple agents
  if (agents.length > 1) {
    colonies.push({
      id: 'colony-1',
      members: agents.slice(0, Math.min(3, agents.length)).map(a => a.id),
      communicationChannels: new Map(),
      formationTime: Date.now() - 10000,
      stability: 0.8,
      coEvolutionBonus: 0.3,
    });

    // Create some symbioses
    for (let i = 0; i < Math.min(agents.length - 1, 2); i++) {
      symbioses.push({
        sourceId: agents[i].id,
        targetId: agents[i + 1].id,
        type: SymbiosisType.MUTUALISM,
        strength: 0.7,
        benefitToSource: 0.6,
        benefitToTarget: 0.7,
      });
    }
  }

  return {
    timestamp: Date.now(),
    agents: new Map(agents.map(a => [a.id, a])),
    colonies,
    symbioses,
    resourceFlows: new Map([
      [ResourceType.TEXT, { resource: ResourceType.TEXT, flowRate: 100, available: 80, capacity: 100 }],
      [ResourceType.STRUCTURED, { resource: ResourceType.STRUCTURED, flowRate: 50, available: 40, capacity: 100 }],
    ]),
    populationDynamics: new Map(),
  };
}

/**
 * Create a mock situation
 */
function createMockSituation(context: string = 'normal'): Situation {
  return {
    id: `situation-${Date.now()}`,
    context,
    resources: new Map([
      [ResourceType.TEXT, 0.8],
      [ResourceType.STRUCTURED, 0.6],
    ]),
    environmentalFactors: new Map([
      ['temperature', 0.5],
      ['pressure', 0.3],
    ]),
    socialContext: new Map([
      ['colony_members', 3],
      ['competition', 0.2],
    ]),
    timePressure: 0.4,
  };
}

/**
 * Create a mock learning context
 */
function createMockLearningContext(): LearningContext {
  return {
    stability: ContextStability.MODERATE,
    domainKnowledge: DomainKnowledge.FAMILIAR,
    taskComplexity: TaskComplexity.MODERATE,
    availableResources: new Map([
      [ResourceType.TEXT, 100],
      [ResourceType.STRUCTURED, 50],
    ]),
    timePressure: 0.4,
    errorTolerance: 0.6,
    agentCount: 5,
    performanceTrend: 0.1,
  };
}

/**
 * Create a mock experience
 */
function createMockExperience(): Experience {
  return {
    id: `experience-${Date.now()}`,
    description: 'Test experience',
    context: createMockLearningContext(),
    actions: ['process_input', 'generate_output'],
    outcomes: new Map([
      ['performance', 0.7],
      ['efficiency', 0.8],
      ['cooperation', 0.6],
    ]),
    reflections: [],
    learnings: [],
    timestamp: Date.now(),
  };
}

// ============================================================================
// TEST SUITES
// ============================================================================

beforeAll(() => {
  jest.useFakeTimers();
});

afterAll(() => {
  jest.useRealTimers();
});

describe('SelfAwarenessEngine', () => {
  let engine: SelfAwarenessEngine;
  let metaLearning: MetaLearningEngine;

  beforeEach(() => {
    // Create meta-learning engine
    metaLearning = new MetaLearningEngine(
      jest.fn() as any, // fitness evaluator
      undefined, // evolution engine
      { enabled: true }
    );

    // Create self-awareness engine
    engine = new SelfAwarenessEngine(metaLearning, {
      enabled: true,
      maxHistorySize: 100,
      updateInterval: 1000,
      predictionThreshold: 0.6,
      blindSpotSensitivity: 0.7,
      theoryOfMindDepth: 2,
      reflectionFrequency: 0.1,
      learningRate: 0.1,
      minCapabilityConfidence: 0.5,
      maxBlindSpotAge: 86400000,
    });
  });

  afterEach(() => {
    engine.clearAllData();
  });

  // ==========================================================================
  // INITIALIZATION TESTS
  // ==========================================================================

  describe('Initialization', () => {
    test('should create engine with default config', () => {
      const defaultEngine = new SelfAwarenessEngine();
      expect(defaultEngine.isEnabled()).toBe(true);
      expect(defaultEngine.getStats().modelsBuilt).toBe(0);
    });

    test('should create engine with custom config', () => {
      const customEngine = new SelfAwarenessEngine(undefined, {
        enabled: false,
        blindSpotSensitivity: 0.9,
      });
      expect(customEngine.isEnabled()).toBe(false);
      expect(customEngine.getConfig().blindSpotSensitivity).toBe(0.9);
    });

    test('should create engine via factory function', () => {
      const factoryEngine = createSelfAwarenessEngine(metaLearning);
      expect(factoryEngine).toBeInstanceOf(SelfAwarenessEngine);
      expect(factoryEngine.isEnabled()).toBe(true);
    });
  });

  // ==========================================================================
  // SELF-MODELING TESTS
  // ==========================================================================

  describe('Self-Modeling', () => {
    test('should build initial self-model for agent', () => {
      const agent = createMockAgent('agent-1');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      expect(model).toBeDefined();
      expect(model.agentId).toBe('agent-1');
      expect(model.taxonomy).toBe(AgentTaxonomy.BACTERIA);
      expect(model.capabilities.length).toBeGreaterThan(0);
      expect(model.performanceHistory).toBeDefined();
      expect(model.lastUpdated).toBeLessThanOrEqual(Date.now());
    });

    test('should extract metabolic capabilities', () => {
      const agent = createMockAgent('agent-2');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      const metabolicCap = model.capabilities.find(c => c.id === 'metabolize_text');
      expect(metabolicCap).toBeDefined();
      expect(metabolicCap?.strength).toBe(agent.metabolism.efficiency);
      expect(metabolicCap?.confidence).toBeGreaterThan(0);
    });

    test('should identify limitations based on agent properties', () => {
      const agent = createMockAgent('agent-3', AgentTaxonomy.BACTERIA, 0.4, 0.2);
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      // Should identify low complexity and poor health limitations
      expect(model.limitations.length).toBeGreaterThan(0);
      const poorHealth = model.limitations.find(l => l.id === 'poor_health');
      expect(poorHealth).toBeDefined();
      expect(poorHealth?.severity).toBeGreaterThan(0.5);
    });

    test('should analyze behavioral patterns', () => {
      const agent = createMockAgent('agent-4');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      expect(model.typicalBehaviors.length).toBeGreaterThan(0);
      const defaultPattern = model.typicalBehaviors.find(b => b.id === 'default_processing');
      expect(defaultPattern).toBeDefined();
      expect(defaultPattern?.frequency).toBeGreaterThan(0);
    });

    test('should include colony behavior when in colony', () => {
      const agents = [
        createMockAgent('agent-5a'),
        createMockAgent('agent-5b'),
        createMockAgent('agent-5c'),
      ];
      const snapshot = createMockSnapshot(agents);

      const model = engine.buildSelfModel(agents[0], snapshot);

      const colonyPattern = model.typicalBehaviors.find(b => b.id === 'colony_behavior');
      expect(colonyPattern).toBeDefined();
      expect(colonyPattern?.contexts).toContain('colony');
    });

    test('should update existing self-model', () => {
      const agent = createMockAgent('agent-6');
      const snapshot = createMockSnapshot([agent]);

      // Build initial model
      const model1 = engine.buildSelfModel(agent, snapshot);

      // Build model again (should update existing)
      const model2 = engine.buildSelfModel(agent, snapshot);

      // Should be the same model (same agent ID)
      expect(model2.agentId).toBe(model1.agentId);

      // Should have been updated or at least not lost data
      expect(model2.capabilities.length).toBeGreaterThan(0);
      expect(model2.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.PERFORMANCE);
    });

    test('should calculate awareness level correctly', () => {
      const agent = createMockAgent('agent-7');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      // Should have at least PERFORMANCE level (has performance history)
      expect(model.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.PERFORMANCE);
    });

    test('should calculate model confidence', () => {
      const agent = createMockAgent('agent-8');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      expect(model.confidence).toBeGreaterThanOrEqual(0);
      expect(model.confidence).toBeLessThanOrEqual(1);
    });

    test('should analyze social connections', () => {
      const agents = [
        createMockAgent('agent-9a'),
        createMockAgent('agent-9b'),
      ];
      const snapshot = createMockSnapshot(agents);

      const model = engine.buildSelfModel(agents[0], snapshot);

      expect(model.socialConnections.size).toBeGreaterThan(0);
    });

    test('should emit event on self-model update', (done) => {
      const agent = createMockAgent('agent-10');
      const snapshot = createMockSnapshot([agent]);

      engine.on('self_model_updated', (data) => {
        expect(data.agentId).toBe('agent-10');
        expect(data.model).toBeDefined();
        done();
      });

      engine.buildSelfModel(agent, snapshot);
    });

    test('should throw error when disabled', () => {
      engine.setEnabled(false);
      const agent = createMockAgent('agent-11');
      const snapshot = createMockSnapshot([agent]);

      expect(() => engine.buildSelfModel(agent, snapshot)).toThrow('Self-awareness is disabled');
    });

    test('should update statistics after building model', () => {
      const agent = createMockAgent('agent-12');
      const snapshot = createMockSnapshot([agent]);

      const initialStats = engine.getStats();
      engine.buildSelfModel(agent, snapshot);
      const finalStats = engine.getStats();

      expect(finalStats.modelsBuilt).toBe(initialStats.modelsBuilt + 1);
    });
  });

  // ==========================================================================
  // SELF-PREDICTION TESTS
  // ==========================================================================

  describe('Self-Prediction', () => {
    test('should predict own behavior', () => {
      const agent = createMockAgent('agent-20');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation('normal');

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      expect(prediction).toBeDefined();
      expect(prediction.situation).toBe(situation);
      expect(prediction.predictedBehavior).toBeDefined();
      expect(prediction.confidence).toBeGreaterThanOrEqual(0);
      expect(prediction.confidence).toBeLessThanOrEqual(1);
    });

    test('should return low confidence for unknown situations', () => {
      const agent = createMockAgent('agent-21');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation('completely_novel_context');

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      // Should have low confidence since no pattern matches (default is 0.3)
      expect(prediction.confidence).toBeLessThanOrEqual(0.5);
    });

    test('should provide alternative behaviors', () => {
      const agent = createMockAgent('agent-22');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation('colony cooperation');

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      expect(prediction.alternatives).toBeDefined();
      expect(Array.isArray(prediction.alternatives)).toBe(true);
    });

    test('should store prediction in history', () => {
      const agent = createMockAgent('agent-23');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      const history = engine.getPredictionHistory(agent.id);
      expect(history.length).toBeGreaterThan(0);
      expect(history[history.length - 1].id).toBe(prediction.id);
    });

    test('should validate prediction accuracy', () => {
      const agent = createMockAgent('agent-24');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      const validation = engine.validatePrediction(agent.id, prediction.id, 0.75);

      expect(validation.accuracy).toBeGreaterThanOrEqual(0);
      expect(validation.accuracy).toBeLessThanOrEqual(1);
      expect(validation.error).toBeGreaterThanOrEqual(0);
    });

    test('should update prediction accuracy stats', () => {
      const agent = createMockAgent('agent-25');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      const initialStats = engine.getStats();
      engine.validatePrediction(agent.id, prediction.id, 0.8);
      const finalStats = engine.getStats();

      expect(finalStats.predictionAccuracy).toBeDefined();
    });

    test('should emit event on behavior prediction', (done) => {
      const agent = createMockAgent('agent-26');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);

      engine.on('behavior_predicted', (data) => {
        expect(data.agentId).toBe('agent-26');
        expect(data.prediction).toBeDefined();
        done();
      });

      engine.predictOwnBehavior(agent, situation);
    });

    test('should throw error when no self-model exists', () => {
      const agent = createMockAgent('agent-27');
      const situation = createMockSituation();

      expect(() => engine.predictOwnBehavior(agent, situation)).toThrow('No self-model found');
    });

    test('should match behavioral patterns to situation context', () => {
      const agent = createMockAgent('agent-28');
      const snapshot = createMockSnapshot([agent, createMockAgent('agent-28b')]);
      const situation = createMockSituation('colony');

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      // Should match colony behavior pattern
      expect(prediction.predictedBehavior).toBeDefined();
    });
  });

  // ==========================================================================
  // PERFORMANCE MONITORING TESTS
  // ==========================================================================

  describe('Performance Monitoring', () => {
    test('should generate performance report', () => {
      const agent = createMockAgent('agent-30');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const report = engine.monitorPerformance(agent);

      expect(report).toBeDefined();
      expect(report.agentId).toBe('agent-30');
      expect(report.overallPerformance).toBeGreaterThanOrEqual(0);
      expect(report.overallPerformance).toBeLessThanOrEqual(1);
      expect(report.performanceTrend).toBeGreaterThanOrEqual(-1);
      expect(report.performanceTrend).toBeLessThanOrEqual(1);
    });

    test('should identify strengths from capabilities', () => {
      const agent = createMockAgent('agent-31', AgentTaxonomy.BACTERIA, 0.9, 0.8);
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const report = engine.monitorPerformance(agent);

      expect(report.strengths.length).toBeGreaterThan(0);
    });

    test('should identify weaknesses from limitations', () => {
      const agent = createMockAgent('agent-32', AgentTaxonomy.BACTERIA, 0.3, 0.2);
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const report = engine.monitorPerformance(agent);

      expect(report.weaknesses.length).toBeGreaterThan(0);
    });

    test('should generate improvement recommendations', () => {
      const agent = createMockAgent('agent-33', AgentTaxonomy.BACTERIA, 0.4, 0.3);
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const report = engine.monitorPerformance(agent);

      expect(report.recommendations).toBeDefined();
      expect(report.recommendations.length).toBeGreaterThan(0);
    });

    test('should store performance report', () => {
      const agent = createMockAgent('agent-34');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);

      const reports = engine['performanceReports'].get(agent.id);
      expect(reports).toBeDefined();
      expect(reports!.length).toBeGreaterThan(0);
    });

    test('should calculate performance trend', () => {
      const agent = createMockAgent('agent-35');
      const snapshot = createMockSnapshot([agent]);

      // Build model multiple times to create history
      for (let i = 0; i < 5; i++) {
        engine.buildSelfModel(agent, snapshot);
      }

      const report = engine.monitorPerformance(agent);
      expect(report.performanceTrend).toBeDefined();
    });

    test('should emit event on performance monitoring', (done) => {
      const agent = createMockAgent('agent-36');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);

      engine.on('performance_monitored', (data) => {
        expect(data.agentId).toBe('agent-36');
        expect(data.report).toBeDefined();
        done();
      });

      engine.monitorPerformance(agent);
    });

    test('should throw error when no self-model exists', () => {
      const agent = createMockAgent('agent-37');

      expect(() => engine.monitorPerformance(agent)).toThrow('No self-model found');
    });
  });

  // ==========================================================================
  // BLIND SPOT DETECTION TESTS
  // ==========================================================================

  describe('Blind Spot Detection', () => {
    test('should detect blind spots', () => {
      const agent = createMockAgent('agent-40');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const blindSpots = engine.detectBlindSpots(agent, snapshot);

      expect(Array.isArray(blindSpots)).toBe(true);
    });

    test('should detect context gaps', () => {
      const agent = createMockAgent('agent-41');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const blindSpots = engine.detectBlindSpots(agent, snapshot);

      const contextGaps = blindSpots.filter(bs => bs.discoveryMethod === 'context_gap');
      expect(contextGaps.length).toBeGreaterThan(0);
    });

    test('should detect performance anomalies', () => {
      const agent = createMockAgent('agent-42');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const blindSpots = engine.detectBlindSpots(agent, snapshot);

      expect(blindSpots).toBeDefined();
    });

    test('should provide mitigation suggestions', () => {
      const agent = createMockAgent('agent-43');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const blindSpots = engine.detectBlindSpots(agent, snapshot);

      for (const blindSpot of blindSpots) {
        expect(blindSpot.mitigations).toBeDefined();
        expect(Array.isArray(blindSpot.mitigations)).toBe(true);
      }
    });

    test('should store blind spots', () => {
      const agent = createMockAgent('agent-44');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);

      const stored = engine.getBlindSpots(agent.id);
      expect(stored).toBeDefined();
    });

    test('should filter by sensitivity threshold', () => {
      const agent = createMockAgent('agent-45');
      const snapshot = createMockSnapshot([agent]);

      engine.updateConfig({ blindSpotSensitivity: 0.9 });
      engine.buildSelfModel(agent, snapshot);
      const blindSpots = engine.detectBlindSpots(agent, snapshot);

      for (const blindSpot of blindSpots) {
        expect(blindSpot.confidence).toBeGreaterThanOrEqual(0.9);
      }
    });

    test('should emit event on blind spot detection', (done) => {
      const agent = createMockAgent('agent-46');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);

      engine.on('blind_spots_detected', (data) => {
        expect(data.agentId).toBe('agent-46');
        expect(data.blindSpots).toBeDefined();
        done();
      });

      engine.detectBlindSpots(agent, snapshot);
    });

    test('should update statistics', () => {
      const agent = createMockAgent('agent-47');
      const snapshot = createMockSnapshot([agent]);

      const initialStats = engine.getStats();
      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);
      const finalStats = engine.getStats();

      expect(finalStats.blindSpotsDiscovered).toBeGreaterThanOrEqual(initialStats.blindSpotsDiscovered);
    });

    test('should merge blind spots avoiding duplicates', () => {
      const agent = createMockAgent('agent-48');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);
      const count1 = engine.getBlindSpots(agent.id).length;

      engine.detectBlindSpots(agent, snapshot);
      const count2 = engine.getBlindSpots(agent.id).length;

      // Should not double blindly duplicate
      expect(count2).toBeLessThanOrEqual(count1 * 2);
    });
  });

  // ==========================================================================
  // THEORY OF MIND TESTS
  // ==========================================================================

  describe('Theory of Mind', () => {
    test('should model other agents mental states', () => {
      const observer = createMockAgent('observer-50');
      const target1 = createMockAgent('target-50a');
      const target2 = createMockAgent('target-50b');
      const snapshot = createMockSnapshot([observer, target1, target2]);

      const mentalStates = engine.modelOtherAgents(observer, [target1, target2], snapshot);

      expect(mentalStates.size).toBe(2);
      expect(mentalStates.has('target-50a')).toBe(true);
      expect(mentalStates.has('target-50b')).toBe(true);
    });

    test('should infer beliefs from capabilities', () => {
      const observer = createMockAgent('observer-51');
      const target = createMockAgent('target-51');
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-51');

      expect(state?.beliefs.size).toBeGreaterThan(0);
    });

    test('should infer desires from metabolism', () => {
      const observer = createMockAgent('observer-52');
      const target = createMockAgent('target-52');
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-52');

      expect(state?.desires.size).toBeGreaterThan(0);
    });

    test('should infer intentions from taxonomy', () => {
      const observer = createMockAgent('observer-53');
      const target = createMockAgent('target-53', AgentTaxonomy.EXPLORER);
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-53');

      expect(state?.intentions.has('explore')).toBe(true);
      expect(state?.intentions.get('explore')).toBeGreaterThan(0.7);
    });

    test('should infer emotions from lifecycle', () => {
      const observer = createMockAgent('observer-54');
      const target = createMockAgent('target-54', AgentTaxonomy.BACTERIA, 0.8);
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-54');

      expect(state?.emotions.has('energy')).toBe(true);
      expect(state?.emotions.get('energy')).toBeCloseTo(0.8);
    });

    test('should generate goals from intentions', () => {
      const observer = createMockAgent('observer-55');
      const target = createMockAgent('target-55');
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-55');

      expect(state?.goals.length).toBeGreaterThan(0);
      expect(state?.goals[0].status).toBe(GoalStatus.IN_PROGRESS);
    });

    test('should calculate inference confidence', () => {
      const observer = createMockAgent('observer-56');
      const target = createMockAgent('target-56');
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-56');

      expect(state?.confidence).toBeGreaterThanOrEqual(0);
      expect(state?.confidence).toBeLessThanOrEqual(1);
    });

    test('should not model observer itself', () => {
      const observer = createMockAgent('observer-57');
      const snapshot = createMockSnapshot([observer]);

      const mentalStates = engine.modelOtherAgents(observer, [observer], snapshot);

      expect(mentalStates.size).toBe(0);
    });

    test('should store mental states', () => {
      const observer = createMockAgent('observer-58');
      const target = createMockAgent('target-58');
      const snapshot = createMockSnapshot([observer, target]);

      engine.modelOtherAgents(observer, [target], snapshot);

      const stored = engine.getMentalState('target-58');
      expect(stored).toBeDefined();
    });

    test('should emit event on mental state modeling', (done) => {
      const observer = createMockAgent('observer-59');
      const target = createMockAgent('target-59');
      const snapshot = createMockSnapshot([observer, target]);

      engine.on('mental_states_modeled', (data) => {
        expect(data.observerId).toBe('observer-59');
        expect(data.mentalStates.size).toBe(1);
        done();
      });

      engine.modelOtherAgents(observer, [target], snapshot);
    });

    test('should update theory of mind statistics', () => {
      const observer = createMockAgent('observer-60');
      const targets = [
        createMockAgent('target-60a'),
        createMockAgent('target-60b'),
      ];
      const snapshot = createMockSnapshot([observer, ...targets]);

      const initialStats = engine.getStats();
      engine.modelOtherAgents(observer, targets, snapshot);
      const finalStats = engine.getStats();

      expect(finalStats.theoryOfMindInferences).toBe(initialStats.theoryOfMindInferences + 2);
    });
  });

  // ==========================================================================
  // REFLECTIVE REASONING TESTS
  // ==========================================================================

  describe('Reflective Reasoning', () => {
    test('should reflect on experience and generate insights', () => {
      const agent = createMockAgent('agent-70');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();

      engine.buildSelfModel(agent, snapshot);
      const insights = engine.reflect(agent, experience);

      expect(Array.isArray(insights)).toBe(true);
      expect(insights.length).toBeGreaterThan(0);
    });

    test('should generate self-discovery insights from positive outcomes', () => {
      const agent = createMockAgent('agent-71');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();
      experience.outcomes.set('unexpected_success', 0.9);

      engine.buildSelfModel(agent, snapshot);
      const insights = engine.reflect(agent, experience);

      const selfDiscoveries = insights.filter(i => i.type === InsightType.SELF_DISCOVERY);
      expect(selfDiscoveries.length).toBeGreaterThan(0);
    });

    test('should generate improvement insights from negative outcomes', () => {
      const agent = createMockAgent('agent-72');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();
      experience.outcomes.set('poor_performance', 0.2);

      engine.buildSelfModel(agent, snapshot);
      const insights = engine.reflect(agent, experience);

      const improvements = insights.filter(i => i.type === InsightType.IMPROVEMENT);
      expect(improvements.length).toBeGreaterThan(0);
    });

    test('should detect pattern novelties', () => {
      const agent = createMockAgent('agent-73');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();
      experience.actions = ['novel_action_xyz'];

      engine.buildSelfModel(agent, snapshot);
      const insights = engine.reflect(agent, experience);

      const patterns = insights.filter(i => i.type === InsightType.PATTERN_RECOGNITION);
      expect(patterns.length).toBeGreaterThan(0);
    });

    test('should check value alignment', () => {
      const agent = createMockAgent('agent-74');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();
      experience.outcomes.set('cooperation', 0.8);

      engine.buildSelfModel(agent, snapshot);
      const insights = engine.reflect(agent, experience);

      const valueAlignments = insights.filter(i => i.type === InsightType.VALUE_ALIGNMENT);
      expect(valueAlignments.length).toBeGreaterThan(0);
    });

    test('should store insights', () => {
      const agent = createMockAgent('agent-75');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();

      engine.buildSelfModel(agent, snapshot);
      engine.reflect(agent, experience);

      const stored = engine.getInsights(agent.id);
      expect(stored).toBeDefined();
      expect(stored.length).toBeGreaterThan(0);
    });

    test('should limit insight history size', () => {
      const agent = createMockAgent('agent-76');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);

      // Generate many insights
      for (let i = 0; i < 150; i++) {
        const experience = createMockExperience();
        engine.reflect(agent, experience);
      }

      const stored = engine.getInsights(agent.id);
      expect(stored.length).toBeLessThanOrEqual(100);
    });

    test('should emit event on reflection complete', (done) => {
      const agent = createMockAgent('agent-77');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();

      engine.buildSelfModel(agent, snapshot);

      engine.on('reflection_complete', (data) => {
        expect(data.agentId).toBe('agent-77');
        expect(data.experience).toBeDefined();
        expect(data.insights).toBeDefined();
        done();
      });

      engine.reflect(agent, experience);
    });

    test('should update statistics', () => {
      const agent = createMockAgent('agent-78');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();

      const initialStats = engine.getStats();
      engine.buildSelfModel(agent, snapshot);
      engine.reflect(agent, experience);
      const finalStats = engine.getStats();

      expect(finalStats.insightsGenerated).toBeGreaterThan(initialStats.insightsGenerated);
    });
  });

  // ==========================================================================
  // SELF-OPTIMIZATION TESTS
  // ==========================================================================

  describe('Self-Optimization', () => {
    test('should generate optimization plan', () => {
      const agent = createMockAgent('agent-80', AgentTaxonomy.BACTERIA, 0.5, 0.4);
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.detectBlindSpots(agent, snapshot);

      const plan = engine.optimizeSelf(agent);

      expect(plan).toBeDefined();
      expect(plan.agentId).toBe('agent-80');
      expect(plan.strategies).toBeDefined();
      expect(plan.expectedImprovement).toBeGreaterThanOrEqual(0);
    });

    test('should create strategies from weaknesses', () => {
      const agent = createMockAgent('agent-81', AgentTaxonomy.BACTERIA, 0.3, 0.2);
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);

      const plan = engine.optimizeSelf(agent);

      expect(plan.strategies.length).toBeGreaterThan(0);
    });

    test('should create strategies from blind spots', () => {
      const agent = createMockAgent('agent-82');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.detectBlindSpots(agent, snapshot);

      const plan = engine.optimizeSelf(agent);

      expect(plan.strategies.length).toBeGreaterThan(0);
    });

    test('should calculate expected improvement', () => {
      const agent = createMockAgent('agent-83');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.detectBlindSpots(agent, snapshot);

      const plan = engine.optimizeSelf(agent);

      expect(plan.expectedImprovement).toBeGreaterThanOrEqual(0);
      expect(plan.expectedImprovement).toBeLessThanOrEqual(1);
    });

    test('should store optimization plan', () => {
      const agent = createMockAgent('agent-84');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.detectBlindSpots(agent, snapshot);

      engine.optimizeSelf(agent);

      const plans = engine.getOptimizationPlans(agent.id);
      expect(plans).toBeDefined();
      expect(plans.length).toBeGreaterThan(0);
    });

    test('should limit optimization plan history', () => {
      const agent = createMockAgent('agent-85');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);

      // Generate many plans
      for (let i = 0; i < 15; i++) {
        engine.optimizeSelf(agent);
      }

      const plans = engine.getOptimizationPlans(agent.id);
      expect(plans.length).toBeLessThanOrEqual(10);
    });

    test('should emit event on plan creation', (done) => {
      const agent = createMockAgent('agent-86');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);

      engine.on('optimization_plan_created', (data) => {
        expect(data.agentId).toBe('agent-86');
        expect(data.plan).toBeDefined();
        done();
      });

      engine.optimizeSelf(agent);
    });

    test('should throw error when no performance report exists', () => {
      const agent = createMockAgent('agent-87');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);

      expect(() => engine.optimizeSelf(agent)).toThrow('No performance report available');
    });

    test('should update statistics', () => {
      const agent = createMockAgent('agent-88');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.detectBlindSpots(agent, snapshot);

      const initialStats = engine.getStats();
      engine.optimizeSelf(agent);
      const finalStats = engine.getStats();

      expect(finalStats.optimizationsSuggested).toBe(initialStats.optimizationsSuggested + 1);
    });
  });

  // ==========================================================================
  // CONFIGURATION TESTS
  // ==========================================================================

  describe('Configuration', () => {
    test('should get configuration', () => {
      const config = engine.getConfig();

      expect(config).toBeDefined();
      expect(config.enabled).toBe(true);
      expect(config.blindSpotSensitivity).toBeDefined();
      expect(config.theoryOfMindDepth).toBeDefined();
    });

    test('should update configuration', () => {
      engine.updateConfig({ blindSpotSensitivity: 0.95 });

      const config = engine.getConfig();
      expect(config.blindSpotSensitivity).toBe(0.95);
    });

    test('should enable and disable', () => {
      expect(engine.isEnabled()).toBe(true);

      engine.setEnabled(false);
      expect(engine.isEnabled()).toBe(false);

      engine.setEnabled(true);
      expect(engine.isEnabled()).toBe(true);
    });

    test('should emit event on config update', (done) => {
      engine.on('config_updated', (config) => {
        expect(config.blindSpotSensitivity).toBe(0.99);
        done();
      });

      engine.updateConfig({ blindSpotSensitivity: 0.99 });
    });

    test('should emit event on enabled change', (done) => {
      engine.on('enabled_changed', (data) => {
        expect(data.enabled).toBe(false);
        done();
      });

      engine.setEnabled(false);
    });
  });

  // ==========================================================================
  // STATISTICS TESTS
  // ==========================================================================

  describe('Statistics', () => {
    test('should get initial statistics', () => {
      const stats = engine.getStats();

      expect(stats).toBeDefined();
      expect(stats.modelsBuilt).toBe(0);
      expect(stats.predictionsMade).toBe(0);
      expect(stats.blindSpotsDiscovered).toBe(0);
      expect(stats.insightsGenerated).toBe(0);
    });

    test('should track models built', () => {
      const agent = createMockAgent('agent-100');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const stats = engine.getStats();

      expect(stats.modelsBuilt).toBe(1);
    });

    test('should track predictions made', () => {
      const agent = createMockAgent('agent-101');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      engine.predictOwnBehavior(agent, situation);
      const stats = engine.getStats();

      expect(stats.predictionsMade).toBe(1);
    });

    test('should track blind spots discovered', () => {
      const agent = createMockAgent('agent-102');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);
      const stats = engine.getStats();

      expect(stats.blindSpotsDiscovered).toBeGreaterThan(0);
    });

    test('should track insights generated', () => {
      const agent = createMockAgent('agent-103');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();

      engine.buildSelfModel(agent, snapshot);
      engine.reflect(agent, experience);
      const stats = engine.getStats();

      expect(stats.insightsGenerated).toBeGreaterThan(0);
    });

    test('should track theory of mind inferences', () => {
      const observer = createMockAgent('agent-104');
      const targets = [createMockAgent('target-104a')];
      const snapshot = createMockSnapshot([observer, ...targets]);

      engine.modelOtherAgents(observer, targets, snapshot);
      const stats = engine.getStats();

      expect(stats.theoryOfMindInferences).toBe(1);
    });

    test('should track optimizations suggested', () => {
      const agent = createMockAgent('agent-105');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.optimizeSelf(agent);
      const stats = engine.getStats();

      expect(stats.optimizationsSuggested).toBe(1);
    });

    test('should calculate average awareness level', () => {
      const agents = [
        createMockAgent('agent-106a'),
        createMockAgent('agent-106b'),
        createMockAgent('agent-106c'),
      ];
      const snapshot = createMockSnapshot(agents);

      for (const agent of agents) {
        engine.buildSelfModel(agent, snapshot);
      }

      const stats = engine.getStats();
      expect(stats.avgAwarenessLevel).toBeGreaterThan(0);
    });
  });

  // ==========================================================================
  // DATA MANAGEMENT TESTS
  // ==========================================================================

  describe('Data Management', () => {
    test('should get self-model', () => {
      const agent = createMockAgent('agent-120');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const model = engine.getSelfModel(agent.id);

      expect(model).toBeDefined();
      expect(model?.agentId).toBe('agent-120');
    });

    test('should get all self-models', () => {
      const agents = [
        createMockAgent('agent-121a'),
        createMockAgent('agent-121b'),
      ];
      const snapshot = createMockSnapshot(agents);

      for (const agent of agents) {
        engine.buildSelfModel(agent, snapshot);
      }

      const models = engine.getAllSelfModels();
      expect(models.size).toBe(2);
    });

    test('should get prediction history', () => {
      const agent = createMockAgent('agent-122');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      engine.predictOwnBehavior(agent, situation);

      const history = engine.getPredictionHistory(agent.id);
      expect(history.length).toBe(1);
    });

    test('should get blind spots', () => {
      const agent = createMockAgent('agent-123');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);

      const blindSpots = engine.getBlindSpots(agent.id);
      expect(blindSpots).toBeDefined();
    });

    test('should get mental state', () => {
      const observer = createMockAgent('agent-124');
      const target = createMockAgent('target-124');
      const snapshot = createMockSnapshot([observer, target]);

      engine.modelOtherAgents(observer, [target], snapshot);

      const state = engine.getMentalState('target-124');
      expect(state).toBeDefined();
    });

    test('should get insights', () => {
      const agent = createMockAgent('agent-125');
      const snapshot = createMockSnapshot([agent]);
      const experience = createMockExperience();

      engine.buildSelfModel(agent, snapshot);
      engine.reflect(agent, experience);

      const insights = engine.getInsights(agent.id);
      expect(insights).toBeDefined();
    });

    test('should get optimization plans', () => {
      const agent = createMockAgent('agent-126');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.monitorPerformance(agent);
      engine.optimizeSelf(agent);

      const plans = engine.getOptimizationPlans(agent.id);
      expect(plans).toBeDefined();
    });

    test('should clear agent data', () => {
      const agent = createMockAgent('agent-127');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.clearAgentData(agent.id);

      const model = engine.getSelfModel(agent.id);
      expect(model).toBeUndefined();
    });

    test('should clear all data', () => {
      const agents = [
        createMockAgent('agent-128a'),
        createMockAgent('agent-128b'),
      ];
      const snapshot = createMockSnapshot(agents);

      for (const agent of agents) {
        engine.buildSelfModel(agent, snapshot);
      }

      engine.clearAllData();

      const models = engine.getAllSelfModels();
      expect(models.size).toBe(0);

      const stats = engine.getStats();
      expect(stats.avgAwarenessLevel).toBe(0);
    });
  });

  // ==========================================================================
  // ETHICAL CONSIDERATIONS TESTS
  // ==========================================================================

  describe('Ethical Considerations', () => {
    test('should ensure value alignment in self-model', () => {
      const agent = createMockAgent('agent-140');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      expect(model.values).toBeDefined();
      expect(model.values.alignment).toBe(1.0); // Fully aligned
    });

    test('should use self-awareness for safety (blind spots)', () => {
      const agent = createMockAgent('agent-141');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      const blindSpots = engine.detectBlindSpots(agent, snapshot);

      // Blind spots help identify safety concerns
      expect(blindSpots).toBeDefined();
      expect(Array.isArray(blindSpots)).toBe(true);
    });

    test('should use theory of mind for empathy', () => {
      const observer = createMockAgent('agent-142');
      const target = createMockAgent('target-142', AgentTaxonomy.BACTERIA, 0.3);
      const snapshot = createMockSnapshot([observer, target]);

      const mentalStates = engine.modelOtherAgents(observer, [target], snapshot);
      const state = mentalStates.get('target-142');

      // Should model target's low energy/emotional state
      expect(state?.emotions.get('energy')).toBeCloseTo(0.3);
    });

    test('should provide mitigations for limitations', () => {
      const agent = createMockAgent('agent-143', AgentTaxonomy.BACTERIA, 0.3, 0.2);
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      for (const limitation of model.limitations) {
        expect(limitation.mitigations).toBeDefined();
        expect(limitation.mitigations.length).toBeGreaterThan(0);
      }
    });

    test('should ensure transparency through events', (done) => {
      const agent = createMockAgent('agent-144');
      const snapshot = createMockSnapshot([agent]);

      let eventCount = 0;
      const checkDone = () => {
        eventCount++;
        if (eventCount >= 2) done();
      };

      engine.on('self_model_updated', checkDone);
      engine.on('blind_spots_detected', checkDone);

      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);
    });

    test('should maintain accountability through tracking', () => {
      const agent = createMockAgent('agent-145');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      const prediction = engine.predictOwnBehavior(agent, situation);

      // Predictions are tracked and can be validated
      expect(prediction.id).toBeDefined();
      expect(prediction.timestamp).toBeDefined();

      const validation = engine.validatePrediction(agent.id, prediction.id, 0.8);
      expect(validation.accuracy).toBeDefined();
    });
  });

  // ==========================================================================
  // AWARENESS LEVEL TESTS
  // ==========================================================================

  describe('Awareness Level Progression', () => {
    test('should start at PERFORMANCE level with history', () => {
      const agent = createMockAgent('agent-160');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      expect(model.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.PERFORMANCE);
    });

    test('should reach MODELING level with capabilities', () => {
      const agent = createMockAgent('agent-161');
      const snapshot = createMockSnapshot([agent]);

      const model = engine.buildSelfModel(agent, snapshot);

      expect(model.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.MODELING);
    });

    test('should reach PREDICTION level after predictions', () => {
      const agent = createMockAgent('agent-162');
      const snapshot = createMockSnapshot([agent]);
      const situation = createMockSituation();

      engine.buildSelfModel(agent, snapshot);
      engine.predictOwnBehavior(agent, situation);

      const model = engine.getSelfModel(agent.id);
      expect(model?.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.PREDICTION);
    });

    test('should reach BLIND_SPOTS level after detection', () => {
      const agent = createMockAgent('agent-163');
      const snapshot = createMockSnapshot([agent]);

      engine.buildSelfModel(agent, snapshot);
      engine.detectBlindSpots(agent, snapshot);

      const model = engine.getSelfModel(agent.id);
      expect(model?.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.BLIND_SPOTS);
    });

    test('should reach THEORY_OF_MIND level after modeling others', () => {
      const observer = createMockAgent('agent-164');
      const target = createMockAgent('target-164');
      const snapshot = createMockSnapshot([observer, target]);

      engine.buildSelfModel(observer, snapshot);
      engine.modelOtherAgents(observer, [target], snapshot);

      const model = engine.getSelfModel(observer.id);
      expect(model?.awarenessLevel).toBeGreaterThanOrEqual(AwarenessLevel.THEORY_OF_MIND);
    });
  });

  // ==========================================================================
  // INTEGRATION TESTS
  // ==========================================================================

  describe('Integration with Meta-Learning', () => {
    test('should use meta-learning for context assessment', () => {
      const agent = createMockAgent('agent-180');
      const snapshot = createMockSnapshot([agent]);

      // Build self-model (may use meta-learning internally)
      const model = engine.buildSelfModel(agent, snapshot);

      expect(model).toBeDefined();
      expect(model.capabilities).toBeDefined();
    });

    test('should work with meta-learning engine', () => {
      const integratedEngine = new SelfAwarenessEngine(metaLearning);
      const agent = createMockAgent('agent-181');
      const snapshot = createMockSnapshot([agent]);

      expect(() => integratedEngine.buildSelfModel(agent, snapshot)).not.toThrow();
    });
  });
});

// ============================================================================
// RUN TESTS
// ============================================================================
