/**
 * POLLN Microbiome - Distributed Ecosystem Integration
 *
 * Phase 8: Distributed Systems - Milestone 1
 * Integrates DistributedConsensus with DigitalTerrarium for
 * multi-node microbiome deployment.
 *
 * @module microbiome/distributed-ecosystem
 */

import { DigitalTerrarium, EcosystemConfig, EcosystemEvent } from './ecosystem.js';
import { MicrobiomeAgent, ResourceType } from './types.js';
import {
  DistributedConsensus,
  createDistributedConsensus,
  NodeId,
  StateChange,
  LogEntry,
  Partition,
  RecoveryStrategy,
  ConsensusStats,
} from './distributed.js';

/**
 * Distributed ecosystem configuration
 */
export interface DistributedEcosystemConfig {
  /** Base ecosystem configuration */
  ecosystem?: Partial<EcosystemConfig>;
  /** Node ID for this instance */
  nodeId: NodeId;
  /** Cluster node IDs */
  clusterNodes: NodeId[];
  /** Enable distributed mode */
  distributedEnabled: boolean;
  /** Replicate state changes */
  replicateState: boolean;
  /** Auto-recover from partitions */
  autoRecover: boolean;
}

/**
 * Distributed ecosystem state
 */
export interface DistributedEcosystemState {
  /** Local state */
  local: any;
  /** Replicated state */
  replicated: any;
  /** Commit index */
  commitIndex: number;
  /** Current leader */
  leaderId: NodeId | null;
}

/**
 * Distributed Digital Terrarium
 *
 * Extends DigitalTerrarium with distributed consensus capabilities
 * for multi-node deployment and coordination.
 */
export class DistributedDigitalTerrarium extends DigitalTerrarium {
  /** Node ID */
  private nodeId: NodeId;
  /** Cluster nodes */
  private clusterNodes: NodeId[];
  /** Distributed consensus */
  private consensus: DistributedConsensus | null;
  /** Distributed mode enabled */
  private distributedEnabled: boolean;
  /** Replicate state changes */
  private replicateState: boolean;
  /** Auto-recover from partitions */
  private autoRecover: boolean;
  /** Pending state changes */
  private pendingChanges: StateChange[];
  /** Committed state changes */
  private committedChanges: StateChange[];

  constructor(config: DistributedEcosystemConfig) {
    super(config.ecosystem);

    this.nodeId = config.nodeId;
    this.clusterNodes = config.clusterNodes;
    this.distributedEnabled = config.distributedEnabled;
    this.replicateState = config.replicateState ?? true;
    this.autoRecover = config.autoRecover ?? true;
    this.pendingChanges = [];
    this.committedChanges = [];

    if (this.distributedEnabled) {
      this.consensus = createDistributedConsensus(
        this.nodeId,
        this.clusterNodes,
        {
          electionTimeout: 5000,
          heartbeatInterval: 1000,
          enablePartitionDetection: true,
        }
      );

      // Register consensus callbacks
      this.setupConsensusCallbacks();
    } else {
      this.consensus = null;
    }
  }

  /**
   * Setup consensus event callbacks
   */
  private setupConsensusCallbacks(): void {
    if (!this.consensus) return;

    // Handle committed log entries
    this.consensus.onCommit((entry: LogEntry) => {
      this.applyCommittedChange(entry.command);
    });

    // Handle leader changes
    this.consensus.onLeaderChange((leaderId: NodeId) => {
      console.log(`[DistributedEcosystem] Leader changed to ${leaderId}`);

      if (leaderId === this.nodeId) {
        console.log('[DistributedEcosystem] This node is now the leader');
      }
    });

    // Handle network partitions
    this.consensus.onPartition((partition: Partition) => {
      console.warn(`[DistributedEcosystem] Partition detected: ${partition.id}`);

      if (this.autoRecover) {
        const strategy = this.consensus?.handlePartition(partition);
        if (strategy) {
          console.log(`[DistributedEcosystem] Recovery strategy: ${strategy}`);
        }
      }
    });
  }

  /**
   * Apply committed state change
   */
  private applyCommittedChange(change: StateChange): void {
    this.committedChanges.push(change);

    switch (change.type) {
      case 'agent_introduce':
        if (change.params.agent) {
          this.introduce(change.params.agent);
        }
        break;

      case 'agent_cull':
        if (change.targetId) {
          this.cull(change.targetId);
        }
        break;

      case 'colony_form':
        if (change.params.members) {
          this.graft(change.params.members);
        }
        break;

      case 'resource_modify':
        if (change.params.resource && change.params.amount) {
          this.fertilize(change.params.resource, change.params.amount);
        }
        break;

      case 'config_update':
        // Config updates handled separately
        break;
    }
  }

  /**
   * Introduce agent with distributed replication
   */
  async introduceReplicated(agent: MicrobiomeAgent): Promise<boolean> {
    // Local introduce first
    const introduced = this.introduce(agent);
    if (!introduced) return false;

    // Replicate if enabled and we're leader
    if (this.replicateState && this.consensus && this.consensus.getState() === 'leader') {
      const change: StateChange = {
        type: 'agent_introduce',
        targetId: agent.id,
        params: { agent },
        timestamp: Date.now(),
        proposedBy: this.nodeId,
      };

      try {
        const result = await this.consensus.proposeStateChange(change);
        return result.achieved;
      } catch (error) {
        console.error('[DistributedEcosystem] Failed to replicate introduce:', error);
        return false;
      }
    }

    return true;
  }

  /**
   * Cull agent with distributed replication
   */
  async cullReplicated(agentId: string): Promise<boolean> {
    // Local cull first
    const culled = this.cull(agentId);
    if (!culled) return false;

    // Replicate if enabled and we're leader
    if (this.replicateState && this.consensus && this.consensus.getState() === 'leader') {
      const change: StateChange = {
        type: 'agent_cull',
        targetId: agentId,
        params: {},
        timestamp: Date.now(),
        proposedBy: this.nodeId,
      };

      try {
        const result = await this.consensus.proposeStateChange(change);
        return result.achieved;
      } catch (error) {
        console.error('[DistributedEcosystem] Failed to replicate cull:', error);
        return false;
      }
    }

    return true;
  }

  /**
   * Form colony with distributed replication
   */
  async graftReplicated(memberIds: string[]): Promise<boolean> {
    // Local graft first
    const colony = this.graft(memberIds);
    if (!colony) return false;

    // Replicate if enabled and we're leader
    if (this.replicateState && this.consensus && this.consensus.getState() === 'leader') {
      const change: StateChange = {
        type: 'colony_form',
        params: { members: memberIds },
        timestamp: Date.now(),
        proposedBy: this.nodeId,
      };

      try {
        const result = await this.consensus.proposeStateChange(change);
        return result.achieved;
      } catch (error) {
        console.error('[DistributedEcosystem] Failed to replicate graft:', error);
        return false;
      }
    }

    return true;
  }

  /**
   * Add resources with distributed replication
   */
  async fertilizeReplicated(resource: ResourceType, amount: number): Promise<boolean> {
    // Local fertilize first
    this.fertilize(resource, amount);

    // Replicate if enabled and we're leader
    if (this.replicateState && this.consensus && this.consensus.getState() === 'leader') {
      const change: StateChange = {
        type: 'resource_modify',
        params: { resource, amount },
        timestamp: Date.now(),
        proposedBy: this.nodeId,
      };

      try {
        const result = await this.consensus.proposeStateChange(change);
        return result.achieved;
      } catch (error) {
        console.error('[DistributedEcosystem] Failed to replicate fertilize:', error);
        return false;
      }
    }

    return true;
  }

  /**
   * Get distributed consensus statistics
   */
  getConsensusStats(): ConsensusStats | null {
    return this.consensus ? this.consensus.getStats() : null;
  }

  /**
   * Get current leader
   */
  getLeader(): NodeId | null {
    return this.consensus ? this.consensus.getLeader() : null;
  }

  /**
   * Check if this node is leader
   */
  isLeader(): boolean {
    return this.consensus ? this.consensus.getLeader() === this.nodeId : false;
  }

  /**
   * Get cluster nodes
   */
  getCluster() {
    return this.consensus ? this.consensus.getCluster() : [];
  }

  /**
   * Add node to cluster
   */
  addClusterNode(nodeId: NodeId, address: string): void {
    this.consensus?.addNode(nodeId, address);
  }

  /**
   * Remove node from cluster
   */
  removeClusterNode(nodeId: NodeId): void {
    this.consensus?.removeNode(nodeId);
  }

  /**
   * Mark node as alive/dead
   */
  setNodeAlive(nodeId: NodeId, alive: boolean): void {
    this.consensus?.setNodeAlive(nodeId, alive);
  }

  /**
   * Trigger leader election
   */
  electLeader(): NodeId | null {
    return this.consensus?.electLeader() ?? null;
  }

  /**
   * Step down as leader
   */
  stepDown(): void {
    this.consensus?.stepDown();
  }

  /**
   * Get distributed state
   */
  getDistributedState(): DistributedEcosystemState {
    return {
      local: this.exportState(),
      replicated: this.consensus ? this.consensus.createSnapshot() : null,
      commitIndex: this.consensus ? this.consensus.getStats().committedEntries : 0,
      leaderId: this.getLeader(),
    };
  }

  /**
   * Create snapshot including distributed state
   */
  createDistributedSnapshot(): {
    ecosystem: any;
    consensus: any;
    timestamp: number;
  } {
    return {
      ecosystem: this.exportState(),
      consensus: this.consensus?.createSnapshot(),
      timestamp: Date.now(),
    };
  }

  /**
   * Restore from distributed snapshot
   */
  restoreDistributedSnapshot(snapshot: {
    ecosystem: any;
    consensus: any;
  }): void {
    this.importState(snapshot.ecosystem);
    if (this.consensus && snapshot.consensus) {
      this.consensus.restoreSnapshot(snapshot.consensus);
    }
  }

  /**
   * Shutdown distributed ecosystem
   */
  async shutdown(): Promise<void> {
    await this.stop();
    this.consensus?.shutdown();
  }

  /**
   * Get performance metrics including distributed stats
   */
  getPerformanceMetrics() {
    const baseMetrics = super.getPerformanceMetrics();

    return {
      ...baseMetrics,
      distributed: this.consensus ? this.consensus.getStats() : null,
    };
  }
}

/**
 * Create distributed digital terrarium
 */
export function createDistributedTerrarium(
  nodeId: NodeId,
  clusterNodes: NodeId[],
  config?: Partial<DistributedEcosystemConfig>
): DistributedDigitalTerrarium {
  return new DistributedDigitalTerrarium({
    nodeId,
    clusterNodes,
    distributedEnabled: true,
    replicateState: true,
    autoRecover: true,
    ...config,
  });
}
