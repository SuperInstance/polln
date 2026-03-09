# Runbook: Dependency Failure Incident

**Severity**: P2 - High
**Escalation**: @on-call -> @engineering-manager
**Target MTTR**: < 30 minutes

## Symptoms

- Partial colony degradation
- Specific features failing (KV-cache, dreaming, etc.)
- Upstream dependency errors
- Timeout errors in logs

## Diagnosis Steps

### 1. Identify Failed Dependency
```bash
# Check all dependencies
kubectl get pods -n production -l tier=dependency

# Check dependency health
for svc in lmcache federated worldmodel meadow; do
  echo "Checking $svc:"
  kubectl exec -it deploy/polln-colony -n production -- curl -s http://$svc:8080/health
done

# Check network policies
kubectl get networkpolicies -n production
```

### 2. Determine Failure Mode
```bash
# LMCache failure (KV-cache broken)
kubectl logs -f deploy/lmcache -n production --tail=50

# Federated learning failure (sync broken)
kubectl logs -f deploy/federated -n production --tail=50

# World model failure (dreaming broken)
kubectl logs -f deploy/worldmodel -n production --tail=50

# Meadow failure (community broken)
kubectl logs -f deploy/meadow -n production --tail=50
```

### 3. Check Circuit Breakers
```bash
# Check if circuit breakers tripped
kubectl exec -it deploy/polln-colony -n production -- npm run cli circuit --status

# Check fallback state
kubectl exec -it deploy/polln-colony -n production -- npm run cli fallback --list
```

## Resolution Steps

### Scenario A: LMCache Failure
```bash
# Restart LMCache
kubectl rollout restart deployment/lmcache -n production

# Clear corrupted cache
kubectl exec -it deploy/lmcache -n production -- npm run clear --force

# Verify KV-cache connectivity
kubectl exec -it deploy/polln-colony -n production -- npm run cli cache --test

# Colony will auto-fallback to local cache
```

### Scenario B: Federated Learning Failure
```bash
# Restart federated coordinator
kubectl rollout restart deployment/federated -n production

# Check sync status
kubectl exec -it deploy/polln-colony -n production -- npm run cli sync --status

# Force partial sync if needed
kubectl exec -it deploy/polln-colony -n production -- npm run cli sync --force --partial

# Colony continues in local mode
```

### Scenario C: World Model Failure
```bash
# Restart world model service
kubectl rollout restart deployment/worldmodel -n production

# Check VAE health
kubectl exec -it deploy/worldmodel -n production -- npm run health --vae

# Disable dreaming if critically degraded
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --disable

# Re-enable when stable
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --enable
```

### Scenario D: Meadow/Community Failure
```bash
# Restart meadow service
kubectl rollout restart deployment/meadow -n production

# Colony operates independently
kubectl exec -it deploy/polln-colony -n production -- npm run cli meadow --disconnect

# Reconnect when stable
kubectl exec -it deploy/polln-colony -n production -- npm run cli meadow --connect
```

### Scenario E: Network Partition
```bash
# Check network policies
kubectl describe networkpolicy polln-colony-net -n production

# Temporarily allow all for debugging
kubectl apply -f ops/network-emergency.yaml

# Re-establish connections
kubectl exec -it deploy/polln-colony -n production -- npm run cli reconnect

# Restore network policies
kubectl delete -f ops/network-emergency.yaml
```

## Verification

```bash
# Dependency health
for svc in lmcache federated worldmodel meadow; do
  curl -f http://$svc-production.example.com/health || exit 1
done

# Colony integration
kubectl exec -it deploy/polln-colony -n production -- npm run cli health --full

# Feature flags
kubectl exec -it deploy/polln-colony -n production -- npm run cli features --verify
```

## Graceful Degradation

The colony is designed to degrade gracefully:

| Dependency Lost | Impact | Fallback |
|----------------|--------|----------|
| LMCache | KV-cache optimization disabled | Local cache only |
| Federated | Multi-colony sync disabled | Local learning |
| World Model | Dreaming disabled | Hebbian learning continues |
| Meadow | Community patterns disabled | Local patterns |

## Post-Incident Actions

1. Update dependency health SLAs
2. Review circuit breaker thresholds
3. Add monitoring for early detection
4. Update fallback documentation
5. Test failover procedures

## Prevention

- Implement dependency health dashboards
- Add circuit breaker alerts
- Implement graceful degradation tests
- Add dependency SLA monitoring

## Related Runbooks
- [01-colony-crash.md](./01-colony-crash.md)
- [05-network-partition.md](./05-network-partition.md)

## Escalation Path

| Time | Action |
|------|--------|
| 0-10 min | Identify failed dependency |
| 10-20 min | Implement fix or fallback |
| 20-30 min | Escalate if unresolved |

**Last Updated**: 2026-03-08
**Version**: 1.0
