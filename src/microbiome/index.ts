/**
 * POLLN Microbiome Architecture
 *
 * A digital terrarium where computational agents evolve,
 * compete, cooperate, and self-organize.
 *
 * @module microbiome
 */

// Core types
export * from './types.js';

// Agent types
export * from './virus.js';
export * from './bacteria.js';

// Systems
export * from './metabolism.js';
export * from './population.js';
export * from './ecosystem.js';
export * from './symbiosis.js';
export * from './evolution.js';
export * from './fitness.js';
export * from './genetic.js';
export * from './colony.js';
export * from './murmuration.js';
export * from './colony-memory.js';
export * from './immune.js';
export * from './competition.js';
export * from './metalearning.js';
export * from './selfawareness.js';
export * from './creativity.js';
export * from './performance.js';
export * from './optimization.js';
export * from './scalability.js';

// Integration & Interoperability (Phase 6)
export * from './bridge.js';
export * from './protocol-adapter.js';

// Re-exports for convenience
export {
  // Main class
  DigitalTerrarium,
  createTerrarium,

  // Event type
  EcosystemEvent,
} from './ecosystem.js';

// Colony system exports
export {
  ColonySystem,
  ColonyState,
  ColonyProposal,
  Task,
  Specialization,
  Colony,
  ColonyFormationOptions,
  ColonyStats,
  createColonySystem,
} from './colony.js';

// Murmuration system exports
export {
  MurmurationEngine,
  MurmurationPattern,
  MurmurationMemory,
  PatternExecutionResult,
  PatternDetectionResult,
  CoEvolutionStage,
  createMurmurationEngine,
} from './murmuration.js';

// Colony memory system exports
export {
  ColonyMemory,
  PatternType,
  MemoryPattern,
  MemoryQuery,
  MemoryRetrievalResult,
  ConsolidationResult,
  DecayResult,
  MemoryTransferResult,
  ColonyConfiguration,
  ColonyMemoryConfig,
  ColonyMemoryStats,
  createColonyMemory,
} from './colony-memory.js';

// Meta-learning system exports
export {
  MetaLearningEngine,
  LearningAlgorithm,
  ContextStability,
  DomainKnowledge,
  TaskComplexity,
  LearningStrategy,
  LearningContext,
  LearningOutcome,
  MetaRewardComponents,
  TransferSource,
  TransferResult,
  MetaLearningConfig,
  MetaLearningStats,
  createMetaLearningEngine,
} from './metalearning.js';

// Self-awareness system exports (Phase 7 - Milestone 2)
export {
  SelfAwarenessEngine,
  AwarenessLevel,
  Capability,
  Limitation,
  BehavioralPattern,
  PerformanceEntry,
  SelfModel,
  Goal,
  GoalStatus,
  ValueSystem,
  SelfPrediction,
  Situation,
  PerformanceReport,
  BlindSpot,
  OptimizationPlan,
  OptimizationStrategy as SelfOptimizationStrategy,
  MentalState,
  Experience,
  Insight,
  InsightType,
  SelfAwarenessConfig,
  SelfAwarenessStats,
  createSelfAwarenessEngine,
} from './selfawareness.js';

// Creativity & Goals system exports (Phase 7 - Milestone 3)
export {
  CreativityEngine,
  CreativityLevel,
  NovelIdea,
  AnalogyMapping,
  DivergentThinkingResult,
  Goal as CreativityGoal,
  GoalType,
  GoalStatus as CreativityGoalStatus,
  GoalHierarchy,
  GoalRelationship,
  GoalRelationType,
  DiscoveredValue,
  GoalPlan,
  PlanStep,
  PlanStatus,
  GoalConflict,
  ConflictType,
  ConflictResolution,
  CreativityConfig,
  CreativityStats,
  createCreativityEngine,
} from './creativity.js';

// Performance monitoring exports
export {
  PerformanceMonitor,
  PerformanceMetric,
  PerformanceAlert,
  PerformanceSummary,
  MetricsExport,
  PerformanceMonitorConfig,
  createPerformanceMonitor,
  monitorOperation,
} from './performance.js';

// Performance optimization exports
export {
  PerformanceOptimizer,
  ResultCache,
  OptimizationTarget,
  OptimizationStrategy,
  OptimizationResult,
  PerformanceProfile,
  CacheConfig,
  CacheStats,
  BatchResult,
  GenericObjectPool,
  createPerformanceOptimizer,
  createObjectPool,
} from './optimization.js';

export type {
  CacheEntry,
  LazyLoadingConfig,
  ParallelConfig,
  ObjectPool,
} from './optimization.js';

// Scalability management exports (Phase 5 - Milestone 3)
export {
  ScalabilityManager,
  PartitioningStrategy,
  LoadBalancingStrategy,
  AutoScalingTrigger,
  createScalabilityManager,
  estimateInfrastructure,
} from './scalability.js';

export type {
  NodeInfo as ScalabilityNodeInfo,
  PartitionAssignment as ScalabilityPartitionAssignment,
  EvolutionTask,
  MapReduceResult,
  AutoScalingPolicy,
  FederationConfig,
  ScalabilityStats,
  ScalabilityConfig,
} from './scalability.js';

// Analytics & Insights system exports (Phase 10)
export * from './analytics.js';
export * from './dashboard.js';
export * from './predictive.js';

// Analytics system exports
export {
  AnalyticsPipeline,
  createAnalyticsPipeline,
} from './analytics.js';

// Dashboard system exports
export {
  DashboardSystem,
  createDashboardSystem,
} from './dashboard.js';

// Predictive intelligence exports
export {
  PredictiveEngine,
  createPredictiveEngine,
} from './predictive.js';

export {
  ForecastingAlgorithm,
  PredictionType,
  ConfidenceLevel,
  WarningSeverity,
  WarningType,
  OptimizationType,
} from './predictive.js';

export type {
  TimeSeriesForecast,
  BehaviorPrediction,
  PredictedAction,
  BehaviorPattern,
  ResourcePrediction,
  EarlyWarning,
  RecommendedAction,
  OptimizationRecommendation,
  ScenarioSimulation,
  SimulationParameters,
  SimulationResult,
  BaselineComparison,
  SensitivityAnalysis,
  PredictiveEngineConfig,
} from './predictive.js';

// Security system exports (Phase 9)
export {
  SecurityManager,
  createSecurityManager,
  createDevSecurityManager,
  createProductionSecurityManager,
} from './security.js';

export {
  EncryptionAlgorithm,
  Role,
  Permission,
} from './security.js';

export type {
  EncryptedState,
  CryptoKey,
  KeyPair,
  Credentials,
  AuthToken,
  TokenPayload,
  Signature,
  SignableMessage,
  SecurityConfig,
  SecurityEvent,
  SecurityMetrics,
} from './security.js';

// Threat detection system exports (Phase 9 - Milestone 2)
export {
  ThreatDetector,
  createThreatDetector,
  createThreatDetectorWithConfig,
} from './threat-detection.js';

export {
  ThreatType,
  ThreatLevel,
  AnomalyType,
  VulnerabilitySeverity,
  VulnerabilityType,
  ComplianceFramework,
  SecurityPosture,
  ActionType,
} from './threat-detection.js';

export type {
  AnomalyReport,
  Anomaly,
  BehavioralBaseline,
  ResourceBaseline,
  CommunicationBaseline,
  PerformanceBaseline,
  ActivityPattern,
  IntrusionAlert,
  Evidence,
  EvidenceType,
  RecommendedAction,
  VulnerabilityReport,
  Vulnerability,
  VulnerabilitySummary,
  ComplianceStatus,
  ControlStatus,
  ComplianceGap,
  SecurityMetricsSummary,
  SecurityTrend,
  ThreatDetectorConfig,
} from './threat-detection.js';

// Audit & Compliance system exports (Phase 9 - Milestone 3)
export {
  AuditSystem,
  getAuditSystem,
  shutdownAuditSystem,
} from './audit.js';

export {
  AuditSeverity,
  AuditCategory,
  ComplianceStandard,
} from './audit.js';

export type {
  AuditEvent,
  AuditTrail,
  ComplianceReport,
  ForensicAnalysis,
  RetentionPolicy,
  HashChainEntry,
  Pattern,
  Anomaly as ForensicAnomaly,
  TimelineEvent,
  Connection,
  AuditSystemConfig,
} from './audit.js';

// Distributed Systems exports (Phase 8)
export {
  // Core consensus types
  ConsensusAlgorithm,
  NodeState,
  NodeId,
  LogIndex,
  Term,

  // State and log types
  StateChange,
  LogEntry,
  Vote,
  VoteRequest,
  VoteResponse,
  AppendEntriesRequest,
  AppendEntriesResponse,
  Partition,
  RecoveryStrategy,
  Proposal,
  ConsensusResult,

  // Configuration
  DistributedConsensusConfig,
  ClusterNode,
  ConsensusStats,

  // Main consensus class
  DistributedConsensus,
  createDistributedConsensus,

  // Helper functions
  calculateQuorum,
  detectPartition,
  recoverFromPartition,
} from './distributed.js';

// Distributed ecosystem exports
export {
  DistributedDigitalTerrarium,
  DistributedEcosystemConfig,
  DistributedEcosystemState,
  createDistributedTerrarium,
} from './distributed-ecosystem.js';

// State replication exports (Phase 8 - Milestone 2)
export {
  // Replication strategies
  ReplicationStrategy,
  ConflictResolutionStrategy,
  ClockComparison,

  // Core types
  VectorClock,
  VersionedState,
  ReplicationConflict,
  ReplicationResult,
  SyncResult,
  StateDelta,
  GossipMessage,
  MerkleNode,
  ReplicationHealth,

  // Configuration
  StateReplicatorConfig,

  // Main replicator class
  StateReplicator,
  createStateReplicator,

  // Helper functions
  vectorClockFromJSON,
} from './replication.js';

// Multi-node coordination exports (Phase 8 - Milestone 3)
export {
  // Core types
  NodeInfo,
  ServiceEntry,
  PartitionAssignment,
  AgentMigration,
  MigrationStatus,
  MigrationStrategy,
  LoadBalancingStrategy,
  PartitioningStrategy,
  TransactionState,
  TransactionType,
  DistributedTransaction,
  TransactionOperation,

  // Configuration
  MultiNodeConfig,

  // Main classes
  MultiNodeCoordinator,
  ServiceRegistry,
  ConsistentHashRing,

  // Factory functions
  createMultiNodeCoordinator,
  assignPartitions,
  balanceClusterLoad,
} from './multinode.js';
