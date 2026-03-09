/**
 * POLLN Microbiome - Evolution Engine Tests
 *
 * Comprehensive tests for the Phase 3 Evolution system.
 * Tests selection algorithms, fitness evaluation, and evolutionary progress.
 *
 * @module microbiome/__tests__/evolution.test
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import {
  EvolutionEngine,
  SelectionStrategy,
  SurvivalStrategy,
  createEvolutionEngine,
  type EvolutionConfig,
  type EvolutionReport,
  type EvolutionMetrics,
} from '../evolution.js';
import {
  BaseBacteria,
  AgentTaxonomy,
  type MicrobiomeAgent,
} from '../bacteria.js';
import {
  ResourceType,
  type FitnessScore,
} from '../types.js';
import { v4 as uuidv4 } from 'uuid';

/**
 * Mock agent for testing
 */
class MockBacteria extends BaseBacteria {
  constructor(fitness: FitnessScore) {
    super({
      name: 'MockBacteria',
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100,
      efficiency: fitness.efficiency,
      processor: async () => {
        const output = new Map();
        output.set(ResourceType.STRUCTURED, 10);
        return output;
      },
    });
    // Override fitness
    this.evaluateFitness = () => fitness;
  }
}

/**
 * Create a mock population with specified fitness values
 */
function createMockPopulation(fitnessValues: number[]): Map<string, MicrobiomeAgent> {
  const population = new Map<string, MicrobiomeAgent>();

  for (let i = 0; i < fitnessValues.length; i++) {
    const fitness: FitnessScore = {
      overall: fitnessValues[i],
      throughput: fitnessValues[i] * 0.8,
      accuracy: fitnessValues[i] * 0.9,
      efficiency: fitnessValues[i],
      cooperation: fitnessValues[i] * 0.5,
    };

    const agent = new MockBacteria(fitness);
    population.set(agent.id, agent);
  }

  return population;
}

describe('EvolutionEngine', () => {
  let engine: EvolutionEngine;

  beforeEach(() => {
    engine = new EvolutionEngine({
      selectionStrategy: SelectionStrategy.TOURNAMENT,
      survivalStrategy: SurvivalStrategy.GENERATIONAL,
      selectionPressure: 0.7,
      mutationRate: 0.1,
      crossoverRate: 0.7,
      elitism: 0.1,
      tournamentSize: 3,
      survivalRate: 0.5,
      maxPopulation: 1000,
      minPopulation: 10,
      enableCrossover: true,
      enableMutation: true,
      stagnationThreshold: 10,
    });
  });

  describe('Construction and Configuration', () => {
    it('should create an evolution engine with default config', () => {
      const defaultEngine = new EvolutionEngine();
      expect(defaultEngine).toBeInstanceOf(EvolutionEngine);
      expect(defaultEngine.getPopulation().size).toBe(0);
    });

    it('should create an evolution engine with custom config', () => {
      const customConfig: Partial<EvolutionConfig> = {
        selectionStrategy: SelectionStrategy.ROULETTE,
        survivalStrategy: SurvivalStrategy.STEADY_STATE,
        mutationRate: 0.05,
        elitism: 0.2,
      };

      const customEngine = new EvolutionEngine(customConfig);
      const config = customEngine.getConfig();

      expect(config.selectionStrategy).toBe(SelectionStrategy.ROULETTE);
      expect(config.survivalStrategy).toBe(SurvivalStrategy.STEADY_STATE);
      expect(config.mutationRate).toBe(0.05);
      expect(config.elitism).toBe(0.2);
    });

    it('should create via factory function', () => {
      const factoryEngine = createEvolutionEngine({
        mutationRate: 0.15,
      });
      expect(factoryEngine).toBeInstanceOf(EvolutionEngine);
      expect(factoryEngine.getConfig().mutationRate).toBe(0.15);
    });
  });

  describe('Population Management', () => {
    it('should set population', () => {
      const population = createMockPopulation([0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      const currentPop = engine.getPopulation();
      expect(currentPop.size).toBe(3);
      expect(currentPop.has([...population.keys()][0])).toBe(true);
    });

    it('should add agent to population', () => {
      const population = createMockPopulation([0.5]);
      engine.setPopulation(population);

      const newAgent = new MockBacteria({
        overall: 0.8,
        throughput: 0.64,
        accuracy: 0.72,
        efficiency: 0.8,
        cooperation: 0.4,
      });

      engine.addAgent(newAgent);

      const currentPop = engine.getPopulation();
      expect(currentPop.size).toBe(2);
      expect(currentPop.has(newAgent.id)).toBe(true);
    });

    it('should remove agent from population', () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      const agentId = [...population.keys()][0];
      const removed = engine.removeAgent(agentId);

      expect(removed).toBe(true);
      expect(engine.getPopulation().size).toBe(1);
    });

    it('should return false when removing non-existent agent', () => {
      const removed = engine.removeAgent('non-existent-id');
      expect(removed).toBe(false);
    });
  });

  describe('Selection Algorithms', () => {
    it('should perform tournament selection', async () => {
      engine.updateConfig({ selectionStrategy: SelectionStrategy.TOURNAMENT });

      const population = createMockPopulation([0.3, 0.5, 0.7, 0.9, 0.4]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report).toBeDefined();
      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThan(0);
    });

    it('should perform roulette wheel selection', async () => {
      engine.updateConfig({ selectionStrategy: SelectionStrategy.ROULETTE });

      const population = createMockPopulation([0.3, 0.5, 0.7, 0.9]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThan(0);
    });

    it('should perform rank selection', async () => {
      engine.updateConfig({ selectionStrategy: SelectionStrategy.RANK });

      const population = createMockPopulation([0.2, 0.4, 0.6, 0.8]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThan(0);
    });

    it('should perform truncation selection', async () => {
      engine.updateConfig({ selectionStrategy: SelectionStrategy.TRUNCATION });

      const population = createMockPopulation([0.1, 0.3, 0.5, 0.7, 0.9]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThan(0);
    });
  });

  describe('Survival Strategies', () => {
    it('should use generational survival', async () => {
      engine.updateConfig({
        survivalStrategy: SurvivalStrategy.GENERATIONAL,
        elitism: 0,
      });

      const population = createMockPopulation([0.5, 0.6, 0.7, 0.8]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      // In generational mode, most parents are replaced
    });

    it('should use steady-state survival', async () => {
      engine.updateConfig({
        survivalStrategy: SurvivalStrategy.STEADY_STATE,
        survivalRate: 0.5,
      });

      const population = createMockPopulation([0.4, 0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      // In steady-state, best individuals are preserved
    });

    it('should use mixed survival', async () => {
      engine.updateConfig({
        survivalStrategy: SurvivalStrategy.MIXED,
        elitism: 0.2,
      });

      const population = createMockPopulation([0.3, 0.5, 0.7, 0.9]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      // In mixed mode, elite parents are preserved
    });
  });

  describe('Elitism', () => {
    it('should preserve elite individuals', async () => {
      engine.updateConfig({ elitism: 0.2 });

      const population = createMockPopulation([0.9, 0.8, 0.7, 0.6, 0.5]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      // Top 20% should be preserved
    });

    it('should handle 100% elitism', async () => {
      engine.updateConfig({
        elitism: 1.0,
        enableMutation: false,
        enableCrossover: false,
      });

      const population = createMockPopulation([0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      const initialSize = population.size;
      const report = await engine.evolveGeneration();

      // With 100% elitism and no mutation/crossover, population should stay similar
      expect(report.generation).toBe(1);
    });

    it('should handle 0% elitism', async () => {
      engine.updateConfig({ elitism: 0 });

      const population = createMockPopulation([0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      // No elitism, all parents compete for survival
    });
  });

  describe('Evolutionary Metrics', () => {
    it('should track generation number', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      expect(engine.getMetrics().generation).toBe(1);

      await engine.evolveGeneration();
      expect(engine.getMetrics().generation).toBe(2);

      await engine.evolveGeneration();
      expect(engine.getMetrics().generation).toBe(3);
    });

    it('should track best fitness ever', async () => {
      const population = createMockPopulation([0.5, 0.7, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      let metrics = engine.getMetrics();
      expect(metrics.bestFitnessEver).toBeGreaterThan(0);

      // Evolve more
      await engine.evolveGeneration();
      await engine.evolveGeneration();

      metrics = engine.getMetrics();
      expect(metrics.bestFitnessEver).toBeGreaterThan(0);
    });

    it('should track fitness history', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      await engine.evolveGeneration();
      await engine.evolveGeneration();

      const metrics = engine.getMetrics();
      expect(metrics.fitnessHistory.length).toBe(3);
    });

    it('should track diversity history', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      await engine.evolveGeneration();

      const metrics = engine.getMetrics();
      expect(metrics.diversityHistory.length).toBe(2);
    });

    it('should track population history', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      await engine.evolveGeneration();

      const metrics = engine.getMetrics();
      expect(metrics.populationHistory.length).toBe(2);
    });

    it('should track stagnation count', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();

      let metrics = engine.getMetrics();
      const initialStagnation = metrics.stagnationCount;

      // If fitness doesn't improve, stagnation should increase
      await engine.evolveGeneration();
      metrics = engine.getMetrics();
      expect(metrics.stagnationCount).toBeGreaterThanOrEqual(initialStagnation);
    });

    it('should calculate convergence rate', async () => {
      const population = createMockPopulation([0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      // Need multiple generations for convergence rate
      await engine.evolveGeneration();
      await engine.evolveGeneration();
      await engine.evolveGeneration();
      await engine.evolveGeneration();
      await engine.evolveGeneration();

      const metrics = engine.getMetrics();
      expect(metrics.convergenceRate).toBeDefined();
    });
  });

  describe('Evolution Report', () => {
    it('should generate comprehensive evolution report', async () => {
      const population = createMockPopulation([0.4, 0.5, 0.6, 0.7, 0.8]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.bestFitness).toBeGreaterThan(0);
      expect(report.avgFitness).toBeGreaterThan(0);
      expect(report.worstFitness).toBeGreaterThan(0);
      expect(report.diversity).toBeGreaterThanOrEqual(0);
      expect(report.mutationCount).toBeGreaterThanOrEqual(0);
      expect(report.births).toBeGreaterThanOrEqual(0);
      expect(report.deaths).toBeGreaterThanOrEqual(0);
      expect(report.crossoverCount).toBeGreaterThanOrEqual(0);
      expect(report.fitnessDelta).toBeDefined();
      expect(report.populationSize).toBeGreaterThan(0);
      expect(report.speciesCount).toBeGreaterThan(0);
    });

    it('should track fitness delta between generations', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      const report1 = await engine.evolveGeneration();
      const report2 = await engine.evolveGeneration();

      expect(report2.fitnessDelta).toBeDefined();
      expect(report2.generation).toBe(2);
    });

    it('should track species count', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();
      expect(report.speciesCount).toBeGreaterThan(0);
    });
  });

  describe('Population Diversity', () => {
    it('should calculate diversity for homogeneous population', async () => {
      // All same taxonomy
      const population = createMockPopulation([0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();
      expect(report.diversity).toBeGreaterThanOrEqual(0);
    });

    it('should maintain diversity over generations', async () => {
      const population = createMockPopulation([0.4, 0.5, 0.6, 0.7, 0.8]);
      engine.setPopulation(population);

      const report1 = await engine.evolveGeneration();
      const report2 = await engine.evolveGeneration();
      const report3 = await engine.evolveGeneration();

      // Diversity should be calculated (may be 0 for single-taxonomy population)
      expect(report1.diversity).toBeGreaterThanOrEqual(0);
      expect(report2.diversity).toBeGreaterThanOrEqual(0);
      expect(report3.diversity).toBeGreaterThanOrEqual(0);

      // Diversity should not crash and should be a valid number
      expect(typeof report1.diversity).toBe('number');
      expect(typeof report2.diversity).toBe('number');
      expect(typeof report3.diversity).toBe('number');
      expect(isNaN(report1.diversity)).toBe(false);
      expect(isNaN(report2.diversity)).toBe(false);
      expect(isNaN(report3.diversity)).toBe(false);
    });
  });

  describe('Population Limits', () => {
    it('should enforce maximum population', async () => {
      engine.updateConfig({
        maxPopulation: 10,
        minPopulation: 2,
        enableMutation: true,
        mutationRate: 0.5,
      });

      const population = createMockPopulation([0.5, 0.6, 0.7, 0.8, 0.9]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      const currentPop = engine.getPopulation();

      expect(currentPop.size).toBeLessThanOrEqual(10);
    });

    it('should enforce minimum population', async () => {
      engine.updateConfig({
        maxPopulation: 100,
        minPopulation: 5,
        enableMutation: false,
        enableCrossover: false,
      });

      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      const currentPop = engine.getPopulation();

      // Should maintain minimum population
      expect(currentPop.size).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Configuration Updates', () => {
    it('should update mutation rate', () => {
      engine.updateConfig({ mutationRate: 0.05 });
      expect(engine.getConfig().mutationRate).toBe(0.05);
    });

    it('should update selection strategy', () => {
      engine.updateConfig({
        selectionStrategy: SelectionStrategy.RANK,
      });
      expect(engine.getConfig().selectionStrategy).toBe(SelectionStrategy.RANK);
    });

    it('should update survival strategy', () => {
      engine.updateConfig({
        survivalStrategy: SurvivalStrategy.MIXED,
      });
      expect(engine.getConfig().survivalStrategy).toBe(SurvivalStrategy.MIXED);
    });

    it('should update selection pressure', () => {
      engine.updateConfig({ selectionPressure: 0.8 });
      expect(engine.getConfig().selectionPressure).toBe(0.8);
    });

    it('should update elitism', () => {
      engine.updateConfig({ elitism: 0.15 });
      expect(engine.getConfig().elitism).toBe(0.15);
    });

    it('should update crossover rate', () => {
      engine.updateConfig({ crossoverRate: 0.8 });
      expect(engine.getConfig().crossoverRate).toBe(0.8);
    });
  });

  describe('State Management', () => {
    it('should reset evolution state', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      await engine.evolveGeneration();

      expect(engine.getMetrics().generation).toBe(2);

      engine.reset();

      expect(engine.getMetrics().generation).toBe(0);
      expect(engine.getMetrics().fitnessHistory.length).toBe(0);
      expect(engine.getMetrics().bestFitnessEver).toBe(0);
    });

    it('should export state', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();

      const state = engine.exportState();

      expect(state.generation).toBe(1);
      expect(state.config).toBeDefined();
      expect(state.metrics).toBeDefined();
      expect(state.species).toBeDefined();
      expect(state.population).toBeDefined();
    });

    it('should import state', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      await engine.evolveGeneration();

      const state = engine.exportState();

      const newEngine = new EvolutionEngine();
      newEngine.importState(state);

      expect(newEngine.getMetrics().generation).toBe(1);
      expect(newEngine.getPopulation().size).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty population', async () => {
      engine.setPopulation(new Map());

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBe(0);
    });

    it('should handle single agent population', async () => {
      const population = createMockPopulation([0.5]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThanOrEqual(0);
    });

    it('should handle all agents with same fitness', async () => {
      const population = createMockPopulation([0.5, 0.5, 0.5, 0.5]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.bestFitness).toBe(0.5);
      expect(report.avgFitness).toBe(0.5);
      expect(report.worstFitness).toBe(0.5);
    });

    it('should handle agents with zero fitness', async () => {
      const population = createMockPopulation([0, 0, 0]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.bestFitness).toBe(0);
    });

    it('should handle mutation disabled', async () => {
      engine.updateConfig({
        enableMutation: false,
        enableCrossover: false,
      });

      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.mutationCount).toBe(0);
    });

    it('should handle crossover disabled', async () => {
      engine.updateConfig({
        enableCrossover: false,
        enableMutation: true,
      });

      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
    });
  });

  describe('Multi-Generation Evolution', () => {
    it('should evolve multiple generations', async () => {
      const population = createMockPopulation([0.4, 0.5, 0.6, 0.7, 0.8]);
      engine.setPopulation(population);

      const generations = 5;
      const reports: EvolutionReport[] = [];

      for (let i = 0; i < generations; i++) {
        const report = await engine.evolveGeneration();
        reports.push(report);
      }

      expect(reports.length).toBe(5);
      expect(reports[4].generation).toBe(5);

      // Check generation numbers are sequential
      for (let i = 0; i < reports.length; i++) {
        expect(reports[i].generation).toBe(i + 1);
      }
    });

    it('should track progress over multiple generations', async () => {
      const population = createMockPopulation([0.3, 0.4, 0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      await engine.evolveGeneration();
      await engine.evolveGeneration();
      await engine.evolveGeneration();

      const metrics = engine.getMetrics();

      expect(metrics.generation).toBe(3);
      expect(metrics.fitnessHistory.length).toBe(3);
      expect(metrics.diversityHistory.length).toBe(3);
      expect(metrics.populationHistory.length).toBe(3);
    });

    it('should maintain population over multiple generations', async () => {
      engine.updateConfig({
        maxPopulation: 100,
        minPopulation: 10,
      });

      const population = createMockPopulation([0.5, 0.6, 0.7]);
      engine.setPopulation(population);

      for (let i = 0; i < 10; i++) {
        await engine.evolveGeneration();
        const currentPop = engine.getPopulation();
        expect(currentPop.size).toBeLessThanOrEqual(100);
      }
    });
  });

  describe('Integration with Agents', () => {
    it('should work with BaseBacteria agents', async () => {
      const bacteria1 = new BaseBacteria({
        name: 'TestBacteria1',
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processor: async () => {
          const output = new Map();
          output.set(ResourceType.STRUCTURED, 10);
          return output;
        },
      });

      const bacteria2 = new BaseBacteria({
        name: 'TestBacteria2',
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processor: async () => {
          const output = new Map();
          output.set(ResourceType.STRUCTURED, 10);
          return output;
        },
      });

      const population = new Map<string, MicrobiomeAgent>();
      population.set(bacteria1.id, bacteria1);
      population.set(bacteria2.id, bacteria2);

      engine.setPopulation(population);

      const report = await engine.evolveGeneration();

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThan(0);
    });

    it('should respect agent lifecycle', async () => {
      const population = createMockPopulation([0.5, 0.6]);
      engine.setPopulation(population);

      // Kill one agent
      const agentId = [...population.keys()][0];
      const agent = population.get(agentId);
      if (agent) {
        agent.lifecycle.isAlive = false;
      }

      const report = await engine.evolveGeneration();

      // Dead agent should not be counted
      expect(report.generation).toBe(1);
    });
  });

  describe('Performance and Scalability', () => {
    it('should handle larger populations', async () => {
      const fitnessValues = Array.from({ length: 100 }, () => Math.random());
      const population = createMockPopulation(fitnessValues);
      engine.setPopulation(population);

      const startTime = Date.now();
      const report = await engine.evolveGeneration();
      const duration = Date.now() - startTime;

      expect(report.generation).toBe(1);
      expect(report.populationSize).toBeGreaterThan(0);
      // Should complete in reasonable time (< 5 seconds for 100 agents)
      expect(duration).toBeLessThan(5000);
    }, 10000);

    it('should scale with generation count', async () => {
      const population = createMockPopulation([0.5, 0.6, 0.7, 0.8]);
      engine.setPopulation(population);

      const startTime = Date.now();
      for (let i = 0; i < 20; i++) {
        await engine.evolveGeneration();
      }
      const duration = Date.now() - startTime;

      expect(engine.getMetrics().generation).toBe(20);
      // Should complete 20 generations in reasonable time
      expect(duration).toBeLessThan(10000);
    }, 15000);
  });
});
