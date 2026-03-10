# Zone Monitor - Quick Reference

## Import

```typescript
import { ZoneMonitor } from './zone-monitor';
```

## Basic Usage

```typescript
// Create monitor
const monitor = new ZoneMonitor({
  thresholds: { green: 0.90, yellow: 0.75 },
  alertConfig: { enabled: true }
});

// Monitor tile
await monitor.monitorTile('tile-id', 0.95);

// Get state
const state = monitor.getTileState('tile-id');
console.log(state.zone); // 'GREEN', 'YELLOW', or 'RED'
```

## Core Concepts

### Zones
- **GREEN** (0.90-1.00): Auto-proceed
- **YELLOW** (0.75-0.89): Review required
- **RED** (0.00-0.74): Stop, diagnose

### Chain Monitoring
- **Sequential**: Confidence multiplies (0.90 × 0.80 = 0.72)
- **Parallel**: Confidence averages (weighted)

## Key Methods

### Monitoring
```typescript
await monitor.monitorTile(tileId, confidence);
await monitor.monitorChain(chainId, tileIds, confidences);
await monitor.monitorBatch(confidencesMap);
```

### Querying
```typescript
monitor.getTileState(tileId);
monitor.getTileMetrics(tileId);
monitor.getChainState(chainId);
monitor.getTilesInZone('RED');
```

### Analysis
```typescript
monitor.generateViolationReport();
monitor.queryHistory({ tileId, startTime, endTime, zone });
monitor.getGlobalMetrics();
```

### Export
```typescript
monitor.exportMetrics('prometheus');
monitor.exportMetrics('json');
```

## Alert Configuration

```typescript
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    webhookUrl: 'https://hooks.example.com/alert',
    minSeverity: 'YELLOW',
    cooldownMs: 5000,
    callback: (alert) => {
      console.log(alert.message);
    }
  }
});
```

## Common Patterns

### Monitor Spreadsheet Cell
```typescript
async function updateCell(cellId: string, value: any) {
  const confidence = calculateConfidence(value);
  await monitor.monitorTile(cellId, confidence);

  const state = monitor.getTileState(cellId);
  cell.setZoneIndicator(state.zone);
}
```

### Monitor Data Pipeline
```typescript
const pipeline = ['extract', 'transform', 'load'];
const confs = new Map([
  ['extract', 0.95],
  ['transform', 0.88],
  ['load', 0.72]
]);

const state = await monitor.monitorChain('etl', pipeline, confs);
if (state.compositeZone === 'RED') {
  console.error('Pipeline failed!');
}
```

### Slack Alerts
```typescript
monitor.setAlertConfig({
  callback: async (alert) => {
    await fetch(webhookUrl, {
      method: 'POST',
      body: JSON.stringify({
        text: `Zone Alert: ${alert.message}`
      })
    });
  }
});
```

### Prometheus Export
```typescript
import express from 'express';
const app = express();

app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain');
  res.send(monitor.exportMetrics('prometheus'));
});
```

## Metrics

### Confidence Metrics
```
confidence_zone_current{tile="tile-1"} 0.95
confidence_avg{tile="tile-1"} 0.87
```

### Zone Metrics
```
zone_state{tile="tile-1",zone="GREEN"} 1
zone_distribution{tile="tile-1",zone="GREEN"} 45
```

### Violation Metrics
```
violations_total{tile="tile-1"} 15
zone_time_seconds{tile="tile-1",zone="GREEN"} 3600
```

## Zone Transitions

```typescript
monitor.setZoneChangeCallback((tileId, transition) => {
  console.log(`${tileId}: ${transition.fromZone} -> ${transition.toZone}`);

  if (transition.transitionType === 'downgrade') {
    console.log('CONFIDENCE DROPPED!');
  }

  if (transition.toZone === 'RED') {
    console.log('CRITICAL!');
  }
});
```

## Configuration Examples

### Strict Thresholds
```typescript
new ZoneMonitor({
  thresholds: { green: 0.95, yellow: 0.85 }
});
```

### Lenient Thresholds
```typescript
new ZoneMonitor({
  thresholds: { green: 0.85, yellow: 0.70 }
});
```

### Aggressive Alerting
```typescript
new ZoneMonitor({
  alertConfig: {
    enabled: true,
    minSeverity: 'YELLOW',
    cooldownMs: 1000
  }
});
```

### Conservative Alerting
```typescript
new ZoneMonitor({
  alertConfig: {
    enabled: true,
    minSeverity: 'RED',
    cooldownMs: 30000
  }
});
```

## Quick Start Checklist

- [ ] Import ZoneMonitor
- [ ] Set thresholds (optional, defaults: 0.90/0.75)
- [ ] Configure alerts (optional)
- [ ] Start monitoring tiles
- [ ] Query states/metrics
- [ ] Export metrics
- [ ] Set up integrations (Slack, Prometheus, etc.)

## Files

- `zone-monitor.ts` - Main implementation
- `zone-monitor.test.ts` - Test suite
- `examples.ts` - 12 code examples
- `README.md` - Full documentation
- `INTEGRATION_GUIDE.md` - Production integration
- `IMPLEMENTATION_SUMMARY.md` - Technical details

## Support

See:
- `README.md` for full API reference
- `examples.ts` for code examples
- `INTEGRATION_GUIDE.md` for production setup
- `zone-monitor.test.ts` for usage patterns
