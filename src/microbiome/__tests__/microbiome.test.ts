/**
 * POLLN Microbiome Tests
 *
 * Comprehensive tests for the microbiome architecture.
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import {
  DigitalTerrarium,
  createTerrarium,
  EcosystemEvent,
  AgentTaxonomy,
  ResourceType,
  MutationType,
} from '../index.js';
import {
  BaseVirus,
  VirusFactory,
  BaseBacteria,
  BacteriaFactory,
} from '../index.js';
import { ResourcePool, MetabolicChamber, MetabolismManager } from '../metabolism.js';
import { PopulationDynamicsEngine, createPopulationEngine, analyzePopulationSeries } from '../population.js';

describe('Virus Agents', () => {
  it('should create a virus with pattern and action', () => {
    let infected = false;
    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => { infected = true; },
      stealth: 0.7,
    });

    expect(virus.taxonomy).toBe(AgentTaxonomy.VIRUS);
    expect(virus.stealth).toBe(0.7);
    expect(virus.size).toBeGreaterThanOrEqual(10);
    expect(virus.size).toBeLessThanOrEqual(100);
  });

  it('should infect data matching pattern', () => {
    let matchCount = 0;
    const virus = new BaseVirus({
      pattern: /email/g,
      action: () => { matchCount++; },
    });

    const result = virus.infect('This is an email test');
    expect(result.infected).toBe(true);
    expect(matchCount).toBe(1);
  });

  it('should not infect data not matching pattern', () => {
    const virus = new BaseVirus({
      pattern: /email/g,
      action: () => {},
    });

    const result = virus.infect('This is a test without the keyword');
    expect(result.infected).toBe(false);
  });

  it('should reproduce with mutation', async () => {
    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => {},
      stealth: 0.5,
    });

    // Set up reproduction conditions
    (virus as any).replicationCount = 100;

    const child = await virus.reproduce({
      mutationRate: 1.0, // Force mutation
      mutationTypes: [MutationType.GOAL_ADJUSTMENT],
      maxMutationImpact: 0.5,
    });

    expect(child.parentId).toBe(virus.id);
    expect(child.generation).toBe(virus.generation + 1);
  });

  it('should evaluate fitness correctly', () => {
    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => {},
    });

    // Infect some data to increase fitness
    virus.infect('test data');

    const fitness = virus.evaluateFitness();
    expect(fitness.overall).toBeGreaterThan(0);
    expect(fitness.efficiency).toBe(1.0); // Viruses are perfectly efficient
    expect(fitness.cooperation).toBe(0.0); // Viruses don't cooperate
  });

  it('should create factory viruses', () => {
    let exfiltrated: string[] = [];
    const emailVirus = VirusFactory.email((email) => exfiltrated.push(email));
    expect(emailVirus.name).toBe('EmailVirus');

    const prion = VirusFactory.jsonPrion();
    expect(prion.name).toBe('JsonPrion');

    const codeInjector = VirusFactory.codeInjection('payload');
    expect(codeInjector.name).toBe('CodeInjectionVirus');
  });
});

describe('Bacteria Agents', () => {
  it('should create a bacteria with metabolism', () => {
    const bacteria = new BaseBacteria({
      name: 'TestBacteria',
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async (input) => {
        const output = new Map();
        output.set(ResourceType.STRUCTURED, 1);
        return output;
      },
    });

    expect(bacteria.taxonomy).toBe(AgentTaxonomy.BACTERIA);
    expect(bacteria.metabolism.inputs).toContain(ResourceType.TEXT);
    expect(bacteria.metabolism.outputs).toContain(ResourceType.STRUCTURED);
    expect(bacteria.size).toBeGreaterThanOrEqual(1024);
  });

  it('should process resources', async () => {
    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100,
      efficiency: 0.8,
      processor: async (input) => {
        const text = input.get(ResourceType.TEXT) || 0;
        const output = new Map();
        output.set(ResourceType.STRUCTURED, Math.floor(text / 100));
        return output;
      },
    });

    const resources = new Map([[ResourceType.TEXT, 500]]);
    const outputs = await bacteria.process(resources);

    expect(outputs.get(ResourceType.STRUCTURED)).toBe(5);
  });

  it('should accumulate resources toward reproduction', async () => {
    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 10,
      efficiency: 0.8,
      reproductionThreshold: 50,
      processor: async (input) => {
        const output = new Map();
        output.set(ResourceType.STRUCTURED, 1);
        return output;
      },
    });

    // Process multiple times
    for (let i = 0; i < 10; i++) {
      await bacteria.process(new Map([[ResourceType.TEXT, 100]]));
    }

    const stats = bacteria.getStats();
    expect(stats.canReproduce).toBe(true);
  });

  it('should reproduce when threshold reached', async () => {
    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 10,
      efficiency: 0.8,
      reproductionThreshold: 10,
      processor: async (input) => {
        const output = new Map();
        output.set(ResourceType.STRUCTURED, 1);
        return output;
      },
    });

    // Accumulate resources
    (bacteria as any).accumulatedResources = 20;

    const child = await bacteria.reproduce({
      mutationRate: 0,
      mutationTypes: [],
      maxMutationImpact: 0.2,
    });

    expect(child.parentId).toBe(bacteria.id);
    expect(child.generation).toBe(bacteria.generation + 1);
    expect((bacteria as any).accumulatedResources).toBeLessThan(20); // Resources consumed
  });

  it('should check if can metabolize resources', () => {
    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    expect(bacteria.canMetabolize(new Map([[ResourceType.TEXT, 100]]))).toBe(true);
    expect(bacteria.canMetabolize(new Map([[ResourceType.AUDIO, 100]]))).toBe(false);
  });

  it('should age and die without resources', () => {
    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    // Age significantly without resources
    bacteria.age(100000); // 100 seconds

    expect(bacteria.lifecycle.health).toBeLessThan(1.0);
  });

  it('should create factory bacteria', () => {
    const textParser = BacteriaFactory.textParser();
    expect(textParser.name).toBe('TextParser_vibrio');

    const sentiment = BacteriaFactory.sentiment();
    expect(sentiment.name).toBe('SentimentAnalysis_ameoba');

    const audio = BacteriaFactory.audioFeature();
    expect(audio.name).toBe('AudioFeature_bacteria');

    const codeReview = BacteriaFactory.codeReviewer();
    expect(codeReview.name).toBe('CodeReview_bacteria');

    const compression = BacteriaFactory.compression();
    expect(compression.name).toBe('Compression_bacteria');
  });
});

describe('Resource Pool', () => {
  it('should add and consume resources', () => {
    const pool = new ResourcePool();

    pool.add(ResourceType.TEXT, 100);
    expect(pool.getAvailable(ResourceType.TEXT)).toBe(100);

    const consumed = pool.consume(ResourceType.TEXT, 30);
    expect(consumed).toBe(30);
    expect(pool.getAvailable(ResourceType.TEXT)).toBe(70);
  });

  it('should not consume more than available', () => {
    const pool = new ResourcePool();

    pool.add(ResourceType.TEXT, 50);
    const consumed = pool.consume(ResourceType.TEXT, 100);

    expect(consumed).toBe(50);
    expect(pool.getAvailable(ResourceType.TEXT)).toBe(0);
  });

  it('should decay flow rates', () => {
    const pool = new ResourcePool();

    pool.add(ResourceType.TEXT, 100);
    expect(pool.getFlowRate(ResourceType.TEXT)).toBe(100);

    pool.decayFlowRates(0.5);
    expect(pool.getFlowRate(ResourceType.TEXT)).toBe(50);
  });
});

describe('Metabolic Chamber', () => {
  it('should feed and process resources', () => {
    const chamber = new MetabolicChamber({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100,
      efficiency: 0.8,
    });

    chamber.feed(new Map([[ResourceType.TEXT, 50]]));
    const inputLevels = chamber.getInputLevels();

    expect(inputLevels.get(ResourceType.TEXT)).toBe(50);
  });

  it('should process resources in ticks', () => {
    const chamber = new MetabolicChamber({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100,
      efficiency: 0.5,
    });

    chamber.feed(new Map([[ResourceType.TEXT, 100]]));
    chamber.process(1000); // 1 second

    const outputLevels = chamber.getOutputLevels();
    expect(outputLevels.get(ResourceType.STRUCTURED)).toBeGreaterThan(0);
  });

  it('should extract outputs', () => {
    const chamber = new MetabolicChamber({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processingRate: 100,
      efficiency: 0.8,
    });

    chamber.feed(new Map([[ResourceType.TEXT, 100]]));
    chamber.process(1000);

    const outputs = chamber.extract();
    expect(outputs.size).toBeGreaterThan(0);

    // After extraction, buffer should be empty
    const outputLevels = chamber.getOutputLevels();
    expect(outputLevels.get(ResourceType.STRUCTURED) || 0).toBe(0);
  });
});

describe('Population Dynamics', () => {
  let engine: PopulationDynamicsEngine;

  beforeEach(() => {
    engine = createPopulationEngine();
  });

  it('should set and get population', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 100);
    expect(engine.getPopulation(AgentTaxonomy.BACTERIA)).toBe(100);
  });

  it('should calculate growth rate', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 50);
    engine.setParams(AgentTaxonomy.BACTERIA, { alpha: 0.2, beta: 0.1, K: 100 });

    const dynamics = engine.getPopulationDynamics(AgentTaxonomy.BACTERIA);
    expect(dynamics?.population).toBe(50);
  });

  it('should update populations', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 10);
    engine.setParams(AgentTaxonomy.BACTERIA, {
      alpha: 0.5,  // High growth
      beta: 0.01,  // Low death
      K: 1000,
    });

    engine.update(1000);

    const newPop = engine.getPopulation(AgentTaxonomy.BACTERIA);
    expect(newPop).toBeGreaterThan(10);
  });

  it('should respect carrying capacity', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 900);
    engine.setParams(AgentTaxonomy.BACTERIA, {
      alpha: 0.1,
      beta: 0.1,
      K: 1000,
    });

    engine.update(1000);

    const newPop = engine.getPopulation(AgentTaxonomy.BACTERIA);
    // Population should be closer to K
    expect(newPop).toBeLessThan(1000);
  });

  it('should get diversity index', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 50);
    engine.setPopulation(AgentTaxonomy.VIRUS, 50);
    engine.setPopulation(AgentTaxonomy.COLONY, 50);

    const diversity = engine.getDiversity();
    expect(diversity).toBeGreaterThan(0);
    expect(diversity).toBeLessThanOrEqual(Math.log(3)); // Max for 3 species
  });

  it('should get dominant species', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 100);
    engine.setPopulation(AgentTaxonomy.VIRUS, 10);
    engine.setPopulation(AgentTaxonomy.COLONY, 20);

    const dominant = engine.getDominantSpecies();
    expect(dominant).toContain(AgentTaxonomy.BACTERIA);
  });

  it('should simulate over time', () => {
    engine.setPopulation(AgentTaxonomy.BACTERIA, 10);
    engine.setParams(AgentTaxonomy.BACTERIA, {
      alpha: 0.2,
      beta: 0.05,
      K: 100,
    });

    const results = engine.simulate(10000, 1000); // 10 seconds, 1s steps

    expect(results.get(AgentTaxonomy.BACTERIA)?.length).toBe(11); // Initial + 10 steps

    // Population should have grown
    const finalPop = results.get(AgentTaxonomy.BACTERIA)?.[10] || 0;
    expect(finalPop).toBeGreaterThan(10);
  });

  it('should analyze population series', () => {
    const series = new Map([
      [AgentTaxonomy.BACTERIA, [10, 20, 30, 40, 50]],
    ]);

    const analysis = analyzePopulationSeries(series);

    expect(analysis.min.get(AgentTaxonomy.BACTERIA)).toBe(10);
    expect(analysis.max.get(AgentTaxonomy.BACTERIA)).toBe(50);
    expect(analysis.mean.get(AgentTaxonomy.BACTERIA)).toBe(30);
  });
});

describe('Digital Terrarium', () => {
  let terrarium: DigitalTerrarium;

  beforeEach(() => {
    terrarium = createTerrarium({
      maxAgents: 100,
      evolutionEnabled: false, // Disable for testing
    });
  });

  afterEach(async () => {
    await terrarium.stop();
  });

  it('should start and stop', async () => {
    await terrarium.start();
    expect(terrarium['running']).toBe(true);

    await terrarium.stop();
    expect(terrarium['running']).toBe(false);
  });

  it('should introduce agents', async () => {
    await terrarium.start();

    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => {},
    });

    const introduced = terrarium.introduce(virus);
    expect(introduced).toBe(true);

    const retrieved = terrarium.getAgent(virus.id);
    expect(retrieved).toBeDefined();
  });

  it('should limit max agents', async () => {
    await terrarium.start();

    const smallTerrarium = createTerrarium({ maxAgents: 5 });
    await smallTerrarium.start();

    // Introduce 6 agents
    for (let i = 0; i < 6; i++) {
      const virus = new BaseVirus({
        pattern: /test/g,
        action: () => {},
      });
      smallTerrarium.introduce(virus);
    }

    // Only 5 should be in
    const health = smallTerrarium.getHealth();
    expect(health.totalAgents).toBeLessThanOrEqual(5);

    await smallTerrarium.stop();
  });

  it('should cull agents', async () => {
    await terrarium.start();

    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => {},
    });

    terrarium.introduce(virus);
    const culled = terrarium.cull(virus.id);
    expect(culled).toBe(true);

    expect(virus.lifecycle.isAlive).toBe(false);
  });

  it('should fertilize with resources', async () => {
    await terrarium.start();

    terrarium.fertilize(ResourceType.TEXT, 1000);

    const pool = terrarium['metabolism'].getResourcePool();
    expect(pool.getAvailable(ResourceType.TEXT)).toBe(1000);
  });

  it('should create colonies', async () => {
    await terrarium.start();

    const agent1 = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    const agent2 = new BaseBacteria({
      inputs: [ResourceType.STRUCTURED],
      outputs: [ResourceType.CODE],
      processor: async () => new Map(),
    });

    terrarium.introduce(agent1);
    terrarium.introduce(agent2);

    const colony = terrarium.graft([agent1.id, agent2.id]);
    expect(colony).toBeDefined();
    expect(colony?.members).toHaveLength(2);
  });

  it('should get ecosystem health', async () => {
    await terrarium.start();

    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => {},
    });

    terrarium.introduce(bacteria);
    terrarium.introduce(virus);

    const health = terrarium.getHealth();
    expect(health.totalAgents).toBe(2);
    expect(health.diversity).toBeGreaterThan(0); // Now we have 2 different species
  });

  it('should execute gardener actions', async () => {
    await terrarium.start();

    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    // Introduce action
    await terrarium.executeAction({
      type: 'introduce',
      params: { agent: bacteria },
    });

    expect(terrarium.getAgent(bacteria.id)).toBeDefined();

    // Fertilize action
    await terrarium.executeAction({
      type: 'fertilize',
      params: { resource: ResourceType.TEXT, amount: 100 },
    });

    // Cull action
    await terrarium.executeAction({
      type: 'cull',
      targetId: bacteria.id,
      params: {},
    });

    expect(bacteria.lifecycle.isAlive).toBe(false);
  });

  it('should emit events', async () => {
    await terrarium.start();

    let eventFired = false;
    terrarium.on(EcosystemEvent.AGENT_BORN, () => {
      eventFired = true;
    });

    const virus = new BaseVirus({
      pattern: /test/g,
      action: () => {},
    });

    terrarium.introduce(virus);
    expect(eventFired).toBe(true);
  });

  it('should simulate ticks', async () => {
    await terrarium.start();

    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    terrarium.introduce(bacteria);
    terrarium.fertilize(ResourceType.TEXT, 1000);

    await terrarium.tick(100);

    expect(bacteria.lifecycle.age).toBeGreaterThan(0);
  });
});

describe('Integration Tests', () => {
  it('should run a complete ecosystem cycle', async () => {
    const terrarium = createTerrarium({
      maxAgents: 50,
      evolutionEnabled: true,
      mutationConfig: {
        mutationRate: 0.1,
        mutationTypes: [MutationType.GOAL_ADJUSTMENT],
        maxMutationImpact: 0.2,
      },
    });

    await terrarium.start();

    // Introduce some bacteria
    for (let i = 0; i < 5; i++) {
      const bacteria = new BaseBacteria({
        inputs: [ResourceType.TEXT],
        outputs: [ResourceType.STRUCTURED],
        processingRate: 10,
        efficiency: 0.8,
        reproductionThreshold: 20,
        processor: async (input) => {
          const text = input.get(ResourceType.TEXT) || 0;
          const output = new Map();
          output.set(ResourceType.STRUCTURED, Math.floor(text / 10));
          return output;
        },
      });
      terrarium.introduce(bacteria);
    }

    // Add resources
    terrarium.fertilize(ResourceType.TEXT, 1000);

    // Run several ticks
    for (let i = 0; i < 10; i++) {
      await terrarium.tick(100);
    }

    const health = terrarium.getHealth();
    expect(health.totalAgents).toBeGreaterThan(0);

    await terrarium.stop();
  });

  it('should maintain equilibrium with resources', async () => {
    const terrarium = createTerrarium({
      maxAgents: 100,
      evolutionEnabled: false,
    });

    await terrarium.start();

    // Introduce bacteria
    const bacteria = new BaseBacteria({
      inputs: [ResourceType.TEXT],
      outputs: [ResourceType.STRUCTURED],
      processor: async () => new Map(),
    });

    terrarium.introduce(bacteria);

    // Continuous resource flow
    for (let i = 0; i < 20; i++) {
      terrarium.fertilize(ResourceType.TEXT, 100);
      await terrarium.tick(100);
    }

    // Agent should still be alive
    expect(bacteria.lifecycle.isAlive).toBe(true);

    await terrarium.stop();
  });
});
