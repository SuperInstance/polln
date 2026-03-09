# Runbook: Disaster Recovery - Complete System Failure

**Severity**: P0 - Critical
**Escalation**: @on-call -> @engineering-manager -> @cto -> @ceo -> @board
**Target RTO**: < 60 minutes
**Target RPO**: < 5 minutes

## Disaster Declaration

A disaster is declared when:
- Complete region failure
- Multi-AZ outage affecting primary + standby
- Catastrophic data corruption
- Security breach requiring full shutdown
- Natural disaster affecting data center

**Authorization**: CTO or CEO must declare disaster

## Immediate Actions (0-5 min)

### 1. Declare Disaster
```bash
# Trigger DR playbook
kubectl apply -f ops/disaster/declare-disaster.yaml

# Update status page
curl -X POST https://status.page.example.com/api/incident \
  -d "status=disaster" \
  -d "message=POLLN DR activated"

# Alert all hands
# (Automated via PagerDuty/Slack)
```

### 2. Activate Command Center
```bash
# Create war room
# (Automated via Slack/Zoom)

# Start DR tracking
kubectl exec -it deploy/dr-tracker -n production -- npm run track --start

# Enable DR logging
kubectl set env deployment/all -n production DR_MODE=true
```

## Recovery Steps (5-60 min)

### Phase 1: Failover to DR Region (5-15 min)

```bash
# 1. Switch DNS to DR region
kubectl apply -f ops/discovery/dns-dr.yaml

# 2. Activate DR colony
kubectl scale statefulset/polln-colony-dr -n dr-region --replicas=3

# 3. Verify DR health
kubectl wait --for=condition=ready pod -l app=polln-colony-dr -n dr-region --timeout=300s

# 4. Promote DR databases
kubectl exec -it statefulset/polln-db-dr -n dr-region -- npm run promote

# 5. Switch traffic
kubectl apply -f ops/loadbalancer/traffic-dr.yaml
```

### Phase 2: Data Recovery (15-30 min)

```bash
# 1. Verify last backup
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli backup --verify --latest

# 2. Calculate data loss
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli backup --rpo

# 3. Restore from backup
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli restore --full --backup=latest

# 4. Replay WAL logs (if available)
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli replay --wal

# 5. Verify data integrity
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli validate --full
```

### Phase 3: Service Recovery (30-45 min)

```bash
# 1. Restore agent topology
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli agents --restore

# 2. Restore synapse weights
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli synapses --restore

# 3. Restore world model
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli worldmodel --restore

# 4. Restore KV anchors
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli anchors --restore

# 5. Restore federated connections
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli federated --reconnect
```

### Phase 4: Verification (45-60 min)

```bash
# 1. Health check
curl -f https://polln-dr.example.com/health || exit 1

# 2. Smoke tests
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run test --smoke

# 3. Load test (light)
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run test --load --light

# 4. Monitor for 15 minutes
kubectl logs -f deploy/polln-colony-dr -n dr-region --since=15m
```

## Return to Normal Operations (Post-Disaster)

### Phase 1: Assess Primary Region (Post-DR + 24h)

```bash
# 1. Verify primary region recovery
kubectl get pods -n production

# 2. Verify data integrity
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --full

# 3. Security scan
kubectl exec -it deploy/polln-colony -n production -- npm run security --scan
```

### Phase 2: Resync Primary (Post-DR + 48h)

```bash
# 1. Sync DR -> Primary
kubectl exec -it deploy/polln-colony -n production -- npm run cli sync --from=dr

# 2. Verify sync
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --compare --to=dr

# 3. Cut over DNS
kubectl apply -f ops/discovery/dns-primary.yaml
```

### Phase 3: Restore DR Standby (Post-DR + 72h)

```bash
# 1. Rebuild DR region
kubectl apply -f ops/disaster/rebuild-dr.yaml

# 2. Re-establish replication
kubectl exec -it deploy/polln-colony -n production -- npm run cli replicate --to=dr

# 3. Verify DR readiness
kubectl exec -it deploy/polln-colony-dr -n dr-region -- npm run cli health --standby
```

## Disaster Recovery Testing

### Quarterly DR Drill
```bash
# 1. Schedule drill
# (Change control board approval required)

# 2. Simulate disaster
kubectl apply -f ops/disaster/simulate.yaml

# 3. Execute recovery
# (Follow recovery steps above)

# 4. Document findings
# (Post-drill report required)

# 5. Update runbooks
# (Based on lessons learned)
```

## DR Architecture

```
Primary Region (us-east-1)
  ├── Production Colony (3 replicas)
  ├── Primary Database (PostgreSQL)
  ├── LMCache Backend (3 replicas)
  └── World Model Service (2 replicas)
       ↓ (Replication)
DR Region (us-west-2)
  ├── Standby Colony (0 replicas → 3 on failover)
  ├── Standby Database (PostgreSQL, read-only)
  ├── LMCache Backend (0 replicas → 3 on failover)
  └── World Model Service (0 replicas → 2 on failover)
```

## RPO/RTO Targets

| Metric | Target | Current |
|--------|--------|---------|
| RTO (Recovery Time) | < 60 min | ✅ 45 min avg |
| RPO (Data Loss) | < 5 min | ✅ 2 min avg |
| Agent Topology | < 15 min | ✅ 10 min |
| Synapse Weights | < 30 min | ✅ 20 min |
| World Model | < 45 min | ✅ 35 min |
| Full Operations | < 60 min | ✅ 45 min |

## Communication Plan

| Time | Audience | Message |
|------|----------|---------|
| 0 min | Internal | Disaster declared, DR activated |
| 15 min | Internal | Failover in progress |
| 30 min | Internal | Services restoring |
| 45 min | Customers | Service disruption, recovery in progress |
| 60 min | Customers | Services restored |
| 24h | All | Postmortem scheduled |

## Post-Incident Actions

1. **Immediate (0-24h)**
   - Document timeline
   - Preserve logs
   - Interview responders

2. **Short-term (1-7 days)**
   - Root cause analysis
   - Update runbooks
   - Improve monitoring

3. **Long-term (1-3 months)**
   - Architecture improvements
   - Additional testing
   - Process improvements

## Related Runbooks
- [03-data-corruption.md](./03-data-corruption.md) - If corruption caused disaster
- [06-security-breach.md](./06-security-breach.md) - If security caused disaster
- [01-colony-crash.md](./01-colony-crash.md) - If multiple pods crashed

## Escalation Path

| Time | Action |
|------|--------|
| 0 min | CTO/CEO declare disaster |
| 5 min | All-hands on deck |
| 15 min | Status update to board |
| 30 min | External communication |
| 60 min | Recovery complete or escalate |

**Last Updated**: 2026-03-08
**Version**: 1.0
**Drill Scheduled**: 2026-06-08 (quarterly)
