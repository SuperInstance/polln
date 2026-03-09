# Schedule Integration Examples

This document provides concrete examples of integrating auto-generated schedules into POLLN core modules.

## Table of Contents

1. [Value Network Integration](#value-network-integration)
2. [World Model Integration](#world-model-integration)
3. [Plinko Decision Layer](#plinko-decision-layer)
4. [Dreaming Module](#dreaming-module)
5. [META Tiles](#meta-tiles)
6. [Federated Learning](#federated-learning)
7. [Complete Colony Integration](#complete-colony-integration)

---

## Value Network Integration

### File: `src/core/valuenetwork.ts`

**Before Optimization:**
```typescript
export class ValueNetwork {
  private learningRate: number = 0.01;  // Fixed LR

  update(values: Float32Array, rewards: Float32Array) {
    // TD(λ) update
    const tdError = this.computeTDError(values, rewards);
    this.weights.addScaled(tdError, this.learningRate);
  }
}
```

**After Schedule Integration:**
```typescript
import { TDLambdaSchedule } from './schedules';

export class ValueNetwork {
  private lrSchedule: TDLambdaSchedule;
  private step: number = 0;

  constructor() {
    this.lrSchedule = new TDLambdaSchedule();
  }

  update(values: Float32Array, rewards: Float32Array) {
    // Get scheduled learning rate
    const lr = this.lrSchedule.getRate();

    // TD(λ) update with scheduled LR
    const tdError = this.computeTDError(values, rewards);
    this.weights.addScaled(tdError, lr);

    // Advance schedule
    this.lrSchedule.advance();
    this.step++;
  }

  reset() {
    this.lrSchedule.reset();
    this.step = 0;
  }

  // Monitor learning rate
  getLearningRate(): number {
    return this.lrSchedule.getRate();
  }

  getProgress(): number {
    return this.lrSchedule.getProgress();
  }
}
```

---

## World Model Integration

### File: `src/core/worldmodel.ts`

**Before Optimization:**
```typescript
export class WorldModel {
  private encoderLearningRate: number = 0.001;
  private decoderLearningRate: number = 0.001;

  train(batch: Tensor[]) {
    const loss = this.computeVAELoss(batch);
    this.updateWeights(loss);
  }
}
```

**After Schedule Integration:**
```typescript
import { VAESchedule } from './schedules';

export class WorldModel {
  private lrSchedule: VAESchedule;

  constructor() {
    this.lrSchedule = new VAESchedule();
  }

  train(batch: Tensor[]) {
    // Get current learning rate
    const lr = this.lrSchedule.getRate();

    // VAE training with scheduled LR
    const loss = this.computeVAELoss(batch);
    const gradients = this.computeGradients(loss);

    // Apply encoder/decoder updates with scheduled LR
    this.encoderWeights.addScaled(gradients.encoder, lr);
    this.decoderWeights.addScaled(gradients.decoder, lr);

    // Advance schedule
    this.lrSchedule.advance();
  }

  // For dream generation, use lower LR
  generateDream(state: Float32Array): DreamEpisode {
    const originalLr = this.lrSchedule.getRate();

    // Use 10% of current LR for dreaming
    const dreamLr = originalLr * 0.1;

    // Generate dream with reduced LR
    // ... dream generation logic ...

    return dreamEpisode;
  }
}
```

---

## Plinko Decision Layer

### File: `src/core/decision.ts`

**Before Optimization:**
```typescript
export class PlinkoLayer {
  private temperature: number = 1.0;  // Fixed temperature

  select(proposals: Proposal[]): Proposal {
    const probabilities = this.computeBoltzmannProbabilities(
      proposals,
      this.temperature
    );
    return this.sampleFromDistribution(probabilities);
  }
}
```

**After Schedule Integration:**
```typescript
import { TemperatureSchedule, getExponentialTemperature } from './schedules';

export class PlinkoLayer {
  private tempSchedule: TemperatureSchedule;
  private step: number = 0;

  constructor() {
    this.tempSchedule = new TemperatureSchedule();
  }

  select(proposals: Proposal[]): Proposal {
    // Get scheduled temperature
    const temperature = this.tempSchedule.getTemperature();

    // Boltzmann selection with scheduled temperature
    const probabilities = this.computeBoltzmannProbabilities(
      proposals,
      temperature
    );

    const selected = this.sampleFromDistribution(probabilities);

    // Advance schedule
    this.tempSchedule.advance();
    this.step++;

    return selected;
  }

  // Alternative: Direct function call
  selectWithFunction(proposals: Proposal[]): Proposal {
    const temperature = getExponentialTemperature(
      this.step,
      2.5,  // initial
      0.1,  // min
      0.995 // decay
    );

    const probabilities = this.computeBoltzmannProbabilities(
      proposals,
      temperature
    );

    this.step++;
    return this.sampleFromDistribution(probabilities);
  }

  // High-temperature exploration
  explore(proposals: Proposal[]): Proposal {
    const baseTemp = this.tempSchedule.getTemperature();
    const exploreTemp = baseTemp * 2.0;  // Double for exploration

    const probabilities = this.computeBoltzmannProbabilities(
      proposals,
      exploreTemp
    );

    return this.sampleFromDistribution(probabilities);
  }
}
```

---

## Dreaming Module

### File: `src/core/dreaming.ts`

**Before Optimization:**
```typescript
export class DreamManager {
  private dreamRatio: number = 0.5;  // 50% dreams

  async optimizePolicy(policy: Policy) {
    if (Math.random() < this.dreamRatio) {
      await this.runDreamEpisode();
    } else {
      await this.runRealEpisode();
    }
  }
}
```

**After Schedule Integration:**
```typescript
import { DreamRatioSchedule } from './schedules';

export class DreamManager {
  private ratioSchedule: DreamRatioSchedule;
  private episodeCount: number = 0;

  constructor() {
    this.ratioSchedule = new DreamRatioSchedule();
  }

  async optimizePolicy(policy: Policy) {
    const shouldDream = this.ratioSchedule.shouldDream();

    if (shouldDream) {
      // Run dream episode
      const dreamEpisode = await this.runDreamEpisode(policy);
      await this.updateFromDream(dreamEpisode);

      this.dreamCount++;
    } else {
      // Run real episode
      const realEpisode = await this.runRealEpisode(policy);
      await this.updateFromReal(realEpisode);

      this.realCount++;
    }

    // Advance schedule
    this.ratioSchedule.advance();
    this.episodeCount++;

    // Log stats
    const currentRatio = this.ratioSchedule.getRatio();
    const progress = this.ratioSchedule.getProgress();

    this.logger.log({
      episode: this.episodeCount,
      dreamRatio: currentRatio,
      progress: progress,
      dreamCount: this.dreamCount,
      realCount: this.realCount
    });
  }

  // Adaptive: increase dreams if policy not improving
  async adaptativeOptimization(policy: Policy, performance: number) {
    let ratio = this.ratioSchedule.getRatio();

    // If performance plateauing, increase dream ratio
    if (this.isPerformancePlateauing(performance)) {
      ratio = Math.min(0.9, ratio + 0.1);
      this.logger.log('Increasing dream ratio due to plateau', { ratio });
    }

    // Use adaptive ratio
    if (Math.random() < ratio) {
      await this.runDreamEpisode(policy);
    } else {
      await this.runRealEpisode(policy);
    }
  }
}
```

---

## META Tiles

### File: `src/core/meta.ts`

**Before Optimization:**
```typescript
export class MetaTile extends BaseTile {
  private plasticity: number = 1.0;  // Always fully plastic

  differentiate(signal: Signal) {
    const differentiationRate = this.baseRate * this.plasticity;
    this.specialization += differentiationRate * signal.strength;
  }
}
```

**After Schedule Integration:**
```typescript
import { PlasticitySchedule } from './schedules';

export class MetaTile extends BaseTile {
  private plasticitySchedule: PlasticitySchedule;
  private differentiationCount: number = 0;

  constructor() {
    super();
    this.plasticitySchedule = new PlasticitySchedule();
  }

  differentiate(signal: Signal) {
    // Get current plasticity
    const plasticity = this.plasticitySchedule.getPlasticity();

    // Apply plasticity modulation
    const baseRate = this.config.differentiationRate;
    const modulatedRate = plasticity * baseRate;

    // Differentiate with modulated rate
    this.specialization += modulatedRate * signal.strength;

    // Enhanced learning during critical period
    if (this.plasticitySchedule.isCriticalPeriod(0.5)) {
      this.specialization *= 1.2;  // Boost during critical period
      this.logger.log('Critical period learning boost');
    }

    // Track differentiation
    this.differentiationCount++;
    this.plasticitySchedule.advance();

    // Log plasticity
    if (this.differentiationCount % 100 === 0) {
      this.logger.log({
        step: this.differentiationCount,
        plasticity: plasticity,
        specialization: this.specialization
      });
    }
  }

  // Check if tile should be more plastic
  shouldReconfigure(): boolean {
    const plasticity = this.plasticitySchedule.getPlasticity();
    const progress = this.plasticitySchedule.getProgress();

    // Reconfigure if early (high plasticity) and signal strong
    return plasticity > 0.5 && progress < 0.3;
  }
}
```

---

## Federated Learning

### File: `src/core/federated.ts`

**Before Optimization:**
```typescript
export class FederatedLearningCoordinator {
  private syncInterval: number = 100;  // Sync every 100 episodes

  async coordinate(colonies: Colony[]) {
    await this.localUpdate(colonies);

    if (this.episode % this.syncInterval === 0) {
      await this.synchronize(colonies);
    }
  }
}
```

**After Schedule Integration:**
```typescript
import { FederatedSyncSchedule } from './schedules';

export class FederatedLearningCoordinator {
  private syncSchedule: FederatedSyncSchedule;
  private syncCount: number = 0;

  constructor() {
    this.syncSchedule = new FederatedSyncSchedule();
  }

  async coordinate(colonies: Colony[]) {
    // Local training round
    await this.localUpdate(colonies);

    // Check if should synchronize
    if (this.syncSchedule.shouldSync()) {
      await this.synchronize(colonies);
      this.syncCount++;
      this.logger.log(`Synchronization #${this.syncCount}`);
    }

    // Advance schedule
    this.syncSchedule.advance();
  }

  async synchronize(colonies: Colony[]) {
    // Measure divergence before sync
    const divergenceBefore = this.computeDivergence(colonies);

    // Perform synchronization
    const globalModel = this.aggregateModels(colonies);
    await this.distributeGlobalModel(colonies, globalModel);

    // Measure improvement
    const divergenceAfter = this.computeDivergence(colonies);

    this.logger.log({
      sync: this.syncCount,
      divergenceBefore,
      divergenceAfter,
      improvement: divergenceBefore - divergenceAfter
    });
  }

  // Adaptive: force sync if colonies diverging too much
  async adaptiveCoordinate(colonies: Colony[]) {
    await this.localUpdate(colonies);

    const divergence = this.computeDivergence(colonies);

    // Sync if schedule says so OR if high divergence
    if (this.syncSchedule.shouldSync() || divergence > 0.5) {
      if (divergence > 0.5) {
        this.logger.log('Emergency sync due to high divergence', { divergence });
      }
      await this.synchronize(colonies);
    }

    this.syncSchedule.advance();
  }

  getSyncStats() {
    return {
      syncCount: this.syncCount,
      syncFrequency: this.syncSchedule.getSyncFrequency(),
      totalSyncs: this.syncSchedule.getTotalSyncs()
    };
  }
}
```

---

## Complete Colony Integration

### File: `src/core/colony.ts`

**Before Optimization:**
```typescript
export class Colony {
  async learn() {
    const valueLr = 0.01;
    const vaeLr = 0.001;
    const temperature = 1.0;
    const dreamRatio = 0.5;

    // Run learning step
    await this.updateValueNetwork(valueLr);
    await this.updateWorldModel(vaeLr);
    this.selectAction(temperature);
    await this.runDreaming(dreamRatio);
  }
}
```

**After Schedule Integration:**
```typescript
import { ScheduleManager } from './schedules';

export class Colony {
  private schedules: ScheduleManager;
  private step: number = 0;

  constructor() {
    this.schedules = new ScheduleManager();
  }

  async learn() {
    // Get all scheduled parameters
    const tdLr = this.schedules.getLearningRate('td_lambda');
    const vaeLr = this.schedules.getLearningRate('vae');
    const hebbianLr = this.schedules.getLearningRate('hebbian');
    const temperature = this.schedules.getTemperature();
    const dreamRatio = this.schedules.getDreamRatio();
    const plasticity = this.schedules.getPlasticity();
    const shouldSync = this.schedules.shouldSync();

    // Run learning with scheduled parameters
    await this.updateValueNetwork(tdLr);
    await this.updateWorldModel(vaeLr);
    await this.updateHebbianConnections(hebbianLr);

    const action = this.selectAction(temperature);

    await this.runDreaming(dreamRatio);
    await this.differentiateTiles(plasticity);

    if (this.isFederated && shouldSync) {
      await this.synchronizeWithNeighbors();
    }

    // Advance all schedules
    this.schedules.advanceAll();
    this.step++;

    // Log progress
    if (this.step % 100 === 0) {
      this.logLearningState();
    }
  }

  private logLearningState() {
    const state = {
      step: this.step,
      progress: this.schedules.getTemperature() as any,  // TODO: fix
      tdLr: this.schedules.getLearningRate('td_lambda'),
      vaeLr: this.schedules.getLearningRate('vae'),
      temperature: this.schedules.getTemperature(),
      dreamRatio: this.schedules.getDreamRatio(),
      plasticity: this.schedules.getPlasticity()
    };

    this.logger.info('Learning state', state);
  }

  reset() {
    this.schedules.resetAll();
    this.step = 0;
    this.logger.info('Schedules reset');
  }

  // Export schedule state for checkpointing
  exportScheduleState(): object {
    return {
      step: this.step,
      schedules: this.schedules
    };
  }

  // Import schedule state from checkpoint
  importScheduleState(state: any) {
    this.step = state.step;
    this.schedules = state.schedules;
  }
}
```

---

## Testing Integration

### Unit Test Example

```typescript
import { TDLambdaSchedule, ScheduleManager } from './schedules';

describe('ValueNetwork with Schedule', () => {
  it('should use decreasing learning rates', () => {
    const schedule = new TDLambdaSchedule({ totalSteps: 100 });
    const network = new ValueNetwork(schedule);

    const initialLr = schedule.getRate();

    // Simulate 10 updates
    for (let i = 0; i < 10; i++) {
      network.update(dummyValues, dummyRewards);
    }

    const finalLr = schedule.getRate();

    expect(finalLr).toBeLessThan(initialLr);
  });

  it('should reset schedule', () => {
    const schedule = new TDLambdaSchedule({ totalSteps: 100 });

    const initialLr = schedule.getRate();

    // Advance 50 steps
    for (let i = 0; i < 50; i++) {
      schedule.advance();
    }

    const midLr = schedule.getRate();
    expect(midLr).toBeLessThan(initialLr);

    // Reset
    schedule.reset();

    const resetLr = schedule.getRate();
    expect(resetLr).toBeCloseTo(initialLr);
  });
});

describe('Colony with ScheduleManager', () => {
  it('should coordinate all schedules', async () => {
    const colony = new Colony();

    // Initial state
    const initialTemp = colony.schedules.getTemperature();

    // Learn for 10 steps
    for (let i = 0; i < 10; i++) {
      await colony.learn();
    }

    // Temperature should decrease
    const finalTemp = colony.schedules.getTemperature();
    expect(finalTemp).toBeLessThan(initialTemp);
  });
});
```

---

## Best Practices Summary

1. **Initialize Once**: Create schedule instances in constructor
2. **Advance Consistently**: Always call `advance()` after using values
3. **Reset Appropriately**: Reset when starting new training phases
4. **Monitor Progress**: Use `getProgress()` to track training
5. **Log Changes**: Log scheduled parameters for debugging
6. **Test Thoroughly**: Verify schedule behavior in unit tests
7. **Checkpoint State**: Export/import schedule states for persistence
