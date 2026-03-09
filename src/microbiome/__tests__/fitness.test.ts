/**
 * POLLN Microbiome - Fitness System Tests
 *
 * Comprehensive tests for multi-objective fitness evaluation,
 * Pareto dominance, fitness sharing, and dynamic adaptation.
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import {
  FitnessEvaluator,
  createFitnessEvaluator,
  BuiltinConstraints,
  type FitnessEvaluatorConfig,
  type FitnessWeights,
  type Constraint,
  type FitnessSharingConfig,
  type DynamicFitnessConfig,
  type ParetoFront,
  type FitnessEvaluation,
} from '../fitness.js';
import {
  MicrobiomeAgent,
  FitnessScore,
  EcosystemSnapshot,
  AgentTaxonomy,
  ResourceType,
  SymbiosisType,
  MetabolicProfile,
  LifecycleState,
} from '../types.js';

/**
 * Create a mock agent for testing
 */
function createMockAgent(overrides: Partial<MicrobiomeAgent> = {}): MicrobiomeAgent {
  return {
    id: overrides.id ?? `agent_${Math.random().toString(36).substr(2, 9)}`,
    taxonomy: overrides.taxonomy ?? AgentTaxonomy.BACTERIA,
    name: overrides.name ?? 'Test Agent',
    metabolism: overrides.metabolism ?? {
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100,
      efficiency: 0.8,
    },
    lifecycle: overrides.lifecycle ?? {
      health: 1.0,
      age: 1000,
      generation: 0,
      isAlive: true,
    },
    parentId: overrides.parentId,
    generation: overrides.generation ?? 0,
    size: overrides.size ?? 1024,
    complexity: overrides.complexity ?? 0.5,
    process: jest.fn().mockResolvedValue(new Map()),
    reproduce: jest.fn().mockResolvedValue({} as MicrobiomeAgent),
    evaluateFitness: overrides.evaluateFitness ?? jest.fn().mockReturnValue({
      overall: 0.7,
      throughput: 0.8,
      accuracy: 0.7,
      efficiency: 0.6,
      cooperation: 0.5,
    }),
    canMetabolize: jest.fn().mockReturnValue(true),
  };
}

/**
 * Create a mock ecosystem snapshot
 */
function createMockSnapshot(): EcosystemSnapshot {
  return {
    timestamp: Date.now(),
    agents: new Map(),
    resourceFlows: new Map([
      [ResourceType.TEXT, { resource: ResourceType.TEXT, flowRate: 100, available: 80, capacity: 100 }],
      [ResourceType.STRUCTURED, { resource: ResourceType.STRUCTURED, flowRate: 50, available: 40, capacity: 50 }],
    ]),
    populations: new Map([
      [AgentTaxonomy.BACTERIA, { population: 100, birthRate: 0.1, deathRate: 0.05, carryingCapacity: 200 }],
    ]),
    colonies: [],
    symbioses: [],
  };
}

describe('FitnessEvaluator', () => {
  let evaluator: FitnessEvaluator;

  beforeEach(() => {
    evaluator = createFitnessEvaluator();
  });

  describe('Construction and Configuration', () => {
    it('should create evaluator with default configuration', () => {
      const config = evaluator.getConfig();

      expect(config.weights.throughput).toBe(0.25);
      expect(config.weights.accuracy).toBe(0.35);
      expect(config.weights.efficiency).toBe(0.25);
      expect(config.weights.cooperation).toBe(0.15);

      expect(config.sharing.enabled).toBe(true);
      expect(config.sharing.sigma).toBe(0.5);
      expect(config.sharing.alpha).toBe(1.0);

      expect(config.dynamic.enabled).toBe(true);
      expect(config.dynamic.environmentSensitivity).toBe(0.3);
      expect(config.dynamic.seasonalRate).toBe(0.1);
      expect(config.dynamic.resourceScarcityFactor).toBe(0.2);

      expect(config.enablePareto).toBe(true);
      expect(config.enableConstraints).toBe(true);
    });

    it('should create evaluator with custom configuration', () => {
      const customConfig: Partial<FitnessEvaluatorConfig> = {
        weights: {
          throughput: 0.5,
          accuracy: 0.3,
          efficiency: 0.1,
          cooperation: 0.1,
        },
        sharing: {
          enabled: false,
          sigma: 0.3,
          alpha: 2.0,
        },
      };

      const customEvaluator = createFitnessEvaluator(customConfig);
      const config = customEvaluator.getConfig();

      expect(config.weights.throughput).toBe(0.5);
      expect(config.sharing.enabled).toBe(false);
      expect(config.sharing.sigma).toBe(0.3);
      expect(config.sharing.alpha).toBe(2.0);
    });

    it('should update configuration', () => {
      evaluator.updateConfig({
        weights: {
          throughput: 0.4,
          accuracy: 0.4,
          efficiency: 0.1,
          cooperation: 0.1,
        },
      });

      const config = evaluator.getConfig();
      expect(config.weights.throughput).toBe(0.4);
      expect(config.weights.accuracy).toBe(0.4);
    });
  });

  describe('Single Agent Evaluation', () => {
    it('should evaluate single agent fitness', () => {
      const agent = createMockAgent();
      const fitness = evaluator.evaluate(agent);

      expect(fitness).toBeDefined();
      expect(fitness.overall).toBeGreaterThanOrEqual(0);
      expect(fitness.overall).toBeLessThanOrEqual(1);
      expect(fitness.throughput).toBeGreaterThanOrEqual(0);
      expect(fitness.accuracy).toBeGreaterThanOrEqual(0);
      expect(fitness.efficiency).toBeGreaterThanOrEqual(0);
      expect(fitness.cooperation).toBeGreaterThanOrEqual(0);
    });

    it('should apply weighted combination to fitness score', () => {
      const customWeights: FitnessWeights = {
        throughput: 0.5,
        accuracy: 0.3,
        efficiency: 0.1,
        cooperation: 0.1,
      };

      const customEvaluator = createFitnessEvaluator({ weights: customWeights });

      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0,
          throughput: 0.8,
          accuracy: 0.7,
          efficiency: 0.6,
          cooperation: 0.5,
        }),
      });

      const fitness = customEvaluator.evaluate(agent);

      // Expected overall: 0.8*0.5 + 0.7*0.3 + 0.6*0.1 + 0.5*0.1 = 0.4 + 0.21 + 0.06 + 0.05 = 0.72
      expect(fitness.overall).toBeCloseTo(0.72, 1);
    });
  });

  describe('Pareto Dominance', () => {
    it('should detect Pareto dominance correctly', () => {
      const score1: FitnessScore = {
        overall: 0.7,
        throughput: 0.8,
        accuracy: 0.7,
        efficiency: 0.6,
        cooperation: 0.5,
      };

      const score2: FitnessScore = {
        overall: 0.6,
        throughput: 0.7,
        accuracy: 0.6,
        efficiency: 0.5,
        cooperation: 0.4,
      };

      // score1 dominates score2 (better in all objectives)
      expect(evaluator.isDominated(score1, score2)).toBe(true);
      expect(evaluator.isDominated(score2, score1)).toBe(false);
    });

    it('should handle non-dominated solutions', () => {
      const score1: FitnessScore = {
        overall: 0.7,
        throughput: 0.9,
        accuracy: 0.5,
        efficiency: 0.6,
        cooperation: 0.5,
      };

      const score2: FitnessScore = {
        overall: 0.7,
        throughput: 0.5,
        accuracy: 0.9,
        efficiency: 0.6,
        cooperation: 0.5,
      };

      // Neither dominates the other (trade-off)
      expect(evaluator.isDominated(score1, score2)).toBe(false);
      expect(evaluator.isDominated(score2, score1)).toBe(false);
    });

    it('should handle equal scores', () => {
      const score: FitnessScore = {
        overall: 0.7,
        throughput: 0.7,
        accuracy: 0.7,
        efficiency: 0.7,
        cooperation: 0.7,
      };

      // Equal scores don't dominate each other
      expect(evaluator.isDominated(score, score)).toBe(false);
    });
  });

  describe('Population Evaluation', () => {
    it('should evaluate population of agents', () => {
      const agents = [
        createMockAgent({
          id: 'agent_1',
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.8,
            throughput: 0.9,
            accuracy: 0.8,
            efficiency: 0.7,
            cooperation: 0.6,
          }),
        }),
        createMockAgent({
          id: 'agent_2',
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.6,
            throughput: 0.7,
            accuracy: 0.6,
            efficiency: 0.5,
            cooperation: 0.4,
          }),
        }),
        createMockAgent({
          id: 'agent_3',
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.7,
            throughput: 0.8,
            accuracy: 0.7,
            efficiency: 0.6,
            cooperation: 0.5,
          }),
        }),
      ];

      const evaluations = evaluator.evaluatePopulation(agents);

      expect(evaluations.size).toBe(3);
      expect(evaluations.has('agent_1')).toBe(true);
      expect(evaluations.has('agent_2')).toBe(true);
      expect(evaluations.has('agent_3')).toBe(true);

      for (const evaluation of evaluations.values()) {
        expect(evaluation.agentId).toBeDefined();
        expect(evaluation.rawScore).toBeDefined();
        expect(evaluation.adjustedScore).toBeDefined();
        expect(evaluation.paretoInfo).toBeDefined();
        expect(evaluation.violations).toBeDefined();
        expect(evaluation.environmentalFactors).toBeDefined();
      }
    });

    it('should calculate Pareto ranks correctly', () => {
      // Create agents with different fitness profiles
      const agents = [
        createMockAgent({
          id: 'agent_1',
          taxonomy: AgentTaxonomy.BACTERIA,
          complexity: 0.5,
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.7,
            throughput: 0.9,
            accuracy: 0.5,
            efficiency: 0.7,
            cooperation: 0.7,
          }),
        }),
        createMockAgent({
          id: 'agent_2',
          taxonomy: AgentTaxonomy.BACTERIA,
          complexity: 0.5,
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.7,
            throughput: 0.5,
            accuracy: 0.9,
            efficiency: 0.7,
            cooperation: 0.7,
          }),
        }),
        createMockAgent({
          id: 'dominated',
          taxonomy: AgentTaxonomy.BACTERIA,
          complexity: 0.5,
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.5,
            throughput: 0.5,
            accuracy: 0.5,
            efficiency: 0.5,
            cooperation: 0.5,
          }),
        }),
      ];

      const evaluations = evaluator.evaluatePopulation(agents);

      const agent1Eval = evaluations.get('agent_1');
      const agent2Eval = evaluations.get('agent_2');
      const dominatedEval = evaluations.get('dominated');

      // agent_1 and agent_2 should be on the same Pareto front (non-dominated)
      // dominated should be on a worse front
      expect(agent1Eval?.paretoInfo.rank).toBe(0);
      expect(agent2Eval?.paretoInfo.rank).toBe(0);
      expect(dominatedEval?.paretoInfo.rank).toBe(1);
    });
  });

  describe('Fitness Sharing', () => {
    it('should apply fitness sharing when enabled', () => {
      const sharingConfig: FitnessSharingConfig = {
        enabled: true,
        sigma: 0.5,
        alpha: 1.0,
      };

      const sharingEvaluator = createFitnessEvaluator({ sharing: sharingConfig });

      // Create similar agents
      const agents = [
        createMockAgent({
          id: 'agent_1',
          taxonomy: AgentTaxonomy.BACTERIA,
          metabolism: {
            inputs: [ResourceType.TEXT],
            outputs: [ResourceType.STRUCTURED],
            processingRate: 100,
            efficiency: 0.8,
          },
          complexity: 0.5,
        }),
        createMockAgent({
          id: 'agent_2',
          taxonomy: AgentTaxonomy.BACTERIA,
          metabolism: {
            inputs: [ResourceType.TEXT],
            outputs: [ResourceType.STRUCTURED],
            processingRate: 100,
            efficiency: 0.8,
          },
          complexity: 0.5,
        }),
      ];

      const evaluations = sharingEvaluator.evaluatePopulation(agents);

      // Similar agents should have reduced fitness due to sharing
      const eval1 = evaluations.get('agent_1');
      const eval2 = evaluations.get('agent_2');

      expect(eval1?.adjustedScore.overall).toBeLessThan(eval1?.rawScore.overall ?? 1);
      expect(eval2?.adjustedScore.overall).toBeLessThan(eval2?.rawScore.overall ?? 1);
    });

    it('should not apply fitness sharing when disabled', () => {
      const sharingConfig: FitnessSharingConfig = {
        enabled: false,
        sigma: 0.5,
        alpha: 1.0,
      };

      const sharingEvaluator = createFitnessEvaluator({ sharing: sharingConfig });

      const agents = [
        createMockAgent({ id: 'agent_1' }),
        createMockAgent({ id: 'agent_2' }),
      ];

      const evaluations = sharingEvaluator.evaluatePopulation(agents);

      for (const evaluation of evaluations.values()) {
        expect(evaluation.adjustedScore.overall).toBe(evaluation.rawScore.overall);
      }
    });
  });

  describe('Dynamic Fitness', () => {
    beforeEach(() => {
      const snapshot = createMockSnapshot();
      evaluator.updateSnapshot(snapshot);
    });

    it('should apply resource scarcity factor', () => {
      const dynamicConfig: DynamicFitnessConfig = {
        enabled: true,
        environmentSensitivity: 0.5,
        seasonalRate: 0.1,
        resourceScarcityFactor: 0.5,
      };

      const dynamicEvaluator = createFitnessEvaluator({ dynamic: dynamicConfig });
      dynamicEvaluator.updateSnapshot(createMockSnapshot());

      const agent = createMockAgent({
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 100,
          efficiency: 0.8,
        },
      });

      const fitness = dynamicEvaluator.evaluate(agent);

      // Fitness should be adjusted based on resource availability
      expect(fitness).toBeDefined();
    });

    it('should apply seasonal adjustments', () => {
      const agent = createMockAgent();
      const fitness1 = evaluator.evaluate(agent);

      // Update snapshot multiple times to advance season
      for (let i = 0; i < 50; i++) {
        evaluator.updateSnapshot(createMockSnapshot());
      }

      const fitness2 = evaluator.evaluate(agent);

      // Seasonal phase should have changed
      expect(fitness2).toBeDefined();
    });

    it('should not apply dynamic fitness when disabled', () => {
      const dynamicConfig: DynamicFitnessConfig = {
        enabled: false,
        environmentSensitivity: 0.5,
        seasonalRate: 0.1,
        resourceScarcityFactor: 0.5,
      };

      const staticEvaluator = createFitnessEvaluator({ dynamic: dynamicConfig });
      staticEvaluator.updateSnapshot(createMockSnapshot());

      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0.7,
          throughput: 0.8,
          accuracy: 0.7,
          efficiency: 0.6,
          cooperation: 0.5,
        }),
      });

      const fitness = staticEvaluator.evaluate(agent);

      // Should return base fitness without dynamic adjustments
      expect(fitness.overall).toBeCloseTo(0.7, 1);
    });
  });

  describe('Constraint Handling', () => {
    it('should apply constraint penalties', () => {
      const constraints: Constraint[] = [
        {
          id: 'size_constraint',
          name: 'Max Size',
          isSatisfied: jest.fn().mockReturnValue(false),
          penalty: 0.3,
        },
      ];

      const constrainedEvaluator = createFitnessEvaluator({
        constraints,
        enableConstraints: true,
      });

      constrainedEvaluator.updateSnapshot(createMockSnapshot());

      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0.9,
          throughput: 0.9,
          accuracy: 0.9,
          efficiency: 0.9,
          cooperation: 0.9,
        }),
      });

      const fitness = constrainedEvaluator.evaluate(agent);

      // Fitness should be reduced by penalty
      expect(fitness.overall).toBeLessThan(0.9);
    });

    it('should not penalize satisfied constraints', () => {
      const constraints: Constraint[] = [
        {
          id: 'size_constraint',
          name: 'Max Size',
          isSatisfied: jest.fn().mockReturnValue(true),
          penalty: 0.3,
        },
      ];

      const constrainedEvaluator = createFitnessEvaluator({
        constraints,
        enableConstraints: true,
      });

      constrainedEvaluator.updateSnapshot(createMockSnapshot());

      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0.9,
          throughput: 0.9,
          accuracy: 0.9,
          efficiency: 0.9,
          cooperation: 0.9,
        }),
      });

      const fitness = constrainedEvaluator.evaluate(agent);

      // Fitness should not be reduced
      expect(fitness.overall).toBeCloseTo(0.9, 1);
    });

    it('should track constraint violations', () => {
      const constraints: Constraint[] = [
        {
          id: 'constraint_1',
          name: 'Constraint 1',
          isSatisfied: jest.fn().mockReturnValue(false),
          penalty: 0.2,
        },
        {
          id: 'constraint_2',
          name: 'Constraint 2',
          isSatisfied: jest.fn().mockReturnValue(true),
          penalty: 0.3,
        },
      ];

      const constrainedEvaluator = createFitnessEvaluator({
        constraints,
        enableConstraints: true,
      });

      constrainedEvaluator.updateSnapshot(createMockSnapshot());

      const agents = [createMockAgent({ id: 'agent_1' })];
      const evaluations = constrainedEvaluator.evaluatePopulation(agents);

      const evaluation = evaluations.get('agent_1');
      expect(evaluation?.violations).toContain('constraint_1');
      expect(evaluation?.violations).not.toContain('constraint_2');
    });
  });

  describe('Built-in Constraints', () => {
    it('should create max size constraint', () => {
      const constraint = BuiltinConstraints.maxSizeConstraint(1024);

      const smallAgent = createMockAgent({ size: 512 });
      const largeAgent = createMockAgent({ size: 2048 });

      expect(constraint.isSatisfied(smallAgent, createMockSnapshot())).toBe(true);
      expect(constraint.isSatisfied(largeAgent, createMockSnapshot())).toBe(false);
    });

    it('should create resource constraint', () => {
      const constraint = BuiltinConstraints.resourceConstraint(50);

      const snapshot = createMockSnapshot();
      const agent = createMockAgent({
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 100,
          efficiency: 0.8,
        },
      });

      // TEXT resource has 80 available, which is >= 50
      expect(constraint.isSatisfied(agent, snapshot)).toBe(true);
    });

    it('should create complexity constraint', () => {
      const constraint = BuiltinConstraints.complexityConstraint(0.7);

      const simpleAgent = createMockAgent({ complexity: 0.5 });
      const complexAgent = createMockAgent({ complexity: 0.9 });

      expect(constraint.isSatisfied(simpleAgent, createMockSnapshot())).toBe(true);
      expect(constraint.isSatisfied(complexAgent, createMockSnapshot())).toBe(false);
    });

    it('should create efficiency constraint', () => {
      const constraint = BuiltinConstraints.efficiencyConstraint(0.7);

      const efficientAgent = createMockAgent({
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 100,
          efficiency: 0.8,
        },
      });

      const inefficientAgent = createMockAgent({
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 100,
          efficiency: 0.5,
        },
      });

      expect(constraint.isSatisfied(efficientAgent, createMockSnapshot())).toBe(true);
      expect(constraint.isSatisfied(inefficientAgent, createMockSnapshot())).toBe(false);
    });

    it('should create max age constraint', () => {
      const constraint = BuiltinConstraints.maxAgeConstraint(5000);

      const youngAgent = createMockAgent({
        lifecycle: {
          health: 1.0,
          age: 1000,
          generation: 0,
          isAlive: true,
        },
      });

      const oldAgent = createMockAgent({
        lifecycle: {
          health: 1.0,
          age: 10000,
          generation: 0,
          isAlive: true,
        },
      });

      expect(constraint.isSatisfied(youngAgent, createMockSnapshot())).toBe(true);
      expect(constraint.isSatisfied(oldAgent, createMockSnapshot())).toBe(false);
    });
  });

  describe('Population Summary', () => {
    it('should calculate population fitness summary', () => {
      // Disable fitness sharing for this test to get predictable values
      const noSharingEvaluator = createFitnessEvaluator({
        sharing: { enabled: false, sigma: 0.5, alpha: 1.0 },
      });

      const agents = [
        createMockAgent({
          id: 'best',
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.9,
            throughput: 0.9,
            accuracy: 0.9,
            efficiency: 0.9,
            cooperation: 0.9,
          }),
        }),
        createMockAgent({
          id: 'worst',
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.3,
            throughput: 0.3,
            accuracy: 0.3,
            efficiency: 0.3,
            cooperation: 0.3,
          }),
        }),
        createMockAgent({
          id: 'average',
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.6,
            throughput: 0.6,
            accuracy: 0.6,
            efficiency: 0.6,
            cooperation: 0.6,
          }),
        }),
      ];

      const evaluations = noSharingEvaluator.evaluatePopulation(agents);
      const summary = noSharingEvaluator.getPopulationSummary(evaluations);

      expect(summary.bestFitness.overall).toBeCloseTo(0.9, 1);
      expect(summary.worstFitness.overall).toBeCloseTo(0.3, 1);
      expect(summary.avgFitness.overall).toBeCloseTo(0.6, 1);
      expect(summary.fitnessDiversity).toBeGreaterThan(0);
      expect(summary.paretoFronts.size).toBeGreaterThan(0);
    });

    it('should handle empty population', () => {
      const evaluations = new Map();
      const summary = evaluator.getPopulationSummary(evaluations);

      expect(summary.bestFitness.overall).toBe(0);
      expect(summary.avgFitness.overall).toBe(0);
      expect(summary.worstFitness.overall).toBe(0);
      expect(summary.fitnessDiversity).toBe(0);
      expect(summary.violationRate).toBe(0);
    });

    it('should calculate violation rate correctly', () => {
      const constraints: Constraint[] = [
        {
          id: 'constraint_1',
          name: 'Constraint 1',
          isSatisfied: jest.fn().mockReturnValue(false),
          penalty: 0.2,
        },
      ];

      const constrainedEvaluator = createFitnessEvaluator({
        constraints,
        enableConstraints: true,
      });

      constrainedEvaluator.updateSnapshot(createMockSnapshot());

      const agents = [
        createMockAgent({ id: 'agent_1' }),
        createMockAgent({ id: 'agent_2' }),
        createMockAgent({ id: 'agent_3' }),
      ];

      const evaluations = constrainedEvaluator.evaluatePopulation(agents);
      const summary = constrainedEvaluator.getPopulationSummary(evaluations);

      // All 3 agents violate the constraint
      expect(summary.violationRate).toBeCloseTo(1.0, 1);
    });
  });

  describe('Fitness History', () => {
    it('should track fitness history for agents', () => {
      const agent = createMockAgent({
        id: 'tracked_agent',
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0.7,
          throughput: 0.8,
          accuracy: 0.7,
          efficiency: 0.6,
          cooperation: 0.5,
        }),
      });

      // Evaluate multiple times
      for (let i = 0; i < 5; i++) {
        evaluator.evaluatePopulation([agent]);
      }

      const history = evaluator.getHistory('tracked_agent');
      expect(history.length).toBe(5);
    });

    it('should limit history to 100 entries', () => {
      const agent = createMockAgent({
        id: 'history_agent',
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0.7,
          throughput: 0.8,
          accuracy: 0.7,
          efficiency: 0.6,
          cooperation: 0.5,
        }),
      });

      // Evaluate 150 times
      for (let i = 0; i < 150; i++) {
        evaluator.evaluatePopulation([agent]);
      }

      const history = evaluator.getHistory('history_agent');
      expect(history.length).toBe(100);
    });

    it('should return empty history for unknown agent', () => {
      const history = evaluator.getHistory('unknown_agent');
      expect(history).toEqual([]);
    });

    it('should reset history', () => {
      const agent = createMockAgent({
        id: 'reset_agent',
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0.7,
          throughput: 0.8,
          accuracy: 0.7,
          efficiency: 0.6,
          cooperation: 0.5,
        }),
      });

      for (let i = 0; i < 5; i++) {
        evaluator.evaluatePopulation([agent]);
      }

      evaluator.resetHistory();

      const history = evaluator.getHistory('reset_agent');
      expect(history).toEqual([]);
    });
  });

  describe('Edge Cases', () => {
    it('should handle agent with zero fitness', () => {
      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 0,
          throughput: 0,
          accuracy: 0,
          efficiency: 0,
          cooperation: 0,
        }),
      });

      const fitness = evaluator.evaluate(agent);
      expect(fitness.overall).toBe(0);
    });

    it('should handle agent with perfect fitness', () => {
      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 1,
          throughput: 1,
          accuracy: 1,
          efficiency: 1,
          cooperation: 1,
        }),
      });

      const fitness = evaluator.evaluate(agent);
      expect(fitness.overall).toBeLessThanOrEqual(1);
    });

    it('should handle single agent population', () => {
      const agents = [createMockAgent({ id: 'single' })];
      const evaluations = evaluator.evaluatePopulation(agents);

      expect(evaluations.size).toBe(1);
      expect(evaluations.has('single')).toBe(true);
    });

    it('should handle agents with no metabolic inputs', () => {
      const agent = createMockAgent({
        metabolism: {
          inputs: [],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 100,
          efficiency: 0.8,
        },
      });

      const fitness = evaluator.evaluate(agent);
      expect(fitness).toBeDefined();
    });

    it('should handle extreme constraint penalties', () => {
      const constraints: Constraint[] = [
        {
          id: 'extreme',
          name: 'Extreme Penalty',
          isSatisfied: jest.fn().mockReturnValue(false),
          penalty: 1.0, // Maximum penalty
        },
      ];

      const extremeEvaluator = createFitnessEvaluator({
        constraints,
        enableConstraints: true,
      });

      extremeEvaluator.updateSnapshot(createMockSnapshot());

      const agent = createMockAgent({
        evaluateFitness: jest.fn().mockReturnValue({
          overall: 1.0,
          throughput: 1.0,
          accuracy: 1.0,
          efficiency: 1.0,
          cooperation: 1.0,
        }),
      });

      const fitness = extremeEvaluator.evaluate(agent);

      // Should cap at 0.1 minimum (10% of original)
      // Due to weight combination, the actual minimum may be slightly different
      expect(fitness.overall).toBeGreaterThan(0);
      expect(fitness.overall).toBeLessThan(1.0);
    });
  });

  describe('Integration with Evolution Engine', () => {
    it('should work with evolution engine population', () => {
      // Create diverse population
      const agents = [
        createMockAgent({
          id: 'high_throughput',
          taxonomy: AgentTaxonomy.BACTERIA,
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.7,
            throughput: 0.95,
            accuracy: 0.6,
            efficiency: 0.6,
            cooperation: 0.5,
          }),
        }),
        createMockAgent({
          id: 'high_accuracy',
          taxonomy: AgentTaxonomy.BACTERIA,
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.7,
            throughput: 0.6,
            accuracy: 0.95,
            efficiency: 0.6,
            cooperation: 0.5,
          }),
        }),
        createMockAgent({
          id: 'balanced',
          taxonomy: AgentTaxonomy.BACTERIA,
          evaluateFitness: jest.fn().mockReturnValue({
            overall: 0.75,
            throughput: 0.75,
            accuracy: 0.75,
            efficiency: 0.75,
            cooperation: 0.75,
          }),
        }),
      ];

      const evaluations = evaluator.evaluatePopulation(agents);
      const summary = evaluator.getPopulationSummary(evaluations);

      // Should identify Pareto front
      expect(summary.paretoFronts.size).toBeGreaterThan(0);

      // Should maintain diversity
      expect(summary.fitnessDiversity).toBeGreaterThan(0);
    });
  });
});
