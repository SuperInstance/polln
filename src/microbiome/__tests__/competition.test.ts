/**
 * POLLN Microbiome - Competition Engine Tests
 *
 * Comprehensive tests for competitive interactions, scarcity detection,
 * niche differentiation, and character displacement.
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import {
  CompetitionEngine,
  ScarcityLevel,
  createCompetitionEngine,
  CompetitionEngineConfig,
} from '../competition.js';
import {
  MetabolismManager,
  ResourcePool,
} from '../metabolism.js';
import {
  FitnessEvaluator,
  FitnessEvaluatorConfig,
} from '../fitness.js';
import {
  SymbiosisManager,
} from '../symbiosis.js';
import { SymbiosisType } from '../types.js';
import {
  MicrobiomeAgent,
  ResourceType,
  AgentTaxonomy,
  LifecycleState,
  MetabolicProfile,
  FitnessScore,
} from '../types.js';
import { v4 as uuidv4 } from 'uuid';

/**
 * Helper: Create a mock agent
 */
function createMockAgent(config: {
  id?: string;
  taxonomy?: AgentTaxonomy;
  inputs?: ResourceType[];
  outputs?: ResourceType[];
  processingRate?: number;
  efficiency?: number;
  health?: number;
}): MicrobiomeAgent {
  const id = config.id ?? uuidv4();
  return {
    id,
    name: `Agent_${id.slice(0, 8)}`,
    taxonomy: config.taxonomy ?? AgentTaxonomy.BACTERIA,
    metabolism: {
      inputs: config.inputs ?? [ResourceType.TEXT],
      outputs: config.outputs ?? [ResourceType.STRUCTURED],
      processingRate: config.processingRate ?? 100,
      efficiency: config.efficiency ?? 0.8,
    },
    lifecycle: {
      health: config.health ?? 1.0,
      age: 0,
      generation: 0,
      isAlive: true,
    },
    parentId: undefined,
    generation: 0,
    size: 1024,
    complexity: 0.5,
    async process(resources) { return new Map(); },
    async reproduce(config) { return this as any; },
    evaluateFitness(): FitnessScore {
      return {
        overall: this.lifecycle.health,
        throughput: this.metabolism.processingRate / 100,
        accuracy: 0.8,
        efficiency: this.metabolism.efficiency,
        cooperation: 0.5,
      };
    },
    canMetabolize(resources) {
      return resources.has(ResourceType.TEXT);
    },
    age(deltaMs) {
      this.lifecycle.age += deltaMs;
    },
  };
}

/**
 * Helper: Set resource capacity using getAllFlows
 */
function setResourceCapacity(pool: ResourcePool, resource: ResourceType, capacity: number): void {
  const flows = pool.getAllFlows();
  const flow = flows.get(resource);
  if (flow) {
    flow.capacity = capacity;
  }
}

describe('CompetitionEngine', () => {
  let metabolism: MetabolismManager;
  let fitness: FitnessEvaluator;
  let symbiosis: SymbiosisManager;
  let competition: CompetitionEngine;

  beforeEach(() => {
    metabolism = new MetabolismManager();
    fitness = new FitnessEvaluator();
    symbiosis = new SymbiosisManager();
    competition = new CompetitionEngine(metabolism, fitness, symbiosis);
  });

  describe('Scarcity Detection', () => {
    it('should detect abundant resources', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 800);

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      const reports = competition.calculateScarcity(agents);
      const textReport = reports.get(ResourceType.TEXT);

      expect(textReport).toBeDefined();
      expect(textReport?.level).toBe(ScarcityLevel.ABUNDANT);
      expect(textReport?.scarcityRatio).toBeLessThan(0.4);
    });

    it('should detect moderate scarcity', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 400);

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      const reports = competition.calculateScarcity(agents);
      const textReport = reports.get(ResourceType.TEXT);

      expect(textReport?.level).toBe(ScarcityLevel.MODERATE);
      expect(textReport?.scarcityRatio).toBeGreaterThanOrEqual(0.4);
      expect(textReport?.scarcityRatio).toBeLessThan(0.7);
    });

    it('should detect scarce resources', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 200);

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      const reports = competition.calculateScarcity(agents);
      const textReport = reports.get(ResourceType.TEXT);

      expect(textReport?.level).toBe(ScarcityLevel.SCARCE);
      expect(textReport?.scarcityRatio).toBeGreaterThanOrEqual(0.7);
      expect(textReport?.scarcityRatio).toBeLessThan(0.9);
    });

    it('should detect critical scarcity', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50);

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      const reports = competition.calculateScarcity(agents);
      const textReport = reports.get(ResourceType.TEXT);

      expect(textReport?.level).toBe(ScarcityLevel.CRITICAL);
      expect(textReport?.scarcityRatio).toBeGreaterThanOrEqual(0.9);
    });

    it('should count competitors correctly', () => {
      const pool = metabolism.getResourcePool();
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
        createMockAgent({ inputs: [ResourceType.TEXT] }),
        createMockAgent({ inputs: [ResourceType.AUDIO] }), // Not competing for TEXT
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      const reports = competition.calculateScarcity(agents);
      const textReport = reports.get(ResourceType.TEXT);

      expect(textReport?.competitorCount).toBe(3);
    });

    it('should calculate competition intensity', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50); // 95% depleted

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      const reports = competition.calculateScarcity(agents);
      const textReport = reports.get(ResourceType.TEXT);

      expect(textReport?.competitionIntensity).toBeGreaterThan(0.5);
    });
  });

  describe('Competitive Resolution', () => {
    it('should trigger competition when scarcity threshold is met', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50); // 95% depleted (well above threshold)

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.5 }),
      ];

      const interactions = competition.resolveCompetition(agents);

      expect(interactions.length).toBeGreaterThan(0);
      if (interactions.length > 0) {
        expect(interactions[0].resource).toBe(ResourceType.TEXT);
      }
    });

    it('should not trigger competition below scarcity threshold', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 800); // Only 20% depleted (below threshold)

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT] }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT] }),
      ];

      const interactions = competition.resolveCompetition(agents);

      expect(interactions.length).toBe(0);
    });

    it('should implement Gause\'s principle - competitive exclusion', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50); // Very high scarcity

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9, health: 1.0 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3, health: 1.0 }),
      ];

      const interactions = competition.resolveCompetition(agents);

      expect(interactions.length).toBeGreaterThan(0);
      expect(interactions[0].outcome).toBe('exclusion');
      expect(interactions[0].winner).toBe('agent1');
      expect(interactions[0].loser).toBe('agent2');
    });

    it('should support coexistence with low fitness difference', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.52 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.51 }),
      ];

      const interactions = competition.resolveCompetition(agents);

      expect(interactions.length).toBeGreaterThan(0);
      expect(interactions[0].outcome).toBe('coexistence');
    });

    it('should trigger niche differentiation with moderate fitness difference', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.7 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.5 }),
      ];

      const interactions = competition.resolveCompetition(agents);

      expect(interactions.length).toBeGreaterThan(0);
      expect(interactions[0].outcome).toBe('differentiation');
    });

    it('should respect mutualism and promote coexistence', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50);

      const agent1 = createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 });
      const agent2 = createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 });

      // Form strong mutualism
      symbiosis.formSymbiosis(agent1, agent2, SymbiosisType.MUTUALISM, 0.8);

      const interactions = competition.resolveCompetition([agent1, agent2]);

      expect(interactions.length).toBeGreaterThan(0);
      expect(interactions[0].outcome).toBe('coexistence');
    });

    it('should apply exclusion outcome - damage loser health', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50);

      const agent1 = createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 });
      const agent2 = createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3, health: 0.8 });

      competition.resolveCompetition([agent1, agent2]);

      expect(agent2.lifecycle.health).toBeLessThan(0.8);
    });

    it('should apply differentiation outcome - modify metabolism', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 50);

      const agent1 = createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.7 });
      const agent2 = createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.5 });

      const initialInputs = [...agent2.metabolism.inputs];
      const initialEfficiency = agent2.metabolism.efficiency;

      // Multiple attempts to trigger differentiation
      for (let i = 0; i < 10; i++) {
        competition.resolveCompetition([agent1, agent2]);
      }

      // Check if metabolism changed
      const inputsChanged = agent2.metabolism.inputs.length !== initialInputs.length ||
        !agent2.metabolism.inputs.every(r => initialInputs.includes(r));

      expect(inputsChanged || agent2.metabolism.efficiency !== initialEfficiency).toBe(true);
    });
  });

  describe('Niche Differentiation', () => {
    it('should create niche specialization', () => {
      const agent1 = createMockAgent({
        id: 'agent1',
        inputs: [ResourceType.TEXT, ResourceType.AUDIO],
      });
      const agent2 = createMockAgent({
        id: 'agent2',
        inputs: [ResourceType.TEXT, ResourceType.VIDEO],
      });

      const specialization = competition.differentiateNiche(agent1, agent2);

      expect(specialization).toBeDefined();
      expect(specialization?.agentId).toBe('agent1');
    });

    it('should identify specialized resources', () => {
      const agent1 = createMockAgent({
        id: 'agent1',
        inputs: [ResourceType.TEXT, ResourceType.AUDIO],
      });
      const agent2 = createMockAgent({
        id: 'agent2',
        inputs: [ResourceType.TEXT, ResourceType.VIDEO],
      });

      const specialization = competition.differentiateNiche(agent1, agent2);

      expect(specialization?.specializedResources).toContain(ResourceType.AUDIO);
    });

    it('should identify avoided resources', () => {
      const agent1 = createMockAgent({
        id: 'agent1',
        inputs: [ResourceType.TEXT, ResourceType.AUDIO],
      });
      const agent2 = createMockAgent({
        id: 'agent2',
        inputs: [ResourceType.TEXT, ResourceType.VIDEO],
      });

      const specialization = competition.differentiateNiche(agent1, agent2);

      expect(specialization?.avoidedResources).toContain(ResourceType.VIDEO);
    });

    it('should assign temporal niche', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT] });

      const specialization = competition.differentiateNiche(agent1, agent2);

      expect(specialization?.temporalNiche).toBeDefined();
      expect(specialization?.temporalNiche.start).toBeGreaterThanOrEqual(0);
      expect(specialization?.temporalNiche.end).toBeGreaterThanOrEqual(0);
    });

    it('should not differentiate when overlap is low', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT] });
      const agent2 = createMockAgent({ inputs: [ResourceType.VIDEO] });

      const specialization = competition.differentiateNiche(agent1, agent2);

      expect(specialization).toBeNull();
    });
  });

  describe('Character Displacement', () => {
    it('should apply character displacement', () => {
      const agent1 = createMockAgent({
        inputs: [ResourceType.TEXT],
        size: 1024,
        efficiency: 0.8,
      });
      const agent2 = createMockAgent({
        inputs: [ResourceType.TEXT],
        size: 2048,
        efficiency: 0.6,
      });

      const displacement = competition.applyCharacterDisplacement(
        agent1,
        agent2,
        ResourceType.TEXT
      );

      expect(displacement).toBeDefined();
      expect(displacement?.resource).toBe(ResourceType.TEXT);
    });

    it('should track initial and current overlap', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT] });

      const displacement = competition.applyCharacterDisplacement(
        agent1,
        agent2,
        ResourceType.TEXT
      );

      expect(displacement?.initialOverlap).toBeGreaterThan(0);
      expect(displacement?.currentOverlap).toBeLessThanOrEqual(displacement!.initialOverlap);
    });

    it('should identify trait differences', () => {
      const agent1 = createMockAgent({
        inputs: [ResourceType.TEXT],
        size: 1024,
        efficiency: 0.8,
      });
      const agent2 = createMockAgent({
        inputs: [ResourceType.TEXT],
        size: 2048,
        efficiency: 0.4,
      });

      const displacement = competition.applyCharacterDisplacement(
        agent1,
        agent2,
        ResourceType.TEXT
      );

      expect(displacement?.traitDifferences.length).toBeGreaterThan(0);
      expect(displacement?.traitDifferences).toContain('size');
      expect(displacement?.traitDifferences).toContain('efficiency');
    });

    it('should reduce overlap with repeated displacement', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT] });

      const displacement1 = competition.applyCharacterDisplacement(
        agent1,
        agent2,
        ResourceType.TEXT
      );

      const displacement2 = competition.applyCharacterDisplacement(
        agent1,
        agent2,
        ResourceType.TEXT
      );

      expect(displacement2?.currentOverlap).toBeLessThan(displacement1!.currentOverlap);
    });
  });

  describe('Statistics', () => {
    it('should track total interactions', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      competition.resolveCompetition(agents);

      const stats = competition.getStats();
      expect(stats.totalInteractions).toBeGreaterThan(0);
    });

    it('should track exclusions', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      competition.resolveCompetition(agents);

      const stats = competition.getStats();
      expect(stats.exclusions).toBeGreaterThan(0);
    });

    it('should track coexistences', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agent1 = createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.55 });
      const agent2 = createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.5 });

      competition.resolveCompetition([agent1, agent2]);

      const stats = competition.getStats();
      expect(stats.coexistences).toBeGreaterThan(0);
    });

    it('should track competition level', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ inputs: [ResourceType.TEXT] }),
        createMockAgent({ inputs: [ResourceType.TEXT] }),
      ];

      competition.resolveCompetition(agents);

      const stats = competition.getStats();
      expect(stats.currentCompetitionLevel).toBeGreaterThan(0);
    });

    it('should reset statistics', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      competition.resolveCompetition(agents);
      competition.resetStats();

      const stats = competition.getStats();
      expect(stats.totalInteractions).toBe(0);
      expect(stats.exclusions).toBe(0);
    });
  });

  describe('Niche and Displacement Tracking', () => {
    it('should retrieve niche specializations', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT, ResourceType.AUDIO] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT, ResourceType.VIDEO] });

      competition.differentiateNiche(agent1, agent2);

      const niches = competition.getNicheSpecializations();
      expect(niches.length).toBeGreaterThan(0);
    });

    it('should retrieve character displacements', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT] });

      competition.applyCharacterDisplacement(agent1, agent2, ResourceType.TEXT);

      const displacements = competition.getCharacterDisplacements();
      expect(displacements.length).toBeGreaterThan(0);
    });

    it('should retrieve competitive history', () => {
      const pool = metabolism.getResourcePool();
      pool.setCapacity(ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      competition.resolveCompetition(agents);

      const history = competition.getHistory();
      expect(history.length).toBeGreaterThan(0);
    });
  });

  describe('Configuration', () => {
    it('should respect exclusion threshold config', () => {
      const customConfig: CompetitionEngineConfig = {
        exclusionThreshold: 0.5,
      };

      const customCompetition = new CompetitionEngine(
        metabolism,
        fitness,
        symbiosis,
        customConfig
      );

      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.7 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      const interactions = customCompetition.resolveCompetition(agents);

      // With higher threshold, should get coexistence instead of exclusion
      expect(interactions[0].outcome).not.toBe('exclusion');
    });

    it('should respect enable/disable exclusion', () => {
      const customConfig: CompetitionEngineConfig = {
        enableExclusion: false,
      };

      const customCompetition = new CompetitionEngine(
        metabolism,
        fitness,
        symbiosis,
        customConfig
      );

      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      const interactions = customCompetition.resolveCompetition(agents);

      expect(interactions[0].outcome).not.toBe('exclusion');
    });

    it('should respect enable/disable differentiation', () => {
      const customConfig: CompetitionEngineConfig = {
        enableDifferentiation: false,
      };

      const customCompetition = new CompetitionEngine(
        metabolism,
        fitness,
        symbiosis,
        customConfig
      );

      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT, ResourceType.AUDIO] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT, ResourceType.VIDEO] });

      const specialization = customCompetition.differentiateNiche(agent1, agent2);

      expect(specialization).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty agent list', () => {
      const interactions = competition.resolveCompetition([]);
      expect(interactions.length).toBe(0);
    });

    it('should handle single agent', () => {
      const agents = [createMockAgent({ inputs: [ResourceType.TEXT] })];

      const interactions = competition.resolveCompetition(agents);
      expect(interactions.length).toBe(0);
    });

    it('should handle agents with different resources', () => {
      const pool = metabolism.getResourcePool();
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT] }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.AUDIO] }),
      ];

      const interactions = competition.resolveCompetition(agents);
      expect(interactions.length).toBe(0);
    });

    it('should handle dead agents', () => {
      const pool = metabolism.getResourcePool();
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], health: 1.0 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], health: 0.0 }),
      ];

      // Set agent2 as dead
      agents[1].lifecycle.isAlive = false;

      const interactions = competition.resolveCompetition(agents);
      expect(interactions.length).toBe(0);
    });

    it('should handle multiple resources', () => {
      const pool = metabolism.getResourcePool();
      pool.setCapacity(ResourceType.TEXT, 1000);
      pool.setCapacity(ResourceType.AUDIO, 1000);
      pool.add(ResourceType.TEXT, 100);
      pool.add(ResourceType.AUDIO, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.3 }),
      ];

      const interactions = competition.resolveCompetition(agents);

      // Should generate interactions for both resources
      expect(interactions.length).toBeGreaterThan(0);
    });

    it('should handle clear() correctly', () => {
      const agent1 = createMockAgent({ inputs: [ResourceType.TEXT] });
      const agent2 = createMockAgent({ inputs: [ResourceType.TEXT] });

      competition.differentiateNiche(agent1, agent2);
      competition.applyCharacterDisplacement(agent1, agent2, ResourceType.TEXT);

      competition.clear();

      expect(competition.getNicheSpecializations().length).toBe(0);
      expect(competition.getCharacterDisplacements().length).toBe(0);
      expect(competition.getHistory().length).toBe(0);
    });
  });

  describe('Factory Function', () => {
    it('should create competition engine with factory', () => {
      const engine = createCompetitionEngine(metabolism, fitness, symbiosis);

      expect(engine).toBeInstanceOf(CompetitionEngine);
    });

    it('should create competition engine with config via factory', () => {
      const config: CompetitionEngineConfig = {
        scarcityThreshold: 0.5,
        exclusionThreshold: 0.4,
      };

      const engine = createCompetitionEngine(metabolism, fitness, symbiosis, config);

      expect(engine).toBeInstanceOf(CompetitionEngine);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 }),
      ];

      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 400); // 60% scarcity

      const interactions = engine.resolveCompetition(agents);

      // Should not trigger with 0.5 threshold and 0.6 scarcity
      expect(interactions.length).toBeGreaterThan(0);
    });
  });

  describe('Integration Scenarios', () => {
    it('should handle complex ecosystem with multiple species', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      setResourceCapacity(pool, ResourceType.AUDIO, 1000);
      pool.add(ResourceType.TEXT, 200);
      pool.add(ResourceType.AUDIO, 200);

      const agents = [
        createMockAgent({ id: 'sp1_a', inputs: [ResourceType.TEXT], efficiency: 0.9 }),
        createMockAgent({ id: 'sp1_b', inputs: [ResourceType.TEXT], efficiency: 0.5 }),
        createMockAgent({ id: 'sp2_a', inputs: [ResourceType.AUDIO], efficiency: 0.8 }),
        createMockAgent({ id: 'sp2_b', inputs: [ResourceType.AUDIO], efficiency: 0.4 }),
        createMockAgent({ id: 'sp3_a', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.6 }),
      ];

      const interactions = competition.resolveCompetition(agents);

      // Should have multiple interactions
      expect(interactions.length).toBeGreaterThan(2);
    });

    it('should evolve ecosystem over multiple generations', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agents = [
        createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.9 }),
        createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT, ResourceType.AUDIO], efficiency: 0.5 }),
      ];

      // Simulate multiple competition rounds
      for (let i = 0; i < 10; i++) {
        competition.resolveCompetition(agents);
      }

      // Check that niche differentiation occurred
      const niches = competition.getNicheSpecializations();
      expect(niches.length).toBeGreaterThan(0);

      // Check that character displacement occurred
      const displacements = competition.getCharacterDisplacements();
      expect(displacements.length).toBeGreaterThan(0);
    });

    it('should balance competition with mutualism', () => {
      const pool = metabolism.getResourcePool();
      setResourceCapacity(pool, ResourceType.TEXT, 1000);
      pool.add(ResourceType.TEXT, 100);

      const agent1 = createMockAgent({ id: 'agent1', inputs: [ResourceType.TEXT], efficiency: 0.9 });
      const agent2 = createMockAgent({ id: 'agent2', inputs: [ResourceType.TEXT], efficiency: 0.3 });
      const agent3 = createMockAgent({ id: 'agent3', inputs: [ResourceType.TEXT], efficiency: 0.5 });

      // Form mutualism between agent1 and agent3
      symbiosis.formSymbiosis(agent1, agent3, SymbiosisType.MUTUALISM, 0.8);

      const interactions = competition.resolveCompetition([agent1, agent2, agent3]);

      // Agent1 and Agent3 should coexist due to mutualism
      // Agent2 should face exclusion from both
      const exclusions = interactions.filter(i => i.outcome === 'exclusion');
      expect(exclusions.length).toBeGreaterThan(0);
    });
  });
});
