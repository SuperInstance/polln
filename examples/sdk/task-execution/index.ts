/**
 * POLLN SDK Example: Task Execution Patterns
 *
 * This example demonstrates how to:
 * - Run synchronous tasks
 * - Stream task results
 * - Execute tasks with specific agents
 * - Handle task timeouts and priorities
 */

import { PollnSDK } from 'polln/sdk';

async function main() {
  console.log('=== POLLN SDK: Task Execution Example ===\n');

  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  const colony = await sdk.createColony({
    name: 'task-execution-colony'
  });

  const processor = await colony.addAgent({
    category: 'role',
    goal: 'process-data'
  });

  // 1. Basic synchronous task
  console.log('1. Basic synchronous task...');
  const basicResult = await colony.runTask({
    input: { text: 'Hello, POLLN!' }
  });
  console.log(`✓ Completed in ${basicResult.executionTimeMs}ms`);
  console.log(`  Success: ${basicResult.success}\n`);

  // 2. Task with specific agent
  console.log('2. Task with specific agent...');
  const agentResult = await colony.runTask({
    agentId: processor.id,
    input: { text: 'Target specific agent' }
  });
  console.log(`✓ Agent ${processor.id} completed task\n`);

  // 3. Task with priority
  console.log('3. Task with priority...');
  const priorityResult = await colony.runTask({
    input: { text: 'High priority task' },
    priority: 0.9
  });
  console.log(`✓ High priority task completed\n`);

  // 4. Task with timeout
  console.log('4. Task with timeout...');
  try {
    const timeoutResult = await colony.runTask({
      input: { text: 'Quick task' },
      timeout: 5000
    });
    console.log(`✓ Task completed within timeout\n`);
  } catch (error) {
    console.log(`✗ Task timed out\n`);
  }

  // 5. Task with metadata
  console.log('5. Task with metadata...');
  const metadataResult = await colony.runTask({
    input: { text: 'Trackable task' },
    metadata: {
      userId: 'user-123',
      requestId: 'req-456',
      tags: ['important', 'batch-1']
    }
  });
  console.log(`✓ Task with metadata completed\n`);

  // 6. Multiple tasks in parallel
  console.log('6. Multiple tasks in parallel...');
  const startTime = Date.now();
  const parallelResults = await Promise.all([
    colony.runTask({ input: { text: 'Task 1' } }),
    colony.runTask({ input: { text: 'Task 2' } }),
    colony.runTask({ input: { text: 'Task 3' } })
  ]);
  const parallelTime = Date.now() - startTime;
  console.log(`✓ Completed ${parallelResults.length} tasks in ${parallelTime}ms\n`);

  // 7. Streaming task
  console.log('7. Streaming task...');
  let chunkCount = 0;
  for await (const chunk of colony.streamTask({
    input: { text: 'Large data to stream' }
  }, { chunkSize: 10 })) {
    chunkCount++;
    process.stdout.write('.');
    if (chunk.done) break;
  }
  console.log(`\n✓ Streamed ${chunkCount} chunks\n`);

  // 8. Sequential task pipeline
  console.log('8. Sequential task pipeline...');
  const pipelineSteps = ['tokenize', 'analyze', 'summarize'];
  let pipelineResult = { text: 'Input data' };

  for (const step of pipelineSteps) {
    const result = await colony.runTask({
      input: { step, data: pipelineResult }
    });
    pipelineResult = result.output as any;
    console.log(`  ${step}: ✓`);
  }
  console.log('✓ Pipeline completed\n');

  // 9. Batch processing
  console.log('9. Batch processing...');
  const batchData = Array.from({ length: 10 }, (_, i) => ({ id: i, data: `item-${i}` }));
  const batchResults = await Promise.all(
    batchData.map(item =>
      colony.runTask({
        input: { text: item.data }
      })
    )
  );
  console.log(`✓ Processed batch of ${batchResults.length} items\n`);

  // 10. Retry logic
  console.log('10. Retry logic...');
  let attempts = 0;
  const maxAttempts = 3;
  let retryResult;

  while (attempts < maxAttempts) {
    try {
      retryResult = await colony.runTask({
        input: { text: 'Retry attempt' }
      });
      console.log(`✓ Succeeded on attempt ${attempts + 1}\n`);
      break;
    } catch (error) {
      attempts++;
      if (attempts >= maxAttempts) {
        console.log(`✗ Failed after ${maxAttempts} attempts\n`);
        break;
      }
      console.log(`  Attempt ${attempts} failed, retrying...`);
      await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
    }
  }

  // Summary statistics
  console.log('11. Summary statistics...');
  const allResults = [
    basicResult, agentResult, priorityResult, timeoutResult || basicResult,
    metadataResult, ...parallelResults, retryResult || basicResult
  ];

  const totalTime = allResults.reduce((sum, r) => sum + r.executionTimeMs, 0);
  const avgTime = totalTime / allResults.length;
  const successCount = allResults.filter(r => r.success).length;

  console.log(`  Total tasks: ${allResults.length}`);
  console.log(`  Successful: ${successCount}`);
  console.log(`  Total time: ${totalTime}ms`);
  console.log(`  Average time: ${avgTime.toFixed(2)}ms\n`);

  await sdk.shutdown();
  console.log('✓ Cleanup complete');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
