# POLLN SDK - Core Concepts

This guide explains the fundamental concepts and architecture of the POLLN distributed intelligence system.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Colonies](#colonies)
- [Agents](#agents)
- [Tasks](#tasks)
- [Communication](#communication)
- [Learning](#learning)
- [Evolution](#evolution)
- [Distributed Coordination](#distributed-coordination)

## Overview

POLLN (Pattern-Organized Large Language Network) is a distributed intelligence system inspired by biological systems like bee colonies and neural networks. The key insight is that **intelligence emerges from the connections between simple agents**, not from any single agent.

### Key Principles

1. **Subsumption Architecture**: Lower-level behaviors override higher-level ones
2. **Emergent Intelligence**: Complex behavior emerges from simple interactions
3. **Learning Through Connection**: Memory is stored in connection weights, not databases
4. **Stochastic Selection**: Probabilistic decision-making enables durability through diversity

## Architecture

### System Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                    POLLN System                          │
├─────────────────────────────────────────────────────────┤
│  Colonies (Collections of agents)                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Agents (Specialized processing units)            │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  Subsumption Layers                          │  │  │
│  │  │  ┌───────────────────────────────────────┐  │  │  │
│  │  │  │  SAFETY (Critical, overrides all)     │  │  │  │
│  │  │  ├───────────────────────────────────────┤  │  │  │
│  │  │  │  REFLEX (Fast, automatic)              │  │  │  │
│  │  │  ├───────────────────────────────────────┤  │  │  │
│  │  │  │  HABITUAL (Learned behaviors)          │  │  │  │
│  │  │  ├───────────────────────────────────────┤  │  │  │
│  │  │  │  DELIBERATE (Slow, conscious)          │  │  │  │
│  │  │  └───────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Subsumption Architecture

Agents process inputs through multiple layers, where lower layers can override higher ones:

```typescript
// Priority order (highest first)
1. SAFETY    - Emergency actions, always wins
2. REFLEX    - Immediate responses
3. HABITUAL  - Learned patterns
4. DELIBERATE - Conscious reasoning
```

This ensures critical safety responses are never blocked by slower deliberation.

## Colonies

A **colony** is a collection of agents that work together towards common goals.

### Colony Lifecycle

```typescript
// Create a colony
const colony = await sdk.createColony({
  name: 'my-colony',
  maxAgents: 100,
  resourceBudget: { totalCompute: 1000, totalMemory: 2048 }
});

// Query colony state
const state = colony.getState();
console.log('Total agents:', state.totalAgents);
console.log('Active agents:', state.activeAgents);
console.log('Diversity index:', state.shannonDiversity);

// Destroy colony
await colony.destroy();
```

### Colony Properties

- **ID**: Unique identifier
- **Name**: Human-readable name
- **Gardener ID**: Owner/creator ID
- **Total Agents**: Number of registered agents
- **Active Agents**: Agents currently processing
- **Shannon Diversity**: Diversity metric (0-1, higher is more diverse)

### Resource Management

Colonies manage resources across all agents:

```typescript
const colony = await sdk.createColony({
  name: 'resource-managed',
  maxAgents: 50,
  resourceBudget: {
    totalCompute: 2000,  // Compute units
    totalMemory: 4096,   // MB
    totalNetwork: 200    // Network units
  }
});
```

## Agents

An **agent** is a specialized processing unit with a specific purpose.

### Agent Categories

#### 1. Ephemeral Agents (TaskAgent)

Short-lived agents created for specific tasks:

```typescript
const agent = await colony.addAgent({
  category: 'ephemeral',
  goal: 'process-single-task',
  maxLifetimeMs: 30000  // Auto-terminate after 30s
});
```

**Characteristics:**
- Created for a specific task
- Short lifespan (seconds to minutes)
- Auto-terminated after completion or timeout
- Ideal for one-off processing jobs

#### 2. Role Agents (RoleAgent)

Long-lived agents with ongoing responsibilities:

```typescript
const agent = await colony.addAgent({
  category: 'role',
  goal: 'monitor-data-stream',
  inputTopics: ['data-stream'],
  outputTopic: 'alerts'
});
```

**Characteristics:**
- Persistent across sessions
- Handle continuous responsibilities
- Subscribe to specific input topics
- Publish to output topics

#### 3. Core Agents (CoreAgent)

Essential agents that maintain colony health:

```typescript
const agent = await colony.addAgent({
  category: 'core',
  goal: 'colony-health-monitor'
});
```

**Characteristics:**
- Always active
- Critical for colony operation
- Monitor system health
- Manage resource allocation

### Agent State

Every agent maintains internal state:

```typescript
const state = agent.getState();
console.log('Status:', state.status);        // dormant, active, hibernating, error
console.log('Value function:', state.valueFunction);  // 0-1
console.log('Success rate:', state.successRate);
console.log('Executions:', state.executionCount);
console.log('Avg latency:', state.avgLatencyMs);
```

### Agent Lifecycle

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│ Created │───>│ Dormant │───>│ Active   │───>│ Removed │
└─────────┘    └────┬────┘    └────┬─────┘    └─────────┘
                    │              │
                    │              v
                    │         ┌──────────┐
                    │         │Hibernate │
                    │         └────┬─────┘
                    │              │
                    └──────────────┘
```

## Tasks

A **task** is a unit of work assigned to an agent.

### Task Structure

```typescript
const result = await colony.runTask({
  id: 'task-123',              // Optional custom ID
  agentId: 'agent-456',        // Optional specific agent
  type: 'text-processing',     // For agent selection
  input: { text: 'Hello' },    // Input data
  priority: 0.8,               // 0-1, higher = more important
  timeout: 5000,               // 5 second timeout
  metadata: {                  // Custom metadata
    userId: 'user-123'
  }
});
```

### Task Result

```typescript
console.log('Success:', result.success);
console.log('Output:', result.output);
console.log('Execution time:', result.executionTimeMs);
console.log('Timestamp:', result.timestamp);

if (!result.success) {
  console.error('Error:', result.error);
}
```

### Streaming Tasks

For large outputs or long-running tasks:

```typescript
for await (const chunk of colony.streamTask({
  input: largeData
}, { chunkSize: 1024 })) {
  console.log('Received:', chunk.chunk);
  if (chunk.done) break;
}
```

## Communication

### A2A Protocol (Agent-to-Agent)

Agents communicate using A2A (Agent-to-Agent) packages:

```typescript
interface A2APackage {
  packageId: string;           // Unique ID
  causalChainId: string;       // Traceability chain
  parentIds: string[];         // Parent packages
  fromAgentId: string;         // Source agent
  toAgentId: string;           // Target agent
  payload: unknown;            // Data
  payloadType: string;         // Type identifier
  timestamp: number;           // Send time
}
```

### SPORE Protocol

SPORE (Secure Pollen-Oriented Routing Exchange) handles pub/sub messaging:

```typescript
const agent = await colony.addAgent({
  category: 'role',
  inputTopics: ['topic-1', 'topic-2'],  // Subscribe
  outputTopic: 'results'                 // Publish
});
```

### Pollen Grains

Compressed behavioral patterns (embeddings) that agents share:

```typescript
// Agents extract and share patterns
const pollenGrain = await agent.extractPollen(inputData);

// Other agents can use the pattern
const result = await agent.applyPollen(pollenGrain, newData);
```

## Learning

### Hebbian Learning

"Neurons that fire together, wire together":

```typescript
// When agents work well together, their connection strengthens
hebbianLearning.update(sourceAgentId, targetAgentId, reward);
```

### Value Network

TD(lambda) learning predicts state values:

```typescript
const value = await valueNetwork.predict(state);
console.log('State value:', value);  // 0-1

// Update based on reward
await valueNetwork.update(state, reward, nextState);
```

### Dreaming

Agents optimize policies during offline "dream" cycles:

```typescript
// Trigger dream cycle
await colony.startDreamCycle({
  episodes: 100,
  learningRate: 0.01
});

// Dreaming optimizes policies based on past experiences
```

## Evolution

### Graph Evolution

The agent network evolves over time:

```typescript
// Prune weak connections
await colony.pruneConnections({ threshold: 0.1 });

// Graft new connections
await colony.graftConnection(fromAgentId, toAgentId);

// Cluster similar agents
await colony.clusterAgents({ algorithm: 'louvain' });
```

### Succession

Knowledge transfer from parent to child agents:

```typescript
// Create child agent with inherited knowledge
const childAgent = await parentAgent.succession({
  mutationRate: 0.1,
  inheritanceRatio: 0.8
});
```

## Distributed Coordination

### Federated Learning

Multiple colonies learn together without sharing raw data:

```typescript
const colony = await sdk.createColony({
  name: 'federated-colony',
  distributed: true,
  distributedConfig: {
    backend: 'redis',
    connectionString: 'redis://localhost:6379'
  }
});

// Sync with federation
await colony.syncFederation();
```

### Meadow System

Community space for pattern sharing:

```typescript
// Share pattern with community
await meadow.publishPattern({
  patternId: 'pattern-123',
  category: 'text-processing',
  performance: 0.95
});

// Discover useful patterns
const patterns = await meadow.discoverPatterns({
  category: 'text-processing',
  minPerformance: 0.8
});
```

## Debugging and Observability

### SDK Debugging

```typescript
import { PollnDebugger } from 'polln/debug';

const debugger = new PollnDebugger({ verbose: true });
await debugger.initialize();

// Inspect agent state
const inspection = await debugger.inspectAgent(agentId, agent);

// Visualize colony graph
const visualization = await debugger.visualizeColony(
  colonyId,
  colony,
  agents
);

// Profile performance
await debugger.startProfile('profile-1', 'cpu');
// ... run tasks ...
const profile = await debugger.stopProfile('profile-1');
```

### Distributed Tracing

```typescript
// Start a trace
const traceId = debugger.startTrace(causalChainId);

// Start spans
const spanId = debugger.startSpan(
  traceId,
  'process-task',
  agentId,
  colonyId
);

// Add logs
debugger.addLog(spanId, 'info', 'Processing started');

// Finish span
debugger.finishSpan(spanId, 'ok');
```

## Best Practices

### 1. Choose the Right Agent Type

- Use **ephemeral** for one-off tasks
- Use **role** for ongoing responsibilities
- Use **core** for essential system functions

### 2. Manage Resources Wisely

```typescript
const colony = await sdk.createColony({
  resourceBudget: {
    totalCompute: 2000,
    totalMemory: 4096,
    totalNetwork: 200
  }
});
```

### 3. Monitor Performance

```typescript
sdk.on('agent:task:completed', (event) => {
  if (event.data.executionTimeMs > 1000) {
    console.warn('Slow task:', event.data);
  }
});
```

### 4. Handle Errors Gracefully

```typescript
try {
  const result = await colony.runTask({ input });
} catch (error) {
  if (error instanceof PollnSDKError) {
    // Handle specific error codes
  }
}
```

### 5. Use Streaming for Large Outputs

```typescript
for await (const chunk of colony.streamTask({ input })) {
  // Process chunk
  if (chunk.done) break;
}
```

## Further Reading

- [API Reference](./api-reference.md)
- [How-To Guides](./how-to-guides.md)
- [Tutorials](./tutorials.md)
- [Debugging Guide](./debugging-guide.md)
