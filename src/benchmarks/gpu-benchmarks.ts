/**
 * GPU Benchmarks
 *
 * GPU vs CPU performance comparisons for compute operations
 */

import { performanceMonitor } from '../superinstance/performance/SuperInstancePerformanceMonitor';
import { BenchmarkConfig, BenchmarkResult } from './benchmark-runner';

// Mock GPU compute classes
class MockGPUProcessor {
  private available: boolean;
  private forceCPU: boolean = false;

  constructor() {
    this.available = Math.random() > 0.5; // Simulate GPU availability
  }

  isAvailable(): boolean {
    return this.available && !this.forceCPU;
  }

  forceCPU(value: boolean): void {
    this.forceCPU = value;
  }

  async processBatch(data: Float32Array, operation: string): Promise<{ result: Float32Array, executionTime: number, usedGPU: boolean }> {
    const start = performance.now();

    let result: Float32Array;

    if (this.isAvailable()) {
      // Simulate GPU processing (much faster)
      await new Promise(resolve => setTimeout(resolve, 1)); // 1ms for GPU
      result = this.processOnGPU(data, operation);
    } else {
      // Simulate CPU processing (slower)
      await new Promise(resolve => setTimeout(resolve, 10)); // 10ms for CPU
      result = this.processOnCPU(data, operation);
    }

    const end = performance.now();
    const executionTime = end - start;

    return { result, executionTime, usedGPU: this.isAvailable() };
  }

  private processOnGPU(data: Float32Array, operation: string): Float32Array {
    // Simulate GPU computation
    const result = new Float32Array(data.length);
    for (let i = 0; i < data.length; i++) {
      switch (operation) {
        case 'add':
          result[i] = data[i] + 1;
          break;
        case 'multiply':
          result[i] = data[i] * 2;
          break;
        case 'matrix_multiply':
          result[i] = data[i] * data[i];
          break;
        default:
          result[i] = data[i];
      }
    }
    return result;
  }

  private processOnCPU(data: Float32Array, operation: string): Float32Array {
    // Simulate CPU computation
    const result = new Float32Array(data.length);
    for (let i = 0; i < data.length; i++) {
      switch (operation) {
        case 'add':
          result[i] = data[i] + 1;
          break;
        case 'multiply':
          result[i] = data[i] * 2;
          break;
        case 'matrix_multiply':
          // Simulate more complex CPU computation
          let sum = 0;
          for (let j = 0; j < 10; j++) {
            sum += data[i] * data[i] * 0.1;
          }
          result[i] = sum;
          break;
        default:
          result[i] = data[i];
      }
    }
    return result;
  }
}

// Mock WebGPU compute shaders
class MockWebGPUComputer {
  private shaders: Map<string, string> = new Map();

  constructor() {
    // Pre-compile some shaders
    this.loadShader('matmul', this.getMatMulShader());
    this.loadShader('vector_add', this.getVectorAddShader());
    this.loadShader('reduce', this.getReduceShader());
  }

  loadShader(name: string, code: string): void {
    this.shaders.set(name, code);
  }

  async runShader(name: string, input: Float32Array, workgroupSize: [number, number, number] = [64, 1, 1]): Promise<Float32Array> {
    const start = performance.now();

    // Simulate shader compilation and execution
    const shader = this.shaders.get(name);
    if (!shader) {
      throw new Error(`Shader ${name} not found`);
    }

    // Simulate GPU execution time based on data size and operation complexity
    const dataSize = input.length;
    const complexity = shader.includes('matrix') ? 100 : 10;
    const gpuTime = (dataSize / 1000000) * complexity; // ~0.1ms per million elements

    await new Promise(resolve => setTimeout(resolve, gpuTime));

    const end = performance.now();
    const executionTime = end - start;

    // Simulate result
    const result = new Float32Array(input.length);
    for (let i = 0; i < input.length; i++) {
      switch (name) {
        case 'vector_add':
          result[i] = input[i] + 1;
          break;
        case 'matmul':
          result[i] = input[i] * (Math.random() * 2);
          break;
        case 'reduce':
          result[i] = input[i] * 0.5; // Simulate reduction
          break;
        default:
          result[i] = input[i];
      }
    }

    return result;
  }

  private getMatMulShader(): string {
    return `
      struct Matrix {
        size: u32,
        data: array<f32>,
      }

      @group(0) @binding(0) var<storage, read> A: Matrix;
      @group(0) @binding(1) var<storage, read> B: Matrix;
      @group(0) @binding(2) var<storage, read_write> C: Matrix;

      @compute @workgroup_size(16, 16)
      fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
        let row = global_id.x;
        let col = global_id.y;
        let size = A.size;

        if (row >= size || col >= size) {
          return;
        }

        var sum = 0.0;
        for (var i = 0u; i < size; i = i + 1) {
          let a = A.data[row * size + i];
          let b = B.data[i * size + col];
          sum = sum + a * b;
        }
        C.data[row * size + col] = sum;
      }
    `;
  }

  private getVectorAddShader(): string {
    return `
      @group(0) @binding(0) var<storage, read> input: array<f32>;
      @group(0) @binding(1) var<storage, read_write> output: array<f32>;

      @compute @workgroup_size(64)
      fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
        let idx = global_id.x;
        if (idx >= arrayLength(&input)) {
          return;
        }
        output[idx] = input[idx] + 1.0;
      }
    `;
  }

  private getReduceShader(): string {
    return `
      @group(0) @binding(0) var<storage, read> input: array<f32>;
      @group(0) @binding(1) var<storage, read_write> output: array<f32>;

      @compute @workgroup_size(64)
      fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
        let idx = global_id.x;
        let stride = arrayLength(&input) / 64u;

        var sum = 0.0;
        for (var i = 0u; i < stride; i = i + 1) {
          let input_idx = idx * stride + i;
          if (input_idx < arrayLength(&input)) {
            sum = sum + input[input_idx];
          }
        }
        output[idx] = sum;
      }
    `;
  }
}

export class GPUBenchmarkRunner {
  private config: BenchmarkConfig;
  private gpuProcessor: MockGPUProcessor;
  private webgpuComputer: MockWebGPUComputer;

  constructor(config: BenchmarkConfig) {
    this.config = config;
    this.gpuProcessor = new MockGPUProcessor();
    this.webgpuComputer = new MockWebGPUComputer();
  }

  async runAll(): Promise<BenchmarkResult[]> {
    const results: BenchmarkResult[] = [];

    console.log('  🎮 Running GPU Benchmarks...');

    // GPU availability benchmark
    results.push(await this.benchmarkGPUAvailability());

    // GPU vs CPU batch processing comparison
    results.push(await this.benchmarkBatchProcessing());

    // WebGPU shader performance
    results.push(await this.benchmarkShaderPerformance());

    // Matrix operations benchmark
    results.push(await this.benchmarkMatrixOperations());

    // Vector operations benchmark
    results.push(await this.benchmarkVectorOperations());

    // GPU memory usage benchmark
    results.push(await this.benchmarkGPUMemory());

    return results;
  }

  private async benchmarkGPUAvailability(): Promise<BenchmarkResult> {
    const times: number[] = [];

    // Test GPU detection and initialization
    for (let i = 0; i < this.config.iterations; i++) {
      const processor = new MockGPUProcessor();
      const start = performance.now();

      const isAvailable = processor.isAvailable();

      const end = performance.now();
      times.push(end - start);
    }

    return this.createResult(
      'GPU Availability Detection',
      'gpu',
      times,
      {
        available: this.gpuProcessor.isAvailable()
      }
    );
  }

  private async benchmarkBatchProcessing(): Promise<BenchmarkResult> {
    console.log('    - Batch Processing Comparison...');

    const results = [];
    const batchSizes = [100, 1000, 10000, 100000];

    for (const batchSize of batchSizes) {
      const gpuTimes: number[] = [];
      const cpuTimes: number[] = [];

      // Create test data
      const data = new Float32Array(batchSize);
      for (let i = 0; i < batchSize; i++) {
        data[i] = Math.random() * 100;
      }

      // GPU timing
      for (let i = 0; i < this.config.iterations; i++) {
        this.gpuProcessor.forceCPU(false);
        const { executionTime } = await this.gpuProcessor.processBatch(data, 'add');
        gpuTimes.push(executionTime);
      }

      // CPU timing
      for (let i = 0; i < this.config.iterations; i++) {
        this.gpuProcessor.forceCPU(true);
        const { executionTime } = await this.gpuProcessor.processBatch(data, 'add');
        cpuTimes.push(executionTime);
      }

      const avgGpuTime = gpuTimes.reduce((sum, t) => sum + t, 0) / gpuTimes.length;
      const avgCpuTime = cpuTimes.reduce((sum, t) => sum + t, 0) / cpuTimes.length;
      const speedup = avgCpuTime / avgGpuTime;
      const throughput = batchSize / (avgGpuTime / 1000); // elements per second

      console.log(`      ${batchSize} elements: GPU=${avgGpuTime.toFixed(2)}ms, CPU=${avgCpuTime.toFixed(2)}ms, Speedup=${speedup.toFixed(2)}x`);

      results.push(this.createResult(
        `GPU Batch ${batchSize} elements`,
        'gpu',
        gpuTimes,
        {
          batchSize,
          speedup,
          throughput
        }
      ));
    }

    return results;
  }

  private async benchmarkShaderPerformance(): Promise<BenchmarkResult> {
    console.log('    - WebGPU Shader Performance...');

    const results = [];
    const dataSizes = [1024, 4096, 16384, 65536];
    const shaders = ['vector_add', 'matmul', 'reduce'];

    for (const shader of shaders) {
      for (const dataSize of dataSizes) {
        const times: number[] = [];

        // Create test data
        const input = new Float32Array(dataSize);
        for (let i = 0; i < dataSize; i++) {
          input[i] = Math.random();
        }

        // Benchmark shader execution
        for (let i = 0; i < this.config.iterations; i++) {
          const start = performance.now();

          await this.webgpuComputer.runShader(shader, input);

          const end = performance.now();
          times.push(end - start);
        }

        const throughput = dataSize / (times.reduce((sum, t) => sum + t, 0) / times.length / 1000); // elements per second

        results.push(this.createResult(
          `${shader.toUpperCase()} Shader ${dataSize} elements`,
          'gpu',
          times,
          {
            shader,
            dataSize,
            throughput
          }
        ));
      }
    }

    return results;
  }

  private async benchmarkMatrixOperations(): Promise<BenchmarkResult> {
    console.log('    - Matrix Operations...');

    const matrixSizes = [16, 32, 64, 128, 256];
    const results = [];

    for (const size of matrixSizes) {
      const gpuTimes: number[] = [];
      const cpuTimes: number[] = [];

      // Create matrices
      const matrixA = new Float32Array(size * size);
      const matrixB = new Float32Array(size * size);
      for (let i = 0; i < size * size; i++) {
        matrixA[i] = Math.random();
        matrixB[i] = Math.random();
      }

      // GPU matrix multiplication
      for (let i = 0; i < this.config.iterations / 10; i++) { // Fewer iterations for large matrices
        this.gpuProcessor.forceCPU(false);
        const { executionTime } = await this.gpuProcessor.processBatch(matrixA, 'matrix_multiply');
        gpuTimes.push(executionTime);
      }

      // CPU matrix multiplication
      for (let i = 0; i < this.config.iterations / 10; i++) {
        this.gpuProcessor.forceCPU(true);
        const { executionTime } = await this.gpuProcessor.processBatch(matrixA, 'matrix_multiply');
        cpuTimes.push(executionTime);
      }

      const avgGpuTime = gpuTimes.reduce((sum, t) => sum + t, 0) / gpuTimes.length;
      const avgCpuTime = cpuTimes.reduce((sum, t) => sum + t, 0) / cpuTimes.length;
      const speedup = avgCpuTime / avgGpuTime;
      const flops = (2 * Math.pow(size, 3)) / (avgGpuTime / 1000); // FLOPS for matrix multiplication

      console.log(`      ${size}x${size} matrix: GPU=${avgGpuTime.toFixed(2)}ms, CPU=${avgCpuTime.toFixed(2)}ms, Speedup=${speedup.toFixed(2)}x, GFLOPS=${(flops / 1e9).toFixed(2)}`);

      results.push(this.createResult(
        `${size}x${size} Matrix Multiplication`,
        'gpu',
        gpuTimes,
        {
          matrixSize: size,
          speedup,
          gflops: flops / 1e9
        }
      ));
    }

    return results;
  }

  private async benchmarkVectorOperations(): Promise<BenchmarkResult> {
    console.log('    - Vector Operations...');

    const vectorSizes = [1000, 10000, 100000, 1000000];
    const operations = ['add', 'multiply', 'dot', 'normalize'];
    const results = [];

    for (const size of vectorSizes) {
      for (const operation of operations) {
        const gpuTimes: number[] = [];
        const cpuTimes: number[] = [];

        // Create vector
        const vector = new Float32Array(size);
        for (let i = 0; i < size; i++) {
          vector[i] = Math.random();
        }

        // GPU computation
        for (let i = 0; i < this.config.iterations; i++) {
          this.gpuProcessor.forceCPU(false);
          const { executionTime } = await this.gpuProcessor.processBatch(vector, operation);
          gpuTimes.push(executionTime);
        }

        // CPU computation
        for (let i = 0; i < this.config.iterations; i++) {
          this.gpuProcessor.forceCPU(true);
          const { executionTime } = await this.gpuProcessor.processBatch(vector, operation);
          cpuTimes.push(executionTime);
        }

        const avgGpuTime = gpuTimes.reduce((sum, t) => sum + t, 0) / gpuTimes.length;
        const avgCpuTime = cpuTimes.reduce((sum, t) => sum + t, 0) / cpuTimes.length;
        const speedup = avgCpuTime / avgGpuTime;
        const throughput = size / (avgGpuTime / 1000); // elements per second

        results.push(this.createResult(
          `${operation.toUpperCase()} ${size} elements`,
          'gpu',
          gpuTimes,
          {
            operation,
            vectorSize: size,
            speedup,
            throughput
          }
        ));
      }
    }

    return results;
  }

  private async benchmarkGPUMemory(): Promise<BenchmarkResult> {
    console.log('    - GPU Memory Usage...');

    const times: number[] = [];
    const memoryUsages: number[] = [];
    const sizes = [10, 100, 1000, 10000]; // MB

    for (const sizeMB of sizes) {
      const memoryBefore = process.memoryUsage().heapUsed;
      const start = performance.now();

      // Allocate memory
      const elements = (sizeMB * 1024 * 1024) / 4; // Float32 = 4 bytes
      const buffer = new Float32Array(elements);

      // Simulate GPU memory allocation and processing
      await this.webgpuComputer.runShader('vector_add', buffer.slice(0, 1000)); // Don't process entire buffer to avoid timeout

      const end = performance.now();
      const memoryAfter = process.memoryUsage().heapUsed;

      times.push(end - start);
      memoryUsages.push(memoryAfter - memoryBefore);
    }

    return this.createResult(
      'GPU Memory Usage',
      'gpu',
      times,
      {
        memoryUsages,
        sizes
      }
    );
  }

  private createResult(
    name: string,
    category: string,
    times: number[],
    metadata: Record<string, any> = {}
  ): BenchmarkResult | BenchmarkResult[] {
    times.sort((a, b) => a - b);
    const iterations = times.length;
    const totalTime = times.reduce((sum, t) => sum + t, 0);
    const avgTime = totalTime / iterations;
    const minTime = times[0];
    const maxTime = times[times.length - 1];
    const p50 = times[Math.floor(iterations * 0.5)];
    const p95 = times[Math.floor(iterations * 0.95)];
    const p99 = times[Math.floor(iterations * 0.99)];

    const result = {
      name,
      category,
      iterations,
      timing: {
        avg: avgTime,
        min: minTime,
        max: maxTime,
        p50,
        p95,
        p99
      },
      memory: {
        before: 0,
        after: 0,
        peak: 0,
        delta: 0
      },
      throughput: {
        opsPerSecond: 1000 / avgTime
      },
      errors: 0,
      metadata
    };

    return result;
  }
}