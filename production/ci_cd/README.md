# SuperInstance CI/CD Pipeline

Complete CI/CD pipeline for automated SuperInstance deployment and testing.

## Overview

This pipeline provides:

- **Multi-stage testing**: Linting, unit tests, integration tests, simulation validation
- **Automated building**: Docker image creation and optimization
- **Kubernetes deployment**: Blue-green deployments with health checks
- **Monitoring stack**: Prometheus, Grafana, Alertmanager integration
- **Rollback capabilities**: Automatic rollback on failure

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │   Lint   │ │   Test   │ │ Security │ │  Build   │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
│       │            │            │            │              │
│       └────────────┴────────────┴────────────┘              │
│                            │                                │
┌────────────────────────────┼────────────────────────────────┐
│                             │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │              Docker Registry                        │   │
│  │   superinstance:latest, crdt:latest, ...            │   │
│  └──────────────────────────┬──────────────────────────┘   │
│                             │                                │
┌────────────────────────────┼────────────────────────────────┐
│                             │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │                  Kubernetes                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │ CRDT Coord  │──│  Consensus  │──│    Web      │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │  Prometheus │──│   Grafana   │──│Alertmanager │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Local Development

```bash
# Run linting
python -m black --check src/
python -m mypy src/
python -m pylint src/

# Run unit tests
pytest tests/unit/ -v --cov=src/

# Run integration tests
pytest tests/integration/ -v

# Validate all simulation schemas
python scripts/validate_all_schemas.py
```

### GitHub Actions

The pipeline triggers on:

- Push to `main`, `develop`, or `papers-main` branches
- Pull requests to `main` or `papers-main`
- Release publication

### Manual Deployment

```bash
# Run complete pipeline
python production/ci_cd/pipeline.py --environment dev

# Deploy to staging
python production/ci_cd/pipeline.py --environment staging

# Deploy to production (requires approval)
python production/ci_cd/pipeline.py --environment production

# Emergency deploy (skip tests)
python production/ci_cd/pipeline.py --environment production --skip-tests
```

## Pipeline Stages

### 1. Lint

Runs code quality checks:

- **Black**: Python code formatting
- **MyPy**: Type checking
- **Pylint**: Code quality analysis
- **ESLint**: JavaScript/TypeScript linting

### 2. Unit Tests

Runs unit tests across Python and Node.js:

- Python tests with pytest
- Node.js tests with Jest
- Coverage reporting (target: 80%)
- Multi-version testing (Python 3.10, 3.11 / Node 18, 20)

### 3. Integration Tests

Tests service integration:

- CRDT coordination service
- Database integration
- Redis integration
- API endpoint testing

### 4. Simulation Validation

Validates all simulation schemas (P24-P40):

```python
# Validate specific paper
python papers/24-self-play-mechanisms/simulation_schema.py

# Validate all papers
python scripts/validate_all_schemas.py
```

### 5. Security Scan

Runs security checks:

- **Safety**: Dependency vulnerability scanning
- **Bandit**: Static application security testing (SAST)
- **Trivy**: Container image scanning

### 6. Build

Builds Docker images:

```bash
# Build all images
docker-compose -f docker-compose.prod.yml build

# Build specific image
docker build -f Dockerfile -t superinstance:latest .
```

### 7. Push

Pushes images to registry:

```bash
# Tag and push
docker tag superinstance:latest registry.example.com/superinstance:latest
docker push registry.example.com/superinstance:latest
```

### 8. Deploy

Deploys to Kubernetes:

```bash
# Deploy to development
kubectl apply -f k8s/superinstance/dev/

# Deploy to staging
kubectl apply -f k8s/superinstance/staging/

# Deploy to production (blue-green)
kubectl apply -f k8s/superinstance/production/
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install Helm (for optional charts)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Deploy Stack

```bash
# Create namespace
kubectl apply -f k8s/superinstance/namespace.yaml

# Apply configuration
kubectl apply -f k8s/superinstance/configmap.yaml

# Deploy CRDT coordinator
kubectl apply -f k8s/superinstance/crdt-deployment.yaml

# Deploy consensus service
kubectl apply -f k8s/superinstance/consensus-deployment.yaml

# Deploy monitoring
kubectl apply -f k8s/superinstance/prometheus.yaml
kubectl apply -f k8s/superinstance/grafana.yaml
kubectl apply -f k8s/superinstance/alertmanager.yaml

# Configure ingress
kubectl apply -f k8s/superinstance/ingress.yaml

# Configure autoscaling
kubectl apply -f k8s/superinstance/hpa.yaml
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n superinstance

# Check services
kubectl get services -n superinstance

# Check logs
kubectl logs -f deployment/crdt-coordinator -n superinstance

# Port forward for local testing
kubectl port-forward svc/crdt-coordinator 8001:8001 -n superinstance
```

## Monitoring

### Prometheus

Access metrics at: `http://prometheus.superinstance.example.com`

Key metrics:

- `operations_total`: Total operations processed
- `fast_path_ops`: Fast path operations
- `slow_path_ops`: Slow path operations
- `errors_total`: Total errors
- `avg_latency_ms`: Average operation latency

Example queries:

```promql
# Fast path ratio
fast_path_ops / operations_total

# Error rate
rate(errors_total[5m]) / rate(operations_total[5m])

# P99 latency
histogram_quantile(0.99, rate(operation_latency_seconds_bucket[5m]))
```

### Grafana

Access dashboards at: `https://grafana.superinstance.example.com`

Default credentials (change in production):
- Username: `admin`
- Password: `changeme`

### Alerts

Alerts are configured for:

- **Service Down**: Critical - Service unreachable
- **High Error Rate**: Warning - Error rate > 5%
- **High Latency**: Warning - P99 latency > 1s
- **High Memory**: Warning - Memory usage > 90%
- **High CPU**: Warning - CPU usage > 80%
- **Merge Queue Backlog**: Warning - Queue size > 1000

## Rollback

### Automatic Rollback

The pipeline automatically rolls back on deployment failure:

```yaml
# In GitHub Actions
- name: Rollback on failure
  if: failure()
  run: |
    kubectl rollout undo deployment/superinstance-production
```

### Manual Rollback

```bash
# Rollback to previous revision
kubectl rollout undo deployment/crdt-coordinator -n superinstance

# Rollback to specific revision
kubectl rollout undo deployment/crdt-coordinator --to-revision=3 -n superinstance

# Check rollback status
kubectl rollout status deployment/crdt-coordinator -n superinstance
```

## Configuration

### Environment Variables

Set these in your GitHub repository settings:

```bash
# Docker Registry
REGISTRY_USERNAME=your-username
REGISTRY_PASSWORD=your-password

# Kubernetes
KUBE_CONFIG_DEV=<base64-encoded-kubeconfig>
KUBE_CONFIG_STAGING=<base64-encoded-kubeconfig>
KUBE_CONFIG_PROD=<base64-encoded-kubeconfig>

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

### Pipeline Configuration

Edit `production/ci_cd/pipeline.py`:

```python
config = PipelineConfig(
    project_name="superinstance",
    registry="registry.example.com",
    code_coverage_threshold=80.0,
    rollback_on_failure=True
)
```

## Troubleshooting

### Pipeline Failures

```bash
# Check GitHub Actions logs
# Navigate to: Actions -> [Workflow Run] -> [Job]

# Re-run failed job
gh run rerun [run-id]

# Re-run failed tests
gh run rerun [run-id] --failed
```

### Deployment Issues

```bash
# Check pod status
kubectl describe pod [pod-name] -n superinstance

# Check logs
kubectl logs [pod-name] -n superinstance --previous

# Check events
kubectl get events -n superinstance --sort-by='.lastTimestamp'

# Port forward for debugging
kubectl port-forward pod/[pod-name] 8001:8001 -n superinstance
```

### Performance Issues

```bash
# Check resource usage
kubectl top pods -n superinstance
kubectl top nodes

# Check HPA status
kubectl get hpa -n superinstance

# Check metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/superinstance/pods
```

## Best Practices

1. **Always test on dev/staging first**
2. **Monitor deployments closely**
3. **Keep rollback plans ready**
4. **Review security scan results**
5. **Maintain high test coverage**
6. **Use feature flags for gradual rollouts**
7. **Set up proper alerting**
8. **Document runbooks for common issues**

## Contributing

When adding new features:

1. Add/update unit tests
2. Add integration tests if needed
3. Update simulation schemas
4. Update documentation
5. Test pipeline locally first

## Support

For issues or questions:

- GitHub Issues: https://github.com/SuperInstance/polln/issues
- Slack: #superinstance-ops
- Email: ops@example.com
