/**
 * POLLN Debugging Tools - Type Definitions
 *
 * Comprehensive type definitions for debugging, profiling, tracing,
 * and visualization of POLLN colonies and agents.
 */

// ============================================================================
// Core Debug Types
// ============================================================================

/**
 * Debug configuration options
 */
export interface DebugConfig {
  /**
   * Enable verbose logging
   */
  verbose?: boolean;

  /**
   * Maximum trace history to retain
   */
  maxTraceHistory?: number;

  /**
   * Maximum profiling samples to retain
   */
  maxProfilingSamples?: number;

  /**
   * Enable automatic profiling
   */
  autoProfile?: boolean;

  /**
   * Profile sampling interval in milliseconds
   */
  profileSampleInterval?: number;

  /**
   * Enable trace collection
   */
  enableTracing?: boolean;

  /**
   * Custom output directory for debug artifacts
   */
  outputDir?: string;

  /**
   * Enable visualization data export
   */
  enableVisualization?: boolean;
}

/**
 * Agent inspection result
 */
export interface AgentInspection {
  /**
   * Agent ID
   */
  agentId: string;

  /**
   * Agent type/category
   */
  category: string;

  /**
   * Current agent state
   */
  state: Record<string, unknown>;

  /**
   * Call stack (if applicable)
   */
  callStack: StackFrame[];

  /**
   * Local variables
   */
  variables: Record<string, unknown>;

  /**
   * Recent A2A packages sent
   */
  sentPackages: A2APackageTrace[];

  /**
   * Recent A2A packages received
   */
  receivedPackages: A2APackageTrace[];

  /**
   * Current breakpoint status
   */
  breakpointStatus: BreakpointStatus;

  /**
   * Performance metrics
   */
  metrics: AgentMetrics;

  /**
   * Timestamp of inspection
   */
  timestamp: number;
}

/**
 * Stack frame in call stack
 */
export interface StackFrame {
  /**
   * Function/method name
   */
  functionName: string;

  /**
   * Source file
   */
  file: string;

  /**
   * Line number
   */
  line: number;

  /**
   * Column number
   */
  column: number;

  /**
   * Local variables in this frame
   */
  locals?: Record<string, unknown>;
}

/**
 * A2A package trace information
 */
export interface A2APackageTrace {
  /**
   * Package ID
   */
  packageId: string;

  /**
   * Causal chain ID
   */
  causalChainId: string;

  /**
   * Parent package IDs
   */
  parentIds: string[];

  /**
   * Source agent ID
   */
  fromAgentId: string;

  /**
   * Target agent ID
   */
  toAgentId: string;

  /**
   * Payload type
   */
  payloadType: string;

  /**
   * Timestamp sent
   */
  timestamp: number;

  /**
   * Delivery status
   */
  status: 'pending' | 'delivered' | 'failed';

  /**
   * Processing time (if delivered)
   */
  processingTime?: number;
}

/**
 * Breakpoint status
 */
export interface BreakpointStatus {
  /**
   * Whether a breakpoint is currently hit
   */
  isHit: boolean;

  /**
   * Active breakpoint ID (if hit)
   */
  breakpointId?: string;

  /**
   * Breakpoint condition (if any)
   */
  condition?: string;

  /**
   * Number of times breakpoint has been hit
   */
  hitCount: number;
}

/**
 * Agent performance metrics
 */
export interface AgentMetrics {
  /**
   * Total execution count
   */
  executionCount: number;

  /**
   * Success count
   */
  successCount: number;

  /**
   * Failure count
   */
  failureCount: number;

  /**
   * Average latency in milliseconds
   */
  avgLatencyMs: number;

  /**
   * Minimum latency
   */
  minLatencyMs: number;

  /**
   * Maximum latency
   */
  maxLatencyMs: number;

  /**
   * Average CPU usage (percentage)
   */
  avgCpuUsage: number;

  /**
   * Average memory usage in MB
   */
  avgMemoryUsage: number;

  /**
   * Average value function
   */
  avgValueFunction: number;

  /**
   * Total learning events
   */
  learningEvents: number;
}

// ============================================================================
// Visualization Types
// ============================================================================

/**
 * Graph visualization data
 */
export interface GraphVisualization {
  /**
   * Colony ID
   */
  colonyId: string;

  /**
   * Graph nodes (agents)
   */
  nodes: GraphNode[];

  /**
   * Graph edges (connections)
   */
  edges: GraphEdge[];

  /**
   * Graph layout information
   */
  layout: GraphLayout;

  /**
   * Clustering information
   */
  clusters?: GraphCluster[];

  /**
   * Visualization metadata
   */
  metadata: VisualizationMetadata;
}

/**
 * Graph node (agent)
 */
export interface GraphNode {
  /**
   * Unique node ID
   */
  id: string;

  /**
   * Agent ID
   */
  agentId: string;

  /**
   * Node label
   */
  label: string;

  /**
   * Node type (category)
   */
  type: string;

  /**
   * Node position
   */
  position: Position;

  /**
   * Node size (relative importance)
   */
  size: number;

  /**
   * Node color (category-based)
   */
  color: string;

  /**
   * Node properties
   */
  properties: Record<string, unknown>;

  /**
   * Node health/status
   */
  health: 'healthy' | 'degraded' | 'unhealthy';

  /**
   * Node activity level
   */
  activity: number; // 0-1
}

/**
 * Graph edge (connection)
 */
export interface GraphEdge {
  /**
   * Unique edge ID
   */
  id: string;

  /**
   * Source node ID
   */
  source: string;

  /**
   * Target node ID
   */
  target: string;

  /**
   * Edge label
   */
  label?: string;

  /**
   * Edge type
   */
  type: 'strong' | 'weak' | 'inhibitory';

  /**
   * Connection weight (synaptic weight)
   */
  weight: number;

  /**
   * Edge thickness (visual representation)
   */
  thickness: number;

  /**
   * Communication frequency
   */
  frequency: number;

  /**
   * Edge color
   */
  color: string;

  /**
   * Directionality
   */
  directed: boolean;
}

/**
 * Position in 2D space
 */
export interface Position {
  /**
   * X coordinate
   */
  x: number;

  /**
   * Y coordinate
   */
  y: number;
}

/**
 * Graph layout information
 */
export interface GraphLayout {
  /**
   * Layout algorithm used
   */
  algorithm: 'force' | 'hierarchical' | 'circular' | 'random';

  /**
   * Layout dimensions
   */
  dimensions: {
    width: number;
    height: number;
  };

  /**
   * Layout parameters
   */
  parameters: Record<string, unknown>;
}

/**
 * Graph cluster
 */
export interface GraphCluster {
  /**
   * Cluster ID
   */
  id: string;

  /**
   * Cluster label
   */
  label: string;

  /**
   * Node IDs in cluster
   */
  nodes: string[];

  /**
   * Cluster color
   */
  color: string;

  /**
   * Cluster strength
   */
  strength: number;
}

/**
 * Visualization metadata
 */
export interface VisualizationMetadata {
  /**
   * Visualization timestamp
   */
  timestamp: number;

  /**
   * Total nodes
   */
  nodeCount: number;

  /**
   * Total edges
   */
  edgeCount: number;

  /**
   * Graph density
   */
  density: number;

  /**
   * Average clustering coefficient
   */
  avgClusteringCoefficient: number;

  /**
   * Average path length
   */
  avgPathLength: number;

  /**
   * Graph modularity
   */
  modularity: number;
}

// ============================================================================
// Tracing Types
// ============================================================================

/**
 * Distributed trace
 */
export interface DistributedTrace {
  /**
   * Unique trace ID
   */
  traceId: string;

  /**
   * Causal chain ID
   */
  causalChainId: string;

  /**
   * Trace root (originating operation)
   */
  root: TraceSpan;

  /**
   * All spans in the trace
   */
  spans: TraceSpan[];

  /**
   * Trace timeline
   */
  timeline: TraceTimeline;

  /**
   * Trace statistics
   */
  stats: TraceStats;

  /**
   * Trace errors (if any)
   */
  errors: TraceError[];

  /**
   * Trace metadata
   */
  metadata: TraceMetadata;
}

/**
 * Trace span (single operation)
 */
export interface TraceSpan {
  /**
   * Unique span ID
   */
  spanId: string;

  /**
   * Parent span ID (if any)
   */
  parentSpanId?: string;

  /**
   * Operation name
   */
  operationName: string;

  /**
   * Agent ID that executed the operation
   */
  agentId: string;

  /**
   * Colony ID
   */
  colonyId: string;

  /**
   * Start timestamp
   */
  startTime: number;

  /**
   * End timestamp
   */
  endTime: number;

  /**
   * Duration in milliseconds
   */
  duration: number;

  /**
   * Span status
   */
  status: 'ok' | 'error' | 'cancelled';

  /**
   * Span tags (metadata)
   */
  tags: Record<string, string | number | boolean>;

  /**
   * Span logs
   */
  logs: TraceLog[];

  /**
   * Span events
   */
  events: TraceEvent[];

  /**
   * Linked A2A packages
   */
  packageIds: string[];
}

/**
 * Trace log entry
 */
export interface TraceLog {
  /**
   * Log timestamp
   */
  timestamp: number;

  /**
   * Log level
   */
  level: 'debug' | 'info' | 'warn' | 'error';

  /**
   * Log message
   */
  message: string;

  /**
   * Log fields
   */
  fields?: Record<string, unknown>;
}

/**
 * Trace event
 */
export interface TraceEvent {
  /**
   * Event timestamp
   */
  timestamp: number;

  /**
   * Event name
   */
  name: string;

  /**
   * Event attributes
   */
  attributes: Record<string, unknown>;
}

/**
 * Trace timeline
 */
export interface TraceTimeline {
  /**
   * Overall start time
   */
  startTime: number;

  /**
   * Overall end time
   */
  endTime: number;

  /**
   * Total duration
   */
  duration: number;

  /**
   * Critical path (spans on critical path)
   */
  criticalPath: string[];
}

/**
 * Trace statistics
 */
export interface TraceStats {
  /**
   * Total span count
   */
  totalSpans: number;

  /**
   * Error count
   */
  errorCount: number;

  /**
   * Total duration
   */
  totalDuration: number;

  /**
   * Average span duration
   */
  avgDuration: number;

  /**
   * Min span duration
   */
  minDuration: number;

  /**
   * Max span duration
   */
  maxDuration: number;

  /**
   * Agents involved
   */
  agentsInvolved: string[];

  /**
   * Colonies involved
   */
  coloniesInvolved: string[];
}

/**
 * Trace error
 */
export interface TraceError {
  /**
   * Error ID
   */
  errorId: string;

  /**
   * Span ID where error occurred
   */
  spanId: string;

  /**
   * Error message
   */
  message: string;

  /**
   * Error stack trace
   */
  stackTrace?: string;

  /**
   * Error timestamp
   */
  timestamp: number;
}

/**
 * Trace metadata
 */
export interface TraceMetadata {
  /**
   * Trace creation timestamp
   */
  timestamp: number;

  /**
   * Trace type
   */
  type: 'task' | 'learning' | 'communication' | 'evolution' | 'dream';

  /**
   * User ID (if applicable)
   */
  userId?: string;

  /**
   * Session ID (if applicable)
   */
  sessionId?: string;

  /**
   * Additional tags
   */
  tags: string[];
}

// ============================================================================
// Profiling Types
// ============================================================================

/**
 * Performance profile
 */
export interface PerformanceProfile {
  /**
   * Profile ID
   */
  profileId: string;

  /**
   * Profile type
   */
  type: 'cpu' | 'memory' | 'io' | 'custom';

  /**
   * Profile start time
   */
  startTime: number;

  /**
   * Profile end time
   */
  endTime: number;

  /**
   * Profile duration
   */
  duration: number;

  /**
   * Sample data points
   */
  samples: ProfileSample[];

  /**
   * Hot spots (most time-consuming operations)
   */
  hotspots: HotSpot[];

  /**
   * Call tree
   */
  callTree: CallTreeNode;

  /**
   * Profile statistics
   */
  stats: ProfileStats;

  /**
   * Optimization suggestions
   */
  suggestions: OptimizationSuggestion[];
}

/**
 * Profile sample
 */
export interface ProfileSample {
  /**
   * Sample timestamp
   */
  timestamp: number;

  /**
   * Stack trace at sample time
   */
  stack: string[];

  /**
   * CPU usage at sample time
   */
  cpuUsage: number;

  /**
   * Memory usage at sample time
   */
  memoryUsage: number;

  /**
   * Active agent ID
   */
  agentId?: string;

  /**
   * Active operation
   */
  operation?: string;
}

/**
 * Performance hot spot
 */
export interface HotSpot {
  /**
   * Function/operation name
   */
  name: string;

  /**
   * File location
   */
  file: string;

  /**
   * Line number
   */
  line: number;

  /**
   * Total time spent (ms)
   */
  totalTime: number;

  /**
   * Percentage of total time
   */
  percentage: number;

  /**
   * Call count
   */
  callCount: number;

  /**
   * Average time per call
   */
  avgTimePerCall: number;

  /**
   * Severity (0-1)
   */
  severity: number;
}

/**
 * Call tree node
 */
export interface CallTreeNode {
  /**
   * Function/operation name
   */
  name: string;

  /**
   * Total time in this function and children
   */
  totalTime: number;

  /**
   * Self time (excluding children)
   */
  selfTime: number;

  /**
   * Call count
   */
  callCount: number;

  /**
   * Percentage of total time
   */
  percentage: number;

  /**
   * Child nodes
   */
  children: CallTreeNode[];

  /**
   * File location
   */
  file?: string;

  /**
   * Line number
   */
  line?: number;
}

/**
 * Profile statistics
 */
export interface ProfileStats {
  /**
   * Total samples collected
   */
  totalSamples: number;

  /**
   * Total duration profiled
   */
  totalDuration: number;

  /**
   * Average CPU usage
   */
  avgCpuUsage: number;

  /**
   * Peak CPU usage
   */
  peakCpuUsage: number;

  /**
   * Average memory usage
   */
  avgMemoryUsage: number;

  /**
   * Peak memory usage
   */
  peakMemoryUsage: number;

  /**
   * Number of unique functions called
   */
  uniqueFunctions: number;

  /**
   * Total function calls
   */
  totalCalls: number;
}

/**
 * Optimization suggestion
 */
export interface OptimizationSuggestion {
  /**
   * Suggestion ID
   */
  id: string;

  /**
   * Suggestion type
   */
  type: 'cache' | 'parallelize' | 'optimize' | 'refactor' | 'scale';

  /**
   * Suggestion priority (0-1)
   */
  priority: number;

  /**
   * Suggestion title
   */
  title: string;

  /**
   * Suggestion description
   */
  description: string;

  /**
   * Affected function/operation
   */
  target: string;

  /**
   * Expected improvement
   */
  expectedImprovement: string;

  /**
   * Estimated effort to implement
   */
  effort: 'low' | 'medium' | 'high';
}

// ============================================================================
// Replay Types
// ============================================================================

/**
 * Execution replay session
 */
export interface ReplaySession {
  /**
   * Replay session ID
   */
  sessionId: string;

  /**
   * Original causal chain ID
   */
  causalChainId: string;

  /**
   * Replay start time
   */
  startTime: number;

  /**
   * Replay end time (or null if in progress)
   */
  endTime?: number;

  /**
   * Replay status
   */
  status: 'running' | 'completed' | 'failed' | 'cancelled' | 'paused';

  /**
   * Original execution trace
   */
  originalTrace: DistributedTrace;

  /**
   * Replay events
   */
  events: ReplayEvent[];

  /**
   * State snapshots
   */
  snapshots: StateSnapshot[];

  /**
   * Divergences from original execution
   */
  divergences: ReplayDivergence[];

  /**
   * Replay statistics
   */
  stats: ReplayStats;
}

/**
 * Replay event
 */
export interface ReplayEvent {
  /**
   * Event ID
   */
  eventId: string;

  /**
   * Event sequence number
   */
  sequence: number;

  /**
   * Timestamp
   */
  timestamp: number;

  /**
   * Event type
   */
  type: 'agent_start' | 'agent_end' | 'package_send' | 'package_receive' | 'state_change' | 'error';

  /**
   * Agent ID involved
   */
  agentId: string;

  /**
   * Event data
   */
  data: Record<string, unknown>;
}

/**
 * State snapshot
 */
export interface StateSnapshot {
  /**
   * Snapshot ID
   */
  snapshotId: string;

  /**
   * Timestamp
   */
  timestamp: number;

  /**
   * Agent states
   */
  agentStates: Record<string, Record<string, unknown>>;

  /**
   * Colony state
   */
  colonyState: Record<string, unknown>;

  /**
   * Global variables
   */
  globals: Record<string, unknown>;
}

/**
 * Replay divergence
 */
export interface ReplayDivergence {
  /**
   * Divergence ID
   */
  divergenceId: string;

  /**
   * Event sequence where divergence occurred
   */
  sequence: number;

  /**
   * Divergence type
   */
  type: 'value' | 'timing' | 'order' | 'error' | 'missing';

  /**
   * Expected value/behavior
   */
  expected: unknown;

  /**
   * Actual value/behavior
   */
  actual: unknown;

  /**
   * Divergence severity
   */
  severity: 'low' | 'medium' | 'high' | 'critical';

  /**
   * Divergence description
   */
  description: string;
}

/**
 * Replay statistics
 */
export interface ReplayStats {
  /**
   * Total events replayed
   */
  totalEvents: number;

  /**
   * Successful events
   */
  successfulEvents: number;

  /**
   * Failed events
   */
  failedEvents: number;

  /**
   * Divergences detected
   */
  divergences: number;

  /**
   * Total replay time
   */
  replayTime: number;

  /**
   * Speedup factor (original time / replay time)
   */
  speedup: number;

  /**
   * Snapshot count
   */
  snapshotCount: number;
}

// ============================================================================
// Breakpoint Types
// ============================================================================

/**
 * Breakpoint definition
 */
export interface Breakpoint {
  /**
   * Unique breakpoint ID
   */
  id: string;

  /**
   * Breakpoint condition
   */
  condition: BreakpointCondition;

  /**
   * Breakpoint action when triggered
   */
  action: BreakpointAction;

  /**
   * Whether breakpoint is enabled
   */
  enabled: boolean;

  /**
   * Hit count
   */
  hitCount: number;

  /**
   * Max hits (0 for unlimited)
   */
  maxHits: number;

  /**
   * Creation timestamp
   */
  createdAt: number;

  /**
   * Last hit timestamp
   */
  lastHitAt?: number;
}

/**
 * Breakpoint condition
 */
export interface BreakpointCondition {
  /**
   * Condition type
   */
  type: 'agent_state' | 'package_received' | 'package_sent' | 'error' | 'custom';

  /**
   * Agent ID to watch (or null for all agents)
   */
  agentId?: string;

  /**
   * State predicate (function returning boolean)
   */
  predicate?: string;

  /**
   * Package type filter
   */
  packageType?: string;

  /**
   * Error type filter
   */
  errorType?: string;
}

/**
 * Breakpoint action
 */
export interface BreakpointAction {
  /**
   * Action type
   */
  type: 'pause' | 'log' | 'snapshot' | 'custom';

  /**
   * Action data (message, callback, etc.)
   */
  data?: unknown;
}

// ============================================================================
// Debug Events
// ============================================================================

/**
 * Debug event types
 */
export type DebugEventType =
  | 'breakpoint_hit'
  | 'trace_started'
  | 'trace_completed'
  | 'trace_error'
  | 'profile_started'
  | 'profile_completed'
  | 'snapshot_created'
  | 'inspection_completed'
  | 'divergence_detected';

/**
 * Debug event
 */
export interface DebugEvent<T = unknown> {
  /**
   * Event type
   */
  type: DebugEventType;

  /**
   * Event data
   */
  data: T;

  /**
   * Event timestamp
   */
  timestamp: number;
}

// ============================================================================
// Error Types
// ============================================================================

/**
 * Debug error codes
 */
export type DebugErrorCode =
  | 'DEBUG_NOT_INITIALIZED'
  | 'AGENT_NOT_FOUND'
  | 'COLONY_NOT_FOUND'
  | 'TRACE_NOT_FOUND'
  | 'BREAKPOINT_NOT_FOUND'
  | 'INSPECTION_FAILED'
  | 'VISUALIZATION_FAILED'
  | 'PROFILING_FAILED'
  | 'REPLAY_FAILED'
  | 'INVALID_CONDITION';

/**
 * Debug error class
 */
export class DebugError extends Error {
  constructor(
    public code: DebugErrorCode,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'DebugError';
  }
}
