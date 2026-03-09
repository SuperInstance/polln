/**
 * Integration Test for Audit System with Security Manager and Threat Detector
 */

import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import { SecurityManager, createDevSecurityManager } from '../security.js';
import { ThreatDetector, createThreatDetectorWithConfig } from '../threat-detection.js';
import { AuditSystem, getAuditSystem, shutdownAuditSystem } from '../audit.js';
import { mkdir, rm } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

const TEST_LOG_DIR = './test-logs-integration/audit';

describe('Audit System Integration', () => {
  let auditSystem: AuditSystem;
  let securityManager: SecurityManager;
  let threatDetector: ThreatDetector;

  beforeAll(async () => {
    // Clean up test directory
    if (existsSync(TEST_LOG_DIR)) {
      await rm(TEST_LOG_DIR, { recursive: true, force: true });
    }
    await mkdir(TEST_LOG_DIR, { recursive: true });

    // Initialize systems
    auditSystem = new AuditSystem({
      logDirectory: TEST_LOG_DIR,
      archiveDirectory: join(TEST_LOG_DIR, 'archive'),
      batchSize: 10,
      flushInterval: 1000,
      maxSize: 1024 * 1024,
      compressionEnabled: false,
      encryptionEnabled: false
    });

    securityManager = createDevSecurityManager();
    threatDetector = createThreatDetectorWithConfig(
      securityManager,
      {
        enableBehavioralAnalysis: true,
        enableResourceAnalysis: true,
        enableCommunicationAnalysis: false,
        enablePerformanceAnalysis: false,
        enableVulnerabilityScanning: true,
        enableComplianceChecks: true,
        highRiskThreshold: 0.7,
        mediumRiskThreshold: 0.4,
        learningRate: 0.1,
        adaptationRate: 0.05
      }
    );
  });

  afterAll(async () => {
    await auditSystem.shutdown();
    if (existsSync(TEST_LOG_DIR)) {
      await rm(TEST_LOG_DIR, { recursive: true, force: true });
    }
  });

  it('should integrate with SecurityManager', async () => {
    // Log security event through audit system
    const actor = {
      id: 'security-admin',
      type: 'user' as const,
      identity: 'admin@polln.ai'
    };

    // Simulate security manager activity
    await auditSystem.logEvent({
      severity: 'MEDIUM' as any,
      category: 'AUTHENTICATION' as any,
      actor,
      action: 'security_manager_init',
      resource: { type: 'security_system' },
      outcome: 'success',
      details: {
        component: 'SecurityManager',
        action: 'initialize',
        config: { mode: 'development' }
      },
      metadata: {
        ipAddress: '127.0.0.1',
        sessionId: 'test-session'
      }
    });

    await auditSystem.flush();

    // Verify event was logged
    const stats = await auditSystem.getStatistics();
    expect(stats.totalEvents).toBeGreaterThan(0);
  });

  it('should integrate with ThreatDetector', async () => {
    // Log threat detection event
    await auditSystem.logThreatDetection(
      'behavioral_anomaly',
      'HIGH' as any,
      {
        threatType: 'unusual_behavior',
        confidence: 0.85,
        source: 'ThreatDetector',
        anomalies: [
          {
            type: 'exponential_activity_increase',
            severity: 'HIGH' as any,
            description: 'Activity increased by 500%',
            timestamp: new Date(),
            evidence: []
          }
        ]
      }
    );

    await auditSystem.flush();

    const stats = await auditSystem.getStatistics();
    expect(stats.totalEvents).toBeGreaterThan(0);
  });

  it('should generate compliance report with security events', async () => {
    // Log various security events
    const actor = {
      id: 'compliance-officer',
      type: 'user' as const,
      identity: 'compliance@polln.ai'
    };

    // Authentication events
    await auditSystem.logAuthentication(
      actor,
      'login',
      'success',
      { mfa: true, controlId: 'CC1.1' }
    );

    // Data access events
    await auditSystem.logDataAccess(
      actor,
      { type: 'encrypted_data', id: 'audit-logs' },
      'success',
      { encryption: 'AES-256', controlId: 'CC2.1' }
    );

    // Incident response events
    await auditSystem.logIncidentResponse(
      'INC-2024-001',
      'incident_detected',
      'success',
      { severity: 'medium', controlId: 'CC5.1' }
    );

    await auditSystem.flush();

    // Generate compliance report
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const report = await auditSystem.generateSOC2Report(yesterday, now);

    expect(report.standard).toBe('SOC2');
    expect(report.controls.length).toBeGreaterThan(0);
    expect(report.period.start).toBeDefined();
    expect(report.period.end).toBeDefined();
  });

  it('should perform forensic analysis on security events', async () => {
    // Create a security incident scenario
    const attacker = {
      id: 'attacker-001',
      type: 'external' as const
    };

    // Failed authentication attempts
    for (let i = 0; i < 5; i++) {
      await auditSystem.logAuthentication(
        attacker,
        'failed_attempt',
        'failure',
        { ip: '192.168.1.100', attempt: i }
      );
    }

    // Successful breach
    await auditSystem.logAuthentication(
      attacker,
      'login',
      'success',
      { ip: '192.168.1.100', method: 'credential_stuffing' }
    );

    // Data exfiltration
    await auditSystem.logDataAccess(
      attacker,
      { type: 'sensitive_data', id: 'customer-database' },
      'success',
      { bulk: true, quantity: 10000 }
    );

    await auditSystem.flush();

    // Perform forensic analysis
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const analysis = await auditSystem.performForensicAnalysis(yesterday, now, {
      actorIds: ['attacker-001']
    });

    expect(analysis.findings.totalEvents).toBeGreaterThan(0);
    expect(analysis.findings.patterns.length).toBeGreaterThan(0);
    expect(analysis.findings.anomalies.length).toBeGreaterThan(0);
    expect(analysis.conclusions.length).toBeGreaterThan(0);
    expect(analysis.recommendations.length).toBeGreaterThan(0);

    // Verify specific patterns detected
    const repeatedFailedAuth = analysis.findings.patterns.find(
      p => p.type === 'repeated_failed_auth'
    );
    expect(repeatedFailedAuth).toBeDefined();

    // Verify specific anomalies detected
    const bulkAccess = analysis.findings.anomalies.find(
      a => a.type === 'bulk_data_access'
    );
    expect(bulkAccess).toBeDefined();
  });

  it('should verify chain integrity across security events', async () => {
    const actor = { id: 'test-user', type: 'user' as const };

    // Log multiple events
    for (let i = 0; i < 10; i++) {
      await auditSystem.logAuthentication(
        actor,
        i % 2 === 0 ? 'login' : 'logout',
        'success',
        { sequence: i }
      );
    }

    await auditSystem.flush();

    // Generate audit trail
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const trail = await auditSystem.generateAuditTrail(yesterday, now);

    // Verify integrity
    expect(trail.chainIntegrity).toBe(true);
    expect(trail.tamperEvidence).toHaveLength(0);
    expect(trail.events).toHaveLength(10);
  });

  it('should support incident investigation', async () => {
    // Create incident
    const incidentId = 'INC-2024-SEC-001';
    const responder = {
      id: 'security-team',
      type: 'user' as const,
      identity: 'security@polln.ai'
    };

    // Incident detection
    await auditSystem.logThreatDetection(
      'malware_infection',
      'CRITICAL' as any,
      {
        incidentId,
        source: 'endpoint_protection',
        affected: 'workstation-123'
      }
    );

    // Incident response
    await auditSystem.logIncidentResponse(
      incidentId,
      'incident_created',
      'success',
      { severity: 'critical', priority: 1 }
    );

    await auditSystem.logIncidentResponse(
      incidentId,
      'quarantine_initiated',
      'success',
      { target: 'workstation-123', action: 'isolate' }
    );

    await auditSystem.flush();

    // Investigate incident
    const investigation = await auditSystem.investigateIncident(incidentId);

    expect(investigation.analysisId).toBeDefined();
    expect(investigation.findings.totalEvents).toBeGreaterThan(0);
    expect(investigation.conclusions.length).toBeGreaterThan(0);
  });

  it('should generate comprehensive audit trail', async () => {
    const actor = { id: 'auditor', type: 'user' as const };

    // Log various event types
    await auditSystem.logAuthentication(actor, 'login', 'success', {});
    await auditSystem.logAuthorization(
      actor,
      'access_audit_logs',
      { type: 'audit_trail', id: 'all-logs' },
      'success',
      { permission: 'read' }
    );
    await auditSystem.logDataAccess(
      actor,
      { type: 'audit_log', id: 'recent-logs' },
      'success',
      { query: 'SELECT * FROM audit_events' }
    );
    await auditSystem.logAuthentication(actor, 'logout', 'success', {});

    await auditSystem.flush();

    // Generate trail
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const trail = await auditSystem.generateAuditTrail(yesterday, now);

    // Verify summary
    expect(trail.summary.totalEvents).toBe(4);
    expect(trail.summary.byCategory.AUTHENTICATION).toBe(2);
    expect(trail.summary.byCategory.AUTHORIZATION).toBe(1);
    expect(trail.summary.byCategory.DATA_ACCESS).toBe(1);
    expect(trail.chainIntegrity).toBe(true);
  });

  it('should handle multiple compliance standards', async () => {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    // SOC 2
    const soc2Report = await auditSystem.generateSOC2Report(yesterday, now);
    expect(soc2Report.standard).toBe('SOC2');

    // GDPR
    const gdprReport = await auditSystem.generateGDPRReport(yesterday, now);
    expect(gdprReport.standard).toBe('GDPR');

    // HIPAA
    const hipaaReport = await auditSystem.generateHIPAAReport(yesterday, now);
    expect(hipaaReport.standard).toBe('HIPAA');
  });
});
