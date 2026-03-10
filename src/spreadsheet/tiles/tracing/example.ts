/**
 * Tile Execution Tracer - Example Usage
 *
 * This file demonstrates how to use the Tile Execution Tracer
 * for debugging and profiling tile execution.
 */

import {
  TileTracer,
  Span,
  TraceExporter,
  traceTile,
  monitorPerformance,
  type TraceContext
} from './tile-tracer';

// ============================================================================
// Example 1: Basic Manual Tracing
// ============================================================================

async function basicExample() {
  console.log('\n=== Example 1: Basic Manual Tracing ===\n');

  const tracer = TileTracer.getInstance();

  // Configure tracer
  tracer.setSamplingRate(1.0); // 100% sampling
  tracer.setEnabled(true);

  // Start a root span
  const rootSpan = tracer.startSpan(
    'data-pipeline',
    'pipeline',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    }
  );

  // Add custom attributes
  rootSpan.setAttribute('pipeline.name', 'data-processing');
  rootSpan.setAttribute('pipeline.stage', 'transform');

  // Add events
  rootSpan.addEvent('pipeline-started', {
    inputSize: 1000,
    timestamp: Date.now()
  });

  // Simulate work
  await simulateWork(100);

  // Update confidence
  rootSpan.updateConfidence(0.95, 'processing-complete');

  // End span
  rootSpan.addEvent('pipeline-completed');
  tracer.endSpan(rootSpan.getContext().spanId, true);

  // Print statistics
  const stats = tracer.getStatistics();
  console.log('Statistics:', JSON.stringify(stats, null, 2));

  // Cleanup
  tracer.clear();
}

// ============================================================================
// Example 2: Nested Spans
// ============================================================================

async function nestedSpansExample() {
  console.log('\n=== Example 2: Nested Spans ===\n');

  const tracer = TileTracer.getInstance();

  // Root span: Data processing pipeline
  const root = tracer.startSpan(
    'process-data',
    'pipeline',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    }
  );

  root.addEvent('pipeline-started');

  // Child span: Validate input
  const validateSpan = tracer.startSpan(
    'validate-input',
    'validation',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    },
    tracer.getCurrentContext(root), // Pass parent context
    0.98
  );

  await simulateWork(50);
  validateSpan.updateConfidence(0.95, 'validation-passed');
  tracer.endSpan(validateSpan.getContext().spanId, true);

  // Child span: Transform data
  const transformSpan = tracer.startSpan(
    'transform-data',
    'transform',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    },
    tracer.getCurrentContext(root),
    0.95
  );

  await simulateWork(100);
  transformSpan.updateConfidence(0.88, 'transform-complete');
  tracer.endSpan(transformSpan.getContext().spanId, true);

  // Child span: Aggregate results
  const aggregateSpan = tracer.startSpan(
    'aggregate-results',
    'aggregation',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    },
    tracer.getCurrentContext(root),
    0.90
  );

  await simulateWork(75);
  aggregateSpan.updateConfidence(0.92, 'aggregation-complete');
  tracer.endSpan(aggregateSpan.getContext().spanId, true);

  // End root span
  root.addEvent('pipeline-completed');
  tracer.endSpan(root.getContext().spanId, true);

  // Print trace hierarchy
  const completed = tracer.getCompletedSpans();
  console.log(`\nTotal spans created: ${completed.length}`);
  console.log('Trace hierarchy:');
  for (const span of completed) {
    const metadata = (span as any).metadata;
    const perf = span.getPerformanceMetrics();
    const conf = span.getConfidenceMetrics();
    const indent = (span as any).context.parentSpanId ? '  ' : '';
    console.log(`${indent}- [${conf.zone}] ${metadata.tileType}: ${perf.duration?.toFixed(2)}ms`);
  }

  tracer.clear();
}

// ============================================================================
// Example 3: Decorator-Based Tracing
// ============================================================================

// Example tile classes with decorators
class DataTransformTile {
  @traceTile('transform', {
    initialConfidence: 0.95,
    recordArgs: true,
    recordResult: true
  })
  @monitorPerformance(500)
  async transform(input: number[]): Promise<{ result: number[]; confidence: number }> {
    await simulateWork(100);

    const result = input.map(x => x * 2);

    return {
      result,
      confidence: 0.92
    };
  }

  @traceTile('aggregate', {
    initialConfidence: 0.90,
    recordArgs: true
  })
  async aggregate(data: number[]): Promise<{ sum: number; avg: number; confidence: number }> {
    await simulateWork(50);

    const sum = data.reduce((a, b) => a + b, 0);
    const avg = sum / data.length;

    return {
      sum,
      avg,
      confidence: 0.88
    };
  }
}

class ValidationTile {
  @traceTile('validate', {
    initialConfidence: 0.98,
    recordArgs: true
  })
  @monitorPerformance(200)
  async validate(input: number[]): Promise<{ valid: boolean; confidence: number }> {
    await simulateWork(75);

    const valid = input.every(x => x >= 0 && x <= 100);

    return {
      valid,
      confidence: valid ? 0.95 : 0.40
    };
  }
}

async function decoratorExample() {
  console.log('\n=== Example 3: Decorator-Based Tracing ===\n');

  const transformTile = new DataTransformTile();
  const validationTile = new ValidationTile();

  // Execute tiles
  const input = [10, 20, 30, 40, 50];

  console.log('Validating input...');
  const validation = await validationTile.validate(input);
  console.log(`Validation result: ${validation.valid}, confidence: ${validation.confidence}`);

  console.log('\nTransforming data...');
  const transform = await transformTile.transform(input);
  console.log(`Transform result: [${transform.result}], confidence: ${transform.confidence}`);

  console.log('\nAggregating results...');
  const aggregate = await transformTile.aggregate(transform.result);
  console.log(`Aggregate: sum=${aggregate.sum}, avg=${aggregate.avg.toFixed(2)}, confidence=${aggregate.confidence}`);

  // Print trace statistics
  const tracer = TileTracer.getInstance();
  const stats = tracer.getStatistics();

  console.log('\n--- Trace Statistics ---');
  console.log(`Total spans: ${stats.totalSpans}`);
  console.log(`Active spans: ${stats.activeSpans}`);
  console.log(`Error rate: ${(stats.errorRate * 100).toFixed(1)}%`);
  console.log(`Average duration: ${stats.averageDuration.toFixed(2)}ms`);
  console.log(`Confidence distribution:`);
  console.log(`  GREEN: ${stats.confidenceDistribution.GREEN}`);
  console.log(`  YELLOW: ${stats.confidenceDistribution.YELLOW}`);
  console.log(`  RED: ${stats.confidenceDistribution.RED}`);

  tracer.clear();
}

// ============================================================================
// Example 4: Confidence Cascade Tracking
// ============================================================================

async function confidenceCascadeExample() {
  console.log('\n=== Example 4: Confidence Cascade Tracking ===\n');

  const tracer = TileTracer.getInstance();

  const span = tracer.startSpan(
    'multi-stage-process',
    'pipeline',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    },
    undefined,
    0.98 // Initial confidence
  );

  console.log('Initial confidence:', span.getConfidenceMetrics().current);

  // Stage 1: Input validation (slight degradation)
  await simulateWork(50);
  span.updateConfidence(0.95, 'input-validation');
  console.log('After validation:', span.getConfidenceMetrics().current);

  // Stage 2: Data transformation (more degradation)
  await simulateWork(100);
  span.updateConfidence(0.85, 'data-quality-issues');
  console.log('After transformation:', span.getConfidenceMetrics().current);

  // Stage 3: Complex calculation (further degradation)
  await simulateWork(75);
  span.updateConfidence(0.78, 'complex-calculation');
  console.log('After calculation:', span.getConfidenceMetrics().current);

  // Stage 4: Result validation (improvement!)
  await simulateWork(50);
  span.updateConfidence(0.88, 'result-verified');
  console.log('After verification:', span.getConfidenceMetrics().current);

  tracer.endSpan(span.getContext().spanId, true);

  // Print confidence history
  const history = span.getConfidenceMetrics().cascadeHistory;
  console.log('\nConfidence cascade history:');
  for (const entry of history) {
    const zone = entry.value >= 0.90 ? 'GREEN' : entry.value >= 0.75 ? 'YELLOW' : 'RED';
    console.log(`  [${zone}] ${entry.value.toFixed(2)} - ${entry.reason}`);
  }

  tracer.clear();
}

// ============================================================================
// Example 5: Pheromone Signal Detection
// ============================================================================

async function pheromoneExample() {
  console.log('\n=== Example 5: Pheromone Signal Detection ===\n');

  const tracer = TileTracer.getInstance();

  const span = tracer.startSpan(
    'coordinated-task',
    'task',
    {
      version: '1.0.0',
      cellCoordinates: 'Sheet1!A1'
    }
  );

  // Simulate detecting pheromone signals from neighboring cells
  console.log('Detecting pheromone signals...');

  span.logPheromone({
    type: 'coordination',
    sourceCell: 'A2',
    strength: 0.8,
    timestamp: Date.now()
  });
  console.log('  - Detected coordination signal from A2 (strength: 0.8)');

  await simulateWork(50);

  span.logPheromone({
    type: 'status-update',
    sourceCell: 'B1',
    strength: 0.6,
    timestamp: Date.now()
  });
  console.log('  - Detected status update from B1 (strength: 0.6)');

  await simulateWork(50);

  span.logPheromone({
    type: 'completion',
    sourceCell: 'A3',
    strength: 0.9,
    timestamp: Date.now()
  });
  console.log('  - Detected completion signal from A3 (strength: 0.9)');

  tracer.endSpan(span.getContext().spanId, true);

  // Print pheromone log
  const json = span.toJSON();
  console.log('\nPheromone signals detected:');
  for (const signal of json.pheromones) {
    console.log(`  - ${signal.type} from ${signal.sourceCell}: strength ${signal.strength}`);
  }

  tracer.clear();
}

// ============================================================================
// Example 6: Export to Jaeger/Zipkin
// ============================================================================

async function exportExample() {
  console.log('\n=== Example 6: Export to Jaeger/Zipkin ===\n');

  const tracer = TileTracer.getInstance();

  // Create some spans
  for (let i = 0; i < 5; i++) {
    const span = tracer.startSpan(
      `task-${i}`,
      'task',
      {
        version: '1.0.0',
        cellCoordinates: `A${i + 1}`
      }
    );

    await simulateWork(50);
    span.updateConfidence(0.90 - (i * 0.05), `task-${i}-complete`);
    tracer.endSpan(span.getContext().spanId, true);
  }

  // Export to JSON (file)
  console.log('Exporting to JSON file...');
  const exporter = TraceExporter.getInstance();
  exporter.export(tracer.getCompletedSpans());
  console.log('  ✓ Traces exported to .traces/ directory');

  // Export to Jaeger (if Jaeger is running)
  console.log('\nAttempting export to Jaeger...');
  console.log('  Note: This requires Jaeger to be running on localhost:14268');
  console.log('  Run: docker run -d -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one');

  try {
    await exporter.exportToJaeger(tracer.getCompletedSpans());
    console.log('  ✓ Traces exported to Jaeger');
    console.log('  View at: http://localhost:16686');
  } catch (error) {
    console.log('  ✗ Jaeger export failed (is Jaeger running?)');
  }

  // Export to Zipkin (if Zipkin is running)
  console.log('\nAttempting export to Zipkin...');
  console.log('  Note: This requires Zipkin to be running on localhost:9411');
  console.log('  Run: docker run -d -p 9411:9411 openzipkin/zipkin');

  try {
    await exporter.exportToZipkin(tracer.getCompletedSpans());
    console.log('  ✓ Traces exported to Zipkin');
    console.log('  View at: http://localhost:9411');
  } catch (error) {
    console.log('  ✗ Zipkin export failed (is Zipkin running?)');
  }

  tracer.clear();
}

// ============================================================================
// Example 7: Error Handling
// ============================================================================

async function errorHandlingExample() {
  console.log('\n=== Example 7: Error Handling ===\n');

  const tracer = TileTracer.getInstance();

  // Successful span
  const successSpan = tracer.startSpan(
    'successful-task',
    'task',
    { version: '1.0.0' }
  );

  await simulateWork(50);
  successSpan.addEvent('task-completed');
  tracer.endSpan(successSpan.getContext().spanId, true);
  console.log('✓ Successful task traced');

  // Failed span
  const errorSpan = tracer.startSpan(
    'failing-task',
    'task',
    { version: '1.0.0' }
  );

  await simulateWork(50);
  errorSpan.addEvent('task-failed', {
    error: 'Intentional error',
    code: 500
  });
  tracer.endSpan(errorSpan.getContext().spanId, false, 'Intentional error for demo');
  console.log('✓ Failed task traced with error');

  // Print error statistics
  const stats = tracer.getStatistics();
  console.log(`\nError rate: ${(stats.errorRate * 100).toFixed(1)}%`);
  console.log(`Total spans: ${stats.totalSpans}`);
  console.log(`Failed spans: ${stats.totalSpans - Math.round(stats.totalSpans * (1 - stats.errorRate))}`);

  tracer.clear();
}

// ============================================================================
// Helper Functions
// ============================================================================

async function simulateWork(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================================
// Run All Examples
// ============================================================================

async function runAllExamples() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║     Tile Execution Tracer - Example Usage               ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  await basicExample();
  await nestedSpansExample();
  await decoratorExample();
  await confidenceCascadeExample();
  await pheromoneExample();
  await exportExample();
  await errorHandlingExample();

  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║     All examples completed!                             ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
}

// Run examples if this file is executed directly
if (require.main === module) {
  runAllExamples().catch(console.error);
}

export {
  basicExample,
  nestedSpansExample,
  decoratorExample,
  confidenceCascadeExample,
  pheromoneExample,
  exportExample,
  errorHandlingExample,
  runAllExamples
};
