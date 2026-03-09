# Runbook: Colony Crash Incident

**Severity**: P1 - Critical
**Escalation**: @on-call -> @engineering-manager -> @cto
**Target MTTR**: < 15 minutes

## Symptoms

- Colony process not responding
- All agents showing as unhealthy
- WebSocket connections rejected
- Health checks failing (HTTP 503)

## Diagnosis Steps

### 1. Verify Colony Status
```bash
# Check colony health
kubectl exec -it deploy/polln-colony -n production -- npm run cli status

# Check pod status
kubectl get pods -n production -l app=polln-colony

# Check logs
kubectl logs -f deploy/polln-colony -n production --tail=100
```

### 2. Identify Crash Type
```bash
# Check for OOMKilled
kubectl describe pod <pod-name> -n production | grep -i oom

# Check for resource exhaustion
kubectl top pod -n production -l app=polln-colony

# Check for deadlock
kubectl exec -it deploy/polln-colony -n production -- node --inspect-brk
```

### 3. Check Dependencies
```bash
# LMCache backend
kubectl exec -it deploy/polln-colony -n production -- curl -s http://lmcache:8080/health

# Federated learning
kubectl exec -it deploy/polln-colony -n production -- curl -s http://federated:8081/health

# World model service
kubectl exec -it deploy/polln-colony -n production -- curl -s http://worldmodel:8082/health
```

## Resolution Steps

### Scenario A: Resource Exhaustion (OOM)
```bash
# Scale up resources
kubectl set resources deployment/polln-colony -n production \
  --limits=memory=8Gi,cpu=4 \
  --requests=memory=4Gi,cpu=2

# Restart with drain
kubectl rollout restart deployment/polln-colony -n production
```

### Scenario B: Deadlock in Agent Network
```bash
# Enable debug mode
kubectl set env deployment/polln-colony -n production DEBUG=deadlock

# Force agent reload
kubectl exec -it deploy/polln-colony -n production -- npm run cli reload --force

# Monitor recovery
kubectl logs -f deploy/polln-colony -n production --since=1m
```

### Scenario C: Dependency Failure
```bash
# Check and restart failed dependencies
kubectl rollout restart deployment/lmcache -n production
kubectl rollout restart deployment/federated -n production
kubectl rollout restart deployment/worldmodel -n production

# Wait for dependencies
kubectl wait --for=condition=ready pod -l app=polln-colony -n production --timeout=300s
```

### Scenario D: Data Corruption
```bash
# Restore from last backup
kubectl exec -it deploy/polln-colony -n production -- npm run cli restore --backup=latest

# Verify state
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate

# If restore fails, failover to standby
kubectl scale statefulset/polln-colony-standby -n production --replicas=1
```

## Verification

```bash
# Health check
curl -f http://polln-production.example.com/health || exit 1

# Agent count
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --count | grep -q "active"

# Dream cycle active
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --status | grep -q "running"
```

## Post-Incident Actions

1. Update incident ticket with root cause
2. Add to postmortem tracker
3. Update runbook if new scenario discovered
4. Schedule follow-up in 24h
5. Update monitoring/alerting if gap identified

## Prevention

- Enable resource auto-scaling (HPA)
- Implement deadlock detection alerts
- Add dependency health checks
- Implement backup validation

## Related Runbooks
- [02-dependency-failure.md](./02-dependency-failure.md)
- [03-data-corruption.md](./03-data-corruption.md)
- [04-performance-degradation.md](./04-performance-degradation.md)

## Escalation Path

| Time | Action |
|------|--------|
| 0-5 min | Initial response, diagnose |
| 5-10 min | Implement fix, monitor |
| 10-15 min | Escalate if unresolved |
| 15+ min | Major incident, all-hands |

**Last Updated**: 2026-03-08
**Version**: 1.0
