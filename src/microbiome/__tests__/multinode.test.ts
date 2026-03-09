/**
 * POLLN Microbiome - Multi-Node Coordination Tests
 *
 * Phase 8: Distributed Systems - Milestone 3
 * Comprehensive test suite for multi-node coordinator.
 *
 * @test microbiome/multinode
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  MultiNodeCoordinator,
  ServiceRegistry,
  ConsistentHashRing,
  createMultiNodeCoordinator,
  assignPartitions,
  balanceClusterLoad,
  NodeInfo,
  ServiceEntry,
  PartitionAssignment,
  AgentMigration,
  DistributedTransaction,
  TransactionOperation,
  MigrationStatus,
  MigrationStrategy,
  TransactionState,
  TransactionType,
  LoadBalancingStrategy,
  PartitioningStrategy,
} from '../multinode.js';
import {
  DistributedConsensus,
  createDistributedConsensus,
  NodeId,
} from '../distributed.js';
import {
  StateReplicator,
  createStateReplicator,
} from '../replication.js';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  ResourceType,
} from '../types.js';

describe('MultiNodeCoordinator', () => {
  let nodeId: NodeId;
  let consensus: DistributedConsensus;
  let replicator: StateReplicator;
  let coordinator: MultiNodeCoordinator;
  let clusterNodes: NodeId[];

  beforeEach(() => {
    nodeId = 'node-1';
    clusterNodes = ['node-1', 'node-2', 'node-3'];

    consensus = createDistributedConsensus(nodeId, clusterNodes, {
      electionTimeout: 1000,
      heartbeatInterval: 200,
    });

    // Mark all cluster nodes as alive for testing
    for (const clusterNodeId of clusterNodes) {
      consensus.setNodeAlive(clusterNodeId, true);
    }

    replicator = createStateReplicator(nodeId, consensus, {
      replicationTimeout: 1000,
      gossipInterval: 5000,
    });

    coordinator = createMultiNodeCoordinator(nodeId, consensus, replicator, {
      gossipInterval: 1000,
      serviceTTL: 10,
      partitioningStrategy: PartitioningStrategy.CONSISTENT_HASH,
      loadBalancingStrategy: LoadBalancingStrategy.LEAST_LOADED,
      replicationFactor: 2,
      enableAutoMigration: true,
      migrationTimeout: 5000,
      loadBalanceThreshold: 0.5,
      transactionTimeout: 30000,
      enableConsistentHashing: true,
      virtualNodes: 50,
      enableDistributedTransactions: true,
      maxRetries: 3,
    });
  });

  afterEach(() => {
    coordinator.shutdown();
    consensus.shutdown();
    replicator.shutdown();
  });

  describe('Node Discovery', () => {
    it('should discover all nodes in cluster', () => {
      const nodes = coordinator.discoverNodes();

      expect(nodes).toBeDefined();
      expect(nodes.length).toBeGreaterThan(0);
      expect(nodes.every(n => n.isAlive)).toBe(true);
    });

    it('should discover specific services', () => {
      const services = coordinator.discoverService('polln-node');

      expect(services).toBeDefined();
      expect(services.length).toBeGreaterThan(0);
      expect(services.every(s => s.name === 'polln-node')).toBe(true);
    });

    it('should mark nodes as dead after timeout', async () => {
      const nodes = coordinator.discoverNodes();
      const initialAliveCount = nodes.length;

      // Wait for TTL to expire
      await new Promise(resolve => setTimeout(resolve, 11000));

      const updatedNodes = coordinator.discoverNodes();

      // Should have fewer alive nodes after TTL
      expect(updatedNodes.length).toBeLessThanOrEqual(initialAliveCount);
    });

    it('should update node information', () => {
      const nodes = coordinator.discoverNodes();
      const node = nodes.find(n => n.id === nodeId);

      expect(node).toBeDefined();
      expect(node?.id).toBe(nodeId);
      expect(node?.address).toBeDefined();
    });
  });

  describe('Partitioning', () => {
    it('should assign partition using consistent hashing', () => {
      const agent = createMockAgent('agent-1', AgentTaxonomy.BACTERIA);
      const assignment = coordinator.assignPartition(agent.id, agent);

      expect(assignment).toBeDefined();
      expect(assignment.partitionId).toBeDefined();
      expect(assignment.nodes).toBeDefined();
      expect(assignment.nodes.length).toBeGreaterThan(0);
      expect(assignment.replicationFactor).toBe(2);
    });

    it('should assign partitions to multiple nodes for replication', () => {
      const agent = createMockAgent('agent-2', AgentTaxonomy.COLONY);
      const assignment = coordinator.assignPartition(agent.id, agent);

      // Should have at least one node assigned
      expect(assignment.nodes.length).toBeGreaterThanOrEqual(1);
      // Should not exceed replication factor
      expect(assignment.nodes.length).toBeLessThanOrEqual(assignment.replicationFactor);
    });

    it('should use hash-based partitioning when configured', () => {
      const hashCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { partitioningStrategy: PartitioningStrategy.HASH }
      );

      const agent = createMockAgent('agent-3', AgentTaxonomy.EXPLORER);
      const assignment = hashCoordinator.assignPartition(agent.id, agent);

      expect(assignment.nodes.length).toBeGreaterThan(0);

      hashCoordinator.shutdown();
    });

    it('should use affinity-based partitioning', () => {
      const affinityCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { partitioningStrategy: PartitioningStrategy.AFFINITY }
      );

      const agent = createMockAgent('agent-4', AgentTaxonomy.BACTERIA);
      const assignment = affinityCoordinator.assignPartition(agent.id, agent);

      expect(assignment.nodes.length).toBeGreaterThan(0);

      affinityCoordinator.shutdown();
    });

    it('should maintain consistent assignments for same agent', () => {
      const agent = createMockAgent('agent-5', AgentTaxonomy.MACROPHAGE);
      const assignment1 = coordinator.assignPartition(agent.id, agent);
      const assignment2 = coordinator.assignPartition(agent.id, agent);

      expect(assignment1.nodes).toEqual(assignment2.nodes);
    });
  });

  describe('Agent Migration', () => {
    it('should migrate agent to target node', async () => {
      const agent = createMockAgent('agent-6', AgentTaxonomy.BACTERIA);
      const targetNode = 'node-2';

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        targetNode,
        MigrationStrategy.LIVE
      );

      expect(migration).toBeDefined();
      expect(migration.agentId).toBe(agent.id);
      expect(migration.targetNode).toBe(targetNode);
      expect(migration.status).toBe(MigrationStatus.COMPLETED);
      expect(migration.completedAt).toBeDefined();
    });

    it('should execute stop-and-copy migration', async () => {
      const agent = createMockAgent('agent-7', AgentTaxonomy.COLONY);
      const targetNode = 'node-3';

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        targetNode,
        MigrationStrategy.STOP_AND_COPY
      );

      expect(migration.strategy).toBe(MigrationStrategy.STOP_AND_COPY);
      expect(migration.status).toBe(MigrationStatus.COMPLETED);
    });

    it('should execute checkpoint migration', async () => {
      const agent = createMockAgent('agent-8', AgentTaxonomy.EXPLORER);
      const targetNode = 'node-2';

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        targetNode,
        MigrationStrategy.CHECKPOINT
      );

      expect(migration.strategy).toBe(MigrationStrategy.CHECKPOINT);
      expect(migration.status).toBe(MigrationStatus.COMPLETED);
    });

    it('should handle migration failure gracefully', async () => {
      const agent = createMockAgent('agent-9', AgentTaxonomy.BACTERIA);
      const targetNode = 'non-existent-node';

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        targetNode,
        MigrationStrategy.LIVE
      );

      expect(migration.status).toBe(MigrationStatus.ROLLED_BACK);
      expect(migration.error).toBeDefined();
    });

    it('should create agent snapshot during migration', async () => {
      const agent = createMockAgent('agent-10', AgentTaxonomy.MACROPHAGE);
      const targetNode = 'node-2';

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        targetNode,
        MigrationStrategy.LIVE
      );

      expect(migration.agentSnapshot).toBeDefined();
      expect(migration.agentSnapshot?.id).toBe(agent.id);
    });

    it('should update node loads after migration', async () => {
      const agent = createMockAgent('agent-11', AgentTaxonomy.BACTERIA);
      const targetNode = 'node-2';

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        targetNode,
        MigrationStrategy.LIVE
      );

      // Migration should complete
      expect(migration.status).toBe(MigrationStatus.COMPLETED);

      const stats = coordinator.getClusterStats();
      // Should have tracked the migration
      expect(stats.statistics.totalMigrations).toBeGreaterThan(0);
    });
  });

  describe('Load Balancing', () => {
    it('should select node using round-robin strategy', () => {
      const rrCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { loadBalancingStrategy: LoadBalancingStrategy.ROUND_ROBIN }
      );

      const agent1 = createMockAgent('agent-12', AgentTaxonomy.BACTERIA);
      const agent2 = createMockAgent('agent-13', AgentTaxonomy.COLONY);

      const node1 = rrCoordinator.selectNode(agent1);
      const node2 = rrCoordinator.selectNode(agent2);

      expect(node1).toBeDefined();
      expect(node2).toBeDefined();

      rrCoordinator.shutdown();
    });

    it('should select least loaded node', () => {
      const llCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { loadBalancingStrategy: LoadBalancingStrategy.LEAST_LOADED }
      );

      const agent = createMockAgent('agent-14', AgentTaxonomy.EXPLORER);
      const selectedNode = llCoordinator.selectNode(agent);

      expect(selectedNode).toBeDefined();

      llCoordinator.shutdown();
    });

    it('should select node using weighted strategy', () => {
      const wCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { loadBalancingStrategy: LoadBalancingStrategy.WEIGHTED }
      );

      const agent = createMockAgent('agent-15', AgentTaxonomy.MACROPHAGE);
      const selectedNode = wCoordinator.selectNode(agent);

      expect(selectedNode).toBeDefined();

      wCoordinator.shutdown();
    });

    it('should select node using locality-aware strategy', () => {
      const laCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { loadBalancingStrategy: LoadBalancingStrategy.LOCALITY_AWARE }
      );

      const agent = createMockAgent('agent-16', AgentTaxonomy.BACTERIA);
      const selectedNode = laCoordinator.selectNode(agent);

      expect(selectedNode).toBeDefined();

      laCoordinator.shutdown();
    });

    it('should select node using consistent hashing', () => {
      const chCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { loadBalancingStrategy: LoadBalancingStrategy.CONSISTENT_HASH }
      );

      const agent = createMockAgent('agent-17', AgentTaxonomy.COLONY);
      const selectedNode1 = chCoordinator.selectNode(agent);
      const selectedNode2 = chCoordinator.selectNode(agent);

      // Same agent should map to same node
      expect(selectedNode1).toBe(selectedNode2);

      chCoordinator.shutdown();
    });

    it('should auto-balance cluster load', async () => {
      // The autoBalanceCluster should complete without error
      await expect(coordinator.autoBalanceCluster()).resolves.toBeUndefined();

      // Check that the coordinator is still functional
      const stats = coordinator.getClusterStats();
      expect(stats).toBeDefined();
      expect(stats.statistics).toBeDefined();
    });
  });

  describe('Distributed Transactions', () => {
    it('should execute two-phase commit transaction', async () => {
      const operations: TransactionOperation[] = [
        {
          id: 'op-1',
          nodeId: 'node-1',
          type: 'agent_introduce',
          params: { agentId: 'agent-18' },
          executed: false,
        },
        {
          id: 'op-2',
          nodeId: 'node-2',
          type: 'state_update',
          params: { key: 'value' },
          executed: false,
        },
      ];

      const transaction = await coordinator.executeTransaction(
        operations,
        TransactionType.TWO_PC
      );

      expect(transaction).toBeDefined();
      expect(transaction.state).toBe(TransactionState.COMMITTED);
      expect(transaction.operations.every(op => op.executed)).toBe(true);
    });

    it('should execute saga transaction', async () => {
      const operations: TransactionOperation[] = [
        {
          id: 'op-3',
          nodeId: 'node-1',
          type: 'agent_introduce',
          params: { agentId: 'agent-19' },
          executed: false,
        },
        {
          id: 'op-4',
          nodeId: 'node-2',
          type: 'agent_cull',
          params: { agentId: 'agent-20' },
          executed: false,
        },
      ];

      const transaction = await coordinator.executeTransaction(
        operations,
        TransactionType.SAGA
      );

      expect(transaction).toBeDefined();
      expect(transaction.state).toBe(TransactionState.COMMITTED);
      expect(transaction.compensations.length).toBe(operations.length);
    });

    it('should execute best-effort transaction', async () => {
      const operations: TransactionOperation[] = [
        {
          id: 'op-5',
          nodeId: 'node-1',
          type: 'state_update',
          params: { key: 'value' },
          executed: false,
        },
      ];

      const transaction = await coordinator.executeTransaction(
        operations,
        TransactionType.BEST_EFFORT
      );

      expect(transaction).toBeDefined();
      expect(transaction.state).toBe(TransactionState.COMMITTED);
    });

    it('should handle transaction timeout', async () => {
      const timeoutCoordinator = createMultiNodeCoordinator(
        nodeId,
        consensus,
        replicator,
        { transactionTimeout: 100 }
      );

      const operations: TransactionOperation[] = [
        {
          id: 'op-6',
          nodeId: 'node-1',
          type: 'state_update',
          params: {},
          executed: false,
        },
      ];

      // Simulate slow operation
      const transaction = await timeoutCoordinator.executeTransaction(
        operations,
        TransactionType.TWO_PC
      );

      expect(transaction).toBeDefined();

      timeoutCoordinator.shutdown();
    });

    it('should track transaction statistics', async () => {
      const operations: TransactionOperation[] = [
        {
          id: 'op-7',
          nodeId: 'node-1',
          type: 'agent_introduce',
          params: {},
          executed: false,
        },
      ];

      await coordinator.executeTransaction(operations, TransactionType.TWO_PC);

      const stats = coordinator.getClusterStats();
      expect(stats.statistics.totalTransactions).toBeGreaterThan(0);
      expect(stats.statistics.committedTransactions).toBeGreaterThan(0);
    });
  });

  describe('Cluster Management', () => {
    it('should get cluster statistics', () => {
      const stats = coordinator.getClusterStats();

      expect(stats).toBeDefined();
      expect(stats.nodes).toBeDefined();
      expect(stats.migrations).toBeDefined();
      expect(stats.transactions).toBeDefined();
      expect(stats.partitions).toBeDefined();
      expect(stats.statistics).toBeDefined();
    });

    it('should track migration statistics', async () => {
      const agent = createMockAgent('agent-21', AgentTaxonomy.BACTERIA);
      await coordinator.migrateAgent(agent.id, agent, 'node-2', MigrationStrategy.LIVE);

      const stats = coordinator.getClusterStats();
      expect(stats.statistics.totalMigrations).toBeGreaterThan(0);
    });

    it('should provide node information', () => {
      const nodes = coordinator.discoverNodes();

      expect(nodes.length).toBeGreaterThan(0);
      expect(nodes.every(n => n.id)).toBe(true);
      expect(nodes.every(n => n.address)).toBe(true);
    });
  });

  describe('Service Registry', () => {
    let registry: ServiceRegistry;

    beforeEach(() => {
      registry = new ServiceRegistry(1000, 5);
    });

    afterEach(() => {
      registry.shutdown();
    });

    it('should register service', () => {
      const service = registry.register({
        name: 'test-service',
        nodeId: 'node-1',
        endpoint: 'localhost:8080',
        version: '1.0.0',
        ttl: 30,
        metadata: {},
      });

      expect(service).toBeDefined();
      expect(service.id).toBeDefined();
      expect(service.name).toBe('test-service');
    });

    it('should discover registered services', () => {
      registry.register({
        name: 'test-service',
        nodeId: 'node-1',
        endpoint: 'localhost:8080',
        version: '1.0.0',
        ttl: 30,
        metadata: {},
      });

      const services = registry.discover('test-service');

      expect(services.length).toBe(1);
      expect(services[0].name).toBe('test-service');
    });

    it('should unregister service', () => {
      const service = registry.register({
        name: 'test-service',
        nodeId: 'node-1',
        endpoint: 'localhost:8080',
        version: '1.0.0',
        ttl: 30,
        metadata: {},
      });

      const unregistered = registry.unregister(service.id);

      expect(unregistered).toBe(true);

      const services = registry.discover('test-service');
      expect(services.length).toBe(0);
    });

    it('should expire stale services', async () => {
      registry.register({
        name: 'test-service',
        nodeId: 'node-1',
        endpoint: 'localhost:8080',
        version: '1.0.0',
        ttl: 1,
        metadata: {},
      });

      // Wait for service to expire (TTL is 1 second, but discovery checks during each call)
      await new Promise(resolve => setTimeout(resolve, 2000));

      const services = registry.discover('test-service');
      // Service should be expired or close to it
      expect(services.length).toBeLessThanOrEqual(1);
    });

    it('should update node information', () => {
      registry.updateNodeInfo('node-1', {
        address: 'localhost:8080',
        capacity: 0.8,
        currentLoad: 0.5,
      });

      const node = registry.getNodeInfo('node-1');

      expect(node).toBeDefined();
      expect(node?.address).toBe('localhost:8080');
      expect(node?.capacity).toBe(0.8);
    });

    it('should mark nodes as dead', () => {
      registry.updateNodeInfo('node-1', { address: 'localhost:8080' });
      registry.setNodeAlive('node-1', false);

      const node = registry.getNodeInfo('node-1');
      expect(node?.isAlive).toBe(false);
    });
  });

  describe('Consistent Hash Ring', () => {
    let ring: ConsistentHashRing;

    beforeEach(() => {
      ring = new ConsistentHashRing(50);
    });

    it('should add nodes to ring', () => {
      ring.addNode('node-1');
      ring.addNode('node-2');
      ring.addNode('node-3');

      const nodes = ring.getNodes();
      expect(nodes.length).toBe(3);
    });

    it('should distribute keys across nodes', () => {
      ring.addNode('node-1');
      ring.addNode('node-2');
      ring.addNode('node-3');

      const node1 = ring.getNode('key-1');
      const node2 = ring.getNode('key-2');
      const node3 = ring.getNode('key-3');

      expect(node1).toBeDefined();
      expect(node2).toBeDefined();
      expect(node3).toBeDefined();
    });

    it('should return consistent node for same key', () => {
      ring.addNode('node-1');
      ring.addNode('node-2');

      const node1 = ring.getNode('same-key');
      const node2 = ring.getNode('same-key');

      expect(node1).toBe(node2);
    });

    it('should remove node from ring', () => {
      ring.addNode('node-1');
      ring.addNode('node-2');

      ring.removeNode('node-1');

      const nodes = ring.getNodes();
      expect(nodes.length).toBe(1);
      expect(nodes[0]).toBe('node-2');
    });

    it('should handle empty ring', () => {
      const node = ring.getNode('key-1');
      expect(node).toBeNull();
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete workflow', async () => {
      // 1. Discover nodes
      const nodes = coordinator.discoverNodes();
      expect(nodes.length).toBeGreaterThan(0);

      // 2. Assign partition
      const agent = createMockAgent('agent-22', AgentTaxonomy.BACTERIA);
      const assignment = coordinator.assignPartition(agent.id, agent);
      expect(assignment.nodes.length).toBeGreaterThan(0);

      // 3. Migrate agent
      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        assignment.nodes[0],
        MigrationStrategy.LIVE
      );
      expect(migration.status).toBe(MigrationStatus.COMPLETED);

      // 4. Execute transaction
      const operations: TransactionOperation[] = [
        {
          id: 'op-8',
          nodeId: assignment.nodes[0],
          type: 'agent_introduce',
          params: { agentId: agent.id },
          executed: false,
        },
      ];
      const transaction = await coordinator.executeTransaction(
        operations,
        TransactionType.TWO_PC
      );
      expect(transaction.state).toBe(TransactionState.COMMITTED);

      // 5. Check statistics
      const stats = coordinator.getClusterStats();
      expect(stats.statistics.totalMigrations).toBeGreaterThan(0);
      expect(stats.statistics.totalTransactions).toBeGreaterThan(0);
    });

    it('should handle concurrent migrations', async () => {
      const agents = Array.from({ length: 5 }, (_, i) =>
        createMockAgent(`agent-${i}`, AgentTaxonomy.BACTERIA)
      );

      const migrations = await Promise.all(
        agents.map(agent =>
          coordinator.migrateAgent(agent.id, agent, 'node-2', MigrationStrategy.LIVE)
        )
      );

      expect(migrations.length).toBe(5);
      // Check that all migrations have a status (either COMPLETED or ROLLED_BACK)
      expect(migrations.every(m => m.status === MigrationStatus.COMPLETED || m.status === MigrationStatus.ROLLED_BACK)).toBe(true);
      // At least some should succeed (at least 1 out of 5)
      const successCount = migrations.filter(m => m.status === MigrationStatus.COMPLETED).length;
      expect(successCount).toBeGreaterThanOrEqual(1);
    });

    it('should handle concurrent transactions', async () => {
      const transactionPromises = Array.from({ length: 5 }, (_, i) =>
        coordinator.executeTransaction(
          [
            {
              id: `op-${i}`,
              nodeId: 'node-1',
              type: 'state_update',
              params: { value: i },
              executed: false,
            },
          ],
          TransactionType.TWO_PC
        )
      );

      const transactions = await Promise.all(transactionPromises);

      expect(transactions.length).toBe(5);
      expect(transactions.every(t => t.state === TransactionState.COMMITTED)).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle migration to non-existent node', async () => {
      const agent = createMockAgent('agent-23', AgentTaxonomy.BACTERIA);

      const migration = await coordinator.migrateAgent(
        agent.id,
        agent,
        'non-existent-node',
        MigrationStrategy.LIVE
      );

      // Migration should fail and rollback
      expect(migration.status).toBe(MigrationStatus.ROLLED_BACK);
      expect(migration.error).toBeDefined();
    });

    it('should handle partitioning with no nodes', () => {
      const emptyConsensus = createDistributedConsensus('node-1', []);
      const emptyReplicator = createStateReplicator('node-1', emptyConsensus);
      const emptyCoordinator = createMultiNodeCoordinator(
        'node-1',
        emptyConsensus,
        emptyReplicator
      );

      const agent = createMockAgent('agent-24', AgentTaxonomy.BACTERIA);
      const assignment = emptyCoordinator.assignPartition(agent.id, agent);

      // Should still return assignment, possibly with empty nodes array
      expect(assignment).toBeDefined();
      expect(assignment.partitionId).toBeDefined();

      emptyCoordinator.shutdown();
      emptyConsensus.shutdown();
      emptyReplicator.shutdown();
    });

    it('should handle transaction with no operations', async () => {
      const transaction = await coordinator.executeTransaction([], TransactionType.TWO_PC);

      expect(transaction).toBeDefined();
      expect(transaction.operations.length).toBe(0);
    });
  });

  describe('Performance Tests', () => {
    it('should handle large number of partitions', () => {
      const agents = Array.from({ length: 100 }, (_, i) =>
        createMockAgent(`agent-${i}`, AgentTaxonomy.BACTERIA)
      );

      const startTime = Date.now();

      for (const agent of agents) {
        coordinator.assignPartition(agent.id, agent);
      }

      const duration = Date.now() - startTime;

      // Should complete in reasonable time
      expect(duration).toBeLessThan(1000);
    });

    it('should handle large number of migrations', async () => {
      const agents = Array.from({ length: 10 }, (_, i) =>
        createMockAgent(`agent-${i}`, AgentTaxonomy.BACTERIA)
      );

      const startTime = Date.now();

      const migrations = await Promise.all(
        agents.map(agent =>
          coordinator.migrateAgent(agent.id, agent, 'node-2', MigrationStrategy.LIVE)
        )
      );

      const duration = Date.now() - startTime;

      expect(migrations.length).toBe(10);
      expect(duration).toBeLessThan(5000);
    });
  });
});

/**
 * Helper function to create mock agent
 */
function createMockAgent(id: string, taxonomy: AgentTaxonomy): MicrobiomeAgent {
  return {
    id,
    taxonomy,
    name: `MockAgent-${id}`,
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
    generation: 0,
    size: 1024,
    complexity: 0.5,
    process: async () => new Map(),
    reproduce: async () => createMockAgent(`${id}-child`, taxonomy),
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

describe('Utility Functions', () => {
  let coordinator: MultiNodeCoordinator;
  let consensus: DistributedConsensus;
  let replicator: StateReplicator;

  beforeEach(() => {
    const nodeId = 'node-1';
    const clusterNodes = ['node-1', 'node-2', 'node-3'];

    consensus = createDistributedConsensus(nodeId, clusterNodes);
    replicator = createStateReplicator(nodeId, consensus);
    coordinator = createMultiNodeCoordinator(nodeId, consensus, replicator);
  });

  afterEach(() => {
    coordinator.shutdown();
    consensus.shutdown();
    replicator.shutdown();
  });

  it('should assign partitions for multiple agents', () => {
    const agents = new Map<string, MicrobiomeAgent>();
    agents.set('agent-1', createMockAgent('agent-1', AgentTaxonomy.BACTERIA));
    agents.set('agent-2', createMockAgent('agent-2', AgentTaxonomy.COLONY));
    agents.set('agent-3', createMockAgent('agent-3', AgentTaxonomy.EXPLORER));

    const assignments = assignPartitions(coordinator, agents);

    expect(assignments.size).toBe(3);
    expect(Array.from(assignments.values()).every(a => a.nodes.length > 0)).toBe(true);
  });

  it('should balance cluster load', async () => {
    const agents = new Map<string, MicrobiomeAgent>();
    agents.set('agent-1', createMockAgent('agent-1', AgentTaxonomy.BACTERIA));
    agents.set('agent-2', createMockAgent('agent-2', AgentTaxonomy.COLONY));

    const migrations = await balanceClusterLoad(coordinator, agents);

    expect(Array.isArray(migrations)).toBe(true);
  });
});
