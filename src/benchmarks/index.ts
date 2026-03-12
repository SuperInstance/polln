/**
 * SuperInstance Benchmark Suite - Round 12
 *
 * Comprehensive performance benchmarks for:
 * - All 19 instance types
 * - Federation with 500+ peers
 * - GPU vs CPU operations
 * - Load testing with 1000+ users
 * - Memory and performance profiling
 */

export * from './instance-benchmarks';
export * from './federation-benchmarks';
export * from './gpu-benchmarks';
export * from './load-test-benchmarks';
export * from './performance-profiler';
export * from './benchmark-runner';
export * from './dashboard-generator';

// Main benchmark runner
export { runAllBenchmarks } from './benchmark-runner';