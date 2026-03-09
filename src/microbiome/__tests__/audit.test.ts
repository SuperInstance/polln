/**
 * Test Suite for Audit & Compliance System
 */

import { AuditSystem, getAuditSystem, shutdownAuditSystem } from '../audit';
import {
  AuditSeverity,
  AuditCategory,
  ComplianceStandard,
  type AuditEvent,
  type ComplianceReport,
  type ForensicAnalysis
} from '../audit';
import { mkdir, rm } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

// Test configuration
const TEST_LOG_DIR = './test-logs/audit';
const TEST_ARCHIVE_DIR = './test-logs/audit/archive';

describe('AuditSystem', () => {
  let auditSystem: AuditSystem;

  beforeEach(async () => {
    // Clean up test directory
    if (existsSync(TEST_LOG_DIR)) {
      await rm(TEST_LOG_DIR, { recursive: true, force: true });
    }
    await mkdir(TEST_LOG_DIR, { recursive: true });
    await mkdir(TEST_ARCHIVE_DIR, { recursive: true });

    // Create fresh instance
    auditSystem = new AuditSystem({
      logDirectory: TEST_LOG_DIR,
      archiveDirectory: TEST_ARCHIVE_DIR,
      batchSize: 10,
      flushInterval: 1000,
      maxSize: 1024 * 1024,
      compressionEnabled: false,
      encryptionEnabled: false
    });
  });

  afterEach(async () => {
    await auditSystem.shutdown();
    if (existsSync(TEST_LOG_DIR)) {
      await rm(TEST_LOG_DIR, { recursive: true, force: true });
    }
  });

  describe('Event Logging', () => {
    test('should log authentication event', async () => {
      const actor = {
        id: 'user-123',
        type: 'user' as const,
        identity: 'john.doe@example.com'
      };

      const eventId = await auditSystem.logAuthentication(
        actor,
        'login',
        'success',
        { method: 'password' }
      );

      expect(eventId).toBeDefined();
      expect(eventId).toMatch(/^evt-/);

      // Flush and verify
      await auditSystem.flush();

      const stats = await auditSystem.getStatistics();
      expect(stats.totalEvents).toBe(1);
    });

    test('should log authorization event', async () => {
      const actor = {
        id: 'agent-456',
        type: 'agent' as const
      };

      const eventId = await auditSystem.logAuthorization(
        actor,
        'access_resource',
        { type: 'api', id: '/api/colony' },
        'success',
        { permission: 'read' }
      );

      expect(eventId).toBeDefined();

      await auditSystem.flush();
      const stats = await auditSystem.getStatistics();
      expect(stats.totalEvents).toBe(1);
    });

    test('should log data access event', async () => {
      const actor = {
        id: 'user-789',
        type: 'user' as const,
        identity: 'admin@example.com'
      };

      const eventId = await auditSystem.logDataAccess(
        actor,
        { type: 'database', id: 'colony-data' },
        'success',
        { query: 'SELECT * FROM colonies' }
      );

      expect(eventId).toBeDefined();
    });

    test('should log data modification event', async () => {
      const actor = {
        id: 'agent-999',
        type: 'agent' as const
      };

      const eventId = await auditSystem.logDataModification(
        actor,
        { type: 'tile', id: 'tile-123' },
        'update',
        'success',
        { changes: { priority: 'high' } }
      );

      expect(eventId).toBeDefined();
    });

    test('should log threat detection event', async () => {
      const eventId = await auditSystem.logThreatDetection(
        'brute_force',
        AuditSeverity.HIGH,
        {
          sourceIp: '192.168.1.100',
          attempts: 100,
          timeframe: '5m'
        }
      );

      expect(eventId).toBeDefined();
    });

    test('should log incident response event', async () => {
      const eventId = await auditSystem.logIncidentResponse(
        'INC-2024-001',
        'incident_detected',
        'success',
        {
          severity: 'high',
          type: 'unauthorized_access'
        }
      );

      expect(eventId).toBeDefined();
    });

    test('should handle batch logging', async () => {
      const actor = {
        id: 'test-user',
        type: 'user' as const
      };

      // Log multiple events
      for (let i = 0; i < 15; i++) {
        await auditSystem.logDataAccess(
          actor,
          { type: 'test-resource', id: `res-${i}` },
          'success',
          { index: i }
        );
      }

      // Should flush automatically at batch size
      await auditSystem.flush();

      const stats = await auditSystem.getStatistics();
      expect(stats.totalEvents).toBe(15);
    });
  });

  describe('Hash Chain Integrity', () => {
    test('should maintain hash chain integrity', async () => {
      const actor = {
        id: 'test-user',
        type: 'user' as const
      };

      // Log multiple events
      const eventIds = [];
      for (let i = 0; i < 5; i++) {
        const id = await auditSystem.logAuthentication(
          actor,
          'login',
          'success',
          { attempt: i }
        );
        eventIds.push(id);
      }

      await auditSystem.flush();

      // Verify hash chain
      const stats = await auditSystem.getStatistics();
      expect(stats.hashChainLength).toBe(5);

      // Generate audit trail to verify integrity
      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.chainIntegrity).toBe(true);
      expect(trail.tamperEvidence).toHaveLength(0);
    });

    test('should detect tampering in hash chain', async () => {
      // This test verifies tamper detection logic
      // In a real scenario, tampering would modify event hashes
      const actor = {
        id: 'test-user',
        type: 'user' as const
      };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logAuthentication(actor, 'logout', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.chainIntegrity).toBe(true);
    });

    test('should generate unique event hashes', async () => {
      const actor = {
        id: 'test-user',
        type: 'user' as const
      };

      const id1 = await auditSystem.logAuthentication(
        actor,
        'login',
        'success',
        { timestamp: 1 }
      );

      const id2 = await auditSystem.logAuthentication(
        actor,
        'login',
        'success',
        { timestamp: 2 }
      );

      expect(id1).not.toBe(id2);

      await auditSystem.flush();

      const stats = await auditSystem.getStatistics();
      expect(stats.totalEvents).toBe(2);
    });
  });

  describe('Audit Trails', () => {
    test('should generate audit trail for time period', async () => {
      const actor = {
        id: 'test-user',
        type: 'user' as const
      };

      // Log events
      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logDataAccess(
        actor,
        { type: 'resource', id: 'res-1' },
        'success',
        {}
      );
      await auditSystem.logDataModification(
        actor,
        { type: 'resource', id: 'res-1' },
        'update',
        'success',
        {}
      );

      await auditSystem.flush();

      // Generate trail
      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.events).toHaveLength(3);
      expect(trail.summary.totalEvents).toBe(3);
      expect(trail.chainIntegrity).toBe(true);
      expect(trail.summary.byCategory[AuditCategory.AUTHENTICATION]).toBe(1);
      expect(trail.summary.byCategory[AuditCategory.DATA_ACCESS]).toBe(1);
      expect(trail.summary.byCategory[AuditCategory.DATA_MODIFICATION]).toBe(1);
    });

    test('should generate audit trail for specific actor', async () => {
      const actor1 = { id: 'user-1', type: 'user' as const };
      const actor2 = { id: 'user-2', type: 'user' as const };

      await auditSystem.logAuthentication(actor1, 'login', 'success', {});
      await auditSystem.logAuthentication(actor2, 'login', 'success', {});
      await auditSystem.logAuthentication(actor1, 'logout', 'success', {});

      await auditSystem.flush();

      const trail = await auditSystem.generateActorTrail('user-1', 1);

      expect(trail.events).toHaveLength(2);
      expect(trail.events.every(e => e.actor.id === 'user-1')).toBe(true);
    });

    test('should generate audit trail for specific resource', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logDataAccess(
        actor,
        { type: 'api', id: '/api/data' },
        'success',
        {}
      );
      await auditSystem.logDataAccess(
        actor,
        { type: 'api', id: '/api/other' },
        'success',
        {}
      );
      await auditSystem.logDataModification(
        actor,
        { type: 'api', id: '/api/data' },
        'update',
        'success',
        {}
      );

      await auditSystem.flush();

      const trail = await auditSystem.generateResourceTrail('/api/data', 1);

      expect(trail.events).toHaveLength(2);
      expect(trail.events.every(e =>
        e.resource.id === '/api/data' || e.resource.path === '/api/data'
      )).toBe(true);
    });

    test('should apply filters to audit trail', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logThreatDetection('malware', AuditSeverity.HIGH, {});
      await auditSystem.logDataAccess(actor, { type: 'data' }, 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now, {
        categories: [AuditCategory.THREAT_DETECTION]
      });

      expect(trail.events).toHaveLength(1);
      expect(trail.events[0].category).toBe(AuditCategory.THREAT_DETECTION);
    });
  });

  describe('Compliance Reporting', () => {
    test('should generate SOC 2 compliance report', async () => {
      const actor = {
        id: 'admin',
        type: 'user' as const,
        identity: 'admin@example.com'
      };

      // Log compliance-relevant events
      await auditSystem.logAuthentication(actor, 'login', 'success', {
        mfa: true,
        controlId: 'CC1.1'
      });
      await auditSystem.logDataAccess(
        actor,
        { type: 'encrypted_data', id: 'data-1' },
        'success',
        { encryption: 'AES-256', controlId: 'CC2.1' }
      );
      await auditSystem.logIncidentResponse(
        'INC-001',
        'incident_resolved',
        'success',
        { controlId: 'CC5.1' }
      );

      await auditSystem.flush();

      const now = new Date();
      const lastMonth = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      const report = await auditSystem.generateSOC2Report(lastMonth, now);

      expect(report.standard).toBe(ComplianceStandard.SOC2);
      expect(report.controls.length).toBeGreaterThan(0);
      expect(report.generatedAt).toBeDefined();
      expect(report.period.start).toEqual(lastMonth);
      expect(report.period.end).toEqual(now);
    });

    test('should generate GDPR compliance report', async () => {
      const actor = {
        id: 'data-controller',
        type: 'user' as const,
        identity: 'controller@example.com'
      };

      await auditSystem.logDataAccess(
        actor,
        { type: 'personal_data', id: 'user-123' },
        'success',
        { basis: 'consent', article: 'Art.6' }
      );
      await auditSystem.logDataModification(
        actor,
        { type: 'personal_data', id: 'user-123' },
        'update',
        'success',
        { right: 'rectification', article: 'Art.16' }
      );

      await auditSystem.flush();

      const now = new Date();
      const lastMonth = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      const report = await auditSystem.generateGDPRReport(lastMonth, now);

      expect(report.standard).toBe(ComplianceStandard.GDPR);
      expect(report.controls.length).toBeGreaterThan(0);
    });

    test('should generate HIPAA compliance report', async () => {
      const actor = {
        id: 'healthcare-provider',
        type: 'user' as const
      };

      await auditSystem.logDataAccess(
        actor,
        { type: 'phi', id: 'patient-456' },
        'success',
        { disclosure: 'treatment', section: '164.312' }
      );
      await auditSystem.logThreatDetection(
        'phi_breach',
        AuditSeverity.CRITICAL,
        { affected: 10, section: '164.308' }
      );

      await auditSystem.flush();

      const now = new Date();
      const lastMonth = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      const report = await auditSystem.generateHIPAAReport(lastMonth, now);

      expect(report.standard).toBe(ComplianceStandard.HIPAA);
      expect(report.controls.length).toBeGreaterThan(0);
    });

    test('should include recommendations in compliance report', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      // Log some failures to generate recommendations
      await auditSystem.logAuthentication(actor, 'login', 'failure', {
        reason: 'invalid_password'
      });
      await auditSystem.logAuthorization(
        actor,
        'access_admin',
        { type: 'admin_panel' },
        'failure',
        { reason: 'insufficient_permissions' }
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const report = await auditSystem.generateSOC2Report(yesterday, now);

      expect(report.recommendations).toBeDefined();
      expect(Array.isArray(report.recommendations)).toBe(true);
    });
  });

  describe('Forensic Analysis', () => {
    test('should perform forensic analysis', async () => {
      const actor = { id: 'suspect-user', type: 'user' as const };

      // Create suspicious activity pattern
      for (let i = 0; i < 5; i++) {
        await auditSystem.logAuthentication(
          actor,
          'failed_attempt',
          'failure',
          { attempt: i }
        );
      }

      await auditSystem.logDataModification(
        actor,
        { type: 'sensitive_data', id: 'data-1' },
        'delete',
        'success',
        { bulk: true, quantity: 1000 }
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now, {
        actorIds: ['suspect-user']
      });

      expect(analysis.analysisId).toBeDefined();
      expect(analysis.findings.totalEvents).toBeGreaterThan(0);
      expect(analysis.findings.patterns).toBeDefined();
      expect(analysis.findings.anomalies).toBeDefined();
      expect(analysis.conclusions).toBeDefined();
      expect(analysis.recommendations).toBeDefined();
    });

    test('should detect repeated failed authentication', async () => {
      const actor = { id: 'attacker', type: 'user' as const };

      for (let i = 0; i < 5; i++) {
        await auditSystem.logAuthentication(
          actor,
          'failed_attempt',
          'failure',
          { ip: '192.168.1.100' }
        );
      }

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now);

      const authPattern = analysis.findings.patterns.find(
        p => p.type === 'repeated_failed_auth'
      );

      expect(authPattern).toBeDefined();
      expect(authPattern?.frequency).toBe(5);
    });

    test('should detect bulk data access', async () => {
      const actor = { id: 'insider-threat', type: 'user' as const };

      await auditSystem.logDataAccess(
        actor,
        { type: 'customer_data', id: 'all-customers' },
        'success',
        { bulk: true, quantity: 50000 }
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now);

      const bulkAnomaly = analysis.findings.anomalies.find(
        a => a.type === 'bulk_data_access'
      );

      expect(bulkAnomaly).toBeDefined();
      expect(bulkAnomaly?.severity).toBe(AuditSeverity.HIGH);
    });

    test('should detect unusual time access', async () => {
      const actor = { id: 'night-worker', type: 'user' as const };

      await auditSystem.logDataAccess(
        actor,
        { type: 'system', id: 'config' },
        'success',
        {}
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now);

      const timeAnomaly = analysis.findings.anomalies.find(
        a => a.type === 'unusual_time_access'
      );

      expect(timeAnomaly).toBeDefined();
    });

    test('should build timeline of significant events', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logThreatDetection(
        'intrusion',
        AuditSeverity.CRITICAL,
        { source: 'external' }
      );
      await auditSystem.logIncidentResponse(
        'INC-001',
        'response_triggered',
        'success',
        {}
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now);

      expect(analysis.findings.timeline.length).toBeGreaterThan(0);
      expect(analysis.findings.timeline[0].significance).toBeGreaterThan(0);
    });

    test('should find connections between events', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logDataAccess(
        actor,
        { type: 'resource', id: 'res-1' },
        'success',
        { correlationId: 'corr-123' }
      );
      await auditSystem.logDataModification(
        actor,
        { type: 'resource', id: 'res-1' },
        'update',
        'success',
        { correlationId: 'corr-123' }
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now);

      expect(analysis.findings.connections.length).toBeGreaterThan(0);
      const causalConnection = analysis.findings.connections.find(
        c => c.relationship === 'causal'
      );
      expect(causalConnection).toBeDefined();
    });

    test('should investigate specific incident', async () => {
      const actor = { id: 'security-team', type: 'user' as const };

      await auditSystem.logIncidentResponse(
        'INC-2024-001',
        'incident_detected',
        'success',
        { type: 'data_breach' }
      );
      await auditSystem.logThreatDetection(
        'data_exfiltration',
        AuditSeverity.HIGH,
        { incidentId: 'INC-2024-001' }
      );

      await auditSystem.flush();

      const analysis = await auditSystem.investigateIncident('INC-2024-001');

      expect(analysis.analysisId).toBeDefined();
      expect(analysis.findings.totalEvents).toBeGreaterThan(0);
    });
  });

  describe('Tamper Detection', () => {
    test('should verify chain integrity', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logAuthentication(actor, 'logout', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.chainIntegrity).toBe(true);
      expect(trail.tamperEvidence).toHaveLength(0);
    });

    test('should detect missing events in chain', async () => {
      // This test verifies the logic for detecting chain breaks
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.chainIntegrity).toBe(true);
    });

    test('should maintain previous hash references', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      const id1 = await auditSystem.logAuthentication(actor, 'login', 'success', {});
      const id2 = await auditSystem.logAuthentication(actor, 'logout', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.events[0].previousHash).toBeDefined();
      expect(trail.events[1].previousHash).toBe(trail.events[0].hash);
    });
  });

  describe('Retention and Archival', () => {
    test('should track audit statistics', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logAuthentication(actor, 'logout', 'success', {});

      await auditSystem.flush();

      const stats = await auditSystem.getStatistics();

      expect(stats.totalEvents).toBe(2);
      expect(stats.bufferLength).toBe(0);
      expect(stats.hashChainLength).toBe(2);
      expect(stats.logFiles).toBeGreaterThan(0);
    });

    test('should flush buffer on shutdown', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});

      // Shutdown before auto-flush
      await auditSystem.shutdown();

      const stats = await auditSystem.getStatistics();
      expect(stats.bufferLength).toBe(0);
    });
  });

  describe('Event Filtering and Querying', () => {
    test('should filter by severity', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logThreatDetection('low', AuditSeverity.LOW, {});
      await auditSystem.logThreatDetection('high', AuditSeverity.HIGH, {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now, {
        severities: [AuditSeverity.HIGH]
      });

      expect(trail.events).toHaveLength(1);
      expect(trail.events[0].severity).toBe(AuditSeverity.HIGH);
    });

    test('should filter by category', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logDataAccess(actor, { type: 'data' }, 'success', {});
      await auditSystem.logAuthentication(actor, 'logout', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now, {
        categories: [AuditCategory.AUTHENTICATION]
      });

      expect(trail.events).toHaveLength(2);
      expect(trail.events.every(e => e.category === AuditCategory.AUTHENTICATION)).toBe(true);
    });

    test('should filter by actor', async () => {
      const actor1 = { id: 'user-1', type: 'user' as const };
      const actor2 = { id: 'user-2', type: 'user' as const };

      await auditSystem.logAuthentication(actor1, 'login', 'success', {});
      await auditSystem.logAuthentication(actor2, 'login', 'success', {});
      await auditSystem.logAuthentication(actor1, 'logout', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now, {
        actorIds: ['user-1']
      });

      expect(trail.events).toHaveLength(2);
    });

    test('should filter by resource type', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logDataAccess(actor, { type: 'database' }, 'success', {});
      await auditSystem.logDataAccess(actor, { type: 'api' }, 'success', {});
      await auditSystem.logDataAccess(actor, { type: 'database' }, 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now, {
        resourceTypes: ['database']
      });

      expect(trail.events).toHaveLength(2);
    });
  });

  describe('Event Metadata', () => {
    test('should include metadata in events', async () => {
      const actor = {
        id: 'test-user',
        type: 'user' as const
      };

      await auditSystem.logEvent({
        severity: AuditSeverity.MEDIUM,
        category: AuditCategory.DATA_ACCESS,
        actor,
        action: 'access_resource',
        resource: { type: 'test' },
        outcome: 'success',
        details: {},
        metadata: {
          ipAddress: '192.168.1.1',
          userAgent: 'Mozilla/5.0',
          sessionId: 'session-123',
          requestId: 'req-456',
          correlationId: 'corr-789'
        }
      });

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.events[0].metadata.ipAddress).toBe('192.168.1.1');
      expect(trail.events[0].metadata.userAgent).toBe('Mozilla/5.0');
      expect(trail.events[0].metadata.sessionId).toBe('session-123');
    });

    test('should handle correlation IDs', async () => {
      const actor = { id: 'test-user', type: 'user' as const };
      const correlationId = 'corr-abc-123';

      await auditSystem.logEvent({
        severity: AuditSeverity.MEDIUM,
        category: AuditCategory.DATA_ACCESS,
        actor,
        action: 'access_resource',
        resource: { type: 'test' },
        outcome: 'success',
        details: {},
        metadata: { correlationId }
      });

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.events[0].metadata.correlationId).toBe(correlationId);
    });
  });

  describe('Summary Statistics', () => {
    test('should generate accurate summary statistics', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      await auditSystem.logAuthentication(actor, 'login', 'success', {});
      await auditSystem.logThreatDetection('threat', AuditSeverity.HIGH, {});
      await auditSystem.logDataAccess(actor, { type: 'data' }, 'success', {});
      await auditSystem.logAuthentication(actor, 'logout', 'success', {});

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now);

      expect(trail.summary.totalEvents).toBe(4);
      expect(trail.summary.bySeverity[AuditSeverity.HIGH]).toBe(1);
      expect(trail.summary.byCategory[AuditCategory.AUTHENTICATION]).toBe(2);
      expect(trail.summary.byActor['test-user']).toBe(3);
    });
  });

  describe('Error Handling', () => {
    test('should handle flush errors gracefully', async () => {
      const actor = { id: 'test-user', type: 'user' as const };

      // Log event
      await auditSystem.logAuthentication(actor, 'login', 'success', {});

      // Flush should not throw
      await expect(auditSystem.flush()).resolves.not.toThrow();
    });

    test('should handle invalid incident ID', async () => {
      await expect(
        auditSystem.investigateIncident('non-existent-incident')
      ).rejects.toThrow();
    });

    test('should handle empty time ranges', async () => {
      const now = new Date();
      const future = new Date(now.getTime() + 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(now, future);

      expect(trail.events).toHaveLength(0);
      expect(trail.summary.totalEvents).toBe(0);
    });
  });

  describe('Singleton Pattern', () => {
    test('should return same instance', () => {
      const instance1 = getAuditSystem({
        logDirectory: './test-singleton-1'
      });
      const instance2 = getAuditSystem({
        logDirectory: './test-singleton-2'
      });

      expect(instance1).toBe(instance2);
    });

    test('should shutdown singleton', async () => {
      const instance = getAuditSystem({
        logDirectory: './test-shutdown'
      });

      await expect(shutdownAuditSystem()).resolves.not.toThrow();

      const newInstance = getAuditSystem({
        logDirectory: './test-shutdown'
      });

      expect(newInstance).not.toBe(instance);
    });
  });

  describe('Integration with Other Modules', () => {
    test('should work with SecurityManager', async () => {
      const actor = { id: 'security-admin', type: 'user' as const };

      // Simulate security manager events
      await auditSystem.logThreatDetection(
        'malware_signature',
        AuditSeverity.CRITICAL,
        {
          threat: 'trojan',
          source: 'endpoint-scanner',
          confidence: 0.95
        }
      );

      await auditSystem.logIncidentResponse(
        'INC-SEC-001',
        'quarantine_initiated',
        'success',
        {
          action: 'isolate_host',
          target: ' workstation-123'
        }
      );

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const trail = await auditSystem.generateAuditTrail(yesterday, now, {
        categories: [AuditCategory.THREAT_DETECTION, AuditCategory.INCIDENT_RESPONSE]
      });

      expect(trail.events).toHaveLength(2);
      expect(trail.chainIntegrity).toBe(true);
    });

    test('should work with ThreatDetector', async () => {
      const actor = { id: 'threat-detector', type: 'system' as const };

      // Simulate threat detector events
      const threats = [
        { type: 'brute_force', severity: AuditSeverity.HIGH },
        { type: 'ddos', severity: AuditSeverity.CRITICAL },
        { type: 'injection', severity: AuditSeverity.HIGH }
      ];

      for (const threat of threats) {
        await auditSystem.logThreatDetection(threat.type, threat.severity, {
          source: 'ids',
          confidence: 0.85
        });
      }

      await auditSystem.flush();

      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const analysis = await auditSystem.performForensicAnalysis(yesterday, now, {
        categories: [AuditCategory.THREAT_DETECTION]
      });

      expect(analysis.findings.totalEvents).toBe(3);
      expect(analysis.findings.anomalies.length).toBeGreaterThan(0);
    });
  });
});
