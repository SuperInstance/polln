# SuperInstance Monitoring Stack - Quick Reference

## Essential Commands

```bash
# Quick Start
make install          # Install dependencies
make start            # Start all services
make status           # Show service status

# Common Operations
make logs             # View all logs
make test             # Run tests
make example          # Run examples
make stop             # Stop all services
make restart          # Restart all services

# Maintenance
make backup           # Backup configuration
make validate         # Validate configs
make health           # Check service health
make clean            # Clean up

# Production
make prod-start       # Start in production mode
make prod-deploy      # Deploy to production
```

## Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9091 | - |
| Jaeger | http://localhost:16686 | - |
| Alertmanager | http://localhost:9093 | - |
| Metrics | http://localhost:9090/metrics | - |

## Key Metrics

### Application Metrics
- `superinstance_operations_total` - Total operations
- `superinstance_operation_duration_seconds` - Operation latency
- `superinstance_crdt_merge_duration_seconds` - CRDT merge time
- `superinstance_consensus_rounds_total` - Consensus rounds
- `superinstance_gpu_utilization_percent` - GPU usage

### System Metrics
- `superinstance_cpu_usage_percent` - CPU usage
- `superinstance_memory_usage_bytes` - Memory usage
- `superinstance_disk_usage_percent` - Disk usage
- `superinstance_agent_count` - Active agents

## Alert Rules

### Critical (Immediate Action)
- `HighErrorRate` - Error rate > 1%
- `ReplicaDown` - Service unavailable
- `ConsensusRoundsFailing` - Consensus failure > 5%

### Warning (Investigate Soon)
- `HighLatency` - P95 latency > 50ms
- `LowFastPathRatio` - Fast path < 90%
- `HighGPUTemperature` - GPU temp > 85°C
- `HighMemoryUsage` - Memory > 90%

## Code Integration

### Basic Setup
```python
from production.monitoring.monitoring_stack import MonitoringStack

monitoring = MonitoringStack("my-service")
monitoring.start_metrics_server(9090)
```

### Record Metrics
```python
monitoring.metrics.record_operation(
    path_type="fast",
    operation_type="read",
    status="success",
    duration_sec=0.002
)
```

### Trace Operations
```python
with monitoring.tracer.trace_operation("my_operation", "fast"):
    # Your code here
    pass
```

### Log Events
```python
monitoring.logger.info("event",
                      key1="value1",
                      key2="value2")
```

### Health Checks
```python
async def check_my_service():
    # Your health check logic
    return True, "OK", {"latency": 5}

monitoring.health_checker.register_check("service", check_my_service)
```

### Custom Alerts
```python
from production.monitoring.monitoring_stack import AlertRule

monitoring.alerter.add_rule(AlertRule(
    name="my_alert",
    condition=lambda m: m.get("metric") > 100,
    severity="warning",
    description="My custom alert"
))
```

## Troubleshooting

### Services Not Starting
```bash
# Check Docker
docker --version
docker compose version

# Check ports
netstat -tuln | grep -E '3000|9090|9091|16686'

# View logs
docker compose logs -f [service-name]

# Restart services
make restart
```

### No Metrics in Prometheus
```bash
# Check metrics endpoint
curl http://localhost:9090/metrics

# Check Prometheus targets
# http://localhost:9091/targets

# Verify network
docker network inspect monitoring
```

### Alerts Not Firing
```bash
# Check alert rules
# http://localhost:9091/alerts

# Check Alertmanager
docker logs alertmanager

# Test webhook
curl -XPOST http://localhost:9093/api/v1/alerts -d '[...]'
```

### Grafana No Data
```bash
# Check datasource
# Settings → Data Sources → Prometheus → Test

# Verify time range includes current time

# Check Prometheus query
curl 'http://localhost:9091/api/v1/query?query=up'
```

## Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables |
| `prometheus/prometheus.yml` | Prometheus config |
| `prometheus/alerts.yml` | Alert rules |
| `alertmanager/alertmanager.yml` | Alert routing |
| `grafana/provisioning/datasources.yml` | Grafana datasources |
| `docker-compose.yml` | Service definitions |

## Common Queries

### Prometheus Query Examples
```promql
# Operation rate
rate(superinstance_operations_total[5m])

# P95 latency
histogram_quantile(0.95, rate(superinstance_operation_duration_seconds_bucket[5m]))

# Error rate
rate(superinstance_operations_total{status="error"}[5m]) / rate(superinstance_operations_total[5m])

# Fast path ratio
rate(superinstance_operations_total{path_type="fast"}[5m]) / rate(superinstance_operations_total[5m])

# GPU utilization
superinstance_gpu_utilization_percent
```

## Performance Tuning

### Reduce Overhead
```python
# Increase scrape interval
SCRAFE_INTERVAL=30s  # in prometheus.yml

# Reduce metrics cardinality
# Avoid high-cardinality labels like user IDs
# Use bounded enumerations

# Adjust retention
PROMETHEUS_RETENTION_TIME=7d  # in docker-compose.yml
```

### Improve Accuracy
```python
# Decrease scrape interval
SCRAFE_INTERVAL=5s

# Increase histogram buckets
# In monitoring_stack.py

# Enable more detailed tracing
ENABLE_TRACING=true
```

## Security Checklist

- [ ] Change default Grafana password
- [ ] Enable TLS/SSL
- [ ] Restrict network access
- [ ] Use secrets management
- [ ] Rotate webhook URLs
- [ ] Enable authentication
- [ ] Configure RBAC
- [ ] Audit logs regularly

## Backup & Restore

### Backup
```bash
make backup

# Or manually
docker exec prometheus tar czf - /prometheus | gzip > backup.tar.gz
docker exec grafana grafana-cli admin export-dashboard > dashboard.json
```

### Restore
```bash
make restore BACKUP=backup_file.tar.gz

# Or manually
docker exec -i prometheus tar xzf - < backup.tar.gz
```

## Monitoring the Monitoring

### Key Metrics to Watch
- Prometheus scrape health
- Alertmanager delivery success
- Grafana dashboard load times
- Disk usage on monitoring nodes
- Memory usage of monitoring stack

### Health Checks
```bash
make health

# Or manually
curl http://localhost:9091/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9093/-/ready     # Alertmanager
```

## Documentation

- **README.md** - Complete user guide
- **DEPLOYMENT_GUIDE.md** - Production deployment
- **SUMMARY.md** - Overview and architecture
- **example_usage.py** - Code examples
- **test_monitoring.py** - Test suite

## Support

### Logs
```bash
# All services
make logs

# Specific service
make logs-prometheus
make logs-grafana
make logs-jaeger
make logs-alertmanager

# Or with Docker
docker compose logs -f [service-name]
```

### Debug Mode
```bash
# Enable in .env
DEBUG=true

# Restart services
make restart
```

### Get Help
- Check logs: `make logs`
- Run tests: `make test`
- View examples: `make example`
- Read docs: `README.md`, `DEPLOYMENT_GUIDE.md`

## Quick Tips

1. **Start Simple**: Use `make install && make start`
2. **Check Status**: `make status` shows all URLs
3. **View Logs**: `make logs` for real-time output
4. **Run Tests**: `make test` to verify setup
5. **Learn by Example**: `make example` for demos
6. **Validate Configs**: `make validate` before deploying
7. **Backup Regularly**: `make backup` before changes
8. **Monitor Health**: `make health` for quick check

## Environment Variables

Key variables in `.env`:

```bash
# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO

# Alerting
SLACK_WEBHOOK_URL=https://...

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=changeme

# Thresholds
LATENCY_WARNING_THRESHOLD=50
ERROR_RATE_WARNING_THRESHOLD=1
FAST_PATH_RATIO_THRESHOLD=90
```

## Common Patterns

### Timed Operation
```python
start = time.time()
# ... operation ...
duration = time.time() - start
monitoring.metrics.record_operation("fast", "op", "success", duration)
```

### Context Manager
```python
with monitoring.tracer.trace_operation("name", "fast", key="value"):
    # Automatic tracing
    pass
```

### Error Handling
```python
try:
    # ... operation ...
    monitoring.metrics.record_operation("fast", "op", "success", duration)
except Exception as e:
    monitoring.metrics.record_operation("fast", "op", "error", duration)
    monitoring.logger.error("operation_failed", error=str(e))
    raise
```

---

**Version**: 1.0.0
**Last Updated**: 2025-03-13
