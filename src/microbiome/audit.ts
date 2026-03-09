/**
 * Audit & Compliance System for POLLN
 *
 * Provides comprehensive security event logging, audit trails,
 * compliance reporting, and forensic analysis capabilities.
 *
 * Defensive security only - no offensive capabilities.
 */

import { createHash, randomBytes, createSign, createVerify } from 'crypto';
import { writeFile, appendFile, readFile, mkdir, stat, unlink } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Audit event severity levels
 */
export enum AuditSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

/**
 * Audit event categories
 */
export enum AuditCategory {
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  ACCESS_CONTROL = 'ACCESS_CONTROL',
  DATA_ACCESS = 'DATA_ACCESS',
  DATA_MODIFICATION = 'DATA_MODIFICATION',
  SYSTEM_CONFIG = 'SYSTEM_CONFIG',
  THREAT_DETECTION = 'THREAT_DETECTION',
  INCIDENT_RESPONSE = 'INCIDENT_RESPONSE',
  COMPLIANCE = 'COMPLIANCE',
  PRIVACY = 'PRIVACY'
}

/**
 * Audit event record
 */
export interface AuditEvent {
  id: string;
  timestamp: Date;
  severity: AuditSeverity;
  category: AuditCategory;
  actor: {
    id: string;
    type: 'user' | 'agent' | 'system' | 'external';
    identity?: string;
  };
  action: string;
  resource: {
    type: string;
    id?: string;
    path?: string;
  };
  outcome: 'success' | 'failure' | 'partial';
  details: Record<string, any>;
  metadata: {
    ipAddress?: string;
    userAgent?: string;
    sessionId?: string;
    requestId?: string;
    correlationId?: string;
  };
  signature?: string;
  previousHash?: string;
  hash?: string;
}

/**
 * Audit trail record
 */
export interface AuditTrail {
  events: AuditEvent[];
  summary: {
    totalEvents: number;
    bySeverity: Record<AuditSeverity, number>;
    byCategory: Record<AuditCategory, number>;
    byActor: Record<string, number>;
    timeRange: {
      start: Date;
      end: Date;
    };
  };
  chainIntegrity: boolean;
  tamperEvidence: string[];
}

/**
 * Compliance report types
 */
export enum ComplianceStandard {
  SOC2 = 'SOC2',
  GDPR = 'GDPR',
  HIPAA = 'HIPAA',
  ISO27001 = 'ISO27001',
  PCIDSS = 'PCIDSS'
}

/**
 * Compliance report
 */
export interface ComplianceReport {
  standard: ComplianceStandard;
  period: {
    start: Date;
    end: Date;
  };
  generatedAt: Date;
  controls: {
    id: string;
    name: string;
    status: 'compliant' | 'non-compliant' | 'partial';
    evidence: string[];
    findings: string[];
  }[];
  overallStatus: 'compliant' | 'non-compliant' | 'partial';
  recommendations: string[];
  signature?: string;
}

/**
 * Forensic analysis result
 */
export interface ForensicAnalysis {
  analysisId: string;
  timestamp: Date;
  timeframe: {
    start: Date;
    end: Date;
  };
  filters: {
    actorIds?: string[];
    categories?: AuditCategory[];
    severities?: AuditSeverity[];
    resources?: string[];
    keywords?: string[];
  };
  findings: {
    totalEvents: number;
    patterns: Pattern[];
    anomalies: Anomaly[];
    timeline: TimelineEvent[];
    connections: Connection[];
  };
  conclusions: string[];
  recommendations: string[];
}

/**
 * Detected pattern
 */
export interface Pattern {
  type: string;
  description: string;
  frequency: number;
  examples: AuditEvent[];
  confidence: number;
}

/**
 * Detected anomaly
 */
export interface Anomaly {
  type: string;
  description: string;
  severity: AuditSeverity;
  events: AuditEvent[];
  riskScore: number;
}

/**
 * Timeline event
 */
export interface TimelineEvent {
  timestamp: Date;
  event: AuditEvent;
  significance: number;
}

/**
 * Connection between events
 */
export interface Connection {
  from: AuditEvent;
  to: AuditEvent;
  relationship: string;
  strength: number;
}

/**
 * Audit retention policy
 */
export interface RetentionPolicy {
  eventTypes: Record<AuditCategory, number>; // days to retain
  archiveAfter: number; // days
  compressionEnabled: boolean;
  encryptionEnabled: boolean;
  deleteMethod: 'secure' | 'standard';
}

/**
 * Hash chain entry for tamper evidence
 */
export interface HashChainEntry {
  index: number;
  hash: string;
  previousHash: string;
  timestamp: Date;
  signature: string;
}

// ============================================================================
// AuditSystem Configuration
// ============================================================================

export interface AuditSystemConfig {
  logDirectory: string;
  archiveDirectory: string;
  retentionPolicy: RetentionPolicy;
  signingKey?: string; // Private key for signing
  verifyKey?: string; // Public key for verification
  batchSize: number;
  flushInterval: number; // ms
  maxSize: number; // bytes per log file
  maxAge: number; // days
  compressionEnabled: boolean;
  encryptionEnabled: boolean;
  complianceStandards: ComplianceStandard[];
}

const DEFAULT_CONFIG: AuditSystemConfig = {
  logDirectory: './logs/audit',
  archiveDirectory: './logs/audit/archive',
  retentionPolicy: {
    eventTypes: {
      [AuditCategory.AUTHENTICATION]: 365,
      [AuditCategory.AUTHORIZATION]: 365,
      [AuditCategory.ACCESS_CONTROL]: 365,
      [AuditCategory.DATA_ACCESS]: 180,
      [AuditCategory.DATA_MODIFICATION]: 365,
      [AuditCategory.SYSTEM_CONFIG]: 180,
      [AuditCategory.THREAT_DETECTION]: 365,
      [AuditCategory.INCIDENT_RESPONSE]: 1825, // 5 years
      [AuditCategory.COMPLIANCE]: 3650, // 10 years
      [AuditCategory.PRIVACY]: 3650
    },
    archiveAfter: 90,
    compressionEnabled: true,
    encryptionEnabled: true,
    deleteMethod: 'secure'
  },
  batchSize: 100,
  flushInterval: 5000,
  maxSize: 100 * 1024 * 1024, // 100MB
  maxAge: 90,
  compressionEnabled: true,
  encryptionEnabled: true,
  complianceStandards: [ComplianceStandard.SOC2, ComplianceStandard.GDPR]
};

// ============================================================================
// AuditSystem Implementation
// ============================================================================

export class AuditSystem {
  private config: AuditSystemConfig;
  private eventBuffer: AuditEvent[] = [];
  private hashChain: HashChainEntry[] = [];
  private flushTimer?: NodeJS.Timeout;
  private isShuttingDown = false;
  private eventCounter = 0;
  private currentLogFile?: string;
  private chainStoreFile: string;

  constructor(config: Partial<AuditSystemConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.chainStoreFile = join(this.config.logDirectory, 'hash-chain.json');
    this.initialize();
  }

  private async initialize(): Promise<void> {
    // Create directories
    await mkdir(this.config.logDirectory, { recursive: true });
    await mkdir(this.config.archiveDirectory, { recursive: true });

    // Load existing hash chain
    await this.loadHashChain();

    // Start flush timer
    this.flushTimer = setInterval(() => {
      this.flush().catch(err => console.error('Flush error:', err));
    }, this.config.flushInterval);

    // Setup shutdown handlers
    process.on('beforeExit', () => this.shutdown());
    process.on('SIGINT', () => this.shutdown());
    process.on('SIGTERM', () => this.shutdown());
  }

  // ============================================================================
  // Event Logging
  // ============================================================================

  /**
   * Log an audit event
   */
  async logEvent(event: Omit<AuditEvent, 'id' | 'timestamp' | 'hash' | 'previousHash' | 'signature'>): Promise<string> {
    const auditEvent: AuditEvent = {
      id: this.generateEventId(),
      timestamp: new Date(),
      ...event
    };

    // Add to hash chain
    const previousEntry = this.hashChain[this.hashChain.length - 1];
    auditEvent.previousHash = previousEntry?.hash || this.genesisHash();

    // Compute event hash
    auditEvent.hash = this.computeEventHash(auditEvent);

    // Sign event if key provided
    if (this.config.signingKey) {
      auditEvent.signature = this.signEvent(auditEvent);
    }

    // Add to buffer
    this.eventBuffer.push(auditEvent);
    this.eventCounter++;

    // Add to hash chain
    this.hashChain.push({
      index: this.hashChain.length,
      hash: auditEvent.hash,
      previousHash: auditEvent.previousHash,
      timestamp: auditEvent.timestamp,
      signature: auditEvent.signature || ''
    });

    // Flush if buffer full
    if (this.eventBuffer.length >= this.config.batchSize) {
      await this.flush();
    }

    return auditEvent.id;
  }

  /**
   * Log authentication events
   */
  async logAuthentication(
    actor: AuditEvent['actor'],
    action: 'login' | 'logout' | 'failed_attempt' | 'password_change' | 'mfa_challenge',
    outcome: AuditEvent['outcome'],
    details: Record<string, any> = {}
  ): Promise<string> {
    return this.logEvent({
      severity: action === 'failed_attempt' ? AuditSeverity.HIGH : AuditSeverity.MEDIUM,
      category: AuditCategory.AUTHENTICATION,
      actor,
      action: `auth_${action}`,
      resource: { type: 'auth_system' },
      outcome,
      details,
      metadata: {}
    });
  }

  /**
   * Log authorization events
   */
  async logAuthorization(
    actor: AuditEvent['actor'],
    action: string,
    resource: AuditEvent['resource'],
    outcome: AuditEvent['outcome'],
    details: Record<string, any> = {}
  ): Promise<string> {
    return this.logEvent({
      severity: outcome === 'failure' ? AuditSeverity.HIGH : AuditSeverity.MEDIUM,
      category: AuditCategory.AUTHORIZATION,
      actor,
      action,
      resource,
      outcome,
      details,
      metadata: {}
    });
  }

  /**
   * Log data access events
   */
  async logDataAccess(
    actor: AuditEvent['actor'],
    resource: AuditEvent['resource'],
    outcome: AuditEvent['outcome'],
    details: Record<string, any> = {}
  ): Promise<string> {
    return this.logEvent({
      severity: AuditSeverity.LOW,
      category: AuditCategory.DATA_ACCESS,
      actor,
      action: 'data_access',
      resource,
      outcome,
      details,
      metadata: {}
    });
  }

  /**
   * Log data modification events
   */
  async logDataModification(
    actor: AuditEvent['actor'],
    resource: AuditEvent['resource'],
    action: 'create' | 'update' | 'delete',
    outcome: AuditEvent['outcome'],
    details: Record<string, any> = {}
  ): Promise<string> {
    return this.logEvent({
      severity: AuditSeverity.MEDIUM,
      category: AuditCategory.DATA_MODIFICATION,
      actor,
      action: `data_${action}`,
      resource,
      outcome,
      details,
      metadata: {}
    });
  }

  /**
   * Log threat detection events
   */
  async logThreatDetection(
    threatType: string,
    severity: AuditSeverity,
    details: Record<string, any> = {}
  ): Promise<string> {
    return this.logEvent({
      severity,
      category: AuditCategory.THREAT_DETECTION,
      actor: { id: 'security_system', type: 'system' },
      action: `threat_detected_${threatType}`,
      resource: { type: 'threat_detection' },
      outcome: 'success',
      details,
      metadata: {}
    });
  }

  /**
   * Log incident response events
   */
  async logIncidentResponse(
    incidentId: string,
    action: string,
    outcome: AuditEvent['outcome'],
    details: Record<string, any> = {}
  ): Promise<string> {
    return this.logEvent({
      severity: AuditSeverity.HIGH,
      category: AuditCategory.INCIDENT_RESPONSE,
      actor: { id: 'incident_response', type: 'system' },
      action,
      resource: { type: 'incident', id: incidentId },
      outcome,
      details,
      metadata: {}
    });
  }

  // ============================================================================
  // Audit Trails
  // ============================================================================

  /**
   * Generate audit trail for a time period
   */
  async generateAuditTrail(
    startTime: Date,
    endTime: Date,
    filters: {
      actorIds?: string[];
      categories?: AuditCategory[];
      severities?: AuditSeverity[];
      resourceTypes?: string[];
    } = {}
  ): Promise<AuditTrail> {
    const events = await this.queryEvents(startTime, endTime, filters);

    // Verify chain integrity
    const chainIntegrity = await this.verifyChainIntegrity(events);

    // Check for tampering
    const tamperEvidence = await this.detectTampering(events);

    // Generate summary
    const summary = this.generateSummary(events);

    return {
      events,
      summary,
      chainIntegrity,
      tamperEvidence
    };
  }

  /**
   * Generate audit trail for a specific actor
   */
  async generateActorTrail(actorId: string, days: number = 30): Promise<AuditTrail> {
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - days * 24 * 60 * 60 * 1000);

    return this.generateAuditTrail(startTime, endTime, {
      actorIds: [actorId]
    });
  }

  /**
   * Generate audit trail for a specific resource
   */
  async generateResourceTrail(resourceId: string, days: number = 30): Promise<AuditTrail> {
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - days * 24 * 60 * 60 * 1000);

    const events = await this.queryEvents(startTime, endTime, {});
    const filtered = events.filter(e =>
      e.resource.id === resourceId ||
      e.resource.path?.includes(resourceId)
    );

    return {
      events: filtered,
      summary: this.generateSummary(filtered),
      chainIntegrity: await this.verifyChainIntegrity(filtered),
      tamperEvidence: await this.detectTampering(filtered)
    };
  }

  // ============================================================================
  // Compliance Reporting
  // ============================================================================

  /**
   * Generate compliance report
   */
  async generateComplianceReport(
    standard: ComplianceStandard,
    startTime: Date,
    endTime: Date
  ): Promise<ComplianceReport> {
    const events = await this.queryEvents(startTime, endTime, {});
    const controls = this.getControlsForStandard(standard);

    // Evaluate each control
    const evaluatedControls = await Promise.all(
      controls.map(async control => ({
        ...control,
        status: await this.evaluateControl(control, events) as 'compliant' | 'non-compliant' | 'partial',
        evidence: this.getEvidenceForControl(control, events),
        findings: this.getFindingsForControl(control, events)
      }))
    );

    // Determine overall status
    const compliantCount = evaluatedControls.filter(c => c.status === 'compliant').length;
    const overallStatus: 'compliant' | 'non-compliant' | 'partial' =
      compliantCount === controls.length ? 'compliant' :
      compliantCount > 0 ? 'partial' : 'non-compliant';

    // Generate recommendations
    const recommendations = this.generateRecommendations(evaluatedControls);

    const report: ComplianceReport = {
      standard,
      period: { start: startTime, end: endTime },
      generatedAt: new Date(),
      controls: evaluatedControls,
      overallStatus,
      recommendations
    };

    // Sign report if key provided
    if (this.config.signingKey) {
      report.signature = this.signReport(report);
    }

    return report;
  }

  /**
   * Generate SOC 2 compliance report
   */
  async generateSOC2Report(startTime: Date, endTime: Date): Promise<ComplianceReport> {
    return this.generateComplianceReport(ComplianceStandard.SOC2, startTime, endTime);
  }

  /**
   * Generate GDPR compliance report
   */
  async generateGDPRReport(startTime: Date, endTime: Date): Promise<ComplianceReport> {
    return this.generateComplianceReport(ComplianceStandard.GDPR, startTime, endTime);
  }

  /**
   * Generate HIPAA compliance report
   */
  async generateHIPAAReport(startTime: Date, endTime: Date): Promise<ComplianceReport> {
    return this.generateComplianceReport(ComplianceStandard.HIPAA, startTime, endTime);
  }

  // ============================================================================
  // Forensic Analysis
  // ============================================================================

  /**
   * Perform forensic analysis
   */
  async performForensicAnalysis(
    startTime: Date,
    endTime: Date,
    filters: ForensicAnalysis['filters'] = {}
  ): Promise<ForensicAnalysis> {
    const events = await this.queryEvents(startTime, endTime, filters);

    // Apply filters
    let filtered = events;
    if (filters.categories) {
      filtered = filtered.filter(e => filters.categories!.includes(e.category));
    }
    if (filters.severities) {
      filtered = filtered.filter(e => filters.severities!.includes(e.severity));
    }
    if (filters.actorIds) {
      filtered = filtered.filter(e => filters.actorIds!.includes(e.actor.id));
    }
    if (filters.resources) {
      filtered = filtered.filter(e =>
        filters.resources!.some(r =>
          e.resource.id === r || e.resource.path?.includes(r)
        )
      );
    }
    if (filters.keywords) {
      filtered = filtered.filter(e =>
        filters.keywords!.some(k =>
          JSON.stringify(e).toLowerCase().includes(k.toLowerCase())
        )
      );
    }

    // Detect patterns
    const patterns = this.detectPatterns(filtered);

    // Detect anomalies
    const anomalies = this.detectAnomalies(filtered);

    // Build timeline
    const timeline = this.buildTimeline(filtered);

    // Find connections
    const connections = this.findConnections(filtered);

    // Generate conclusions and recommendations
    const conclusions = this.generateConclusions(patterns, anomalies, connections);
    const recommendations = this.generateForensicRecommendations(patterns, anomalies);

    return {
      analysisId: this.generateEventId(),
      timestamp: new Date(),
      timeframe: { start: startTime, end: endTime },
      filters,
      findings: {
        totalEvents: filtered.length,
        patterns,
        anomalies,
        timeline,
        connections
      },
      conclusions,
      recommendations
    };
  }

  /**
   * Investigate a specific incident
   */
  async investigateIncident(incidentId: string): Promise<ForensicAnalysis> {
    // Find incident events
    const incidentEvents = await this.queryEventsByIncident(incidentId);

    if (incidentEvents.length === 0) {
      throw new Error(`Incident ${incidentId} not found`);
    }

    // Determine time range (extended before and after)
    const firstEvent = incidentEvents[0];
    const lastEvent = incidentEvents[incidentEvents.length - 1];
    const startTime = new Date(firstEvent.timestamp.getTime() - 24 * 60 * 60 * 1000); // 1 day before
    const endTime = new Date(lastEvent.timestamp.getTime() + 7 * 24 * 60 * 60 * 1000); // 7 days after

    return this.performForensicAnalysis(startTime, endTime, {
      categories: [AuditCategory.INCIDENT_RESPONSE, AuditCategory.THREAT_DETECTION]
    });
  }

  // ============================================================================
  // Tamper Evidence
  // ============================================================================

  /**
   * Verify hash chain integrity
   */
  async verifyChainIntegrity(events: AuditEvent[]): Promise<boolean> {
    for (let i = 0; i < events.length; i++) {
      const event = events[i];

      // Verify hash
      const computedHash = this.computeEventHash(event);
      if (computedHash !== event.hash) {
        return false;
      }

      // Verify chain link
      if (i > 0) {
        const prevEvent = events[i - 1];
        if (event.previousHash !== prevEvent.hash) {
          return false;
        }
      } else {
        // Verify genesis hash
        if (event.previousHash !== this.genesisHash()) {
          return false;
        }
      }

      // Verify signature if present
      if (event.signature && this.config.verifyKey) {
        const isValid = this.verifySignature(event, event.signature);
        if (!isValid) {
          return false;
        }
      }
    }

    return true;
  }

  /**
   * Detect tampering in event chain
   */
  async detectTampering(events: AuditEvent[]): Promise<string[]> {
    const evidence: string[] = [];

    for (let i = 0; i < events.length; i++) {
      const event = events[i];

      // Check hash integrity
      const computedHash = this.computeEventHash(event);
      if (computedHash !== event.hash) {
        evidence.push(`Hash mismatch at event ${event.id} (${i})`);
      }

      // Check chain integrity
      if (i > 0) {
        const prevEvent = events[i - 1];
        if (event.previousHash !== prevEvent.hash) {
          evidence.push(`Chain break detected: event ${event.id} references incorrect previous hash`);
        }
      }

      // Check signature
      if (event.signature && this.config.verifyKey) {
        const isValid = this.verifySignature(event, event.signature);
        if (!isValid) {
          evidence.push(`Invalid signature on event ${event.id}`);
        }
      }

      // Check timestamp consistency
      if (i > 0) {
        const prevEvent = events[i - 1];
        if (event.timestamp < prevEvent.timestamp) {
          evidence.push(`Timestamp inconsistency: event ${event.id} is before previous event`);
        }
      }
    }

    return evidence;
  }

  // ============================================================================
  // Retention and Archival
  // ============================================================================

  /**
   * Apply retention policy
   */
  async applyRetentionPolicy(): Promise<void> {
    const now = Date.now();
    const files = await this.getAuditLogFiles();

    for (const file of files) {
      const stats = await stat(file.path);
      const ageDays = (now - stats.mtime.getTime()) / (24 * 60 * 60 * 1000);

      // Archive if old enough
      if (ageDays >= this.config.retentionPolicy.archiveAfter) {
        await this.archiveFile(file.path);
      }

      // Delete if past retention
      const maxAge = Math.max(...Object.values(this.config.retentionPolicy.eventTypes));
      if (ageDays >= maxAge) {
        await this.deleteAuditFile(file.path);
      }
    }
  }

  /**
   * Archive audit log file
   */
  private async archiveFile(filePath: string): Promise<void> {
    const filename = filePath.split('/').pop() || '';
    const archivePath = join(this.config.archiveDirectory, filename);

    // Read content
    const content = await readFile(filePath, 'utf-8');

    // Compress if enabled
    let finalContent = content;
    if (this.config.retentionPolicy.compressionEnabled) {
      // Simple compression placeholder (use zlib in production)
      finalContent = JSON.stringify({ compressed: true, data: content });
    }

    // Write to archive
    await writeFile(archivePath, finalContent);

    // Delete original
    await unlink(filePath);
  }

  /**
   * Delete audit file securely
   */
  private async deleteAuditFile(filePath: string): Promise<void> {
    if (this.config.retentionPolicy.deleteMethod === 'secure') {
      // Secure delete: overwrite with random data multiple times
      const stats = await stat(filePath);
      const size = stats.size;

      for (let i = 0; i < 3; i++) {
        const randomData = randomBytes(size);
        await writeFile(filePath, randomData);
      }
    }

    await unlink(filePath);
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Query events from log files
   */
  private async queryEvents(
    startTime: Date,
    endTime: Date,
    filters: {
      actorIds?: string[];
      categories?: AuditCategory[];
      severities?: AuditSeverity[];
      resourceTypes?: string[];
    }
  ): Promise<AuditEvent[]> {
    const files = await this.getAuditLogFiles();
    const events: AuditEvent[] = [];

    for (const file of files) {
      const content = await readFile(file.path, 'utf-8');
      const lines = content.split('\n').filter(l => l.trim());

      for (const line of lines) {
        try {
          const event: AuditEvent = JSON.parse(line);

          // Time range filter
          if (event.timestamp < startTime || event.timestamp > endTime) {
            continue;
          }

          // Apply filters
          if (filters.actorIds && !filters.actorIds.includes(event.actor.id)) {
            continue;
          }
          if (filters.categories && !filters.categories.includes(event.category)) {
            continue;
          }
          if (filters.severities && !filters.severities.includes(event.severity)) {
            continue;
          }
          if (filters.resourceTypes && !filters.resourceTypes.includes(event.resource.type)) {
            continue;
          }

          events.push(event);
        } catch (err) {
          console.error('Error parsing audit event:', err);
        }
      }
    }

    return events.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  /**
   * Query events by incident ID
   */
  private async queryEventsByIncident(incidentId: string): Promise<AuditEvent[]> {
    const files = await this.getAuditLogFiles();
    const events: AuditEvent[] = [];

    for (const file of files) {
      const content = await readFile(file.path, 'utf-8');
      const lines = content.split('\n').filter(l => l.trim());

      for (const line of lines) {
        try {
          const event: AuditEvent = JSON.parse(line);
          if (event.resource.id === incidentId ||
              event.details.incidentId === incidentId) {
            events.push(event);
          }
        } catch (err) {
          console.error('Error parsing audit event:', err);
        }
      }
    }

    return events.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  /**
   * Generate summary from events
   */
  private generateSummary(events: AuditEvent[]): AuditTrail['summary'] {
    const bySeverity: Record<AuditSeverity, number> = {
      [AuditSeverity.LOW]: 0,
      [AuditSeverity.MEDIUM]: 0,
      [AuditSeverity.HIGH]: 0,
      [AuditSeverity.CRITICAL]: 0
    };

    const byCategory: Record<AuditCategory, number> = {
      [AuditCategory.AUTHENTICATION]: 0,
      [AuditCategory.AUTHORIZATION]: 0,
      [AuditCategory.ACCESS_CONTROL]: 0,
      [AuditCategory.DATA_ACCESS]: 0,
      [AuditCategory.DATA_MODIFICATION]: 0,
      [AuditCategory.SYSTEM_CONFIG]: 0,
      [AuditCategory.THREAT_DETECTION]: 0,
      [AuditCategory.INCIDENT_RESPONSE]: 0,
      [AuditCategory.COMPLIANCE]: 0,
      [AuditCategory.PRIVACY]: 0
    };

    const byActor: Record<string, number> = {};

    for (const event of events) {
      bySeverity[event.severity]++;
      byCategory[event.category]++;
      byActor[event.actor.id] = (byActor[event.actor.id] || 0) + 1;
    }

    return {
      totalEvents: events.length,
      bySeverity,
      byCategory,
      byActor,
      timeRange: {
        start: events[0]?.timestamp || new Date(),
        end: events[events.length - 1]?.timestamp || new Date()
      }
    };
  }

  /**
   * Get controls for compliance standard
   */
  private getControlsForStandard(standard: ComplianceStandard): Array<{
    id: string;
    name: string;
    description: string;
  }> {
    const controls: Record<ComplianceStandard, Array<{ id: string; name: string; description: string }>> = {
      [ComplianceStandard.SOC2]: [
        { id: 'CC1.1', name: 'Access Control', description: 'Logical and physical access controls' },
        { id: 'CC2.1', name: 'Encryption', description: 'Data encryption at rest and in transit' },
        { id: 'CC3.2', name: 'Audit Logging', description: 'Comprehensive audit trails' },
        { id: 'CC4.1', name: 'Change Management', description: 'Controlled change processes' },
        { id: 'CC5.1', name: 'Incident Response', description: 'Security incident handling' },
        { id: 'CC6.1', name: 'Risk Assessment', description: 'Regular risk assessments' },
        { id: 'CC7.2', name: 'Monitoring', description: 'Continuous security monitoring' }
      ],
      [ComplianceStandard.GDPR]: [
        { id: 'Art.32', name: 'Security of Processing', description: 'Technical and organizational measures' },
        { id: 'Art.33', name: 'Breach Notification', description: 'Personal data breach reporting' },
        { id: 'Art.25', name: 'Privacy by Design', description: 'Data protection by design and default' },
        { id: 'Art.30', name: 'Records of Processing', description: 'Documentation of processing activities' },
        { id: 'Art.35', name: 'DPIA', description: 'Data protection impact assessments' }
      ],
      [ComplianceStandard.HIPAA]: [
        { id: '164.308(a)', name: 'Security Management', description: 'Administrative safeguards' },
        { id: '164.312(a)', name: 'Access Controls', description: 'Technical access controls' },
        { id: '164.312(e)', name: 'Transmission Security', description: 'Encryption and controls' },
        { id: '164.310(b)', name: 'Audit Controls', description: 'Hardware and software audits' },
        { id: '164.308(a)(1)', name: 'Risk Analysis', description: 'Risk assessment and management' }
      ],
      [ComplianceStandard.ISO27001]: [
        { id: 'A.9.1', name: 'Access Control', description: 'Access control policy' },
        { id: 'A.12.3', name: 'Backup', description: 'Information backup' },
        { id: 'A.12.4', name: 'Logging', description: 'Logging and monitoring' },
        { id: 'A.14.1', name: 'Incident Management', description: 'Information security incidents' },
        { id: 'A.16.1', name: 'Compliance', description: 'Compliance with requirements' }
      ],
      [ComplianceStandard.PCIDSS]: [
        { id: 'Req.7', name: 'Access Control', description: 'Restrict access to system components' },
        { id: 'Req.8', name: 'Authentication', description: 'Identification and authentication' },
        { id: 'Req.10', name: 'Logging', description: 'Track and monitor all access' },
        { id: 'Req.11', name: 'Testing', description: 'Regular security testing' },
        { id: 'Req.12', name: 'Policy', description: 'Information security policy' }
      ]
    };

    return controls[standard] || [];
  }

  /**
   * Evaluate control compliance
   */
  private async evaluateControl(
    control: { id: string; name: string; description: string },
    events: AuditEvent[]
  ): Promise<'compliant' | 'non-compliant' | 'partial'> {
    // This is a simplified evaluation
    // In production, this would be more sophisticated based on control requirements

    const relevantEvents = events.filter(e =>
      e.category === AuditCategory.COMPLIANCE ||
      e.category === AuditCategory.THREAT_DETECTION ||
      e.category === AuditCategory.INCIDENT_RESPONSE
    );

    if (relevantEvents.length === 0) {
      return 'non-compliant';
    }

    const successRate = relevantEvents.filter(e => e.outcome === 'success').length / relevantEvents.length;

    if (successRate >= 0.95) {
      return 'compliant';
    } else if (successRate >= 0.7) {
      return 'partial';
    } else {
      return 'non-compliant';
    }
  }

  /**
   * Get evidence for control
   */
  private getEvidenceForControl(
    control: { id: string; name: string },
    events: AuditEvent[]
  ): string[] {
    return events
      .filter(e => e.details.controlId === control.id || e.details.control === control.name)
      .map(e => `${e.timestamp.toISOString()}: ${e.action}`);
  }

  /**
   * Get findings for control
   */
  private getFindingsForControl(
    control: { id: string; name: string },
    events: AuditEvent[]
  ): string[] {
    const findings: string[] = [];

    const failures = events.filter(e => e.outcome === 'failure');
    if (failures.length > 0) {
      findings.push(`${failures.length} failures detected`);
    }

    const critical = events.filter(e => e.severity === AuditSeverity.CRITICAL);
    if (critical.length > 0) {
      findings.push(`${critical.length} critical events`);
    }

    return findings;
  }

  /**
   * Generate recommendations
   */
  private generateRecommendations(
    controls: ComplianceReport['controls']
  ): string[] {
    const recommendations: string[] = [];

    for (const control of controls) {
      if (control.status !== 'compliant') {
        recommendations.push(`Address ${control.id} (${control.name}): ${control.findings.join(', ')}`);
      }
    }

    return recommendations;
  }

  /**
   * Detect patterns in events
   */
  private detectPatterns(events: AuditEvent[]): Pattern[] {
    const patterns: Pattern[] = [];

    // Detect repeated failed authentication
    const failedAuth = events.filter(e =>
      e.category === AuditCategory.AUTHENTICATION &&
      e.action === 'auth_failed_attempt'
    );
    const byActor = this.groupBy(failedAuth, e => e.actor.id);
    for (const [actorId, actorEvents] of Object.entries(byActor)) {
      if (actorEvents.length >= 3) {
        patterns.push({
          type: 'repeated_failed_auth',
          description: `Multiple failed authentication attempts by ${actorId}`,
          frequency: actorEvents.length,
          examples: actorEvents.slice(0, 3),
          confidence: 0.9
        });
      }
    }

    // Detect access pattern anomalies
    const accessEvents = events.filter(e => e.category === AuditCategory.DATA_ACCESS);
    const byResource = this.groupBy(accessEvents, e => e.resource.id || e.resource.path);
    for (const [resourceId, resourceEvents] of Object.entries(byResource)) {
      if (resourceEvents.length >= 10) {
        patterns.push({
          type: 'high_frequency_access',
          description: `High frequency access to ${resourceId}`,
          frequency: resourceEvents.length,
          examples: resourceEvents.slice(0, 3),
          confidence: 0.8
        });
      }
    }

    return patterns;
  }

  /**
   * Detect anomalies in events
   */
  private detectAnomalies(events: AuditEvent[]): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Detect unusual time access
    const nightEvents = events.filter(e => {
      const hour = e.timestamp.getHours();
      return hour >= 22 || hour <= 6;
    });
    if (nightEvents.length > 0) {
      anomalies.push({
        type: 'unusual_time_access',
        description: 'Access during unusual hours',
        severity: AuditSeverity.MEDIUM,
        events: nightEvents.slice(0, 5),
        riskScore: 0.6
      });
    }

    // Detect privilege escalation attempts
    const escalationEvents = events.filter(e =>
      e.action.includes('escalate') ||
      e.action.includes('privilege') ||
      e.details.escalation
    );
    if (escalationEvents.length > 0) {
      anomalies.push({
        type: 'privilege_escalation',
        description: 'Potential privilege escalation attempts',
        severity: AuditSeverity.HIGH,
        events: escalationEvents,
        riskScore: 0.8
      });
    }

    // Detect bulk data access
    const bulkEvents = events.filter(e =>
      e.details.bulk ||
      e.details.quantity && e.details.quantity > 100
    );
    if (bulkEvents.length > 0) {
      anomalies.push({
        type: 'bulk_data_access',
        description: 'Bulk data access detected',
        severity: AuditSeverity.HIGH,
        events: bulkEvents,
        riskScore: 0.7
      });
    }

    return anomalies;
  }

  /**
   * Build timeline from events
   */
  private buildTimeline(events: AuditEvent[]): TimelineEvent[] {
    return events
      .filter(e => e.severity !== AuditSeverity.LOW)
      .map(event => ({
        timestamp: event.timestamp,
        event,
        significance: this.calculateSignificance(event)
      }))
      .sort((a, b) => b.significance - a.significance)
      .slice(0, 100);
  }

  /**
   * Calculate event significance
   */
  private calculateSignificance(event: AuditEvent): number {
    let score = 0;

    // Severity score
    const severityScores = {
      [AuditSeverity.LOW]: 1,
      [AuditSeverity.MEDIUM]: 3,
      [AuditSeverity.HIGH]: 7,
      [AuditSeverity.CRITICAL]: 10
    };
    score += severityScores[event.severity];

    // Outcome score
    if (event.outcome === 'failure') score += 5;

    // Category score
    if (event.category === AuditCategory.INCIDENT_RESPONSE) score += 8;
    if (event.category === AuditCategory.THREAT_DETECTION) score += 6;

    return score;
  }

  /**
   * Find connections between events
   */
  private findConnections(events: AuditEvent[]): Connection[] {
    const connections: Connection[] = [];

    for (let i = 0; i < events.length; i++) {
      for (let j = i + 1; j < events.length; j++) {
        const from = events[i];
        const to = events[j];

        // Check for actor relationship
        if (from.actor.id === to.actor.id) {
          const timeDiff = Math.abs(to.timestamp.getTime() - from.timestamp.getTime());
          if (timeDiff < 60000) { // Within 1 minute
            connections.push({
              from,
              to,
              relationship: 'same_actor_sequence',
              strength: 1 - (timeDiff / 60000)
            });
          }
        }

        // Check for resource relationship
        if (from.resource.id === to.resource.id) {
          connections.push({
            from,
            to,
            relationship: 'same_resource',
            strength: 0.8
          });
        }

        // Check for causal relationship
        if (from.metadata.correlationId === to.metadata.correlationId) {
          connections.push({
            from,
            to,
            relationship: 'causal',
            strength: 1.0
          });
        }
      }
    }

    return connections.sort((a, b) => b.strength - a.strength).slice(0, 50);
  }

  /**
   * Generate conclusions from analysis
   */
  private generateConclusions(
    patterns: Pattern[],
    anomalies: Anomaly[],
    connections: Connection[]
  ): string[] {
    const conclusions: string[] = [];

    if (patterns.length > 0) {
      conclusions.push(`Detected ${patterns.length} significant patterns`);
    }

    if (anomalies.length > 0) {
      conclusions.push(`Identified ${anomalies.length} anomalies requiring attention`);
    }

    const highRiskAnomalies = anomalies.filter(a => a.riskScore > 0.7);
    if (highRiskAnomalies.length > 0) {
      conclusions.push(`Found ${highRiskAnomalies.length} high-risk anomalies`);
    }

    if (connections.length > 10) {
      conclusions.push('Strong event correlations indicate coordinated activity');
    }

    if (conclusions.length === 0) {
      conclusions.push('No significant security concerns identified');
    }

    return conclusions;
  }

  /**
   * Generate forensic recommendations
   */
  private generateForensicRecommendations(
    patterns: Pattern[],
    anomalies: Anomaly[]
  ): string[] {
    const recommendations: string[] = [];

    for (const anomaly of anomalies) {
      if (anomaly.riskScore > 0.7) {
        recommendations.push(`Investigate ${anomaly.type}: ${anomaly.description}`);
      }
    }

    for (const pattern of patterns) {
      if (pattern.confidence > 0.8) {
        recommendations.push(`Review ${pattern.type}: ${pattern.description}`);
      }
    }

    if (anomalies.some(a => a.type === 'privilege_escalation')) {
      recommendations.push('Review privilege assignment and escalation policies');
    }

    if (anomalies.some(a => a.type === 'bulk_data_access')) {
      recommendations.push('Implement additional controls for bulk data access');
    }

    return recommendations;
  }

  // ============================================================================
  // Hash Chain Methods
  // ============================================================================

  /**
   * Generate genesis hash
   */
  private genesisHash(): string {
    return createHash('sha256').update('POLLN-AUDIT-GENESIS').digest('hex');
  }

  /**
   * Compute event hash
   */
  private computeEventHash(event: AuditEvent): string {
    const data = JSON.stringify({
      id: event.id,
      timestamp: event.timestamp.toISOString(),
      severity: event.severity,
      category: event.category,
      actor: event.actor,
      action: event.action,
      resource: event.resource,
      outcome: event.outcome,
      details: event.details,
      previousHash: event.previousHash
    });

    return createHash('sha256').update(data).digest('hex');
  }

  /**
   * Sign event
   */
  private signEvent(event: AuditEvent): string {
    if (!this.config.signingKey) {
      throw new Error('No signing key configured');
    }

    const sign = createSign('SHA256');
    sign.update(event.hash);
    sign.end();

    return sign.sign(this.config.signingKey, 'hex');
  }

  /**
   * Verify event signature
   */
  private verifySignature(event: AuditEvent, signature: string): boolean {
    if (!this.config.verifyKey) {
      return true; // Skip verification if no key
    }

    const verify = createVerify('SHA256');
    verify.update(event.hash);
    verify.end();

    return verify.verify(this.config.verifyKey, signature, 'hex');
  }

  /**
   * Sign report
   */
  private signReport(report: ComplianceReport): string {
    if (!this.config.signingKey) {
      throw new Error('No signing key configured');
    }

    const data = JSON.stringify({
      standard: report.standard,
      period: report.period,
      generatedAt: report.generatedAt.toISOString(),
      overallStatus: report.overallStatus
    });

    const sign = createSign('SHA256');
    sign.update(data);
    sign.end();

    return sign.sign(this.config.signingKey, 'hex');
  }

  /**
   * Load hash chain from disk
   */
  private async loadHashChain(): Promise<void> {
    try {
      if (existsSync(this.chainStoreFile)) {
        const content = await readFile(this.chainStoreFile, 'utf-8');
        this.hashChain = JSON.parse(content);
      }
    } catch (err) {
      console.error('Error loading hash chain:', err);
      this.hashChain = [];
    }
  }

  /**
   * Save hash chain to disk
   */
  private async saveHashChain(): Promise<void> {
    try {
      await writeFile(this.chainStoreFile, JSON.stringify(this.hashChain, null, 2));
    } catch (err) {
      console.error('Error saving hash chain:', err);
    }
  }

  // ============================================================================
  // File Management
  // ============================================================================

  /**
   * Get audit log files
   */
  private async getAuditLogFiles(): Promise<Array<{ path: string; date: Date }>> {
    const fs = await import('fs/promises');
    const files: Array<{ path: string; date: Date }> = [];

    try {
      const entries = await fs.readdir(this.config.logDirectory, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isFile() && entry.name.startsWith('audit-') && entry.name.endsWith('.log')) {
          const filePath = join(this.config.logDirectory, entry.name);
          const stats = await fs.stat(filePath);
          files.push({ path: filePath, date: stats.mtime });
        }
      }
    } catch (err) {
      console.error('Error reading audit directory:', err);
    }

    return files.sort((a, b) => b.date.getTime() - a.date.getTime());
  }

  /**
   * Flush event buffer to disk
   */
  public async flush(): Promise<void> {
    if (this.eventBuffer.length === 0 || this.isShuttingDown) {
      return;
    }

    try {
      // Determine log file
      const date = new Date().toISOString().split('T')[0];
      const logFile = join(this.config.logDirectory, `audit-${date}.log`);

      // Check file size
      let targetFile = logFile;
      if (existsSync(logFile)) {
        const stats = await stat(logFile);
        if (stats.size >= this.config.maxSize) {
          // Rotate file
          const timestamp = Date.now();
          targetFile = join(this.config.logDirectory, `audit-${date}-${timestamp}.log`);
        }
      }

      // Write events
      for (const event of this.eventBuffer) {
        await appendFile(targetFile, JSON.stringify(event) + '\n');
      }

      // Clear buffer
      this.eventBuffer = [];

      // Save hash chain
      await this.saveHashChain();
    } catch (err) {
      console.error('Error flushing audit events:', err);
    }
  }

  /**
   * Generate unique event ID
   */
  private generateEventId(): string {
    return `evt-${Date.now()}-${randomBytes(8).toString('hex')}`;
  }

  /**
   * Group array by key function
   */
  private groupBy<T>(array: T[], keyFn: (item: T) => string): Record<string, T[]> {
    return array.reduce((groups, item) => {
      const key = keyFn(item);
      groups[key] = groups[key] || [];
      groups[key].push(item);
      return groups;
    }, {} as Record<string, T[]>);
  }

  // ============================================================================
  // Lifecycle Management
  // ============================================================================

  /**
   * Shutdown audit system
   */
  async shutdown(): Promise<void> {
    if (this.isShuttingDown) {
      return;
    }

    this.isShuttingDown = true;

    // Clear flush timer
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    // Flush remaining events
    await this.flush();

    // Apply retention policy
    await this.applyRetentionPolicy();
  }

  /**
   * Get audit system statistics
   */
  async getStatistics(): Promise<{
    totalEvents: number;
    bufferLength: number;
    hashChainLength: number;
    logFiles: number;
    retentionStatus: string;
  }> {
    const logFiles = await this.getAuditLogFiles();

    return {
      totalEvents: this.eventCounter,
      bufferLength: this.eventBuffer.length,
      hashChainLength: this.hashChain.length,
      logFiles: logFiles.length,
      retentionStatus: 'active'
    };
  }
}

// ============================================================================
// Singleton Instance
// ============================================================================

let auditSystemInstance: AuditSystem | null = null;

/**
 * Get or create audit system instance
 */
export function getAuditSystem(config?: Partial<AuditSystemConfig>): AuditSystem {
  if (!auditSystemInstance) {
    auditSystemInstance = new AuditSystem(config);
  }
  return auditSystemInstance;
}

/**
 * Shutdown audit system
 */
export async function shutdownAuditSystem(): Promise<void> {
  if (auditSystemInstance) {
    await auditSystemInstance.shutdown();
    auditSystemInstance = null;
  }
}
