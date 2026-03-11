/**
 * CompoundRateTile: Combines multiple rate vectors
 *
 * This tile combines multiple rate vectors from different sources into a
 * unified compound rate with confidence-weighted aggregation.
 *
 * Based on SuperInstance white paper: "Rate-Based Change Mechanics"
 */

import { Tile, TileResult, classifyZone } from '../core/Tile';
import { RateVector, Vector3D } from '../../../superinstance/types/base';

/**
 * Input rate source for CompoundRateTile
 */
export interface RateSource {
  // Source identifier
  id: string;

  // Rate vector from this source
  rateVector: RateVector;

  // Position in space (optional, for spatial weighting)
  position?: Vector3D;

  // Weight for this source (0-1, defaults to confidence)
  weight?: number;

  // Metadata about the source
  metadata?: {
    type: string;
    reliability: number; // 0-1
    freshness: number; // 0-1, how recent is this data
  };
}

/**
 * Input for CompoundRateTile
 */
export interface CompoundRateInput {
  // Multiple rate sources to combine
  sources: RateSource[];

  // Reference point for spatial weighting (optional)
  referencePoint?: Vector3D;

  // Configuration
  config?: {
    aggregationMethod?: 'weighted_average' | 'confidence_weighted' | 'spatial_weighted';
    minSources?: number;
    outlierThreshold?: number;
    spatialDecay?: number; // Exponential decay for spatial distance
  };
}

/**
 * Output from CompoundRateTile
 */
export interface CompoundRateOutput {
  // Combined rate vector
  compoundRate: RateVector;

  // Source contributions
  contributions: Array<{
    sourceId: string;
    weight: number;
    contribution: number;
    distance?: number; // Spatial distance if reference point provided
  }>;

  // Quality metrics
  quality: {
    sourceCount: number;
    effectiveSources: number; // After outlier removal
    consensus: number; // 0-1, how much sources agree
    reliability: number; // 0-1, overall reliability
  };

  // Outlier detection
  outliers: Array<{
    sourceId: string;
    reason: 'high_deviation' | 'low_confidence' | 'stale_data';
    deviation: number;
  }>;

  // Confidence in compound rate
  confidence: number;
}

/**
 * CompoundRateTile Configuration
 */
export interface CompoundRateConfig {
  id: string;
  aggregationMethod: 'weighted_average' | 'confidence_weighted' | 'spatial_weighted';
  minSources: number;
  outlierThreshold: number; // Standard deviations for outlier detection
  spatialDecay: number; // Exponential decay constant for spatial weighting
  minConfidence: number; // Minimum confidence to include source
  maxAge: number; // Maximum age in ms for source data
}

/**
 * CompoundRateTile - Combines multiple rate vectors
 */
export class CompoundRateTile implements Tile<CompoundRateInput, CompoundRateOutput> {
  readonly id: string;
  readonly type = 'compound_rate';
  readonly version = '1.0.0';

  private config: CompoundRateConfig;

  constructor(config: Partial<CompoundRateConfig> = {}) {
    this.id = config.id || `compound_rate_${Date.now()}`;
    this.config = {
      id: this.id,
      aggregationMethod: 'confidence_weighted',
      minSources: 2,
      outlierThreshold: 2.0,
      spatialDecay: 0.1,
      minConfidence: 0.3,
      maxAge: 30000, // 30 seconds
      ...config,
    };
  }

  /**
   * Execute the tile
   */
  async execute(input: CompoundRateInput): Promise<TileResult<CompoundRateOutput>> {
    const startTime = Date.now();

    try {
      // Validate inputs
      if (input.sources.length < this.config.minSources) {
        throw new Error(`Insufficient sources: ${input.sources.length} < ${this.config.minSources}`);
      }

      // Filter and validate sources
      const validSources = this.filterValidSources(input.sources);
      if (validSources.length < this.config.minSources) {
        throw new Error(`Insufficient valid sources: ${validSources.length} < ${this.config.minSources}`);
      }

      // Calculate weights for each source
      const weightedSources = this.calculateWeights(validSources, input.referencePoint);

      // Detect outliers
      const { inliers, outliers } = this.detectOutliers(weightedSources);

      // Calculate compound rate
      const compoundRate = this.calculateCompoundRate(inliers);

      // Calculate source contributions
      const contributions = this.calculateContributions(inliers, compoundRate.value);

      // Calculate quality metrics
      const quality = this.calculateQualityMetrics(inliers, outliers);

      // Calculate overall confidence
      const confidence = this.calculateConfidence(compoundRate, quality, outliers.length);

      const output: CompoundRateOutput = {
        compoundRate,
        contributions,
        quality,
        outliers,
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
          totalSources: input.sources.length,
          validSources: validSources.length,
          inliers: inliers.length,
          referencePoint: input.referencePoint,
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
   * Filter valid sources based on confidence and age
   */
  private filterValidSources(sources: RateSource[]): RateSource[] {
    const now = Date.now();
    return sources.filter(source => {
      // Check confidence
      if (source.rateVector.confidence < this.config.minConfidence) {
        return false;
      }

      // Check age
      const age = now - source.rateVector.timestamp;
      if (age > this.config.maxAge) {
        return false;
      }

      return true;
    });
  }

  /**
   * Calculate weights for each source
   */
  private calculateWeights(
    sources: RateSource[],
    referencePoint?: Vector3D
  ): Array<RateSource & { weight: number; distance?: number }> {
    return sources.map(source => {
      let weight = source.weight ?? source.rateVector.confidence;

      // Apply spatial weighting if reference point provided
      if (referencePoint && source.position) {
        const distance = this.calculateDistance(source.position, referencePoint);
        const spatialWeight = Math.exp(-this.config.spatialDecay * distance);
        weight *= spatialWeight;

        return {
          ...source,
          weight,
          distance,
        };
      }

      return {
        ...source,
        weight,
      };
    });
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
   * Detect outliers using statistical methods
   */
  private detectOutliers(
    sources: Array<RateSource & { weight: number }>
  ): {
    inliers: Array<RateSource & { weight: number }>;
    outliers: CompoundRateOutput['outliers'];
  } {
    if (sources.length < 3) {
      return {
        inliers: sources,
        outliers: [],
      };
    }

    // Calculate weighted mean and standard deviation
    const rates = sources.map(s => s.rateVector.value);
    const weights = sources.map(s => s.weight);
    const mean = this.weightedMean(rates, weights);
    const stdDev = this.weightedStandardDeviation(rates, weights, mean);

    const inliers: Array<RateSource & { weight: number }> = [];
    const outliers: CompoundRateOutput['outliers'] = [];

    for (let i = 0; i < sources.length; i++) {
      const source = sources[i];
      const rate = source.rateVector.value;
      const deviation = Math.abs(rate - mean);

      // Check for statistical outlier
      if (stdDev > 0 && deviation > this.config.outlierThreshold * stdDev) {
        outliers.push({
          sourceId: source.id,
          reason: 'high_deviation',
          deviation: deviation / stdDev,
        });
        continue;
      }

      // Check for low confidence
      if (source.rateVector.confidence < this.config.minConfidence * 2) {
        outliers.push({
          sourceId: source.id,
          reason: 'low_confidence',
          deviation: deviation / (stdDev || 1),
        });
        continue;
      }

      // Check for stale data
      const age = Date.now() - source.rateVector.timestamp;
      if (age > this.config.maxAge * 0.5) {
        outliers.push({
          sourceId: source.id,
          reason: 'stale_data',
          deviation: deviation / (stdDev || 1),
        });
        continue;
      }

      inliers.push(source);
    }

    return { inliers, outliers };
  }

  /**
   * Calculate weighted mean
   */
  private weightedMean(values: number[], weights: number[]): number {
    let sum = 0;
    let weightSum = 0;

    for (let i = 0; i < values.length; i++) {
      sum += values[i] * weights[i];
      weightSum += weights[i];
    }

    return weightSum > 0 ? sum / weightSum : 0;
  }

  /**
   * Calculate weighted standard deviation
   */
  private weightedStandardDeviation(
    values: number[],
    weights: number[],
    mean: number
  ): number {
    let varianceSum = 0;
    let weightSum = 0;

    for (let i = 0; i < values.length; i++) {
      const deviation = values[i] - mean;
      varianceSum += weights[i] * deviation * deviation;
      weightSum += weights[i];
    }

    return weightSum > 0 ? Math.sqrt(varianceSum / weightSum) : 0;
  }

  /**
   * Calculate compound rate from inliers
   */
  private calculateCompoundRate(
    inliers: Array<RateSource & { weight: number }>
  ): RateVector {
    if (inliers.length === 0) {
      return {
        value: 0,
        acceleration: 0,
        timestamp: Date.now(),
        confidence: 0,
      };
    }

    // Calculate weighted average of rates
    const rates = inliers.map(s => s.rateVector.value);
    const weights = inliers.map(s => s.weight);
    const weightedRate = this.weightedMean(rates, weights);

    // Calculate weighted average of accelerations
    const accelerations = inliers.map(s => s.rateVector.acceleration);
    const weightedAcceleration = this.weightedMean(accelerations, weights);

    // Calculate weighted average confidence
    const confidences = inliers.map(s => s.rateVector.confidence);
    const weightedConfidence = this.weightedMean(confidences, weights);

    // Use latest timestamp
    const latestTimestamp = Math.max(...inliers.map(s => s.rateVector.timestamp));

    return {
      value: weightedRate,
      acceleration: weightedAcceleration,
      timestamp: latestTimestamp,
      confidence: weightedConfidence,
    };
  }

  /**
   * Calculate source contributions
   */
  private calculateContributions(
    sources: Array<RateSource & { weight: number }>,
    compoundRate: number
  ): CompoundRateOutput['contributions'] {
    return sources.map(source => {
      const contribution = source.weight * source.rateVector.value;
      const normalizedContribution = compoundRate !== 0
        ? contribution / (Math.abs(compoundRate) * sources.reduce((sum, s) => sum + s.weight, 0))
        : 0;

      return {
        sourceId: source.id,
        weight: source.weight,
        contribution: normalizedContribution,
        distance: (source as any).distance,
      };
    });
  }

  /**
   * Calculate quality metrics
   */
  private calculateQualityMetrics(
    inliers: Array<RateSource & { weight: number }>,
    outliers: CompoundRateOutput['outliers']
  ): CompoundRateOutput['quality'] {
    const sourceCount = inliers.length + outliers.length;

    // Calculate consensus (inverse of rate variance)
    const rates = inliers.map(s => s.rateVector.value);
    const mean = rates.reduce((sum, r) => sum + r, 0) / rates.length;
    const variance = rates.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / rates.length;
    const consensus = variance > 0 ? 1 / (1 + Math.sqrt(variance)) : 1;

    // Calculate reliability (weighted average of source reliabilities)
    let reliability = 0;
    let totalWeight = 0;

    for (const source of inliers) {
      const sourceReliability = source.metadata?.reliability ?? source.rateVector.confidence;
      reliability += source.weight * sourceReliability;
      totalWeight += source.weight;
    }

    reliability = totalWeight > 0 ? reliability / totalWeight : 0;

    return {
      sourceCount,
      effectiveSources: inliers.length,
      consensus: Math.max(0, Math.min(1, consensus)),
      reliability: Math.max(0, Math.min(1, reliability)),
    };
  }

  /**
   * Calculate overall confidence
   */
  private calculateConfidence(
    compoundRate: RateVector,
    quality: CompoundRateOutput['quality'],
    outlierCount: number
  ): number {
    let confidence = compoundRate.confidence;

    // Adjust based on quality metrics
    confidence = confidence * 0.5 + quality.consensus * 0.3 + quality.reliability * 0.2;

    // Penalize for outliers
    const outlierRatio = outlierCount / (quality.sourceCount || 1);
    confidence *= (1 - outlierRatio * 0.5);

    // Penalize for few sources
    if (quality.effectiveSources < 3) {
      confidence *= 0.8;
    }
    if (quality.effectiveSources < 2) {
      confidence *= 0.7;
    }

    return Math.max(0.1, Math.min(1, confidence));
  }

  /**
   * Generate execution trace
   */
  private generateTrace(
    input: CompoundRateInput,
    output: CompoundRateOutput,
    duration: number
  ): string {
    const lines = [
      `CompoundRateTile Execution Trace`,
      `ID: ${this.id}`,
      `Timestamp: ${new Date().toISOString()}`,
      `Duration: ${duration}ms`,
      ``,
      `Input Summary:`,
      `  Total Sources: ${input.sources.length}`,
      `  Reference Point: ${input.referencePoint ? 'provided' : 'not provided'}`,
      `  Aggregation Method: ${this.config.aggregationMethod}`,
      ``,
      `Compound Rate:`,
      `  Value: ${output.compoundRate.value.toFixed(4)}`,
      `  Acceleration: ${output.compoundRate.acceleration.toFixed(4)}`,
      `  Confidence: ${(output.compoundRate.confidence * 100).toFixed(1)}%`,
      `  Timestamp: ${new Date(output.compoundRate.timestamp).toISOString()}`,
      ``,
      `Quality Metrics:`,
      `  Source Count: ${output.quality.sourceCount}`,
      `  Effective Sources: ${output.quality.effectiveSources}`,
      `  Consensus: ${(output.quality.consensus * 100).toFixed(1)}%`,
      `  Reliability: ${(output.quality.reliability * 100).toFixed(1)}%`,
      ``,
      `Outliers: ${output.outliers.length}`,
    ];

    if (output.outliers.length > 0) {
      lines.push(``, `Outlier Details:`);
      for (const outlier of output.outliers) {
        lines.push(`  ${outlier.sourceId}: ${outlier.reason} (deviation: ${outlier.deviation.toFixed(2)}σ)`);
      }
    }

    lines.push(
      ``,
      `Contributions:`,
      `  Total Weight: ${output.contributions.reduce((sum, c) => sum + c.weight, 0).toFixed(3)}`
    );

    for (const contribution of output.contributions.slice(0, 5)) {
      lines.push(
        `  ${contribution.sourceId}: weight=${contribution.weight.toFixed(3)}, ` +
        `contribution=${(contribution.contribution * 100).toFixed(1)}%` +
        (contribution.distance !== undefined ? `, distance=${contribution.distance.toFixed(2)}` : '')
      );
    }

    if (output.contributions.length > 5) {
      lines.push(`  ... and ${output.contributions.length - 5} more`);
    }

    lines.push(
      ``,
      `Overall Confidence: ${(output.confidence * 100).toFixed(1)}%`,
      `Zone: ${classifyZone(output.confidence)}`
    );

    return lines.join('\n');
  }

  /**
   * Get error output
   */
  private getErrorOutput(): CompoundRateOutput {
    return {
      compoundRate: {
        value: 0,
        acceleration: 0,
        timestamp: Date.now(),
        confidence: 0,
      },
      contributions: [],
      quality: {
        sourceCount: 0,
        effectiveSources: 0,
        consensus: 0,
        reliability: 0,
      },
      outliers: [],
      confidence: 0,
    };
  }

  /**
   * Validate input
   */
  validateInput(input: unknown): input is CompoundRateInput {
    if (!input || typeof input !== 'object') return false;

    const obj = input as Record<string, unknown>;

    // Check sources
    if (!Array.isArray(obj.sources)) return false;
    if (obj.sources.length < this.config.minSources) return false;

    for (const source of obj.sources) {
      if (!this.validateRateSource(source)) return false;
    }

    // Check optional reference point
    if (obj.referencePoint !== undefined) {
      const ref = obj.referencePoint;
      if (!ref || typeof ref !== 'object') return false;
      const refObj = ref as Record<string, unknown>;
      if (typeof refObj.x !== 'number' || typeof refObj.y !== 'number' || typeof refObj.z !== 'number') {
        return false;
      }
    }

    return true;
  }

  /**
   * Validate a rate source
   */
  private validateRateSource(source: unknown): source is RateSource {
    if (!source || typeof source !== 'object') return false;

    const obj = source as Record<string, unknown>;

    // Check id
    if (typeof obj.id !== 'string') return false;

    // Check rateVector
    if (!obj.rateVector || typeof obj.rateVector !== 'object') return false;
    const rateVec = obj.rateVector as Record<string, unknown>;
    if (typeof rateVec.value !== 'number' || typeof rateVec.acceleration !== 'number' ||
        typeof rateVec.timestamp !== 'number' || typeof rateVec.confidence !== 'number') {
      return false;
    }

    // Check optional position
    if (obj.position !== undefined) {
      const pos = obj.position;
      if (!pos || typeof pos !== 'object') return false;
      const posObj = pos as Record<string, unknown>;
      if (typeof posObj.x !== 'number' || typeof posObj.y !== 'number' || typeof posObj.z !== 'number') {
        return false;
      }
    }

    // Check optional weight
    if (obj.weight !== undefined && typeof obj.weight !== 'number') {
      return false;
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
    };
  }

  /**
   * Deserialize tile state
   */
  deserialize(data: Record<string, unknown>): void {
    // Note: In a real implementation, this would restore state
    // For simplicity, we just update the ID if provided
    if (data.id && typeof data.id === 'string') {
      (this as any).id = data.id;
    }
  }
}

/**
 * Factory function to create CompoundRateTile
 */
export function createCompoundRateTile(
  config?: Partial<CompoundRateConfig>
): CompoundRateTile {
  return new CompoundRateTile(config);
}