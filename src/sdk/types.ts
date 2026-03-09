/**
 * POLLN SDK Types
 * High-level TypeScript types for the POLLN SDK
 */

// ============================================================================
// SDK Configuration
// ============================================================================

export interface PollnSDKConfig {
  /**
   * API key for authentication (optional for local colonies)
   */
  apiKey?: string;

  /**
   * WebSocket endpoint for remote colonies
   * Format: ws://localhost:3000 or wss://api.polln.ai
   */
  endpoint?: string;

  /**
   * Default timeout for operations (ms)
   * @default 30000
   */
  timeout?: number;

  /**
   * Enable debug logging
   * @default false
   */
  debug?: boolean;

  /**
   * Default colony configuration
   */
  defaults?: {
    maxAgents?: number;
    resourceBudget?: ResourceBudgetConfig;
  };
}

export interface ResourceBudgetConfig {
  totalCompute?: number;
  totalMemory?: number;
  totalNetwork?: number;
}

// ============================================================================
// Colony Management
// ============================================================================

export interface ColonyConfig {
  /**
   * Unique identifier (auto-generated if not provided)
   */
  id?: string;

  /**
   * Human-readable name
   */
  name: string;

  /**
   * Maximum number of agents
   * @default 100
   */
  maxAgents?: number;

  /**
   * Resource budget for the colony
   */
  resourceBudget?: ResourceBudgetConfig;

  /**
   * Enable distributed coordination
   */
  distributed?: boolean;

  /**
   * Distributed backend configuration
   */
  distributedConfig?: {
    backend: 'memory' | 'redis' | 'nats';
    connectionString?: string;
    nodeId?: string;
  };
}

export interface ColonyState {
  id: string;
  name: string;
  gardenerId: string;
  totalAgents: number;
  activeAgents: number;
  dormantAgents: number;
  shannonDiversity: number;
  createdAt: number;
  lastActive: number;
}

// ============================================================================
// Agent Management
// ============================================================================

export type AgentCategory = 'ephemeral' | 'role' | 'core';

export interface AgentConfig {
  /**
   * Unique identifier (auto-generated if not provided)
   */
  id?: string;

  /**
   * Agent category
   */
  category: AgentCategory;

  /**
   * Agent type identifier
   */
  typeId?: string;

  /**
   * Human-readable name
   */
  name?: string;

  /**
   * Goal or purpose of the agent
   */
  goal?: string;

  /**
   * Model family to use
   * @default 'default'
   */
  modelFamily?: string;

  /**
   * Default model parameters
   */
  defaultParams?: Record<string, unknown>;

  /**
   * Input topics for SPORE protocol
   */
  inputTopics?: string[];

  /**
   * Output topic for SPORE protocol
   */
  outputTopic?: string;

  /**
   * Target latency in milliseconds
   */
  targetLatencyMs?: number;

  /**
   * Maximum memory in MB
   */
  maxMemoryMB?: number;

  /**
   * Minimum training examples
   */
  minExamples?: number;

  /**
   * Whether world model is required
   */
  requiresWorldModel?: boolean;

  /**
   * Maximum lifetime for ephemeral agents (ms)
   */
  maxLifetimeMs?: number;
}

export interface AgentState {
  id: string;
  category: AgentCategory;
  typeId: string;
  name?: string;
  goal?: string;
  status: 'dormant' | 'active' | 'hibernating' | 'error';
  valueFunction: number;
  successCount: number;
  failureCount: number;
  avgLatencyMs: number;
  successRate: number;
  executionCount: number;
  lastActive: number;
  createdAt: number;
}

// ============================================================================
// Task Execution
// ============================================================================

export interface TaskInput<T = unknown> {
  /**
   * Task identifier
   */
  id?: string;

  /**
   * Agent to execute the task
   */
  agentId?: string;

  /**
   * Task type (for agent selection)
   */
  type?: string;

  /**
   * Input data for the task
   */
  input: T;

  /**
   * Priority for task selection
   * @default 0.5
   */
  priority?: number;

  /**
   * Timeout for task execution (ms)
   */
  timeout?: number;

  /**
   * Task metadata
   */
  metadata?: Record<string, unknown>;
}

export interface TaskResult<T = unknown> {
  /**
   * Task identifier
   */
  id: string;

  /**
   * Agent that executed the task
   */
  agentId: string;

  /**
   * Whether the task was successful
   */
  success: boolean;

  /**
   * Output data
   */
  output: T;

  /**
   * Execution time in milliseconds
   */
  executionTimeMs: number;

  /**
   * Error message if failed
   */
  error?: string;

  /**
   * Task metadata
   */
  metadata?: Record<string, unknown>;

  /**
   * Timestamp
   */
  timestamp: number;
}

export interface TaskStreamChunk<T = unknown> {
  /**
   * Task identifier
   */
  taskId: string;

  /**
   * Agent executing the task
   */
  agentId: string;

  /**
   * Chunk data
   */
  chunk: T;

  /**
   * Whether this is the final chunk
   */
  done: boolean;

  /**
   * Cumulative execution time
   */
  executionTimeMs: number;

  /**
   * Timestamp
   */
  timestamp: number;
}

// ============================================================================
// Events
// ============================================================================

export type EventType =
  | 'colony:created'
  | 'colony:destroyed'
  | 'colony:agent:added'
  | 'colony:agent:removed'
  | 'colony:agent:updated'
  | 'agent:born'
  | 'agent:activated'
  | 'agent:deactivated'
  | 'agent:task:started'
  | 'agent:task:completed'
  | 'agent:task:failed'
  | 'task:created'
  | 'task:completed'
  | 'task:failed'
  | 'dream:started'
  | 'dream:completed'
  | 'dream:episode'
  | 'error';

export interface Event<T = unknown> {
  type: EventType;
  data: T;
  timestamp: number;
  colonyId?: string;
  agentId?: string;
  taskId?: string;
}

export type EventHandler<T = unknown> = (event: Event<T>) => void | Promise<void>;

// ============================================================================
// Errors
// ============================================================================

export type ErrorCode =
  | 'SDK_NOT_INITIALIZED'
  | 'COLONY_NOT_FOUND'
  | 'COLONY_ALREADY_EXISTS'
  | 'AGENT_NOT_FOUND'
  | 'AGENT_ALREADY_EXISTS'
  | 'AGENT_CREATION_FAILED'
  | 'TASK_NOT_FOUND'
  | 'TASK_EXECUTION_FAILED'
  | 'TASK_TIMEOUT'
  | 'INVALID_CONFIGURATION'
  | 'CONNECTION_FAILED'
  | 'AUTHENTICATION_FAILED'
  | 'PERMISSION_DENIED'
  | 'RESOURCE_EXHAUSTED'
  | 'STREAM_INTERRUPTED'
  | 'UNKNOWN_ERROR';

export class PollnSDKError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'PollnSDKError';
  }
}

// ============================================================================
// Streaming
// ============================================================================

export interface StreamOptions {
  /**
   * Chunk size for streaming
   * @default 1024
   */
  chunkSize?: number;

  /**
   * Delay between chunks (ms)
   * @default 0
   */
  chunkDelay?: number;

  /**
   * Include metadata in chunks
   * @default true
   */
  includeMetadata?: boolean;
}

// ============================================================================
// Query & Filtering
// ============================================================================

export interface AgentQuery {
  category?: AgentCategory;
  status?: AgentState['status'];
  minSuccessRate?: number;
  maxLatencyMs?: number;
  limit?: number;
}

export interface ColonyQuery {
  active?: boolean;
  minAgents?: number;
  maxAgents?: number;
  limit?: number;
}
