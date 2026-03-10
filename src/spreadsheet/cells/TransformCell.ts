/**
 * POLLN Spreadsheet Integration - TransformCell
 *
 * TransformCell applies various transformations to input data.
 * Supports: map, filter, reduce, flatMap, sort, reverse, slice, split, merge, transpose, zip
 *
 * Logic Level: L0-L1 (computation + simple patterns)
 */

import { LogCell, LogCellConfig } from '../core/LogCell.js';
import { CellType, CellState, LogicLevel, CellOutput, ProcessingResult, ProcessingContext, ReasoningStep, ReasoningStepType } from '../core/types.js';
import { v4 as uuidv4 } from 'uuid';

/**
 * Simple transform result interface
 */
interface TransformResult {
  success: boolean;
  value: unknown;
  timestamp: number;
  duration?: number;
  error?: string;
}

/**
 * Transformation types supported by TransformCell
 */
export enum TransformType {
  MAP = 'map',           // Apply function to each element
  FILTER = 'filter',       // Filter elements (subset of map)
  REDUCE = 'reduce',       // Reduce to single value
  FLAT_MAP = 'flat_map',   // Flatten then map
  SORT = 'sort',           // Sort elements
  REVERSE = 'reverse',     // Reverse order
  SLICE = 'slice',         // Extract portion
  SPLIT = 'split',         // Split into parts
  MERGE = 'merge',         // Merge multiple inputs
  TRANSPOSE = 'transpose', // Transpose dimensions
  ZIP = 'zip',             // Combine arrays element-wise
}

/**
 * Transformation function type
 */
export type TransformFunction = (input: unknown, index?: number, array?: unknown[]) => unknown;

/**
 * Configuration for TransformCell
 */
export interface TransformCellConfig extends LogCellConfig {
  transformType: TransformType;
  transformFn?: TransformFunction;
}

/**
 * TransformCell - Transforms data using various operations
 *
 * Responsibilities:
 * - Apply transformations to input data
 * - Support map, filter, reduce, etc.
 * - Chain multiple transformations
 * - Preserve transformation history
 *
 * Logic Level: L0-L1 (computation + simple patterns)
 */
export class TransformCell extends LogCell {
  private transformType: TransformType;
  private transformFn?: TransformFunction;
  private transformHistory: Array<{ input: unknown; output: unknown; timestamp: number }> = [];

  constructor(config: TransformCellConfig) {
    super({
      type: CellType.TRANSFORM,
      position: config.position,
      logicLevel: LogicLevel.L1_PATTERN,
      memoryLimit: config.memoryLimit,
    });

    this.transformType = config.transformType;
    this.transformFn = config.transformFn;
  }

  /**
   * Transform input data
   */
  async transform(input: unknown): Promise<TransformResult> {
    this.state = CellState.PROCESSING;
    const startTime = Date.now();

    try {
      let output: unknown;

      switch (this.transformType) {
        case TransformType.MAP:
          output = await this.applyMap(input);
          break;
        case TransformType.FILTER:
          output = await this.applyFilter(input);
          break;
        case TransformType.REDUCE:
          output = await this.applyReduce(input);
          break;
        case TransformType.FLAT_MAP:
          output = await this.applyFlatMap(input);
          break;
        case TransformType.SORT:
          output = await this.applySort(input);
          break;
        case TransformType.REVERSE:
          output = await this.applyReverse(input);
          break;
        case TransformType.SLICE:
          output = await this.applySlice(input);
          break;
        case TransformType.SPLIT:
          output = await this.applySplit(input);
          break;
        case TransformType.MERGE:
          output = await this.applyMerge(input);
          break;
        case TransformType.TRANSPOSE:
          output = this.applyTranspose(input);
          break;
        case TransformType.ZIP:
          output = this.applyZip(input);
          break;
        default:
          throw new Error(`Unknown transform type: ${this.transformType}`);
      }

      this.state = CellState.EMITTING;
      this.transformHistory.push({
        input,
        output,
        timestamp: Date.now(),
      });

      return {
        success: true,
        value: output,
        timestamp: Date.now(),
        duration: Date.now() - startTime,
      };
    } catch (error) {
      this.state = CellState.ERROR;
      return {
        success: false,
        value: null,
        error: error instanceof Error ? error.message : 'Transform failed',
        timestamp: Date.now(),
      };
    }
  }

  // ========================================================================
  // Transformation Implementations
  // ========================================================================

  /**
   * Apply map transformation
   */
  private async applyMap(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('Map transform requires array input');
    }

    if (this.transformFn) {
      return input.map((item, index) => this.transformFn!(item, index, input));
    }

    return input; // Identity if no function
  }

  /**
   * Apply filter transformation
   */
  private async applyFilter(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('Filter transform requires array input');
    }

    if (this.transformFn) {
      return input.filter((item, index) => this.transformFn!(item, index, input) as boolean);
    }

    return input; // No filter, return all
  }

  /**
   * Apply reduce transformation
   */
  private async applyReduce(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('Reduce transform requires array input');
    }

    if (!this.transformFn) {
      throw new Error('Reduce transform requires transformFn');
    }

    return input.reduce((acc, item, index) => {
      const result = this.transformFn!(item, index, input);
      return this.mergeReduceResult(acc, result);
    });
  }

  /**
   * Merge reduce results
   */
  private mergeReduceResult(acc: unknown, result: unknown): unknown {
    if (typeof acc === 'number' && typeof result === 'number') {
      return acc + result;
    }
    if (Array.isArray(acc) && Array.isArray(result)) {
      return [...acc, ...result];
    }
    if (typeof acc === 'object' && typeof result === 'object') {
      return { ...acc, ...result };
    }
    return result;
  }

  /**
   * Apply flatMap transformation
   */
  private async applyFlatMap(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('FlatMap transform requires array input');
    }

    if (!this.transformFn) {
      return input.flat(Infinity);
    }

    return input.flatMap((item, index) => {
      const result = this.transformFn!(item, index, input);
      return Array.isArray(result) ? result : [result];
    });
  }

  /**
   * Apply sort transformation
   */
  private async applySort(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('Sort transform requires array input');
    }

    const sorted = [...input];

    if (this.transformFn) {
      // Custom sort using transformFn as comparator
      return sorted.sort((a, b) => {
        const aVal = this.transformFn!(a);
        const bVal = this.transformFn!(b);
        if (aVal < bVal) return -1;
        if (aVal > bVal) return 1;
        return 0;
      });
    }

    // Default: natural sort
    return sorted.sort();
  }

  /**
   * Apply reverse transformation
   */
  private async applyReverse(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('Reverse transform requires array input');
    }

    return [...input].reverse();
  }

  /**
   * Apply slice transformation
   */
  private async applySlice(input: unknown): Promise<unknown> {
    if (!Array.isArray(input)) {
      throw new Error('Slice transform requires array input');
    }

    if (!this.transformFn) {
      throw new Error('Slice transform requires transformFn with [start, end]');
    }

    const [start, end] = this.transformFn!(input) as [number, number];
    return input.slice(start, end);
  }

  /**
   * Apply split transformation
   */
  private async applySplit(input: unknown): Promise<unknown> {
    if (typeof input !== 'string' && !Array.isArray(input)) {
      throw new Error('Split transform requires string or array input');
    }

    if (typeof input === 'string') {
      if (!this.transformFn) {
        return input.split('');
      }
      const delimiter = this.transformFn!(input) as string;
      return input.split(delimiter);
    }

    // Array split: split array into chunks
    if (!this.transformFn) {
      throw new Error('Split transform requires transformFn with chunk size');
    }

    const chunkSize = this.transformFn!(input) as number;
    const chunks: unknown[][] = [];
    for (let i = 0; i < input.length; i += chunkSize) {
      chunks.push(input.slice(i, i + chunkSize));
    }
    return chunks;
  }

  /**
   * Apply merge transformation
   */
  private async applyMerge(input: unknown): Promise<unknown> {
    if (!this.transformFn) {
      throw new Error('Merge transform requires transformFn with merge strategy');
    }

    const strategy = this.transformFn!(input) as string;

    if (Array.isArray(input)) {
      switch (strategy) {
        case 'flatten':
          return input.flat(Infinity);
        case 'concat':
          return input.flat();
        case 'unique':
          return Array.from(new Set(input.flat()));
        default:
          return input;
      }
    }

    if (typeof input === 'object' && input !== null) {
      const keys = Object.keys(input);
      const merged: unknown[] = [];
      for (const key of keys) {
        merged.push((input as Record<string, unknown>)[key]);
      }
      return merged;
    }

    return input;
  }

  /**
   * Apply transpose transformation
   */
  private applyTranspose(input: unknown): unknown {
    if (!Array.isArray(input)) {
      throw new Error('Transpose transform requires array input');
    }

    if (input.length === 0) {
      return [];
    }

    // Check if it's a 2D array
    if (!Array.isArray(input[0])) {
      return input;
    }

    // Transpose 2D array
    const rows = input.length;
    const cols = (input[0] as unknown[]).length;
    const transposed: unknown[][] = [];

    for (let j = 0; j < cols; j++) {
      transposed[j] = [];
      for (let i = 0; i < rows; i++) {
        transposed[j][i] = (input[i] as unknown[])[j];
      }
    }

    return transposed;
  }

  /**
   * Apply zip transformation
   */
  private applyZip(input: unknown): unknown {
    if (!Array.isArray(input)) {
      throw new Error('Zip transform requires array input');
    }

    if (!this.transformFn) {
      throw new Error('Zip transform requires transformFn with arrays to zip');
    }

    const otherArrays = this.transformFn!(input) as unknown[][];
    const arrays = [input, ...otherArrays];
    const maxLength = Math.max(...arrays.map(arr => arr.length));
    const zipped: unknown[] = [];

    for (let i = 0; i < maxLength; i++) {
      const tuple: unknown[] = [];
      for (const arr of arrays) {
        tuple.push(arr[i] ?? null);
      }
      zipped.push(tuple);
    }

    return zipped;
  }

  // ========================================================================
  // Abstract Method Implementations
  // ========================================================================

  /**
   * Activate the cell
   */
  async activate(): Promise<void> {
    this.state = CellState.SENSING;
  }

  /**
   * Process input using transform
   */
  async process(input: unknown): Promise<CellOutput> {
    const result = await this.transform(input);

    // Create a reasoning step
    const step: ReasoningStep = {
      id: uuidv4(),
      type: ReasoningStepType.ANALYSIS,
      description: `Applied ${this.transformType} transform`,
      input,
      output: result.value,
      confidence: result.success ? 1.0 : 0.0,
      duration: result.duration || 0,
      timestamp: result.timestamp,
      dependencies: [],
    };

    // Convert TransformResult to CellOutput format
    return {
      value: result.value,
      confidence: result.success ? 1.0 : 0.0,
      explanation: result.error || `Applied ${this.transformType} transform`,
      trace: {
        steps: [step],
        dependencies: [],
        confidence: result.success ? 1.0 : 0.0,
        totalTime: result.duration || 0,
        startTime: result.timestamp - (result.duration || 0),
        endTime: result.timestamp,
      },
      effects: [],
    };
  }

  /**
   * Learn from feedback
   */
  async learn(feedback: unknown): Promise<void> {
    // For transform cells, learning could involve:
    // - Adjusting transform function based on feedback
    // - Learning optimal slice parameters
    // - Improving sort comparators
    // For now, this is a placeholder
    if (typeof feedback === 'object' && feedback !== null) {
      const fb = feedback as Record<string, unknown>;
      if (fb.adjustTransformFn && typeof fb.adjustTransformFn === 'function') {
        this.transformFn = fb.adjustTransformFn as TransformFunction;
      }
    }
  }

  /**
   * Deactivate the cell
   */
  async deactivate(): Promise<void> {
    this.state = CellState.DORMANT;
  }

  /**
   * Execute processing (required by LogCell)
   */
  protected async executeProcessing(
    input: unknown,
    context: ProcessingContext
  ): Promise<ProcessingResult> {
    const result = await this.transform(input);

    // Create a reasoning step
    const step: ReasoningStep = {
      id: uuidv4(),
      type: ReasoningStepType.ANALYSIS,
      description: `Applied ${this.transformType} transform`,
      input,
      output: result.value,
      confidence: result.success ? 1.0 : 0.0,
      duration: result.duration || 0,
      timestamp: result.timestamp,
      dependencies: [],
    };

    return {
      value: result.value,
      confidence: result.success ? 1.0 : 0.0,
      explanation: result.error || `Applied ${this.transformType} transform`,
      trace: {
        steps: [step],
        dependencies: [],
        confidence: result.success ? 1.0 : 0.0,
        totalTime: result.duration || 0,
        startTime: result.timestamp - (result.duration || 0),
        endTime: result.timestamp,
      },
    };
  }

  // ========================================================================
  // Utility Methods
  // ========================================================================

  /**
   * Get transform history
   */
  getTransformHistory(): Array<{ input: unknown; output: unknown; timestamp: number }> {
    return [...this.transformHistory];
  }

  /**
   * Get current transform type
   */
  getTransformType(): TransformType {
    return this.transformType;
  }

  /**
   * Set transform function
   */
  setTransformFn(fn: TransformFunction): void {
    this.transformFn = fn;
  }

  /**
   * Get transform function
   */
  getTransformFn(): TransformFunction | undefined {
    return this.transformFn;
  }

  /**
   * Clear transform history
   */
  clearHistory(): void {
    this.transformHistory = [];
  }

  /**
   * Create the processing logic for this cell
   */
  protected createProcessingLogic(): any {
    return {
      type: 'transform',
      transformType: this.transformType,
      logic: this.logicLevel,
    };
  }
}