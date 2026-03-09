# POLLN SDK - Debugging Guide

Learn how to use the POLLN debugger to inspect, profile, and debug your colonies and agents.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Agent Inspection](#agent-inspection)
- [Colony Visualization](#colony-visualization)
- [Distributed Tracing](#distributed-tracing)
- [Performance Profiling](#performance-profiling)
- [Execution Replay](#execution-replay)
- [Breakpoints](#breakpoints)
- [Best Practices](#best-practices)

## Overview

The POLLN debugger (`PollnDebugger`) provides comprehensive debugging capabilities:

- **Agent Inspection**: Inspect agent state, variables, and call stacks
- **Colony Visualization**: Visualize agent graph structure and connections
- **Distributed Tracing**: Trace execution across agents and colonies
- **Performance Profiling**: Profile CPU, memory, and I/O operations
- **Execution Replay**: Replay and analyze past executions
- **Breakpoints**: Set conditional breakpoints on agent state

## Getting Started

### Install the Debugger

The debugger is included with the POLLN SDK:

```typescript
import { PollnDebugger } from 'polln/debug';
```

### Initialize the Debugger

```typescript
const debugger = new PollnDebugger({
  verbose: true,
  maxTraceHistory: 1000,
  maxProfilingSamples: 10000,
  autoProfile: false,
  enableTracing: true,
  enableVisualization: true
});

await debugger.initialize();
```

### Shutdown the Debugger

```typescript
await debugger.shutdown();
```

## Agent Inspection

Inspect the state of any agent at any time.

### Basic Inspection

```typescript
const inspection = await debugger.inspectAgent(
  'agent-id',
  agentInstance
);

console.log('Agent state:', inspection.state);
console.log('Call stack:', inspection.callStack);
console.log('Variables:', inspection.variables);
```

### Get Historical State

```typescript
// Get latest state
const latestState = debugger.getAgentState('agent-id');

// Get state at specific timestamp
const pastState = debugger.getAgentState('agent-id', timestamp);
```

### Compare States

```typescript
const inspection1 = await debugger.inspectAgent('agent-id', agent1);
const inspection2 = await debugger.inspectAgent('agent-id', agent2);

const differences = debugger.compareAgentStates(inspection1, inspection2);
console.log('Differences:', differences);
```

### Inspection Data

```typescript
interface AgentInspection {
  agentId: string;
  category: string;
  state: Record<string, unknown>;
  callStack: StackFrame[];
  variables: Record<string, unknown>;
  sentPackages: A2APackageTrace[];
  receivedPackages: A2APackageTrace[];
  breakpointStatus: BreakpointStatus;
  metrics: AgentMetrics;
  timestamp: number;
}
```

## Colony Visualization

Visualize the structure and connections of your colony.

### Create Visualization

```typescript
const agents = new Map<string, any>();
agents.set('agent-1', agent1Instance);
agents.set('agent-2', agent2Instance);

const visualization = await debugger.visualizeColony(
  'colony-id',
  colonyInstance,
  agents,
  {
    layout: 'force',
    showLabels: true,
    colorBy: 'category',
    sizeBy: 'activity'
  }
);
```

### Get Cached Visualization

```typescript
const cached = debugger.getCachedVisualization('colony-id');
```

### Export Visualization

```typescript
// Export as DOT (Graphviz)
const dot = debugger.exportVisualization(visualization, 'dot');

// Export as JSON
const json = debugger.exportVisualization(visualization, 'json');

// Export as SVG
const svg = debugger.exportVisualization(visualization, 'svg');
```

### Graph Metrics

```typescript
const metrics = debugger.computeGraphMetrics(visualization);
console.log('Node count:', metrics.nodeCount);
console.log('Edge count:', metrics.edgeCount);
console.log('Density:', metrics.density);
console.log('Clustering coefficient:', metrics.avgClusteringCoefficient);
```

### Visualization Data

```typescript
interface GraphVisualization {
  colonyId: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  layout: GraphLayout;
  clusters?: GraphCluster[];
  metadata: VisualizationMetadata;
}
```

## Distributed Tracing

Trace execution flow across agents and colonies.

### Start a Trace

```typescript
const traceId = debugger.startTrace('causal-chain-123', {
  type: 'task',
  userId: 'user-123'
});
```

### Start Spans

```typescript
const spanId = debugger.startSpan(
  traceId,
  'process-task',
  'agent-id',
  'colony-id',
  undefined, // parentSpanId
  { 'task.type': 'text-processing' } // tags
);
```

### Add Logs to Spans

```typescript
debugger.addLog(spanId, 'info', 'Processing started', {
  inputSize: data.length
});

debugger.addLog(spanId, 'debug', 'Tokenizing text', {
  tokenCount: tokens.length
});
```

### Finish Spans

```typescript
debugger.finishSpan(spanId, 'ok');
// or with error
debugger.finishSpan(spanId, 'error', new Error('Processing failed'));
```

### Finish Trace

```typescript
const trace = debugger.finishTrace(traceId);
console.log('Trace completed:', trace.stats);
```

### Query Traces

```typescript
// Get by trace ID
const trace = debugger.getTrace('trace-id');

// Get by causal chain ID
const trace = debugger.getTraceByCausalChain('causal-chain-id');

// List with filters
const traces = debugger.listTraces({
  agentId: 'agent-id',
  minStartTime: Date.now() - 3600000,
  limit: 10
});
```

### Analyze Performance

```typescript
const analysis = debugger.analyzeTracePerformance('trace-id');
console.log('Total duration:', analysis.totalDuration);
console.log('Critical path:', analysis.criticalPath);
console.log('Bottlenecks:', analysis.bottlenecks);
```

### Export Traces

```typescript
// Export as JSON
const json = debugger.exportTrace('trace-id', 'json');

// Export as Jaeger format
const jaeger = debugger.exportTrace('trace-id', 'jaeger');

// Export as Zipkin format
const zipkin = debugger.exportTrace('trace-id', 'zipkin');
```

## Performance Profiling

Profile CPU, memory, and I/O operations.

### Start Profiling

```typescript
await debugger.startProfile('profile-1', 'cpu');
```

### Stop Profiling

```typescript
const profile = await debugger.stopProfile('profile-1');
```

### Get Profile

```typescript
const profile = debugger.getProfile('profile-1');
console.log('Duration:', profile.duration);
console.log('Samples:', profile.samples.length);
```

### List Profiles

```typescript
const profiles = debugger.listProfiles({
  type: 'cpu',
  minStartTime: Date.now() - 3600000
});
```

### Get Hotspots

```typescript
const hotspots = debugger.getHotspots('profile-1', 0.5);
hotspots.forEach(hotspot => {
  console.log(`${hotspot.name}: ${hotspot.percentage}%`);
});
```

### Get Call Tree

```typescript
const callTree = debugger.getCallTree('profile-1', 10);
console.log('Call tree:', callTree);
```

### Optimization Suggestions

```typescript
const suggestions = debugger.getOptimizationSuggestions('profile-1', 0.7);
suggestions.forEach(suggestion => {
  console.log(`${suggestion.title}: ${suggestion.expectedImprovement}`);
});
```

### Compare Profiles

```typescript
const comparison = debugger.compareProfiles('profile-1', 'profile-2');
console.log('Duration diff:', comparison.durationDiff);
console.log('New hotspots:', comparison.newHotspots);
console.log('Recommendations:', comparison.recommendations);
```

### Export Profiles

```typescript
// Export as JSON
const json = debugger.exportProfile('profile-1', 'json');

// Export as Flamegraph
const flamegraph = debugger.exportProfile('profile-1', 'flamegraph');

// Export as Call Tree
const calltree = debugger.exportProfile('profile-1', 'calltree');

// Export as CSV
const csv = debugger.exportProfile('profile-1', 'csv');
```

## Execution Replay

Replay and analyze past executions.

### Start Replay

```typescript
const sessionId = await debugger.startReplay('causal-chain-id', {
  speed: 1.0,
  stopOnError: true,
  recordSnapshots: true
});
```

### Get Replay Session

```typescript
const session = debugger.getReplaySession(sessionId);
console.log('Status:', session.status);
console.log('Events:', session.events.length);
```

### Step Through Replay

```typescript
let event;
while ((event = await debugger.stepReplay(sessionId))) {
  console.log('Event:', event);
  // Analyze event
}
```

### Control Replay

```typescript
// Pause
await debugger.pauseReplay(sessionId);

// Resume
await debugger.resumeReplay(sessionId);

// Cancel
await debugger.cancelReplay(sessionId);
```

### Get Divergences

```typescript
const divergences = debugger.getReplayDivergences(sessionId);
divergences.forEach(divergence => {
  console.warn(`Divergence: ${divergence.description}`);
});
```

### Get Snapshots

```typescript
const snapshots = debugger.getReplaySnapshots(sessionId);
snapshots.forEach(snapshot => {
  console.log('Snapshot:', snapshot.snapshotId);
  console.log('State:', snapshot.agentStates);
});
```

### What-If Analysis

```typescript
const result = await debugger.whatIf('causal-chain-id', [
  {
    type: 'modify_agent',
    agentId: 'agent-1',
    modification: { learningRate: 0.1 }
  }
]);

console.log('What-if result:', result);
```

### Export Replay

```typescript
// Export as JSON
const json = debugger.exportReplay(sessionId, 'json');

// Export as CSV
const csv = debugger.exportReplay(sessionId, 'csv');
```

## Breakpoints

Set conditional breakpoints on agent state.

### Set Breakpoint

```typescript
const breakpointId = debugger.setBreakpoint({
  type: 'agent_state',
  agentId: 'agent-1',
  predicate: 'state.valueFunction < 0.5'
});
```

### Breakpoint Conditions

```typescript
// Agent state condition
{
  type: 'agent_state',
  agentId: 'agent-1',
  predicate: 'state.errorCount > 10'
}

// Package received condition
{
  type: 'package_received',
  agentId: 'agent-1',
  packageType: 'error'
}

// Error condition
{
  type: 'error',
  errorType: 'TimeoutError'
}
```

### Remove Breakpoint

```typescript
debugger.removeBreakpoint(breakpointId);
```

### List Breakpoints

```typescript
// All breakpoints
const all = debugger.listBreakpoints();

// For specific agent
const agentBreakpoints = debugger.listBreakpoints('agent-1');
```

## Best Practices

### 1. Enable Debugging Early

```typescript
const debugger = new PollnDebugger({ verbose: true });
await debugger.initialize();
```

### 2. Use Distributed Tracing

```typescript
const traceId = debugger.startTrace(causalChainId);
const spanId = debugger.startSpan(traceId, operation, agentId, colonyId);
// ... do work ...
debugger.finishSpan(spanId);
debugger.finishTrace(traceId);
```

### 3. Profile Regularly

```typescript
await debugger.startProfile('daily-profile', 'cpu');
// ... run for 24 hours ...
const profile = await debugger.stopProfile('daily-profile');
const suggestions = debugger.getOptimizationSuggestions('daily-profile');
```

### 4. Monitor Performance

```typescript
debugger.on('profile:completed', (event) => {
  const { profileId, profile } = event.data;
  const hotspots = debugger.getHotspots(profileId);
  console.log('Hotspots:', hotspots);
});
```

### 5. Use What-If Analysis

```typescript
const result = await debugger.whatIf(causalChainId, [
  { type: 'modify_agent', agentId: 'agent-1', modification: {...} }
]);
console.log('Predicted outcome:', result);
```

## Integration with SDK

### Combine SDK and Debugger

```typescript
import { PollnSDK } from 'polln/sdk';
import { PollnDebugger } from 'polln/debug';

const sdk = new PollnSDK({ debug: true });
const debugger = new PollnDebugger({ verbose: true });

await Promise.all([sdk.initialize(), debugger.initialize()]);

// Use SDK for operations
const colony = await sdk.createColony({ name: 'debugged-colony' });

// Use debugger for inspection
const visualization = await debugger.visualizeColony(
  colony.id,
  colony.getCoreColony(),
  new Map()
);

// Cleanup
await Promise.all([sdk.shutdown(), debugger.shutdown()]);
```

## Debugging Workflows

### Workflow 1: Debug Slow Tasks

```typescript
// 1. Profile the task
await debugger.startProfile('slow-task', 'cpu');
const result = await colony.runTask({ input });
await debugger.stopProfile('slow-task');

// 2. Analyze hotspots
const hotspots = debugger.getHotspots('slow-task');
console.log('Hotspots:', hotspots);

// 3. Get optimization suggestions
const suggestions = debugger.getOptimizationSuggestions('slow-task');
console.log('Suggestions:', suggestions);
```

### Workflow 2: Debug Failed Tasks

```typescript
// 1. Trace the execution
const traceId = debugger.startTrace(causalChainId);
const spanId = debugger.startSpan(traceId, 'task', agentId, colonyId);

try {
  await colony.runTask({ input });
  debugger.finishSpan(spanId, 'ok');
} catch (error) {
  debugger.finishSpan(spanId, 'error', error);
}

debugger.finishTrace(traceId);

// 2. Analyze the trace
const trace = debugger.getTrace(traceId);
console.log('Errors:', trace.errors);
```

### Workflow 3: Debug Agent Communication

```typescript
// 1. Visualize colony
const agents = new Map();
colony.listAgents().forEach(agent => {
  agents.set(agent.id, agent);
});

const visualization = await debugger.visualizeColony(
  colony.id,
  colony.getCoreColony(),
  agents
);

// 2. Check communication patterns
visualization.edges.forEach(edge => {
  if (edge.frequency < 0.1) {
    console.warn('Weak connection:', edge);
  }
});
```

## Further Reading

- [Getting Started](./getting-started.md)
- [Core Concepts](./core-concepts.md)
- [API Reference](./api-reference.md)
- [How-To Guides](./how-to-guides.md)
- [Tutorials](./tutorials.md)
