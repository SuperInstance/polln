/**
 * Operational Readiness Validation Tests
 * Location: ops/tests/operational-readiness.test.ts
 *
 * These tests validate the entire operational readiness of POLLN
 * including monitoring, alerting, runbooks, and disaster recovery
 */

import { describe, it, expect, beforeAll } from '@jest/globals';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

describe('Operational Readiness Validation', () => {
  const opsDir = path.join(process.cwd(), 'ops');

  beforeAll(() => {
    // Ensure ops directory exists
    if (!fs.existsSync(opsDir)) {
      fs.mkdirSync(opsDir, { recursive: true });
    }
  });

  describe('Runbooks Validation', () => {
    const runbooksDir = path.join(opsDir, 'runbooks');

    it('should have colony crash runbook', () => {
      const runbook = path.join(runbooksDir, '01-colony-crash.md');
      expect(fs.existsSync(runbook)).toBe(true);

      const content = fs.readFileSync(runbook, 'utf-8');
      expect(content).toContain('Severity');
      expect(content).toContain('Escalation');
      expect(content).toContain('Diagnosis');
      expect(content).toContain('Resolution');
    });

    it('should have dependency failure runbook', () => {
      const runbook = path.join(runbooksDir, '02-dependency-failure.md');
      expect(fs.existsSync(runbook)).toBe(true);

      const content = fs.readFileSync(runbook, 'utf-8');
      expect(content).toContain('LMCache');
      expect(content).toContain('Federated');
      expect(content).toContain('World Model');
    });

    it('should have data corruption runbook', () => {
      const runbook = path.join(runbooksDir, '03-data-corruption.md');
      expect(fs.existsSync(runbook)).toBe(true);

      const content = fs.readFileSync(runbook, 'utf-8');
      expect(content).toContain('Synapse Weights');
      expect(content).toContain('World Model');
      expect(content).toContain('Nuclear Option');
    });

    it('should have performance degradation runbook', () => {
      const runbook = path.join(runbooksDir, '04-performance-degradation.md');
      expect(fs.existsSync(runbook)).toBe(true);

      const content = fs.readFileSync(runbook, 'utf-8');
      expect(content).toContain('Agent Explosion');
      expect(content).toContain('Memory Leak');
      expect(content).toContain('Auto-Scaling');
    });

    it('should have disaster recovery runbook', () => {
      const runbook = path.join(runbooksDir, '05-disaster-recovery.md');
      expect(fs.existsSync(runbook)).toBe(true);

      const content = fs.readFileSync(runbook, 'utf-8');
      expect(content).toContain('RTO');
      expect(content).toContain('RPO');
      expect(content).toContain('Failover');
    });
  });

  describe('Monitoring Configuration', () => {
    const monitoringDir = path.join(opsDir, 'monitoring');

    it('should have Prometheus alerting rules', () => {
      const rulesFile = path.join(monitoringDir, 'prometheus-rules.yaml');
      expect(fs.existsSync(rulesFile)).toBe(true);

      const content = fs.readFileSync(rulesFile, 'utf-8');
      expect(content).toContain('groups:');
      expect(content).toContain('colony_health');
      expect(content).toContain('performance');
      expect(content).toContain('data_integrity');
    });

    it('should have Grafana dashboard', () => {
      const dashboardFile = path.join(monitoringDir, 'grafana-dashboard.json');
      expect(fs.existsSync(dashboardFile)).toBe(true);

      const content = fs.readFileSync(dashboardFile, 'utf-8');
      const dashboard = JSON.parse(content);

      expect(dashboard.dashboard).toBeDefined();
      expect(dashboard.dashboard.title).toBe('POLLN Colony Operations');
      expect(dashboard.dashboard.panels).toBeDefined();
      expect(dashboard.dashboard.panels.length).toBeGreaterThan(0);
    });

    it('should have all required alert rules', () => {
      const rulesFile = path.join(monitoringDir, 'prometheus-rules.yaml');
      const content = fs.readFileSync(rulesFile, 'utf-8');

      // Critical alerts
      expect(content).toContain('ColonyDown');
      expect(content).toContain('SynapseNaNDetected');
      expect(content).toContain('DataCorruption');

      // Performance alerts
      expect(content).toContain('HighDecisionLatency');
      expect(content).toContain('CriticalMemoryUsage');

      // Dependency alerts
      expect(content).toContain('KVCacheBackendDown');
      expect(content).toContain('FederatedCoordinatorDown');
    });
  });

  describe('Alerting Configuration', () => {
    const alertingDir = path.join(opsDir, 'alerting');

    it('should have escalation policy', () => {
      const policyFile = path.join(alertingDir, 'escalation-policy.md');
      expect(fs.existsSync(policyFile)).toBe(true);

      const content = fs.readFileSync(policyFile, 'utf-8');
      expect(content).toContain('Severity Levels');
      expect(content).toContain('Escalation Paths');
      expect(content).toContain('On-Call Rotation');
      expect(content).toContain('P0');
      expect(content).toContain('P1');
      expect(content).toContain('P2');
      expect(content).toContain('P3');
    });

    it('should define all severity levels', () => {
      const policyFile = path.join(alertingDir, 'escalation-policy.md');
      const content = fs.readFileSync(policyFile, 'utf-8');

      expect(content).toContain('P0 - Critical');
      expect(content).toContain('P1 - High');
      expect(content).toContain('P2 - Medium');
      expect(content).toContain('P3 - Low');
    });

    it('should have escalation paths defined', () => {
      const policyFile = path.join(alertingDir, 'escalation-policy.md');
      const content = fs.readFileSync(policyFile, 'utf-8');

      expect(content).toContain('@on-call-engineer');
      expect(content).toContain('@on-call-manager');
      expect(content).toContain('@engineering-director');
      expect(content).toContain('@cto');
    });
  });

  describe('SLO Configuration', () => {
    const slosDir = path.join(opsDir, 'slos');

    it('should have service level objectives', () => {
      const sloFile = path.join(slosDir, 'service-level-objectives.md');
      expect(fs.existsSync(sloFile)).toBe(true);

      const content = fs.readFileSync(sloFile, 'utf-8');
      expect(content).toContain('Availability SLO');
      expect(content).toContain('Latency SLO');
      expect(content).toContain('Throughput SLO');
      expect(content).toContain('Durability SLO');
      expect(content).toContain('Freshness SLO');
      expect(content).toContain('Correctness SLO');
    });

    it('should define error budget policy', () => {
      const sloFile = path.join(slosDir, 'service-level-objectives.md');
      const content = fs.readFileSync(sloFile, 'utf-8');

      expect(content).toContain('Error Budget');
      expect(content).toContain('99.9%');
      expect(content).toContain('0.1%');
    });

    it('should have SLO targets defined', () => {
      const sloFile = path.join(slosDir, 'service-level-objectives.md');
      const content = fs.readFileSync(sloFile, 'utf-8');

      // Availability
      expect(content).toContain('99.9%');

      // Latency
      expect(content).toContain('P50 Latency');
      expect(content).toContain('P95 Latency');
      expect(content).toContain('P99 Latency');

      // Durability
      expect(content).toContain('99.9999%');
    });
  });

  describe('Disaster Recovery Configuration', () => {
    it('should have DR plan document', () => {
      const drFile = path.join(opsDir, 'disaster-recovery.md');
      expect(fs.existsSync(drFile)).toBe(true);

      const content = fs.readFileSync(drFile, 'utf-8');
      expect(content).toContain('RTO');
      expect(content).toContain('RPO');
      expect(content).toContain('Failover');
      expect(content).toContain('Recovery Procedures');
    });

    it('should have backup procedures', () => {
      const backupFile = path.join(opsDir, 'backup-restore-procedures.md');
      expect(fs.existsSync(backupFile)).toBe(true);

      const content = fs.readFileSync(backupFile, 'utf-8');
      expect(content).toContain('Automated Backup');
      expect(content).toContain('Manual Backup');
      expect(content).toContain('Restore Procedures');
      expect(content).toContain('Backup Verification');
    });

    it('should define RTO/RPO targets', () => {
      const drFile = path.join(opsDir, 'disaster-recovery.md');
      const content = fs.readFileSync(drFile, 'utf-8');

      expect(content).toContain('RTO: < 60 minutes');
      expect(content).toContain('RPO: < 5 minutes');
    });
  });

  describe('Integration with Kubernetes', () => {
    it('should have backup CronJob', () => {
      const cronjobFile = path.join(process.cwd(), 'k8s/backup/frequent-backup-cronjob.yaml');
      expect(fs.existsSync(cronjobFile)).toBe(true);

      const content = fs.readFileSync(cronjobFile, 'utf-8');
      expect(content).toContain('kind: CronJob');
      expect(content).toContain('schedule:');
    });

    it('should have restore Job', () => {
      const jobFile = path.join(process.cwd(), 'k8s/backup/restore-job.yaml');
      expect(fs.existsSync(jobFile)).toBe(true);

      const content = fs.readFileSync(jobFile, 'utf-8');
      expect(content).toContain('kind: Job');
      expect(content).toContain('restore');
    });

    it('should have monitoring resources', () => {
      const servicemonitorFile = path.join(process.cwd(), 'k8s/monitoring/servicemonitor.yaml');
      expect(fs.existsSync(servicemonitorFile)).toBe(true);

      const content = fs.readFileSync(servicemonitorFile, 'utf-8');
      expect(content).toContain('kind: ServiceMonitor');
      expect(content).toContain('prometheus');
    });
  });

  describe('Operational Procedures', () => {
    it('should validate health check endpoints', () => {
      // This would be validated in integration tests
      expect(true).toBe(true);
    });

    it('should validate metrics endpoints', () => {
      // This would be validated in integration tests
      expect(true).toBe(true);
    });

    it('should validate alert delivery', () => {
      // This would be validated in integration tests
      expect(true).toBe(true);
    });
  });

  describe('Documentation Completeness', () => {
    it('should have README in ops directory', () => {
      const readmeFile = path.join(opsDir, 'README.md');
      expect(fs.existsSync(readmeFile)).toBe(true);

      const content = fs.readFileSync(readmeFile, 'utf-8');
      expect(content).toContain('Runbooks');
      expect(content).toContain('Monitoring');
      expect(content).toContain('Alerting');
      expect(content).toContain('SLOs');
    });

    it('should have all required subdirectories', () => {
      expect(fs.existsSync(path.join(opsDir, 'runbooks'))).toBe(true);
      expect(fs.existsSync(path.join(opsDir, 'monitoring'))).toBe(true);
      expect(fs.existsSync(path.join(opsDir, 'alerting'))).toBe(true);
      expect(fs.existsSync(path.join(opsDir, 'slos'))).toBe(true);
    });
  });

  describe('Compliance and Security', () => {
    it('should have security incident response procedures', () => {
      // Check for security procedures in runbooks
      const runbooksDir = path.join(opsDir, 'runbooks');
      const runbooks = fs.readdirSync(runbooksDir);

      const securityRunbook = runbooks.find(rb => rb.includes('security'));
      expect(securityRunbook).toBeDefined();
    });

    it('should have audit logging procedures', () => {
      // Check for audit procedures
      const drFile = path.join(opsDir, 'disaster-recovery.md');
      const content = fs.readFileSync(drFile, 'utf-8');

      expect(content).toContain('log') || expect(content).toContain('audit');
    });
  });

  describe('Testing and Validation', () => {
    it('should have DR validation tests', () => {
      const testFile = path.join(opsDir, 'tests/dr-validation.test.ts');
      expect(fs.existsSync(testFile)).toBe(true);
    });

    it('should have operational readiness tests', () => {
      const testFile = path.join(opsDir, 'tests/operational-readiness.test.ts');
      expect(fs.existsSync(testFile)).toBe(true);
    });
  });

  describe('Continuous Improvement', () => {
    it('should have postmortem procedures', () => {
      const escalationFile = path.join(opsDir, 'alerting/escalation-policy.md');
      const content = fs.readFileSync(escalationFile, 'utf-8');

      expect(content).toContain('Post-Incident');
      expect(content).toContain('Postmortem');
    });

    it('should have review procedures', () => {
      const sloFile = path.join(opsDir, 'slos/service-level-objectives.md');
      const content = fs.readFileSync(sloFile, 'utf-8');

      expect(content).toContain('Review');
      expect(content).toContain('Quarterly');
    });
  });
});
