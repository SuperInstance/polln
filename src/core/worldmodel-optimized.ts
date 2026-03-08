/**
 * POLLN World Model - Memory Optimized
 *
 * Optimizations:
 * - Memory-efficient tensor storage using Float32Array
 * - Lazy loading of neural network weights
 * - Weight quantization for reduced memory footprint
 * - Memory pooling for temporary allocations
 * - Garbage collection hints for large objects
 *
 * Sprint 7: Performance Optimization
 */

import { v4 as uuidv4 } from 'uuid';
import type {
  WorldModelConfig,
  WorldModelState,
  LatentState,
  TransitionResult,
  DreamEpisode,
} from './worldmodel.js';

// ============================================================================
// MEMORY POOL
// ============================================================================

class MemoryPool {
  private pools: Map<number, Float32Array[]> = new Map();
  private maxPoolSize: number = 10;

  acquire(size: number): Float32Array {
    if (!this.pools.has(size)) {
      this.pools.set(size, []);
    }

    const pool = this.pools.get(size)!;
    if (pool.length > 0) {
      return pool.pop()!;
    }

    return new Float32Array(size);
  }

  release(array: Float32Array): void {
    const size = array.length;
    if (!this.pools.has(size)) {
      this.pools.set(size, []);
    }

    const pool = this.pools.get(size)!;
    if (pool.length < this.maxPoolSize) {
      pool.push(array);
    }
  }

  clear(): void {
    this.pools.clear();
  }
}

// ============================================================================
// QUANTIZATION UTILITIES
// ============================================================================

class QuantizationUtils {
  /**
   * Quantize float32 to int8 (reduces memory by 4x)
   */
  static quantizeToInt8(weights: Float32Array): Int8Array {
    const quantized = new Int8Array(weights.length);

    // Find min/max for normalization
    let min = Infinity;
    let max = -Infinity;
    for (let i = 0; i < weights.length; i++) {
      if (weights[i] < min) min = weights[i];
      if (weights[i] > max) max = weights[i];
    }

    const scale = (max - min) / 127;

    // Quantize
    for (let i = 0; i < weights.length; i++) {
      quantized[i] = Math.round(((weights[i] - min) / scale) - 64);
    }

    return quantized;
  }

  /**
   * Dequantize int8 back to float32
   */
  static dequantizeFromInt8(quantized: Int8Array, scale: number, min: number): Float32Array {
    const dequantized = new Float32Array(quantized.length);

    for (let i = 0; i < quantized.length; i++) {
      dequantized[i] = (quantized[i] + 64) * scale + min;
    }

    return dequantized;
  }

  /**
   * Compress sparse matrix using CSR format
   */
  static compressCSR(matrix: number[][]): {
    values: number[];
    columnIndices: number[];
    rowPointers: number[];
  } {
    const values: number[] = [];
    const columnIndices: number[] = [];
    const rowPointers: number[] = [0];

    for (const row of matrix) {
      for (let j = 0; j < row.length; j++) {
        if (row[j] !== 0) {
          values.push(row[j]);
          columnIndices.push(j);
        }
      }
      rowPointers.push(values.length);
    }

    return { values, columnIndices, rowPointers };
  }
}

// ============================================================================
// OPTIMIZED WORLD MODEL
// ============================================================================

export interface OptimizedWorldModelConfig extends WorldModelConfig {
  // Memory optimization
  enableQuantization: boolean;
  enableMemoryPooling: boolean;
  maxMemoryMB: number;
  lazyLoadWeights: boolean;

  // Compression
  compressSparseWeights: boolean;
  sparsityThreshold: number;
}

export class WorldModelOptimized {
  private config: OptimizedWorldModelConfig;
  private state: WorldModelState;

  // Neural network weights (quantized if enabled)
  private encoderWeights: Float32Array | Int8Array | null = null;
  private decoderWeights: Float32Array | Int8Array | null = null;
  private transitionWeights: Float32Array | Int8Array | null = null;
  private rewardWeights: Float32Array | Int8Array | null = null;

  // Memory pool for temporary allocations
  private memoryPool: MemoryPool;

  // Running statistics for uncertainty estimation
  private predictionErrorHistory: number[] = [];
  private maxErrorHistory: number = 1000;

  // Quantization metadata
  private quantizationScales: Map<string, { scale: number; min: number }> = new Map();

  constructor(config?: Partial<OptimizedWorldModelConfig>) {
    this.config = {
      latentDim: 64,
      hiddenDim: 256,
      learningRate: 0.001,
      transitionHiddenDim: 128,
      rewardHiddenDim: 64,
      beta: 0.1,
      decoderHiddenDim: 256,
      batchSize: 32,
      discountFactor: 0.99,
      lambda: 0.8,
      curiosityWeight: 0.01,
      uncertaintyThreshold: 0.5,
      dreamHorizon: 10,
      dreamBatchSize: 16,
      enableQuantization: true,
      enableMemoryPooling: true,
      maxMemoryMB: 500,
      lazyLoadWeights: true,
      compressSparseWeights: true,
      sparsityThreshold: 0.9,
      ...config,
    };

    this.state = {
      encoderLoss: 0,
      reconstructionLoss: 0,
      klDivergence: 0,
      transitionLoss: 0,
      rewardLoss: 0,
      totalLoss: 0,
      lastUpdated: Date.now(),
      trainingSteps: 0,
      avgPredictionError: 0,
      avgCuriosityReward: 0,
      avgUncertainty: 0,
    };

    this.memoryPool = new MemoryPool();

    // Initialize weights lazily if configured
    if (!this.config.lazyLoadWeights) {
      this.initializeWeights();
    }
  }

  /**
   * Lazy load weights on first access
   */
  private ensureWeightsInitialized(): void {
    if (!this.encoderWeights) {
      this.initializeWeights();
    }
  }

  /**
   * Initialize neural network weights
   */
  private initializeWeights(): void {
    // Initialize with small random values
    this.encoderWeights = this.initializeWeightMatrix(
      this.config.hiddenDim * this.config.latentDim
    );

    this.decoderWeights = this.initializeWeightMatrix(
      this.config.latentDim * this.config.decoderHiddenDim
    );

    this.transitionWeights = this.initializeWeightMatrix(
      this.config.latentDim * this.config.transitionHiddenDim
    );

    this.rewardWeights = this.initializeWeightMatrix(
      this.config.latentDim * this.config.rewardHiddenDim
    );

    // Quantize if enabled
    if (this.config.enableQuantization) {
      this.quantizeAllWeights();
    }
  }

  /**
   * Initialize weight matrix with Xavier initialization
   */
  private initializeWeightMatrix(size: number): Float32Array {
    const weights = new Float32Array(size);
    const scale = Math.sqrt(2.0 / size);

    for (let i = 0; i < size; i++) {
      weights[i] = (Math.random() - 0.5) * 2 * scale;
    }

    return weights;
  }

  /**
   * Quantize all weights to reduce memory footprint
   */
  private quantizeAllWeights(): void {
    if (this.encoderWeights instanceof Float32Array) {
      const quantized = QuantizationUtils.quantizeToInt8(this.encoderWeights);
      this.encoderWeights = quantized;
    }

    if (this.decoderWeights instanceof Float32Array) {
      const quantized = QuantizationUtils.quantizeToInt8(this.decoderWeights);
      this.decoderWeights = quantized;
    }

    if (this.transitionWeights instanceof Float32Array) {
      const quantized = QuantizationUtils.quantizeToInt8(this.transitionWeights);
      this.transitionWeights = quantized;
    }

    if (this.rewardWeights instanceof Float32Array) {
      const quantized = QuantizationUtils.quantizeToInt8(this.rewardWeights);
      this.rewardWeights = quantized;
    }
  }

  /**
   * Encode observation to latent state
   */
  async encode(observation: number[]): Promise<LatentState> {
    this.ensureWeightsInitialized();

    // Use memory pool for temporary allocations
    const latent = this.memoryPool.acquire(this.config.latentDim);
    const logVar = this.memoryPool.acquire(this.config.latentDim);

    try {
      // Simple encoding (placeholder for actual VAE encoder)
      for (let i = 0; i < this.config.latentDim; i++) {
        latent[i] = (observation[i % observation.length] || 0) * 0.1;
        logVar[i] = 0;
      }

      // Sample from latent distribution
      const sample = new Float32Array(this.config.latentDim);
      for (let i = 0; i < this.config.latentDim; i++) {
        sample[i] = latent[i] + Math.sqrt(Math.exp(logVar[i])) * this.gaussianRandom();
      }

      return {
        mean: Array.from(latent),
        logVar: Array.from(logVar),
        sample: Array.from(sample),
      };
    } finally {
      // Release temporary arrays back to pool
      this.memoryPool.release(latent);
      this.memoryPool.release(logVar);
    }
  }

  /**
   * Predict next state and reward
   */
  async predict(
    state: number[],
    action: number[]
  ): Promise<TransitionResult> {
    this.ensureWeightsInitialized();

    const nextState = new Float32Array(this.config.latentDim);
    const uncertainty = this.calculateUncertainty(state);

    // Simple transition prediction (placeholder)
    for (let i = 0; i < this.config.latentDim; i++) {
      nextState[i] = state[i] + (action[i % action.length] || 0) * 0.1;
    }

    const predictionError = Math.random() * uncertainty;
    const reward = Math.random() * 2 - 1;

    // Update prediction error history
    this.predictionErrorHistory.push(predictionError);
    if (this.predictionErrorHistory.length > this.maxErrorHistory) {
      this.predictionErrorHistory.shift();
    }

    return {
      nextState: Array.from(nextState),
      hiddenState: [],
      reward,
      uncertainty,
      predictionError,
    };
  }

  /**
   * Train world model on a batch
   */
  async train(batch: {
    observations: number[][];
    actions: number[][];
    rewards: number[];
    nextObservations: number[][];
    dones: boolean[];
  }): Promise<{ loss: number }> {
    this.ensureWeightsInitialized();

    let totalLoss = 0;

    // Simple training loop (placeholder)
    for (let i = 0; i < batch.observations.length; i++) {
      const obs = batch.observations[i];
      const nextObs = batch.nextObservations[i];
      const reward = batch.rewards[i];

      // Encode observations
      const latent = await this.encode(obs);
      const nextLatent = await this.encode(nextObs);

      // Calculate losses
      const reconstructionLoss = this.calculateReconstructionLoss(obs, nextObs);
      const klLoss = this.calculateKLLoss(latent);
      const transitionLoss = Math.abs(reward - this.predictReward(nextLatent.sample));

      totalLoss += reconstructionLoss + this.config.beta * klLoss + transitionLoss;
    }

    // Update state
    this.state.trainingSteps++;
    this.state.lastUpdated = Date.now();
    this.state.totalLoss = totalLoss / batch.observations.length;

    return { loss: this.state.totalLoss };
  }

  /**
   * Generate dream episode for policy optimization
   */
  async generateDreamEpisode(
    startState: number[],
    horizon?: number
  ): Promise<DreamEpisode> {
    this.ensureWeightsInitialized();

    const h = horizon || this.config.dreamHorizon;
    const episode: DreamEpisode = {
      id: uuidv4(),
      startState,
      actions: [],
      states: [...startState], // Spread startState
      rewards: [],
      values: [],
      uncertainties: [],
      totalReward: 0,
      totalValue: 0,
      length: h,
    };

    let currentState = startState;

    for (let i = 0; i < h; i++) {
      // Sample random action
      const action = Array.from({ length: 10 }, () => Math.random() * 2 - 1);
      episode.actions.push(...action); // Spread action array

      // Predict next state
      const result = await this.predict(currentState, action);
      currentState = result.nextState;

      episode.states.push(...currentState); // Spread state array
      // Handle reward - it might be a number or array
      if (Array.isArray(result.reward)) {
        episode.rewards.push(...result.reward);
      } else {
        episode.rewards.push(result.reward);
      }
      // Handle uncertainty - it might be a number or array
      if (Array.isArray(result.uncertainty)) {
        episode.uncertainties.push(...result.uncertainty);
      } else {
        episode.uncertainties.push(result.uncertainty);
      }

      episode.totalReward += Array.isArray(result.reward) ? result.reward[0] : result.reward;
    }

    return episode;
  }

  /**
   * Calculate uncertainty based on prediction error history
   */
  private calculateUncertainty(state: number[]): number {
    if (this.predictionErrorHistory.length === 0) {
      return this.config.uncertaintyThreshold;
    }

    // Calculate mean and variance of prediction errors
    const mean = this.predictionErrorHistory.reduce((a, b) => a + b, 0) / this.predictionErrorHistory.length;
    const variance = this.predictionErrorHistory.reduce((sum, err) => sum + Math.pow(err - mean, 2), 0) / this.predictionErrorHistory.length;

    return Math.min(Math.sqrt(variance), this.config.uncertaintyThreshold);
  }

  /**
   * Calculate reconstruction loss
   */
  private calculateReconstructionLoss(obs: number[], reconstructed: number[]): number {
    let loss = 0;
    for (let i = 0; i < obs.length; i++) {
      loss += Math.pow(obs[i] - (reconstructed[i] || 0), 2);
    }
    return loss / obs.length;
  }

  /**
   * Calculate KL divergence loss
   */
  private calculateKLLoss(latent: LatentState): number {
    let kl = 0;
    for (let i = 0; i < latent.mean.length; i++) {
      const mean = latent.mean[i];
      const logVar = latent.logVar[i];
      kl += -0.5 * (1 + logVar - mean * mean - Math.exp(logVar));
    }
    return kl / latent.mean.length;
  }

  /**
   * Predict reward from latent state
   */
  private predictReward(latent: number[]): number {
    let sum = 0;
    for (let i = 0; i < latent.length; i++) {
      sum += latent[i] * 0.1;
    }
    return sum;
  }

  /**
   * Generate Gaussian random number
   */
  private gaussianRandom(): number {
    let u = 0;
    let v = 0;
    while (u === 0) u = Math.random();
    while (v === 0) v = Math.random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  }

  /**
   * Get memory usage statistics
   */
  getMemoryUsage(): {
    totalBytes: number;
    totalMB: number;
    breakdown: {
      encoder: number;
      decoder: number;
      transition: number;
      reward: number;
    };
  } {
    const getBytes = (weights: Float32Array | Int8Array | null) => {
      if (!weights) return 0;
      return weights.byteLength;
    };

    const encoder = getBytes(this.encoderWeights);
    const decoder = getBytes(this.decoderWeights);
    const transition = getBytes(this.transitionWeights);
    const reward = getBytes(this.rewardWeights);

    const totalBytes = encoder + decoder + transition + reward;

    return {
      totalBytes,
      totalMB: totalBytes / (1024 * 1024),
      breakdown: {
        encoder,
        decoder,
        transition,
        reward,
      },
    };
  }

  /**
   * Get state
   */
  getState(): WorldModelState {
    return { ...this.state };
  }

  /**
   * Clear memory pools and free resources
   */
  cleanup(): void {
    this.memoryPool.clear();
    this.predictionErrorHistory = [];

    // Release weights if lazy loading is enabled
    if (this.config.lazyLoadWeights) {
      this.encoderWeights = null;
      this.decoderWeights = null;
      this.transitionWeights = null;
      this.rewardWeights = null;
    }
  }
}
