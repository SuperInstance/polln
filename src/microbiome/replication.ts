/**
 * POLLN Microbiome - State Replication System
 *
 * Phase 8: Distributed Systems - Milestone 2
 * State replication across distributed nodes with conflict resolution,
 * vector clocks, and anti-entropy gossip protocol.
 *
 * @module microbiome/replication
 */

import { v4 as uuidv4 } from 'uuid';
import { DistributedConsensus, NodeId, StateChange } from './distributed.js';
import { MicrobiomeAgent, EcosystemSnapshot } from './types.js';

/**
 * Replication strategy types
 */
export enum ReplicationStrategy {
  /** Synchronous - wait for all replicas before commit */
  SYNCHRONOUS = 'synchronous',
  /** Asynchronous - fire and forget */
  ASYNCHRONOUS = 'asynchronous',
  /** Semi-synchronous - wait for quorum */
  SEMISYNCHRONOUS = 'semisynchronous',
}

/**
 * Conflict resolution strategies
 */
export enum ConflictResolutionStrategy {
  /** Last writer wins (based on timestamp) */
  LAST_WRITE_WINS = 'last_write_wins',
  /** CRDT merge (conflict-free replicated data type) */
  CRDT_MERGE = 'crdt_merge',
  /** Application-level custom resolution */
  APPLICATION = 'application',
  /** Vector clock causality */
  VECTOR_CLOCK = 'vector_clock',
}

/**
 * Vector clock for tracking causality
 */
export interface VectorClock {
  /** Node ID to version mapping */
  clock: Map<NodeId, number>;
  /** Dot in version vector (nodeId, version) */
  addDot(nodeId: NodeId, version: number): void;
  /** Compare two vector clocks */
  compare(other: VectorClock): ClockComparison;
  /** Merge two vector clocks (taking max) */
  merge(other: VectorClock): VectorClock;
  /** Check if this clock dominates other */
  dominates(other: VectorClock): boolean;
  /** Check if concurrent (neither dominates) */
  isConcurrentWith(other: VectorClock): boolean;
  /** Clone the clock */
  clone(): VectorClock;
  /** Serialize to JSON */
  toJSON(): Record<string, number>;
}

/**
 * Vector clock comparison result
 */
export enum ClockComparison {
  /** This clock happened before other */
  BEFORE = 'before',
  /** This clock happened after other */
  AFTER = 'after',
  /** Clocks are equal */
  EQUAL = 'equal',
  /** Clocks are concurrent (causally unrelated) */
  CONCURRENT = 'concurrent',
}

/**
 * Versioned state with vector clock
 */
export interface VersionedState {
  /** State identifier */
  id: string;
  /** State data */
  state: any;
  /** Vector clock for causality */
  vectorClock: VectorClock;
  /** Timestamp */
  timestamp: number;
  /** Version at originating node */
  version: number;
  /** Originating node */
  originNode: NodeId;
  /** Deleted flag (for tombstones) */
  deleted?: boolean;
}

/**
 * Replication conflict
 */
export interface ReplicationConflict {
  /** Conflict ID */
  id: string;
  /** State ID */
  stateId: string;
  /** Conflicting versions */
  versions: VersionedState[];
  /** Conflict type */
  type: ConflictType;
  /** Detected timestamp */
  detectedAt: number;
  /** Resolution strategy */
  resolutionStrategy: ConflictResolutionStrategy;
  /** Resolution status */
  resolved: boolean;
}

/**
 * Conflict types
 */
export enum ConflictType {
  /** Concurrent updates */
  CONCURRENT_UPDATE = 'concurrent_update',
  /** divergent branches */
  DIVERGENT = 'divergent',
  /** Deleted vs updated */
  UPDATE_DELETE = 'update_delete',
}

/**
 * Replication result
 */
export interface ReplicationResult {
  /** Replication successful */
  success: boolean;
  /** Nodes replicated to */
  replicatedTo: NodeId[];
  /** Failed nodes */
  failedNodes: NodeId[];
  /** Conflicts detected */
  conflicts: ReplicationConflict[];
  /** Replication duration (ms) */
  duration: number;
}

/**
 * Sync result for ecosystem state
 */
export interface SyncResult {
  /** Sync successful */
  success: boolean;
  /** States synchronized */
  statesSynced: number;
  /** Conflicts resolved */
  conflictsResolved: number;
  /** Bytes transferred */
  bytesTransferred: number;
  /** Sync duration (ms) */
  duration: number;
}

/**
 * State delta for anti-entropy
 */
export interface StateDelta {
  /** States to add/update */
  additions: Map<string, VersionedState>;
  /** States to delete */
  deletions: Set<string>;
  /** Vector clock changes */
  clockChanges: Map<NodeId, number>;
  /** Delta timestamp */
  timestamp: number;
}

/**
 * Gossip message for anti-entropy
 */
export interface GossipMessage {
  /** Message ID */
  id: string;
  /** From node */
  fromNode: NodeId;
  /** To node */
  toNode: NodeId;
  /** State delta */
  delta: StateDelta;
  /** Message timestamp */
  timestamp: number;
}

/**
 * Merkle tree node for state verification
 */
export interface MerkleNode {
  /** Node hash */
  hash: string;
  /** Left child */
  left?: MerkleNode;
  /** Right child */
  right?: MerkleNode;
  /** State key (if leaf) */
  key?: string;
  /** State value (if leaf) */
  value?: any;
}

/**
 * Replication health status
 */
export interface ReplicationHealth {
  /** Node ID */
  nodeId: NodeId;
  /** Replication lag (ms) */
  lag: number;
  /** Last sync timestamp */
  lastSync: number;
  /** Sync success rate */
  successRate: number;
  /** Pending replicas */
  pendingReplicas: number;
  /** Conflicts pending resolution */
  pendingConflicts: number;
  /** Is healthy */
  isHealthy: boolean;
}

/**
 * State replicator configuration
 */
export interface StateReplicatorConfig {
  /** Replication strategy */
  strategy: ReplicationStrategy;
  /** Conflict resolution strategy */
  conflictResolution: ConflictResolutionStrategy;
  /** Replication timeout (ms) */
  replicationTimeout: number;
  /** Gossip interval (ms) */
  gossipInterval: number;
  /** Maximum retries for failed replication */
  maxRetries: number;
  /** Enable anti-entropy */
  enableAntiEntropy: boolean;
  /** Enable Merkle tree verification */
  enableMerkleVerification: boolean;
  /** Maximum conflicts before intervention */
  maxConflicts: number;
}

/**
 * State replicator - handles replication across distributed nodes
 */
export class StateReplicator {
  /** Local node ID */
  private nodeId: NodeId;
  /** Consensus instance */
  private consensus: DistributedConsensus;
  /** Replicated states */
  private states: Map<string, VersionedState>;
  /** Pending replicas */
  private pendingReplicas: Map<string, Set<NodeId>>;
  /** Active conflicts */
  private conflicts: Map<string, ReplicationConflict>;
  /** Replication health */
  private healthStatus: Map<NodeId, ReplicationHealth>;
  /** Gossip timer */
  private gossipTimer: NodeJS.Timeout | null;
  /** Configuration */
  private config: StateReplicatorConfig;
  /** Replication statistics */
  private stats: {
    totalReplications: number;
    successfulReplications: number;
    failedReplications: number;
    conflictsDetected: number;
    conflictsResolved: number;
    gossipExchanges: number;
  };

  /**
   * Create state replicator instance
   */
  constructor(
    nodeId: NodeId,
    consensus: DistributedConsensus,
    config: Partial<StateReplicatorConfig> = {}
  ) {
    this.nodeId = nodeId;
    this.consensus = consensus;
    this.states = new Map();
    this.pendingReplicas = new Map();
    this.conflicts = new Map();
    this.healthStatus = new Map();
    this.gossipTimer = null;

    this.config = {
      strategy: config.strategy ?? ReplicationStrategy.SYNCHRONOUS,
      conflictResolution: config.conflictResolution ?? ConflictResolutionStrategy.VECTOR_CLOCK,
      replicationTimeout: config.replicationTimeout ?? 5000,
      gossipInterval: config.gossipInterval ?? 10000,
      maxRetries: config.maxRetries ?? 3,
      enableAntiEntropy: config.enableAntiEntropy ?? true,
      enableMerkleVerification: config.enableMerkleVerification ?? true,
      maxConflicts: config.maxConflicts ?? 100,
    };

    this.stats = {
      totalReplications: 0,
      successfulReplications: 0,
      failedReplications: 0,
      conflictsDetected: 0,
      conflictsResolved: 0,
      gossipExchanges: 0,
    };

    // Start gossip if enabled
    if (this.config.enableAntiEntropy) {
      this.startGossip();
    }
  }

  /**
   * Replicate agent state to backup nodes
   */
  async replicateAgent(
    agentId: string,
    nodes: NodeId[],
    state: MicrobiomeAgent
  ): Promise<ReplicationResult> {
    const startTime = Date.now();
    this.stats.totalReplications++;

    // Create versioned state
    const vectorClock = this.createVectorClock();
    vectorClock.addDot(this.nodeId, this.getCurrentVersion(agentId) + 1);

    const versionedState: VersionedState = {
      id: agentId,
      state: this.serializeAgent(state),
      vectorClock,
      timestamp: Date.now(),
      version: this.getCurrentVersion(agentId) + 1,
      originNode: this.nodeId,
    };

    // Store locally
    this.states.set(agentId, versionedState);

    // Replicate to nodes
    const result = await this.replicateToNodes(versionedState, nodes);

    result.duration = Date.now() - startTime;

    if (result.success) {
      this.stats.successfulReplications++;
    } else {
      this.stats.failedReplications++;
    }

    return result;
  }

  /**
   * Synchronize ecosystem state
   */
  async syncEcosystemState(snapshot: EcosystemSnapshot): Promise<SyncResult> {
    const startTime = Date.now();
    let statesSynced = 0;
    let conflictsResolved = 0;
    let bytesTransferred = 0;

    // Serialize all agents
    for (const [agentId, agent] of Array.from(snapshot.agents.entries())) {
      const vectorClock = this.createVectorClock();
      vectorClock.addDot(this.nodeId, this.getCurrentVersion(agentId) + 1);

      const versionedState: VersionedState = {
        id: agentId,
        state: this.serializeAgent(agent),
        vectorClock,
        timestamp: Date.now(),
        version: this.getCurrentVersion(agentId) + 1,
        originNode: this.nodeId,
      };

      bytesTransferred += JSON.stringify(versionedState).length;

      // Check for conflicts
      const existing = this.states.get(agentId);
      if (existing) {
        const conflict = this.detectConflict(existing, versionedState);
        if (conflict) {
          this.conflicts.set(conflict.id, conflict);
          this.stats.conflictsDetected++;

          const resolved = await this.resolveConflict(conflict);
          if (resolved) {
            conflictsResolved++;
            this.stats.conflictsResolved++;
          }
          continue;
        }
      }

      this.states.set(agentId, versionedState);
      statesSynced++;
    }

    const duration = Date.now() - startTime;

    return {
      success: true,
      statesSynced,
      conflictsResolved,
      bytesTransferred,
      duration,
    };
  }

  /**
   * Resolve conflict between versions
   */
  async resolveConflict(conflict: ReplicationConflict): Promise<boolean> {
    if (conflict.resolved) {
      return true;
    }

    let resolvedState: VersionedState | null = null;

    switch (conflict.resolutionStrategy) {
      case ConflictResolutionStrategy.LAST_WRITE_WINS:
        resolvedState = this.resolveLastWriteWins(conflict);
        break;

      case ConflictResolutionStrategy.CRDT_MERGE:
        resolvedState = this.resolveCRDTMerge(conflict);
        break;

      case ConflictResolutionStrategy.VECTOR_CLOCK:
        resolvedState = this.resolveVectorClock(conflict);
        break;

      case ConflictResolutionStrategy.APPLICATION:
        resolvedState = await this.resolveApplicationLevel(conflict);
        break;
    }

    if (resolvedState) {
      // Apply resolved state
      this.states.set(conflict.stateId, resolvedState);
      conflict.resolved = true;
      return true;
    }

    return false;
  }

  /**
   * Update vector clock for agent
   */
  updateVectorClock(agentId: string, version: number): VectorClock {
    const vectorClock = this.createVectorClock();
    vectorClock.addDot(this.nodeId, version);

    // Update existing state if present
    const existing = this.states.get(agentId);
    if (existing) {
      existing.vectorClock.merge(vectorClock);
      return existing.vectorClock;
    }

    return vectorClock;
  }

  /**
   * Exchange state with peer (anti-entropy gossip)
   */
  exchangeState(peer: NodeId): StateDelta {
    this.stats.gossipExchanges++;

    // Update health status for peer
    this.updateHealthStatus(peer);

    // Calculate delta
    const delta: StateDelta = {
      additions: new Map(),
      deletions: new Set(),
      clockChanges: new Map(),
      timestamp: Date.now(),
    };

    // Add all local states
    for (const [id, state] of Array.from(this.states.entries())) {
      delta.additions.set(id, state);
    }

    // Add vector clock changes
    delta.clockChanges.set(this.nodeId, this.getCurrentVersion('local'));

    return delta;
  }

  /**
   * Receive gossip message
   */
  receiveGossip(message: GossipMessage): void {
    // Apply incoming delta
    for (const [id, state] of Array.from(message.delta.additions.entries())) {
      const existing = this.states.get(id);

      if (!existing) {
        // New state - accept it
        this.states.set(id, state);
      } else {
        // Check for conflict
        const comparison = existing.vectorClock.compare(state.vectorClock);

        if (comparison === ClockComparison.CONCURRENT) {
          // Conflict detected
          const conflict: ReplicationConflict = {
            id: uuidv4(),
            stateId: id,
            versions: [existing, state],
            type: ConflictType.CONCURRENT_UPDATE,
            detectedAt: Date.now(),
            resolutionStrategy: this.config.conflictResolution,
            resolved: false,
          };

          this.conflicts.set(conflict.id, conflict);
          this.stats.conflictsDetected++;
        } else if (comparison === ClockComparison.BEFORE) {
          // Incoming state is newer - accept it
          this.states.set(id, state);
        }
        // If AFTER, keep existing (we're newer)
      }
    }

    // Process deletions
    for (const id of Array.from(message.delta.deletions)) {
      this.states.delete(id);
    }

    // Update health status
    this.updateHealthStatus(message.fromNode);
  }

  /**
   * Verify state consistency using Merkle tree
   */
  verifyStateConsistency(root: MerkleNode): boolean {
    if (!this.config.enableMerkleVerification) {
      return true;
    }

    // Build local Merkle tree
    const localRoot = this.buildMerkleTree();

    // Compare hashes
    return root.hash === localRoot.hash;
  }

  /**
   * Get replication health for all nodes
   */
  getReplicationHealth(): Map<NodeId, ReplicationHealth> {
    return new Map(this.healthStatus);
  }

  /**
   * Get replication statistics
   */
  getStats(): {
    totalReplications: number;
    successfulReplications: number;
    failedReplications: number;
    successRate: number;
    conflictsDetected: number;
    conflictsResolved: number;
    gossipExchanges: number;
  } {
    const successRate = this.stats.totalReplications > 0
      ? this.stats.successfulReplications / this.stats.totalReplications
      : 1.0;

    return {
      ...this.stats,
      successRate,
    };
  }

  /**
   * Shutdown replicator
   */
  shutdown(): void {
    if (this.gossipTimer) {
      clearInterval(this.gossipTimer);
      this.gossipTimer = null;
    }
  }

  // Private methods

  /**
   * Replicate state to specific nodes
   */
  private async replicateToNodes(
    state: VersionedState,
    nodes: NodeId[]
  ): Promise<ReplicationResult> {
    const result: ReplicationResult = {
      success: true,
      replicatedTo: [],
      failedNodes: [],
      conflicts: [],
      duration: 0,
    };

    const clusterNodes = this.consensus.getCluster();
    const aliveNodes = clusterNodes.filter(n => n.isAlive && nodes.includes(n.id));

    // Determine quorum size based on strategy
    let requiredAcks = aliveNodes.length;
    if (this.config.strategy === ReplicationStrategy.SEMISYNCHRONOUS) {
      requiredAcks = Math.floor(aliveNodes.length / 2) + 1;
    }

    let acks = 0;

    for (const node of aliveNodes) {
      try {
        // Simulate replication (in real system, would be RPC)
        const success = await this.sendToNode(node.id, state);

        if (success) {
          result.replicatedTo.push(node.id);
          acks++;

          if (this.config.strategy === ReplicationStrategy.ASYNCHRONOUS) {
            // Fire and forget - count as success
            result.success = true;
            break;
          }
        } else {
          result.failedNodes.push(node.id);
        }
      } catch (error) {
        result.failedNodes.push(node.id);
      }
    }

    // Check if we met requirements
    if (this.config.strategy !== ReplicationStrategy.ASYNCHRONOUS) {
      result.success = acks >= requiredAcks;
    }

    return result;
  }

  /**
   * Send state to node (simulated)
   */
  private async sendToNode(nodeId: NodeId, state: VersionedState): Promise<boolean> {
    // In real system, this would be an RPC call
    // For now, simulate with timeout
    await new Promise(resolve => setTimeout(resolve, Math.random() * 100));

    // Simulate 90% success rate
    return Math.random() < 0.9;
  }

  /**
   * Detect conflict between versions
   */
  private detectConflict(
    existing: VersionedState,
    incoming: VersionedState
  ): ReplicationConflict | null {
    const comparison = existing.vectorClock.compare(incoming.vectorClock);

    if (comparison === ClockComparison.CONCURRENT) {
      return {
        id: uuidv4(),
        stateId: existing.id,
        versions: [existing, incoming],
        type: ConflictType.CONCURRENT_UPDATE,
        detectedAt: Date.now(),
        resolutionStrategy: this.config.conflictResolution,
        resolved: false,
      };
    }

    // Check for update-delete conflict
    if (existing.deleted && !incoming.deleted) {
      return {
        id: uuidv4(),
        stateId: existing.id,
        versions: [existing, incoming],
        type: ConflictType.UPDATE_DELETE,
        detectedAt: Date.now(),
        resolutionStrategy: this.config.conflictResolution,
        resolved: false,
      };
    }

    return null;
  }

  /**
   * Resolve conflict using last-write-wins
   */
  private resolveLastWriteWins(conflict: ReplicationConflict): VersionedState {
    // Sort by timestamp, pick latest
    const sorted = [...conflict.versions].sort((a, b) => b.timestamp - a.timestamp);
    return sorted[0];
  }

  /**
   * Resolve conflict using CRDT merge
   */
  private resolveCRDTMerge(conflict: ReplicationConflict): VersionedState {
    // Merge states taking max of each field
    const merged: any = {};

    for (const version of conflict.versions) {
      if (version.state && typeof version.state === 'object') {
        for (const [key, value] of Object.entries(version.state)) {
          if (!(key in merged) || value > merged[key]) {
            merged[key] = value;
          }
        }
      }
    }

    // Merge vector clocks
    const mergedClock = this.createVectorClock();
    for (const version of conflict.versions) {
      mergedClock.merge(version.vectorClock);
    }

    return {
      ...conflict.versions[0],
      state: merged,
      vectorClock: mergedClock,
      timestamp: Date.now(),
      version: Math.max(...conflict.versions.map(v => v.version)) + 1,
    };
  }

  /**
   * Resolve conflict using vector clock
   */
  private resolveVectorClock(conflict: ReplicationConflict): VersionedState {
    // Pick version with causally latest vector clock
    const sorted = [...conflict.versions].sort((a, b) => {
      const comparison = a.vectorClock.compare(b.vectorClock);
      if (comparison === ClockComparison.AFTER) return -1;
      if (comparison === ClockComparison.BEFORE) return 1;
      return 0;
    });

    // If concurrent, prefer local node
    const local = sorted.find(v => v.originNode === this.nodeId);
    return local ?? sorted[0];
  }

  /**
   * Resolve conflict at application level
   */
  private async resolveApplicationLevel(
    conflict: ReplicationConflict
  ): Promise<VersionedState | null> {
    // In real system, would call application-specific resolver
    // For now, use vector clock as fallback
    return this.resolveVectorClock(conflict);
  }

  /**
   * Create vector clock
   */
  private createVectorClock(): VectorClock {
    const clock = new Map<NodeId, number>();

    return {
      clock,

      addDot(nodeId: NodeId, version: number): void {
        const current = this.clock.get(nodeId) ?? 0;
        this.clock.set(nodeId, Math.max(current, version));
      },

      compare(other: VectorClock): ClockComparison {
        let thisGreater = false;
        let otherGreater = false;

        const allKeys = new Set([...this.clock.keys(), ...other.clock.keys()]);

        for (const key of Array.from(allKeys)) {
          const thisVal = this.clock.get(key) ?? 0;
          const otherVal = other.clock.get(key) ?? 0;

          if (thisVal > otherVal) thisGreater = true;
          if (otherVal > thisVal) otherGreater = true;
        }

        if (thisGreater && !otherGreater) return ClockComparison.AFTER;
        if (otherGreater && !thisGreater) return ClockComparison.BEFORE;
        if (!thisGreater && !otherGreater) return ClockComparison.EQUAL;
        return ClockComparison.CONCURRENT;
      },

      merge(other: VectorClock): VectorClock {
        const merged = this.clone();

        for (const [nodeId, version] of Array.from(other.clock.entries())) {
          merged.addDot(nodeId, version);
        }

        return merged;
      },

      dominates(other: VectorClock): boolean {
        const comparison = this.compare(other);
        return comparison === ClockComparison.AFTER;
      },

      isConcurrentWith(other: VectorClock): boolean {
        return this.compare(other) === ClockComparison.CONCURRENT;
      },

      clone(): VectorClock {
        const clonedClock = new Map<NodeId, number>();
        for (const [nodeId, version] of Array.from(this.clock.entries())) {
          clonedClock.set(nodeId, version);
        }

        return createVectorClockFromMap(clonedClock);
      },

      toJSON(): Record<string, number> {
        const obj: Record<string, number> = {};
        for (const [nodeId, version] of Array.from(this.clock.entries())) {
          obj[nodeId] = version;
        }
        return obj;
      },
    };
  }

  /**
   * Get current version for state
   */
  private getCurrentVersion(stateId: string): number {
    const state = this.states.get(stateId);
    if (!state) return 0;

    // Get version from vector clock for this node
    return state.vectorClock.clock.get(this.nodeId) ?? 0;
  }

  /**
   * Serialize agent to state
   */
  private serializeAgent(agent: MicrobiomeAgent): any {
    if (!agent) {
      return null;
    }

    return {
      id: agent.id,
      taxonomy: agent.taxonomy,
      name: agent.name,
      metabolism: agent.metabolism,
      lifecycle: agent.lifecycle,
      generation: agent.generation,
      size: agent.size,
      complexity: agent.complexity,
    };
  }

  /**
   * Build Merkle tree from current states
   */
  private buildMerkleTree(): MerkleNode {
    // Simple implementation - in production would use proper crypto
    const hashes: string[] = [];

    for (const [id, state] of Array.from(this.states.entries())) {
      const leafHash = this.hashState(id, state);
      hashes.push(leafHash);
    }

    // Build tree bottom-up
    while (hashes.length > 1) {
      const newHashes: string[] = [];

      for (let i = 0; i < hashes.length; i += 2) {
        const left = hashes[i];
        const right = hashes[i + 1] ?? left;
        newHashes.push(this.hashCombine(left, right));
      }

      hashes.length = 0;
      hashes.push(...newHashes);
    }

    return {
      hash: hashes[0] ?? 'empty',
    };
  }

  /**
   * Hash state for Merkle tree
   */
  private hashState(id: string, state: VersionedState): string {
    // Simple hash - in production use crypto
    const str = JSON.stringify({ id, state: state.state, clock: state.vectorClock.toJSON() });
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return hash.toString(16);
  }

  /**
   * Combine two hashes
   */
  private hashCombine(left: string, right: string): string {
    const combined = left + right;
    let hash = 0;
    for (let i = 0; i < combined.length; i++) {
      const char = combined.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(16);
  }

  /**
   * Start gossip protocol
   */
  private startGossip(): void {
    this.gossipTimer = setInterval(() => {
      this.performGossipRound();
    }, this.config.gossipInterval);
  }

  /**
   * Perform one round of gossip
   */
  private performGossipRound(): void {
    const clusterNodes = this.consensus.getCluster();
    const aliveNodes = clusterNodes.filter(n => n.isAlive && n.id !== this.nodeId);

    // Select random peer to gossip with
    if (aliveNodes.length > 0) {
      const peer = aliveNodes[Math.floor(Math.random() * aliveNodes.length)];
      const delta = this.exchangeState(peer.id);

      const message: GossipMessage = {
        id: uuidv4(),
        fromNode: this.nodeId,
        toNode: peer.id,
        delta,
        timestamp: Date.now(),
      };

      // In real system, would send message to peer
      // For now, just track the exchange
      this.updateHealthStatus(peer.id);
    }
  }

  /**
   * Update health status for node
   */
  private updateHealthStatus(nodeId: NodeId): void {
    const existing = this.healthStatus.get(nodeId) ?? {
      nodeId,
      lag: 0,
      lastSync: 0,
      successRate: 1.0,
      pendingReplicas: 0,
      pendingConflicts: 0,
      isHealthy: true,
    };

    existing.lastSync = Date.now();
    existing.lag = Math.min(existing.lag + 100, 5000); // Simulated lag

    // Calculate health
    const isHealthy = existing.lag < 1000 &&
                     existing.successRate > 0.8 &&
                     existing.pendingConflicts < this.config.maxConflicts;

    existing.isHealthy = isHealthy;

    this.healthStatus.set(nodeId, existing);
  }
}

/**
 * Create state replicator instance
 */
export function createStateReplicator(
  nodeId: NodeId,
  consensus: DistributedConsensus,
  config?: Partial<StateReplicatorConfig>
): StateReplicator {
  return new StateReplicator(nodeId, consensus, config);
}

/**
 * Create vector clock from JSON
 */
export function vectorClockFromJSON(json: Record<string, number>): VectorClock {
  const clockMap = new Map<NodeId, number>();

  for (const [nodeId, version] of Object.entries(json)) {
    clockMap.set(nodeId, version);
  }

  return createVectorClockFromMap(clockMap);
}

/**
 * Create vector clock from map (internal helper)
 */
function createVectorClockFromMap(clockMap: Map<NodeId, number>): VectorClock {
  const clock = new Map<NodeId, number>(clockMap);

  return {
    clock,

    addDot(nodeId: NodeId, version: number): void {
      const current = this.clock.get(nodeId) ?? 0;
      this.clock.set(nodeId, Math.max(current, version));
    },

    compare(other: VectorClock): ClockComparison {
      let thisGreater = false;
      let otherGreater = false;

      const allKeys = new Set([...this.clock.keys(), ...other.clock.keys()]);

      for (const key of Array.from(allKeys)) {
        const thisVal = this.clock.get(key) ?? 0;
        const otherVal = other.clock.get(key) ?? 0;

        if (thisVal > otherVal) thisGreater = true;
        if (otherVal > thisVal) otherGreater = true;
      }

      if (thisGreater && !otherGreater) return ClockComparison.AFTER;
      if (otherGreater && !thisGreater) return ClockComparison.BEFORE;
      if (!thisGreater && !otherGreater) return ClockComparison.EQUAL;
      return ClockComparison.CONCURRENT;
    },

    merge(other: VectorClock): VectorClock {
      const merged = this.clone();

      for (const [nodeId, version] of Array.from(other.clock.entries())) {
        merged.addDot(nodeId, version);
      }

      return merged;
    },

    dominates(other: VectorClock): boolean {
      const comparison = this.compare(other);
      return comparison === ClockComparison.AFTER;
    },

    isConcurrentWith(other: VectorClock): boolean {
      return this.compare(other) === ClockComparison.CONCURRENT;
    },

    clone(): VectorClock {
      const clonedClock = new Map<NodeId, number>();
      for (const [nodeId, version] of Array.from(this.clock.entries())) {
        clonedClock.set(nodeId, version);
      }

      return createVectorClockFromMap(clonedClock);
    },

    toJSON(): Record<string, number> {
      const obj: Record<string, number> = {};
      for (const [nodeId, version] of Array.from(this.clock.entries())) {
        obj[nodeId] = version;
      }
      return obj;
    },
  };
}
