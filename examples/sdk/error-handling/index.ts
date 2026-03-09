/**
 * POLLN SDK Example: Error Handling Patterns
 *
 * This example demonstrates how to:
 * - Handle SDK errors properly
 * - Implement retry logic with exponential backoff
 * - Handle timeout errors
 * - Validate inputs
 * - Create error boundaries
 */

import { PollnSDK, PollnSDKError } from 'polln/sdk';

async function main() {
  console.log('=== POLLN SDK: Error Handling Example ===\n');

  const sdk = new PollnSDK({ debug: true });
  await sdk.initialize();

  const colony = await sdk.createColony({
    name: 'error-handling-colony'
  });

  const agent = await colony.addAgent({
    category: 'role',
    goal: 'process-data'
  });

  // 1. Basic error handling
  console.log('1. Basic error handling...\n');

  try {
    const result = await colony.runTask({
      input: { text: 'Valid input' }
    });
    console.log('✓ Task succeeded\n');
  } catch (error) {
    if (error instanceof PollnSDKError) {
      console.error('PollnSDKError:', error.code, error.message);
    }
  }

  // 2. Type-safe error handling
  console.log('2. Type-safe error handling...\n');

  async function safeRunTask(input: unknown) {
    try {
      const result = await colony.runTask({ input });
      return { success: true, result };
    } catch (error) {
      if (error instanceof PollnSDKError) {
        return {
          success: false,
          error: {
            code: error.code,
            message: error.message,
            details: error.details
          }
        };
      }
      return {
        success: false,
        error: { code: 'UNKNOWN', message: String(error) }
      };
    }
  }

  const safeResult = await safeRunTask({ text: 'Type-safe input' });
  if (safeResult.success) {
    console.log('✓ Type-safe execution succeeded\n');
  } else {
    console.log('✗ Error:', safeResult.error.code, '-', safeResult.error.message);
    console.log();
  }

  // 3. Handle specific error codes
  console.log('3. Handling specific error codes...\n');

  try {
    const result = await colony.runTask({
      input: { text: 'Test input' }
    });
  } catch (error) {
    if (error instanceof PollnSDKError) {
      switch (error.code) {
        case 'COLONY_NOT_FOUND':
          console.log('  Colony does not exist');
          break;
        case 'AGENT_NOT_FOUND':
          console.log('  Agent does not exist');
          break;
        case 'TASK_EXECUTION_FAILED':
          console.log('  Task execution failed');
          break;
        case 'TASK_TIMEOUT':
          console.log('  Task timed out');
          break;
        default:
          console.log(`  Unknown error: ${error.code}`);
      }
      console.log();
    }
  }

  // 4. Retry with exponential backoff
  console.log('4. Retry with exponential backoff...\n');

  async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries = 3
  ): Promise<T> {
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000;
          console.log(`  Attempt ${attempt} failed, retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError;
  }

  try {
    const result = await retryWithBackoff(async () => {
      return await colony.runTask({ input: { text: 'Retry test' } });
    });
    console.log('✓ Retry succeeded\n');
  } catch (error) {
    console.log('✗ All retries failed\n');
  }

  // 5. Retry only specific errors
  console.log('5. Retry only specific errors...\n');

  const RETRYABLE_ERRORS = ['TASK_TIMEOUT', 'RESOURCE_EXHAUSTED'];

  async function smartRetry<T>(
    fn: () => Promise<T>,
    maxRetries = 3
  ): Promise<T> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        if (error instanceof PollnSDKError) {
          if (RETRYABLE_ERRORS.includes(error.code) && attempt < maxRetries) {
            console.log(`  Retrying (${attempt}/${maxRetries})...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            continue;
          }
        }
        throw error;
      }
    }
    throw new Error('Max retries exceeded');
  }

  try {
    const result = await smartRetry(async () => {
      return await colony.runTask({ input: { text: 'Smart retry test' } });
    });
    console.log('✓ Smart retry succeeded\n');
  } catch (error) {
    console.log('✗ Smart retry failed\n');
  }

  // 6. Timeout handling
  console.log('6. Timeout handling...\n');

  async function runWithTimeout(input: unknown, timeout: number) {
    try {
      const result = await colony.runTask({
        input,
        timeout
      });
      console.log(`✓ Task completed within ${timeout}ms\n`);
      return result;
    } catch (error) {
      if (error instanceof PollnSDKError && error.code === 'TASK_TIMEOUT') {
        console.log(`✗ Task timed out after ${timeout}ms\n`);
        // Handle timeout - maybe retry with longer timeout
        return null;
      }
      throw error;
    }
  }

  await runWithTimeout({ text: 'Timeout test' }, 5000);

  // 7. Input validation
  console.log('7. Input validation...\n');

  function validateInput(input: unknown): { valid: boolean; error?: string } {
    if (!input) {
      return { valid: false, error: 'Input is required' };
    }

    if (typeof input !== 'object') {
      return { valid: false, error: 'Input must be an object' };
    }

    const obj = input as any;
    if (!obj.text || typeof obj.text !== 'string') {
      return { valid: false, error: 'Input must have a text property' };
    }

    if (obj.text.length > 1000) {
      return { valid: false, error: 'Text too long (max 1000 chars)' };
    }

    return { valid: true };
  }

  const validInput = { text: 'Valid input' };
  const validation = validateInput(validInput);
  if (!validation.valid) {
    console.log(`✗ Invalid input: ${validation.error}\n`);
  } else {
    console.log('✓ Input valid\n');
  }

  // 8. Error boundary pattern
  console.log('8. Error boundary pattern...\n');

  class ErrorBoundary {
    private errors: Error[] = [];

    async execute<T>(fn: () => Promise<T>): Promise<T | null> {
      try {
        return await fn();
      } catch (error) {
        this.errors.push(error as Error);
        console.log('  Error caught by boundary:', error);
        return null;
      }
    }

    getErrors(): Error[] {
      return this.errors;
    }

    hasErrors(): boolean {
      return this.errors.length > 0;
    }

    clear(): void {
      this.errors = [];
    }
  }

  const boundary = new ErrorBoundary();

  const result1 = await boundary.execute(async () => {
    return await colony.runTask({ input: { text: 'Task 1' } });
  });

  const result2 = await boundary.execute(async () => {
    return await colony.runTask({ input: { text: 'Task 2' } });
  });

  if (boundary.hasErrors()) {
    console.log(`  Boundary caught ${boundary.getErrors().length} errors\n`);
  } else {
    console.log('  ✓ No errors caught by boundary\n');
  }

  // 9. Aggregate error reporting
  console.log('9. Aggregate error reporting...\n');

  const errorStats = new Map<string, number>();

  function trackError(error: PollnSDKError) {
    const count = errorStats.get(error.code) || 0;
    errorStats.set(error.code, count + 1);
  }

  // Simulate various errors
  const testErrors = ['TASK_TIMEOUT', 'AGENT_NOT_FOUND', 'TASK_EXECUTION_FAILED'];
  testErrors.forEach(code => {
    trackError(new PollnSDKError(code as any, `Test error: ${code}`));
  });

  console.log('  Error statistics:');
  errorStats.forEach((count, code) => {
    console.log(`    ${code}: ${count}`);
  });
  console.log();

  // 10. Graceful degradation
  console.log('10. Graceful degradation...\n');

  async function runWithFallback(
    primary: () => Promise<any>,
    fallback: () => Promise<any>
  ) {
    try {
      return await primary();
    } catch (error) {
      console.log('  Primary failed, using fallback...');
      return await fallback();
    }
  }

  const degradedResult = await runWithFallback(
    async () => await colony.runTask({ input: { text: 'Primary' } }),
    async () => ({ output: { text: 'Fallback result' }, success: true })
  );
  console.log('✓ Degraded result:', degradedResult.output);
  console.log();

  await sdk.shutdown();
  console.log('✓ Cleanup complete');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
