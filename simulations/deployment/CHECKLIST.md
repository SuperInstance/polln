# Pre-Deployment Checklist

Comprehensive verification checklist before executing any deployment.

## General Checklist

### Planning
- [ ] Deployment strategy selected (Rolling/Blue-Green/Canary)
- [ ] Risk assessment completed (Low/Medium/High)
- [ ] Rollback plan documented
- [ ] Deployment window scheduled
- [ ] Stakeholders notified

### Code Readiness
- [ ] Code reviewed and approved
- [ ] All tests passing (unit, integration, e2e)
- [ ] Test coverage meets threshold (> 80%)
- [ ] No critical bugs or known issues
- [ ] Performance benchmarks met

### Documentation
- [ ] Changelog updated
- [ ] Release notes prepared
- [ ] API documentation updated (if applicable)
- [ ] Runbook updated
- [ ] Migration guides prepared (if needed)

---

## Rolling Deployment Checklist

### Pre-Deployment
- [ ] Current deployment healthy
- [ ] Sufficient capacity for batch updates
- [ ] Health checks configured and tested
- [ ] Batch sizes determined (1%, 5%, 10%, 25%, 50%, 100%)
- [ ] Auto-rollback enabled

### Health Checks
- [ ] Readiness probe configured
  - [ ] Path: `/health/ready`
  - [ ] Timeout: < 3s
  - [ ] Threshold: 3 failures
- [ ] Liveness probe configured
  - [ ] Path: `/health/live`
  - [ ] Timeout: < 5s
  - [ ] Threshold: 3 failures
- [ ] Custom metrics configured
  - [ ] Error rate < 1%
  - [ ] Latency P99 < 500ms
  - [ ] Throughput > baseline

### During Deployment
- [ ] Monitor batch success rate
- [ ] Monitor error rate (< 1%)
- [ ] Monitor latency (P50, P95, P99)
- [ ] Monitor CPU/memory usage
- [ ] Verify each batch before proceeding

### Post-Deployment
- [ ] All instances updated
- [ ] Health checks passing (100%)
- [ ] Error rate normal (< 0.1%)
- [ ] Performance baseline maintained
- [ ] No increase in errors or latency

---

## Blue-Green Deployment Checklist

### Pre-Deployment
- [ ] Blue environment healthy and stable
- [ ] Green environment provisioned
- [ ] Sufficient resources for 2x capacity
- [ ] Database migration plan (if needed)
- [ ] State synchronization plan

### Green Environment Setup
- [ ] New version deployed to green
- [ ] Smoke tests configured
  - [ ] Basic functionality
  - [ ] Database connectivity
  - [ ] External service connectivity
- [ ] Load testing configured
- [ ] Monitoring configured for green

### Testing Phase
- [ ] Health checks passing (green)
- [ ] Smoke tests passing (100%)
- [ ] Load tests passing (target RPS)
- [ ] Error rate < 1% (green)
- [ ] Latency within baseline (green)

### Traffic Cutover
- [ ] Load balancer configured
- [ ] DNS ready (if applicable)
- [ ] Traffic switching automated
- [ ] Rollback automation ready
- [ ] Monitoring alerts configured

### Post-Cutover
- [ ] Traffic fully switched to green
- [ ] Blue environment kept warm (for rollback)
- [ ] Monitor for 15+ minutes
- [ ] Clean up blue (after validation period)

---

## Canary Deployment Checklist

### Pre-Deployment
- [ ] Baseline metrics captured
  - [ ] Error rate
  - [ ] Latency (P50, P95, P99)
  - [ ] Throughput
  - [ ] CPU/memory usage
- [ ] Canary instances provisioned
- [ ] Monitoring dashboards ready
- [ ] Alert thresholds configured

### Regression Detection
- [ ] Error rate threshold: 2x baseline
- [ ] Latency threshold: 1.5x baseline
- [ ] CPU threshold: 1.5x baseline
- [ ] Minimum sample size: 100 requests
- [ ] Detection interval: 10s

### Canary Stages
- [ ] **Stage 1: 1% traffic**
  - [ ] Deploy canary instances
  - [ ] Monitor for 5 minutes
  - [ ] No regressions detected
  - [ ] Proceed to next stage

- [ ] **Stage 2: 5% traffic**
  - [ ] Increase canary to 5%
  - [ ] Monitor for 5 minutes
  - [ ] No regressions detected
  - [ ] Proceed to next stage

- [ ] **Stage 3: 25% traffic**
  - [ ] Increase canary to 25%
  - [ ] Monitor for 5 minutes
  - [ ] No regressions detected
  - [ ] Proceed to next stage

- [ ] **Stage 4: 100% traffic**
  - [ ] Full rollout
  - [ ] Monitor for 15+ minutes
  - [ ] No regressions detected
  - [ ] Mark as successful

### Rollback Triggers
- [ ] Automatic rollback configured
- [ ] Manual rollback procedure tested
- [ ] Rollback time < 30s
- [ ] State consistency verified

---

## Database Migration Checklist

### Pre-Migration
- [ ] Migration script reviewed
- [ ] Backward-compatible changes
- [ ] Rollback script prepared
- [ ] Test data prepared
- [ ] Backup completed

### Testing
- [ ] Migration tested in staging
- [ ] Data integrity verified
- [ ] Performance impact measured
- [ ] Rollback tested
- [ ] Application tested with new schema

### Execution
- [ ] Maintenance window scheduled
- [ ] Dependent services notified
- [ ] Migration executed
- [ ] Data integrity verified
- [ ] Application restarted

### Post-Migration
- [ ] Performance baseline verified
- [ ] No data corruption
- [ ] No application errors
- [ ] Monitor for 24+ hours
- [ ] Old backup retained

---

## Emergency Hotfix Checklist

### Assessment
- [ ] Severity level confirmed (Critical/High)
- [ ] Impact scope identified
- [ ] Root cause understood
- [ ] Fix developed and tested
- [ ] Risk assessed

### Deployment
- [ ] Blue-green strategy selected
- [ ] Fast-track approval obtained
- [ ] Pre-deployment checks accelerated
- [ ] Deployment executed immediately
- [ ] Verification streamlined

### Validation
- [ ] Fix verified in production
- [ ] Symptoms resolved
- [ ] No new issues introduced
- [ ] Monitor for 1+ hour
- [ ] Post-mortem scheduled

---

## Monitoring & Alerts Checklist

### Pre-Deployment
- [ ] Monitoring dashboards prepared
- [ ] Alert thresholds configured
- [ ] On-call engineer notified
- [ ] Runbook available
- [ ] Communication channels open

### During Deployment
- [ ] Real-time metrics monitored
- [ ] Error rate < 1%
- [ ] Latency within baseline
- [ ] CPU/memory < 80%
- [ ] No critical alerts

### Post-Deployment
- [ ] Extended monitoring (1+ hour)
- [ ] Performance validated
- [ ] User feedback monitored
- [ ] Metrics documented
- [ ] Alerts reset to normal

---

## Rollback Checklist

### Pre-Rollback
- [ ] Rollback decision made
- [ ] Rollback strategy selected
- [ ] Stakeholders notified
- [ ] Rollback plan confirmed
- [ ] State snapshot identified

### During Rollback
- [ ] Rollback executed
- [ ] Traffic redirected
- [ ] State restored (if needed)
- [ ] Old version active
- [ ] Rollback time measured

### Post-Rollback
- [ ] System stability verified
- [ ] Error rate normal
- [ ] Performance baseline restored
- [ ] State consistency verified
- [ ] Post-mortem initiated

---

## Post-Deployment Checklist

### Immediate (0-15 minutes)
- [ ] Deployment marked successful
- [ ] Health checks passing (100%)
- [ ] Error rate normal
- [ ] Performance baseline maintained
- [ ] No critical alerts

### Short-term (15-60 minutes)
- [ ] Extended monitoring
- [ ] User feedback collected
- [ ] Metrics documented
- [ ] No regression detected
- [ ] Stakeholders informed

### Long-term (24+ hours)
- [ ] Stable operation confirmed
- [ ] Performance validated
- [ ] Documentation updated
- [ ] Runbook updated
- [ ] Post-mortem completed (if needed)

---

## Risk Assessment Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Deployment failure | Low | High | Auto-rollback enabled |
| Performance regression | Medium | High | Canary deployment |
| Data corruption | Low | Critical | Database backups |
| Extended downtime | Low | High | Blue-green strategy |
| Rollback failure | Low | Critical | Rollback tested |
| Monitoring gap | Medium | Medium | Comprehensive alerts |

---

## Quick Reference

### Rolling Deployment
```
Total Time: 5-10 minutes
Downtime: < 1s
Rollback: < 30s
Best: Low-risk changes
```

### Blue-Green Deployment
```
Total Time: 5-15 minutes
Downtime: < 0.5s
Rollback: < 0.5s
Best: Emergency fixes
```

### Canary Deployment
```
Total Time: 20-30 minutes
Downtime: 0s
Rollback: < 30s
Best: Major releases
```

---

## Final Verification

Before clicking "Deploy", verify:

- [ ] All relevant checklists completed
- [ ] Strategy appropriate for risk level
- [ ] Rollback plan tested
- [ ] On-call engineer ready
- [ ] Monitoring active
- [ ] Stakeholders informed

**Only proceed if ALL items are checked.**

---

*Remember: A failed deployment is better than a broken production system.*
*When in doubt, rollback first, investigate later.*
