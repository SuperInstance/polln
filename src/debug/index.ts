/**
 * POLLN Debugger
 *
 * Main orchestrator for debugging, profiling, tracing, and visualization
 * of POLLN colonies and agents.
 */

import { EventEmitter } from 'events';
import type { DebugConfig, DebugEvent, AgentInspection, GraphVisualization, DistributedTrace, PerformanceProfile, ReplaySession } from './types.js';
import { DebugError, DebugErrorCode } from './types.js';
import { AgentInspector } from './agent-inspector.js';
import { ColonyVisualizer, VisualizationOptions, ExportFormat as VizExportFormat } from './colony-visualizer.js';
import { DistributedTracer, TraceFilters, TraceExportFormat } from './distributed-tracer.js';
import { Profiler, ProfileFilters, ProfileExportFormat } from './profiler.js';
import { Replayer, ReplayOptions, SessionFilters, ReplayExportFormat, WhatIfModification } from './replayer.js';

// ============================================================================
// PollnDebugger Class
// ============================================================================

/**
 * Main debugger orchestrator for POLLN colonies
 *
 * Provides a unified interface for all debugging capabilities:
 * - Agent inspection and state analysis
 * - Colony graph visualization
 * - Distributed tracing
 * - Performance profiling
 * - Execution replay
 */
export class PollnDebugger extends EventEmitter {
  private config: DebugConfig;
  private inspector: AgentInspector;
  private visualizer: ColonyVisualizer;
  private tracer: DistributedTracer;
  private profiler: Profiler;
  private replayer: Replayer;
  private initialized: boolean = false;

  constructor(config: DebugConfig = {}) {
    super();

    this.config = {
      verbose: false,
      maxTraceHistory: 1000,
      maxProfilingSamples: 10000,
      autoProfile: false,
      profileSampleInterval: 100,
      enableTracing: true,
      enableVisualization: true,
      ...config,
    };

    this.inspector = new AgentInspector();
    this.visualizer = new ColonyVisualizer();
    this.tracer = new DistributedTracer();
    this.profiler = new Profiler();
    this.replayer = new Replayer();
  }

  /**
   * Initialize the debugger
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      throw new DebugError('DEBUG_NOT_INITIALIZED', 'Debugger already initialized');
    }

    this.log('Initializing POLLN Debugger...');

    // Start automatic profiling if enabled
    if (this.config.autoProfile) {
      await this.profiler.startProfile('default', 'cpu');
      this.log('Automatic profiling started');
    }

    this.initialized = true;
    this.log('POLLN Debugger initialized');

    this.emitDebugEvent('debugger:initialized', { timestamp: Date.now() });
  }

  /**
   * Shutdown the debugger
   */
  async shutdown(): Promise<void> {
    this.log('Shutting down POLLN Debugger...');

    // Stop automatic profiling if active
    if (this.config.autoProfile) {
      try {
        await this.profiler.stopProfile('default');
      } catch {
        // Ignore if not profiling
      }
    }

    // Clear visualizer cache
    this.visualizer.clearCache();

    this.initialized = false;
    this.log('POLLN Debugger shutdown complete');

    this.emitDebugEvent('debugger:shutdown', { timestamp: Date.now() });
  }

  // ==========================================================================
  // Agent Inspection
  // ==========================================================================

  /**
   * Inspect an agent's current state
   *
   * @param agentId - Agent ID
   * @param agentInstance - Agent instance
   * @returns Agent inspection
   */
  async inspectAgent(
    agentId: string,
    agentInstance: any
  ): Promise<AgentInspection> {
    this.ensureInitialized();

    const inspection = await this.inspector.inspect(agentId, agentInstance);

    this.emitDebugEvent('inspection:completed', { agentId, inspection });

    return inspection;
  }

  /**
   * Get agent state at a specific point in history
   *
   * @param agentId - Agent ID
   * @param timestamp - Timestamp to retrieve (null for latest)
   * @returns Agent inspection or null
   */
  getAgentState(agentId: string, timestamp?: number): AgentInspection | null {
    this.ensureInitialized();
    return this.inspector.getHistoricalState(agentId, timestamp || null);
  }

  /**
   * Compare two agent states
   *
   * @param inspection1 - First inspection
   * @param inspection2 - Second inspection
   * @returns Array of differences
   */
  compareAgentStates(
    inspection1: AgentInspection,
    inspection2: AgentInspection
  ) {
    this.ensureInitialized();
    return this.inspector.compareStates(inspection1, inspection2);
  }

  /**
   * Set a breakpoint
   *
   * @param condition - Breakpoint condition
   * @returns Breakpoint ID
   */
  setBreakpoint(condition: any): string {
    this.ensureInitialized();
    return this.inspector.setBreakpoint(condition);
  }

  /**
   * Remove a breakpoint
   *
   * @param breakpointId - Breakpoint ID
   */
  removeBreakpoint(breakpointId: string): void {
    this.ensureInitialized();
    this.inspector.removeBreakpoint(breakpointId);
  }

  /**
   * List all breakpoints
   *
   * @param agentId - Optional agent ID filter
   * @returns Array of breakpoints
   */
  listBreakpoints(agentId?: string): any[] {
    this.ensureInitialized();
    return this.inspector.listBreakpoints(agentId);
  }

  // ==========================================================================
  // Visualization
  // ==========================================================================

  /**
   * Visualize a colony's graph structure
   *
   * @param colonyId - Colony ID
   * @param colony - Colony instance
   * @param agents - Map of agent instances
   * @param options - Visualization options
   * @returns Graph visualization
   */
  async visualizeColony(
    colonyId: string,
    colony: any,
    agents: Map<string, any>,
    options?: VisualizationOptions
  ): Promise<GraphVisualization> {
    this.ensureInitialized();

    const visualization = await this.visualizer.visualize(colonyId, colony, agents, options);

    this.emitDebugEvent('visualization:created', { colonyId, visualization });

    return visualization;
  }

  /**
   * Get a cached visualization
   *
   * @param colonyId - Colony ID
   * @returns Cached visualization or null
   */
  getCachedVisualization(colonyId: string): GraphVisualization | null {
    this.ensureInitialized();
    return this.visualizer.getCached(colonyId);
  }

  /**
   * Export visualization
   *
   * @param visualization - Graph visualization
   * @param format - Export format
   * @returns Exported data
   */
  exportVisualization(visualization: GraphVisualization, format: VizExportFormat): string {
    this.ensureInitialized();
    return this.visualizer.export(visualization, format);
  }

  /**
   * Compute graph metrics
   *
   * @param visualization - Graph visualization
   * @returns Graph metrics
   */
  computeGraphMetrics(visualization: GraphVisualization): any {
    this.ensureInitialized();
    return this.visualizer.computeGraphMetrics(visualization);
  }

  // ==========================================================================
  // Tracing
  // ==========================================================================

  /**
   * Start a new trace
   *
   * @param causalChainId - Causal chain ID
   * @param metadata - Trace metadata
   * @returns Trace ID
   */
  startTrace(causalChainId: string, metadata?: any): string {
    this.ensureInitialized();

    const traceId = this.tracer.startTrace(causalChainId, metadata);

    this.emitDebugEvent('trace:started', { traceId, causalChainId });

    return traceId;
  }

  /**
   * Start a new span
   *
   * @param traceId - Trace ID
   * @param operationName - Operation name
   * @param agentId - Agent ID
   * @param colonyId - Colony ID
   * @param parentSpanId - Parent span ID
   * @param tags - Span tags
   * @returns Span ID
   */
  startSpan(
    traceId: string,
    operationName: string,
    agentId: string,
    colonyId: string,
    parentSpanId?: string,
    tags?: Record<string, string | number | boolean>
  ): string {
    this.ensureInitialized();

    return this.tracer.startSpan(traceId, operationName, agentId, colonyId, parentSpanId, tags);
  }

  /**
   * Finish a span
   *
   * @param spanId - Span ID
   * @param status - Span status
   * @param error - Error (if failed)
   */
  finishSpan(spanId: string, status?: 'ok' | 'error' | 'cancelled', error?: Error): void {
    this.ensureInitialized();
    this.tracer.finishSpan(spanId, status, error);
  }

  /**
   * Add a log to a span
   *
   * @param spanId - Span ID
   * @param level - Log level
   * @param message - Log message
   * @param fields - Log fields
   */
  addLog(spanId: string, level: any, message: string, fields?: Record<string, unknown>): void {
    this.ensureInitialized();
    this.tracer.addLog(spanId, level, message, fields);
  }

  /**
   * Finish a trace
   *
   * @param traceId - Trace ID
   * @returns Completed trace
   */
  finishTrace(traceId: string): DistributedTrace {
    this.ensureInitialized();

    const trace = this.tracer.finishTrace(traceId);

    this.emitDebugEvent('trace:completed', { traceId, trace });

    return trace;
  }

  /**
   * Get a trace
   *
   * @param traceId - Trace ID
   * @returns Trace or null
   */
  getTrace(traceId: string): DistributedTrace | null {
    this.ensureInitialized();
    return this.tracer.getTrace(traceId);
  }

  /**
   * Get trace by causal chain ID
   *
   * @param causalChainId - Causal chain ID
   * @returns Trace or null
   */
  getTraceByCausalChain(causalChainId: string): DistributedTrace | null {
    this.ensureInitialized();
    return this.tracer.getTraceByCausalChain(causalChainId);
  }

  /**
   * List all traces
   *
   * @param filters - Optional filters
   * @returns Array of traces
   */
  listTraces(filters?: TraceFilters): DistributedTrace[] {
    this.ensureInitialized();
    return this.tracer.listTraces(filters);
  }

  /**
   * Analyze trace performance
   *
   * @param traceId - Trace ID
   * @returns Performance analysis
   */
  analyzeTracePerformance(traceId: string): any {
    this.ensureInitialized();
    return this.tracer.analyzePerformance(traceId);
  }

  /**
   * Export trace
   *
   * @param traceId - Trace ID
   * @param format - Export format
   * @returns Exported data
   */
  exportTrace(traceId: string, format: TraceExportFormat): string {
    this.ensureInitialized();
    return this.tracer.exportTrace(traceId, format);
  }

  // ==========================================================================
  // Profiling
  // ==========================================================================

  /**
   * Start a profiling session
   *
   * @param profileId - Profile ID
   * @param type - Profile type
   */
  async startProfile(profileId: string, type?: 'cpu' | 'memory' | 'io' | 'custom'): Promise<void> {
    this.ensureInitialized();

    await this.profiler.startProfile(profileId, type);

    this.emitDebugEvent('profile:started', { profileId, type });
  }

  /**
   * Stop a profiling session
   *
   * @param profileId - Profile ID
   * @returns Completed profile
   */
  async stopProfile(profileId: string): Promise<PerformanceProfile> {
    this.ensureInitialized();

    const profile = await this.profiler.stopProfile(profileId);

    this.emitDebugEvent('profile:completed', { profileId, profile });

    return profile;
  }

  /**
   * Get a profile
   *
   * @param profileId - Profile ID
   * @returns Profile or null
   */
  getProfile(profileId: string): PerformanceProfile | null {
    this.ensureInitialized();
    return this.profiler.getProfile(profileId);
  }

  /**
   * List all profiles
   *
   * @param filters - Optional filters
   * @returns Array of profiles
   */
  listProfiles(filters?: ProfileFilters): PerformanceProfile[] {
    this.ensureInitialized();
    return this.profiler.listProfiles(filters);
  }

  /**
   * Compare two profiles
   *
   * @param profileId1 - First profile ID
   * @param profileId2 - Second profile ID
   * @returns Profile comparison
   */
  compareProfiles(profileId1: string, profileId2: string): any {
    this.ensureInitialized();
    return this.profiler.compareProfiles(profileId1, profileId2);
  }

  /**
   * Get hot spots from a profile
   *
   * @param profileId - Profile ID
   * @param threshold - Minimum severity threshold
   * @returns Array of hot spots
   */
  getHotspots(profileId: string, threshold?: number): any[] {
    this.ensureInitialized();
    return this.profiler.getHotspots(profileId, threshold);
  }

  /**
   * Get call tree from a profile
   *
   * @param profileId - Profile ID
   * @param maxDepth - Maximum depth
   * @returns Call tree root
   */
  getCallTree(profileId: string, maxDepth?: number): any {
    this.ensureInitialized();
    return this.profiler.getCallTree(profileId, maxDepth);
  }

  /**
   * Get optimization suggestions
   *
   * @param profileId - Profile ID
   * @param priority - Minimum priority threshold
   * @returns Array of suggestions
   */
  getOptimizationSuggestions(profileId: string, priority?: number): any[] {
    this.ensureInitialized();
    return this.profiler.getOptimizationSuggestions(profileId, priority);
  }

  /**
   * Export profile
   *
   * @param profileId - Profile ID
   * @param format - Export format
   * @returns Exported data
   */
  exportProfile(profileId: string, format: ProfileExportFormat): string {
    this.ensureInitialized();
    return this.profiler.exportProfile(profileId, format);
  }

  // ==========================================================================
  // Replay
  // ==========================================================================

  /**
   * Start a replay session
   *
   * @param causalChainId - Causal chain ID to replay
   * @param options - Replay options
   * @returns Replay session ID
   */
  async startReplay(causalChainId: string, options?: ReplayOptions): Promise<string> {
    this.ensureInitialized();

    const sessionId = await this.replayer.startReplay(causalChainId, options);

    this.emitDebugEvent('replay:started', { sessionId, causalChainId });

    return sessionId;
  }

  /**
   * Get a replay session
   *
   * @param sessionId - Replay session ID
   * @returns Replay session or null
   */
  getReplaySession(sessionId: string): ReplaySession | null {
    this.ensureInitialized();
    return this.replayer.getSession(sessionId);
  }

  /**
   * List replay sessions
   *
   * @param filters - Optional filters
   * @returns Array of sessions
   */
  listReplaySessions(filters?: SessionFilters): ReplaySession[] {
    this.ensureInitialized();
    return this.replayer.listSessions(filters);
  }

  /**
   * Pause a replay session
   *
   * @param sessionId - Replay session ID
   */
  async pauseReplay(sessionId: string): Promise<void> {
    this.ensureInitialized();
    await this.replayer.pauseReplay(sessionId);
  }

  /**
   * Resume a replay session
   *
   * @param sessionId - Replay session ID
   */
  async resumeReplay(sessionId: string): Promise<void> {
    this.ensureInitialized();
    await this.replayer.resumeReplay(sessionId);
  }

  /**
   * Cancel a replay session
   *
   * @param sessionId - Replay session ID
   */
  async cancelReplay(sessionId: string): Promise<void> {
    this.ensureInitialized();
    await this.replayer.cancelReplay(sessionId);
  }

  /**
   * Step through a replay
   *
   * @param sessionId - Replay session ID
   * @returns Next event or null if complete
   */
  async stepReplay(sessionId: string): Promise<any | null> {
    this.ensureInitialized();
    return this.replayer.stepReplay(sessionId);
  }

  /**
   * Get replay divergences
   *
   * @param sessionId - Replay session ID
   * @returns Array of divergences
   */
  getReplayDivergences(sessionId: string): any[] {
    this.ensureInitialized();
    return this.replayer.getDivergences(sessionId);
  }

  /**
   * Get state snapshots from replay
   *
   * @param sessionId - Replay session ID
   * @param timestamp - Specific timestamp (null for all)
   * @returns Array of snapshots
   */
  getReplaySnapshots(sessionId: string, timestamp?: number): any[] {
    this.ensureInitialized();
    return this.replayer.getSnapshots(sessionId, timestamp || null);
  }

  /**
   * Perform what-if analysis
   *
   * @param causalChainId - Causal chain ID
   * @param modifications - Modifications to apply
   * @returns What-if analysis result
   */
  async whatIf(causalChainId: string, modifications: WhatIfModification[]): Promise<any> {
    this.ensureInitialized();

    const result = await this.replayer.whatIf(causalChainId, modifications);

    this.emitDebugEvent('replay:whatif', { causalChainId, modifications, result });

    return result;
  }

  /**
   * Export replay session
   *
   * @param sessionId - Replay session ID
   * @param format - Export format
   * @returns Exported data
   */
  exportReplay(sessionId: string, format: ReplayExportFormat): string {
    this.ensureInitialized();
    return this.replayer.exportReplay(sessionId, format);
  }

  // ==========================================================================
  // Utility Methods
  // ==========================================================================

  /**
   * Get debugger state
   */
  getState(): DebuggerState {
    return {
      initialized: this.initialized,
      config: this.config,
      activeProfiles: this.profiler.listProfiles({}).filter(p => !p.endTime).length,
      activeTraces: this.tracer.listTraces().filter(t => t.timeline.endTime === 0).length,
      activeReplays: this.replayer.listSessions({ status: 'running' }).length,
    };
  }

  /**
   * Clear all cached data
   */
  clearCache(): void {
    this.visualizer.clearCache();
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new DebugError('DEBUG_NOT_INITIALIZED', 'Debugger not initialized. Call initialize() first');
    }
  }

  private emitDebugEvent<T = unknown>(type: string, data: T): void {
    const event: DebugEvent<T> = {
      type: type as any,
      data,
      timestamp: Date.now(),
    };

    this.emit(type, event);
  }

  private log(...args: unknown[]): void {
    if (this.config.verbose) {
      console.log('[PollnDebugger]', ...args);
    }
  }
}

// ============================================================================
// Types
// ============================================================================

/**
 * Debugger state
 */
export interface DebuggerState {
  /**
   * Whether debugger is initialized
   */
  initialized: boolean;

  /**
   * Debugger configuration
   */
  config: DebugConfig;

  /**
   * Number of active profiles
   */
  activeProfiles: number;

  /**
   * Number of active traces
   */
  activeTraces: number;

  /**
   * Number of active replays
   */
  activeReplays: number;
}

// ============================================================================
// Exports
// ============================================================================

// Re-export all types
export * from './types.js';

// Re-export individual components
export { AgentInspector } from './agent-inspector.js';
export { ColonyVisualizer } from './colony-visualizer.js';
export { DistributedTracer } from './distributed-tracer.js';
export { Profiler } from './profiler.js';
export { Replayer } from './replayer.js';

// Create debugger factory function
export function createDebugger(config?: DebugConfig): PollnDebugger {
  return new PollnDebugger(config);
}

// Default export
export default PollnDebugger;
