# POLLN Topology Catalog

A comprehensive catalog of optimized network topologies for POLLN agent colonies.

## Quick Reference

| Colony Size | Recommended Topology | Use Case |
|-------------|---------------------|----------|
| 1-20 | Small World (Small) | Small teams, prototypes |
| 21-100 | Watts-Strogatz (Medium) | Production systems |
| 101-500 | Hierarchical (Large) | Enterprise deployments |
| 501-1000+ | Modular (Very Large) | Cloud-scale systems |

## Topology Templates

### SMALL_COLONY

**Best for**: Colonies of 1-20 agents

**Topology**: Watts-Strogatz Small-World

**Parameters**:
- Mean degree (k): 4
- Rewiring probability (p): 0.1

**Expected Metrics**:
- Average Path Length: 2.5
- Clustering Coefficient: 0.4
- Global Efficiency: 0.7
- Attack Tolerance: 0.7
- Edge Cost: 0.15

**Characteristics**:
- Network Type: small_world
- Efficiency: high
- Robustness: medium
- Cost: low

**Use Cases**:
- Small teams
- Prototype colonies
- Local clusters

**Limitations**:
- Not suitable for large-scale deployments

**Generation**:
```python
params = TopologyParams(n=10, k=4, p=0.1)
G = generator.generate(TopologyType.WATTS_STROGATZ, params)
```

---

### MEDIUM_COLONY

**Best for**: Colonies of 21-100 agents

**Topology**: Watts-Strogatz Small-World

**Parameters**:
- Mean degree (k): 6
- Rewiring probability (p): 0.2

**Expected Metrics**:
- Average Path Length: 3.2
- Clustering Coefficient: 0.35
- Global Efficiency: 0.65
- Attack Tolerance: 0.65
- Edge Cost: 0.2

**Characteristics**:
- Network Type: small_world
- Efficiency: medium
- Robustness: medium
- Cost: medium

**Use Cases**:
- Medium-scale deployments
- Production systems
- Multi-team coordination

**Limitations**:
- May need optimization for specialized workloads

**Generation**:
```python
params = TopologyParams(n=50, k=6, p=0.2)
G = generator.generate(TopologyType.WATTS_STROGATZ, params)
```

---

### LARGE_COLONY

**Best for**: Colonies of 101-500 agents

**Topology**: Hierarchical

**Parameters**:
- Hierarchy levels: 3
- Mean degree (k): 6

**Expected Metrics**:
- Average Path Length: 4.5
- Clustering Coefficient: 0.3
- Global Efficiency: 0.55
- Attack Tolerance: 0.8
- Edge Cost: 0.15

**Characteristics**:
- Network Type: community
- Efficiency: medium
- Robustness: high
- Cost: medium

**Use Cases**:
- Large-scale deployments
- Enterprise systems
- Distributed coordination

**Limitations**:
- Higher latency due to hierarchy

**Generation**:
```python
params = TopologyParams(n=200, levels=3, k=6)
G = generator.generate(TopologyType.HIERARCHICAL, params)
```

---

### VERY_LARGE_COLONY

**Best for**: Colonies of 501-1000+ agents

**Topology**: Modular

**Parameters**:
- Number of modules: 10
- Mean degree (k): 6

**Expected Metrics**:
- Average Path Length: 5.5
- Clustering Coefficient: 0.4
- Global Efficiency: 0.5
- Attack Tolerance: 0.85
- Edge Cost: 0.12

**Characteristics**:
- Network Type: community
- Efficiency: medium
- Robustness: high
- Cost: low

**Use Cases**:
- Massive deployments
- Cloud-scale systems
- Global coordination

**Limitations**:
- Complex setup and configuration

**Generation**:
```python
params = TopologyParams(n=1000, modules=10, k=6)
G = generator.generate(TopologyType.MODULAR, params)
```

---

### HIGH_EFFICIENCY

**Best for**: Latency-sensitive applications

**Topology**: Two-Tier

**Parameters**:
- Edge connections to core (k): 8

**Expected Metrics**:
- Average Path Length: 2.0
- Clustering Coefficient: 0.25
- Global Efficiency: 0.8
- Attack Tolerance: 0.5
- Edge Cost: 0.35

**Characteristics**:
- Network Type: small_world
- Efficiency: high
- Robustness: low
- Cost: high

**Use Cases**:
- Real-time systems
- High-frequency trading
- Low-latency applications

**Limitations**:
- Higher cost
- Lower robustness

**Generation**:
```python
params = TopologyParams(n=100, k=8)
G = generator.generate(TopologyType.TWO_TIER, params)
```

---

### HIGH_ROBUSTNESS

**Best for**: Fault-tolerant deployments

**Topology**: Modular

**Parameters**:
- Number of modules: 7
- Mean degree (k): 6

**Expected Metrics**:
- Average Path Length: 4.8
- Clustering Coefficient: 0.45
- Global Efficiency: 0.52
- Attack Tolerance: 0.9
- Edge Cost: 0.18

**Characteristics**:
- Network Type: community
- Efficiency: medium
- Robustness: high
- Cost: medium

**Use Cases**:
- Mission-critical systems
- Fault-tolerant deployments
- High-availability

**Limitations**:
- Higher latency
- Moderate cost

**Generation**:
```python
params = TopologyParams(n=100, modules=7, k=6)
G = generator.generate(TopologyType.MODULAR, params)
```

---

### LOW_COST

**Best for**: Resource-constrained environments

**Topology**: Erdős-Rényi Random

**Parameters**:
- Edge probability (p): 0.05

**Expected Metrics**:
- Average Path Length: 3.8
- Clustering Coefficient: 0.05
- Global Efficiency: 0.55
- Attack Tolerance: 0.5
- Edge Cost: 0.05

**Characteristics**:
- Network Type: random
- Efficiency: medium
- Robustness: low
- Cost: low

**Use Cases**:
- Resource-constrained
- Edge computing
- IoT deployments

**Limitations**:
- Lower robustness
- Poor clustering for learning

**Generation**:
```python
params = TopologyParams(n=100, p=0.05)
G = generator.generate(TopologyType.ERDOS_RENYI, params)
```

---

## Workload-Specific Recommendations

### Uniform Point-to-Point Traffic

**Scenario**: Random communication between agent pairs

**Recommended Topology**: Watts-Strogatz (k=6, p=0.2)

**Rationale**: Good balance of path length and clustering

### Hotspot Aggregation

**Scenario**: Few agents receive most traffic

**Recommended Topology**: Two-Tier (k=8)

**Rationale**: Core layer handles hotspot traffic efficiently

### Hierarchical Broadcast

**Scenario**: Periodic broadcasts to all agents

**Recommended Topology**: Hierarchical (levels=3)

**Rationale**: Natural broadcast tree structure

### Locality Gossip

**Scenario**: Local communication with gradual spread

**Recommended Topology**: Modular (modules=5)

**Rationale**: Modules provide locality, bridges enable gossip

### Bursty Multicast

**Scenario**: Periodic bursts of multicast traffic

**Recommended Topology**: Hybrid Small-World + Scale-Free (k=6, p=0.2)

**Rationale**: Hubs efficiently distribute bursty traffic

## Performance Trade-offs

### Efficiency vs Robustness

| Topology | Efficiency | Robustness | Best Use |
|----------|-----------|------------|----------|
| Two-Tier | High | Low | Real-time |
| Watts-Strogatz | Medium | Medium | General |
| Modular | Low | High | Critical |

### Cost vs Performance

| Topology | Edge Cost | Performance | Best Use |
|----------|-----------|-------------|----------|
| Erdős-Rényi | Low | Medium | Constrained |
| Watts-Strogatz | Medium | High | Production |
| Complete | High | Very High | Luxury |

### Clustering vs Path Length

| Topology | Clustering | Path Length | Best Use |
|----------|-----------|-------------|----------|
| Regular Lattice | Very High | High | Learning |
| Small-World | High | Low | Balanced |
| Random | Low | Medium | Simple |

## Scaling Guidelines

### 1-10 Agents
- Use: Complete graph or dense small-world
- Reason: Minimal cost overhead
- Path Length: ~1-2 hops

### 10-50 Agents
- Use: Small-world (k=4-6, p=0.1)
- Reason: Good balance of metrics
- Path Length: ~2-3 hops

### 50-200 Agents
- Use: Small-world or modular
- Reason: Maintain connectivity without excessive edges
- Path Length: ~3-4 hops

### 200-1000 Agents
- Use: Hierarchical or modular
- Reason: Scalable structure with local clustering
- Path Length: ~4-6 hops

### 1000+ Agents
- Use: Modular with many modules
- Reason: Extreme robustness through isolation
- Path Length: ~6+ hops

## Optimization Tips

### For Minimum Latency
1. Increase mean degree (k)
2. Use two-tier topology
3. Minimize hierarchy levels
4. Accept higher edge cost

### For Maximum Robustness
1. Use modular topology
2. Add redundant bridge connections
3. Increase module count
4. Accept higher path length

### For Maximum Learning
1. Maximize clustering coefficient
2. Use regular lattice or small-world
3. Accept longer path lengths
4. Ensure strong local connections

### For Minimum Cost
1. Minimize edge count
2. Use sparse random graphs
3. Accept lower robustness
4. Optimize for critical paths only

## Integration Examples

### TypeScript

```typescript
import { TOPOLOGY_TEMPLATES, getTemplateForSize } from './templates';

// Get template for colony size
const template = getTemplateForSize(100);

// Use in colony initialization
const colony = new Colony({
  size: 100,
  topology: {
    type: template.topologyType,
    params: template.params
  }
});
```

### Python

```python
from topology_generator import TopologyGenerator, TopologyType, TopologyParams

# Use template parameters
template = TOPOLOGY_TEMPLATES['MEDIUM_COLONY']
params = TopologyParams(**template['params'])

generator = TopologyGenerator()
G = generator.generate(TopologyType.WATTS_STROGATZ, params)
```

## Research References

1. **Small-World Networks**: Watts, D.J., Strogatz, S.H. (1998). "Collective dynamics of 'small-world' networks." Nature.

2. **Scale-Free Networks**: Barabási, A.-L., Albert, R. (1999). "Emergence of scaling in random networks." Science.

3. **Network Efficiency**: Latora, V., Marchiori, M. (2001). "Efficient behavior of small-world networks." Physical Review Letters.

4. **Modular Networks**: Newman, M.E.J. (2006). "Modularity and community structure in networks." PNAS.

## Version History

- **v1.0** (2026-03-07): Initial catalog with 7 topology templates
- Future versions will include workload-specific optimized topologies

## Contributing

To contribute new topology templates:

1. Run optimization simulations
2. Validate metrics meet requirements
3. Document use cases and limitations
4. Submit pull request with template

## Contact

For topology recommendations or questions, please open a GitHub issue.
