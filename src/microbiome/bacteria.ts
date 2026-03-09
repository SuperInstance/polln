/**
 * POLLN Microbiome - Bacteria/Protozoa Agents
 *
 * Full agents with specific metabolic needs.
 * Size: 1KB - 1MB
 * Metabolism: Consumes specific data types
 * Goal: Process data, reproduce when successful
 *
 * @module microbiome/bacteria
 */

import { v4 as uuidv4 } from 'uuid';
import {
  BacteriaAgent,
  AgentTaxonomy,
  ResourceType,
  MetabolicProfile,
  LifecycleState,
  FitnessScore,
  MutationConfig,
  MutationType,
} from './types.js';

/**
 * Processing function type
 */
export type ProcessingFunction = (
  input: Map<ResourceType, any>
) => Promise<Map<ResourceType, any>>;

/**
 * Base Bacteria Agent Implementation
 *
 * Bacteria are full agents with metabolic needs.
 * They consume specific data types and produce outputs.
 */
export class BaseBacteria implements BacteriaAgent {
  id: string;
  taxonomy: AgentTaxonomy.BACTERIA = AgentTaxonomy.BACTERIA;
  name: string;
  metabolism: MetabolicProfile;
  lifecycle: LifecycleState;
  parentId?: string;
  generation: number;
  size: number;
  complexity: number;

  reproductionThreshold: number;
  accumulatedResources: number;
  dependencies: string[];

  /** Processing function */
  private processor: ProcessingFunction;

  /** Processing statistics */
  private processedCount: number = 0;
  private successCount: number = 0;
  private totalProcessingTime: number = 0;

  constructor(config: {
    name?: string;
    inputs: ResourceType[];
    outputs: ResourceType[];
    processingRate?: number;
    efficiency?: number;
    processor: ProcessingFunction;
    reproductionThreshold?: number;
    dependencies?: string[];
    parentId?: string;
    generation?: number;
    size?: number;
    complexity?: number;
  }) {
    this.id = uuidv4();
    this.name = config.name || `Bacteria_${this.id.slice(0, 8)}`;

    this.metabolism = {
      inputs: config.inputs,
      outputs: config.outputs,
      processingRate: config.processingRate ?? 10,
      efficiency: config.efficiency ?? 0.7,
    };

    this.processor = config.processor;
    this.reproductionThreshold = config.reproductionThreshold ?? 1000;
    this.accumulatedResources = 0;
    this.dependencies = config.dependencies ?? [];
    this.parentId = config.parentId;
    this.generation = config.generation ?? 0;
    this.size = config.size ?? Math.floor(1024 + Math.random() * (1024 * 1024 - 1024));
    this.complexity = config.complexity ?? 0.5;

    this.lifecycle = {
      health: 1.0,
      age: 0,
      generation: this.generation,
      isAlive: true,
    };
  }

  /**
   * Check if can metabolize given resources
   */
  canMetabolize(resources: Map<ResourceType, number>): boolean {
    // Check if any required input is available
    for (const input of this.metabolism.inputs) {
      if (resources.has(input) && resources.get(input)! > 0) {
        return true;
      }
    }
    return false;
  }

  /**
   * Process resources
   */
  async process(resources: Map<ResourceType, number>): Promise<Map<ResourceType, number>> {
    if (!this.lifecycle.isAlive) {
      return new Map();
    }

    const startTime = Date.now();
    this.processedCount++;

    try {
      // Convert resource counts to actual data
      const inputData = new Map<ResourceType, any>();
      for (const input of this.metabolism.inputs) {
        const amount = resources.get(input) || 0;
        if (amount > 0) {
          inputData.set(input, amount);
        }
      }

      // Process using the processor function
      const outputData = await this.processor(inputData);

      // Convert output data back to resource counts
      const outputCounts = new Map<ResourceType, number>();
      for (const output of this.metabolism.outputs) {
        const value = outputData.get(output);
        if (value !== undefined) {
          outputCounts.set(output, Number(value) || 1);
        }
      }

      // Update success metrics
      this.successCount++;
      this.accumulatedResources += this.metabolism.processingRate * this.metabolism.efficiency;

      // Check reproduction threshold
      if (this.accumulatedResources >= this.reproductionThreshold) {
        this.lifecycle.health = Math.min(1.0, this.lifecycle.health + 0.1);
      }

      const processingTime = Date.now() - startTime;
      this.totalProcessingTime += processingTime;

      return outputCounts;
    } catch (error) {
      // Processing failed
      this.lifecycle.health -= 0.1;
      if (this.lifecycle.health <= 0) {
        this.lifecycle.isAlive = false;
      }
      return new Map();
    }
  }

  /**
   * Reproduce (asexual with mutation)
   */
  async reproduce(config: MutationConfig): Promise<BaseBacteria> {
    if (!this.lifecycle.isAlive) {
      throw new Error('Dead bacteria cannot reproduce');
    }

    if (this.accumulatedResources < this.reproductionThreshold) {
      throw new Error('Insufficient resources to reproduce');
    }

    // Reset accumulated resources
    this.accumulatedResources = 0;

    // Check for mutation
    let inputs = [...this.metabolism.inputs];
    let outputs = [...this.metabolism.outputs];
    let processingRate = this.metabolism.processingRate;
    let efficiency = this.metabolism.efficiency;
    let dependencies = [...this.dependencies];

    if (Math.random() < config.mutationRate) {
      const mutationType = config.mutationTypes[
        Math.floor(Math.random() * config.mutationTypes.length)
      ];

      switch (mutationType) {
        case MutationType.GOAL_ADJUSTMENT:
          // Adjust processing parameters
          processingRate = Math.max(1, processingRate * (1 + (Math.random() - 0.5) * config.maxMutationImpact));
          efficiency = Math.max(0.1, Math.min(1.0, efficiency * (1 + (Math.random() - 0.5) * config.maxMutationImpact * 0.5)));
          break;

        case MutationType.METHOD_VARIATION:
          // Change efficiency (different algorithm)
          efficiency = Math.max(0.1, Math.min(1.0, efficiency + (Math.random() - 0.5) * config.maxMutationImpact));
          break;

        case MutationType.METABOLIC_SHIFT:
          // Add or remove input/output
          if (Math.random() < 0.5 && inputs.length < 5) {
            // Add new input
            const newInput = this.getRandomResourceType();
            if (!inputs.includes(newInput)) {
              inputs.push(newInput);
            }
          } else if (outputs.length < 5) {
            // Add new output
            const newOutput = this.getRandomResourceType();
            if (!outputs.includes(newOutput)) {
              outputs.push(newOutput);
            }
          }
          break;

        case MutationType.SYMBIOSIS_GAIN:
          // Add dependency (symbiosis with another agent)
          // This would be populated with actual agent IDs in a real system
          dependencies.push(`dependency_${Math.random().toString(36).slice(2, 8)}`);
          break;
      }
    }

    // Create child bacteria
    const child = new BaseBacteria({
      name: `${this.name}_v${this.generation + 1}`,
      inputs,
      outputs,
      processingRate,
      efficiency,
      processor: this.processor, // Inherit processor
      reproductionThreshold: this.reproductionThreshold,
      dependencies,
      parentId: this.id,
      generation: this.generation + 1,
      size: Math.floor(this.size * (0.9 + Math.random() * 0.2)), // Size variation
      complexity: this.complexity,
    });

    return child;
  }

  /**
   * Evaluate fitness
   */
  evaluateFitness(): FitnessScore {
    const successRate = this.processedCount > 0 ? this.successCount / this.processedCount : 0;
    const avgProcessingTime = this.processedCount > 0 ? this.totalProcessingTime / this.processedCount : 0;
    const throughput = this.processedCount / Math.max(1, this.lifecycle.age / 1000); // per second

    return {
      overall: (successRate * 0.4 + this.metabolism.efficiency * 0.3 + this.lifecycle.health * 0.3),
      throughput: Math.min(1, throughput / this.metabolism.processingRate),
      accuracy: successRate,
      efficiency: this.metabolism.efficiency,
      cooperation: this.dependencies.length > 0 ? 0.5 : 0, // Has symbiotic relationships
    };
  }

  /**
   * Age the bacteria
   */
  age(deltaMs: number): void {
    this.lifecycle.age += deltaMs;

    // Health decreases without resources
    if (this.accumulatedResources < this.metabolism.processingRate) {
      this.lifecycle.health -= 0.01 * (deltaMs / 1000);
    }

    if (this.lifecycle.health <= 0) {
      this.lifecycle.isAlive = false;
    }
  }

  /**
   * Get statistics
   */
  getStats() {
    return {
      processedCount: this.processedCount,
      successCount: this.successCount,
      successRate: this.processedCount > 0 ? this.successCount / this.processedCount : 0,
      avgProcessingTime: this.processedCount > 0 ? this.totalProcessingTime / this.processedCount : 0,
      accumulatedResources: this.accumulatedResources,
      canReproduce: this.accumulatedResources >= this.reproductionThreshold,
    };
  }

  /**
   * Get a random resource type
   */
  private getRandomResourceType(): ResourceType {
    const types = Object.values(ResourceType);
    return types[Math.floor(Math.random() * types.length)];
  }
}

/**
 * Text Parser Bacteria
 *
 * Processes raw text and outputs sentences
 */
export class TextParserBacteria extends BaseBacteria {
  constructor() {
    super({
      name: 'TextParser_vibrio',
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100, // sentences per second
      efficiency: 0.8,
      reproductionThreshold: 1000, // 1000 sentences
      processor: async (input) => {
        const textAmount = input.get(ResourceType.TEXT) || 0;
        // Simulate parsing text into sentences
        const sentenceCount = Math.floor(textAmount / 100); // Approx 100 chars per sentence
        const output = new Map();
        output.set(ResourceType.STRUCTURED, sentenceCount);
        return output;
      },
    });
  }
}

/**
 * Sentiment Analysis Protozoa
 *
 * Processes sentences and outputs sentiment
 */
export class SentimentProtozoa extends BaseBacteria {
  constructor() {
    super({
      name: 'SentimentAnalysis_ameoba',
      inputs: [ResourceType.STRUCTURED],
      outputs: [ResourceType.STRUCTURED], // Sentiment is structured data
      processingRate: 50, // sentences per second
      efficiency: 0.7,
      reproductionThreshold: 500, // 500 sentences
      dependencies: ['TextParser_vibrio'], // Depends on text parser
      processor: async (input) => {
        const sentenceCount = input.get(ResourceType.STRUCTURED) || 0;
        // Simulate sentiment analysis
        const output = new Map();
        output.set(ResourceType.STRUCTURED, sentenceCount); // Same number with sentiment added
        return output;
      },
    });
  }
}

/**
 * Audio Feature Extractor Bacteria
 *
 * Processes audio and outputs features
 */
export class AudioFeatureBacteria extends BaseBacteria {
  constructor() {
    super({
      name: 'AudioFeature_bacteria',
      inputs: [ResourceType.AUDIO],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 10, // frames per second
      efficiency: 0.6,
      reproductionThreshold: 300, // 30 seconds of audio
      processor: async (input) => {
        const audioAmount = input.get(ResourceType.AUDIO) || 0;
        // Simulate feature extraction
        const featureCount = Math.floor(audioAmount / 10);
        const output = new Map();
        output.set(ResourceType.STRUCTURED, featureCount);
        return output;
      },
    });
  }
}

/**
 * Code Reviewer Bacteria
 *
 * Processes code and outputs reviews
 */
export class CodeReviewerBacteria extends BaseBacteria {
  constructor() {
    super({
      name: 'CodeReview_bacteria',
      inputs: [ResourceType.CODE],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 5, // lines per second
      efficiency: 0.75,
      reproductionThreshold: 200, // 200 lines reviewed
      processor: async (input) => {
        const lineCount = input.get(ResourceType.CODE) || 0;
        // Simulate code review
        const output = new Map();
        output.set(ResourceType.STRUCTURED, Math.floor(lineCount / 10)); // Reviews per 10 lines
        return output;
      },
    });
  }
}

/**
 * Compression Bacteria
 *
 * Compresses data for storage
 */
export class CompressionBacteria extends BaseBacteria {
  constructor() {
    super({
      name: 'Compression_bacteria',
      inputs: [ResourceType.TEXT, ResourceType.STRUCTURED, ResourceType.CODE],
      outputs: [ResourceType.ANCHORS], // Compressed KV-cache anchors
      processingRate: 1000, // bytes per second
      efficiency: 0.85,
      reproductionThreshold: 10000, // 10KB compressed
      processor: async (input) => {
        let totalBytes = 0;
        for (const [_, amount] of input.entries()) {
          totalBytes += amount;
        }
        // Simulate compression (typically 2-5x reduction)
        const compressedSize = Math.floor(totalBytes / 3);
        const output = new Map();
        output.set(ResourceType.ANCHORS, compressedSize);
        return output;
      },
    });
  }
}

/**
 * Bacteria factory - create common bacteria types
 */
export const BacteriaFactory = {
  textParser: () => new TextParserBacteria(),
  sentiment: () => new SentimentProtozoa(),
  audioFeature: () => new AudioFeatureBacteria(),
  codeReviewer: () => new CodeReviewerBacteria(),
  compression: () => new CompressionBacteria(),

  custom: (config: {
    inputs: ResourceType[];
    outputs: ResourceType[];
    processor: ProcessingFunction;
    name?: string;
    processingRate?: number;
    efficiency?: number;
  }) => new BaseBacteria({
    ...config,
    reproductionThreshold: config.processingRate * 100,
  }),
};
