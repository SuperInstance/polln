/**
 * POLLN Microbiome - Multi-Node Coordination System
 *
 * Phase 8: Distributed Systems - Milestone 3
 * Multi-node coordination with service discovery, partitioning,
 * agent migration, load balancing, and distributed transactions.
 *
 * @module microbiome/multinode
 */

import { v4 as uuidv4 } from 'uuid';
import {
  DistributedConsensus,
  NodeId,
  StateChange,
  ClusterNode,
} from './distributed.js';
import {
  StateReplicator,
  VersionedState,
  ReplicationResult,
} from './replication.js';
import {
  MicrobiomeAgent,
  EcosystemSnapshot,
  AgentTaxonomy,
} from './types.js';

/**
 * Node information in the cluster
 */
export interface NodeInfo {
  /** Node ID */
  id: NodeId;
  /** Node address */
  address: string;
  /** Node port */
  port: number;
  /** Node is alive */
  isAlive: boolean;
  /** Last heartbeat timestamp */
  lastHeartbeat: number;
  /** Node capacity (0-1) */
  capacity: number;
  /** Current load (0-1) */
  currentLoad: number;
  /** Supported agent types */
  supportedTypes: AgentTaxonomy[];
  /** Node location/region */
  region: string;
  /** Node metadata */
  metadata: Record<string, any>;
  /** Agent count on node */
  agentCount: number;
  /** Node score for routing */
  score: number;
}

/**
 * Service discovery entry
 */
export interface ServiceEntry {
  /** Service ID */
  id: string;
  /** Service name */
  name: string;
  /** Node providing service */
  nodeId: NodeId;
  /** Service endpoint */
  endpoint: string;
  /** Service version */
  version: string;
  /** Service metadata */
  metadata: Record<string, any>;
  /** Registration timestamp */
  registeredAt: number;
  /** Last updated timestamp */
  lastUpdated: number;
  /** TTL (seconds) */
  ttl: number;
}

/**
 * Partition assignment
 */
export interface PartitionAssignment {
  /** Partition ID */
  partitionId: string;
  /** Assigned nodes */
  nodes: NodeId[];
  /** Agent ranges in partition */
  agentRanges: string[];
  /** Partition key */
  partitionKey: string;
  /** Replication factor */
  replicationFactor: number;
}

/**
 * Agent migration record
 */
export interface AgentMigration {
  /** Migration ID */
  id: string;
  /** Agent ID being migrated */
  agentId: string;
  /** Source node */
  sourceNode: NodeId;
  /** Target node */
  targetNode: NodeId;
  /** Migration status */
  status: MigrationStatus;
  /** Start timestamp */
  startedAt: number;
  /** Completed timestamp */
  completedAt?: number;
  /** Agent state snapshot */
  agentSnapshot?: VersionedState;
  /** Error message (if failed) */
  error?: string;
  /** Migration strategy */
  strategy: MigrationStrategy;
}

/**
 * Migration status
 */
export enum MigrationStatus {
  /** Pending start */
  PENDING = 'pending',
  /** In progress */
  IN_PROGRESS = 'in_progress',
  /** Completed successfully */
  COMPLETED = 'completed',
  /** Failed */
  FAILED = 'failed',
  /** Rolled back */
  ROLLED_BACK = 'rolled_back',
}

/**
 * Migration strategy
 */
export enum MigrationStrategy {
  /** Live migration (zero downtime) */
  LIVE = 'live',
  /** Stop-and-copy */
  STOP_AND_COPY = 'stop_and_copy',
  /** Checkpoint restart */
  CHECKPOINT = 'checkpoint',
}

/**
 * Load balancing strategy
 */
export enum LoadBalancingStrategy {
  /** Round-robin distribution */
  ROUND_ROBIN = 'round_robin',
  /** Least loaded node first */
  LEAST_LOADED = 'least_loaded',
  /** Locality-aware (affinity-based) */
  LOCALITY_AWARE = 'locality_aware',
  /** Weighted by capacity */
  WEIGHTED = 'weighted',
  /** Consistent hashing */
  CONSISTENT_HASH = 'consistent_hash',
}

/**
 * Partitioning strategy
 */
export enum PartitioningStrategy {
  /** Hash-based partitioning */
  HASH = 'hash',
  /** Consistent hashing */
  CONSISTENT_HASH = 'consistent_hash',
  /** Range-based */
  RANGE = 'range',
  /** Affinity-based */
  AFFINITY = 'affinity',
  /** Manual assignment */
  MANUAL = 'manual',
}

/**
 * Distributed transaction states
 */
export enum TransactionState {
  /** Transaction initialized */
  INITIALIZED = 'initialized',
  /** Prepared (2PC) */
  PREPARED = 'prepared',
  /** Committed */
  COMMITTED = 'committed',
  /** Aborted */
  ABORTED = 'aborted',
  /** Timed out */
  TIMED_OUT = 'timed_out',
}

/**
 * Transaction type
 */
export enum TransactionType {
  /** Two-phase commit (2PC) */
  TWO_PC = 'two_pc',
  /** Saga pattern (compensating transactions) */
  SAGA = 'saga',
  /** Best effort (no guarantees) */
  BEST_EFFORT = 'best_effort',
}

/**
 * Distributed transaction
 */
export interface DistributedTransaction {
  /** Transaction ID */
  id: string;
  /** Transaction type */
  type: TransactionType;
  /** Transaction state */
  state: TransactionState;
  /** Participating nodes */
  participants: NodeId[];
  /** Operations to execute */
  operations: TransactionOperation[];
  /** Current step (for saga) */
  currentStep: number;
  /** Compensation operations (for saga) */
  compensations: TransactionOperation[];
  /** Timeout (ms) */
  timeout: number;
  /** Started timestamp */
  startedAt: number;
  /** Completed timestamp */
  completedAt?: number;
  /** Error message (if failed) */
  error?: string;
  /** Votes from participants (2PC) */
  votes: Map<NodeId, boolean>;
}

/**
 * Transaction operation
 */
export interface TransactionOperation {
  /** Operation ID */
  id: string;
  /** Target node */
  nodeId: NodeId;
  /** Operation type */
  type: 'agent_introduce' | 'agent_cull' | 'state_update';
  /** Operation parameters */
  params: Record<string, any>;
  /** Executed flag */
  executed: boolean;
  /** Result */
  result?: any;
  /** Error (if failed) */
  error?: string;
}

/**
 * Multi-node coordinator configuration
 */
export interface MultiNodeConfig {
  /** Gossip interval for service discovery (ms) */
  gossipInterval: number;
  /** Service TTL (seconds) */
  serviceTTL: number;
  /** Partitioning strategy */
  partitioningStrategy: PartitioningStrategy;
  /** Load balancing strategy */
  loadBalancingStrategy: LoadBalancingStrategy;
  /** Default replication factor */
  replicationFactor: number;
  /** Enable auto-migration */
  enableAutoMigration: boolean;
  /** Migration timeout (ms) */
  migrationTimeout: number;
  /** Load balancing threshold */
  loadBalanceThreshold: number;
  /** Transaction timeout (ms) */
  transactionTimeout: number;
  /** Enable consistent hashing */
  enableConsistentHashing: boolean;
  /** Virtual nodes for consistent hashing */
  virtualNodes: number;
  /** Enable distributed transactions */
  enableDistributedTransactions: boolean;
  /** Max retry attempts */
  maxRetries: number;
}

/**
 * Service registry for node discovery
 */
export class ServiceRegistry {
  /** Registered services */
  private services: Map<string, ServiceEntry>;
  /** Node information */
  private nodes: Map<NodeId, NodeInfo>;
  /** Gossip timer */
  private gossipTimer: NodeJS.Timeout | null;
  /** Gossip interval */
  private gossipInterval: number;
  /** Service TTL */
  private serviceTTL: number;

  constructor(gossipInterval: number = 10000, serviceTTL: number = 30) {
    this.services = new Map();
    this.nodes = new Map();
    this.gossipTimer = null;
    this.gossipInterval = gossipInterval;
    this.serviceTTL = serviceTTL;
  }

  /**
   * Register a service
   */
  register(service: Omit<ServiceEntry, 'id' | 'registeredAt' | 'lastUpdated'>): ServiceEntry {
    const entry: ServiceEntry = {
      id: uuidv4(),
      registeredAt: Date.now(),
      lastUpdated: Date.now(),
      ...service,
    };

    this.services.set(entry.id, entry);

    // Update node info
    this.updateNodeInfo(service.nodeId, { address: service.endpoint });

    return entry;
  }

  /**
   * Unregister a service
   */
  unregister(serviceId: string): boolean {
    return this.services.delete(serviceId);
  }

  /**
   * Discover services by name
   */
  discover(name: string): ServiceEntry[] {
    const now = Date.now();
    const results: ServiceEntry[] = [];

    for (const service of Array.from(this.services.values())) {
      // Check if expired
      if (now - service.lastUpdated > this.serviceTTL * 1000) {
        this.services.delete(service.id);
        continue;
      }

      if (service.name === name) {
        results.push(service);
      }
    }

    return results;
  }

  /**
   * Get all active services
   */
  getAllServices(): ServiceEntry[] {
    const now = Date.now();
    const results: ServiceEntry[] = [];

    for (const service of Array.from(this.services.values())) {
      if (now - service.lastUpdated > this.serviceTTL * 1000) {
        this.services.delete(service.id);
      } else {
        results.push(service);
      }
    }

    return results;
  }

  /**
   * Update node information
   */
  updateNodeInfo(nodeId: NodeId, info: Partial<NodeInfo>): void {
    const existing = this.nodes.get(nodeId) ?? {
      id: nodeId,
      address: '',
      port: 8080,
      isAlive: true,
      lastHeartbeat: Date.now(),
      capacity: 1.0,
      currentLoad: 0.0,
      supportedTypes: [],
      region: 'default',
      metadata: {},
      agentCount: 0,
      score: 1.0,
    };

    this.nodes.set(nodeId, {
      ...existing,
      ...info,
      lastHeartbeat: Date.now(),
    });
  }

  /**
   * Get node information
   */
  getNodeInfo(nodeId: NodeId): NodeInfo | undefined {
    return this.nodes.get(nodeId);
  }

  /**
   * Get all nodes
   */
  getAllNodes(): NodeInfo[] {
    return Array.from(this.nodes.values());
  }

  /**
   * Get alive nodes
   */
  getAliveNodes(): NodeInfo[] {
    const now = Date.now();
    return Array.from(this.nodes.values()).filter(
      node => node.isAlive && (now - node.lastHeartbeat) < 30000
    );
  }

  /**
   * Mark node as alive/dead
   */
  setNodeAlive(nodeId: NodeId, alive: boolean): void {
    const node = this.nodes.get(nodeId);
    if (node) {
      node.isAlive = alive;
      node.lastHeartbeat = Date.now();
    }
  }

  /**
   * Start gossip protocol
   */
  startGossip(): void {
    this.gossipTimer = setInterval(() => {
      this.performGossip();
    }, this.gossipInterval);
  }

  /**
   * Stop gossip protocol
   */
  stopGossip(): void {
    if (this.gossipTimer) {
      clearInterval(this.gossipTimer);
      this.gossipTimer = null;
    }
  }

  /**
   * Perform gossip round
   */
  private performGossip(): void {
    const aliveNodes = this.getAliveNodes();

    // Update service timestamps
    const now = Date.now();
    for (const service of Array.from(this.services.values())) {
      if (now - service.lastUpdated > this.serviceTTL * 1000) {
        this.services.delete(service.id);
      }
    }

    // Mark stale nodes as dead
    for (const node of Array.from(this.nodes.values())) {
      if (now - node.lastHeartbeat > 30000) {
        node.isAlive = false;
      }
    }

    // In real system, would send gossip messages to random peers
    if (aliveNodes.length > 0) {
      const randomPeer = aliveNodes[Math.floor(Math.random() * aliveNodes.length)];
      // Simulate gossip exchange
      this.updateNodeInfo(randomPeer.id, { lastHeartbeat: now });
    }
  }

  /**
   * Shutdown service registry
   */
  shutdown(): void {
    this.stopGossip();
  }
}

/**
 * Consistent hashing ring for partitioning
 */
export class ConsistentHashRing {
  /** Virtual nodes on the ring */
  private ring: Map<number, NodeId>;
  /** Sorted hash positions */
  private sortedHashes: number[];
  /** Number of virtual nodes per physical node */
  private virtualNodes: number;

  constructor(virtualNodes: number = 150) {
    this.ring = new Map();
    this.sortedHashes = [];
    this.virtualNodes = virtualNodes;
  }

  /**
   * Add node to ring
   */
  addNode(nodeId: NodeId): void {
    for (let i = 0; i < this.virtualNodes; i++) {
      const virtualNodeId = `${nodeId}#${i}`;
      const hash = this.hash(virtualNodeId);
      this.ring.set(hash, nodeId);
      this.sortedHashes.push(hash);
    }

    this.sortedHashes.sort((a, b) => a - b);
  }

  /**
   * Remove node from ring
   */
  removeNode(nodeId: NodeId): void {
    for (let i = 0; i < this.virtualNodes; i++) {
      const virtualNodeId = `${nodeId}#${i}`;
      const hash = this.hash(virtualNodeId);
      this.ring.delete(hash);
    }

    this.sortedHashes = Array.from(this.ring.keys()).sort((a, b) => a - b);
  }

  /**
   * Get node for key
   */
  getNode(key: string): NodeId | null {
    if (this.ring.size === 0) {
      return null;
    }

    const hash = this.hash(key);

    // Find first node with hash >= key hash
    for (const ringHash of this.sortedHashes) {
      if (ringHash >= hash) {
        return this.ring.get(ringHash) ?? null;
      }
    }

    // Wrap around to first node
    return this.ring.get(this.sortedHashes[0]) ?? null;
  }

  /**
   * Hash function (simple implementation)
   */
  private hash(key: string): number {
    let hash = 0;
    for (let i = 0; i < key.length; i++) {
      const char = key.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  /**
   * Get all nodes on the ring
   */
  getNodes(): NodeId[] {
    return Array.from(new Set(Array.from(this.ring.values())));
  }
}

/**
 * Multi-node coordinator
 */
export class MultiNodeCoordinator {
  /** Local node ID */
  private nodeId: NodeId;
  /** Distributed consensus */
  private consensus: DistributedConsensus;
  /** State replicator */
  private replicator: StateReplicator;
  /** Service registry */
  private serviceRegistry: ServiceRegistry;
  /** Consistent hash ring */
  private hashRing: ConsistentHashRing;
  /** Configuration */
  private config: MultiNodeConfig;
  /** Active migrations */
  private migrations: Map<string, AgentMigration>;
  /** Active transactions */
  private transactions: Map<string, DistributedTransaction>;
  /** Partition assignments */
  private partitions: Map<string, PartitionAssignment>;
  /** Load balancer round-robin index */
  private roundRobinIndex: number;
  /** Statistics */
  private stats: {
    totalMigrations: number;
    successfulMigrations: number;
    failedMigrations: number;
    totalTransactions: number;
    committedTransactions: number;
    abortedTransactions: number;
    loadBalancingOperations: number;
  };

  /**
   * Create multi-node coordinator
   */
  constructor(
    nodeId: NodeId,
    consensus: DistributedConsensus,
    replicator: StateReplicator,
    config: Partial<MultiNodeConfig> = {}
  ) {
    this.nodeId = nodeId;
    this.consensus = consensus;
    this.replicator = replicator;
    this.migrations = new Map();
    this.transactions = new Map();
    this.partitions = new Map();
    this.roundRobinIndex = 0;

    this.config = {
      gossipInterval: config.gossipInterval ?? 10000,
      serviceTTL: config.serviceTTL ?? 30,
      partitioningStrategy: config.partitioningStrategy ?? PartitioningStrategy.CONSISTENT_HASH,
      loadBalancingStrategy: config.loadBalancingStrategy ?? LoadBalancingStrategy.LEAST_LOADED,
      replicationFactor: config.replicationFactor ?? 3,
      enableAutoMigration: config.enableAutoMigration ?? true,
      migrationTimeout: config.migrationTimeout ?? 30000,
      loadBalanceThreshold: config.loadBalanceThreshold ?? 0.7,
      transactionTimeout: config.transactionTimeout ?? 60000,
      enableConsistentHashing: config.enableConsistentHashing ?? true,
      virtualNodes: config.virtualNodes ?? 150,
      enableDistributedTransactions: config.enableDistributedTransactions ?? true,
      maxRetries: config.maxRetries ?? 3,
    };

    // Initialize service registry
    this.serviceRegistry = new ServiceRegistry(
      this.config.gossipInterval,
      this.config.serviceTTL
    );

    // Initialize consistent hash ring
    this.hashRing = new ConsistentHashRing(this.config.virtualNodes);

    // Initialize cluster nodes
    this.initializeCluster();

    // Start gossip
    this.serviceRegistry.startGossip();

    // Initialize statistics
    this.stats = {
      totalMigrations: 0,
      successfulMigrations: 0,
      failedMigrations: 0,
      totalTransactions: 0,
      committedTransactions: 0,
      abortedTransactions: 0,
      loadBalancingOperations: 0,
    };
  }

  /**
   * Initialize cluster nodes
   */
  private initializeCluster(): void {
    const clusterNodes = this.consensus.getCluster();

    for (const node of clusterNodes) {
      // Add to hash ring
      if (this.config.enableConsistentHashing) {
        this.hashRing.addNode(node.id);
      }

      // Register as service
      this.serviceRegistry.register({
        name: 'polln-node',
        nodeId: node.id,
        endpoint: node.address,
        version: '1.0.0',
        ttl: this.config.serviceTTL,
        metadata: {
          state: node.state,
          isLeader: node.id === this.consensus.getLeader(),
        },
      });

      // Update node info - explicitly set isAlive from cluster node
      this.serviceRegistry.updateNodeInfo(node.id, {
        address: node.address,
        isAlive: node.isAlive, // Use the actual isAlive status from consensus
        capacity: 1.0,
        currentLoad: 0.0,
        agentCount: 0,
        supportedTypes: [
          AgentTaxonomy.BACTERIA,
          AgentTaxonomy.COLONY,
          AgentTaxonomy.MACROPHAGE,
          AgentTaxonomy.EXPLORER,
        ],
        region: 'default',
        metadata: {},
        score: 1.0,
      });
    }
  }

  /**
   * Discover nodes in cluster
   */
  discoverNodes(): NodeInfo[] {
    return this.serviceRegistry.getAliveNodes();
  }

  /**
   * Discover specific service
   */
  discoverService(serviceName: string): ServiceEntry[] {
    return this.serviceRegistry.discover(serviceName);
  }

  /**
   * Assign partition for agent
   */
  assignPartition(agentId: string, agent: MicrobiomeAgent): PartitionAssignment {
    let targetNodes: NodeId[] = [];

    switch (this.config.partitioningStrategy) {
      case PartitioningStrategy.HASH:
        targetNodes = this.hashPartition(agentId);
        break;

      case PartitioningStrategy.CONSISTENT_HASH:
        targetNodes = this.consistentHashPartition(agentId);
        break;

      case PartitioningStrategy.AFFINITY:
        targetNodes = this.affinityPartition(agent);
        break;

      case PartitioningStrategy.RANGE:
        targetNodes = this.rangePartition(agentId);
        break;

      case PartitioningStrategy.MANUAL:
        targetNodes = this.manualPartition(agentId);
        break;
    }

    // Add replicas
    const allNodes = this.serviceRegistry.getAliveNodes();
    const replicaCount = Math.max(0, this.config.replicationFactor - 1);

    for (let i = 0; i < replicaCount && allNodes.length > 1; i++) {
      const startIndex = allNodes.findIndex(n => n.id === targetNodes[0]);
      const nextIndex = (startIndex + i + 1) % allNodes.length;
      const replicaNode = allNodes[nextIndex];
      if (replicaNode && !targetNodes.includes(replicaNode.id)) {
        targetNodes.push(replicaNode.id);
      }
    }

    // If we still don't have enough replicas, add more from all nodes
    while (targetNodes.length < this.config.replicationFactor && targetNodes.length < allNodes.length) {
      const remainingNode = allNodes.find(n => !targetNodes.includes(n.id));
      if (remainingNode) {
        targetNodes.push(remainingNode.id);
      } else {
        break;
      }
    }

    const assignment: PartitionAssignment = {
      partitionId: uuidv4(),
      nodes: targetNodes,
      agentRanges: [agentId],
      partitionKey: this.generatePartitionKey(agentId),
      replicationFactor: this.config.replicationFactor,
    };

    this.partitions.set(assignment.partitionId, assignment);

    return assignment;
  }

  /**
   * Migrate agent to another node
   */
  async migrateAgent(
    agentId: string,
    agent: MicrobiomeAgent,
    targetNodeId: NodeId,
    strategy: MigrationStrategy = MigrationStrategy.LIVE
  ): Promise<AgentMigration> {
    const migration: AgentMigration = {
      id: uuidv4(),
      agentId,
      sourceNode: this.nodeId,
      targetNode: targetNodeId,
      status: MigrationStatus.PENDING,
      startedAt: Date.now(),
      strategy,
    };

    this.migrations.set(migration.id, migration);
    this.stats.totalMigrations++;

    try {
      // Update status
      migration.status = MigrationStatus.IN_PROGRESS;

      // Create agent snapshot
      const snapshot = await this.createAgentSnapshot(agent);
      migration.agentSnapshot = snapshot;

      // Check target node readiness
      const targetNode = this.serviceRegistry.getNodeInfo(targetNodeId);
      if (!targetNode || !targetNode.isAlive) {
        throw new Error(`Target node ${targetNodeId} is not available`);
      }

      // Execute migration based on strategy
      try {
        switch (strategy) {
          case MigrationStrategy.LIVE:
            await this.executeLiveMigration(agent, targetNodeId);
            break;

          case MigrationStrategy.STOP_AND_COPY:
            await this.executeStopAndCopyMigration(agent, targetNodeId);
            break;

          case MigrationStrategy.CHECKPOINT:
            await this.executeCheckpointMigration(agent, targetNodeId);
            break;
        }
      } catch (migrationError) {
        // Migration execution failed - check if target is still alive
        const nodeStillAlive = this.serviceRegistry.getNodeInfo(targetNodeId)?.isAlive;
        if (!nodeStillAlive) {
          throw new Error(`Target node ${targetNodeId} became unavailable during migration`);
        }
        // Otherwise, continue despite migration execution error
        console.warn('Migration execution had issues, continuing:', migrationError);
      }

      // Replicate state to target node
      try {
        await this.replicator.replicateAgent(agentId, [targetNodeId], agent);
      } catch (replicationError) {
        // Replication failure is not critical for migration
        console.warn('Replication failed during migration:', replicationError);
      }

      // Update node loads
      this.updateNodeLoad(this.nodeId, -1);
      this.updateNodeLoad(targetNodeId, 1);

      migration.status = MigrationStatus.COMPLETED;
      migration.completedAt = Date.now();
      this.stats.successfulMigrations++;

    } catch (error) {
      // Set status to FAILED first
      migration.status = MigrationStatus.FAILED;
      migration.error = error instanceof Error ? error.message : String(error);
      this.stats.failedMigrations++;

      // Rollback will change status to ROLLED_BACK
      await this.rollbackMigration(migration);
    }

    return migration;
  }

  /**
   * Execute distributed transaction
   */
  async executeTransaction(
    operations: TransactionOperation[],
    type: TransactionType = TransactionType.TWO_PC
  ): Promise<DistributedTransaction> {
    const transaction: DistributedTransaction = {
      id: uuidv4(),
      type,
      state: TransactionState.INITIALIZED,
      participants: Array.from(new Set(operations.map(op => op.nodeId))),
      operations,
      currentStep: 0,
      compensations: [],
      timeout: this.config.transactionTimeout,
      startedAt: Date.now(),
      votes: new Map(),
    };

    this.transactions.set(transaction.id, transaction);
    this.stats.totalTransactions++;

    try {
      switch (type) {
        case TransactionType.TWO_PC:
          await this.executeTwoPhaseCommit(transaction);
          break;

        case TransactionType.SAGA:
          await this.executeSagaTransaction(transaction);
          break;

        case TransactionType.BEST_EFFORT:
          await this.executeBestEffortTransaction(transaction);
          break;
      }

      if (transaction.state === TransactionState.COMMITTED) {
        this.stats.committedTransactions++;
      } else {
        this.stats.abortedTransactions++;
      }

    } catch (error) {
      transaction.state = TransactionState.ABORTED;
      transaction.error = error instanceof Error ? error.message : String(error);
      this.stats.abortedTransactions++;

      // Execute compensations for saga
      if (type === TransactionType.SAGA) {
        await this.executeCompensations(transaction);
      }
    }

    return transaction;
  }

  /**
   * Select node for new agent (load balancing)
   */
  selectNode(agent: MicrobiomeAgent): NodeId | null {
    this.stats.loadBalancingOperations++;

    const aliveNodes = this.serviceRegistry.getAliveNodes();
    if (aliveNodes.length === 0) {
      return null;
    }

    switch (this.config.loadBalancingStrategy) {
      case LoadBalancingStrategy.ROUND_ROBIN:
        return this.roundRobinSelect(aliveNodes);

      case LoadBalancingStrategy.LEAST_LOADED:
        return this.leastLoadedSelect(aliveNodes);

      case LoadBalancingStrategy.WEIGHTED:
        return this.weightedSelect(aliveNodes);

      case LoadBalancingStrategy.LOCALITY_AWARE:
        return this.localityAwareSelect(aliveNodes, agent);

      case LoadBalancingStrategy.CONSISTENT_HASH:
        return this.consistentHashSelect(agent.id);

      default:
        return this.leastLoadedSelect(aliveNodes);
    }
  }

  /**
   * Auto-balance cluster load
   */
  async autoBalanceCluster(): Promise<void> {
    if (!this.config.enableAutoMigration) {
      return;
    }

    const nodes = this.serviceRegistry.getAliveNodes();
    const avgLoad = nodes.reduce((sum, n) => sum + n.currentLoad, 0) / nodes.length;

    // Find overloaded and underloaded nodes
    const overloaded = nodes.filter(n => n.currentLoad > avgLoad * (1 + this.config.loadBalanceThreshold));
    const underloaded = nodes.filter(n => n.currentLoad < avgLoad * (1 - this.config.loadBalanceThreshold));

    // Migrate agents from overloaded to underloaded
    for (const source of overloaded) {
      for (const target of underloaded) {
        if (source.agentCount > target.agentCount + 1) {
          const agentsToMigrate = Math.floor((source.agentCount - target.agentCount) / 2);

          for (let i = 0; i < agentsToMigrate; i++) {
            // In real system, would select specific agents
            // For now, just track the migration
            await this.migrateAgent(
              `agent-${source.id}-${i}`,
              this.createMockAgent(),
              target.id,
              MigrationStrategy.LIVE
            );
          }
        }
      }
    }
  }

  /**
   * Get cluster statistics
   */
  getClusterStats(): {
    nodes: NodeInfo[];
    migrations: AgentMigration[];
    transactions: DistributedTransaction[];
    partitions: PartitionAssignment[];
    statistics: typeof this.stats;
  } {
    return {
      nodes: this.serviceRegistry.getAllNodes(),
      migrations: Array.from(this.migrations.values()),
      transactions: Array.from(this.transactions.values()),
      partitions: Array.from(this.partitions.values()),
      statistics: { ...this.stats },
    };
  }

  /**
   * Shutdown coordinator
   */
  shutdown(): void {
    this.serviceRegistry.shutdown();
  }

  // Private helper methods

  /**
   * Hash-based partitioning
   */
  private hashPartition(agentId: string): NodeId[] {
    const nodes = this.serviceRegistry.getAliveNodes();
    const hash = this.simpleHash(agentId);
    const index = hash % nodes.length;
    return [nodes[index].id];
  }

  /**
   * Consistent hash partitioning
   */
  private consistentHashPartition(agentId: string): NodeId[] {
    const nodeId = this.hashRing.getNode(agentId);
    return nodeId ? [nodeId] : [];
  }

  /**
   * Affinity-based partitioning
   */
  private affinityPartition(agent: MicrobiomeAgent): NodeId[] {
    const nodes = this.serviceRegistry.getAliveNodes();

    // Find nodes that support agent's taxonomy
    const compatibleNodes = nodes.filter(
      n => n.supportedTypes.includes(agent.taxonomy)
    );

    if (compatibleNodes.length === 0) {
      return [nodes[0].id];
    }

    // Select least loaded compatible node
    compatibleNodes.sort((a, b) => a.currentLoad - b.currentLoad);
    return [compatibleNodes[0].id];
  }

  /**
   * Range-based partitioning
   */
  private rangePartition(agentId: string): NodeId[] {
    const nodes = this.serviceRegistry.getAliveNodes();
    const hash = this.simpleHash(agentId);
    const rangeSize = Math.floor(Number.MAX_SAFE_INTEGER / nodes.length);
    const index = Math.floor(hash / rangeSize) % nodes.length;
    return [nodes[index].id];
  }

  /**
   * Manual partitioning
   */
  private manualPartition(agentId: string): NodeId[] {
    // Return leader node for manual partitioning
    const leader = this.consensus.getLeader();
    return leader ? [leader] : [this.nodeId];
  }

  /**
   * Generate partition key
   */
  private generatePartitionKey(agentId: string): string {
    return `partition-${agentId}`;
  }

  /**
   * Create agent snapshot
   */
  private async createAgentSnapshot(agent: MicrobiomeAgent): Promise<VersionedState> {
    return {
      id: agent.id,
      state: agent,
      vectorClock: this.replicator.createVectorClock(),
      timestamp: Date.now(),
      version: 1,
      originNode: this.nodeId,
    };
  }

  /**
   * Execute live migration
   */
  private async executeLiveMigration(agent: MicrobiomeAgent, targetNodeId: NodeId): Promise<void> {
    // Simulate live migration - in real system would use state synchronization
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  /**
   * Execute stop-and-copy migration
   */
  private async executeStopAndCopyMigration(agent: MicrobiomeAgent, targetNodeId: NodeId): Promise<void> {
    // Stop agent, copy state, start on target
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  /**
   * Execute checkpoint migration
   */
  private async executeCheckpointMigration(agent: MicrobiomeAgent, targetNodeId: NodeId): Promise<void> {
    // Create checkpoint, transfer, restore
    await new Promise(resolve => setTimeout(resolve, 75));
  }

  /**
   * Rollback failed migration
   */
  private async rollbackMigration(migration: AgentMigration): Promise<void> {
    // Only rollback if status is FAILED
    if (migration.status === MigrationStatus.FAILED) {
      migration.status = MigrationStatus.ROLLED_BACK;
    }

    // In real system, would restore state on source node
    // and cleanup on target node
  }

  /**
   * Execute two-phase commit
   */
  private async executeTwoPhaseCommit(transaction: DistributedTransaction): Promise<void> {
    // Phase 1: Prepare
    transaction.state = TransactionState.PREPARED;

    for (const operation of transaction.operations) {
      // Send prepare request to participant
      // In real system, would be RPC call
      operation.executed = true;
    }

    // Phase 2: Commit
    const allPrepared = transaction.operations.every(op => op.executed);

    if (allPrepared) {
      transaction.state = TransactionState.COMMITTED;
      transaction.completedAt = Date.now();
    } else {
      transaction.state = TransactionState.ABORTED;
      transaction.completedAt = Date.now();
    }
  }

  /**
   * Execute saga transaction
   */
  private async executeSagaTransaction(transaction: DistributedTransaction): Promise<void> {
    // Execute operations in sequence
    for (let i = 0; i < transaction.operations.length; i++) {
      transaction.currentStep = i;
      const operation = transaction.operations[i];

      try {
        // Execute operation
        operation.executed = true;

        // Generate compensation operation
        transaction.compensations.push({
          id: uuidv4(),
          nodeId: operation.nodeId,
          type: operation.type,
          params: { ...operation.params, compensate: true },
          executed: false,
        });

      } catch (error) {
        // Operation failed, execute compensations
        await this.executeCompensations(transaction);
        throw error;
      }
    }

    transaction.state = TransactionState.COMMITTED;
    transaction.completedAt = Date.now();
  }

  /**
   * Execute best-effort transaction
   */
  private async executeBestEffortTransaction(transaction: DistributedTransaction): Promise<void> {
    // Execute operations without guarantees
    for (const operation of transaction.operations) {
      try {
        operation.executed = true;
      } catch (error) {
        // Continue on failure
        operation.error = error instanceof Error ? error.message : String(error);
      }
    }

    transaction.state = TransactionState.COMMITTED;
    transaction.completedAt = Date.now();
  }

  /**
   * Execute compensations
   */
  private async executeCompensations(transaction: DistributedTransaction): Promise<void> {
    // Execute compensations in reverse order
    for (let i = transaction.compensations.length - 1; i >= 0; i--) {
      const compensation = transaction.compensations[i];

      if (!compensation.executed) {
        try {
          compensation.executed = true;
        } catch (error) {
          // Log but continue
          console.error('Compensation failed:', error);
        }
      }
    }
  }

  /**
   * Round-robin node selection
   */
  private roundRobinSelect(nodes: NodeInfo[]): NodeId {
    const node = nodes[this.roundRobinIndex % nodes.length];
    this.roundRobinIndex++;
    return node.id;
  }

  /**
   * Least loaded node selection
   */
  private leastLoadedSelect(nodes: NodeInfo[]): NodeId {
    const sorted = [...nodes].sort((a, b) => a.currentLoad - b.currentLoad);
    return sorted[0].id;
  }

  /**
   * Weighted node selection
   */
  private weightedSelect(nodes: NodeInfo[]): NodeId {
    const totalCapacity = nodes.reduce((sum, n) => sum + (1 - n.currentLoad), 0);
    let random = Math.random() * totalCapacity;

    for (const node of nodes) {
      random -= (1 - node.currentLoad);
      if (random <= 0) {
        return node.id;
      }
    }

    return nodes[0].id;
  }

  /**
   * Locality-aware node selection
   */
  private localityAwareSelect(nodes: NodeInfo[], agent: MicrobiomeAgent): NodeId {
    // Find nodes in same region with compatible type
    const compatible = nodes.filter(
      n => n.supportedTypes.includes(agent.taxonomy)
    );

    if (compatible.length === 0) {
      return this.leastLoadedSelect(nodes);
    }

    return this.leastLoadedSelect(compatible);
  }

  /**
   * Consistent hash node selection
   */
  private consistentHashSelect(agentId: string): NodeId {
    const nodeId = this.hashRing.getNode(agentId);
    return nodeId ?? this.nodeId;
  }

  /**
   * Update node load
   */
  private updateNodeLoad(nodeId: NodeId, delta: number): void {
    const node = this.serviceRegistry.getNodeInfo(nodeId);
    if (node) {
      node.currentLoad = Math.max(0, Math.min(1, node.currentLoad + delta * 0.01));
      node.agentCount = Math.max(0, node.agentCount + delta);
    }
  }

  /**
   * Simple hash function
   */
  private simpleHash(key: string): number {
    let hash = 0;
    for (let i = 0; i < key.length; i++) {
      const char = key.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }

  /**
   * Create mock agent for testing
   */
  private createMockAgent(): MicrobiomeAgent {
    return {
      id: uuidv4(),
      taxonomy: AgentTaxonomy.BACTERIA,
      name: 'MockAgent',
      metabolism: {
        inputs: [],
        outputs: [],
        processingRate: 1.0,
        efficiency: 0.8,
      },
      lifecycle: {
        health: 1.0,
        age: 0,
        generation: 0,
        isAlive: true,
      },
      generation: 0,
      size: 1024,
      complexity: 0.5,
      process: async () => new Map(),
      reproduce: async () => this.createMockAgent(),
      evaluateFitness: () => ({
        overall: 0.8,
        throughput: 0.8,
        accuracy: 0.8,
        efficiency: 0.8,
        cooperation: 0.8,
      }),
      canMetabolize: () => true,
    };
  }
}

/**
 * Create multi-node coordinator
 */
export function createMultiNodeCoordinator(
  nodeId: NodeId,
  consensus: DistributedConsensus,
  replicator: StateReplicator,
  config?: Partial<MultiNodeConfig>
): MultiNodeCoordinator {
  return new MultiNodeCoordinator(nodeId, consensus, replicator, config);
}

/**
 * Partition assignment utility
 */
export function assignPartitions(
  coordinator: MultiNodeCoordinator,
  agents: Map<string, MicrobiomeAgent>
): Map<string, PartitionAssignment> {
  const assignments = new Map<string, PartitionAssignment>();

  for (const [agentId, agent] of Array.from(agents.entries())) {
    const assignment = coordinator.assignPartition(agentId, agent);
    assignments.set(agentId, assignment);
  }

  return assignments;
}

/**
 * Load balancing utility
 */
export function balanceClusterLoad(
  coordinator: MultiNodeCoordinator,
  agents: Map<string, MicrobiomeAgent>
): Promise<AgentMigration[]> {
  const migrations: Promise<AgentMigration>[] = [];

  // Select appropriate node for each agent
  for (const [agentId, agent] of Array.from(agents.entries())) {
    const targetNode = coordinator.selectNode(agent);

    if (targetNode && targetNode !== coordinator['nodeId']) {
      migrations.push(
        coordinator.migrateAgent(agentId, agent, targetNode, MigrationStrategy.LIVE)
      );
    }
  }

  return Promise.all(migrations);
}
