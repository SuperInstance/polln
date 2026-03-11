/**
 * SuperInstance Confidence Cascade Integration
 *
 * Integrates the confidence cascade system with SuperInstance confidence tracking.
 * This module provides confidence propagation between SuperInstances and
 * integrates with the existing confidence cascade system.
 */

import {
  createConfidence,
  sequentialCascade,
  parallelCascade,
  conditionalCascade,
  Confidence,
  CascadeConfig,
  CascadeResult,
  ConfidenceZone,
  EscalationLevel
} from '../../spreadsheet/tiles/confidence-cascade';
import { SuperInstance, InstanceType, InstanceState } from '../types/base';

/**
 * SuperInstance confidence wrapper
 */
export interface SuperInstanceConfidence {
  instanceId: string;
  instanceType: InstanceType;
  instanceState: InstanceState;
  confidence: Confidence;
  dependencies: string[]; // IDs of dependent instances
  dependents: string[];   // IDs of instances that depend on this one
  lastPropagation: number;
}

/**
 * Confidence propagation graph
 */
export interface ConfidenceGraph {
  nodes: Map<string, SuperInstanceConfidence>;
  edges: Map<string, string[]>; // instanceId -> [dependentInstanceIds]
  adjacency: Map<string, string[]>; // instanceId -> [dependencyInstanceIds]
}

/**
 * SuperInstance confidence cascade manager
 */
export class SuperInstanceConfidenceCascade {
  private graph: ConfidenceGraph;
  private cascadeConfig: CascadeConfig;

  constructor(config?: Partial<CascadeConfig>) {
    this.graph = {
      nodes: new Map(),
      edges: new Map(),
      adjacency: new Map()
    };

    this.cascadeConfig = {
      greenThreshold: 0.85,
      yellowThreshold: 0.60,
      redThreshold: 0.00,
      escalateOnYellow: false,
      escalateOnRed: true,
      ...config
    };
  }

  /**
   * Register a SuperInstance for confidence tracking
   */
  registerInstance(instance: SuperInstance, initialConfidence: number = 1.0): void {
    const confidence = createConfidence(
      initialConfidence,
      `superinstance:${instance.id}`,
      this.cascadeConfig
    );

    const node: SuperInstanceConfidence = {
      instanceId: instance.id,
      instanceType: instance.type,
      instanceState: instance.state,
      confidence,
      dependencies: [],
      dependents: [],
      lastPropagation: Date.now()
    };

    this.graph.nodes.set(instance.id, node);
    this.graph.edges.set(instance.id, []);
    this.graph.adjacency.set(instance.id, []);
  }

  /**
   * Add a dependency relationship between instances
   */
  addDependency(sourceId: string, targetId: string): void {
    // Source depends on target (target -> source)
    const sourceNode = this.graph.nodes.get(sourceId);
    const targetNode = this.graph.nodes.get(targetId);

    if (!sourceNode || !targetNode) {
      throw new Error(`Instance not found: ${!sourceNode ? sourceId : targetId}`);
    }

    // Update adjacency (target depends on source)
    const targetDeps = this.graph.adjacency.get(targetId) || [];
    if (!targetDeps.includes(sourceId)) {
      targetDeps.push(sourceId);
      this.graph.adjacency.set(targetId, targetDeps);
    }

    // Update edges (source depends on target)
    const sourceEdges = this.graph.edges.get(sourceId) || [];
    if (!sourceEdges.includes(targetId)) {
      sourceEdges.push(targetId);
      this.graph.edges.set(sourceId, sourceEdges);
    }

    // Update node dependencies
    sourceNode.dependencies.push(targetId);
    targetNode.dependents.push(sourceId);
  }

  /**
   * Update confidence for an instance
   */
  updateInstanceConfidence(instanceId: string, newConfidence: number, source: string = 'manual'): void {
    const node = this.graph.nodes.get(instanceId);
    if (!node) {
      throw new Error(`Instance not found: ${instanceId}`);
    }

    node.confidence = createConfidence(
      newConfidence,
      `${source}:${instanceId}`,
      this.cascadeConfig
    );
    node.lastPropagation = Date.now();

    // Propagate confidence to dependents
    this.propagateConfidence(instanceId);
  }

  /**
   * Propagate confidence from source to its dependents
   */
  private propagateConfidence(sourceId: string): void {
    const sourceNode = this.graph.nodes.get(sourceId);
    if (!sourceNode) return;

    const dependents = sourceNode.dependents;
    if (dependents.length === 0) return;

    for (const dependentId of dependents) {
      const dependentNode = this.graph.nodes.get(dependentId);
      if (!dependentNode) continue;

      // Calculate propagated confidence
      const propagatedConfidence = this.calculatePropagatedConfidence(
        sourceNode.confidence,
        dependentNode.confidence,
        sourceId,
        dependentId
      );

      // Update dependent confidence
      dependentNode.confidence = createConfidence(
        propagatedConfidence,
        `propagated:${sourceId}->${dependentId}`,
        this.cascadeConfig
      );
      dependentNode.lastPropagation = Date.now();

      // Recursively propagate
      this.propagateConfidence(dependentId);
    }
  }

  /**
   * Calculate propagated confidence based on dependency strength
   */
  private calculatePropagatedConfidence(
    sourceConfidence: Confidence,
    currentConfidence: Confidence,
    sourceId: string,
    targetId: string
  ): number {
    // Simple propagation: weighted average of source and current confidence
    // In a real system, this would consider dependency strength, distance, etc.

    const dependencyStrength = this.calculateDependencyStrength(sourceId, targetId);
    const propagated = sourceConfidence.value * dependencyStrength;

    // Blend with current confidence
    const blendFactor = 0.7; // Weight given to propagated confidence
    return (propagated * blendFactor) + (currentConfidence.value * (1 - blendFactor));
  }

  /**
   * Calculate dependency strength between instances
   */
  private calculateDependencyStrength(sourceId: string, targetId: string): number {
    // Simple implementation: strength based on dependency depth
    // In a real system, this could consider instance types, connection types, etc.

    const sourceNode = this.graph.nodes.get(sourceId);
    const targetNode = this.graph.nodes.get(targetId);

    if (!sourceNode || !targetNode) return 0.5;

    // Type-based strength adjustments
    const typeStrength = this.getTypeStrength(sourceNode.instanceType, targetNode.instanceType);

    // State-based strength adjustments
    const stateStrength = this.getStateStrength(sourceNode.instanceState, targetNode.instanceState);

    // Distance-based attenuation (more hops = weaker)
    const distance = this.calculateDependencyDistance(sourceId, targetId);
    const distanceAttenuation = Math.exp(-0.5 * distance); // Exponential decay

    return typeStrength * stateStrength * distanceAttenuation;
  }

  /**
   * Calculate dependency distance (number of hops)
   */
  private calculateDependencyDistance(sourceId: string, targetId: string): number {
    // BFS to find shortest path
    const visited = new Set<string>();
    const queue: Array<{id: string, distance: number}> = [{ id: sourceId, distance: 0 }];

    while (queue.length > 0) {
      const current = queue.shift()!;

      if (current.id === targetId) {
        return current.distance;
      }

      if (visited.has(current.id)) continue;
      visited.add(current.id);

      const dependencies = this.graph.adjacency.get(current.id) || [];
      for (const depId of dependencies) {
        queue.push({ id: depId, distance: current.distance + 1 });
      }
    }

    return Infinity; // No path found
  }

  /**
   * Get type-based strength multiplier
   */
  private getTypeStrength(sourceType: InstanceType, targetType: InstanceType): number {
    // Type compatibility matrix
    const compatibility: Record<string, Record<string, number>> = {
      [InstanceType.DATA_BLOCK]: {
        [InstanceType.DATA_BLOCK]: 0.9,
        [InstanceType.PROCESS]: 0.7,
        [InstanceType.LEARNING_AGENT]: 0.6,
        [InstanceType.SMPBOT]: 0.8
      },
      [InstanceType.PROCESS]: {
        [InstanceType.DATA_BLOCK]: 0.8,
        [InstanceType.PROCESS]: 0.9,
        [InstanceType.LEARNING_AGENT]: 0.7,
        [InstanceType.SMPBOT]: 0.8
      },
      [InstanceType.LEARNING_AGENT]: {
        [InstanceType.DATA_BLOCK]: 0.8,
        [InstanceType.PROCESS]: 0.7,
        [InstanceType.LEARNING_AGENT]: 0.95,
        [InstanceType.SMPBOT]: 0.9
      },
      [InstanceType.SMPBOT]: {
        [InstanceType.DATA_BLOCK]: 0.8,
        [InstanceType.PROCESS]: 0.8,
        [InstanceType.LEARNING_AGENT]: 0.9,
        [InstanceType.SMPBOT]: 0.95
      }
    };

    return compatibility[sourceType]?.[targetType] ?? 0.5;
  }

  /**
   * Get state-based strength multiplier
   */
  private getStateStrength(sourceState: InstanceState, targetState: InstanceState): number {
    // States that indicate reliable operation
    const reliableStates = [
      InstanceState.RUNNING,
      InstanceState.IDLE,
      InstanceState.LISTENING
    ];

    // States that indicate potential issues
    const unreliableStates = [
      InstanceState.ERROR,
      InstanceState.DEGRADED,
      InstanceState.BLOCKED
    ];

    if (unreliableStates.includes(sourceState) || unreliableStates.includes(targetState)) {
      return 0.3;
    }

    if (reliableStates.includes(sourceState) && reliableStates.includes(targetState)) {
      return 0.9;
    }

    return 0.6;
  }

  /**
   * Get confidence for an instance
   */
  getInstanceConfidence(instanceId: string): Confidence | undefined {
    return this.graph.nodes.get(instanceId)?.confidence;
  }

  /**
   * Get confidence cascade for a dependency chain
   */
  getDependencyCascade(instanceId: string): CascadeResult {
    const node = this.graph.nodes.get(instanceId);
    if (!node) {
      throw new Error(`Instance not found: ${instanceId}`);
    }

    // Get all dependencies in order
    const dependencyChain = this.getDependencyChain(instanceId);
    const confidences = dependencyChain.map(depId => {
      const depNode = this.graph.nodes.get(depId)!;
      return depNode.confidence;
    });

    // Add the instance itself
    confidences.push(node.confidence);

    // Run sequential cascade
    return sequentialCascade(confidences, this.cascadeConfig);
  }

  /**
   * Get dependency chain (all dependencies in order)
   */
  private getDependencyChain(instanceId: string): string[] {
    const visited = new Set<string>();
    const chain: string[] = [];

    const dfs = (currentId: string) => {
      if (visited.has(currentId)) return;
      visited.add(currentId);

      const dependencies = this.graph.adjacency.get(currentId) || [];
      for (const depId of dependencies) {
        dfs(depId);
      }

      if (currentId !== instanceId) {
        chain.push(currentId);
      }
    };

    dfs(instanceId);
    return chain.reverse(); // Return in dependency order
  }

  /**
   * Get system-wide confidence status
   */
  getSystemConfidenceStatus(): {
    totalInstances: number;
    byZone: Record<ConfidenceZone, number>;
    averageConfidence: number;
    criticalInstances: string[];
  } {
    const byZone: Record<ConfidenceZone, number> = {
      [ConfidenceZone.GREEN]: 0,
      [ConfidenceZone.YELLOW]: 0,
      [ConfidenceZone.RED]: 0
    };

    let totalConfidence = 0;
    const criticalInstances: string[] = [];

    for (const [id, node] of this.graph.nodes) {
      const zone = node.confidence.zone;
      byZone[zone] = (byZone[zone] || 0) + 1;
      totalConfidence += node.confidence.value;

      if (zone === ConfidenceZone.RED) {
        criticalInstances.push(id);
      }
    }

    const totalInstances = this.graph.nodes.size;
    const averageConfidence = totalInstances > 0 ? totalConfidence / totalInstances : 0;

    return {
      totalInstances,
      byZone,
      averageConfidence,
      criticalInstances
    };
  }

  /**
   * Export confidence graph for visualization/debugging
   */
  exportGraph(): any {
    const nodes = Array.from(this.graph.nodes.values()).map(node => ({
      id: node.instanceId,
      type: node.instanceType,
      state: node.instanceState,
      confidence: node.confidence.value,
      zone: node.confidence.zone,
      dependencies: node.dependencies,
      dependents: node.dependents,
      lastPropagation: node.lastPropagation
    }));

    const edges: Array<{source: string, target: string, strength: number}> = [];

    for (const [sourceId, targetIds] of this.graph.edges.entries()) {
      for (const targetId of targetIds) {
        const strength = this.calculateDependencyStrength(sourceId, targetId);
        edges.push({ source: targetId, target: sourceId, strength });
      }
    }

    return {
      nodes,
      edges,
      config: this.cascadeConfig,
      timestamp: Date.now()
    };
  }
}

/**
 * Factory function to create confidence cascade for SuperInstance system
 */
export function createSuperInstanceConfidenceCascade(
  instances: SuperInstance[],
  dependencies?: Array<[string, string]>, // [sourceId, targetId]
  config?: Partial<CascadeConfig>
): SuperInstanceConfidenceCascade {
  const cascade = new SuperInstanceConfidenceCascade(config);

  // Register all instances
  for (const instance of instances) {
    cascade.registerInstance(instance);
  }

  // Add dependencies
  if (dependencies) {
    for (const [sourceId, targetId] of dependencies) {
      cascade.addDependency(sourceId, targetId);
    }
  }

  return cascade;
}