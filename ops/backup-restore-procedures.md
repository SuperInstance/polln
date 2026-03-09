# Backup and Restore Procedures

**Version**: 1.0
**Last Updated**: 2026-03-08
**Owner**: SRE Team

## Overview

This document provides detailed procedures for backing up and restoring POLLN Colony data. These procedures are critical for disaster recovery, data migration, and operational maintenance.

---

## Backup Architecture

### Backup Locations

```
Primary Region (us-east-1)
├── S3 Primary Bucket (polln-backups-us-east-1)
│   ├── Continuous/        # WAL logs, 24h retention
│   ├── Frequent/          # 5-min backups, 30d retention
│   ├── Daily/             # Daily snapshots, 90d retention
│   └── Weekly/            # Weekly archives, 1y retention
└── RDS Automated Backups
    ├── Transaction logs   # Continuous, 7d retention
    └── Snapshots          # Daily, 35d retention

DR Region (us-west-2)
├── S3 DR Bucket (polln-backups-us-west-2)
│   └── [Cross-region replication]
└── RDS Standby
    └── [Replicated from primary]
```

### Backup Components

| Component | Method | Frequency | Retention | Location |
|-----------|--------|-----------|-----------|----------|
| Colony State | S3 Versioning | Continuous | 30 days | Primary + DR |
| Agent Topology | DB Dump | 5 min | 30 days | Primary + DR |
| Synapse Weights | DB Dump | 5 min | 30 days | Primary + DR |
| World Model | S3 Versioning | 5 min | 30 days | Primary + DR |
| KV Anchors | S3 Versioning | 5 min | 30 days | Primary + DR |
| Federated State | DB Dump | 5 min | 30 days | Primary + DR |
| Meadow Patterns | S3 Versioning | Hourly | 30 days | Primary + DR |
| Configuration | Git | Per commit | Indefinite | GitHub |
| Logs | CloudWatch | Continuous | 7 days | Primary |

---

## Automated Backup Procedures

### 1. Continuous Backups (WAL Logs)

**Purpose**: Point-in-time recovery
**RPO**: < 1 minute
**Retention**: 24 hours

```bash
# WAL logs are automatically shipped to S3
# Configured in RDS parameter group

# Verify WAL log shipping
aws rds describe-db-instances \
  --db-instance-identifier polln-db \
  --query '*[].[DBInstanceIdentifier,EnabledCloudwatchLogsExports]'

# Check WAL log retention
aws rds describe-db-instances \
  --db-instance-identifier polln-db \
  --query '*[].[DBInstanceIdentifier,BackupRetentionPeriod]'
```

### 2. Frequent Automated Backups

**Purpose**: Standard recovery
**RPO**: 5 minutes
**Retention**: 30 days

```bash
# Automated via Kubernetes CronJob
# Location: k8s/backup/frequent-backup-cronjob.yaml

# Manually trigger backup
kubectl create job backup-$(date +%Y%m%d-%H%M%S) \
  -n production \
  --from=cronjob/polln-frequent-backup

# Check backup status
kubectl get jobs -n production -l app=polln-backup

# View backup logs
kubectl logs -f job/backup-<timestamp> -n production
```

### 3. Daily Snapshot Backups

**Purpose**: Long-term recovery
**RPO**: 24 hours
**Retention**: 90 days

```bash
# Automated via Kubernetes CronJob
# Location: k8s/backup/daily-backup-cronjob.yaml

# Manually trigger snapshot
kubectl create job snapshot-$(date +%Y%m%d) \
  -n production \
  --from=cronjob/polln-daily-snapshot

# List snapshots
aws s3 ls s3://polln-backups-us-east-1/Daily/ | tail -30

# Verify snapshot integrity
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --verify --id=<snapshot-id>
```

### 4. Weekly Archive Backups

**Purpose**: Compliance, archival
**RPO**: 7 days
**Retention**: 1 year

```bash
# Automated via Kubernetes CronJob
# Location: k8s/backup/weekly-archive-cronjob.yaml

# Manually trigger archive
kubectl create job archive-$(date +%Y%m%d) \
  -n production \
  --from=cronjob/polln-weekly-archive

# List archives
aws s3 ls s3://polln-backups-us-east-1/Weekly/ | tail -52

# Verify archive in Glacier
aws s3 ls s3://polln-backups-us-east-1/Weekly/ --recursive
```

---

## Manual Backup Procedures

### On-Demand Full Backup

**Use Case**: Before major changes, migrations

```bash
# Trigger full backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --full --manual --reason="Pre-migration"

# Backup includes:
# - Colony state
# - Agent topology
# - Synapse weights
# - World model
# - KV anchors
# - Federated state
# - Configuration

# View backup details
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --info --id=<backup-id>
```

### Component-Specific Backup

**Use Case**: Backup specific components

```bash
# Backup agent topology only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --agents

# Backup synapse weights only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --synapses

# Backup world model only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --worldmodel

# Backup KV anchors only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --anchors
```

### Emergency Backup

**Use Case**: Before critical operations, suspected corruption

```bash
# Create emergency backup with highest priority
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --emergency --priority=critical

# This will:
# - Stop all writes
# - Flush all caches
# - Create consistent snapshot
# - Verify integrity
# - Upload to multiple regions
# - Notify on-call
```

---

## Backup Verification

### Automated Verification

```bash
# Daily automated verification (via CronJob)
kubectl get cronjobs -n production -l app=polln-backup-verify

# Manual verification
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --verify --latest

# Verify specific backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --verify --id=<backup-id>

# Verify all backups in window
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --verify --since="24h"
```

### Verification Checklist

- [ ] Backup exists in S3
- [ ] Backup size is reasonable
- [ ] Backup checksum matches
- [ ] Backup can be downloaded
- [ ] Backup passes integrity check
- [ ] Backup replicated to DR region
- [ ] Backup metadata is correct

---

## Restore Procedures

### Prerequisites

1. **Verify Backup**
   ```bash
   # List available backups
   kubectl exec -it deploy/polln-colony -n production \
     -- npm run cli backup --list

   # Verify specific backup
   kubectl exec -it deploy/polln-colony -n production \
     -- npm run cli backup --verify --id=<backup-id>
   ```

2. **Prepare Environment**
   ```bash
   # Stop colony (optional, for consistency)
   kubectl scale deployment/polln-colony -n production --replicas=0

   # Create restore job
   kubectl create job restore-$(date +%Y%m%d-%H%M%S) \
     -n production \
     --from=cronjob/polln-restore
   ```

### Full Restore

**Use Case**: Complete disaster recovery

```bash
# Restore from latest backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --full --backup=latest

# Restore from specific backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --full --backup=<backup-id>

# Restore with point-in-time recovery
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --full --pitr --timestamp="2026-03-08T12:00:00Z"

# Restore from DR region backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --full --backup=<dr-backup-id> --from-region=us-west-2
```

### Component-Specific Restore

**Use Case**: Restore specific components

```bash
# Restore agent topology only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --agents --backup=<backup-id>

# Restore synapse weights only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --synapses --backup=<backup-id>

# Restore world model only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --worldmodel --backup=<backup-id>

# Restore KV anchors only
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --anchors --backup=<backup-id>
```

### Point-in-Time Recovery

**Use Case**: Recover to specific point in time

```bash
# List available restore points
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --list-pitr --since="24h"

# Restore to specific timestamp
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --pitr --timestamp="2026-03-08T12:00:00Z"

# Restore to before specific transaction
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --pitr --before-transaction=<tx-id>

# Restore to after specific transaction
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli restore --pitr --after-transaction=<tx-id>
```

### Validation After Restore

```bash
# Validate restored data
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli validate --full

# Compare with backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli compare --with-backup=<backup-id>

# Test colony operations
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli test --smoke

# Monitor for issues
kubectl logs -f deploy/polln-colony -n production --since=10m
```

---

## Backup Lifecycle Management

### Retention Policy

| Backup Type | Retention | Archive Location |
|-------------|-----------|------------------|
| WAL Logs | 24 hours | Deleted |
| Frequent Backups | 30 days | S3 Standard |
| Daily Snapshots | 90 days | S3 Standard → Glacier after 30d |
| Weekly Archives | 1 year | S3 Glacier |
| Yearly Archives | 7 years | S3 Glacier Deep Archive |

### Automated Lifecycle Rules

```bash
# View lifecycle rules
aws s3api get-bucket-lifecycle-configuration \
  --bucket polln-backups-us-east-1

# Lifecycle rules:
# 1. Delete WAL logs after 24 hours
# 2. Transition daily snapshots to Glacier after 30 days
# 3. Delete daily snapshots after 90 days
# 4. Keep weekly archives in Glacier for 1 year
# 5. Transition yearly archives to Glacier Deep Archive after 1 year
# 6. Delete yearly archives after 7 years
```

### Backup Cleanup

```bash
# Manual cleanup of old backups
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --cleanup --older-than=90d

# Cleanup specific backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --delete --id=<backup-id>

# Cleanup failed backups
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --cleanup --failed
```

---

## Monitoring and Alerting

### Backup Metrics

```bash
# View backup metrics
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --metrics

# Metrics include:
# - Backup success rate
# - Backup duration
# - Backup size
# - Backup age
# - Restore success rate
# - Restore duration
```

### Backup Alerts

**Critical Alerts**:
- Backup failed for 2 consecutive attempts
- No successful backup in 1 hour
- Backup verification failed
- Backup not replicated to DR region

**Warning Alerts**:
- Backup duration > 10 minutes
- Backup size > 110% of average
- Backup age > 15 minutes

---

## Backup Best Practices

### Before Major Changes
1. Create emergency backup
2. Verify backup integrity
3. Test restore procedure
4. Document backup ID

### Regular Maintenance
1. Review backup retention policy
2. Clean up old backups
3. Verify lifecycle rules
4. Test restore procedures

### Disaster Recovery
1. Use latest verified backup
2. Verify backup before restore
3. Validate after restore
4. Monitor for issues

---

## Troubleshooting

### Backup Fails

**Symptoms**: Backup job fails, errors in logs

**Diagnosis**:
```bash
# Check backup job status
kubectl get jobs -n production -l app=polln-backup

# View backup logs
kubectl logs -f job/backup-<timestamp> -n production

# Check disk space
kubectl exec -it deploy/polln-colony -n production -- df -h
```

**Resolution**:
1. Check available storage
2. Retry backup
3. Check network connectivity
4. Verify S3 permissions

### Restore Fails

**Symptoms**: Restore job fails, errors in logs

**Diagnosis**:
```bash
# Check restore job status
kubectl get jobs -n production -l app=polln-restore

# View restore logs
kubectl logs -f job/restore-<timestamp> -n production

# Verify backup integrity
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --verify --id=<backup-id>
```

**Resolution**:
1. Verify backup exists and is valid
2. Check available storage
3. Try restoring from earlier backup
4. Contact SRE team

### Backup Verification Fails

**Symptoms**: Verification job fails, checksum mismatch

**Diagnosis**:
```bash
# Check verification logs
kubectl logs -f job/verify-<timestamp> -n production

# Manually verify backup
kubectl exec -it deploy/polln-colony -n production \
  -- npm run cli backup --verify --id=<backup-id> --verbose
```

**Resolution**:
1. Check for data corruption
2. Verify network integrity
3. Create new backup
4. Delete corrupted backup

---

## Related Documents
- [Disaster Recovery Plan](./disaster-recovery.md)
- [Runbooks](../runbooks/03-data-corruption.md)
- [SLOs](../slos/service-level-objectives.md)

---

**Approval**:
- **SRE Lead**: ______________________
- **Engineering Director**: ______________________

**Last Updated**: 2026-03-08
**Next Review**: 2026-06-08
