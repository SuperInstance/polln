# POLLN SDK - Getting Started Guide

Welcome to the POLLN SDK! This guide will help you get up and running with the POLLN distributed intelligence system in minutes.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Concepts](#basic-concepts)
- [Your First Colony](#your-first-colony)
- [Next Steps](#next-steps)

## Installation

### Requirements

- Node.js 18.0.0 or higher
- npm or yarn

### Install the SDK

```bash
npm install polln
```

Or with yarn:

```bash
yarn add polln
```

### Import the SDK

```typescript
// ES Modules
import { PollnSDK } from 'polln/sdk';

// CommonJS
const { PollnSDK } = require('polln/sdk');
```

## Quick Start

Get a colony running in under 5 minutes:

```typescript
import { PollnSDK } from 'polln/sdk';

async function main() {
  // 1. Initialize the SDK
  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  // 2. Create a colony
  const colony = await sdk.createColony({
    name: 'my-first-colony',
    maxAgents: 10
  });

  console.log('Colony created:', colony.id);

  // 3. Add an agent
  const agent = await colony.addAgent({
    category: 'ephemeral',
    goal: 'process-data',
    inputTopics: ['data'],
    outputTopic: 'results'
  });

  console.log('Agent added:', agent.id);

  // 4. Run a task
  const result = await colony.runTask({
    input: { message: 'Hello, POLLN!' }
  });

  console.log('Task result:', result.output);

  // 5. Cleanup
  await sdk.shutdown();
}

main().catch(console.error);
```

## Basic Concepts

### What is POLLN?

POLLN (Pattern-Organized Large Language Network) is a distributed intelligence system where simple, specialized agents work together to produce intelligent behavior through emergent coordination.

### Key Concepts

#### Colony
A **colony** is a collection of agents that work together. Think of it like a bee colony - individual bees are simple, but the colony becomes intelligent through coordination.

#### Agent
An **agent** is a specialized unit that performs specific tasks. There are three types:

- **Ephemeral Agents**: Short-lived, created for a specific task, then terminated
- **Role Agents**: Long-lived, handle ongoing responsibilities
- **Core Agents**: Essential, always-active agents that maintain colony health

#### Task
A **task** is a unit of work assigned to an agent. Tasks have inputs, outputs, and execution metadata.

#### Events
The SDK emits events for everything that happens: colony creation, agent lifecycle, task execution, etc. You can subscribe to these events to monitor and react to changes.

## Your First Colony

Let's build something more interesting - a simple text processing colony:

```typescript
import { PollnSDK } from 'polln/sdk';

async function createTextProcessingColony() {
  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  // Create a colony with custom configuration
  const colony = await sdk.createColony({
    name: 'text-processor',
    maxAgents: 50,
    resourceBudget: {
      totalCompute: 1000,
      totalMemory: 2048
    }
  });

  // Add multiple specialized agents
  const tokenizer = await colony.addAgent({
    category: 'role',
    goal: 'tokenize-text',
    inputTopics: ['raw-text'],
    outputTopic: 'tokens'
  });

  const analyzer = await colony.addAgent({
    category: 'role',
    goal: 'analyze-sentiment',
    inputTopics: ['tokens'],
    outputTopic: 'sentiment'
  });

  const summarizer = await colony.addAgent({
    category: 'ephemeral',
    goal: 'summarize-text',
    maxLifetimeMs: 30000 // 30 seconds
  });

  console.log('Colony state:', colony.getState());

  return { sdk, colony };
}
```

## Running Tasks

### Synchronous Tasks

Execute a task and wait for the result:

```typescript
const result = await colony.runTask({
  input: { text: 'POLLN is amazing!' }
});

if (result.success) {
  console.log('Success:', result.output);
  console.log('Execution time:', result.executionTimeMs, 'ms');
} else {
  console.error('Error:', result.error);
}
```

### Streaming Tasks

Stream results as they arrive:

```typescript
for await (const chunk of colony.streamTask({
  input: { text: longText }
}, { chunkSize: 100 })) {
  console.log('Chunk:', chunk.chunk);
  console.log('Done:', chunk.done);

  if (chunk.done) break;
}
```

### Task with Specific Agent

Target a specific agent for execution:

```typescript
const result = await colony.runTask({
  agentId: tokenizer.id,
  input: { text: 'Hello world' }
});
```

## Event Handling

Subscribe to colony events to monitor activity:

```typescript
// Subscribe to task completion events
sdk.on('agent:task:completed', (event) => {
  console.log('Task completed:', event.data);
});

// Subscribe to agent lifecycle events
sdk.on('colony:agent:added', (event) => {
  console.log('New agent:', event.data.agentId);
});

// Subscribe to errors
sdk.on('error', (event) => {
  console.error('Error:', event.data);
});
```

## Querying State

### List Colonies

```typescript
const allColonies = sdk.listColonies();
const activeColonies = sdk.listColonies({ active: true });
const largeColonies = sdk.listColonies({ minAgents: 10 });
```

### List Agents

```typescript
const allAgents = colony.listAgents();
const ephemeralAgents = colony.listAgents({ category: 'ephemeral' });
const successfulAgents = colony.listAgents({ minSuccessRate: 0.8 });
```

### Get Agent State

```typescript
const agent = colony.getAgent('agent-id');
if (agent) {
  const state = agent.getState();
  console.log('Success rate:', state.successRate);
  console.log('Execution count:', state.executionCount);
  console.log('Avg latency:', state.avgLatencyMs);
}
```

## Error Handling

The SDK provides detailed error information:

```typescript
import { PollnSDKError } from 'polln/sdk';

try {
  const result = await colony.runTask({
    input: data
  });
} catch (error) {
  if (error instanceof PollnSDKError) {
    console.error('Error code:', error.code);
    console.error('Message:', error.message);
    console.error('Details:', error.details);
  }
}
```

### Common Error Codes

- `SDK_NOT_INITIALIZED`: SDK not initialized
- `COLONY_NOT_FOUND`: Colony doesn't exist
- `AGENT_NOT_FOUND`: Agent doesn't exist
- `TASK_EXECUTION_FAILED`: Task execution failed
- `TIMEOUT`: Operation timed out

## Configuration

### SDK Configuration

```typescript
const sdk = new PollnSDK({
  // API key for remote colonies
  apiKey: process.env.POLLN_API_KEY,

  // WebSocket endpoint for remote colonies
  endpoint: 'wss://api.polln.ai',

  // Default timeout for operations
  timeout: 30000,

  // Enable debug logging
  debug: true,

  // Default colony configuration
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

### Colony Configuration

```typescript
const colony = await sdk.createColony({
  name: 'my-colony',
  maxAgents: 100,
  resourceBudget: {
    totalCompute: 2000,
    totalMemory: 4096,
    totalNetwork: 200
  },
  distributed: true,
  distributedConfig: {
    backend: 'redis',
    connectionString: 'redis://localhost:6379'
  }
});
```

## Next Steps

- Learn about [Core Concepts](./core-concepts.md)
- Explore the [API Reference](./api-reference.md)
- Follow the [Tutorials](./tutorials.md)
- Check out [How-To Guides](./how-to-guides.md)
- Learn about [Debugging](./debugging-guide.md)

## Additional Resources

- [GitHub Repository](https://github.com/SuperInstance/polln)
- [Examples](../examples/)
- [API Documentation](../api/)
- [Research Papers](../research/)

## Support

- GitHub Issues: https://github.com/SuperInstance/polln/issues
- Discussions: https://github.com/SuperInstance/polln/discussions
- Discord: (coming soon)
