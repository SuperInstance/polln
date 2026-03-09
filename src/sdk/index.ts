/**
 * POLLN SDK
 * High-level TypeScript SDK for POLLN distributed intelligence system
 *
 * @example
 * ```typescript
 * import { PollnSDK } from 'polln/sdk';
 *
 * const sdk = new PollnSDK({ apiKey: 'your-api-key' });
 * const colony = await sdk.createColony({ name: 'my-colony' });
 * const agent = await sdk.addAgent(colony.id, {
 *   category: 'ephemeral',
 *   goal: 'process-data'
 * });
 * const result = await sdk.runTask({ colonyId: colony.id, input: data });
 * ```
 */

import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';
import type {
  PollnSDKConfig,
  ColonyConfig,
  ColonyState,
  AgentConfig,
  AgentState,
  TaskInput,
  TaskResult,
  TaskStreamChunk,
  Event,
  EventType,
  EventHandler,
  AgentQuery,
  ColonyQuery,
  StreamOptions,
  AgentCategory,
} from './types.js';
import { PollnSDKError, ErrorCode } from './types.js';

// Import core types (re-exported for convenience)
export * from './types.js';

// ============================================================================
// PollnSDK - Main SDK Class
// ============================================================================

/**
 * High-level SDK for interacting with POLLN colonies
 *
 * Provides a simple, intuitive API for:
 * - Creating and managing colonies
 * - Adding and managing agents
 * - Running tasks (sync and streaming)
 * - Subscribing to events
 * - Querying state
 */
export class PollnSDK extends EventEmitter {
  private config: PollnSDKConfig;
  private colonies: Map<string, ColonyHandle> = new Map();
  private agents: Map<string, Map<string, AgentHandle>> = new Map(); // colonyId -> agents
  private tasks: Map<string, TaskHandle> = new Map();
  private eventHandlers: Map<EventType, Set<EventHandler>> = new Map();
  private initialized: boolean = false;
  private debug: boolean;

  // Internal tracking
  private agentInstanceCounter: number = 0;
  private taskCounter: number = 0;

  constructor(config: PollnSDKConfig = {}) {
    super();
    this.config = {
      timeout: 30000,
      debug: false,
      ...config,
    };
    this.debug = this.config.debug ?? false;
  }

  // ==========================================================================
  // Initialization
  // ==========================================================================

  /**
   * Initialize the SDK
   *
   * Sets up internal state and connects to remote endpoint if configured
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      throw new PollnSDKError('SDK_NOT_INITIALIZED', 'SDK already initialized');
    }

    this.log('Initializing POLLN SDK...');

    // Connect to remote endpoint if configured
    if (this.config.endpoint) {
      await this.connectToEndpoint(this.config.endpoint);
    }

    this.initialized = true;
    this.log('POLLN SDK initialized successfully');

    this.emit('sdk:initialized', { timestamp: Date.now() });
  }

  /**
   * Shutdown the SDK
   *
   * Cleanly shuts down all colonies and connections
   */
  async shutdown(): Promise<void> {
    this.log('Shutting down POLLN SDK...');

    // Shutdown all colonies
    for (const [colonyId, colony] of this.colonies) {
      await colony.destroy();
    }

    // Clear all state
    this.colonies.clear();
    this.agents.clear();
    this.tasks.clear();
    this.eventHandlers.clear();
    this.initialized = false;

    this.log('POLLN SDK shutdown complete');
    this.emit('sdk:shutdown', { timestamp: Date.now() });
  }

  // ==========================================================================
  // Colony Management
  // ==========================================================================

  /**
   * Create a new colony
   *
   * @param config - Colony configuration
   * @returns Colony handle with state and methods
   *
   * @example
   * ```typescript
   * const colony = await sdk.createColony({
   *   name: 'my-colony',
   *   maxAgents: 100,
   *   resourceBudget: { totalCompute: 1000, totalMemory: 2048 }
   * });
   * ```
   */
  async createColony(config: ColonyConfig): Promise<ColonyHandle> {
    this.ensureInitialized();

    const colonyId = config.id || uuidv4();

    if (this.colonies.has(colonyId)) {
      throw new PollnSDKError(
        'COLONY_ALREADY_EXISTS',
        `Colony with id ${colonyId} already exists`
      );
    }

    this.log(`Creating colony: ${colonyId}`);

    // Import Colony dynamically to avoid circular dependencies
    const { Colony } = await import('../core/colony.js');

    // Create core Colony instance
    const coreColony = new Colony({
      id: colonyId,
      gardenerId: 'sdk-user', // Could be extracted from API key
      name: config.name,
      maxAgents: config.maxAgents || this.config.defaults?.maxAgents || 100,
      resourceBudget: {
        totalCompute: config.resourceBudget?.totalCompute || this.config.defaults?.resourceBudget?.totalCompute || 1000,
        totalMemory: config.resourceBudget?.totalMemory || this.config.defaults?.resourceBudget?.totalMemory || 2048,
        totalNetwork: config.resourceBudget?.totalNetwork || this.config.defaults?.resourceBudget?.totalNetwork || 100,
      },
      distributed: config.distributed,
      distributedConfig: config.distributedConfig,
    });

    // Create SDK handle
    const handle = new ColonyHandle(this, coreColony, colonyId, config);
    this.colonies.set(colonyId, handle);
    this.agents.set(colonyId, new Map());

    this.log(`Colony created: ${colonyId}`);
    this.emitEvent('colony:created', { colonyId, config });

    return handle;
  }

  /**
   * Get a colony by ID
   *
   * @param colonyId - Colony ID
   * @returns Colony handle or null if not found
   */
  getColony(colonyId: string): ColonyHandle | null {
    return this.colonies.get(colonyId) || null;
  }

  /**
   * List all colonies
   *
   * @param query - Optional query filters
   * @returns Array of colony handles
   */
  listColonies(query?: ColonyQuery): ColonyHandle[] {
    let colonies = Array.from(this.colonies.values());

    if (query) {
      if (query.active !== undefined) {
        colonies = colonies.filter(c => {
          const agents = this.agents.get(c.id);
          return agents && agents.size > 0;
        });
      }
      if (query.minAgents !== undefined) {
        colonies = colonies.filter(c => {
          const agents = this.agents.get(c.id);
          return agents && agents.size >= query.minAgents!;
        });
      }
      if (query.maxAgents !== undefined) {
        colonies = colonies.filter(c => {
          const agents = this.agents.get(c.id);
          return agents && agents.size <= query.maxAgents!;
        });
      }
      if (query.limit) {
        colonies = colonies.slice(0, query.limit);
      }
    }

    return colonies;
  }

  /**
   * Destroy a colony
   *
   * @param colonyId - Colony ID
   */
  async destroyColony(colonyId: string): Promise<void> {
    this.ensureInitialized();

    const colony = this.colonies.get(colonyId);
    if (!colony) {
      throw new PollnSDKError('COLONY_NOT_FOUND', `Colony ${colonyId} not found`);
    }

    this.log(`Destroying colony: ${colonyId}`);

    await colony.destroy();

    this.colonies.delete(colonyId);
    this.agents.delete(colonyId);

    this.log(`Colony destroyed: ${colonyId}`);
    this.emitEvent('colony:destroyed', { colonyId });
  }

  // ==========================================================================
  // Agent Management
  // ==========================================================================

  /**
   * Add an agent to a colony
   *
   * @param colonyId - Colony ID
   * @param config - Agent configuration
   * @returns Agent handle
   *
   * @example
   * ```typescript
   * const agent = await sdk.addAgent(colony.id, {
   *   category: 'ephemeral',
   *   goal: 'process-data',
   *   inputTopics: ['data'],
   *   outputTopic: 'results'
   * });
   * ```
   */
  async addAgent(colonyId: string, config: AgentConfig): Promise<AgentHandle> {
    this.ensureInitialized();

    const colony = this.colonies.get(colonyId);
    if (!colony) {
      throw new PollnSDKError('COLONY_NOT_FOUND', `Colony ${colonyId} not found`);
    }

    const agentId = config.id || `agent_${this.agentInstanceCounter++}`;

    this.log(`Adding agent: ${agentId} to colony: ${colonyId}`);

    // Import agent classes dynamically
    const { TaskAgent, RoleAgent, CoreAgent } = await import('../core/agents.js');
    const { TileCategory } = await import('../core/agents.js');

    // Create agent config for core
    const coreAgentConfig = {
      id: agentId,
      typeId: config.typeId || config.category,
      categoryId: config.category.toUpperCase(),
      modelFamily: config.modelFamily || 'default',
      defaultParams: config.defaultParams || {},
      inputTopics: config.inputTopics || [],
      outputTopic: config.outputTopic || 'default',
      targetLatencyMs: config.targetLatencyMs,
      maxMemoryMB: config.maxMemoryMB,
      minExamples: config.minExamples || 10,
      requiresWorldModel: config.requiresWorldModel || false,
    };

    // Create appropriate agent instance based on category
    let agentInstance;
    switch (config.category) {
      case 'ephemeral':
        agentInstance = new TaskAgent(coreAgentConfig, config.maxLifetimeMs);
        break;
      case 'role':
        agentInstance = new RoleAgent(coreAgentConfig);
        break;
      case 'core':
        agentInstance = new CoreAgent(coreAgentConfig);
        break;
      default:
        throw new PollnSDKError(
          'AGENT_CREATION_FAILED',
          `Unknown agent category: ${config.category}`
        );
    }

    await agentInstance.initialize();

    // Register with colony
    colony.getCoreColony().registerAgent(coreAgentConfig);

    // Create SDK handle
    const handle = new AgentHandle(this, colonyId, agentId, agentInstance, config);
    const agents = this.agents.get(colonyId)!;
    agents.set(agentId, handle);

    this.log(`Agent added: ${agentId}`);
    this.emitEvent('colony:agent:added', { colonyId, agentId, config });

    return handle;
  }

  /**
   * Get an agent by ID
   *
   * @param colonyId - Colony ID
   * @param agentId - Agent ID
   * @returns Agent handle or null if not found
   */
  getAgent(colonyId: string, agentId: string): AgentHandle | null {
    const agents = this.agents.get(colonyId);
    return agents?.get(agentId) || null;
  }

  /**
   * List agents in a colony
   *
   * @param colonyId - Colony ID
   * @param query - Optional query filters
   * @returns Array of agent handles
   */
  listAgents(colonyId: string, query?: AgentQuery): AgentHandle[] {
    const agents = this.agents.get(colonyId);
    if (!agents) {
      return [];
    }

    let result = Array.from(agents.values());

    if (query) {
      if (query.category) {
        result = result.filter(a => a.getCategory() === query.category);
      }
      if (query.status) {
        result = result.filter(a => a.getState().status === query.status);
      }
      if (query.minSuccessRate !== undefined) {
        result = result.filter(a => a.getState().successRate >= query.minSuccessRate!);
      }
      if (query.maxLatencyMs !== undefined) {
        result = result.filter(a => a.getState().avgLatencyMs <= query.maxLatencyMs!);
      }
      if (query.limit) {
        result = result.slice(0, query.limit);
      }
    }

    return result;
  }

  /**
   * Remove an agent from a colony
   *
   * @param colonyId - Colony ID
   * @param agentId - Agent ID
   */
  async removeAgent(colonyId: string, agentId: string): Promise<void> {
    this.ensureInitialized();

    const colony = this.colonies.get(colonyId);
    if (!colony) {
      throw new PollnSDKError('COLONY_NOT_FOUND', `Colony ${colonyId} not found`);
    }

    const agents = this.agents.get(colonyId);
    const agent = agents?.get(agentId);

    if (!agent) {
      throw new PollnSDKError('AGENT_NOT_FOUND', `Agent ${agentId} not found`);
    }

    this.log(`Removing agent: ${agentId} from colony: ${colonyId}`);

    await agent.shutdown();

    agents!.delete(agentId);

    this.log(`Agent removed: ${agentId}`);
    this.emitEvent('colony:agent:removed', { colonyId, agentId });
  }

  // ==========================================================================
  // Task Execution
  // ==========================================================================

  /**
   * Run a task synchronously
   *
   * @param task - Task input
   * @returns Task result
   *
   * @example
   * ```typescript
   * const result = await sdk.runTask({
   *   colonyId: colony.id,
   *   agentId: agent.id,
   *   input: { data: 'value' }
   * });
   * ```
   */
  async runTask<T = unknown, R = unknown>(task: TaskInput<T> & { colonyId: string }): Promise<TaskResult<R>> {
    this.ensureInitialized();

    const taskId = task.id || `task_${this.taskCounter++}`;

    this.log(`Running task: ${taskId}`);

    const colony = this.colonies.get(task.colonyId);
    if (!colony) {
      throw new PollnSDKError('COLONY_NOT_FOUND', `Colony ${task.colonyId} not found`);
    }

    let agent: AgentHandle | null = null;

    // Use specific agent if provided
    if (task.agentId) {
      agent = this.getAgent(task.colonyId, task.agentId);
      if (!agent) {
        throw new PollnSDKError('AGENT_NOT_FOUND', `Agent ${task.agentId} not found`);
      }
    } else {
      // Auto-select agent based on type (could use Plinko here)
      const agents = this.listAgents(task.colonyId);
      if (agents.length === 0) {
        throw new PollnSDKError('AGENT_NOT_FOUND', 'No agents available in colony');
      }
      agent = agents[0]; // Simple selection for now
    }

    this.emitEvent('agent:task:started', {
      colonyId: task.colonyId,
      agentId: agent!.getId(),
      taskId,
    });

    const startTime = Date.now();

    try {
      // Execute task
      const result = await agent!.process(task.input);

      const executionTime = Date.now() - startTime;

      const taskResult: TaskResult<R> = {
        id: taskId,
        agentId: agent!.getId(),
        success: true,
        output: result.payload as R,
        executionTimeMs: executionTime,
        metadata: task.metadata,
        timestamp: Date.now(),
      };

      this.log(`Task completed: ${taskId} in ${executionTime}ms`);
      this.emitEvent('agent:task:completed', {
        colonyId: task.colonyId,
        agentId: agent!.getId(),
        taskId,
        result: taskResult,
      });

      return taskResult;
    } catch (error) {
      const executionTime = Date.now() - startTime;

      const taskResult: TaskResult<R> = {
        id: taskId,
        agentId: agent!.getId(),
        success: false,
        output: undefined as R,
        executionTimeMs: executionTime,
        error: error instanceof Error ? error.message : String(error),
        metadata: task.metadata,
        timestamp: Date.now(),
      };

      this.log(`Task failed: ${taskId} - ${taskResult.error}`);
      this.emitEvent('agent:task:failed', {
        colonyId: task.colonyId,
        agentId: agent!.getId(),
        taskId,
        error: taskResult.error,
      });

      return taskResult;
    }
  }

  /**
   * Stream a task result
   *
   * @param task - Task input
   * @param options - Stream options
   * @returns AsyncGenerator of stream chunks
   *
   * @example
   * ```typescript
   * for await (const chunk of sdk.streamTask({
   *   colonyId: colony.id,
   *   agentId: agent.id,
   *   input: largeData
   * })) {
   *   console.log('Received chunk:', chunk.chunk);
   * }
   * ```
   */
  async *streamTask<T = unknown, R = unknown>(
    task: TaskInput<T> & { colonyId: string },
    options: StreamOptions = {}
  ): AsyncGenerator<TaskStreamChunk<R>> {
    this.ensureInitialized();

    const taskId = task.id || `task_${this.taskCounter++}`;

    this.log(`Streaming task: ${taskId}`);

    const colony = this.colonies.get(task.colonyId);
    if (!colony) {
      throw new PollnSDKError('COLONY_NOT_FOUND', `Colony ${task.colonyId} not found`);
    }

    let agent: AgentHandle | null = null;

    if (task.agentId) {
      agent = this.getAgent(task.colonyId, task.agentId);
      if (!agent) {
        throw new PollnSDKError('AGENT_NOT_FOUND', `Agent ${task.agentId} not found`);
      }
    } else {
      const agents = this.listAgents(task.colonyId);
      if (agents.length === 0) {
        throw new PollnSDKError('AGENT_NOT_FOUND', 'No agents available in colony');
      }
      agent = agents[0];
    }

    const startTime = Date.now();
    let chunkCount = 0;

    try {
      // Simulate streaming by processing the task
      // In a real implementation, the agent would support streaming natively
      const result = await agent!.process(task.input);
      const executionTime = Date.now() - startTime;

      // For streaming, we'll send the result as chunks
      // If it's a simple result, we'll wrap it
      const payload = result.payload;
      const chunkSize = options.chunkSize || 1024;

      // Handle different payload types
      if (typeof payload === 'string') {
        // Stream string as character chunks
        for (let i = 0; i < payload.length; i += chunkSize) {
          chunkCount++;
          const chunk = payload.slice(i, i + chunkSize);

          const streamChunk: TaskStreamChunk<R> = {
            taskId,
            agentId: agent!.getId(),
            chunk: chunk as R,
            done: i + chunkSize >= payload.length,
            executionTimeMs: Date.now() - startTime,
            timestamp: Date.now(),
          };

          yield streamChunk;

          if (options.chunkDelay && !streamChunk.done) {
            await new Promise(resolve => setTimeout(resolve, options.chunkDelay));
          }
        }
      } else if (payload != null && typeof payload === 'object') {
        // Stream object as single chunk (in real implementation, would split differently)
        chunkCount++;
        const streamChunk: TaskStreamChunk<R> = {
          taskId,
          agentId: agent!.getId(),
          chunk: payload as R,
          done: true,
          executionTimeMs: Date.now() - startTime,
          timestamp: Date.now(),
        };

        yield streamChunk;

        if (options.chunkDelay) {
          await new Promise(resolve => setTimeout(resolve, options.chunkDelay));
        }
      } else {
        // Stream primitive values
        chunkCount++;
        const streamChunk: TaskStreamChunk<R> = {
          taskId,
          agentId: agent!.getId(),
          chunk: payload as R,
          done: true,
          executionTimeMs: Date.now() - startTime,
          timestamp: Date.now(),
        };

        yield streamChunk;

        if (options.chunkDelay) {
          await new Promise(resolve => setTimeout(resolve, options.chunkDelay));
        }
      }

      this.log(`Stream completed: ${taskId} (${chunkCount} chunks in ${executionTime}ms)`);
    } catch (error) {
      this.log(`Stream failed: ${taskId} - ${error}`);
      throw new PollnSDKError(
        'TASK_EXECUTION_FAILED',
        `Task execution failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  // ==========================================================================
  // Event Handling
  // ==========================================================================

  /**
   * Subscribe to events
   *
   * @param eventType - Type of event to listen for
   * @param handler - Event handler function
   *
   * @example
   * ```typescript
   * sdk.on('agent:task:completed', (event) => {
   *   console.log('Task completed:', event.data);
   * });
   * ```
   */
  override on<T = unknown>(eventType: EventType, handler: EventHandler<T>): this {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set());
    }
    this.eventHandlers.get(eventType)!.add(handler as EventHandler);
    return this;
  }

  /**
   * Unsubscribe from events
   *
   * @param eventType - Type of event
   * @param handler - Event handler to remove
   */
  override off<T = unknown>(eventType: EventType, handler: EventHandler<T>): this {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler as EventHandler);
    }
    return this;
  }

  /**
   * Emit an event to all subscribers
   */
  private emitEvent<T = unknown>(eventType: EventType, data: T): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const event: Event<T> = {
        type: eventType,
        data,
        timestamp: Date.now(),
      };

      for (const handler of handlers) {
        try {
          handler(event);
        } catch (error) {
          this.log(`Error in event handler for ${eventType}:`, error);
        }
      }
    }
  }

  // ==========================================================================
  // State Queries
  // ==========================================================================

  /**
   * Get SDK state
   */
  getState(): {
    initialized: boolean;
    colonies: number;
    agents: number;
    tasks: number;
  } {
    let totalAgents = 0;
    for (const agents of this.agents.values()) {
      totalAgents += agents.size;
    }

    return {
      initialized: this.initialized,
      colonies: this.colonies.size,
      agents: totalAgents,
      tasks: this.tasks.size,
    };
  }

  // ==========================================================================
  // Private Helpers
  // ==========================================================================

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new PollnSDKError('SDK_NOT_INITIALIZED', 'SDK not initialized. Call initialize() first');
    }
  }

  private async connectToEndpoint(endpoint: string): Promise<void> {
    this.log(`Connecting to endpoint: ${endpoint}`);

    // TODO: Implement WebSocket connection to remote endpoint
    // This would connect to the POLLN WebSocket API

    this.log(`Connected to endpoint: ${endpoint}`);
  }

  private log(...args: unknown[]): void {
    if (this.debug) {
      console.log('[PollnSDK]', ...args);
    }
  }
}

// ============================================================================
// ColonyHandle - Colony Management Helper
// ============================================================================

/**
 * Helper class for managing a colony
 *
 * Provides convenient methods for interacting with a specific colony
 */
export class ColonyHandle {
  constructor(
    private sdk: PollnSDK,
    private coreColony: any, // Colony from core
    public readonly id: string,
    public readonly config: ColonyConfig
  ) {}

  /**
   * Get colony state
   */
  getState(): ColonyState {
    const stats = this.coreColony.getStats() || {
      totalAgents: 0,
      activeAgents: 0,
      shannonDiversity: 0,
    };
    return {
      id: this.id,
      name: this.config.name,
      gardenerId: this.coreColony.config?.gardenerId || 'sdk-user',
      totalAgents: stats.totalAgents || 0,
      activeAgents: stats.activeAgents || 0,
      dormantAgents: (stats.totalAgents || 0) - (stats.activeAgents || 0),
      shannonDiversity: stats.shannonDiversity || 0,
      createdAt: Date.now(), // Would be tracked by core
      lastActive: Date.now(),
    };
  }

  /**
   * Get the core Colony instance
   */
  getCoreColony(): any {
    return this.coreColony;
  }

  /**
   * Add an agent to this colony
   */
  async addAgent(config: AgentConfig): Promise<AgentHandle> {
    return this.sdk.addAgent(this.id, config);
  }

  /**
   * List agents in this colony
   */
  listAgents(query?: AgentQuery): AgentHandle[] {
    return this.sdk.listAgents(this.id, query);
  }

  /**
   * Get an agent in this colony
   */
  getAgent(agentId: string): AgentHandle | null {
    return this.sdk.getAgent(this.id, agentId);
  }

  /**
   * Remove an agent from this colony
   */
  async removeAgent(agentId: string): Promise<void> {
    return this.sdk.removeAgent(this.id, agentId);
  }

  /**
   * Run a task in this colony
   */
  async runTask<T = unknown, R = unknown>(task: Omit<TaskInput<T>, 'colonyId'>): Promise<TaskResult<R>> {
    return this.sdk.runTask<T, R>({ ...task, colonyId: this.id });
  }

  /**
   * Stream a task in this colony
   */
  async *streamTask<T = unknown, R = unknown>(
    task: Omit<TaskInput<T>, 'colonyId'>,
    options?: StreamOptions
  ): AsyncGenerator<TaskStreamChunk<R>> {
    yield* this.sdk.streamTask<T, R>({ ...task, colonyId: this.id }, options);
  }

  /**
   * Destroy this colony
   */
  async destroy(): Promise<void> {
    // Shutdown all agents
    const agents = this.listAgents();
    for (const agent of agents) {
      await agent.shutdown();
    }

    // Shutdown core colony
    if (this.coreColony.removeAllListeners) {
      this.coreColony.removeAllListeners();
    }
  }
}

// ============================================================================
// AgentHandle - Agent Management Helper
// ============================================================================

/**
 * Helper class for managing an agent
 *
 * Provides convenient methods for interacting with a specific agent
 */
export class AgentHandle {
  constructor(
    private sdk: PollnSDK,
    public readonly colonyId: string,
    public readonly id: string,
    private agentInstance: any, // TaskAgent, RoleAgent, or CoreAgent
    public readonly config: AgentConfig
  ) {}

  /**
   * Get agent state
   */
  getState(): AgentState {
    return {
      id: this.id,
      category: this.config.category,
      typeId: this.config.typeId || this.config.category,
      name: this.config.name,
      goal: this.config.goal,
      status: 'active', // Would be tracked by core
      valueFunction: this.agentInstance.valueFunction || 0.5,
      successCount: this.agentInstance.successCount || 0,
      failureCount: this.agentInstance.failureCount || 0,
      avgLatencyMs: 0, // Would be tracked by core
      successRate: this.calculateSuccessRate(),
      executionCount: (this.agentInstance.successCount || 0) + (this.agentInstance.failureCount || 0),
      lastActive: Date.now(),
      createdAt: Date.now(),
    };
  }

  /**
   * Get agent category
   */
  getCategory(): string {
    return this.config.category;
  }

  /**
   * Get agent ID
   */
  getId(): string {
    return this.id;
  }

  /**
   * Process input with this agent
   */
  async process<T = unknown, R = unknown>(input: T): Promise<{ payload: R }> {
    // @ts-ignore - process method exists on agent instances
    return this.agentInstance.process(input);
  }

  /**
   * Shutdown this agent
   */
  async shutdown(): Promise<void> {
    await this.agentInstance.shutdown();
  }

  /**
   * Check if agent should be terminated
   */
  shouldTerminate(): boolean {
    return this.agentInstance.shouldTerminate?.() || false;
  }

  /**
   * Extract knowledge from this agent
   */
  extractKnowledge(): unknown {
    return this.agentInstance.extractKnowledge?.() || null;
  }

  private calculateSuccessRate(): number {
    const success = this.agentInstance.successCount || 0;
    const failure = this.agentInstance.failureCount || 0;
    const total = success + failure;
    return total > 0 ? success / total : 0;
  }
}

// ============================================================================
// TaskHandle - Task Management Helper
// ============================================================================

class TaskHandle {
  constructor(
    public readonly id: string,
    public readonly colonyId: string,
    public readonly agentId: string,
    public readonly input: unknown,
    public readonly createdAt: number
  ) {}
}

// ============================================================================
// Default Export
// ============================================================================

export default PollnSDK;
