/**
 * RateDeltaTile: Monitors rate of change per unit
 *
 * This tile tracks the rate of change of a value over time and provides
 * intelligent monitoring with deadband triggers and confidence tracking.
 *
 * Based on SuperInstance white paper: "Rate-Based Change Mechanics"
 */

import { Tile, TileResult, classifyZone } from '../core/Tile';
import { RateVector, DeadbandTrigger, DeadbandConfig } from '../../../superinstance/types/base';

/**
 * Input for RateDeltaTile
 */
export interface RateDeltaInput {
  // Current value to monitor
  value: number;

  // Timestamp of current value (defaults to now)
  timestamp?: number;

  // Unit of measurement (for display and normalization)
  unit?: string;

  // Previous measurement context
  previous?: {
    value: number;
    timestamp: number;
    rate?: number;
  };

  // Configuration overrides
  config?: {
    deadband?: Partial<DeadbandConfig>;
    minUpdateInterval?: number;
    normalizationFactor?: number; // For converting to standard units
  };
}

/**
 * Output from RateDeltaTile
 */
export interface RateDeltaOutput {
  // Current value
  value: number;

  // Rate of change (first derivative)
  rate: number;

  // Acceleration (second derivative)
  acceleration: number;

  // Rate vector with full metadata
  rateVector: RateVector;

  // Deadband trigger status
  deadband: {
    triggered: boolean;
    lastTriggerValue: number;
    lastTriggerTime: number;
    withinDeadband: boolean;
  };

  // Statistical summary
  statistics: {
    meanRate: number;
    rateVariance: number;
    trend: 'increasing' | 'decreasing' | 'stable' | 'oscillating';
    stability: number; // 0-1, higher = more stable
  };

  // Confidence in rate measurement
  confidence: number;
}

/**
 * RateDeltaTile Configuration
 */
export interface RateDeltaConfig {
  id: string;
  deadband: DeadbandConfig;
  minUpdateInterval: number; // ms
  normalizationFactor: number;
  historyLength: number;
  stabilityThreshold: number;
}

/**
 * RateDeltaTile - Monitors rate of change with deadband triggers
 */
export class RateDeltaTile implements Tile<RateDeltaInput, RateDeltaOutput> {
  readonly id: string;
  readonly type = 'rate_delta';
  readonly version = '1.0.0';

  private config: RateDeltaConfig;
  private deadbandTrigger: DeadbandTrigger;
  private history: Array<{
    value: number;
    timestamp: number;
    rate: number;
  }> = [];
  private lastTriggerValue: number = 0;
  private lastTriggerTime: number = 0;

  constructor(config: Partial<RateDeltaConfig> = {}) {
    this.id = config.id || `rate_delta_${Date.now()}`;

    const deadbandConfig: DeadbandConfig = {
      threshold: 0.1,    // 10% change threshold
      deadband: 0.05,    // 5% deadband
      enabled: true,
      minUpdateInterval: 1000, // 1 second
      ...config.deadband,
    };

    this.config = {
      id: this.id,
      deadband: deadbandConfig,
      minUpdateInterval: 1000,
      normalizationFactor: 1.0,
      historyLength: 50,
      stabilityThreshold: 0.1,
      ...config,
    };

    this.deadbandTrigger = new DeadbandTrigger(this.config.deadband);
  }

  /**
   * Execute the tile
   */
  async execute(input: RateDeltaInput): Promise<TileResult<RateDeltaOutput>> {
    const startTime = Date.now();

    try {
      const timestamp = input.timestamp || Date.now();
      const normalizedValue = input.value * this.config.normalizationFactor;

      // Get previous measurement
      const previous = input.previous || this.getLatestHistory();
      const previousValue = previous?.value || normalizedValue;
      const previousTimestamp = previous?.timestamp || timestamp - 1000; // Default 1 second ago

      // Calculate rate of change
      const dt = (timestamp - previousTimestamp) / 1000; // Convert to seconds
      const rate = dt > 0 ? (normalizedValue - previousValue) / dt : 0;

      // Calculate acceleration
      const previousRate = previous?.rate || 0;
      const acceleration = dt > 0 ? (rate - previousRate) / dt : 0;

      // Check deadband trigger
      const deadbandTriggered = this.deadbandTrigger.shouldTrigger(
        normalizedValue,
        previousValue
      );
      const canUpdate = this.deadbandTrigger.canUpdate();

      if (deadbandTriggered && canUpdate) {
        this.lastTriggerValue = normalizedValue;
        this.lastTriggerTime = timestamp;
      }

      // Update history
      this.updateHistory({
        value: normalizedValue,
        timestamp,
        rate,
      });

      // Calculate statistics
      const statistics = this.calculateStatistics(rate);

      // Create rate vector
      const rateVector: RateVector = {
        value: rate,
        acceleration,
        timestamp,
        confidence: this.calculateRateConfidence(rate, acceleration, statistics.stability),
      };

      // Calculate overall confidence
      const confidence = this.calculateConfidence(rateVector, statistics, deadbandTriggered);

      const output: RateDeltaOutput = {
        value: normalizedValue,
        rate,
        acceleration,
        rateVector,
        deadband: {
          triggered: deadbandTriggered && canUpdate,
          lastTriggerValue: this.lastTriggerValue,
          lastTriggerTime: this.lastTriggerTime,
          withinDeadband: !deadbandTriggered,
        },
        statistics,
        confidence,
      };

      const duration = Date.now() - startTime;

      return {
        output,
        confidence,
        zone: classifyZone(confidence),
        trace: this.generateTrace(input, output, duration),
        duration,
        metadata: {
          unit: input.unit,
          rawValue: input.value,
          normalizedValue,
          dt,
          deadbandConfig: this.config.deadband,
        },
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      return {
        output: this.getErrorOutput(),
        confidence: 0.1,
        zone: 'RED',
        trace: `Error: ${error instanceof Error ? error.message : String(error)}`,
        duration,
        metadata: { error: String(error) },
      };
    }
  }

  /**
   * Get latest history entry
   */
  private getLatestHistory(): { value: number; timestamp: number; rate: number } | null {
    if (this.history.length === 0) return null;
    return this.history[this.history.length - 1];
  }

  /**
   * Update history with new measurement
   */
  private updateHistory(measurement: {
    value: number;
    timestamp: number;
    rate: number;
  }): void {
    this.history.push(measurement);

    // Trim history if too long
    if (this.history.length > this.config.historyLength) {
      this.history = this.history.slice(-this.config.historyLength);
    }
  }

  /**
   * Calculate statistics from rate history
   */
  private calculateStatistics(currentRate: number): RateDeltaOutput['statistics'] {
    if (this.history.length < 2) {
      return {
        meanRate: currentRate,
        rateVariance: 0,
        trend: 'stable',
        stability: 1.0,
      };
    }

    // Calculate mean rate
    const rates = this.history.map(h => h.rate);
    const meanRate = rates.reduce((sum, r) => sum + r, 0) / rates.length;

    // Calculate variance
    const variance = rates.reduce((sum, r) => sum + Math.pow(r - meanRate, 2), 0) / rates.length;

    // Determine trend
    const recentRates = rates.slice(-5);
    const trend = this.determineTrend(recentRates);

    // Calculate stability (inverse of coefficient of variation)
    const stability = meanRate !== 0
      ? 1 / (1 + Math.sqrt(variance) / Math.abs(meanRate))
      : 1 / (1 + Math.sqrt(variance));

    return {
      meanRate,
      rateVariance: variance,
      trend,
      stability: Math.max(0, Math.min(1, stability)),
    };
  }

  /**
   * Determine trend from recent rates
   */
  private determineTrend(rates: number[]): 'increasing' | 'decreasing' | 'stable' | 'oscillating' {
    if (rates.length < 2) return 'stable';

    // Check for consistent direction
    let increasing = 0;
    let decreasing = 0;
    let signChanges = 0;

    for (let i = 1; i < rates.length; i++) {
      const diff = rates[i] - rates[i - 1];
      if (diff > 0.001) increasing++;
      if (diff < -0.001) decreasing++;
      if (rates[i] * rates[i - 1] < 0) signChanges++;
    }

    const oscillationRatio = signChanges / (rates.length - 1);

    if (oscillationRatio > 0.5) return 'oscillating';
    if (increasing > decreasing * 2) return 'increasing';
    if (decreasing > increasing * 2) return 'decreasing';
    return 'stable';
  }

  /**
   * Calculate confidence for rate measurement
   */
  private calculateRateConfidence(
    rate: number,
    acceleration: number,
    stability: number
  ): number {
    let confidence = 1.0;

    // Penalize for high rates (potentially noisy)
    if (Math.abs(rate) > 1000) confidence *= 0.3;
    else if (Math.abs(rate) > 100) confidence *= 0.6;
    else if (Math.abs(rate) > 10) confidence *= 0.8;

    // Penalize for high acceleration
    if (Math.abs(acceleration) > 100) confidence *= 0.5;
    else if (Math.abs(acceleration) > 10) confidence *= 0.7;

    // Reward for stability
    confidence = confidence * 0.7 + stability * 0.3;

    return Math.max(0, Math.min(1, confidence));
  }

  /**
   * Calculate overall confidence
   */
  private calculateConfidence(
    rateVector: RateVector,
    statistics: RateDeltaOutput['statistics'],
    deadbandTriggered: boolean
  ): number {
    let confidence = rateVector.confidence;

    // Adjust based on statistics
    confidence = confidence * 0.6 + statistics.stability * 0.4;

    // Penalize for deadband triggers (sudden changes)
    if (deadbandTriggered) {
      confidence *= 0.8;
    }

    // Penalize for oscillating trends
    if (statistics.trend === 'oscillating') {
      confidence *= 0.7;
    }

    return Math.max(0.1, Math.min(1, confidence));
  }

  /**
   * Generate execution trace
   */
  private generateTrace(
    input: RateDeltaInput,
    output: RateDeltaOutput,
    duration: number
  ): string {
    const lines = [
      `RateDeltaTile Execution Trace`,
      `ID: ${this.id}`,
      `Timestamp: ${new Date().toISOString()}`,
      `Duration: ${duration}ms`,
      ``,
      `Input:`,
      `  Value: ${input.value}${input.unit ? ' ' + input.unit : ''}`,
      `  Normalized: ${output.value}`,
      ``,
      `Rate Analysis:`,
      `  Rate: ${output.rate.toFixed(4)}/sec`,
      `  Acceleration: ${output.acceleration.toFixed(4)}/sec²`,
      `  Confidence: ${(output.rateVector.confidence * 100).toFixed(1)}%`,
      ``,
      `Deadband Status:`,
      `  Triggered: ${output.deadband.triggered ? 'YES' : 'no'}`,
      `  Within Deadband: ${output.deadband.withinDeadband ? 'YES' : 'no'}`,
      `  Last Trigger: ${output.deadband.lastTriggerTime ? new Date(output.deadband.lastTriggerTime).toISOString() : 'never'}`,
      ``,
      `Statistics:`,
      `  Mean Rate: ${output.statistics.meanRate.toFixed(4)}`,
      `  Variance: ${output.statistics.rateVariance.toFixed(6)}`,
      `  Trend: ${output.statistics.trend}`,
      `  Stability: ${(output.statistics.stability * 100).toFixed(1)}%`,
      ``,
      `Overall Confidence: ${(output.confidence * 100).toFixed(1)}%`,
      `Zone: ${classifyZone(output.confidence)}`,
      ``,
      `History: ${this.history.length} entries`,
    ];

    return lines.join('\n');
  }

  /**
   * Get error output
   */
  private getErrorOutput(): RateDeltaOutput {
    return {
      value: 0,
      rate: 0,
      acceleration: 0,
      rateVector: {
        value: 0,
        acceleration: 0,
        timestamp: Date.now(),
        confidence: 0,
      },
      deadband: {
        triggered: false,
        lastTriggerValue: 0,
        lastTriggerTime: 0,
        withinDeadband: true,
      },
      statistics: {
        meanRate: 0,
        rateVariance: 0,
        trend: 'stable',
        stability: 0,
      },
      confidence: 0,
    };
  }

  /**
   * Validate input
   */
  validateInput(input: unknown): input is RateDeltaInput {
    if (!input || typeof input !== 'object') return false;

    const obj = input as Record<string, unknown>;

    // Check value
    if (typeof obj.value !== 'number') return false;

    // Check optional timestamp
    if (obj.timestamp !== undefined && typeof obj.timestamp !== 'number') {
      return false;
    }

    // Check optional unit
    if (obj.unit !== undefined && typeof obj.unit !== 'string') {
      return false;
    }

    // Check optional previous
    if (obj.previous !== undefined) {
      const previous = obj.previous;
      if (!previous || typeof previous !== 'object') return false;
      const prev = previous as Record<string, unknown>;
      if (typeof prev.value !== 'number' || typeof prev.timestamp !== 'number') {
        return false;
      }
      if (prev.rate !== undefined && typeof prev.rate !== 'number') {
        return false;
      }
    }

    return true;
  }

  /**
   * Serialize tile state
   */
  serialize(): Record<string, unknown> {
    return {
      id: this.id,
      type: this.type,
      version: this.version,
      config: this.config,
      historyLength: this.history.length,
      lastTriggerValue: this.lastTriggerValue,
      lastTriggerTime: this.lastTriggerTime,
      deadbandState: {
        lastValue: (this.deadbandTrigger as any).lastValue,
        lastUpdate: (this.deadbandTrigger as any).lastUpdate,
        triggered: (this.deadbandTrigger as any).triggered,
      },
    };
  }

  /**
   * Deserialize tile state
   */
  deserialize(data: Record<string, unknown>): void {
    // Note: In a real implementation, this would restore history and state
    // For simplicity, we just update the ID if provided
    if (data.id && typeof data.id === 'string') {
      (this as any).id = data.id;
    }
  }
}

/**
 * Factory function to create RateDeltaTile
 */
export function createRateDeltaTile(
  config?: Partial<RateDeltaConfig>
): RateDeltaTile {
  return new RateDeltaTile(config);
}