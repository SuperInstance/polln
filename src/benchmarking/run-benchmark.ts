/**
 * SMP Baseline Comparison - Test Runner
 *
 * Run comparisons for SMP vs monolithic LLM
 */

import { runComparison, ComparisonEngine, MonolithicBaseline } from './baseline-comparison.js';

// ============================================================================
// TEST CASES
// ============================================================================

const TEST_CASES = [
  {
    name: 'Sentiment Analysis',
    taskType: 'sentiment',
    prompts: [
      'I absolutely love this product! It works great and looks amazing.',
      'This is the worst experience I have ever had. Terrible service.',
      'The product is okay. Nothing special, but does the job.',
    ],
  },
  {
    name: 'Document Classification',
    taskType: 'classification',
    prompts: [
      'AI researchers at Stanford have developed a new machine learning algorithm that can process images 10x faster than previous methods.',
      'The stock market saw significant gains today as tech companies reported strong quarterly earnings.',
      'A new study shows that regular exercise can reduce the risk of heart disease by up to 50%.',
    ],
  },
  {
    name: 'Multi-step Reasoning',
    taskType: 'reasoning',
    prompts: [
      'If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?',
      'A bat and ball cost $1.10. The bat costs $1.00 more than the ball. How much does the ball cost?',
    ],
  },
];

// ============================================================================
// RUNNER
// ============================================================================

/**
 * Run all test cases
 */
export async function runAllTests(
  format: 'text' | 'json' | 'markdown' | 'html' = 'text'
): Promise<void> {
  console.log('='.repeat(80));
  console.log('SMP BASELINE COMPARISON TEST SUITE');
  console.log('='.repeat(80));
  console.log();

  for (const testCase of TEST_CASES) {
    console.log(`\nRunning: ${testCase.name}`);
    console.log('-'.repeat(80));

    for (const prompt of testCase.prompts) {
      console.log(`\nPrompt: "${prompt}"`);
      console.log();

      try {
        const report = await runComparison(prompt, testCase.taskType, format);
        console.log(report);
      } catch (error) {
        console.error('Error running comparison:', error);
      }

      console.log();
    }
  }
}

/**
 * Run single test case
 */
export async function runSingleTest(
  prompt: string,
  taskType: string = 'sentiment',
  format: 'text' | 'json' | 'markdown' | 'html' = 'text'
): Promise<void> {
  console.log('Running single comparison...');
  console.log();

  const report = await runComparison(prompt, taskType, format);
  console.log(report);
}

/**
 * Run custom benchmark
 */
export async function runCustomBenchmark(
  prompts: string[],
  taskType: string = 'sentiment',
  format: 'text' | 'json' | 'markdown' | 'html' = 'text'
): Promise<void> {
  const baseline = new MonolithicBaseline('gpt-4', 100);
  const engine = new ComparisonEngine(baseline);

  console.log('='.repeat(80));
  console.log('CUSTOM SMP BENCHMARK');
  console.log('='.repeat(80));
  console.log(`Task Type: ${taskType}`);
  console.log(`Prompts: ${prompts.length}`);
  console.log();

  const results = [];

  for (const prompt of prompts) {
    console.log(`Testing: "${prompt.substring(0, 50)}..."`);

    try {
      const report = await engine.compare(prompt, taskType);
      results.push(report);
    } catch (error) {
      console.error('Error:', error);
    }
  }

  // Aggregate results
  console.log();
  console.log('='.repeat(80));
  console.log('AGGREGATE RESULTS');
  console.log('='.repeat(80));

  const avgImprovement = {
    latency: results.reduce((sum, r) => sum + r.improvement.latency, 0) / results.length,
    accuracy: results.reduce((sum, r) => sum + r.improvement.accuracy, 0) / results.length,
    energy: results.reduce((sum, r) => sum + r.improvement.energy, 0) / results.length,
  };

  const wins = results.filter(r => r.winner === 'smp').length;
  const losses = results.filter(r => r.winner === 'monolithic').length;
  const ties = results.filter(r => r.winner === 'tie').length;

  console.log(`Wins: ${wins}`);
  console.log(`Losses: ${losses}`);
  console.log(`Ties: ${ties}`);
  console.log();
  console.log('Average Improvement:');
  console.log(`  Latency:  ${avgImprovement.latency.toFixed(1)}%`);
  console.log(`  Accuracy: ${avgImprovement.accuracy.toFixed(1)}%`);
  console.log(`  Energy:   ${avgImprovement.energy.toFixed(1)}%`);
}

// ============================================================================
// CLI INTERFACE
// ============================================================================

/**
 * Main entry point for CLI
 */
export async function main(args: string[]): Promise<void> {
  const format = (args.find(a => a.startsWith('--format='))?.split('=')[1] || 'text') as any;
  const taskType = args.find(a => a.startsWith('--task='))?.split('=')[1] || 'sentiment';
  const prompt = args.find(a => !a.startsWith('--'));

  if (prompt) {
    // Single prompt mode
    await runSingleTest(prompt, taskType, format);
  } else {
    // Full test suite mode
    await runAllTests(format);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main(process.argv.slice(2)).catch(console.error);
}
