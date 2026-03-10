/**
 * CONFIDENCE ZONE MONITOR
 *
 * Real-time monitoring and alerting for Three-Zone Confidence Model
 *
 * ZONE DEFINITIONS:
 * - GREEN: 0.90-1.00 (Auto-proceed)
 * - YELLOW: 0.75-0.89 (Human review required)
 * - RED: 0.00-0.74 (Stop, diagnose)
 *
 * @module ZoneMonitor
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type ConfidenceZone = 'GREEN' | 'YELLOW' | 'RED';

export interface ZoneThresholds {
  green: number;  // Default: 0.90
  yellow: number; // Default: 0.75
}

export interface ZoneState {
  zone: ConfidenceZone;
  confidence: number;
  timestamp: number;
  tileId: string;
  chainPath?: string; // Path through tile chain (e.g., "A->B->C")
}

export interface ZoneTransition {
  fromZone: ConfidenceZone;
  toZone: ConfidenceZone;
  confidence: number;
  timestamp: number;
  tileId: string;
  transitionType: 'upgrade' | 'downgrade' | 'unchanged';
}

export interface AlertConfig {
  enabled: boolean;
  webhookUrl?: string;
  callback?: (alert: ZoneAlert) => void;
  minSeverity: 'YELLOW' | 'RED';
  cooldownMs: number; // Minimum time between alerts for same tile
}

export interface ZoneAlert {
  id: string;
  tileId: string;
  zone: ConfidenceZone;
  confidence: number;
  alertType: 'zone_enter' | 'zone_drop' | 'zone_escalation';
  timestamp: number;
  message: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
}

export interface ZoneHistoryEntry {
  timestamp: number;
  tileId: string;
  zone: ConfidenceZone;
  confidence: number;
  chainPath?: string;
}

export interface ZoneMetrics {
  tileId: string;
  currentZone: ConfidenceZone;
  currentConfidence: number;
  zoneDistribution: { [K in ConfidenceZone]: number };
  avgConfidence: number;
  transitionCount: number;
  lastTransitionTime: number;
  timeInCurrentZone: number;
  violationCount: number;
}

export interface ChainZoneState {
  chainId: string;
  tiles: string[];
  currentZones: Map<string, ZoneState>;
  compositeZone: ConfidenceZone;
  compositeConfidence: number;
  weakestTile: string;
  violationCount: number;
}

// ============================================================================
// ZONE CALCULATOR
// ============================================================================

export class ZoneCalculator {
  private thresholds: ZoneThresholds;

  constructor(thresholds?: Partial<ZoneThresholds>) {
    this.thresholds = {
      green: thresholds?.green ?? 0.90,
      yellow: thresholds?.yellow ?? 0.75
    };
  }

  /**
   * Calculate zone from confidence score
   */
  calculateZone(confidence: number): ConfidenceZone {
    if (confidence >= this.thresholds.green) {
      return 'GREEN';
    } else if (confidence >= this.thresholds.yellow) {
      return 'YELLOW';
    } else {
      return 'RED';
    }
  }

  /**
   * Calculate composite confidence for sequential tiles (multiplies)
   * A -> B -> C: conf(A) * conf(B) * conf(C)
   */
  calculateSequentialComposite(confidences: number[]): number {
    return confidences.reduce((product, conf) => product * conf, 1.0);
  }

  /**
   * Calculate composite confidence for parallel tiles (weighted average)
   * A || B || C: weighted average based on trust weights
   */
  calculateParallelComposite(
    confidences: number[],
    weights: number[]
  ): number {
    if (confidences.length !== weights.length) {
      throw new Error('Confidences and weights must have same length');
    }

    const totalWeight = weights.reduce((sum, w) => sum + w, 0);
    const weightedSum = confidences.reduce(
      (sum, conf, i) => sum + (conf * weights[i]),
      0
    );

    return weightedSum / totalWeight;
  }

  /**
   * Calculate zone transition type
   */
  calculateTransition(
    fromZone: ConfidenceZone,
    toZone: ConfidenceZone
  ): ZoneTransition['transitionType'] {
    if (fromZone === toZone) return 'unchanged';

    const zoneOrder: Record<ConfidenceZone, number> = {
      'RED': 0,
      'YELLOW': 1,
      'GREEN': 2
    };

    return zoneOrder[toZone] > zoneOrder[fromZone] ? 'upgrade' : 'downgrade';
  }

  /**
   * Check if zone transition requires escalation
   */
  requiresEscalation(
    fromZone: ConfidenceZone,
    toZone: ConfidenceZone
  ): boolean {
    // Escalate if dropping to RED or entering YELLOW from GREEN
    return (
      (fromZone === 'GREEN' && toZone === 'YELLOW') ||
      (fromZone !== 'RED' && toZone === 'RED')
    );
  }

  /**
   * Calculate distance to zone boundary
   */
  distanceToBoundary(confidence: number, targetZone: ConfidenceZone): number {
    const zone = this.calculateZone(confidence);

    if (zone === targetZone) return 0;

    switch (targetZone) {
      case 'GREEN':
        return Math.max(0, this.thresholds.green - confidence);
      case 'YELLOW':
        if (confidence < this.thresholds.yellow) {
          return Math.max(0, this.thresholds.yellow - confidence);
        } else {
          return Math.max(0, confidence - this.thresholds.green);
        }
      case 'RED':
        return Math.max(0, confidence - this.thresholds.yellow);
      default:
        return 0;
    }
  }

  /**
   * Get thresholds
   */
  getThresholds(): ZoneThresholds {
    return { ...this.thresholds };
  }

  /**
   * Update thresholds
   */
  setThresholds(thresholds: Partial<ZoneThresholds>): void {
    if (thresholds.green !== undefined) {
      this.thresholds.green = thresholds.green;
    }
    if (thresholds.yellow !== undefined) {
      this.thresholds.yellow = thresholds.yellow;
    }

    // Validate thresholds
    if (this.thresholds.yellow >= this.thresholds.green) {
      throw new Error('Yellow threshold must be less than green threshold');
    }
  }
}

// ============================================================================
// ALERTER
// ============================================================================

export class Alerter {
  private config: AlertConfig;
  private alertHistory: Map<string, number>; // tileId -> last alert time
  private alertCount: number;

  constructor(config?: Partial<AlertConfig>) {
    this.config = {
      enabled: config?.enabled ?? true,
      webhookUrl: config?.webhookUrl,
      callback: config?.callback,
      minSeverity: config?.minSeverity ?? 'YELLOW',
      cooldownMs: config?.cooldownMs ?? 5000 // 5 seconds default
    };
    this.alertHistory = new Map();
    this.alertCount = 0;
  }

  /**
   * Check if alert should fire based on zone transition
   */
  async checkAlert(
    tileId: string,
    transition: ZoneTransition
  ): Promise<ZoneAlert | null> {
    if (!this.config.enabled) {
      return null;
    }

    // Check cooldown
    const lastAlertTime = this.alertHistory.get(tileId) ?? 0;
    const now = Date.now();
    if (now - lastAlertTime < this.config.cooldownMs) {
      return null;
    }

    // Check minimum severity
    if (this.config.minSeverity === 'RED' && transition.toZone !== 'RED') {
      return null;
    }

    // Determine alert type and severity
    const alertType = this.determineAlertType(transition);
    const severity = this.determineSeverity(transition.toZone);

    // Create alert
    const alert: ZoneAlert = {
      id: `alert_${this.alertCount++}_${Date.now()}`,
      tileId,
      zone: transition.toZone,
      confidence: transition.confidence,
      alertType,
      timestamp: now,
      message: this.generateAlertMessage(tileId, transition),
      severity
    };

    // Update cooldown
    this.alertHistory.set(tileId, now);

    // Send alert
    await this.sendAlert(alert);

    return alert;
  }

  /**
   * Determine alert type from transition
   */
  private determineAlertType(transition: ZoneTransition): ZoneAlert['alertType'] {
    if (transition.transitionType === 'downgrade') {
      return 'zone_drop';
    } else if (transition.transitionType === 'upgrade') {
      return 'zone_escalation';
    } else {
      return 'zone_enter';
    }
  }

  /**
   * Determine severity from zone
   */
  private determineSeverity(zone: ConfidenceZone): ZoneAlert['severity'] {
    switch (zone) {
      case 'RED':
        return 'CRITICAL';
      case 'YELLOW':
        return 'WARNING';
      case 'GREEN':
        return 'INFO';
    }
  }

  /**
   * Generate human-readable alert message
   */
  private generateAlertMessage(tileId: string, transition: ZoneTransition): string {
    const action = {
      'upgrade': 'Improved to',
      'downgrade': 'Dropped to',
      'unchanged': 'Remains in'
    }[transition.transitionType];

    return `Tile ${tileId}: ${action} ${transition.toZone} zone (confidence: ${transition.confidence.toFixed(3)})`;
  }

  /**
   * Send alert via configured channels
   */
  private async sendAlert(alert: ZoneAlert): Promise<void> {
    // Callback
    if (this.config.callback) {
      try {
        this.config.callback(alert);
      } catch (error) {
        console.error('Alert callback error:', error);
      }
    }

    // Webhook
    if (this.config.webhookUrl) {
      try {
        await fetch(this.config.webhookUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(alert)
        });
      } catch (error) {
        console.error('Webhook error:', error);
      }
    }
  }

  /**
   * Get alert count
   */
  getAlertCount(): number {
    return this.alertCount;
  }

  /**
   * Clear alert history (for testing)
   */
  clearHistory(): void {
    this.alertHistory.clear();
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<AlertConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// ============================================================================
// ZONE HISTORY
// ============================================================================

export class ZoneHistory {
  private history: ZoneHistoryEntry[];
  private maxEntries: number;

  constructor(maxEntries: number = 10000) {
    this.history = [];
    this.maxEntries = maxEntries;
  }

  /**
   * Record zone state
   */
  record(state: ZoneState): void {
    const entry: ZoneHistoryEntry = {
      timestamp: state.timestamp,
      tileId: state.tileId,
      zone: state.zone,
      confidence: state.confidence,
      chainPath: state.chainPath
    };

    this.history.push(entry);

    // Maintain max entries
    if (this.history.length > this.maxEntries) {
      this.history.shift();
    }
  }

  /**
   * Get history for specific tile
   */
  getTileHistory(tileId: string, limit?: number): ZoneHistoryEntry[] {
    const tileHistory = this.history.filter(e => e.tileId === tileId);
    return limit ? tileHistory.slice(-limit) : tileHistory;
  }

  /**
   * Get history for time range
   */
  getTimeRange(startTime: number, endTime: number): ZoneHistoryEntry[] {
    return this.history.filter(
      e => e.timestamp >= startTime && e.timestamp <= endTime
    );
  }

  /**
   * Get zone transitions for tile
   */
  getTransitions(tileId: string): ZoneTransition[] {
    const tileHistory = this.getTileHistory(tileId);
    const transitions: ZoneTransition[] = [];

    for (let i = 1; i < tileHistory.length; i++) {
      const prev = tileHistory[i - 1];
      const curr = tileHistory[i];

      if (prev.zone !== curr.zone) {
        const calculator = new ZoneCalculator();
        transitions.push({
          fromZone: prev.zone,
          toZone: curr.zone,
          confidence: curr.confidence,
          timestamp: curr.timestamp,
          tileId: curr.tileId,
          transitionType: calculator.calculateTransition(prev.zone, curr.zone)
        });
      }
    }

    return transitions;
  }

  /**
   * Calculate zone distribution
   */
  getZoneDistribution(tileId?: string): { [K in ConfidenceZone]: number } {
    const entries = tileId
      ? this.getTileHistory(tileId)
      : this.history;

    const distribution = { GREEN: 0, YELLOW: 0, RED: 0 };
    entries.forEach(e => {
      distribution[e.zone]++;
    });

    return distribution;
  }

  /**
   * Get average confidence
   */
  getAverageConfidence(tileId?: string): number {
    const entries = tileId
      ? this.getTileHistory(tileId)
      : this.history;

    if (entries.length === 0) return 0;

    const sum = entries.reduce((acc, e) => acc + e.confidence, 0);
    return sum / entries.length;
  }

  /**
   * Get violation count (YELLOW/RED occurrences)
   */
  getViolationCount(tileId?: string): number {
    const entries = tileId
      ? this.getTileHistory(tileId)
      : this.history;

    return entries.filter(e => e.zone !== 'GREEN').length;
  }

  /**
   * Get violation rate
   */
  getViolationRate(tileId?: string): number {
    const entries = tileId
      ? this.getTileHistory(tileId)
      : this.history;

    if (entries.length === 0) return 0;

    return this.getViolationCount(tileId) / entries.length;
  }

  /**
   * Clear history
   */
  clear(): void {
    this.history = [];
  }

  /**
   * Get all history
   */
  getAll(): ZoneHistoryEntry[] {
    return [...this.history];
  }
}

// ============================================================================
// METRICS EXPORTER (PROMETHEUS)
// ============================================================================

export class MetricsExporter {
  private metrics: Map<string, string>;

  constructor() {
    this.metrics = new Map();
  }

  /**
   * Update metrics from zone state
   */
  update(tileId: string, state: ZoneState): void {
    this.metrics.set(
      `confidence_zone_current{tile="${tileId}"}`,
      String(state.confidence)
    );

    this.metrics.set(
      `zone_state{tile="${tileId}",zone="${state.zone}"}`,
      '1'
    );
  }

  /**
   * Update metrics from zone metrics
   */
  updateFromMetrics(tileId: string, metrics: ZoneMetrics): void {
    // Current confidence
    this.metrics.set(
      `confidence_zone_current{tile="${tileId}"}`,
      String(metrics.currentConfidence)
    );

    // Zone distribution
    Object.entries(metrics.zoneDistribution).forEach(([zone, count]) => {
      this.metrics.set(
        `zone_distribution{tile="${tileId}",zone="${zone}"}`,
        String(count)
      );
    });

    // Average confidence
    this.metrics.set(
      `confidence_avg{tile="${tileId}"}`,
      String(metrics.avgConfidence)
    );

    // Violation count
    this.metrics.set(
      `violations_total{tile="${tileId}"}`,
      String(metrics.violationCount)
    );

    // Time in current zone
    this.metrics.set(
      `zone_time_seconds{tile="${tileId}",zone="${metrics.currentZone}"}`,
      String(metrics.timeInCurrentZone / 1000)
    );
  }

  /**
   * Export as Prometheus format
   */
  exportPrometheus(): string {
    let output = '# HELP confidence_zone_current Current confidence score\n';
    output += '# TYPE confidence_zone_current gauge\n';

    const confidenceMetrics = Array.from(this.metrics.entries())
      .filter(([key]) => key.startsWith('confidence_zone_current'));

    confidenceMetrics.forEach(([key, value]) => {
      const labels = key.match(/\{(.+)\}/)?.[1] ?? '';
      output += `confidence_zone_current{${labels}} ${value}\n`;
    });

    output += '\n# HELP zone_state Current zone state (1 if in zone)\n';
    output += '# TYPE zone_state gauge\n';

    const zoneMetrics = Array.from(this.metrics.entries())
      .filter(([key]) => key.startsWith('zone_state'));

    zoneMetrics.forEach(([key, value]) => {
      const labels = key.match(/\{(.+)\}/)?.[1] ?? '';
      output += `zone_state{${labels}} ${value}\n`;
    });

    output += '\n# HELP violations_total Total zone violations\n';
    output += '# TYPE violations_total counter\n';

    const violationMetrics = Array.from(this.metrics.entries())
      .filter(([key]) => key.startsWith('violations_total'));

    violationMetrics.forEach(([key, value]) => {
      const labels = key.match(/\{(.+)\}/)?.[1] ?? '';
      output += `violations_total{${labels}} ${value}\n`;
    });

    return output;
  }

  /**
   * Export as JSON
   */
  exportJson(): Record<string, string> {
    return Object.fromEntries(this.metrics);
  }

  /**
   * Clear metrics
   */
  clear(): void {
    this.metrics.clear();
  }
}

// ============================================================================
// ZONE MONITOR (MAIN CLASS)
// ============================================================================

export class ZoneMonitor {
  private calculator: ZoneCalculator;
  private alerter: Alerter;
  private history: ZoneHistory;
  private exporter: MetricsExporter;

  // Current states
  private currentStates: Map<string, ZoneState>;
  private chainStates: Map<string, ChainZoneState>;

  // Callbacks
  private onZoneChange?: (tileId: string, transition: ZoneTransition) => void;

  constructor(config?: {
    thresholds?: Partial<ZoneThresholds>;
    alertConfig?: Partial<AlertConfig>;
    maxHistoryEntries?: number;
    onZoneChange?: (tileId: string, transition: ZoneTransition) => void;
  }) {
    this.calculator = new ZoneCalculator(config?.thresholds);
    this.alerter = new Alerter(config?.alertConfig);
    this.history = new ZoneHistory(config?.maxHistoryEntries);
    this.exporter = new MetricsExporter();

    this.currentStates = new Map();
    this.chainStates = new Map();
    this.onZoneChange = config?.onZoneChange;
  }

  // ========================================================================
  // SINGLE TILE MONITORING
  // ========================================================================

  /**
   * Monitor single tile confidence
   */
  async monitorTile(
    tileId: string,
    confidence: number,
    chainPath?: string
  ): Promise<ZoneState | null> {
    const zone = this.calculator.calculateZone(confidence);
    const timestamp = Date.now();

    const newState: ZoneState = {
      zone,
      confidence,
      timestamp,
      tileId,
      chainPath
    };

    // Check for transition
    const oldState = this.currentStates.get(tileId);
    if (oldState && oldState.zone !== zone) {
      const transition: ZoneTransition = {
        fromZone: oldState.zone,
        toZone: zone,
        confidence,
        timestamp,
        tileId,
        transitionType: this.calculator.calculateTransition(oldState.zone, zone)
      };

      // Trigger alert
      await this.alerter.checkAlert(tileId, transition);

      // Trigger callback
      if (this.onZoneChange) {
        this.onZoneChange(tileId, transition);
      }
    }

    // Update state
    this.currentStates.set(tileId, newState);
    this.history.record(newState);
    this.exporter.update(tileId, newState);

    return newState;
  }

  /**
   * Get current state for tile
   */
  getTileState(tileId: string): ZoneState | undefined {
    return this.currentStates.get(tileId);
  }

  /**
   * Get metrics for tile
   */
  getTileMetrics(tileId: string): ZoneMetrics {
    const currentState = this.currentStates.get(tileId);
    if (!currentState) {
      throw new Error(`No state found for tile ${tileId}`);
    }

    const tileHistory = this.history.getTileHistory(tileId);
    const transitions = this.history.getTransitions(tileId);

    return {
      tileId,
      currentZone: currentState.zone,
      currentConfidence: currentState.confidence,
      zoneDistribution: this.history.getZoneDistribution(tileId),
      avgConfidence: this.history.getAverageConfidence(tileId),
      transitionCount: transitions.length,
      lastTransitionTime: transitions.length > 0
        ? transitions[transitions.length - 1].timestamp
        : currentState.timestamp,
      timeInCurrentZone: Date.now() - currentState.timestamp,
      violationCount: this.history.getViolationCount(tileId)
    };
  }

  // ========================================================================
  // CHAIN MONITORING
  // ========================================================================

  /**
   * Monitor tile chain (sequential execution)
   */
  async monitorChain(
    chainId: string,
    tileIds: string[],
    confidences: Map<string, number>
  ): Promise<ChainZoneState> {
    if (tileIds.length !== confidences.size) {
      throw new Error('Tile IDs and confidences must have same count');
    }

    // Monitor each tile
    const states: ZoneState[] = [];
    for (const tileId of tileIds) {
      const confidence = confidences.get(tileId);
      if (confidence === undefined) {
        throw new Error(`Missing confidence for tile ${tileId}`);
      }

      const chainPath = tileIds.join('->');
      const state = await this.monitorTile(tileId, confidence, chainPath);
      if (state) {
        states.push(state);
      }
    }

    // Calculate composite confidence (sequential multiplication)
    const confidenceValues = states.map(s => s.confidence);
    const compositeConfidence = this.calculator.calculateSequentialComposite(confidenceValues);
    const compositeZone = this.calculator.calculateZone(compositeConfidence);

    // Find weakest tile
    const weakestTile = states.reduce((weakest, state) =>
      state.confidence < weakest.confidence ? state : weakest
    );

    // Count violations
    const violationCount = states.filter(s => s.zone !== 'GREEN').length;

    // Create chain state
    const chainState: ChainZoneState = {
      chainId,
      tiles: tileIds,
      currentZones: new Map(states.map(s => [s.tileId, s])),
      compositeZone,
      compositeConfidence,
      weakestTile: weakestTile.tileId,
      violationCount
    };

    this.chainStates.set(chainId, chainState);

    return chainState;
  }

  /**
   * Get chain state
   */
  getChainState(chainId: string): ChainZoneState | undefined {
    return this.chainStates.get(chainId);
  }

  /**
   * Get all chains with violations
   */
  getChainsWithViolations(): ChainZoneState[] {
    return Array.from(this.chainStates.values())
      .filter(chain => chain.violationCount > 0);
  }

  // ========================================================================
  // BULK OPERATIONS
  // ========================================================================

  /**
   * Monitor multiple tiles in batch
   */
  async monitorBatch(
    tileConfidences: Map<string, number>
  ): Promise<Map<string, ZoneState>> {
    const results = new Map<string, ZoneState>();

    for (const [tileId, confidence] of tileConfidences.entries()) {
      const state = await this.monitorTile(tileId, confidence);
      if (state) {
        results.set(tileId, state);
      }
    }

    return results;
  }

  /**
   * Get all tiles in specific zone
   */
  getTilesInZone(zone: ConfidenceZone): string[] {
    return Array.from(this.currentStates.entries())
      .filter(([_, state]) => state.zone === zone)
      .map(([tileId, _]) => tileId);
  }

  /**
   * Get global metrics
   */
  getGlobalMetrics(): {
    totalTiles: number;
    zoneDistribution: { [K in ConfidenceZone]: number };
    violationRate: number;
    avgConfidence: number;
    chainsWithViolations: number;
  } {
    const allStates = Array.from(this.currentStates.values());

    return {
      totalTiles: allStates.length,
      zoneDistribution: this.history.getZoneDistribution(),
      violationRate: this.history.getViolationRate(),
      avgConfidence: this.history.getAverageConfidence(),
      chainsWithViolations: this.getChainsWithViolations().length
    };
  }

  // ========================================================================
  // EXPORT & QUERY
  // ========================================================================

  /**
   * Export metrics
   */
  exportMetrics(format: 'prometheus' | 'json' = 'prometheus'): string {
    if (format === 'prometheus') {
      return this.exporter.exportPrometheus();
    } else {
      return JSON.stringify(this.exporter.exportJson(), null, 2);
    }
  }

  /**
   * Query history
   */
  queryHistory(filter?: {
    tileId?: string;
    startTime?: number;
    endTime?: number;
    zone?: ConfidenceZone;
  }): ZoneHistoryEntry[] {
    let entries = this.history.getAll();

    if (filter?.tileId) {
      entries = entries.filter(e => e.tileId === filter.tileId);
    }

    if (filter?.startTime) {
      entries = entries.filter(e => e.timestamp >= filter.startTime!);
    }

    if (filter?.endTime) {
      entries = entries.filter(e => e.timestamp <= filter.endTime!);
    }

    if (filter?.zone) {
      entries = entries.filter(e => e.zone === filter.zone);
    }

    return entries;
  }

  /**
   * Generate violation report
   */
  generateViolationReport(): {
    timestamp: number;
    violations: Array<{
      tileId: string;
      currentZone: ConfidenceZone;
      confidence: number;
      violationCount: number;
      violationRate: number;
    }>;
    summary: {
      totalViolations: number;
      tilesWithViolations: number;
      criticalViolations: number; // RED zone
    };
  } {
    const tiles = Array.from(this.currentStates.keys());
    const violations = tiles
      .map(tileId => {
        const metrics = this.getTileMetrics(tileId);
        return {
          tileId,
          currentZone: metrics.currentZone,
          confidence: metrics.currentConfidence,
          violationCount: metrics.violationCount,
          violationRate: this.history.getViolationRate(tileId)
        };
      })
      .filter(v => v.violationCount > 0);

    const criticalViolations = violations.filter(
      v => v.currentZone === 'RED'
    ).length;

    return {
      timestamp: Date.now(),
      violations,
      summary: {
        totalViolations: violations.reduce((sum, v) => sum + v.violationCount, 0),
        tilesWithViolations: violations.length,
        criticalViolations
      }
    };
  }

  // ========================================================================
  // CONFIGURATION
  // ========================================================================

  /**
   * Update zone thresholds
   */
  setThresholds(thresholds: Partial<ZoneThresholds>): void {
    this.calculator.setThresholds(thresholds);
  }

  /**
   * Update alert configuration
   */
  setAlertConfig(config: Partial<AlertConfig>): void {
    this.alerter.updateConfig(config);
  }

  /**
   * Set zone change callback
   */
  setZoneChangeCallback(
    callback: (tileId: string, transition: ZoneTransition) => void
  ): void {
    this.onZoneChange = callback;
  }

  // ========================================================================
  // RESET & CLEAR
  // ========================================================================

  /**
   * Clear all history
   */
  clearHistory(): void {
    this.history.clear();
  }

  /**
   * Clear all states
   */
  clearStates(): void {
    this.currentStates.clear();
    this.chainStates.clear();
    this.exporter.clear();
  }

  /**
   * Full reset
   */
  reset(): void {
    this.clearHistory();
    this.clearStates();
    this.alerter.clearHistory();
  }
}

// ============================================================================
// EXAMPLE USAGE
// ============================================================================

/**
 * Example: Basic tile monitoring
 */
export async function exampleBasicMonitoring() {
  const monitor = new ZoneMonitor({
    thresholds: {
      green: 0.90,
      yellow: 0.75
    },
    alertConfig: {
      enabled: true,
      minSeverity: 'YELLOW',
      cooldownMs: 5000
    },
    onZoneChange: (tileId, transition) => {
      console.log(`Zone change: ${tileId} ${transition.fromZone} -> ${transition.toZone}`);
    }
  });

  // Monitor tiles
  await monitor.monitorTile('tile-a', 0.95); // GREEN
  await monitor.monitorTile('tile-b', 0.82); // YELLOW
  await monitor.monitorTile('tile-c', 0.65); // RED (alerts)

  // Get metrics
  const metrics = monitor.getTileMetrics('tile-c');
  console.log('Tile C metrics:', metrics);

  // Export Prometheus metrics
  console.log(monitor.exportMetrics('prometheus'));
}

/**
 * Example: Chain monitoring
 */
export async function exampleChainMonitoring() {
  const monitor = new ZoneMonitor();

  // Define chain: A -> B -> C
  const chainId = 'chain-1';
  const tileIds = ['tile-a', 'tile-b', 'tile-c'];
  const confidences = new Map([
    ['tile-a', 0.95],
    ['tile-b', 0.88],
    ['tile-c', 0.72]
  ]);

  // Monitor chain
  const chainState = await monitor.monitorChain(chainId, tileIds, confidences);

  console.log('Chain composite confidence:', chainState.compositeConfidence);
  console.log('Chain composite zone:', chainState.compositeZone);
  console.log('Weakest tile:', chainState.weakestTile);
  console.log('Violations:', chainState.violationCount);
}

/**
 * Example: Webhook alerts
 */
export async function exampleWebhookAlerts() {
  const monitor = new ZoneMonitor({
    alertConfig: {
      enabled: true,
      webhookUrl: 'https://hooks.example.com/alerts',
      minSeverity: 'YELLOW',
      cooldownMs: 10000,
      callback: (alert) => {
        console.log(`Alert callback: ${alert.message}`);
      }
    }
  });

  // Simulate zone drops
  await monitor.monitorTile('tile-1', 0.92); // GREEN
  await monitor.monitorTile('tile-1', 0.78); // YELLOW (alerts)
  await monitor.monitorTile('tile-1', 0.65); // RED (alerts)
}

/**
 * Example: Violation reporting
 */
export async function exampleViolationReporting() {
  const monitor = new ZoneMonitor();

  // Monitor many tiles
  const tiles = new Map<string, number>();
  for (let i = 1; i <= 10; i++) {
    tiles.set(`tile-${i}`, 0.5 + Math.random() * 0.5);
  }

  await monitor.monitorBatch(tiles);

  // Generate report
  const report = monitor.generateViolationReport();
  console.log('Violation report:', JSON.stringify(report, null, 2));

  // Get global metrics
  const globalMetrics = monitor.getGlobalMetrics();
  console.log('Global metrics:', globalMetrics);
}

/**
 * Example: Historical analysis
 */
export async function exampleHistoricalAnalysis() {
  const monitor = new ZoneMonitor();

  // Simulate time series
  const tileId = 'tile-1';
  for (let i = 0; i < 100; i++) {
    const confidence = 0.5 + Math.random() * 0.5;
    await monitor.monitorTile(tileId, confidence);

    // Small delay between updates
    await new Promise(resolve => setTimeout(resolve, 10));
  }

  // Query history
  const lastHour = Date.now() - 60 * 60 * 1000;
  const recentHistory = monitor.queryHistory({
    tileId,
    startTime: lastHour,
    zone: 'RED'
  });

  console.log(`RED zone occurrences in last hour: ${recentHistory.length}`);

  // Get transitions
  const transitions = monitor.history.getTransitions(tileId);
  console.log(`Total transitions: ${transitions.length}`);
  console.log(`Downgrades: ${transitions.filter(t => t.transitionType === 'downgrade').length}`);
}

// Run examples if executed directly
if (require.main === module) {
  (async () => {
    console.log('=== Basic Monitoring Example ===');
    await exampleBasicMonitoring();

    console.log('\n=== Chain Monitoring Example ===');
    await exampleChainMonitoring();

    console.log('\n=== Violation Report Example ===');
    await exampleViolationReporting();
  })();
}

export * from './zone-monitor';
