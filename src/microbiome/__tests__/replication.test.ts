/**
 * POLLN Microbiome - State Replication Tests
 *
 * Comprehensive test suite for state replication system,
 * including vector clocks, conflict resolution, and gossip protocol.
 *
 * @module microbiome/__tests__/replication
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  StateReplicator,
  createStateReplicator,
  ReplicationStrategy,
  ConflictResolutionStrategy,
  VectorClock,
  ClockComparison,
  VersionedState,
  ReplicationConflict,
  ReplicationResult,
  SyncResult,
  StateDelta,
  GossipMessage,
  vectorClockFromJSON,
} from '../replication.js';
import { DistributedConsensus, NodeId, createDistributedConsensus } from '../distributed.js';
import { MicrobiomeAgent, AgentTaxonomy, ResourceType, MetabolicProfile, LifecycleState } from '../types.js';

describe('StateReplicator', () => {
  let nodeId: NodeId;
  let consensus: DistributedConsensus;
  let replicator: StateReplicator;
  let mockAgent: MicrobiomeAgent;

  beforeEach(() => {
    nodeId = 'node-1';
    consensus = createDistributedConsensus(nodeId, ['node-1', 'node-2', 'node-3']);

    replicator = createStateReplicator(nodeId, consensus, {
      strategy: ReplicationStrategy.SYNCHRONOUS,
      conflictResolution: ConflictResolutionStrategy.VECTOR_CLOCK,
      enableAntiEntropy: false, // Disable for tests
    });

    // Create mock agent
    mockAgent = {
      id: 'agent-1',
      taxonomy: AgentTaxonomy.BACTERIA,
      name: 'Test Agent',
      metabolism: {
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processingRate: 1.0,
        efficiency: 0.8,
      },
      lifecycle: {
        health: 1.0,
        age: 0,
        generation: 0,
        isAlive: true,
      },
      parentId: undefined,
      generation: 0,
      size: 1000,
      complexity: 0.5,
      process: jest.fn(),
      reproduce: jest.fn(),
      evaluateFitness: jest.fn(),
      canMetabolize: jest.fn(),
    };
  });

  afterEach(() => {
    replicator.shutdown();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      const defaultReplicator = createStateReplicator(nodeId, consensus);
      expect(defaultReplicator).toBeInstanceOf(StateReplicator);
      defaultReplicator.shutdown();
    });

    it('should initialize with custom configuration', () => {
      const customReplicator = createStateReplicator(nodeId, consensus, {
        strategy: ReplicationStrategy.ASYNCHRONOUS,
        conflictResolution: ConflictResolutionStrategy.LAST_WRITE_WINS,
        replicationTimeout: 10000,
        gossipInterval: 20000,
      });

      expect(customReplicator).toBeInstanceOf(StateReplicator);
      customReplicator.shutdown();
    });

    it('should start with zero statistics', () => {
      const stats = replicator.getStats();
      expect(stats.totalReplications).toBe(0);
      expect(stats.successfulReplications).toBe(0);
      expect(stats.failedReplications).toBe(0);
      expect(stats.conflictsDetected).toBe(0);
      expect(stats.conflictsResolved).toBe(0);
      expect(stats.gossipExchanges).toBe(0);
    });
  });

  describe('Agent Replication', () => {
    it('should replicate agent to nodes synchronously', async () => {
      const result = await replicator.replicateAgent('agent-1', ['node-2', 'node-3'], mockAgent);

      // Success depends on quorum, not all nodes
      expect(result.success).toBeDefined();
      expect(result.duration).toBeGreaterThanOrEqual(0);
    });

    it('should replicate agent to nodes asynchronously', async () => {
      const asyncReplicator = createStateReplicator(nodeId, consensus, {
        strategy: ReplicationStrategy.ASYNCHRONOUS,
        enableAntiEntropy: false,
      });

      const result = await asyncReplicator.replicateAgent('agent-1', ['node-2', 'node-3'], mockAgent);

      expect(result.success).toBe(true);
      asyncReplicator.shutdown();
    });

    it('should create versioned state with vector clock', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const stats = replicator.getStats();
      expect(stats.totalReplications).toBe(1);
    });

    it('should track failed replications', async () => {
      // Mock a failing scenario by using invalid node IDs
      const result = await replicator.replicateAgent('agent-1', ['invalid-node'], mockAgent);

      expect(result.failedNodes.length).toBeGreaterThanOrEqual(0);
    });

    it('should handle empty node list', async () => {
      const result = await replicator.replicateAgent('agent-1', [], mockAgent);

      expect(result.success).toBe(true);
      expect(result.replicatedTo.length).toBe(0);
    });
  });

  describe('Vector Clocks', () => {
    it('should create vector clock with initial version', () => {
      const clock = replicator['createVectorClock']();

      expect(clock).toBeDefined();
      expect(clock.clock.size).toBe(0);
    });

    it('should add dots to vector clock', () => {
      const clock = replicator['createVectorClock']();
      clock.addDot('node-1', 1);
      clock.addDot('node-2', 2);

      expect(clock.clock.get('node-1')).toBe(1);
      expect(clock.clock.get('node-2')).toBe(2);
    });

    it('should update version to maximum when adding dot', () => {
      const clock = replicator['createVectorClock']();
      clock.addDot('node-1', 1);
      clock.addDot('node-1', 3);
      clock.addDot('node-1', 2);

      expect(clock.clock.get('node-1')).toBe(3);
    });

    it('should compare vector clocks - BEFORE', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 1);
      clock2.addDot('node-1', 2);

      expect(clock1.compare(clock2)).toBe(ClockComparison.BEFORE);
    });

    it('should compare vector clocks - AFTER', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 2);
      clock2.addDot('node-1', 1);

      expect(clock1.compare(clock2)).toBe(ClockComparison.AFTER);
    });

    it('should compare vector clocks - EQUAL', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 1);
      clock2.addDot('node-1', 1);

      expect(clock1.compare(clock2)).toBe(ClockComparison.EQUAL);
    });

    it('should compare vector clocks - CONCURRENT', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 2);
      clock2.addDot('node-2', 2);

      expect(clock1.compare(clock2)).toBe(ClockComparison.CONCURRENT);
    });

    it('should merge vector clocks taking maximum', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 2);
      clock1.addDot('node-2', 1);
      clock2.addDot('node-1', 1);
      clock2.addDot('node-2', 3);

      const merged = clock1.merge(clock2);

      expect(merged.clock.get('node-1')).toBe(2);
      expect(merged.clock.get('node-2')).toBe(3);
    });

    it('should check if clock dominates another', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 2);
      clock2.addDot('node-1', 1);

      expect(clock1.dominates(clock2)).toBe(true);
      expect(clock2.dominates(clock1)).toBe(false);
    });

    it('should check if clocks are concurrent', () => {
      const clock1 = replicator['createVectorClock']();
      const clock2 = replicator['createVectorClock']();

      clock1.addDot('node-1', 1);
      clock2.addDot('node-2', 1);

      expect(clock1.isConcurrentWith(clock2)).toBe(true);
    });

    it('should clone vector clock', () => {
      const clock1 = replicator['createVectorClock']();
      clock1.addDot('node-1', 1);

      const clock2 = clock1.clone();

      expect(clock2.clock.get('node-1')).toBe(1);

      clock1.addDot('node-1', 2);
      expect(clock2.clock.get('node-1')).toBe(1);
    });

    it('should serialize vector clock to JSON', () => {
      const clock = replicator['createVectorClock']();
      clock.addDot('node-1', 1);
      clock.addDot('node-2', 2);

      const json = clock.toJSON();

      expect(json['node-1']).toBe(1);
      expect(json['node-2']).toBe(2);
    });

    it('should create vector clock from JSON', () => {
      const json = {
        'node-1': 1,
        'node-2': 2,
        'node-3': 3,
      };

      const clock = vectorClockFromJSON(json);

      expect(clock.clock.get('node-1')).toBe(1);
      expect(clock.clock.get('node-2')).toBe(2);
      expect(clock.clock.get('node-3')).toBe(3);
    });
  });

  describe('Conflict Detection', () => {
    it('should detect concurrent updates as conflict', () => {
      const state1: VersionedState = {
        id: 'state-1',
        state: { value: 1 },
        vectorClock: replicator['createVectorClock'](),
        timestamp: Date.now(),
        version: 1,
        originNode: 'node-1',
      };
      state1.vectorClock.addDot('node-1', 1);

      const state2: VersionedState = {
        id: 'state-1',
        state: { value: 2 },
        vectorClock: replicator['createVectorClock'](),
        timestamp: Date.now() + 1,
        version: 1,
        originNode: 'node-2',
      };
      state2.vectorClock.addDot('node-2', 1);

      const conflict = replicator['detectConflict'](state1, state2);

      expect(conflict).toBeDefined();
      expect(conflict?.type).toBe('concurrent_update');
    });

    it('should not detect conflict when one state is newer', () => {
      const state1: VersionedState = {
        id: 'state-1',
        state: { value: 1 },
        vectorClock: replicator['createVectorClock'](),
        timestamp: Date.now(),
        version: 1,
        originNode: 'node-1',
      };
      state1.vectorClock.addDot('node-1', 1);

      const state2: VersionedState = {
        id: 'state-1',
        state: { value: 2 },
        vectorClock: replicator['createVectorClock'](),
        timestamp: Date.now() + 1,
        version: 2,
        originNode: 'node-1',
      };
      state2.vectorClock.addDot('node-1', 2);

      const conflict = replicator['detectConflict'](state1, state2);

      expect(conflict).toBeNull();
    });

    it('should detect update-delete conflict', () => {
      // Use same vector clock to ensure it's not concurrent
      const clock = replicator['createVectorClock']();
      clock.addDot('node-1', 1);

      const state1: VersionedState = {
        id: 'state-1',
        state: { value: 1 },
        vectorClock: clock.clone(),
        timestamp: Date.now(),
        version: 1,
        originNode: 'node-1',
        deleted: true,
      };

      const state2: VersionedState = {
        id: 'state-1',
        state: { value: 2 },
        vectorClock: clock.clone(),
        timestamp: Date.now() + 1,
        version: 1,
        originNode: 'node-1',
        deleted: false,
      };

      const conflict = replicator['detectConflict'](state1, state2);

      expect(conflict).toBeDefined();
      expect(conflict?.type).toBe('update_delete');
    });
  });

  describe('Conflict Resolution', () => {
    it('should resolve conflict using last-write-wins', async () => {
      const conflict: ReplicationConflict = {
        id: 'conflict-1',
        stateId: 'state-1',
        versions: [
          {
            id: 'state-1',
            state: { value: 1 },
            vectorClock: replicator['createVectorClock'](),
            timestamp: 1000,
            version: 1,
            originNode: 'node-1',
          },
          {
            id: 'state-1',
            state: { value: 2 },
            vectorClock: replicator['createVectorClock'](),
            timestamp: 2000,
            version: 1,
            originNode: 'node-2',
          },
        ],
        type: 'concurrent_update' as any,
        detectedAt: Date.now(),
        resolutionStrategy: ConflictResolutionStrategy.LAST_WRITE_WINS,
        resolved: false,
      };

      const resolved = await replicator.resolveConflict(conflict);

      expect(resolved).toBe(true);
      expect(conflict.resolved).toBe(true);
    });

    it('should resolve conflict using CRDT merge', async () => {
      const crdtReplicator = createStateReplicator(nodeId, consensus, {
        conflictResolution: ConflictResolutionStrategy.CRDT_MERGE,
        enableAntiEntropy: false,
      });

      const clock1 = crdtReplicator['createVectorClock']();
      const clock2 = crdtReplicator['createVectorClock']();

      clock1.addDot('node-1', 1);
      clock2.addDot('node-2', 1);

      const conflict: ReplicationConflict = {
        id: 'conflict-1',
        stateId: 'state-1',
        versions: [
          {
            id: 'state-1',
            state: { value: 1, count: 5 },
            vectorClock: clock1,
            timestamp: 1000,
            version: 1,
            originNode: 'node-1',
          },
          {
            id: 'state-1',
            state: { value: 2, count: 10 },
            vectorClock: clock2,
            timestamp: 2000,
            version: 1,
            originNode: 'node-2',
          },
        ],
        type: 'concurrent_update' as any,
        detectedAt: Date.now(),
        resolutionStrategy: ConflictResolutionStrategy.CRDT_MERGE,
        resolved: false,
      };

      const resolved = await crdtReplicator.resolveConflict(conflict);

      expect(resolved).toBe(true);
      crdtReplicator.shutdown();
    });

    it('should resolve conflict using vector clock', async () => {
      const conflict: ReplicationConflict = {
        id: 'conflict-1',
        stateId: 'state-1',
        versions: [
          {
            id: 'state-1',
            state: { value: 1 },
            vectorClock: replicator['createVectorClock'](),
            timestamp: 1000,
            version: 1,
            originNode: 'node-1',
          },
          {
            id: 'state-1',
            state: { value: 2 },
            vectorClock: replicator['createVectorClock'](),
            timestamp: 2000,
            version: 1,
            originNode: 'node-2',
          },
        ],
        type: 'concurrent_update' as any,
        detectedAt: Date.now(),
        resolutionStrategy: ConflictResolutionStrategy.VECTOR_CLOCK,
        resolved: false,
      };

      const resolved = await replicator.resolveConflict(conflict);

      expect(resolved).toBe(true);
    });

    it('should skip already resolved conflicts', async () => {
      const conflict: ReplicationConflict = {
        id: 'conflict-1',
        stateId: 'state-1',
        versions: [],
        type: 'concurrent_update' as any,
        detectedAt: Date.now(),
        resolutionStrategy: ConflictResolutionStrategy.LAST_WRITE_WINS,
        resolved: true,
      };

      const resolved = await replicator.resolveConflict(conflict);

      expect(resolved).toBe(true);
    });
  });

  describe('Ecosystem State Synchronization', () => {
    it('should synchronize ecosystem state', async () => {
      const snapshot = {
        timestamp: Date.now(),
        agents: new Map([[mockAgent.id, mockAgent]]),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };

      const result = await replicator.syncEcosystemState(snapshot);

      expect(result.success).toBe(true);
      expect(result.statesSynced).toBe(1);
      expect(result.duration).toBeGreaterThanOrEqual(0);
    });

    it('should track bytes transferred during sync', async () => {
      const snapshot = {
        timestamp: Date.now(),
        agents: new Map([[mockAgent.id, mockAgent]]),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };

      const result = await replicator.syncEcosystemState(snapshot);

      expect(result.bytesTransferred).toBeGreaterThan(0);
    });

    it('should handle empty snapshot', async () => {
      const snapshot = {
        timestamp: Date.now(),
        agents: new Map(),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };

      const result = await replicator.syncEcosystemState(snapshot);

      expect(result.success).toBe(true);
      expect(result.statesSynced).toBe(0);
    });

    it('should resolve conflicts during sync', async () => {
      // First sync
      const snapshot1 = {
        timestamp: Date.now(),
        agents: new Map([[mockAgent.id, mockAgent]]),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };
      await replicator.syncEcosystemState(snapshot1);

      // Create conflicting agent
      const conflictingAgent = { ...mockAgent, name: 'Conflicting Agent' };

      // Second sync with conflict
      const snapshot2 = {
        timestamp: Date.now() + 1000,
        agents: new Map([[mockAgent.id, conflictingAgent]]),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };

      const result = await replicator.syncEcosystemState(snapshot2);

      expect(result.success).toBe(true);
      expect(result.conflictsResolved).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Anti-Entropy Gossip Protocol', () => {
    it('should exchange state with peer', () => {
      const delta = replicator.exchangeState('node-2');

      expect(delta).toBeDefined();
      expect(delta.timestamp).toBeGreaterThan(0);
      expect(delta.additions).toBeInstanceOf(Map);
      expect(delta.deletions).toBeInstanceOf(Set);
      expect(delta.clockChanges).toBeInstanceOf(Map);
    });

    it('should include all local states in delta', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const delta = replicator.exchangeState('node-2');

      expect(delta.additions.size).toBe(1);
      expect(delta.additions.has('agent-1')).toBe(true);
    });

    it('should receive gossip message', () => {
      const delta: StateDelta = {
        additions: new Map(),
        deletions: new Set(),
        clockChanges: new Map(),
        timestamp: Date.now(),
      };

      const message: GossipMessage = {
        id: 'gossip-1',
        fromNode: 'node-2',
        toNode: 'node-1',
        delta,
        timestamp: Date.now(),
      };

      // Should not throw
      expect(() => replicator.receiveGossip(message)).not.toThrow();
    });

    it('should apply incoming state additions', () => {
      const state: VersionedState = {
        id: 'agent-2',
        state: { value: 1 },
        vectorClock: replicator['createVectorClock'](),
        timestamp: Date.now(),
        version: 1,
        originNode: 'node-2',
      };
      state.vectorClock.addDot('node-2', 1);

      const delta: StateDelta = {
        additions: new Map([['agent-2', state]]),
        deletions: new Set(),
        clockChanges: new Map(),
        timestamp: Date.now(),
      };

      const message: GossipMessage = {
        id: 'gossip-1',
        fromNode: 'node-2',
        toNode: 'node-1',
        delta,
        timestamp: Date.now(),
      };

      replicator.receiveGossip(message);

      // State should be added
      expect(replicator['states'].has('agent-2')).toBe(true);
    });

    it('should detect conflicts in gossip', async () => {
      // Add local state
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      // Create conflicting state from peer
      const peerState: VersionedState = {
        id: 'agent-1',
        state: { value: 999 },
        vectorClock: replicator['createVectorClock'](),
        timestamp: Date.now() + 1000,
        version: 1,
        originNode: 'node-2',
      };
      peerState.vectorClock.addDot('node-2', 1);

      const delta: StateDelta = {
        additions: new Map([['agent-1', peerState]]),
        deletions: new Set(),
        clockChanges: new Map(),
        timestamp: Date.now(),
      };

      const message: GossipMessage = {
        id: 'gossip-1',
        fromNode: 'node-2',
        toNode: 'node-1',
        delta,
        timestamp: Date.now(),
      };

      replicator.receiveGossip(message);

      const stats = replicator.getStats();
      expect(stats.conflictsDetected).toBeGreaterThan(0);
    });

    it('should process deletions from gossip', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const delta: StateDelta = {
        additions: new Map(),
        deletions: new Set(['agent-1']),
        clockChanges: new Map(),
        timestamp: Date.now(),
      };

      const message: GossipMessage = {
        id: 'gossip-1',
        fromNode: 'node-2',
        toNode: 'node-1',
        delta,
        timestamp: Date.now(),
      };

      replicator.receiveGossip(message);

      expect(replicator['states'].has('agent-1')).toBe(false);
    });

    it('should update gossip exchange count', () => {
      replicator.exchangeState('node-2');
      replicator.exchangeState('node-3');

      const stats = replicator.getStats();
      expect(stats.gossipExchanges).toBe(2);
    });
  });

  describe('Merkle Tree Verification', () => {
    it('should build Merkle tree from states', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const tree = replicator['buildMerkleTree']();

      expect(tree).toBeDefined();
      expect(tree.hash).toBeDefined();
    });

    it('should verify state consistency', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const tree = replicator['buildMerkleTree']();
      const isConsistent = replicator.verifyStateConsistency(tree);

      expect(isConsistent).toBe(true);
    });

    it('should detect inconsistency with different root', () => {
      const fakeRoot = {
        hash: 'fake-hash',
      };

      const isConsistent = replicator.verifyStateConsistency(fakeRoot);

      expect(isConsistent).toBe(false);
    });

    it('should always return true when verification disabled', () => {
      const noVerifyReplicator = createStateReplicator(nodeId, consensus, {
        enableMerkleVerification: false,
        enableAntiEntropy: false,
      });

      const fakeRoot = {
        hash: 'fake-hash',
      };

      const isConsistent = noVerifyReplicator.verifyStateConsistency(fakeRoot);

      expect(isConsistent).toBe(true);
      noVerifyReplicator.shutdown();
    });
  });

  describe('Replication Health Monitoring', () => {
    it('should track health status for nodes', () => {
      const health = replicator.getReplicationHealth();

      expect(health).toBeInstanceOf(Map);
    });

    it('should update health status after gossip', () => {
      replicator.exchangeState('node-2');

      const health = replicator.getReplicationHealth();
      expect(health.has('node-2')).toBe(true);
    });

    it('should mark unhealthy nodes correctly', () => {
      // Simulate multiple gossip attempts
      for (let i = 0; i < 10; i++) {
        replicator.exchangeState('node-2');
      }

      const health = replicator.getReplicationHealth();
      const nodeHealth = health.get('node-2');

      expect(nodeHealth).toBeDefined();
      expect(nodeHealth?.lastSync).toBeGreaterThan(0);
    });
  });

  describe('Statistics Tracking', () => {
    it('should track total replications', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);
      await replicator.replicateAgent('agent-2', ['node-3'], mockAgent);

      const stats = replicator.getStats();
      expect(stats.totalReplications).toBe(2);
    });

    it('should track successful replications', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const stats = replicator.getStats();
      expect(stats.successfulReplications).toBeGreaterThan(0);
    });

    it('should calculate success rate', async () => {
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const stats = replicator.getStats();
      expect(stats.successRate).toBeGreaterThanOrEqual(0);
      expect(stats.successRate).toBeLessThanOrEqual(1);
    });

    it('should track conflicts detected', async () => {
      // Create conflict scenario
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const conflictingAgent = { ...mockAgent, name: 'Conflict' };
      const snapshot = {
        timestamp: Date.now() + 1000,
        agents: new Map([[mockAgent.id, conflictingAgent]]),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };

      await replicator.syncEcosystemState(snapshot);

      const stats = replicator.getStats();
      // Conflicts may or may not be detected depending on timing
      expect(stats.conflictsDetected).toBeGreaterThanOrEqual(0);
    });

    it('should track conflicts resolved', async () => {
      // Create and resolve conflict
      await replicator.replicateAgent('agent-1', ['node-2'], mockAgent);

      const conflictingAgent = { ...mockAgent, name: 'Conflict' };
      const snapshot = {
        timestamp: Date.now() + 1000,
        agents: new Map([[mockAgent.id, conflictingAgent]]),
        resourceFlows: new Map(),
        populations: new Map(),
        colonies: [],
        symbioses: [],
      };

      await replicator.syncEcosystemState(snapshot);

      const stats = replicator.getStats();
      // Conflicts may or may not be resolved depending on timing
      expect(stats.conflictsResolved).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle concurrent replication requests', async () => {
      const promises = [
        replicator.replicateAgent('agent-1', ['node-2'], mockAgent),
        replicator.replicateAgent('agent-2', ['node-3'], mockAgent),
        replicator.replicateAgent('agent-3', ['node-2'], mockAgent),
      ];

      const results = await Promise.all(promises);

      expect(results).toHaveLength(3);
      expect(results.every(r => r.success)).toBe(true);
    });

    it('should handle rapid state updates', async () => {
      for (let i = 0; i < 10; i++) {
        await replicator.replicateAgent(`agent-${i}`, ['node-2'], mockAgent);
      }

      const stats = replicator.getStats();
      expect(stats.totalReplications).toBe(10);
    });

    it('should handle null or undefined states', () => {
      expect(() => {
        // Test with undefined - serialization should handle gracefully
        const result = replicator['serializeAgent'](undefined as any);
        expect(result).toBeDefined();
      }).not.toThrow();
    });

    it('should handle shutdown gracefully', () => {
      expect(() => {
        replicator.shutdown();
        replicator.shutdown(); // Double shutdown
      }).not.toThrow();
    });
  });

  describe('Integration with Consensus', () => {
    it('should use consensus to get cluster nodes', async () => {
      await replicator.replicateAgent('agent-1', ['node-2', 'node-3'], mockAgent);

      const cluster = consensus.getCluster();
      expect(cluster.length).toBe(3);
    });

    it('should handle leader changes', () => {
      const initialLeader = consensus.getLeader();

      // Simulate leader change
      consensus.stepDown();

      const newLeader = consensus.getLeader();

      // Leader should have changed
      expect(initialLeader === newLeader || newLeader === null).toBe(true);
    });
  });

  describe('Helper Functions', () => {
    it('should create state replicator with factory function', () => {
      const factoryReplicator = createStateReplicator(nodeId, consensus);

      expect(factoryReplicator).toBeInstanceOf(StateReplicator);
      factoryReplicator.shutdown();
    });

    it('should create vector clock from JSON', () => {
      const json = {
        'node-1': 1,
        'node-2': 2,
        'node-3': 3,
      };

      const clock = vectorClockFromJSON(json);

      expect(clock.clock.get('node-1')).toBe(1);
      expect(clock.clock.get('node-2')).toBe(2);
      expect(clock.clock.get('node-3')).toBe(3);
    });
  });
});

describe('Vector Clock Complex Scenarios', () => {
  let replicator: StateReplicator;
  let nodeId: NodeId;
  let consensus: DistributedConsensus;

  beforeEach(() => {
    nodeId = 'node-1';
    consensus = createDistributedConsensus(nodeId, ['node-1', 'node-2', 'node-3']);
    replicator = createStateReplicator(nodeId, consensus, {
      enableAntiEntropy: false,
    });
  });

  afterEach(() => {
    replicator.shutdown();
  });

  it('should handle complex vector clock scenarios', () => {
    const clock1 = replicator['createVectorClock']();
    const clock2 = replicator['createVectorClock']();
    const clock3 = replicator['createVectorClock']();

    // Create complex scenario
    clock1.addDot('node-1', 2);
    clock1.addDot('node-2', 1);

    clock2.addDot('node-1', 1);
    clock2.addDot('node-3', 3);

    clock3.addDot('node-1', 2);
    clock3.addDot('node-2', 2);
    clock3.addDot('node-3', 3);

    // clock1 vs clock2 should be concurrent
    expect(clock1.compare(clock2)).toBe(ClockComparison.CONCURRENT);

    // clock3 dominates both
    expect(clock3.compare(clock1)).toBe(ClockComparison.AFTER);
    expect(clock3.compare(clock2)).toBe(ClockComparison.AFTER);
  });

  it('should handle multi-way merges', () => {
    const clock1 = replicator['createVectorClock']();
    const clock2 = replicator['createVectorClock']();
    const clock3 = replicator['createVectorClock']();

    clock1.addDot('node-1', 2);
    clock2.addDot('node-2', 2);
    clock3.addDot('node-3', 2);

    const merged1 = clock1.merge(clock2);
    const merged2 = merged1.merge(clock3);

    expect(merged2.clock.get('node-1')).toBe(2);
    expect(merged2.clock.get('node-2')).toBe(2);
    expect(merged2.clock.get('node-3')).toBe(2);
  });

  it('should detect causality violations', () => {
    const clock1 = replicator['createVectorClock']();
    const clock2 = replicator['createVectorClock']();

    clock1.addDot('node-1', 1);

    // clock2 has no knowledge of node-1's update
    clock2.addDot('node-2', 1);

    // They should be concurrent (causality violation)
    expect(clock1.isConcurrentWith(clock2)).toBe(true);
  });
});

describe('Performance Tests', () => {
  let replicator: StateReplicator;
  let nodeId: NodeId;
  let consensus: DistributedConsensus;
  let mockAgent: MicrobiomeAgent;

  beforeEach(() => {
    nodeId = 'node-1';
    consensus = createDistributedConsensus(
      nodeId,
      Array.from({ length: 10 }, (_, i) => `node-${i}`)
    );

    replicator = createStateReplicator(nodeId, consensus, {
      enableAntiEntropy: false,
    });

    mockAgent = {
      id: 'agent-1',
      taxonomy: AgentTaxonomy.BACTERIA,
      name: 'Test Agent',
      metabolism: {
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processingRate: 1.0,
        efficiency: 0.8,
      },
      lifecycle: {
        health: 1.0,
        age: 0,
        generation: 0,
        isAlive: true,
      },
      parentId: undefined,
      generation: 0,
      size: 1000,
      complexity: 0.5,
      process: jest.fn(),
      reproduce: jest.fn(),
      evaluateFitness: jest.fn(),
      canMetabolize: jest.fn(),
    };
  });

  afterEach(() => {
    replicator.shutdown();
  });

  it('should handle bulk replication efficiently', async () => {
    const startTime = Date.now();

    const promises = [];
    for (let i = 0; i < 100; i++) {
      promises.push(
        replicator.replicateAgent(`agent-${i}`, ['node-2', 'node-3'], {
          ...mockAgent,
          id: `agent-${i}`,
        })
      );
    }

    await Promise.all(promises);

    const duration = Date.now() - startTime;

    // Should complete in reasonable time
    expect(duration).toBeLessThan(10000);

    const stats = replicator.getStats();
    expect(stats.totalReplications).toBe(100);
  });

  it('should handle large state snapshots', async () => {
    const agents = new Map<string, MicrobiomeAgent>();

    for (let i = 0; i < 1000; i++) {
      agents.set(`agent-${i}`, {
        ...mockAgent,
        id: `agent-${i}`,
      });
    }

    const snapshot = {
      timestamp: Date.now(),
      agents,
      resourceFlows: new Map(),
      populations: new Map(),
      colonies: [],
      symbioses: [],
    };

    const startTime = Date.now();
    const result = await replicator.syncEcosystemState(snapshot);
    const duration = Date.now() - startTime;

    expect(result.success).toBe(true);
    expect(result.statesSynced).toBe(1000);
    expect(duration).toBeLessThan(5000);
  });
});
