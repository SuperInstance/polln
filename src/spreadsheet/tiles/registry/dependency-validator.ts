/**
 * Dependency Validator
 *
 * Validates tile dependencies and builds dependency graphs
 */

import { TileRegistry, TileDependency, TileMetadata } from './tile-registry';
import { SemVer } from './tile-registry';

/**
 * Dependency graph node
 */
export interface DependencyNode {
  tileId: string;
  version: string;
  dependencies: DependencyEdge[];
  dependents: DependencyEdge[];
  depth: number;
  circular: boolean;
}

/**
 * Dependency graph edge
 */
export interface DependencyEdge {
  from: string;
  to: string;
  versionRange: string;
  optional: boolean;
  satisfied: boolean;
}

/**
 * Dependency resolution result
 */
export interface DependencyResolution {
  resolved: Map<string, string>; // tileId -> version
  unresolved: Set<string>;
  conflicts: DependencyConflict[];
  circular: string[][];
  order: string[]; // Load order
}

/**
 * Dependency conflict
 */
export interface DependencyConflict {
  tileId: string;
  required: string[];
  current?: string;
  reason: string;
}

/**
 * Validation options
 */
export interface ValidationOptions {
  allowOptionalMissing?: boolean;
  checkCircular?: boolean;
  resolveConflicts?: boolean;
}

/**
 * Dependency Validator class
 */
export class DependencyValidator {
  constructor(private registry: TileRegistry) {}

  /**
   * Validate tile dependencies
   */
  validate(
    metadata: TileMetadata,
    options: ValidationOptions = {}
  ): DependencyResolution {
    const resolution: DependencyResolution = {
      resolved: new Map(),
      unresolved: new Set(),
      conflicts: [],
      circular: [],
      order: []
    };

    if (!metadata.dependencies || metadata.dependencies.length === 0) {
      return resolution;
    }

    // Build dependency graph
    const graph = this.buildGraph(metadata);

    // Check for circular dependencies
    if (options.checkCircular !== false) {
      resolution.circular = this.detectCircular(graph);
    }

    // Resolve dependencies
    for (const dep of metadata.dependencies) {
      const resolved = this.resolveDependency(dep, options);

      if (resolved) {
        resolution.resolved.set(dep.tileId, resolved);
      } else {
        resolution.unresolved.add(dep.tileId);
      }
    }

    // Detect conflicts
    resolution.conflicts = this.detectConflicts(resolution.resolved, graph);

    // Determine load order
    resolution.order = this.topologicalSort(graph);

    return resolution;
  }

  /**
   * Build dependency graph
   */
  buildGraph(metadata: TileMetadata): Map<string, DependencyNode> {
    const graph = new Map<string, DependencyNode>();

    // Build graph recursively
    this.buildNode(metadata.id, metadata.version, graph, new Set(), 0);

    return graph;
  }

  /**
   * Build a node in the dependency graph
   */
  private buildNode(
    tileId: string,
    version: string,
    graph: Map<string, DependencyNode>,
    visiting: Set<string>,
    depth: number
  ): DependencyNode {
    const nodeId = `${tileId}@${version}`;

    if (graph.has(nodeId)) {
      return graph.get(nodeId)!;
    }

    const node: DependencyNode = {
      tileId,
      version,
      dependencies: [],
      dependents: [],
      depth,
      circular: visiting.has(nodeId)
    };

    graph.set(nodeId, node);

    // Mark as visiting
    visiting.add(nodeId);

    // Get tile metadata
    const tile = this.registry.get(tileId, version);
    if (tile?.metadata.dependencies) {
      for (const dep of tile.metadata.dependencies) {
        const depTile = this.resolveDependency(dep, {});

        if (depTile) {
          const depNode = this.buildNode(dep.tileId, depTile, graph, visiting, depth + 1);

          node.dependencies.push({
            from: nodeId,
            to: `${dep.tileId}@${depTile}`,
            versionRange: dep.versionRange,
            optional: dep.optional || false,
            satisfied: true
          });

          depNode.dependents.push({
            from: nodeId,
            to: `${dep.tileId}@${depTile}`,
            versionRange: dep.versionRange,
            optional: dep.optional || false,
            satisfied: true
          });
        }
      }
    }

    // Mark as visited
    visiting.delete(nodeId);

    return node;
  }

  /**
   * Resolve a single dependency
   */
  resolveDependency(
    dep: TileDependency,
    options: ValidationOptions
  ): string | null {
    const versions = this.registry.findAllVersions(dep.tileId);

    if (versions.length === 0) {
      return dep.optional ? null : null;
    }

    // Find version that satisfies range
    for (const tile of versions) {
      const ver = SemVer.parse(tile.metadata.version);
      if (ver.satisfies(dep.versionRange)) {
        return tile.metadata.version;
      }
    }

    return null;
  }

  /**
   * Detect circular dependencies
   */
  detectCircular(graph: Map<string, DependencyNode>): string[][] {
    const cycles: string[][] = [];
    const visited = new Set<string>();
    const path: string[] = [];

    const dfs = (nodeId: string): void => {
      if (path.includes(nodeId)) {
        const cycleStart = path.indexOf(nodeId);
        cycles.push([...path.slice(cycleStart), nodeId]);
        return;
      }

      if (visited.has(nodeId)) {
        return;
      }

      visited.add(nodeId);
      path.push(nodeId);

      const node = graph.get(nodeId);
      if (node) {
        for (const edge of node.dependencies) {
          dfs(edge.to);
        }
      }

      path.pop();
    };

    for (const nodeId of graph.keys()) {
      dfs(nodeId);
    }

    return cycles;
  }

  /**
   * Detect version conflicts
   */
  detectConflicts(
    resolved: Map<string, string>,
    graph: Map<string, DependencyNode>
  ): DependencyConflict[] {
    const conflicts: DependencyConflict[] = [];
    const versionMap = new Map<string, Set<string>>();

    // Group by tile ID
    for (const [tileId, version] of resolved) {
      if (!versionMap.has(tileId)) {
        versionMap.set(tileId, new Set());
      }
      versionMap.get(tileId)!.add(version);
    }

    // Check for conflicts
    for (const [tileId, versions] of versionMap) {
      if (versions.size > 1) {
        conflicts.push({
          tileId,
          required: Array.from(versions),
          reason: 'Multiple versions required'
        });
      }
    }

    return conflicts;
  }

  /**
   * Topological sort for load order
   */
  topologicalSort(graph: Map<string, DependencyNode>): string[] {
    const order: string[] = [];
    const visited = new Set<string>();
    const temp = new Set<string>();

    const visit = (nodeId: string): void => {
      if (visited.has(nodeId)) {
        return;
      }

      if (temp.has(nodeId)) {
        // Circular dependency - skip
        return;
      }

      temp.add(nodeId);

      const node = graph.get(nodeId);
      if (node) {
        for (const edge of node.dependencies) {
          visit(edge.to);
        }
      }

      temp.delete(nodeId);
      visited.add(nodeId);
      order.push(nodeId);
    };

    for (const nodeId of graph.keys()) {
      visit(nodeId);
    }

    return order.reverse();
  }

  /**
   * Get dependency tree
   */
  getDependencyTree(tileId: string, version: string): DependencyTree {
    const tile = this.registry.get(tileId, version);

    if (!tile) {
      throw new Error(`Tile not found: ${tileId}@${version}`);
    }

    return {
      tileId,
      version,
      metadata: tile.metadata,
      dependencies: (tile.metadata.dependencies || []).map(dep => ({
        tileId: dep.tileId,
        versionRange: dep.versionRange,
        optional: dep.optional || false,
        tree: this.resolveDependency(dep, {})
          ? this.getDependencyTree(dep.tileId, this.resolveDependency(dep, {})!)
          : null
      }))
    };
  }

  /**
   * Check if tile can be loaded
   */
  canLoad(tileId: string, version?: string): boolean {
    const tile = version
      ? this.registry.get(tileId, version)
      : this.registry.get(tileId);

    if (!tile) {
      return false;
    }

    const resolution = this.validate(tile.metadata);

    return (
      resolution.unresolved.size === 0 &&
      resolution.circular.length === 0 &&
      resolution.conflicts.length === 0
    );
  }

  /**
   * Get all dependents of a tile
   */
  getDependents(tileId: string, version: string): string[] {
    const dependents: string[] = [];

    for (const tile of this.registry.list()) {
      if (tile.metadata.dependencies) {
        for (const dep of tile.metadata.dependencies) {
          if (dep.tileId === tileId) {
            const ver = SemVer.parse(tile.metadata.version);
            if (ver.satisfies(dep.versionRange)) {
              dependents.push(`${tile.metadata.id}@${tile.metadata.version}`);
            }
          }
        }
      }
    }

    return dependents;
  }
}

/**
 * Dependency tree
 */
export interface DependencyTree {
  tileId: string;
  version: string;
  metadata: TileMetadata;
  dependencies: DependencyTreeNode[];
}

/**
 * Dependency tree node
 */
export interface DependencyTreeNode {
  tileId: string;
  versionRange: string;
  optional: boolean;
  tree: DependencyTree | null;
}
