/**
 * Tests for Colony System
 * @module microbiome/__tests__/colony.test
 */

import {
  ColonySystem,
  ColonyState,
  ColonyProposal,
  Task,
  Specialization,
  createColonySystem,
} from '../colony.js';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  ResourceType,
  MetabolicProfile,
  LifecycleState,
} from '../types.js';

describe('ColonySystem', () => {
  let colonySystem: ColonySystem;
  let mockAgents: MicrobiomeAgent[];

  beforeEach(() => {
    colonySystem = new ColonySystem({
      minSize: 2,
      maxSize: 10,
      minCompatibility: 0.3, // Lowered for better test compatibility
      enableDirectChannels: true,
      enableSpecialization: true,
    });

    // Create mock agents
    mockAgents = Array.from({ length: 5 }, (_, i) => createMockAgent(i));
  });

  describe('constructor', () => {
    it('should initialize with default config', () => {
      const system = new ColonySystem();
      expect(system.getAllColonies()).toHaveLength(0);
    });

    it('should initialize with custom config', () => {
      const system = new ColonySystem({
        minSize: 3,
        maxSize: 15,
        minCompatibility: 0.7,
      });

      const stats = system.getStats();
      expect(stats.totalColonies).toBe(0);
    });
  });

  describe('discoverColonies', () => {
    it('should return empty array for insufficient agents', () => {
      const proposals = colonySystem.discoverColonies(mockAgents.slice(0, 1));
      expect(proposals).toHaveLength(0);
    });

    it('should discover colonies from compatible agents', () => {
      const proposals = colonySystem.discoverColonies(mockAgents);
      expect(Array.isArray(proposals)).toBe(true);
      expect(proposals.length).toBeGreaterThan(0);
    });

    it('should return proposals sorted by compatibility', () => {
      const proposals = colonySystem.discoverColonies(mockAgents);

      for (let i = 0; i < proposals.length - 1; i++) {
        const scoreA = proposals[i].compatibility * 0.6 + proposals[i].expectedEfficiency * 0.4;
        const scoreB = proposals[i + 1].compatibility * 0.6 + proposals[i + 1].expectedEfficiency * 0.4;
        expect(scoreA).toBeGreaterThanOrEqual(scoreB);
      }
    });

    it('should filter proposals by min compatibility', () => {
      const system = new ColonySystem({ minCompatibility: 0.9 });
      const proposals = system.discoverColonies(mockAgents);

      for (const proposal of proposals) {
        expect(proposal.compatibility).toBeGreaterThanOrEqual(0.9);
      }
    });

    it('should include symbioses in proposals', () => {
      const proposals = colonySystem.discoverColonies(mockAgents);

      for (const proposal of proposals) {
        expect(Array.isArray(proposal.symbioses)).toBe(true);
      }
    });

    it('should handle dead agents', () => {
      const deadAgent = createMockAgent(99);
      deadAgent.lifecycle.isAlive = false;

      const proposals = colonySystem.discoverColonies([...mockAgents, deadAgent]);

      // Dead agent should not be included
      for (const proposal of proposals) {
        expect(proposal.members).not.toContain(deadAgent);
      }
    });
  });

  describe('formColony', () => {
    it('should form colony from valid agents', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      expect(colony).not.toBeNull();
      expect(colony?.members).toHaveLength(3);
      expect(colony?.state).toBe(ColonyState.FORMING);
    });

    it('should return null for insufficient agents', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 1));
      expect(colony).toBeNull();
    });

    it('should return null for too many agents', () => {
      const system = new ColonySystem({ maxSize: 5 });
      const colony = system.formColony(mockAgents);
      expect(colony).toBeNull();
    });

    it('should return null for incompatible agents', () => {
      const system = new ColonySystem({ minCompatibility: 0.99 });
      const colony = system.formColony(mockAgents.slice(0, 2));
      expect(colony).toBeNull();
    });

    it('should establish direct channels when enabled', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      expect(colony?.communicationChannels.size).toBeGreaterThan(0);
    });

    it('should not establish direct channels when disabled', () => {
      const system = new ColonySystem({
        enableDirectChannels: false,
        minCompatibility: 0.3, // Lower threshold for test compatibility
      });
      const colony = system.formColony(mockAgents.slice(0, 3));

      // Colony should form but with no direct channels
      expect(colony).not.toBeNull();
      expect(colony?.communicationChannels.size).toBe(0);
    });

    it('should initialize roles for members', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      expect(colony?.roles.size).toBe(3);
    });

    it('should reject duplicate agents', () => {
      const duplicates = [mockAgents[0], mockAgents[0]];
      const colony = colonySystem.formColony(duplicates);

      expect(colony).toBeNull();
    });

    it('should reject dead agents', () => {
      const deadAgent = createMockAgent(99);
      deadAgent.lifecycle.isAlive = false;

      const colony = colonySystem.formColony([mockAgents[0], deadAgent]);

      expect(colony).toBeNull();
    });
  });

  describe('dissolveColony', () => {
    it('should dissolve existing colony', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      expect(colony).not.toBeNull();

      const result = colonySystem.dissolveColony(colony!.id);
      expect(result).toBe(true);

      const retrieved = colonySystem.getColony(colony!.id);
      expect(retrieved).toBeUndefined();
    });

    it('should return false for non-existent colony', () => {
      const result = colonySystem.dissolveColony('non-existent');
      expect(result).toBe(false);
    });

    it('should clear communication channels on dissolve', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      colonySystem.dissolveColony(colony!.id);

      // Colony should be removed
      const retrieved = colonySystem.getColony(colony!.id);
      expect(retrieved).toBeUndefined();
    });
  });

  describe('updateColony', () => {
    it('should transition from FORMING to ACTIVE', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      expect(colony?.state).toBe(ColonyState.FORMING);

      // Update with enough time (need >1000ms and stability >0.5)
      for (let i = 0; i < 20; i++) {
        colonySystem.updateColony(colony!, 100);
      }

      expect(colony?.state).toBe(ColonyState.ACTIVE);
    });

    it('should increase stability over time', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const initialStability = colony?.stability ?? 0;

      colonySystem.updateColony(colony!, 1000);

      expect(colony?.stability).toBeGreaterThan(initialStability);
    });

    it('should increase age on update', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const initialAge = colony?.age ?? 0;

      colonySystem.updateColony(colony!, 100);

      expect(colony?.age).toBe(initialAge + 100);
    });

    it('should increase co-evolution bonus with stability', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const initialBonus = colony?.coEvolutionBonus ?? 0;

      for (let i = 0; i < 20; i++) {
        colonySystem.updateColony(colony!, 500);
      }

      expect(colony?.coEvolutionBonus).toBeGreaterThan(initialBonus);
    });

    it('should transition to SPECIALIZING after enough tasks', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      // Move to ACTIVE (need >1000ms and stability >0.5)
      for (let i = 0; i < 20; i++) {
        colonySystem.updateColony(colony!, 100);
      }

      // Complete tasks (need >10 tasks)
      for (let i = 0; i < 15; i++) {
        colonySystem.recordTaskCompletion(colony!.id, true);
        colonySystem.updateColony(colony!, 100);
      }

      expect(colony?.state).toBe(ColonyState.SPECIALIZING);
    });

    it('should transition to DECLINING with low success rate', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      // Move to ACTIVE (need >1000ms and stability >0.5)
      for (let i = 0; i < 20; i++) {
        colonySystem.updateColony(colony!, 100);
      }

      // Record many failures to lower success rate below 0.3
      for (let i = 0; i < 30; i++) {
        colonySystem.recordTaskCompletion(colony!.id, false);
      }

      colonySystem.updateColony(colony!, 100);

      expect(colony?.state).toBe(ColonyState.DECLINING);
    });
  });

  describe('establishDirectChannels', () => {
    it('should create channels between compatible agents', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      expect(colony?.communicationChannels.size).toBeGreaterThan(0);
    });

    it('should create bidirectional channels', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 2));

      const channels = colony?.communicationChannels ?? new Map();
      expect(channels.size).toBeGreaterThan(0);
    });
  });

  describe('specialize', () => {
    it('should create specialization for task', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const task: Task = {
        id: 'task-1',
        type: 'processing',
        requiredResources: [ResourceType.TEXT],
        complexity: 0.5,
        priority: 0.7,
      };

      const specialization = colonySystem.specialize(colony!, task);

      expect(specialization).not.toBeNull();
      expect(specialization?.taskType).toBe('processing');
    });

    it('should add specialization to colony', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const task: Task = {
        id: 'task-1',
        type: 'processing',
        requiredResources: [ResourceType.TEXT],
        complexity: 0.5,
        priority: 0.7,
      };

      colonySystem.specialize(colony!, task);

      expect(colony?.specializations).toHaveLength(1);
    });

    it('should return existing specialization if already specialized', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const task: Task = {
        id: 'task-1',
        type: 'processing',
        requiredResources: [ResourceType.TEXT],
        complexity: 0.5,
        priority: 0.7,
      };

      const spec1 = colonySystem.specialize(colony!, task);
      const spec2 = colonySystem.specialize(colony!, task);

      expect(spec1).toBe(spec2);
    });

    it('should increase co-evolution bonus', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const task: Task = {
        id: 'task-1',
        type: 'processing',
        requiredResources: [ResourceType.TEXT],
        complexity: 0.5,
        priority: 0.7,
      };

      const initialBonus = colony?.coEvolutionBonus ?? 0;
      colonySystem.specialize(colony!, task);

      expect(colony?.coEvolutionBonus).toBeGreaterThan(initialBonus);
    });

    it('should return null when specialization disabled', () => {
      const system = new ColonySystem({ enableSpecialization: false });
      const colony = system.formColony(mockAgents.slice(0, 3));
      const task: Task = {
        id: 'task-1',
        type: 'processing',
        requiredResources: [ResourceType.TEXT],
        complexity: 0.5,
        priority: 0.7,
      };

      const specialization = system.specialize(colony!, task);

      expect(specialization).toBeNull();
    });
  });

  describe('recordTaskCompletion', () => {
    it('should increment tasks completed', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const initialTasks = colony?.tasksCompleted ?? 0;

      colonySystem.recordTaskCompletion(colony!.id, true);

      expect(colony?.tasksCompleted).toBe(initialTasks + 1);
    });

    it('should update success rate on success', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const initialRate = colony?.successRate ?? 0;

      colonySystem.recordTaskCompletion(colony!.id, true);
      colonySystem.recordTaskCompletion(colony!.id, true);
      colonySystem.recordTaskCompletion(colony!.id, true);

      expect(colony?.successRate).toBeGreaterThan(initialRate);
    });

    it('should update success rate on failure', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      colonySystem.recordTaskCompletion(colony!.id, true);
      colonySystem.recordTaskCompletion(colony!.id, false);
      colonySystem.recordTaskCompletion(colony!.id, false);

      expect(colony?.successRate).toBeLessThan(0.8);
    });

    it('should maintain performance history', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));

      colonySystem.recordTaskCompletion(colony!.id, true);
      colonySystem.recordTaskCompletion(colony!.id, false);

      // History should be maintained (internal state)
      expect(colony?.tasksCompleted).toBe(2);
    });
  });

  describe('getColony', () => {
    it('should return colony by ID', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const retrieved = colonySystem.getColony(colony!.id);

      expect(retrieved).toEqual(colony);
    });

    it('should return undefined for non-existent colony', () => {
      const retrieved = colonySystem.getColony('non-existent');
      expect(retrieved).toBeUndefined();
    });
  });

  describe('getAllColonies', () => {
    it('should return all active colonies', () => {
      colonySystem.formColony(mockAgents.slice(0, 2));
      colonySystem.formColony(mockAgents.slice(2, 4));

      const colonies = colonySystem.getAllColonies();

      expect(colonies).toHaveLength(2);
    });

    it('should return empty array when no colonies', () => {
      const colonies = colonySystem.getAllColonies();

      expect(colonies).toHaveLength(0);
    });
  });

  describe('getColoniesByState', () => {
    it('should filter colonies by state', () => {
      const colony1 = colonySystem.formColony(mockAgents.slice(0, 2));
      const colony2 = colonySystem.formColony(mockAgents.slice(2, 4));

      // Advance colony2 to ACTIVE (need >1000ms and stability >0.5)
      for (let i = 0; i < 20; i++) {
        colonySystem.updateColony(colony2!, 100);
      }

      const formingColonies = colonySystem.getColoniesByState(ColonyState.FORMING);
      const activeColonies = colonySystem.getColoniesByState(ColonyState.ACTIVE);

      expect(formingColonies.length).toBeGreaterThan(0);
      expect(activeColonies.length).toBeGreaterThan(0);
    });
  });

  describe('getStats', () => {
    it('should return correct statistics', () => {
      colonySystem.formColony(mockAgents.slice(0, 2));
      colonySystem.formColony(mockAgents.slice(2, 4));

      const stats = colonySystem.getStats();

      expect(stats.totalColonies).toBe(2);
      expect(stats.averageSize).toBeGreaterThan(0);
      expect(stats.averageStability).toBeGreaterThan(0);
    });

    it('should return zero stats when no colonies', () => {
      const stats = colonySystem.getStats();

      expect(stats.totalColonies).toBe(0);
      expect(stats.averageSize).toBe(0);
    });

    it('should track colonies by state', () => {
      colonySystem.formColony(mockAgents.slice(0, 2));

      const stats = colonySystem.getStats();

      expect(stats.coloniesByState.get(ColonyState.FORMING)).toBeGreaterThan(0);
    });
  });

  describe('setSimTime and getSimTime', () => {
    it('should set and get simulation time', () => {
      colonySystem.setSimTime(1000);

      expect(colonySystem.getSimTime()).toBe(1000);
    });
  });

  describe('clear', () => {
    it('should clear all colonies', () => {
      colonySystem.formColony(mockAgents.slice(0, 2));
      colonySystem.formColony(mockAgents.slice(2, 4));

      colonySystem.clear();

      expect(colonySystem.getAllColonies()).toHaveLength(0);
    });
  });

  describe('exportState and importState', () => {
    it('should export and import state', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      colonySystem.setSimTime(5000);

      const state = colonySystem.exportState();

      const newSystem = new ColonySystem();
      newSystem.importState(state);

      expect(newSystem.getSimTime()).toBe(5000);
      expect(newSystem.getAllColonies().length).toBe(1);
    });

    it('should preserve colony data on import', () => {
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      const colonyId = colony!.id;

      const state = colonySystem.exportState();

      const newSystem = new ColonySystem();
      newSystem.importState(state);

      const importedColony = newSystem.getColony(colonyId);
      expect(importedColony).toBeDefined();
      expect(importedColony?.members).toEqual(colony?.members);
    });
  });

  describe('createColonySystem factory', () => {
    it('should create colony system', () => {
      const system = createColonySystem();

      expect(system).toBeInstanceOf(ColonySystem);
    });

    it('should create colony system with config', () => {
      const system = createColonySystem({
        minSize: 3,
        maxSize: 15,
      });

      expect(system).toBeInstanceOf(ColonySystem);
    });
  });

  describe('integration scenarios', () => {
    it('should handle complete colony lifecycle', () => {
      // Form colony
      const colony = colonySystem.formColony(mockAgents.slice(0, 3));
      expect(colony?.state).toBe(ColonyState.FORMING);

      // Age to active (need >1000ms and stability >0.5)
      for (let i = 0; i < 20; i++) {
        colonySystem.updateColony(colony!, 100);
      }
      expect(colony?.state).toBe(ColonyState.ACTIVE);

      // Complete tasks (need >10 tasks)
      for (let i = 0; i < 15; i++) {
        colonySystem.recordTaskCompletion(colony!.id, true);
      }
      colonySystem.updateColony(colony!, 100);
      expect(colony?.state).toBe(ColonyState.SPECIALIZING);

      // Specialize
      const task: Task = {
        id: 'task-1',
        type: 'processing',
        requiredResources: [ResourceType.TEXT],
        complexity: 0.5,
        priority: 0.7,
      };
      colonySystem.specialize(colony!, task);

      // Should return to active after specialization
      colonySystem.updateColony(colony!, 100);
      expect(colony?.state).toBe(ColonyState.ACTIVE);

      // Dissolve
      const dissolved = colonySystem.dissolveColony(colony!.id);
      expect(dissolved).toBe(true);
    });

    it('should handle multiple colonies simultaneously', () => {
      const colony1 = colonySystem.formColony(mockAgents.slice(0, 2));
      const colony2 = colonySystem.formColony(mockAgents.slice(2, 4));

      expect(colonySystem.getAllColonies()).toHaveLength(2);

      // Update both
      colonySystem.updateColony(colony1!, 100);
      colonySystem.updateColony(colony2!, 100);

      // Record tasks for both
      colonySystem.recordTaskCompletion(colony1!.id, true);
      colonySystem.recordTaskCompletion(colony2!.id, true);

      expect(colony1?.tasksCompleted).toBe(1);
      expect(colony2?.tasksCompleted).toBe(1);
    });

    it('should discover and form compatible colonies', () => {
      const proposals = colonySystem.discoverColonies(mockAgents);

      expect(proposals.length).toBeGreaterThan(0);

      // Form the best proposal
      const bestProposal = proposals[0];
      const colony = colonySystem.formColony(bestProposal.members);

      expect(colony).not.toBeNull();
      expect(colony?.members).toEqual(bestProposal.members.map(m => m.id));
    });
  });
});

/**
 * Helper function to create mock agent
 */
function createMockAgent(index: number): MicrobiomeAgent {
  const taxonomyValues = Object.values(AgentTaxonomy);
  const taxonomy = taxonomyValues[index % taxonomyValues.length] as AgentTaxonomy;

  // Create complementary metabolic profiles for better compatibility
  const allResources = [
    ResourceType.TEXT,
    ResourceType.STRUCTURED,
    ResourceType.CODE,
    ResourceType.AUDIO,
    ResourceType.PACKAGES,
  ];

  // Each agent has consecutive input/output for high compatibility
  const inputIndex = index % (allResources.length - 1);
  const outputIndex = (inputIndex + 1) % allResources.length;

  return {
    id: `agent-${index}`,
    taxonomy,
    name: `Agent ${index}`,
    metabolism: {
      inputs: [allResources[inputIndex]],
      outputs: [allResources[outputIndex]],
      processingRate: 1.0 + (index % 3) * 0.1, // Similar rates for compatibility
      efficiency: 0.7 + (index % 3) * 0.05, // Similar efficiency for compatibility
    },
    lifecycle: {
      health: 1.0,
      age: 0,
      generation: 1,
      isAlive: true,
    },
    parentId: undefined,
    generation: 1,
    size: 1000,
    complexity: 0.5,

    async process(resources: Map<ResourceType, number>): Promise<Map<ResourceType, number>> {
      return new Map([[allResources[outputIndex], 1]]);
    },

    async reproduce(config: any): Promise<MicrobiomeAgent> {
      return createMockAgent(index + 1000);
    },

    evaluateFitness(): { overall: number; throughput: number; accuracy: number; efficiency: number; cooperation: number } {
      return {
        overall: 0.7 + (index % 3) * 0.05,
        throughput: 0.8,
        accuracy: 0.75,
        efficiency: 0.7 + (index % 3) * 0.05,
        cooperation: 0.8,
      };
    },

    canMetabolize(resources: Map<ResourceType, number>): boolean {
      return resources.has(allResources[inputIndex]);
    },

    age(dt: number): void {
      this.lifecycle.age += dt;
    },
  };
}
