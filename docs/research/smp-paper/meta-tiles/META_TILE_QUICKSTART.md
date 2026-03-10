# META-TILES: Quick Start Guide

**Practical Guide for Power Users**
**Last Updated:** 2026-03-10

---

## Table of Contents

1. [Installation](#1-installation)
2. [Your First Meta-Tile](#2-your-first-meta-tile)
3. [Common Patterns](#3-common-patterns)
4. [Best Practices](#4-best-practices)
5. [Troubleshooting](#5-troubleshooting)
6. [Examples](#6-examples)

---

## 1. Installation

```bash
# Install dependencies
npm install

# The meta-tile system is included in the core SMP package
# No additional installation needed
```

---

## 2. Your First Meta-Tile

### 2.1 The "Hello World" of Meta-Tiles

Let's create a simple meta-tile that counts tiles in a graph:

```typescript
import { MetaTile, TileGraph } from '@polln/spreadsheet'

class TileCounter implements MetaTile<TileGraph, TileGraph> {
  id = 'tile_counter'
  level = 1
  description = 'Count the number of tiles in a graph'

  transform(graph: TileGraph): TileGraph {
    const count = graph.tiles.size
    console.log(`This graph has ${count} tiles`)

    // Add metadata
    graph.metadata.tile_count = count

    return graph
  }

  confidence(graph: TileGraph): Confidence {
    return {
      value: 1.0,  // We're 100% confident in counting
      zone: 'GREEN',
      source: 'tile_counter',
      timestamp: Date.now()
    }
  }

  safety(graph: TileGraph): SafetyScore {
    return {
      score: 1.0,  // Safe - just counting
      violations: []
    }
  }

  explain(graph: TileGraph): string {
    return `Counted ${graph.tiles.size} tiles in the graph`
  }

  input_schema = {}
  output_schema = {}
  preserved_constraints = []
  broken_constraints = []
}

// Use it
const counter = new TileCounter()
const result = counter.transform(myTileGraph)
console.log(result.metadata.tile_count)  // → 42
```

### 2.2 A More Useful Example: Tile Pruner

Remove tiles that don't affect the output:

```typescript
class TilePruner implements MetaTile<TileGraph, TileGraph> {
  id = 'tile_pruner'
  level = 1
  description = 'Remove tiles that don\'t affect the output'

  transform(graph: TileGraph): TileGraph {
    // Find output tiles (tiles with no outgoing edges)
    const outputTiles = this.findOutputTiles(graph)

    // Find all tiles that lead to outputs
    const necessaryTiles = new Set<TileID>()
    for (const outputTile of outputTiles) {
      this.findAncestors(graph, outputTile, necessaryTiles)
    }

    // Remove unnecessary tiles
    for (const [tileId, tile] of graph.tiles) {
      if (!necessaryTiles.has(tileId)) {
        graph.tiles.delete(tileId)
        // Remove edges to/from this tile
        graph.edges = graph.edges.filter(e =>
          e.from !== tileId && e.to !== tileId
        )
      }
    }

    return graph
  }

  private findOutputTiles(graph: TileGraph): TileID[] {
    const hasOutgoing = new Set<TileID>()
    for (const edge of graph.edges) {
      hasOutgoing.add(edge.from)
    }

    return Array.from(graph.tiles.keys()).filter(id => !hasOutgoing.has(id))
  }

  private findAncestors(
    graph: TileGraph,
    tileId: TileID,
    visited: Set<TileID>
  ): void {
    if (visited.has(tileId)) return
    visited.add(tileId)

    // Find all tiles that have edges to this tile
    for (const edge of graph.edges) {
      if (edge.to === tileId) {
        this.findAncestors(graph, edge.from, visited)
      }
    }
  }

  confidence(graph: TileGraph): Confidence {
    // Confidence depends on how much we're removing
    const before = graph.tiles.size
    const after = this.transform(graph).tiles.size
    const removed = before - after

    // If we're removing a lot, be less confident
    const confidence = 1.0 - (removed / before) * 0.1

    return {
      value: confidence,
      zone: confidence > 0.85 ? 'GREEN' : 'YELLOW',
      source: 'tile_pruner',
      timestamp: Date.now()
    }
  }

  // ... other required methods
}
```

---

## 3. Common Patterns

### 3.1 Pattern: Template Generator

Generate tiles from parameterized templates:

```typescript
class TemplateGenerator implements MetaTile<TileGraph, TileGraph> {
  id = 'template_generator'
  level = 1
  description = 'Generate tiles from templates'

  transform(graph: TileGraph): TileGraph {
    // Find template instantiations in the graph
    const templates = this.findTemplates(graph)

    // Instantiate each template
    for (const template of templates) {
      const tile = this.instantiate(template)
      graph.tiles.set(tile.id, tile)
    }

    return graph
  }

  private instantiate(template: TemplateInstantiation): Tile {
    // Extract parameters
    const params = template.parameters

    // Create tile from template
    return {
      id: this.generateId(),
      description: `Generated from template ${template.template_id}`,
      input_type: this.resolveType(template.input_type, params),
      output_type: this.resolveType(template.output_type, params),
      constraints: this.resolveConstraints(template.constraints, params),
      base_confidence: template.base_confidence,
      has_side_effects: false,
      discriminate: (input) => {
        // Template logic with parameter substitution
        return this.executeTemplate(template, input, params)
      },
      confidence: (input) => template.base_confidence,
      trace: (input) => `Executed template ${template.template_id}`
    }
  }
}

// Usage: Define a template
const validationTemplate = {
  id: 'range_validator',
  parameters: ['field', 'min', 'max'],
  input_type: { type: 'object' },
  output_type: { type: 'object' },
  constraints: [
    {
      variable: '{{field}}',
      min: '{{min}}',
      max: '{{max}}',
      required: true,
      description: '{{field}} must be between {{min}} and {{max}}'
    }
  ],
  logic: (input, params) => {
    const value = input[params.field]
    if (value < params.min || value > params.max) {
      throw new Error(`${params.field} out of range`)
    }
    return input
  }
}

// Instantiate the template
const generator = new TemplateGenerator()
const ageValidator = generator.instantiate({
  template: validationTemplate,
  parameters: {
    field: 'age',
    min: 0,
    max: 120
  }
})
```

### 3.2 Pattern: Graph Optimizer

Optimize tile graphs for performance:

```typescript
class PerformanceOptimizer implements MetaTile<TileGraph, TileGraph> {
  id = 'performance_optimizer'
  level = 1
  description = 'Optimize tile graph for performance'

  transform(graph: TileGraph): TileGraph {
    // Apply optimization passes
    graph = this.parallelizeIndependentChains(graph)
    graph = this.insertMemoization(graph)
    graph = this.fuseConsecutiveTiles(graph)

    return graph
  }

  private parallelizeIndependentChains(graph: TileGraph): TileGraph {
    // Find chains that can run in parallel
    const chains = this.findIndependentChains(graph)

    // Convert to parallel execution
    for (const chain of chains) {
      const parallelTile = this.createParallelTile(chain)

      // Replace chain with parallel tile
      for (const tileId of chain) {
        graph.tiles.delete(tileId)
      }
      graph.tiles.set(parallelTile.id, parallelTile)

      // Rewire edges
      this.rewireForParallel(graph, chain, parallelTile.id)
    }

    return graph
  }

  private insertMemoization(graph: TileGraph): TileGraph {
    // Find expensive pure functions
    for (const [tileId, tile] of graph.tiles) {
      if (this.isExpensive(tile) && this.isPure(tile)) {
        const memoTile = this.createMemoizationTile(tileId)
        graph.tiles.set(memoTile.id, memoTile)

        // Insert before original tile
        this.insertBefore(graph, memoTile.id, tileId)
      }
    }

    return graph
  }

  private fuseConsecutiveTiles(graph: TileGraph): TileGraph {
    // Find pairs of tiles that can be fused
    const pairs = this.findFusablePairs(graph)

    for (const [t1, t2] of pairs) {
      const fused = this.fuseTiles(t1, t2)

      // Replace with fused tile
      graph.tiles.delete(t1.id)
      graph.tiles.delete(t2.id)
      graph.tiles.set(fused.id, fused)

      // Rewire edges
      this.rewireForFusion(graph, t1.id, t2.id, fused.id)
    }

    return graph
  }
}
```

### 3.3 Pattern: Property Analyzer

Extract properties from tile graphs:

```typescript
class PropertyAnalyzer implements MetaTile<TileGraph, AnalysisReport> {
  id = 'property_analyzer'
  level = 1
  description = 'Analyze tile graph properties'

  transform(graph: TileGraph): AnalysisReport {
    return {
      complexity: this.analyzeComplexity(graph),
      confidence: this.analyzeConfidence(graph),
      safety: this.analyzeSafety(graph),
      bottlenecks: this.findBottlenecks(graph),
      recommendations: this.generateRecommendations(graph)
    }
  }

  private analyzeComplexity(graph: TileGraph): ComplexityMetrics {
    let totalComplexity = 0

    for (const [id, tile] of graph.tiles) {
      totalComplexity += this.estimateComplexity(tile)
    }

    // Account for parallelism
    const parallelism = this.calculateParallelism(graph)
    const effectiveComplexity = totalComplexity / parallelism

    return {
      total: totalComplexity,
      effective: effectiveComplexity,
      parallelism: parallelism,
      big_o: this.calculateBigO(graph)
    }
  }

  private analyzeConfidence(graph: TileGraph): ConfidenceBounds {
    const confidences = Array.from(graph.tiles.values())
      .map(t => t.base_confidence)

    // Propagate confidence through graph
    const propagated = this.propagateConfidence(graph)

    return {
      min: Math.min(...confidences),
      max: Math.max(...confidences),
      average: confidences.reduce((a, b) => a + b, 0) / confidences.length,
      propagated: propagated
    }
  }

  private analyzeSafety(graph: TileGraph): SafetyReport {
    const violations: SafetyViolation[] = []

    // Check type compatibility
    for (const edge of graph.edges) {
      const fromTile = graph.tiles.get(edge.from)!
      const toTile = graph.tiles.get(edge.to)!

      if (!this.typesCompatible(fromTile.output_type, toTile.input_type)) {
        violations.push({
          type: 'type_mismatch',
          edge: edge,
          message: `Type mismatch between ${edge.from} and ${edge.to}`
        })
      }
    }

    // Check constraint satisfaction
    for (const [id, tile] of graph.tiles) {
      for (const constraint of tile.constraints) {
        if (!this.constraintSatisfiable(tile, constraint)) {
          violations.push({
            type: 'unsatisfiable_constraint',
            tile_id: id,
            constraint: constraint,
            message: `Constraint ${constraint.variable} cannot be satisfied`
          })
        }
      }
    }

    return {
      valid: violations.length === 0,
      violations: violations,
      score: this.calculateSafetyScore(violations)
    }
  }
}
```

---

## 4. Best Practices

### 4.1 Always Declare Stratification Level

```typescript
// GOOD
class MyMetaTile implements MetaTile {
  level = 1  // Explicitly declare level
  // ...
}

// BAD
class MyMetaTile implements MetaTile {
  // Missing level - will fail at runtime
  // ...
}
```

### 4.2 Preserve Constraints When Possible

```typescript
// GOOD
class MyMetaTile implements MetaTile {
  preserved_constraints = [
    ConstraintSet.TypeSafety,
    ConstraintSet.ConfidenceMonotonicity
  ]
  // ...
}

// BAD
class MyMetaTile implements MetaTile {
  preserved_constraints = []  // Empty - claims to preserve nothing
  // Even if you do preserve some constraints
}
```

### 4.3 Provide Explanations

```typescript
// GOOD
transform(graph: TileGraph): TileGraph {
  const before = graph.tiles.size
  // ... transformation ...
  const after = graph.tiles.size

  graph.annotations.explanation =
    `Removed ${before - after} redundant tiles`

  return graph
}

// BAD
transform(graph: TileGraph): TileGraph {
  // ... transformation ...
  return graph  // No explanation
}
```

### 4.4 Calculate Confidence Accurately

```typescript
// GOOD
confidence(graph: TileGraph): Confidence {
  // Base confidence
  let confidence = 0.95

  // Reduce based on complexity
  confidence -= graph.tiles.size * 0.01

  // Reduce based on transformations
  confidence -= this.countTransformations(graph) * 0.02

  return {
    value: Math.max(0, confidence),
    zone: confidence > 0.85 ? 'GREEN' : confidence > 0.60 ? 'YELLOW' : 'RED',
    source: this.id,
    timestamp: Date.now()
  }
}

// BAD
confidence(graph: TileGraph): Confidence {
  // Always returns 1.0 - overconfident!
  return {
    value: 1.0,
    zone: 'GREEN',
    source: this.id,
    timestamp: Date.now()
  }
}
```

### 4.5 Validate Before Transforming

```typescript
// GOOD
transform(graph: TileGraph): TileGraph {
  // Validate input
  const validation = this.validateInput(graph)
  if (!validation.valid) {
    throw new ValidationError(validation.errors)
  }

  // Perform transformation
  const result = this.doTransform(graph)

  // Validate output
  const outputValidation = this.validateOutput(result)
  if (!outputValidation.valid) {
    throw new ValidationError(outputValidation.errors)
  }

  return result
}

// BAD
transform(graph: TileGraph): TileGraph {
  // No validation - might produce invalid graphs
  return this.doTransform(graph)
}
```

---

## 5. Troubleshooting

### 5.1 Infinite Recursion

**Symptom:** Stack overflow or hangs forever.

**Solution:**
```typescript
// Add recursion detection
class RecursionSafeMetaTile implements MetaTile {
  private maxDepth = 10
  private currentDepth = 0

  transform(graph: TileGraph): TileGraph {
    if (this.currentDepth >= this.maxDepth) {
      throw new Error('Maximum recursion depth exceeded')
    }

    this.currentDepth++
    try {
      return this.doTransform(graph)
    } finally {
      this.currentDepth--
    }
  }
}
```

### 5.2 Type Mismatches

**Symptom:** Runtime type errors.

**Solution:**
```typescript
// Add type checking
class TypeSafeMetaTile implements MetaTile {
  transform(graph: TileGraph): TileGraph {
    // Check all edges for type compatibility
    for (const edge of graph.edges) {
      const fromTile = graph.tiles.get(edge.from)!
      const toTile = graph.tiles.get(edge.to)!

      if (!this.typesCompatible(fromTile.output_type, toTile.input_type)) {
        throw new TypeError(
          `Type mismatch: ${edge.from} output incompatible with ${edge.to} input`
        )
      }
    }

    return this.doTransform(graph)
  }
}
```

### 5.3 Low Confidence

**Symptom:** Transformations are below confidence threshold.

**Solution:**
```typescript
// Improve confidence estimation
class ConfidenceAwareMetaTile implements MetaTile {
  confidence(graph: TileGraph): Confidence {
    // Consider multiple factors
    let confidence = 0.95

    // Factor 1: Complexity
    confidence -= graph.tiles.size * 0.005

    // Factor 2: Number of transformations
    confidence -= this.countTransformations(graph) * 0.01

    // Factor 3: Historical accuracy
    confidence *= this.historicalAccuracy

    // Factor 4: Graph quality
    confidence *= this.assessGraphQuality(graph)

    return {
      value: Math.max(0, Math.min(1, confidence)),
      zone: this.classifyZone(confidence),
      source: this.id,
      timestamp: Date.now()
    }
  }
}
```

### 5.4 Broken Constraints

**Symptom:** Constraints violated after transformation.

**Solution:**
```typescript
// Declare which constraints you break
class HonestMetaTile implements MetaTile {
  preserved_constraints = [
    ConstraintSet.TypeSafety
  ]

  broken_constraints = [
    ConstraintSet.IndividualTileIdentity  // We merge tiles, so identities change
  ]

  transform(graph: TileGraph): TileGraph {
    const result = this.doTransform(graph)

    // Verify preserved constraints
    for (const constraint of this.preserved_constraints) {
      if (!this.verifyConstraint(result, constraint)) {
        throw new Error(
          `Failed to preserve constraint: ${constraint}`
        )
      }
    }

    return result
  }
}
```

---

## 6. Examples

### 6.1 Complete Example: Auto-Tile Generator

```typescript
import { MetaTile, TileGraph, Tile, Confidence } from '@polln/spreadsheet'

/**
 * Automatically generates tiles from datasets
 */
class AutoTileGenerator implements MetaTile<TileGraph, TileGraph> {
  id = 'auto_tile_generator'
  level = 1
  description = 'Generate tiles from datasets'

  preserved_constraints = [
    ConstraintSet.TypeSafety,
    ConstraintSet.ConfidenceMonotonicity
  ]

  broken_constraints = []

  transform(graph: TileGraph): TileGraph {
    // Find datasets in the graph
    const datasets = this.findDatasets(graph)

    // Generate a tile for each dataset
    for (const dataset of datasets) {
      const tile = this.generateTile(dataset)

      // Add tile to graph
      graph.tiles.set(tile.id, tile)

      // Connect to dataset
      graph.edges.push({
        from: dataset.id,
        to: tile.id,
        type: 'sequential'
      })
    }

    return graph
  }

  private generateTile(dataset: Dataset): Tile {
    // Extract examples
    const examples = dataset.examples

    // Infer types
    const inputType = this.inferType(examples.map(e => e.input))
    const outputType = this.inferType(examples.map(e => e.output))

    // Train model
    const model = this.trainModel(examples)

    // Calculate confidence
    const confidence = this.evaluateModel(model, examples)

    // Infer constraints
    const constraints = this.inferConstraints(examples)

    return {
      id: this.generateId(),
      description: `Auto-generated tile from dataset ${dataset.id}`,
      input_type: inputType,
      output_type: outputType,
      constraints: constraints,
      base_confidence: confidence,
      has_side_effects: false,
      discriminate: (input) => model.predict(input),
      confidence: (input) => model.predictConfidence(input),
      trace: (input) => model.explain(input)
    }
  }

  confidence(graph: TileGraph): Confidence {
    // Confidence depends on dataset quality
    const datasets = this.findDatasets(graph)
    const avgQuality = datasets.reduce((sum, d) =>
      sum + this.assessQuality(d), 0
    ) / datasets.length

    return {
      value: avgQuality,
      zone: avgQuality > 0.85 ? 'GREEN' : avgQuality > 0.60 ? 'YELLOW' : 'RED',
      source: this.id,
      timestamp: Date.now()
    }
  }

  safety(graph: TileGraph): SafetyScore {
    // Safe if datasets are valid
    const datasets = this.findDatasets(graph)
    const invalidDatasets = datasets.filter(d => !this.isValid(d))

    return {
      score: 1.0 - (invalidDatasets.length / datasets.length) * 0.5,
      violations: invalidDatasets.map(d => ({
        type: 'invalid_dataset',
        dataset_id: d.id,
        message: `Dataset ${d.id} is invalid`
      }))
    }
  }

  explain(graph: TileGraph): string {
    const datasets = this.findDatasets(graph)
    return `Generated ${datasets.length} tiles from datasets`
  }

  input_schema = {}
  output_schema = {}

  // Helper methods
  private findDatasets(graph: TileGraph): Dataset[] {
    return Array.from(graph.tiles.values())
      .filter(tile => tile.type === 'dataset')
      .map(tile => tile as any as Dataset)
  }

  private inferType(values: any[]): TypeConstraint {
    // Simple type inference
    if (values.every(v => typeof v === 'string')) {
      return { type: 'string', optional: false }
    } else if (values.every(v => typeof v === 'number')) {
      return { type: 'number', optional: false }
    } else if (values.every(v => typeof v === 'boolean')) {
      return { type: 'boolean', optional: false }
    } else if (values.every(v => Array.isArray(v))) {
      return { type: 'array', optional: false }
    } else {
      return { type: 'object', optional: false }
    }
  }

  private trainModel(examples: Example[]): MLModel {
    // Try different models and return best
    const models = [
      this.trainDecisionTree(examples),
      this.trainNeuralNetwork(examples),
      this.trainSVM(examples)
    ]

    return models.sort((a, b) => b.accuracy - a.accuracy)[0]
  }

  private evaluateModel(model: MLModel, examples: Example[]): number {
    const correct = examples.filter(e =>
      model.predict(e.input) === e.output
    ).length

    return correct / examples.length
  }

  private inferConstraints(examples: Example[]): ConstraintBound[] {
    // Infer constraints from examples
    const constraints: ConstraintBound[] = []

    if (examples.length === 0) return constraints

    // For numeric fields, infer min/max
    const firstInput = examples[0].input
    for (const key of Object.keys(firstInput)) {
      const values = examples.map(e => e.input[key])

      if (values.every(v => typeof v === 'number')) {
        constraints.push({
          variable: key,
          min: Math.min(...values),
          max: Math.max(...values),
          required: true,
          description: `${key} range inferred from data`
        })
      }
    }

    return constraints
  }

  private assessQuality(dataset: Dataset): number {
    // Assess dataset quality
    let quality = 1.0

    // Reduce if small dataset
    if (dataset.examples.length < 10) {
      quality -= 0.3
    }

    // Reduce if inconsistent
    if (this.hasInconsistencies(dataset)) {
      quality -= 0.2
    }

    // Reduce if outliers
    if (this.hasOutliers(dataset)) {
      quality -= 0.1
    }

    return Math.max(0, quality)
  }

  private isValid(dataset: Dataset): boolean {
    return dataset.examples.length > 0 &&
           !this.hasInconsistencies(dataset)
  }

  private hasInconsistencies(dataset: Dataset): boolean {
    // Check for inconsistent examples
    const inputMap = new Map<string, any[]>()

    for (const example of dataset.examples) {
      const key = JSON.stringify(example.input)
      if (!inputMap.has(key)) {
        inputMap.set(key, [])
      }
      inputMap.get(key)!.push(example.output)
    }

    // Check if any input has multiple different outputs
    for (const [input, outputs] of inputMap) {
      const uniqueOutputs = new Set(outputs.map(o => JSON.stringify(o)))
      if (uniqueOutputs.size > 1) {
        return true
      }
    }

    return false
  }

  private hasOutliers(dataset: Dataset): boolean {
    // Simple outlier detection
    const values = dataset.examples.map(e =>
      Object.values(e.input).filter(v => typeof v === 'number')
    ).flat()

    if (values.length === 0) return false

    const mean = values.reduce((a, b) => a + b, 0) / values.length
    const std = Math.sqrt(
      values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length
    )

    return values.some(v => Math.abs(v - mean) > 3 * std)
  }

  private generateId(): string {
    return `tile_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // Placeholder methods for model training
  private trainDecisionTree(examples: Example[]): MLModel {
    // Implementation would train a decision tree
    return {} as MLModel
  }

  private trainNeuralNetwork(examples: Example[]): MLModel {
    // Implementation would train a neural network
    return {} as MLModel
  }

  private trainSVM(examples: Example[]): MLModel {
    // Implementation would train an SVM
    return {} as MLModel
  }
}

// Usage
const generator = new AutoTileGenerator()
const graph = generator.transform(myTileGraph)
console.log(generator.explain(graph))  // → "Generated 3 tiles from datasets"
```

### 6.2 Complete Example: Confidence Booster

```typescript
/**
 * Boost confidence by adding parallel verification tiles
 */
class ConfidenceBooster implements MetaTile<TileGraph, TileGraph> {
  id = 'confidence_booster'
  level = 1
  description = 'Boost confidence by adding parallel verification'

  preserved_constraints = [
    ConstraintSet.TypeSafety,
    ConstraintSet.ConfidenceMonotonicity
  ]

  broken_constraints = [
    ConstraintSet.IndividualTileIdentity  // We add/modify tiles
  ]

  transform(graph: TileGraph): TileGraph {
    // Find low-confidence tiles
    const lowConfidence = this.findLowConfidenceTiles(graph)

    // Boost each one
    for (const tileId of lowConfidence) {
      graph = this.boostTile(graph, tileId)
    }

    return graph
  }

  private boostTile(graph: TileGraph, tileId: string): TileGraph {
    const originalTile = graph.tiles.get(tileId)!

    // Create variants
    const variants = this.createVariants(originalTile)

    // Create ensemble
    const ensemble = this.createEnsemble([originalTile, ...variants])

    // Replace original with ensemble
    graph.tiles.set(tileId, ensemble)

    // Add variants to graph
    for (const variant of variants) {
      graph.tiles.set(variant.id, variant)
    }

    // Rewire edges
    this.rewireForEnsemble(graph, tileId, ensemble, variants)

    return graph
  }

  private createVariants(tile: Tile): Tile[] {
    const variants: Tile[] = []

    // Conservative variant
    variants.push({
      ...tile,
      id: `${tile.id}_conservative`,
      base_confidence: tile.base_confidence * 0.95,
      description: `${tile.description} (conservative)`
    })

    // Alternative model variant
    variants.push({
      ...tile,
      id: `${tile.id}_alternative`,
      base_confidence: tile.base_confidence * 0.90,
      description: `${tile.description} (alternative model)`
    })

    return variants
  }

  private createEnsemble(tiles: Tile[]): Tile {
    return {
      id: this.generateId(),
      description: `Ensemble of ${tiles.length} tiles`,
      input_type: tiles[0].input_type,
      output_type: tiles[0].output_type,
      constraints: tiles[0].constraints,
      base_confidence: Math.max(...tiles.map(t => t.base_confidence)),
      has_side_effects: tiles.some(t => t.has_side_effects),
      discriminate: (input) => {
        const results = tiles.map(t => t.discriminate(input))
        return this.majorityVote(results)
      },
      confidence: (input) => {
        const confidences = tiles.map(t => t.confidence(input))
        return confidences.reduce((a, b) => a + b, 0) / confidences.length
      },
      trace: (input) => {
        return tiles.map(t => t.trace(input)).join('\n')
      }
    }
  }

  private majorityVote(results: any[]): any {
    // Simple majority vote
    const counts = new Map<string, number>()

    for (const result of results) {
      const key = JSON.stringify(result)
      counts.set(key, (counts.get(key) || 0) + 1)
    }

    // Return most common result
    let maxCount = 0
    let maxKey = ''
    for (const [key, count] of counts) {
      if (count > maxCount) {
        maxCount = count
        maxKey = key
      }
    }

    return JSON.parse(maxKey)
  }

  private findLowConfidenceTiles(graph: TileGraph): string[] {
    return Array.from(graph.tiles.entries())
      .filter(([id, tile]) => tile.base_confidence < 0.85)
      .map(([id]) => id)
  }

  private rewireForEnsemble(
    graph: TileGraph,
    originalId: string,
    ensemble: Tile,
    variants: Tile[]
  ): void {
    // Find all incoming edges to original tile
    const incoming = graph.edges.filter(e => e.to === originalId)

    // Redirect them to point to ensemble input
    for (const edge of incoming) {
      edge.to = ensemble.id
    }

    // Add edges from ensemble to variants
    for (const variant of variants) {
      graph.edges.push({
        from: ensemble.id,
        to: variant.id,
        type: 'parallel'
      })
    }

    // Find all outgoing edges from original tile
    const outgoing = graph.edges.filter(e => e.from === originalId)

    // Redirect them to come from ensemble output
    for (const edge of outgoing) {
      edge.from = ensemble.id
    }
  }

  confidence(graph: TileGraph): Confidence {
    const lowConfidence = this.findLowConfidenceTiles(graph)
    const boostAmount = lowConfidence.length * 0.05

    return {
      value: Math.min(1.0, 0.90 + boostAmount),
      zone: 'GREEN',
      source: this.id,
      timestamp: Date.now()
    }
  }

  safety(graph: TileGraph): SafetyScore {
    // Safe if we're not creating inconsistencies
    return {
      score: 0.95,
      violations: []
    }
  }

  explain(graph: TileGraph): string {
    const lowConfidence = this.findLowConfidenceTiles(graph)
    return `Boosted confidence for ${lowConfidence.length} tiles`
  }

  input_schema = {}
  output_schema = {}

  private generateId(): string {
    return `ensemble_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
}

// Usage
const booster = new ConfidenceBooster()
const optimized = booster.transform(myTileGraph)
console.log(booster.explain(optimized))  // → "Boosted confidence for 5 tiles"
```

---

## Conclusion

Meta-tiles give you the power to program the SMP tile system itself. With these patterns and examples, you can:

1. **Generate tiles** automatically from data
2. **Optimize** tile graphs for performance
3. **Analyze** tile properties and metrics
4. **Compose** complex pipelines
5. **Validate** tile graph safety

**Remember:**
- Always declare your stratification level
- Preserve constraints when possible
- Provide explanations for transformations
- Calculate confidence accurately
- Test thoroughly before deploying

Happy meta-programming!

---

*Meta-Tile Quick Start v1.0 | POLLN Research | 2026-03-10*
