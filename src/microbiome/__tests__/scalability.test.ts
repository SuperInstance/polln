/**
 * POLLN Microbiome - Scalability System Tests
 *
 * Comprehensive test suite for scalability management system
 * including partitioning, distributed evolution, load balancing,
 * and auto-scaling.
 *
 * @test microbiome/scalability
 */

import {
  ScalabilityManager,
  PartitioningStrategy,
  LoadBalancingStrategy,
  AutoScalingTrigger,
  createScalabilityManager,
  estimateInfrastructure,
  type NodeInfo,
  type PartitionAssignment,
  type EvolutionTask,
  type MapReduceResult,
  type AutoScalingPolicy,
  type FederationConfig,
  type ScalabilityStats,
  type ScalabilityConfig,
} from '../scalability.js';
import {
  PerformanceMonitor,
  createPerformanceMonitor,
} from '../performance.js';
import {
  PerformanceOptimizer,
  createPerformanceOptimizer,
} from '../optimization.js';
import type { MicrobiomeAgent, FitnessScore, EcosystemSnapshot } from '../types.js';

describe('ScalabilityManager', () => {
  let monitor: PerformanceMonitor;
  let optimizer: PerformanceOptimizer;
  let manager: ScalabilityManager;

  beforeEach(() => {
    monitor = createPerformanceMonitor({
      maxSamples: 100,
      enableAnomalyDetection: false,
    });
    optimizer = createPerformanceOptimizer(monitor);
    manager = createScalabilityManager(monitor, optimizer, {
      targetPartitionSize: 100,
      enableAutoScaling: false,
      enableFederation: false,
      heartbeatInterval: 1000,
      evolutionTimeout: 5000,
    });
  });

  afterEach(() => {
    manager.destroy();
    optimizer.destroy();
    monitor.reset();
  });

  describe('Node Management', () => {
    test('should register a new node', () => {
      const node: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024, // 1GB
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      manager.registerNode(node);

      const retrieved = manager.getNode('node_1');
      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe('node_1');
      expect(retrieved?.isHealthy).toBe(true);
    });

    test('should unregister a node and reassign partitions', () => {
      const node1: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      const node2: NodeInfo = {
        id: 'node_2',
        host: 'localhost',
        port: 3001,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      manager.registerNode(node1);
      manager.registerNode(node2);

      // Create partitions
      const agentIds = Array.from({ length: 200 }, (_, i) => `agent_${i}`);
      manager.partitionPopulation(agentIds);

      // Unregister node1
      manager.unregisterNode('node_1');

      expect(manager.getNode('node_1')).toBeUndefined();
      expect(manager.getNode('node_2')).toBeDefined();
    });

    test('should update node heartbeat', () => {
      const node: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: false,
        lastHeartbeat: Date.now() - 10000,
      };

      manager.registerNode(node);
      expect(manager.getNode('node_1')?.isHealthy).toBe(true); // Registration sets healthy

      manager.updateHeartbeat('node_1');
      const retrieved = manager.getNode('node_1');
      expect(retrieved?.lastHeartbeat).toBeGreaterThan(Date.now() - 100);
    });

    test('should return all nodes', () => {
      const node1: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      const node2: NodeInfo = {
        id: 'node_2',
        host: 'localhost',
        port: 3001,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      manager.registerNode(node1);
      manager.registerNode(node2);

      const nodes = manager.getNodes();
      expect(nodes).toHaveLength(2);
    });
  });

  describe('Population Partitioning', () => {
    beforeEach(() => {
      // Register multiple nodes
      for (let i = 0; i < 5; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        manager.registerNode(node);
      }
    });

    test('should partition population using hash-based strategy', () => {
      const agentIds = Array.from({ length: 500 }, (_, i) => `agent_${i}`);

      const partitions = manager.partitionPopulation(agentIds);

      expect(partitions.size).toBeGreaterThan(0);
      expect(partitions.size).toBeLessThanOrEqual(5); // 500 / 100 = 5 partitions

      // Verify all agents are assigned
      const assignedAgents = new Set<string>();
      for (const partition of partitions.values()) {
        for (const agentId of partition.agentIds) {
          assignedAgents.add(agentId);
        }
      }
      expect(assignedAgents.size).toBe(500);
    });

    test('should partition population using range-based strategy', () => {
      const config: Partial<ScalabilityConfig> = {
        partitioningStrategy: PartitioningStrategy.RANGE_BASED,
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      // Register nodes
      for (let i = 0; i < 5; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        customManager.registerNode(node);
      }

      const agentIds = Array.from({ length: 500 }, (_, i) => `agent_${i}`);
      const partitions = customManager.partitionPopulation(agentIds);

      expect(partitions.size).toBeGreaterThan(0);

      // Verify range-based ordering
      const allAgentIds: string[] = [];
      for (const partition of partitions.values()) {
        allAgentIds.push(...partition.agentIds);
      }
      const sorted = [...allAgentIds].sort();
      expect(allAgentIds).toEqual(sorted);

      customManager.destroy();
    });

    test('should handle large populations (10K+ agents)', () => {
      const agentIds = Array.from({ length: 10000 }, (_, i) => `agent_${i}`);

      const startTime = Date.now();
      const partitions = manager.partitionPopulation(agentIds);
      const duration = Date.now() - startTime;

      expect(partitions.size).toBeGreaterThan(0);
      expect(duration).toBeLessThan(5000); // Should complete in under 5 seconds

      // Verify all agents are assigned
      const totalAgents = Array.from(partitions.values())
        .reduce((sum, p) => sum + p.size, 0);
      expect(totalAgents).toBe(10000);
    });

    test('should handle very large populations (100K+ agents)', () => {
      const agentIds = Array.from({ length: 100000 }, (_, i) => `agent_${i}`);

      const startTime = Date.now();
      const partitions = manager.partitionPopulation(agentIds);
      const duration = Date.now() - startTime;

      expect(partitions.size).toBeGreaterThan(0);
      expect(duration).toBeLessThan(30000); // Should complete in under 30 seconds

      // Verify all agents are assigned
      const totalAgents = Array.from(partitions.values())
        .reduce((sum, p) => sum + p.size, 0);
      expect(totalAgents).toBe(100000);
    });

    test('should assign partitions to available nodes', () => {
      const agentIds = Array.from({ length: 250 }, (_, i) => `agent_${i}`);
      const partitions = manager.partitionPopulation(agentIds);

      // Verify each partition has a node assigned
      for (const partition of partitions.values()) {
        expect(partition.nodeId).toBeTruthy();
        expect(partition.nodeId.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Distributed Evolution', () => {
    beforeEach(() => {
      // Register multiple nodes
      for (let i = 0; i < 5; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        manager.registerNode(node);
      }
    });

    test('should execute map-reduce style evolution', async () => {
      const agents = new Map<string, MicrobiomeAgent>();
      for (let i = 0; i < 100; i++) {
        agents.set(`agent_${i}`, {
          id: `agent_${i}`,
          taxonomy: 'bacteria' as any,
          health: 1.0,
        } as MicrobiomeAgent);
      }

      const snapshot: EcosystemSnapshot = {
        timestamp: Date.now(),
        agents: new Map(),
        resourceFlows: new Map(),
        populationDynamics: new Map(),
      };

      const fitnessFn = async (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot): Promise<FitnessScore> => {
        return {
          overall: Math.random(),
          components: {
            survival: Math.random(),
            reproduction: Math.random(),
            efficiency: Math.random(),
          },
        };
      };

      const result = await manager.executeDistributedEvolution(agents, snapshot, fitnessFn);

      expect(result.reduceResult.size).toBe(100);
      expect(result.agentsEvaluated).toBe(100);
      expect(result.partitionsProcessed).toBeGreaterThan(0);
    });

    test('should handle large-scale evolution (1K+ agents)', async () => {
      const agents = new Map<string, MicrobiomeAgent>();
      for (let i = 0; i < 1000; i++) {
        agents.set(`agent_${i}`, {
          id: `agent_${i}`,
          taxonomy: 'bacteria' as any,
          health: 1.0,
        } as MicrobiomeAgent);
      }

      const snapshot: EcosystemSnapshot = {
        timestamp: Date.now(),
        agents: new Map(),
        resourceFlows: new Map(),
        populationDynamics: new Map(),
      };

      const fitnessFn = async (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot): Promise<FitnessScore> => {
        return {
          overall: Math.random(),
          components: {
            survival: Math.random(),
            reproduction: Math.random(),
            efficiency: Math.random(),
          },
        };
      };

      const startTime = Date.now();
      const result = await manager.executeDistributedEvolution(agents, snapshot, fitnessFn);
      const duration = Date.now() - startTime;

      expect(result.reduceResult.size).toBe(1000);
      expect(result.agentsEvaluated).toBe(1000);
      expect(duration).toBeLessThan(10000); // Should complete in under 10 seconds

      // Check throughput
      expect(result.agentsEvaluated / (duration / 1000)).toBeGreaterThan(100); // > 100 agents/sec
    });

    test('should track evolution tasks', async () => {
      const agents = new Map<string, MicrobiomeAgent>();
      for (let i = 0; i < 50; i++) {
        agents.set(`agent_${i}`, {
          id: `agent_${i}`,
          taxonomy: 'bacteria' as any,
          health: 1.0,
        } as MicrobiomeAgent);
      }

      const snapshot: EcosystemSnapshot = {
        timestamp: Date.now(),
        agents: new Map(),
        resourceFlows: new Map(),
        populationDynamics: new Map(),
      };

      const fitnessFn = async (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot): Promise<FitnessScore> => {
        return {
          overall: Math.random(),
          components: {
            survival: Math.random(),
            reproduction: Math.random(),
            efficiency: Math.random(),
          },
        };
      };

      await manager.executeDistributedEvolution(agents, snapshot, fitnessFn);

      const tasks = manager.getEvolutionTasks();
      expect(tasks.length).toBeGreaterThan(0);

      // Verify tasks are completed
      const completedTasks = tasks.filter(t => t.status === 'completed');
      expect(completedTasks.length).toBe(tasks.length);
    });
  });

  describe('Load Balancing', () => {
    beforeEach(() => {
      // Register nodes with different capacities
      const node1: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 0.5,
        memoryCapacity: 512 * 1024 * 1024,
        cpuUsage: 0.1,
        memoryUsage: 256 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      const node2: NodeInfo = {
        id: 'node_2',
        host: 'localhost',
        port: 3001,
        cpuCapacity: 1.0,
        memoryCapacity: 2 * 1024 * 1024 * 1024,
        cpuUsage: 0.1,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      const node3: NodeInfo = {
        id: 'node_3',
        host: 'localhost',
        port: 3002,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.1,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      manager.registerNode(node1);
      manager.registerNode(node2);
      manager.registerNode(node3);
    });

    test('should balance load using least-loaded strategy', () => {
      const config: Partial<ScalabilityConfig> = {
        loadBalancingStrategy: LoadBalancingStrategy.LEAST_LOADED,
        enableAutoScaling: false,
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      // Register nodes
      for (let i = 0; i < 3; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        customManager.registerNode(node);
      }

      const agentIds = Array.from({ length: 300 }, (_, i) => `agent_${i}`);
      customManager.partitionPopulation(agentIds);
      customManager.balanceLoad();

      const stats = customManager.getStats();
      expect(stats.loadBalanceScore).toBeGreaterThan(0.5);

      customManager.destroy();
    });

    test('should balance load using weighted strategy', () => {
      const config: Partial<ScalabilityConfig> = {
        loadBalancingStrategy: LoadBalancingStrategy.WEIGHTED,
        enableAutoScaling: false,
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      // Register nodes
      for (let i = 0; i < 3; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        customManager.registerNode(node);
      }

      const agentIds = Array.from({ length: 300 }, (_, i) => `agent_${i}`);
      customManager.partitionPopulation(agentIds);
      customManager.balanceLoad();

      const stats = customManager.getStats();
      expect(stats.loadBalanceScore).toBeGreaterThan(0.5);

      customManager.destroy();
    });

    test('should calculate load balance score correctly', () => {
      const agentIds = Array.from({ length: 300 }, (_, i) => `agent_${i}`);
      manager.partitionPopulation(agentIds);

      const stats = manager.getStats();
      expect(stats.loadBalanceScore).toBeGreaterThan(0);
      expect(stats.loadBalanceScore).toBeLessThanOrEqual(1);
    });
  });

  describe('Auto-Scaling', () => {
    test('should create default scaling policies', () => {
      const config: Partial<ScalabilityConfig> = {
        enableAutoScaling: true,
        autoScalingPolicies: [],
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      const policies = customManager.getScalingPolicies();
      expect(policies.length).toBeGreaterThan(0);

      customManager.destroy();
    });

    test('should execute auto-scaling based on CPU threshold', async () => {
      const config: Partial<ScalabilityConfig> = {
        enableAutoScaling: true,
        autoScalingPolicies: [
          {
            id: 'cpu_test',
            trigger: AutoScalingTrigger.CPU_THRESHOLD,
            threshold: 0.5,
            scaleUpPercent: 50,
            scaleDownPercent: 25,
            minInstances: 1,
            maxInstances: 10,
            cooldownPeriod: 1000,
            lastScaleAction: 0,
            enabled: true,
          },
        ],
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      // Register a node with high CPU usage
      const node: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 1.0,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.8, // Above threshold
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 100,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      customManager.registerNode(node);

      // Trigger auto-scaling
      await customManager.executeAutoScaling();

      // Wait for cooldown
      await new Promise(resolve => setTimeout(resolve, 1100));

      // Check that scaling occurred
      const stats = customManager.getStats();
      expect(stats.scalingEvents).toBeGreaterThan(0);

      customManager.destroy();
    });

    test('should update scaling policy', () => {
      const policies = manager.getScalingPolicies();
      if (policies.length > 0) {
        const originalThreshold = policies[0].threshold;

        manager.updateScalingPolicy(policies[0].id, { threshold: 0.9 });

        const updatedPolicies = manager.getScalingPolicies();
        const updated = updatedPolicies.find(p => p.id === policies[0].id);
        expect(updated?.threshold).toBe(0.9);
        expect(updated?.threshold).not.toBe(originalThreshold);
      }
    });
  });

  describe('Federation', () => {
    test('should add federation configuration', () => {
      const federation: FederationConfig = {
        id: 'fed_1',
        members: ['eco_1', 'eco_2', 'eco_3'],
        coordinator: 'eco_1',
        syncInterval: 60000,
        dataSharingPolicy: 'partial',
        conflictResolution: 'timestamp',
      };

      manager.addFederation(federation);

      // Should not throw
      expect(true).toBe(true);
    });

    test('should remove federation', () => {
      const federation: FederationConfig = {
        id: 'fed_1',
        members: ['eco_1', 'eco_2'],
        coordinator: 'eco_1',
        syncInterval: 60000,
        dataSharingPolicy: 'minimal',
        conflictResolution: 'voting',
      };

      manager.addFederation(federation);
      manager.removeFederation('fed_1');

      // Should not throw
      expect(true).toBe(true);
    });

    test('should sync with federation', async () => {
      const config: Partial<ScalabilityConfig> = {
        enableFederation: true,
        federationConfigs: [],
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      const federation: FederationConfig = {
        id: 'fed_1',
        members: ['member_1', 'member_2'],
        coordinator: 'coordinator_1',
        syncInterval: 1000,
        dataSharingPolicy: 'full',
        conflictResolution: 'coordinator',
      };

      customManager.addFederation(federation);

      // Sync should not throw
      await customManager.syncFederation('fed_1');

      const stats = customManager.getStats();
      expect(stats.federationSyncs).toBeGreaterThan(0);

      customManager.destroy();
    });
  });

  describe('Statistics', () => {
    beforeEach(() => {
      // Register nodes
      for (let i = 0; i < 5; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        manager.registerNode(node);
      }
    });

    test('should calculate statistics correctly', () => {
      const agentIds = Array.from({ length: 500 }, (_, i) => `agent_${i}`);
      manager.partitionPopulation(agentIds);

      const stats = manager.getStats();

      expect(stats.totalPopulation).toBe(500);
      expect(stats.activeNodes).toBe(5);
      expect(stats.partitionCount).toBeGreaterThan(0);
      expect(stats.avgNodeLoad).toBeGreaterThan(0);
      expect(stats.maxNodeLoad).toBeGreaterThanOrEqual(stats.avgNodeLoad);
    });

    test('should estimate max population', () => {
      const maxPop = manager.estimateMaxPopulation();
      expect(maxPop).toBeGreaterThan(0);
      expect(maxPop).toBeLessThan(Infinity);
    });

    test('should update statistics after operations', async () => {
      const agents = new Map<string, MicrobiomeAgent>();
      for (let i = 0; i < 100; i++) {
        agents.set(`agent_${i}`, {
          id: `agent_${i}`,
          taxonomy: 'bacteria' as any,
          health: 1.0,
        } as MicrobiomeAgent);
      }

      const snapshot: EcosystemSnapshot = {
        timestamp: Date.now(),
        agents: new Map(),
        resourceFlows: new Map(),
        populationDynamics: new Map(),
      };

      const fitnessFn = async (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot): Promise<FitnessScore> => {
        return {
          overall: Math.random(),
          components: {
            survival: Math.random(),
            reproduction: Math.random(),
            efficiency: Math.random(),
          },
        };
      };

      await manager.executeDistributedEvolution(agents, snapshot, fitnessFn);

      const stats = manager.getStats();
      expect(stats.evolutionThroughput).toBeGreaterThan(0);
      expect(stats.avgEvolutionLatency).toBeGreaterThan(0);
    });
  });

  describe('Infrastructure Estimation', () => {
    test('should estimate infrastructure for target population', () => {
      const estimate = estimateInfrastructure(10000);

      expect(estimate.requiredNodes).toBeGreaterThan(0);
      expect(estimate.requiredMemory).toBeGreaterThan(0);
      expect(estimate.requiredPartitions).toBeGreaterThan(0);
      expect(estimate.estimatedCost).toBeGreaterThan(0);
    });

    test('should scale estimates with population size', () => {
      const estimate1 = estimateInfrastructure(1000);
      const estimate2 = estimateInfrastructure(10000);

      expect(estimate2.requiredNodes).toBeGreaterThan(estimate1.requiredNodes);
      expect(estimate2.requiredMemory).toBeGreaterThan(estimate1.requiredMemory);
      expect(estimate2.requiredPartitions).toBeGreaterThan(estimate1.requiredPartitions);
    });

    test('should adjust for different agent sizes', () => {
      const estimate1 = estimateInfrastructure(1000, 512);
      const estimate2 = estimateInfrastructure(1000, 2048);

      expect(estimate2.requiredMemory).toBeGreaterThan(estimate1.requiredMemory);
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('should handle empty population', () => {
      const agentIds: string[] = [];
      const partitions = manager.partitionPopulation(agentIds);

      expect(partitions.size).toBe(0);
    });

    test('should handle no available nodes', () => {
      const agentIds = Array.from({ length: 100 }, (_, i) => `agent_${i}`);
      const partitions = manager.partitionPopulation(agentIds);

      // Partitions should be created but not assigned
      expect(partitions.size).toBeGreaterThan(0);
      for (const partition of partitions.values()) {
        expect(partition.nodeId).toBe('');
      }
    });

    test('should handle single node', () => {
      const node: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 1.0,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      manager.registerNode(node);

      const agentIds = Array.from({ length: 100 }, (_, i) => `agent_${i}`);
      const partitions = manager.partitionPopulation(agentIds);

      // All partitions should be assigned to the single node
      for (const partition of partitions.values()) {
        expect(partition.nodeId).toBe('node_1');
      }
    });

    test('should handle node failure during partitioning', () => {
      const node1: NodeInfo = {
        id: 'node_1',
        host: 'localhost',
        port: 3000,
        cpuCapacity: 1.0,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };

      const node2: NodeInfo = {
        id: 'node_2',
        host: 'localhost',
        port: 3001,
        cpuCapacity: 1.0,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.2,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: false, // Unhealthy
        lastHeartbeat: Date.now() - 10000,
      };

      manager.registerNode(node1);
      manager.registerNode(node2);

      const agentIds = Array.from({ length: 100 }, (_, i) => `agent_${i}`);
      const partitions = manager.partitionPopulation(agentIds);

      // Partitions should only be assigned to healthy node
      for (const partition of partitions.values()) {
        expect(partition.nodeId).not.toBe('node_2');
      }
    });
  });

  describe('Integration with Performance Monitor', () => {
    test('should record partition operation metrics', () => {
      const agentIds = Array.from({ length: 200 }, (_, i) => `agent_${i}`);
      manager.partitionPopulation(agentIds);

      const metric = monitor.getMetric('partition_population');
      expect(metric).toBeDefined();
      expect(metric?.count).toBeGreaterThan(0);
    });

    test('should record load balancing metrics', () => {
      // Register nodes
      for (let i = 0; i < 3; i++) {
        const node: NodeInfo = {
          id: `node_${i}`,
          host: 'localhost',
          port: 3000 + i,
          cpuCapacity: 0.8,
          memoryCapacity: 1024 * 1024 * 1024,
          cpuUsage: 0.2,
          memoryUsage: 512 * 1024 * 1024,
          agentCount: 0,
          isHealthy: true,
          lastHeartbeat: Date.now(),
        };
        manager.registerNode(node);
      }

      manager.balanceLoad();

      const metric = monitor.getMetric('load_balancing');
      expect(metric).toBeDefined();
      expect(metric?.count).toBeGreaterThan(0);
    });

    test('should record federation sync metrics', async () => {
      const config: Partial<ScalabilityConfig> = {
        enableFederation: true,
        federationConfigs: [],
      };
      const customManager = createScalabilityManager(monitor, optimizer, config);

      const federation: FederationConfig = {
        id: 'fed_1',
        members: ['member_1'],
        coordinator: 'coordinator_1',
        syncInterval: 1000,
        dataSharingPolicy: 'full',
        conflictResolution: 'coordinator',
      };

      customManager.addFederation(federation);
      await customManager.syncFederation('fed_1');

      const metric = monitor.getMetric('federation_sync');
      expect(metric).toBeDefined();
      expect(metric?.count).toBeGreaterThan(0);

      customManager.destroy();
    });
  });
});

describe('Scalability Stress Tests', () => {
  let monitor: PerformanceMonitor;
  let optimizer: PerformanceOptimizer;
  let manager: ScalabilityManager;

  beforeEach(() => {
    monitor = createPerformanceMonitor({
      maxSamples: 100,
      enableAnomalyDetection: false,
    });
    optimizer = createPerformanceOptimizer(monitor);
  });

  afterEach(() => {
    if (manager) {
      manager.destroy();
    }
    optimizer.destroy();
    monitor.reset();
  });

  test('should handle 100K agents with reasonable performance', async () => {
    manager = createScalabilityManager(monitor, optimizer, {
      targetPartitionSize: 1000,
      enableAutoScaling: false,
      enableFederation: false,
      heartbeatInterval: 1000,
    });

    // Register nodes
    for (let i = 0; i < 10; i++) {
      const node: NodeInfo = {
        id: `node_${i}`,
        host: 'localhost',
        port: 3000 + i,
        cpuCapacity: 1.0,
        memoryCapacity: 2 * 1024 * 1024 * 1024,
        cpuUsage: 0.1,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };
      manager.registerNode(node);
    }

    // Create large population
    const agentIds = Array.from({ length: 100000 }, (_, i) => `agent_${i}`);

    // Test partitioning performance
    const partitionStart = Date.now();
    const partitions = manager.partitionPopulation(agentIds);
    const partitionDuration = Date.now() - partitionStart;

    expect(partitions.size).toBeGreaterThan(0);
    expect(partitionDuration).toBeLessThan(30000); // Under 30 seconds

    // Test distributed evolution with subset
    const agents = new Map<string, MicrobiomeAgent>();
    for (let i = 0; i < 1000; i++) {
      agents.set(`agent_${i}`, {
        id: `agent_${i}`,
        taxonomy: 'bacteria' as any,
        health: 1.0,
      } as MicrobiomeAgent);
    }

    const snapshot: EcosystemSnapshot = {
      timestamp: Date.now(),
      agents: new Map(),
      resourceFlows: new Map(),
      populationDynamics: new Map(),
    };

    const fitnessFn = async (agent: MicrobiomeAgent, snapshot: EcosystemSnapshot): Promise<FitnessScore> => {
      return {
        overall: Math.random(),
        components: {
          survival: Math.random(),
          reproduction: Math.random(),
          efficiency: Math.random(),
        },
      };
    };

    const evolutionStart = Date.now();
    await manager.executeDistributedEvolution(agents, snapshot, fitnessFn);
    const evolutionDuration = Date.now() - evolutionStart;

    expect(evolutionDuration).toBeLessThan(15000); // Under 15 seconds

    const stats = manager.getStats();
    expect(stats.evolutionThroughput).toBeGreaterThan(50); // > 50 agents/sec
  });

  test('should maintain performance under load', async () => {
    manager = createScalabilityManager(monitor, optimizer, {
      targetPartitionSize: 500,
      enableAutoScaling: false,
      enableFederation: false,
    });

    // Register nodes
    for (let i = 0; i < 5; i++) {
      const node: NodeInfo = {
        id: `node_${i}`,
        host: 'localhost',
        port: 3000 + i,
        cpuCapacity: 0.8,
        memoryCapacity: 1024 * 1024 * 1024,
        cpuUsage: 0.1,
        memoryUsage: 512 * 1024 * 1024,
        agentCount: 0,
        isHealthy: true,
        lastHeartbeat: Date.now(),
      };
      manager.registerNode(node);
    }

    // Run multiple iterations
    const iterations = 5;
    const durations: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const agentIds = Array.from({ length: 5000 }, (_, j) => `agent_${i}_${j}`);

      const start = Date.now();
      manager.partitionPopulation(agentIds);
      const duration = Date.now() - start;

      durations.push(duration);
    }

    // Check that performance doesn't degrade significantly
    const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const maxDuration = Math.max(...durations);

    expect(maxDuration).toBeLessThan(avgDuration * 2); // Max should be < 2x average
  });
});
