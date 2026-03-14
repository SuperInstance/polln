# SuperInstance Monitoring Stack - Deployment Guide

Complete production deployment guide for the SuperInstance monitoring system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Configuration](#configuration)
5. [Monitoring Stack Components](#monitoring-stack-components)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Security](#security)

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 11+) or macOS 12+
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Disk**: 20GB minimum for metrics storage
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Software Requirements

```bash
# Check Docker version
docker --version  # Should be 20.10+

# Check Docker Compose version
docker compose version  # Should be 2.0+
```

### GPU Monitoring (Optional)

For GPU monitoring, install NVIDIA drivers and CUDA toolkit:

```bash
# On Ubuntu
sudo apt-get install nvidia-driver-535
sudo apt-get install nvidia-cuda-toolkit

# Verify
nvidia-smi
```

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/SuperInstance/SuperInstance-papers.git
cd SuperInstance-papers/production/monitoring
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
# Monitoring Configuration
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO

# Jaeger Configuration
JAEGER_HOST=localhost
JAEGER_PORT=6831

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
EOF
```

### 4. Start Monitoring Stack

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps
```

### 5. Verify Deployment

```bash
# Check Prometheus
curl http://localhost:9091/-/healthy

# Check Grafana
curl http://localhost:3000/api/health

# Check Jaeger
curl http://localhost:16686/api/status

# View metrics
curl http://localhost:9090/metrics
```

### 6. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9091
- **Jaeger**: http://localhost:16686
- **Alertmanager**: http://localhost:9093

## Production Deployment

### 1. Prepare Production Environment

```bash
# Create production user
sudo useradd -m -s /bin/bash monitor

# Create directories
sudo mkdir -p /opt/monitoring
sudo mkdir -p /var/lib/monitoring/prometheus
sudo mkdir -p /var/lib/monitoring/grafana
sudo mkdir -p /var/lib/monitoring/alertmanager

# Set permissions
sudo chown -R monitor:monitor /opt/monitoring
sudo chown -R monitor:monitor /var/lib/monitoring
```

### 2. Deploy with Docker Compose

```bash
# Copy files to production server
scp -r production/monitoring/* user@server:/opt/monitoring/

# SSH to server
ssh user@server

# Start services
cd /opt/monitoring
docker compose -f docker-compose.yml up -d
```

### 3. Deploy with Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/prometheus/
kubectl apply -f k8s/grafana/
kubectl apply -f k8s/jaeger/
kubectl apply -f k8s/alertmanager/

# Check deployment
kubectl get pods -n monitoring
```

### 4. Configure Reverse Proxy (Nginx)

```nginx
# /etc/nginx/conf.d/monitoring.conf

server {
    listen 80;
    server_name monitoring.example.com;

    # Grafana
    location /grafana/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9091/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Jaeger
    location /jaeger/ {
        proxy_pass http://localhost:16686/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Enable HTTPS

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d monitoring.example.com

# Auto-renewal (configured automatically)
sudo certbot renew --dry-run
```

## Configuration

### Prometheus Configuration

Edit `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    environment: 'prod'

scrape_configs:
  - job_name: 'superinstance'
    static_configs:
      - targets:
          - 'node-1:9090'
          - 'node-2:9090'
          - 'node-3:9090'
```

### Alert Rules

Edit `prometheus/alerts.yml`:

```yaml
groups:
  - name: superinstance_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(superinstance_operation_duration_seconds_bucket[5m])) > 0.1
        for: 5m
        annotations:
          summary: "High latency detected"
```

### Grafana Dashboards

1. Import dashboards from `grafana/dashboards/`
2. Configure datasources
3. Set up alerts and notifications

### Alertmanager

Edit `alertmanager/alertmanager.yml`:

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  receiver: 'slack-critical'
  group_wait: 10s
  repeat_interval: 12h

receivers:
  - name: 'slack-critical'
    slack_configs:
      - send_resolved: true
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
```

## Monitoring Stack Components

### Prometheus

- **Purpose**: Metrics collection and storage
- **Port**: 9091
- **Retention**: 15 days (configurable)
- **Storage**: `/var/lib/monitoring/prometheus`

**Key Commands**:
```bash
# Check logs
docker logs prometheus

# Restart service
docker restart prometheus

# Check configuration
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

### Grafana

- **Purpose**: Visualization and dashboards
- **Port**: 3000
- **Storage**: `/var/lib/monitoring/grafana`

**Key Commands**:
```bash
# Check logs
docker logs grafana

# Restart service
docker restart grafana

# Backup dashboards
docker exec grafana grafana-cli admin export-dashboard > backup.json
```

### Jaeger

- **Purpose**: Distributed tracing
- **Port**: 16686 (UI), 6831 (agent)
- **Storage**: Memory (development), Elasticsearch (production)

**Key Commands**:
```bash
# Check logs
docker logs jaeger

# Restart service
docker restart jaeger
```

### Alertmanager

- **Purpose**: Alert routing and management
- **Port**: 9093
- **Storage**: `/var/lib/monitoring/alertmanager`

**Key Commands**:
```bash
# Check logs
docker logs alertmanager

# Restart service
docker restart alertmanager

# Test alerts
curl -XPOST http://localhost:9093/api/v1/alerts -d '[{
  "labels": {
    "alertname": "TestAlert",
    "severity": "warning"
  },
  "annotations": {
    "description": "This is a test alert"
  }
}]'
```

## Maintenance

### Daily Tasks

- Check alert history in Grafana
- Review error rates and latency
- Verify all services are healthy

### Weekly Tasks

- Review and tune alert thresholds
- Check disk usage on monitoring nodes
- Update dashboards as needed

### Monthly Tasks

- Review and optimize Prometheus queries
- Archive old metrics data
- Update monitoring stack components

### Backup Procedures

```bash
#!/bin/bash
# backup_monitoring.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/monitoring/$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup Grafana dashboards
docker exec grafana grafana-cli admin export-dashboard > $BACKUP_DIR/grafana-dashboards.json

# Backup Prometheus data
docker exec prometheus tar czf - /prometheus | gzip > $BACKUP_DIR/prometheus-data.tar.gz

# Backup configurations
tar czf $BACKUP_DIR/configs.tar.gz /opt/monitoring/prometheus /opt/monitoring/grafana /opt/monitoring/alertmanager

# Keep last 30 days
find /backup/monitoring -mtime +30 -delete
```

### Update Procedure

```bash
#!/bin/bash
# update_monitoring.sh

# Pull latest images
docker compose pull

# Restart services one by one
for service in prometheus grafana jaeger alertmanager; do
    echo "Updating $service..."
    docker compose up -d --no-deps --force-recreate $service
    sleep 30
done

# Verify all services are running
docker compose ps
```

## Troubleshooting

### Common Issues

#### 1. Prometheus Not Scraping Metrics

**Symptoms**: No data in Prometheus, targets show "DOWN"

**Solutions**:
```bash
# Check if metrics endpoint is accessible
curl http://target:9090/metrics

# Check Prometheus logs
docker logs prometheus

# Verify network connectivity
docker network inspect monitoring

# Test Prometheus configuration
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

#### 2. Alerts Not Firing

**Symptoms**: Alerts should fire but don't

**Solutions**:
```bash
# Check alert rules in Prometheus UI
# http://localhost:9091/alerts

# Verify alert rule syntax
docker exec prometheus promtool check rules /etc/prometheus/alerts.yml

# Check Alertmanager logs
docker logs alertmanager

# Test Alertmanager webhook
curl -XPOST http://localhost:9093/api/v1/alerts -d '...'
```

#### 3. Grafana Not Showing Data

**Symptoms**: Dashboards show "No Data"

**Solutions**:
```bash
# Verify datasource configuration
# Settings → Data Sources → Prometheus → Test

# Check Prometheus query
curl 'http://localhost:9091/api/v1/query?query=up'

# Verify time range in Grafana
# Check that time range includes current time

# Check Grafana logs
docker logs grafana
```

#### 4. High Disk Usage

**Symptoms**: Monitoring nodes running out of disk space

**Solutions**:
```bash
# Check disk usage
df -h

# Reduce Prometheus retention
# Add to prometheus command: --storage.tsdb.retention.time=7d

# Clean old data
docker exec prometheus tsdb delete-series --match='{__name__=~".+"}' --start=2024-01-01 --end=2024-02-01
```

#### 5. Jaeger Not Showing Traces

**Symptoms**: No traces in Jaeger UI

**Solutions**:
```bash
# Check Jaeger agent connectivity
# Verify JAEGER_HOST and JAEGER_PORT in application

# Check Jaeger logs
docker logs jaeger

# Verify traces are being sent
# Look for " spans reported" in application logs
```

## Security

### Authentication

1. **Grafana**:
```bash
# Change default password
docker exec grafana grafana-cli admin reset-admin-password newpassword

# Enable anonymous access (not recommended)
# Edit grafana.ini: set anonymous_enabled = true
```

2. **Prometheus**:
```bash
# Use reverse proxy with authentication
# Or use basic auth with nginx
```

3. **Network Security**:
```bash
# Firewall rules
ufw allow from 10.0.0.0/8 to any port 3000  # Grafana
ufw allow from 10.0.0.0/8 to any port 9091  # Prometheus
ufw deny from any to any port 9091          # Block external access
```

### TLS/SSL

```bash
# Use Certbot for Let's Encrypt
sudo certbot --nginx -d monitoring.example.com

# Or use self-signed certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

### Secrets Management

```bash
# Use Docker secrets
echo "https://hooks.slack.com/services/YOUR/WEBHOOK" | docker secret create slack_webhook -

# Reference in docker-compose.yml
services:
  alertmanager:
    secrets:
      - slack_webhook
```

### RBAC (Grafana)

```bash
# Configure in grafana.ini
[users]
default_theme = dark
[auth.anonymous]
enabled = false
[auth.basic]
enabled = true
```

## Scaling

### Horizontal Scaling

1. **Prometheus Federation**:
```yaml
# Secondary Prometheus
global:
  external_labels:
    replica: '2'

scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="prometheus"}'
    static_configs:
      - targets:
          - 'prometheus-1:9090'
```

2. **Cortex/Thanos**: For long-term storage and horizontal scaling

### Vertical Scaling

Increase resource limits in `docker-compose.yml`:

```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

## Monitoring the Monitoring

Monitor the monitoring stack itself:

```yaml
# Add to prometheus.yml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'alertmanager'
    static_configs:
      - targets: ['alertmanager:9093']
```

## Support

For issues and questions:
- Check logs: `docker compose logs -f [service]`
- Verify configuration: `docker exec [service] cat /etc/[config]`
- Test connectivity: `docker exec [service] ping [target]`
- GitHub Issues: https://github.com/SuperInstance/SuperInstance-papers/issues

## License

MIT License - See LICENSE file for details
