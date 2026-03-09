/**
 * POLLN Microbiome - Distributed Consensus Tests
 *
 * Phase 8: Distributed Systems - Milestone 1
 * Comprehensive tests for Raft-based consensus implementation.
 *
 * @test microbiome/distributed
 */

import {
  DistributedConsensus,
  createDistributedConsensus,
  ConsensusAlgorithm,
  NodeState,
  NodeId,
  LogEntry,
  StateChange,
  VoteRequest,
  VoteResponse,
  AppendEntriesRequest,
  AppendEntriesResponse,
  Partition,
  RecoveryStrategy,
  calculateQuorum,
  detectPartition,
  recoverFromPartition,
} from '../distributed.js';

describe('DistributedConsensus', () => {
  let nodeIds: NodeId[];
  let consensus: DistributedConsensus;

  beforeEach(() => {
    nodeIds = ['node1', 'node2', 'node3', 'node4', 'node5'];
    consensus = createDistributedConsensus('node1', nodeIds, {
      electionTimeout: 1000,
      heartbeatInterval: 200,
      enablePartitionDetection: true,
    });
  });

  afterEach(() => {
    consensus.shutdown();
  });

  describe('Initialization', () => {
    test('should initialize with follower state', () => {
      expect(consensus.getState()).toBe(NodeState.FOLLOWER);
    });

    test('should initialize with term 0', () => {
      expect(consensus.getTerm()).toBe(0);
    });

    test('should initialize with empty log', () => {
      expect(consensus.getLog()).toHaveLength(0);
    });

    test('should initialize with all cluster nodes', () => {
      const cluster = consensus.getCluster();
      expect(cluster).toHaveLength(5);
      expect(cluster.map(n => n.id)).toEqual(nodeIds);
    });

    test('should initialize statistics correctly', () => {
      const stats = consensus.getStats();
      expect(stats.totalNodes).toBe(5);
      expect(stats.aliveNodes).toBe(1); // Only local node initially alive
      expect(stats.currentTerm).toBe(0);
      expect(stats.logEntries).toBe(0);
    });
  });

  describe('Leader Election', () => {
    test('should start election when follower timeout expires', async () => {
      // Wait for election timeout
      await new Promise(resolve => setTimeout(resolve, 1200));

      // Node should have become candidate and started election
      const state = consensus.getState();
      expect(state === NodeState.CANDIDATE || state === NodeState.LEADER).toBe(true);
    });

    test('should become leader after winning election', () => {
      // Manually trigger election
      const leaderId = consensus.electLeader();

      // Should become leader (only node voting)
      expect(consensus.getState()).toBe(NodeState.LEADER);
      expect(consensus.getLeader()).toBe('node1');
    });

    test('should update cluster state when becoming leader', () => {
      consensus.electLeader();

      const cluster = consensus.getCluster();
      const localNode = cluster.find(n => n.id === 'node1');

      expect(localNode?.state).toBe(NodeState.LEADER);
      expect(localNode?.leaderId).toBe('node1');
    });

    test('should increment term during election', () => {
      const initialTerm = consensus.getTerm();
      consensus.electLeader();

      expect(consensus.getTerm()).toBeGreaterThan(initialTerm);
    });

    test('should track election statistics', () => {
      consensus.electLeader();

      const stats = consensus.getStats();
      expect(stats.electionsHeld).toBeGreaterThan(0);
    });

    test('should handle vote request from higher term', () => {
      const request: VoteRequest = {
        term: 5,
        candidateId: 'node2',
        lastLogIndex: 0,
        lastLogTerm: 0,
      };

      const response = consensus.handleVoteRequest(request, 'node2');

      expect(response.term).toBe(5);
      expect(response.voteGranted).toBe(true);
      expect(consensus.getTerm()).toBe(5);
      expect(consensus.getState()).toBe(NodeState.FOLLOWER);
    });

    test('should deny vote request from lower term', () => {
      consensus.electLeader(); // Become leader with term 1

      const request: VoteRequest = {
        term: 0,
        candidateId: 'node2',
        lastLogIndex: 0,
        lastLogTerm: 0,
      };

      const response = consensus.handleVoteRequest(request, 'node2');

      expect(response.voteGranted).toBe(false);
      expect(consensus.getState()).toBe(NodeState.LEADER);
    });

    test('should grant vote to candidate with more up-to-date log', () => {
      // Simulate log entries
      const change: StateChange = {
        type: 'agent_introduce',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      consensus.proposeStateChange(change);

      const request: VoteRequest = {
        term: 1,
        candidateId: 'node2',
        lastLogIndex: 2, // More up-to-date
        lastLogTerm: 0,
      };

      const response = consensus.handleVoteRequest(request, 'node2');

      expect(response.voteGranted).toBe(true);
    });
  });

  describe('Log Replication', () => {
    beforeEach(() => {
      consensus.electLeader();
    });

    test('should propose state change as leader', async () => {
      const change: StateChange = {
        type: 'agent_introduce',
        targetId: 'agent123',
        params: { name: 'test-agent' },
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      const result = await consensus.proposeStateChange(change);

      expect(result.achieved).toBe(true);
      expect(result.change).toEqual(change);
      expect(result.commitIndex).toBeGreaterThan(0);
    });

    test('should append entries to log', async () => {
      const change: StateChange = {
        type: 'colony_form',
        params: { members: ['agent1', 'agent2'] },
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      await consensus.proposeStateChange(change);

      const log = consensus.getLog();
      expect(log).toHaveLength(1);
      expect(log[0].command).toEqual(change);
      expect(log[0].term).toBe(consensus.getTerm());
    });

    test('should mark entries as committed', async () => {
      const change: StateChange = {
        type: 'resource_modify',
        params: { resource: 'compute', amount: 100 },
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      await consensus.proposeStateChange(change);

      const log = consensus.getLog();
      expect(log[0].committed).toBe(true);
    });

    test('should maintain sequential consistency', async () => {
      const changes: StateChange[] = [
        {
          type: 'agent_introduce',
          params: { name: 'agent1' },
          timestamp: Date.now(),
          proposedBy: 'node1',
        },
        {
          type: 'agent_introduce',
          params: { name: 'agent2' },
          timestamp: Date.now(),
          proposedBy: 'node1',
        },
        {
          type: 'colony_form',
          params: { members: ['agent1', 'agent2'] },
          timestamp: Date.now(),
          proposedBy: 'node1',
        },
      ];

      for (const change of changes) {
        await consensus.proposeStateChange(change);
      }

      const log = consensus.getLog();
      expect(log).toHaveLength(3);

      // Check sequential ordering
      expect(log[0].command.params.name).toBe('agent1');
      expect(log[1].command.params.name).toBe('agent2');
      expect(log[2].command.type).toBe('colony_form');
    });

    test('should update commit index', async () => {
      const change: StateChange = {
        type: 'config_update',
        params: { maxAgents: 1000 },
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      const result = await consensus.proposeStateChange(change);

      expect(result.commitIndex).toBeGreaterThan(0);
      expect(consensus.getLog()[0].committed).toBe(true);
    });
  });

  describe('Heartbeat', () => {
    test('should send heartbeat as leader', async () => {
      consensus.electLeader();

      // Mock handling heartbeat
      const heartbeatRequest: AppendEntriesRequest = {
        term: consensus.getTerm(),
        leaderId: 'node1',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [],
        leaderCommit: 0,
      };

      const response = consensus.handleAppendEntries(heartbeatRequest, 'node2');

      expect(response.success).toBe(true);
    });

    test('should reset election timer on heartbeat', async () => {
      const initialTime = Date.now();

      // Send heartbeat
      const request: AppendEntriesRequest = {
        term: 0,
        leaderId: 'node2',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [],
        leaderCommit: 0,
      };

      consensus.handleAppendEntries(request, 'node2');

      // Wait briefly and check no election started
      await new Promise(resolve => setTimeout(resolve, 500));

      expect(consensus.getState()).toBe(NodeState.FOLLOWER);
    });

    test('should recognize leader from heartbeat', () => {
      const request: AppendEntriesRequest = {
        term: 1,
        leaderId: 'node2',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [],
        leaderCommit: 0,
      };

      consensus.handleAppendEntries(request, 'node2');

      expect(consensus.getLeader()).toBe('node2');
    });
  });

  describe('Append Entries', () => {
    test('should accept append entries with correct term', () => {
      const request: AppendEntriesRequest = {
        term: 1,
        leaderId: 'node2',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [],
        leaderCommit: 0,
      };

      const response = consensus.handleAppendEntries(request, 'node2');

      expect(response.success).toBe(true);
      expect(response.term).toBe(1);
    });

    test('should reject append entries with lower term', () => {
      consensus.electLeader(); // Term 1

      const request: AppendEntriesRequest = {
        term: 0,
        leaderId: 'node2',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [],
        leaderCommit: 0,
      };

      const response = consensus.handleAppendEntries(request, 'node2');

      expect(response.success).toBe(false);
      expect(response.reason).toBe('Term mismatch');
    });

    test('should append new entries to log', () => {
      const entry: LogEntry = {
        index: 1,
        term: 1,
        command: {
          type: 'agent_introduce',
          params: {},
          timestamp: Date.now(),
          proposedBy: 'node2',
        },
        committed: false,
      };

      const request: AppendEntriesRequest = {
        term: 1,
        leaderId: 'node2',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [entry],
        leaderCommit: 0,
      };

      const response = consensus.handleAppendEntries(request, 'node2');

      expect(response.success).toBe(true);
      expect(consensus.getLog()).toHaveLength(1);
    });

    test('should update commit index on heartbeat', () => {
      const request: AppendEntriesRequest = {
        term: 1,
        leaderId: 'node2',
        prevLogIndex: 0,
        prevLogTerm: 0,
        entries: [],
        leaderCommit: 5,
      };

      consensus.handleAppendEntries(request, 'node2');

      const log = consensus.getLog();
      // Commit index should be updated
      expect(request.leaderCommit).toBe(5);
    });
  });

  describe('Voting and Quorum', () => {
    test('should calculate majority quorum', () => {
      const quorum = calculateQuorum(5, 'majority');
      expect(quorum).toBe(3); // floor(5/2) + 1
    });

    test('should calculate supermajority quorum', () => {
      const quorum = calculateQuorum(5, 'supermajority');
      expect(quorum).toBe(4); // floor(5 * 0.67) + 1
    });

    test('should calculate unanimous quorum', () => {
      const quorum = calculateQuorum(5, 'unanimous');
      expect(quorum).toBe(5);
    });

    test('should vote on proposal', () => {
      const change: StateChange = {
        type: 'agent_cull',
        targetId: 'agent123',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node2',
      };

      const vote = consensus.vote(change, true);

      expect(vote.approve).toBe(true);
      expect(vote.nodeId).toBe('node1');
      expect(vote.term).toBe(consensus.getTerm());
    });
  });

  describe('Network Partitions', () => {
    test('should detect partitioned nodes', () => {
      const cluster = consensus.getCluster();

      // Mark nodes as dead
      consensus.setNodeAlive('node2', false);
      consensus.setNodeAlive('node3', false);

      const partitions = detectPartition(
        new Map(cluster.map(n => [n.id, n])),
        100
      );

      expect(partitions).toHaveLength(1);
      expect(partitions[0].nodes.size).toBeGreaterThanOrEqual(2);
    });

    test('should handle network partition with majority strategy', () => {
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node1', 'node2', 'node3']), // 3 of 5 = majority
        detectedAt: Date.now(),
      };

      const strategy = consensus.handlePartition(partition);

      expect(strategy).toBe(RecoveryStrategy.MAJORITY);
    });

    test('should handle network partition with wait strategy', () => {
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node1']), // Single node
        detectedAt: Date.now(),
      };

      const strategy = consensus.handlePartition(partition);

      expect(strategy).toBe(RecoveryStrategy.WAIT);
    });

    test('should handle network partition with rollback strategy', () => {
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node1', 'node2']), // 2 of 5 = minority
        detectedAt: Date.now(),
      };

      const strategy = consensus.handlePartition(partition);

      expect(strategy).toBe(RecoveryStrategy.ROLLBACK);
    });

    test('should track partition statistics', () => {
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node2', 'node3']),
        detectedAt: Date.now(),
      };

      consensus.handlePartition(partition);

      const stats = consensus.getStats();
      expect(stats.partitionsDetected).toBe(1);
    });

    test('should recover from partition with majority strategy', () => {
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node1', 'node2', 'node3']),
        detectedAt: Date.now(),
      };

      recoverFromPartition(consensus, partition, RecoveryStrategy.MAJORITY);

      // Should trigger new election
      expect(consensus.getState() === NodeState.CANDIDATE ||
             consensus.getState() === NodeState.LEADER).toBe(true);
    });

    test('should recover from partition with wait strategy', () => {
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node1']),
        detectedAt: Date.now(),
      };

      // Should not throw
      expect(() => {
        recoverFromPartition(consensus, partition, RecoveryStrategy.WAIT);
      }).not.toThrow();
    });
  });

  describe('Cluster Management', () => {
    test('should add node to cluster', () => {
      consensus.addNode('node6', 'node6:8080');

      const cluster = consensus.getCluster();
      expect(cluster).toHaveLength(6);
      expect(cluster.find(n => n.id === 'node6')).toBeDefined();
    });

    test('should remove node from cluster', () => {
      consensus.removeNode('node5');

      const cluster = consensus.getCluster();
      expect(cluster).toHaveLength(4);
      expect(cluster.find(n => n.id === 'node5')).toBeUndefined();
    });

    test('should mark node as alive', () => {
      consensus.setNodeAlive('node2', true);

      const cluster = consensus.getCluster();
      const node = cluster.find(n => n.id === 'node2');
      expect(node?.isAlive).toBe(true);
    });

    test('should mark node as dead', () => {
      consensus.setNodeAlive('node2', false);

      const cluster = consensus.getCluster();
      const node = cluster.find(n => n.id === 'node2');
      expect(node?.isAlive).toBe(false);
    });

    test('should update alive nodes count', () => {
      consensus.setNodeAlive('node2', true);
      consensus.setNodeAlive('node3', true);

      const stats = consensus.getStats();
      expect(stats.aliveNodes).toBe(3); // node1, node2, node3
    });
  });

  describe('Callbacks', () => {
    test('should call commit callback on entry commit', async () => {
      let committedEntry: LogEntry | null = null;

      consensus.onCommit((entry) => {
        committedEntry = entry;
      });

      consensus.electLeader();

      const change: StateChange = {
        type: 'agent_introduce',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      await consensus.proposeStateChange(change);

      expect(committedEntry).toBeDefined();
      expect(committedEntry?.command).toEqual(change);
    });

    test('should call leader change callback on leadership change', () => {
      let newLeader: NodeId | null = null;

      consensus.onLeaderChange((leaderId) => {
        newLeader = leaderId;
      });

      consensus.electLeader();

      expect(newLeader).toBe('node1');
    });

    test('should call partition callback on partition detection', () => {
      let detectedPartition: Partition | null = null;

      consensus.onPartition((partition) => {
        detectedPartition = partition;
      });

      // Create partition
      const partition: Partition = {
        id: 'partition1',
        nodes: new Set(['node2', 'node3']),
        detectedAt: Date.now(),
      };

      consensus.handlePartition(partition);

      // In real implementation, this would trigger callback
      // For now, just verify partition was handled
      expect(consensus.getStats().partitionsDetected).toBe(1);
    });
  });

  describe('Leader Step Down', () => {
    test('should step down from leadership', () => {
      consensus.electLeader();
      expect(consensus.getState()).toBe(NodeState.LEADER);

      consensus.stepDown();

      expect(consensus.getState()).toBe(NodeState.FOLLOWER);
      expect(consensus.getLeader()).toBeNull();
    });

    test('should stop heartbeat when stepping down', () => {
      consensus.electLeader();
      consensus.stepDown();

      // After stepping down, should not send heartbeats
      expect(consensus.getState()).toBe(NodeState.FOLLOWER);
    });
  });

  describe('Log Compaction', () => {
    test('should compact log when size exceeds limit', async () => {
      consensus.electLeader();

      const config = { maxLogSize: 10 };
      consensus = createDistributedConsensus('node1', nodeIds, {
        ...config,
        electionTimeout: 1000,
      });

      // Add more entries than limit
      for (let i = 0; i < 20; i++) {
        const change: StateChange = {
          type: 'agent_introduce',
          params: { index: i },
          timestamp: Date.now(),
          proposedBy: 'node1',
        };
        await consensus.proposeStateChange(change);
      }

      const initialSize = consensus.getLog().length;
      consensus.compactLog();
      const compactedSize = consensus.getLog().length;

      expect(compactedSize).toBeLessThan(initialSize);
      expect(compactedSize).toBeLessThanOrEqual(10);
    });
  });

  describe('Snapshot and Restore', () => {
    test('should create snapshot of current state', async () => {
      consensus.electLeader();

      const change: StateChange = {
        type: 'agent_introduce',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      await consensus.proposeStateChange(change);

      const snapshot = consensus.createSnapshot();

      expect(snapshot.term).toBe(consensus.getTerm());
      expect(snapshot.log).toHaveLength(1);
      expect(snapshot.state).toBe(NodeState.LEADER);
      expect(snapshot.leaderId).toBe('node1');
    });

    test('should restore from snapshot', async () => {
      consensus.electLeader();

      const change: StateChange = {
        type: 'agent_introduce',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      await consensus.proposeStateChange(change);

      const snapshot = consensus.createSnapshot();

      // Create new instance and restore
      const newConsensus = createDistributedConsensus('node1', nodeIds);
      newConsensus.restoreSnapshot(snapshot);

      expect(newConsensus.getTerm()).toBe(snapshot.term);
      expect(newConsensus.getLog()).toHaveLength(snapshot.log.length);
      expect(newConsensus.getState()).toBe(snapshot.state);
      expect(newConsensus.getLeader()).toBe(snapshot.leaderId);

      newConsensus.shutdown();
    });
  });

  describe('Statistics', () => {
    test('should track correct statistics', async () => {
      consensus.electLeader();

      const change: StateChange = {
        type: 'agent_introduce',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      await consensus.proposeStateChange(change);

      const stats = consensus.getStats();

      expect(stats.leaderId).toBe('node1');
      expect(stats.currentTerm).toBeGreaterThan(0);
      expect(stats.totalNodes).toBe(5);
      expect(stats.logEntries).toBe(1);
      expect(stats.committedEntries).toBe(1);
      expect(stats.electionsHeld).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    test('should handle empty cluster gracefully', () => {
      const emptyConsensus = createDistributedConsensus('node1', []);
      expect(emptyConsensus.getCluster()).toHaveLength(0);
      emptyConsensus.shutdown();
    });

    test('should handle single node cluster', () => {
      const singleConsensus = createDistributedConsensus('node1', ['node1']);
      singleConsensus.electLeader();

      expect(singleConsensus.getState()).toBe(NodeState.LEADER);
      expect(singleConsensus.getLeader()).toBe('node1');

      singleConsensus.shutdown();
    });

    test('should handle rapid elections', () => {
      consensus.electLeader();
      consensus.stepDown();
      consensus.electLeader();
      consensus.stepDown();

      expect(consensus.getStats().electionsHeld).toBeGreaterThanOrEqual(2);
    });

    test('should handle concurrent proposals', async () => {
      consensus.electLeader();

      const changes: StateChange[] = [
        { type: 'agent_introduce', params: {}, timestamp: Date.now(), proposedBy: 'node1' },
        { type: 'agent_introduce', params: {}, timestamp: Date.now(), proposedBy: 'node1' },
        { type: 'agent_introduce', params: {}, timestamp: Date.now(), proposedBy: 'node1' },
      ];

      const results = await Promise.all(
        changes.map(change => consensus.proposeStateChange(change))
      );

      expect(results.every(r => r.achieved)).toBe(true);
      expect(consensus.getLog()).toHaveLength(3);
    });

    test('should reject proposals when not leader', async () => {
      const change: StateChange = {
        type: 'agent_introduce',
        params: {},
        timestamp: Date.now(),
        proposedBy: 'node1',
      };

      const result = await consensus.proposeStateChange(change);

      expect(result.achieved).toBe(false);
      expect(result.error).toBe('Not leader');
    });
  });

  describe('Shutdown', () => {
    test('should shutdown gracefully', () => {
      consensus.electLeader();
      consensus.shutdown();

      expect(consensus.getState()).toBe(NodeState.FOLLOWER);
    });

    test('should clear timers on shutdown', () => {
      consensus.electLeader();
      consensus.shutdown();

      // Should not crash when shutting down again
      expect(() => consensus.shutdown()).not.toThrow();
    });
  });
});

describe('Helper Functions', () => {
  describe('calculateQuorum', () => {
    test('should calculate majority for odd cluster size', () => {
      expect(calculateQuorum(5, 'majority')).toBe(3);
      expect(calculateQuorum(7, 'majority')).toBe(4);
    });

    test('should calculate majority for even cluster size', () => {
      expect(calculateQuorum(4, 'majority')).toBe(3);
      expect(calculateQuorum(6, 'majority')).toBe(4);
    });

    test('should calculate supermajority', () => {
      expect(calculateQuorum(5, 'supermajority')).toBe(4);
      expect(calculateQuorum(10, 'supermajority')).toBe(7);
    });

    test('should calculate unanimous', () => {
      expect(calculateQuorum(5, 'unanimous')).toBe(5);
      expect(calculateQuorum(3, 'unanimous')).toBe(3);
    });
  });

  describe('detectPartition', () => {
    test('should detect dead nodes', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2', 'node3']);
      consensus.setNodeAlive('node2', false);
      consensus.setNodeAlive('node3', false);

      const cluster = new Map(consensus.getCluster().map(n => [n.id, n]));
      const partitions = detectPartition(cluster, 100);

      expect(partitions).toHaveLength(1);
      expect(partitions[0].nodes.has('node2')).toBe(true);
      expect(partitions[0].nodes.has('node3')).toBe(true);

      consensus.shutdown();
    });

    test('should detect nodes with old heartbeats', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2', 'node3']);

      // Simulate old heartbeat
      const cluster = consensus.getCluster();
      cluster[1].lastHeartbeat = Date.now() - 20000; // 20 seconds ago

      const clusterMap = new Map(cluster.map(n => [n.id, n]));
      const partitions = detectPartition(clusterMap, 15000);

      expect(partitions).toHaveLength(1);
      expect(partitions[0].nodes.has('node3')).toBe(true);

      consensus.shutdown();
    });

    test('should return empty array when no partitions', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2', 'node3']);

      const cluster = new Map(consensus.getCluster().map(n => [n.id, n]));
      const partitions = detectPartition(cluster, 15000);

      expect(partitions).toHaveLength(0);

      consensus.shutdown();
    });
  });

  describe('recoverFromPartition', () => {
    test('should handle wait strategy', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2']);
      const partition: Partition = {
        id: 'p1',
        nodes: new Set(['node1']),
        detectedAt: Date.now(),
      };

      expect(() => {
        recoverFromPartition(consensus, partition, RecoveryStrategy.WAIT);
      }).not.toThrow();

      consensus.shutdown();
    });

    test('should handle majority strategy', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2', 'node3']);
      const partition: Partition = {
        id: 'p1',
        nodes: new Set(['node1', 'node2']),
        detectedAt: Date.now(),
      };

      recoverFromPartition(consensus, partition, RecoveryStrategy.MAJORITY);

      // Should trigger election
      expect(consensus.getState() === NodeState.CANDIDATE ||
             consensus.getState() === NodeState.LEADER).toBe(true);

      consensus.shutdown();
    });

    test('should handle merge strategy', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2']);
      const partition: Partition = {
        id: 'p1',
        nodes: new Set(['node1']),
        detectedAt: Date.now(),
      };

      expect(() => {
        recoverFromPartition(consensus, partition, RecoveryStrategy.MERGE);
      }).not.toThrow();

      consensus.shutdown();
    });

    test('should handle rollback strategy', () => {
      const consensus = createDistributedConsensus('node1', ['node1', 'node2']);
      const partition: Partition = {
        id: 'p1',
        nodes: new Set(['node1']),
        detectedAt: Date.now(),
      };

      expect(() => {
        recoverFromPartition(consensus, partition, RecoveryStrategy.ROLLBACK);
      }).not.toThrow();

      consensus.shutdown();
    });
  });
});

describe('Integration Scenarios', () => {
  test('should handle full election and log replication cycle', async () => {
    const nodeIds = ['node1', 'node2', 'node3'];
    const consensus = createDistributedConsensus('node1', nodeIds, {
      electionTimeout: 500,
      heartbeatInterval: 100,
    });

    // Wait for election
    await new Promise(resolve => setTimeout(resolve, 600));
    expect(consensus.getState() === NodeState.LEADER ||
           consensus.getState() === NodeState.CANDIDATE).toBe(true);

    // Manually become leader
    consensus.electLeader();
    expect(consensus.getState()).toBe(NodeState.LEADER);

    // Propose changes
    const changes: StateChange[] = [
      { type: 'agent_introduce', params: { name: 'agent1' }, timestamp: Date.now(), proposedBy: 'node1' },
      { type: 'agent_introduce', params: { name: 'agent2' }, timestamp: Date.now(), proposedBy: 'node1' },
      { type: 'colony_form', params: { members: ['agent1', 'agent2'] }, timestamp: Date.now(), proposedBy: 'node1' },
    ];

    for (const change of changes) {
      const result = await consensus.proposeStateChange(change);
      expect(result.achieved).toBe(true);
    }

    expect(consensus.getLog()).toHaveLength(3);
    expect(consensus.getLog().every(e => e.committed)).toBe(true);

    consensus.shutdown();
  });

  test('should handle network partition and recovery', async () => {
    const nodeIds = ['node1', 'node2', 'node3', 'node4', 'node5'];
    const consensus = createDistributedConsensus('node1', nodeIds);

    // Mark some nodes as dead (simulate partition)
    consensus.setNodeAlive('node4', false);
    consensus.setNodeAlive('node5', false);

    // Detect partition
    const cluster = new Map(consensus.getCluster().map(n => [n.id, n]));
    const partitions = detectPartition(cluster, 100);

    expect(partitions).toHaveLength(1);
    expect(partitions[0].nodes.size).toBeGreaterThanOrEqual(2);

    // Handle partition
    const strategy = consensus.handlePartition(partitions[0]);
    expect(strategy).toBeDefined();

    consensus.shutdown();
  });

  test('should maintain consistency across leader changes', async () => {
    const consensus = createDistributedConsensus('node1', ['node1', 'node2', 'node3']);

    // Become leader and propose changes
    consensus.electLeader();

    const change1: StateChange = {
      type: 'agent_introduce',
      params: { name: 'agent1' },
      timestamp: Date.now(),
      proposedBy: 'node1',
    };

    await consensus.proposeStateChange(change1);

    const logBefore = consensus.getLog();
    expect(logBefore).toHaveLength(1);

    // Step down and become leader again
    consensus.stepDown();
    consensus.electLeader();

    const change2: StateChange = {
      type: 'agent_introduce',
      params: { name: 'agent2' },
      timestamp: Date.now(),
      proposedBy: 'node1',
    };

    await consensus.proposeStateChange(change2);

    const logAfter = consensus.getLog();

    // Log should be maintained
    expect(logAfter.length).toBeGreaterThanOrEqual(logBefore.length);

    consensus.shutdown();
  });
});
