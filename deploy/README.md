# POLLN Deployment Guide

This directory contains production deployment configurations for POLLN.

## Directory Structure

```
deploy/
├── docker/              # Docker support files
├── helm/               # Helm charts
├── k8s/                # Kubernetes manifests (legacy, use Helm)
├── monitoring/         # Monitoring configurations
└── scripts/            # Deployment scripts
```

## Quick Start

### Local Development (Docker Compose)

```bash
# Start all services
docker-compose up

# Start production build
docker-compose -f docker-compose.prod.yml up
```

### Kubernetes (Helm)

```bash
# Install dependencies
helm dependency update deploy/helm/polln

# Install POLLN
helm install polln deploy/helm/polln \
  --namespace polln \
  --create-namespace \
  --values deploy/helm/polln/values.prod.yaml

# Upgrade POLLN
helm upgrade polln deploy/helm/polln \
  --namespace polln \
  --values deploy/helm/polln/values.prod.yaml
```

## Configuration

### Environment Variables

See `.env.example` for all available environment variables.

### Secrets Management

Generate secrets before deployment:

```bash
./scripts/generate-secrets.sh
```

## Health Checks

- **Liveness**: `GET /health` - Container is running
- **Readiness**: `GET /ready` - Ready to accept traffic
- **Startup**: `GET /health` - Initial startup check

## Monitoring

- **Metrics**: `GET /metrics` - Prometheus metrics
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

## Security

- Images scanned with Trivy
- Non-root container execution
- Network policies enforced
- RBAC configured
- Secrets encrypted at rest

## Scaling

### Horizontal Scaling

```bash
# Manual scaling
kubectl scale deployment polln-api --replicas=5 -n polln

# Auto-scaling (configured in HPA)
kubectl get hpa -n polln
```

### Vertical Scaling

Vertical Pod Autoscaler automatically adjusts resource requests/limits.

## Disaster Recovery

### Backup

```bash
# Backup all data
./scripts/backup.sh

# Backup specific colony
./scripts/backup.sh --colony my-colony
```

### Restore

```bash
# Restore from backup
./scripts/restore.sh --backup backup-20240308.tar.gz
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n polln
kubectl describe pod -l app=polln-api -n polln
```

### View Logs

```bash
# All logs
kubectl logs -f deployment/polln-api -n polln

# Specific container
kubectl logs -f deployment/polln-api -c polln-api -n polln
```

### Port Forward

```bash
# Forward API port
kubectl port-forward deployment/polln-api 3000:3000 -n polln

# Forward debugging port
kubectl port-forward deployment/polln-api 9229:9229 -n polln
```

## Performance

### Load Testing

```bash
# Run load tests
kubectl run -i --tty load-test \
  --image=locustio/locust \
  --restart=Never \
  -- -f /locust/locustfile.py --host=http://polln-api:3000
```

### Benchmarking

```bash
# Run benchmarks
npm run bench:all
```

## Upgrading

### Rolling Update

```bash
# Update image
helm upgrade polln deploy/helm/polln \
  --namespace polln \
  --set image.tag=v0.2.0 \
  --values deploy/helm/polln/values.prod.yaml

# Monitor rollout
kubectl rollout status deployment/polln-api -n polln
```

### Rollback

```bash
# Rollback to previous version
helm rollback polln -n polln

# Rollback to specific revision
helm rollback polln 2 -n polln
```

## Maintenance

### Certificate Renewal

```bash
# Check certificate expiry
kubectl get cert -n polln

# Renew certificates
kubectl annotate cert polln-tls cert-manager.io/issue-temporary-certificate=true -n polln
```

### Database Migration

```bash
# Run migrations
kubectl exec -it deployment/polln-api -n polln -- npm run migrate
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/SuperInstance/polln/issues
- Documentation: https://docs.polln.dev
- Slack: #polln-dev
