/**
 * Profiler
 *
 * Provides performance profiling capabilities including CPU, memory,
 * hot spot detection, call tree analysis, and optimization suggestions.
 */

import type {
  PerformanceProfile,
  ProfileSample,
  HotSpot,
  CallTreeNode,
  ProfileStats,
  OptimizationSuggestion,
} from './types.js';
import { DebugError } from './types.js';

// ============================================================================
// Profiler Class
// ============================================================================

/**
 * Performance profiler for colony and agent operations
 */
export class Profiler {
  private profiles: Map<string, PerformanceProfile> = new Map();
  private activeProfiling: Map<string, ProfilingSession> = new Map();
  private sampleInterval: number = 100; // milliseconds
  private maxSamples: number = 10000;

  /**
   * Start a profiling session
   *
   * @param profileId - Profile ID
   * @param type - Profile type
   * @returns Promise that resolves when profiling started
   */
  async startProfile(
    profileId: string,
    type: PerformanceProfile['type'] = 'cpu'
  ): Promise<void> {
    if (this.activeProfiling.has(profileId)) {
      throw new DebugError(
        'PROFILING_FAILED',
        `Profile ${profileId} already active`
      );
    }

    const session: ProfilingSession = {
      profileId,
      type,
      startTime: Date.now(),
      samples: [],
      intervalId: null,
    };

    // Start sampling
    session.intervalId = setInterval(() => {
      this.collectSample(session);
    }, this.sampleInterval);

    this.activeProfiling.set(profileId, session);
  }

  /**
   * Stop a profiling session
   *
   * @param profileId - Profile ID
   * @returns Completed profile
   */
  async stopProfile(profileId: string): Promise<PerformanceProfile> {
    const session = this.activeProfiling.get(profileId);
    if (!session) {
      throw new DebugError(
        'PROFILING_FAILED',
        `Profile ${profileId} not found`
      );
    }

    // Stop sampling
    if (session.intervalId) {
      clearInterval(session.intervalId);
    }

    const endTime = Date.now();

    // Build profile from samples
    const profile = this.buildProfile(session, endTime);

    // Store profile
    this.profiles.set(profileId, profile);
    this.activeProfiling.delete(profileId);

    return profile;
  }

  /**
   * Get a profile
   *
   * @param profileId - Profile ID
   * @returns Profile or null
   */
  getProfile(profileId: string): PerformanceProfile | null {
    return this.profiles.get(profileId) || null;
  }

  /**
   * List all profiles
   *
   * @param filters - Optional filters
   * @returns Array of profiles
   */
  listProfiles(filters?: ProfileFilters): PerformanceProfile[] {
    let profiles = Array.from(this.profiles.values());

    if (filters) {
      if (filters.type) {
        profiles = profiles.filter(p => p.type === filters.type);
      }

      if (filters.minStartTime) {
        profiles = profiles.filter(p => p.startTime >= filters.minStartTime!);
      }

      if (filters.maxStartTime) {
        profiles = profiles.filter(p => p.startTime <= filters.maxStartTime!);
      }

      if (filters.limit) {
        profiles = profiles.slice(0, filters.limit);
      }
    }

    return profiles;
  }

  /**
   * Compare two profiles
   *
   * @param profileId1 - First profile ID
   * @param profileId2 - Second profile ID
   * @returns Profile comparison
   */
  compareProfiles(profileId1: string, profileId2: string): ProfileComparison {
    const profile1 = this.profiles.get(profileId1);
    const profile2 = this.profiles.get(profileId2);

    if (!profile1 || !profile2) {
      throw new DebugError('PROFILING_FAILED', 'One or both profiles not found');
    }

    const comparison: ProfileComparison = {
      profile1Id: profileId1,
      profile2Id: profileId2,
      durationDiff: profile2.duration - profile1.duration,
      durationPercentChange: ((profile2.duration - profile1.duration) / profile1.duration) * 100,

      sampleCountDiff: profile2.samples.length - profile1.samples.length,
      sampleCountPercentChange: ((profile2.samples.length - profile1.samples.length) / profile1.samples.length) * 100,

      avgCpuDiff: profile2.stats.avgCpuUsage - profile1.stats.avgCpuUsage,
      peakCpuDiff: profile2.stats.peakCpuUsage - profile1.stats.peakCpuUsage,

      avgMemoryDiff: profile2.stats.avgMemoryUsage - profile1.stats.avgMemoryUsage,
      peakMemoryDiff: profile2.stats.peakMemoryUsage - profile1.stats.peakMemoryUsage,

      newHotspots: this.identifyNewHotspots(profile1, profile2),
      resolvedHotspots: this.identifyResolvedHotspots(profile1, profile2),

      recommendations: this.generateComparisonRecommendations(profile1, profile2),
    };

    return comparison;
  }

  /**
   * Get hot spots from a profile
   *
   * @param profileId - Profile ID
   * @param threshold - Minimum severity threshold (0-1)
   * @returns Array of hot spots
   */
  getHotspots(profileId: string, threshold: number = 0.5): HotSpot[] {
    const profile = this.profiles.get(profileId);
    if (!profile) {
      throw new DebugError('PROFILING_FAILED', `Profile ${profileId} not found`);
    }

    return profile.hotspots.filter(h => h.severity >= threshold);
  }

  /**
   * Get call tree from a profile
   *
   * @param profileId - Profile ID
   * @param maxDepth - Maximum depth to display
   * @returns Call tree root
   */
  getCallTree(profileId: string, maxDepth: number = 10): CallTreeNode {
    const profile = this.profiles.get(profileId);
    if (!profile) {
      throw new DebugError('PROFILING_FAILED', `Profile ${profileId} not found`);
    }

    return this.pruneCallTree(profile.callTree, maxDepth);
  }

  /**
   * Get optimization suggestions
   *
   * @param profileId - Profile ID
   * @param priority - Minimum priority threshold (0-1)
   * @returns Array of suggestions
   */
  getOptimizationSuggestions(
    profileId: string,
    priority: number = 0.5
  ): OptimizationSuggestion[] {
    const profile = this.profiles.get(profileId);
    if (!profile) {
      throw new DebugError('PROFILING_FAILED', `Profile ${profileId} not found`);
    }

    return profile.suggestions.filter(s => s.priority >= priority);
  }

  /**
   * Export profile to various formats
   *
   * @param profileId - Profile ID
   * @param format - Export format
   * @returns Exported data
   */
  exportProfile(profileId: string, format: ProfileExportFormat): string {
    const profile = this.profiles.get(profileId);
    if (!profile) {
      throw new DebugError('PROFILING_FAILED', `Profile ${profileId} not found`);
    }

    switch (format) {
      case 'json':
        return JSON.stringify(profile, null, 2);

      case 'flamegraph':
        return this.exportToFlamegraph(profile);

      case 'calltree':
        return this.exportToCallTree(profile);

      case 'csv':
        return this.exportToCSV(profile);

      default:
        throw new DebugError(
          'PROFILING_FAILED',
          `Unknown export format: ${format}`
        );
    }
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private collectSample(session: ProfilingSession): void {
    // In a real implementation, this would use:
    // - v8's profiler module for CPU profiling
    // - Node.js heap snapshot for memory profiling
    // - perf hooks for timing

    const sample: ProfileSample = {
      timestamp: Date.now(),
      stack: this.captureStackTrace(),
      cpuUsage: this.getCPUUsage(),
      memoryUsage: this.getMemoryUsage(),
      agentId: this.getActiveAgent(),
      operation: this.getActiveOperation(),
    };

    session.samples.push(sample);

    // Enforce max samples
    if (session.samples.length > this.maxSamples) {
      session.samples.shift();
    }
  }

  private captureStackTrace(): string[] {
    // Capture current stack trace
    const stack: string[] = [];

    // In a real implementation, this would use Error.stack or v8's profiler
    const error = new Error();
    if (error.stack) {
      const lines = error.stack.split('\n').slice(2); // Skip Error and captureStackTrace
      for (const line of lines) {
        // Extract function name from stack line
        const match = line.match(/at (\w+)/);
        if (match) {
          stack.push(match[1]);
        }
      }
    }

    return stack.length > 0 ? stack : ['anonymous'];
  }

  private getCPUUsage(): number {
    // In a real implementation, this would use process.cpuUsage()
    const usage = process.cpuUsage();
    return (usage.user + usage.system) / 1000000; // Convert to seconds
  }

  private getMemoryUsage(): number {
    // Return memory usage in MB
    return process.memoryUsage().heapUsed / 1024 / 1024;
  }

  private getActiveAgent(): string | undefined {
    // In a real implementation, this would track the currently executing agent
    return undefined;
  }

  private getActiveOperation(): string | undefined {
    // In a real implementation, this would track the current operation
    return undefined;
  }

  private buildProfile(session: ProfilingSession, endTime: number): PerformanceProfile {
    const duration = endTime - session.startTime;

    // Compute hot spots
    const hotspots = this.computeHotspots(session.samples);

    // Build call tree
    const callTree = this.buildCallTree(session.samples);

    // Compute stats
    const stats = this.computeStats(session.samples, duration);

    // Generate suggestions
    const suggestions = this.generateSuggestions(hotspots, stats);

    return {
      profileId: session.profileId,
      type: session.type,
      startTime: session.startTime,
      endTime,
      duration,
      samples: session.samples,
      hotspots,
      callTree,
      stats,
      suggestions,
    };
  }

  private computeHotspots(samples: ProfileSample[]): HotSpot[] {
    const functionStats = new Map<string, {
      totalTime: number;
      callCount: number;
      file: string;
      line: number;
    }>();

    // Aggregate by function
    for (const sample of samples) {
      for (const func of sample.stack) {
        let stats = functionStats.get(func);
        if (!stats) {
          stats = {
            totalTime: 0,
            callCount: 0,
            file: 'unknown',
            line: 0,
          };
          functionStats.set(func, stats);
        }

        stats.totalTime += this.sampleInterval;
        stats.callCount++;
      }
    }

    const totalTime = samples.length * this.sampleInterval;

    // Convert to hotspots
    return Array.from(functionStats.entries())
      .map(([name, stats]) => ({
        name,
        file: stats.file,
        line: stats.line,
        totalTime: stats.totalTime,
        percentage: (stats.totalTime / totalTime) * 100,
        callCount: stats.callCount,
        avgTimePerCall: stats.totalTime / stats.callCount,
        severity: (stats.totalTime / totalTime), // 0-1
      }))
      .filter(h => h.percentage > 1) // Only functions taking > 1% of time
      .sort((a, b) => b.totalTime - a.totalTime);
  }

  private buildCallTree(samples: ProfileSample[]): CallTreeNode {
    const root: CallTreeNode = {
      name: 'root',
      totalTime: samples.length * this.sampleInterval,
      selfTime: 0,
      callCount: samples.length,
      percentage: 100,
      children: [],
    };

    // Build tree from stack traces
    const stackMap = new Map<string, CallTreeNode>();

    for (const sample of samples) {
      let current = root;

      for (let i = sample.stack.length - 1; i >= 0; i--) {
        const func = sample.stack[i];
        let node = stackMap.get(func);

        if (!node) {
          node = {
            name: func,
            totalTime: 0,
            selfTime: 0,
            callCount: 0,
            percentage: 0,
            children: [],
          };
          stackMap.set(func, node);
          current.children.push(node);
        }

        node.totalTime += this.sampleInterval;
        node.callCount++;
        current = node;
      }

      // Leaf node gets self time
      current.selfTime += this.sampleInterval;
    }

    // Compute percentages
    this.computePercentages(root, root.totalTime);

    return root;
  }

  private computePercentages(node: CallTreeNode, totalTime: number): void {
    node.percentage = (node.totalTime / totalTime) * 100;

    for (const child of node.children) {
      this.computePercentages(child, totalTime);
    }
  }

  private pruneCallTree(node: CallTreeNode, maxDepth: number, currentDepth: number = 0): CallTreeNode {
    const pruned: CallTreeNode = {
      name: node.name,
      totalTime: node.totalTime,
      selfTime: node.selfTime,
      callCount: node.callCount,
      percentage: node.percentage,
      children: [],
    };

    if (currentDepth < maxDepth) {
      for (const child of node.children) {
        pruned.children.push(this.pruneCallTree(child, maxDepth, currentDepth + 1));
      }
    }

    return pruned;
  }

  private computeStats(samples: ProfileSample[], duration: number): ProfileStats {
    const cpuUsages = samples.map(s => s.cpuUsage);
    const memoryUsages = samples.map(s => s.memoryUsage);

    // Count unique functions
    const uniqueFunctions = new Set<string>();
    for (const sample of samples) {
      for (const func of sample.stack) {
        uniqueFunctions.add(func);
      }
    }

    return {
      totalSamples: samples.length,
      totalDuration: duration,
      avgCpuUsage: cpuUsages.reduce((a, b) => a + b, 0) / cpuUsages.length,
      peakCpuUsage: Math.max(...cpuUsages),
      avgMemoryUsage: memoryUsages.reduce((a, b) => a + b, 0) / memoryUsages.length,
      peakMemoryUsage: Math.max(...memoryUsages),
      uniqueFunctions: uniqueFunctions.size,
      totalCalls: samples.length,
    };
  }

  private generateSuggestions(
    hotspots: HotSpot[],
    stats: ProfileStats
  ): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];

    // Suggest caching for frequently called functions
    for (const hotspot of hotspots) {
      if (hotspot.callCount > 1000 && hotspot.avgTimePerCall > 1) {
        suggestions.push({
          id: `cache_${hotspot.name}`,
          type: 'cache',
          priority: Math.min(hotspot.severity, 1),
          title: `Cache results for ${hotspot.name}`,
          description: `Function ${hotspot.name} is called ${hotspot.callCount} times with average ${hotspot.avgTimePerCall.toFixed(2)}ms per call. Consider caching results.`,
          target: hotspot.name,
          expectedImprovement: `~${(hotspot.percentage * 0.5).toFixed(0)}% reduction in execution time`,
          effort: 'low',
        });
      }
    }

    // Suggest parallelization for CPU-intensive operations
    if (stats.avgCpuUsage > 0.8) {
      suggestions.push({
        id: 'parallelize_cpu',
        type: 'parallelize',
        priority: 0.7,
        title: 'Parallelize CPU-intensive operations',
        description: 'High CPU usage detected. Consider parallelizing independent operations.',
        target: 'system',
        expectedImprovement: '~30-50% reduction in execution time',
        effort: 'medium',
      });
    }

    // Suggest memory optimization
    if (stats.peakMemoryUsage > 1000) {
      suggestions.push({
        id: 'optimize_memory',
        type: 'optimize',
        priority: 0.6,
        title: 'Optimize memory usage',
        description: `High memory usage detected (${stats.peakMemoryUsage.toFixed(0)}MB). Consider implementing memory pooling or reducing object allocations.`,
        target: 'system',
        expectedImprovement: '~20-30% reduction in memory usage',
        effort: 'medium',
      });
    }

    // Suggest code optimization for hotspots
    for (const hotspot of hotspots.slice(0, 5)) {
      if (hotspot.severity > 0.3) {
        suggestions.push({
          id: `optimize_${hotspot.name}`,
          type: 'optimize',
          priority: hotspot.severity,
          title: `Optimize ${hotspot.name}`,
          description: `Function ${hotspot.name} accounts for ${hotspot.percentage.toFixed(1)}% of execution time. Review algorithm and data structures.`,
          target: hotspot.name,
          expectedImprovement: `~${(hotspot.percentage * 0.2).toFixed(0)}% reduction in execution time`,
          effort: 'high',
        });
      }
    }

    return suggestions.sort((a, b) => b.priority - a.priority);
  }

  private identifyNewHotspots(
    profile1: PerformanceProfile,
    profile2: PerformanceProfile
  ): HotSpot[] {
    const names1 = new Set(profile1.hotspots.map(h => h.name));

    return profile2.hotspots.filter(h => !names1.has(h.name));
  }

  private identifyResolvedHotspots(
    profile1: PerformanceProfile,
    profile2: PerformanceProfile
  ): HotSpot[] {
    const names2 = new Set(profile2.hotspots.map(h => h.name));

    return profile1.hotspots.filter(h => !names2.has(h.name));
  }

  private generateComparisonRecommendations(
    profile1: PerformanceProfile,
    profile2: PerformanceProfile
  ): string[] {
    const recommendations: string[] = [];

    // Duration comparison
    if (profile2.duration > profile1.duration * 1.2) {
      recommendations.push('Performance has degraded by >20%. Review recent changes.');
    } else if (profile2.duration < profile1.duration * 0.8) {
      recommendations.push('Performance has improved by >20%. Consider profiling baseline update.');
    }

    // Memory comparison
    if (profile2.stats.peakMemoryUsage > profile1.stats.peakMemoryUsage * 1.5) {
      recommendations.push('Memory usage has increased by >50%. Check for memory leaks.');
    }

    // CPU comparison
    if (profile2.stats.avgCpuUsage > profile1.stats.avgCpuUsage * 1.3) {
      recommendations.push('CPU usage has increased by >30%. Review algorithmic complexity.');
    }

    return recommendations;
  }

  private exportToFlamegraph(profile: PerformanceProfile): string {
    // Export to flamegraph format (simplified)
    const lines: string[] = [];

    for (const sample of profile.samples) {
      const stack = sample.stack.reverse(); // Flamegraph uses root at bottom
      lines.push(stack.join(';'));
    }

    return lines.join('\n');
  }

  private exportToCallTree(profile: PerformanceProfile): string {
    // Export to call tree format (text-based)
    let output = '';

    const formatNode = (node: CallTreeNode, indent: number = 0): void => {
      const prefix = '  '.repeat(indent);
      const selfPercent = ((node.selfTime / node.totalTime) * 100).toFixed(1);
      output += `${prefix}${node.name} (${node.percentage.toFixed(1)}%, self: ${selfPercent}%)\n`;

      for (const child of node.children) {
        formatNode(child, indent + 1);
      }
    };

    formatNode(profile.callTree);

    return output;
  }

  private exportToCSV(profile: PerformanceProfile): string {
    // Export hotspots as CSV
    let csv = 'function,file,line,total_time,percentage,call_count,avg_time,severity\n';

    for (const hotspot of profile.hotspots) {
      csv += `${hotspot.name},${hotspot.file},${hotspot.line},${hotspot.totalTime},${hotspot.percentage.toFixed(2)},${hotspot.callCount},${hotspot.avgTimePerCall.toFixed(2)},${hotspot.severity.toFixed(2)}\n`;
    }

    return csv;
  }
}

// ============================================================================
// Types
// ============================================================================

/**
 * Profiling session
 */
interface ProfilingSession {
  /**
   * Profile ID
   */
  profileId: string;

  /**
   * Profile type
   */
  type: PerformanceProfile['type'];

  /**
   * Start time
   */
  startTime: number;

  /**
   * Collected samples
   */
  samples: ProfileSample[];

  /**
   * Interval ID for sampling
   */
  intervalId: NodeJS.Timeout | null;
}

/**
 * Profile filters
 */
export interface ProfileFilters {
  /**
   * Filter by type
   */
  type?: PerformanceProfile['type'];

  /**
   * Filter by minimum start time
   */
  minStartTime?: number;

  /**
   * Filter by maximum start time
   */
  maxStartTime?: number;

  /**
   * Limit results
   */
  limit?: number;
}

/**
 * Profile comparison
 */
export interface ProfileComparison {
  /**
   * First profile ID
   */
  profile1Id: string;

  /**
   * Second profile ID
   */
  profile2Id: string;

  /**
   * Duration difference
   */
  durationDiff: number;

  /**
   * Duration percent change
   */
  durationPercentChange: number;

  /**
   * Sample count difference
   */
  sampleCountDiff: number;

  /**
   * Sample count percent change
   */
  sampleCountPercentChange: number;

  /**
   * Average CPU difference
   */
  avgCpuDiff: number;

  /**
   * Peak CPU difference
   */
  peakCpuDiff: number;

  /**
   * Average memory difference
   */
  avgMemoryDiff: number;

  /**
   * Peak memory difference
   */
  peakMemoryDiff: number;

  /**
   * New hotspots in profile 2
   */
  newHotspots: HotSpot[];

  /**
   * Resolved hotspots from profile 1
   */
  resolvedHotspots: HotSpot[];

  /**
   * Comparison recommendations
   */
  recommendations: string[];
}

/**
 * Profile export format
 */
export type ProfileExportFormat = 'json' | 'flamegraph' | 'calltree' | 'csv';
