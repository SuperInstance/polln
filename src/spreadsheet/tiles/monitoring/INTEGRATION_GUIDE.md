# Zone Monitor Integration Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Spreadsheet Integration](#spreadsheet-integration)
3. [Tile Integration](#tile-integration)
4. [Alert System Integration](#alert-system-integration)
5. [Monitoring Dashboard](#monitoring-dashboard)
6. [Prometheus Integration](#prometheus-integration)
7. [Production Deployment](#production-deployment)

## Quick Start

### Basic Setup

```typescript
import { ZoneMonitor } from './zone-monitor';

const monitor = new ZoneMonitor({
  thresholds: { green: 0.90, yellow: 0.75 },
  alertConfig: { enabled: true }
});

// Start monitoring
await monitor.monitorTile('my-tile', 0.95);
```

## Spreadsheet Integration

### Cell-Level Monitoring

Monitor individual cells for confidence violations:

```typescript
import { ZoneMonitor } from './zone-monitor';

class SpreadsheetMonitor {
  private monitor: ZoneMonitor;

  constructor() {
    this.monitor = new ZoneMonitor({
      alertConfig: {
        enabled: true,
        callback: (alert) => {
          // Highlight violating cells in spreadsheet
          this.highlightCell(alert.tileId, alert.zone);
        }
      }
    });
  }

  // Monitor cell after calculation
  async monitorCell(cellId: string, confidence: number) {
    await this.monitor.monitorTile(cellId, confidence);

    // Get current state
    const state = this.monitor.getTileState(cellId);

    // Update cell visualization
    this.updateCellVisualization(cellId, state?.zone);
  }

  // Update cell based on zone
  private updateCellVisualization(cellId: string, zone?: string) {
    const cell = getCell(cellId);

    switch (zone) {
      case 'GREEN':
        cell.setBackgroundColor('#00ff00');
        cell.setBorder('2px solid #008000');
        break;
      case 'YELLOW':
        cell.setBackgroundColor('#ffff00');
        cell.setBorder('2px solid #ffaa00');
        break;
      case 'RED':
        cell.setBackgroundColor('#ff0000');
        cell.setBorder('2px solid #8b0000');
        break;
    }
  }

  // Highlight violating cell
  private highlightCell(cellId: string, zone: string) {
    if (zone === 'RED') {
      // Flash animation for critical violations
      flashCell(cellId, 'red');
    }
  }
}
```

### Dependency Chain Monitoring

Monitor chains of dependent cells:

```typescript
class DependencyChainMonitor {
  private monitor: ZoneMonitor;

  constructor() {
    this.monitor = new ZoneMonitor();
  }

  // Analyze dependency chain
  async monitorDependencyChain(startCell: string) {
    // Get dependency graph
    const dependencies = getDependencyGraph(startCell);

    // Get confidences for all cells in chain
    const confidences = new Map<string, number>();
    for (const cell of dependencies) {
      const confidence = getCellConfidence(cell);
      confidences.set(cell, confidence);
    }

    // Monitor chain
    const chainState = await this.monitor.monitorChain(
      `chain-${startCell}`,
      dependencies,
      confidences
    );

    // Display chain metrics
    this.displayChainMetrics(chainState);
  }

  private displayChainMetrics(chainState: any) {
    console.log(`Chain: ${chainState.chainId}`);
    console.log(`Composite confidence: ${chainState.compositeConfidence.toFixed(4)}`);
    console.log(`Weakest link: ${chainState.weakestTile}`);

    // Highlight weakest cell
    highlightCell(chainState.weakestTile, 'orange');
  }
}
```

## Tile Integration

### Tile-Level Monitoring

Integrate monitoring into tile execution:

```typescript
import { ZoneMonitor } from './zone-monitor';

class MonitoredTile {
  private monitor: ZoneMonitor;
  private tileId: string;

  constructor(tileId: string, monitor: ZoneMonitor) {
    this.tileId = tileId;
    this.monitor = monitor;
  }

  // Execute tile with monitoring
  async execute(input: any): Promise<any> {
    const startTime = Date.now();

    try {
      // Execute tile logic
      const result = await this.executeTile(input);

      // Calculate confidence
      const confidence = this.calculateConfidence(result);

      // Monitor result
      await this.monitor.monitorTile(this.tileId, confidence);

      return result;
    } catch (error) {
      // Low confidence on error
      await this.monitor.monitorTile(this.tileId, 0.0);
      throw error;
    }
  }

  private async executeTile(input: any): Promise<any> {
    // Tile-specific logic here
    return input;
  }

  private calculateConfidence(result: any): number {
    // Tile-specific confidence calculation
    return 0.95;
  }
}
```

### Tile Chain Monitoring

Monitor tiles in sequence:

```typescript
class TileChainExecutor {
  private monitor: ZoneMonitor;

  constructor(monitor: ZoneMonitor) {
    this.monitor = monitor;
  }

  async executeChain(tiles: MonitoredTile[]): Promise<any[]> {
    const results: any[] = [];
    const tileIds = tiles.map(t => t.getTileId());
    const confidences = new Map<string, number>();

    // Execute tiles sequentially
    let input = null;
    for (const tile of tiles) {
      const result = await tile.execute(input);
      results.push(result);

      // Get confidence
      const state = this.monitor.getTileState(tile.getTileId());
      if (state) {
        confidences.set(tile.getTileId(), state.confidence);
      }

      input = result;
    }

    // Monitor chain
    const chainState = await this.monitor.monitorChain(
      `chain-${Date.now()}`,
      tileIds,
      confidences
    );

    // Check if chain is healthy
    if (chainState.compositeZone === 'RED') {
      throw new Error(`Chain failed: ${chainState.weakestTile} is critical`);
    }

    return results;
  }
}
```

## Alert System Integration

### Slack Alerts

```typescript
class SlackAlerter {
  private webhookUrl: string;

  constructor(webhookUrl: string) {
    this.webhookUrl = webhookUrl;
  }

  async sendAlert(alert: any): Promise<void> {
    const message = this.formatSlackMessage(alert);

    await fetch(this.webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(message)
    });
  }

  private formatSlackMessage(alert: any): any {
    const color = {
      'INFO': '#36a64f',
      'WARNING': '#ff9900',
      'CRITICAL': '#ff0000'
    }[alert.severity];

    return {
      attachments: [{
        color,
        title: `Zone Alert: ${alert.tileId}`,
        text: alert.message,
        fields: [
          { title: 'Zone', value: alert.zone, short: true },
          { title: 'Confidence', value: alert.confidence.toFixed(3), short: true },
          { title: 'Severity', value: alert.severity, short: true },
          { title: 'Time', value: new Date(alert.timestamp).toISOString(), short: true }
        ]
      }]
    };
  }
}

// Usage
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    callback: async (alert) => {
      const slackAlerter = new SlackAlerter(process.env.SLACK_WEBHOOK_URL!);
      await slackAlerter.sendAlert(alert);
    }
  }
});
```

### PagerDuty Alerts

```typescript
class PagerDutyAlerter {
  private apiKey: string;
  private integrationKey: string;

  constructor(apiKey: string, integrationKey: string) {
    this.apiKey = apiKey;
    this.integrationKey = integrationKey;
  }

  async sendCriticalAlert(alert: any): Promise<void> {
    if (alert.severity !== 'CRITICAL') return;

    await fetch('https://events.pagerduty.com/v2/enqueue', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token token=${this.apiKey}`
      },
      body: JSON.stringify({
        routing_key: this.integrationKey,
        event_action: 'trigger',
        payload: {
          summary: alert.message,
          severity: 'critical',
          source: alert.tileId,
          custom_details: {
            zone: alert.zone,
            confidence: alert.confidence
          }
        }
      })
    });
  }
}

// Usage
const monitor = new ZoneMonitor({
  alertConfig: {
    enabled: true,
    minSeverity: 'RED',
    callback: async (alert) => {
      const pdAlerter = new PagerDutyAlerter(
        process.env.PAGERDUTY_API_KEY!,
        process.env.PAGERDUTY_INTEGRATION_KEY!
      );
      await pdAlerter.sendCriticalAlert(alert);
    }
  }
});
```

## Monitoring Dashboard

### Real-time Dashboard

```typescript
import express from 'express';
import { ZoneMonitor } from './zone-monitor';

class DashboardServer {
  private app: express.Application;
  private monitor: ZoneMonitor;

  constructor(monitor: ZoneMonitor) {
    this.app = express();
    this.monitor = monitor;
    this.setupRoutes();
  }

  private setupRoutes() {
    // Serve dashboard HTML
    this.app.get('/', (req, res) => {
      res.send(this.getDashboardHTML());
    });

    // API: Current states
    this.app.get('/api/states', (req, res) => {
      const states = Array.from(this.monitor['currentStates'].values());
      res.json(states);
    });

    // API: Global metrics
    this.app.get('/api/metrics', (req, res) => {
      const metrics = this.monitor.getGlobalMetrics();
      res.json(metrics);
    });

    // API: Violation report
    this.app.get('/api/violations', (req, res) => {
      const report = this.monitor.generateViolationReport();
      res.json(report);
    });

    // API: Tiles in zone
    this.app.get('/api/tiles/:zone', (req, res) => {
      const zone = req.params.zone as 'GREEN' | 'YELLOW' | 'RED';
      const tiles = this.monitor.getTilesInZone(zone);
      res.json({ zone, tiles });
    });

    // SSE: Real-time updates
    this.app.get('/api/stream', (req, res) => {
      res.setHeader('Content-Type', 'text/event-stream');

      // Send updates every second
      const interval = setInterval(async () => {
        const metrics = this.monitor.getGlobalMetrics();
        res.write(`data: ${JSON.stringify(metrics)}\n\n`);
      }, 1000);

      req.on('close', () => clearInterval(interval));
    });
  }

  private getDashboardHTML(): string {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Zone Monitor Dashboard</title>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
            .metric-card { padding: 20px; border-radius: 8px; text-align: center; }
            .green { background: #d4edda; color: #155724; }
            .yellow { background: #fff3cd; color: #856404; }
            .red { background: #f8d7da; color: #721c24; }
            .chart-container { margin-top: 20px; height: 300px; }
          </style>
        </head>
        <body>
          <h1>Zone Monitor Dashboard</h1>

          <div class="metrics">
            <div class="metric-card green">
              <h2>GREEN</h2>
              <div id="green-count">0</div>
            </div>
            <div class="metric-card yellow">
              <h2>YELLOW</h2>
              <div id="yellow-count">0</div>
            </div>
            <div class="metric-card red">
              <h2>RED</h2>
              <div id="red-count">0</div>
            </div>
            <div class="metric-card">
              <h2>Avg Confidence</h2>
              <div id="avg-conf">0.00</div>
            </div>
          </div>

          <div class="chart-container">
            <canvas id="zoneChart"></canvas>
          </div>

          <script>
            const ctx = document.getElementById('zoneChart').getContext('2d');
            const chart = new Chart(ctx, {
              type: 'line',
              data: {
                labels: [],
                datasets: [{
                  label: 'Average Confidence',
                  data: [],
                  borderColor: 'rgb(75, 192, 192)',
                  tension: 0.1
                }]
              },
              options: {
                scales: {
                  y: { min: 0, max: 1 }
                }
              }
            });

            const eventSource = new EventSource('/api/stream');
            eventSource.onmessage = (event) => {
              const metrics = JSON.parse(event.data);

              document.getElementById('green-count').textContent = metrics.zoneDistribution.GREEN;
              document.getElementById('yellow-count').textContent = metrics.zoneDistribution.YELLOW;
              document.getElementById('red-count').textContent = metrics.zoneDistribution.RED;
              document.getElementById('avg-conf').textContent = metrics.avgConfidence.toFixed(3);

              // Update chart
              const now = new Date().toLocaleTimeString();
              chart.data.labels.push(now);
              chart.data.datasets[0].data.push(metrics.avgConfidence);

              if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
              }

              chart.update();
            };
          </script>
        </body>
      </html>
    `;
  }

  start(port: number) {
    this.app.listen(port, () => {
      console.log(`Dashboard server running on port ${port}`);
      console.log(`Visit http://localhost:${port} to view dashboard`);
    });
  }
}

// Usage
const monitor = new ZoneMonitor();
const dashboard = new DashboardServer(monitor);
dashboard.start(3000);
```

## Prometheus Integration

### Metrics Endpoint

```typescript
import express from 'express';
import { ZoneMonitor } from './zone-monitor';

class PrometheusServer {
  private app: express.Application;
  private monitor: ZoneMonitor;

  constructor(monitor: ZoneMonitor) {
    this.app = express();
    this.monitor = monitor;
    this.setupRoutes();
  }

  private setupRoutes() {
    // Prometheus metrics endpoint
    this.app.get('/metrics', (req, res) => {
      res.set('Content-Type', 'text/plain');
      res.send(this.monitor.exportMetrics('prometheus'));
    });
  }

  start(port: number) {
    this.app.listen(port, () => {
      console.log(`Prometheus metrics available on port ${port}/metrics`);
    });
  }
}

// Usage
const monitor = new ZoneMonitor();
const prometheusServer = new PrometheusServer(monitor);
prometheusServer.start(9090);
```

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'zone-monitor'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Zone Monitor",
    "panels": [
      {
        "title": "Current Confidence by Tile",
        "targets": [
          {
            "expr": "confidence_zone_current"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Zone Distribution",
        "targets": [
          {
            "expr": "zone_state"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Total Violations",
        "targets": [
          {
            "expr": "sum(violations_total)"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

## Production Deployment

### Environment Configuration

```typescript
// config.ts
export const config = {
  zoneMonitor: {
    thresholds: {
      green: parseFloat(process.env.ZONE_GREEN_THRESHOLD || '0.90'),
      yellow: parseFloat(process.env.ZONE_YELLOW_THRESHOLD || '0.75')
    },
    alert: {
      enabled: process.env.ALERT_ENABLED === 'true',
      slack: {
        webhookUrl: process.env.SLACK_WEBHOOK_URL
      },
      pagerDuty: {
        apiKey: process.env.PAGERDUTY_API_KEY,
        integrationKey: process.env.PAGERDUTY_INTEGRATION_KEY
      }
    },
    history: {
      maxEntries: parseInt(process.env.MAX_HISTORY_ENTRIES || '10000')
    }
  }
};
```

### Monitoring Service

```typescript
class MonitoringService {
  private monitor: ZoneMonitor;

  constructor() {
    this.monitor = new ZoneMonitor({
      thresholds: config.zoneMonitor.thresholds,
      alertConfig: config.zoneMonitor.alert,
      maxHistoryEntries: config.zoneMonitor.history.maxEntries
    });

    this.setupAlertIntegrations();
  }

  private setupAlertIntegrations() {
    this.monitor.setAlertConfig({
      callback: async (alert) => {
        if (alert.severity === 'CRITICAL') {
          await this.sendToPagerDuty(alert);
        }
        await this.sendToSlack(alert);
      }
    });
  }

  private async sendToSlack(alert: any) {
    // Send to Slack
  }

  private async sendToPagerDuty(alert: any) {
    // Send to PagerDuty
  }

  async monitorTile(tileId: string, confidence: number) {
    return await this.monitor.monitorTile(tileId, confidence);
  }

  getMetrics() {
    return this.monitor.getGlobalMetrics();
  }

  exportMetrics(format: 'prometheus' | 'json' = 'prometheus') {
    return this.monitor.exportMetrics(format);
  }
}
```

### Health Check Endpoint

```typescript
import express from 'express';

class HealthCheckServer {
  private app: express.Application;
  private monitoringService: MonitoringService;

  constructor(monitoringService: MonitoringService) {
    this.app = express();
    this.monitoringService = monitoringService;
    this.setupRoutes();
  }

  private setupRoutes() {
    this.app.get('/health', (req, res) => {
      const metrics = this.monitoringService.getMetrics();
      const isHealthy = metrics.violationRate < 0.5;

      res.status(isHealthy ? 200 : 503).json({
        status: isHealthy ? 'healthy' : 'unhealthy',
        metrics,
        timestamp: new Date().toISOString()
      });
    });
  }

  start(port: number) {
    this.app.listen(port, () => {
      console.log(`Health check server running on port ${port}`);
    });
  }
}
```

This integration guide provides comprehensive examples for integrating the Zone Monitor into various systems and deployments.
