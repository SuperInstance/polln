# POLLN System Blueprint

> **Purpose**: Implementation guide with code examples, edge cases, and test scenarios for POLLN implementation agents.
>
> **Audience**: glm-4.7 implementation agents and human developers.
>
> **Last Updated**: 2026-03-08

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Agent Implementation Guide](#2-agent-implementation-guide)
3. [Colony Implementation Guide](#3-colony-implementation-guide)
4. [Communication Implementation Guide](#4-communication-implementation-guide)
5. [Learning System Implementation Guide](#5-learning-system-implementation-guide)
6. [KV-Cache Implementation Guide](#6-kv-cache-implementation-guide)
7. [Distributed System Implementation Guide](#7-distributed-system-implementation-guide)
8. [Safety System Implementation Guide](#8-safety-system-implementation-guide)
9. [Edge Cases to Handle](#9-edge-cases-to-handle)
10. [Test Scenarios](#10-test-scenarios)

---

## 1. Getting Started

### 1.1 Project Structure

```
polln/
├── src/
│   ├── core/                 # Core library
│   │   ├── types.ts          # Type definitions
│   │   ├── agent.ts          # BaseAgent class
│   │   ├── agents.ts         # TaskAgent, RoleAgent, CoreAgent
│   │   ├── colony.ts         # Colony management
│   │   ├── protocol.ts       # SPORE protocol
│   │   ├── communication.ts  # A2A package system
│   │   ├── learning.ts       # Hebbian learning
│   │   ├── decision.ts       # Plinko layer
│   │   ├── kvanchor.ts       # KV-Cache anchors
│   │   ├── distributed/      # Distributed coordination
│   │   └── guardian/         # Safety system
│   ├── api/                  # WebSocket API
│   └── cli/                  # CLI tool
├── docs/
│   └── planning/             # Planning documents
└── tests/
```

### 1.2 Import Patterns

```typescript
// Core types and interfaces
import type {
  A2APackage,
  AgentConfig,
  AgentState,
  ColonyConfig,
  ColonyStats
} from './types.js';

// Core classes
import { BaseAgent } from './agent.js';
import { Colony } from './colony.js';
import { SPOREProtocol } from './protocol.js';
import { PlinkoLayer } from './decision.js';
import { HebbianLearning } from './learning.js';
import { KVAnchorPool } from './kvanchor.js';

// Enums
import { PrivacyLevel, SubsumptionLayer, TileCategory } from './types.js';
```

### 1.3 Common Patterns

#### Async Initialization Pattern

```typescript
class MyComponent implements IInitializable, IShutdownable {
  private initialized = false;
  private shutdown = false;

  async initialize(): Promise<void> {
    if (this.initialized) {
      throw new POLLNError(
        POLLNErrorCode.AGENT_INITIALIZATION_FAILED,
        'Already initialized'
      );
    }

    // Perform initialization
    await this.setupResources();

    this.initialized = true;
    this.shutdown = false;
  }

  async shutdown(): Promise<void> {
    if (this.shutdown) {
      return; // Idempotent shutdown
    }

    // Perform cleanup
    await this.cleanupResources();

    this.shutdown = true;
    this.initialized = false;
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  isShutdown(): boolean {
    return this.shutdown;
  }
}
```

#### Event Emitter Pattern

```typescript
import { EventEmitter } from 'events';

class MyEventEmitter extends EventEmitter {
  emitAgentRegistered(agentId: string, state: AgentState): void {
    this.emit('agent_registered', { agentId, state });
  }

  onAgentRegistered(handler: (event: AgentEvent) => void): void {
    this.on('agent_registered', handler);
  }
}
```

---

## 2. Agent Implementation Guide

### 2.1 Creating a Custom Agent

```typescript
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import type { AgentConfig, A2APackage } from './types.js';
import { PrivacyLevel, SubsumptionLayer, TileCategory } from './types.js';

/**
 * Custom agent implementation for specific tasks.
 */
class CustomAgent extends EventEmitter {
  public readonly id: string;
  public readonly category = TileCategory.EPHEMERAL;
  public readonly config: AgentConfig;

  protected state: Map<string, unknown> = new Map();
  protected valueFunction: number = 0.5;
  protected successCount: number = 0;
  protected failureCount: number = 0;
  protected lastActive: number = Date.now();

  constructor(config: AgentConfig) {
    super();
    this.id = config.id;
    this.config = config;
  }

  /**
   * Initialize the agent.
   * Must be called before process().
   */
  async initialize(): Promise<void> {
    this.setState('initializedAt', Date.now());
    this.setState('category', this.category);

    // Perform custom initialization
    await this.loadResources();

    this.emit('initialized', { agentId: this.id });
  }

  /**
   * Process input and produce output.
   * Core method - override in subclasses.
   */
  async process<T>(input: T): Promise<A2APackage<T>> {
    const startTime = Date.now();
    this.touch();

    try {
      // Execute the task
      const result = await this.executeTask(input);

      // Update metrics on success
      this.updateValueFunction(1);
      this.successCount++;

      // Create A2A package
      const pkg = this.createPackage(result, 'task_result');

      const executionTime = Date.now() - startTime;
      this.setState('lastExecutionTime', executionTime);

      this.emit('executed', { agentId: this.id, success: true, executionTime });

      return pkg as A2APackage<T>;
    } catch (error) {
      // Update metrics on failure
      this.updateValueFunction(-1);
      this.failureCount++;

      this.emit('error', { agentId: this.id, error });

      throw error;
    }
  }

  /**
   * Shutdown the agent.
   * Must be idempotent.
   */
  async shutdown(): Promise<void> {
    // Cleanup resources
    await this.cleanupResources();

    this.setState('shutdownAt', Date.now());
    this.emit('shutdown', { agentId: this.id });
  }

  /**
   * Execute the specific task.
   * Override this method in subclasses.
   */
  protected async executeTask<T>(input: T): Promise<T> {
    // Default implementation - override in subclasses
    return input;
  }

  /**
   * Check if agent should be terminated.
   */
  shouldTerminate(): boolean {
    const initializedAt = this.getState<number>('initializedAt') || Date.now();
    const age = Date.now() - initializedAt;
    const maxLifetime = 3600000; // 1 hour

    return age > maxLifetime || this.valueFunction < 0.1;
  }

  // State management helpers
  getState<K>(key: string): K | undefined {
    return this.state.get(key) as K;
  }

  setState<K>(key: string, value: K): void {
    this.state.set(key, value);
  }

  updateValueFunction(reward: number): void {
    // Bounded update: valueFunction in [0, 1]
    this.valueFunction = Math.max(0, Math.min(1,
      this.valueFunction + 0.1 * (reward - 0.5)
    ));
  }

  touch(): void {
    this.lastActive = Date.now();
  }

  // Private helpers
  private createPackage<T>(payload: T, type: string): A2APackage<T> {
    return {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.id,
      receiverId: 'colony',
      type,
      payload,
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.COLONY,
      layer: SubsumptionLayer.HABITUAL,
    };
  }

  private async loadResources(): Promise<void> {
    // Custom resource loading
  }

  private async cleanupResources(): Promise<void> {
    // Custom resource cleanup
  }
}
```

### 2.2 Creating a Role Agent with Succession

```typescript
/**
 * Role agent with knowledge transfer capability.
 */
class RoleAgentImpl extends EventEmitter {
  public readonly id: string;
  public readonly category = TileCategory.ROLE;

  private successor: RoleAgentImpl | null = null;
  private knowledgeAccumulated: Map<string, unknown> = new Map();
  private performanceWindow: number[] = [];

  // ... constructor and other methods ...

  /**
   * Set successor for knowledge transfer.
   */
  setSuccessor(successor: RoleAgentImpl): void {
    this.successor = successor;
    this.emit('successor_set', { agentId: this.id, successorId: successor.id });
  }

  /**
   * Transfer knowledge to successor on shutdown.
   */
  async shutdown(): Promise<void> {
    if (this.successor) {
      await this.transferKnowledge(this.successor);
    }

    this.setState('shutdownAt', Date.now());
    this.emit('shutdown', { agentId: this.id });
  }

  /**
   * Extract knowledge for external use.
   */
  extractKnowledge(): Map<string, unknown> {
    return new Map(this.knowledgeAccumulated);
  }

  /**
   * Internal knowledge transfer.
   */
  private async transferKnowledge(successor: RoleAgentImpl): Promise<void> {
    // Transfer accumulated patterns
    for (const [key, value] of this.knowledgeAccumulated) {
      successor.receiveKnowledge(key, value);
    }

    // Transfer performance history
    successor.receivePerformanceHistory(this.performanceWindow);

    // Transfer value function (karmic record)
    successor.receiveValueFunction(this.valueFunction);

    this.emit('knowledge_transferred', {
      agentId: this.id,
      successorId: successor.id,
      patternsTransferred: this.knowledgeAccumulated.size
    });
  }

  receiveKnowledge(key: string, value: unknown): void {
    this.knowledgeAccumulated.set(key, value);
  }

  receivePerformanceHistory(history: number[]): void {
    this.performanceWindow = [...history];
  }

  receiveValueFunction(value: number): void {
    this.valueFunction = value;
  }
}
```

### 2.3 Creating a Core Agent with Backup

```typescript
/**
 * Core agent with backup and recovery.
 */
class CoreAgentImpl extends EventEmitter {
  public readonly category = TileCategory.CORE;

  private backup: Map<string, unknown> = new Map();
  private lastBackupTime: number = 0;
  private backupIntervalMs: number = 3600000; // 1 hour

  /**
   * Initialize with recovery attempt.
   */
  async initialize(): Promise<void> {
    // Attempt recovery from backup
    const recovered = this.attemptRecovery();

    if (recovered) {
      this.emit('recovered', { agentId: this.id });
    }

    await super.initialize();
  }

  /**
   * Process with periodic backup.
   */
  async process<T>(input: T): Promise<A2APackage<T>> {
    const result = await super.process(input);

    // Create periodic backup
    if (Date.now() - this.lastBackupTime > this.backupIntervalMs) {
      this.createBackup();
    }

    return result;
  }

  /**
   * Create backup of current state.
   */
  createBackup(): void {
    this.backup = new Map(this.state);
    this.backup.set('valueFunction', this.valueFunction);
    this.backup.set('successCount', this.successCount);
    this.backup.set('failureCount', this.failureCount);
    this.lastBackupTime = Date.now();

    this.emit('backup_created', {
      agentId: this.id,
      backupSize: this.backup.size
    });
  }

  /**
   * Attempt recovery from backup.
   */
  private attemptRecovery(): boolean {
    if (this.backup.size === 0) {
      return false;
    }

    // Restore state from backup
    for (const [key, value] of this.backup) {
      if (key === 'valueFunction') {
        this.valueFunction = value as number;
      } else if (key === 'successCount') {
        this.successCount = value as number;
      } else if (key === 'failureCount') {
        this.failureCount = value as number;
      } else {
        this.state.set(key, value);
      }
    }

    return true;
  }

  /**
   * Core agents rarely terminate.
   */
  shouldTerminate(): boolean {
    // Only terminate on critical failure (>80% failure rate)
    const failureRate = this.failureCount / (this.successCount + this.failureCount + 1);
    return failureRate > 0.8;
  }
}
```

---

## 3. Colony Implementation Guide

### 3.1 Creating and Managing a Colony

```typescript
import { Colony } from './colony.js';
import type { ColonyConfig, AgentConfig } from './types.js';

// Create colony configuration
const colonyConfig: ColonyConfig = {
  id: 'colony-001',
  gardenerId: 'user-001',
  name: 'Primary Colony',
  maxAgents: 100,
  resourceBudget: {
    totalCompute: 1000,  // CPU units
    totalMemory: 8192,   // MB
    totalNetwork: 100,   // Mbps
  },
};

// Initialize colony
const colony = new Colony(colonyConfig);

// Register an agent
const agentConfig: AgentConfig = {
  id: 'agent-001',
  typeId: 'code-reviewer',
  categoryId: TileCategory.ROLE,
  modelFamily: 'gpt-4',
  defaultParams: { temperature: 0.7 },
  inputTopics: ['code:submit'],
  outputTopic: 'code:review',
  minExamples: 10,
  requiresWorldModel: false,
};

const agentState = colony.registerAgent(agentConfig);
console.log('Agent registered:', agentState.id);

// Activate the agent
colony.activateAgent('agent-001');

// Get colony statistics
const stats = await colony.getStats();
console.log('Colony stats:', stats);

// Record execution result
colony.recordResult('agent-001', true, 150); // success, 150ms latency

// Deactivate agent
colony.deactivateAgent('agent-001');

// Unregister agent
colony.unregisterAgent('agent-001');
```

### 3.2 Distributed Colony Setup

```typescript
import { Colony } from './colony.js';

const distributedConfig: ColonyConfig = {
  id: 'distributed-colony-001',
  gardenerId: 'user-001',
  name: 'Distributed Colony',
  maxAgents: 500,
  resourceBudget: {
    totalCompute: 5000,
    totalMemory: 32768,
    totalNetwork: 1000,
  },
  distributed: true,
  distributedConfig: {
    backend: 'redis',
    connectionString: 'redis://localhost:6379',
    nodeId: 'node-001',
  },
};

const colony = new Colony(distributedConfig);

// Listen for distributed events
colony.on('distributed_connected', (event) => {
  console.log('Connected to distributed backend:', event.backend);
});

colony.on('node_discovered', (event) => {
  console.log('New node discovered:', event.nodeId);
});

colony.on('pattern_received', (data) => {
  console.log('Pattern received from federation:', data);
});
```

### 3.3 Colony Event Handling

```typescript
// Set up event listeners
colony.on('agent_registered', ({ agentId, state }) => {
  console.log(`Agent ${agentId} registered with value ${state.valueFunction}`);
});

colony.on('agent_unregistered', ({ agentId }) => {
  console.log(`Agent ${agentId} unregistered`);
});

colony.on('agent_updated', ({ agentId, updates }) => {
  console.log(`Agent ${agentId} updated:`, updates);
});

// Query agents
const allAgents = colony.getAllAgents();
const activeAgents = colony.getActiveAgents();
const codeReviewers = colony.getAgentsByType('code-reviewer');

// Check diversity
const stats = await colony.getStats();
console.log(`Shannon Diversity Index: ${stats.shannonDiversity}`);
```

---

## 4. Communication Implementation Guide

### 4.1 Creating A2A Packages

```typescript
import { A2APackageSystem } from './communication.js';
import { PrivacyLevel, SubsumptionLayer } from './types.js';

const a2aSystem = new A2APackageSystem({
  historySize: 100,
  defaultPrivacyLevel: PrivacyLevel.COLONY,
  defaultLayer: SubsumptionLayer.HABITUAL,
});

// Create a package
const pkg = await a2aSystem.createPackage(
  'agent-001',           // senderId
  'agent-002',           // receiverId
  'code_review_request', // type
  { code: 'function foo() {}', language: 'javascript' }, // payload
  {
    privacyLevel: PrivacyLevel.COLONY,
    layer: SubsumptionLayer.DELIBERATE,
    parentIds: ['pkg-parent-001'], // Reference parent packages
  }
);

console.log('Created package:', pkg.id);
console.log('Causal chain:', pkg.causalChainId);
```

### 4.2 Tracing Causal Chains

```typescript
// Get the full causal chain for a package
const chain = a2aSystem.getCausalChain(pkg.id);
console.log('Causal chain length:', chain.length);

// Replay the chain (returns packages in order)
const replay = await a2aSystem.replayChain(pkg.id);
for (const step of replay) {
  console.log(`Step: ${step.type} from ${step.senderId} to ${step.receiverId}`);
}

// Get message history for an agent
const history = a2aSystem.getHistory('agent-001', 10);
console.log(`Last 10 messages for agent-001:`, history);
```

### 4.3 Using SPORE Protocol

```typescript
import { SPOREProtocol } from './protocol.js';

const protocol = new SPOREProtocol({
  distributed: false,
  backend: 'memory',
});

// Subscribe to a topic
const subscriptionId = await protocol.subscribe('code:submit', async (message) => {
  console.log('Received message:', message);
  // Process the message
});

// Publish a message
await protocol.publish('code:submit', {
  code: 'function bar() {}',
  language: 'javascript',
});

// Get recent messages
const recentMessages = protocol.getHistory('code:submit', 5);

// Unsubscribe
await protocol.unsubscribe(subscriptionId);

// Shutdown
await protocol.shutdown();
```

### 4.4 Distributed SPORE Protocol

```typescript
const distributedProtocol = new SPOREProtocol({
  distributed: true,
  backend: 'redis',
  connectionString: 'redis://localhost:6379',
  nodeId: 'node-001',
});

// Messages published here will be broadcast to all nodes
await distributedProtocol.publish('global:event', {
  type: 'agent_spawned',
  agentId: 'agent-001',
});
```

---

## 5. Learning System Implementation Guide

### 5.1 Hebbian Learning

```typescript
import { HebbianLearning } from './learning.js';

const hebbianLearning = new HebbianLearning({
  learningRate: 0.01,
  decayRate: 0.001,
  minWeight: 0.01,
  maxWeight: 1.0,
  traceLength: 100,
  traceDecay: 0.95,
  ojaNormalization: true,
});

// Update synapse weight based on co-activation
const weightChange = await hebbianLearning.updateSynapse(
  'agent-001',    // sourceId
  'agent-002',    // targetId
  0.8,            // preActivity (source activity level)
  0.9,            // postActivity (target activity level)
  0.5             // reward
);

console.log('Weight change:', weightChange);

// Get current weight
const weight = hebbianLearning.getWeight('agent-001', 'agent-002');
console.log('Current weight:', weight);

// Get all synapses for an agent
const agentSynapses = hebbianLearning.getAgentSynapses('agent-001');

// Decay all synapses (overnight optimization)
await hebbianLearning.decayAll();

// Prune weak synapses
const prunedCount = await hebbianLearning.pruneWeak(0.05);
console.log(`Pruned ${prunedCount} weak synapses`);

// Get statistics
const stats = hebbianLearning.getStats();
console.log('Learning stats:', stats);
```

### 5.2 Plinko Stochastic Selection

```typescript
import { PlinkoLayer } from './decision.js';

const plinkoLayer = new PlinkoLayer({
  temperature: 1.0,
  minTemperature: 0.1,
  decayRate: 0.001,
});

// Register discriminators (safety/quality checks)
plinkoLayer.registerDiscriminator('safety', (proposal) => {
  // Check if proposal passes safety constraints
  return proposal.confidence > 0.5 && proposal.bid > 0;
});

plinkoLayer.registerDiscriminator('quality', (proposal) => {
  // Check if proposal meets quality threshold
  return proposal.confidence > 0.7;
});

// Process proposals with stochastic selection
const proposals = [
  { agentId: 'agent-001', confidence: 0.9, bid: 0.8 },
  { agentId: 'agent-002', confidence: 0.85, bid: 0.9 },
  { agentId: 'agent-003', confidence: 0.75, bid: 0.7 },
];

const result = await plinkoLayer.process(proposals);
console.log('Selected agent:', result.selectedAgentId);
console.log('Temperature:', result.temperature);
console.log('Entropy:', result.entropy);
console.log('Was overridden:', result.wasOverridden);

// Get decision history
const history = plinkoLayer.getHistory(10);
```

### 5.3 Value Network (TD(lambda))

```typescript
import { ValueNetwork } from './valuenetwork.js';

const valueNetwork = new ValueNetwork({
  lambda: 0.95,
  gamma: 0.99,
  learningRate: 0.001,
});

// Predict value for a state-action pair
const prediction = valueNetwork.predict({
  state: [0.5, 0.3, 0.8],
  action: 'execute_task',
});
console.log('Value prediction:', prediction.value);
console.log('Confidence:', prediction.confidence);

// Update from a trajectory
valueNetwork.update(
  {
    states: [
      { state: [0.5, 0.3, 0.8], action: 'start' },
      { state: [0.6, 0.4, 0.7], action: 'process' },
      { state: [0.8, 0.5, 0.9], action: 'complete' },
    ],
    rewards: [0, 0.5, 1.0],
    terminal: true,
  },
  1.0  // final reward
);

// Train on batch of samples
valueNetwork.train([
  { state: { state: [0.5, 0.3], action: 'a1' }, target: 0.7 },
  { state: { state: [0.6, 0.4], action: 'a2' }, target: 0.8 },
]);
```

---

## 6. KV-Cache Implementation Guide

### 6.1 Creating and Using KV Anchors

```typescript
import {
  KVAnchorPool,
  AnchorMatcher,
  OffsetPredictor,
  AnchorPredictor,
} from './kvanchor.js';

// Initialize anchor pool
const anchorPool = new KVAnchorPool({
  maxAnchors: 1000,
  maxAgeMs: 24 * 60 * 60 * 1000, // 24 hours
  minQualityScore: 0.7,
  minCompressionRatio: 2.0,
  similarityThreshold: 0.8,
  maxMatches: 5,
  keyProjectionDim: 64,
  valueProjectionDim: 64,
  quantizationBits: 8,
  embeddingDim: 128,
  enableClustering: true,
  numClusters: 10,
  enableLRU: true,
  enableANN: true,
  annAlgorithm: 'auto',
});

// Create a KV-cache segment
const segment: KVCacheSegment = {
  layerId: 0,
  segmentId: 'seg-001',
  tokens: [1, 2, 3, 4, 5],
  keyCache: [[0.1, 0.2], [0.3, 0.4]],
  valueCache: [[0.5, 0.6], [0.7, 0.8]],
  metadata: {
    createdAt: Date.now(),
    modelHash: 'model-hash-001',
    agentId: 'agent-001',
    turnNumber: 1,
    position: 0,
    length: 5,
  },
};

// Create anchor from segment
const embedding = [0.1, 0.2, 0.3, 0.4]; // Computed embedding
const anchor = await anchorPool.createAnchor(segment, embedding);
console.log('Created anchor:', anchor.anchorId);

// Find similar anchors
const similarAnchors = anchorPool.findSimilarAnchors(
  [0.15, 0.25, 0.35, 0.45], // query embedding
  0, // layerId
  0.8 // threshold
);
console.log('Found similar anchors:', similarAnchors.length);
```

### 6.2 Anchor Matching and Offset Prediction

```typescript
// Initialize matcher and predictor
const anchorMatcher = new AnchorMatcher({
  similarityThreshold: 0.8,
  maxMatches: 5,
  useTokenOverlap: true,
  usePositionalAlignment: true,
  embeddingWeight: 0.6,
  tokenWeight: 0.3,
  positionWeight: 0.1,
});

const offsetPredictor = new OffsetPredictor({
  windowSize: 3,
  learningRate: 0.01,
  smoothingFactor: 0.9,
  minConfidence: 0.5,
});

// Find matches for a query segment
const matches = anchorMatcher.findMatches(
  segment,
  embedding,
  anchorPool
);

console.log('Matches found:', matches.length);
for (const match of matches) {
  console.log(`  Anchor: ${match.anchor.anchorId}, Similarity: ${match.similarity}`);
}

// Predict offsets for matched anchors
const predictions = offsetPredictor.predictOffset(matches, segment);
for (const pred of predictions) {
  console.log(`  Anchor: ${pred.anchorId}, Confidence: ${pred.confidence}`);
}

// Update offset history with actual offset
const actualOffset = [[0.01, 0.02], [0.03, 0.04]];
offsetPredictor.updateOffsetHistory(anchor.anchorId, actualOffset);

// Learn from prediction error
offsetPredictor.learn(
  anchor.anchorId,
  predictions[0].predictedOffset,
  actualOffset,
  0.8 // reward
);
```

### 6.3 Anchor Pool Management

```typescript
// Get pool statistics
const stats = anchorPool.getStats();
console.log('Total anchors:', stats.totalAnchors);
console.log('Avg quality score:', stats.avgQualityScore);
console.log('Avg compression ratio:', stats.avgCompressionRatio);

// Get cluster information
const clusters = anchorPool.getClusters(0); // layerId = 0
for (const cluster of clusters) {
  console.log(`Cluster ${cluster.clusterId}: ${cluster.anchorIds.size} anchors`);
}

// Cleanup old or low-quality anchors
const removedCount = anchorPool.cleanup();
console.log(`Removed ${removedCount} anchors`);

// Clear all anchors
anchorPool.clear();

// Rebuild ANN indexes
anchorPool.rebuildANNIndexes();

// Get ANN statistics
const annStats = anchorPool.getANNStats();
console.log('ANN indexes built:', annStats.indexesBuilt);
```

---

## 7. Distributed System Implementation Guide

### 7.1 Setting Up Distributed Coordination

```typescript
import {
  createDistributedCoordination,
  MemoryBackend,
  RedisBackend,
} from './distributed/index.js';

// Create distributed coordination
const coordination = createDistributedCoordination({
  backend: 'redis',
  connectionString: 'redis://localhost:6379',
  nodeId: 'node-001',
  heartbeatIntervalMs: 5000,
  discoveryIntervalMs: 5000,
  colonyInfo: {
    id: 'colony-001',
    name: 'Primary Colony',
    gardenerId: 'user-001',
    capabilities: ['code-review', 'text-generation'],
  },
});

// Start coordination
await coordination.start();

// Listen for discovery events
coordination.discovery.on('discovery', (event) => {
  console.log('Node discovered:', event.nodeId);
  console.log('Capabilities:', event.capabilities);
});

coordination.discovery.on('rebalance_needed', (metrics) => {
  console.log('Rebalance needed:', metrics);
});

// Get cluster metrics
const metrics = coordination.getClusterMetrics();
console.log('Total nodes:', metrics.totalNodes);
console.log('Active nodes:', metrics.activeNodes);

// Stop coordination
await coordination.stop();
```

### 7.2 Federation Between Colonies

```typescript
// Access federation if available
if (coordination.federation) {
  // Listen for pattern reception
  coordination.federation.on('pattern_received', (data) => {
    console.log('Pattern received:', data.patternId);
    console.log('From colony:', data.sourceColonyId);
  });

  coordination.federation.on('migration_request', (data) => {
    console.log('Migration requested:', data);
    // Handle migration request
  });

  // Share a pattern
  await coordination.federation.sharePattern({
    patternId: 'pattern-001',
    type: 'embedding',
    data: { embedding: [0.1, 0.2, 0.3] },
    privacyLevel: PrivacyLevel.COLONY,
  });
}
```

---

## 8. Safety System Implementation Guide

### 8.1 Using Safety Layer

```typescript
import { SafetyLayer } from './safety.js';
import { SafetySeverity } from './types.js';

const safetyLayer = new SafetyLayer();

// Add constitutional constraints
safetyLayer.addConstraint({
  id: 'constraint-001',
  name: 'No Harmful Actions',
  category: 'safety',
  rule: 'Actions must not cause harm to users or systems',
  severity: SafetySeverity.CRITICAL,
  isActive: true,
  cannotOverride: true,
});

safetyLayer.addConstraint({
  id: 'constraint-002',
  name: 'Privacy Protection',
  category: 'privacy',
  rule: 'Private data must not be exposed',
  severity: SafetySeverity.ERROR,
  isActive: true,
  cannotOverride: false,
});

// Check an action
const checkResult = safetyLayer.check(
  { type: 'execute', payload: 'some action' },
  { agentId: 'agent-001', colonyId: 'colony-001' }
);

if (!checkResult.passed) {
  console.log('Action blocked:', checkResult.message);
  console.log('Constraint:', checkResult.constraintId);
  console.log('Override possible:', checkResult.overridePossible);
}

// Emergency controls
safetyLayer.triggerEmergency('Critical security breach detected');
console.log('In emergency:', safetyLayer.isInEmergency());

// All non-safety operations are blocked in emergency
safetyLayer.clearEmergency();
```

### 8.2 Using Guardian Angel

```typescript
import {
  GuardianAngelAgent,
  createGuardianAgent,
} from './guardian/index.js';

// Create guardian agent
const guardian = createGuardianAgent({
  learningEnabled: true,
  strictness: 0.8,
  adaptiveness: 0.5,
});

// Review an action
const decision = guardian.review({
  action: { type: 'execute', payload: 'some action' },
  agent: agentState,
  colony: colonyStats,
  history: [],
});

if (decision.allowed) {
  console.log('Action allowed');
  if (decision.modified) {
    console.log('Action was modified:', decision.modified);
  }
} else {
  console.log('Action blocked:', decision.reason);
}

// Provide feedback for learning
guardian.learn({
  decision,
  outcome: 'success',
  actualImpact: { latencyMs: 100, resourceUsage: 0.5 },
});

// Get guardian statistics
const guardianStats = guardian.getStats();
console.log('Guardian stats:', guardianStats);
```

---

## 9. Edge Cases to Handle

### 9.1 Agent Edge Cases

```typescript
/**
 * Edge case: Agent initialization failure
 */
async function handleInitializationFailure(agent: IAgent) {
  try {
    await agent.initialize();
  } catch (error) {
    // Log the error
    console.error('Agent initialization failed:', error);

    // Attempt recovery or create new agent
    if (agent instanceof CoreAgent) {
      // Try to restore from backup
      const backup = agent.extractKnowledge();
      if (backup) {
        // Create new agent and restore
      }
    }

    // For ephemeral agents, just create a new one
    throw new POLLNError(
      POLLNErrorCode.AGENT_INITIALIZATION_FAILED,
      `Failed to initialize agent ${agent.id}`,
      { originalError: error }
    );
  }
}

/**
 * Edge case: Agent processing timeout
 */
async function processWithTimeout<T>(
  agent: IAgent,
  input: T,
  timeoutMs: number = 30000
): Promise<IA2APackage<T>> {
  const timeoutPromise = new Promise<never>((_, reject) => {
    setTimeout(() => {
      reject(new Error(`Processing timed out after ${timeoutMs}ms`));
    }, timeoutMs);
  });

  try {
    return await Promise.race([
      agent.process(input),
      timeoutPromise,
    ]);
  } catch (error) {
    // Update agent failure metrics
    agent.updateValueFunction(-1);

    // Check if agent should be terminated
    if (agent.shouldTerminate()) {
      await agent.shutdown();
    }

    throw error;
  }
}

/**
 * Edge case: Circular dependency in agent calls
 */
class CircularDependencyDetector {
  private activeCalls: Map<string, Set<string>> = new Map();

  checkCall(callerId: string, calleeId: string): boolean {
    if (!this.activeCalls.has(calleeId)) {
      return false; // No active calls from callee
    }

    const callees = this.activeCalls.get(calleeId)!;
    return callees.has(callerId); // Circular if callee is calling caller
  }

  beginCall(callerId: string, calleeId: string): void {
    if (!this.activeCalls.has(callerId)) {
      this.activeCalls.set(callerId, new Set());
    }
    this.activeCalls.get(callerId)!.add(calleeId);
  }

  endCall(callerId: string, calleeId: string): void {
    this.activeCalls.get(callerId)?.delete(calleeId);
  }
}
```

### 9.2 Colony Edge Cases

```typescript
/**
 * Edge case: Colony capacity exceeded
 */
function safeRegisterAgent(colony: IColony, config: IAgentConfig): IAgentState {
  const currentCount = colony.count;
  const maxAgents = (colony.config as ColonyConfig).maxAgents;

  if (currentCount >= maxAgents) {
    // Try to evict dormant agents first
    const dormantAgents = colony.getAllAgents().filter(a => a.status === 'dormant');

    if (dormantAgents.length > 0) {
      // Evict the least valuable dormant agent
      const toEvict = dormantAgents.sort((a, b) =>
        a.valueFunction - b.valueFunction
      )[0];
      colony.unregisterAgent(toEvict.id);
    } else {
      throw new POLLNError(
        POLLNErrorCode.COLONY_CAPACITY_EXCEEDED,
        `Colony ${colony.id} has reached maximum capacity of ${maxAgents} agents`,
        { currentCount, maxAgents }
      );
    }
  }

  return colony.registerAgent(config);
}

/**
 * Edge case: Resource exhaustion
 */
async function checkResources(colony: IColony, requiredResources: {
  compute: number;
  memory: number;
  network: number;
}): Promise<boolean> {
  const stats = await colony.getStats();
  const budget = (colony.config as ColonyConfig).resourceBudget;

  const availableCompute = budget.totalCompute - stats.totalCompute;
  const availableMemory = budget.totalMemory - stats.totalMemory;
  const availableNetwork = budget.totalNetwork - stats.totalNetwork;

  if (
    availableCompute < requiredResources.compute ||
    availableMemory < requiredResources.memory ||
    availableNetwork < requiredResources.network
  ) {
    throw new POLLNError(
      POLLNErrorCode.COLONY_RESOURCE_EXHAUSTED,
      'Insufficient resources for operation',
      {
        required: requiredResources,
        available: {
          compute: availableCompute,
          memory: availableMemory,
          network: availableNetwork,
        },
      }
    );
  }

  return true;
}
```

### 9.3 Communication Edge Cases

```typescript
/**
 * Edge case: Broken causal chain
 */
async function repairCausalChain(
  a2aSystem: IA2APackageSystem,
  packageId: string
): Promise<string[]> {
  const chain = a2aSystem.getCausalChain(packageId);

  // Check for missing parents
  const validChain: string[] = [];
  for (const id of chain) {
    const pkg = a2aSystem.getPackage(id);
    if (pkg) {
      validChain.push(id);
    } else {
      console.warn(`Missing package in causal chain: ${id}`);
      // Stop chain at missing package
      break;
    }
  }

  return validChain;
}

/**
 * Edge case: Message queue overflow
 */
class BoundedMessageQueue {
  private queue: IA2APackage[] = [];
  private maxSize: number;

  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
  }

  enqueue(pkg: IA2APackage): boolean {
    if (this.queue.length >= this.maxSize) {
      // Drop oldest message
      const dropped = this.queue.shift();
      console.warn(`Dropped message ${dropped?.id} due to queue overflow`);
    }

    this.queue.push(pkg);
    return true;
  }

  dequeue(): IA2APackage | undefined {
    return this.queue.shift();
  }

  get length(): number {
    return this.queue.length;
  }
}
```

### 9.4 Learning Edge Cases

```typescript
/**
 * Edge case: Weight explosion in Hebbian learning
 */
function safeUpdateSynapse(
  learning: IHebbianLearning,
  sourceId: string,
  targetId: string,
  preActivity: number,
  postActivity: number,
  reward: number
): Promise<number> {
  // Clamp activities to valid range
  const clampedPre = Math.max(0, Math.min(1, preActivity));
  const clampedPost = Math.max(0, Math.min(1, postActivity));
  const clampedReward = Math.max(-1, Math.min(1, reward));

  return learning.updateSynapse(
    sourceId,
    targetId,
    clampedPre,
    clampedPost,
    clampedReward
  );
}

/**
 * Edge case: Plinko with no valid proposals
 */
async function safePlinkoSelect(
  plinko: IPlinkoLayer,
  proposals: IAgentProposal[]
): Promise<string> {
  if (proposals.length === 0) {
    throw new POLLNError(
      POLLNErrorCode.SAFETY_CONSTRAINT_VIOLATION,
      'No proposals available for selection'
    );
  }

  const result = await plinko.process(proposals);

  // If all proposals failed safety, select fallback
  if (result.wasOverridden && !result.selectedAgentId) {
    // Select the proposal with highest confidence as fallback
    const fallback = proposals.reduce((best, current) =>
      current.confidence > best.confidence ? current : best
    );

    console.warn(`All proposals failed safety, using fallback: ${fallback.agentId}`);
    return fallback.agentId;
  }

  return result.selectedAgentId;
}
```

### 9.5 KV-Cache Edge Cases

```typescript
/**
 * Edge case: Anchor pool corruption
 */
async function recoverAnchorPool(pool: IKVAnchorPool): Promise<void> {
  // Get all anchors
  const stats = pool.getStats();
  const layers = Object.keys(stats.anchorsByLayer).map(Number);

  let corruptedCount = 0;

  for (const layerId of layers) {
    const anchors = pool.getAnchorsForLayer(layerId);

    for (const anchor of anchors) {
      // Check for corruption
      if (
        !anchor.anchorId ||
        !anchor.embedding ||
        anchor.qualityScore < 0 ||
        anchor.qualityScore > 1
      ) {
        // Remove corrupted anchor
        pool.updateAnchor(anchor.anchorId, { qualityScore: 0 }); // Will be cleaned up
        corruptedCount++;
      }
    }
  }

  // Force cleanup
  pool.cleanup();

  if (corruptedCount > 0) {
    console.warn(`Recovered ${corruptedCount} corrupted anchors`);
  }
}

/**
 * Edge case: ANN index stale
 */
async function ensureFreshANNIndex(pool: IKVAnchorPool): Promise<void> {
  const stats = pool.getANNStats();

  if (!stats.enabled) {
    return;
  }

  // Rebuild if index seems stale
  if (stats.indexesBuilt === 0) {
    pool.rebuildANNIndexes();
  }
}
```

---

## 10. Test Scenarios

### 10.1 Agent Test Scenarios

```typescript
describe('Agent Lifecycle', () => {
  test('should initialize and shutdown correctly', async () => {
    const agent = new CustomAgent(createTestConfig());

    await agent.initialize();
    expect(agent.isInitialized()).toBe(true);

    await agent.shutdown();
    expect(agent.isShutdown()).toBe(true);
  });

  test('should handle process timeout', async () => {
    const agent = new SlowAgent(createTestConfig());
    await agent.initialize();

    await expect(
      processWithTimeout(agent, 'input', 100) // 100ms timeout
    ).rejects.toThrow('timed out');
  });

  test('should maintain value function bounds', async () => {
    const agent = new CustomAgent(createTestConfig());

    // Extreme rewards should not break bounds
    agent.updateValueFunction(100);
    expect(agent.valueFunction).toBeLessThanOrEqual(1);

    agent.updateValueFunction(-100);
    expect(agent.valueFunction).toBeGreaterThanOrEqual(0);
  });

  test('should transfer knowledge on succession', async () => {
    const predecessor = new RoleAgentImpl(createTestConfig());
    const successor = new RoleAgentImpl(createTestConfig());

    await predecessor.initialize();
    predecessor.setState('pattern1', { data: 'test' });

    predecessor.setSuccessor(successor);
    await predecessor.shutdown();

    const knowledge = successor.extractKnowledge();
    expect(knowledge.has('pattern1')).toBe(true);
  });
});
```

### 10.2 Colony Test Scenarios

```typescript
describe('Colony Management', () => {
  test('should enforce agent capacity', async () => {
    const colony = new Colony({
      ...createTestColonyConfig(),
      maxAgents: 2,
    });

    colony.registerAgent(createTestAgentConfig('agent-1'));
    colony.registerAgent(createTestAgentConfig('agent-2'));

    expect(() =>
      safeRegisterAgent(colony, createTestAgentConfig('agent-3'))
    ).toThrow(POLLNErrorCode.COLONY_CAPACITY_EXCEEDED);
  });

  test('should calculate Shannon diversity correctly', async () => {
    const colony = new Colony(createTestColonyConfig());

    // Register diverse agents
    colony.registerAgent({ ...createTestAgentConfig('a1'), typeId: 'type-a' });
    colony.registerAgent({ ...createTestAgentConfig('a2'), typeId: 'type-a' });
    colony.registerAgent({ ...createTestAgentConfig('a3'), typeId: 'type-b' });

    const stats = await colony.getStats();

    // Higher diversity with more even distribution
    expect(stats.shannonDiversity).toBeGreaterThan(0);
    expect(stats.shannonDiversity).toBeLessThan(2); // Max for 2 types
  });

  test('should handle distributed events', async () => {
    const colony = new Colony({
      ...createTestColonyConfig(),
      distributed: true,
      distributedConfig: {
        backend: 'memory',
      },
    });

    const discoveryPromise = new Promise(resolve => {
      colony.on('node_discovered', resolve);
    });

    // Simulate node discovery
    // ... emit event ...

    await expect(discoveryPromise).resolves.toBeDefined();
  });
});
```

### 10.3 Communication Test Scenarios

```typescript
describe('A2A Package System', () => {
  test('should create traceable packages', async () => {
    const system = new A2APackageSystem();

    const parent = await system.createPackage('a1', 'a2', 'test', {});
    const child = await system.createPackage('a2', 'a3', 'test', {}, {
      parentIds: [parent.id],
    });

    expect(child.parentIds).toContain(parent.id);
    expect(child.causalChainId).toBeDefined();
  });

  test('should trace causal chains', async () => {
    const system = new A2APackageSystem();

    const pkg1 = await system.createPackage('a1', 'a2', 'test', {});
    const pkg2 = await system.createPackage('a2', 'a3', 'test', {}, {
      parentIds: [pkg1.id],
    });
    const pkg3 = await system.createPackage('a3', 'a4', 'test', {}, {
      parentIds: [pkg2.id],
    });

    const chain = system.getCausalChain(pkg3.id);
    expect(chain).toHaveLength(3);
    expect(chain).toContain(pkg1.id);
    expect(chain).toContain(pkg2.id);
    expect(chain).toContain(pkg3.id);
  });

  test('should enforce privacy hierarchy', async () => {
    const system = new A2APackageSystem();

    // Private package should not reference public parent
    const publicPkg = await system.createPackage('a1', 'a2', 'test', {}, {
      privacyLevel: PrivacyLevel.PUBLIC,
    });

    // This should be allowed (higher privacy can reference lower)
    const privatePkg = await system.createPackage('a2', 'a3', 'test', {}, {
      privacyLevel: PrivacyLevel.PRIVATE,
      parentIds: [publicPkg.id],
    });

    expect(privatePkg.privacyLevel).toBe(PrivacyLevel.PRIVATE);
  });
});
```

### 10.4 Learning Test Scenarios

```typescript
describe('Hebbian Learning', () => {
  test('should strengthen co-activated pathways', async () => {
    const learning = new HebbianLearning({});

    const initialWeight = learning.getWeight('a1', 'a2');

    // Co-activate multiple times with reward
    for (let i = 0; i < 10; i++) {
      await learning.updateSynapse('a1', 'a2', 0.9, 0.9, 1.0);
    }

    const finalWeight = learning.getWeight('a1', 'a2');
    expect(finalWeight).toBeGreaterThan(initialWeight);
  });

  test('should decay unused pathways', async () => {
    const learning = new HebbianLearning({
      decayRate: 0.1,
    });

    // Create a pathway
    await learning.updateSynapse('a1', 'a2', 0.9, 0.9, 1.0);
    const initialWeight = learning.getWeight('a1', 'a2');

    // Decay all pathways
    await learning.decayAll();

    const decayedWeight = learning.getWeight('a1', 'a2');
    expect(decayedWeight).toBeLessThan(initialWeight);
  });

  test('should prune weak synapses', async () => {
    const learning = new HebbianLearning({
      minWeight: 0.01,
    });

    // Create weak pathway
    await learning.updateSynapse('a1', 'a2', 0.1, 0.1, -1.0);

    const pruned = await learning.pruneWeak(0.1);
    expect(pruned).toBeGreaterThan(0);
  });
});

describe('Plinko Selection', () => {
  test('should select probabilistically, not deterministically', async () => {
    const plinko = new PlinkoLayer({ temperature: 1.0 });

    const proposals = [
      { agentId: 'a1', confidence: 0.9, bid: 1.0 },
      { agentId: 'a2', confidence: 0.5, bid: 0.5 },
    ];

    const selections: Record<string, number> = { a1: 0, a2: 0 };

    // Run multiple selections
    for (let i = 0; i < 100; i++) {
      const result = await plinko.process(proposals);
      selections[result.selectedAgentId]++;
    }

    // Both should be selected sometimes (stochastic)
    expect(selections.a1).toBeGreaterThan(0);
    expect(selections.a2).toBeGreaterThan(0);
  });

  test('should override on safety violation', async () => {
    const plinko = new PlinkoLayer();

    plinko.registerDiscriminator('safety', (p) =>
      p.agentId !== 'unsafe-agent'
    );

    const proposals = [
      { agentId: 'unsafe-agent', confidence: 0.99, bid: 1.0 },
      { agentId: 'safe-agent', confidence: 0.5, bid: 0.5 },
    ];

    const result = await plinko.process(proposals);

    expect(result.wasOverridden).toBe(true);
    expect(result.selectedAgentId).toBe('safe-agent');
  });
});
```

### 10.5 KV-Cache Test Scenarios

```typescript
describe('KV Anchor Pool', () => {
  test('should create and retrieve anchors', async () => {
    const pool = new KVAnchorPool({});

    const segment = createTestSegment();
    const embedding = [0.1, 0.2, 0.3];

    const anchor = await pool.createAnchor(segment, embedding);
    const retrieved = pool.getAnchor(anchor.anchorId);

    expect(retrieved).toBeDefined();
    expect(retrieved?.anchorId).toBe(anchor.anchorId);
  });

  test('should find similar anchors', async () => {
    const pool = new KVAnchorPool({
      similarityThreshold: 0.5,
    });

    // Create anchors with different embeddings
    await pool.createAnchor(createTestSegment(0), [1, 0, 0]);
    await pool.createAnchor(createTestSegment(0), [0.9, 0.1, 0]);
    await pool.createAnchor(createTestSegment(0), [0, 1, 0]);

    // Query for similar to [1, 0, 0]
    const similar = pool.findSimilarAnchors([1, 0, 0], 0, 0.5);

    expect(similar.length).toBeGreaterThanOrEqual(2);
    expect(similar[0].embedding[0]).toBeCloseTo(1, 0.1);
  });

  test('should enforce capacity with LRU eviction', async () => {
    const pool = new KVAnchorPool({
      maxAnchors: 2,
      enableLRU: true,
    });

    await pool.createAnchor(createTestSegment(0), [1, 0]);
    await pool.createAnchor(createTestSegment(0), [0, 1]);
    await pool.createAnchor(createTestSegment(0), [1, 1]); // Should evict

    const stats = pool.getStats();
    expect(stats.totalAnchors).toBeLessThanOrEqual(2);
  });

  test('should cleanup old anchors', async () => {
    const pool = new KVAnchorPool({
      maxAgeMs: 100, // 100ms
    });

    const anchor = await pool.createAnchor(createTestSegment(0), [1, 0]);

    // Wait for expiry
    await new Promise(resolve => setTimeout(resolve, 150));

    const removed = pool.cleanup();
    expect(removed).toBeGreaterThan(0);
  });
});
```

### 10.6 Integration Test Scenarios

```typescript
describe('Full System Integration', () => {
  test('should complete agent lifecycle in colony', async () => {
    // Create colony
    const colony = new Colony(createTestColonyConfig());

    // Create and register agent
    const agentConfig = createTestAgentConfig();
    const state = colony.registerAgent(agentConfig);

    // Activate agent
    colony.activateAgent(state.id);

    // Simulate execution
    colony.recordResult(state.id, true, 100);

    // Check state updated
    const updatedState = colony.getAgent(state.id);
    expect(updatedState?.successCount).toBe(1);

    // Deactivate and unregister
    colony.deactivateAgent(state.id);
    colony.unregisterAgent(state.id);

    expect(colony.count).toBe(0);
  });

  test('should coordinate agents via SPORE', async () => {
    const protocol = new SPOREProtocol();

    const receivedMessages: unknown[] = [];

    await protocol.subscribe('test:topic', (msg) => {
      receivedMessages.push(msg);
    });

    await protocol.publish('test:topic', { data: 'test' });

    // Wait for message delivery
    await new Promise(resolve => setTimeout(resolve, 10));

    expect(receivedMessages).toHaveLength(1);
    expect(receivedMessages[0]).toEqual({ data: 'test' });

    await protocol.shutdown();
  });

  test('should learn from agent interactions', async () => {
    const learning = new HebbianLearning({});
    const plinko = new PlinkoLayer({});

    // Simulate agent interactions
    for (let i = 0; i < 10; i++) {
      // Agent 1 proposes
      const proposals = [
        { agentId: 'agent-1', confidence: 0.8, bid: 1.0 },
        { agentId: 'agent-2', confidence: 0.6, bid: 0.8 },
      ];

      const result = await plinko.process(proposals);

      // Update synapse based on outcome
      await learning.updateSynapse(
        'agent-1',
        result.selectedAgentId,
        0.8,
        0.7,
        result.selectedAgentId === 'agent-1' ? 1.0 : 0.5
      );
    }

    // Check that learning occurred
    const weight = learning.getWeight('agent-1', 'agent-1');
    expect(weight).toBeGreaterThan(0.5);
  });
});
```

---

## Appendix: Quick Reference

### Common Imports

```typescript
// Core
import { Colony } from './colony.js';
import { BaseAgent } from './agent.js';
import { TaskAgent, RoleAgent, CoreAgent, TileCategory } from './agents.js';

// Communication
import { A2APackageSystem } from './communication.js';
import { SPOREProtocol } from './protocol.js';

// Learning
import { HebbianLearning } from './learning.js';
import { PlinkoLayer } from './decision.js';
import { ValueNetwork } from './valuenetwork.js';

// KV-Cache
import { KVAnchorPool, AnchorMatcher, OffsetPredictor } from './kvanchor.js';

// Safety
import { SafetyLayer } from './safety.js';
import { GuardianAngelAgent } from './guardian/index.js';

// Types
import type {
  AgentConfig,
  AgentState,
  ColonyConfig,
  ColonyStats,
  A2APackage,
} from './types.js';
import { PrivacyLevel, SubsumptionLayer, SafetySeverity } from './types.js';
```

### Error Handling Pattern

```typescript
try {
  // Operation that may fail
  await someOperation();
} catch (error) {
  if (error instanceof POLLNError) {
    // Handle known POLLN errors
    switch (error.code) {
      case POLLNErrorCode.AGENT_NOT_FOUND:
        // Handle missing agent
        break;
      case POLLNErrorCode.COLONY_CAPACITY_EXCEEDED:
        // Handle capacity issue
        break;
      default:
        // Handle other POLLN errors
    }
  } else {
    // Handle unexpected errors
    throw error;
  }
}
```

---

*Document Version: 1.0.0*
*Compatible with POLLN v5.0.0+*
