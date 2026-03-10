/**
 * ZONE MONITOR TEST SUITE
 *
 * Comprehensive tests for ZoneMonitor functionality
 */

import {
  ZoneMonitor,
  ZoneCalculator,
  Alerter,
  ZoneHistory,
  MetricsExporter,
  type ZoneState,
  type ZoneTransition,
  type ConfidenceZone
} from './zone-monitor';

// ============================================================================
// TEST UTILITIES
// ============================================================================

class TestRunner {
  private tests: Array<{ name: string; fn: () => void | Promise<void> }> = [];
  private passed = 0;
  private failed = 0;

  test(name: string, fn: () => void | Promise<void>) {
    this.tests.push({ name, fn });
  }

  async run() {
    console.log('Running Zone Monitor Tests...\n');

    for (const { name, fn } of this.tests) {
      try {
        await fn();
        this.passed++;
        console.log(`✓ ${name}`);
      } catch (error) {
        this.failed++;
        console.error(`✗ ${name}`);
        console.error(`  Error: ${error}`);
      }
    }

    console.log(`\nResults: ${this.passed} passed, ${this.failed} failed`);
    return this.failed === 0;
  }
}

const runner = new TestRunner();

// ============================================================================
// ZONE CALCULATOR TESTS
// ============================================================================

runner.test('ZoneCalculator: GREEN zone for high confidence', () => {
  const calc = new ZoneCalculator();
  const zone = calc.calculateZone(0.95);
  if (zone !== 'GREEN') throw new Error(`Expected GREEN, got ${zone}`);
});

runner.test('ZoneCalculator: YELLOW zone for medium confidence', () => {
  const calc = new ZoneCalculator();
  const zone = calc.calculateZone(0.82);
  if (zone !== 'YELLOW') throw new Error(`Expected YELLOW, got ${zone}`);
});

runner.test('ZoneCalculator: RED zone for low confidence', () => {
  const calc = new ZoneCalculator();
  const zone = calc.calculateZone(0.65);
  if (zone !== 'RED') throw new Error(`Expected RED, got ${zone}`);
});

runner.test('ZoneCalculator: Sequential composite multiplies', () => {
  const calc = new ZoneCalculator();
  const confidences = [0.90, 0.80, 0.70];
  const composite = calc.calculateSequentialComposite(confidences);
  const expected = 0.90 * 0.80 * 0.70;
  if (Math.abs(composite - expected) > 0.0001) {
    throw new Error(`Expected ${expected}, got ${composite}`);
  }
});

runner.test('ZoneCalculator: Parallel composite averages', () => {
  const calc = new ZoneCalculator();
  const confidences = [0.90, 0.80];
  const weights = [1, 1];
  const composite = calc.calculateParallelComposite(confidences, weights);
  const expected = (0.90 + 0.80) / 2;
  if (Math.abs(composite - expected) > 0.0001) {
    throw new Error(`Expected ${expected}, got ${composite}`);
  }
});

runner.test('ZoneCalculator: Detects downgrade transitions', () => {
  const calc = new ZoneCalculator();
  const transition = calc.calculateTransition('GREEN', 'YELLOW');
  if (transition !== 'downgrade') throw new Error(`Expected downgrade, got ${transition}`);
});

runner.test('ZoneCalculator: Detects upgrade transitions', () => {
  const calc = new ZoneCalculator();
  const transition = calc.calculateTransition('RED', 'YELLOW');
  if (transition !== 'upgrade') throw new Error(`Expected upgrade, got ${transition}`);
});

runner.test('ZoneCalculator: Escalation on RED zone', () => {
  const calc = new ZoneCalculator();
  if (!calc.requiresEscalation('YELLOW', 'RED')) {
    throw new Error('Should require escalation to RED');
  }
});

runner.test('ZoneCalculator: Distance to GREEN boundary', () => {
  const calc = new ZoneCalculator();
  const distance = calc.distanceToBoundary(0.85, 'GREEN');
  if (distance !== 0.05) throw new Error(`Expected 0.05, got ${distance}`);
});

// ============================================================================
// ALERTER TESTS
// ============================================================================

runner.test('Alerter: Fires on zone downgrade', async () => {
  const alerts: any[] = [];
  const alerter = new Alerter({
    enabled: true,
    callback: (alert) => alerts.push(alert),
    cooldownMs: 0
  });

  const transition: ZoneTransition = {
    fromZone: 'GREEN',
    toZone: 'YELLOW',
    confidence: 0.82,
    timestamp: Date.now(),
    tileId: 'test-tile',
    transitionType: 'downgrade'
  };

  const alert = await alerter.checkAlert('test-tile', transition);
  if (!alert) throw new Error('Expected alert to fire');
  if (alert.severity !== 'WARNING') throw new Error(`Expected WARNING, got ${alert.severity}`);
});

runner.test('Alerter: Respects cooldown', async () => {
  let alertCount = 0;
  const alerter = new Alerter({
    enabled: true,
    callback: () => alertCount++,
    cooldownMs: 1000
  });

  const transition: ZoneTransition = {
    fromZone: 'GREEN',
    toZone: 'YELLOW',
    confidence: 0.82,
    timestamp: Date.now(),
    tileId: 'test-tile',
    transitionType: 'downgrade'
  };

  await alerter.checkAlert('test-tile', transition);
  await alerter.checkAlert('test-tile', transition);

  if (alertCount !== 1) throw new Error(`Expected 1 alert, got ${alertCount}`);
});

runner.test('Alerter: Respects minSeverity', async () => {
  const alerter = new Alerter({
    enabled: true,
    minSeverity: 'RED',
    cooldownMs: 0
  });

  const transition: ZoneTransition = {
    fromZone: 'GREEN',
    toZone: 'YELLOW',
    confidence: 0.82,
    timestamp: Date.now(),
    tileId: 'test-tile',
    transitionType: 'downgrade'
  };

  const alert = await alerter.checkAlert('test-tile', transition);
  if (alert !== null) throw new Error('Expected no alert for YELLOW when minSeverity is RED');
});

// ============================================================================
// ZONE HISTORY TESTS
// ============================================================================

runner.test('ZoneHistory: Records and retrieves entries', () => {
  const history = new ZoneHistory();
  const state: ZoneState = {
    zone: 'GREEN',
    confidence: 0.95,
    timestamp: Date.now(),
    tileId: 'test-tile'
  };

  history.record(state);
  const entries = history.getTileHistory('test-tile');

  if (entries.length !== 1) throw new Error(`Expected 1 entry, got ${entries.length}`);
  if (entries[0].zone !== 'GREEN') throw new Error(`Expected GREEN, got ${entries[0].zone}`);
});

runner.test('ZoneHistory: Tracks transitions', () => {
  const history = new ZoneHistory();
  const now = Date.now();

  history.record({
    zone: 'GREEN',
    confidence: 0.95,
    timestamp: now - 2000,
    tileId: 'test-tile'
  });

  history.record({
    zone: 'YELLOW',
    confidence: 0.82,
    timestamp: now - 1000,
    tileId: 'test-tile'
  });

  history.record({
    zone: 'RED',
    confidence: 0.65,
    timestamp: now,
    tileId: 'test-tile'
  });

  const transitions = history.getTransitions('test-tile');

  if (transitions.length !== 2) throw new Error(`Expected 2 transitions, got ${transitions.length}`);
  if (transitions[0].fromZone !== 'GREEN' || transitions[0].toZone !== 'YELLOW') {
    throw new Error('First transition incorrect');
  }
});

runner.test('ZoneHistory: Calculates zone distribution', () => {
  const history = new ZoneHistory();

  for (let i = 0; i < 5; i++) {
    history.record({
      zone: 'GREEN',
      confidence: 0.95,
      timestamp: Date.now(),
      tileId: 'test-tile'
    });
  }

  for (let i = 0; i < 3; i++) {
    history.record({
      zone: 'YELLOW',
      confidence: 0.82,
      timestamp: Date.now(),
      tileId: 'test-tile'
    });
  }

  const distribution = history.getZoneDistribution('test-tile');

  if (distribution.GREEN !== 5) throw new Error(`Expected 5 GREEN, got ${distribution.GREEN}`);
  if (distribution.YELLOW !== 3) throw new Error(`Expected 3 YELLOW, got ${distribution.YELLOW}`);
});

runner.test('ZoneHistory: Calculates violation count', () => {
  const history = new ZoneHistory();

  for (let i = 0; i < 5; i++) {
    history.record({
      zone: 'GREEN',
      confidence: 0.95,
      timestamp: Date.now(),
      tileId: 'test-tile'
    });
  }

  for (let i = 0; i < 3; i++) {
    history.record({
      zone: 'YELLOW',
      confidence: 0.82,
      timestamp: Date.now(),
      tileId: 'test-tile'
    });
  }

  const violations = history.getViolationCount('test-tile');

  if (violations !== 3) throw new Error(`Expected 3 violations, got ${violations}`);
});

// ============================================================================
// METRICS EXPORTER TESTS
// ============================================================================

runner.test('MetricsExporter: Updates and exports metrics', () => {
  const exporter = new MetricsExporter();

  const state: ZoneState = {
    zone: 'GREEN',
    confidence: 0.95,
    timestamp: Date.now(),
    tileId: 'test-tile'
  };

  exporter.update('test-tile', state);
  const metrics = exporter.exportJson();

  if (!metrics['confidence_zone_current{tile="test-tile"}']) {
    throw new Error('Expected confidence metric');
  }

  const value = metrics['confidence_zone_current{tile="test-tile"}'];
  if (value !== '0.95') throw new Error(`Expected 0.95, got ${value}`);
});

runner.test('MetricsExporter: Exports Prometheus format', () => {
  const exporter = new MetricsExporter();

  const state: ZoneState = {
    zone: 'GREEN',
    confidence: 0.95,
    timestamp: Date.now(),
    tileId: 'test-tile'
  };

  exporter.update('test-tile', state);
  const prometheus = exporter.exportPrometheus();

  if (!prometheus.includes('confidence_zone_current{tile="test-tile"} 0.95')) {
    throw new Error('Expected Prometheus format with correct value');
  }

  if (!prometheus.includes('# HELP')) {
    throw new Error('Expected HELP comments');
  }

  if (!prometheus.includes('# TYPE')) {
    throw new Error('Expected TYPE comments');
  }
});

// ============================================================================
// ZONE MONITOR INTEGRATION TESTS
// ============================================================================

runner.test('ZoneMonitor: Monitors single tile', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  const state = await monitor.monitorTile('test-tile', 0.95);

  if (!state) throw new Error('Expected state to be returned');
  if (state.zone !== 'GREEN') throw new Error(`Expected GREEN, got ${state.zone}`);
  if (state.confidence !== 0.95) throw new Error(`Expected 0.95, got ${state.confidence}`);
});

runner.test('ZoneMonitor: Detects zone transitions', async () => {
  let transitionDetected = false;
  const monitor = new ZoneMonitor({
    alertConfig: { enabled: false },
    onZoneChange: (tileId, transition) => {
      if (tileId === 'test-tile' && transition.toZone === 'YELLOW') {
        transitionDetected = true;
      }
    }
  });

  await monitor.monitorTile('test-tile', 0.95);
  await monitor.monitorTile('test-tile', 0.82);

  if (!transitionDetected) throw new Error('Expected zone change callback');
});

runner.test('ZoneMonitor: Calculates tile metrics', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('test-tile', 0.95);
  await monitor.monitorTile('test-tile', 0.82);
  await monitor.monitorTile('test-tile', 0.65);

  const metrics = monitor.getTileMetrics('test-tile');

  if (metrics.currentZone !== 'RED') throw new Error(`Expected RED, got ${metrics.currentZone}`);
  if (metrics.transitionCount !== 2) throw new Error(`Expected 2 transitions, got ${metrics.transitionCount}`);
  if (metrics.violationCount !== 2) throw new Error(`Expected 2 violations, got ${metrics.violationCount}`);
});

runner.test('ZoneMonitor: Monitors tile chain', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  const tileIds = ['tile-a', 'tile-b', 'tile-c'];
  const confidences = new Map([
    ['tile-a', 0.95],
    ['tile-b', 0.88],
    ['tile-c', 0.72]
  ]);

  const chainState = await monitor.monitorChain('chain-1', tileIds, confidences);

  if (chainState.compositeZone !== 'RED') {
    throw new Error(`Expected RED composite zone, got ${chainState.compositeZone}`);
  }

  // 0.95 * 0.88 * 0.72 = 0.60288
  if (chainState.compositeConfidence < 0.60 || chainState.compositeConfidence > 0.61) {
    throw new Error(`Composite confidence out of range: ${chainState.compositeConfidence}`);
  }

  if (chainState.violationCount !== 1) {
    throw new Error(`Expected 1 violation, got ${chainState.violationCount}`);
  }
});

runner.test('ZoneMonitor: Batch monitoring', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  const confidences = new Map<string, number>([
    ['tile-1', 0.95],
    ['tile-2', 0.82],
    ['tile-3', 0.65]
  ]);

  const results = await monitor.monitorBatch(confidences);

  if (results.size !== 3) throw new Error(`Expected 3 results, got ${results.size}`);
});

runner.test('ZoneMonitor: Gets tiles in zone', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('tile-1', 0.95);
  await monitor.monitorTile('tile-2', 0.82);
  await monitor.monitorTile('tile-3', 0.65);

  const redTiles = monitor.getTilesInZone('RED');
  const yellowTiles = monitor.getTilesInZone('YELLOW');
  const greenTiles = monitor.getTilesInZone('GREEN');

  if (redTiles.length !== 1 || redTiles[0] !== 'tile-3') {
    throw new Error('Expected tile-3 in RED zone');
  }

  if (yellowTiles.length !== 1 || yellowTiles[0] !== 'tile-2') {
    throw new Error('Expected tile-2 in YELLOW zone');
  }

  if (greenTiles.length !== 1 || greenTiles[0] !== 'tile-1') {
    throw new Error('Expected tile-1 in GREEN zone');
  }
});

runner.test('ZoneMonitor: Generates violation report', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('tile-1', 0.95);
  await monitor.monitorTile('tile-2', 0.82);
  await monitor.monitorTile('tile-3', 0.65);

  const report = monitor.generateViolationReport();

  if (report.violations.length !== 2) {
    throw new Error(`Expected 2 violating tiles, got ${report.violations.length}`);
  }

  if (report.summary.tilesWithViolations !== 2) {
    throw new Error(`Expected 2 tiles with violations, got ${report.summary.tilesWithViolations}`);
  }

  if (report.summary.criticalViolations !== 1) {
    throw new Error(`Expected 1 critical violation, got ${report.summary.criticalViolations}`);
  }
});

runner.test('ZoneMonitor: Queries history', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('tile-1', 0.95);
  await monitor.monitorTile('tile-1', 0.82);

  const history = monitor.queryHistory({ tileId: 'tile-1' });

  if (history.length !== 2) throw new Error(`Expected 2 history entries, got ${history.length}`);
});

runner.test('ZoneMonitor: Exports metrics', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('tile-1', 0.95);

  const prometheus = monitor.exportMetrics('prometheus');

  if (!prometheus.includes('confidence_zone_current{tile="tile-1"}')) {
    throw new Error('Expected tile-1 in Prometheus export');
  }

  const json = monitor.exportMetrics('json');
  const parsed = JSON.parse(json);

  if (!parsed['confidence_zone_current{tile="tile-1"}']) {
    throw new Error('Expected tile-1 in JSON export');
  }
});

runner.test('ZoneMonitor: Gets global metrics', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('tile-1', 0.95);
  await monitor.monitorTile('tile-2', 0.82);
  await monitor.monitorTile('tile-3', 0.65);

  const globalMetrics = monitor.getGlobalMetrics();

  if (globalMetrics.totalTiles !== 3) {
    throw new Error(`Expected 3 total tiles, got ${globalMetrics.totalTiles}`);
  }

  if (globalMetrics.avgConfidence <= 0 || globalMetrics.avgConfidence > 1) {
    throw new Error(`Average confidence out of range: ${globalMetrics.avgConfidence}`);
  }
});

runner.test('ZoneMonitor: Reset functionality', async () => {
  const monitor = new ZoneMonitor({ alertConfig: { enabled: false } });

  await monitor.monitorTile('tile-1', 0.95);
  monitor.clearStates();

  const state = monitor.getTileState('tile-1');

  if (state !== undefined) {
    throw new Error('Expected state to be cleared');
  }
});

// ============================================================================
// RUN ALL TESTS
// ============================================================================

if (require.main === module) {
  runner.run().then(success => {
    process.exit(success ? 0 : 1);
  });
}

export { runner };
