/**
 * POLLN SDK Example: Agent Management
 *
 * This example demonstrates how to:
 * - Create different types of agents
 * - List and filter agents
 * - Monitor agent performance
 * - Remove agents
 */

import { PollnSDK } from 'polln/sdk';

async function main() {
  console.log('=== POLLN SDK: Agent Management Example ===\n');

  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  const colony = await sdk.createColony({
    name: 'agent-management-colony',
    maxAgents: 50
  });

  // Create different types of agents
  console.log('Creating agents...\n');

  // Ephemeral agents
  console.log('1. Creating ephemeral agents...');
  for (let i = 0; i < 5; i++) {
    await colony.addAgent({
      category: 'ephemeral',
      goal: `task-${i}`,
      maxLifetimeMs: 60000
    });
  }
  console.log('✓ Created 5 ephemeral agents\n');

  // Role agents
  console.log('2. Creating role agents...');
  const dataProcessor = await colony.addAgent({
    category: 'role',
    goal: 'process-data',
    inputTopics: ['raw-data'],
    outputTopic: 'processed-data'
  });

  const dataAnalyzer = await colony.addAgent({
    category: 'role',
    goal: 'analyze-data',
    inputTopics: ['processed-data'],
    outputTopic: 'insights'
  });

  const alertNotifier = await colony.addAgent({
    category: 'role',
    goal: 'send-alerts',
    inputTopics: ['insights'],
    outputTopic: 'alerts'
  });
  console.log('✓ Created 3 role agents\n');

  // Core agents
  console.log('3. Creating core agents...');
  await colony.addAgent({
    category: 'core',
    goal: 'health-monitor'
  });

  await colony.addAgent({
    category: 'core',
    goal: 'resource-manager'
  });
  console.log('✓ Created 2 core agents\n');

  // List all agents
  console.log('4. Listing all agents...');
  const allAgents = colony.listAgents();
  console.log(`✓ Total agents: ${allAgents.length}\n`);

  // Filter agents by category
  console.log('5. Filtering agents by category...');
  const ephemeralAgents = colony.listAgents({ category: 'ephemeral' });
  const roleAgents = colony.listAgents({ category: 'role' });
  const coreAgents = colony.listAgents({ category: 'core' });

  console.log(`  Ephemeral: ${ephemeralAgents.length}`);
  console.log(`  Role: ${roleAgents.length}`);
  console.log(`  Core: ${coreAgents.length}\n`);

  // Get agent details
  console.log('6. Getting agent details...');
  const agentDetails = colony.getAgent(dataProcessor.id);
  if (agentDetails) {
    const state = agentDetails.getState();
    console.log(`  Agent ID: ${state.id}`);
    console.log(`  Category: ${state.category}`);
    console.log(`  Goal: ${state.goal}`);
    console.log(`  Status: ${state.status}`);
    console.log(`  Success Rate: ${(state.successRate * 100).toFixed(1)}%\n`);
  }

  // Simulate some tasks to update stats
  console.log('7. Running sample tasks...');
  for (let i = 0; i < 3; i++) {
    await colony.runTask({
      agentId: dataProcessor.id,
      input: { data: `sample-${i}` }
    });
  }
  console.log('✓ Completed 3 tasks\n');

  // Check updated stats
  console.log('8. Updated agent stats...');
  const updatedState = agentDetails.getState();
  console.log(`  Execution count: ${updatedState.executionCount}`);
  console.log(`  Success count: ${updatedState.successCount}`);
  console.log(`  Failure count: ${updatedState.failureCount}\n`);

  // Find best performing agents
  console.log('9. Finding best performing agents...');
  const topAgents = colony.listAgents({
    minSuccessRate: 0.5,
    limit: 3
  });
  console.log(`✓ Found ${topAgents.length} top agents:`);
  topAgents.forEach((agent, index) => {
    const state = agent.getState();
    console.log(`  ${index + 1}. ${agent.id} - ${(state.successRate * 100).toFixed(1)}% success`);
  });
  console.log();

  // Remove an agent
  console.log('10. Removing an agent...');
  const agentToRemove = ephemeralAgents[0];
  await colony.removeAgent(agentToRemove.id);
  console.log(`✓ Removed agent: ${agentToRemove.id}\n`);

  // Final count
  console.log('11. Final agent count...');
  const finalCount = colony.listAgents().length;
  console.log(`✓ Total agents: ${finalCount}\n`);

  // Cleanup
  await sdk.shutdown();
  console.log('✓ Cleanup complete');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
