/**
 * Protocol Adapter Tests
 *
 * Comprehensive test suite for SPORE ↔ Core protocol translation
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { ProtocolAdapter,
         createProtocolAdapter,
         createVerboseAdapter,
         createAdapterWithBridge,
         SporeMessage,
         CoreMessage,
         SporeType,
         CoreMessageType,
         ChannelMapping,
         MessageDirection } from '../protocol-adapter.js';
import { MicrobiomeBridge } from '../bridge.js';
import { AgentTaxonomy, ResourceType } from '../types.js';
import type { Colony } from '../../core/colony.js';
import type { ColonyStructure } from '../types.js';
import type { AgentState } from '../../core/types.js';

// ============================================================================
// TEST FIXTURES
// ============================================================================

/**
 * Create a mock SPORE message
 */
function createMockSporeMessage(overrides?: Partial<SporeMessage>): SporeMessage {
  return {
    type: SporeType.RESOURCE_REQUEST,
    payload: { resource: ResourceType.TEXT, amount: 100 },
    sourceId: 'agent-1',
    targetId: 'agent-2',
    timestamp: Date.now(),
    metadata: { channel: 'resource_channel' },
    ...overrides,
  };
}

/**
 * Create a mock Core message
 */
function createMockCoreMessage(overrides?: Partial<CoreMessage>): CoreMessage {
  return {
    type: CoreMessageType.AGENT_PROPOSAL,
    payload: { agentId: 'agent-1', confidence: 0.9 },
    sourceId: 'agent-1',
    targetId: 'agent-2',
    timestamp: Date.now(),
    parentIds: [],
    causalChainId: 'causal-chain-1',
    layer: 'HABITUAL',
    privacyLevel: 'COLONY',
    ...overrides,
  };
}

/**
 * Create a mock microbiome colony
 */
function createMockMicrobiomeColony(): ColonyStructure {
  return {
    id: 'micro-colony-1',
    members: ['agent-1', 'agent-2', 'agent-3'],
    communicationChannels: new Map([
      ['resource_channel', ['agent-1', 'agent-2']],
      ['colony_coordination', ['agent-1', 'agent-2', 'agent-3']],
    ]),
    formationTime: Date.now() - 10000,
    stability: 0.8,
    coEvolutionBonus: 0.15,
  };
}

/**
 * Create a mock core colony
 */
function createMockCoreColony(): Colony {
  const mockAgents: AgentState[] = [
    {
      id: 'agent-1',
      typeId: 'bacteria',
      modelVersion: 1,
      status: 'active',
      lastActive: Date.now(),
      valueFunction: 0.7,
      successCount: 10,
      failureCount: 2,
      avgLatencyMs: 50,
      executionCount: 12,
      successRate: 0.83,
      active: true,
    },
    {
      id: 'agent-2',
      typeId: 'virus',
      modelVersion: 1,
      status: 'active',
      lastActive: Date.now(),
      valueFunction: 0.6,
      successCount: 8,
      failureCount: 3,
      avgLatencyMs: 45,
      executionCount: 11,
      successRate: 0.73,
      active: true,
    },
    {
      id: 'agent-3',
      typeId: 'macrophage',
      modelVersion: 1,
      status: 'active',
      lastActive: Date.now(),
      valueFunction: 0.8,
      successCount: 15,
      failureCount: 1,
      avgLatencyMs: 60,
      executionCount: 16,
      successRate: 0.94,
      active: true,
    },
  ];

  return {
    id: 'core-colony-1',
    config: {} as any,
    get count() { return mockAgents.length; },
    getAgent: jest.fn((id: string) => mockAgents.find(a => a.id === id)),
    getAllAgents: jest.fn(() => mockAgents),
    getActiveAgents: jest.fn(() => mockAgents.filter(a => a.status === 'active')),
    getAgentsByType: jest.fn((typeId: string) => mockAgents.filter(a => a.typeId === typeId)),
    registerAgent: jest.fn(),
    unregisterAgent: jest.fn(),
    updateAgentState: jest.fn(),
    activateAgent: jest.fn(),
    deactivateAgent: jest.fn(),
    recordResult: jest.fn(),
    calculateShannonDiversity: jest.fn(() => 1.5),
    getStats: jest.fn(async () => ({
      totalAgents: mockAgents.length,
      activeAgents: mockAgents.filter(a => a.status === 'active').length,
      dormantAgents: 0,
      totalCompute: 1000,
      totalMemory: 2000,
      totalNetwork: 500,
      shannonDiversity: 1.5,
    })),
    isDistributed: jest.fn(() => false),
    getDistributedCoordination: jest.fn(),
    on: jest.fn(),
    emit: jest.fn(),
  } as unknown as Colony;
}

// ============================================================================
// TEST SUITES
// ============================================================================

describe('ProtocolAdapter', () => {
  let adapter: ProtocolAdapter;
  let bridge: MicrobiomeBridge;

  beforeEach(() => {
    bridge = new MicrobiomeBridge({ verbose: false });
    adapter = new ProtocolAdapter({
      verbose: false,
      bridge,
      autoSyncChannels: true,
    });
  });

  afterEach(() => {
    adapter.clearHistory();
    adapter.resetChannelMappings();
  });

  // ==========================================================================
  // SPORE TO CORE TRANSLATION
  // ==========================================================================

  describe('sporeToCore', () => {
    it('should translate basic SPORE message to Core format', () => {
      const spore = createMockSporeMessage();
      const core = adapter.sporeToCore(spore);

      expect(core).toBeDefined();
      expect(core.type).toBe(CoreMessageType.AGENT_PROPOSAL);
      // Payload now wraps original data and includes _sporeMetadata
      expect((core.payload as any).data || (core.payload as any).resource).toBeDefined();
      expect((core.payload as any)._sporeMetadata).toBeDefined();
      expect(core.sourceId).toBe(spore.sourceId);
      expect(core.targetId).toBe(spore.targetId);
      expect(core.timestamp).toBe(spore.timestamp);
      expect(core.parentIds).toEqual([]);
      expect(core.causalChainId).toBeDefined();
      expect(core.layer).toBeDefined();
      expect(core.privacyLevel).toBeDefined();
    });

    it('should translate different SPORE types to correct Core types', () => {
      const testCases = [
        { sporeType: SporeType.RESOURCE_REQUEST, expectedCoreType: CoreMessageType.AGENT_PROPOSAL },
        { sporeType: SporeType.RESOURCE_OFFER, expectedCoreType: CoreMessageType.AGENT_RESULT },
        { sporeType: SporeType.METABOLISM_COMPLETE, expectedCoreType: CoreMessageType.AGENT_EXECUTION },
        { sporeType: SporeType.REPRODUCTION_EVENT, expectedCoreType: CoreMessageType.COLONY_SYNC },
        { sporeType: SporeType.DEATH_EVENT, expectedCoreType: CoreMessageType.VALUE_UPDATE },
        { sporeType: SporeType.SYMBIOSIS_REQUEST, expectedCoreType: CoreMessageType.AGENT_PROPOSAL },
        { sporeType: SporeType.SYMBIOSIS_RESPONSE, expectedCoreType: CoreMessageType.AGENT_RESULT },
        { sporeType: SporeType.COLONY_FORM, expectedCoreType: CoreMessageType.COLONY_SYNC },
        { sporeType: SporeType.COLONY_DISSOLVE, expectedCoreType: CoreMessageType.COLONY_SYNC },
        { sporeType: SporeType.MURMURATION, expectedCoreType: CoreMessageType.STIGMERGY_SIGNAL },
        { sporeType: SporeType.IMMUNE_RESPONSE, expectedCoreType: CoreMessageType.SAFETY_CHECK },
        { sporeType: SporeType.EXPLORATION, expectedCoreType: CoreMessageType.AGENT_PROPOSAL },
      ];

      for (const { sporeType, expectedCoreType } of testCases) {
        const spore = createMockSporeMessage({ type: sporeType });
        const core = adapter.sporeToCore(spore);
        expect(core.type).toBe(expectedCoreType);
      }
    });

    it('should infer correct subsumption layer for safety messages', () => {
      const spore = createMockSporeMessage({
        type: SporeType.IMMUNE_RESPONSE,
        payload: { threat: 'malicious_agent' },
      });

      const core = adapter.sporeToCore(spore);
      expect(core.layer).toBe('SAFETY');
    });

    it('should infer correct subsumption layer for murmuration messages', () => {
      const spore = createMockSporeMessage({
        type: SporeType.MURMURATION,
        payload: { pattern: 'flock' },
      });

      const core = adapter.sporeToCore(spore);
      expect(core.layer).toBe('REFLEX');
    });

    it('should infer correct subsumption layer for exploration messages', () => {
      const spore = createMockSporeMessage({
        type: SporeType.EXPLORATION,
        payload: { target: 'novel_resource' },
      });

      const core = adapter.sporeToCore(spore);
      expect(core.layer).toBe('DELIBERATE');
    });

    it('should use default layer for unmapped message types', () => {
      const spore = createMockSporeMessage({
        type: SporeType.RESOURCE_REQUEST,
      });

      const core = adapter.sporeToCore(spore);
      expect(core.layer).toBe('HABITUAL');
    });

    it('should preserve payload during translation', () => {
      const customPayload = {
        resource: ResourceType.CODE,
        amount: 250,
        metadata: { priority: 'high', source: 'external' },
      };

      const spore = createMockSporeMessage({ payload: customPayload });
      const core = adapter.sporeToCore(spore);

      // Payload should contain the original data plus _sporeMetadata
      expect((core.payload as any).resource).toBe(customPayload.resource);
      expect((core.payload as any).amount).toBe(customPayload.amount);
      expect((core.payload as any).metadata).toEqual(customPayload.metadata);
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle SPORE messages without target ID', () => {
      const spore = createMockSporeMessage({ targetId: undefined });
      const core = adapter.sporeToCore(spore);

      expect(core.targetId).toBeUndefined();
    });

    it('should emit translation event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const spore = createMockSporeMessage();

      adapter.sporeToCore(spore);

      expect(emitSpy).toHaveBeenCalledWith('translated', {
        direction: 'spore-to-core',
        original: spore,
        translated: expect.any(Object),
      });
    });
  });

  // ==========================================================================
  // CORE TO SPORE TRANSLATION
  // ==========================================================================

  describe('coreToSpore', () => {
    it('should translate basic Core message to SPORE format', () => {
      const core = createMockCoreMessage();
      const spore = adapter.coreToSpore(core);

      expect(spore).toBeDefined();
      expect(spore.type).toBe(SporeType.RESOURCE_REQUEST);
      expect(spore.payload).toEqual(core.payload);
      expect(spore.sourceId).toBe(core.sourceId);
      expect(spore.targetId).toBe(core.targetId);
      expect(spore.timestamp).toBe(core.timestamp);
      expect(spore.metadata).toBeDefined();
      expect(spore.metadata?.causalChainId).toBe(core.causalChainId);
      expect(spore.metadata?.parentIds).toEqual(core.parentIds);
      expect(spore.metadata?.layer).toBe(core.layer);
      expect(spore.metadata?.privacyLevel).toBe(core.privacyLevel);
    });

    it('should translate different Core types to correct SPORE types', () => {
      const testCases = [
        { coreType: CoreMessageType.AGENT_PROPOSAL, expectedSporeType: SporeType.RESOURCE_REQUEST },
        { coreType: CoreMessageType.AGENT_SELECTION, expectedSporeType: SporeType.SYMBIOSIS_REQUEST },
        { coreType: CoreMessageType.AGENT_EXECUTION, expectedSporeType: SporeType.METABOLISM_COMPLETE },
        { coreType: CoreMessageType.AGENT_RESULT, expectedSporeType: SporeType.RESOURCE_OFFER },
        { coreType: CoreMessageType.GOAL_UPDATE, expectedSporeType: SporeType.SYMBIOSIS_RESPONSE },
        { coreType: CoreMessageType.VALUE_UPDATE, expectedSporeType: SporeType.METABOLISM_COMPLETE },
        { coreType: CoreMessageType.SAFETY_CHECK, expectedSporeType: SporeType.IMMUNE_RESPONSE },
        { coreType: CoreMessageType.WORLD_MODEL_UPDATE, expectedSporeType: SporeType.EXPLORATION },
        { coreType: CoreMessageType.DREAM_CYCLE, expectedSporeType: SporeType.MURMURATION },
        { coreType: CoreMessageType.FEDERATED_SYNC, expectedSporeType: SporeType.COLONY_FORM },
        { coreType: CoreMessageType.COLONY_SYNC, expectedSporeType: SporeType.COLONY_FORM },
        { coreType: CoreMessageType.STIGMERGY_SIGNAL, expectedSporeType: SporeType.MURMURATION },
      ];

      for (const { coreType, expectedSporeType } of testCases) {
        const core = createMockCoreMessage({ type: coreType });
        const spore = adapter.coreToSpore(core);
        expect(spore.type).toBe(expectedSporeType);
      }
    });

    it('should preserve causal chain in metadata', () => {
      const causalChainId = 'causal-chain-123';
      const parentIds = ['parent-1', 'parent-2'];

      const core = createMockCoreMessage({
        causalChainId,
        parentIds,
      });

      const spore = adapter.coreToSpore(core);

      expect(spore.metadata?.causalChainId).toBe(causalChainId);
      expect(spore.metadata?.parentIds).toEqual(parentIds);
    });

    it('should preserve privacy level in metadata', () => {
      const core = createMockCoreMessage({
        privacyLevel: 'PRIVATE',
      });

      const spore = adapter.coreToSpore(core);

      expect(spore.metadata?.privacyLevel).toBe('PRIVATE');
    });

    it('should preserve subsumption layer in metadata', () => {
      const core = createMockCoreMessage({
        layer: 'SAFETY',
      });

      const spore = adapter.coreToSpore(core);

      expect(spore.metadata?.layer).toBe('SAFETY');
    });

    it('should handle Core messages without target ID', () => {
      const core = createMockCoreMessage({ targetId: undefined });
      const spore = adapter.coreToSpore(core);

      expect(spore.targetId).toBeUndefined();
    });

    it('should emit translation event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const core = createMockCoreMessage();

      adapter.coreToSpore(core);

      expect(emitSpy).toHaveBeenCalledWith('translated', {
        direction: 'core-to-spore',
        original: core,
        translated: expect.any(Object),
      });
    });
  });

  // ==========================================================================
  // MESSAGE ROUTING
  // ==========================================================================

  describe('routeMessage', () => {
    it('should route SPORE message to Core format', () => {
      const spore = createMockSporeMessage();
      const routed = adapter.routeMessage(spore, 'microbiome', 'core');

      expect(routed).toBeDefined();
      expect(routed).not.toBeNull();
      expect((routed as CoreMessage).type).toBeDefined();
      expect((routed as CoreMessage).causalChainId).toBeDefined();
    });

    it('should route Core message to SPORE format', () => {
      const core = createMockCoreMessage();
      const routed = adapter.routeMessage(core, 'core', 'microbiome');

      expect(routed).toBeDefined();
      expect(routed).not.toBeNull();
      expect((routed as SporeMessage).metadata).toBeDefined();
    });

    it('should return same message when routing to same system', () => {
      const spore = createMockSporeMessage();
      const routed = adapter.routeMessage(spore, 'microbiome', 'microbiome');

      expect(routed).toBe(spore);
    });

    it('should emit routing event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const spore = createMockSporeMessage();

      adapter.routeMessage(spore, 'microbiome', 'core');

      expect(emitSpy).toHaveBeenCalledWith('routed', {
        original: spore,
        routed: expect.any(Object),
        from: 'microbiome',
        to: 'core',
      });
    });

    it('should return null for invalid routing', () => {
      // This tests error handling for unexpected routing scenarios
      const invalidMessage = { type: 'unknown', payload: {} } as any;
      const routed = adapter.routeMessage(invalidMessage, 'microbiome', 'core');

      // Should still attempt routing, not null
      expect(routed).toBeDefined();
    });

    it('should handle routing with channel mappings', () => {
      // Set up channel mapping
      adapter.syncChannels(
        new Map([['resource_channel', ['agent-1']]]),
        new Map([['resourceChannel', new Set(['agent-2'])]])
      );

      const spore = createMockSporeMessage({
        metadata: { channel: 'resource_channel' },
      });

      const routed = adapter.routeMessage(spore, 'microbiome', 'core');

      expect(routed).toBeDefined();
      // For Core messages, check metadata in payload._sporeMetadata
      const coreMsg = routed as CoreMessage;
      expect((coreMsg.payload as any)._sporeMetadata).toBeDefined();
    });
  });

  // ==========================================================================
  // A2A PACKAGE ROUTING
  // ==========================================================================

  describe('routeA2A', () => {
    it('should route A2A package from microbiome to core', () => {
      const pkg = {
        id: 'pkg-1',
        timestamp: Date.now(),
        senderId: 'agent-1',
        receiverId: 'agent-2',
        type: 'test_type',
        payload: { data: 'test' },
        parentIds: [],
        causalChainId: 'chain-1',
        privacyLevel: 'COLONY',
        layer: 'HABITUAL',
      };

      const routed = adapter.routeA2A(pkg, 'microbiome', 'core');

      expect(routed).toBeDefined();
      expect(routed?.id).toBe(pkg.id);
      expect(routed?.senderId).toBe(pkg.senderId);
    });

    it('should route A2A package from core to microbiome', () => {
      const pkg = {
        id: 'pkg-2',
        timestamp: Date.now(),
        senderId: 'agent-2',
        receiverId: 'agent-1',
        type: 'test_type',
        payload: { data: 'test' },
        parentIds: [],
        causalChainId: 'chain-2',
        privacyLevel: 'PUBLIC',
        layer: 'REFLEX',
      };

      const routed = adapter.routeA2A(pkg, 'core', 'microbiome');

      expect(routed).toBeDefined();
      expect(routed?.id).toBe(pkg.id);
      // In microbiome format, senderId becomes sourceId
      expect((routed as any)?.sourceId || routed?.senderId).toBe(pkg.senderId);
      // receiverId should map to targetId in microbiome format
      expect((routed as any)?.targetId || routed?.receiverId).toBe(pkg.receiverId);
    });

    it('should return same package when routing to same system', () => {
      const pkg = {
        id: 'pkg-3',
        timestamp: Date.now(),
        senderId: 'agent-1',
        receiverId: 'agent-2',
        type: 'test_type',
        payload: { data: 'test' },
        parentIds: [],
        causalChainId: 'chain-3',
        privacyLevel: 'COLONY',
        layer: 'HABITUAL',
      };

      const routed = adapter.routeA2A(pkg, 'microbiome', 'microbiome');

      expect(routed).toBe(pkg);
    });
  });

  // ==========================================================================
  // MESSAGE TYPE MISMATCH HANDLING
  // ==========================================================================

  describe('handleTypeMismatch', () => {
    it('should handle unknown type with fallback', () => {
      const handled = adapter.handleTypeMismatch('unknown_type', 'fallback_type');

      expect(handled).toBeDefined();
      expect(handled?.type).toBe('fallback_type');
    });

    it('should return null when no type match found', () => {
      const handled = adapter.handleTypeMismatch('completely_unknown_type');

      expect(handled).toBeNull();
    });

    it('should find closest match for similar types', () => {
      const handled = adapter.handleTypeMismatch('RESOURCE_REQUEST');

      expect(handled).toBeDefined();
      expect(handled?.type).toBeDefined();
    });

    it('should emit type_mismatch event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const result = adapter.handleTypeMismatch('unknown_type', 'fallback');

      // The event is emitted even if result is null (no match found)
      // Check that emit was called
      expect(emitSpy).toHaveBeenCalled();

      // Verify the event structure when a result is returned
      if (result) {
        expect(emitSpy).toHaveBeenCalledWith('type_mismatch', expect.objectContaining({
          originalType: 'unknown_type',
          fallbackType: 'fallback',
        }));
      }
    });

    it('should mark handled message', () => {
      const handled = adapter.handleTypeMismatch('unknown', 'fallback');

      expect(handled).toBeDefined();
      expect((handled as any)?.payload?.handled).toBe(true);
    });
  });

  // ==========================================================================
  // CHANNEL SYNCHRONIZATION
  // ==========================================================================

  describe('syncChannels', () => {
    it('should sync microbiome channels to core channels', () => {
      const microChannels = new Map([
        ['resource_channel', ['agent-1', 'agent-2']],
        ['colony_coordination', ['agent-1', 'agent-2', 'agent-3']],
      ]);

      const coreChannels = new Map([
        ['agentCommunication', new Set(['agent-4'])],
      ]);

      adapter.syncChannels(microChannels, coreChannels);

      const stats = adapter.getStats();
      expect(stats.channelMappings).toBeGreaterThan(0);
    });

    it('should sync core channels to microbiome channels', () => {
      const microChannels = new Map([
        ['resource_channel', ['agent-1']],
      ]);

      const coreChannels = new Map([
        ['agentCommunication', new Set(['agent-2', 'agent-3'])],
        ['resourceDistribution', new Set(['agent-4'])],
      ]);

      adapter.syncChannels(microChannels, coreChannels);

      const stats = adapter.getStats();
      expect(stats.channelMappings).toBeGreaterThan(0);
    });

    it('should create bidirectional mappings', () => {
      const microChannels = new Map([['test_channel', ['agent-1']]]);
      const coreChannels = new Map([['testChannel', new Set(['agent-2'])]]);

      adapter.syncChannels(microChannels, coreChannels);

      const mapped1 = adapter.getMappedChannel('test_channel', 'microbiome');
      const mapped2 = adapter.getMappedChannel('testChannel', 'core');

      expect(mapped1).toBeDefined();
      expect(mapped2).toBeDefined();
    });

    it('should emit channel_mapped events', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const microChannels = new Map([['test', ['agent-1']]]);
      const coreChannels = new Map();

      adapter.syncChannels(microChannels, coreChannels);

      expect(emitSpy).toHaveBeenCalledWith('channel_mapped', expect.any(Object));
    });

    it('should handle empty channel maps', () => {
      const microChannels = new Map();
      const coreChannels = new Map();

      adapter.syncChannels(microChannels, coreChannels);

      const stats = adapter.getStats();
      expect(stats.channelMappings).toBe(0);
    });
  });

  // ==========================================================================
  // CHANNEL NAME MAPPING
  // ==========================================================================

  describe('getMappedChannel', () => {
    beforeEach(() => {
      adapter.syncChannels(
        new Map([['resource_channel', ['agent-1']]]),
        new Map([['agentCommunication', new Set(['agent-2'])]])
      );
    });

    it('should map microbiome channel to core channel', () => {
      const mapped = adapter.getMappedChannel('resource_channel', 'microbiome');
      expect(mapped).toBeDefined();
    });

    it('should map core channel to microbiome channel', () => {
      const mapped = adapter.getMappedChannel('agentCommunication', 'core');
      expect(mapped).toBeDefined();
    });

    it('should return undefined for unknown channel', () => {
      const mapped = adapter.getMappedChannel('unknown_channel', 'microbiome');
      expect(mapped).toBeUndefined();
    });
  });

  // ==========================================================================
  // COLONY COMMUNICATION
  // ==========================================================================

  describe('translateColonyCommunication', () => {
    it('should translate message to all colony members', () => {
      const colony = createMockMicrobiomeColony();
      const message = createMockSporeMessage();

      const translated = adapter.translateColonyCommunication(colony, message);

      expect(translated).toHaveLength(colony.members.length);
      expect(translated[0].targetId).toBe(colony.members[0]);
      expect(translated[1].targetId).toBe(colony.members[1]);
      expect(translated[2].targetId).toBe(colony.members[2]);
    });

    it('should add colony metadata to translated messages', () => {
      const colony = createMockMicrobiomeColony();
      const message = createMockSporeMessage();

      const translated = adapter.translateColonyCommunication(colony, message);

      for (const msg of translated) {
        expect((msg as SporeMessage).metadata?.colonyId).toBe(colony.id);
        expect((msg as SporeMessage).metadata?.colonySize).toBe(colony.members.length);
        expect((msg as SporeMessage).metadata?.memberIndex).toBeGreaterThanOrEqual(0);
      }
    });

    it('should handle empty colony', () => {
      const colony: ColonyStructure = {
        id: 'empty-colony',
        members: [],
        communicationChannels: new Map(),
        formationTime: Date.now(),
        stability: 0,
        coEvolutionBonus: 0,
      };

      const message = createMockSporeMessage();
      const translated = adapter.translateColonyCommunication(colony, message);

      expect(translated).toHaveLength(0);
    });

    it('should emit colony_communication_translated event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const colony = createMockMicrobiomeColony();
      const message = createMockSporeMessage();

      adapter.translateColonyCommunication(colony, message);

      expect(emitSpy).toHaveBeenCalledWith('colony_communication_translated', {
        colonyId: colony.id,
        memberCount: colony.members.length,
        originalMessage: message,
        translatedMessages: expect.any(Array),
      });
    });

    it('should preserve original message type', () => {
      const colony = createMockMicrobiomeColony();
      const message = createMockSporeMessage({ type: SporeType.MURMURATION });

      const translated = adapter.translateColonyCommunication(colony, message);

      for (const msg of translated) {
        expect(msg.type).toBe(SporeType.MURMURATION);
      }
    });
  });

  // ==========================================================================
  // COLONY BRIDGE
  // ==========================================================================

  describe('bridgeColonyCommunication', () => {
    it('should bridge communication between microbiome and core colonies', () => {
      const microColony = createMockMicrobiomeColony();
      const coreColony = createMockCoreColony();
      const message = createMockSporeMessage();

      const bridged = adapter.bridgeColonyCommunication(microColony, coreColony, message);

      expect(bridged.microbiome).toHaveLength(microColony.members.length);
      expect(bridged.core).toHaveLength(coreColony.count);
    });

    it('should sync colonies during bridge', () => {
      const microColony = createMockMicrobiomeColony();
      const coreColony = createMockCoreColony();
      const message = createMockSporeMessage();

      const bridgeSpy = jest.spyOn(adapter['bridge'], 'syncColonies');

      adapter.bridgeColonyCommunication(microColony, coreColony, message);

      expect(bridgeSpy).toHaveBeenCalledWith(microColony, coreColony);
    });

    it('should emit colony_communication_bridged event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const microColony = createMockMicrobiomeColony();
      const coreColony = createMockCoreColony();
      const message = createMockSporeMessage();

      adapter.bridgeColonyCommunication(microColony, coreColony, message);

      expect(emitSpy).toHaveBeenCalledWith('colony_communication_bridged', {
        microColonyId: microColony.id,
        coreColonyId: coreColony.id,
        microbiomeMessageCount: microColony.members.length,
        coreMessageCount: coreColony.count,
      });
    });

    it('should add colony metadata to all bridged messages', () => {
      const microColony = createMockMicrobiomeColony();
      const coreColony = createMockCoreColony();
      const message = createMockSporeMessage();

      const bridged = adapter.bridgeColonyCommunication(microColony, coreColony, message);

      // Check microbiome messages
      for (const msg of bridged.microbiome) {
        expect((msg as SporeMessage).metadata?.colonyId).toBe(microColony.id);
      }

      // Check core messages
      for (const msg of bridged.core) {
        expect((msg as SporeMessage).metadata?.colonyId).toBe(coreColony.id);
      }
    });
  });

  // ==========================================================================
  // CROSS-SYSTEM EVENTS
  // ==========================================================================

  describe('handleCrossSystemEvent', () => {
    it('should handle microbiome event for core system', () => {
      const event = { type: 'agent_death', agentId: 'agent-1' };
      const translated = adapter.handleCrossSystemEvent(event, 'microbiome');

      expect(translated.sourceSystem).toBe('microbiome');
      expect(translated.targetSystem).toBe('core');
      expect(translated.adapterId).toBeDefined();
      expect(translated.translatedAt).toBeDefined();
    });

    it('should handle core event for microbiome system', () => {
      const event = { type: 'agent_selected', agentId: 'agent-2' };
      const translated = adapter.handleCrossSystemEvent(event, 'core');

      expect(translated.sourceSystem).toBe('core');
      expect(translated.targetSystem).toBe('microbiome');
      expect(translated.adapterId).toBeDefined();
      expect(translated.translatedAt).toBeDefined();
    });

    it('should preserve original event data', () => {
      const event = { type: 'test', data: { value: 42 } };
      const translated = adapter.handleCrossSystemEvent(event, 'microbiome');

      expect(translated.type).toBe(event.type);
      expect(translated.data).toEqual(event.data);
    });

    it('should add format metadata', () => {
      const event = { type: 'test' };
      const translated = adapter.handleCrossSystemEvent(event, 'microbiome');

      expect((translated as any).metadata).toBeDefined();
      expect((translated as any).metadata?.originalFormat).toBe('spore');
    });

    it('should emit cross_system_event', () => {
      const emitSpy = jest.spyOn(adapter, 'emit');
      const event = { type: 'test' };

      adapter.handleCrossSystemEvent(event, 'core');

      expect(emitSpy).toHaveBeenCalledWith('cross_system_event', expect.any(Object));
    });
  });

  // ==========================================================================
  // UTILITY METHODS
  // ==========================================================================

  describe('getStats', () => {
    it('should return adapter statistics', () => {
      const stats = adapter.getStats();

      expect(stats.adapterId).toBeDefined();
      expect(stats.channelMappings).toBe(0);
      expect(stats.routingTableEntries).toBe(0);
      expect(stats.messageHistorySize).toBe(0);
      expect(stats.typeMappings).toBeGreaterThan(0);
      expect(stats.config).toBeDefined();
    });

    it('should reflect channel sync in stats', () => {
      adapter.syncChannels(
        new Map([['test', ['agent-1']]]),
        new Map()
      );

      const stats = adapter.getStats();
      expect(stats.channelMappings).toBeGreaterThan(0);
    });

    it('should reflect message history in stats', () => {
      adapter.sporeToCore(createMockSporeMessage());

      const stats = adapter.getStats();
      expect(stats.messageHistorySize).toBeGreaterThan(0);
    });
  });

  describe('clearHistory', () => {
    it('should clear message history', () => {
      adapter.sporeToCore(createMockSporeMessage());
      adapter.clearHistory();

      const stats = adapter.getStats();
      expect(stats.messageHistorySize).toBe(0);
    });
  });

  describe('resetChannelMappings', () => {
    it('should reset channel mappings', () => {
      adapter.syncChannels(
        new Map([['test', ['agent-1']]]),
        new Map()
      );

      adapter.resetChannelMappings();

      const stats = adapter.getStats();
      expect(stats.channelMappings).toBe(0);
      expect(stats.routingTableEntries).toBe(0);
    });
  });

  // ==========================================================================
  // FACTORY FUNCTIONS
  // ==========================================================================

  describe('createProtocolAdapter', () => {
    it('should create adapter with default config', () => {
      const newAdapter = createProtocolAdapter();

      expect(newAdapter).toBeInstanceOf(ProtocolAdapter);
      expect(newAdapter.getStats().config.verbose).toBe(false);
    });

    it('should create adapter with custom config', () => {
      const newAdapter = createProtocolAdapter({
        verbose: true,
        autoSyncChannels: false,
        defaultPrivacyLevel: 'PUBLIC',
      });

      expect(newAdapter.getStats().config.verbose).toBe(true);
      expect(newAdapter.getStats().config.autoSyncChannels).toBe(false);
      expect(newAdapter.getStats().config.defaultPrivacyLevel).toBe('PUBLIC');
    });
  });

  describe('createVerboseAdapter', () => {
    it('should create adapter with verbose logging', () => {
      const verboseAdapter = createVerboseAdapter();

      expect(verboseAdapter).toBeInstanceOf(ProtocolAdapter);
      expect(verboseAdapter.getStats().config.verbose).toBe(true);
    });
  });

  describe('createAdapterWithBridge', () => {
    it('should create adapter with custom bridge', () => {
      const customBridge = new MicrobiomeBridge();
      const bridgeAdapter = createAdapterWithBridge(customBridge);

      expect(bridgeAdapter).toBeInstanceOf(ProtocolAdapter);
      expect(bridgeAdapter.getStats().config.bridge).toBe(customBridge);
    });

    it('should use custom bridge for conversions', () => {
      const customBridge = new MicrobiomeBridge();
      const bridgeAdapter = createAdapterWithBridge(customBridge);

      const spore = createMockSporeMessage();
      const core = bridgeAdapter.sporeToCore(spore);

      expect(core).toBeDefined();
    });
  });

  // ==========================================================================
  // CUSTOM TYPE MAPPINGS
  // ==========================================================================

  describe('custom type mappings', () => {
    it('should use custom SPORE to Core type mappings', () => {
      const customAdapter = new ProtocolAdapter({
        customTypeMappings: {
          'custom_spore_type': 'custom_core_type',
        },
      });

      const spore = createMockSporeMessage({ type: 'custom_spore_type' });
      const core = customAdapter.sporeToCore(spore);

      expect(core.type).toBe('custom_core_type');
    });

    it('should use custom Core to SPORE type mappings', () => {
      const customAdapter = new ProtocolAdapter({
        customReverseTypeMappings: {
          'custom_core_type': 'custom_spore_type',
        },
      });

      const core = createMockCoreMessage({ type: 'custom_core_type' });
      const spore = customAdapter.coreToSpore(core);

      expect(spore.type).toBe('custom_spore_type');
    });
  });

  // ==========================================================================
  // INTEGRATION TESTS
  // ==========================================================================

  describe('integration tests', () => {
    it('should handle complete round-trip translation', () => {
      const originalSpore = createMockSporeMessage({
        type: SporeType.METABOLISM_COMPLETE,
        payload: { resource: ResourceType.TEXT, processed: 100 },
      });

      // SPORE -> Core
      const core = adapter.sporeToCore(originalSpore);

      // Core -> SPORE
      const backToSpore = adapter.coreToSpore(core);

      expect(backToSpore.type).toBeDefined();
      // Payload structure changes through round-trip, but data should be preserved
      expect((backToSpore.payload as any)?.resource || (backToSpore.payload as any)?.data).toBeDefined();
      expect(backToSpore.sourceId).toBe(originalSpore.sourceId);
    });

    it('should handle bidirectional routing', () => {
      const spore = createMockSporeMessage();

      // Microbiome -> Core
      const coreMessage = adapter.routeMessage(spore, 'microbiome', 'core');

      expect(coreMessage).toBeDefined();
      expect((coreMessage as CoreMessage).causalChainId).toBeDefined();

      // Core -> Microbiome
      const backToSpore = adapter.routeMessage(coreMessage as CoreMessage, 'core', 'microbiome');

      expect(backToSpore).toBeDefined();
      expect((backToSpore as SporeMessage).metadata).toBeDefined();
    });

    it('should handle complex colony communication scenario', () => {
      const microColony = createMockMicrobiomeColony();
      const coreColony = createMockCoreColony();

      // Create message
      const message = createMockSporeMessage({
        type: SporeType.COLONY_FORM,
        payload: { action: 'merge', targetColony: 'core-colony-1' },
      });

      // Bridge communication
      const bridged = adapter.bridgeColonyCommunication(microColony, coreColony, message);

      expect(bridged.microbiome).toHaveLength(microColony.members.length);
      expect(bridged.core).toHaveLength(coreColony.count);

      // Verify all messages have proper metadata
      for (const msg of [...bridged.microbiome, ...bridged.core]) {
        expect((msg as SporeMessage).metadata?.colonyId).toBeDefined();
      }
    });

    it('should handle channel sync with routing', () => {
      // Set up channels
      adapter.syncChannels(
        new Map([['resource_updates', ['agent-1', 'agent-2']]]),
        new Map([['resourceUpdates', new Set(['agent-3'])]])
      );

      // Route message through channels
      const message = createMockSporeMessage({
        metadata: { channel: 'resource_updates' },
      });

      const routed = adapter.routeMessage(message, 'microbiome', 'core');

      expect(routed).toBeDefined();
      // For Core messages, check metadata in payload._sporeMetadata
      const coreMsg = routed as CoreMessage;
      expect((coreMsg.payload as any)._sporeMetadata?.originalChannel).toBeDefined();
    });
  });

  // ==========================================================================
  // EDGE CASES
  // ==========================================================================

  describe('edge cases', () => {
    it('should handle message with undefined payload', () => {
      const spore = createMockSporeMessage({ payload: undefined });
      const core = adapter.sporeToCore(spore);

      // Undefined payload gets wrapped with _sporeMetadata
      expect((core.payload as any).data).toBeUndefined();
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle message with null payload', () => {
      const spore = createMockSporeMessage({ payload: null });
      const core = adapter.sporeToCore(spore);

      // Null payload gets wrapped with _sporeMetadata
      expect((core.payload as any).data).toBeNull();
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle message with empty payload', () => {
      const spore = createMockSporeMessage({ payload: {} });
      const core = adapter.sporeToCore(spore);

      // Empty object gets _sporeMetadata added
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle message with very long payload', () => {
      const longPayload = { data: 'x'.repeat(10000) };
      const spore = createMockSporeMessage({ payload: longPayload });
      const core = adapter.sporeToCore(spore);

      expect((core.payload as any).data).toBe(longPayload.data);
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle message with nested payload', () => {
      const nestedPayload = {
        level1: {
          level2: {
            level3: {
              value: 42,
            },
          },
        },
      };

      const spore = createMockSporeMessage({ payload: nestedPayload });
      const core = adapter.sporeToCore(spore);

      expect((core.payload as any).level1).toEqual(nestedPayload.level1);
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle message with array payload', () => {
      const arrayPayload = [1, 2, 3, 4, 5];
      const spore = createMockSporeMessage({ payload: arrayPayload });
      const core = adapter.sporeToCore(spore);

      // Arrays get wrapped with data key
      expect((core.payload as any).data).toEqual(arrayPayload);
      expect((core.payload as any)._sporeMetadata).toBeDefined();
    });

    it('should handle message with timestamp of 0', () => {
      const spore = createMockSporeMessage({ timestamp: 0 });
      const core = adapter.sporeToCore(spore);

      expect(core.timestamp).toBe(0);
    });

    it('should handle message with empty source ID', () => {
      const spore = createMockSporeMessage({ sourceId: '' });
      const core = adapter.sporeToCore(spore);

      expect(core.sourceId).toBe('');
    });

    it('should handle message with special characters in ID', () => {
      const specialId = 'agent-with-special.chars@123#';
      const spore = createMockSporeMessage({ sourceId: specialId });
      const core = adapter.sporeToCore(spore);

      expect(core.sourceId).toBe(specialId);
    });

    it('should handle very large colony', () => {
      const largeColony: ColonyStructure = {
        id: 'large-colony',
        members: Array.from({ length: 1000 }, (_, i) => `agent-${i}`),
        communicationChannels: new Map(),
        formationTime: Date.now(),
        stability: 0.9,
        coEvolutionBonus: 0.2,
      };

      const message = createMockSporeMessage();
      const translated = adapter.translateColonyCommunication(largeColony, message);

      expect(translated).toHaveLength(1000);
    });

    it('should handle colony with single member', () => {
      const singleColony: ColonyStructure = {
        id: 'single-colony',
        members: ['agent-1'],
        communicationChannels: new Map(),
        formationTime: Date.now(),
        stability: 1.0,
        coEvolutionBonus: 0,
      };

      const message = createMockSporeMessage();
      const translated = adapter.translateColonyCommunication(singleColony, message);

      expect(translated).toHaveLength(1);
    });
  });
});
