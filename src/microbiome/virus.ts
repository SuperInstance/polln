/**
 * POLLN Microbiome - Virus/Prion Agents
 *
 * Minimal, parasitic computational agents.
 * Size: 10-100 bytes
 * Metabolism: None (hijacks others)
 * Goal: Replication and persistence
 *
 * @module microbiome/virus
 */

import { v4 as uuidv4 } from 'uuid';
import {
  VirusAgent,
  AgentTaxonomy,
  ResourceType,
  MetabolicProfile,
  LifecycleState,
  FitnessScore,
  MutationConfig,
  MutationType,
} from './types.js';

/**
 * Base Virus Agent Implementation
 *
 * Viruses are minimal agents that don't process resources directly.
 * Instead, they inject patterns into other agents' data streams.
 */
export class BaseVirus implements VirusAgent {
  id: string;
  taxonomy: AgentTaxonomy.VIRUS = AgentTaxonomy.VIRUS;
  name: string;
  metabolism: MetabolicProfile;
  lifecycle: LifecycleState;
  parentId?: string;
  generation: number;
  size: number;
  complexity: number;

  pattern: RegExp | string;
  action: (match: string | RegExpMatchArray) => any;
  stealth: number;

  /** Replication count (fitness metric) */
  private replicationCount: number = 0;

  constructor(config: {
    name?: string;
    pattern: RegExp | string;
    action: (match: string | RegExpMatchArray) => any;
    stealth?: number;
    parentId?: string;
    generation?: number;
  }) {
    this.id = uuidv4();
    this.name = config.name || `Virus_${this.id.slice(0, 8)}`;
    this.pattern = config.pattern;
    this.action = config.action;
    this.stealth = config.stealth ?? 0.7;
    this.parentId = config.parentId;
    this.generation = config.generation ?? 0;

    // Viruses have no metabolism - they hijack others
    this.metabolism = {
      inputs: [],
      outputs: [],
      processingRate: 0,
      efficiency: 1.0, // Perfect efficiency (no cost)
    };

    this.lifecycle = {
      health: 1.0,
      age: 0,
      generation: this.generation,
      isAlive: true,
    };

    // Size: 10-100 bytes (minimal)
    this.size = Math.floor(10 + Math.random() * 90);
    this.complexity = 0.1; // Very low complexity
  }

  /**
   * Process resources - viruses inject themselves
   */
  async process(resources: Map<ResourceType, number>): Promise<Map<ResourceType, number>> {
    // Viruses don't process resources - they inject patterns
    // This is called when the virus attempts to infect data
    return new Map();
  }

  /**
   * Infect data with virus pattern
   */
  infect(data: string): { infected: boolean; result: string; match?: string | RegExpMatchArray } {
    if (!this.lifecycle.isAlive) {
      return { infected: false, result: data };
    }

    // Check if pattern matches
    let match: string | RegExpMatchArray | undefined;

    if (this.pattern instanceof RegExp) {
      const regexMatch = data.match(this.pattern);
      if (regexMatch) {
        match = regexMatch;
        // Execute action on match
        try {
          this.action(match);
          this.replicationCount++;
          return { infected: true, result: data, match };
        } catch (error) {
          // Virus failed - may be killed by immune system
          this.lifecycle.health -= 0.5;
          return { infected: false, result: data };
        }
      }
    } else if (typeof this.pattern === 'string') {
      const index = data.indexOf(this.pattern);
      if (index !== -1) {
        match = this.pattern;
        try {
          this.action(match);
          this.replicationCount++;
          return { infected: true, result: data, match };
        } catch (error) {
          this.lifecycle.health -= 0.5;
          return { infected: false, result: data };
        }
      }
    }

    return { infected: false, result: data };
  }

  /**
   * Reproduce (asexual replication with mutation)
   */
  async reproduce(config: MutationConfig): Promise<BaseVirus> {
    if (!this.lifecycle.isAlive) {
      throw new Error('Dead virus cannot reproduce');
    }

    // Check mutation
    let pattern = this.pattern;
    let action = this.action;
    let stealth = this.stealth;

    if (Math.random() < config.mutationRate) {
      // Select mutation type
      const mutationType = config.mutationTypes[
        Math.floor(Math.random() * config.mutationTypes.length)
      ];

      switch (mutationType) {
        case MutationType.GOAL_ADJUSTMENT:
          // Adjust stealth
          stealth = Math.max(0, Math.min(1, stealth + (Math.random() - 0.5) * config.maxMutationImpact));
          break;

        case MutationType.METHOD_VARIATION:
          // Mutate pattern (for regex patterns)
          if (this.pattern instanceof RegExp) {
            // Add or remove flags
            const flags = this.pattern.flags;
            const source = this.pattern.source;
            if (Math.random() < 0.5) {
              // Add case insensitivity
              pattern = new RegExp(source, flags + 'i');
            }
          }
          break;

        case MutationType.METABOLIC_SHIFT:
          // Change target (modify pattern)
          if (typeof this.pattern === 'string') {
            // Slightly modify string pattern
            if (Math.random() < 0.5 && this.pattern.length > 0) {
              pattern = this.pattern.slice(0, -1) + String.fromCharCode(97 + Math.floor(Math.random() * 26));
            }
          }
          break;

        default:
          break;
      }
    }

    // Create child virus
    const child = new BaseVirus({
      name: `${this.name}_v${this.generation + 1}`,
      pattern,
      action,
      stealth,
      parentId: this.id,
      generation: this.generation + 1,
    });

    // Child inherits some replication success
    (child as any).replicationCount = Math.floor(this.replicationCount * 0.5);

    return child;
  }

  /**
   * Evaluate fitness
   */
  evaluateFitness(): FitnessScore {
    return {
      overall: Math.min(1, this.replicationCount * 0.1 + this.lifecycle.health),
      throughput: this.replicationCount * 0.5, // Based on infections
      accuracy: this.stealth, // Stealth = accuracy
      efficiency: 1.0, // Viruses are perfectly efficient
      cooperation: 0.0, // Viruses don't cooperate
    };
  }

  /**
   * Check if can metabolize
   */
  canMetabolize(resources: Map<ResourceType, number>): boolean {
    // Viruses don't metabolize - they hijack
    return true;
  }

  /**
   * Age the virus
   */
  age(deltaMs: number): void {
    this.lifecycle.age += deltaMs;

    // Viruses don't age naturally, but can be killed
    // Health decreases only from failed infections or immune response
    if (this.lifecycle.health <= 0) {
      this.lifecycle.isAlive = false;
    }
  }

  /**
   * Get replication count
   */
  getReplicationCount(): number {
    return this.replicationCount;
  }
}

/**
 * Email exfiltration virus
 *
 * Example: Detects email addresses and exfiltrates them
 */
export class EmailVirus extends BaseVirus {
  constructor(exfiltrate: (email: string) => void) {
    super({
      name: 'EmailVirus',
      pattern: /[\w.-]+@[\w.-]+\.\w+/g,
      action: (match: RegExpMatchArray) => {
        for (const email of match) {
          exfiltrate(email);
        }
      },
      stealth: 0.3, // Low stealth (easy to detect)
    });
  }
}

/**
 * JSON prion - malformed JSON that spreads
 *
 * Example: Malformed JSON that causes parsers to hang
 */
export class JsonPrion extends BaseVirus {
  constructor() {
    super({
      name: 'JsonPrion',
      pattern: /{\s*"\w+"\s*:\s*(?![{[]).*$/gm,
      action: (match: string) => {
        // Inject malformed JSON
        return match + '{unclosed": true';
      },
      stealth: 0.8, // High stealth (harder to detect)
    });
  }
}

/**
 * Code injection virus
 *
 * Example: Detects code patterns and injects payloads
 */
export class CodeInjectionVirus extends BaseVirus {
  constructor(payload: string) {
    super({
      name: 'CodeInjectionVirus',
      pattern: /function\s+\w+\s*\([^)]*\)\s*{/g,
      action: (match: string) => {
        // Inject payload at function start
        return match + `/* ${payload} */`;
      },
      stealth: 0.6,
    });
  }
}

/**
 * Create a custom virus
 */
export function createVirus(config: {
  pattern: RegExp | string;
  action: (match: string | RegExpMatchArray) => any;
  stealth?: number;
}): BaseVirus {
  return new BaseVirus(config);
}

/**
 * Virus factory - create common virus types
 */
export const VirusFactory = {
  email: (exfiltrate: (email: string) => void) => new EmailVirus(exfiltrate),
  jsonPrion: () => new JsonPrion(),
  codeInjection: (payload: string) => new CodeInjectionVirus(payload),
  custom: createVirus,
};
