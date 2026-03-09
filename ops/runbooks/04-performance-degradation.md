# Runbook: Performance Degradation Incident

**Severity**: P3 - Medium
**Escalation**: @on-call
**Target MTTR**: < 45 minutes

## Symptoms

- High latency responses
- Slow agent decision making
- Dream cycle taking too long
- Memory/CPU usage elevated
- SLA violations

## Diagnosis Steps

### 1. Identify Bottleneck
```bash
# Check resource usage
kubectl top pod -n production -l app=polln-colony

# Check agent performance
kubectl exec -it deploy/polln-colony -n production -- npm run cli perf --agents

# Check dreaming performance
kubectl exec -it deploy/polln-colony -n production -- npm run cli perf --dream

# Check KV-cache performance
kubectl exec -it deploy/polln-colony -n production -- npm run cli perf --cache
```

### 2. Profile Colony
```bash
# Enable profiling
kubectl exec -it deploy/polln-colony -n production -- npm run cli profile --enable

# Generate flame graph
kubectl exec -it deploy/polln-colony -n production -- npm run cli profile --flamegraph

# Check memory allocation
kubectl exec -it deploy/polln-colony -n production -- npm run cli profile --memory

# Check event loop lag
kubectl exec -it deploy/polln-colony -n production -- npm run cli profile --eventloop
```

### 3. Check External Factors
```bash
# Check network latency
kubectl exec -it deploy/polln-colony -n production -- ping -c 10 lmcache.production.svc.cluster.local

# Check dependency performance
for svc in lmcache federated worldmodel meadow; do
  echo "Latency to $svc:"
  kubectl exec -it deploy/polln-colony -n production -- curl -w "@-" -o /dev/null -s http://$svc:8080/health <<< 'time_total: %{time_total}s\n'
done

# Check disk I/O
kubectl exec -it deploy/polln-colony -n production -- iostat -x 1 5
```

## Resolution Steps

### Scenario A: Agent Explosion (Too Many Agents)
```bash
# Check agent count
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --count

# Kill idle agents
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --prune --idle=1h

# Limit agent spawning
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --limit --max=1000

# Monitor recovery
kubectl exec -it deploy/polln-colony -n production -- npm run cli perf --watch
```

### Scenario B: Memory Leak
```bash
# Identify memory hog
kubectl exec -it deploy/polln-colony -n production -- npm run cli profile --memory --top

# Force garbage collection
kubectl exec -it deploy/polln-colony -n production -- npm run cli gc --force

# Clear caches
kubectl exec -it deploy/polln-colony -n production -- npm run cli cache --clear --all

# Restart if leak persists
kubectl rollout restart deployment/polln-colony -n production

# Add memory limit increase if needed
kubectl set resources deployment/polln-colony -n production --limits=memory=16Gi
```

### Scenario C: Synapse Bloat
```bash
# Check synapse count
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --count

# Prune weak synapses
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --prune --threshold=0.1

# Cluster similar agents
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --cluster

# Verify topology
kubectl exec -it deploy/polln-colony -n production -- npm run cli topology --check
```

### Scenario D: Dream Cycle Saturation
```bash
# Check dream status
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --status

# Reduce dream frequency
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --config --interval=6h

# Limit dream iterations
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --config --max-iterations=100

# Disable dreaming temporarily
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --disable

# Re-enable when stable
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --enable
```

### Scenario E: KV-Cache Saturation
```bash
# Check anchor pool size
kubectl exec -it deploy/polln-colony -n production -- npm run cli anchors --stats

# Evict old anchors
kubectl exec -it deploy/polln-colony -n production -- npm run cli anchors --evict --older-than=24h

# Reduce anchor quality threshold
kubectl exec -it deploy/polln-colony -n production -- npm run cli anchors --config --quality-threshold=0.7

# Clear ANN index
kubectl exec -it deploy/polln-colony -n production -- npm run cli ann --clear

# Rebuild index
kubectl exec -it deploy/polln-colony -n production -- npm run cli ann --rebuild
```

### Scenario F: Network Contention
```bash
# Check network policies
kubectl get networkpolicies -n production

# Enable compression
kubectl exec -it deploy/polln-colony -n production -- npm run cli config --compression=true

# Reduce sync frequency
kubectl exec -it deploy/polln-colony -n production -- npm run cli sync --config --interval=5m

# Disconnect from meadow temporarily
kubectl exec -it deploy/polln-colony -n production -- npm run cli meadow --disconnect

# Reconnect when stable
kubectl exec -it deploy/polln-colony -n production -- npm run cli meadow --connect
```

### Scenario G: Hot Partition
```bash
# Identify hot partition
kubectl exec -it deploy/polln-colony -n production -- npm run cli topology --hot

# Rebalance agents
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --rebalance

# Enable agent migration
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --migrate --enable

# Monitor redistribution
kubectl exec -it deploy/polln-colony -n production -- npm run cli topology --watch
```

## Auto-Scaling

```bash
# Horizontal Pod Autoscaler
kubectl autoscale deployment/polln-colony -n production \
  --min=3 --max=10 \
  --cpu-percent=70 \
  --memory-percent=80

# Check HPA status
kubectl get hpa -n production
```

## Verification

```bash
# Performance baseline
kubectl exec -it deploy/polln-colony -n production -- npm run cli perf --baseline

# SLA check
kubectl exec -it deploy/polln-colony -n production -- npm run cli sla --check

# Load test (careful in production)
kubectl exec -it deploy/polln-colony -n production -- npm run cli loadtest --rps=100 --duration=30s
```

## Performance Baselines

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Agent decision latency | < 100ms | > 500ms |
| Dream cycle duration | < 5min | > 15min |
| KV-cache lookup | < 10ms | > 50ms |
| Memory per agent | < 10MB | > 50MB |
| Event loop lag | < 10ms | > 100ms |

## Post-Incident Actions

1. Update performance baselines
2. Add auto-scaling rules
3. Review resource limits
4. Add performance alerts
5. Optimize hot paths
6. Document lessons learned

## Prevention

- Implement auto-scaling (HPA/VPA)
- Add performance monitoring
- Implement circuit breakers
- Add rate limiting
- Implement caching strategies
- Add load shedding capabilities

## Related Runbooks
- [01-colony-crash.md](./01-colony-crash.md)
- [02-dependency-failure.md](./02-dependency-failure.md)

## Escalation Path

| Time | Action |
|------|--------|
| 0-15 min | Identify bottleneck |
| 15-30 min | Implement optimization |
| 30-45 min | Escalate if unresolved |

**Last Updated**: 2026-03-08
**Version**: 1.0
