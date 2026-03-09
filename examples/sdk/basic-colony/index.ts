/**
 * POLLN SDK Example: Basic Colony Creation
 *
 * This example demonstrates how to:
 * - Initialize the POLLN SDK
 * - Create a colony
 * - Add an agent
 * - Run a task
 * - Cleanup resources
 */

import { PollnSDK } from 'polln/sdk';

async function main() {
  console.log('=== POLLN SDK: Basic Colony Example ===\n');

  // Step 1: Initialize SDK
  console.log('1. Initializing SDK...');
  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();
  console.log('✓ SDK initialized\n');

  // Step 2: Create a colony
  console.log('2. Creating colony...');
  const colony = await sdk.createColony({
    name: 'basic-colony',
    maxAgents: 10,
    resourceBudget: {
      totalCompute: 1000,
      totalMemory: 2048,
      totalNetwork: 100
    }
  });
  console.log(`✓ Colony created: ${colony.id}`);
  console.log(`  Name: ${colony.getState().name}\n`);

  // Step 3: Add an agent
  console.log('3. Adding agent...');
  const agent = await colony.addAgent({
    category: 'ephemeral',
    goal: 'process-greeting',
    inputTopics: ['greetings'],
    outputTopic: 'responses'
  });
  console.log(`✓ Agent added: ${agent.id}`);
  console.log(`  Category: ${agent.getCategory()}`);
  console.log(`  Goal: ${agent.config.goal}\n`);

  // Step 4: Run a task
  console.log('4. Running task...');
  const result = await colony.runTask({
    input: { text: 'Hello, POLLN!' }
  });

  console.log(`✓ Task completed`);
  console.log(`  Success: ${result.success}`);
  console.log(`  Execution time: ${result.executionTimeMs}ms`);
  if (result.success) {
    console.log(`  Output:`, result.output);
  } else {
    console.log(`  Error: ${result.error}`);
  }
  console.log();

  // Step 5: Query state
  console.log('5. Colony state:');
  const state = colony.getState();
  console.log(`  Total agents: ${state.totalAgents}`);
  console.log(`  Active agents: ${state.activeAgents}`);
  console.log(`  Diversity: ${state.shannonDiversity.toFixed(3)}\n`);

  // Step 6: Cleanup
  console.log('6. Cleaning up...');
  await sdk.shutdown();
  console.log('✓ Shutdown complete');
}

// Run the example
main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
