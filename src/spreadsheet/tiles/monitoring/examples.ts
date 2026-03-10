/**
 * ZONE MONITOR COMPREHENSIVE EXAMPLES
 *
 * Complete demonstrations of all ZoneMonitor features
 */

import {
  ZoneMonitor,
  ZoneCalculator,
  Alerter,
  ZoneHistory,
  MetricsExporter,
  type ZoneState,
  type ZoneTransition,
  type ZoneAlert,
  type ChainZoneState
} from './zone-monitor';

// ============================================================================
// EXAMPLE 1: BASIC TILE MONITORING
// ============================================================================

export async function example1_BasicMonitoring() {
  console.log('\n=== Example 1: Basic Tile Monitoring ===\n');

  const monitor = new ZoneMonitor({
    thresholds: {
      green: 0.90,
      yellow: 0.75
    },
    onZoneChange: (tileId, transition) => {
      console.log(`  Zone Change: ${tileId} ${transition.fromZone} -> ${transition.toZone}`);
    }
  });

  // Monitor tiles
  console.log('Monitoring tiles:');
  await monitor.monitorTile('classifier', 0.95);
  console.log('  classifier: GREEN (0.95)');

  await monitor.monitorTile('validator', 0.82);
  console.log('  validator: YELLOW (0.82)');

  await monitor.monitorTile('transformer', 0.65);
  console.log('  transformer: RED (0.65)');

  // Get current states
  console.log('\nCurrent states:');
  const tiles = ['classifier', 'validator', 'transformer'];
  for (const tile of tiles) {
    const state = monitor.getTileState(tile);
    console.log(`  ${tile}: ${state?.zone} (${state?.confidence.toFixed(3)})`);
  }
}

// ============================================================================
// EXAMPLE 2: CHAIN MONITORING
// ============================================================================

export async function example2_ChainMonitoring() {
  console.log('\n=== Example 2: Chain Monitoring ===\n');

  const monitor = new ZoneMonitor();

  // Define a data pipeline chain
  const pipelineChain = 'etl-pipeline';
  const pipelineStages = ['extract', 'validate', 'transform', 'load'];
  const stageConfidences = new Map([
    ['extract', 0.95],
    ['validate', 0.88],
    ['transform', 0.92],
    ['load', 0.78]
  ]);

  console.log('Monitoring ETL pipeline:');
  console.log('  Stages: extract -> validate -> transform -> load');
  console.log('  Confidences:');
  for (const [stage, conf] of stageConfidences) {
    console.log(`    ${stage}: ${conf.toFixed(3)}`);
  }

  const chainState = await monitor.monitorChain(
    pipelineChain,
    pipelineStages,
    stageConfidences
  );

  console.log('\nChain analysis:');
  console.log(`  Composite confidence: ${chainState.compositeConfidence.toFixed(4)}`);
  console.log(`  Composite zone: ${chainState.compositeZone}`);
  console.log(`  Weakest tile: ${chainState.weakestTile}`);
  console.log(`  Violations: ${chainState.violationCount}`);

  // Show individual tile states
  console.log('\nIndividual tile states:');
  for (const tile of pipelineStages) {
    const state = monitor.getTileState(tile);
    console.log(`  ${tile}: ${state?.zone} (${state?.confidence.toFixed(3)})`);
  }
}

// ============================================================================
// EXAMPLE 3: ALERT CONFIGURATION
// ============================================================================

export async function example3_AlertConfiguration() {
  console.log('\n=== Example 3: Alert Configuration ===\n');

  const alerts: ZoneAlert[] = [];

  const monitor = new ZoneMonitor({
    alertConfig: {
      enabled: true,
      minSeverity: 'YELLOW',
      cooldownMs: 1000,
      callback: (alert) => {
        console.log(`  ALERT [${alert.severity}]: ${alert.message}`);
        alerts.push(alert);
      }
    }
  });

  console.log('Triggering alerts:');

  // Simulate confidence degradation
  const confidences = [0.95, 0.92, 0.88, 0.82, 0.78, 0.65, 0.50];
  for (const conf of confidences) {
    await monitor.monitorTile('critical-service', conf);
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  console.log(`\nTotal alerts fired: ${alerts.length}`);
  console.log(`Alerts by severity:`);
  const bySeverity = alerts.reduce((acc, alert) => {
    acc[alert.severity] = (acc[alert.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  for (const [severity, count] of Object.entries(bySeverity)) {
    console.log(`  ${severity}: ${count}`);
  }
}

// ============================================================================
// EXAMPLE 4: WEBHOOK INTEGRATION
// ============================================================================

export async function example4_WebhookIntegration() {
  console.log('\n=== Example 4: Webhook Integration ===\n');

  // Mock webhook handler
  const webhookAlerts: any[] = [];
  const mockWebhookUrl = 'https://hooks.example.com/alerts';

  const monitor = new ZoneMonitor({
    alertConfig: {
      enabled: true,
      webhookUrl: mockWebhookUrl,
      minSeverity: 'RED',
      callback: (alert) => {
        // Simulate webhook call
        webhookAlerts.push({
          url: mockWebhookUrl,
          payload: alert,
          timestamp: Date.now()
        });
        console.log(`  Webhook called: ${mockWebhookUrl}`);
        console.log(`  Payload: ${JSON.stringify(alert, null, 2).split('\n').join('\n  ')}`);
      }
    }
  });

  console.log('Simulating critical events:');
  await monitor.monitorTile('database', 0.72);
  console.log('  Database confidence dropped to 0.72 (RED)');

  await monitor.monitorTile('cache', 0.68);
  console.log('  Cache confidence dropped to 0.68 (RED)');

  console.log(`\nTotal webhook calls: ${webhookAlerts.length}`);
}

// ============================================================================
// EXAMPLE 5: HISTORICAL ANALYSIS
// ============================================================================

export async function example5_HistoricalAnalysis() {
  console.log('\n=== Example 5: Historical Analysis ===\n');

  const monitor = new ZoneMonitor();

  // Simulate time series data
  console.log('Generating time series data...');
  const tileId = 'time-series-tile';

  for (let i = 0; i < 50; i++) {
    // Simulate confidence fluctuation
    const baseConfidence = 0.85;
    const noise = (Math.random() - 0.5) * 0.2;
    const confidence = Math.max(0, Math.min(1, baseConfidence + noise));

    await monitor.monitorTile(tileId, confidence);

    // Small delay between updates
    await new Promise(resolve => setTimeout(resolve, 10));
  }

  console.log('Historical analysis:');

  // Get tile metrics
  const metrics = monitor.getTileMetrics(tileId);
  console.log(`  Current zone: ${metrics.currentZone}`);
  console.log(`  Current confidence: ${metrics.currentConfidence.toFixed(3)}`);
  console.log(`  Average confidence: ${metrics.avgConfidence.toFixed(3)}`);
  console.log(`  Total transitions: ${metrics.transitionCount}`);
  console.log(`  Violation count: ${metrics.violationCount}`);
  console.log(`  Time in current zone: ${(metrics.timeInCurrentZone / 1000).toFixed(1)}s`);

  // Zone distribution
  console.log('\n  Zone distribution:');
  for (const [zone, count] of Object.entries(metrics.zoneDistribution)) {
    const pct = (count / 50 * 100).toFixed(1);
    console.log(`    ${zone}: ${count} (${pct}%)`);
  }

  // Transitions
  const transitions = monitor.queryHistory({ tileId });
  const zoneChanges = transitions.filter((e, i, arr) =>
    i === 0 ? false : e.zone !== arr[i - 1].zone
  );

  console.log(`\n  Zone changes: ${zoneChanges.length}`);
  for (const change of zoneChanges.slice(-5)) {
    console.log(`    ${new Date(change.timestamp).toISOString()}: ${change.zone}`);
  }
}

// ============================================================================
// EXAMPLE 6: VIOLATION REPORTING
// ============================================================================

export async function example6_ViolationReporting() {
  console.log('\n=== Example 6: Violation Reporting ===\n');

  const monitor = new ZoneMonitor();

  // Monitor multiple tiles
  const tiles = new Map<string, number>([
    ['service-a', 0.95],
    ['service-b', 0.82],
    ['service-c', 0.65],
    ['service-d', 0.78],
    ['service-e', 0.92],
    ['service-f', 0.55]
  ]);

  console.log('Monitoring services:');
  for (const [tile, conf] of tiles) {
    await monitor.monitorTile(tile, conf);
    console.log(`  ${tile}: ${conf.toFixed(3)}`);
  }

  // Generate violation report
  const report = monitor.generateViolationReport();

  console.log('\nViolation Report:');
  console.log(`  Timestamp: ${new Date(report.timestamp).toISOString()}`);
  console.log(`  Total tiles with violations: ${report.violations.length}`);
  console.log(`  Total violations: ${report.summary.totalViolations}`);
  console.log(`  Critical violations (RED): ${report.summary.criticalViolations}`);

  console.log('\nViolating tiles:');
  for (const violation of report.violations) {
    console.log(`  ${violation.tileId}:`);
    console.log(`    Zone: ${violation.currentZone}`);
    console.log(`    Confidence: ${violation.confidence.toFixed(3)}`);
    console.log(`    Violations: ${violation.violationCount}`);
    console.log(`    Violation rate: ${(violation.violationRate * 100).toFixed(1)}%`);
  }
}

// ============================================================================
// EXAMPLE 7: BATCH MONITORING
// ============================================================================

export async function example7_BatchMonitoring() {
  console.log('\n=== Example 7: Batch Monitoring ===\n');

  const monitor = new ZoneMonitor();

  // Generate random tiles
  const tileCount = 20;
  const confidences = new Map<string, number>();

  console.log(`Generating ${tileCount} random tiles...`);
  for (let i = 1; i <= tileCount; i++) {
    const confidence = 0.5 + Math.random() * 0.5;
    confidences.set(`tile-${i}`, confidence);
  }

  // Batch monitor
  console.log('Batch monitoring...');
  const startTime = Date.now();
  const results = await monitor.monitorBatch(confidences);
  const elapsed = Date.now() - startTime;

  console.log(`Monitored ${results.size} tiles in ${elapsed}ms`);

  // Get tiles by zone
  const greenTiles = monitor.getTilesInZone('GREEN');
  const yellowTiles = monitor.getTilesInZone('YELLOW');
  const redTiles = monitor.getTilesInZone('RED');

  console.log('\nZone distribution:');
  console.log(`  GREEN: ${greenTiles.length}`);
  console.log(`  YELLOW: ${yellowTiles.length}`);
  console.log(`  RED: ${redTiles.length}`);

  // Show some examples from each zone
  console.log('\nExample tiles:');
  if (greenTiles.length > 0) {
    const tile = greenTiles[0];
    const state = monitor.getTileState(tile);
    console.log(`  GREEN: ${tile} (${state?.confidence.toFixed(3)})`);
  }
  if (yellowTiles.length > 0) {
    const tile = yellowTiles[0];
    const state = monitor.getTileState(tile);
    console.log(`  YELLOW: ${tile} (${state?.confidence.toFixed(3)})`);
  }
  if (redTiles.length > 0) {
    const tile = redTiles[0];
    const state = monitor.getTileState(tile);
    console.log(`  RED: ${tile} (${state?.confidence.toFixed(3)})`);
  }
}

// ============================================================================
// EXAMPLE 8: METRICS EXPORT
// ============================================================================

export async function example8_MetricsExport() {
  console.log('\n=== Example 8: Metrics Export ===\n');

  const monitor = new ZoneMonitor();

  // Monitor some tiles
  await monitor.monitorTile('tile-1', 0.95);
  await monitor.monitorTile('tile-2', 0.82);
  await monitor.monitorTile('tile-3', 0.65);

  console.log('Prometheus metrics:');
  console.log('---');
  const prometheusMetrics = monitor.exportMetrics('prometheus');
  console.log(prometheusMetrics);
  console.log('---');

  console.log('\nJSON metrics:');
  console.log('---');
  const jsonMetrics = monitor.exportMetrics('json');
  console.log(jsonMetrics);
  console.log('---');
}

// ============================================================================
// EXAMPLE 9: GLOBAL METRICS
// ============================================================================

export async function example9_GlobalMetrics() {
  console.log('\n=== Example 9: Global Metrics ===\n');

  const monitor = new ZoneMonitor();

  // Monitor many tiles
  const tiles = ['service-a', 'service-b', 'service-c', 'service-d', 'service-e',
                 'service-f', 'service-g', 'service-h', 'service-i', 'service-j'];

  for (const tile of tiles) {
    const confidence = 0.6 + Math.random() * 0.4;
    await monitor.monitorTile(tile, confidence);
  }

  // Get global metrics
  const globalMetrics = monitor.getGlobalMetrics();

  console.log('Global Metrics:');
  console.log(`  Total tiles: ${globalMetrics.totalTiles}`);
  console.log(`  Average confidence: ${globalMetrics.avgConfidence.toFixed(3)}`);
  console.log(`  Violation rate: ${(globalMetrics.violationRate * 100).toFixed(1)}%`);
  console.log(`  Chains with violations: ${globalMetrics.chainsWithViolations}`);

  console.log('\nZone distribution:');
  for (const [zone, count] of Object.entries(globalMetrics.zoneDistribution)) {
    console.log(`  ${zone}: ${count}`);
  }
}

// ============================================================================
// EXAMPLE 10: ADVANCED CHAIN ANALYSIS
// ============================================================================

export async function example10_AdvancedChainAnalysis() {
  console.log('\n=== Example 10: Advanced Chain Analysis ===\n');

  const monitor = new ZoneMonitor();

  // Define multiple chains
  const chains = [
    {
      id: 'ml-pipeline',
      tiles: ['data-ingest', 'preprocess', 'model-inference', 'postprocess'],
      confidences: new Map([
        ['data-ingest', 0.95],
        ['preprocess', 0.88],
        ['model-inference', 0.92],
        ['postprocess', 0.85]
      ])
    },
    {
      id: 'api-gateway',
      tiles: ['auth', 'rate-limit', 'proxy', 'cache'],
      confidences: new Map([
        ['auth', 0.98],
        ['rate-limit', 0.95],
        ['proxy', 0.78],
        ['cache', 0.72]
      ])
    },
    {
      id: 'data-pipeline',
      tiles: ['extract', 'transform', 'load'],
      confidences: new Map([
        ['extract', 0.92],
        ['transform', 0.85],
        ['load', 0.80]
      ])
    }
  ];

  console.log('Monitoring multiple chains...\n');

  for (const chain of chains) {
    const state = await monitor.monitorChain(
      chain.id,
      chain.tiles,
      chain.confidences
    );

    console.log(`${chain.id}:`);
    console.log(`  Composite confidence: ${state.compositeConfidence.toFixed(4)}`);
    console.log(`  Composite zone: ${state.compositeZone}`);
    console.log(`  Weakest tile: ${state.weakestTile}`);
    console.log(`  Violations: ${state.violationCount}`);

    // Show tile breakdown
    for (const tile of chain.tiles) {
      const tileState = monitor.getTileState(tile);
      console.log(`    ${tile}: ${tileState?.zone} (${tileState?.confidence.toFixed(3)})`);
    }
    console.log();
  }

  // Get chains with violations
  const violatingChains = monitor.getChainsWithViolations();
  console.log(`Chains with violations: ${violatingChains.length}`);
  for (const chain of violatingChains) {
    console.log(`  ${chain.chainId}: ${chain.violationCount} violations`);
  }
}

// ============================================================================
// EXAMPLE 11: CUSTOM THRESHOLDS
// ============================================================================

export async function example11_CustomThresholds() {
  console.log('\n=== Example 11: Custom Thresholds ===\n');

  // Strict monitor
  const strictMonitor = new ZoneMonitor({
    thresholds: {
      green: 0.95,
      yellow: 0.85
    }
  });

  // Lenient monitor
  const lenientMonitor = new ZoneMonitor({
    thresholds: {
      green: 0.85,
      yellow: 0.70
    }
  });

  const testConfidence = 0.88;

  console.log(`Testing confidence: ${testConfidence}\n`);

  await strictMonitor.monitorTile('test', testConfidence);
  const strictState = strictMonitor.getTileState('test');

  await lenientMonitor.monitorTile('test', testConfidence);
  const lenientState = lenientMonitor.getTileState('test');

  console.log('Strict thresholds (GREEN: 0.95, YELLOW: 0.85):');
  console.log(`  Zone: ${strictState?.zone}`);

  console.log('\nLenient thresholds (GREEN: 0.85, YELLOW: 0.70):');
  console.log(`  Zone: ${lenientState?.zone}`);
}

// ============================================================================
// EXAMPLE 12: QUERY HISTORY
// ============================================================================

export async function example12_QueryHistory() {
  console.log('\n=== Example 12: Query History ===\n');

  const monitor = new ZoneMonitor();

  // Generate historical data
  console.log('Generating historical data...');
  for (let i = 0; i < 20; i++) {
    await monitor.monitorTile('tile-a', 0.7 + Math.random() * 0.3);
    await monitor.monitorTile('tile-b', 0.6 + Math.random() * 0.4);
    await new Promise(resolve => setTimeout(resolve, 10));
  }

  // Query by tile
  console.log('\nHistory for tile-a:');
  const tileAHistory = monitor.queryHistory({ tileId: 'tile-a' });
  console.log(`  Total entries: ${tileAHistory.length}`);

  const recentA = tileAHistory.slice(-3);
  console.log('  Recent entries:');
  for (const entry of recentA) {
    console.log(`    ${entry.zone} (${entry.confidence.toFixed(3)})`);
  }

  // Query by zone
  console.log('\nRED zone entries:');
  const redEntries = monitor.queryHistory({ zone: 'RED' });
  console.log(`  Total RED entries: ${redEntries.length}`);

  // Query by time range
  const now = Date.now();
  const lastSecond = monitor.queryHistory({
    startTime: now - 1000,
    endTime: now
  });
  console.log(`\nEntries in last second: ${lastSecond.length}`);
}

// ============================================================================
// RUN ALL EXAMPLES
// ============================================================================

export async function runAllExamples() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║     ZONE MONITOR - COMPREHENSIVE EXAMPLES               ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  const examples = [
    example1_BasicMonitoring,
    example2_ChainMonitoring,
    example3_AlertConfiguration,
    example4_WebhookIntegration,
    example5_HistoricalAnalysis,
    example6_ViolationReporting,
    example7_BatchMonitoring,
    example8_MetricsExport,
    example9_GlobalMetrics,
    example10_AdvancedChainAnalysis,
    example11_CustomThresholds,
    example12_QueryHistory
  ];

  for (const example of examples) {
    try {
      await example();
    } catch (error) {
      console.error(`Error in ${example.name}:`, error);
    }
  }

  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║     ALL EXAMPLES COMPLETE                                ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
}

// Run examples if executed directly
if (require.main === module) {
  runAllExamples().catch(console.error);
}

export * from './examples';
