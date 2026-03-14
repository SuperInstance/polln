# SuperInstance Production Monitoring Stack

Complete monitoring solution for SuperInstance deployment with metrics, traces, logs, health checks, and alerting.

## Features

- **Prometheus Metrics**: Application performance metrics with custom SuperInstance instrumentation
- **OpenTelemetry Tracing**: Distributed tracing for operations, CRDT merges, and consensus rounds
- **Structured Logging**: JSON logging with contextual metadata
- **Health Checks**: Comprehensive system health monitoring
- **Alerting**: Configurable alert rules with Slack integration
- **Grafana Dashboards**: Pre-built dashboards for visualization
- **Docker Compose**: One-command deployment of full monitoring stack

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Monitoring Stack

```bash
docker-compose up -d
```

This starts:
- Prometheus (port 9091): Metrics collection
- Grafana (port 3000): Dashboards and visualization
- Jaeger (port 16686): Distributed tracing UI
- Alertmanager (port 9093): Alert routing and management

### 4. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9091
- **Jaeger**: http://localhost:16686

## Monitoring Components

### Metrics

The following metrics are collected:

**Operation Metrics:**
- `superinstance_operations_total` - Total operations by path type and status
- `superinstance_operation_duration_seconds` - Operation duration histogram
- `superinstance_network_requests_total` - Network request count
- `superinstance_network_request_duration_seconds` - Network request latency

**CRDT Metrics:**
- `superinstance_crdt_merge_duration_seconds` - CRDT merge duration
- `superinstance_crdt_state_size_bytes` - CRDT state size
- `superinstance_crdt_conflict_resolutions_total` - Conflict resolution count

**Consensus Metrics:**
- `superinstance_consensus_rounds_total` - Consensus round count
- `superinstance_consensus_duration_seconds` - Round duration
- `superinstance_consensus_participants` - Participant count

**GPU Metrics:**
- `superinstance_gpu_utilization_percent` - GPU utilization
- `superinstance_gpu_memory_used_bytes` - GPU memory usage
- `superinstance_gpu_temperature_celsius` - GPU temperature
- `superinstance_gpu_power_draw_watts` - GPU power consumption

**Agent Metrics:**
- `superinstance_agent_count` - Active agent count by type
- `superinstance_agent_messages_total` - Agent message count

**System Metrics:**
- `superinstance_cpu_usage_percent` - CPU usage
- `superinstance_memory_usage_bytes` - Memory usage
- `superinstance_disk_usage_percent` - Disk usage by mount point

### Tracing

Distributed tracing tracks:
- Operation execution with path type context
- CRDT merge operations with replica IDs
- Consensus rounds with participant information
- Tile execution with tile metadata

### Health Checks

System health checks include:
- **Replica Connectivity**: Check if all replicas are accessible
- **Consensus Service**: Verify consensus service health
- **GPU Availability**: Monitor GPU status and temperature
- **Disk Space**: Ensure adequate disk space
- **Memory Usage**: Monitor memory consumption

### Alerting

Pre-configured alert rules:

**Critical Alerts:**
- High error rate (>1%)
- Replica down
- Consensus rounds failing

**Warning Alerts:**
- High P95 latency (>50ms)
- Low fast path ratio (<90%)
- High GPU temperature (>85°C)
- High memory usage (>90%)
- High CPU usage (>80%)
- Disk space low (>90%)

Alerts are sent to Slack via webhook.

## Usage

### Python Integration

```python
from production.monitoring.monitoring_stack import MonitoringStack

# Create monitoring stack
monitoring = MonitoringStack(
    service_name="superinstance",
    config={
        "replica_urls": ["http://node-1:8000", "http://node-2:8000"],
        "consensus_url": "http://consensus:8001",
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL")
    }
)

# Start metrics server
monitoring.start_metrics_server(port=9090)

# Record operation
monitoring.metrics.record_operation(
    path_type="fast",
    operation_type="read",
    status="success",
    duration_sec=0.002
)

# Trace operation
with monitoring.tracer.trace_operation("custom_operation", "fast"):
    # Your operation code here
    pass

# Check health
health = await monitoring.get_health()

# Get alert history
alerts = monitoring.get_alert_history(limit=100)
```

### FastAPI Integration

```python
from production.monitoring.monitoring_stack import create_monitoring_app, MonitoringStack

# Create monitoring stack
monitoring = MonitoringStack("superinstance")

# Create FastAPI app
app = create_monitoring_app(monitoring)

# Endpoints available:
# GET /health - Health check
# GET /metrics - Prometheus metrics
# GET /alerts - Alert history
# GET /status - System status
```

## Configuration

### Environment Variables

```bash
# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO

# Jaeger
JAEGER_HOST=jaeger
JAEGER_PORT=6831

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

### Docker Compose

Edit `docker-compose.yml` to customize:
- Port mappings
- Volume mounts
- Environment variables
- Resource limits

### Prometheus

Edit `prometheus/prometheus.yml` to:
- Add scrape targets
- Configure retention
- Adjust scrape intervals

Edit `prometheus/alerts.yml` to:
- Add custom alert rules
- Adjust thresholds
- Configure alert conditions

### Alertmanager

Edit `alertmanager/alertmanager.yml` to:
- Configure notification channels (Slack, email, PagerDuty)
- Set up routing rules
- Configure inhibition rules

## Dashboards

### SuperInstance Overview

Main dashboard showing:
- Fast path ratio
- P95 latency
- Error rate
- Service health

### Custom Dashboards

Create custom dashboards in Grafana:
1. Navigate to Dashboards → New
2. Add panels with Prometheus queries
3. Save and export to `grafana/dashboards/`

## Troubleshooting

### Prometheus Not Scraping Metrics

Check:
1. Metrics server is running: `curl http://localhost:9090/metrics`
2. Prometheus configuration: `docker logs prometheus`
3. Network connectivity: `docker network inspect monitoring`

### Alerts Not Firing

Check:
1. Alertmanager configuration: `docker logs alertmanager`
2. Alert rules in Prometheus UI: http://localhost:9091/alerts
3. Webhook URL is correct and accessible

### Grafana Not Showing Data

Check:
1. Datasource configuration: Settings → Data Sources → Prometheus
2. Prometheus is accessible: `curl http://prometheus:9090/api/v1/query?query=up`
3. Time range is correct

## Performance Considerations

### Metrics Cardinality

Avoid high cardinality labels:
- Don't use user IDs, request IDs, or timestamps
- Use bounded enumerations (operation types, status codes)
- Keep label values under 100 unique values

### Scrape Interval

Default: 15 seconds
- Lower = more granular data, higher load
- Higher = less granular data, lower load

### Data Retention

Prometheus default: 15 days
- Configure with `--storage.tsdb.retention.time`
- Adjust based on storage capacity and query patterns

## Production Deployment

### Security

1. Change default Grafana password
2. Enable authentication on Prometheus
3. Use TLS for all communications
4. Restrict network access with firewalls

### High Availability

1. Deploy multiple Prometheus replicas withThanos
2. Use load balancer for Grafana
3. Configure alert failover

### Scaling

1. Horizontal scaling: Add more Prometheus targets
2. Vertical scaling: Increase resource limits
3. Federation: Configure Prometheus federation

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d
```

### Backup

```bash
# Backup Grafana dashboards
docker exec grafana grafana-cli admin export-dashboard > backup.json

# Backup Prometheus data
docker exec prometheus tar czf - /prometheus | gzip > prometheus-backup.tar.gz
```

### Monitoring the Monitoring

Monitor:
- Prometheus scrape health
- Alertmanager delivery status
- Grafana performance
- Disk usage on monitoring nodes

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f [service]`
2. Verify configuration: `docker exec [service] cat /etc/[config-file]`
3. Test connectivity: `docker exec [service] ping [target]`

## License

MIT License - See LICENSE file for details
