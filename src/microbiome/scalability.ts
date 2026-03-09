/**
 * POLLN Microbiome - Scalability Management System
 *
 * Phase 5: Production Optimization - Milestone 3
 * Comprehensive scalability system supporting 100K+ agents through
 * population partitioning, distributed evolution, load balancing,
 * horizontal scaling, and federation coordination.
 *
 * @module microbiome/scalability
 */

import { PerformanceMonitor } from './performance.js';
import { PerformanceOptimizer } from './optimization.js';
import {
  MicrobiomeAgent,
  FitnessScore,
  EcosystemSnapshot,
  ColonyStructure,
  AgentTaxonomy,
} from './types.js';

/**
 * Partitioning strategy for large populations
 */
export enum PartitioningStrategy {
  /** Hash-based partitioning (consistent hashing) */
  HASH_BASED = 'hash_based',
  /** Range-based partitioning */
  RANGE_BASED = 'range_based',
  /** Geographic partitioning */
  GEOGRAPHIC = 'geographic',
  /** Hierarchical partitioning */
  HIERARCHICAL = 'hierarchical',
}

/**
 * Load balancing strategy
 */
export enum LoadBalancingStrategy {
  /** Round-robin distribution */
  ROUND_ROBIN = 'round_robin',
  /** Least loaded first */
  LEAST_LOADED = 'least_loaded',
  /** Weighted by node capacity */
  WEIGHTED = 'weighted',
  /** Consistent hashing */
  CONSISTENT_HASH = 'consistent_hash',
}

/**
 * Auto-scaling trigger type
 */
export enum AutoScalingTrigger {
  /** CPU usage threshold */
  CPU_THRESHOLD = 'cpu_threshold',
  /** Memory usage threshold */
  MEMORY_THRESHOLD = 'memory_threshold',
  /** Queue depth threshold */
  QUEUE_DEPTH = 'queue_depth',
  /** Response time threshold */
  RESPONSE_TIME = 'response_time',
  /** Custom trigger */
  CUSTOM = 'custom',
}

/**
 * Node information in distributed system
 */
export interface NodeInfo {
  /** Unique node identifier */
  id: string;
  /** Node address/host */
  host: string;
  /** Node port */
  port: number;
  /** CPU capacity (0-1) */
  cpuCapacity: number;
  /** Memory capacity (bytes) */
  memoryCapacity: number;
  /** Current CPU usage (0-1) */
  cpuUsage: number;
  /** Current memory usage (bytes) */
  memoryUsage: number;
  /** Number of agents assigned */
  agentCount: number;
  /** Node is healthy */
  isHealthy: boolean;
  /** Last heartbeat timestamp */
  lastHeartbeat: number;
}

/**
 * Partition assignment
 */
export interface PartitionAssignment {
  /** Partition ID */
  partitionId: string;
  /** Assigned node ID */
  nodeId: string;
  /** Agent IDs in partition */
  agentIds: string[];
  /** Partition size (agent count) */
  size: number;
  /** Partition load (0-1) */
  load: number;
  /** Assignment timestamp */
  assignedAt: number;
}

/**
 * Evolution task for distributed processing
 */
export interface EvolutionTask {
  /** Task ID */
  id: string;
  /** Agent IDs to evaluate */
  agentIds: string[];
  /** Partition ID */
  partitionId: string;
  /** Task status */
  status: 'pending' | 'processing' | 'completed' | 'failed';
  /** Assigned node ID */
  assignedNode: string;
  /** Task creation timestamp */
  createdAt: number;
  /** Task start timestamp */
  startedAt?: number;
  /** Task completion timestamp */
  completedAt?: number;
  /** Fitness results */
  results?: Map<string, FitnessScore>;
  /** Error message if failed */
  error?: string;
}

/**
 * Map-reduce style evolution result
 */
export interface MapReduceResult {
  /** Map phase results (by partition) */
  mapResults: Map<string, Map<string, FitnessScore>>;
  /** Reduce phase result (aggregated fitness) */
  reduceResult: Map<string, FitnessScore>;
  /** Total map time */
  mapTime: number;
  /** Total reduce time */
  reduceTime: number;
  /** Total shuffle time */
  shuffleTime: number;
  /** Number of partitions processed */
  partitionsProcessed: number;
  /** Number of agents evaluated */
  agentsEvaluated: number;
}

/**
 * Auto-scaling policy
 */
export interface AutoScalingPolicy {
  /** Policy ID */
  id: string;
  /** Trigger type */
  trigger: AutoScalingTrigger;
  /** Trigger threshold value */
  threshold: number;
  /** Scale up percentage */
  scaleUpPercent: number;
  /** Scale down percentage */
  scaleDownPercent: number;
  /** Minimum instances */
  minInstances: number;
  /** Maximum instances */
  maxInstances: number;
  /** Cooldown period (ms) */
  cooldownPeriod: number;
  /** Last scale action timestamp */
  lastScaleAction: number;
  /** Policy is enabled */
  enabled: boolean;
}

/**
 * Federation configuration for multi-ecosystem coordination
 */
export interface FederationConfig {
  /** Federation ID */
  id: string;
  /** Member ecosystem IDs */
  members: string[];
  /** Federation coordinator ID */
  coordinator: string;
  /** Sync interval (ms) */
  syncInterval: number;
  /** Data sharing policy */
  dataSharingPolicy: 'full' | 'partial' | 'minimal';
  /** Conflict resolution strategy */
  conflictResolution: 'timestamp' | 'coordinator' | 'voting';
}

/**
 * Scalability statistics
 */
export interface ScalabilityStats {
  /** Total population size */
  totalPopulation: number;
  /** Number of partitions */
  partitionCount: number;
  /** Number of active nodes */
  activeNodes: number;
  /** Average load per node (0-1) */
  avgNodeLoad: number;
  /** Maximum load across nodes (0-1) */
  maxNodeLoad: number;
  /** Load balance score (0-1, higher is better) */
  loadBalanceScore: number;
  /** Evolution throughput (agents/sec) */
  evolutionThroughput: number;
  /** Average evolution latency (ms) */
  avgEvolutionLatency: number;
  /** Scaling events count */
  scalingEvents: number;
  /** Federation syncs completed */
  federationSyncs: number;
}

/**
 * Scalability configuration
 */
export interface ScalabilityConfig {
  /** Target partition size (agents per partition) */
  targetPartitionSize?: number;
  /** Partitioning strategy */
  partitioningStrategy?: PartitioningStrategy;
  /** Load balancing strategy */
  loadBalancingStrategy?: LoadBalancingStrategy;
  /** Enable auto-scaling */
  enableAutoScaling?: boolean;
  /** Auto-scaling policies */
  autoScalingPolicies?: AutoScalingPolicy[];
  /** Enable federation */
  enableFederation?: boolean;
  /** Federation configs */
  federationConfigs?: FederationConfig[];
  /** Maximum evolution tasks per node */
  maxTasksPerNode?: number;
  /** Evolution timeout (ms) */
  evolutionTimeout?: number;
  /** Heartbeat interval (ms) */
  heartbeatInterval?: number;
  /** Node failure threshold (missed heartbeats) */
  nodeFailureThreshold?: number;
}

/**
 * Scalability manager - handles large-scale distributed evolution
 */
export class ScalabilityManager {
  /** Performance monitor */
  private monitor: PerformanceMonitor;
  /** Performance optimizer */
  private optimizer: PerformanceOptimizer;
  /** Configuration */
  private config: Required<ScalabilityConfig>;
  /** Registered nodes */
  private nodes: Map<string, NodeInfo>;
  /** Partition assignments */
  private partitions: Map<string, PartitionAssignment>;
  /** Active evolution tasks */
  private evolutionTasks: Map<string, EvolutionTask>;
  /** Auto-scaling policies */
  private scalingPolicies: AutoScalingPolicy[];
  /** Federation configurations */
  private federations: Map<string, FederationConfig>;
  /** Statistics */
  private stats: ScalabilityStats;
  /** Heartbeat timer */
  private heartbeatTimer: NodeJS.Timeout | null;
  /** Auto-scaling timer */
  private scalingTimer: NodeJS.Timeout | null;
  /** Federation sync timer */
  private federationTimer: NodeJS.Timeout | null;

  constructor(
    monitor: PerformanceMonitor,
    optimizer: PerformanceOptimizer,
    config: ScalabilityConfig = {}
  ) {
    this.monitor = monitor;
    this.optimizer = optimizer;
    this.nodes = new Map();
    this.partitions = new Map();
    this.evolutionTasks = new Map();
    this.federations = new Map();
    this.config = {
      targetPartitionSize: config.targetPartitionSize ?? 1000,
      partitioningStrategy: config.partitioningStrategy ?? PartitioningStrategy.HASH_BASED,
      loadBalancingStrategy: config.loadBalancingStrategy ?? LoadBalancingStrategy.LEAST_LOADED,
      enableAutoScaling: config.enableAutoScaling ?? true,
      autoScalingPolicies: config.autoScalingPolicies ?? this.createDefaultPolicies(),
      enableFederation: config.enableFederation ?? false,
      federationConfigs: config.federationConfigs ?? [],
      maxTasksPerNode: config.maxTasksPerNode ?? 10,
      evolutionTimeout: config.evolutionTimeout ?? 30000,
      heartbeatInterval: config.heartbeatInterval ?? 5000,
      nodeFailureThreshold: config.nodeFailureThreshold ?? 3,
    };
    this.scalingPolicies = this.config.autoScalingPolicies;
    this.stats = this.createEmptyStats();

    // Start background tasks
    this.startBackgroundTasks();
  }

  /**
   * Register a node in the distributed system
   */
  registerNode(node: NodeInfo): void {
    this.nodes.set(node.id, {
      ...node,
      lastHeartbeat: Date.now(),
      isHealthy: true,
    });

    this.updateStats();
  }

  /**
   * Unregister a node
   */
  unregisterNode(nodeId: string): void {
    const node = this.nodes.get(nodeId);
    if (node) {
      // Reassign partitions from this node
      this.reassignPartitions(nodeId);
      this.nodes.delete(nodeId);
      this.updateStats();
    }
  }

  /**
   * Update node heartbeat
   */
  updateHeartbeat(nodeId: string): void {
    const node = this.nodes.get(nodeId);
    if (node) {
      node.lastHeartbeat = Date.now();
      node.isHealthy = true;
    }
  }

  /**
   * Partition population for distributed processing
   */
  partitionPopulation(agentIds: string[]): Map<string, PartitionAssignment> {
    const startTime = Date.now();
    const partitionAssignments = new Map<string, PartitionAssignment>();
    const targetSize = this.config.targetPartitionSize;
    const strategy = this.config.partitioningStrategy;

    // Calculate number of partitions needed
    const numPartitions = Math.ceil(agentIds.length / targetSize);

    // Partition based on strategy
    switch (strategy) {
      case PartitioningStrategy.HASH_BASED:
        this.hashBasedPartitioning(agentIds, numPartitions, partitionAssignments);
        break;

      case PartitioningStrategy.RANGE_BASED:
        this.rangeBasedPartitioning(agentIds, numPartitions, partitionAssignments);
        break;

      case PartitioningStrategy.HIERARCHICAL:
        this.hierarchicalPartitioning(agentIds, numPartitions, partitionAssignments);
        break;

      default:
        this.hashBasedPartitioning(agentIds, numPartitions, partitionAssignments);
    }

    // Assign partitions to available nodes
    this.assignPartitionsToNodes(partitionAssignments);

    // Store partition assignments
    this.partitions = partitionAssignments;

    const duration = Date.now() - startTime;
    this.monitor.recordOperation('partition_population', duration);

    return partitionAssignments;
  }

  /**
   * Execute distributed evolution using map-reduce pattern
   */
  async executeDistributedEvolution(
    agents: Map<string, MicrobiomeAgent>,
    snapshot: EcosystemSnapshot,
    fitnessFn: (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot) => Promise<FitnessScore>
  ): Promise<MapReduceResult> {
    const startTime = Date.now();
    const agentIds = Array.from(agents.keys());

    // Partition population
    const partitions = this.partitionPopulation(agentIds);

    // Create evolution tasks
    const tasks = this.createEvolutionTasks(partitions, agents);

    // Map phase: evaluate fitness in parallel across nodes
    const mapResult = await this.executeMapPhase(tasks, snapshot, fitnessFn);

    // Shuffle phase: redistribute data by agent ID
    const shuffleTime = await this.executeShufflePhase(mapResult);

    // Reduce phase: aggregate results
    const reduceResult = await this.executeReducePhase(mapResult);

    const duration = Date.now() - startTime;

    // Update stats
    this.stats.evolutionThroughput = agents.size / (duration / 1000);
    this.stats.avgEvolutionLatency = duration / agents.size;

    return {
      mapResults: mapResult,
      reduceResult: reduceResult,
      mapTime: duration - shuffleTime,
      reduceTime: 0, // Calculated in executeReducePhase
      shuffleTime: shuffleTime,
      partitionsProcessed: partitions.size,
      agentsEvaluated: agents.size,
    };
  }

  /**
   * Balance load across nodes
   */
  balanceLoad(): void {
    const startTime = Date.now();
    const strategy = this.config.loadBalancingStrategy;

    switch (strategy) {
      case LoadBalancingStrategy.LEAST_LOADED:
        this.leastLoadedBalancing();
        break;

      case LoadBalancingStrategy.WEIGHTED:
        this.weightedBalancing();
        break;

      case LoadBalancingStrategy.CONSISTENT_HASH:
        this.consistentHashBalancing();
        break;

      case LoadBalancingStrategy.ROUND_ROBIN:
      default:
        this.roundRobinBalancing();
    }

    this.updateStats();

    const duration = Date.now() - startTime;
    this.monitor.recordOperation('load_balancing', duration);
  }

  /**
   * Check and execute auto-scaling
   */
  async executeAutoScaling(): Promise<void> {
    if (!this.config.enableAutoScaling) {
      return;
    }

    const now = Date.now();
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);

    for (const policy of this.scalingPolicies) {
      if (!policy.enabled) continue;

      // Check cooldown
      if (now - policy.lastScaleAction < policy.cooldownPeriod) {
        continue;
      }

      // Check trigger
      const shouldScale = await this.checkScalingTrigger(policy, activeNodes);

      if (shouldScale.scaleUp) {
        await this.scaleUp(policy);
        policy.lastScaleAction = now;
        this.stats.scalingEvents++;
      } else if (shouldScale.scaleDown) {
        await this.scaleDown(policy);
        policy.lastScaleAction = now;
        this.stats.scalingEvents++;
      }
    }
  }

  /**
   * Add federation configuration
   */
  addFederation(config: FederationConfig): void {
    this.federations.set(config.id, config);
  }

  /**
   * Remove federation
   */
  removeFederation(federationId: string): void {
    this.federations.delete(federationId);
  }

  /**
   * Sync with federation members
   */
  async syncFederation(federationId: string): Promise<void> {
    const federation = this.federations.get(federationId);
    if (!federation) {
      throw new Error(`Federation ${federationId} not found`);
    }

    const startTime = Date.now();

    // Sync with each member
    for (const memberId of federation.members) {
      await this.syncWithMember(memberId, federation);
    }

    const duration = Date.now() - startTime;
    this.monitor.recordOperation('federation_sync', duration);
    this.stats.federationSyncs++;
  }

  /**
   * Get scalability statistics
   */
  getStats(): ScalabilityStats {
    return { ...this.stats };
  }

  /**
   * Get all nodes
   */
  getNodes(): NodeInfo[] {
    return Array.from(this.nodes.values());
  }

  /**
   * Get node by ID
   */
  getNode(nodeId: string): NodeInfo | undefined {
    return this.nodes.get(nodeId);
  }

  /**
   * Get all partitions
   */
  getPartitions(): PartitionAssignment[] {
    return Array.from(this.partitions.values());
  }

  /**
   * Get evolution tasks
   */
  getEvolutionTasks(): EvolutionTask[] {
    return Array.from(this.evolutionTasks.values());
  }

  /**
   * Get active scaling policies
   */
  getScalingPolicies(): AutoScalingPolicy[] {
    return [...this.scalingPolicies];
  }

  /**
   * Update scaling policy
   */
  updateScalingPolicy(policyId: string, updates: Partial<AutoScalingPolicy>): void {
    const policy = this.scalingPolicies.find(p => p.id === policyId);
    if (policy) {
      Object.assign(policy, updates);
    }
  }

  /**
   * Estimate maximum population size supported
   */
  estimateMaxPopulation(): number {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
    if (activeNodes.length === 0) {
      return 0;
    }

    // Calculate based on node capacity and partition size
    const avgMemoryCapacity = activeNodes.reduce((sum, n) => sum + n.memoryCapacity, 0) / activeNodes.length;
    const avgAgentSize = 1024; // 1KB average agent size
    const agentsPerNode = Math.floor(avgMemoryCapacity / avgAgentSize);
    const maxPopulation = agentsPerNode * activeNodes.length;

    // Apply safety factor (use only 80% of capacity)
    return Math.floor(maxPopulation * 0.8);
  }

  /**
   * Destroy manager and cleanup resources
   */
  destroy(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    if (this.scalingTimer) {
      clearInterval(this.scalingTimer);
      this.scalingTimer = null;
    }
    if (this.federationTimer) {
      clearInterval(this.federationTimer);
      this.federationTimer = null;
    }

    this.nodes.clear();
    this.partitions.clear();
    this.evolutionTasks.clear();
    this.federations.clear();
  }

  /**
   * Hash-based partitioning
   */
  private hashBasedPartitioning(
    agentIds: string[],
    numPartitions: number,
    assignments: Map<string, PartitionAssignment>
  ): void {
    for (const agentId of agentIds) {
      // Simple hash function
      let hash = 0;
      for (let i = 0; i < agentId.length; i++) {
        hash = ((hash << 5) - hash) + agentId.charCodeAt(i);
        hash = hash & hash; // Convert to 32-bit integer
      }

      const partitionId = `partition_${Math.abs(hash) % numPartitions}`;

      if (!assignments.has(partitionId)) {
        assignments.set(partitionId, {
          partitionId,
          nodeId: '',
          agentIds: [],
          size: 0,
          load: 0,
          assignedAt: Date.now(),
        });
      }

      const assignment = assignments.get(partitionId)!;
      assignment.agentIds.push(agentId);
      assignment.size++;
    }
  }

  /**
   * Range-based partitioning
   */
  private rangeBasedPartitioning(
    agentIds: string[],
    numPartitions: number,
    assignments: Map<string, PartitionAssignment>
  ): void {
    // Sort agent IDs
    const sortedIds = [...agentIds].sort();
    const partitionSize = Math.ceil(sortedIds.length / numPartitions);

    for (let i = 0; i < numPartitions; i++) {
      const start = i * partitionSize;
      const end = Math.min(start + partitionSize, sortedIds.length);
      const partitionAgentIds = sortedIds.slice(start, end);

      const partitionId = `partition_${i}`;
      assignments.set(partitionId, {
        partitionId,
        nodeId: '',
        agentIds: partitionAgentIds,
        size: partitionAgentIds.length,
        load: 0,
        assignedAt: Date.now(),
      });
    }
  }

  /**
   * Hierarchical partitioning
   */
  private hierarchicalPartitioning(
    agentIds: string[],
    numPartitions: number,
    assignments: Map<string, PartitionAssignment>
  ): void {
    // First level: partition by agent type (taxonomy)
    const byType: Map<string, string[]> = new Map();

    for (const agentId of agentIds) {
      // Extract type from agent ID (assuming format: type_id)
      const type = agentId.split('_')[0] || 'unknown';
      if (!byType.has(type)) {
        byType.set(type, []);
      }
      byType.get(type)!.push(agentId);
    }

    // Second level: partition within each type
    let partitionIndex = 0;
    for (const [type, typeAgentIds] of Array.from(byType.entries())) {
      const partitionsForType = Math.max(1, Math.floor((typeAgentIds.length / agentIds.length) * numPartitions));
      const partitionSize = Math.ceil(typeAgentIds.length / partitionsForType);

      for (let i = 0; i < partitionsForType; i++) {
        const start = i * partitionSize;
        const end = Math.min(start + partitionSize, typeAgentIds.length);
        const partitionAgentIds = typeAgentIds.slice(start, end);

        if (partitionAgentIds.length > 0) {
          const partitionId = `partition_${type}_${i}`;
          assignments.set(partitionId, {
            partitionId,
            nodeId: '',
            agentIds: partitionAgentIds,
            size: partitionAgentIds.length,
            load: 0,
            assignedAt: Date.now(),
          });
          partitionIndex++;
        }
      }
    }
  }

  /**
   * Assign partitions to nodes
   */
  private assignPartitionsToNodes(assignments: Map<string, PartitionAssignment>): void {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);

    if (activeNodes.length === 0) {
      return;
    }

    // Sort nodes by capacity
    const sortedNodes = [...activeNodes].sort((a, b) =>
      (b.cpuCapacity + b.memoryCapacity) - (a.cpuCapacity + a.memoryCapacity)
    );

    // Assign partitions using consistent hashing
    let nodeIndex = 0;
    for (const [partitionId, assignment] of Array.from(assignments.entries())) {
      const node = sortedNodes[nodeIndex % sortedNodes.length];
      assignment.nodeId = node.id;
      assignment.load = assignment.size / this.config.targetPartitionSize;
      nodeIndex++;
    }

    // Update node agent counts
    for (const node of sortedNodes) {
      node.agentCount = 0;
    }
    for (const assignment of Array.from(assignments.values())) {
      const node = this.nodes.get(assignment.nodeId);
      if (node) {
        node.agentCount += assignment.size;
      }
    }
  }

  /**
   * Reassign partitions from failed node
   */
  private reassignPartitions(nodeId: string): void {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy && n.id !== nodeId);

    if (activeNodes.length === 0) {
      return;
    }

    // Find partitions assigned to failed node
    const partitionsToReassign = Array.from(this.partitions.values())
      .filter(p => p.nodeId === nodeId);

    // Reassign to least loaded nodes
    for (const partition of partitionsToReassign) {
      const leastLoaded = activeNodes.reduce((min, node) =>
        node.agentCount < min.agentCount ? node : min
      );

      partition.nodeId = leastLoaded.id;
      leastLoaded.agentCount += partition.size;
    }
  }

  /**
   * Create evolution tasks from partitions
   */
  private createEvolutionTasks(
    partitions: Map<string, PartitionAssignment>,
    agents: Map<string, MicrobiomeAgent>
  ): EvolutionTask[] {
    const tasks: EvolutionTask[] = [];

    for (const [partitionId, assignment] of Array.from(partitions.entries())) {
      const task: EvolutionTask = {
        id: `task_${partitionId}_${Date.now()}`,
        agentIds: assignment.agentIds,
        partitionId: partitionId,
        status: 'pending',
        assignedNode: assignment.nodeId,
        createdAt: Date.now(),
      };
      tasks.push(task);
      this.evolutionTasks.set(task.id, task);
    }

    return tasks;
  }

  /**
   * Execute map phase of distributed evolution
   */
  private async executeMapPhase(
    tasks: EvolutionTask[],
    snapshot: EcosystemSnapshot,
    fitnessFn: (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot) => Promise<FitnessScore>
  ): Promise<Map<string, Map<string, FitnessScore>>> {
    const mapResults = new Map<string, Map<string, FitnessScore>>();

    // Process tasks in parallel using optimizer
    const result = await this.optimizer.parallelProcess(
      tasks,
      async (task) => {
        const taskResults = new Map<string, FitnessScore>();

        // Process agents in this task
        for (const agentId of task.agentIds) {
          // Simulate fitness evaluation
          const fitness = await fitnessFn(
            { id: agentId } as MicrobiomeAgent,
            snapshot
          );
          taskResults.set(agentId, fitness);
        }

        return { taskId: task.id, results: taskResults };
      },
      { maxWorkers: this.config.maxTasksPerNode }
    );

    // Collect results
    for (const success of result.successes) {
      const { taskId, results } = success.result as { taskId: string; results: Map<string, FitnessScore> };
      mapResults.set(taskId, results);
    }

    return mapResults;
  }

  /**
   * Execute shuffle phase
   */
  private async executeShufflePhase(mapResults: Map<string, Map<string, FitnessScore>>): Promise<number> {
    const startTime = Date.now();

    // In a real distributed system, this would shuffle data across nodes
    // For this implementation, we simulate the shuffle time

    return Date.now() - startTime;
  }

  /**
   * Execute reduce phase
   */
  private async executeReducePhase(
    mapResults: Map<string, Map<string, FitnessScore>>
  ): Promise<Map<string, FitnessScore>> {
    const startTime = Date.now();
    const reduceResult = new Map<string, FitnessScore>();

    // Aggregate all fitness results
    for (const taskResults of Array.from(mapResults.values())) {
      for (const [agentId, fitness] of Array.from(taskResults.entries())) {
        reduceResult.set(agentId, fitness);
      }
    }

    this.monitor.recordOperation('reduce_phase', Date.now() - startTime);

    return reduceResult;
  }

  /**
   * Round-robin load balancing
   */
  private roundRobinBalancing(): void {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
    const partitions = Array.from(this.partitions.values());

    let nodeIndex = 0;
    for (const partition of partitions) {
      const node = activeNodes[nodeIndex % activeNodes.length];
      partition.nodeId = node.id;
      nodeIndex++;
    }
  }

  /**
   * Least-loaded load balancing
   */
  private leastLoadedBalancing(): void {
    const partitions = Array.from(this.partitions.values());

    for (const partition of partitions) {
      const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
      const leastLoaded = activeNodes.reduce((min, node) =>
        node.agentCount < min.agentCount ? node : min
      );

      partition.nodeId = leastLoaded.id;
      leastLoaded.agentCount += partition.size;
    }
  }

  /**
   * Weighted load balancing
   */
  private weightedBalancing(): void {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
    const partitions = Array.from(this.partitions.values());

    for (const partition of partitions) {
      // Calculate weights based on capacity
      const totalCapacity = activeNodes.reduce((sum, n) =>
        sum + n.cpuCapacity + n.memoryCapacity, 0
      );

      let selectedNode = activeNodes[0];
      let maxWeight = 0;

      for (const node of activeNodes) {
        const capacity = node.cpuCapacity + node.memoryCapacity;
        const currentLoad = node.agentCount / this.config.targetPartitionSize;
        const availableCapacity = capacity - currentLoad;
        const weight = availableCapacity / totalCapacity;

        if (weight > maxWeight) {
          maxWeight = weight;
          selectedNode = node;
        }
      }

      partition.nodeId = selectedNode.id;
      selectedNode.agentCount += partition.size;
    }
  }

  /**
   * Consistent hash load balancing
   */
  private consistentHashBalancing(): void {
    const partitions = Array.from(this.partitions.values());
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);

    for (const partition of partitions) {
      // Hash partition ID to determine node
      let hash = 0;
      for (let i = 0; i < partition.partitionId.length; i++) {
        hash = ((hash << 5) - hash) + partition.partitionId.charCodeAt(i);
        hash = hash & hash;
      }

      const nodeIndex = Math.abs(hash) % activeNodes.length;
      const node = activeNodes[nodeIndex];

      partition.nodeId = node.id;
      node.agentCount += partition.size;
    }
  }

  /**
   * Check scaling trigger
   */
  private async checkScalingTrigger(
    policy: AutoScalingPolicy,
    nodes: NodeInfo[]
  ): Promise<{ scaleUp: boolean; scaleDown: boolean }> {
    let scaleUp = false;
    let scaleDown = false;

    switch (policy.trigger) {
      case AutoScalingTrigger.CPU_THRESHOLD:
        const avgCpu = nodes.reduce((sum, n) => sum + n.cpuUsage, 0) / nodes.length;
        scaleUp = avgCpu > policy.threshold;
        scaleDown = avgCpu < policy.threshold * 0.5;
        break;

      case AutoScalingTrigger.MEMORY_THRESHOLD:
        const totalMemory = nodes.reduce((sum, n) => sum + n.memoryUsage, 0);
        const totalCapacity = nodes.reduce((sum, n) => sum + n.memoryCapacity, 0);
        const memoryUsage = totalMemory / totalCapacity;
        scaleUp = memoryUsage > policy.threshold;
        scaleDown = memoryUsage < policy.threshold * 0.5;
        break;

      case AutoScalingTrigger.QUEUE_DEPTH:
        const pendingTasks = Array.from(this.evolutionTasks.values()).filter(t => t.status === 'pending').length;
        const totalQueueCapacity = nodes.length * this.config.maxTasksPerNode;
        scaleUp = pendingTasks / totalQueueCapacity > policy.threshold;
        scaleDown = pendingTasks / totalQueueCapacity < policy.threshold * 0.3;
        break;

      case AutoScalingTrigger.RESPONSE_TIME:
        const avgLatency = this.stats.avgEvolutionLatency;
        scaleUp = avgLatency > policy.threshold;
        scaleDown = avgLatency < policy.threshold * 0.5;
        break;
    }

    return { scaleUp, scaleDown };
  }

  /**
   * Scale up resources
   */
  private async scaleUp(policy: AutoScalingPolicy): Promise<void> {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
    const currentCount = activeNodes.length;
    const scaleCount = Math.max(1, Math.floor(currentCount * (policy.scaleUpPercent / 100)));

    const newCount = Math.min(currentCount + scaleCount, policy.maxInstances);

    // In a real system, this would provision new nodes
    // For this implementation, we simulate by creating placeholder nodes
    for (let i = 0; i < newCount - currentCount; i++) {
      const newNode: NodeInfo = {
        id: `node_auto_${Date.now()}_${i}`,
        host: 'auto-generated',
        port: 0,
        cpuCapacity: 0.5,
        memoryCapacity: 1024 * 1024 * 1024, // 1GB
        cpuUsage: 0,
        memoryUsage: 0,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };
      this.registerNode(newNode);
    }

    // Rebalance load
    this.balanceLoad();
  }

  /**
   * Scale down resources
   */
  private async scaleDown(policy: AutoScalingPolicy): Promise<void> {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
    const currentCount = activeNodes.length;
    const scaleCount = Math.max(1, Math.floor(currentCount * (policy.scaleDownPercent / 100)));

    const newCount = Math.max(currentCount - scaleCount, policy.minInstances);

    // Remove excess nodes (least loaded first)
    const sortedNodes = [...activeNodes].sort((a, b) => a.agentCount - b.agentCount);
    const toRemove = sortedNodes.slice(0, currentCount - newCount);

    for (const node of toRemove) {
      this.unregisterNode(node.id);
    }
  }

  /**
   * Sync with federation member
   */
  private async syncWithMember(memberId: string, federation: FederationConfig): Promise<void> {
    // In a real system, this would perform network sync
    // For this implementation, we simulate the sync

    const syncData = {
      timestamp: Date.now(),
      member: memberId,
      federation: federation.id,
      populationSize: this.stats.totalPopulation,
      partitionCount: this.stats.partitionCount,
    };

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  /**
   * Create default auto-scaling policies
   */
  private createDefaultPolicies(): AutoScalingPolicy[] {
    return [
      {
        id: 'cpu_scaling',
        trigger: AutoScalingTrigger.CPU_THRESHOLD,
        threshold: 0.7,
        scaleUpPercent: 50,
        scaleDownPercent: 25,
        minInstances: 1,
        maxInstances: 100,
        cooldownPeriod: 60000, // 1 minute
        lastScaleAction: 0,
        enabled: true,
      },
      {
        id: 'memory_scaling',
        trigger: AutoScalingTrigger.MEMORY_THRESHOLD,
        threshold: 0.8,
        scaleUpPercent: 50,
        scaleDownPercent: 25,
        minInstances: 1,
        maxInstances: 100,
        cooldownPeriod: 60000,
        lastScaleAction: 0,
        enabled: true,
      },
      {
        id: 'queue_scaling',
        trigger: AutoScalingTrigger.QUEUE_DEPTH,
        threshold: 0.8,
        scaleUpPercent: 100,
        scaleDownPercent: 50,
        minInstances: 1,
        maxInstances: 200,
        cooldownPeriod: 30000, // 30 seconds
        lastScaleAction: 0,
        enabled: true,
      },
    ];
  }

  /**
   * Create empty statistics
   */
  private createEmptyStats(): ScalabilityStats {
    return {
      totalPopulation: 0,
      partitionCount: 0,
      activeNodes: 0,
      avgNodeLoad: 0,
      maxNodeLoad: 0,
      loadBalanceScore: 1,
      evolutionThroughput: 0,
      avgEvolutionLatency: 0,
      scalingEvents: 0,
      federationSyncs: 0,
    };
  }

  /**
   * Update statistics
   */
  private updateStats(): void {
    const activeNodes = Array.from(this.nodes.values()).filter(n => n.isHealthy);
    const partitions = Array.from(this.partitions.values());

    this.stats.activeNodes = activeNodes.length;
    this.stats.partitionCount = partitions.length;
    this.stats.totalPopulation = partitions.reduce((sum, p) => sum + p.size, 0);

    if (activeNodes.length > 0) {
      const loads = activeNodes.map(n =>
        n.agentCount / this.config.targetPartitionSize
      );
      this.stats.avgNodeLoad = loads.reduce((sum, l) => sum + l, 0) / loads.length;
      this.stats.maxNodeLoad = Math.max(...loads);

      // Calculate load balance score (1 = perfectly balanced, 0 = completely imbalanced)
      const variance = loads.reduce((sum, l) => sum + Math.pow(l - this.stats.avgNodeLoad, 2), 0) / loads.length;
      this.stats.loadBalanceScore = Math.max(0, 1 - variance);
    }
  }

  /**
   * Start background tasks
   */
  private startBackgroundTasks(): void {
    // Heartbeat monitoring
    this.heartbeatTimer = setInterval(() => {
      this.monitorHeartbeats();
    }, this.config.heartbeatInterval);

    // Auto-scaling checks
    if (this.config.enableAutoScaling) {
      this.scalingTimer = setInterval(() => {
        this.executeAutoScaling();
      }, 30000); // Check every 30 seconds
    }

    // Federation sync
    if (this.config.enableFederation && this.federations.size > 0) {
      this.federationTimer = setInterval(() => {
        for (const federationId of Array.from(this.federations.keys())) {
          this.syncFederation(federationId);
        }
      }, 60000); // Sync every minute
    }
  }

  /**
   * Monitor node heartbeats
   */
  private monitorHeartbeats(): void {
    const now = Date.now();
    const threshold = this.config.heartbeatInterval * this.config.nodeFailureThreshold;

    for (const node of Array.from(this.nodes.values())) {
      if (now - node.lastHeartbeat > threshold) {
        node.isHealthy = false;
        // Reassign partitions from unhealthy node
        this.reassignPartitions(node.id);
      }
    }
  }
}

/**
 * Factory function to create scalability manager
 */
export function createScalabilityManager(
  monitor: PerformanceMonitor,
  optimizer: PerformanceOptimizer,
  config?: ScalabilityConfig
): ScalabilityManager {
  return new ScalabilityManager(monitor, optimizer, config);
}

/**
 * Estimate required infrastructure for target population
 */
export function estimateInfrastructure(
  targetPopulation: number,
  avgAgentSize: number = 1024,
  targetPartitionSize: number = 1000
): {
  requiredNodes: number;
  requiredMemory: number;
  requiredPartitions: number;
  estimatedCost: number;
} {
  // Calculate required partitions
  const requiredPartitions = Math.ceil(targetPopulation / targetPartitionSize);

  // Estimate memory per node (1GB base + agent storage)
  const agentsPerNode = Math.min(targetPartitionSize, targetPopulation);
  const memoryPerNode = 1024 * 1024 * 1024 + (agentsPerNode * avgAgentSize * 2); // 2x for overhead
  const requiredNodes = Math.ceil(targetPopulation / agentsPerNode);
  const requiredMemory = requiredNodes * memoryPerNode;

  // Estimate cost (assuming $0.10 per GB per month)
  const memoryGB = requiredMemory / (1024 * 1024 * 1024);
  const estimatedCost = memoryGB * 0.10;

  return {
    requiredNodes,
    requiredMemory,
    requiredPartitions,
    estimatedCost,
  };
}
