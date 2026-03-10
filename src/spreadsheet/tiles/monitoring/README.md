# Confidence Zone Monitor

**Real-time monitoring and alerting for the Three-Zone Confidence Model**

## Overview

The Zone Monitor provides comprehensive real-time monitoring, alerting, and metrics for confidence zones across individual tiles and tile chains. It implements the Three-Zone Model:

- **GREEN (0.90-1.00)**: Auto-proceed, full trust
- **YELLOW (0.75-0.89)**: Human review required
- **RED (0.00-0.74)**: Stop, diagnose critical issues

## Features

### Core Capabilities

- **Real-time Zone Tracking**: Monitor confidence scores and zone transitions
- **Alert System**: Configurable alerts via webhooks and callbacks
- **Historical Analysis**: Track zone transitions, violations, and trends
- **Chain Monitoring**: Composite confidence calculation for sequential tile chains
- **Metrics Export**: Prometheus-compatible metrics for observability
- **Violation Reporting**: Comprehensive violation analysis and reporting

### Advanced Features

- **Zone Propagation**: Track how zones change through tile chains
- **Confidence Cascade**: Multiply sequential confidences, average parallel
- **Transition Analysis**: Detect upgrades, downgrades, and escalations
- **Cooldown Management**: Prevent alert fatigue with intelligent cooldowns
- **Time-Series Queries**: Query history by tile, time range, and zone

## Architecture

```
ZoneMonitor (Main)
├── ZoneCalculator        # Zone calculations and transitions
├── Alerter               # Alert management and dispatch
├── ZoneHistory           # Historical data storage
├── MetricsExporter       # Prometheus/JSON metrics export
└── ChainState           # Tile chain monitoring
```

## Installation

```bash
# Add to your project
npm install @polln/zone-monitor
```

## Quick Start

### Basic Tile Monitoring

```typescript
import { ZoneMonitor } from './zone-monitor';

const monitor = new ZoneMonitor({
  thresholds: {
    green: 0.90,
    yellow: 0.75
  },
  alertConfig: {
    enabled: true,
    minSeverity: 'YELLOW'
  },
  onZoneChange: (tileId, transition) => {
    console.log(`${tileId}: ${transition.fromZone} -> ${transition.toZone}`);
  }
});

// Monitor a tile
await monitor.monitorTile('my-tile', 0.95); // GREEN
await monitor.monitorTile('my-tile', 0.82); // YELLOW (triggers alert)
await monitor.monitorTile('my-tile', 0.65); // RED (triggers alert)
```

### Chain Monitoring

```typescript
// Monitor sequential chain: A -> B -> C
const chainId = 'data-pipeline-1';
const tileIds = ['extract', 'transform', 'load'];
const confidences = new Map([
  ['extract', 0.95],
  ['transform', 0.88],
  ['load', 0.72]
]);

const chainState = await monitor.monitorChain(chainId, tileIds, confidences);

console.log('Composite confidence:', chainState.compositeConfidence);
console.log('Composite zone:', chainState.compositeZone);
console.log('Weakest tile:', chainState.weakestTile);
console.log('Violations:', chainState.violationCount);
```

### Alert Configuration

```typescript
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    webhookUrl: 'https://hooks.example.com/alerts',
    minSeverity: 'YELLOW',
    cooldownMs: 5000, // 5 seconds between alerts
    callback: (alert) => {
      console.log(`ALERT: ${alert.message}`);
      // Send to Slack, PagerDuty, etc.
    }
  }
});
```

### Metrics Export

```typescript
// Monitor tiles
await monitor.monitorTile('tile-1', 0.95);

// Export as Prometheus format
const prometheusMetrics = monitor.exportMetrics('prometheus');
console.log(prometheusMetrics);

// Output:
// # HELP confidence_zone_current Current confidence score
// # TYPE confidence_zone_current gauge
// confidence_zone_current{tile="tile-1"} 0.95
//
// # HELP zone_state Current zone state
// # TYPE zone_state gauge
// zone_state{tile="tile-1",zone="GREEN"} 1

// Export as JSON
const jsonMetrics = monitor.exportMetrics('json');
console.log(JSON.stringify(jsonMetrics, null, 2));
```

## API Reference

### ZoneMonitor

Main class for monitoring confidence zones.

#### Constructor Options

```typescript
interface ZoneMonitorOptions {
  thresholds?: {
    green?: number;    // Default: 0.90
    yellow?: number;   // Default: 0.75
  };
  alertConfig?: {
    enabled?: boolean;
    webhookUrl?: string;
    callback?: (alert: ZoneAlert) => void;
    minSeverity?: 'YELLOW' | 'RED';
    cooldownMs?: number;
  };
  maxHistoryEntries?: number;
  onZoneChange?: (tileId: string, transition: ZoneTransition) => void;
}
```

#### Methods

##### `monitorTile(tileId, confidence, chainPath?)`

Monitor a single tile's confidence.

```typescript
const state = await monitor.monitorTile('tile-1', 0.95);
// Returns: ZoneState | null
```

##### `monitorChain(chainId, tileIds, confidences)`

Monitor a sequential tile chain.

```typescript
const chainState = await monitor.monitorChain(
  'chain-1',
  ['tile-a', 'tile-b', 'tile-c'],
  new Map([
    ['tile-a', 0.95],
    ['tile-b', 0.88],
    ['tile-c', 0.72]
  ])
);
// Returns: ChainZoneState
```

##### `monitorBatch(tileConfidences)`

Monitor multiple tiles in batch.

```typescript
const results = await monitor.monitorBatch(
  new Map([
    ['tile-1', 0.95],
    ['tile-2', 0.82],
    ['tile-3', 0.65]
  ])
);
// Returns: Map<string, ZoneState>
```

##### `getTileState(tileId)`

Get current state for a tile.

```typescript
const state = monitor.getTileState('tile-1');
// Returns: ZoneState | undefined
```

##### `getTileMetrics(tileId)`

Get comprehensive metrics for a tile.

```typescript
const metrics = monitor.getTileMetrics('tile-1');
// Returns: ZoneMetrics
```

##### `getChainState(chainId)`

Get state for a chain.

```typescript
const chainState = monitor.getChainState('chain-1');
// Returns: ChainZoneState | undefined
```

##### `getTilesInZone(zone)`

Get all tiles in a specific zone.

```typescript
const redTiles = monitor.getTilesInZone('RED');
// Returns: string[]
```

##### `generateViolationReport()`

Generate comprehensive violation report.

```typescript
const report = monitor.generateViolationReport();
// Returns: ViolationReport
```

##### `queryHistory(filter?)`

Query historical data.

```typescript
const history = monitor.queryHistory({
  tileId: 'tile-1',
  startTime: Date.now() - 3600000,
  endTime: Date.now(),
  zone: 'RED'
});
// Returns: ZoneHistoryEntry[]
```

##### `exportMetrics(format?)`

Export metrics.

```typescript
const prometheus = monitor.exportMetrics('prometheus');
const json = monitor.exportMetrics('json');
```

### ZoneCalculator

Utility class for zone calculations.

```typescript
import { ZoneCalculator } from './zone-monitor';

const calc = new ZoneCalculator({ green: 0.90, yellow: 0.75 });

// Calculate zone from confidence
const zone = calc.calculateZone(0.82); // 'YELLOW'

// Sequential composite (multiply)
const composite = calc.calculateSequentialComposite([0.90, 0.80, 0.70]);
// Returns: 0.504 (0.90 * 0.80 * 0.70)

// Parallel composite (weighted average)
const parallel = calc.calculateParallelComposite(
  [0.90, 0.80],
  [1, 1]
);
// Returns: 0.85

// Transition type
const transition = calc.calculateTransition('GREEN', 'YELLOW');
// Returns: 'downgrade'

// Escalation check
const needsEscalation = calc.requiresEscalation('YELLOW', 'RED');
// Returns: true

// Distance to boundary
const distance = calc.distanceToBoundary(0.85, 'GREEN');
// Returns: 0.05
```

### Alerter

Alert management and dispatch.

```typescript
import { Alerter } from './zone-monitor';

const alerter = new Alerter({
  enabled: true,
  webhookUrl: 'https://hooks.example.com/alerts',
  minSeverity: 'YELLOW',
  cooldownMs: 5000,
  callback: (alert) => {
    console.log(`Alert: ${alert.message}`);
  }
});

// Check and fire alert
const alert = await alerter.checkAlert(tileId, transition);
```

### ZoneHistory

Historical data storage and analysis.

```typescript
import { ZoneHistory } from './zone-monitor';

const history = new ZoneHistory(10000); // max entries

// Record state
history.record(zoneState);

// Query tile history
const tileHistory = history.getTileHistory('tile-1');

// Get transitions
const transitions = history.getTransitions('tile-1');

// Zone distribution
const distribution = history.getZoneDistribution('tile-1');
// Returns: { GREEN: 5, YELLOW: 3, RED: 2 }

// Average confidence
const avg = history.getAverageConfidence('tile-1');

// Violation count
const violations = history.getViolationCount('tile-1');

// Violation rate
const rate = history.getViolationRate('tile-1');
```

## Use Cases

### 1. Real-time Monitoring Dashboard

```typescript
const monitor = new ZoneMonitor();

// Update dashboard in real-time
setInterval(async () => {
  const tiles = await getCurrentTileConfidences();
  await monitor.monitorBatch(tiles);

  const globalMetrics = monitor.getGlobalMetrics();
  updateDashboard(globalMetrics);
}, 1000);
```

### 2. Alerting System

```typescript
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    webhookUrl: process.env.SLACK_WEBHOOK_URL,
    callback: (alert) => {
      if (alert.severity === 'CRITICAL') {
        // Send to PagerDuty
        sendToPagerDuty(alert);
      }
    }
  }
});
```

### 3. Pipeline Monitoring

```typescript
// Monitor data pipeline
const pipeline = ['extract', 'validate', 'transform', 'load'];

setInterval(async () => {
  const confidences = new Map();
  for (const stage of pipeline) {
    confidences.set(stage, await getStageConfidence(stage));
  }

  const state = await monitor.monitorChain(
    'etl-pipeline',
    pipeline,
    confidences
  );

  if (state.compositeZone === 'RED') {
    console.error('Pipeline in critical state!');
    console.log('Weakest stage:', state.weakestTile);
  }
}, 5000);
```

### 4. Historical Analysis

```typescript
// Analyze trends over time
const monitor = new ZoneMonitor();

// After collecting data...
const last24h = Date.now() - 24 * 60 * 60 * 1000;
const recentHistory = monitor.queryHistory({
  startTime: last24h
});

// Calculate trends
const redZoneTrend = recentHistory.filter(e => e.zone === 'RED').length;
console.log(`RED zone occurrences in last 24h: ${redZoneTrend}`);
```

### 5. Prometheus Integration

```typescript
import express from 'express';
import { ZoneMonitor } from './zone-monitor';

const app = express();
const monitor = new ZoneMonitor();

// Expose metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain');
  res.send(monitor.exportMetrics('prometheus'));
});

app.listen(9090, () => {
  console.log('Metrics endpoint available on :9090/metrics');
});
```

## Metrics Reference

### Confidence Metrics

```
# Current confidence score
confidence_zone_current{tile="tile-1"} 0.95

# Average confidence
confidence_avg{tile="tile-1"} 0.87
```

### Zone State Metrics

```
# Current zone (1 if in zone)
zone_state{tile="tile-1",zone="GREEN"} 1
zone_state{tile="tile-1",zone="YELLOW"} 0
zone_state{tile="tile-1",zone="RED"} 0
```

### Zone Distribution Metrics

```
# Count of times in each zone
zone_distribution{tile="tile-1",zone="GREEN"} 45
zone_distribution{tile="tile-1",zone="YELLOW"} 12
zone_distribution{tile="tile-1",zone="RED"} 3
```

### Violation Metrics

```
# Total violations
violations_total{tile="tile-1"} 15

# Time in current zone (seconds)
zone_time_seconds{tile="tile-1",zone="GREEN"} 3600
```

## Configuration Examples

### Strict Thresholds

```typescript
const monitor = new ZoneMonitor({
  thresholds: {
    green: 0.95,  // Higher bar for GREEN
    yellow: 0.85  // Higher bar for YELLOW
  }
});
```

### Lenient Thresholds

```typescript
const monitor = new ZoneMonitor({
  thresholds: {
    green: 0.85,  // Lower bar for GREEN
    yellow: 0.70  // Lower bar for YELLOW
  }
});
```

### Aggressive Alerting

```typescript
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    minSeverity: 'YELLOW',  // Alert on YELLOW
    cooldownMs: 1000        // Short cooldown
  }
});
```

### Conservative Alerting

```typescript
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    minSeverity: 'RED',     // Only alert on RED
    cooldownMs: 30000       // Long cooldown
  }
});
```

## Testing

Run the test suite:

```bash
npm test
```

Example test output:

```
Running Zone Monitor Tests...

✓ ZoneCalculator: GREEN zone for high confidence
✓ ZoneCalculator: YELLOW zone for medium confidence
✓ ZoneCalculator: RED zone for low confidence
✓ ZoneCalculator: Sequential composite multiplies
✓ ZoneCalculator: Parallel composite averages
✓ Alerter: Fires on zone downgrade
✓ Alerter: Respects cooldown
✓ ZoneHistory: Records and retrieves entries
✓ ZoneHistory: Tracks transitions
✓ ZoneMonitor: Monitors single tile
✓ ZoneMonitor: Detects zone transitions
✓ ZoneMonitor: Calculates tile metrics
✓ ZoneMonitor: Monitors tile chain
✓ ZoneMonitor: Generates violation report

Results: 14 passed, 0 failed
```

## Performance Considerations

### Memory Usage

- Default history: 10,000 entries
- Adjust with `maxHistoryEntries` constructor option
- Use `clearHistory()` to free memory

### Alert Cooldowns

- Prevent alert fatigue with appropriate `cooldownMs`
- Default: 5,000ms (5 seconds)
- Adjust based on your monitoring frequency

### Batch Operations

- Use `monitorBatch()` for multiple tiles
- More efficient than individual `monitorTile()` calls

## Best Practices

1. **Set appropriate thresholds** for your use case
2. **Configure alert cooldowns** to prevent fatigue
3. **Use batch operations** for multiple tiles
4. **Export metrics regularly** for observability
5. **Review violation reports** to identify patterns
6. **Query historical data** for trend analysis
7. **Test alert configurations** before production

## License

MIT

## Contributing

Contributions welcome! Please submit pull requests to the main repository.

## Support

For issues and questions, please open a GitHub issue.
