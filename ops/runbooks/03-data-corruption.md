# Runbook: Data Corruption Incident

**Severity**: P0 - Critical
**Escalation**: @on-call -> @engineering-manager -> @cto -> @ceo
**Target MTTR**: < 60 minutes

## Symptoms

- Agents behaving unexpectedly
- Nonsensical outputs
- Synapse weights NaN or infinite
- World model artifacts corrupted
- Validation failures

## Diagnosis Steps

### 1. Detect Corruption Type
```bash
# Check synapse weights
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --synapses

# Check world model
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --worldmodel

# Check KV-cache anchors
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --anchors

# Check federated state
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --federated
```

### 2. Identify Corruption Scope
```bash
# Agent-level corruption
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --health | grep unhealthy

# Synapse-level corruption
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --check --nan

# Knowledge-level corruption
kubectl exec -it deploy/polln-colony -n production -- npm run cli knowledge --integrity
```

### 3. Check Backup Integrity
```bash
# List available backups
kubectl exec -it deploy/polln-colony -n production -- npm run cli backup --list

# Verify backup integrity
kubectl exec -it deploy/polln-colony -n production -- npm run cli backup --verify --id=<backup-id>

# Check backup age
kubectl exec -it deploy/polln-colony -n production -- npm run cli backup --list --sort=time
```

## Resolution Steps

### Scenario A: Agent State Corruption
```bash
# Kill corrupted agents
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --kill --unhealthy

# Spawn replacements
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --spawn --count=<killed>

# Restore from checkpoint
kubectl exec -it deploy/polln-colony -n production -- npm run cli restore --checkpoint --latest

# Verify behavior
kubectl exec -it deploy/polln-colony -n production -- npm run cli agents --test
```

### Scenario B: Synapse Weight Corruption
```bash
# Rollback synapse state
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --rollback --hours=1

# Reset corrupted weights
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --reset --nan

# Reinitialize Hebbian learning
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --reinit

# Monitor recovery
kubectl exec -it deploy/polln-colony -n production -- npm run cli synapses --watch
```

### Scenario C: World Model Corruption
```bash
# Restore world model
kubectl exec -it deploy/polln-colony -n production -- npm run cli worldmodel --restore --backup=latest

# Disable dreaming if corrupted
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --disable

# Rebuild VAE
kubectl exec -it deploy/polln-colony -n production -- npm run cli worldmodel --rebuild --vae

# Re-enable dreaming
kubectl exec -it deploy/polln-colony -n production -- npm run cli dream --enable
```

### Scenario D: KV-Cache Anchor Corruption
```bash
# Clear corrupted anchors
kubectl exec -it deploy/polln-colony -n production -- npm run cli anchors --clear --corrupted

# Rebuild ANN index
kubectl exec -it deploy/polln-colony -n production -- npm run cli ann --rebuild

# Restore from backup
kubectl exec -it deploy/polln-colony -n production -- npm run cli anchors --restore --backup=latest

# Verify compression
kubectl exec -it deploy/polln-colony -n production -- npm run cli anchors --test
```

### Scenario E: Federated State Corruption
```bash
# Disconnect from federation
kubectl exec -it deploy/polln-colony -n production -- npm run cli federated --disconnect

# Reset local state
kubectl exec -it deploy/polln-colony -n production -- npm run cli federated --reset --local

# Restore from local backup
kubectl exec -it deploy/polln-colony -n production -- npm run cli restore --backup=latest

# Rejoin federation
kubectl exec -it deploy/polln-colony -n production -- npm run cli federated --connect --sync
```

### Scenario F: Full Colony Corruption (Nuclear Option)
```bash
# ⚠️ LAST RESORT - Full colony reset

# 1. Emergency backup current state
kubectl exec -it deploy/polln-colony -n production -- npm run cli backup --emergency

# 2. Shutdown colony gracefully
kubectl scale deployment/polln-colony -n production --replicas=0

# 3. Clear all state
kubectl exec -it statefulset/polln-colony-db -n production -- rm -rf /data/*

# 4. Restore from last good backup
kubectl exec -it deploy/polln-colony -n production -- npm run cli restore --full --id=<good-backup>

# 5. Verify integrity
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --full

# 6. Restart colony
kubectl scale deployment/polln-colony -n production --replicas=3
```

## Verification

```bash
# Full integrity check
kubectl exec -it deploy/polln-colony -n production -- npm run cli validate --full

# Test agent behavior
kubectl exec -it deploy/polln-colony -n production -- npm run cli test --agents

# Test dreaming
kubectl exec -it deploy/polln-colony -n production -- npm run cli test --dream

# Test federated sync
kubectl exec -it deploy/polln-colony -n production -- npm run cli test --federated
```

## Data Recovery Priorities

1. **Agent Topology** (critical) - colony structure
2. **Synapse Weights** (critical) - learned behavior
3. **World Model** (high) - dreaming capability
4. **KV Anchors** (medium) - optimization cache
5. **Meadow Patterns** (low) - community knowledge

## Post-Incident Actions

1. Root cause analysis (how did corruption occur?)
2. Update validation checks
3. Add corruption detection alerts
4. Review backup frequency
5. Test restore procedures
6. Update data integrity SLAs

## Prevention

- Implement continuous validation
- Add checksums for critical data
- Implement anomaly detection
- Add write-ahead logging
- Implement atomic transactions
- Add data versioning

## Related Runbooks
- [01-colony-crash.md](./01-colony-crash.md)
- [04-backup-restore.md](./04-backup-restore.md)
- [06-security-breach.md](./06-security-breach.md)

## Escalation Path

| Time | Action |
|------|--------|
| 0-5 min | Detect and isolate corruption |
| 5-15 min | Attempt targeted restore |
| 15-30 min | Escalate if partial restore fails |
| 30-60 min | Nuclear option if needed |
| 60+ min | Major incident, executive involvement |

**Last Updated**: 2026-03-08
**Version**: 1.0
