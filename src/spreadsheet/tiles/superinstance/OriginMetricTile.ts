/**
 * OriginMetricTile: Tracks radial distance changes
 *
 * This tile implements origin-centric metric tracking for SuperInstance cells.
 * It tracks the radial distance from a cell's origin and monitors changes in
 * that distance over time.
 *
 * Based on SuperInstance white paper: "Origin-Centric Reference System"
 */

import { Tile, TileResult, classifyZone } from '../core/Tile';
import { RateVector, Vector3D } from '../../../superinstance/types/base';

/**
 * Input for OriginMetricTile
 */
export interface OriginMetricInput {
  // Current position in 3D space
  position: Vector3D;

  // Reference origin (defaults to [0,0,0] if not provided)
  origin?: Vector3D;

  // Previous measurement (for rate calculation)
  previous?: {
    position: Vector3D;
    timestamp: number;
    distance: number;
  };

  // Configuration
  config?: {
    smoothingFactor?: number; // Exponential smoothing factor (0-1)
    minChangeThreshold?: number; // Minimum change to trigger update
    maxHistoryLength?: number; // Maximum history to keep
  };
}

/**
 * Output from OriginMetricTile
 */
export interface OriginMetricOutput {
  // Current radial distance from origin
  distance: number;

  // Rate of change of distance
  rateOfChange: RateVector;

  // Historical distances (for trend analysis)
  history: Array<{
    distance: number;
    timestamp: number;
    position: Vector3D;
  }>;

  // Anomaly detection flags
  anomalies: {
    suddenChange: boolean;
    acceleratingChange: boolean;
    oscillating: boolean;
  };

  // Confidence in measurements
  confidence: number;
}

/**
 * OriginMetricTile Configuration
 */
export interface OriginMetricConfig {
  id: string;
  smoothingFactor: number; // 0 = no smoothing, 1 = maximum smoothing
  minChangeThreshold: number; // Minimum distance change to record
  maxHistoryLength: number; // Maximum history entries
  anomalyThresholds: {
    suddenChange: number; // Threshold for sudden distance changes
    acceleration: number; // Threshold for acceleration
    oscillation: number; // Threshold for oscillation detection
  };
}

/**
 * OriginMetricTile - Tracks radial distance changes from origin
 */
export class OriginMetricTile implements Tile<OriginMetricInput, OriginMetricOutput> {
  readonly id: string;
  readonly type = 'origin_metric';
  readonly version = '1.0.0';

  private config: OriginMetricConfig;
  private history: Array<{
    distance: number;
    timestamp: number;
    position: Vector3D;
  }> = [];

  constructor(config: Partial<OriginMetricConfig> = {}) {
    this.id = config.id || `origin_metric_${Date.now()}`;
    this.config = {
      id: this.id,
      smoothingFactor: 0.7,
      minChangeThreshold: 0.01,
      maxHistoryLength: 100,
      anomalyThresholds: {
        suddenChange: 0.5, // 50% sudden change
        acceleration: 0.2, // 20% acceleration threshold
        oscillation: 0.3, // 30% oscillation threshold
      },
      ...config,
    };
  }

  /**
   * Execute the tile
   */
  async execute(input: OriginMetricInput): Promise<TileResult<OriginMetricOutput>> {
    const startTime = Date.now();

    try {
      // Calculate current distance
      const origin = input.origin || { x: 0, y: 0, z: 0 };
      const distance = this.calculateDistance(input.position, origin);

      // Get previous measurement
      const previous = input.previous || this.getLatestHistory();
      const timestamp = Date.now();

      // Calculate rate of change
      const rateOfChange = this.calculateRateOfChange(
        distance,
        previous,
        timestamp
      );

      // Update history
      this.updateHistory({
        distance,
        timestamp,
        position: input.position,
      });

      // Detect anomalies
      const anomalies = this.detectAnomalies(distance, rateOfChange);

      // Calculate confidence
      const confidence = this.calculateConfidence(anomalies, rateOfChange);

      // Apply smoothing if configured
      const smoothedDistance = this.applySmoothing(distance);

      const output: OriginMetricOutput = {
        distance: smoothedDistance,
        rateOfChange,
        history: this.history.slice(-this.config.maxHistoryLength),
        anomalies,
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
          origin,
          position: input.position,
          rawDistance: distance,
          smoothedDistance,
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
   * Calculate Euclidean distance between two points
   */
  private calculateDistance(a: Vector3D, b: Vector3D): number {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const dz = a.z - b.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  /**
   * Calculate rate of change
   */
  private calculateRateOfChange(
    currentDistance: number,
    previous: { distance: number; timestamp: number } | null,
    currentTimestamp: number
  ): RateVector {
    if (!previous || previous.timestamp === currentTimestamp) {
      return {
        value: 0,
        acceleration: 0,
        timestamp: currentTimestamp,
        confidence: 0.5,
      };
    }

    const dt = (currentTimestamp - previous.timestamp) / 1000; // Convert to seconds
    if (dt <= 0) {
      return {
        value: 0,
        acceleration: 0,
        timestamp: currentTimestamp,
        confidence: 0.5,
      };
    }

    // Calculate velocity (first derivative)
    const velocity = (currentDistance - previous.distance) / dt;

    // Get previous rate for acceleration calculation
    const previousRate = this.getPreviousRate();
    const previousVelocity = previousRate?.value || 0;
    const previousTimestamp = previousRate?.timestamp || previous.timestamp;

    const dtRate = (currentTimestamp - previousTimestamp) / 1000;
    const acceleration = dtRate > 0 ? (velocity - previousVelocity) / dtRate : 0;

    // Calculate confidence based on measurement stability
    const confidence = this.calculateRateConfidence(
      currentDistance,
      previous.distance,
      dt
    );

    return {
      value: velocity,
      acceleration,
      timestamp: currentTimestamp,
      confidence,
    };
  }

  /**
   * Get previous rate from history
   */
  private getPreviousRate(): RateVector | null {
    if (this.history.length < 2) return null;

    const current = this.history[this.history.length - 1];
    const previous = this.history[this.history.length - 2];

    const dt = (current.timestamp - previous.timestamp) / 1000;
    if (dt <= 0) return null;

    const velocity = (current.distance - previous.distance) / dt;

    return {
      value: velocity,
      acceleration: 0, // Would need more history for acceleration
      timestamp: current.timestamp,
      confidence: 0.8,
    };
  }

  /**
   * Update history with new measurement
   */
  private updateHistory(measurement: {
    distance: number;
    timestamp: number;
    position: Vector3D;
  }): void {
    // Check if change is significant enough to record
    if (this.history.length > 0) {
      const last = this.history[this.history.length - 1];
      const change = Math.abs(measurement.distance - last.distance);
      const relativeChange = change / Math.max(last.distance, 0.001);

      if (relativeChange < this.config.minChangeThreshold) {
        // Update last entry instead of adding new one
        this.history[this.history.length - 1] = measurement;
        return;
      }
    }

    this.history.push(measurement);

    // Trim history if too long
    if (this.history.length > this.config.maxHistoryLength) {
      this.history = this.history.slice(-this.config.maxHistoryLength);
    }
  }

  /**
   * Get latest history entry
   */
  private getLatestHistory(): { distance: number; timestamp: number } | null {
    if (this.history.length === 0) return null;
    const latest = this.history[this.history.length - 1];
    return {
      distance: latest.distance,
      timestamp: latest.timestamp,
    };
  }

  /**
   * Detect anomalies in distance measurements
   */
  private detectAnomalies(
    currentDistance: number,
    rateOfChange: RateVector
  ): OriginMetricOutput['anomalies'] {
    if (this.history.length < 3) {
      return {
        suddenChange: false,
        acceleratingChange: false,
        oscillating: false,
      };
    }

    // Check for sudden changes
    const lastDistance = this.history[this.history.length - 2]?.distance || 0;
    const change = Math.abs(currentDistance - lastDistance);
    const relativeChange = change / Math.max(lastDistance, 0.001);
    const suddenChange = relativeChange > this.config.anomalyThresholds.suddenChange;

    // Check for accelerating changes
    const acceleratingChange =
      Math.abs(rateOfChange.acceleration) > this.config.anomalyThresholds.acceleration;

    // Check for oscillations (sign changes in rate)
    const oscillating = this.detectOscillations();

    return {
      suddenChange,
      acceleratingChange,
      oscillating,
    };
  }

  /**
   * Detect oscillations in distance measurements
   */
  private detectOscillations(): boolean {
    if (this.history.length < 5) return false;

    // Count sign changes in rate of change
    let signChanges = 0;
    for (let i = 1; i < Math.min(this.history.length, 5); i++) {
      const current = this.history[this.history.length - i];
      const previous = this.history[this.history.length - i - 1];

      if (previous && current) {
        const rate = current.distance - previous.distance;
        const prevRate = i > 1
          ? this.history[this.history.length - i].distance -
            this.history[this.history.length - i - 1].distance
          : 0;

        if (rate * prevRate < 0) {
          // Sign change
          signChanges++;
        }
      }
    }

    const oscillationRatio = signChanges / Math.min(this.history.length - 1, 4);
    return oscillationRatio > this.config.anomalyThresholds.oscillation;
  }

  /**
   * Calculate confidence based on anomalies and rate stability
   */
  private calculateConfidence(
    anomalies: OriginMetricOutput['anomalies'],
    rateOfChange: RateVector
  ): number {
    let confidence = 1.0;

    // Penalize for anomalies
    if (anomalies.suddenChange) confidence *= 0.5;
    if (anomalies.acceleratingChange) confidence *= 0.7;
    if (anomalies.oscillating) confidence *= 0.6;

    // Penalize for high rates (potentially noisy)
    if (Math.abs(rateOfChange.value) > 10) confidence *= 0.8;
    if (Math.abs(rateOfChange.acceleration) > 5) confidence *= 0.7;

    // Reward for high rate confidence
    confidence = confidence * 0.7 + rateOfChange.confidence * 0.3;

    return Math.max(0, Math.min(1, confidence));
  }

  /**
   * Apply exponential smoothing to distance
   */
  private applySmoothing(currentDistance: number): number {
    if (this.history.length < 2 || this.config.smoothingFactor === 0) {
      return currentDistance;
    }

    const previousDistance = this.history[this.history.length - 2]?.distance || currentDistance;
    const alpha = this.config.smoothingFactor;

    return alpha * currentDistance + (1 - alpha) * previousDistance;
  }

  /**
   * Calculate confidence for rate measurement
   */
  private calculateRateConfidence(
    currentDistance: number,
    previousDistance: number,
    dt: number
  ): number {
    if (dt <= 0) return 0;

    const rate = Math.abs(currentDistance - previousDistance) / dt;

    // Lower confidence for very high rates (potentially noisy)
    if (rate > 100) return 0.3;
    if (rate > 50) return 0.5;
    if (rate > 10) return 0.7;
    if (rate > 1) return 0.85;
    return 0.95;
  }

  /**
   * Generate execution trace
   */
  private generateTrace(
    input: OriginMetricInput,
    output: OriginMetricOutput,
    duration: number
  ): string {
    const origin = input.origin || { x: 0, y: 0, z: 0 };
    const lines = [
      `OriginMetricTile Execution Trace`,
      `ID: ${this.id}`,
      `Timestamp: ${new Date().toISOString()}`,
      `Duration: ${duration}ms`,
      ``,
      `Input:`,
      `  Position: (${input.position.x}, ${input.position.y}, ${input.position.z})`,
      `  Origin: (${origin.x}, ${origin.y}, ${origin.z})`,
      ``,
      `Output:`,
      `  Distance: ${output.distance.toFixed(4)}`,
      `  Rate: ${output.rateOfChange.value.toFixed(4)} units/sec`,
      `  Acceleration: ${output.rateOfChange.acceleration.toFixed(4)} units/sec²`,
      `  Confidence: ${(output.confidence * 100).toFixed(1)}%`,
      ``,
      `Anomalies:`,
      `  Sudden Change: ${output.anomalies.suddenChange ? 'YES' : 'no'}`,
      `  Accelerating: ${output.anomalies.acceleratingChange ? 'YES' : 'no'}`,
      `  Oscillating: ${output.anomalies.oscillating ? 'YES' : 'no'}`,
      ``,
      `History: ${this.history.length} entries`,
    ];

    return lines.join('\n');
  }

  /**
   * Get error output
   */
  private getErrorOutput(): OriginMetricOutput {
    return {
      distance: 0,
      rateOfChange: {
        value: 0,
        acceleration: 0,
        timestamp: Date.now(),
        confidence: 0,
      },
      history: [],
      anomalies: {
        suddenChange: false,
        acceleratingChange: false,
        oscillating: false,
      },
      confidence: 0,
    };
  }

  /**
   * Validate input
   */
  validateInput(input: unknown): input is OriginMetricInput {
    if (!input || typeof input !== 'object') return false;

    const obj = input as Record<string, unknown>;

    // Check position
    const position = obj.position;
    if (!position || typeof position !== 'object') return false;
    const pos = position as Record<string, unknown>;
    if (typeof pos.x !== 'number' || typeof pos.y !== 'number' || typeof pos.z !== 'number') {
      return false;
    }

    // Check optional origin
    if (obj.origin !== undefined) {
      const origin = obj.origin;
      if (!origin || typeof origin !== 'object') return false;
      const org = origin as Record<string, unknown>;
      if (typeof org.x !== 'number' || typeof org.y !== 'number' || typeof org.z !== 'number') {
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
      lastUpdate: this.history.length > 0 ? this.history[this.history.length - 1].timestamp : null,
    };
  }

  /**
   * Deserialize tile state
   */
  deserialize(data: Record<string, unknown>): void {
    // Note: In a real implementation, this would restore history and config
    // For simplicity, we just update the ID if provided
    if (data.id && typeof data.id === 'string') {
      (this as any).id = data.id;
    }
  }
}

/**
 * Factory function to create OriginMetricTile
 */
export function createOriginMetricTile(
  config?: Partial<OriginMetricConfig>
): OriginMetricTile {
  return new OriginMetricTile(config);
}