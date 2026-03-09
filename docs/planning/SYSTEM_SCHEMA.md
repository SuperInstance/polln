# POLLN System Schema

> **Purpose**: TypeScript interface definitions, type definitions, component contracts, and invariants for POLLN implementation agents.
>
> **Audience**: glm-4.7 implementation agents and human developers.
>
> **Last Updated**: 2026-03-08

---

## Table of Contents

1. [Core Agent Interfaces](#1-core-agent-interfaces)
2. [Colony Management Interfaces](#2-colony-management-interfaces)
3. [Communication Protocol Interfaces](#3-communication-protocol-interfaces)
4. [Learning System Interfaces](#4-learning-system-interfaces)
5. [KV-Cache System Interfaces](#5-kv-cache-system-interfaces)
6. [Distributed System Interfaces](#6-distributed-system-interfaces)
7. [Safety and Guardian Interfaces](#7-safety-and-guardian-interfaces)
8. [Lifecycle Interfaces](#8-lifecycle-interfaces)
9. [API Layer Interfaces](#9-api-layer-interfaces)
10. [System Invariants](#10-system-invariants)

---

## 1. Core Agent Interfaces

### 1.1 IAgent - Base Agent Contract

```typescript
/**
 * Base interface for all agents in the POLLN system.
 * Every agent must implement these core methods.
 */
interface IAgent<TConfig = unknown> {
  // Identity
  readonly id: string;
  readonly config: IAgentConfig;

  // Core Lifecycle
  initialize(): Promise<void>;
  process<T>(input: T): Promise<IA2APackage<T>>;
  shutdown(): Promise<void>;

  // State Management
  getState<K>(key: string): K | undefined;
  setState<K>(key: string, value: K): void;

  // Value Function (Karmic Record)
  readonly valueFunction: number;
  updateValueFunction(reward: number): void;

  // Activity Tracking
  readonly lastActive: number;
  touch(): void;
}
```

### 1.2 IAgentConfig - Agent Configuration

```typescript
/**
 * Configuration for creating an agent.
 * All fields are required unless marked optional.
 */
interface IAgentConfig {
  // Identity
  id: string;
  typeId: string;
  categoryId: TileCategory;

  // Model Specification
  modelFamily: string;
  defaultParams: Record<string, unknown>;

  // SPORE Protocol Binding
  inputTopics: string[];
  outputTopic: string;

  // Performance Targets (Optional)
  targetLatencyMs?: number;
  maxMemoryMB?: number;

  // Training Requirements
  minExamples: number;
  requiresWorldModel: boolean;
}
```

### 1.3 IAgentState - Runtime State

```typescript
/**
 * Runtime state of an agent, persisted across restarts.
 */
interface IAgentState {
  id: string;
  typeId: string;

  // Model State
  modelHash?: string;
  parameterCount?: number;
  modelVersion: number;

  // Runtime Status
  status: AgentStatus;
  lastActive: number;

  // Performance Metrics
  valueFunction: number;
  successCount: number;
  failureCount: number;
  avgLatencyMs: number;
  executionCount: number;
  successRate: number;
  active: boolean;

  // Internal State Snapshot
  stateSnapshot?: Record<string, unknown>;
}

type AgentStatus = 'dormant' | 'active' | 'hibernating' | 'error';
```

### 1.4 TileCategory - Agent Lifespan Classification

```typescript
/**
 * Defines agent lifespan and succession behavior.
 */
enum TileCategory {
  /**
   * Ephemeral: Task-bound (minutes to hours), no succession
   * Like blood cells - born, task, die
   */
  EPHEMERAL = 'EPHEMERAL',

  /**
   * Role: Performance-bound (days to weeks), knowledge handoff
   * Like skin cells - medium lifespan, succession
   */
  ROLE = 'ROLE',

  /**
   * Core: Age-bound (months to years), backup and recovery
   * Like bone cells - long-lived, rarely replaced
   */
  CORE = 'CORE',
}
```

### 1.5 ITileAgent - Extended Agent with Succession

```typescript
/**
 * Extended interface for agents that support knowledge succession.
 */
interface ITileAgent<TConfig = unknown> extends IAgent<TConfig> {
  readonly category: TileCategory;

  // Termination Check
  shouldTerminate(): boolean;

  // Knowledge Extraction (for succession)
  extractKnowledge(): IKnowledgePacket | null;

  // Performance Metrics
  getPerformanceMetrics(): IPerformanceMetrics;
}

interface IKnowledgePacket {
  patterns: Map<string, unknown>;
  valueFunction: number;
  performanceHistory: number[];
  extractedAt: number;
}

interface IPerformanceMetrics {
  successRate: number;
  totalExecutions: number;
  knowledgePatterns: number;
  avgLatencyMs: number;
}
```

---

## 2. Colony Management Interfaces

### 2.1 IColony - Colony Contract

```typescript
/**
 * Interface for agent collection management.
 */
interface IColony {
  // Identity
  readonly id: string;
  readonly config: IColonyConfig;

  // Agent Management
  registerAgent(config: IAgentConfig): IAgentState;
  unregisterAgent(agentId: string): boolean;
  getAgent(agentId: string): IAgentState | undefined;
  getAgentConfig(agentId: string): IAgentConfig | undefined;
  getAllAgents(): IAgentState[];
  getActiveAgents(): IAgentState[];
  getAgentsByType(typeId: string): IAgentState[];

  // State Updates
  updateAgentState(agentId: string, updates: Partial<IAgentState>): boolean;
  activateAgent(agentId: string): boolean;
  deactivateAgent(agentId: string): boolean;
  recordResult(agentId: string, success: boolean, latencyMs: number): void;

  // Statistics
  getStats(): Promise<IColonyStats>;
  readonly count: number;

  // Distributed Coordination (Optional)
  isDistributed(): boolean;
  getDistributedCoordination(): IDistributedCoordination | null;
}
```

### 2.2 IColonyConfig - Colony Configuration

```typescript
/**
 * Configuration for creating a colony.
 */
interface IColonyConfig {
  id: string;
  gardenerId: string;
  name: string;
  maxAgents: number;

  resourceBudget: {
    totalCompute: number;
    totalMemory: number;
    totalNetwork: number;
  };

  // Distributed Options
  distributed?: boolean;
  distributedConfig?: IDistributedConfig;
}

interface IDistributedConfig {
  backend: 'memory' | 'redis' | 'nats';
  connectionString?: string;
  nodeId?: string;
}
```

### 2.3 IColonyStats - Colony Statistics

```typescript
/**
 * Statistics about colony state and health.
 */
interface IColonyStats {
  totalAgents: number;
  activeAgents: number;
  dormantAgents: number;
  totalCompute: number;
  totalMemory: number;
  totalNetwork: number;
  shannonDiversity: number;

  // Distributed Metrics (Optional)
  clusterMetrics?: {
    totalNodes: number;
    activeNodes: number;
    averageLoad: number;
  };
}
```

---

## 3. Communication Protocol Interfaces

### 3.1 IA2APackage - Agent-to-Agent Message

```typescript
/**
 * Core communication artifact between agents.
 * Every A2A package is visible, inspectable, stored, and replayable.
 */
interface IA2APackage<T = unknown> {
  id: string;
  timestamp: number;

  // Routing
  senderId: string;
  receiverId: string;

  // Content
  type: string;
  payload: T;

  // Causal Chain (Traceability)
  parentIds: string[];
  causalChainId: string;

  // Privacy
  privacyLevel: PrivacyLevel;

  // Subsumption Architecture
  layer: SubsumptionLayer;

  // Differential Privacy Metadata (Optional)
  dpMetadata?: {
    epsilon: number;
    delta: number;
    noiseScale: number;
  };
}

enum PrivacyLevel {
  PUBLIC = 'PUBLIC',
  COLONY = 'COLONY',
  PRIVATE = 'PRIVATE',
}

enum SubsumptionLayer {
  SAFETY = 'SAFETY',      // Immediate, hardwired (bypasses all)
  REFLEX = 'REFLEX',      // Fast, cached responses
  HABITUAL = 'HABITUAL',  // Learned routines
  DELIBERATE = 'DELIBERATE', // Planning, reasoning
}
```

### 3.2 IA2APackageSystem - Communication Layer

```typescript
/**
 * System for creating, storing, and tracing A2A packages.
 */
interface IA2APackageSystem {
  // Package Creation
  createPackage<T>(
    senderId: string,
    receiverId: string,
    type: string,
    payload: T,
    options?: {
      privacyLevel?: PrivacyLevel;
      layer?: SubsumptionLayer;
      parentIds?: string[];
      dpMetadata?: IDPMetadata;
    }
  ): Promise<IA2APackage<T>>;

  // Retrieval
  getPackage<T>(id: string): IA2APackage<T> | undefined;
  getHistory(agentId: string, limit?: number): IA2APackage[];

  // Causal Chain Operations
  getCausalChain(packageId: string): string[];
  replayChain(packageId: string): Promise<IA2APackage[]>;

  // Management
  clearHistory(): void;
  getStats(): {
    totalPackages: number;
    historySize: number;
    uniqueChains: number;
  };
}
```

### 3.3 ISPOREProtocol - Pub/Sub Messaging

```typescript
/**
 * Simple pub/sub messaging for agent coordination.
 */
interface ISPOREProtocol {
  // Subscription Management
  subscribe(topic: string, handler: TopicHandler): Promise<string>;
  unsubscribe(subscriptionId: string): Promise<void>;

  // Publishing
  publish(topic: string, message: unknown): Promise<void>;

  // History
  getHistory(topic: string, limit?: number): unknown[];

  // Lifecycle
  shutdown(): Promise<void>;

  // Distributed Status
  isDistributed(): boolean;
}

type TopicHandler = (message: unknown) => void | unknown;
```

---

## 4. Learning System Interfaces

### 4.1 IHebbianLearning - Synaptic Plasticity

```typescript
/**
 * Hebbian learning for pathway strengthening.
 * "Neurons that fire together, wire together"
 */
interface IHebbianLearning {
  // Weight Update
  updateSynapse(
    sourceId: string,
    targetId: string,
    preActivity: number,
    postActivity: number,
    reward: number
  ): Promise<number>;

  // Retrieval
  getWeight(sourceId: string, targetId: string): number;
  getAgentSynapses(agentId: string): ISynapseState[];

  // Maintenance
  decayAll(): Promise<void>;
  pruneWeak(threshold?: number): Promise<number>;

  // Statistics
  getStats(): {
    totalSynapses: number;
    avgWeight: number;
    maxWeight: number;
    minWeight: number;
  };
}

interface ISynapseState {
  sourceAgentId: string;
  targetAgentId: string;
  weight: number;
  coactivationCount: number;
  lastCoactivated: number;
  learningRate: number;
  decayRate: number;
}
```

### 4.2 IPlinkoLayer - Stochastic Selection

```typescript
/**
 * Stochastic decision making using Gumbel-Softmax.
 * Key insight: Stochastic selection maintains diversity.
 */
interface IPlinkoLayer {
  // Discriminator Registration
  registerDiscriminator(
    name: string,
    check: (proposal: IAgentProposal) => boolean
  ): void;

  // Selection Process
  process(proposals: IAgentProposal[]): Promise<IPlinkoResult>;

  // History
  getHistory(limit?: number): IPlinkoResult[];
}

interface IAgentProposal {
  agentId: string;
  confidence: number;
  bid: number;
}

interface IPlinkoResult {
  id: string;
  proposals: IAgentProposal[];
  selectedAgentId: string;
  temperature: number;
  entropy: number;
  discriminatorResults: Record<string, boolean>;
  explanation?: string;
  wasOverridden: boolean;
  overrideReason?: string;
}
```

### 4.3 IValueNetwork - TD(lambda) Learning

```typescript
/**
 * Value prediction using TD(lambda) learning.
 */
interface IValueNetwork {
  // Prediction
  predict(state: IStateAction): IValuePrediction;

  // Learning
  update(
    trajectory: ITrajectory,
    reward: number
  ): void;

  // Training
  train(samples: ITrainingSample[]): void;

  // Statistics
  getStats(): {
    totalPredictions: number;
    avgError: number;
    convergenceRate: number;
  };
}

interface IStateAction {
  state: number[];
  action?: string;
}

interface IValuePrediction {
  value: number;
  confidence: number;
  advantage?: number;
}

interface ITrajectory {
  states: IStateAction[];
  rewards: number[];
  terminal: boolean;
}

interface ITrainingSample {
  state: IStateAction;
  target: number;
  weight?: number;
}
```

---

## 5. KV-Cache System Interfaces

### 5.1 IKVAnchorPool - Anchor Storage

```typescript
/**
 * Manages storage and retrieval of KV-cache anchors.
 */
interface IKVAnchorPool {
  // Anchor Creation
  createAnchor(
    segment: IKVCacheSegment,
    embedding: number[]
  ): Promise<IKVAnchor>;

  // Retrieval
  getAnchor(anchorId: string): IKVAnchor | undefined;
  getAnchorsForLayer(layerId: number): IKVAnchor[];
  findSimilarAnchors(
    queryEmbedding: number[],
    layerId: number,
    threshold?: number
  ): IKVAnchor[];

  // Batch Operations
  batchFindSimilarAnchors(
    queryEmbeddings: number[][],
    layerId: number,
    threshold?: number
  ): IBatchMatchResult[];

  // Updates
  updateAnchor(anchorId: string, updates: Partial<IKVAnchor>): boolean;
  cleanup(now?: number): number;

  // Statistics
  getStats(): IKVPoolStats;
  getClusters(layerId?: number): IAnchorCluster[];
  clear(): void;
}
```

### 5.2 IKVCacheSegment - Cache Data

```typescript
/**
 * Key-Value cache segment from an LLM attention layer.
 */
interface IKVCacheSegment {
  layerId: number;
  segmentId: string;
  tokens: number[];
  keyCache: number[][];   // [seq_len, d_k]
  valueCache: number[][]; // [seq_len, d_v]
  metadata: IKVCacheMetadata;
}

interface IKVCacheMetadata {
  createdAt: number;
  modelHash: string;
  agentId: string;
  conversationId?: string;
  turnNumber: number;
  position: number;
  length: number;
}
```

### 5.3 IKVAnchor - Compressed Anchor

```typescript
/**
 * Compressed anchor representation.
 */
interface IKVAnchor {
  anchorId: string;
  layerId: number;
  segmentId: string;

  // Compressed Data
  compressedKeys: Float32Array;
  compressedValues: Float32Array;
  embedding: number[];

  // Source Reference
  sourceSegmentId: string;
  sourceAgentId: string;

  // Usage Statistics (for LRU)
  usageCount: number;
  lastUsed: number;

  // Quality Metrics
  qualityScore: number;
  compressionRatio: number;

  // Temporal Information
  createdAt: number;
  updatedAt: number;

  // Clustering Support
  clusterId?: string;
  clusterCenterDistance?: number;
}
```

### 5.4 IAnchorMatcher - Similarity Matching

```typescript
/**
 * Finds similar segments using embedding distance and token overlap.
 */
interface IAnchorMatcher {
  findMatches(
    querySegment: IKVCacheSegment,
    queryEmbedding: number[],
    anchorPool: IKVAnchorPool
  ): IAnchorMatch[];
}

interface IAnchorMatch {
  anchor: IKVAnchor;
  similarity: number;
  tokenOverlap: number;
  positionalDeviation: number;
}
```

### 5.5 IOffsetPredictor - Offset Prediction

```typescript
/**
 * Predicts KV-cache offsets from anchor patterns.
 */
interface IOffsetPredictor {
  predictOffset(
    matches: IAnchorMatch[],
    querySegment: IKVCacheSegment
  ): IOffsetPrediction[];

  updateOffsetHistory(
    anchorId: string,
    actualOffset: number[][]
  ): void;

  learn(
    anchorId: string,
    predictedOffset: number[][],
    actualOffset: number[][],
    reward: number
  ): void;

  getStats(): {
    trackedAnchors: number;
    avgHistoryLength: number;
    avgWeight: number;
  };
}

interface IOffsetPrediction {
  anchorId: string;
  predictedOffset: number[][];
  confidence: number;
  deviationScore: number;
}
```

---

## 6. Distributed System Interfaces

### 6.1 IDistributedCoordination - Cluster Coordination

```typescript
/**
 * Coordinates multiple colonies across a distributed cluster.
 */
interface IDistributedCoordination {
  // Lifecycle
  start(): Promise<void>;
  stop(): Promise<void>;

  // Discovery
  discovery: IDiscoveryService;

  // Federation (Optional)
  federation?: IColonyFederation;

  // Load Balancing
  loadBalancer: ILoadBalancer;

  // Metrics
  getClusterMetrics(): IClusterMetrics;
}

interface IDiscoveryService {
  on(event: 'discovery', handler: (event: IDiscoveryEvent) => void): void;
  on(event: 'rebalance_needed', handler: (metrics: IClusterMetrics) => void): void;
}

interface IClusterMetrics {
  totalNodes: number;
  activeNodes: number;
  averageLoad: number;
  nodeLoad: Map<string, number>;
}
```

### 6.2 IDistributedBackend - Backend Abstraction

```typescript
/**
 * Abstract interface for distributed backends.
 */
interface IDistributedBackend {
  // Connection
  connect(): Promise<void>;
  disconnect(): Promise<void>;

  // Pub/Sub
  subscribe(topic: string, handler: IMessageHandler): Promise<string>;
  unsubscribe(subscriptionId: string): Promise<void>;
  publish(topic: string, message: IDistributedMessage): Promise<void>;

  // Status
  isConnected(): boolean;
}

interface IDistributedMessage {
  id: string;
  sourceNodeId: string;
  channel: string;
  payload: unknown;
  timestamp: number;
  requiresAck: boolean;
}

type IMessageHandler = (message: IDistributedMessage) => Promise<void>;
```

---

## 7. Safety and Guardian Interfaces

### 7.1 ISafetyLayer - Constitutional Constraints

```typescript
/**
 * Safety layer with constitutional constraints.
 */
interface ISafetyLayer {
  // Constraint Management
  addConstraint(constraint: IConstitutionalConstraint): void;
  removeConstraint(constraintId: string): boolean;

  // Safety Checks
  check(action: unknown, context: ISafetyContext): ISafetyCheckResult;

  // Emergency Controls
  triggerEmergency(reason: string): void;
  clearEmergency(): void;
  isInEmergency(): boolean;
}

interface IConstitutionalConstraint {
  id: string;
  name: string;
  category: string;
  rule: string;
  ruleCode?: string;
  severity: SafetySeverity;
  isActive: boolean;
  cannotOverride: boolean;
}

interface ISafetyCheckResult {
  passed: boolean;
  constraintId: string;
  severity: SafetySeverity;
  message: string;
  overridePossible: boolean;
}

enum SafetySeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL',
}
```

### 7.2 IGuardianAngel - Safety Agent

```typescript
/**
 * Guardian Angel agent for proactive safety.
 */
interface IGuardianAngel {
  // Decision Making
  review(context: IGuardianContext): IGuardianDecision;

  // Learning
  learn(feedback: IGuardianFeedback): void;

  // Statistics
  getStats(): IGuardianStats;
}

interface IGuardianContext {
  action: unknown;
  agent: IAgentState;
  colony: IColonyStats;
  history: IGuardianDecision[];
}

interface IGuardianDecision {
  allowed: boolean;
  modified?: unknown;
  reason: string;
  confidence: number;
  constraintResults: IConstraintResult[];
}

interface IConstraintResult {
  constraintId: string;
  passed: boolean;
  severity: ConstraintSeverity;
  message: string;
}

interface IGuardianFeedback {
  decision: IGuardianDecision;
  outcome: 'success' | 'failure' | 'neutral';
  actualImpact?: unknown;
}
```

---

## 8. Lifecycle Interfaces

### 8.1 IInitializable - Initialization Contract

```typescript
/**
 * Interface for components that require initialization.
 */
interface IInitializable {
  initialize(): Promise<void>;
  isInitialized(): boolean;
}
```

### 8.2 IShutdownable - Shutdown Contract

```typescript
/**
 * Interface for components that require clean shutdown.
 */
interface IShutdownable {
  shutdown(): Promise<void>;
  isShutdown(): boolean;
}
```

### 8.3 IRecoverable - Recovery Contract

```typescript
/**
 * Interface for components that support recovery from failure.
 */
interface IRecoverable {
  // Checkpointing
  createCheckpoint(): Promise<ICheckpoint>;
  restoreFromCheckpoint(checkpoint: ICheckpoint): Promise<void>;

  // Recovery
  canRecover(error: Error): boolean;
  recover(error: Error): Promise<void>;
}

interface ICheckpoint {
  id: string;
  timestamp: number;
  state: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}
```

### 8.4 ILifecycleManager - Lifecycle Orchestration

```typescript
/**
 * Manages the lifecycle of multiple components.
 */
interface ILifecycleManager<T extends IInitializable & IShutdownable> {
  // Registration
  register(name: string, component: T): void;
  unregister(name: string): void;

  // Bulk Operations
  initializeAll(): Promise<void>;
  shutdownAll(): Promise<void>;

  // Status
  getStatus(name: string): ILifecycleStatus;
  getAllStatus(): Record<string, ILifecycleStatus>;
}

interface ILifecycleStatus {
  name: string;
  initialized: boolean;
  shutdown: boolean;
  error?: Error;
  lastActivity: number;
}
```

---

## 9. API Layer Interfaces

### 9.1 IAPIServer - WebSocket Server

```typescript
/**
 * WebSocket API server for POLLN.
 */
interface IAPIServer {
  // Lifecycle
  start(port: number): Promise<void>;
  stop(): Promise<void>;

  // Client Management
  getConnectedClients(): IAuthenticatedClient[];
  broadcast(message: IServerMessage): void;

  // Statistics
  getStats(): IAPIServerStats;
}
```

### 9.2 IMessageHandler - Message Processing

```typescript
/**
 * Handler for processing API messages.
 */
interface IMessageHandler {
  canHandle(messageType: ClientMessageType): boolean;
  handle(
    message: IClientMessage,
    client: IAuthenticatedClient
  ): Promise<IServerMessage>;
}
```

### 9.3 IMiddleware - Request Pipeline

```typescript
/**
 * Middleware for API request processing.
 */
interface IMiddleware {
  process(
    message: IClientMessage,
    client: IAuthenticatedClient,
    next: () => Promise<IServerMessage>
  ): Promise<IServerMessage>;
}
```

---

## 10. System Invariants

### 10.1 Agent Invariants

```typescript
/**
 * Invariants that must always hold for agents.
 */
interface AgentInvariants {
  // I1: Agent ID Uniqueness
  // All agent IDs within a colony must be unique
  'agent:id:unique': true;

  // I2: Value Function Bounds
  // Value function must always be in [0, 1]
  'agent:valueFunction:bounds': (v: number) => v >= 0 && v <= 1;

  // I3: State Consistency
  // Agent state must be serializable
  'agent:state:serializable': true;

  // I4: Lifecycle Order
  // initialize() must be called before process()
  'agent:lifecycle:order': true;

  // I5: Shutdown Idempotency
  // shutdown() must be idempotent
  'agent:shutdown:idempotent': true;
}
```

### 10.2 Colony Invariants

```typescript
/**
 * Invariants that must always hold for colonies.
 */
interface ColonyInvariants {
  // C1: Agent Count Limit
  // Agent count must not exceed maxAgents
  'colony:agentCount:limit': (count: number, max: number) => count <= max;

  // C2: Resource Budget
  // Total resource usage must not exceed budget
  'colony:resources:budget': true;

  // C3: Shannon Diversity
  // Diversity index must be non-negative
  'colony:diversity:nonNegative': (d: number) => d >= 0;

  // C4: Agent Registration Atomicity
  // Agent registration is atomic (all or nothing)
  'colony:registration:atomic': true;
}
```

### 10.3 Communication Invariants

```typescript
/**
 * Invariants that must always hold for communication.
 */
interface CommunicationInvariants {
  // A1: Package Traceability
  // Every package has a valid causalChainId
  'a2a:traceability:chainId': (pkg: IA2APackage) => pkg.causalChainId !== '';

  // A2: Causal Chain Integrity
  // All parentIds in a package must exist
  'a2a:causal:parentExists': true;

  // A3: Privacy Level Hierarchy
  // PRIVATE packages cannot reference PUBLIC content
  'a2a:privacy:hierarchy': true;

  // A4: Timestamp Monotonicity
  // Timestamps must be monotonically increasing within a chain
  'a2a:timestamp:monotonic': true;
}
```

### 10.4 Learning Invariants

```typescript
/**
 * Invariants that must always hold for learning.
 */
interface LearningInvariants {
  // L1: Weight Bounds
  // Synaptic weights must be in [minWeight, maxWeight]
  'learning:weight:bounds': (w: number, min: number, max: number) =>
    w >= min && w <= max;

  // L2: Learning Rate Positivity
  // Learning rate must be positive
  'learning:rate:positive': (lr: number) => lr > 0;

  // L3: Value Prediction Bounded
  // Value predictions must be in reasonable range
  'learning:value:bounded': (v: number) => v >= -1000 && v <= 1000;

  // L4: Plinko Temperature
  // Temperature must be >= minTemperature
  'plinko:temperature:min': (t: number, min: number) => t >= min;
}
```

### 10.5 KV-Cache Invariants

```typescript
/**
 * Invariants that must always hold for KV-Cache system.
 */
interface KVCacheInvariants {
  // K1: Anchor Pool Capacity
  // Anchor count must not exceed maxAnchors
  'kv:anchor:capacity': (count: number, max: number) => count <= max;

  // K2: Quality Score Bounds
  // Quality score must be in [0, 1]
  'kv:quality:bounds': (q: number) => q >= 0 && q <= 1;

  // K3: Embedding Dimension Consistency
  // All embeddings in a pool must have the same dimension
  'kv:embedding:dimension': true;

  // K4: Compression Ratio Positivity
  // Compression ratio must be positive
  'kv:compression:positive': (r: number) => r > 0;

  // K5: LRU Consistency
  // LRU list must contain exactly the anchors in the pool
  'kv:lru:consistency': true;
}
```

### 10.6 Safety Invariants

```typescript
/**
 * Invariants that must always hold for safety.
 */
interface SafetyInvariants {
  // S1: Safety Override Priority
  // SAFETY layer always overrides all other layers
  'safety:layer:priority': true;

  // S2: Constraint Activation
  // cannotOverride constraints must always be checked
  'safety:constraint:always': true;

  // S3: Emergency State
  // Emergency state blocks all non-safety operations
  'safety:emergency:block': true;

  // S4: Guardian Decision Required
  // All actions must be reviewed by Guardian before execution
  'safety:guardian:required': true;
}
```

---

## Appendix A: Type Aliases

```typescript
// Common type aliases used throughout the system

type AgentId = string;
type ColonyId = string;
type TopicName = string;
type CausalChainId = string;
type AnchorId = string;
type LayerId = number;

type EmbeddingVector = number[];
type TokenSequence = number[];

type Timestamp = number;
type DurationMs = number;

type Probability = number; // [0, 1]
type Weight = number;      // [0, 1]
type Score = number;       // [0, 1]

type AsyncResult<T> = Promise<Result<T, Error>>;

interface Result<T, E> {
  ok: boolean;
  value?: T;
  error?: E;
}
```

---

## Appendix B: Error Types

```typescript
/**
 * Standard error types for the POLLN system.
 */
enum POLLNErrorCode {
  // Agent Errors
  AGENT_NOT_FOUND = 'AGENT_NOT_FOUND',
  AGENT_ALREADY_EXISTS = 'AGENT_ALREADY_EXISTS',
  AGENT_INITIALIZATION_FAILED = 'AGENT_INITIALIZATION_FAILED',
  AGENT_SHUTDOWN_FAILED = 'AGENT_SHUTDOWN_FAILED',

  // Colony Errors
  COLONY_NOT_FOUND = 'COLONY_NOT_FOUND',
  COLONY_CAPACITY_EXCEEDED = 'COLONY_CAPACITY_EXCEEDED',
  COLONY_RESOURCE_EXHAUSTED = 'COLONY_RESOURCE_EXHAUSTED',

  // Communication Errors
  A2A_PACKAGE_INVALID = 'A2A_PACKAGE_INVALID',
  A2A_CHAIN_BROKEN = 'A2A_CHAIN_BROKEN',
  TOPIC_NOT_FOUND = 'TOPIC_NOT_FOUND',

  // Learning Errors
  LEARNING_CONVERGENCE_FAILED = 'LEARNING_CONVERGENCE_FAILED',
  SYNAPSE_WEIGHT_VIOLATION = 'SYNAPSE_WEIGHT_VIOLATION',

  // KV-Cache Errors
  KV_ANCHOR_NOT_FOUND = 'KV_ANCHOR_NOT_FOUND',
  KV_POOL_CAPACITY_EXCEEDED = 'KV_POOL_CAPACITY_EXCEEDED',
  KV_COMPRESSION_FAILED = 'KV_COMPRESSION_FAILED',

  // Safety Errors
  SAFETY_CONSTRAINT_VIOLATION = 'SAFETY_CONSTRAINT_VIOLATION',
  SAFETY_EMERGENCY_ACTIVE = 'SAFETY_EMERGENCY_ACTIVE',
  GUARDIAN_REJECTED = 'GUARDIAN_REJECTED',

  // Distributed Errors
  DISTRIBUTED_CONNECTION_FAILED = 'DISTRIBUTED_CONNECTION_FAILED',
  DISTRIBUTED_NODE_UNREACHABLE = 'DISTRIBUTED_NODE_UNREACHABLE',
  DISTRIBUTED_CONSENSUS_FAILED = 'DISTRIBUTED_CONSENSUS_FAILED',
}

class POLLNError extends Error {
  constructor(
    public code: POLLNErrorCode,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'POLLNError';
  }
}
```

---

## Appendix C: Configuration Schemas

```typescript
/**
 * Complete configuration schema for POLLN system.
 */
interface POLLNConfig {
  // Colony Configuration
  colony: IColonyConfig;

  // Learning Configuration
  learning: {
    hebbian: {
      learningRate: number;
      decayRate: number;
      minWeight: number;
      maxWeight: number;
      traceLength: number;
      traceDecay: number;
      ojaNormalization: boolean;
    };
    plinko: {
      temperature: number;
      minTemperature: number;
      decayRate: number;
    };
    valueNetwork: {
      lambda: number;
      gamma: number;
      learningRate: number;
    };
  };

  // KV-Cache Configuration
  kvCache: {
    anchorPool: IKVAnchorPoolConfig;
    matcher: IAnchorMatcherConfig;
    predictor: IOffsetPredictorConfig;
  };

  // Safety Configuration
  safety: {
    constraints: IConstitutionalConstraint[];
    emergencyShutdownEnabled: boolean;
    guardianEnabled: boolean;
  };

  // Distributed Configuration (Optional)
  distributed?: IDistributedConfig;

  // API Configuration (Optional)
  api?: {
    port: number;
    rateLimit: IRateLimitConfig;
    authentication: boolean;
  };
}
```

---

*Document Version: 1.0.0*
*Compatible with POLLN v5.0.0+*
