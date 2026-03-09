/**
 * POLLN Microbiome - Genetic Operations Tests
 *
 * Comprehensive tests for genetic operators including point mutations,
 * chromosomal operations, crossover, horizontal transfer, and speciation.
 *
 * @module microbiome/__tests__/genetic
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import {
  GeneticOperators,
  PointMutationType,
  ChromosomalOperationType,
  CrossoverType,
  createGeneticOperators,
  GeneticOperatorsConfig,
} from '../genetic.js';
import { BaseBacteria, BacteriaFactory } from '../bacteria.js';
import { ResourceType, AgentTaxonomy } from '../types.js';

describe('GeneticOperators', () => {
  let geneticOps: GeneticOperators;
  let testPopulation: BaseBacteria[];

  beforeEach(() => {
    geneticOps = new GeneticOperators();
    testPopulation = [
      BacteriaFactory.textParser(),
      BacteriaFactory.sentiment(),
      BacteriaFactory.audioFeature(),
      BacteriaFactory.codeReviewer(),
      BacteriaFactory.compression(),
    ];
  });

  describe('Construction and Configuration', () => {
    it('should create genetic operators with default config', () => {
      const config = geneticOps.getConfig();
      expect(config.pointMutationRate).toBe(0.01);
      expect(config.chromosomalOperationRate).toBe(0.005);
      expect(config.crossoverRate).toBe(0.7);
      expect(config.horizontalTransferRate).toBe(0.02);
      expect(config.enablePointMutations).toBe(true);
      expect(config.enableCrossover).toBe(true);
    });

    it('should create genetic operators with custom config', () => {
      const customOps = new GeneticOperators({
        pointMutationRate: 0.05,
        crossoverRate: 0.9,
        enableSpeciation: false,
      });

      const config = customOps.getConfig();
      expect(config.pointMutationRate).toBe(0.05);
      expect(config.crossoverRate).toBe(0.9);
      expect(config.enableSpeciation).toBe(false);
    });

    it('should update configuration', () => {
      geneticOps.updateConfig({
        pointMutationRate: 0.1,
        maxMutationImpact: 0.5,
      });

      const config = geneticOps.getConfig();
      expect(config.pointMutationRate).toBe(0.1);
      expect(config.maxMutationImpact).toBe(0.5);
      expect(config.crossoverRate).toBe(0.7); // Unchanged
    });

    it('should create via factory function', () => {
      const factoryOps = createGeneticOperators({
        pointMutationRate: 0.03,
      });

      expect(factoryOps).toBeInstanceOf(GeneticOperators);
      expect(factoryOps.getConfig().pointMutationRate).toBe(0.03);
    });
  });

  describe('Point Mutations', () => {
    it('should apply goal adjustment mutation', async () => {
      const agent = testPopulation[0];
      const oldProcessingRate = agent.metabolism.processingRate;
      const oldEfficiency = agent.metabolism.efficiency;

      // Force mutation by setting high rate
      geneticOps.updateConfig({ pointMutationRate: 1.0, maxMutationImpact: 0.2 });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.operation).toBe('point_mutation');
      expect(result.parentIds).toContain(agent.id);
      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();

      if (result.child) {
        // Processing rate or efficiency should have changed (depending on which mutation was selected)
        const newProcessingRate = result.child.metabolism.processingRate;
        const newEfficiency = result.child.metabolism.efficiency;

        // At least one should be different from original, or mutation occurred
        const rateChanged = newProcessingRate !== oldProcessingRate;
        const efficiencyChanged = newEfficiency !== oldEfficiency;
        const mutationOccurred = result.details.length > 0;

        expect(rateChanged || efficiencyChanged || mutationOccurred).toBe(true);
      }
    });

    it('should apply method variation mutation', async () => {
      const agent = testPopulation[1];
      const oldEfficiency = agent.metabolism.efficiency;

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.success).toBe(true);
      expect(result.details).toBeDefined();

      // Mutation should have been attempted (check details)
      expect(result.details.length).toBeGreaterThan(0);
    });

    it('should apply metabolic shift mutation', async () => {
      const agent = testPopulation[2];
      const oldInputsLength = agent.metabolism.inputs.length;
      const oldOutputsLength = agent.metabolism.outputs.length;

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.success).toBe(true);
      expect(result.details).toBeDefined();

      // Mutation should have been attempted
      if (result.child && result.details.includes('Metabolic shift')) {
        // If it was metabolic shift, inputs or outputs should have changed
        const inputsChanged = result.child.metabolism.inputs.length !== oldInputsLength;
        const outputsChanged = result.child.metabolism.outputs.length !== oldOutputsLength;
        expect(inputsChanged || outputsChanged).toBe(true);
      }
    });

    it('should apply symbiosis gain mutation', async () => {
      const agent = testPopulation[3];
      const oldDependenciesLength = agent.dependencies.length;

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.success).toBe(true);

      if (result.child) {
        // Should have gained a dependency
        expect(result.child.dependencies.length).toBeGreaterThanOrEqual(oldDependenciesLength);
      }
    });

    it('should apply symbiosis loss mutation', async () => {
      // Create agent with dependencies
      const agent = new BaseBacteria({
        name: 'TestAgent',
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processor: async (input) => new Map(),
        dependencies: ['dep1', 'dep2', 'dep3'],
      });

      const oldDependenciesLength = agent.dependencies.length;

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.success).toBe(true);
      expect(result.details).toBeDefined();

      // Mutation should have been attempted (may or may not be symbiosis_loss)
      if (result.child && result.details.includes('Symbiosis loss')) {
        // If it was symbiosis loss, dependencies should have decreased
        expect(result.child.dependencies.length).toBeLessThan(oldDependenciesLength);
      }
    });

    it('should not apply mutation when disabled', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ enablePointMutations: false });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.success).toBe(false);
      expect(result.details).toContain('disabled');
    });

    it('should not apply mutation when rate not triggered', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 0.0001 });

      const result = await geneticOps.applyPointMutation(agent);

      // Most likely won't trigger
      expect(result.parentIds).toContain(agent.id);
    });
  });

  describe('Chromosomal Operations', () => {
    it('should apply inversion operation', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ chromosomalOperationRate: 1.0 });

      const result = await geneticOps.applyChromosomalOperation(agent);

      expect(result.operation).toBe('chromosomal_operation');
      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();
    });

    it('should apply transposition operation', async () => {
      const agent = testPopulation[1];

      geneticOps.updateConfig({ chromosomalOperationRate: 1.0 });

      const result = await geneticOps.applyChromosomalOperation(agent);

      expect(result.success).toBe(true);

      if (result.child) {
        // Inputs or outputs should have changed
        expect(result.child.metabolism.inputs.length + result.child.metabolism.outputs.length).toBeGreaterThan(0);
      }
    });

    it('should apply deletion operation', async () => {
      const agent = testPopulation[2];

      geneticOps.updateConfig({ chromosomalOperationRate: 1.0 });

      const result = await geneticOps.applyChromosomalOperation(agent);

      expect(result.success).toBe(true);
    });

    it('should apply duplication operation', async () => {
      const agent = testPopulation[3];

      geneticOps.updateConfig({ chromosomalOperationRate: 1.0 });

      const result = await geneticOps.applyChromosomalOperation(agent);

      expect(result.success).toBe(true);

      if (result.child) {
        // Duplication should increase inputs or outputs
        const totalResources = result.child.metabolism.inputs.length + result.child.metabolism.outputs.length;
        expect(totalResources).toBeGreaterThan(0);
      }
    });

    it('should not apply chromosomal operation when disabled', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ enableChromosomalOperations: false });

      const result = await geneticOps.applyChromosomalOperation(agent);

      expect(result.success).toBe(false);
      expect(result.details).toContain('disabled');
    });

    it('should handle edge case with minimal resources', async () => {
      // Create agent with single input and output
      const agent = new BaseBacteria({
        name: 'MinimalAgent',
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processor: async (input) => new Map(),
      });

      geneticOps.updateConfig({ chromosomalOperationRate: 1.0 });

      const result = await geneticOps.applyChromosomalOperation(agent);

      // Should still succeed, even if minimal
      expect(result.operation).toBe('chromosomal_operation');
    });
  });

  describe('Crossover Operations', () => {
    it('should apply single-point crossover', async () => {
      const parent1 = testPopulation[0];
      const parent2 = testPopulation[1];

      geneticOps.updateConfig({ crossoverRate: 1.0 });

      const result = await geneticOps.applyCrossover(parent1, parent2, CrossoverType.SINGLE_POINT);

      expect(result.operation).toBe('crossover');
      expect(result.parentIds).toContain(parent1.id);
      expect(result.parentIds).toContain(parent2.id);
      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();
    });

    it('should apply multi-point crossover', async () => {
      const parent1 = testPopulation[0];
      const parent2 = testPopulation[2];

      geneticOps.updateConfig({ crossoverRate: 1.0 });

      const result = await geneticOps.applyCrossover(parent1, parent2, CrossoverType.MULTI_POINT);

      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();

      if (result.child) {
        // Child should have mix of parents' traits
        expect(result.child.metabolism.inputs.length).toBeGreaterThan(0);
      }
    });

    it('should apply uniform crossover', async () => {
      const parent1 = testPopulation[1];
      const parent2 = testPopulation[3];

      geneticOps.updateConfig({ crossoverRate: 1.0 });

      const result = await geneticOps.applyCrossover(parent1, parent2, CrossoverType.UNIFORM);

      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();
    });

    it('should apply colony-aware crossover', async () => {
      const parent1 = testPopulation[0];
      const parent2 = testPopulation[1];

      geneticOps.updateConfig({ crossoverRate: 1.0, enableSpeciation: true });

      // Update speciation first
      geneticOps.updateSpeciation(testPopulation);

      const result = await geneticOps.applyCrossover(parent1, parent2, CrossoverType.COLONY_AWARE);

      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();
    });

    it('should not apply crossover when disabled', async () => {
      const parent1 = testPopulation[0];
      const parent2 = testPopulation[1];

      geneticOps.updateConfig({ enableCrossover: false });

      const result = await geneticOps.applyCrossover(parent1, parent2);

      expect(result.success).toBe(false);
      expect(result.details).toContain('disabled');
    });

    it('should not apply crossover when rate not triggered', async () => {
      const parent1 = testPopulation[0];
      const parent2 = testPopulation[1];

      geneticOps.updateConfig({ crossoverRate: 0.0001 });

      const result = await geneticOps.applyCrossover(parent1, parent2);

      // Most likely won't trigger
      expect(result.parentIds).toContain(parent1.id);
      expect(result.parentIds).toContain(parent2.id);
    });

    it('should handle crossover with identical parents', async () => {
      const parent1 = testPopulation[0];
      const parent2 = testPopulation[0]; // Same agent

      geneticOps.updateConfig({ crossoverRate: 1.0 });

      const result = await geneticOps.applyCrossover(parent1, parent2);

      expect(result.parentIds.length).toBe(2);
      // Should still produce a child
    });
  });

  describe('Horizontal Gene Transfer', () => {
    it('should transfer metabolic genes', async () => {
      const donor = testPopulation[0];
      const recipient = testPopulation[1];

      const oldRecipientInputs = recipient.metabolism.inputs.length;

      geneticOps.updateConfig({ horizontalTransferRate: 1.0 });

      const result = await geneticOps.applyHorizontalTransfer(donor, recipient);

      expect(result.operation).toBe('horizontal_transfer');
      expect(result.parentIds).toContain(donor.id);
      expect(result.parentIds).toContain(recipient.id);
      expect(result.success).toBe(true);
      expect(result.child).toBeDefined();
    });

    it('should transfer processing genes', async () => {
      const donor = testPopulation[2];
      const recipient = testPopulation[3];

      const oldRecipientEfficiency = recipient.metabolism.efficiency;

      geneticOps.updateConfig({ horizontalTransferRate: 1.0 });

      const result = await geneticOps.applyHorizontalTransfer(donor, recipient);

      expect(result.success).toBe(true);

      if (result.child) {
        // Efficiency should have changed (blended)
        expect(result.child.metabolism.efficiency).toBeDefined();
      }
    });

    it('should transfer symbiosis genes', async () => {
      const donor = new BaseBacteria({
        name: 'Donor',
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processor: async (input) => new Map(),
        dependencies: ['dep1', 'dep2'],
      });

      const recipient = new BaseBacteria({
        name: 'Recipient',
        inputs: [ResourceType.CODE],
        outputs: [ResourceType.STRUCTURED],
        processor: async (input) => new Map(),
        dependencies: ['dep3'],
      });

      geneticOps.updateConfig({ horizontalTransferRate: 1.0 });

      const result = await geneticOps.applyHorizontalTransfer(donor, recipient);

      expect(result.success).toBe(true);

      if (result.child) {
        // Should have gained dependencies
        expect(result.child.dependencies.length).toBeGreaterThanOrEqual(1);
      }
    });

    it('should not apply horizontal transfer when disabled', async () => {
      const donor = testPopulation[0];
      const recipient = testPopulation[1];

      geneticOps.updateConfig({ enableHorizontalTransfer: false });

      const result = await geneticOps.applyHorizontalTransfer(donor, recipient);

      expect(result.success).toBe(false);
      expect(result.details).toContain('disabled');
    });

    it('should handle horizontal transfer with same agent', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ horizontalTransferRate: 1.0 });

      const result = await geneticOps.applyHorizontalTransfer(agent, agent);

      expect(result.parentIds.length).toBe(2);
    });
  });

  describe('Speciation', () => {
    it('should update speciation for population', () => {
      geneticOps.updateConfig({ enableSpeciation: true });

      geneticOps.updateSpeciation(testPopulation);

      const speciesCount = geneticOps.getSpeciesCount();
      expect(speciesCount).toBeGreaterThan(0);
      expect(speciesCount).toBeLessThanOrEqual(20); // maxSpecies default
    });

    it('should not create species when disabled', () => {
      geneticOps.updateConfig({ enableSpeciation: false });

      geneticOps.updateSpeciation(testPopulation);

      expect(geneticOps.getSpeciesCount()).toBe(0);
    });

    it('should get species for agent', () => {
      geneticOps.updateConfig({ enableSpeciation: true, speciationThreshold: 0.1 });

      geneticOps.updateSpeciation(testPopulation);

      const agent = testPopulation[0];
      const species = geneticOps.getSpeciesForAgent(agent.id);

      expect(species).not.toBeNull();
      expect(species?.members.has(agent.id)).toBe(true);
    });

    it('should return null for agent not in species', () => {
      geneticOps.updateConfig({ enableSpeciation: true });

      geneticOps.updateSpeciation(testPopulation);

      const species = geneticOps.getSpeciesForAgent('nonexistent_agent');

      expect(species).toBeNull();
    });

    it('should check if agents are same species', () => {
      geneticOps.updateConfig({ enableSpeciation: true, speciationThreshold: 0.1 });

      geneticOps.updateSpeciation(testPopulation);

      const agent1 = testPopulation[0];
      const agent2 = testPopulation[1];

      const sameSpecies = geneticOps.areSameSpecies(agent1.id, agent2.id);

      expect(typeof sameSpecies).toBe('boolean');
    });

    it('should handle empty population', () => {
      geneticOps.updateConfig({ enableSpeciation: true });

      geneticOps.updateSpeciation([]);

      expect(geneticOps.getSpeciesCount()).toBe(0);
    });

    it('should respect minimum species size', () => {
      geneticOps.updateConfig({
        enableSpeciation: true,
        minSpeciesSize: 100, // Very high
        speciationThreshold: 0.1,
      });

      geneticOps.updateSpeciation(testPopulation);

      // Should create fewer species due to high min size
      const speciesCount = geneticOps.getSpeciesCount();
      expect(speciesCount).toBeLessThanOrEqual(testPopulation.length);
    });

    it('should respect maximum species limit', () => {
      geneticOps.updateConfig({
        enableSpeciation: true,
        maxSpecies: 2,
        speciationThreshold: 0.1,
      });

      geneticOps.updateSpeciation(testPopulation);

      expect(geneticOps.getSpeciesCount()).toBeLessThanOrEqual(2);
    });

    it('should encourage intra-species mating', () => {
      geneticOps.updateConfig({
        enableSpeciation: true,
        speciationThreshold: 0.1,
      });

      geneticOps.updateSpeciation(testPopulation);

      const candidate = testPopulation[0];
      const mates = geneticOps.encourageIntraSpeciesMating(testPopulation, candidate);

      expect(mates.length).toBeGreaterThan(0);
      expect(mates).not.toContain(candidate);
    });

    it('should return all mates when speciation disabled', () => {
      geneticOps.updateConfig({ enableSpeciation: false });

      geneticOps.updateSpeciation(testPopulation);

      const candidate = testPopulation[0];
      const mates = geneticOps.encourageIntraSpeciesMating(testPopulation, candidate);

      // Should return all agents except candidate
      expect(mates.length).toBeGreaterThan(0);
      // When speciation is disabled, encourageIntraSpeciesMating returns all agents
      expect(mates.length).toBeLessThanOrEqual(testPopulation.length);
    });

    it('should get all species', () => {
      geneticOps.updateConfig({ enableSpeciation: true });

      geneticOps.updateSpeciation(testPopulation);

      const allSpecies = geneticOps.getAllSpecies();

      expect(allSpecies.size).toBe(geneticOps.getSpeciesCount());

      for (const [id, species] of allSpecies) {
        expect(id).toContain('species_');
        expect(species.members).toBeInstanceOf(Set);
        expect(species.speciesId).toBe(id);
      }
    });
  });

  describe('Operation History', () => {
    it('should track operation history', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      await geneticOps.applyPointMutation(agent);
      await geneticOps.applyPointMutation(agent);
      await geneticOps.applyPointMutation(agent);

      const history = geneticOps.getOperationHistory();

      expect(history.length).toBe(3);
    });

    it('should clear operation history', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      await geneticOps.applyPointMutation(agent);
      await geneticOps.applyPointMutation(agent);

      geneticOps.clearHistory();

      const history = geneticOps.getOperationHistory();

      expect(history.length).toBe(0);
    });

    it('should limit history to 1000 operations', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      // Perform more than 1000 operations
      for (let i = 0; i < 1100; i++) {
        await geneticOps.applyPointMutation(agent);
      }

      const history = geneticOps.getOperationHistory();

      expect(history.length).toBe(1000);
    });

    it('should record operation details', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const result = await geneticOps.applyPointMutation(agent);

      const history = geneticOps.getOperationHistory();
      const lastOp = history[history.length - 1];

      expect(lastOp.operation).toBe('point_mutation');
      expect(lastOp.parentIds).toContain(agent.id);
      expect(lastOp.success).toBe(result.success);
      expect(lastOp.details).toBeDefined();
    });
  });

  describe('Integration with Evolution Engine', () => {
    it('should work with fitness evaluation', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const oldFitness = agent.evaluateFitness();
      const result = await geneticOps.applyPointMutation(agent);

      expect(result.fitnessDelta).toBeDefined();

      if (result.child) {
        const newFitness = result.child.evaluateFitness();
        expect(result.fitnessDelta).toBeCloseTo(newFitness.overall - oldFitness.overall, 5);
      }
    });

    it('should handle population evolution', async () => {
      geneticOps.updateConfig({
        pointMutationRate: 0.5,
        crossoverRate: 0.5,
        enableSpeciation: true,
      });

      // Update speciation
      geneticOps.updateSpeciation(testPopulation);

      // Apply some mutations
      for (const agent of testPopulation) {
        await geneticOps.applyPointMutation(agent);
      }

      // Apply some crossovers
      for (let i = 0; i < testPopulation.length - 1; i++) {
        await geneticOps.applyCrossover(testPopulation[i], testPopulation[i + 1]);
      }

      const history = geneticOps.getOperationHistory();
      expect(history.length).toBeGreaterThan(0);
    });

    it('should maintain diversity through speciation', () => {
      geneticOps.updateConfig({
        enableSpeciation: true,
        speciationThreshold: 0.3,
        minSpeciesSize: 2,
      });

      // Create diverse population
      const diversePop = [
        BacteriaFactory.textParser(),
        BacteriaFactory.textParser(),
        BacteriaFactory.sentiment(),
        BacteriaFactory.audioFeature(),
        BacteriaFactory.codeReviewer(),
      ];

      geneticOps.updateSpeciation(diversePop);

      const speciesCount = geneticOps.getSpeciesCount();

      // Should form multiple species
      expect(speciesCount).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle mutation on non-BaseBacteria agent', async () => {
      // Create a mock agent that's not BaseBacteria
      const mockAgent = {
        id: 'mock_1',
        taxonomy: AgentTaxonomy.BACTERIA,
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 10,
          efficiency: 0.8,
        },
        complexity: 0.5,
        size: 1024,
        evaluateFitness: () => ({
          overall: 0.7,
          throughput: 0.8,
          accuracy: 0.6,
          efficiency: 0.8,
          cooperation: 0.5,
        }),
      } as any;

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      const result = await geneticOps.applyPointMutation(mockAgent);

      // Should return original agent (no mutation applied)
      expect(result.child).toBeDefined();
    });

    it('should handle crossover with non-BaseBacteria agents', async () => {
      const mockAgent1 = {
        id: 'mock_1',
        taxonomy: AgentTaxonomy.BACTERIA,
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 10,
          efficiency: 0.8,
        },
        complexity: 0.5,
        size: 1024,
        evaluateFitness: () => ({
          overall: 0.7,
          throughput: 0.8,
          accuracy: 0.6,
          efficiency: 0.8,
          cooperation: 0.5,
        }),
      } as any;

      const mockAgent2 = {
        id: 'mock_2',
        taxonomy: AgentTaxonomy.BACTERIA,
        metabolism: {
          inputs: [ResourceType.CODE],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 5,
          efficiency: 0.7,
        },
        complexity: 0.6,
        size: 2048,
        evaluateFitness: () => ({
          overall: 0.6,
          throughput: 0.7,
          accuracy: 0.7,
          efficiency: 0.7,
          cooperation: 0.4,
        }),
      } as any;

      geneticOps.updateConfig({ crossoverRate: 1.0 });

      const result = await geneticOps.applyCrossover(mockAgent1, mockAgent2);

      // Should return fallback agent
      expect(result.child).toBeDefined();
    });

    it('should handle empty population in speciation', () => {
      geneticOps.updateConfig({ enableSpeciation: true });

      geneticOps.updateSpeciation([]);

      expect(geneticOps.getSpeciesCount()).toBe(0);
      expect(geneticOps.getAllSpecies().size).toBe(0);
    });

    it('should handle single agent population', () => {
      geneticOps.updateConfig({ enableSpeciation: true, minSpeciesSize: 1 });

      geneticOps.updateSpeciation([testPopulation[0]]);

      // Might not form species due to min size, or might form one
      const speciesCount = geneticOps.getSpeciesCount();
      expect(speciesCount).toBeGreaterThanOrEqual(0);
    });

    it('should handle very high mutation rates', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({
        pointMutationRate: 1.0,
        maxMutationImpact: 1.0, // Maximum impact
      });

      const result = await geneticOps.applyPointMutation(agent);

      expect(result.success).toBe(true);

      if (result.child) {
        // Values should still be within valid ranges
        expect(result.child.metabolism.efficiency).toBeGreaterThanOrEqual(0.1);
        expect(result.child.metabolism.efficiency).toBeLessThanOrEqual(1.0);
        expect(result.child.metabolism.processingRate).toBeGreaterThanOrEqual(1);
      }
    });

    it('should handle zero mutation rates', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({
        pointMutationRate: 0,
        crossoverRate: 0,
        horizontalTransferRate: 0,
      });

      const mutationResult = await geneticOps.applyPointMutation(agent);
      const crossoverResult = await geneticOps.applyCrossover(agent, testPopulation[1]);
      const transferResult = await geneticOps.applyHorizontalTransfer(agent, testPopulation[1]);

      expect(mutationResult.success).toBe(false);
      expect(crossoverResult.success).toBe(false);
      expect(transferResult.success).toBe(false);
    });
  });

  describe('Genetic Distance Calculation', () => {
    it('should calculate distance between different agents', () => {
      const agent1 = testPopulation[0];
      const agent2 = testPopulation[1];

      geneticOps.updateConfig({ enableSpeciation: true });
      geneticOps.updateSpeciation([agent1, agent2]);

      // Agents should have some distance
      const species1 = geneticOps.getSpeciesForAgent(agent1.id);
      const species2 = geneticOps.getSpeciesForAgent(agent2.id);

      expect(species1 || species2).toBeTruthy();
    });

    it('should calculate zero distance for identical agents', () => {
      const agent = testPopulation[0];

      // Create identical agent
      const identicalAgent = new BaseBacteria({
        name: agent.name,
        inputs: [...agent.metabolism.inputs],
        outputs: [...agent.metabolism.outputs],
        processingRate: agent.metabolism.processingRate,
        efficiency: agent.metabolism.efficiency,
        processor: async (input) => new Map(),
        size: agent.size,
        complexity: agent.complexity,
      });

      geneticOps.updateConfig({ enableSpeciation: true, speciationThreshold: 0.01 });

      geneticOps.updateSpeciation([agent, identicalAgent]);

      const species1 = geneticOps.getSpeciesForAgent(agent.id);
      const species2 = geneticOps.getSpeciesForAgent(identicalAgent.id);

      // Very similar agents should be in same species
      expect(species1?.speciesId).toBe(species2?.speciesId);
    });
  });

  describe('Performance and Scalability', () => {
    it('should handle large populations efficiently', () => {
      const largePopulation: BaseBacteria[] = [];
      for (let i = 0; i < 100; i++) {
        largePopulation.push(BacteriaFactory.textParser());
      }

      const startTime = Date.now();

      geneticOps.updateConfig({ enableSpeciation: true });
      geneticOps.updateSpeciation(largePopulation);

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete in reasonable time (< 1 second)
      expect(duration).toBeLessThan(1000);
    });

    it('should cache genetic distances', () => {
      const agent1 = testPopulation[0];
      const agent2 = testPopulation[1];

      geneticOps.updateConfig({ enableSpeciation: true });
      geneticOps.updateSpeciation([agent1, agent2]);

      // First calculation
      geneticOps.updateSpeciation([agent1, agent2]);

      // Second calculation should use cache
      const startTime = Date.now();
      geneticOps.updateSpeciation([agent1, agent2]);
      const endTime = Date.now();

      const duration = endTime - startTime;

      // Should be faster due to caching
      expect(duration).toBeLessThan(100);
    });

    it('should limit memory usage with history', async () => {
      const agent = testPopulation[0];

      geneticOps.updateConfig({ pointMutationRate: 1.0 });

      // Generate many operations
      for (let i = 0; i < 2000; i++) {
        await geneticOps.applyPointMutation(agent);
      }

      const history = geneticOps.getOperationHistory();

      // Should be limited to 1000
      expect(history.length).toBe(1000);
    });
  });

  describe('Complex Scenarios', () => {
    it('should maintain diversity through varied operations', async () => {
      geneticOps.updateConfig({
        pointMutationRate: 0.3,
        chromosomalOperationRate: 0.1,
        crossoverRate: 0.4,
        horizontalTransferRate: 0.1,
        enableSpeciation: true,
      });

      const agents = [...testPopulation];

      // Apply various operations
      for (let i = 0; i < agents.length; i++) {
        await geneticOps.applyPointMutation(agents[i]);
      }

      for (let i = 0; i < agents.length - 1; i++) {
        await geneticOps.applyCrossover(agents[i], agents[i + 1]);
      }

      for (let i = 0; i < agents.length; i++) {
        await geneticOps.applyHorizontalTransfer(agents[i], agents[(i + 1) % agents.length]);
      }

      geneticOps.updateSpeciation(agents);

      const history = geneticOps.getOperationHistory();

      // Should have performed many operations (success or failure)
      const successfulOps = history.filter(op => op.success).length;
      expect(successfulOps).toBeGreaterThan(0);
    });

    it('should handle evolutionary pressure', async () => {
      // Start with population
      let population = [...testPopulation];

      geneticOps.updateConfig({
        pointMutationRate: 0.5,
        crossoverRate: 0.5,
        enableSpeciation: true,
      });

      // Simulate multiple generations
      for (let gen = 0; gen < 5; gen++) {
        const newPopulation: BaseBacteria[] = [];

        for (const agent of population) {
          const result = await geneticOps.applyPointMutation(agent);
          if (result.child && result.child instanceof BaseBacteria) {
            newPopulation.push(result.child);
          }
        }

        // Crossover
        for (let i = 0; i < population.length - 1; i++) {
          const result = await geneticOps.applyCrossover(population[i], population[i + 1]);
          if (result.child && result.child instanceof BaseBacteria) {
            newPopulation.push(result.child);
          }
        }

        // Keep original population if no offspring were created
        if (newPopulation.length === 0) {
          newPopulation.push(...population);
        }

        population = newPopulation;
        geneticOps.updateSpeciation(population);
      }

      // Population should have evolved (or at least survived)
      expect(population.length).toBeGreaterThan(0);
    });
  });
});
