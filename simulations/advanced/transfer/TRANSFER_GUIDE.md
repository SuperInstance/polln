# POLLN Transfer Learning Guide

## Table of Contents

1. [Introduction](#introduction)
2. [When to Use Transfer Learning](#when-to-use-transfer-learning)
3. [Task Similarity Assessment](#task-similarity-assessment)
4. [Fine-Tuning Strategies](#fine-tuning-strategies)
5. [Knowledge Succession](#knowledge-succession)
6. [Cross-Colony Federation](#cross-colony-federation)
7. [Negative Transfer Prevention](#negative-transfer-prevention)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

## Introduction

POLLN's transfer learning system enables efficient knowledge transfer between agents, tasks, and colonies. This guide provides practical guidance on when and how to use transfer learning effectively.

### Key Benefits

- **Faster Training:** 2-5x speedup for similar tasks
- **Better Performance:** 2-15% improvement over from-scratch training
- **Knowledge Retention:** >70% knowledge preserved during succession
- **Cross-Colony Learning:** 5-10% boost from federation

### Core Concepts

1. **Task Similarity:** Multi-dimensional similarity between tasks
2. **Fine-Tuning:** Adapting pre-trained knowledge to new tasks
3. **Succession:** Teacher-student knowledge transfer
4. **Federation:** Multi-colony knowledge sharing
5. **Negative Transfer:** Harmful transfer scenarios to avoid

## When to Use Transfer Learning

### Good Candidates for Transfer

✅ **High Similarity (>0.8):**
- Same domain (e.g., code review → code generation)
- Same modalities (text → text)
- Shared capabilities
- **Expected:** 5x speedup, 15% performance gain

✅ **Medium Similarity (0.5-0.8):**
- Related domains (e.g., summarization → question answering)
- Same architecture
- Partial capability overlap
- **Expected:** 2.5x speedup, 8% performance gain

⚠️ **Low Similarity (0.3-0.5):**
- Different domains (e.g., coding → sentiment analysis)
- Different architectures
- Limited capability overlap
- **Expected:** 1.2x speedup, 2% performance gain

❌ **Very Low Similarity (<0.3):**
- **Do NOT transfer** - high risk of negative transfer
- Train from scratch instead

### Decision Tree

```
Is task similarity > 0.3?
├─ No → Train from scratch
└─ Yes → Is task similarity > 0.8?
    ├─ Yes → Use LoRA (rank=8, 10 epochs, LR=0.001)
    └─ No → Is task similarity > 0.5?
        ├─ Yes → Use full fine-tuning (frozen embeddings, 50 epochs, LR=0.0001)
        └─ No → Use selective fine-tuning (100 epochs, LR=0.0005)
```

## Task Similarity Assessment

### Computing Similarity

```typescript
import { computeTaskSimilarity } from '@polln/learning/transfer';

const taskA = {
  name: 'code_review',
  description: 'Review code for bugs and style issues',
  domain: 'coding',
  capabilities: ['syntax_analysis', 'pattern_matching'],
  architecture: 'decoder-only',
  inputModality: 'text',
  outputModality: 'text'
};

const taskB = {
  name: 'code_generation',
  description: 'Generate code from descriptions',
  domain: 'coding',
  capabilities: ['syntax_analysis', 'generation'],
  architecture: 'decoder-only',
  inputModality: 'text',
  outputModality: 'text'
};

const similarity = computeTaskSimilarity(taskA, taskB);
console.log(`Similarity: ${similarity.toFixed(3)}`);
// Output: Similarity: 0.723
```

### Similarity Components

Task similarity is composed of:

1. **Semantic Similarity (40%):** Text similarity of descriptions
2. **Structural Similarity (30%):** Architecture and modality match
3. **Capability Overlap (30%):** Shared required capabilities

### Manual Assessment Checklist

Use this checklist when automated similarity is unavailable:

- [ ] Same domain? (coding, NLP, vision, etc.)
- [ ] Same architecture? (decoder-only, encoder-decoder, etc.)
- [ ] Same input modality? (text, image, audio, etc.)
- [ ] Same output modality?
- [ ] Shared capabilities? (>50% overlap)
- [ ] Similar complexity? (within 0.2 on 0-1 scale)

**Score:** 4-6 = High similarity, 2-3 = Medium, 0-1 = Low

## Fine-Tuning Strategies

### Strategy Selection Guide

#### High Similarity (>0.8): LoRA

**Configuration:**
```typescript
{
  method: 'lora',
  rank: 8,
  alpha: 16,
  learningRate: 0.001,
  epochs: 10,
  batchSize: 32,
  warmupRatio: 0.1,
  weightDecay: 0.01
}
```

**When to use:**
- Same task, different data
- Same domain, slight variation
- Quick adaptation needed

**Expected outcomes:**
- 5x training speedup
- 15% performance improvement
- 5% forgetting risk
- Minimal compute cost

#### Medium Similarity (0.5-0.8): Full Fine-Tuning

**Configuration:**
```typescript
{
  method: 'full_finetune',
  learningRate: 0.0001,
  epochs: 50,
  batchSize: 32,
  warmupRatio: 0.1,
  weightDecay: 0.01,
  freezeLayers: ['embedding']
}
```

**When to use:**
- Related tasks in same domain
- Different but compatible architectures
- Sufficient training data available

**Expected outcomes:**
- 2.5x training speedup
- 8% performance improvement
- 15% forgetting risk
- Moderate compute cost

#### Low Similarity (0.3-0.5): Selective Fine-Tuning

**Configuration:**
```typescript
{
  method: 'selective',
  learningRate: 0.0005,
  epochs: 100,
  batchSize: 32,
  warmupRatio: 0.1,
  weightDecay: 0.01,
  freezeLayers: ['embedding', 'lower_layers']
}
```

**When to use:**
- Different domains with some overlap
- Limited training data
- Want to preserve some knowledge

**Expected outcomes:**
- 1.2x training speedup
- 2% performance improvement
- 40% forgetting risk
- High compute cost

### Implementation Example

```typescript
import { getFineTuningStrategy, transferKnowledge } from '@polln/learning/transfer';

// 1. Compute similarity
const similarity = computeTaskSimilarity(sourceTask, targetTask);

// 2. Get optimal strategy
const strategy = getFineTuningStrategy(similarity);

// 3. Apply transfer
const result = await transferKnowledge(sourceAgent, targetAgent, {
  method: strategy.method,
  learningRate: strategy.learning_rate,
  epochs: strategy.epochs,
  batchSize: strategy.batch_size,
  // ... other config
});

// 4. Monitor performance
console.log(`Performance: ${result.performance.toFixed(3)}`);
console.log(`Forgetting: ${result.forgetting.toFixed(3)}`);
```

## Knowledge Succession

### Overview

Knowledge succession enables transfer from a dying (predecessor) agent to a new (successor) agent, preserving learned patterns and behaviors.

### Succession Protocol

**1. Extraction:**
```typescript
const packet = successionManager.extractKnowledge(
  agentId,
  agentType,
  agentCategory,
  state,
  valueFunction,
  executionCount,
  successCount,
  'death'  // Transfer reason
);
```

**2. Compression:**
```typescript
const compressed = successionManager.compressKnowledge(packet);
// Compresses to 50% of original patterns (top by importance)
```

**3. Transfer:**
```typescript
const event = successionManager.transferKnowledge(
  packetId,
  successorId,
  successorState
);

console.log(`Knowledge retained: ${(event.patternsPreserved / event.knowledgeTransferred * 100).toFixed(1)}%`);
```

### Best Practices

✅ **DO:**
- Use feature-based distillation (temperature=3.0, alpha=0.7)
- Compress knowledge before transfer (80% ratio)
- Validate transfer performance
- Enable rollback on failure

❌ **DON'T:**
- Transfer from low-performance agents (<0.5)
- Skip validation step
- Use response-only distillation
- Transfer stale patterns (>7 days old)

### Configuration

```typescript
const successionConfig = {
  distillationMethod: 'feature_based',
  temperature: 3.0,
  alpha: 0.7,  // 70% distillation, 30% task loss
  minRetention: 0.7,
  compressionRatio: 0.8,
  validateBeforeTransfer: true,
  rollbackOnFailure: true
};
```

## Cross-Colony Federation

### Overview

Federation enables knowledge sharing between multiple colonies, improving performance through diverse experiences.

### Federation Methods

#### Weighted Averaging (Recommended)

**Best for:** General-purpose federation

```typescript
const federationConfig = {
  method: 'weighted_averaging',
  minColonies: 2,
  minSimilarity: 0.5,
  weightByPerformance: true,
  weightByDiversity: true,
  aggregationFrequency: 10
};
```

**Expected:** 5-10% performance boost

#### Parameter Mixing

**Best for:** Highly similar colonies

```typescript
const federationConfig = {
  method: 'parameter_mixing',
  minColonies: 2,
  minSimilarity: 0.7,
  validateBeforeTransfer: true
};
```

**Expected:** 2-5% performance boost

### Implementation

```typescript
import { FederationManager } from '@polln/federation';

// 1. Create federation manager
const federation = new FederationManager(config);

// 2. Register colonies
colonies.forEach(colony => federation.registerColony(colony));

// 3. Run federation round
const result = await federation.federate();

console.log(`Performance boost: ${(result.boost * 100).toFixed(1)}%`);
console.log(`Consensus: ${result.consensus.toFixed(3)}`);
```

### Best Practices

✅ **DO:**
- Require minimum 2 colonies
- Filter by similarity (>0.5)
- Weight by performance and diversity
- Validate before applying

❌ **DON'T:**
- Federation with very dissimilar colonies (<0.3 similarity)
- Skip validation step
- Apply all updates blindly
- Federation with single colony

## Negative Transfer Prevention

### Overview

Negative transfer occurs when knowledge transfer harms rather than helps performance. The system includes multiple protection mechanisms.

### Protection Mechanisms

#### 1. Similarity Gating

Block transfers below similarity threshold:

```typescript
const protectionConfig = {
  enabled: true,
  similarityThreshold: 0.3
};

if (similarity < protectionConfig.similarityThreshold) {
  console.log('Transfer blocked: similarity too low');
  return;
}
```

#### 2. Validation Set Testing

Test on validation set before applying:

```typescript
const protectionConfig = {
  validation: {
    enabled: true,
    validationFraction: 0.1,
    minImprovement: 0.01
  }
};

// Test transfer on validation set
const validationResult = await testTransfer(transferConfig, validationData);

if (validationResult.improvement < protectionConfig.validation.minImprovement) {
  console.log('Transfer blocked: insufficient validation improvement');
  return;
}
```

#### 3. Rollback on Degradation

Monitor performance and rollback if needed:

```typescript
const protectionConfig = {
  rollback: {
    enabled: true,
    threshold: -0.02,  // 2% degradation
    monitorPerformance: true
  }
};

// Apply transfer with monitoring
const result = await applyTransferWithRollback(transferConfig, protectionConfig);

if (result.rollbackTriggered) {
  console.log('Transfer rolled back: performance degraded');
}
```

### ML-Based Prediction

Train classifier to predict negative transfer:

```typescript
const predictionConfig = {
  enabled: true,
  model: 'random_forest',
  confidenceThreshold: 0.7
};

// Predict if transfer will be negative
const prediction = await predictNegativeTransfer(scenario, predictionConfig);

if (prediction.negative && prediction.confidence > predictionConfig.confidenceThreshold) {
  console.log('Transfer blocked: predicted negative transfer');
  console.log(`Confidence: ${(prediction.confidence * 100).toFixed(1)}%`);
  return;
}
```

## Best Practices

### General Guidelines

1. **Always compute similarity** before attempting transfer
2. **Validate on held-out set** before applying to production
3. **Monitor performance** after transfer
4. **Enable rollback** for critical systems
5. **Document transfers** for reproducibility

### Performance Optimization

1. **Use LoRA** for high-similarity transfers (>0.8)
2. **Freeze embeddings** for medium-similarity transfers
3. **Use selective fine-tuning** for low-similarity transfers
4. **Avoid transfer** for very low similarity (<0.3)

### Knowledge Retention

1. **Use feature-based distillation** for succession
2. **Compress to 80%** before transfer
3. **Set temperature to 3.0** and alpha to 0.7
4. **Validate retention** >70% threshold

### Federation

1. **Require minimum 2 colonies** for federation
2. **Filter by similarity** (>0.5 threshold)
3. **Weight by performance** and diversity
4. **Aggregate periodically** (every 10 rounds)

## Troubleshooting

### Common Issues

#### Issue: Negative Transfer (Performance Degradation)

**Symptoms:**
- Performance decreases after transfer
- High forgetting ratio (>20%)

**Solutions:**
1. Check task similarity (should be >0.3)
2. Reduce learning rate by 50%
3. Use more conservative method (e.g., LoRA instead of full)
4. Enable rollback mechanism

#### Issue: Catastrophic Forgetting

**Symptoms:**
- Source task performance drops significantly
- Agent loses previous capabilities

**Solutions:**
1. Use lower learning rate
2. Freeze more layers
3. Increase distillation weight (alpha)
4. Use elastic weight consolidation

#### Issue: Low Knowledge Retention

**Symptoms:**
- Succession preserves <50% of knowledge
- Student performs much worse than teacher

**Solutions:**
1. Use feature-based distillation
2. Increase temperature to 3.0-5.0
3. Increase alpha to 0.7-0.9
4. Reduce compression ratio

#### Issue: Federation Not Converging

**Symptoms:**
- Colonies don't reach consensus
- Performance fluctuates wildly

**Solutions:**
1. Increase similarity threshold (>0.5)
2. Reduce aggregation frequency
3. Use weighted averaging instead of parameter mixing
4. Ensure sufficient colonies (>=2)

### Debug Mode

Enable debug logging:

```typescript
const debugConfig = {
  debug: true,
  logMetrics: true,
  logFrequency: 10
};

const result = await transferKnowledge(source, target, {
  ...transferConfig,
  ...debugConfig
});
```

## API Reference

### Core Functions

#### `computeTaskSimilarity(taskA, taskB): number`

Computes multi-dimensional similarity between two tasks.

**Parameters:**
- `taskA`: First task description
- `taskB`: Second task description

**Returns:** Similarity score (0-1)

**Example:**
```typescript
const similarity = computeTaskSimilarity(taskA, taskB);
console.log(`Similarity: ${similarity.toFixed(3)}`);
```

#### `getFineTuningStrategy(similarity): FineTuningConfig`

Returns optimal fine-tuning configuration for given similarity.

**Parameters:**
- `similarity`: Task similarity (0-1)

**Returns:** Fine-tuning configuration

**Example:**
```typescript
const strategy = getFineTuningStrategy(0.75);
console.log(`Method: ${strategy.method}`);
console.log(`Learning rate: ${strategy.learning_rate}`);
```

#### `shouldAllowTransfer(similarity): boolean`

Checks if transfer should be allowed based on similarity.

**Parameters:**
- `similarity`: Task similarity (0-1)

**Returns:** True if transfer allowed

**Example:**
```typescript
if (shouldAllowTransfer(similarity)) {
  await transferKnowledge(source, target);
}
```

#### `getExpectedBenefits(similarity): TransferBenefits`

Returns expected transfer benefits for given similarity.

**Parameters:**
- `similarity`: Task similarity (0-1)

**Returns:** Expected speedup, performance gain, forgetting risk

**Example:**
```typescript
const benefits = getExpectedBenefits(0.8);
console.log(`Speedup: ${benefits.speedup}x`);
console.log(`Performance gain: ${(benefits.performanceGain * 100).toFixed(1)}%`);
console.log(`Forgetting risk: ${(benefits.forgettingRisk * 100).toFixed(1)}%`);
```

### Configuration Objects

#### `TRANSFER_CONFIG`

Main transfer configuration object.

```typescript
import { TRANSFER_CONFIG } from '@polln/learning/transfer';

// Access fine-tuning configs
const highSimConfig = TRANSFER_CONFIG.fine_tuning.high;
const mediumSimConfig = TRANSFER_CONFIG.fine_tuning.medium;
const lowSimConfig = TRANSFER_CONFIG.fine_tuning.low;

// Access succession config
const successionConfig = TRANSFER_CONFIG.succession;

// Access federation config
const federationConfig = TRANSFER_CONFIG.federation;

// Access protection config
const protectionConfig = TRANSFER_CONFIG.protection;
```

---

**Last Updated:** 2026-03-07
**Version:** 1.0.0
