# POLLN SDK - API Reference

Complete API documentation for the POLLN SDK.

## Table of Contents

- [PollnSDK](#pollnsdk)
- [ColonyHandle](#colonyhandle)
- [AgentHandle](#agenthandle)
- [Types](#types)
- [Events](#events)
- [Errors](#errors)

## PollnSDK

The main SDK class for managing POLLN colonies.

### Constructor

```typescript
constructor(config?: PollnSDKConfig)
```

Creates a new SDK instance.

**Parameters:**
- `config` (optional): SDK configuration

**Example:**
```typescript
const sdk = new PollnSDK({
  apiKey: 'your-api-key',
  endpoint: 'wss://api.polln.ai',
  timeout: 30000,
  debug: true
});
```

### Methods

#### initialize()

```typescript
async initialize(): Promise<void>
```

Initialize the SDK. Must be called before any other operations.

**Throws:**
- `PollnSDKError` with code `SDK_NOT_INITIALIZED` if already initialized

**Example:**
```typescript
await sdk.initialize();
```

#### shutdown()

```typescript
async shutdown(): Promise<void>
```

Shutdown the SDK and cleanup all resources.

**Example:**
```typescript
await sdk.shutdown();
```

#### createColony()

```typescript
async createColony(config: ColonyConfig): Promise<ColonyHandle>
```

Create a new colony.

**Parameters:**
- `config`: Colony configuration

**Returns:** Colony handle

**Throws:**
- `PollnSDKError` with code `COLONY_ALREADY_EXISTS` if colony ID exists

**Example:**
```typescript
const colony = await sdk.createColony({
  id: 'my-colony',
  name: 'My Colony',
  maxAgents: 100,
  resourceBudget: {
    totalCompute: 1000,
    totalMemory: 2048
  }
});
```

#### getColony()

```typescript
getColony(colonyId: string): ColonyHandle | null
```

Get a colony by ID.

**Parameters:**
- `colonyId`: Colony ID

**Returns:** Colony handle or null if not found

**Example:**
```typescript
const colony = sdk.getColony('colony-123');
if (colony) {
  console.log('Found colony:', colony.name);
}
```

#### listColonies()

```typescript
listColonies(query?: ColonyQuery): ColonyHandle[]
```

List all colonies with optional filtering.

**Parameters:**
- `query` (optional): Filter criteria

**Returns:** Array of colony handles

**Example:**
```typescript
// All colonies
const all = sdk.listColonies();

// Active colonies
const active = sdk.listColonies({ active: true });

// Colonies with at least 10 agents
const large = sdk.listColonies({ minAgents: 10 });

// First 5 colonies
const limited = sdk.listColonies({ limit: 5 });
```

#### destroyColony()

```typescript
async destroyColony(colonyId: string): Promise<void>
```

Destroy a colony and cleanup resources.

**Parameters:**
- `colonyId`: Colony ID

**Throws:**
- `PollnSDKError` with code `COLONY_NOT_FOUND` if colony doesn't exist

**Example:**
```typescript
await sdk.destroyColony('colony-123');
```

#### addAgent()

```typescript
async addAgent(colonyId: string, config: AgentConfig): Promise<AgentHandle>
```

Add an agent to a colony.

**Parameters:**
- `colonyId`: Colony ID
- `config`: Agent configuration

**Returns:** Agent handle

**Throws:**
- `PollnSDKError` with code `COLONY_NOT_FOUND` if colony doesn't exist
- `PollnSDKError` with code `AGENT_CREATION_FAILED` if agent creation fails

**Example:**
```typescript
const agent = await sdk.addAgent('colony-123', {
  category: 'ephemeral',
  goal: 'process-data',
  inputTopics: ['data'],
  outputTopic: 'results'
});
```

#### getAgent()

```typescript
getAgent(colonyId: string, agentId: string): AgentHandle | null
```

Get an agent by ID.

**Parameters:**
- `colonyId`: Colony ID
- `agentId`: Agent ID

**Returns:** Agent handle or null if not found

**Example:**
```typescript
const agent = sdk.getAgent('colony-123', 'agent-456');
```

#### listAgents()

```typescript
listAgents(colonyId: string, query?: AgentQuery): AgentHandle[]
```

List agents in a colony with optional filtering.

**Parameters:**
- `colonyId`: Colony ID
- `query` (optional): Filter criteria

**Returns:** Array of agent handles

**Example:**
```typescript
// All agents
const all = sdk.listAgents('colony-123');

// Ephemeral agents only
const ephemeral = sdk.listAgents('colony-123', { category: 'ephemeral' });

// Successful agents
const successful = sdk.listAgents('colony-123', { minSuccessRate: 0.8 });

// Fast agents
const fast = sdk.listAgents('colony-123', { maxLatencyMs: 100 });
```

#### removeAgent()

```typescript
async removeAgent(colonyId: string, agentId: string): Promise<void>
```

Remove an agent from a colony.

**Parameters:**
- `colonyId`: Colony ID
- `agentId`: Agent ID

**Throws:**
- `PollnSDKError` with code `COLONY_NOT_FOUND` if colony doesn't exist
- `PollnSDKError` with code `AGENT_NOT_FOUND` if agent doesn't exist

**Example:**
```typescript
await sdk.removeAgent('colony-123', 'agent-456');
```

#### runTask()

```typescript
async runTask<T = unknown, R = unknown>(
  task: TaskInput<T> & { colonyId: string }
): Promise<TaskResult<R>>
```

Run a task synchronously.

**Parameters:**
- `task`: Task input with colony ID

**Returns:** Task result

**Throws:**
- `PollnSDKError` with code `COLONY_NOT_FOUND` if colony doesn't exist
- `PollnSDKError` with code `AGENT_NOT_FOUND` if specified agent doesn't exist
- `PollnSDKError` with code `TASK_EXECUTION_FAILED` if task execution fails

**Example:**
```typescript
const result = await sdk.runTask({
  colonyId: 'colony-123',
  agentId: 'agent-456',
  input: { text: 'Hello world' },
  priority: 0.8,
  timeout: 5000
});

if (result.success) {
  console.log('Output:', result.output);
} else {
  console.error('Error:', result.error);
}
```

#### streamTask()

```typescript
async *streamTask<T = unknown, R = unknown>(
  task: TaskInput<T> & { colonyId: string },
  options?: StreamOptions
): AsyncGenerator<TaskStreamChunk<R>>
```

Stream a task result.

**Parameters:**
- `task`: Task input with colony ID
- `options` (optional): Stream options

**Yields:** Task stream chunks

**Example:**
```typescript
for await (const chunk of sdk.streamTask({
  colonyId: 'colony-123',
  input: largeData
}, { chunkSize: 1024, chunkDelay: 100 })) {
  console.log('Chunk:', chunk.chunk);
  if (chunk.done) break;
}
```

#### on()

```typescript
on<T = unknown>(eventType: EventType, handler: EventHandler<T>): this
```

Subscribe to events.

**Parameters:**
- `eventType`: Type of event to listen for
- `handler`: Event handler function

**Returns:** SDK instance (for chaining)

**Example:**
```typescript
sdk.on('agent:task:completed', (event) => {
  console.log('Task completed:', event.data);
});
```

#### off()

```typescript
off<T = unknown>(eventType: EventType, handler: EventHandler<T>): this
```

Unsubscribe from events.

**Parameters:**
- `eventType`: Type of event
- `handler`: Event handler to remove

**Returns:** SDK instance (for chaining)

**Example:**
```typescript
const handler = (event) => console.log(event.data);
sdk.on('agent:task:completed', handler);
sdk.off('agent:task:completed', handler);
```

#### getState()

```typescript
getState(): {
  initialized: boolean;
  colonies: number;
  agents: number;
  tasks: number;
}
```

Get SDK state.

**Returns:** SDK state object

**Example:**
```typescript
const state = sdk.getState();
console.log('Colonies:', state.colonies);
console.log('Agents:', state.agents);
```

## ColonyHandle

Helper class for managing a colony.

### Properties

```typescript
id: string              // Colony ID
config: ColonyConfig    // Colony configuration
```

### Methods

#### getState()

```typescript
getState(): ColonyState
```

Get colony state.

**Returns:** Colony state object

**Example:**
```typescript
const state = colony.getState();
console.log('Total agents:', state.totalAgents);
console.log('Active agents:', state.activeAgents);
console.log('Diversity:', state.shannonDiversity);
```

#### getCoreColony()

```typescript
getCoreColony(): any
```

Get the core Colony instance.

**Returns:** Core Colony object

#### addAgent()

```typescript
async addAgent(config: AgentConfig): Promise<AgentHandle>
```

Add an agent to this colony.

**Parameters:**
- `config`: Agent configuration

**Returns:** Agent handle

**Example:**
```typescript
const agent = await colony.addAgent({
  category: 'role',
  goal: 'process-data'
});
```

#### listAgents()

```typescript
listAgents(query?: AgentQuery): AgentHandle[]
```

List agents in this colony.

**Parameters:**
- `query` (optional): Filter criteria

**Returns:** Array of agent handles

**Example:**
```typescript
const agents = colony.listAgents({ category: 'ephemeral' });
```

#### getAgent()

```typescript
getAgent(agentId: string): AgentHandle | null
```

Get an agent in this colony.

**Parameters:**
- `agentId`: Agent ID

**Returns:** Agent handle or null

**Example:**
```typescript
const agent = colony.getAgent('agent-456');
```

#### removeAgent()

```typescript
async removeAgent(agentId: string): Promise<void>
```

Remove an agent from this colony.

**Parameters:**
- `agentId`: Agent ID

**Example:**
```typescript
await colony.removeAgent('agent-456');
```

#### runTask()

```typescript
async runTask<T = unknown, R = unknown>(
  task: Omit<TaskInput<T>, 'colonyId'>
): Promise<TaskResult<R>>
```

Run a task in this colony.

**Parameters:**
- `task`: Task input (colony ID automatically added)

**Returns:** Task result

**Example:**
```typescript
const result = await colony.runTask({
  input: { text: 'Hello' }
});
```

#### streamTask()

```typescript
async *streamTask<T = unknown, R = unknown>(
  task: Omit<TaskInput<T>, 'colonyId'>,
  options?: StreamOptions
): AsyncGenerator<TaskStreamChunk<R>>
```

Stream a task in this colony.

**Parameters:**
- `task`: Task input (colony ID automatically added)
- `options` (optional): Stream options

**Yields:** Task stream chunks

**Example:**
```typescript
for await (const chunk of colony.streamTask({ input: data })) {
  console.log(chunk.chunk);
  if (chunk.done) break;
}
```

#### destroy()

```typescript
async destroy(): Promise<void>
```

Destroy this colony and cleanup resources.

**Example:**
```typescript
await colony.destroy();
```

## AgentHandle

Helper class for managing an agent.

### Properties

```typescript
id: string              // Agent ID
colonyId: string        // Colony ID
config: AgentConfig     // Agent configuration
```

### Methods

#### getState()

```typescript
getState(): AgentState
```

Get agent state.

**Returns:** Agent state object

**Example:**
```typescript
const state = agent.getState();
console.log('Status:', state.status);
console.log('Success rate:', state.successRate);
console.log('Executions:', state.executionCount);
```

#### getCategory()

```typescript
getCategory(): string
```

Get agent category.

**Returns:** Agent category ('ephemeral', 'role', or 'core')

**Example:**
```typescript
const category = agent.getCategory();
console.log('Category:', category);
```

#### getId()

```typescript
getId(): string
```

Get agent ID.

**Returns:** Agent ID

**Example:**
```typescript
const id = agent.getId();
```

#### process()

```typescript
async process<T = unknown, R = unknown>(input: T): Promise<{ payload: R }>
```

Process input with this agent.

**Parameters:**
- `input`: Input data

**Returns:** Processed output

**Example:**
```typescript
const result = await agent.process({ text: 'Hello' });
console.log('Output:', result.payload);
```

#### shutdown()

```typescript
async shutdown(): Promise<void>
```

Shutdown this agent.

**Example:**
```typescript
await agent.shutdown();
```

#### shouldTerminate()

```typescript
shouldTerminate(): boolean
```

Check if agent should be terminated.

**Returns:** True if agent should terminate

**Example:**
```typescript
if (agent.shouldTerminate()) {
  await agent.shutdown();
}
```

#### extractKnowledge()

```typescript
extractKnowledge(): unknown
```

Extract knowledge from this agent.

**Returns:** Agent's learned knowledge

**Example:**
```typescript
const knowledge = agent.extractKnowledge();
```

## Types

### PollnSDKConfig

SDK configuration options.

```typescript
interface PollnSDKConfig {
  apiKey?: string;
  endpoint?: string;
  timeout?: number;
  debug?: boolean;
  defaults?: {
    maxAgents?: number;
    resourceBudget?: ResourceBudgetConfig;
  };
}
```

### ColonyConfig

Colony configuration options.

```typescript
interface ColonyConfig {
  id?: string;
  name: string;
  maxAgents?: number;
  resourceBudget?: ResourceBudgetConfig;
  distributed?: boolean;
  distributedConfig?: {
    backend: 'memory' | 'redis' | 'nats';
    connectionString?: string;
    nodeId?: string;
  };
}
```

### ColonyState

Colony state information.

```typescript
interface ColonyState {
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
```

### AgentConfig

Agent configuration options.

```typescript
interface AgentConfig {
  id?: string;
  category: AgentCategory;
  typeId?: string;
  name?: string;
  goal?: string;
  modelFamily?: string;
  defaultParams?: Record<string, unknown>;
  inputTopics?: string[];
  outputTopic?: string;
  targetLatencyMs?: number;
  maxMemoryMB?: number;
  minExamples?: number;
  requiresWorldModel?: boolean;
  maxLifetimeMs?: number;
}
```

### AgentCategory

Agent category type.

```typescript
type AgentCategory = 'ephemeral' | 'role' | 'core';
```

### AgentState

Agent state information.

```typescript
interface AgentState {
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
```

### TaskInput

Task input data.

```typescript
interface TaskInput<T = unknown> {
  id?: string;
  agentId?: string;
  type?: string;
  input: T;
  priority?: number;
  timeout?: number;
  metadata?: Record<string, unknown>;
}
```

### TaskResult

Task execution result.

```typescript
interface TaskResult<T = unknown> {
  id: string;
  agentId: string;
  success: boolean;
  output: T;
  executionTimeMs: number;
  error?: string;
  metadata?: Record<string, unknown>;
  timestamp: number;
}
```

### TaskStreamChunk

Task streaming chunk.

```typescript
interface TaskStreamChunk<T = unknown> {
  taskId: string;
  agentId: string;
  chunk: T;
  done: boolean;
  executionTimeMs: number;
  timestamp: number;
}
```

### StreamOptions

Streaming options.

```typescript
interface StreamOptions {
  chunkSize?: number;
  chunkDelay?: number;
  includeMetadata?: boolean;
}
```

### AgentQuery

Agent query filters.

```typescript
interface AgentQuery {
  category?: AgentCategory;
  status?: AgentState['status'];
  minSuccessRate?: number;
  maxLatencyMs?: number;
  limit?: number;
}
```

### ColonyQuery

Colony query filters.

```typescript
interface ColonyQuery {
  active?: boolean;
  minAgents?: number;
  maxAgents?: number;
  limit?: number;
}
```

## Events

### Event Types

```typescript
type EventType =
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
```

### Event Object

```typescript
interface Event<T = unknown> {
  type: EventType;
  data: T;
  timestamp: number;
  colonyId?: string;
  agentId?: string;
  taskId?: string;
}
```

### Event Handler

```typescript
type EventHandler<T = unknown> = (event: Event<T>) => void | Promise<void>;
```

### Event Examples

#### colony:created

```typescript
sdk.on('colony:created', (event) => {
  console.log('Colony created:', event.data.colonyId);
});
```

#### agent:task:completed

```typescript
sdk.on('agent:task:completed', (event) => {
  console.log('Task completed:', event.data.taskId);
  console.log('Result:', event.data.result);
});
```

#### error

```typescript
sdk.on('error', (event) => {
  console.error('Error:', event.data);
});
```

## Errors

### PollnSDKError

Base error class for SDK errors.

```typescript
class PollnSDKError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'PollnSDKError';
  }
}
```

### Error Codes

```typescript
type ErrorCode =
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
```

### Error Handling Example

```typescript
try {
  const result = await colony.runTask({ input });
} catch (error) {
  if (error instanceof PollnSDKError) {
    switch (error.code) {
      case 'TASK_EXECUTION_FAILED':
        console.error('Task failed:', error.message);
        break;
      case 'TASK_TIMEOUT':
        console.error('Task timed out');
        break;
      default:
        console.error('Unknown error:', error);
    }
  }
}
```

## Type Guards

### isPollnSDKError

```typescript
function isPollnSDKError(error: unknown): error is PollnSDKError {
  return error instanceof PollnSDKError;
}
```

### isAgentHandle

```typescript
function isAgentHandle(value: unknown): value is AgentHandle {
  return value instanceof AgentHandle;
}
```

### isColonyHandle

```typescript
function isColonyHandle(value: unknown): value is ColonyHandle {
  return value instanceof ColonyHandle;
}
```

## Utility Functions

### createSDK

Factory function to create SDK instance.

```typescript
import { createSDK } from 'polln/sdk';

const sdk = createSDK({ debug: true });
```

### Default Export

```typescript
import PollnSDK from 'polln/sdk';

const sdk = new PollnSDK();
```
