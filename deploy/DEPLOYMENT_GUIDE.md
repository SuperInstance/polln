# POLLN Production Deployment Guide

Complete guide for deploying POLLN to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Methods](#deployment-methods)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

### Infrastructure Requirements

- **Kubernetes Cluster**: v1.25+ with at least 3 nodes
- **Node Requirements**:
  - Minimum 4 CPU cores per node
  - Minimum 8GB RAM per node
  - 50GB+ storage available
- **Load Balancer**: For ingress/external access
- **DNS**: Domain name configured for the service

### Tools Required

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Trivy (security scanning)
brew install trivy  # macOS
# or visit: https://aquasecurity.github.io/trivy/
```

### Access Requirements

- Kubernetes cluster admin access
- Container registry access (for pushing images)
- DNS management access
- Monitoring system access (Prometheus, Grafana)

---

## Pre-Deployment Checklist

### 1. Security

- [ ] Secrets generated and stored securely
- [ ] TLS certificates obtained
- [ ] Network policies reviewed
- [ ] RBAC roles configured
- [ ] Container image vulnerability scan completed

### 2. Infrastructure

- [ ] Kubernetes cluster provisioned
- [ ] Persistent storage provisioned
- [ ] Ingress controller installed
- [ ] Cert-manager installed (for TLS)
- [ ] Monitoring stack installed (Prometheus, Grafana)

### 3. Application

- [ ] Container image built and pushed
- [ ] Configuration reviewed
- [ ] Feature flags configured
- [ ] Resource limits validated
- [ ] Health checks tested

### 4. Operations

- [ ] Backup procedures documented
- [ ] Runbooks created
- [ ] On-call rotation established
- [ ] Alerting configured
- [ ] Logging configured

---

## Deployment Methods

### Method 1: Automated Deployment Script

```bash
# Set environment variables
export NAMESPACE="polln-production"
export RELEASE_NAME="polln"
export VALUES_FILE="deploy/helm/polln/values.prod.yaml"

# Run deployment script
./deploy/scripts/deploy.sh install

# Verify deployment
./deploy/scripts/verify-deployment.sh

# Test health endpoints
./deploy/scripts/test-health.sh
```

### Method 2: Manual Helm Deployment

```bash
# 1. Create namespace
kubectl create namespace polln-production

# 2. Generate secrets
./deploy/scripts/generate-secrets.sh

# 3. Update Helm dependencies
helm dependency update deploy/helm/polln

# 4. Install POLLN
helm install polln deploy/helm/polln \
  --namespace polln-production \
  --values deploy/helm/polln/values.prod.yaml \
  --wait \
  --timeout 10m

# 5. Verify installation
kubectl get pods -n polln-production
kubectl get svc -n polln-production
```

### Method 3: GitOps with ArgoCD

Create an ArgoCD Application:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: polln-production
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/SuperInstance/polln.git
    targetRevision: main
    path: deploy/helm/polln
    helm:
      valueFiles:
        - values.prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: polln-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

## Post-Deployment Verification

### 1. Health Checks

```bash
# Run automated verification
./deploy/scripts/verify-deployment.sh

# Manual health check
kubectl port-forward deployment/polln 3000:3000 -n polln-production
curl http://localhost:3000/health
curl http://localhost:3000/ready
curl http://localhost:3000/metrics
```

### 2. Resource Utilization

```bash
# Check pod resource usage
kubectl top pods -n polln-production

# Check node resource usage
kubectl top nodes

# Check PVC usage
kubectl get pvc -n polln-production
```

### 3. Connectivity Tests

```bash
# Test from cluster
kubectl run test-pod --image=curlimages/curl -i --rm --restart=Never \
  -- curl http://polln-api.polln-production.svc.cluster.local:3000/health

# Test from external (if ingress configured)
curl https://api.polln.dev/health
```

### 4. Smoke Tests

```bash
# Test WebSocket connection
wscat -c wss://api.polln.dev/api/ws

# Test API endpoints
curl https://api.polln.dev/health | jq
curl https://api.polln.dev/metrics | head -20
```

---

## Monitoring and Observability

### Prometheus Metrics

Access metrics at: `http://prometheus:9090`

Key metrics to monitor:

- `polln_api_uptime_seconds` - Server uptime
- `polln_api_connections_active` - Active connections
- `polln_api_messages_sent` - Messages sent
- `polln_api_messages_received` - Messages received
- `polln_api_messages_errors` - Message errors
- `polln_api_rate_limits_rejected` - Rate limit rejections

### Grafana Dashboards

Access Grafana at: `http://grafana:3000` (admin/admin)

Import dashboard from: `deploy/monitoring/grafana-dashboards/`

### Alerts

Alerts are configured in `deploy/monitoring/prometheus-alerts.yml`

Key alerts:
- `PollnAPIDown` - API server is down
- `PollnHighErrorRate` - High error rate
- `PollnHighMemoryUsage` - Memory usage high
- `PollnAvailabilitySLO` - Availability SLO breach

### Logging

```bash
# View logs
kubectl logs -f deployment/polln -n polln-production

# View logs from all pods
kubectl logs -f -l app.kubernetes.io/name=polln -n polln-production

# View logs with specific label
kubectl logs -f -l version=v0.1.0 -n polln-production
```

---

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Describe pod
kubectl describe pod -l app.kubernetes.io/name=polln -n polln-production

# Check events
kubectl get events -n polln-production --sort-by='.lastTimestamp'

# Common solutions:
# - Image pull error: Check image name and registry access
# - CrashLoopBackOff: Check logs for application errors
# - Insufficient resources: Check resource requests/limits
```

#### 2. High Memory Usage

```bash
# Check memory usage
kubectl top pods -n polln-production

# Increase memory limits
helm upgrade polln deploy/helm/polln \
  --namespace polln-production \
  --set resources.limits.memory=8Gi \
  --values deploy/helm/polln/values.prod.yaml
```

#### 3. Connection Issues

```bash
# Check service endpoints
kubectl get endpoints -n polln-production

# Check network policies
kubectl get networkpolicy -n polln-production

# Test connectivity
kubectl run test-pod --image=busybox -i --rm --restart=Never \
  -- nc -zv polln-api 3000
```

#### 4. Performance Issues

```bash
# Check HPA status
kubectl get hpa -n polln-production

# Check resource usage
kubectl top pods -n polln-production

# View metrics
kubectl port-forward svc/polln-prometheus 9090:9090 -n polln-production
```

---

## Maintenance

### Scaling

```bash
# Manual scaling
kubectl scale deployment/polln --replicas=10 -n polln-production

# Auto-scaling (configured in HPA)
kubectl get hpa -n polln-production
kubectl describe hpa polln -n polln-production
```

### Updating

```bash
# Update image
helm upgrade polln deploy/helm/polln \
  --namespace polln-production \
  --set image.tag=v0.2.0 \
  --values deploy/helm/polln/values.prod.yaml

# Rollback
helm rollback polln -n polln-production

# Rollback to specific version
helm rollback polln 2 -n polln-production
```

### Backup and Restore

```bash
# Backup
./deploy/scripts/backup.sh

# List backups
ls -lh backups/

# Restore
./deploy/scripts/restore.sh backups/polln-backup-20240308.tar.gz
```

### Certificate Renewal

```bash
# Check certificate expiry
kubectl get cert -n polln-production

# Force renewal
kubectl annotate cert polln-tls cert-manager.io/issue-temporary-certificate=true -n polln-production
```

---

## Security Best Practices

1. **Regular Updates**: Keep Kubernetes and dependencies updated
2. **Network Policies**: Restrict network traffic between services
3. **RBAC**: Use role-based access control
4. **Secrets Management**: Use external secret management (e.g., AWS Secrets Manager)
5. **Image Scanning**: Scan images for vulnerabilities before deployment
6. **Audit Logging**: Enable audit logging for Kubernetes API
7. **Pod Security**: Use Pod Security Standards (Pod Security Policies deprecated)

---

## Support and Resources

- **Documentation**: https://docs.polln.dev
- **GitHub**: https://github.com/SuperInstance/polln
- **Issues**: https://github.com/SuperInstance/polln/issues
- **Slack**: #polln-dev

---

## Appendix

### Environment Variables

See `.env.example` for all available environment variables.

### API Documentation

Access API documentation at: `https://api.polln.dev/docs`

### Performance Tuning

See `docs/PERFORMANCE_TUNING.md` for performance optimization.

### Disaster Recovery

See `ops/runbooks/disaster-recovery.md` for DR procedures.
