# Tier Selection Guide

Guide for selecting appropriate configuration tiers for POLLN deployments.

## Quick Selection Matrix

| Scenario | Recommended Tier | Key Characteristics |
|----------|-----------------|-------------------|
| **Edge/IoT** | `SPEED_QUALITY_REALTIME` + `ACCURACY_COST_BUDGET` | <100ms latency, minimal cost |
| **Web App** | `SPEED_QUALITY_INTERACTIVE` + `ROBUSTNESS_EFFICIENCY_HIGH` | 100-500ms, 99.9% availability |
| **API Service** | `ACCURACY_COST_STANDARD` + `ROBUSTNESS_EFFICIENCY_HIGH` | Balanced performance, reliable |
| **Internal Tool** | `ACCURACY_COST_BUDGET` + `ROBUSTNESS_EFFICIENCY_BASIC` | Cost-effective, 99% availability |
| **Research** | `ACCURACY_COST_MAXIMUM` + `SPEED_QUALITY_BATCH` | Maximum quality, no latency concern |
| **Real-time System** | `SPEED_QUALITY_REALTIME` + `ROBUSTNESS_EFFICIENCY_HIGH` | <100ms, highly available |
| **Batch Processing** | `SPEED_QUALITY_BATCH` + `SCALABILITY_COMPLEXITY_LARGE` | High throughput, large scale |
| **Development** | `ACCURACY_COST_BUDGET` + `ROBUSTNESS_EFFICIENCY_BASIC` | Low cost, simple setup |

## Detailed Tier Selection

### Step 1: Identify Primary Constraints

Answer these questions to narrow down tiers:

#### 1. What is your primary constraint?

**Latency-Critical** (<100ms required)
→ Go to [Real-time Tiers](#real-time-tiers)

**Throughput-Critical** (>1000 req/s required)
→ Go to [Scalability Tiers](#scalability-tiers)

**Availability-Critical** (>99.9% required)
→ Go to [Robustness Tiers](#robustness-tiers)

**Cost-Critical** (Budget < $1/hour)
→ Go to [Budget Tiers](#budget-tiers)

**Quality-Critical** (>95% accuracy required)
→ Go to [Performance Tiers](#performance-tiers)

**No Critical Constraint** (Balanced requirements)
→ Go to [Standard Tiers](#standard-tiers)

### Real-Time Tiers <a name="real-time-tiers"></a>

**Use when:** Sub-100ms latency is required

#### Option 1: Maximum Real-time
```typescript
import { CONFIG_TIERS } from '@polln/core/config/tiers';

const config = {
  ...CONFIG_TIERS.SPEED_QUALITY_REALTIME,
  // Characteristics:
  // - Latency: 50-100ms
  // - Model: 10M (quantized)
  // - Speculative decoding: enabled
  // - Batch size: 1
};
```

**Tradeoffs:**
- ✅ Lowest latency
- ✅ Predictable performance
- ❌ Lower accuracy (~85%)
- ❌ Limited capability

**Best for:** Gaming, real-time control, live interactions

#### Option 2: Real-time with Quality
```typescript
const config = combineTiers([
  CONFIG_TIERS.SPEED_QUALITY_REALTIME,
  CONFIG_TIERS.ACCURACY_COST_STANDARD  // Override for better model
]);
```

**Tradeoffs:**
- ✅ Low latency (<100ms)
- ✅ Better accuracy (~90%)
- ❌ Higher cost
- ❌ More complex

**Best for:** Interactive assistants, chat applications

### Budget Tiers <a name="budget-tiers"></a>

**Use when:** Cost is primary concern, < $1/hour

#### Option 1: Minimum Budget
```typescript
const config = {
  ...CONFIG_TIERS.ACCURACY_COST_BUDGET,
  // Characteristics:
  // - Model: 10M
  // - Cache: 128MB
  // - Replication: 1
  // - Expected cost: $0.30/hour
};
```

**Tradeoffs:**
- ✅ Lowest cost
- ✅ Simple deployment
- ❌ Lower accuracy (~85%)
- ❌ No fault tolerance

**Best for:** Development, testing, internal tools

#### Option 2: Budget with Reliability
```typescript
const config = combineTiers([
  CONFIG_TIERS.ACCURACY_COST_BUDGET,
  {
    replication_factor: 2,  // Add redundancy
    backup_enabled: true
  }
]);
```

**Tradeoffs:**
- ✅ Still low cost (~$0.50/hour)
- ✅ Basic fault tolerance
- ❌ Slightly higher complexity

**Best for:** Non-critical production services

### Standard Tiers <a name="standard-tiers"></a>

**Use when:** Balanced requirements, no critical constraints

#### Option 1: Standard Production
```typescript
const config = {
  ...CONFIG_TIERS.ACCURACY_COST_STANDARD,
  // Characteristics:
  // - Model: 100M
  // - Cache: 512MB
  // - Latency: 300-500ms
  // - Accuracy: ~90%
  // - Cost: ~$1.00/hour
};
```

**Tradeoffs:**
- ✅ Good balance
- ✅ Predictable performance
- ⚠️ Not optimized for any specific constraint

**Best for:** General-purpose applications

#### Option 2: Standard with High Availability
```typescript
const config = combineTiers([
  CONFIG_TIERS.ACCURACY_COST_STANDARD,
  CONFIG_TIERS.ROBUSTNESS_EFFICIENCY_HIGH
]);
```

**Tradeoffs:**
- ✅ High availability (99.9%)
- ✅ Good performance
- ❌ Higher cost (~$1.50/hour)

**Best for:** Production APIs, web services

### Performance Tiers <a name="performance-tiers"></a>

**Use when:** Quality is critical, cost not a concern

#### Option 1: High Performance
```typescript
const config = {
  ...CONFIG_TIERS.ACCURACY_COST_PERFORMANCE,
  // Characteristics:
  // - Model: 500M
  // - Cache: 2GB
  // - Accuracy: ~93%
  // - Cost: ~$2.00/hour
};
```

**Tradeoffs:**
- ✅ High accuracy
- ✅ Better capability
- ❌ Higher cost
- ❌ Higher latency

**Best for:** Premium services, quality-critical applications

#### Option 2: Maximum Quality
```typescript
const config = {
  ...CONFIG_TIRES.ACCURACY_COST_MAXIMUM,
  // Characteristics:
  // - Model: 1B
  // - Cache: 4GB
  // - Accuracy: ~95%
  // - Cost: ~$3.00/hour
};
```

**Tradeoffs:**
- ✅ Maximum quality
- ✅ Best capability
- ❌ Highest cost
- ❌ Highest latency

**Best for:** Research, experimentation, premium offerings

### Robustness Tiers <a name="robustness-tiers"></a>

**Use when:** Availability is critical

#### Option 1: High Availability
```typescript
const config = {
  ...CONFIG_TIRES.ROBUSTNESS_EFFICIENCY_HIGH,
  // Characteristics:
  // - Availability: 99.9%
  // - Replication: 3
  // - Backup: Daily
  // - Monitoring: Level 2
};
```

**Tradeoffs:**
- ✅ High availability
- ✅ Good fault tolerance
- ❌ 1.5x cost multiplier

**Best for:** Production services, customer-facing applications

#### Option 2: Critical Availability
```typescript
const config = {
  ...CONFIG_TIRES.ROBUSTNESS_EFFICIENCY_CRITICAL,
  // Characteristics:
  // - Availability: 99.99%
  // - Replication: 5
  // - Backup: Hourly
  // - Disaster recovery: enabled
};
```

**Tradeoffs:**
- ✅ Maximum availability
- ✅ Disaster recovery
- ❌ 2x cost multiplier
- ❌ Complex setup

**Best for:** Mission-critical systems, financial applications

### Scalability Tiers <a name="scalability-tiers"></a>

**Use when:** Throughput is critical

#### Option 1: Medium Scale
```typescript
const config = {
  ...CONFIG_TIERS.SCALABILITY_COMPLEXITY_MEDIUM,
  // Characteristics:
  // - Colony size: 100-500
  // - Topology: Hierarchical
  // - Throughput: 1000 req/s
};
```

**Tradeoffs:**
- ✅ Good throughput
- ✅ Manageable complexity
- ❌ Requires coordination

**Best for:** Growing services, moderate traffic

#### Option 2: Large Scale
```typescript
const config = {
  ...CONFIG_TIERS.SCALABILITY_COMPLEXITY_LARGE,
  // Characteristics:
  // - Colony size: 500-1000
  // - Topology: Mesh
  // - Auto-scaling: enabled
  // - Throughput: 3000+ req/s
};
```

**Tradeoffs:**
- ✅ High throughput
- ✅ Auto-scaling
- ❌ High complexity
- ❌ Expensive

**Best for:** High-traffic services, large-scale deployments

## Scenario-Based Selection

### Scenario 1: Edge IoT Device

**Requirements:**
- Latency: <200ms
- Cost: <$0.50/hour
- Power: Battery-constrained
- Availability: >99%

**Recommended Configuration:**
```typescript
const config = combineTiers([
  CONFIG_TIERS.SPEED_QUALITY_REALTIME,  // Latency
  CONFIG_TIRES.ACCURACY_COST_BUDGET,    // Cost
  {
    replication_factor: 1,  // Battery constraint
    use_quantization: true,
    model_size: '10M'
  }
]);

// Expected characteristics:
// - Latency: 100-150ms
// - Cost: $0.30/hour
// - Availability: 99.0%
// - Accuracy: ~85%
```

### Scenario 2: Production Web API

**Requirements:**
- Latency: <500ms
- Availability: >99.9%
- Accuracy: >90%
- Cost: Flexible

**Recommended Configuration:**
```typescript
const config = combineTiers([
  CONFIG_TIRES.ROBUSTNESS_EFFICIENCY_HIGH,  // Availability
  CONFIG_TIRES.SPEED_QUALITY_INTERACTIVE,   // Latency
  CONFIG_TIRES.ACCURACY_COST_STANDARD       // Quality
]);

// Expected characteristics:
// - Latency: 300-400ms
// - Availability: 99.92%
// - Accuracy: ~90%
// - Cost: $1.50/hour
```

### Scenario 3: Internal Analytics Tool

**Requirements:**
- Latency: Not critical
- Availability: >99%
- Accuracy: >85%
- Cost: Minimize

**Recommended Configuration:**
```typescript
const config = combineTiers([
  CONFIG_TIRES.ACCURACY_COST_BUDGET,       // Cost
  CONFIG_TIRES.SPEED_QUALITY_BATCH,        // Batch processing
  CONFIG_TIRES.ROBUSTNESS_EFFICIENCY_BASIC // Basic availability
]);

// Expected characteristics:
// - Latency: 2000-5000ms
// - Availability: 99.0%
// - Accuracy: ~87%
// - Cost: $0.40/hour
```

### Scenario 4: Research Experimentation

**Requirements:**
- Accuracy: Maximum possible
- Latency: Not critical
- Availability: >95%
- Cost: Not a concern

**Recommended Configuration:**
```typescript
const config = combineTiers([
  CONFIG_TIRES.ACCURACY_COST_MAXIMUM,     // Quality
  CONFIG_TIRES.SPEED_QUALITY_BATCH,      // Batch
  {
    temperature: 0.5,        // More deterministic
    checkpoint_frequency: 20,  # Frequent checkpoints
    use_federated: true
  }
]);

// Expected characteristics:
// - Latency: 3000-5000ms
// - Availability: 99.5%
// - Accuracy: ~95%
// - Cost: $3.00/hour
```

## Migration Paths

### Upgrading Tiers

**Budget → Standard:**
```typescript
// Phase 1: Start with budget
let config = {...CONFIG_TIRES.ACCURACY_COST_BUDGET};

// Phase 2: Upgrade when needed
if (needBetterAccuracy) {
  config = {...CONFIG_TIRES.ACCURACY_COST_STANDARD};
}
```

**Standard → Performance:**
```typescript
// Gradual model upgrade
config.model_size = '100M';   // Standard
config.model_size = '250M';   // Intermediate
config.model_size = '500M';   // Performance
```

**Small → Large Scale:**
```typescript
// Start small
config = {...CONFIG_TIRES.SCALABILITY_COMPLEXITY_SMALL};

// Grow with demand
if (throughput > config.expected_throughput * 0.8) {
  config = {...CONFIG_TIRES.SCALABILITY_COMPLEXITY_MEDIUM};
}
```

## Helper Functions

```typescript
/**
 * Combine multiple tier configurations
 */
function combineTiers(tiers: object[]): object {
  return Object.assign({}, ...tiers);
}

/**
 * Validate configuration meets requirements
 */
function validateConfig(config: object, requirements: object): boolean {
  return config.latency < requirements.max_latency &&
         config.availability >= requirements.min_availability &&
         config.accuracy >= requirements.min_accuracy;
}

/**
 * Recommend tier based on requirements
 */
function recommendTier(requirements: object): object {
  if (requirements.max_latency < 100) {
    return CONFIG_TIRES.SPEED_QUALITY_REALTIME;
  }
  if (requirements.min_availability > 0.999) {
    return CONFIG_TIRES.ROBUSTNESS_EFFICIENCY_CRITICAL;
  }
  if (requirements.max_cost < 0.5) {
    return CONFIG_TIRES.ACCURACY_COST_BUDGET;
  }
  return CONFIG_TIRES.ACCURACY_COST_STANDARD;
}
```

## Decision Tree

```
Start
  │
  ├─ Is latency < 100ms required?
  │   └─ YES → Use REALTIME tier
  │
  ├─ Is availability > 99.9% required?
  │   └─ YES → Use HIGH or CRITICAL tier
  │
  ├─ Is cost < $0.50/hour required?
  │   └─ YES → Use BUDGET tier
  │
  ├─ Is accuracy > 95% required?
  │   └─ YES → Use MAXIMUM tier
  │
  ├─ Is throughput > 1000 req/s required?
  │   └─ YES → Use LARGE or XLARGE tier
  │
  └─ No critical requirements → Use STANDARD tier
```

## Conclusion

Select tiers based on your primary constraints:

1. **Latency-critical** → Real-time tiers
2. **Availability-critical** → Robustness tiers
3. **Cost-critical** → Budget tiers
4. **Quality-critical** → Performance tiers
5. **Throughput-critical** → Scalability tiers
6. **Balanced** → Standard tiers

Use scenario-based configurations as starting points, then adjust based on testing and monitoring.
