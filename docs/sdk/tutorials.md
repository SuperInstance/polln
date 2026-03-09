# POLLN SDK - Tutorials

Step-by-step tutorials to learn the POLLN SDK.

## Table of Contents

- [Tutorial 1: Hello World](#tutorial-1-hello-world)
- [Tutorial 2: Text Processing Pipeline](#tutorial-2-text-processing-pipeline)
- [Tutorial 3: Multi-Agent Collaboration](#tutorial-3-multi-agent-collaboration)
- [Tutorial 4: Event-Driven Architecture](#tutorial-4-event-driven-architecture)
- [Tutorial 5: Error Handling and Retry](#tutorial-5-error-handling-and-retry)
- [Tutorial 6: Performance Monitoring](#tutorial-6-performance-monitoring)

## Tutorial 1: Hello World

Learn the basics by creating a simple colony that processes text.

### What You'll Learn

- How to initialize the SDK
- How to create a colony
- How to add an agent
- How to run a task
- How to cleanup resources

### Step 1: Install and Import

```bash
npm install polln
```

```typescript
import { PollnSDK } from 'polln/sdk';
```

### Step 2: Initialize SDK

```typescript
const sdk = new PollnSDK({ debug: true });
await sdk.initialize();
```

### Step 3: Create Colony

```typescript
const colony = await sdk.createColony({
  name: 'hello-world-colony',
  maxAgents: 10
});

console.log('Colony created:', colony.id);
```

### Step 4: Add Agent

```typescript
const agent = await colony.addAgent({
  category: 'ephemeral',
  goal: 'process-greeting',
  inputTopics: ['greetings'],
  outputTopic: 'responses'
});

console.log('Agent added:', agent.id);
```

### Step 5: Run Task

```typescript
const result = await colony.runTask({
  input: { text: 'Hello, POLLN!' }
});

if (result.success) {
  console.log('Success:', result.output);
} else {
  console.error('Error:', result.error);
}
```

### Step 6: Cleanup

```typescript
await sdk.shutdown();
```

### Complete Code

```typescript
import { PollnSDK } from 'polln/sdk';

async function helloWorld() {
  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  const colony = await sdk.createColony({
    name: 'hello-world-colony'
  });

  const agent = await colony.addAgent({
    category: 'ephemeral',
    goal: 'process-greeting'
  });

  const result = await colony.runTask({
    input: { text: 'Hello, POLLN!' }
  });

  console.log('Result:', result.output);

  await sdk.shutdown();
}

helloWorld().catch(console.error);
```

## Tutorial 2: Text Processing Pipeline

Create a pipeline of agents that process text through multiple stages.

### What You'll Learn

- How to create multiple agents
- How to chain agents together
- How to use role agents
- How to work with streaming

### Architecture

```
Input → Tokenizer → Analyzer → Summarizer → Output
```

### Step 1: Create Colony

```typescript
const sdk = new PollnSDK({ debug: true });
await sdk.initialize();

const colony = await sdk.createColony({
  name: 'text-pipeline',
  maxAgents: 50
});
```

### Step 2: Create Pipeline Agents

```typescript
// Tokenizer - splits text into tokens
const tokenizer = await colony.addAgent({
  category: 'role',
  goal: 'tokenize-text',
  inputTopics: ['raw-text'],
  outputTopic: 'tokens'
});

// Analyzer - analyzes sentiment
const analyzer = await colony.addAgent({
  category: 'role',
  goal: 'analyze-sentiment',
  inputTopics: ['tokens'],
  outputTopic: 'sentiment'
});

// Summarizer - creates summary
const summarizer = await colony.addAgent({
  category: 'ephemeral',
  goal: 'summarize-text',
  inputTopics: ['sentiment'],
  outputTopic: 'summary',
  maxLifetimeMs: 60000
});
```

### Step 3: Process Text Through Pipeline

```typescript
async function processPipeline(text: string) {
  // Step 1: Tokenize
  const tokenizeResult = await colony.runTask({
    agentId: tokenizer.id,
    input: { text }
  });

  // Step 2: Analyze
  const analyzeResult = await colony.runTask({
    agentId: analyzer.id,
    input: tokenizeResult.output
  });

  // Step 3: Summarize
  const summarizeResult = await colony.runTask({
    agentId: summarizer.id,
    input: analyzeResult.output
  });

  return summarizeResult.output;
}
```

### Step 4: Use Pipeline

```typescript
const result = await processPipeline(
  'POLLN is an amazing distributed intelligence system!'
);

console.log('Pipeline result:', result);
```

### Complete Code

```typescript
import { PollnSDK } from 'polln/sdk';

async function textPipeline() {
  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  const colony = await sdk.createColony({
    name: 'text-pipeline'
  });

  // Create agents
  const tokenizer = await colony.addAgent({
    category: 'role',
    goal: 'tokenize-text'
  });

  const analyzer = await colony.addAgent({
    category: 'role',
    goal: 'analyze-sentiment'
  });

  const summarizer = await colony.addAgent({
    category: 'ephemeral',
    goal: 'summarize-text'
  });

  // Process text
  const text = 'POLLN is amazing!';
  const result = await colony.runTask({
    agentId: summarizer.id,
    input: { text }
  });

  console.log('Result:', result.output);

  await sdk.shutdown();
}

textPipeline().catch(console.error);
```

## Tutorial 3: Multi-Agent Collaboration

Create a team of agents that collaborate to solve a complex problem.

### What You'll Learn

- How to create specialized agents
- How agents communicate
- How to coordinate multiple agents
- How to aggregate results

### Architecture

```
Researcher Agents → Aggregator → Validator → Output
```

### Step 1: Create Research Colony

```typescript
const sdk = new PollnSDK({ debug: true });
await sdk.initialize();

const colony = await sdk.createColony({
  name: 'research-colony',
  maxAgents: 100
});
```

### Step 2: Create Specialist Agents

```typescript
// Create multiple research specialists
const specialists = [];
const topics = ['technology', 'science', 'business', 'health'];

for (const topic of topics) {
  const specialist = await colony.addAgent({
    category: 'role',
    goal: `research-${topic}`,
    inputTopics: ['queries'],
    outputTopic: 'findings'
  });
  specialists.push(specialist);
}
```

### Step 3: Create Aggregator

```typescript
const aggregator = await colony.addAgent({
  category: 'role',
  goal: 'aggregate-findings',
  inputTopics: ['findings'],
  outputTopic: 'aggregated'
});
```

### Step 4: Create Validator

```typescript
const validator = await colony.addAgent({
  category: 'core',
  goal: 'validate-results',
  inputTopics: ['aggregated'],
  outputTopic: 'validated'
});
```

### Step 5: Parallel Research

```typescript
async function parallelResearch(query: string) {
  // Run all specialists in parallel
  const results = await Promise.all(
    specialists.map(specialist =>
      colony.runTask({
        agentId: specialist.id,
        input: { query }
      })
    )
  );

  console.log('Specialist results:', results.length);

  return results;
}
```

### Step 6: Complete Workflow

```typescript
async function researchWorkflow(query: string) {
  // Step 1: Parallel research
  const specialistResults = await parallelResearch(query);

  // Step 2: Aggregate findings
  const aggregatedResult = await colony.runTask({
    agentId: aggregator.id,
    input: { findings: specialistResults }
  });

  // Step 3: Validate results
  const validatedResult = await colony.runTask({
    agentId: validator.id,
    input: aggregatedResult.output
  });

  return validatedResult.output;
}

// Use the workflow
const result = await researchWorkflow('AI trends 2025');
console.log('Research result:', result);
```

## Tutorial 4: Event-Driven Architecture

Build an event-driven system using POLLN's event system.

### What You'll Learn

- How to subscribe to events
- How to react to events
- How to build event-driven workflows
- How to monitor system health

### Step 1: Setup Event Monitoring

```typescript
const sdk = new PollnSDK({ debug: true });
await sdk.initialize();

// Track all task completions
const taskTimes = new Map<string, number[]>();

sdk.on('agent:task:completed', (event) => {
  const agentId = event.data.agentId;
  const time = event.data.result.executionTimeMs;

  if (!taskTimes.has(agentId)) {
    taskTimes.set(agentId, []);
  }
  taskTimes.get(agentId)!.push(time);

  console.log(`Agent ${agentId}: ${time}ms`);
});
```

### Step 2: Track Failures

```typescript
const failures = new Map<string, number>();

sdk.on('agent:task:failed', (event) => {
  const agentId = event.data.agentId;
  const count = failures.get(agentId) || 0;
  failures.set(agentId, count + 1);

  console.error(`Agent ${agentId} failed:`, event.data.error);
});
```

### Step 3: Alert on Performance Issues

```typescript
sdk.on('agent:task:completed', (event) => {
  const time = event.data.result.executionTimeMs;

  if (time > 5000) {
    console.warn('Slow task detected:', {
      agentId: event.data.agentId,
      time: time
    });
  }
});
```

### Step 4: Monitor Colony Health

```typescript
setInterval(() => {
  const colonies = sdk.listColonies();

  colonies.forEach(colony => {
    const state = colony.getState();
    const diversity = state.shannonDiversity;

    if (diversity < 0.3) {
      console.warn('Low diversity:', colony.id, diversity);
    }

    if (state.activeAgents === 0) {
      console.warn('No active agents:', colony.id);
    }
  });
}, 30000);
```

### Step 5: Auto-Scale Based on Events

```typescript
const taskQueue: string[] = [];
let activeAgents = 0;

sdk.on('agent:task:started', (event) => {
  activeAgents++;
});

sdk.on('agent:task:completed', (event) => {
  activeAgents--;

  // Process next task
  if (taskQueue.length > 0) {
    const nextTask = taskQueue.shift();
    // Process next task
  }
});
```

## Tutorial 5: Error Handling and Retry

Build robust error handling and retry logic.

### What You'll Learn

- How to handle different error types
- How to implement retry logic
- How to use exponential backoff
- How to track retry statistics

### Step 1: Basic Error Handling

```typescript
import { PollnSDKError } from 'polln/sdk';

async function safeTask(colony: ColonyHandle, input: unknown) {
  try {
    const result = await colony.runTask({ input });
    return result;
  } catch (error) {
    if (error instanceof PollnSDKError) {
      console.error('Error code:', error.code);
      console.error('Message:', error.message);

      // Handle specific errors
      switch (error.code) {
        case 'TASK_TIMEOUT':
          // Handle timeout
          break;
        case 'AGENT_NOT_FOUND':
          // Handle missing agent
          break;
        default:
          // Handle other errors
      }
    }
    throw error;
  }
}
```

### Step 2: Retry with Exponential Backoff

```typescript
async function retryWithBackoff(
  colony: ColonyHandle,
  input: unknown,
  maxRetries = 3
) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await colony.runTask({ input });
      return result;
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000;
        console.warn(`Attempt ${attempt} failed, retrying in ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
```

### Step 3: Retry Only Specific Errors

```typescript
const RETRYABLE_ERRORS = ['TASK_TIMEOUT', 'RESOURCE_EXHAUSTED'];

async function smartRetry(
  colony: ColonyHandle,
  input: unknown
) {
  let attempts = 0;
  const maxAttempts = 3;

  while (attempts < maxAttempts) {
    try {
      const result = await colony.runTask({ input });
      return result;
    } catch (error) {
      if (error instanceof PollnSDKError) {
        if (RETRYABLE_ERRORS.includes(error.code)) {
          attempts++;
          continue;
        }
      }
      throw error;
    }
  }

  throw new Error('Max retries exceeded');
}
```

### Step 4: Track Retry Statistics

```typescript
const retryStats = new Map<string, { attempts: number; successes: number }>();

async function trackedRetry(
  colony: ColonyHandle,
  input: unknown
) {
  const taskId = Math.random().toString(36);

  if (!retryStats.has(taskId)) {
    retryStats.set(taskId, { attempts: 0, successes: 0 });
  }

  const stats = retryStats.get(taskId)!;

  try {
    const result = await retryWithBackoff(colony, input);
    stats.successes++;
    return result;
  } finally {
    stats.attempts++;
    console.log('Retry stats:', stats);
  }
}
```

## Tutorial 6: Performance Monitoring

Build a comprehensive performance monitoring system.

### What You'll Learn

- How to track performance metrics
- How to visualize performance data
- How to detect performance issues
- How to generate reports

### Step 1: Track Execution Times

```typescript
const executionTimes = new Map<string, number[]>();

sdk.on('agent:task:completed', (event) => {
  const agentId = event.data.agentId;
  const time = event.data.result.executionTimeMs;

  if (!executionTimes.has(agentId)) {
    executionTimes.set(agentId, []);
  }
  executionTimes.get(agentId)!.push(time);
});
```

### Step 2: Calculate Statistics

```typescript
function calculateStats(times: number[]) {
  if (times.length === 0) return null;

  const sorted = [...times].sort((a, b) => a - b);
  const sum = times.reduce((a, b) => a + b, 0);

  return {
    count: times.length,
    min: sorted[0],
    max: sorted[sorted.length - 1],
    avg: sum / times.length,
    median: sorted[Math.floor(sorted.length / 2)],
    p95: sorted[Math.floor(sorted.length * 0.95)],
    p99: sorted[Math.floor(sorted.length * 0.99)]
  };
}
```

### Step 3: Generate Performance Report

```typescript
function generatePerformanceReport() {
  const report = [];

  executionTimes.forEach((times, agentId) => {
    const stats = calculateStats(times);
    if (stats) {
      report.push({
        agentId,
        ...stats
      });
    }
  });

  return report;
}
```

### Step 4: Monitor in Real-Time

```typescript
setInterval(() => {
  const report = generatePerformanceReport();

  report.forEach(agentStats => {
    if (agentStats.p95 > 1000) {
      console.warn('Slow agent (p95 > 1s):', agentStats);
    }
  });
}, 60000);
```

### Step 5: Alert on Anomalies

```typescript
function detectAnomalies(agentId: string) {
  const times = executionTimes.get(agentId);
  if (!times || times.length < 10) return;

  const stats = calculateStats(times);
  const recent = times.slice(-5);
  const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;

  // Alert if recent average is 2x overall average
  if (recentAvg > stats.avg * 2) {
    console.warn('Performance anomaly detected:', {
      agentId,
      recentAvg,
      overallAvg: stats.avg
    });
  }
}
```

## Next Steps

- Explore the [API Reference](./api-reference.md)
- Learn about [Debugging](./debugging-guide.md)
- Check out [How-To Guides](./how-to-guides.md)
- Review [Core Concepts](./core-concepts.md)

## Getting Help

- GitHub Issues: https://github.com/SuperInstance/polln/issues
- Discussions: https://github.com/SuperInstance/polln/discussions
- Documentation: https://github.com/SuperInstance/polln/tree/main/docs
