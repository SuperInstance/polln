/**
 * POLLN SDK Example: Debugging Workflows
 *
 * This example demonstrates how to:
 * - Use the POLLN debugger
 * - Inspect agent state
 * - Visualize colony graph
 * - Profile performance
 * - Trace execution
 */

import { PollnSDK } from 'polln/sdk';
import { PollnDebugger } from 'polln/debug';

async function main() {
  console.log('=== POLLN SDK: Debugging Workflows Example ===\n');

  // Initialize SDK and Debugger
  const sdk = new PollnSDK({ debug: true });
  const debugger = new PollnDebugger({
    verbose: true,
    enableTracing: true,
    enableVisualization: true
  });

  await Promise.all([sdk.initialize(), debugger.initialize()]);
  console.log('✓ SDK and Debugger initialized\n');

  // Create colony
  console.log('1. Creating colony...');
  const colony = await sdk.createColony({
    name: 'debugging-colony',
    maxAgents: 20
  });
  console.log(`✓ Colony created: ${colony.id}\n`);

  // Add agents
  console.log('2. Adding agents...');
  const agents = [];
  for (let i = 0; i < 5; i++) {
    const agent = await colony.addAgent({
      category: 'role',
      goal: `task-${i}`
    });
    agents.push(agent);
  }
  console.log(`✓ Added ${agents.length} agents\n`);

  // 3. Inspect agent state
  console.log('3. Inspecting agent state...');
  const agentToInspect = agents[0];
  const inspection = await debugger.inspectAgent(
    agentToInspect.id,
    agentToInspect
  );
  console.log('  Agent inspection:');
  console.log(`    ID: ${inspection.agentId}`);
  console.log(`    Category: ${inspection.category}`);
  console.log(`    Status: ${inspection.state.status}`);
  console.log(`    Value function: ${inspection.metrics.avgValueFunction.toFixed(3)}`);
  console.log(`    Success rate: ${(inspection.metrics.successCount / (inspection.metrics.successCount + inspection.metrics.failureCount) * 100).toFixed(1)}%\n`);

  // 4. Visualize colony graph
  console.log('4. Visualizing colony graph...');
  const agentsMap = new Map<string, any>();
  agents.forEach(agent => {
    agentsMap.set(agent.id, agent);
  });

  const visualization = await debugger.visualizeColony(
    colony.id,
    colony.getCoreColony(),
    agentsMap,
    {
      layout: 'force',
      showLabels: true,
      colorBy: 'category'
    }
  );

  console.log('  Colony visualization:');
  console.log(`    Nodes: ${visualization.metadata.nodeCount}`);
  console.log(`    Edges: ${visualization.metadata.edgeCount}`);
  console.log(`    Density: ${visualization.metadata.density.toFixed(3)}`);
  console.log(`    Clustering: ${visualization.metadata.avgClusteringCoefficient.toFixed(3)}\n`);

  // 5. Start distributed trace
  console.log('5. Starting distributed trace...');
  const causalChainId = `trace-${Date.now()}`;
  const traceId = debugger.startTrace(causalChainId, {
    type: 'task',
    userId: 'example-user'
  });

  // Run task with tracing
  const spanId = debugger.startSpan(
    traceId,
    'example-task',
    agents[0].id,
    colony.id,
    undefined,
    { 'example': 'true' }
  );

  debugger.addLog(spanId, 'info', 'Starting task', { timestamp: Date.now() });

  const result = await colony.runTask({
    agentId: agents[0].id,
    input: { text: 'Debugging example' }
  });

  debugger.addLog(spanId, 'info', 'Task completed', {
    success: result.success,
    time: result.executionTimeMs
  });

  debugger.finishSpan(spanId, 'ok');
  const trace = debugger.finishTrace(traceId);

  console.log('  Trace completed:');
  console.log(`    Spans: ${trace.stats.totalSpans}`);
  console.log(`    Duration: ${trace.stats.totalDuration}ms`);
  console.log(`    Agents: ${trace.stats.agentsInvolved.length}\n`);

  // 6. Profile performance
  console.log('6. Profiling performance...');
  await debugger.startProfile('example-profile', 'cpu');

  // Run some tasks
  const profileResults = [];
  for (let i = 0; i < 5; i++) {
    const r = await colony.runTask({
      input: { text: `Profile task ${i}` }
    });
    profileResults.push(r);
  }

  const profile = await debugger.stopProfile('example-profile');

  console.log('  Profile completed:');
  console.log(`    Duration: ${profile.duration}ms`);
  console.log(`    Samples: ${profile.stats.totalSamples}`);
  console.log(`    Avg CPU: ${profile.stats.avgCpuUsage.toFixed(2)}%`);
  console.log(`    Avg Memory: ${profile.stats.avgMemoryUsage.toFixed(2)}MB\n`);

  // 7. Get hotspots
  console.log('7. Finding performance hotspots...');
  const hotspots = debugger.getHotspots('example-profile', 0.1);
  console.log(`  Found ${hotspots.length} hotspots:`);
  hotspots.slice(0, 5).forEach((hotspot, index) => {
    console.log(`    ${index + 1}. ${hotspot.name}: ${hotspot.percentage.toFixed(1)}%`);
  });
  console.log();

  // 8. Get optimization suggestions
  console.log('8. Getting optimization suggestions...');
  const suggestions = debugger.getOptimizationSuggestions('example-profile', 0.3);
  console.log(`  Found ${suggestions.length} suggestions:`);
  suggestions.slice(0, 3).forEach((suggestion, index) => {
    console.log(`    ${index + 1}. [${suggestion.type}] ${suggestion.title}`);
    console.log(`       Priority: ${(suggestion.priority * 100).toFixed(0)}%`);
    console.log(`       Effort: ${suggestion.effort}`);
    console.log(`       Expected: ${suggestion.expectedImprovement}`);
  });
  console.log();

  // 9. Compare agent states
  console.log('9. Comparing agent states...');
  const inspection1 = await debugger.inspectAgent(agents[0].id, agents[0]);
  const inspection2 = await debugger.inspectAgent(agents[1].id, agents[1]);

  const differences = debugger.compareAgentStates(inspection1, inspection2);
  console.log('  State differences:');
  console.log(`    Value function diff: ${differences.valueFunctionDiff.toFixed(3)}`);
  console.log(`    Success count diff: ${differences.successCountDiff}`);
  console.log(`    Execution count diff: ${differences.executionCountDiff}\n`);

  // 10. Export trace data
  console.log('10. Exporting trace data...');
  const traceJson = debugger.exportTrace(traceId, 'json');
  console.log(`  Trace export size: ${traceJson.length} bytes\n`);

  // 11. Get debugger state
  console.log('11. Debugger state...');
  const debuggerState = debugger.getState();
  console.log('  Debugger state:');
  console.log(`    Initialized: ${debuggerState.initialized}`);
  console.log(`    Active profiles: ${debuggerState.activeProfiles}`);
  console.log(`    Active traces: ${debuggerState.activeTraces}`);
  console.log(`    Active replays: ${debuggerState.activeReplays}\n`);

  // Cleanup
  console.log('12. Cleaning up...');
  await Promise.all([sdk.shutdown(), debugger.shutdown()]);
  console.log('✓ Cleanup complete');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
