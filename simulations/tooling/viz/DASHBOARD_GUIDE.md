# POLLN Real-Time Dashboard Guide

Complete guide to using the POLLN real-time metrics dashboard.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Dashboard Components](#dashboard-components)
5. [Configuration](#configuration)
6. [Metrics Explained](#metrics-explained)
7. [Alerts](#alerts)
8. [Export and Sharing](#export-and-sharing)
9. [Troubleshooting](#troubleshooting)

## Overview

The POLLN Real-Time Dashboard provides live monitoring of system performance, resource usage, and agent behavior. It features auto-refreshing plots, configurable alerts, and both interactive and exportable views.

### Key Features

- **Live Monitoring**: Real-time updates (configurable interval)
- **Comprehensive Metrics**: Performance, resources, and learning
- **Alert System**: Configurable thresholds with notifications
- **Historical Views**: Track metrics over time
- **Export Options**: Save snapshots and HTML dashboards

## Installation

### Requirements

```bash
# Core dependencies
pip install numpy matplotlib seaborn

# Optional: For HTML export
pip install plotly

# Optional: For animations
pip install ffmpeg-python
```

### Quick Install

```bash
cd simulations/tooling/viz
pip install -r requirements.txt
```

## Quick Start

### Basic Dashboard

```python
from metrics_dashboard import MetricsDashboard, SystemMetrics
import time
import numpy as np

# Create dashboard
dashboard = MetricsDashboard(
    update_interval=1.0,    # Update every second
    history_window=300      # Show 5 minutes of history
)

# Define metrics source
def fetch_system_metrics():
    # Replace with your actual metrics source
    return SystemMetrics(
        timestamp=time.time(),
        throughput=50.0 + np.random.normal(0, 5),
        avg_latency=100.0 + np.random.normal(0, 20),
        p95_latency=150.0,
        p99_latency=200.0,
        error_rate=1.0,
        cpu_usage=50.0,
        memory_usage=60.0,
        network_usage=10.0,
        active_agents=15,
        total_agents=20,
        queued_tasks=5,
        completed_tasks=1000,
        avg_value=0.7,
        avg_reward=5.0,
        convergence_rate=0.01
    )

# Set callback
dashboard.set_metrics_callback(fetch_system_metrics)

# Start dashboard (opens window)
dashboard.start()
```

### Export to HTML

```python
# Export dashboard without opening window
dashboard = MetricsDashboard()
dashboard.set_metrics_callback(fetch_system_metrics)

# Collect some data
for _ in range(60):
    time.sleep(1)
    # Metrics collected automatically

# Export
dashboard.export_html("dashboard.html")
```

## Dashboard Components

### Performance Metrics

#### Throughput Panel
- **What**: Requests processed per second
- **Target**: > 10 req/s
- **Alert if**: Below minimum threshold

#### Latency Panel
- **What**: Average, P95, and P99 response times
- **Target**: < 500ms avg, < 1000ms P99
- **Alert if**: Above threshold

#### Error Rate Panel
- **What**: Percentage of failed requests
- **Target**: < 5%
- **Alert if**: Above threshold

#### Task Queue Panel
- **What**: Queued vs completed tasks
- **Shows**: System backlog and throughput
- **Alert if**: Queue growing continuously

### Resource Metrics

#### CPU Usage
- **What**: Percentage CPU utilization
- **Target**: < 90%
- **Alert if**: Sustained high usage

#### Memory Usage
- **What**: Percentage memory utilization
- **Target**: < 90%
- **Alert if**: Critical (>= 90%)

#### Network Usage
- **What**: Network throughput in MB/s
- **Target**: Baseline dependent
- **Monitor**: Sudden changes

#### Active Agents
- **What**: Number of active agents
- **Shows**: System scale
- **Monitor**: Unexpected changes

### Learning Metrics

#### Average Value
- **What**: TD(λ) value predictions
- **Target**: Increasing trend
- **Monitor**: Convergence and stability

#### Average Reward
- **What**: Recent reward accumulation
- **Target**: Increasing trend
- **Monitor**: Performance improvement

#### Convergence Rate
- **What**: Rate of value function change
- **Target**: Stabilizing near zero
- **Monitor**: Learning progress

### Alerts Panel

Displays recent system alerts with severity:
- **INFO**: Informational
- **WARNING**: Caution warranted
- **ERROR**: Error condition
- **CRITICAL**: Immediate attention needed

## Configuration

### Dashboard Settings

```python
from metrics_dashboard import MetricsDashboard, AlertConfig

# Alert configuration
alerts = AlertConfig(
    avg_latency_threshold=500.0,
    p99_latency_threshold=1000.0,
    error_rate_threshold=5.0,
    cpu_threshold=90.0,
    memory_threshold=90.0,
    throughput_min=10.0,
    stagnation_threshold=100
)

# Create dashboard with custom settings
dashboard = MetricsDashboard(
    update_interval=0.5,        # Update every 0.5 seconds
    history_window=600,         # Show 10 minutes of history
    alert_config=alerts
)
```

### Update Interval

**Fast (0.5-1s)**: Real-time monitoring, development
**Medium (2-5s)**: Production monitoring
**Slow (10-30s)**: Long-term trends, low overhead

### History Window

**Short (60s)**: Recent events, debugging
**Medium (300s)**: Standard monitoring
**Long (600-1800s)**: Trend analysis

## Metrics Explained

### Throughput

**Definition**: Number of requests processed per second

**Calculation**:
```
throughput = completed_requests / time_window
```

**Healthy Range**:
- Minimum: 10 req/s
- Good: 50-100 req/s
- Excellent: > 100 req/s

**Issues**:
- Low: Check agent availability, resource constraints
- Decreasing: Check for bottlenecks, errors

### Latency

**Definition**: Time to process a request

**Percentiles**:
- **Average**: Overall performance
- **P95**: 95th percentile (5% are slower)
- **P99**: 99th percentile (1% are slower)

**Healthy Range**:
- Average: < 500ms
- P95: < 750ms
- P99: < 1000ms

**Issues**:
- Increasing: Check resource contention
- Spikes: Check for garbage collection, I/O

### Error Rate

**Definition**: Percentage of failed requests

**Calculation**:
```
error_rate = (failed_requests / total_requests) * 100
```

**Healthy Range**: < 5%

**Issues**:
- Increasing: Check logs for error patterns
- Spikes: Check for service dependencies

### CPU Usage

**Definition**: Percentage of CPU utilization

**Healthy Range**: < 90%

**Issues**:
- Consistently high: Scale up or optimize
- Spiky: Check for periodic tasks

### Memory Usage

**Definition**: Percentage of RAM utilization

**Healthy Range**: < 90%

**Issues**:
- Increasing: Check for memory leaks
- High: Risk of OOM errors

### Active Agents

**Definition**: Number of agents currently processing

**Monitor**:
- Should match expected count
- Decreasing: Check for agent failures
- Increasing: Check for unintended spawns

### Average Value

**Definition**: Expected long-term reward (TD(λ))

**Range**: -1 to 1

**Monitor**:
- Increasing: Learning is working
- Stable: Converged
- Decreasing: Problem with learning

### Convergence Rate

**Definition**: Rate of change in value function

**Range**: 0 to 1

**Monitor**:
- High: Learning in progress
- Low: Converged or stuck
- Negative: Diverging (bad!)

## Alerts

### Alert Types

#### Latency Alerts
```python
# Triggered when: avg_latency > threshold
Alert(
    severity='warning',
    metric='avg_latency',
    value=650.0,
    threshold=500.0,
    message='High average latency: 650.0ms'
)
```

#### Error Rate Alerts
```python
# Triggered when: error_rate > threshold
Alert(
    severity='error',
    metric='error_rate',
    value=7.5,
    threshold=5.0,
    message='High error rate: 7.5%'
)
```

#### Resource Alerts
```python
# Triggered when: cpu_usage > threshold
Alert(
    severity='warning',
    metric='cpu_usage',
    value=95.0,
    threshold=90.0,
    message='High CPU usage: 95.0%'
)
```

#### Critical Alerts
```python
# Triggered when: memory_usage > critical_threshold
Alert(
    severity='critical',
    metric='memory_usage',
    value=98.0,
    threshold=90.0,
    message='High memory usage: 98.0%'
)
```

### Alert Management

```python
# Access recent alerts
recent_alerts = list(dashboard.alerts)[-10:]

# Filter by severity
critical_alerts = [a for a in dashboard.alerts if a.severity == 'critical']

# Clear old alerts
dashboard.alerts.clear()
```

## Export and Sharing

### Save Snapshot

```python
# Save current dashboard state as image
dashboard.save_snapshot("dashboard_snapshot.png")
```

### Export HTML Dashboard

```python
# Export as standalone HTML (requires plotly)
dashboard.export_html("dashboard.html")

# Features:
# - Interactive plots
# - Zoom and pan
# - Hover tooltips
# - Responsive design
```

### Embed in Web Page

```html
<!DOCTYPE html>
<html>
<head>
    <title>POLLN Dashboard</title>
</head>
<body>
    <iframe src="dashboard.html"
            width="100%"
            height="900"
            frameborder="0">
    </iframe>
</body>
</html>
```

### API Access

```python
# Get current metrics
metrics = dashboard.metrics_callback()

# Get historical data
recent = dashboard.metrics_buffer.get_latest(100)

# Get by time range
last_minute = dashboard.metrics_buffer.get_by_timerange(60)
```

## Troubleshooting

### Dashboard Not Updating

**Check**:
1. Metrics callback is set
2. Callback returns valid data
3. Update interval is reasonable

**Solution**:
```python
# Verify callback
def test_callback():
    metrics = dashboard.metrics_callback()
    assert metrics is not None
    assert isinstance(metrics, SystemMetrics)
    print(metrics)
```

### High Memory Usage

**Cause**: Large history window

**Solution**:
```python
# Reduce history window
dashboard = MetricsDashboard(history_window=60)  # 1 minute
```

### Slow Rendering

**Cause**: Too many data points

**Solution**:
```python
# Reduce update frequency or data points
dashboard = MetricsDashboard(
    update_interval=5.0,     # Update every 5 seconds
    history_window=60        # Show only 1 minute
)
```

### Missing Plotly Export

**Cause**: Plotly not installed

**Solution**:
```bash
pip install plotly
```

### Animation Not Working

**Cause**: ffmpeg not installed

**Solution**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Best Practices

### For Development

```python
# Fast updates for debugging
dashboard = MetricsDashboard(
    update_interval=0.5,
    history_window=30
)
```

### For Production

```python
# Slower updates, longer history
dashboard = MetricsDashboard(
    update_interval=5.0,
    history_window=1800,
    alert_config=production_alerts
)

# Export定期ly
import schedule

def export_dashboard():
    dashboard.export_html(f"daily_reports/dashboard_{time.strftime('%Y%m%d')}.html")

schedule.every().hour.do(export_dashboard)
```

### For Presentations

```python
# Clean, simplified view
dashboard = MetricsDashboard(
    update_interval=10.0,
    history_window=120
)

# Save snapshots at key moments
dashboard.save_snapshot("before_optimization.png")
# ... make changes ...
dashboard.save_snapshot("after_optimization.png")
```

## Advanced Usage

### Custom Metrics

```python
from dataclasses import dataclass
from metrics_dashboard import SystemMetrics

@dataclass
class CustomMetrics(SystemMetrics):
    # Add custom fields
    cache_hit_rate: float = 0.0
    gpu_utilization: float = 0.0

    def fetch_custom_metrics():
        return CustomMetrics(
            timestamp=time.time(),
            throughput=50.0,
            # ... standard fields ...
            cache_hit_rate=0.85,
            gpu_utilization=45.0
        )
```

### Multiple Dashboards

```python
# Separate dashboards for different concerns
performance_dashboard = MetricsDashboard(
    history_window=60,
    alert_config=performance_alerts
)

resource_dashboard = MetricsDashboard(
    history_window=300,
    alert_config=resource_alerts
)
```

### Dashboard Composition

```python
# Create custom multi-dashboard view
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Add custom plots
# ...

# Save as image
plt.savefig("custom_dashboard.png", dpi=150)
```

## Resources

- [Main Documentation](README.md)
- [Visualization Guide](VISUALIZATION_GUIDE.md)
- [API Reference](README.md#api-reference)
- [Examples](../../examples/)

## Support

For issues or questions:
- GitHub: https://github.com/SuperInstance/polln/issues
- Documentation: https://docs.polln.ai
