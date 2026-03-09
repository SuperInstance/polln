/**
 * POLLN SDK Example: Event Handling
 *
 * This example demonstrates how to:
 * - Subscribe to colony events
 * - Subscribe to agent lifecycle events
 * - Subscribe to task events
 * - Unsubscribe from events
 * - Build event-driven workflows
 */

import { PollnSDK } from 'polln/sdk';

async function main() {
  console.log('=== POLLN SDK: Event Handling Example ===\n');

  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  const colony = await sdk.createColony({
    name: 'event-handling-colony'
  });

  // Track event counts
  const eventCounts = new Map<string, number>();

  // Helper to track events
  const trackEvent = (eventType: string) => {
    const count = eventCounts.get(eventType) || 0;
    eventCounts.set(eventType, count + 1);
    console.log(`  [${eventType}] Count: ${count + 1}`);
  };

  // 1. Colony events
  console.log('1. Subscribing to colony events...\n');

  sdk.on('colony:created', (event) => {
    trackEvent('colony:created');
    console.log(`    Colony created: ${event.data.colonyId}`);
  });

  sdk.on('colony:destroyed', (event) => {
    trackEvent('colony:destroyed');
    console.log(`    Colony destroyed: ${event.data.colonyId}`);
  });

  // 2. Agent lifecycle events
  console.log('2. Subscribing to agent lifecycle events...\n');

  sdk.on('colony:agent:added', (event) => {
    trackEvent('colony:agent:added');
    console.log(`    Agent added: ${event.data.agentId} to colony ${event.data.colonyId}`);
  });

  sdk.on('agent:born', (event) => {
    trackEvent('agent:born');
    console.log(`    Agent born: ${event.data.agentId}`);
  });

  sdk.on('agent:activated', (event) => {
    trackEvent('agent:activated');
    console.log(`    Agent activated: ${event.data.agentId}`);
  });

  sdk.on('agent:deactivated', (event) => {
    trackEvent('agent:deactivated');
    console.log(`    Agent deactivated: ${event.data.agentId}`);
  });

  // 3. Task events
  console.log('3. Subscribing to task events...\n');

  sdk.on('task:created', (event) => {
    trackEvent('task:created');
    console.log(`    Task created: ${event.data.taskId}`);
  });

  sdk.on('agent:task:started', (event) => {
    trackEvent('agent:task:started');
    console.log(`    Task started: ${event.data.taskId} on agent ${event.data.agentId}`);
  });

  sdk.on('agent:task:completed', (event) => {
    trackEvent('agent:task:completed');
    const time = event.data.result.executionTimeMs;
    console.log(`    Task completed: ${event.data.taskId} in ${time}ms`);
  });

  sdk.on('agent:task:failed', (event) => {
    trackEvent('agent:task:failed');
    console.log(`    Task failed: ${event.data.taskId} - ${event.data.error}`);
  });

  // 4. Error events
  console.log('4. Subscribing to error events...\n');

  sdk.on('error', (event) => {
    trackEvent('error');
    console.log(`    Error occurred:`, event.data);
  });

  // 5. Dream events
  console.log('5. Subscribing to dream events...\n');

  sdk.on('dream:started', (event) => {
    trackEvent('dream:started');
    console.log(`    Dream cycle started`);
  });

  sdk.on('dream:episode', (event) => {
    trackEvent('dream:episode');
    console.log(`    Dream episode: ${event.data.episode}`);
  });

  sdk.on('dream:completed', (event) => {
    trackEvent('dream:completed');
    console.log(`    Dream cycle completed`);
  });

  // Trigger some events
  console.log('6. Triggering events...\n');

  // Add agents (triggers agent events)
  const agent1 = await colony.addAgent({
    category: 'ephemeral',
    goal: 'task-1'
  });
  console.log();

  const agent2 = await colony.addAgent({
    category: 'role',
    goal: 'task-2'
  });
  console.log();

  // Run tasks (triggers task events)
  console.log('7. Running tasks to trigger task events...\n');

  await colony.runTask({
    input: { text: 'Task 1' }
  });
  console.log();

  await colony.runTask({
    agentId: agent2.id,
    input: { text: 'Task 2' }
  });
  console.log();

  await colony.runTask({
    input: { text: 'Task 3' }
  });
  console.log();

  // 8. Event-driven workflow
  console.log('8. Building event-driven workflow...\n');

  const workflowState = {
    tasksStarted: 0,
    tasksCompleted: 0,
    totalTime: 0
  };

  const workflowHandler = (event: any) => {
    if (event.type === 'agent:task:started') {
      workflowState.tasksStarted++;
    } else if (event.type === 'agent:task:completed') {
      workflowState.tasksCompleted++;
      workflowState.totalTime += event.data.result.executionTimeMs;
    }

    console.log(`  Workflow state: ${JSON.stringify(workflowState)}`);
  };

  sdk.on('agent:task:started', workflowHandler);
  sdk.on('agent:task:completed', workflowHandler);

  // Run more tasks
  await colony.runTask({ input: { text: 'Workflow task 1' } });
  console.log();
  await colony.runTask({ input: { text: 'Workflow task 2' } });
  console.log();

  // 9. Conditional event handling
  console.log('9. Conditional event handling (slow tasks)...\n');

  sdk.on('agent:task:completed', (event) => {
    const time = event.data.result.executionTimeMs;
    if (time > 100) {
      console.log(`  ⚠ Slow task detected: ${time}ms`);
    }
  });

  await new Promise(resolve => setTimeout(resolve, 200));
  await colony.runTask({ input: { text: 'Potentially slow task' } });
  console.log();

  // 10. Event aggregation
  console.log('10. Event aggregation summary...\n');

  console.log('  Event counts:');
  eventCounts.forEach((count, eventType) => {
    console.log(`    ${eventType}: ${count}`);
  });
  console.log();

  // 11. Unsubscribe example
  console.log('11. Unsubscribing from events...\n');

  const handler = (event: any) => {
    console.log(`  This handler will be removed`);
  };

  sdk.on('agent:task:started', handler);
  sdk.off('agent:task:started', handler);
  console.log('  Handler removed\n');

  // Final statistics
  console.log('12. Final statistics...\n');
  console.log(`  Total events tracked: ${Array.from(eventCounts.values()).reduce((a, b) => a + b, 0)}`);
  console.log(`  Unique event types: ${eventCounts.size}`);
  console.log(`  Workflow tasks: ${workflowState.tasksCompleted}`);
  console.log(`  Avg task time: ${(workflowState.totalTime / workflowState.tasksCompleted || 0).toFixed(2)}ms\n`);

  await sdk.shutdown();
  console.log('✓ Cleanup complete');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
