/**
 * Tests for MicrobiomeBridge
 *
 * Comprehensive test suite for bidirectional agent conversion,
 * taxonomy mapping, metabolism translation, A2A bridging, and colony sync.
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import {
  MicrobiomeBridge,
  createMicrobiomeBridge,
  createVerboseBridge,
  BridgeConfig,
} from '../bridge.js';
import {
  AgentTaxonomy,
  ResourceType,
  BacteriaAgent,
  LifecycleState,
  MetabolicProfile,
  ColonyStructure,
} from '../types.js';
import type {
  BaseAgent,
  A2APackage,
  TileCategory,
  Goal,
} from '../../core/index.js';

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Create a mock bacteria agent for testing
 */
function createMockBacteriaAgent(overrides?: Partial<BacteriaAgent>): BacteriaAgent {
  const metabolism: MetabolicProfile = {
    inputs: [ResourceType.TEXT],
    outputs: [ResourceType.STRUCTURED],
    processingRate: 100,
    efficiency: 0.8,
  };

  const lifecycle: LifecycleState = {
    health: 0.9,
    age: 1000,
    generation: 2,
    isAlive: true,
  };

  return {
    id: 'test-bacteria-1',
    taxonomy: AgentTaxonomy.BACTERIA,
    name: 'TestBacteria',
    metabolism,
    lifecycle,
    generation: 2,
    size: 1024,
    complexity: 0.5,
    reproductionThreshold: 1000,
    accumulatedResources: 500,
    dependencies: ['agent-1', 'agent-2'],
    parentId: 'parent-bacteria',
    process: jest.fn(),
    reproduce: jest.fn(),
    evaluateFitness: jest.fn(),
    canMetabolize: jest.fn(),
    ...overrides,
  };
}

/**
 * Create a mock core agent for testing
 */
function createMockCoreAgent(overrides?: Partial<BaseAgent>): BaseAgent {
  const mockAgent = {
    id: 'test-core-1',
    config: {
      id: 'test-core-1',
      typeId: 'test-type',
      categoryId: 'EPHEMERAL',
      modelFamily: 'test-model',
      defaultParams: {},
      inputTopics: ['text'],
      outputTopic: 'structured',
      minExamples: 10,
      requiresWorldModel: false,
    },
    state: new Map(),
    lastActive: Date.now(),
    valueFunction: 0.7,
    successCount: 5,
    failureCount: 2,
    initialize: jest.fn(),
    process: jest.fn(),
    shutdown: jest.fn(),
    getState: jest.fn(),
    setState: jest.fn(),
    updateValueFunction: jest.fn(),
    touch: jest.fn(),
    emit: jest.fn(),
    on: jest.fn(),
    once: jest.fn(),
    removeListener: jest.fn(),
    removeAllListeners: jest.fn(),
    ...overrides,
  } as any;

  return mockAgent;
}

/**
 * Create a mock A2A package
 */
function createMockA2APackage(overrides?: Partial<A2APackage<any>>): A2APackage<any> {
  return {
    id: 'test-package-1',
    timestamp: Date.now(),
    senderId: 'agent-1',
    receiverId: 'agent-2',
    type: 'test-message',
    payload: { test: 'data' },
    parentIds: ['parent-1'],
    causalChainId: 'chain-1',
    privacyLevel: 'PUBLIC',
    layer: 'HABITUAL',
    dpMetadata: {
      epsilon: 1.0,
      delta: 0.001,
      noiseScale: 0.1,
    },
    ...overrides,
  };
}

/**
 * Create a mock colony structure
 */
function createMockColony(overrides?: Partial<ColonyStructure>): ColonyStructure {
  return {
    id: 'test-colony-1',
    members: ['agent-1', 'agent-2', 'agent-3'],
    communicationChannels: new Map([
      ['agent-1', 'agent-2'],
      ['agent-2', 'agent-3'],
    ]),
    formationTime: Date.now() - 10000,
    stability: 0.8,
    coEvolutionBonus: 0.2,
    ...overrides,
  };
}

// ============================================================================
// TEST SUITES
// ============================================================================

describe('MicrobiomeBridge', () => {
  let bridge: MicrobiomeBridge;
  let mockBacteria: BacteriaAgent;
  let mockCoreAgent: BaseAgent;
  let mockA2A: A2APackage<any>;
  let mockColony: ColonyStructure;

  beforeEach(() => {
    bridge = new MicrobiomeBridge({ verbose: false });
    mockBacteria = createMockBacteriaAgent();
    mockCoreAgent = createMockCoreAgent();
    mockA2A = createMockA2APackage();
    mockColony = createMockColony();
  });

  // ========================================================================
  // AGENT CONVERSION TESTS
  // ========================================================================

  describe('toCoreAgent', () => {
    it('should convert microbiome agent to core representation', () => {
      const result = bridge.toCoreAgent(mockBacteria);

      expect(result).toBeDefined();
      expect(result.config).toBeDefined();
      expect(result.goals).toBeDefined();
      expect(result.metadata).toBeDefined();

      // Check config
      expect(result.config.id).toBe(mockBacteria.id);
      expect(result.config.typeId).toBe(mockBacteria.taxonomy);
      expect(result.config.categoryId).toBe('EPHEMERAL'); // BACTERIA -> EPHEMERAL

      // Check goals
      expect(result.goals.length).toBeGreaterThan(0);
      expect(result.goals[0].preconditions.size).toBeGreaterThan(0);
      expect(result.goals[0].expectedOutcomes.size).toBeGreaterThan(0);

      // Check metadata
      expect(result.metadata.sourceSystem).toBe('microbiome');
      expect(result.metadata.originalAgentId).toBe(mockBacteria.id);
      expect(result.metadata.originalTaxonomy).toBe(mockBacteria.taxonomy);
    });

    it('should preserve health and lifecycle in metadata', () => {
      const result = bridge.toCoreAgent(mockBacteria);

      expect(result.metadata.health).toBe(mockBacteria.lifecycle.health);
      expect(result.metadata.age).toBe(mockBacteria.lifecycle.age);
      expect(result.metadata.isAlive).toBe(mockBacteria.lifecycle.isAlive);
    });

    it('should handle different agent taxonomies', () => {
      const virusAgent = createMockBacteriaAgent({
        taxonomy: AgentTaxonomy.VIRUS,
        name: 'TestVirus',
      });

      const result = bridge.toCoreAgent(virusAgent);

      expect(result.config.categoryId).toBe('CORE'); // VIRUS -> CORE
      expect(result.metadata.originalTaxonomy).toBe(AgentTaxonomy.VIRUS);
    });

    it('should cache conversion results', () => {
      bridge.toCoreAgent(mockBacteria);
      const stats = bridge.getStats();

      expect(stats.cachedConversions).toBeGreaterThan(0);
    });
  });

  describe('toMicrobiomeAgent', () => {
    it('should convert core agent to microbiome representation', () => {
      const goals: Goal[] = [
        {
          id: 'goal-1',
          name: 'test-goal',
          description: 'Test goal',
          preconditions: new Map([['text', true]]),
          expectedOutcomes: new Map([['structured', true]]),
          priority: 0.8,
          rewardFunction: (outcome: any) => 0.7,
          layer: 'HABITUAL',
        },
      ];

      const result = bridge.toMicrobiomeAgent(mockCoreAgent, {
        tileCategory: 'EPHEMERAL',
        goals,
      });

      expect(result).toBeDefined();
      expect(result.taxonomy).toBe(AgentTaxonomy.BACTERIA); // EPHEMERAL -> BACTERIA
      expect(result.metabolism).toBeDefined();
      expect(result.lifecycle).toBeDefined();
      expect(result.metadata).toBeDefined();

      // Check metabolism
      expect(result.metabolism.inputs).toContain(ResourceType.TEXT);
      expect(result.metabolism.outputs).toContain(ResourceType.STRUCTURED);
      expect(result.metabolism.processingRate).toBeGreaterThan(0);
      expect(result.metabolism.efficiency).toBeGreaterThan(0);
      expect(result.metabolism.efficiency).toBeLessThanOrEqual(1);

      // Check metadata
      expect(result.metadata.sourceSystem).toBe('core');
      expect(result.metadata.originalAgentId).toBe(mockCoreAgent.id);
      expect(result.metadata.originalTileCategory).toBe('EPHEMERAL');
    });

    it('should use custom taxonomy when provided', () => {
      const result = bridge.toMicrobiomeAgent(mockCoreAgent, {
        tileCategory: 'CORE',
        customTaxonomy: AgentTaxonomy.VIRUS,
      });

      expect(result.taxonomy).toBe(AgentTaxonomy.VIRUS);
    });

    it('should handle goals with empty preconditions', () => {
      const goals: Goal[] = [
        {
          id: 'goal-1',
          name: 'test-goal',
          description: 'Test goal',
          preconditions: new Map(),
          expectedOutcomes: new Map([['structured', true]]),
          priority: 0.5,
          rewardFunction: (outcome: any) => 0.6,
          layer: 'HABITUAL',
        },
      ];

      const result = bridge.toMicrobiomeAgent(mockCoreAgent, {
        tileCategory: 'EPHEMERAL',
        goals,
      });

      // Should use default metabolism when goals are empty
      expect(result.metabolism).toBeDefined();
      expect(result.metabolism.inputs.length).toBeGreaterThan(0);
    });

    it('should cache conversion results', () => {
      bridge.toMicrobiomeAgent(mockCoreAgent, {
        tileCategory: 'EPHEMERAL',
      });
      const stats = bridge.getStats();

      expect(stats.cachedConversions).toBeGreaterThan(0);
    });
  });

  // ========================================================================
  // TAXONOMY ↔ TILE MAPPING TESTS
  // ========================================================================

  describe('mapTaxonomyToTile', () => {
    it('should map BACTERIA to EPHEMERAL', () => {
      const result = bridge.mapTaxonomyToTile(AgentTaxonomy.BACTERIA);
      expect(result).toBe('EPHEMERAL');
    });

    it('should map VIRUS to CORE', () => {
      const result = bridge.mapTaxonomyToTile(AgentTaxonomy.VIRUS);
      expect(result).toBe('CORE');
    });

    it('should map MACROPHAGE to CORE', () => {
      const result = bridge.mapTaxonomyToTile(AgentTaxonomy.MACROPHAGE);
      expect(result).toBe('CORE');
    });

    it('should map EXPLORER to ROLE', () => {
      const result = bridge.mapTaxonomyToTile(AgentTaxonomy.EXPLORER);
      expect(result).toBe('ROLE');
    });

    it('should map COLONY to CORE', () => {
      const result = bridge.mapTaxonomyToTile(AgentTaxonomy.COLONY);
      expect(result).toBe('CORE');
    });

    it('should use custom mappings when provided', () => {
      const customBridge = new MicrobiomeBridge({
        customTaxonomyMappings: {
          [AgentTaxonomy.BACTERIA]: 'CORE' as TileCategory,
        },
      });

      const result = customBridge.mapTaxonomyToTile(AgentTaxonomy.BACTERIA);
      expect(result).toBe('CORE');
    });
  });

  describe('mapTileToTaxonomy', () => {
    it('should map EPHEMERAL to BACTERIA', () => {
      const result = bridge.mapTileToTaxonomy('EPHEMERAL');
      expect(result).toBe(AgentTaxonomy.BACTERIA);
    });

    it('should map ROLE to EXPLORER', () => {
      const result = bridge.mapTileToTaxonomy('ROLE');
      expect(result).toBe(AgentTaxonomy.EXPLORER);
    });

    it('should map CORE to MACROPHAGE', () => {
      const result = bridge.mapTileToTaxonomy('CORE');
      expect(result).toBe(AgentTaxonomy.MACROPHAGE);
    });

    it('should use custom mappings when provided', () => {
      const customBridge = new MicrobiomeBridge({
        customTileMappings: {
          'EPHEMERAL': AgentTaxonomy.VIRUS,
        },
      });

      const result = customBridge.mapTileToTaxonomy('EPHEMERAL');
      expect(result).toBe(AgentTaxonomy.VIRUS);
    });
  });

  // ========================================================================
  // METABOLISM ↔ GOAL TRANSLATION TESTS
  // ========================================================================

  describe('translateMetabolismToGoals', () => {
    it('should translate metabolism to goals', () => {
      const metabolism: MetabolicProfile = {
        inputs: [ResourceType.TEXT, ResourceType.CODE],
        outputs: [ResourceType.STRUCTURED],
        processingRate: 100,
        efficiency: 0.8,
      };

      const goals = bridge['translateMetabolismToGoals'](metabolism, AgentTaxonomy.BACTERIA);

      expect(goals).toBeDefined();
      expect(goals.length).toBeGreaterThan(0);

      const primaryGoal = goals[0];
      expect(primaryGoal.preconditions.size).toBe(2); // TEXT + CODE
      expect(primaryGoal.expectedOutcomes.size).toBe(1); // STRUCTURED
      expect(primaryGoal.priority).toBeGreaterThan(0);
      expect(primaryGoal.rewardFunction).toBeDefined();
    });

    it('should map processing rate to priority', () => {
      const metabolism: MetabolicProfile = {
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processingRate: 500,
        efficiency: 0.7,
      };

      const goals = bridge['translateMetabolismToGoals'](metabolism, AgentTaxonomy.BACTERIA);

      expect(goals[0].priority).toBeGreaterThan(0);
      expect(goals[0].priority).toBeLessThanOrEqual(1.0);
    });

    it('should add survival goal for bacteria', () => {
      const metabolism: MetabolicProfile = {
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processingRate: 100,
        efficiency: 0.8,
      };

      const goals = bridge['translateMetabolismToGoals'](metabolism, AgentTaxonomy.BACTERIA);

      // Should have primary goal + survival goal
      expect(goals.length).toBeGreaterThanOrEqual(2);
      const survivalGoal = goals.find(g => g.name === 'survival_goal');
      expect(survivalGoal).toBeDefined();
    });
  });

  describe('translateGoalsToMetabolism', () => {
    it('should translate goals to metabolism', () => {
      const goals: Goal[] = [
        {
          id: 'goal-1',
          name: 'test-goal',
          description: 'Test goal',
          preconditions: new Map([
            ['text', true],
            ['code', true],
          ]),
          expectedOutcomes: new Map([['structured', true]]),
          priority: 0.8,
          rewardFunction: (outcome: any) => 0.7,
          layer: 'HABITUAL',
        },
      ];

      const metabolism = bridge['translateGoalsToMetabolism'](goals);

      expect(metabolism).toBeDefined();
      expect(metabolism.inputs).toContain(ResourceType.TEXT);
      expect(metabolism.inputs).toContain(ResourceType.CODE);
      expect(metabolism.outputs).toContain(ResourceType.STRUCTURED);
    });

    it('should use default metabolism for empty goals', () => {
      const metabolism = bridge['translateGoalsToMetabolism']([]);

      expect(metabolism).toBeDefined();
      expect(metabolism.inputs.length).toBeGreaterThan(0);
      expect(metabolism.outputs.length).toBeGreaterThan(0);
    });

    it('should map priority to processing rate', () => {
      const goals: Goal[] = [
        {
          id: 'goal-1',
          name: 'test-goal',
          description: 'Test goal',
          preconditions: new Map([['text', true]]),
          expectedOutcomes: new Map([['structured', true]]),
          priority: 0.5,
          rewardFunction: (outcome: any) => 0.7,
          layer: 'HABITUAL',
        },
      ];

      const metabolism = bridge['translateGoalsToMetabolism'](goals);

      expect(metabolism.processingRate).toBeGreaterThan(0);
    });
  });

  // ========================================================================
  // A2A PACKAGE BRIDGING TESTS
  // ========================================================================

  describe('bridgeA2AToCore', () => {
    it('should bridge microbiome package to core format', () => {
      const microPackage = {
        id: 'micro-1',
        timestamp: Date.now(),
        sourceId: 'agent-1',
        targetId: 'agent-2',
        type: 'test-type',
        payload: { data: 'test' },
        parentIds: ['parent-1'],
        causalChainId: 'chain-1',
        privacyLevel: 'PUBLIC',
        layer: 'HABITUAL',
        dpMetadata: {
          epsilon: 1.0,
          delta: 0.001,
        },
      };

      const corePackage = bridge.bridgeA2AToCore(microPackage);

      expect(corePackage.id).toBe(microPackage.id);
      expect(corePackage.senderId).toBe(microPackage.sourceId);
      expect(corePackage.receiverId).toBe(microPackage.targetId);
      expect(corePackage.payload).toBe(microPackage.payload);
      expect(corePackage.parentIds).toEqual(microPackage.parentIds);
      expect(corePackage.causalChainId).toBe(microPackage.causalChainId);
    });

    it('should generate missing fields', () => {
      const incompletePackage = {
        sourceId: 'agent-1',
        targetId: 'agent-2',
        type: 'test-type',
        payload: { data: 'test' },
      };

      const corePackage = bridge.bridgeA2AToCore(incompletePackage);

      expect(corePackage.id).toBeDefined();
      expect(corePackage.timestamp).toBeDefined();
      expect(corePackage.parentIds).toBeDefined();
      expect(corePackage.causalChainId).toBeDefined();
    });
  });

  describe('bridgeA2AToMicrobiome', () => {
    it('should bridge core package to microbiome format', () => {
      const corePackage = createMockA2APackage();

      const microPackage = bridge.bridgeA2AToMicrobiome(corePackage);

      expect(microPackage.id).toBe(corePackage.id);
      expect(microPackage.sourceId).toBe(corePackage.senderId);
      expect(microPackage.targetId).toBe(corePackage.receiverId);
      expect(microPackage.payload).toBe(corePackage.payload);
      expect(microPackage.parentIds).toEqual(corePackage.parentIds);
      expect(microPackage.causalChainId).toBe(corePackage.causalChainId);
    });

    it('should preserve all metadata', () => {
      const corePackage = createMockA2APackage({
        dpMetadata: {
          epsilon: 1.5,
          delta: 0.002,
          noiseScale: 0.2,
        },
      });

      const microPackage = bridge.bridgeA2AToMicrobiome(corePackage);

      expect(microPackage.dpMetadata).toBeDefined();
      expect(microPackage.dpMetadata.epsilon).toBe(1.5);
      expect(microPackage.dpMetadata.delta).toBe(0.002);
      expect(microPackage.dpMetadata.noiseScale).toBe(0.2);
    });
  });

  // ========================================================================
  // COLONY SYNCHRONIZATION TESTS
  // ========================================================================

  describe('Colony Synchronization', () => {
    it('should register colony mapping', () => {
      bridge.registerColonyMapping('micro-colony-1', 'core-colony-1');

      const mappedId = bridge.getMappedColonyId('micro-colony-1', 'microbiome');
      expect(mappedId).toBe('core-colony-1');
    });

    it('should perform reverse lookup', () => {
      bridge.registerColonyMapping('micro-colony-1', 'core-colony-1');

      const mappedId = bridge.getMappedColonyId('core-colony-1', 'core');
      expect(mappedId).toBe('micro-colony-1');
    });

    it('should sync colonies', () => {
      const coreColony = {
        id: 'core-colony-1',
        agents: [
          { id: 'agent-1' },
          { id: 'agent-2' },
        ],
        communicationChannels: new Map([
          ['agent-1', ['agent-2']],
        ]),
      };

      bridge.registerColonyMapping('micro-colony-1', 'core-colony-1');
      bridge.syncColonies(mockColony, coreColony);

      // Should register mapping
      expect(bridge.getMappedColonyId('micro-colony-1', 'microbiome')).toBe('core-colony-1');
    });

    it('should return undefined for unmapped colonies', () => {
      const mappedId = bridge.getMappedColonyId('unknown-colony', 'microbiome');
      expect(mappedId).toBeUndefined();
    });

    it('should handle multiple colony mappings', () => {
      bridge.registerColonyMapping('micro-1', 'core-1');
      bridge.registerColonyMapping('micro-2', 'core-2');
      bridge.registerColonyMapping('micro-3', 'core-3');

      expect(bridge.getMappedColonyId('micro-1', 'microbiome')).toBe('core-1');
      expect(bridge.getMappedColonyId('micro-2', 'microbiome')).toBe('core-2');
      expect(bridge.getMappedColonyId('micro-3', 'microbiome')).toBe('core-3');

      const stats = bridge.getStats();
      expect(stats.registeredColonyMappings).toBe(3);
    });
  });

  // ========================================================================
  // UTILITY METHODS TESTS
  // ========================================================================

  describe('Utility Methods', () => {
    it('should return bridge statistics', () => {
      bridge.registerColonyMapping('test-micro', 'test-core');
      bridge.toCoreAgent(mockBacteria);

      const stats = bridge.getStats();

      expect(stats).toBeDefined();
      expect(stats.bridgeId).toBeDefined();
      expect(stats.registeredColonyMappings).toBeGreaterThan(0);
      expect(stats.cachedConversions).toBeGreaterThan(0);
      expect(stats.config).toBeDefined();
    });

    it('should clear conversion cache', () => {
      bridge.toCoreAgent(mockBacteria);
      let stats = bridge.getStats();
      expect(stats.cachedConversions).toBeGreaterThan(0);

      bridge.clearCache();
      stats = bridge.getStats();
      expect(stats.cachedConversions).toBe(0);
    });

    it('should include custom config in stats', () => {
      const customConfig: BridgeConfig = {
        verbose: true,
        preservationLevel: 0.9,
        autoSyncColonies: false,
        autoBridgePackages: false,
      };

      const customBridge = new MicrobiomeBridge(customConfig);
      const stats = customBridge.getStats();

      expect(stats.config.preservationLevel).toBe(0.9);
      expect(stats.config.autoSyncColonies).toBe(false);
      expect(stats.config.autoBridgePackages).toBe(false);
    });
  });

  // ========================================================================
  // FACTORY FUNCTIONS TESTS
  // ========================================================================

  describe('Factory Functions', () => {
    it('should create bridge with createMicrobiomeBridge', () => {
      const testBridge = createMicrobiomeBridge();

      expect(testBridge).toBeInstanceOf(MicrobiomeBridge);
      expect(testBridge.getStats().config.verbose).toBe(false);
    });

    it('should create verbose bridge with createVerboseBridge', () => {
      const testBridge = createVerboseBridge();

      expect(testBridge).toBeInstanceOf(MicrobiomeBridge);
      expect(testBridge.getStats().config.verbose).toBe(true);
    });

    it('should pass config to createMicrobiomeBridge', () => {
      const config: BridgeConfig = {
        preservationLevel: 0.95,
        autoSyncColonies: false,
      };

      const testBridge = createMicrobiomeBridge(config);
      const stats = testBridge.getStats();

      expect(stats.config.preservationLevel).toBe(0.95);
      expect(stats.config.autoSyncColonies).toBe(false);
    });
  });

  // ========================================================================
  // INTEGRATION TESTS
  // ========================================================================

  describe('Integration Tests', () => {
    it('should handle full round-trip conversion', () => {
      // Microbiome -> Core
      const coreRepresentation = bridge.toCoreAgent(mockBacteria);

      // Core -> Microbiome (simulated)
      const microbiomeRepresentation = bridge.toMicrobiomeAgent(
        mockCoreAgent,
        {
          tileCategory: coreRepresentation.config.categoryId as TileCategory,
          goals: coreRepresentation.goals,
        }
      );

      // Verify round-trip preservation
      expect(microbiomeRepresentation.taxonomy).toBeDefined();
      expect(microbiomeRepresentation.metabolism).toBeDefined();
      expect(microbiomeRepresentation.lifecycle).toBeDefined();
    });

    it('should handle full A2A package round-trip', () => {
      const originalPackage = createMockA2APackage();

      // Core -> Microbiome
      const microPackage = bridge.bridgeA2AToMicrobiome(originalPackage);

      // Microbiome -> Core
      const corePackage = bridge.bridgeA2AToCore(microPackage);

      // Verify preservation
      expect(corePackage.id).toBe(originalPackage.id);
      expect(corePackage.senderId).toBe(originalPackage.senderId);
      expect(corePackage.receiverId).toBe(originalPackage.receiverId);
      expect(corePackage.payload).toEqual(originalPackage.payload);
      expect(corePackage.parentIds).toEqual(originalPackage.parentIds);
    });

    it('should handle colony mapping and sync together', () => {
      // Register multiple colonies
      bridge.registerColonyMapping('micro-1', 'core-1');
      bridge.registerColonyMapping('micro-2', 'core-2');

      // Sync first colony
      const coreColony = {
        id: 'core-1',
        agents: [{ id: 'agent-1' }],
        communicationChannels: new Map(),
      };

      bridge.syncColonies(mockColony, coreColony);

      // Verify mappings
      expect(bridge.getMappedColonyId('micro-1', 'microbiome')).toBe('core-1');
      expect(bridge.getMappedColonyId('micro-2', 'microbiome')).toBe('core-2');
    });

    it('should maintain consistency across multiple operations', () => {
      // Convert multiple agents
      const agent1 = createMockBacteriaAgent({ id: 'agent-1' });
      const agent2 = createMockBacteriaAgent({ id: 'agent-2' });
      const agent3 = createMockBacteriaAgent({ id: 'agent-3' });

      bridge.toCoreAgent(agent1);
      bridge.toCoreAgent(agent2);
      bridge.toCoreAgent(agent3);

      // Bridge multiple packages
      bridge.bridgeA2AToCore(createMockA2APackage());
      bridge.bridgeA2AToCore(createMockA2APackage());

      // Register multiple colonies
      bridge.registerColonyMapping('micro-1', 'core-1');
      bridge.registerColonyMapping('micro-2', 'core-2');

      // Verify consistency
      const stats = bridge.getStats();
      expect(stats.cachedConversions).toBe(3);
      expect(stats.registeredColonyMappings).toBe(2);
    });
  });

  // ========================================================================
  // EDGE CASE TESTS
  // ========================================================================

  describe('Edge Cases', () => {
    it('should handle agents with empty metabolism', () => {
      const emptyMetabolismAgent = createMockBacteriaAgent({
        metabolism: {
          inputs: [],
          outputs: [],
          processingRate: 0,
          efficiency: 0,
        },
      });

      const result = bridge.toCoreAgent(emptyMetabolismAgent);

      expect(result).toBeDefined();
      expect(result.config).toBeDefined();
    });

    it('should handle agents with maximum processing rate', () => {
      const maxProcessingAgent = createMockBacteriaAgent({
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 10000,
          efficiency: 1.0,
        },
      });

      const result = bridge.toCoreAgent(maxProcessingAgent);
      const goals = bridge['translateMetabolismToGoals'](maxProcessingAgent.metabolism, AgentTaxonomy.BACTERIA);

      // Priority should be capped at 1.0
      expect(goals[0].priority).toBeLessThanOrEqual(1.0);
    });

    it('should handle agents with zero efficiency', () => {
      const zeroEfficiencyAgent = createMockBacteriaAgent({
        metabolism: {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 100,
          efficiency: 0,
        },
      });

      const result = bridge.toCoreAgent(zeroEfficiencyAgent);

      expect(result).toBeDefined();
      expect(result.config).toBeDefined();
    });

    it('should handle colony with no members', () => {
      const emptyColony = createMockColony({
        members: [],
        communicationChannels: new Map(),
      });

      const coreColony = {
        id: 'core-1',
        agents: [],
        communicationChannels: new Map(),
      };

      expect(() => {
        bridge.syncColonies(emptyColony, coreColony);
      }).not.toThrow();
    });

    it('should handle package with no payload', () => {
      const emptyPackage = createMockA2APackage({
        payload: undefined,
      });

      const result = bridge.bridgeA2AToCore(emptyPackage);

      expect(result).toBeDefined();
      expect(result.payload).toBeUndefined();
    });
  });
});
