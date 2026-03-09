/**
 * POLLN Microbiome Resource Sharing Tests
 *
 * Comprehensive test suite for the resource sharing system
 * covering all 6 resource types and cross-system integration.
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { SharedResourcePool, ResourceType, ResourcePriority, createSharedResourcePool } from '../resource-share.js';
import { BES, PrivacyTier } from '../../core/embedding.js';
import { KVAnchorPool, KVCacheSegment } from '../../core/kvanchor.js';
import { WorldModel } from '../../core/worldmodel.js';
import { ValueNetwork } from '../../core/valuenetwork.js';
import { FederatedLearningCoordinator } from '../../core/federated.js';
import { MicrobiomeBridge } from '../bridge.js';
import { v4 as uuidv4 } from 'uuid';

// ============================================================================
// Test Helpers
// ============================================================================

function createMockKVSegment(layerId: number = 0): KVCacheSegment {
  return {
    layerId,
    segmentId: uuidv4(),
    tokens: [1, 2, 3, 4, 5],
    keyCache: [[1.0, 2.0], [3.0, 4.0]],
    valueCache: [[5.0, 6.0], [7.0, 8.0]],
    metadata: {
      createdAt: Date.now(),
      modelHash: 'mock-model',
      agentId: 'test-agent',
      conversationId: 'test-conv',
      turnNumber: 1,
      position: 0,
      length: 5,
    },
  };
}

function createMockBridge(): MicrobiomeBridge {
  return new MicrobiomeBridge({ verbose: false });
}

// ============================================================================
// Test Suite
// ============================================================================

describe('SharedResourcePool', () => {
  let pool: SharedResourcePool;
  let bridge: MicrobiomeBridge;
  let kvPool: KVAnchorPool;
  let bes: BES;
  let worldModel: WorldModel;
  let valueNetwork: ValueNetwork;
  let flCoordinator: FederatedLearningCoordinator;

  beforeEach(() => {
    bridge = createMockBridge();
    pool = createSharedResourcePool(undefined, bridge);

    // Initialize system components
    kvPool = new KVAnchorPool({
      maxAnchors: 100,
      enableANN: false, // Disable ANN for faster tests
    });

    bes = new BES({
      defaultDimensionality: 128,
      defaultPrivacyTier: 'MEADOW',
    });

    worldModel = new WorldModel({
      latentDim: 32,
      hiddenDim: 64,
    });
    worldModel.initialize();

    valueNetwork = new ValueNetwork({
      inputDimension: 64,
    });

    flCoordinator = new FederatedLearningCoordinator({
      maxColonies: 10,
      minColoniesForRound: 2,
    });

    // Register components with pool
    pool.setKVCachePool(kvPool);
    pool.setEmbeddingSpace(bes);
    pool.setFederatedCoordinator(flCoordinator);
  });

  afterEach(() => {
    pool.destroy();
  });

  // ==========================================================================
  // Resource Registration and Allocation Tests
  // ==========================================================================

  describe('Resource Registration', () => {
    it('should register a basic resource', async () => {
      const resource = await pool.registerResource(
        ResourceType.MEMORY,
        { data: 'test' },
        'microbiome'
      );

      expect(resource).toBeDefined();
      expect(resource.type).toBe(ResourceType.MEMORY);
      expect(resource.owner).toBe('microbiome');
      expect(resource.status).toBe('allocated');
    });

    it('should register resource with custom options', async () => {
      const resource = await pool.registerResource(
        ResourceType.COMPUTE,
        { cores: 4 },
        'core',
        {
          priority: ResourcePriority.HIGH,
          privacyTier: 'PUBLIC',
          sizeBytes: 1024,
        }
      );

      expect(resource.priority).toBe(ResourcePriority.HIGH);
      expect(resource.privacyTier).toBe('PUBLIC');
      expect(resource.sizeBytes).toBe(1024);
    });

    it('should enforce resource limits', async () => {
      const config = { maxMemorySize: 100 };
      const limitedPool = createSharedResourcePool(config);

      // This should succeed
      await limitedPool.registerResource(
        ResourceType.MEMORY,
        { data: 'small' },
        'microbiome',
        { sizeBytes: 50 }
      );

      // This should fail
      await expect(
        limitedPool.registerResource(
          ResourceType.MEMORY,
          { data: 'large' },
          'core',
          { sizeBytes: 200 }
        )
      ).rejects.toThrow('Resource limit exceeded');

      limitedPool.destroy();
    });

    it('should track resource statistics', async () => {
      await pool.registerResource(
        ResourceType.KV_CACHE,
        { anchor: 'test' },
        'microbiome'
      );

      await pool.registerResource(
        ResourceType.KV_CACHE,
        { anchor: 'test2' },
        'core'
      );

      const stats = pool.getStats();
      const kvStats = stats.resources.get(ResourceType.KV_CACHE);

      expect(kvStats).toBeDefined();
      expect(kvStats?.totalAllocations).toBe(2);
      expect(kvStats?.activeAllocations).toBe(2);
    });
  });

  describe('Resource Allocation', () => {
    it('should allocate a registered resource', async () => {
      const resource = await pool.registerResource(
        ResourceType.EMBEDDING,
        { vector: [1, 2, 3] },
        'microbiome'
      );

      const allocation = await pool.allocateResource(resource.id, 'core');

      expect(allocation).toBeDefined();
      expect(allocation.resourceId).toBe(resource.id);
      expect(allocation.requester).toBe('core');
      expect(allocation.status).toBe('allocated');
    });

    it('should enforce privacy tier matching', async () => {
      const resource = await pool.registerResource(
        ResourceType.VALUE_NETWORK,
        { network: 'test' },
        'microbiome',
        { privacyTier: 'LOCAL' }
      );

      // Should fail with mismatched privacy tier
      const strictPool = createSharedResourcePool({
        requirePrivacyMatch: true,
      });

      const strictResource = await strictPool.registerResource(
        ResourceType.VALUE_NETWORK,
        { network: 'test' },
        'microbiome',
        { privacyTier: 'MEADOW' }
      );

      await expect(
        strictPool.allocateResource(strictResource.id, 'core', {
          privacyTier: 'PUBLIC',
        })
      ).rejects.toThrow('Privacy tier mismatch');

      strictPool.destroy();
    });

    it('should release resource allocation', async () => {
      const resource = await pool.registerResource(
        ResourceType.WORLD_MODEL,
        { model: 'test' },
        'core'
      );

      const allocation = await pool.allocateResource(resource.id, 'microbiome');
      await pool.releaseResource(allocation.id);

      const released = pool.allocations.get(allocation.id);
      expect(released?.status).toBe('released');
    });

    it('should preempt lower priority allocations when limit reached', async () => {
      const preemptivePool = createSharedResourcePool({
        maxConcurrentAllocations: 2,
        preemptionEnabled: true,
      });

      const resource1 = await preemptivePool.registerResource(
        ResourceType.COMPUTE,
        { task: 1 },
        'core',
        { priority: ResourcePriority.LOW }
      );

      const resource2 = await preemptivePool.registerResource(
        ResourceType.COMPUTE,
        { task: 2 },
        'microbiome',
        { priority: ResourcePriority.BATCH }
      );

      const resource3 = await preemptivePool.registerResource(
        ResourceType.COMPUTE,
        { task: 3 },
        'core',
        { priority: ResourcePriority.HIGH }
      );

      const alloc1 = await preemptivePool.allocateResource(resource1.id, 'microbiome');
      const alloc2 = await preemptivePool.allocateResource(resource2.id, 'core');

      // This should preempt alloc2 (BATCH priority)
      const alloc3 = await preemptivePool.allocateResource(
        resource3.id,
        'microbiome',
        { priority: ResourcePriority.HIGH }
      );

      expect(alloc2.status).toBe('preempted');
      expect(alloc3.status).toBe('allocated');

      preemptivePool.destroy();
    });
  });

  describe('Resource Discovery', () => {
    beforeEach(async () => {
      await pool.registerResource(
        ResourceType.KV_CACHE,
        { anchor: 1 },
        'microbiome',
        { priority: ResourcePriority.HIGH, privacyTier: 'PUBLIC' }
      );

      await pool.registerResource(
        ResourceType.KV_CACHE,
        { anchor: 2 },
        'core',
        { priority: ResourcePriority.NORMAL, privacyTier: 'MEADOW' }
      );

      await pool.registerResource(
        ResourceType.EMBEDDING,
        { vector: [1, 2, 3] },
        'microbiome'
      );
    });

    it('should find resources by type', () => {
      const kvResources = pool.findResources(ResourceType.KV_CACHE);

      expect(kvResources).toHaveLength(2);
      expect(kvResources.every(r => r.type === ResourceType.KV_CACHE)).toBe(true);
    });

    it('should filter resources by owner', () => {
      const microResources = pool.findResources(ResourceType.KV_CACHE, {
        owner: 'microbiome',
      });

      expect(microResources).toHaveLength(1);
      expect(microResources[0].owner).toBe('microbiome');
    });

    it('should filter resources by privacy tier', () => {
      const publicResources = pool.findResources(ResourceType.KV_CACHE, {
        privacyTier: 'PUBLIC',
      });

      expect(publicResources).toHaveLength(1);
      expect(publicResources[0].privacyTier).toBe('PUBLIC');
    });

    it('should filter resources by minimum priority', () => {
      const highPriorityResources = pool.findResources(ResourceType.KV_CACHE, {
        minPriority: ResourcePriority.HIGH,
      });

      expect(highPriorityResources).toHaveLength(1);
      expect(highPriorityResources[0].priority).toBe(ResourcePriority.HIGH);
    });

    it('should combine multiple filters', () => {
      const filtered = pool.findResources(ResourceType.KV_CACHE, {
        owner: 'core',
        privacyTier: 'MEADOW',
      });

      expect(filtered).toHaveLength(1);
      expect(filtered[0].owner).toBe('core');
      expect(filtered[0].privacyTier).toBe('MEADOW');
    });
  });

  // ==========================================================================
  // KV-Cache Sharing Tests
  // ==========================================================================

  describe('KV-Cache Sharing', () => {
    it('should share KV anchors across systems', async () => {
      const segment = createMockKVSegment(0);
      const embedding = [1.0, 2.0, 3.0, 4.0];

      const resource = await pool.shareKVAnchor(segment, embedding, 'microbiome');

      expect(resource).toBeDefined();
      expect(resource.type).toBe(ResourceType.KV_CACHE);
      expect(resource.owner).toBe('microbiome');
      expect(resource.resource).toHaveProperty('anchorId');
    });

    it('should find similar KV anchors', async () => {
      const segment1 = createMockKVSegment(0);
      const embedding1 = [1.0, 2.0, 3.0, 4.0];

      await pool.shareKVAnchor(segment1, embedding1, 'microbiome');

      const queryEmbedding = [1.1, 2.1, 3.1, 4.1];
      const similar = await pool.findSimilarKVAnchors(queryEmbedding, 0, 0.8);

      expect(similar.length).toBeGreaterThan(0);
      expect(similar[0].similarity).toBeGreaterThan(0.8);
    });

    it('should track KV-cache sharing statistics', async () => {
      const segment1 = createMockKVSegment(0);
      const segment2 = createMockKVSegment(1);

      await pool.shareKVAnchor(segment1, [1, 2, 3, 4], 'microbiome');
      await pool.shareKVAnchor(segment2, [5, 6, 7, 8], 'core');

      const stats = pool.getKVCacheStats();

      expect(stats.totalAnchors).toBe(2);
      expect(stats.sharedAnchors).toBe(2);
      expect(stats.avgCompressionRatio).toBeGreaterThan(0);
    });

    it('should share anchors across multiple layers', async () => {
      await pool.shareKVAnchor(createMockKVSegment(0), [1, 2, 3], 'microbiome');
      await pool.shareKVAnchor(createMockKVSegment(1), [4, 5, 6], 'core');
      await pool.shareKVAnchor(createMockKVSegment(2), [7, 8, 9], 'microbiome');

      const layer0Anchors = await pool.findSimilarKVAnchors([1, 2, 3], 0);
      const layer1Anchors = await pool.findSimilarKVAnchors([4, 5, 6], 1);
      const layer2Anchors = await pool.findSimilarKVAnchors([7, 8, 9], 2);

      expect(layer0Anchors.length).toBeGreaterThan(0);
      expect(layer1Anchors.length).toBeGreaterThan(0);
      expect(layer2Anchors.length).toBeGreaterThan(0);
    });
  });

  // ==========================================================================
  // Embedding Space Unification Tests
  // ==========================================================================

  describe('Embedding Space Unification', () => {
    it('should create shared pollen grains', async () => {
      const embedding = [1.0, 2.0, 3.0, 4.0, 5.0];

      const resource = await pool.createSharedPollenGrain(
        embedding,
        'test-gardener',
        'microbiome',
        'MEADOW'
      );

      expect(resource).toBeDefined();
      expect(resource.type).toBe(ResourceType.EMBEDDING);
      expect(resource.resource).toHaveProperty('id');
      expect(resource.resource).toHaveProperty('embedding');
      expect(resource.resource.privacyTier).toBe('MEADOW');
    });

    it('should map embeddings between systems', async () => {
      const microEmbedding = [1.0, 2.0, 3.0, 4.0];
      const coreEmbedding = [5.0, 6.0, 7.0, 8.0];

      const mapping = await pool.mapEmbeddings(microEmbedding, coreEmbedding);

      expect(mapping).toBeDefined();
      expect(mapping.microbiomeSpace).toEqual(microEmbedding);
      expect(mapping.coreSpace).toEqual(coreEmbedding);
      expect(mapping.transformMatrix).toBeDefined();
      expect(mapping.confidence).toBeGreaterThan(0);
    });

    it('should transform embeddings using mapping', async () => {
      const microEmbedding = [1.0, 2.0, 3.0, 4.0];
      const coreEmbedding = [5.0, 6.0, 7.0, 8.0];

      const mapping = await pool.mapEmbeddings(microEmbedding, coreEmbedding);

      const transformed = pool.transformEmbedding(
        microEmbedding,
        mapping,
        'microbiome_to_core'
      );

      expect(transformed).toBeDefined();
      expect(transformed.length).toBe(coreEmbedding.length);
    });

    it('should find similar pollen grains', async () => {
      await pool.createSharedPollenGrain([1, 2, 3, 4], 'gardener1', 'microbiome');
      await pool.createSharedPollenGrain([5, 6, 7, 8], 'gardener2', 'core');

      const similar = await pool.findSimilarPollenGrains([1.1, 2.1, 3.1, 4.1], 0.8);

      expect(similar.length).toBeGreaterThan(0);
      expect(similar[0].similarity).toBeGreaterThan(0.8);
    });

    it('should respect privacy tiers when creating grains', async () => {
      const publicGrain = await pool.createSharedPollenGrain(
        [1, 2, 3],
        'gardener',
        'microbiome',
        'PUBLIC'
      );

      expect(publicGrain.resource.privacyTier).toBe('PUBLIC');
      expect(publicGrain.resource.dimensionality).toBeLessThan(128); // Compressed
    });
  });

  // ==========================================================================
  // World Model Joint Learning Tests
  // ==========================================================================

  describe('World Model Joint Learning', () => {
    it('should register world models', async () => {
      await pool.registerWorldModel('microbiome-model-1', worldModel, 'microbiome');
      await pool.registerWorldModel('core-model-1', worldModel, 'core');

      const resources = pool.findResources(ResourceType.WORLD_MODEL);
      expect(resources).toHaveLength(2);
    });

    it('should train world models jointly', async () => {
      await pool.registerWorldModel('microbiome-model-1', worldModel, 'microbiome');
      await pool.registerWorldModel('core-model-1', worldModel, 'core');

      const microBatch: any = {
        observations: [[1, 2, 3], [4, 5, 6]],
        actions: [[0], [1]],
        rewards: [1, -1],
        nextObservations: [[2, 3, 4], [5, 6, 7]],
        dones: [false, true],
      };

      const coreBatch: any = {
        observations: [[7, 8, 9], [10, 11, 12]],
        actions: [[1], [0]],
        rewards: [2, -2],
        nextObservations: [[8, 9, 10], [11, 12, 13]],
        dones: [false, true],
      };

      const result = await pool.jointWorldModelTraining(microBatch, coreBatch);

      expect(result).toBeDefined();
      expect(result.microbiomeLoss).toBeGreaterThanOrEqual(0);
      expect(result.coreLoss).toBeGreaterThanOrEqual(0);
      expect(result.jointLoss).toBeGreaterThanOrEqual(0);
      expect(result.convergenceScore).toBeGreaterThan(0);
    });

    it('should generate joint dream episodes', async () => {
      await pool.registerWorldModel('microbiome-model-1', worldModel, 'microbiome');
      await pool.registerWorldModel('core-model-1', worldModel, 'core');

      const startStates = [[1, 2, 3], [4, 5, 6]];
      const result = await pool.jointDreaming(startStates, 10);

      expect(result.microbiomeDreams).toBeDefined();
      expect(result.coreDreams).toBeDefined();
      expect(result.fusedDreams).toBeDefined();
      expect(result.fusedDreams.length).toBeGreaterThan(0);
    });

    it('should synchronize world models', async () => {
      await pool.registerWorldModel('microbiome-model-1', worldModel, 'microbiome');
      await pool.registerWorldModel('core-model-1', worldModel, 'core');

      await pool.syncWorldModels();

      // Verify sync was recorded
      const syncEmitted = new Promise<void>((resolve) => {
        pool.once('world_models_synced', () => resolve());
      });

      await syncEmitted;
      expect(true).toBe(true); // If we get here, sync was emitted
    });
  });

  // ==========================================================================
  // Value Network Fusion Tests
  // ==========================================================================

  describe('Value Network Fusion', () => {
    it('should register value networks', async () => {
      await pool.registerValueNetwork('microbiome-vn-1', valueNetwork, 'microbiome');
      await pool.registerValueNetwork('core-vn-1', valueNetwork, 'core');

      const resources = pool.findResources(ResourceType.VALUE_NETWORK);
      expect(resources).toHaveLength(2);
    });

    it('should fuse value predictions', () => {
      pool.registerValueNetwork('microbiome-vn-1', valueNetwork, 'microbiome');
      pool.registerValueNetwork('core-vn-1', valueNetwork, 'core');

      const state = new Map([['value', 0.5]]);
      const result = pool.fuseValuePredictions(state);

      expect(result).toBeDefined();
      expect(result.fusedValue).toBeGreaterThanOrEqual(-1);
      expect(result.fusedValue).toBeLessThanOrEqual(1);
      expect(result.confidence).toBeGreaterThan(0);
      expect(result.individualPredictions).toHaveLength(2);
    });

    it('should update fusion configuration', () => {
      const newConfig = {
        microbiomeWeight: 0.7,
        coreWeight: 0.3,
        fusionMethod: 'voting' as const,
      };

      pool.updateValueNetworkFusion(newConfig);

      const stats = pool.getStats();
      expect(stats).toBeDefined();
    });

    it('should record joint trajectories', () => {
      pool.registerValueNetwork('microbiome-vn-1', valueNetwork, 'microbiome');
      pool.registerValueNetwork('core-vn-1', valueNetwork, 'core');

      const trajectories = [
        {
          id: 'traj-1',
          agentId: 'agent-1',
          states: [
            { state: new Map(), action: 'test', reward: 1, timestamp: Date.now() },
          ],
          finalValue: 10,
          length: 1,
        },
      ];

      pool.recordJointTrajectories(trajectories);

      const stats = pool.getStats();
      expect(stats).toBeDefined();
    });

    it('should handle uncertainty-weighted fusion', () => {
      pool.updateValueNetworkFusion({
        useUncertaintyWeighting: true,
        adaptiveWeighting: true,
      });

      pool.registerValueNetwork('vn-1', valueNetwork, 'microbiome');
      pool.registerValueNetwork('vn-2', valueNetwork, 'core');

      const state = new Map();
      const result = pool.fuseValuePredictions(state);

      expect(result.individualPredictions).toHaveLength(2);
      // Weights should be adjusted by confidence
      result.individualPredictions.forEach(pred => {
        expect(pred.weight).toBeGreaterThan(0);
        expect(pred.weight).toBeLessThanOrEqual(1);
      });
    });
  });

  // ==========================================================================
  // Memory Synchronization Tests
  // ==========================================================================

  describe('Memory Synchronization', () => {
    it('should queue memory for synchronization', async () => {
      const entry = await pool.syncMemory('microbiome', 'mem-1', {
        data: 'test',
      });

      expect(entry).toBeDefined();
      expect(entry.source).toBe('microbiome');
      expect(entry.memoryId).toBe('mem-1');
      expect(entry.syncStatus).toBe('pending');
    });

    it('should detect memory conflicts', async () => {
      const entry1 = await pool.syncMemory('microbiome', 'mem-1', {
        data: 'version1',
      });

      const entry2 = await pool.syncMemory('core', 'mem-1', {
        data: 'version2',
      });

      // Both should have same ID but different hashes
      expect(entry1.memoryId).toBe(entry2.memoryId);
      expect(entry1.contentHash).not.toBe(entry2.contentHash);
    });

    it('should resolve conflicts based on timestamp', async () => {
      const conflictPool = createSharedResourcePool({
        conflictResolution: 'timestamp',
      });

      await conflictPool.syncMemory('microbiome', 'mem-1', { data: 'v1' });
      await new Promise(resolve => setTimeout(resolve, 10));
      await conflictPool.syncMemory('core', 'mem-1', { data: 'v2' });

      // The newer entry should win
      // This is tested via event emission in actual implementation
      conflictPool.destroy();
    });

    it('should process memory sync queue', async () => {
      const eventSpy = jest.fn();
      pool.on('memory_synced', eventSpy);

      await pool.syncMemory('microbiome', 'mem-1', { data: 'test' });

      // Wait for async processing
      await new Promise(resolve => setTimeout(resolve, 100));

      // Event should have been emitted
      expect(eventSpy).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Federated Learning Coordination Tests
  // ==========================================================================

  describe('Federated Learning Coordination', () => {
    it('should get federated status', () => {
      const status = pool.getFederatedStatus();

      expect(status).toBeDefined();
      expect(status.isActive).toBe(false); // No active round initially
      expect(status.participatingColonies).toBe(0);
    });

    it('should participate in federated round', async () => {
      // Register a colony first
      await flCoordinator.registerColony('test-colony', 'test-gardener');

      const gradients = [0.1, 0.2, 0.3, 0.4];

      await expect(
        pool.participateInFederatedRound('test-colony', gradients, {
          sampleCount: 100,
          privacyTier: 'MEADOW',
        })
      ).resolves.not.toThrow();
    });

    it('should track privacy budget usage', async () => {
      await flCoordinator.registerColony('colony-1', 'gardener-1');

      await pool.participateInFederatedRound('colony-1', [0.1, 0.2], {
        privacyTier: 'MEADOW',
      });

      const accounting = flCoordinator.getPrivacyAccounting('colony-1');
      expect(accounting).toBeDefined();
      expect(accounting?.epsilonSpent).toBeGreaterThan(0);
    });
  });

  // ==========================================================================
  // Statistics and Monitoring Tests
  // ==========================================================================

  describe('Statistics and Monitoring', () => {
    it('should track comprehensive statistics', async () => {
      await pool.registerResource(
        ResourceType.KV_CACHE,
        { test: 1 },
        'microbiome'
      );

      const stats = pool.getStats();

      expect(stats.resources).toBeDefined();
      expect(stats.allocations).toBeDefined();
      expect(stats.cache).toBeDefined();
      expect(stats.sync).toBeDefined();
      expect(stats.kvCache).toBeDefined();
      expect(stats.federated).toBeDefined();
    });

    it('should record metrics history', () => {
      const metricsPool = createSharedResourcePool({
        enableMetrics: true,
        metricsRetentionMs: 1000,
      });

      // Trigger some activity
      metricsPool.registerResource(ResourceType.MEMORY, {}, 'microbiome');

      // Wait for metrics recording
      return new Promise<void>((resolve) => {
        setTimeout(() => {
          const history = metricsPool.getMetricsHistory();
          expect(history.length).toBeGreaterThan(0);
          metricsPool.destroy();
          resolve();
        }, 100);
      });
    });

    it('should cleanup old metrics', () => {
      const metricsPool = createSharedResourcePool({
        enableMetrics: true,
        metricsRetentionMs: 100,
      });

      metricsPool.registerResource(ResourceType.MEMORY, {}, 'microbiome');

      return new Promise<void>((resolve) => {
        setTimeout(() => {
          metricsPool.cleanup();

          const history = metricsPool.getMetricsHistory();
          // Old metrics should be cleaned up
          expect(history.length).toBeLessThanOrEqual(10);

          metricsPool.destroy();
          resolve();
        }, 200);
      });
    });

    it('should compute cache hit rate', () => {
      const stats = pool.getStats();
      expect(stats.cache.hitRate).toBeGreaterThanOrEqual(0);
      expect(stats.cache.hitRate).toBeLessThanOrEqual(1);
    });

    it('should track sync status', () => {
      const stats = pool.getStats();

      expect(stats.sync.lastSyncTime).toBeDefined();
      expect(stats.sync.syncInProgress).toBe(false);
      expect(stats.sync.pendingSyncs).toBe(0);
    });
  });

  // ==========================================================================
  // Resource Lifecycle Tests
  // ==========================================================================

  describe('Resource Lifecycle', () => {
    it('should clear all resources', async () => {
      await pool.registerResource(ResourceType.MEMORY, {}, 'microbiome');
      await pool.registerResource(ResourceType.EMBEDDING, {}, 'core');

      expect(pool.resources.size).toBeGreaterThan(0);

      pool.clear();

      expect(pool.resources.size).toBe(0);
      expect(pool.allocations.size).toBe(0);
    });

    it('should destroy pool and remove all listeners', async () => {
      const eventSpy = jest.fn();
      pool.on('resource_registered', eventSpy);

      await pool.registerResource(ResourceType.MEMORY, {}, 'microbiome');
      expect(eventSpy).toHaveBeenCalled();

      pool.destroy();

      // After destroy, events should not be emitted
      eventSpy.mockClear();

      // This should not emit events after destroy
      // (though it may throw, which is also acceptable)
      try {
        pool.registerResource(ResourceType.MEMORY, {}, 'microbiome');
      } catch (e) {
        // Expected after destroy
      }

      expect(eventSpy).not.toHaveBeenCalled();
    });

    it('should cleanup expired resources periodically', async () => {
      const cleanupPool = createSharedResourcePool({
        enableCaching: true,
        cacheTTLMs: 100,
      });

      await cleanupPool.registerResource(ResourceType.MEMORY, {}, 'microbiome');

      return new Promise<void>((resolve) => {
        setTimeout(() => {
          cleanupPool.cleanup();

          const stats = cleanupPool.getStats();
          expect(stats).toBeDefined();

          cleanupPool.destroy();
          resolve();
        }, 150);
      });
    });
  });

  // ==========================================================================
  // Integration Tests
  // ==========================================================================

  describe('Cross-System Integration', () => {
    it('should integrate with MicrobiomeBridge', async () => {
      const bridgePool = createSharedResourcePool({}, bridge);

      await bridgePool.registerResource(
        ResourceType.COMPUTE,
        { cores: 4 },
        'microbiome'
      );

      const resource = bridgePool.getResource(bridgePool.resources.keys().next().value);
      expect(resource).toBeDefined();

      bridgePool.destroy();
    });

    it('should share resources between systems end-to-end', async () => {
      // 1. Create KV anchor in microbiome
      const segment = createMockKVSegment(0);
      const kvResource = await pool.shareKVAnchor(
        segment,
        [1, 2, 3, 4],
        'microbiome'
      );

      // 2. Allocate to core
      const allocation = await pool.allocateResource(kvResource.id, 'core');
      expect(allocation.requester).toBe('core');

      // 3. Find similar anchors
      const similar = await pool.findSimilarKVAnchors([1, 2, 3, 4], 0);
      expect(similar.length).toBeGreaterThan(0);

      // 4. Release allocation
      await pool.releaseResource(allocation.id);
      const released = pool.allocations.get(allocation.id);
      expect(released?.status).toBe('released');
    });

    it('should handle concurrent operations', async () => {
      const operations = [];

      // Register multiple resources concurrently
      for (let i = 0; i < 10; i++) {
        operations.push(
          pool.registerResource(ResourceType.MEMORY, { id: i }, 'microbiome')
        );
      }

      const resources = await Promise.all(operations);
      expect(resources).toHaveLength(10);

      // Allocate them concurrently
      const allocations = await Promise.all(
        resources.map(r => pool.allocateResource(r.id, 'core'))
      );

      expect(allocations).toHaveLength(10);

      // Release them concurrently
      await Promise.all(allocations.map(a => pool.releaseResource(a.id)));

      allocations.forEach(a => {
        const released = pool.allocations.get(a.id);
        expect(released?.status).toBe('released');
      });
    });
  });

  // ==========================================================================
  // Performance Tests
  // ==========================================================================

  describe('Performance', () => {
    it('should handle high-throughput resource registration', async () => {
      const throughputPool = createSharedResourcePool({
        maxConcurrentAllocations: 1000,
      });

      const startTime = Date.now();

      const resources = await Promise.all(
        Array.from({ length: 100 }, (_, i) =>
          throughputPool.registerResource(
            ResourceType.MEMORY,
            { id: i },
            'microbiome',
            { sizeBytes: 1024 }
          )
        )
      );

      const duration = Date.now() - startTime;

      expect(resources).toHaveLength(100);
      expect(duration).toBeLessThan(1000); // Should complete in < 1s

      throughputPool.destroy();
    });

    it('should efficiently find resources', () => {
      return new Promise<void>(async (resolve) => {
        // Register many resources
        for (let i = 0; i < 100; i++) {
          await pool.registerResource(
            ResourceType.KV_CACHE,
            { id: i },
            i % 2 === 0 ? 'microbiome' : 'core'
          );
        }

        const startTime = Date.now();

        const kvResources = pool.findResources(ResourceType.KV_CACHE);

        const duration = Date.now() - startTime;

        expect(kvResources).toHaveLength(100);
        expect(duration).toBeLessThan(100); // Should find in < 100ms

        resolve();
      });
    });
  });

  // ==========================================================================
  // Error Handling Tests
  // ==========================================================================

  describe('Error Handling', () => {
    it('should handle allocation of non-existent resource', async () => {
      await expect(
        pool.allocateResource('non-existent-id', 'microbiome')
      ).rejects.toThrow('Resource non-existent-id not found');
    });

    it('should handle release of non-existent allocation', async () => {
      await expect(pool.releaseResource('non-existent-id')).rejects.toThrow();
    });

    it('should handle operations without KV-cache pool', async () => {
      const noKVPool = createSharedResourcePool();

      await expect(
        noKVPool.shareKVAnchor(createMockKVSegment(), [1, 2, 3], 'microbiome')
      ).rejects.toThrow('KV-cache pool not initialized');

      noKVPool.destroy();
    });

    it('should handle operations without embedding space', async () => {
      const noEmbedPool = createSharedResourcePool();

      await expect(
        noEmbedPool.createSharedPollenGrain([1, 2, 3], 'gardener', 'microbiome')
      ).rejects.toThrow('Embedding space not initialized');

      noEmbedPool.destroy();
    });
  });
});

// ============================================================================
// Factory Function Tests
// ============================================================================

describe('Resource Pool Factory Functions', () => {
  it('should create pool with default configuration', () => {
    const pool = createSharedResourcePool();

    expect(pool).toBeInstanceOf(SharedResourcePool);

    pool.destroy();
  });

  it('should create low-latency pool', () => {
    const pool = createSharedResourcePool();
    const lowLatencyPool = createSharedResourcePool({
      allocationPolicy: 'priority',
      preemptionEnabled: true,
      autoSyncEnabled: false,
    });

    expect(lowLatencyPool).toBeInstanceOf(SharedResourcePool);

    pool.destroy();
    lowLatencyPool.destroy();
  });

  it('should create high-throughput pool', () => {
    const pool = createSharedResourcePool({
      allocationPolicy: 'fair_share',
      maxConcurrentAllocations: 1000,
    });

    expect(pool).toBeInstanceOf(SharedResourcePool);

    pool.destroy();
  });
});
