# CRDT Coordination Service - Quick Start Guide

**Get up and running in 5 minutes**

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM available
- Linux/Mac/Windows with WSL2

---

## Installation & Deployment

### Option 1: Using Makefile (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd crdt_deployment

# Start services
make start

# Check health
make health

# Run tests
make test

# View metrics
make metrics
```

### Option 2: Using Docker Compose Directly

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 3: Using Deployment Script (Linux/Mac)

```bash
# Make script executable
chmod +x deploy.sh

# Start deployment
./deploy.sh start

# Check health
./deploy.sh health

# Run tests
./deploy.sh test
```

---

## Service Endpoints

Once deployed, services are available at:

- **Node 1**: http://localhost:8001
- **Node 2**: http://localhost:8002
- **Node 3**: http://localhost:8003
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

---

## Quick API Test

### 1. Health Check

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "node_id": "crdt-1",
  "uptime_seconds": 123.45
}
```

### 2. Write Operation (Fast Path)

```bash
curl -X POST http://localhost:8001/operation \
  -H "Content-Type: application/json" \
  -d '{
    "op_id": "test-001",
    "op_type": "write",
    "key": "counter",
    "value": "42"
  }'
```

**Response:**
```json
{
  "op_id": "test-001",
  "status": "success",
  "result": {
    "op_id": "test-001",
    "success": true,
    "value": "42",
    "version": 1
  },
  "error": null,
  "latency_ms": 2.5,
  "path_used": "fast"
}
```

### 3. Read Operation

```bash
curl -X POST http://localhost:8001/operation \
  -H "Content-Type: application/json" \
  -d '{
    "op_id": "test-002",
    "op_type": "read",
    "key": "counter"
  }'
```

### 4. Critical Operation (Slow Path)

```bash
curl -X POST http://localhost:8001/operation \
  -H "Content-Type: application/json" \
  -d '{
    "op_id": "test-003",
    "op_type": "write",
    "key": "critical_config",
    "value": "production_value",
    "criticality": 0.9
  }'
```

**Note**: `criticality >= 0.7` triggers slow path

### 5. Get Metrics

```bash
curl http://localhost:8001/metrics | jq '.'
```

**Response:**
```json
{
  "node_id": "crdt-1",
  "fast_path_ops": 950,
  "slow_path_ops": 50,
  "total_ops": 1000,
  "avg_latency_ms": 3.2,
  "fast_path_ratio": 0.95,
  "error_count": 2,
  "merge_queue_size": 12
}
```

---

## Common Operations

### View All Logs

```bash
# Using Makefile
make logs

# Using Docker Compose
docker-compose logs -f

# Using deploy script
./deploy.sh logs
```

### Scale Nodes

```bash
# Using Makefile
make k8s-scale N=5

# Using Docker Compose
docker-compose up -d --scale crdt-node=5
```

### Stop Services

```bash
# Using Makefile
make stop

# Using Docker Compose
docker-compose down

# Using deploy script
./deploy.sh stop
```

### Clean Everything

```bash
# Using Makefile
make clean

# Using Docker Compose
docker-compose down -v

# Using deploy script
./deploy.sh clean
```

---

## Monitoring

### Open Prometheus

```bash
# Using Makefile
make prometheus

# Or open in browser
open http://localhost:9090
```

### Open Grafana

```bash
# Using Makefile
make grafana

# Or open in browser
open http://localhost:3000
```

**Grafana Credentials:**
- Username: `admin`
- Password: `admin`

### Key Metrics to Monitor

1. **Fast Path Ratio**: Should be > 0.8 (80%)
2. **Average Latency**: Should be < 10ms
3. **Merge Queue Size**: Should be < 100
4. **Error Rate**: Should be < 1%

---

## Troubleshooting

### Issue: Services Won't Start

**Solution:**
```bash
# Check if ports are already in use
netstat -an | grep 8001

# Stop existing containers
docker-compose down

# Try again
docker-compose up -d
```

### Issue: High Merge Queue Size

**Solution:**
```bash
# Check current queue size
curl http://localhost:8001/metrics | jq '.merge_queue_size'

# Reduce merge interval (faster merges)
export MERGE_INTERVAL_MS=50
docker-compose restart
```

### Issue: Slow Path Dominance

**Solution:**
```bash
# Check path ratio
curl http://localhost:8001/metrics | jq '.fast_path_ratio'

# Lower criticality threshold (more fast path)
# Edit crdt_coordination_service.py:
#   criticality_threshold: float = 0.5  # was 0.7
```

### Issue: Node Unhealthy

**Solution:**
```bash
# Check health
curl http://localhost:8001/health

# View logs
docker-compose logs crdt-node-1

# Restart node
docker-compose restart crdt-node-1
```

---

## Performance Testing

### Load Test with Apache Bench

```bash
# Install ab
sudo apt-get install apache2-utils  # Linux
brew install ab                      # Mac

# Run load test (1000 requests, 10 concurrent)
ab -n 1000 -c 10 -p request.json -T application/json \
  http://localhost:8001/operation
```

**Create request.json:**
```json
{
  "op_id": "load-test-001",
  "op_type": "write",
  "key": "load_key",
  "value": "load_value"
}
```

### Benchmark with Script

```bash
# Using Makefile
make benchmark

# Expected output:
# Successful: 100/100
# Time: 2.15s
# Throughput: 46.51 ops/sec
```

---

## Development

### Run Tests

```bash
# Using Makefile
make test

# Using pytest directly
python -m pytest test_crdt_service.py -v -s
```

### Code Linting

```bash
# Using Makefile
make lint

# Using flake8 directly
flake8 crdt_coordination_service.py --max-line-length=120
```

### Format Code

```bash
# Using Makefile
make format

# Using black directly
black crdt_coordination_service.py test_crdt_service.py
```

---

## Production Deployment

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
make deploy-k8s

# Check status
make k8s-status

# View logs
make k8s-logs

# Scale to 5 replicas
make k8s-scale N=5

# Remove deployment
make undeploy-k8s
```

### Configuration

Edit environment variables in `docker-compose.yml`:

```yaml
environment:
  - NODE_ID=crdt-1
  - REPLICA_URLS=http://crdt-node-2:8001,http://crdt-node-3:8001
  - CONSENSUS_URL=http://consensus:8002
  - MERGE_INTERVAL_MS=100
  - LOG_LEVEL=INFO
```

### Resource Limits

Edit in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

---

## Next Steps

1. **Read the Architecture**: `ARCHITECTURE.md` for deep dive
2. **Review API Reference**: See `README.md` for complete API docs
3. **Set Up Monitoring**: Configure Grafana dashboards
4. **Configure Alerts**: Set up Prometheus alerting rules
5. **Tune Performance**: Adjust thresholds based on workload

---

## Getting Help

- **Documentation**: See `README.md` and `ARCHITECTURE.md`
- **Issues**: Open a GitHub issue
- **Logs**: Check `docker-compose logs` for errors
- **Health**: Run `make health` to check status

---

**Version:** 1.0.0
**Last Updated:** 2026-03-13
