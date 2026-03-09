/**
 * POLLN Microbiome Resource Sharing System
 *
 * Phase 6 - Milestone 3: Resource Sharing
 *
 * This module provides comprehensive resource sharing capabilities between
 * the Microbiome system and Core POLLN system, enabling:
 *
 * 1. KV-Cache Sharing: Unified anchor pools across systems
 * 2. Embedding Space Unification: Shared BES instances
 * 3. World Model Joint Learning: Collaborative VAE training
 * 4. Value Network Fusion: Merged TD(λ) predictions
 * 5. Memory Synchronization: Cross-system memory alignment
 * 6. Federated Learning Coordination: Unified FL participation
 *
 * Key Features:
 * - Privacy-aware resource sharing with tier management
 * - Resource allocation and optimization
 * - Cross-system communication bridges
 * - Performance monitoring and analytics
 * - Conflict resolution and synchronization
 *
 * @module microbiome/resource-share
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import type { PrivacyTier } from '../core/embedding.js';
import type { KVAnchor, KVCacheSegment, KVAnchorPool, AnchorMatch } from '../core/kvanchor.js';
import type { PollenGrain, BES } from '../core/embedding.js';
import type { WorldModel, TrainingBatch, DreamEpisode } from '../core/worldmodel.js';
import type { ValueNetwork, Trajectory, ValuePrediction } from '../core/valuenetwork.js';
import type { FederatedLearningCoordinator, GradientUpdate, ModelVersion } from '../core/federated.js';
import type { MicrobiomeBridge } from './bridge.js';
import type { ProtocolAdapter } from './protocol-adapter.js';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Shared resource types
 */
export enum ResourceType {
  KV_CACHE = 'kv_cache',
  EMBEDDING = 'embedding',
  WORLD_MODEL = 'world_model',
  VALUE_NETWORK = 'value_network',
  MEMORY = 'memory',
  FEDERATED_MODEL = 'federated_model',
  COMPUTE = 'compute',
  BANDWIDTH = 'bandwidth',
}

/**
 * Resource priority levels
 */
export enum ResourcePriority {
  CRITICAL = 'critical',      // Safety-critical, always available
  HIGH = 'high',             // Important tasks
  NORMAL = 'normal',         // Default priority
  LOW = 'low',               // Background tasks
  BATCH = 'batch',           // Deferred processing
}

/**
 * Resource allocation status
 */
export enum AllocationStatus {
  PENDING = 'pending',
  ALLOCATED = 'allocated',
  IN_USE = 'in_use',
  RELEASED = 'released',
  FAILED = 'failed',
  PREEMPTED = 'preempted',
}

/**
 * Shared resource container
 */
export interface SharedResource<T = unknown> {
  id: string;
  type: ResourceType;
  resource: T;
  owner: 'microbiome' | 'core' | 'shared';
  priority: ResourcePriority;
  privacyTier: PrivacyTier;
  createdAt: number;
  lastAccessed: number;
  accessCount: number;
  sizeBytes: number;
  metadata: Record<string, unknown>;
  status: AllocationStatus;
}

/**
 * Resource allocation request
 */
export interface ResourceAllocation {
  id: string;
  requester: 'microbiome' | 'core';
  resourceId: string;
  type: ResourceType;
  priority: ResourcePriority;
  requestedAt: number;
  timeout: number;
  status: AllocationStatus;
  allocatedAt?: number;
  releasedAt?: number;
}

/**
 * Resource sharing configuration
 */
export interface ResourceShareConfig {
  // Resource limits
  maxKVCacheSize: number;
  maxEmbeddingSize: number;
  maxWorldModels: number;
  maxValueNetworks: number;
  maxMemorySize: number;

  // Allocation policy
  allocationPolicy: 'fifo' | 'priority' | 'fair_share' | 'adaptive';
  preemptionEnabled: boolean;
  maxConcurrentAllocations: number;

  // Privacy
  defaultPrivacyTier: PrivacyTier;
  privacyEnforcement: boolean;
  requirePrivacyMatch: boolean;

  // Synchronization
  syncInterval: number;
  autoSyncEnabled: boolean;
  conflictResolution: 'timestamp' | 'priority' | 'merge' | 'manual';

  // Performance
  enableCompression: boolean;
  enableCaching: boolean;
  cacheSize: number;
  cacheTTLMs: number;

  // Monitoring
  enableMetrics: boolean;
  metricsRetentionMs: number;
}

/**
 * Resource usage statistics
 */
export interface ResourceStats {
  type: ResourceType;
  totalAllocations: number;
  activeAllocations: number;
  failedAllocations: number;
  preemptedAllocations: number;
  totalBytesTransferred: number;
  avgAllocationTime: number;
  avgUtilization: number;
  peakUtilization: number;
}

/**
 * Cross-system embedding mapping
 */
export interface EmbeddingMapping {
  microbiomeSpace: number[];
  coreSpace: number[];
  transformMatrix: number[][];
  confidence: number;
  lastUpdated: number;
}

/**
 * World model sync status
 */
export interface WorldModelSync {
  microbiomeVersion: number;
  coreVersion: number;
  lastSyncTime: number;
  syncPending: boolean;
  divergentSamples: number;
  convergenceScore: number;
}

/**
 * Value network fusion config
 */
export interface ValueNetworkFusion {
  microbiomeWeight: number;
  coreWeight: number;
  useUncertaintyWeighting: boolean;
  adaptiveWeighting: boolean;
  fusionMethod: 'weighted_average' | 'voting' | 'stacking' | 'mixture';
}

/**
 * Memory sync entry
 */
export interface MemorySyncEntry {
  id: string;
  source: 'microbiome' | 'core';
  memoryId: string;
  contentHash: string;
  timestamp: number;
  syncStatus: 'pending' | 'synced' | 'conflict' | 'failed';
}

/**
 * Federated learning participation
 */
export interface FederatedParticipation {
  colonyId: string;
  lastRound: number;
  contributions: number;
  averageGradientNorm: number;
  privacyTierUsed: PrivacyTier;
}

// ============================================================================
// Shared Resource Pool Implementation
// ============================================================================

/**
 * SharedResourcePool - Central resource management for cross-system sharing
 *
 * Manages the unified resource pool shared between Microbiome and Core POLLN
 * systems with intelligent allocation, privacy controls, and synchronization.
 */
export class SharedResourcePool extends EventEmitter {
  private config: ResourceShareConfig;
  private bridge: MicrobiomeBridge | null;
  private protocolAdapter: ProtocolAdapter | null;

  // Resource storage
  private resources: Map<string, SharedResource> = new Map();
  private allocations: Map<string, ResourceAllocation> = new Map();

  // System-specific resources
  private kvCachePool: KVAnchorPool | null;
  private embeddingSpace: BES | null;
  private worldModels: Map<string, WorldModel> = new Map();
  private valueNetworks: Map<string, ValueNetwork> = new Map();
  private federatedCoordinator: FederatedLearningCoordinator | null;

  // Cross-system mappings
  private embeddingMappings: Map<string, EmbeddingMapping> = new Map();
  private worldModelSyncs: Map<string, WorldModelSync> = new Map();
  private valueNetworkFusion: ValueNetworkFusion;
  private memorySyncQueue: MemorySyncEntry[] = [];

  // Statistics tracking
  private stats: Map<ResourceType, ResourceStats> = new Map();
  private metricsHistory: Array<{
    timestamp: number;
    stats: Map<ResourceType, ResourceStats>;
  }> = [];

  // Synchronization state
  private lastSyncTime: number = 0;
  private syncInProgress: boolean = false;
  private pendingSyncs: Set<string> = new Set();

  // Cache
  private resourceCache: Map<string, {
    resource: SharedResource;
    expiresAt: number;
  }> = new Map();

  constructor(
    config?: Partial<ResourceShareConfig>,
    bridge?: MicrobiomeBridge,
    protocolAdapter?: ProtocolAdapter
  ) {
    super();

    this.config = {
      maxKVCacheSize: 1000000000,      // 1GB
      maxEmbeddingSize: 500000000,     // 500MB
      maxWorldModels: 5,
      maxValueNetworks: 10,
      maxMemorySize: 2000000000,       // 2GB

      allocationPolicy: 'adaptive',
      preemptionEnabled: true,
      maxConcurrentAllocations: 100,

      defaultPrivacyTier: 'MEADOW',
      privacyEnforcement: true,
      requirePrivacyMatch: false,

      syncInterval: 60000,             // 1 minute
      autoSyncEnabled: true,
      conflictResolution: 'merge',

      enableCompression: true,
      enableCaching: true,
      cacheSize: 1000,
      cacheTTLMs: 300000,             // 5 minutes

      enableMetrics: true,
      metricsRetentionMs: 86400000,   // 24 hours
      ...config,
    };

    this.bridge = bridge || null;
    this.protocolAdapter = protocolAdapter || null;

    // Initialize value network fusion config
    this.valueNetworkFusion = {
      microbiomeWeight: 0.5,
      coreWeight: 0.5,
      useUncertaintyWeighting: true,
      adaptiveWeighting: true,
      fusionMethod: 'weighted_average',
    };

    // Initialize system resources (will be set via setters)
    this.kvCachePool = null;
    this.embeddingSpace = null;
    this.federatedCoordinator = null;

    // Initialize statistics
    this.initializeStats();

    // Start auto-sync if enabled
    if (this.config.autoSyncEnabled) {
      this.startAutoSync();
    }

    // Clean up expired resources periodically
    setInterval(() => this.cleanup(), 60000);
  }

  // ==========================================================================
  // Resource Registration and Management
  // ==========================================================================

  /**
   * Register a shared resource
   */
  async registerResource<T>(
    type: ResourceType,
    resource: T,
    owner: 'microbiome' | 'core' | 'shared',
    options?: {
      priority?: ResourcePriority;
      privacyTier?: PrivacyTier;
      metadata?: Record<string, unknown>;
      sizeBytes?: number;
    }
  ): Promise<SharedResource<T>> {
    const id = uuidv4();
    const now = Date.now();

    // Estimate size if not provided
    let sizeBytes = options?.sizeBytes || 0;
    if (sizeBytes === 0) {
      sizeBytes = this.estimateResourceSize(type, resource);
    }

    const sharedResource: SharedResource<T> = {
      id,
      type,
      resource,
      owner,
      priority: options?.priority || ResourcePriority.NORMAL,
      privacyTier: options?.privacyTier || this.config.defaultPrivacyTier,
      createdAt: now,
      lastAccessed: now,
      accessCount: 0,
      sizeBytes,
      metadata: options?.metadata || {},
      status: AllocationStatus.ALLOCATED,
    };

    // Check resource limits
    if (!this.checkResourceLimit(type, sizeBytes)) {
      throw new Error(`Resource limit exceeded for type ${type}`);
    }

    // Store resource
    this.resources.set(id, sharedResource);

    // Update statistics
    this.updateStats(type, {
      totalAllocations: 1,
      activeAllocations: 1,
    });

    this.emit('resource_registered', {
      id,
      type,
      owner,
      sizeBytes,
    });

    return sharedResource;
  }

  /**
   * Allocate a resource to a requester
   */
  async allocateResource(
    resourceId: string,
    requester: 'microbiome' | 'core',
    options?: {
      priority?: ResourcePriority;
      timeout?: number;
      privacyTier?: PrivacyTier;
    }
  ): Promise<ResourceAllocation> {
    const resource = this.resources.get(resourceId);
    if (!resource) {
      throw new Error(`Resource ${resourceId} not found`);
    }

    // Privacy check
    if (this.config.requirePrivacyMatch && options?.privacyTier) {
      if (resource.privacyTier !== options.privacyTier) {
        throw new Error(`Privacy tier mismatch: resource ${resource.privacyTier}, request ${options.privacyTier}`);
      }
    }

    // Check concurrent allocation limit
    const activeAllocations = Array.from(this.allocations.values())
      .filter(a => a.status === AllocationStatus.IN_USE).length;
    if (activeAllocations >= this.config.maxConcurrentAllocations) {
      // Try to preempt lower priority allocations
      if (!this.preemptAllocations(requester, options?.priority || ResourcePriority.NORMAL)) {
        throw new Error('Maximum concurrent allocations reached');
      }
    }

    const id = uuidv4();
    const now = Date.now();
    const timeout = options?.timeout || 300000; // 5 minutes default

    const allocation: ResourceAllocation = {
      id,
      requester,
      resourceId,
      type: resource.type,
      priority: options?.priority || resource.priority,
      requestedAt: now,
      timeout,
      status: AllocationStatus.ALLOCATED,
      allocatedAt: now,
    };

    this.allocations.set(id, allocation);
    resource.status = AllocationStatus.IN_USE;
    resource.accessCount++;
    resource.lastAccessed = now;

    // Cache if enabled
    if (this.config.enableCaching) {
      this.cacheResource(resource);
    }

    this.emit('resource_allocated', {
      allocationId: id,
      resourceId,
      requester,
      type: resource.type,
    });

    return allocation;
  }

  /**
   * Release a resource allocation
   */
  async releaseResource(allocationId: string): Promise<void> {
    const allocation = this.allocations.get(allocationId);
    if (!allocation) {
      throw new Error(`Allocation ${allocationId} not found`);
    }

    const resource = this.resources.get(allocation.resourceId);
    if (resource) {
      resource.status = AllocationStatus.RELEASED;
      resource.lastAccessed = Date.now();
    }

    allocation.status = AllocationStatus.RELEASED;
    allocation.releasedAt = Date.now();

    this.emit('resource_released', {
      allocationId,
      resourceId: allocation.resourceId,
    });
  }

  /**
   * Get a resource by ID
   */
  getResource<T>(resourceId: string): SharedResource<T> | undefined {
    const resource = this.resources.get(resourceId);
    if (resource) {
      resource.lastAccessed = Date.now();
      resource.accessCount++;
    }
    return resource as SharedResource<T> | undefined;
  }

  /**
   * Find resources by type and criteria
   */
  findResources(
    type: ResourceType,
    criteria?: {
      owner?: 'microbiome' | 'core' | 'shared';
      privacyTier?: PrivacyTier;
      minPriority?: ResourcePriority;
    }
  ): SharedResource[] {
    let results = Array.from(this.resources.values()).filter(r => r.type === type);

    if (criteria?.owner) {
      results = results.filter(r => r.owner === criteria.owner);
    }
    if (criteria?.privacyTier) {
      results = results.filter(r => r.privacyTier === criteria.privacyTier);
    }
    if (criteria?.minPriority) {
      const priorityOrder = [
        ResourcePriority.CRITICAL,
        ResourcePriority.HIGH,
        ResourcePriority.NORMAL,
        ResourcePriority.LOW,
        ResourcePriority.BATCH,
      ];
      const minIndex = priorityOrder.indexOf(criteria.minPriority);
      results = results.filter(r => priorityOrder.indexOf(r.priority) <= minIndex);
    }

    return results;
  }

  // ==========================================================================
  // KV-Cache Sharing
  // ==========================================================================

  /**
   * Set the shared KV-cache pool
   */
  setKVCachePool(pool: KVAnchorPool): void {
    this.kvCachePool = pool;
    this.emit('kv_cache_pool_registered');
  }

  /**
   * Share a KV-cache anchor across systems
   */
  async shareKVAnchor(
    segment: KVCacheSegment,
    embedding: number[],
    owner: 'microbiome' | 'core'
  ): Promise<SharedResource<KVAnchor>> {
    if (!this.kvCachePool) {
      throw new Error('KV-cache pool not initialized');
    }

    // Create anchor in shared pool
    const anchor = await this.kvCachePool.createAnchor(segment, embedding);

    // Register as shared resource
    const resource = await this.registerResource(
      ResourceType.KV_CACHE,
      anchor,
      owner,
      {
        priority: ResourcePriority.HIGH,
        metadata: {
          layerId: segment.layerId,
          segmentId: segment.segmentId,
          agentId: segment.metadata.agentId,
        },
      }
    );

    this.emit('kv_anchor_shared', {
      anchorId: anchor.anchorId,
      owner,
      resource: resource.id,
    });

    return resource as SharedResource<KVAnchor>;
  }

  /**
   * Find similar KV anchors across systems
   */
  async findSimilarKVAnchors(
    queryEmbedding: number[],
    layerId: number,
    threshold?: number,
    maxResults?: number
  ): Promise<AnchorMatch[]> {
    if (!this.kvCachePool) {
      throw new Error('KV-cache pool not initialized');
    }

    const anchors = this.kvCachePool.findSimilarAnchors(
      queryEmbedding,
      layerId,
      threshold
    );

    // Convert to AnchorMatch format
    return anchors.map(anchor => ({
      anchor,
      similarity: this.cosineSimilarity(queryEmbedding, anchor.embedding),
      tokenOverlap: 0,
      positionalDeviation: 0,
    }));
  }

  /**
   * Get KV-cache sharing statistics
   */
  getKVCacheStats(): {
    totalAnchors: number;
    sharedAnchors: number;
    avgCompressionRatio: number;
    totalBytesSaved: number;
  } {
    if (!this.kvCachePool) {
      return {
        totalAnchors: 0,
        sharedAnchors: 0,
        avgCompressionRatio: 0,
        totalBytesSaved: 0,
      };
    }

    const poolStats = this.kvCachePool.getStats();
    const sharedAnchors = this.findResources(ResourceType.KV_CACHE);

    return {
      totalAnchors: poolStats.totalAnchors,
      sharedAnchors: sharedAnchors.length,
      avgCompressionRatio: poolStats.avgCompressionRatio,
      totalBytesSaved: sharedAnchors.reduce((sum, r) => sum + r.sizeBytes, 0),
    };
  }

  // ==========================================================================
  // Embedding Space Unification
  // ==========================================================================

  /**
   * Set the shared embedding space (BES)
   */
  setEmbeddingSpace(bes: BES): void {
    this.embeddingSpace = bes;
    this.emit('embedding_space_registered');
  }

  /**
   * Create a shared pollen grain
   */
  async createSharedPollenGrain(
    embedding: number[],
    gardenerId: string,
    owner: 'microbiome' | 'core',
    privacyTier?: PrivacyTier
  ): Promise<SharedResource<PollenGrain>> {
    if (!this.embeddingSpace) {
      throw new Error('Embedding space not initialized');
    }

    const grain = await this.embeddingSpace.createGrain(
      embedding,
      gardenerId,
      { privacyTier }
    );

    const resource = await this.registerResource(
      ResourceType.EMBEDDING,
      grain,
      owner,
      {
        privacyTier: grain.privacyTier,
        metadata: {
          dimensionality: grain.dimensionality,
          sourceLogCount: grain.sourceLogCount,
        },
      }
    );

    this.emit('pollen_grain_shared', {
      grainId: grain.id,
      owner,
      resource: resource.id,
    });

    return resource as SharedResource<PollenGrain>;
  }

  /**
   * Map embeddings between microbiome and core spaces
   */
  async mapEmbeddings(
    microbiomeEmbedding: number[],
    coreEmbedding: number[]
  ): Promise<EmbeddingMapping> {
    const id = uuidv4();
    const now = Date.now();

    // Learn transformation matrix (simplified)
    const transformMatrix = this.learnTransformMatrix(
      microbiomeEmbedding,
      coreEmbedding
    );

    const mapping: EmbeddingMapping = {
      microbiomeSpace: microbiomeEmbedding,
      coreSpace: coreEmbedding,
      transformMatrix,
      confidence: this.computeMappingConfidence(microbiomeEmbedding, coreEmbedding),
      lastUpdated: now,
    };

    this.embeddingMappings.set(id, mapping);

    this.emit('embedding_mapped', { mappingId: id });

    return mapping;
  }

  /**
   * Transform embedding from one space to another
   */
  transformEmbedding(
    embedding: number[],
    mapping: EmbeddingMapping,
    direction: 'microbiome_to_core' | 'core_to_microbiome'
  ): number[] {
    const matrix = direction === 'microbiome_to_core'
      ? mapping.transformMatrix
      : this.transposeMatrix(mapping.transformMatrix);

    return this.applyTransform(embedding, matrix);
  }

  /**
   * Find similar pollen grains across systems
   */
  async findSimilarPollenGrains(
    query: number[],
    threshold?: number,
    limit?: number
  ): Promise<Array<{ grain: PollenGrain; similarity: number }>> {
    if (!this.embeddingSpace) {
      throw new Error('Embedding space not initialized');
    }

    const grains = this.embeddingSpace.findSimilar(query, threshold, limit);
    return grains.map(grain => ({
      grain,
      similarity: this.cosineSimilarity(query, grain.embedding),
    }));
  }

  // ==========================================================================
  // World Model Joint Learning
  // ==========================================================================

  /**
   * Register a world model for sharing
   */
  async registerWorldModel(
    modelId: string,
    model: WorldModel,
    owner: 'microbiome' | 'core'
  ): Promise<void> {
    this.worldModels.set(modelId, model);

    await this.registerResource(
      ResourceType.WORLD_MODEL,
      model,
      owner,
      {
        priority: ResourcePriority.HIGH,
        metadata: { modelId },
      }
    );

    this.emit('world_model_registered', { modelId, owner });
  }

  /**
   * Train world models jointly across systems
   */
  async jointWorldModelTraining(
    microbiomeBatch: TrainingBatch,
    coreBatch: TrainingBatch,
    options?: {
      microbiomeWeight?: number;
      coreWeight?: number;
      syncAfterTraining?: boolean;
    }
  ): Promise<{
    microbiomeLoss: number;
    coreLoss: number;
    jointLoss: number;
    convergenceScore: number;
  }> {
    const microWeight = options?.microbiomeWeight || 0.5;
    const coreWeight = options?.coreWeight || 0.5;

    let microbiomeLoss = 0;
    let coreLoss = 0;
    let totalLoss = 0;
    let modelsTrained = 0;

    // Train all registered world models
    for (const [modelId, model] of this.worldModels) {
      const isMicrobiome = modelId.startsWith('microbiome');
      const batch = isMicrobiome ? microbiomeBatch : coreBatch;
      const weight = isMicrobiome ? microWeight : coreWeight;

      const result = model.train(batch);
      const weightedLoss = result.totalLoss * weight;

      if (isMicrobiome) {
        microbiomeLoss = result.totalLoss;
      } else {
        coreLoss = result.totalLoss;
      }

      totalLoss += weightedLoss;
      modelsTrained++;
    }

    const jointLoss = totalLoss / modelsTrained;
    const convergenceScore = this.computeConvergenceScore(microbiomeLoss, coreLoss);

    // Sync models if requested
    if (options?.syncAfterTraining) {
      await this.syncWorldModels();
    }

    this.emit('joint_training_complete', {
      microbiomeLoss,
      coreLoss,
      jointLoss,
      convergenceScore,
    });

    return {
      microbiomeLoss,
      coreLoss,
      jointLoss,
      convergenceScore,
    };
  }

  /**
   * Generate joint dream episodes
   */
  async jointDreaming(
    startStates: number[][],
    horizon?: number
  ): Promise<{
    microbiomeDreams: DreamEpisode[];
    coreDreams: DreamEpisode[];
    fusedDreams: DreamEpisode[];
  }> {
    const microbiomeDreams: DreamEpisode[] = [];
    const coreDreams: DreamEpisode[] = [];

    // Generate dreams from each system
    for (const [modelId, model] of this.worldModels) {
      const isMicrobiome = modelId.startsWith('microbiome');
      const dreams = model.dreamBatch(startStates, horizon);

      if (isMicrobiome) {
        microbiomeDreams.push(...dreams);
      } else {
        coreDreams.push(...dreams);
      }
    }

    // Fuse dreams from both systems
    const fusedDreams = this.fuseDreamEpisodes(microbiomeDreams, coreDreams);

    this.emit('joint_dreaming_complete', {
      microbiomeCount: microbiomeDreams.length,
      coreCount: coreDreams.length,
      fusedCount: fusedDreams.length,
    });

    return {
      microbiomeDreams,
      coreDreams,
      fusedDreams,
    };
  }

  /**
   * Synchronize world models across systems
   */
  async syncWorldModels(): Promise<void> {
    if (this.syncInProgress) {
      this.pendingSyncs.add('world_models');
      return;
    }

    this.syncInProgress = true;
    try {
      const microbiomeModels = Array.from(this.worldModels.entries())
        .filter(([id]) => id.startsWith('microbiome'));
      const coreModels = Array.from(this.worldModels.entries())
        .filter(([id]) => id.startsWith('core'));

      for (const [microId, microModel] of microbiomeModels) {
        for (const [coreId, coreModel] of coreModels) {
          const syncKey = `${microId}-${coreId}`;
          const existingSync = this.worldModelSyncs.get(syncKey);

          // Compute divergence
          const microState = microModel.getState();
          const coreState = coreModel.getState();
          const divergence = Math.abs(microState.totalLoss - coreState.totalLoss);

          const sync: WorldModelSync = {
            microbiomeVersion: microState.trainingSteps,
            coreVersion: coreState.trainingSteps,
            lastSyncTime: Date.now(),
            syncPending: divergence > 0.1,
            divergentSamples: Math.floor(divergence * 100),
            convergenceScore: 1 - Math.min(1, divergence),
          };

          this.worldModelSyncs.set(syncKey, sync);

          // Update models toward convergence
          if (sync.syncPending && sync.convergenceScore > 0.8) {
            await this.convergeWorldModels(microModel, coreModel);
          }
        }
      }

      this.lastSyncTime = Date.now();
      this.emit('world_models_synced');
    } finally {
      this.syncInProgress = false;
    }
  }

  // ==========================================================================
  // Value Network Fusion
  // ==========================================================================

  /**
   * Register a value network for sharing
   */
  async registerValueNetwork(
    networkId: string,
    network: ValueNetwork,
    owner: 'microbiome' | 'core'
  ): Promise<void> {
    this.valueNetworks.set(networkId, network);

    await this.registerResource(
      ResourceType.VALUE_NETWORK,
      network,
      owner,
      {
        priority: ResourcePriority.HIGH,
        metadata: { networkId },
      }
    );

    this.emit('value_network_registered', { networkId, owner });
  }

  /**
   * Fuse predictions from multiple value networks
   */
  fuseValuePredictions(
    state: Map<string, unknown> | unknown,
    networks?: string[]
  ): {
    fusedValue: number;
    confidence: number;
    individualPredictions: Array<{
      networkId: string;
      value: number;
      confidence: number;
      weight: number;
    }>;
  } {
    const networksToUse = networks
      ? networks.map(id => this.valueNetworks.get(id)).filter((n): n is ValueNetwork => n !== undefined)
      : Array.from(this.valueNetworks.values());

    if (networksToUse.length === 0) {
      return {
        fusedValue: 0,
        confidence: 0,
        individualPredictions: [],
      };
    }

    const individualPredictions = networksToUse.map(network => {
      const prediction = network.predict(state);
      const isMicrobiome = network.constructor.name.includes('Microbiome');
      const baseWeight = isMicrobiome
        ? this.valueNetworkFusion.microbiomeWeight
        : this.valueNetworkFusion.coreWeight;

      let weight = baseWeight;
      if (this.valueNetworkFusion.useUncertaintyWeighting) {
        // Adjust weight based on prediction confidence
        weight *= prediction.confidence;
      }

      return {
        networkId: network.constructor.name,
        value: prediction.value,
        confidence: prediction.confidence,
        weight,
      };
    });

    // Normalize weights
    const totalWeight = individualPredictions.reduce((sum, p) => sum + p.weight, 0);
    const normalizedPredictions = individualPredictions.map(p => ({
      ...p,
      weight: p.weight / totalWeight,
    }));

    // Compute fused value
    const fusedValue = normalizedPredictions.reduce(
      (sum, p) => sum + p.value * p.weight,
      0
    );

    // Compute overall confidence (weighted average)
    const confidence = normalizedPredictions.reduce(
      (sum, p) => sum + p.confidence * p.weight,
      0
    );

    return {
      fusedValue,
      confidence,
      individualPredictions: normalizedPredictions,
    };
  }

  /**
   * Update value network fusion configuration
   */
  updateValueNetworkFusion(config: Partial<ValueNetworkFusion>): void {
    this.valueNetworkFusion = { ...this.valueNetworkFusion, ...config };
    this.emit('value_network_fusion_updated', this.valueNetworkFusion);
  }

  /**
   * Record trajectories for joint training
   */
  recordJointTrajectories(trajectories: Trajectory[]): void {
    for (const trajectory of trajectories) {
      // Distribute to all value networks
      for (const network of this.valueNetworks.values()) {
        network.addTrajectory(trajectory);
      }
    }

    this.emit('joint_trajectories_recorded', {
      count: trajectories.length,
    });
  }

  // ==========================================================================
  // Memory Synchronization
  // ==========================================================================

  /**
   * Queue a memory for synchronization
   */
  async syncMemory(
    source: 'microbiome' | 'core',
    memoryId: string,
    content: unknown
  ): Promise<MemorySyncEntry> {
    const id = uuidv4();
    const contentHash = this.computeHash(content);

    const entry: MemorySyncEntry = {
      id,
      source,
      memoryId,
      contentHash,
      timestamp: Date.now(),
      syncStatus: 'pending',
    };

    this.memorySyncQueue.push(entry);

    // Process sync queue if not already processing
    if (this.memorySyncQueue.length === 1) {
      this.processMemorySyncQueue();
    }

    return entry;
  }

  /**
   * Process the memory synchronization queue
   */
  private async processMemorySyncQueue(): Promise<void> {
    while (this.memorySyncQueue.length > 0) {
      const entry = this.memorySyncQueue[0];

      try {
        // Check for conflicts
        const conflict = this.findMemoryConflict(entry);
        if (conflict) {
          entry.syncStatus = 'conflict';
          this.resolveMemoryConflict(entry, conflict);
        } else {
          // Sync memory to other system
          await this.transferMemory(entry);
          entry.syncStatus = 'synced';
        }

        this.emit('memory_synced', entry);
      } catch (error) {
        entry.syncStatus = 'failed';
        this.emit('memory_sync_failed', { entry, error });
      }

      // Remove processed entry
      this.memorySyncQueue.shift();
    }
  }

  /**
   * Find conflicting memory entries
   */
  private findMemoryConflict(entry: MemorySyncEntry): MemorySyncEntry | undefined {
    const targetSystem = entry.source === 'microbiome' ? 'core' : 'microbiome';

    return this.memorySyncQueue.find(e =>
      e.source === targetSystem &&
      e.memoryId === entry.memoryId &&
      e.contentHash !== entry.contentHash
    );
  }

  /**
   * Resolve memory synchronization conflict
   */
  private resolveMemoryConflict(
    entry1: MemorySyncEntry,
    entry2: MemorySyncEntry
  ): void {
    switch (this.config.conflictResolution) {
      case 'timestamp':
        // Keep the most recent entry
        const winner = entry1.timestamp > entry2.timestamp ? entry1 : entry2;
        winner.syncStatus = 'synced';
        break;

      case 'priority':
        // Would use priority-based resolution if available
        entry1.syncStatus = 'synced';
        break;

      case 'merge':
        // Would merge both entries
        entry1.syncStatus = 'synced';
        entry2.syncStatus = 'synced';
        break;

      case 'manual':
        // Emit event for manual resolution
        this.emit('memory_conflict_requires_resolution', { entry1, entry2 });
        break;
    }
  }

  /**
   * Transfer memory between systems
   */
  private async transferMemory(entry: MemorySyncEntry): Promise<void> {
    // In production, this would use the bridge to actually transfer data
    if (this.protocolAdapter) {
      // Use protocol adapter for cross-system communication
      await this.protocolAdapter.sendMemory(
        entry.source === 'microbiome' ? 'core' : 'microbiome',
        entry.memoryId,
        entry.contentHash
      );
    }
  }

  // ==========================================================================
  // Federated Learning Coordination
  // ==========================================================================

  /**
   * Set the federated learning coordinator
   */
  setFederatedCoordinator(coordinator: FederatedLearningCoordinator): void {
    this.federatedCoordinator = coordinator;
    this.emit('federated_coordinator_registered');
  }

  /**
   * Participate in federated learning round
   */
  async participateInFederatedRound(
    colonyId: string,
    gradients: number[],
    options?: {
      sampleCount?: number;
      privacyTier?: PrivacyTier;
    }
  ): Promise<void> {
    if (!this.federatedCoordinator) {
      throw new Error('Federated coordinator not initialized');
    }

    const update: GradientUpdate = {
      colonyId,
      roundNumber: 0, // Will be filled by coordinator
      gradients,
      sampleCount: options?.sampleCount || 100,
      metadata: {
        agentId: colonyId,
        privacyTier: options?.privacyTier || this.config.defaultPrivacyTier,
        epsilonSpent: 0.1,
        deltaSpent: 1e-5,
        compressed: this.config.enableCompression,
        trainingLoss: 0,
      },
      timestamp: Date.now(),
    };

    await this.federatedCoordinator.submitGradients(update);

    this.emit('federated_round_participated', {
      colonyId,
      gradientCount: gradients.length,
    });
  }

  /**
   * Get federated learning status
   */
  getFederatedStatus(): {
    isActive: boolean;
    currentRound: number | null;
    participatingColonies: number;
    privacyBudgetUsed: number;
  } {
    if (!this.federatedCoordinator) {
      return {
        isActive: false,
        currentRound: null,
        participatingColonies: 0,
        privacyBudgetUsed: 0,
      };
    }

    const status = this.federatedCoordinator.getFederationStatus();
    const stats = this.federatedCoordinator.getStats();

    return {
      isActive: status.currentRound !== null,
      currentRound: status.globalRound,
      participatingColonies: status.activeColonies,
      privacyBudgetUsed: stats.totalPrivacyBudgetUsed,
    };
  }

  // ==========================================================================
  // Synchronization and Cleanup
  // ==========================================================================

  /**
   * Start automatic synchronization
   */
  private startAutoSync(): void {
    setInterval(async () => {
      if (!this.syncInProgress) {
        await this.performSync();
      }
    }, this.config.syncInterval);
  }

  /**
   * Perform full synchronization across all resources
   */
  private async performSync(): Promise<void> {
    if (this.syncInProgress) return;

    this.syncInProgress = true;
    try {
      // Sync world models
      await this.syncWorldModels();

      // Process memory sync queue
      await this.processMemorySyncQueue();

      // Sync KV-cache anchors
      if (this.kvCachePool) {
        this.kvCachePool.cleanup();
      }

      // Record metrics
      if (this.config.enableMetrics) {
        this.recordMetrics();
      }

      this.lastSyncTime = Date.now();
      this.emit('sync_complete', { timestamp: this.lastSyncTime });
    } finally {
      this.syncInProgress = false;

      // Process any pending syncs
      if (this.pendingSyncs.size > 0) {
        this.pendingSyncs.clear();
        setTimeout(() => this.performSync(), 100);
      }
    }
  }

  /**
   * Cleanup expired resources and cache entries
   */
  private cleanup(): void {
    const now = Date.now();

    // Clean up expired cache entries
    if (this.config.enableCaching) {
      for (const [key, cached] of this.resourceCache.entries()) {
        if (cached.expiresAt < now) {
          this.resourceCache.delete(key);
        }
      }
    }

    // Clean up old metrics
    if (this.config.enableMetrics) {
      const cutoff = now - this.config.metricsRetentionMs;
      this.metricsHistory = this.metricsHistory.filter(
        m => m.timestamp > cutoff
      );
    }

    // Clean up old allocations
    for (const [id, allocation] of this.allocations.entries()) {
      if (allocation.status === AllocationStatus.RELEASED &&
          allocation.releasedAt &&
          now - allocation.releasedAt > 3600000) { // 1 hour
        this.allocations.delete(id);
      }
    }

    this.emit('cleanup_complete', {
      resourcesCleaned: this.resources.size,
      allocationsCleaned: this.allocations.size,
      cacheEntries: this.resourceCache.size,
    });
  }

  // ==========================================================================
  // Statistics and Monitoring
  // ==========================================================================

  /**
   * Get comprehensive statistics
   */
  getStats(): {
    resources: Map<ResourceType, ResourceStats>;
    allocations: {
      total: number;
      active: number;
      byType: Map<ResourceType, number>;
    };
    cache: {
      size: number;
      hitRate: number;
      avgAccessTime: number;
    };
    sync: {
      lastSyncTime: number;
      syncInProgress: boolean;
      pendingSyncs: number;
    };
    kvCache: ReturnType<SharedResourcePool['getKVCacheStats']>;
    federated: ReturnType<SharedResourcePool['getFederatedStatus']>;
  } {
    const allocationsByType = new Map<ResourceType, number>();
    for (const type of Object.values(ResourceType)) {
      allocationsByType.set(
        type,
        Array.from(this.allocations.values()).filter(a => a.type === type).length
      );
    }

    return {
      resources: new Map(this.stats),
      allocations: {
        total: this.allocations.size,
        active: Array.from(this.allocations.values())
          .filter(a => a.status === AllocationStatus.IN_USE).length,
        byType: allocationsByType,
      },
      cache: {
        size: this.resourceCache.size,
        hitRate: this.computeCacheHitRate(),
        avgAccessTime: this.computeAvgAccessTime(),
      },
      sync: {
        lastSyncTime: this.lastSyncTime,
        syncInProgress: this.syncInProgress,
        pendingSyncs: this.pendingSyncs.size,
      },
      kvCache: this.getKVCacheStats(),
      federated: this.getFederatedStatus(),
    };
  }

  /**
   * Get metrics history
   */
  getMetricsHistory(limit?: number): Array<{
    timestamp: number;
    stats: Map<ResourceType, ResourceStats>;
  }> {
    if (limit) {
      return this.metricsHistory.slice(-limit);
    }
    return [...this.metricsHistory];
  }

  // ==========================================================================
  // Private Helper Methods
  // ==========================================================================

  private initializeStats(): void {
    for (const type of Object.values(ResourceType)) {
      this.stats.set(type, {
        type,
        totalAllocations: 0,
        activeAllocations: 0,
        failedAllocations: 0,
        preemptedAllocations: 0,
        totalBytesTransferred: 0,
        avgAllocationTime: 0,
        avgUtilization: 0,
        peakUtilization: 0,
      });
    }
  }

  private updateStats(
    type: ResourceType,
    updates: Partial<ResourceStats>
  ): void {
    const stats = this.stats.get(type);
    if (stats) {
      Object.assign(stats, updates);

      // Update peak utilization
      const currentUtil = stats.activeAllocations / this.config.maxConcurrentAllocations;
      if (currentUtil > stats.peakUtilization) {
        stats.peakUtilization = currentUtil;
      }
    }
  }

  private recordMetrics(): void {
    const snapshot = new Map(this.stats);
    this.metricsHistory.push({
      timestamp: Date.now(),
      stats: snapshot,
    });
  }

  private checkResourceLimit(type: ResourceType, sizeBytes: number): boolean {
    switch (type) {
      case ResourceType.KV_CACHE:
        return sizeBytes <= this.config.maxKVCacheSize;
      case ResourceType.EMBEDDING:
        return sizeBytes <= this.config.maxEmbeddingSize;
      case ResourceType.WORLD_MODEL:
        return this.worldModels.size < this.config.maxWorldModels;
      case ResourceType.VALUE_NETWORK:
        return this.valueNetworks.size < this.config.maxValueNetworks;
      case ResourceType.MEMORY:
        return sizeBytes <= this.config.maxMemorySize;
      default:
        return true;
    }
  }

  private estimateResourceSize(type: ResourceType, resource: unknown): number {
    // Rough estimation - in production, use actual serialization
    return JSON.stringify(resource).length * 2; // Assume 2 bytes per char
  }

  private preemptAllocations(
    requester: 'microbiome' | 'core',
    priority: ResourcePriority
  ): boolean {
    if (!this.config.preemptionEnabled) return false;

    const priorityOrder = [
      ResourcePriority.BATCH,
      ResourcePriority.LOW,
      ResourcePriority.NORMAL,
      ResourcePriority.HIGH,
      ResourcePriority.CRITICAL,
    ];

    const requestPriorityIndex = priorityOrder.indexOf(priority);

    // Find lower priority allocations to preempt
    for (const [id, allocation] of this.allocations.entries()) {
      if (allocation.status === AllocationStatus.IN_USE) {
        const allocPriorityIndex = priorityOrder.indexOf(allocation.priority);
        if (allocPriorityIndex < requestPriorityIndex) {
          // Preempt this allocation
          allocation.status = AllocationStatus.PREEMPTED;
          this.updateStats(allocation.type, { preemptedAllocations: 1 });
          this.emit('allocation_preempted', { allocationId: id });
          return true;
        }
      }
    }

    return false;
  }

  private cacheResource(resource: SharedResource): void {
    if (this.resourceCache.size >= this.config.cacheSize) {
      // Evict oldest entry
      const oldestKey = this.resourceCache.keys().next().value;
      this.resourceCache.delete(oldestKey);
    }

    this.resourceCache.set(resource.id, {
      resource,
      expiresAt: Date.now() + this.config.cacheTTLMs,
    });
  }

  private computeCacheHitRate(): number {
    // Simplified - in production, track actual hits/misses
    return 0.8;
  }

  private computeAvgAccessTime(): number {
    // Simplified - in production, track actual access times
    return 10; // 10ms
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0;

    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const normA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const normB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));

    if (normA === 0 || normB === 0) return 0;

    return dotProduct / (normA * normB);
  }

  private learnTransformMatrix(
    from: number[],
    to: number[]
  ): number[][] {
    // Simplified transformation learning
    // In production, use proper linear regression
    const dim = Math.min(from.length, to.length);
    const matrix: number[][] = [];

    for (let i = 0; i < dim; i++) {
      const row: number[] = [];
      for (let j = 0; j < dim; j++) {
        row.push(i === j ? 1 : 0); // Identity matrix as baseline
      }
      matrix.push(row);
    }

    return matrix;
  }

  private transposeMatrix(matrix: number[][]): number[][] {
    const rows = matrix.length;
    const cols = matrix[0].length;
    const transposed: number[][] = [];

    for (let j = 0; j < cols; j++) {
      const row: number[] = [];
      for (let i = 0; i < rows; i++) {
        row.push(matrix[i][j]);
      }
      transposed.push(row);
    }

    return transposed;
  }

  private applyTransform(vector: number[], matrix: number[][]): number[] {
    const result: number[] = [];

    for (const row of matrix) {
      let sum = 0;
      for (let i = 0; i < Math.min(vector.length, row.length); i++) {
        sum += vector[i] * row[i];
      }
      result.push(sum);
    }

    return result;
  }

  private computeMappingConfidence(from: number[], to: number[]): number {
    const similarity = this.cosineSimilarity(from, to);
    return similarity;
  }

  private computeConvergenceScore(loss1: number, loss2: number): number {
    const diff = Math.abs(loss1 - loss2);
    return Math.max(0, 1 - diff / Math.max(loss1, loss2));
  }

  private async convergeWorldModels(
    model1: WorldModel,
    model2: WorldModel
  ): Promise<void> {
    // In production, implement proper model convergence
    // For now, just emit an event
    this.emit('world_models_converged', {
      model1: model1.constructor.name,
      model2: model2.constructor.name,
    });
  }

  private fuseDreamEpisodes(
    dreams1: DreamEpisode[],
    dreams2: DreamEpisode[]
  ): DreamEpisode[] {
    // Simplified fusion - in production, use more sophisticated methods
    const fused: DreamEpisode[] = [];

    const minLen = Math.min(dreams1.length, dreams2.length);
    for (let i = 0; i < minLen; i++) {
      const dream1 = dreams1[i];
      const dream2 = dreams2[i];

      // Average rewards and values
      const avgRewards = dream1.rewards.map((r, j) =>
        (r + dream2.rewards[j]) / 2
      );
      const avgValues = dream1.values.map((v, j) =>
        (v + dream2.values[j]) / 2
      );

      fused.push({
        ...dream1,
        id: uuidv4(),
        rewards: avgRewards,
        values: avgValues,
        totalReward: avgRewards.reduce((a, b) => a + b, 0),
        totalValue: avgValues.reduce((a, b) => a + b, 0),
      });
    }

    return fused;
  }

  private computeHash(content: unknown): string {
    const str = JSON.stringify(content);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(16);
  }

  // ==========================================================================
  // Resource Lifecycle
  // ==========================================================================

  /**
   * Clear all resources and reset state
   */
  clear(): void {
    this.resources.clear();
    this.allocations.clear();
    this.worldModels.clear();
    this.valueNetworks.clear();
    this.embeddingMappings.clear();
    this.worldModelSyncs.clear();
    this.memorySyncQueue = [];
    this.resourceCache.clear();
    this.metricsHistory = [];
    this.pendingSyncs.clear();
    this.initializeStats();

    this.emit('cleared');
  }

  /**
   * Destroy the resource pool and release all resources
   */
  destroy(): void {
    this.clear();
    this.removeAllListeners();
  }
}

// ============================================================================
// Factory Functions
// ============================================================================

/**
 * Create a shared resource pool with default configuration
 */
export function createSharedResourcePool(
  config?: Partial<ResourceShareConfig>,
  bridge?: MicrobiomeBridge,
  protocolAdapter?: ProtocolAdapter
): SharedResourcePool {
  return new SharedResourcePool(config, bridge, protocolAdapter);
}

/**
 * Create a shared resource pool optimized for low-latency operations
 */
export function createLowLatencyResourcePool(
  bridge?: MicrobiomeBridge,
  protocolAdapter?: ProtocolAdapter
): SharedResourcePool {
  return new SharedResourcePool({
    allocationPolicy: 'priority',
    preemptionEnabled: true,
    autoSyncEnabled: false, // Manual sync for lower latency
    enableCaching: true,
    cacheSize: 2000,
    cacheTTLMs: 600000, // 10 minutes
  }, bridge, protocolAdapter);
}

/**
 * Create a shared resource pool optimized for high-throughput operations
 */
export function createHighThroughputResourcePool(
  bridge?: MicrobiomeBridge,
  protocolAdapter?: ProtocolAdapter
): SharedResourcePool {
  return new SharedResourcePool({
    allocationPolicy: 'fair_share',
    preemptionEnabled: false,
    maxConcurrentAllocations: 1000,
    autoSyncEnabled: true,
    enableCaching: true,
    cacheSize: 5000,
  }, bridge, protocolAdapter);
}
