# POLLN SDK - How-To Guides

Practical guides for common tasks with the POLLN SDK.

## Table of Contents

- [Create a Colony](#create-a-colony)
- [Manage Agents](#manage-agents)
- [Execute Tasks](#execute-tasks)
- [Handle Events](#handle-events)
- [Query State](#query-state)
- [Handle Errors](#handle-errors)
- [Configure Resources](#configure-resources)
- [Use Streaming](#use-streaming)
- [Work with Multiple Colonies](#work-with-multiple-colonies)
- [Implement Retry Logic](#implement-retry-logic)
- [Monitor Performance](#monitor-performance)
- [Cleanup Resources](#cleanup-resources)

## Create a Colony

### Basic Colony

Create a simple colony with default settings:

```typescript
import { PollnSDK } from 'polln/sdk';

const sdk = new PollnSDK();
await sdk.initialize();

const colony = await sdk.createColony({
  name: 'my-colony'
});
```

### Colony with Resource Limits

Create a colony with resource constraints:

```typescript
const colony = await sdk.createColony({
  name: 'resource-limited',
  maxAgents: 50,
  resourceBudget: {
    totalCompute: 2000,
    totalMemory: 4096,
    totalNetwork: 200
  }
});
```

### Distributed Colony

Create a colony with distributed coordination:

```typescript
const colony = await sdk.createColony({
  name: 'distributed-colony',
  distributed: true,
  distributedConfig: {
    backend: 'redis',
    connectionString: 'redis://localhost:6379',
    nodeId: 'node-1'
  }
});
```

## Manage Agents

### Add an Ephemeral Agent

Create a short-lived agent for a specific task:

```typescript
const agent = await colony.addAgent({
  category: 'ephemeral',
  goal: 'process-single-task',
  maxLifetimeMs: 30000  // 30 seconds
});
```

### Add a Role Agent

Create a long-lived agent with specific responsibilities:

```typescript
const agent = await colony.addAgent({
  category: 'role',
  goal: 'monitor-data-stream',
  inputTopics: ['data-stream'],
  outputTopic: 'alerts'
});
```

### Add a Core Agent

Create an essential system agent:

```typescript
const agent = await colony.addAgent({
  category: 'core',
  goal: 'colony-health-monitor'
});
```

### List Agents by Category

```typescript
// Get all ephemeral agents
const ephemeralAgents = colony.listAgents({ category: 'ephemeral' });

// Get all role agents
const roleAgents = colony.listAgents({ category: 'role' });

// Get all core agents
const coreAgents = colony.listAgents({ category: 'core' });
```

### List Agents by Performance

```typescript
// Get successful agents (80%+ success rate)
const successfulAgents = colony.listAgents({ minSuccessRate: 0.8 });

// Get fast agents (<100ms avg latency)
const fastAgents = colony.listAgents({ maxLatencyMs: 100 });

// Get top 5 agents by success rate
const topAgents = colony.listAgents({
  minSuccessRate: 0.5,
  limit: 5
});
```

### Remove an Agent

```typescript
try {
  await colony.removeAgent('agent-id');
} catch (error) {
  if (error instanceof PollnSDKError && error.code === 'AGENT_NOT_FOUND') {
    console.error('Agent not found');
  }
}
```

## Execute Tasks

### Basic Task Execution

```typescript
const result = await colony.runTask({
  input: { text: 'Hello, POLLN!' }
});

if (result.success) {
  console.log('Output:', result.output);
} else {
  console.error('Error:', result.error);
}
```

### Task with Specific Agent

```typescript
const result = await colony.runTask({
  agentId: 'specific-agent-id',
  input: { data: 'value' }
});
```

### Task with Timeout

```typescript
const result = await colony.runTask({
  input: largeData,
  timeout: 10000  // 10 seconds
});
```

### Task with Priority

```typescript
const result = await colony.runTask({
  input: urgentData,
  priority: 0.9  // High priority (0-1)
});
```

### Task with Metadata

```typescript
const result = await colony.runTask({
  input: data,
  metadata: {
    userId: 'user-123',
    requestId: 'req-456'
  }
});
```

## Handle Events

### Subscribe to Task Events

```typescript
sdk.on('agent:task:started', (event) => {
  console.log('Task started:', event.data.taskId);
});

sdk.on('agent:task:completed', (event) => {
  console.log('Task completed:', event.data);
  console.log('Execution time:', event.data.result.executionTimeMs);
});

sdk.on('agent:task:failed', (event) => {
  console.error('Task failed:', event.data.error);
});
```

### Subscribe to Agent Lifecycle Events

```typescript
sdk.on('colony:agent:added', (event) => {
  console.log('Agent added:', event.data.agentId);
});

sdk.on('agent:activated', (event) => {
  console.log('Agent activated:', event.data.agentId);
});

sdk.on('agent:deactivated', (event) => {
  console.log('Agent deactivated:', event.data.agentId);
});
```

### Subscribe to Colony Events

```typescript
sdk.on('colony:created', (event) => {
  console.log('Colony created:', event.data.colonyId);
});

sdk.on('colony:destroyed', (event) => {
  console.log('Colony destroyed:', event.data.colonyId);
});
```

### Subscribe to Dream Events

```typescript
sdk.on('dream:started', (event) => {
  console.log('Dream cycle started');
});

sdk.on('dream:episode', (event) => {
  console.log('Dream episode:', event.data);
});

sdk.on('dream:completed', (event) => {
  console.log('Dream cycle completed');
});
```

### Subscribe to All Errors

```typescript
sdk.on('error', (event) => {
  console.error('Error:', event.data);
});
```

### Unsubscribe from Events

```typescript
const handler = (event) => console.log(event.data);

sdk.on('agent:task:completed', handler);
// ... later ...
sdk.off('agent:task:completed', handler);
```

## Query State

### Get SDK State

```typescript
const state = sdk.getState();
console.log('Initialized:', state.initialized);
console.log('Colonies:', state.colonies);
console.log('Agents:', state.agents);
```

### Get Colony State

```typescript
const state = colony.getState();
console.log('Total agents:', state.totalAgents);
console.log('Active agents:', state.activeAgents);
console.log('Dormant agents:', state.dormantAgents);
console.log('Diversity index:', state.shannonDiversity);
```

### Get Agent State

```typescript
const agent = colony.getAgent('agent-id');
if (agent) {
  const state = agent.getState();
  console.log('Status:', state.status);
  console.log('Success rate:', state.successRate);
  console.log('Execution count:', state.executionCount);
  console.log('Avg latency:', state.avgLatencyMs);
  console.log('Value function:', state.valueFunction);
}
```

### Filter Colonies

```typescript
// Get active colonies
const activeColonies = sdk.listColonies({ active: true });

// Get large colonies (10+ agents)
const largeColonies = sdk.listColonies({ minAgents: 10 });

// Get small colonies (<5 agents)
const smallColonies = sdk.listColonies({ maxAgents: 5 });

// Get first 10 colonies
const firstColonies = sdk.listColonies({ limit: 10 });
```

## Handle Errors

### Basic Error Handling

```typescript
try {
  const result = await colony.runTask({ input });
} catch (error) {
  console.error('Error:', error);
}
```

### Type-Safe Error Handling

```typescript
import { PollnSDKError } from 'polln/sdk';

try {
  const result = await colony.runTask({ input });
} catch (error) {
  if (error instanceof PollnSDKError) {
    console.error('Error code:', error.code);
    console.error('Message:', error.message);
    console.error('Details:', error.details);
  }
}
```

### Handle Specific Error Codes

```typescript
try {
  const result = await colony.runTask({ input });
} catch (error) {
  if (error instanceof PollnSDKError) {
    switch (error.code) {
      case 'COLONY_NOT_FOUND':
        console.error('Colony does not exist');
        break;
      case 'AGENT_NOT_FOUND':
        console.error('Agent does not exist');
        break;
      case 'TASK_EXECUTION_FAILED':
        console.error('Task execution failed');
        break;
      case 'TASK_TIMEOUT':
        console.error('Task timed out');
        break;
      default:
        console.error('Unknown error:', error.message);
    }
  }
}
```

### Retry on Failure

```typescript
async function runTaskWithRetry(
  colony: ColonyHandle,
  input: unknown,
  maxRetries = 3
) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await colony.runTask({ input });
      if (result.success) {
        return result;
      }
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      console.warn(`Attempt ${attempt} failed, retrying...`);
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
  throw new Error('All retries failed');
}
```

## Configure Resources

### Set Colony Resource Budget

```typescript
const colony = await sdk.createColony({
  name: 'resource-managed',
  resourceBudget: {
    totalCompute: 2000,  // Compute units
    totalMemory: 4096,   // MB
    totalNetwork: 200    // Network units
  }
});
```

### Configure Agent Resources

```typescript
const agent = await colony.addAgent({
  category: 'role',
  goal: 'process-data',
  targetLatencyMs: 100,   // Target latency
  maxMemoryMB: 512        // Max memory usage
});
```

### Set SDK Defaults

```typescript
const sdk = new PollnSDK({
  defaults: {
    maxAgents: 100,
    resourceBudget: {
      totalCompute: 1000,
      totalMemory: 2048,
      totalNetwork: 100
    }
  }
});
```

## Use Streaming

### Stream Task Results

```typescript
for await (const chunk of colony.streamTask({
  input: largeData
})) {
  console.log('Chunk:', chunk.chunk);
  console.log('Done:', chunk.done);

  if (chunk.done) break;
}
```

### Stream with Custom Chunk Size

```typescript
for await (const chunk of colony.streamTask({
  input: largeData
}, { chunkSize: 2048 })) {
  // Process 2KB chunks
  if (chunk.done) break;
}
```

### Stream with Delay

```typescript
for await (const chunk of colony.streamTask({
  input: largeData
}, { chunkDelay: 100 })) {
  // 100ms delay between chunks
  if (chunk.done) break;
}
```

### Collect All Chunks

```typescript
async function collectStream(colony: ColonyHandle, input: unknown) {
  const chunks = [];

  for await (const chunk of colony.streamTask({ input })) {
    chunks.push(chunk.chunk);
    if (chunk.done) break;
  }

  return chunks;
}
```

## Work with Multiple Colonies

### Create Multiple Colonies

```typescript
const colony1 = await sdk.createColony({ name: 'colony-1' });
const colony2 = await sdk.createColony({ name: 'colony-2' });
const colony3 = await sdk.createColony({ name: 'colony-3' });
```

### List All Colonies

```typescript
const colonies = sdk.listColonies();
colonies.forEach(colony => {
  console.log('Colony:', colony.id, colony.getState().name);
});
```

### Execute Tasks Across Colonies

```typescript
async function runTaskInColonies(colonies: ColonyHandle[], input: unknown) {
  const results = await Promise.all(
    colonies.map(colony => colony.runTask({ input }))
  );
  return results;
}
```

### Distribute Load Across Colonies

```typescript
async function distributeTask(colonies: ColonyHandle[], tasks: unknown[]) {
  const results = [];

  for (let i = 0; i < tasks.length; i++) {
    const colony = colonies[i % colonies.length];
    const result = await colony.runTask({ input: tasks[i] });
    results.push(result);
  }

  return results;
}
```

## Implement Retry Logic

### Exponential Backoff

```typescript
async function runTaskWithBackoff(
  colony: ColonyHandle,
  input: unknown,
  maxRetries = 3
) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await colony.runTask({ input });
      return result;
    } catch (error) {
      if (attempt === maxRetries) throw error;

      const delay = Math.pow(2, attempt) * 1000;  // 2s, 4s, 8s
      console.warn(`Retry ${attempt} after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

### Retry on Specific Errors

```typescript
async function runTaskRetrySpecific(
  colony: ColonyHandle,
  input: unknown
) {
  const retryableCodes = ['TASK_TIMEOUT', 'RESOURCE_EXHAUSTED'];
  let attempts = 0;
  const maxAttempts = 3;

  while (attempts < maxAttempts) {
    try {
      const result = await colony.runTask({ input });
      return result;
    } catch (error) {
      if (error instanceof PollnSDKError) {
        if (retryableCodes.includes(error.code)) {
          attempts++;
          console.warn(`Retry ${attempts}/${maxAttempts}`);
          continue;
        }
      }
      throw error;
    }
  }

  throw new Error('Max retries exceeded');
}
```

## Monitor Performance

### Track Task Execution Time

```typescript
sdk.on('agent:task:completed', (event) => {
  const time = event.data.result.executionTimeMs;
  if (time > 1000) {
    console.warn('Slow task:', time, 'ms');
  }
});
```

### Monitor Success Rates

```typescript
setInterval(() => {
  const agents = colony.listAgents();
  agents.forEach(agent => {
    const state = agent.getState();
    if (state.successRate < 0.5) {
      console.warn('Low success rate:', agent.id, state.successRate);
    }
  });
}, 60000);  // Every minute
```

### Track Resource Usage

```typescript
setInterval(() => {
  const state = colony.getState();
  console.log('Active agents:', state.activeAgents);
  console.log('Total agents:', state.totalAgents);
  console.log('Diversity:', state.shannonDiversity);
}, 30000);  // Every 30 seconds
```

### Alert on Errors

```typescript
sdk.on('error', (event) => {
  console.error('Error occurred:', event.data);
  // Send alert, log to external service, etc.
});
```

## Cleanup Resources

### Shutdown SDK

```typescript
await sdk.shutdown();
```

### Destroy Specific Colony

```typescript
await sdk.destroyColony('colony-id');
```

### Remove Specific Agent

```typescript
await colony.removeAgent('agent-id');
```

### Cleanup All Colonies

```typescript
async function cleanupAll(sdk: PollnSDK) {
  const colonies = sdk.listColonies();

  for (const colony of colonies) {
    await colony.destroy();
  }

  await sdk.shutdown();
}
```

### Graceful Shutdown

```typescript
process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');

  try {
    await sdk.shutdown();
    console.log('Shutdown complete');
    process.exit(0);
  } catch (error) {
    console.error('Shutdown error:', error);
    process.exit(1);
  }
});
```

## Best Practices

### 1. Always Initialize SDK

```typescript
const sdk = new PollnSDK();
await sdk.initialize();  // Don't forget this!
```

### 2. Handle Errors Properly

```typescript
try {
  const result = await colony.runTask({ input });
} catch (error) {
  if (error instanceof PollnSDKError) {
    // Handle specific error
  }
}
```

### 3. Use Appropriate Agent Types

- Ephemeral for one-off tasks
- Role for ongoing responsibilities
- Core for system functions

### 4. Monitor Performance

```typescript
sdk.on('agent:task:completed', (event) => {
  if (event.data.result.executionTimeMs > 1000) {
    console.warn('Slow task detected');
  }
});
```

### 5. Clean Up Resources

```typescript
await sdk.shutdown();
```

## Further Reading

- [Getting Started](./getting-started.md)
- [Core Concepts](./core-concepts.md)
- [API Reference](./api-reference.md)
- [Tutorials](./tutorials.md)
- [Debugging Guide](./debugging-guide.md)
