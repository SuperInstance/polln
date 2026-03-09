/**
 * POLLN Microbiome - Immune System
 *
 * Biological defense system for ecosystem health.
 * Detects and neutralizes threats while protecting beneficial agents.
 *
 * @module microbiome/immune
 */

import { v4 as uuidv4 } from 'uuid';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  ResourceType,
  MetabolicProfile,
  LifecycleState,
  FitnessScore,
  MutationConfig,
  MacrophageAgent as MacrophageAgentInterface,
} from './types.js';

/**
 * Threat severity levels
 */
export enum ThreatLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Threat report from scanning
 */
export interface ThreatReport {
  /** Agent ID that is a threat */
  agentId: string;
  /** Threat severity */
  level: ThreatLevel;
  /** Type of threat */
  type: 'dead' | 'unhealthy' | 'anomaly' | 'parasitic' | 'known_pattern';
  /** Confidence score (0-1) */
  confidence: number;
  /** Recommended action */
  action: 'monitor' | 'quarantine' | 'terminate';
  /** Reason for threat classification */
  reason: string;
  /** Timestamp of detection */
  timestamp: number;
}

/**
 * Anomaly detection report
 */
export interface AnomalyReport {
  /** Agent ID with anomaly */
  agentId: string;
  /** Whether an anomaly was detected */
  isAnomaly: boolean;
  /** Anomaly score (0-1, higher = more anomalous) */
  anomalyScore: number;
  /** Detection method used */
  method: 'statistical' | 'behavioral' | 'pattern';
  /** Confidence in detection (0-1) */
  confidence: number;
  /** Specific anomalies detected */
  anomalies: string[];
  /** Recommended action */
  recommendedAction: 'monitor' | 'quarantine' | 'terminate';
}

/**
 * Antibody for pattern-based defense
 */
export interface Antibody {
  /** Unique antibody ID */
  id: string;
  /** Threat pattern this antibody targets */
  threatPattern: string;
  /** Defense pattern */
  defensePattern: string;
  /** Potency (0-1) */
  potency: number;
  /** Success count */
  successCount: number;
  /** Failure count */
  failureCount: number;
  /** Last used timestamp */
  lastUsed: number;
  /** Created timestamp */
  created: number;
}

/**
 * Immune memory entry
 */
export interface ImmuneMemory {
  /** Memory ID */
  id: string;
  /** Threat pattern */
  threatPattern: string;
  /** Times encountered */
  encounterCount: number;
  /** Times successfully neutralized */
  successCount: number;
  /** Last encounter timestamp */
  lastEncounter: number;
  /** Effectiveness (0-1) */
  effectiveness: number;
}

/**
 * Immune system statistics
 */
export interface ImmuneStats {
  /** Total scans performed */
  totalScans: number;
  /** Total threats detected */
  threatsDetected: number;
  /** Total threats neutralized */
  threatsNeutralized: number;
  /** Agents quarantined */
  agentsQuarantined: number;
  /** Agents terminated */
  agentsTerminated: number;
  /** Antibodies in memory */
  antibodyCount: number;
  /** Memory entries */
  memoryEntries: number;
  /** Current threat level */
  currentThreatLevel: ThreatLevel;
}

/**
 * Macrophage action types
 */
export type MacrophageAction = 'prune' | 'quarantine' | 'terminate' | 'report';

/**
 * Macrophage configuration
 */
export interface MacrophageConfig {
  /** Health threshold for cleanup (0-1) */
  healthThreshold?: number;
  /** Age threshold for cleanup (milliseconds) */
  ageThreshold?: number;
  /** Efficiency threshold for cleanup (0-1) */
  efficiencyThreshold?: number;
  /** Actions to perform */
  actions?: MacrophageAction[];
}

/**
 * T-Cell detection method
 */
export type DetectionMethod = 'statistical' | 'behavioral' | 'pattern';

/**
 * T-Cell configuration
 */
export interface TCellConfig {
  /** Detection method */
  method?: DetectionMethod;
  /** Tolerance threshold (standard deviations) */
  tolerance?: number;
  /** Sample size for statistical analysis */
  sampleSize?: number;
  /** Pattern matching sensitivity (0-1) */
  patternSensitivity?: number;
}

/**
 * Immune system configuration
 */
export interface ImmuneSystemConfig {
  /** Whether immune system is enabled */
  enabled?: boolean;
  /** Scan interval (milliseconds) */
  scanInterval?: number;
  /** Threat sensitivity (0-1) */
  sensitivity?: number;
  /** Maximum antibodies to store */
  maxAntibodies?: number;
  /** Antibody decay rate (0-1 per scan) */
  antibodyDecayRate?: number;
  /** Quarantine duration (milliseconds) */
  quarantineDuration?: number;
  /** Macrophage config */
  macrophage?: MacrophageConfig;
  /** T-Cell config */
  tcell?: TCellConfig;
}

/**
 * Macrophage Agent - Garbage collection and cleanup
 *
 * Scans for dead, unhealthy, or inefficient agents and performs cleanup actions.
 */
export class MacrophageAgent implements MacrophageAgentInterface {
  id: string;
  taxonomy: AgentTaxonomy.MACROPHAGE = AgentTaxonomy.MACROPHAGE;
  name: string;
  metabolism: MetabolicProfile;
  lifecycle: LifecycleState;
  parentId?: string;
  generation: number;
  size: number;
  complexity: number;

  /** Targets to clean up */
  targets: string[] = [];
  /** Actions to take */
  actions: MacrophageAction[];
  /** Configuration */
  private config: Required<MacrophageConfig>;
  /** Cleanup statistics */
  private stats: {
    agentsCleaned: number;
    resourcesRecycled: number;
    threatsReported: number;
  };

  constructor(config: MacrophageConfig = {}) {
    this.id = uuidv4();
    this.name = `Macrophage_${this.id.slice(0, 8)}`;
    this.parentId = undefined;
    this.generation = 0;
    this.size = 2048; // 2KB
    this.complexity = 0.7;

    this.config = {
      healthThreshold: config.healthThreshold ?? 0.2,
      ageThreshold: config.ageThreshold ?? 3600000, // 1 hour
      efficiencyThreshold: config.efficiencyThreshold ?? 0.3,
      actions: config.actions ?? ['prune', 'quarantine', 'report'],
    };

    this.actions = this.config.actions;

    this.metabolism = {
      inputs: [ResourceType.MEMORY, ResourceType.COMPUTE],
      outputs: [ResourceType.MEMORY],
      processingRate: 100, // agents per second
      efficiency: 0.9,
    };

    this.lifecycle = {
      health: 1.0,
      age: 0,
      generation: 0,
      isAlive: true,
    };

    this.stats = {
      agentsCleaned: 0,
      resourcesRecycled: 0,
      threatsReported: 0,
    };
  }

  /**
   * Scan agents for threats
   */
  scan(agents: MicrobiomeAgent[]): ThreatReport[] {
    const threats: ThreatReport[] = [];
    const now = Date.now();

    for (const agent of agents) {
      if (!agent.lifecycle.isAlive) {
        // Dead agent
        threats.push({
          agentId: agent.id,
          level: ThreatLevel.LOW,
          type: 'dead',
          confidence: 1.0,
          action: 'terminate',
          reason: 'Agent is dead',
          timestamp: now,
        });
        continue;
      }

      // Check health threshold
      if (agent.lifecycle.health < this.config.healthThreshold) {
        threats.push({
          agentId: agent.id,
          level: ThreatLevel.MEDIUM,
          type: 'unhealthy',
          confidence: 1 - agent.lifecycle.health,
          action: agent.lifecycle.health < 0.1 ? 'terminate' : 'quarantine',
          reason: `Health ${(agent.lifecycle.health * 100).toFixed(1)}% below threshold`,
          timestamp: now,
        });
      }

      // Check age threshold
      if (agent.lifecycle.age > this.config.ageThreshold) {
        threats.push({
          agentId: agent.id,
          level: ThreatLevel.LOW,
          type: 'unhealthy',
          confidence: Math.min(1, agent.lifecycle.age / this.config.ageThreshold),
          action: 'prune',
          reason: `Age ${(agent.lifecycle.age / 1000).toFixed(0)}s exceeds threshold`,
          timestamp: now,
        });
      }

      // Check efficiency threshold
      if (agent.metabolism.efficiency < this.config.efficiencyThreshold) {
        threats.push({
          agentId: agent.id,
          level: ThreatLevel.LOW,
          type: 'unhealthy',
          confidence: 1 - agent.metabolism.efficiency,
          action: 'prune',
          reason: `Efficiency ${(agent.metabolism.efficiency * 100).toFixed(1)}% below threshold`,
          timestamp: now,
        });
      }
    }

    return threats;
  }

  /**
   * Perform cleanup action on an agent
   */
  cleanup(agent: MicrobiomeAgent, action: MacrophageAction): boolean {
    if (!this.actions.includes(action)) {
      return false;
    }

    switch (action) {
      case 'prune':
        // Remove weak but not critical agents
        if (agent.lifecycle.health > 0 && agent.lifecycle.health < 0.3) {
          agent.lifecycle.isAlive = false;
          this.stats.agentsCleaned++;
          return true;
        }
        return false;

      case 'quarantine':
        // Isolate problematic agents (marked for review)
        if (agent.lifecycle.health < 0.5) {
          // Quarantine logic: mark but don't kill
          (agent as any).quarantined = true;
          (agent as any).quarantineTime = Date.now();
          this.stats.agentsCleaned++;
          return true;
        }
        return false;

      case 'terminate':
        // Kill dangerous agents (even if health is low but not zero)
        agent.lifecycle.isAlive = false;
        this.stats.agentsCleaned++;
        return true;

      case 'report':
        // Just report, don't act
        this.stats.threatsReported++;
        return true;

      default:
        return false;
    }
  }

  /**
   * Recycle resources from dead agent
   */
  recycle(agent: MicrobiomeAgent): number {
    if (agent.lifecycle.isAlive) {
      return 0;
    }

    // Calculate resource value based on agent size and complexity
    const recycled = Math.floor(agent.size * agent.complexity * 0.5);
    this.stats.resourcesRecycled += recycled;
    return recycled;
  }

  /**
   * Process resources (not used by macrophages)
   */
  async process(resources: Map<ResourceType, number>): Promise<Map<ResourceType, number>> {
    // Macrophages don't process resources in the traditional sense
    return new Map();
  }

  /**
   * Reproduce (not used by macrophages)
   */
  async reproduce(config: MutationConfig): Promise<MacrophageAgent> {
    throw new Error('Macrophages cannot reproduce');
  }

  /**
   * Evaluate fitness
   */
  evaluateFitness(): FitnessScore {
    const efficiency = this.stats.agentsCleaned > 0
      ? Math.min(1, this.stats.resourcesRecycled / (this.stats.agentsCleaned * 1000))
      : 0.5;

    return {
      overall: (this.lifecycle.health * 0.5 + efficiency * 0.5),
      throughput: this.stats.agentsCleaned,
      accuracy: 1.0, // Macrophages are always accurate
      efficiency: efficiency,
      cooperation: 0.3, // Moderate cooperation
    };
  }

  /**
   * Check if can metabolize
   */
  canMetabolize(resources: Map<ResourceType, number>): boolean {
    return resources.has(ResourceType.MEMORY) || resources.has(ResourceType.COMPUTE);
  }

  /**
   * Age the macrophage
   */
  age(deltaMs: number): void {
    this.lifecycle.age += deltaMs;
    if (this.lifecycle.health <= 0) {
      this.lifecycle.isAlive = false;
    }
  }

  /**
   * Get statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      agentsCleaned: 0,
      resourcesRecycled: 0,
      threatsReported: 0,
    };
  }
}

/**
 * T-Cell Agent - Anomaly detection
 *
 * Detects statistical outliers, behavioral anomalies, and pattern mismatches.
 */
export class TCellAgent implements MicrobiomeAgent {
  id: string;
  taxonomy: AgentTaxonomy = AgentTaxonomy.MACROPHAGE; // Use macrophage as immune agent type
  name: string;
  metabolism: MetabolicProfile;
  lifecycle: LifecycleState;
  parentId?: string;
  generation: number;
  size: number;
  complexity: number;

  /** Detection method */
  detectionMethod: DetectionMethod;
  /** Tolerance (standard deviations) */
  tolerance: number;
  /** Configuration */
  private config: Required<TCellConfig>;
  /** Statistics */
  private stats: {
    scansPerformed: number;
    anomaliesDetected: number;
    truePositives: number;
    falsePositives: number;
  };
  /** Historical data for statistical analysis */
  private history: Map<string, number[]>;

  constructor(config: TCellConfig = {}) {
    this.id = uuidv4();
    this.name = `TCell_${this.id.slice(0, 8)}`;
    this.parentId = undefined;
    this.generation = 0;
    this.size = 3072; // 3KB
    this.complexity = 0.8;

    this.config = {
      method: config.method ?? 'statistical',
      tolerance: config.tolerance ?? 2.5, // 2.5 standard deviations
      sampleSize: config.sampleSize ?? 100,
      patternSensitivity: config.patternSensitivity ?? 0.7,
    };

    this.detectionMethod = this.config.method;
    this.tolerance = this.config.tolerance;

    this.metabolism = {
      inputs: [ResourceType.COMPUTE, ResourceType.MEMORY],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 50, // agents per second
      efficiency: 0.85,
    };

    this.lifecycle = {
      health: 1.0,
      age: 0,
      generation: 0,
      isAlive: true,
    };

    this.stats = {
      scansPerformed: 0,
      anomaliesDetected: 0,
      truePositives: 0,
      falsePositives: 0,
    };

    this.history = new Map();
  }

  /**
   * Detect anomaly in an agent
   */
  detectAnomaly(agent: MicrobiomeAgent): AnomalyReport {
    this.stats.scansPerformed++;

    const anomalies: string[] = [];
    let anomalyScore = 0;
    let confidence = 0;

    switch (this.detectionMethod) {
      case 'statistical':
        return this.statisticalDetection(agent);
      case 'behavioral':
        return this.behavioralDetection(agent);
      case 'pattern':
        return this.patternDetection(agent);
      default:
        return {
          agentId: agent.id,
          isAnomaly: false,
          anomalyScore: 0,
          method: this.detectionMethod,
          confidence: 0,
          anomalies: [],
          recommendedAction: 'monitor',
        };
    }
  }

  /**
   * Statistical outlier detection using z-score
   */
  private statisticalDetection(agent: MicrobiomeAgent): AnomalyReport {
    const anomalies: string[] = [];
    let totalAnomalyScore = 0;

    // Update history
    if (!this.history.has(agent.id)) {
      this.history.set(agent.id, []);
    }
    const history = this.history.get(agent.id)!;

    // Calculate metrics
    const healthMetric = agent.lifecycle.health;
    const efficiencyMetric = agent.metabolism.efficiency;
    const ageMetric = agent.lifecycle.age;

    // Add to history
    history.push(healthMetric, efficiencyMetric);
    if (history.length > this.config.sampleSize) {
      history.splice(0, history.length - this.config.sampleSize);
    }

    if (history.length < 10) {
      // Not enough data
      return {
        agentId: agent.id,
        isAnomaly: false,
        anomalyScore: 0,
        method: 'statistical',
        confidence: 0,
        anomalies: [],
        recommendedAction: 'monitor',
      };
    }

    // Calculate mean and standard deviation
    const mean = history.reduce((sum, val) => sum + val, 0) / history.length;
    const variance = history.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / history.length;
    const stdDev = Math.sqrt(variance);

    if (stdDev < 0.01) {
      // Low variance, can't detect anomalies
      return {
        agentId: agent.id,
        isAnomaly: false,
        anomalyScore: 0,
        method: 'statistical',
        confidence: 0,
        anomalies: [],
        recommendedAction: 'monitor',
      };
    }

    // Check z-score
    const zScore = Math.abs((healthMetric - mean) / stdDev);

    if (zScore > this.tolerance) {
      anomalies.push(`Health z-score: ${zScore.toFixed(2)}`);
      totalAnomalyScore += Math.min(1, zScore / this.tolerance);
    }

    // Check efficiency
    const efficiencyZScore = Math.abs((efficiencyMetric - mean) / stdDev);
    if (efficiencyZScore > this.tolerance) {
      anomalies.push(`Efficiency z-score: ${efficiencyZScore.toFixed(2)}`);
      totalAnomalyScore += Math.min(1, efficiencyZScore / this.tolerance);
    }

    // Check age outlier
    if (ageMetric > 0) {
      const ageScore = Math.min(1, ageMetric / (24 * 60 * 60 * 1000)); // 24 hours
      if (ageScore > 0.8) {
        anomalies.push(`Age outlier: ${(ageMetric / 1000 / 60).toFixed(0)} minutes`);
        totalAnomalyScore += ageScore * 0.3;
      }
    }

    const isAnomaly = anomalies.length > 0;
    const confidence = isAnomaly ? Math.min(1, totalAnomalyScore / anomalies.length) : 0;

    if (isAnomaly) {
      this.stats.anomaliesDetected++;
    }

    return {
      agentId: agent.id,
      isAnomaly,
      anomalyScore: Math.min(1, totalAnomalyScore),
      method: 'statistical',
      confidence,
      anomalies,
      recommendedAction: totalAnomalyScore > 0.7 ? 'quarantine' : totalAnomalyScore > 0.4 ? 'monitor' : 'monitor',
    };
  }

  /**
   * Behavioral pattern analysis
   */
  private behavioralDetection(agent: MicrobiomeAgent): AnomalyReport {
    const anomalies: string[] = [];
    let anomalyScore = 0;

    // Check for unusual metabolic patterns
    const inputCount = agent.metabolism.inputs.length;
    const outputCount = agent.metabolism.outputs.length;

    // Too many inputs (possible resource hog)
    if (inputCount > 5) {
      anomalies.push(`Excessive inputs: ${inputCount}`);
      anomalyScore += 0.4;
    }

    // Too many outputs (possible spam)
    if (outputCount > 5) {
      anomalies.push(`Excessive outputs: ${outputCount}`);
      anomalyScore += 0.4;
    }

    // No inputs or outputs (possible parasite)
    if (inputCount === 0 && outputCount === 0) {
      anomalies.push('No metabolism (possible parasite)');
      anomalyScore += 0.8;
    }

    // Very low efficiency
    if (agent.metabolism.efficiency < 0.2) {
      anomalies.push(`Very low efficiency: ${(agent.metabolism.efficiency * 100).toFixed(1)}%`);
      anomalyScore += 0.3;
    }

    // High processing rate with low efficiency
    if (agent.metabolism.processingRate > 100 && agent.metabolism.efficiency < 0.5) {
      anomalies.push('High processing rate with low efficiency (possible DoS)');
      anomalyScore += 0.5;
    }

    const isAnomaly = anomalies.length > 0;
    const confidence = isAnomaly ? Math.min(1, anomalyScore / anomalies.length) : 0;

    if (isAnomaly) {
      this.stats.anomaliesDetected++;
    }

    return {
      agentId: agent.id,
      isAnomaly,
      anomalyScore: Math.min(1, anomalyScore),
      method: 'behavioral',
      confidence,
      anomalies,
      recommendedAction: anomalyScore > 0.7 ? 'quarantine' : anomalyScore > 0.4 ? 'monitor' : 'monitor',
    };
  }

  /**
   * Pattern matching detection
   */
  private patternDetection(agent: MicrobiomeAgent): AnomalyReport {
    const anomalies: string[] = [];
    let anomalyScore = 0;

    // Check for known suspicious patterns
    const name = agent.name.toLowerCase();

    // Suspicious name patterns
    if (name.includes('virus') || name.includes('malware') || name.includes('exploit')) {
      anomalies.push(`Suspicious name pattern: ${agent.name}`);
      anomalyScore += 0.9;
    }

    // High complexity with low generation (possible injected code)
    if (agent.complexity > 0.8 && agent.generation === 0) {
      anomalies.push('High complexity in generation 0 (possible injection)');
      anomalyScore += 0.6;
    }

    // Very large size
    if (agent.size > 1024 * 1024) { // > 1MB
      anomalies.push(`Excessive size: ${(agent.size / 1024).toFixed(0)}KB`);
      anomalyScore += 0.5;
    }

    // Taxonomy mismatch
    if (agent.taxonomy === AgentTaxonomy.VIRUS) {
      anomalies.push('Virus taxonomy detected');
      anomalyScore += 0.7;
    }

    // Check for virus-specific patterns
    if ('stealth' in agent) {
      const stealth = (agent as any).stealth;
      if (stealth > 0.8) {
        anomalies.push(`High stealth: ${(stealth * 100).toFixed(0)}%`);
        anomalyScore += 0.5;
      }
    }

    const isAnomaly = anomalies.length > 0;
    const confidence = isAnomaly ? Math.min(1, anomalyScore / anomalies.length) : 0;

    if (isAnomaly) {
      this.stats.anomaliesDetected++;
    }

    return {
      agentId: agent.id,
      isAnomaly,
      anomalyScore: Math.min(1, anomalyScore),
      method: 'pattern',
      confidence,
      anomalies,
      recommendedAction: anomalyScore > 0.7 ? 'terminate' : anomalyScore > 0.4 ? 'quarantine' : 'monitor',
    };
  }

  /**
   * Process resources
   */
  async process(resources: Map<ResourceType, number>): Promise<Map<ResourceType, number>> {
    // T-cells don't process resources traditionally
    return new Map();
  }

  /**
   * Reproduce (not used by T-cells)
   */
  async reproduce(config: MutationConfig): Promise<TCellAgent> {
    throw new Error('T-cells cannot reproduce');
  }

  /**
   * Evaluate fitness
   */
  evaluateFitness(): FitnessScore {
    const precision = this.stats.anomaliesDetected > 0
      ? this.stats.truePositives / this.stats.anomaliesDetected
      : 1.0;

    return {
      overall: (this.lifecycle.health * 0.5 + precision * 0.5),
      throughput: this.stats.scansPerformed,
      accuracy: precision,
      efficiency: this.metabolism.efficiency,
      cooperation: 0.5, // T-cells cooperate with other immune components
    };
  }

  /**
   * Check if can metabolize
   */
  canMetabolize(resources: Map<ResourceType, number>): boolean {
    return resources.has(ResourceType.COMPUTE) || resources.has(ResourceType.MEMORY);
  }

  /**
   * Age the T-cell
   */
  age(deltaMs: number): void {
    this.lifecycle.age += deltaMs;
    if (this.lifecycle.health <= 0) {
      this.lifecycle.isAlive = false;
    }
  }

  /**
   * Get statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      scansPerformed: 0,
      anomaliesDetected: 0,
      truePositives: 0,
      falsePositives: 0,
    };
  }

  /**
   * Clear history
   */
  clearHistory(): void {
    this.history.clear();
  }
}

/**
 * Antibody System - Pattern-based defense
 *
 * Learns from threats and produces antibodies for future protection.
 */
export class AntibodySystem {
  /** Antibodies by threat pattern */
  private antibodies: Map<string, Antibody>;
  /** Immune memory */
  private memory: Map<string, ImmuneMemory>;
  /** Configuration */
  private config: Required<Pick<ImmuneSystemConfig, 'maxAntibodies' | 'antibodyDecayRate'>>;
  /** Statistics */
  private stats: {
    antibodiesProduced: number;
    threatsRecognized: number;
    successfulDefenses: number;
    failedDefenses: number;
  };

  constructor(config: Pick<ImmuneSystemConfig, 'maxAntibodies' | 'antibodyDecayRate'> = {}) {
    this.antibodies = new Map();
    this.memory = new Map();
    this.config = {
      maxAntibodies: config.maxAntibodies ?? 1000,
      antibodyDecayRate: config.antibodyDecayRate ?? 0.01,
    };
    this.stats = {
      antibodiesProduced: 0,
      threatsRecognized: 0,
      successfulDefenses: 0,
      failedDefenses: 0,
    };
  }

  /**
   * Learn pattern from a threat
   */
  learnPattern(threat: ThreatReport | AnomalyReport): Antibody | null {
    const pattern = this.extractPattern(threat);
    if (!pattern) {
      return null;
    }

    // Check if antibody already exists
    const existing = this.antibodies.get(pattern);
    if (existing) {
      // Strengthen existing antibody
      existing.potency = Math.min(1, existing.potency + 0.1);
      existing.lastUsed = Date.now();
      return existing;
    }

    // Create new antibody
    const antibody: Antibody = {
      id: uuidv4(),
      threatPattern: pattern,
      defensePattern: this.generateDefensePattern(pattern),
      potency: 0.5, // Start at medium potency
      successCount: 0,
      failureCount: 0,
      lastUsed: Date.now(),
      created: Date.now(),
    };

    // Add to antibodies (with LRU eviction if needed)
    if (this.antibodies.size >= this.config.maxAntibodies) {
      this.evictLRU();
    }
    this.antibodies.set(pattern, antibody);

    // Update memory
    this.updateMemory(pattern, true);

    this.stats.antibodiesProduced++;
    return antibody;
  }

  /**
   * Recognize if agent matches known threat patterns
   */
  recognize(agent: MicrobiomeAgent): boolean {
    const pattern = this.agentToPattern(agent);

    for (const antibody of this.antibodies.values()) {
      if (this.patternMatch(pattern, antibody.threatPattern)) {
        // Update antibody usage
        antibody.lastUsed = Date.now();
        this.stats.threatsRecognized++;
        return true;
      }
    }

    return false;
  }

  /**
   * Get antibody for a threat pattern
   */
  getAntibody(pattern: string): Antibody | null {
    const antibody = this.antibodies.get(pattern);
    if (antibody) {
      antibody.lastUsed = Date.now();
    }
    return antibody || null;
  }

  /**
   * Produce antibody for a pattern
   */
  produceAntibody(pattern: string): Antibody | null {
    const existing = this.antibodies.get(pattern);
    if (existing) {
      return existing;
    }

    if (this.antibodies.size >= this.config.maxAntibodies) {
      this.evictLRU();
    }

    const antibody: Antibody = {
      id: uuidv4(),
      threatPattern: pattern,
      defensePattern: this.generateDefensePattern(pattern),
      potency: 0.5,
      successCount: 0,
      failureCount: 0,
      lastUsed: Date.now(),
      created: Date.now(),
    };

    this.antibodies.set(pattern, antibody);
    this.stats.antibodiesProduced++;
    return antibody;
  }

  /**
   * Record defense outcome
   */
  recordOutcome(antibodyId: string, success: boolean): void {
    for (const antibody of this.antibodies.values()) {
      if (antibody.id === antibodyId) {
        if (success) {
          antibody.successCount++;
          antibody.potency = Math.min(1, antibody.potency + 0.1);
          this.stats.successfulDefenses++;
        } else {
          antibody.failureCount++;
          antibody.potency = Math.max(0, antibody.potency - 0.2);
          this.stats.failedDefenses++;
        }

        // Update memory
        this.updateMemory(antibody.threatPattern, success);
        break;
      }
    }

    // Remove weak antibodies
    this.decayAntibodies();
  }

  /**
   * Extract pattern from threat report
   */
  private extractPattern(threat: ThreatReport | AnomalyReport): string | null {
    if ('type' in threat) {
      // ThreatReport
      switch (threat.type) {
        case 'dead':
          return 'dead_agent';
        case 'unhealthy':
          return `health_${(threat.confidence * 100).toFixed(0)}`;
        case 'anomaly':
          return `anomaly_${threat.level}`;
        case 'parasitic':
          return 'parasitic';
        case 'known_pattern':
          return threat.agentId;
        default:
          return null;
      }
    } else {
      // AnomalyReport
      if (threat.anomalies.length === 0) {
        return null;
      }
      return threat.anomalies.join('|');
    }
  }

  /**
   * Convert agent to pattern
   */
  private agentToPattern(agent: MicrobiomeAgent): string {
    const parts: string[] = [
      agent.taxonomy,
      agent.complexity.toFixed(2),
      agent.metabolism.efficiency.toFixed(2),
    ];

    if (agent.metabolism.inputs.length > 0) {
      parts.push(agent.metabolism.inputs.join(','));
    }

    if (agent.metabolism.outputs.length > 0) {
      parts.push(agent.metabolism.outputs.join(','));
    }

    return parts.join(':');
  }

  /**
   * Generate defense pattern from threat pattern
   */
  private generateDefensePattern(threatPattern: string): string {
    return `defense_${threatPattern.replace(/[^a-zA-Z0-9]/g, '_')}`;
  }

  /**
   * Check if patterns match
   */
  private patternMatch(pattern1: string, pattern2: string): boolean {
    // Simple exact match for now
    // Could be enhanced with fuzzy matching, regex, etc.
    return pattern1 === pattern2 ||
           pattern1.includes(pattern2) ||
           pattern2.includes(pattern1);
  }

  /**
   * Update immune memory
   */
  private updateMemory(pattern: string, success: boolean): void {
    const existing = this.memory.get(pattern);
    const now = Date.now();

    if (existing) {
      existing.encounterCount++;
      existing.lastEncounter = now;
      if (success) {
        existing.successCount++;
      }
      existing.effectiveness = existing.successCount / existing.encounterCount;
    } else {
      this.memory.set(pattern, {
        id: uuidv4(),
        threatPattern: pattern,
        encounterCount: 1,
        successCount: success ? 1 : 0,
        lastEncounter: now,
        effectiveness: success ? 1.0 : 0.0,
      });
    }
  }

  /**
   * Evict least recently used antibody
   */
  private evictLRU(): void {
    let oldest: Antibody | null = null;
    let oldestTime = Infinity;

    for (const antibody of this.antibodies.values()) {
      if (antibody.lastUsed < oldestTime) {
        oldestTime = antibody.lastUsed;
        oldest = antibody;
      }
    }

    if (oldest) {
      this.antibodies.delete(oldest.threatPattern);
    }
  }

  /**
   * Decay weak antibodies
   */
  private decayAntibodies(): void {
    const toRemove: string[] = [];

    for (const [pattern, antibody] of this.antibodies.entries()) {
      if (antibody.potency < 0.2) {
        toRemove.push(pattern);
      }
    }

    for (const pattern of toRemove) {
      this.antibodies.delete(pattern);
    }
  }

  /**
   * Get all antibodies
   */
  getAntibodies(): Antibody[] {
    return Array.from(this.antibodies.values());
  }

  /**
   * Get immune memory
   */
  getMemory(): ImmuneMemory[] {
    return Array.from(this.memory.values());
  }

  /**
   * Get statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Clear all antibodies and memory
   */
  clear(): void {
    this.antibodies.clear();
    this.memory.clear();
  }
}

/**
 * Immune System - Coordinator for all immune components
 *
 * Manages macrophages, T-cells, and antibodies to protect the ecosystem.
 */
export class ImmuneSystem {
  /** Macrophage agents */
  private macrophages: MacrophageAgent[];
  /** T-Cell agents */
  private tcells: TCellAgent[];
  /** Antibody system */
  private antibodies: AntibodySystem;
  /** Configuration */
  private config: Required<ImmuneSystemConfig>;
  /** Statistics */
  private stats: ImmuneStats;
  /** Quarantined agents */
  private quarantined: Map<string, number>;
  /** Last scan timestamp */
  private lastScan: number = 0;

  constructor(config: ImmuneSystemConfig = {}) {
    this.config = {
      enabled: config.enabled ?? true,
      scanInterval: config.scanInterval ?? 10000, // 10 seconds
      sensitivity: config.sensitivity ?? 0.7,
      maxAntibodies: config.maxAntibodies ?? 1000,
      antibodyDecayRate: config.antibodyDecayRate ?? 0.01,
      quarantineDuration: config.quarantineDuration ?? 300000, // 5 minutes
      macrophage: config.macrophage ?? {},
      tcell: config.tcell ?? {},
    };

    // Create immune components
    this.macrophages = [
      new MacrophageAgent(this.config.macrophage),
      new MacrophageAgent(this.config.macrophage),
    ];

    this.tcells = [
      new TCellAgent({ ...this.config.tcell, method: 'statistical' }),
      new TCellAgent({ ...this.config.tcell, method: 'behavioral' }),
      new TCellAgent({ ...this.config.tcell, method: 'pattern' }),
    ];

    this.antibodies = new AntibodySystem({
      maxAntibodies: this.config.maxAntibodies,
      antibodyDecayRate: this.config.antibodyDecayRate,
    });

    this.quarantined = new Map();

    this.stats = {
      totalScans: 0,
      threatsDetected: 0,
      threatsNeutralized: 0,
      agentsQuarantined: 0,
      agentsTerminated: 0,
      antibodyCount: 0,
      memoryEntries: 0,
      currentThreatLevel: ThreatLevel.LOW,
    };
  }

  /**
   * Scan ecosystem for threats
   */
  scan(agents: MicrobiomeAgent[]): ThreatReport[] {
    if (!this.config.enabled) {
      return [];
    }

    const now = Date.now();
    if (now - this.lastScan < this.config.scanInterval) {
      return [];
    }

    this.lastScan = now;
    this.stats.totalScans++;

    const allThreats: ThreatReport[] = [];

    // Macrophage scan
    for (const macrophage of this.macrophages) {
      const threats = macrophage.scan(agents);
      allThreats.push(...threats);
    }

    // T-Cell scan
    for (const tcell of this.tcells) {
      for (const agent of agents) {
        if (!agent.lifecycle.isAlive) continue;

        const anomaly = tcell.detectAnomaly(agent);
        if (anomaly.isAnomaly && anomaly.anomalyScore > (1 - this.config.sensitivity)) {
          allThreats.push({
            agentId: agent.id,
            level: this.anomalyScoreToThreatLevel(anomaly.anomalyScore),
            type: 'anomaly',
            confidence: anomaly.confidence,
            action: anomaly.recommendedAction,
            reason: anomaly.anomalies.join('; '),
            timestamp: now,
          });
        }
      }
    }

    // Antibody recognition
    for (const agent of agents) {
      if (!agent.lifecycle.isAlive) continue;

      if (this.antibodies.recognize(agent)) {
        allThreats.push({
          agentId: agent.id,
          level: ThreatLevel.HIGH,
          type: 'known_pattern',
          confidence: 0.9,
          action: 'terminate',
          reason: 'Matches known threat pattern',
          timestamp: now,
        });
      }
    }

    // Update statistics
    this.stats.threatsDetected += allThreats.length;
    this.stats.currentThreatLevel = this.calculateThreatLevel(allThreats);
    this.stats.antibodyCount = this.antibodies.getAntibodies().length;
    this.stats.memoryEntries = this.antibodies.getMemory().length;

    return allThreats;
  }

  /**
   * Respond to detected threats
   */
  respond(agents: Map<string, MicrobiomeAgent>, threats: ThreatReport[]): {
    neutralized: number;
    quarantined: number;
    terminated: number;
  } {
    if (!this.config.enabled) {
      return { neutralized: 0, quarantined: 0, terminated: 0 };
    }

    let neutralized = 0;
    let quarantined = 0;
    let terminated = 0;

    for (const threat of threats) {
      const agent = agents.get(threat.agentId);
      if (!agent || !agent.lifecycle.isAlive) {
        continue;
      }

      // Learn from threat
      this.antibodies.learnPattern(threat);

      // Take action based on threat level
      switch (threat.action) {
        case 'terminate':
          agent.lifecycle.isAlive = false;
          this.antibodies.recordOutcome(
            this.antibodies.getAntibody(threat.agentId)?.id || '',
            true
          );
          terminated++;
          neutralized++;
          break;

        case 'quarantine':
          this.quarantined.set(agent.id, Date.now());
          (agent as any).quarantined = true;
          quarantined++;
          break;

        case 'monitor':
        default:
          // Just monitor, no action
          break;
      }
    }

    // Update statistics
    this.stats.threatsNeutralized += neutralized;
    this.stats.agentsQuarantined += quarantined;
    this.stats.agentsTerminated += terminated;

    return { neutralized, quarantined, terminated };
  }

  /**
   * Release quarantined agents if quarantine period expired
   */
  releaseQuarantined(agents: Map<string, MicrobiomeAgent>): number {
    const now = Date.now();
    const released: string[] = [];

    for (const [agentId, quarantineTime] of this.quarantined.entries()) {
      if (now - quarantineTime > this.config.quarantineDuration) {
        const agent = agents.get(agentId);
        if (agent) {
          (agent as any).quarantined = false;
          released.push(agentId);
        }
      }
    }

    for (const agentId of released) {
      this.quarantined.delete(agentId);
    }

    return released.length;
  }

  /**
   * Get immune system statistics
   */
  getStats(): ImmuneStats {
    return { ...this.stats };
  }

  /**
   * Get antibodies
   */
  getAntibodies(): Antibody[] {
    return this.antibodies.getAntibodies();
  }

  /**
   * Get immune memory
   */
  getMemory(): ImmuneMemory[] {
    return this.antibodies.getMemory();
  }

  /**
   * Get quarantined agents
   */
  getQuarantined(): string[] {
    return Array.from(this.quarantined.keys());
  }

  /**
   * Check if agent is quarantined
   */
  isQuarantined(agentId: string): boolean {
    return this.quarantined.has(agentId);
  }

  /**
   * Get macrophages
   */
  getMacrophages(): MacrophageAgent[] {
    return [...this.macrophages];
  }

  /**
   * Get T-cells
   */
  getTCells(): TCellAgent[] {
    return [...this.tcells];
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      totalScans: 0,
      threatsDetected: 0,
      threatsNeutralized: 0,
      agentsQuarantined: 0,
      agentsTerminated: 0,
      antibodyCount: 0,
      memoryEntries: 0,
      currentThreatLevel: ThreatLevel.LOW,
    };

    for (const macrophage of this.macrophages) {
      macrophage.resetStats();
    }

    for (const tcell of this.tcells) {
      tcell.resetStats();
    }
  }

  /**
   * Convert anomaly score to threat level
   */
  private anomalyScoreToThreatLevel(score: number): ThreatLevel {
    if (score >= 0.8) return ThreatLevel.CRITICAL;
    if (score >= 0.6) return ThreatLevel.HIGH;
    if (score >= 0.4) return ThreatLevel.MEDIUM;
    return ThreatLevel.LOW;
  }

  /**
   * Calculate overall threat level from threats
   */
  private calculateThreatLevel(threats: ThreatReport[]): ThreatLevel {
    if (threats.length === 0) {
      return ThreatLevel.LOW;
    }

    const criticalCount = threats.filter(t => t.level === ThreatLevel.CRITICAL).length;
    const highCount = threats.filter(t => t.level === ThreatLevel.HIGH).length;

    if (criticalCount > 0) return ThreatLevel.CRITICAL;
    if (highCount > 2) return ThreatLevel.HIGH;
    if (threats.length > 10) return ThreatLevel.MEDIUM;
    if (threats.length > 5) return ThreatLevel.LOW;

    return ThreatLevel.LOW;
  }
}

/**
 * Create an immune system with default configuration
 */
export function createImmuneSystem(config?: ImmuneSystemConfig): ImmuneSystem {
  return new ImmuneSystem(config);
}
