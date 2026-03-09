/**
 * POLLN Microbiome - Threat Detection System
 *
 * Phase 9: Security & Safety - Milestone 2
 * Comprehensive threat detection and security monitoring system for identifying
 * and responding to security threats in the microbiome ecosystem.
 *
 * @module microbiome/threat-detection
 */

import {
  MicrobiomeAgent,
  AgentTaxonomy,
  EcosystemSnapshot,
  ResourceType,
  Symbiosis,
} from './types.js';
import { SecurityManager, SecurityEvent, SecurityMetrics } from './security.js';
import { AnalyticsPipeline, AnalyticsEventType } from './analytics.js';

/**
 * Threat types in the microbiome ecosystem
 */
export enum ThreatType {
  /** Malicious agent behavior */
  MALICIOUS_AGENT = 'malicious_agent',
  /** Code or data injection attack */
  INJECTION_ATTACK = 'injection_attack',
  /** Denial of service attack */
  DOS_ATTACK = 'dos_attack',
  /** Unauthorized privilege escalation */
  PRIVILEGE_ESCALATION = 'privilege_escalation',
  /** Data theft or exfiltration */
  DATA_EXFILTRATION = 'data_exfiltration',
  /** Message replay attack */
  REPLAY_ATTACK = 'replay_attack',
  /** Man-in-the-middle interception */
  MAN_IN_THE_MIDDLE = 'man_in_the_middle',
  /** Resource exhaustion */
  RESOURCE_EXHAUSTION = 'resource_exhaustion',
  /** Suspicious communication pattern */
  SUSPICIOUS_COMMUNICATION = 'suspicious_communication',
  /** Abnormal agent behavior */
  BEHAVIORAL_ANOMALY = 'behavioral_anomaly',
  /** Configuration vulnerability */
  CONFIGURATION_VULNERABILITY = 'configuration_vulnerability',
  /** Dependency vulnerability */
  DEPENDENCY_VULNERABILITY = 'dependency_vulnerability',
}

/**
 * Threat severity levels
 */
export enum ThreatLevel {
  /** No threat detected */
  NONE = 'none',
  /** Low severity - informational */
  LOW = 'low',
  /** Medium severity - requires attention */
  MEDIUM = 'medium',
  /** High severity - requires immediate action */
  HIGH = 'high',
  /** Critical severity - system at risk */
  CRITICAL = 'critical',
}

/**
 * Anomaly detection result
 */
export interface AnomalyReport {
  /** Agent ID */
  agentId: string;
  /** Whether anomaly was detected */
  isAnomalous: boolean;
  /** Anomaly score (0-1) */
  anomalyScore: number;
  /** Detected anomalies */
  anomalies: Anomaly[];
  /** Timestamp */
  timestamp: number;
  /** Baseline used for comparison */
  baseline: BehavioralBaseline;
}

/**
 * Individual anomaly
 */
export interface Anomaly {
  /** Anomaly type */
  type: AnomalyType;
  /** Severity (0-1) */
  severity: number;
  /** Description */
  description: string;
  /** Affected metrics */
  affectedMetrics: string[];
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Types of anomalies
 */
export enum AnomalyType {
  /** Statistical outlier */
  STATISTICAL_OUTLIER = 'statistical_outlier',
  /** Behavioral deviation */
  BEHAVIORAL_DEVIATION = 'behavioral_deviation',
  /** Resource consumption anomaly */
  RESOURCE_ANOMALY = 'resource_anomaly',
  /** Communication anomaly */
  COMMUNICATION_ANOMALY = 'communication_anomaly',
  /** Performance anomaly */
  PERFORMANCE_ANOMALY = 'performance_anomaly',
  /** Pattern deviation */
  PATTERN_DEVIATION = 'pattern_deviation',
}

/**
 * Behavioral baseline for an agent
 */
export interface BehavioralBaseline {
  /** Agent ID */
  agentId: string;
  /** Baseline timestamp */
  timestamp: number;
  /** Resource consumption baseline */
  resourceBaseline: ResourceBaseline;
  /** Communication baseline */
  communicationBaseline: CommunicationBaseline;
  /** Performance baseline */
  performanceBaseline: PerformanceBaseline;
  /** Activity patterns */
  activityPatterns: ActivityPattern[];
}

/**
 * Resource consumption baseline
 */
export interface ResourceBaseline {
  /** Average consumption rates by resource type */
  averageConsumption: Map<ResourceType, number>;
  /** Standard deviation */
  stdDeviation: Map<ResourceType, number>;
  /** Peak consumption */
  peakConsumption: Map<ResourceType, number>;
  /** Typical consumption patterns */
  patterns: ResourcePattern[];
}

/**
 * Resource consumption pattern
 */
export interface ResourcePattern {
  /** Resource type */
  resource: ResourceType;
  /** Time-based pattern (hourly averages) */
  hourlyPattern: number[];
  /** Typical duration */
  typicalDuration: number;
  /** Frequency */
  frequency: number;
}

/**
 * Communication baseline
 */
export interface CommunicationBaseline {
  /** Average message rate */
  averageMessageRate: number;
  /** Typical communication partners */
  typicalPartners: Set<string>;
  /** Message size distribution */
  messageSizeDistribution: {
    min: number;
    max: number;
    average: number;
    percentile95: number;
  };
  /** Communication frequency patterns */
  frequencyPatterns: Map<string, number>;
}

/**
 * Performance baseline
 */
export interface PerformanceBaseline {
  /** Average processing time */
  averageProcessingTime: number;
  /** Throughput baseline */
  throughputBaseline: number;
  /** Success rate baseline */
  successRateBaseline: number;
  /** Error rate baseline */
  errorRateBaseline: number;
  /** Latency percentiles */
  latencyPercentiles: {
    p50: number;
    p95: number;
    p99: number;
  };
}

/**
 * Activity pattern
 */
export interface ActivityPattern {
  /** Pattern type */
  type: 'circadian' | 'burst' | 'periodic' | 'irregular';
  /** Period in milliseconds */
  period: number;
  /** Amplitude */
  amplitude: number;
  /** Phase offset */
  phase: number;
  /** Confidence */
  confidence: number;
}

/**
 * Intrusion detection alert
 */
export interface IntrusionAlert {
  /** Alert ID */
  alertId: string;
  /** Threat type */
  threatType: ThreatType;
  /** Threat level */
  threatLevel: ThreatLevel;
  /** Source agent(s) */
  sourceAgents: string[];
  /** Target agent(s) */
  targetAgents: string[];
  /** Description */
  description: string;
  /** Evidence */
  evidence: Evidence[];
  /** Timestamp */
  timestamp: number;
  /** Recommended actions */
  recommendedActions: RecommendedAction[];
  /** False positive probability (0-1) */
  falsePositiveProbability: number;
}

/**
 * Evidence for security alert
 */
export interface Evidence {
  /** Evidence type */
  type: EvidenceType;
  /** Description */
  description: string;
  /** Evidence data */
  data: Record<string, any>;
  /** Timestamp */
  timestamp: number;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Evidence types
 */
export enum EvidenceType {
  /** Log entry */
  LOG_ENTRY = 'log_entry',
  /** Metrics data */
  METRICS_DATA = 'metrics_data',
  /** Network traffic */
  NETWORK_TRAFFIC = 'network_traffic',
  /** System call */
  SYSTEM_CALL = 'system_call',
  /** File access */
  FILE_ACCESS = 'file_access',
  /** Resource access */
  RESOURCE_ACCESS = 'resource_access',
  /** Communication pattern */
  COMMUNICATION_PATTERN = 'communication_pattern',
}

/**
 * Recommended action
 */
export interface RecommendedAction {
  /** Action type */
  type: ActionType;
  /** Priority */
  priority: 'low' | 'medium' | 'high' | 'critical';
  /** Description */
  description: string;
  /** Parameters */
  parameters: Record<string, any>;
  /** Expected outcome */
  expectedOutcome: string;
}

/**
 * Action types for threat response
 */
export enum ActionType {
  /** Isolate agent from network */
  ISOLATE_AGENT = 'isolate_agent',
  /** Terminate agent */
  TERMINATE_AGENT = 'terminate_agent',
  /** Revoke credentials */
  REVOKE_CREDENTIALS = 'revoke_credentials',
  /** Block communication */
  BLOCK_COMMUNICATION = 'block_communication',
  /** Rate limit */
  RATE_LIMIT = 'rate_limit',
  /** Increase monitoring */
  INCREASE_MONITORING = 'increase_monitoring',
  /** Quarantine agent */
  QUARANTINE_AGENT = 'quarantine_agent',
  /** Scan for vulnerabilities */
  SCAN_VULNERABILITIES = 'scan_vulnerabilities',
  /** Update security rules */
  UPDATE_SECURITY_RULES = 'update_security_rules',
  /** Alert administrator */
  ALERT_ADMIN = 'alert_admin',
}

/**
 * Vulnerability scan result
 */
export interface VulnerabilityReport {
  /** Report ID */
  reportId: string;
  /** Timestamp */
  timestamp: number;
  /** Scan duration (ms) */
  scanDuration: number;
  /** Vulnerabilities found */
  vulnerabilities: Vulnerability[];
  /** Summary statistics */
  summary: VulnerabilitySummary;
  /** Recommendations */
  recommendations: string[];
}

/**
 * Individual vulnerability
 */
export interface Vulnerability {
  /** Vulnerability ID */
  id: string;
  /** Severity level */
  severity: VulnerabilitySeverity;
  /** Vulnerability type */
  type: VulnerabilityType;
  /** Title */
  title: string;
  /** Description */
  description: string;
  /** Affected components */
  affectedComponents: string[];
  /** CVSS score (0-10) */
  cvssScore?: number;
  /** CVE reference */
  cve?: string;
  /** Remediation steps */
  remediation: string[];
  /** References */
  references: string[];
}

/**
 * Vulnerability severity
 */
export enum VulnerabilitySeverity {
  /** Critical - requires immediate patching */
  CRITICAL = 'critical',
  /** High - should patch soon */
  HIGH = 'high',
  /** Medium - patch when possible */
  MEDIUM = 'medium',
  /** Low - patch when convenient */
  LOW = 'low',
  /** Informational */
  INFO = 'info',
}

/**
 * Vulnerability types
 */
export enum VulnerabilityType {
  /** Dependency vulnerability */
  DEPENDENCY = 'dependency',
  /** Configuration issue */
  CONFIGURATION = 'configuration',
  /** Code vulnerability */
  CODE_VULNERABILITY = 'code_vulnerability',
  /** Security misconfiguration */
  SECURITY_MISCONFIGURATION = 'security_misconfiguration',
  /** Cryptographic issue */
  CRYPTOGRAPHIC = 'cryptographic',
  /** Authorization issue */
  AUTHORIZATION = 'authorization',
  /** Authentication issue */
  AUTHENTICATION = 'authentication',
  /** Input validation */
  INPUT_VALIDATION = 'input_validation',
}

/**
 * Vulnerability summary
 */
export interface VulnerabilitySummary {
  /** Total vulnerabilities */
  total: number;
  /** Count by severity */
  bySeverity: Map<VulnerabilitySeverity, number>;
  /** Count by type */
  byType: Map<VulnerabilityType, number>;
  /** Average CVSS score */
  averageCvssScore: number;
  /** Percentage scanned */
  percentScanned: number;
}

/**
 * Compliance status
 */
export interface ComplianceStatus {
  /** Compliance framework */
  framework: ComplianceFramework;
  /** Overall compliance score (0-1) */
  complianceScore: number;
  /** Status by control */
  controlStatus: Map<string, ControlStatus>;
  /** Gaps identified */
  gaps: ComplianceGap[];
  /** Last assessment timestamp */
  lastAssessment: number;
  /** Recommendations */
  recommendations: string[];
}

/**
 * Compliance frameworks
 */
export enum ComplianceFramework {
  /** SOC 2 Type II */
  SOC2 = 'soc2',
  /** General Data Protection Regulation */
  GDPR = 'gdpr',
  /** Health Insurance Portability and Accountability Act */
  HIPAA = 'hipaa',
  /** ISO 27001 */
  ISO27001 = 'iso27001',
  /** NIST Cybersecurity Framework */
  NIST_CSF = 'nist_csf',
}

/**
 * Control compliance status
 */
export interface ControlStatus {
  /** Control ID */
  controlId: string;
  /** Control name */
  name: string;
  /** Description */
  description: string;
  /** Compliant status */
  isCompliant: boolean;
  /** Compliance score (0-1) */
  score: number;
  /** Evidence of compliance */
  evidence: string[];
  /** Gaps */
  gaps: string[];
}

/**
 * Compliance gap
 */
export interface ComplianceGap {
  /** Control ID */
  controlId: string;
  /** Gap description */
  description: string;
  /** Severity */
  severity: 'critical' | 'high' | 'medium' | 'low';
  /** Remediation steps */
  remediation: string[];
  /** Priority */
  priority: number;
}

/**
 * Security metrics summary
 */
export interface SecurityMetricsSummary {
  /** Overall threat level */
  overallThreatLevel: ThreatLevel;
  /** Active threats */
  activeThreats: number;
  /** Threats by level */
  threatsByLevel: Map<ThreatLevel, number>;
  /** Threats by type */
  threatsByType: Map<ThreatType, number>;
  /** Open vulnerabilities */
  openVulnerabilities: number;
  /** Compliance score */
  complianceScore: number;
  /** Security posture */
  securityPosture: SecurityPosture;
  /** Trend data */
  trends: SecurityTrend[];
  /** Timestamp */
  timestamp: number;
}

/**
 * Security posture assessment
 */
export enum SecurityPosture {
  /** Excellent security posture */
  EXCELLENT = 'excellent',
  /** Good security posture */
  GOOD = 'good',
  /** Fair security posture */
  FAIR = 'fair',
  /** Poor security posture */
  POOR = 'poor',
  /** Critical security issues */
  CRITICAL = 'critical',
}

/**
 * Security trend data
 */
export interface SecurityTrend {
  /** Metric name */
  metric: string;
  /** Direction */
  direction: 'improving' | 'stable' | 'degrading';
  /** Change percentage */
  changePercentage: number;
  /** Time period */
  period: number;
}

/**
 * Threat detector configuration
 */
export interface ThreatDetectorConfig {
  /** Anomaly detection threshold (0-1) */
  anomalyThreshold: number;
  /** Baseline update interval (ms) */
  baselineUpdateInterval: number;
  /** Intrusion detection sensitivity (0-1) */
  intrusionSensitivity: number;
  /** Vulnerability scan interval (ms) */
  vulnerabilityScanInterval: number;
  /** Compliance check interval (ms) */
  complianceCheckInterval: number;
  /** Maximum baseline history */
  maxBaselineHistory: number;
  /** Alert retention period (ms) */
  alertRetentionPeriod: number;
}

/**
 * Default threat detector configuration
 */
const DEFAULT_THREAT_DETECTOR_CONFIG: ThreatDetectorConfig = {
  anomalyThreshold: 0.7,
  baselineUpdateInterval: 3600000, // 1 hour
  intrusionSensitivity: 0.8,
  vulnerabilityScanInterval: 86400000, // 24 hours
  complianceCheckInterval: 604800000, // 7 days
  maxBaselineHistory: 100,
  alertRetentionPeriod: 2592000000, // 30 days
};

/**
 * Threat Detection System
 *
 * Comprehensive security monitoring system that detects anomalies,
 * intrusions, vulnerabilities, and compliance issues in the microbiome.
 */
export class ThreatDetector {
  private securityManager: SecurityManager;
  private analyticsPipeline?: AnalyticsPipeline;
  private config: ThreatDetectorConfig;

  // Behavioral baselines for agents
  private baselines: Map<string, BehavioralBaseline>;
  private baselineHistory: Map<string, BehavioralBaseline[]>;

  // Recent activity for pattern analysis
  private recentActivity: Map<string, SecurityEvent[]>;

  // Active alerts
  private activeAlerts: Map<string, IntrusionAlert>;
  private alertHistory: IntrusionAlert[];

  // Known threat signatures
  private threatSignatures: Map<ThreatType, ThreatSignature>;

  // Vulnerability database
  private vulnerabilityDatabase: Map<string, Vulnerability>;

  // Compliance control mappings
  private complianceControls: Map<ComplianceFramework, Map<string, ControlStatus>>;

  /**
   * Create a new threat detector
   */
  constructor(
    securityManager: SecurityManager,
    analyticsPipeline?: AnalyticsPipeline,
    config: Partial<ThreatDetectorConfig> = {}
  ) {
    this.securityManager = securityManager;
    this.analyticsPipeline = analyticsPipeline;
    this.config = { ...DEFAULT_THREAT_DETECTOR_CONFIG, ...config };

    this.baselines = new Map();
    this.baselineHistory = new Map();
    this.recentActivity = new Map();
    this.activeAlerts = new Map();
    this.alertHistory = [];
    this.threatSignatures = new Map();
    this.vulnerabilityDatabase = new Map();
    this.complianceControls = new Map();

    this.initializeThreatSignatures();
    this.initializeComplianceControls();
  }

  /**
   * Detect anomalies in agent behavior
   */
  detectAnomaly(agent: MicrobiomeAgent, currentMetrics: any): AnomalyReport {
    const baseline = this.baselines.get(agent.id);
    const anomalies: Anomaly[] = [];
    let isAnomalous = false;

    if (!baseline) {
      // Create initial baseline
      this.createBaseline(agent, currentMetrics);
      return {
        agentId: agent.id,
        isAnomalous: false,
        anomalyScore: 0,
        anomalies: [],
        timestamp: Date.now(),
        baseline: this.baselines.get(agent.id)!,
      };
    }

    // Check for resource anomalies
    const resourceAnomalies = this.detectResourceAnomalies(agent, baseline, currentMetrics);
    anomalies.push(...resourceAnomalies);

    // Check for communication anomalies
    const commAnomalies = this.detectCommunicationAnomalies(agent, baseline, currentMetrics);
    anomalies.push(...commAnomalies);

    // Check for performance anomalies
    const perfAnomalies = this.detectPerformanceAnomalies(agent, baseline, currentMetrics);
    anomalies.push(...perfAnomalies);

    // Check for statistical outliers
    const statisticalAnomalies = this.detectStatisticalOutliers(agent, baseline, currentMetrics);
    anomalies.push(...statisticalAnomalies);

    // Calculate overall anomaly score
    const anomalyScore = this.calculateAnomalyScore(anomalies);
    isAnomalous = anomalyScore >= this.config.anomalyThreshold;

    // Log detection event
    if (this.analyticsPipeline && isAnomalous) {
      this.analyticsPipeline.recordEvent(
        AnalyticsEventType.ANOMALY_DETECTED,
        {
          agentId: agent.id,
          anomalyScore,
          anomalies,
        }
      );
    }

    return {
      agentId: agent.id,
      isAnomalous,
      anomalyScore,
      anomalies,
      timestamp: Date.now(),
      baseline,
    };
  }

  /**
   * Detect intrusion attempts
   */
  detectIntrusion(activities: SecurityEvent[]): IntrusionAlert[] {
    const alerts: IntrusionAlert[] = [];

    // Analyze activities for threat signatures
    for (const activity of activities) {
      const detectedThreats = this.matchThreatSignatures(activity);

      for (const threat of detectedThreats) {
        const alert = this.createIntrusionAlert(threat, activity);
        alerts.push(alert);
        this.activeAlerts.set(alert.alertId, alert);
      }
    }

    // Check for suspicious patterns
    const patternAlerts = this.detectSuspiciousPatterns(activities);
    alerts.push(...patternAlerts);

    // Check for escalation attempts
    const escalationAlerts = this.detectPrivilegeEscalation(activities);
    alerts.push(...escalationAlerts);

    return alerts;
  }

  /**
   * Scan for vulnerabilities
   */
  async scanVulnerabilities(system: {
    agents: Map<string, MicrobiomeAgent>;
    dependencies: Map<string, string>;
    configuration: Record<string, any>;
  }): Promise<VulnerabilityReport> {
    const startTime = Date.now();
    const vulnerabilities: Vulnerability[] = [];

    // Scan dependencies
    const depVulnerabilities = await this.scanDependencies(system.dependencies);
    vulnerabilities.push(...depVulnerabilities);

    // Scan configuration
    const configVulnerabilities = this.scanConfiguration(system.configuration);
    vulnerabilities.push(...configVulnerabilities);

    // Scan agent code for vulnerabilities
    const agentVulnerabilities = await this.scanAgents(system.agents);
    vulnerabilities.push(...agentVulnerabilities);

    // Generate summary
    const summary = this.generateVulnerabilitySummary(vulnerabilities);

    // Generate recommendations
    const recommendations = this.generateVulnerabilityRecommendations(vulnerabilities);

    const report: VulnerabilityReport = {
      reportId: this.generateId(),
      timestamp: Date.now(),
      scanDuration: Date.now() - startTime,
      vulnerabilities,
      summary,
      recommendations,
    };

    return report;
  }

  /**
   * Monitor compliance
   */
  monitorCompliance(framework: ComplianceFramework): ComplianceStatus {
    const controls = this.complianceControls.get(framework);
    if (!controls) {
      throw new Error(`Compliance framework ${framework} not configured`);
    }

    const controlStatus = new Map<string, ControlStatus>();
    const gaps: ComplianceGap[] = [];
    let totalScore = 0;

    // Evaluate each control
    for (const [controlId, control] of controls) {
      const status = this.evaluateControl(control);
      controlStatus.set(controlId, status);

      if (!status.isCompliant) {
        gaps.push(...status.gaps.map(gap => ({
          controlId,
          ...gap,
        })));
      }

      totalScore += status.score;
    }

    const complianceScore = totalScore / controls.size;
    const recommendations = this.generateComplianceRecommendations(gaps, framework);

    return {
      framework,
      complianceScore,
      controlStatus,
      gaps,
      lastAssessment: Date.now(),
      recommendations,
    };
  }

  /**
   * Get security metrics summary
   */
  getSecurityMetrics(): SecurityMetricsSummary {
    const threatsByLevel = new Map<ThreatLevel, number>();
    const threatsByType = new Map<ThreatType, number>();

    // Count active threats
    for (const alert of this.activeAlerts.values()) {
      threatsByLevel.set(
        alert.threatLevel,
        (threatsByLevel.get(alert.threatLevel) || 0) + 1
      );
      threatsByType.set(
        alert.threatType,
        (threatsByType.get(alert.threatType) || 0) + 1
      );
    }

    // Calculate overall threat level
    const overallThreatLevel = this.calculateOverallThreatLevel();

    // Get open vulnerabilities
    const openVulnerabilities = this.vulnerabilityDatabase.size;

    // Calculate compliance score
    let complianceScore = 0;
    for (const framework of Object.values(ComplianceFramework)) {
      try {
        const status = this.monitorCompliance(framework);
        complianceScore += status.complianceScore;
      } catch (e) {
        // Framework not configured
      }
    }
    complianceScore /= Object.keys(ComplianceFramework).length;

    // Determine security posture
    const securityPosture = this.determineSecurityPosture(
      overallThreatLevel,
      openVulnerabilities,
      complianceScore
    );

    // Generate trends
    const trends = this.generateSecurityTrends();

    return {
      overallThreatLevel,
      activeThreats: this.activeAlerts.size,
      threatsByLevel,
      threatsByType,
      openVulnerabilities,
      complianceScore,
      securityPosture,
      trends,
      timestamp: Date.now(),
    };
  }

  /**
   * Create behavioral baseline for an agent
   */
  private createBaseline(agent: MicrobiomeAgent, metrics: any): BehavioralBaseline {
    const baseline: BehavioralBaseline = {
      agentId: agent.id,
      timestamp: Date.now(),
      resourceBaseline: this.createResourceBaseline(metrics),
      communicationBaseline: this.createCommunicationBaseline(metrics),
      performanceBaseline: this.createPerformanceBaseline(metrics),
      activityPatterns: this.detectActivityPatterns(metrics),
    };

    this.baselines.set(agent.id, baseline);

    // Update history
    const history = this.baselineHistory.get(agent.id) || [];
    history.push(baseline);
    if (history.length > this.config.maxBaselineHistory) {
      history.shift();
    }
    this.baselineHistory.set(agent.id, history);

    return baseline;
  }

  /**
   * Create resource baseline
   */
  private createResourceBaseline(metrics: any): ResourceBaseline {
    const averageConsumption = new Map<ResourceType, number>();
    const stdDeviation = new Map<ResourceType, number>();
    const peakConsumption = new Map<ResourceType, number>();

    for (const resource of Object.values(ResourceType)) {
      const values = metrics.resources?.[resource] || [];
      if (values.length > 0) {
        const avg = values.reduce((a: number, b: number) => a + b, 0) / values.length;
        const variance = values.reduce((sum: number, val: number) => sum + Math.pow(val - avg, 2), 0) / values.length;
        const stdDev = Math.sqrt(variance);

        averageConsumption.set(resource, avg);
        stdDeviation.set(resource, stdDev);
        peakConsumption.set(resource, Math.max(...values));
      }
    }

    return {
      averageConsumption,
      stdDeviation,
      peakConsumption,
      patterns: [],
    };
  }

  /**
   * Create communication baseline
   */
  private createCommunicationBaseline(metrics: any): CommunicationBaseline {
    const messages = metrics.messages || [];

    const averageMessageRate = messages.length / (metrics.timeWindow || 1);
    const typicalPartners = new Set(
      messages.map((m: any) => m.partnerId).filter((p: string) => p)
    );

    const sizes = messages.map((m: any) => m.size || 0);
    const messageSizeDistribution = {
      min: sizes.length > 0 ? Math.min(...sizes) : 0,
      max: sizes.length > 0 ? Math.max(...sizes) : 0,
      average: sizes.length > 0 ? sizes.reduce((a: number, b: number) => a + b, 0) / sizes.length : 0,
      percentile95: this.percentile(sizes, 95),
    };

    const frequencyPatterns = new Map<string, number>();
    for (const partner of typicalPartners) {
      const count = messages.filter((m: any) => m.partnerId === partner).length;
      frequencyPatterns.set(partner, count / messages.length);
    }

    return {
      averageMessageRate,
      typicalPartners,
      messageSizeDistribution,
      frequencyPatterns,
    };
  }

  /**
   * Create performance baseline
   */
  private createPerformanceBaseline(metrics: any): PerformanceBaseline {
    const processingTimes = metrics.processingTimes || [];
    const operations = metrics.operations || [];

    const averageProcessingTime = processingTimes.length > 0
      ? processingTimes.reduce((a: number, b: number) => a + b, 0) / processingTimes.length
      : 0;

    const throughput = operations.length / (metrics.timeWindow || 1);

    const successful = operations.filter((op: any) => op.success).length;
    const successRate = operations.length > 0 ? successful / operations.length : 1;
    const errorRate = 1 - successRate;

    const latencyPercentiles = {
      p50: this.percentile(processingTimes, 50),
      p95: this.percentile(processingTimes, 95),
      p99: this.percentile(processingTimes, 99),
    };

    return {
      averageProcessingTime,
      throughputBaseline: throughput,
      successRateBaseline: successRate,
      errorRateBaseline: errorRate,
      latencyPercentiles,
    };
  }

  /**
   * Detect activity patterns
   */
  private detectActivityPatterns(metrics: any): ActivityPattern[] {
    // Simple pattern detection based on time series analysis
    const patterns: ActivityPattern[] = [];

    // Detect circadian patterns (24-hour cycles)
    // Detect burst patterns
    // Detect periodic patterns

    // For now, return irregular pattern as default
    patterns.push({
      type: 'irregular',
      period: 0,
      amplitude: 0,
      phase: 0,
      confidence: 0.5,
    });

    return patterns;
  }

  /**
   * Detect resource anomalies
   */
  private detectResourceAnomalies(
    agent: MicrobiomeAgent,
    baseline: BehavioralBaseline,
    currentMetrics: any
  ): Anomaly[] {
    const anomalies: Anomaly[] = [];

    for (const [resource, avgConsumption] of baseline.resourceBaseline.averageConsumption) {
      const currentValue = currentMetrics.resources?.[resource]?.slice(-1)[0] || 0;
      const stdDev = baseline.resourceBaseline.stdDeviation.get(resource) || 0;

      // Check if value is significantly different from baseline (3-sigma rule)
      const zScore = stdDev > 0 ? Math.abs((currentValue - avgConsumption) / stdDev) : 0;

      if (zScore > 3) {
        anomalies.push({
          type: AnomalyType.RESOURCE_ANOMALY,
          severity: Math.min(zScore / 5, 1),
          description: `Resource ${resource} consumption ${zScore.toFixed(1)}σ from baseline`,
          affectedMetrics: [`${resource}_consumption`],
          confidence: Math.min(zScore / 3, 1),
        });
      }
    }

    return anomalies;
  }

  /**
   * Detect communication anomalies
   */
  private detectCommunicationAnomalies(
    agent: MicrobiomeAgent,
    baseline: BehavioralBaseline,
    currentMetrics: any
  ): Anomaly[] {
    const anomalies: Anomaly[] = [];
    const messages = currentMetrics.messages || [];

    // Check message rate
    const currentRate = messages.length / (currentMetrics.timeWindow || 1);
    const baselineRate = baseline.communicationBaseline.averageMessageRate;

    if (baselineRate > 0) {
      const rateChange = Math.abs(currentRate - baselineRate) / baselineRate;
      if (rateChange > 2) { // More than 2x change
        anomalies.push({
          type: AnomalyType.COMMUNICATION_ANOMALY,
          severity: Math.min(rateChange / 5, 1),
          description: `Message rate ${rateChange.toFixed(1)}x from baseline`,
          affectedMetrics: ['message_rate'],
          confidence: Math.min(rateChange / 2, 1),
        });
      }
    }

    // Check for new communication partners
    const currentPartners = new Set(messages.map((m: any) => m.partnerId).filter((p: string) => p));
    const typicalPartners = baseline.communicationBaseline.typicalPartners;

    const newPartners = [...currentPartners].filter(p => !typicalPartners.has(p));
    if (newPartners.length > 0 && typicalPartners.size > 0) {
      const newPartnerRatio = newPartners.length / typicalPartners.size;
      if (newPartnerRatio > 0.5) {
        anomalies.push({
          type: AnomalyType.COMMUNICATION_ANOMALY,
          severity: Math.min(newPartnerRatio, 1),
          description: `Communicating with ${newPartners.length} new partners`,
          affectedMetrics: ['communication_partners'],
          confidence: 0.7,
        });
      }
    }

    return anomalies;
  }

  /**
   * Detect performance anomalies
   */
  private detectPerformanceAnomalies(
    agent: MicrobiomeAgent,
    baseline: BehavioralBaseline,
    currentMetrics: any
  ): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Check processing time
    const currentProcessingTime = currentMetrics.processingTimes?.slice(-1)[0] || 0;
    const baselineProcessingTime = baseline.performanceBaseline.averageProcessingTime;

    if (baselineProcessingTime > 0) {
      const timeChange = Math.abs(currentProcessingTime - baselineProcessingTime) / baselineProcessingTime;
      if (timeChange > 2) {
        anomalies.push({
          type: AnomalyType.PERFORMANCE_ANOMALY,
          severity: Math.min(timeChange / 5, 1),
          description: `Processing time ${timeChange.toFixed(1)}x from baseline`,
          affectedMetrics: ['processing_time'],
          confidence: Math.min(timeChange / 2, 1),
        });
      }
    }

    // Check success rate
    const operations = currentMetrics.operations || [];
    if (operations.length > 0) {
      const currentSuccessRate = operations.filter((op: any) => op.success).length / operations.length;
      const baselineSuccessRate = baseline.performanceBaseline.successRateBaseline;
      const successDrop = baselineSuccessRate - currentSuccessRate;

      if (successDrop > 0.2) {
        anomalies.push({
          type: AnomalyType.PERFORMANCE_ANOMALY,
          severity: successDrop / 0.5,
          description: `Success rate dropped ${(successDrop * 100).toFixed(1)}%`,
          affectedMetrics: ['success_rate'],
          confidence: 0.8,
        });
      }
    }

    return anomalies;
  }

  /**
   * Detect statistical outliers
   */
  private detectStatisticalOutliers(
    agent: MicrobiomeAgent,
    baseline: BehavioralBaseline,
    currentMetrics: any
  ): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Use IQR method for outlier detection
    const metrics = ['processingTime', 'memoryUsage', 'cpuUsage'];

    for (const metric of metrics) {
      const values = currentMetrics[metric] || [];
      if (values.length < 4) continue;

      const sorted = [...values].sort((a, b) => a - b);
      const q1 = sorted[Math.floor(sorted.length * 0.25)];
      const q3 = sorted[Math.floor(sorted.length * 0.75)];
      const iqr = q3 - q1;

      const lowerBound = q1 - 1.5 * iqr;
      const upperBound = q3 + 1.5 * iqr;

      const outliers = values.filter(v => v < lowerBound || v > upperBound);
      if (outliers.length > 0) {
        anomalies.push({
          type: AnomalyType.STATISTICAL_OUTLIER,
          severity: outliers.length / values.length,
          description: `${outliers.length} outliers detected in ${metric}`,
          affectedMetrics: [metric],
          confidence: 0.9,
        });
      }
    }

    return anomalies;
  }

  /**
   * Calculate anomaly score
   */
  private calculateAnomalyScore(anomalies: Anomaly[]): number {
    if (anomalies.length === 0) return 0;

    // Weight anomalies by severity and confidence
    const weightedScores = anomalies.map(a => a.severity * a.confidence);
    const average = weightedScores.reduce((a, b) => a + b, 0) / weightedScores.length;

    // Boost score for multiple anomalies
    const multiplier = 1 + (anomalies.length - 1) * 0.1;

    return Math.min(average * multiplier, 1);
  }

  /**
   * Match threat signatures
   */
  private matchThreatSignatures(activity: SecurityEvent): ThreatType[] {
    const matches: ThreatType[] = [];

    for (const [threatType, signature] of this.threatSignatures) {
      if (this.matchesSignature(activity, signature)) {
        matches.push(threatType);
      }
    }

    return matches;
  }

  /**
   * Check if activity matches signature
   */
  private matchesSignature(activity: SecurityEvent, signature: ThreatSignature): boolean {
    // Check event type
    if (signature.eventTypes && !signature.eventTypes.includes(activity.type)) {
      return false;
    }

    // Check patterns
    if (signature.patterns) {
      for (const pattern of signature.patterns) {
        const value = this.getNestedValue(activity.data, pattern.path);
        if (value === undefined) continue;

        if (pattern.operator === 'equals' && value !== pattern.value) return false;
        if (pattern.operator === 'contains' && !String(value).includes(pattern.value)) return false;
        if (pattern.operator === 'greater_than' && value <= pattern.value) return false;
        if (pattern.operator === 'less_than' && value >= pattern.value) return false;
        if (pattern.operator === 'regex' && !new RegExp(pattern.value).test(String(value))) return false;
      }
    }

    return true;
  }

  /**
   * Get nested value from object
   */
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  /**
   * Create intrusion alert
   */
  private createIntrusionAlert(threatType: ThreatType, activity: SecurityEvent): IntrusionAlert {
    const alert: IntrusionAlert = {
      alertId: this.generateId(),
      threatType,
      threatLevel: this.determineThreatLevel(threatType, activity),
      sourceAgents: [activity.agentId || 'unknown'],
      targetAgents: activity.targetAgents || [],
      description: this.generateThreatDescription(threatType, activity),
      evidence: [{
        type: EvidenceType.LOG_ENTRY,
        description: 'Security event triggered alert',
        data: activity,
        timestamp: activity.timestamp,
        confidence: 0.8,
      }],
      timestamp: Date.now(),
      recommendedActions: this.generateRecommendedActions(threatType),
      falsePositiveProbability: this.estimateFalsePositiveProbability(threatType, activity),
    };

    return alert;
  }

  /**
   * Detect suspicious patterns
   */
  private detectSuspiciousPatterns(activities: SecurityEvent[]): IntrusionAlert[] {
    const alerts: IntrusionAlert[] = [];

    // Detect rate-based attacks
    const agentEventCounts = new Map<string, number>();
    for (const activity of activities) {
      const agentId = activity.agentId || 'unknown';
      agentEventCounts.set(agentId, (agentEventCounts.get(agentId) || 0) + 1);
    }

    for (const [agentId, count] of agentEventCounts) {
      const avgCount = activities.length / (agentEventCounts.size || 1);
      if (count > avgCount * 10) { // More than 10x average
        alerts.push({
          alertId: this.generateId(),
          threatType: ThreatType.DOS_ATTACK,
          threatLevel: ThreatLevel.HIGH,
          sourceAgents: [agentId],
          targetAgents: [],
          description: `Agent ${agentId} generating ${count} events (${(count / avgCount).toFixed(1)}x normal rate)`,
          evidence: [{
            type: EvidenceType.METRICS_DATA,
            description: 'Elevated event rate',
            data: { agentId, count, avgCount },
            timestamp: Date.now(),
            confidence: 0.9,
          }],
          timestamp: Date.now(),
          recommendedActions: [
            {
              type: ActionType.RATE_LIMIT,
              priority: 'high',
              description: 'Rate limit agent',
              parameters: { agentId, limit: Math.floor(avgCount * 2) },
              expectedOutcome: 'Reduced event rate to normal levels',
            },
          ],
          falsePositiveProbability: 0.1,
        });
      }
    }

    return alerts;
  }

  /**
   * Detect privilege escalation
   */
  private detectPrivilegeEscalation(activities: SecurityEvent[]): IntrusionAlert[] {
    const alerts: IntrusionAlert[] = [];

    // Look for privilege changes
    const privilegeChanges = activities.filter(a =>
      a.type === 'authorization_check' &&
      a.data?.requestedPermission &&
      !a.data?.hasPermission
    );

    // Group by agent
    const agentFailures = new Map<string, number>();
    for (const activity of privilegeChanges) {
      const agentId = activity.agentId || 'unknown';
      agentFailures.set(agentId, (agentFailures.get(agentId) || 0) + 1);
    }

    for (const [agentId, failures] of agentFailures) {
      if (failures >= 5) { // 5 or more failed authorization attempts
        alerts.push({
          alertId: this.generateId(),
          threatType: ThreatType.PRIVILEGE_ESCALATION,
          threatLevel: ThreatLevel.HIGH,
          sourceAgents: [agentId],
          targetAgents: [],
          description: `Agent ${agentId} made ${failures} failed authorization attempts`,
          evidence: privilegeChanges
            .filter(a => a.agentId === agentId)
            .map(a => ({
              type: EvidenceType.LOG_ENTRY,
              description: 'Failed authorization attempt',
              data: a,
              timestamp: a.timestamp,
              confidence: 0.85,
            })),
          timestamp: Date.now(),
          recommendedActions: [
            {
              type: ActionType.ALERT_ADMIN,
              priority: 'high',
              description: 'Notify administrator of potential privilege escalation',
              parameters: { agentId, failures },
              expectedOutcome: 'Administrator investigates suspicious activity',
            },
            {
              type: ActionType.INCREASE_MONITORING,
              priority: 'medium',
              description: 'Increase monitoring on agent',
              parameters: { agentId },
              expectedOutcome: 'Enhanced visibility into agent activities',
            },
          ],
          falsePositiveProbability: 0.2,
        });
      }
    }

    return alerts;
  }

  /**
   * Determine threat level
   */
  private determineThreatLevel(threatType: ThreatType, activity: SecurityEvent): ThreatLevel {
    const criticalThreats = [ThreatType.MALICIOUS_AGENT, ThreatType.DATA_EXFILTRATION];
    const highThreats = [
      ThreatType.INJECTION_ATTACK,
      ThreatType.PRIVILEGE_ESCALATION,
      ThreatType.MAN_IN_THE_MIDDLE,
    ];
    const mediumThreats = [
      ThreatType.DOS_ATTACK,
      ThreatType.REPLAY_ATTACK,
      ThreatType.RESOURCE_EXHAUSTION,
    ];

    if (criticalThreats.includes(threatType)) return ThreatLevel.CRITICAL;
    if (highThreats.includes(threatType)) return ThreatLevel.HIGH;
    if (mediumThreats.includes(threatType)) return ThreatLevel.MEDIUM;
    return ThreatLevel.LOW;
  }

  /**
   * Generate threat description
   */
  private generateThreatDescription(threatType: ThreatType, activity: SecurityEvent): string {
    const descriptions: Record<ThreatType, string> = {
      [ThreatType.MALICIOUS_AGENT]: 'Malicious agent behavior detected',
      [ThreatType.INJECTION_ATTACK]: 'Potential injection attack detected',
      [ThreatType.DOS_ATTACK]: 'Denial of service attack detected',
      [ThreatType.PRIVILEGE_ESCALATION]: 'Privilege escalation attempt detected',
      [ThreatType.DATA_EXFILTRATION]: 'Data exfiltration attempt detected',
      [ThreatType.REPLAY_ATTACK]: 'Replay attack detected',
      [ThreatType.MAN_IN_THE_MIDDLE]: 'Man-in-the-middle attack detected',
      [ThreatType.RESOURCE_EXHAUSTION]: 'Resource exhaustion detected',
      [ThreatType.SUSPICIOUS_COMMUNICATION]: 'Suspicious communication pattern detected',
      [ThreatType.BEHAVIORAL_ANOMALY]: 'Behavioral anomaly detected',
      [ThreatType.CONFIGURATION_VULNERABILITY]: 'Configuration vulnerability detected',
      [ThreatType.DEPENDENCY_VULNERABILITY]: 'Dependency vulnerability detected',
    };

    return descriptions[threatType] || 'Threat detected';
  }

  /**
   * Generate recommended actions
   */
  private generateRecommendedActions(threatType: ThreatType): RecommendedAction[] {
    const actions: RecommendedAction[] = [];

    switch (threatType) {
      case ThreatType.MALICIOUS_AGENT:
        actions.push({
          type: ActionType.ISOLATE_AGENT,
          priority: 'critical',
          description: 'Isolate malicious agent from network',
          parameters: {},
          expectedOutcome: 'Prevent further malicious activity',
        });
        actions.push({
          type: ActionType.TERMINATE_AGENT,
          priority: 'high',
          description: 'Terminate malicious agent',
          parameters: {},
          expectedOutcome: 'Remove threat from system',
        });
        break;

      case ThreatType.DOS_ATTACK:
        actions.push({
          type: ActionType.RATE_LIMIT,
          priority: 'high',
          description: 'Apply rate limiting',
          parameters: {},
          expectedOutcome: 'Mitigate DoS attack',
        });
        break;

      case ThreatType.PRIVILEGE_ESCALATION:
        actions.push({
          type: ActionType.REVOKE_CREDENTIALS,
          priority: 'critical',
          description: 'Revoke escalated credentials',
          parameters: {},
          expectedOutcome: 'Prevent unauthorized access',
        });
        break;

      default:
        actions.push({
          type: ActionType.INCREASE_MONITORING,
          priority: 'medium',
          description: 'Increase monitoring intensity',
          parameters: {},
          expectedOutcome: 'Better threat visibility',
        });
    }

    return actions;
  }

  /**
   * Estimate false positive probability
   */
  private estimateFalsePositiveProbability(threatType: ThreatType, activity: SecurityEvent): number {
    // Higher false positive rate for behavioral anomalies
    if (threatType === ThreatType.BEHAVIORAL_ANOMALY) return 0.3;
    if (threatType === ThreatType.SUSPICIOUS_COMMUNICATION) return 0.25;

    // Lower false positive rate for clear threat indicators
    if (threatType === ThreatType.MALICIOUS_AGENT) return 0.05;
    if (threatType === ThreatType.INJECTION_ATTACK) return 0.1;

    return 0.2;
  }

  /**
   * Scan dependencies for vulnerabilities
   */
  private async scanDependencies(
    dependencies: Map<string, string>
  ): Promise<Vulnerability[]> {
    const vulnerabilities: Vulnerability[] = [];

    // Check against known vulnerability database
    for (const [name, version] of dependencies) {
      const knownVulns = await this.checkKnownVulnerabilities(name, version);
      vulnerabilities.push(...knownVulns);
    }

    return vulnerabilities;
  }

  /**
   * Check known vulnerabilities
   */
  private async checkKnownVulnerabilities(
    name: string,
    version: string
  ): Promise<Vulnerability[]> {
    // In production, this would query CVE database, npm audit, etc.
    // For now, return empty array
    return [];
  }

  /**
   * Scan configuration for vulnerabilities
   */
  private scanConfiguration(configuration: Record<string, any>): Vulnerability[] {
    const vulnerabilities: Vulnerability[] = [];

    // Check for weak encryption
    if (configuration.encryptionAlgorithm === 'DES' ||
        configuration.encryptionAlgorithm === 'RC4') {
      vulnerabilities.push({
        id: this.generateId(),
        severity: VulnerabilitySeverity.HIGH,
        type: VulnerabilityType.CONFIGURATION,
        title: 'Weak encryption algorithm',
        description: 'Using weak or deprecated encryption algorithm',
        affectedComponents: ['encryption'],
        cvssScore: 7.5,
        remediation: [
          'Upgrade to AES-256-GCM or stronger',
          'Review all cryptographic implementations',
        ],
        references: [],
      });
    }

    // Check for missing security headers
    if (!configuration.securityHeaders?.enabled) {
      vulnerabilities.push({
        id: this.generateId(),
        severity: VulnerabilitySeverity.MEDIUM,
        type: VulnerabilityType.CONFIGURATION,
        title: 'Missing security headers',
        description: 'Security headers not configured',
        affectedComponents: ['http'],
        cvssScore: 5.3,
        remediation: [
          'Enable security headers (CSP, X-Frame-Options, etc.)',
          'Review OWASP secure headers recommendations',
        ],
        references: [],
      });
    }

    return vulnerabilities;
  }

  /**
   * Scan agents for vulnerabilities
   */
  private async scanAgents(agents: Map<string, MicrobiomeAgent>): Promise<Vulnerability[]> {
    const vulnerabilities: Vulnerability[] = [];

    // Check for insecure patterns in agent code
    for (const [id, agent] of agents) {
      const agentVulns = await this.scanAgentForVulnerabilities(agent);
      vulnerabilities.push(...agentVulns);
    }

    return vulnerabilities;
  }

  /**
   * Scan single agent for vulnerabilities
   */
  private async scanAgentForVulnerabilities(agent: MicrobiomeAgent): Promise<Vulnerability[]> {
    // In production, this would use static analysis tools
    // For now, return empty array
    return [];
  }

  /**
   * Generate vulnerability summary
   */
  private generateVulnerabilitySummary(vulnerabilities: Vulnerability[]): VulnerabilitySummary {
    const bySeverity = new Map<VulnerabilitySeverity, number>();
    const byType = new Map<VulnerabilityType, number>();
    let totalCvss = 0;
    let cvssCount = 0;

    for (const vuln of vulnerabilities) {
      bySeverity.set(vuln.severity, (bySeverity.get(vuln.severity) || 0) + 1);
      byType.set(vuln.type, (byType.get(vuln.type) || 0) + 1);

      if (vuln.cvssScore !== undefined) {
        totalCvss += vuln.cvssScore;
        cvssCount++;
      }
    }

    return {
      total: vulnerabilities.length,
      bySeverity,
      byType,
      averageCvssScore: cvssCount > 0 ? totalCvss / cvssCount : 0,
      percentScanned: 100,
    };
  }

  /**
   * Generate vulnerability recommendations
   */
  private generateVulnerabilityRecommendations(vulnerabilities: Vulnerability[]): string[] {
    const recommendations: string[] = [];

    // Prioritize critical vulnerabilities
    const critical = vulnerabilities.filter(v => v.severity === VulnerabilitySeverity.CRITICAL);
    if (critical.length > 0) {
      recommendations.push(`Address ${critical.length} critical vulnerabilities immediately`);
    }

    // Check for common patterns
    const depVulns = vulnerabilities.filter(v => v.type === VulnerabilityType.DEPENDENCY);
    if (depVulns.length > 0) {
      recommendations.push('Update dependencies to latest secure versions');
    }

    const configVulns = vulnerabilities.filter(v => v.type === VulnerabilityType.CONFIGURATION);
    if (configVulns.length > 0) {
      recommendations.push('Review and update security configuration');
    }

    return recommendations;
  }

  /**
   * Evaluate compliance control
   */
  private evaluateControl(control: ControlStatus): ControlStatus {
    // In production, this would check actual system state
    // For now, return control as-is
    return control;
  }

  /**
   * Generate compliance recommendations
   */
  private generateComplianceRecommendations(
    gaps: ComplianceGap[],
    framework: ComplianceFramework
  ): string[] {
    const recommendations: string[] = [];

    // Prioritize critical gaps
    const criticalGaps = gaps.filter(g => g.severity === 'critical');
    if (criticalGaps.length > 0) {
      recommendations.push(`Address ${criticalGaps.length} critical compliance gaps`);
    }

    // Framework-specific recommendations
    switch (framework) {
      case ComplianceFramework.SOC2:
        recommendations.push('Ensure all security events are logged and auditable');
        recommendations.push('Document all access control policies');
        break;
      case ComplianceFramework.GDPR:
        recommendations.push('Implement data subject rights mechanisms');
        recommendations.push('Ensure consent management is in place');
        break;
      case ComplianceFramework.HIPAA:
        recommendations.push('Implement PHI access controls');
        recommendations.push('Ensure audit logs retention for 6 years');
        break;
    }

    return recommendations;
  }

  /**
   * Calculate overall threat level
   */
  private calculateOverallThreatLevel(): ThreatLevel {
    if (this.activeAlerts.size === 0) return ThreatLevel.NONE;

    let maxLevel = ThreatLevel.NONE;
    for (const alert of this.activeAlerts.values()) {
      if (alert.threatLevel === ThreatLevel.CRITICAL) return ThreatLevel.CRITICAL;
      if (alert.threatLevel === ThreatLevel.HIGH) maxLevel = ThreatLevel.HIGH;
      else if (alert.threatLevel === ThreatLevel.MEDIUM && maxLevel !== ThreatLevel.HIGH) {
        maxLevel = ThreatLevel.MEDIUM;
      }
    }

    return maxLevel;
  }

  /**
   * Determine security posture
   */
  private determineSecurityPosture(
    threatLevel: ThreatLevel,
    vulnerabilities: number,
    complianceScore: number
  ): SecurityPosture {
    if (threatLevel === ThreatLevel.CRITICAL || vulnerabilities > 10) {
      return SecurityPosture.CRITICAL;
    }
    if (threatLevel === ThreatLevel.HIGH || vulnerabilities > 5) {
      return SecurityPosture.POOR;
    }
    if (threatLevel === ThreatLevel.MEDIUM || complianceScore < 0.7) {
      return SecurityPosture.FAIR;
    }
    if (threatLevel === ThreatLevel.LOW || complianceScore < 0.9) {
      return SecurityPosture.GOOD;
    }
    return SecurityPosture.EXCELLENT;
  }

  /**
   * Generate security trends
   */
  private generateSecurityTrends(): SecurityTrend[] {
    // In production, this would analyze historical data
    // For now, return empty array
    return [];
  }

  /**
   * Initialize threat signatures
   */
  private initializeThreatSignatures(): void {
    // SQL Injection signature
    this.threatSignatures.set(ThreatType.INJECTION_ATTACK, {
      eventTypes: ['agent_processing'],
      patterns: [
        { path: 'input', operator: 'contains', value: "'" },
        { path: 'input', operator: 'contains', value: 'OR' },
        { path: 'input', operator: 'contains', value: '=' },
      ],
    });

    // XSS signature
    this.threatSignatures.set(ThreatType.INJECTION_ATTACK, {
      eventTypes: ['agent_processing'],
      patterns: [
        { path: 'input', operator: 'contains', value: '<script>' },
      ],
    });
  }

  /**
   * Initialize compliance controls
   */
  private initializeComplianceControls(): void {
    // SOC 2 controls
    const soc2Controls = new Map<string, ControlStatus>();
    soc2Controls.set('CC1.1', {
      controlId: 'CC1.1',
      name: 'Access Control Policy',
      description: 'Implement access control policies',
      isCompliant: true,
      score: 0.9,
      evidence: ['RBAC implemented'],
      gaps: [],
    });
    // Add more SOC 2 controls...
    this.complianceControls.set(ComplianceFramework.SOC2, soc2Controls);

    // GDPR controls
    const gdprControls = new Map<string, ControlStatus>();
    gdprControls.set('ART.32', {
      controlId: 'ART.32',
      name: 'Security of Processing',
      description: 'Implement appropriate technical security measures',
      isCompliant: true,
      score: 0.85,
      evidence: ['Encryption implemented'],
      gaps: [],
    });
    // Add more GDPR controls...
    this.complianceControls.set(ComplianceFramework.GDPR, gdprControls);
  }

  /**
   * Calculate percentile
   */
  private percentile(values: number[], p: number): number {
    if (values.length === 0) return 0;
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `td_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Clear old alerts
   */
  clearOldAlerts(): void {
    const cutoff = Date.now() - this.config.alertRetentionPeriod;

    for (const [alertId, alert] of this.activeAlerts) {
      if (alert.timestamp < cutoff) {
        this.activeAlerts.delete(alertId);
        this.alertHistory.push(alert);
      }
    }

    // Trim history
    this.alertHistory = this.alertHistory.filter(a => a.timestamp >= cutoff);
  }

  /**
   * Get active alerts
   */
  getActiveAlerts(): IntrusionAlert[] {
    return Array.from(this.activeAlerts.values());
  }

  /**
   * Dismiss alert
   */
  dismissAlert(alertId: string): boolean {
    return this.activeAlerts.delete(alertId);
  }

  /**
   * Update baseline for agent
   */
  updateBaseline(agentId: string, metrics: any): void {
    // This would trigger a baseline recalculation
    // For now, just create a new baseline
    const agent = { id: agentId } as any;
    this.createBaseline(agent, metrics);
  }

  /**
   * Get baseline for agent
   */
  getBaseline(agentId: string): BehavioralBaseline | undefined {
    return this.baselines.get(agentId);
  }

  /**
   * Get all baselines
   */
  getAllBaselines(): Map<string, BehavioralBaseline> {
    return new Map(this.baselines);
  }
}

/**
 * Threat signature for pattern matching
 */
interface ThreatSignature {
  /** Event types to match */
  eventTypes?: string[];
  /** Patterns to match */
  patterns?: PatternMatch[];
  /** Description */
  description?: string;
}

/**
 * Pattern match rule
 */
interface PatternMatch {
  /** Path to value (dot notation) */
  path: string;
  /** Comparison operator */
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'regex';
  /** Value to compare against */
  value: any;
}

/**
 * Create a threat detector with default configuration
 */
export function createThreatDetector(
  securityManager: SecurityManager,
  analyticsPipeline?: AnalyticsPipeline
): ThreatDetector {
  return new ThreatDetector(securityManager, analyticsPipeline);
}

/**
 * Create a threat detector with custom configuration
 */
export function createThreatDetectorWithConfig(
  securityManager: SecurityManager,
  config: ThreatDetectorConfig,
  analyticsPipeline?: AnalyticsPipeline
): ThreatDetector {
  return new ThreatDetector(securityManager, analyticsPipeline, config);
}
