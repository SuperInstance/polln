#!/usr/bin/env node
/**
 * SMP Baseline Comparison - Example Usage
 *
 * This example demonstrates how to use the baseline comparison infrastructure
 * to compare SMP tile chains against monolithic LLM calls.
 */

import { runComparison } from '../src/benchmarking/baseline-comparison.js';

// ============================================================================
// EXAMPLE 1: Simple Sentiment Analysis
// ============================================================================

async function example1_sentiment() {
  console.log('\n=== Example 1: Sentiment Analysis ===\n');

  const report = await runComparison(
    'I absolutely love this product! It works great and looks amazing.',
    'sentiment',
    'text'
  );

  console.log(report);
}

// ============================================================================
// EXAMPLE 2: Document Classification
// ============================================================================

async function example2_classification() {
  console.log('\n=== Example 2: Document Classification ===\n');

  const report = await runComparison(
    'AI researchers at Stanford have developed a new machine learning algorithm.',
    'classification',
    'text'
  );

  console.log(report);
}

// ============================================================================
// EXAMPLE 3: Multi-step Reasoning
// ============================================================================

async function example3_reasoning() {
  console.log('\n=== Example 3: Multi-step Reasoning ===\n');

  const report = await runComparison(
    'If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?',
    'reasoning',
    'text'
  );

  console.log(report);
}

// ============================================================================
// EXAMPLE 4: Generate HTML Report
// ============================================================================

async function example4_htmlReport() {
  console.log('\n=== Example 4: HTML Report ===\n');

  const htmlReport = await runComparison(
    'This product exceeded all my expectations!',
    'sentiment',
    'html'
  );

  // Save to file
  const fs = await import('fs/promises');
  await fs.writeFile('baseline-report.html', htmlReport);
  console.log('HTML report saved to: baseline-report.html');
}

// ============================================================================
// EXAMPLE 5: Batch Comparison
// ============================================================================

async function example5_batch() {
  console.log('\n=== Example 5: Batch Comparison ===\n');

  const prompts = [
    'Best purchase ever!',
    'Terrible quality, do not buy.',
    'It\'s okay, nothing special.',
  ];

  const results = [];

  for (const prompt of prompts) {
    console.log(`\nTesting: "${prompt}"`);
    const report = await runComparison(prompt, 'sentiment', 'text');
    results.push(report);

    // Print summary
    console.log(`\nWinner: ${report.winner}`);
    console.log(`Latency Improvement: ${report.improvement.latency.toFixed(1)}%`);
    console.log(`Pareto Rank: ${report.paretoRank}`);
  }

  // Aggregate summary
  const wins = results.filter(r => r.winner === 'smp').length;
  console.log(`\n\nSMP won ${wins}/${results.length} comparisons`);
}

// ============================================================================
// EXAMPLE 6: Custom Comparison Engine
// ============================================================================

async function example6_customEngine() {
  console.log('\n=== Example 6: Custom Comparison Engine ===\n');

  const { ComparisonEngine, MonolithicBaseline } = await import('../src/benchmarking/baseline-comparison.js');

  // Create custom baseline with different model
  const baseline = new MonolithicBaseline('gpt-3.5-turbo', 50); // Faster model
  const engine = new ComparisonEngine(baseline);

  // Run comparison with custom context
  const report = await engine.compare(
    'The service was excellent and the staff was very helpful.',
    'sentiment',
    {
      iterations: 5,      // More iterations for accuracy
      warmup: true,       // Enable warmup
    }
  );

  console.log(JSON.stringify(report, null, 2));
}

// ============================================================================
// EXAMPLE 7: Pareto Frontier Analysis
// ============================================================================

async function example7_paretoAnalysis() {
  console.log('\n=== Example 7: Pareto Frontier Analysis ===\n');

  const { TileChainBuilder, ParetoFrontierCalculator } = await import('../src/benchmarking/baseline-comparison.js');

  // Build multiple patterns
  const patterns = [
    TileChainBuilder.buildSequential('sentiment'),
    TileChainBuilder.buildParallel('sentiment'),
    TileChainBuilder.buildMixed('sentiment'),
  ];

  // Calculate metrics for each
  const results = patterns.map(pattern => ({
    approach: 'smp' as const,
    metrics: {
      ...TileChainBuilder.estimateMetrics(pattern),
      throughput: 1000 / TileChainBuilder.estimateMetrics(pattern).latency,
      memory: pattern.tiles.length * 50,
    },
    tilePattern: pattern,
  }));

  // Calculate Pareto frontier
  const frontier = ParetoFrontierCalculator.calculate(results);

  console.log(`Pareto Frontier: ${frontier.length} non-dominated solutions`);
  frontier.forEach((point, idx) => {
    console.log(`\nSolution ${idx + 1}:`);
    console.log(`  Latency: ${point.metrics.latency.toFixed(2)} ms`);
    console.log(`  Accuracy: ${(point.metrics.accuracy * 100).toFixed(1)}%`);
    console.log(`  Energy: ${point.metrics.energy.toFixed(2)} units`);
    console.log(`  Dominates: ${point.dominates.length} solutions`);
  });
}

// ============================================================================
// MAIN RUNNER
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  const example = args[0] || '1';

  try {
    switch (example) {
      case '1':
        await example1_sentiment();
        break;
      case '2':
        await example2_classification();
        break;
      case '3':
        await example3_reasoning();
        break;
      case '4':
        await example4_htmlReport();
        break;
      case '5':
        await example5_batch();
        break;
      case '6':
        await example6_customEngine();
        break;
      case '7':
        await example7_paretoAnalysis();
        break;
      case 'all':
        await example1_sentiment();
        await example2_classification();
        await example3_reasoning();
        await example5_batch();
        break;
      default:
        console.log(`
Usage: node baseline-comparison-example.ts [example]

Examples:
  1 - Sentiment analysis (default)
  2 - Document classification
  3 - Multi-step reasoning
  4 - Generate HTML report
  5 - Batch comparison
  6 - Custom comparison engine
  7 - Pareto frontier analysis
  all - Run all examples

Example:
  node baseline-comparison-example.ts 1
  node baseline-comparison-example.ts all
        `);
    }
  } catch (error) {
    console.error('Error running example:', error);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export {
  example1_sentiment,
  example2_classification,
  example3_reasoning,
  example4_htmlReport,
  example5_batch,
  example6_customEngine,
  example7_paretoAnalysis,
};
