# Topology Optimization Integration Guide

Guide for integrating topology optimization results into POLLN core system.

## Overview

The topology optimization simulator generates production-ready topology templates that can be directly integrated into the POLLN core system. This guide explains how to use these templates in production deployments.

## File Structure

```
polln/
├── src/core/topology/
│   ├── templates/
│   │   ├── templates.ts      # Main template definitions
│   │   ├── types.ts          # TypeScript types
│   │   └── recommender.ts    # Recommendation engine
│   └── topology.ts           # Topology builder (NEW)
└── simulations/optimization/topology/
    ├── topology_generator.py
    ├── topology_evaluator.py
    ├── workload_modeling.py
    ├── topology_optimizer.py
    ├── template_generator.py
    └── run_all.py
```

## Integration Steps

### Step 1: Generate Topology Templates

Run the topology optimization simulator:

```bash
cd simulations/optimization/topology
python run_all.py --sizes 10 50 100 500 1000 --iterations 50
```

This generates:
- `src/core/topology/templates/templates.ts`
- `src/core/topology/templates/types.ts`
- `src/core/topology/templates/recommender.ts`
- `output/TOPOLOGY_CATALOG.json`

### Step 2: Import Templates in POLLN Core

In `src/core/colony.ts`:

```typescript
import {
  TOPOLOGY_TEMPLATES,
  getTemplateForSize,
  recommendTopology
} from './topology/templates';

export interface ColonyConfig {
  size: number;
  topology?: {
    type: string;
    params: Record<string, any>;
  };
  autoTopology?: boolean;
  priorities?: {
    efficiency?: boolean;
    robustness?: boolean;
    lowCost?: boolean;
  };
}
```

### Step 3: Add Topology Builder

Create `src/core/topology/topology.ts`:

```typescript
import { Colony } from '../colony';
import { BaseAgent } from '../agent';
import { TopologyTemplate } from './templates/types';

/**
 * Build agent topology from template
 */
export function buildTopology(
  agents: BaseAgent[],
  template: TopologyTemplate
): void {
  const topology = generateGraph(
    agents.length,
    template.topologyType,
    template.params
  );

  // Connect agents according to topology
  for (const [sourceId, targetIds] of Object.entries(topology)) {
    const source = agents[parseInt(sourceId)];

    for (const targetId of targetIds) {
      const target = agents[targetId];
      if (target) {
        source.connect(target);
      }
    }
  }
}

/**
 * Generate graph from template parameters
 */
function generateGraph(
  n: number,
  type: string,
  params: Record<string, any>
): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};

  // Initialize empty graph
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  switch (type) {
    case 'watts_strogatz':
      return wattsStrogatz(n, params.k || 4, params.p || 0.1);
    case 'barabasi_albert':
      return barabasiAlbert(n, params.m || 2);
    case 'modular':
      return modular(n, params.modules || 5);
    case 'hierarchical':
      return hierarchical(n, params.levels || 3);
    case 'two_tier':
      return twoTier(n, params.k || 4);
    case 'erdos_renyi':
      return erdosRenyi(n, params.p || 0.1);
    default:
      throw new Error(`Unknown topology type: ${type}`);
  }
}

/**
 * Watts-Strogatz small-world topology
 */
function wattsStrogatz(
  n: number,
  k: number,
  p: number
): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};

  // Initialize empty
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Create ring lattice
  for (let i = 0; i < n; i++) {
    for (let j = 1; j <= k / 2; j++) {
      const neighbor = (i + j) % n;
      adjacency[i].push(neighbor);
      adjacency[neighbor].push(i);
    }
  }

  // Rewire edges
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (adjacency[i].includes(j) && Math.random() < p) {
        // Rewire
        adjacency[i] = adjacency[i].filter((x) => x !== j);
        adjacency[j] = adjacency[j].filter((x) => x !== i);

        const newNeighbor = Math.floor(Math.random() * n);
        if (newNeighbor !== i && !adjacency[i].includes(newNeighbor)) {
          adjacency[i].push(newNeighbor);
          adjacency[newNeighbor].push(i);
        }
      }
    }
  }

  return adjacency;
}

/**
 * Barabási-Albert scale-free topology
 */
function barabasiAlbert(n: number, m: number): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};

  // Initialize with small clique
  for (let i = 0; i < m; i++) {
    adjacency[i] = [];
    for (let j = 0; j < m; j++) {
      if (i !== j) {
        adjacency[i].push(j);
      }
    }
  }

  // Add nodes with preferential attachment
  for (let i = m; i < n; i++) {
    adjacency[i] = [];

    // Calculate degrees
    const degrees: number[] = [];
    for (let j = 0; j < i; j++) {
      degrees[j] = adjacency[j].length;
    }
    const totalDegree = degrees.reduce((a, b) => a + b, 0);

    // Add m edges with probability proportional to degree
    let added = 0;
    while (added < m) {
      const r = Math.random() * totalDegree;
      let sum = 0;
      for (let j = 0; j < i; j++) {
        sum += degrees[j];
        if (sum >= r && !adjacency[i].includes(j)) {
          adjacency[i].push(j);
          adjacency[j].push(i);
          added++;
          break;
        }
      }
    }
  }

  return adjacency;
}

/**
 * Modular topology
 */
function modular(
  n: number,
  modules: number
): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};
  const moduleSize = Math.floor(n / modules);

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Create modules
  for (let m = 0; m < modules; m++) {
    const startIdx = m * moduleSize;
    const endIdx = Math.min(startIdx + moduleSize, n);

    // Small-world within module
    const moduleAdj = wattsStrogatz(
      endIdx - startIdx,
      4,
      0.1
    );

    for (const [src, targets] of Object.entries(moduleAdj)) {
      const realSrc = startIdx + parseInt(src);
      adjacency[realSrc] = [
        ...adjacency[realSrc],
        ...targets.map((t) => startIdx + t)
      ];
    }
  }

  // Add bridge connections between modules
  for (let m = 0; m < modules - 1; m++) {
    const bridgeCount = 2;
    for (let b = 0; b < bridgeCount; b++) {
      const srcModule = m * moduleSize + Math.floor(Math.random() * moduleSize);
      const dstModule = (m + 1) * moduleSize + Math.floor(Math.random() * moduleSize);

      if (!adjacency[srcModule].includes(dstModule)) {
        adjacency[srcModule].push(dstModule);
        adjacency[dstModule].push(srcModule);
      }
    }
  }

  return adjacency;
}

/**
 * Hierarchical topology
 */
function hierarchical(
  n: number,
  levels: number
): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};
  const nodesPerLevel: number[] = [];

  // Calculate nodes per level
  let remaining = n;
  for (let l = 0; l < levels; l++) {
    if (l === levels - 1) {
      nodesPerLevel.push(remaining);
    } else {
      const count = Math.max(1, Math.floor(remaining / 4));
      nodesPerLevel.push(count);
      remaining -= count;
    }
  }

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Build hierarchy
  let levelStart = 0;
  const upperNodes: number[] = [];

  for (let levelIdx = 0; levelIdx < levels; levelIdx++) {
    const count = nodesPerLevel[levelIdx];
    const levelNodes: number[] = [];

    for (let i = 0; i < count; i++) {
      levelNodes.push(levelStart + i);
    }

    if (levelIdx === 0) {
      // Top level: fully connected
      for (const i of levelNodes) {
        for (const j of levelNodes) {
          if (i < j && !adjacency[i].includes(j)) {
            adjacency[i].push(j);
            adjacency[j].push(i);
          }
        }
      }
      upperNodes.push(...levelNodes);
    } else {
      // Connect to upper level
      for (const node of levelNodes) {
        const numConnections = Math.min(upperNodes.length, 3);
        const targets = upperNodes.slice(0, numConnections);

        for (const target of targets) {
          if (!adjacency[node].includes(target)) {
            adjacency[node].push(target);
            adjacency[target].push(node);
          }
        }
      }

      // Some within-level connections
      for (const i of levelNodes) {
        for (const j of levelNodes) {
          if (i < j && Math.random() < 0.3 && !adjacency[i].includes(j)) {
            adjacency[i].push(j);
            adjacency[j].push(i);
          }
        }
      }

      upperNodes.push(...levelNodes.slice(0, Math.max(1, Math.floor(levelNodes.length / 4))));
    }

    levelStart += count;
  }

  return adjacency;
}

/**
 * Two-tier topology
 */
function twoTier(n: number, k: number): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};
  const coreSize = Math.max(3, Math.floor(n * 0.2));

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Core tier: fully connected
  for (let i = 0; i < coreSize; i++) {
    for (let j = i + 1; j < coreSize; j++) {
      adjacency[i].push(j);
      adjacency[j].push(i);
    }
  }

  // Edge tier: connect to core
  for (let i = coreSize; i < n; i++) {
    const connections = [];
    for (let j = 0; j < coreSize && connections.length < k; j++) {
      connections.push(j);
    }

    for (const target of connections) {
      adjacency[i].push(target);
      adjacency[target].push(i);
    }
  }

  // Some edge-to-edge connections
  for (let i = coreSize; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (Math.random() < 0.1) {
        adjacency[i].push(j);
        adjacency[j].push(i);
      }
    }
  }

  return adjacency;
}

/**
 * Erdős-Rényi random topology
 */
function erdosRenyi(n: number, p: number): Record<string, number[]> {
  const adjacency: Record<string, number[]> = {};

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Add edges with probability p
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (Math.random() < p) {
        adjacency[i].push(j);
        adjacency[j].push(i);
      }
    }
  }

  return adjacency;
}

export { buildTopology };
```

### Step 4: Update Colony Class

Modify `src/core/colony.ts` to use topology templates:

```typescript
import { buildTopology } from './topology/topology';
import { getTemplateForSize, recommendTopology } from './topology/templates';

export class Colony {
  constructor(config: ColonyConfig) {
    // ... existing code ...

    // Auto-select topology if requested
    if (config.autoTopology || !config.topology) {
      const template = this._selectTopology(config);
      this.topology = template;
    } else {
      this.topology = config.topology;
    }
  }

  private _selectTopology(config: ColonyConfig): TopologyTemplate {
    const { size, priorities } = config;

    // Use recommendation engine
    return recommendTopology({
      colonySize: size,
      prioritizeEfficiency: priorities?.efficiency,
      prioritizeRobustness: priorities?.robustness,
      prioritizeLowCost: priorities?.lowCost,
    });
  }

  initialize(): void {
    // Create agents
    const agents = this._createAgents();

    // Build topology
    if (this.topology) {
      buildTopology(agents, this.topology);
    }

    // ... rest of initialization ...
  }
}
```

## Usage Examples

### Example 1: Auto-Select Topology

```typescript
import { Colony } from './core';

const colony = new Colony({
  size: 100,
  autoTopology: true
});

// Automatically selects MEDIUM_COLONY template
```

### Example 2: Specify Priorities

```typescript
const colony = new Colony({
  size: 100,
  autoTopology: true,
  priorities: {
    robustness: true
  }
});

// Selects HIGH_ROBUSTNESS template
```

### Example 3: Use Specific Template

```typescript
import { TOPOLOGY_TEMPLATES } from './core/topology/templates';

const colony = new Colony({
  size: 100,
  topology: TOPOLOGY_TEMPLATES.HIGH_EFFICIENCY
});
```

### Example 4: Custom Topology

```typescript
const colony = new Colony({
  size: 100,
  topology: {
    type: 'watts_strogatz',
    params: { k: 8, p: 0.3 }
  }
});
```

## CLI Integration

Update CLI to support topology selection:

```typescript
// src/cli/commands/init.ts
import { recommendTopology } from '../../core/topology/templates';

export const initCommand = new Command('init')
  .description('Initialize colony')
  .option('-s, --size <number>', 'Colony size')
  .option('-t, --topology <type>', 'Topology type')
  .option('--efficiency', 'Prioritize efficiency')
  .option('--robustness', 'Prioritize robustness')
  .action((options) => {
    let topology;

    if (options.topology) {
      topology = TOPOLOGY_TEMPLATES[options.topology.toUpperCase()];
    } else {
      topology = recommendTopology({
        colonySize: parseInt(options.size),
        prioritizeEfficiency: options.efficiency,
        prioritizeRobustness: options.robustness,
      });
    }

    console.log(`Using topology: ${topology.name}`);
    console.log(`Description: ${topology.description}`);

    // ... initialize colony with topology ...
  });
```

## Runtime Optimization

### Dynamic Topology Adjustment

```typescript
export class Colony {
  optimizeTopology(): void {
    // Evaluate current performance
    const currentMetrics = this.evaluate();

    // If metrics don't match template expectations, consider adjustment
    const template = this.topology;
    const expected = template.expectedMetrics;

    if (currentMetrics.avgPathLength > expected.avgPathLength * 1.5) {
      console.warn('Path length higher than expected');
      // Consider adding strategic connections
    }

    if (currentMetrics.clustering < expected.clusteringCoeff * 0.8) {
      console.warn('Clustering lower than expected');
      // Consider enhancing local connections
    }
  }
}
```

### Topology Validation

```typescript
export function validateTopology(
  agents: BaseAgent[],
  template: TopologyTemplate
): ValidationResult {
  const actual = measureTopology(agents);
  const expected = template.expectedMetrics;

  return {
    isValid: actual.avgPathLength <= expected.avgPathLength * 1.5,
    pathLength: { actual: actual.avgPathLength, expected: expected.avgPathLength },
    clustering: { actual: actual.clustering, expected: expected.clusteringCoeff },
  };
}
```

## Monitoring and Metrics

```typescript
export class TopologyMonitor {
  private metrics: TopologyMetrics[];

  constructor(private colony: Colony) {}

  measure(): TopologyMetrics {
    const agents = this.colony.getAgents();

    return {
      avgPathLength: this.calculateAvgPathLength(agents),
      clustering: this.calculateClustering(agents),
      efficiency: this.calculateEfficiency(agents),
      robustness: this.calculateRobustness(agents),
    };
  }

  compareWithTemplate(): Comparison {
    const actual = this.measure();
    const expected = this.colony.topology.expectedMetrics;

    return {
      pathLengthRatio: actual.avgPathLength / expected.avgPathLength,
      clusteringRatio: actual.clustering / expected.clusteringCoeff,
      efficiencyRatio: actual.efficiency / expected.globalEfficiency,
    };
  }
}
```

## Testing

```typescript
describe('Topology Integration', () => {
  it('should auto-select appropriate topology', () => {
    const colony = new Colony({ size: 50, autoTopology: true });
    expect(colony.topology.name).toBe('Medium Colony');
  });

  it('should build topology correctly', () => {
    const agents = createTestAgents(20);
    const template = TOPOLOGY_TEMPLATES.SMALL_COLONY;

    buildTopology(agents, template);

    const connections = countConnections(agents);
    expect(connections).toBeGreaterThan(0);
  });
});
```

## Performance Considerations

1. **Template Selection**: O(1) - Direct lookup or recommendation
2. **Topology Building**: O(n + m) where n=agents, m=connections
3. **Validation**: O(n × avgPathLength) - Acceptable for periodic checks

## Troubleshooting

### Issue: Topology doesn't match expected metrics

**Solution**:
- Verify colony size matches template range
- Check agent IDs are sequential from 0
- Review connection implementation

### Issue: Poor performance with selected topology

**Solution**:
- Re-run optimization with actual workload patterns
- Use custom topology parameters
- Consider hybrid approaches

### Issue: Memory usage too high

**Solution**:
- Use lower-density topologies
- Implement sparse representation
- Consider hierarchical partitioning

## Future Enhancements

1. **Dynamic Reconfiguration**: Automatically adjust topology based on performance
2. **Multi-Topology**: Different topologies for different agent subsets
3. **Topology Evolution**: Gradually evolve topology using genetic algorithms
4. **Workload Adaptation**: Detect workload changes and adapt topology
5. **Machine Learning**: Use ML to predict optimal topology from features

## References

- Main Simulator: `simulations/optimization/topology/`
- Template Definitions: `src/core/topology/templates/templates.ts`
- Recommendation Engine: `src/core/topology/templates/recommender.ts`
- Core Colony: `src/core/colony.ts`
