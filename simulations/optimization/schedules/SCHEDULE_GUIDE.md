# POLLN Learning Schedules - Integration Guide

## Overview

This guide explains how to integrate auto-generated optimal learning schedules into POLLN core modules.

## Generated Schedules

After running `run_all.py`, the following TypeScript classes are generated in `src/core/schedules/`:

### 1. Learning Rate Schedules (`learning-rate.ts`)

```typescript
// TD(λ) Value Learning
const tdSchedule = new TDLambdaSchedule();
const lr = tdSchedule.getRate();  // Current learning rate
tdSchedule.advance();             // Move to next step

// VAE World Model
const vaeSchedule = new VAESchedule();
const vaeLr = vaeSchedule.getRate();

// Hebbian Learning
const hebbianSchedule = new HebbianSchedule();

// Oja's Rule
const ojaSchedule = new OjaSchedule();

// Unified manager
const lrManager = new LearningRateManager();
const tdLr = lrManager.getRate('td_lambda');
```

### 2. Temperature Schedule (`temperature.ts`)

```typescript
// For Plinko stochastic selection
const tempSchedule = new TemperatureSchedule();
const temperature = tempSchedule.getTemperature();
tempSchedule.advance();
```

### 3. Dream Ratio Schedule (`dream-ratio.ts`)

```typescript
// For dream-based policy optimization
const dreamSchedule = new DreamRatioSchedule();

if (dreamSchedule.shouldDream()) {
  // Run dream episode
} else {
  // Run real episode
}
dreamSchedule.advance();
```

### 4. Plasticity Schedule (`plasticity.ts`)

```typescript
// For META tile differentiation
const plasticitySchedule = new PlasticitySchedule();

// Apply plasticity modulation
const baseLr = 0.01;
const modulatedLr = plasticitySchedule.modulate(baseLr);

// Check if in critical period
if (plasticitySchedule.isCriticalPeriod()) {
  // Higher learning rate during critical period
}
plasticitySchedule.advance();
```

### 5. Federated Sync Schedule (`federated-sync.ts`)

```typescript
// For multi-colony synchronization
const syncSchedule = new FederatedSyncSchedule();

if (syncSchedule.shouldSync()) {
  // Synchronize with other colonies
}
syncSchedule.advance();
```

## Integration Points

### Value Network (`src/core/valuenetwork.ts`)

**Before**:
```typescript
const learningRate = 0.01;  // Fixed
```

**After**:
```typescript
import { TDLambdaSchedule } from './schedules';

class ValueNetwork {
  private lrSchedule: TDLambdaSchedule;

  constructor() {
    this.lrSchedule = new TDLambdaSchedule();
  }

  update(values: number[], rewards: number[]) {
    const lr = this.lrSchedule.getRate();
    // TD(λ) update with scheduled LR
    // ...
    this.lrSchedule.advance();
  }
}
```

### World Model (`src/core/worldmodel.ts`)

**Before**:
```typescript
const learningRate = 0.001;  // Fixed
```

**After**:
```typescript
import { VAESchedule } from './schedules';

class WorldModel {
  private lrSchedule: VAESchedule;

  constructor() {
    this.lrSchedule = new VAESchedule();
  }

  train(batch: Tensor[]) {
    const lr = this.lrSchedule.getRate();
    // VAE training with scheduled LR
    // ...
    this.lrSchedule.advance();
  }
}
```

### Plinko Decision Layer (`src/core/decision.ts`)

**Before**:
```typescript
const temperature = 1.0;  // Fixed
```

**After**:
```typescript
import { TemperatureSchedule } from './schedules';

class PlinkoLayer {
  private tempSchedule: TemperatureSchedule;

  constructor() {
    this.tempSchedule = new TemperatureSchedule();
  }

  select(proposals: Proposal[]): Proposal {
    const temperature = this.tempSchedule.getTemperature();
    // Boltzmann selection with scheduled temperature
    // ...
    this.tempSchedule.advance();
  }
}
```

### Dreaming Module (`src/core/dreaming.ts`)

**Before**:
```typescript
const dreamRatio = 0.5;  // Fixed 50% dreams
```

**After**:
```typescript
import { DreamRatioSchedule } from './schedules';

class DreamManager {
  private ratioSchedule: DreamRatioSchedule;

  constructor() {
    this.ratioSchedule = new DreamRatioSchedule();
  }

  async optimize(policy: Policy) {
    if (this.ratioSchedule.shouldDream()) {
      await this.dreamEpisode();
    } else {
      await this.realEpisode();
    }
    this.ratioSchedule.advance();
  }
}
```

### META Tiles (`src/core/meta.ts`)

**Before**:
```typescript
const plasticity = 1.0;  // Always plastic
```

**After**:
```typescript
import { PlasticitySchedule } from './schedules';

class MetaTile extends BaseTile {
  private plasticitySchedule: PlasticitySchedule;

  constructor() {
    super();
    this.plasticitySchedule = new PlasticitySchedule();
  }

  differentiate(signal: Signal) {
    const plasticity = this.plasticitySchedule.getPlasticity();

    // Apply differentiation with modulated plasticity
    const differentiationRate = this.baseRate * plasticity;

    if (this.plasticitySchedule.isCriticalPeriod(0.5)) {
      // Enhanced learning during critical period
      this.emergeSpecialization(signal);
    }

    this.plasticitySchedule.advance();
  }
}
```

### Federated Learning (`src/core/federated.ts`)

**Before**:
```typescript
const syncInterval = 100;  // Fixed
```

**After**:
```typescript
import { FederatedSyncSchedule } from './schedules';

class FederatedLearningCoordinator {
  private syncSchedule: FederatedSyncSchedule;

  constructor() {
    this.syncSchedule = new FederatedSyncSchedule();
  }

  async coordinate(colonies: Colony[]) {
    // Local training
    await this.localUpdate(colonies);

    // Conditional synchronization
    if (this.syncSchedule.shouldSync()) {
      await this.synchronize(colonies);
    }

    this.syncSchedule.advance();
  }
}
```

## Unified Schedule Manager

For centralized control, use the `ScheduleManager`:

```typescript
import { ScheduleManager } from './schedules';

class Colony {
  private schedules: ScheduleManager;

  constructor() {
    this.schedules = new ScheduleManager();
  }

  async learn() {
    // Get all scheduled parameters
    const tdLr = this.schedules.getLearningRate('td_lambda');
    const vaeLr = this.schedules.getLearningRate('vae');
    const temperature = this.schedules.getTemperature();
    const dreamRatio = this.schedules.getDreamRatio();
    const plasticity = this.schedules.getPlasticity();
    const shouldSync = this.schedules.shouldSync();

    // Use in learning
    // ...

    // Advance all schedules
    this.schedules.advanceAll();
  }

  reset() {
    this.schedules.resetAll();
  }
}
```

## Schedule Reset Behavior

All schedules support reset for repeated training:

```typescript
const schedule = new TDLambdaSchedule();

// First training session
for (let i = 0; i < 1000; i++) {
  const lr = schedule.getRate();
  // ...
  schedule.advance();
}

// Reset for second session
schedule.reset();

// Schedule starts from beginning
for (let i = 0; i < 1000; i++) {
  const lr = schedule.getRate();
  // ...
  schedule.advance();
}
```

## Custom Schedule Configuration

Override default parameters:

```typescript
import { TemperatureSchedule, TemperatureScheduleConfig } from './schedules';

const config: TemperatureScheduleConfig = {
  initialTemp: 3.0,
  minTemp: 0.05,
  decayRate: 0.998,
  totalSteps: 2000
};

const customTempSchedule = new TemperatureSchedule(config);
```

## Monitoring Schedule Progress

Check schedule progress during training:

```typescript
const schedule = new TDLambdaSchedule();

console.log(`Progress: ${schedule.getProgress() * 100}%`);
console.log(`Current LR: ${schedule.getRate()}`);
console.log(`Step: ${schedule.step}`);
```

## Testing Integration

Verify schedule integration with tests:

```typescript
import { TDLambdaSchedule } from './schedules';

describe('ValueNetwork with Schedule', () => {
  it('should use scheduled learning rates', () => {
    const schedule = new TDLambdaSchedule();
    const network = new ValueNetwork(schedule);

    const initialLr = schedule.getRate();

    network.update([1, 2, 3], [1, 0, 1]);

    const finalLr = schedule.getRate();

    expect(finalLr).toBeLessThan(initialLr);
  });
});
```

## Performance Considerations

### Memory Usage

Each schedule stores an array of values:

```typescript
// For 1000 steps, schedule uses ~8KB (1000 × 8 bytes)
const schedule = new TDLambdaSchedule({ totalSteps: 1000 });
```

For very long training runs, consider periodic resets:

```typescript
const schedule = new TDLambdaSchedule({ totalSteps: 10000 });

// After 10000 steps, reset to reuse schedule
if (schedule.getProgress() >= 1.0) {
  schedule.reset();
}
```

### Computation Overhead

Schedule lookups are O(1):

```typescript
// Very fast - just array access
const lr = schedule.getRate();
```

No significant performance impact.

## Debugging Schedule Issues

### 1. Learning Too Fast

```typescript
// Check if schedule is advancing
console.log(`Step: ${schedule.step}, LR: ${schedule.getRate()}`);
```

### 2. Learning Too Slow

```typescript
// Verify schedule parameters
const config = {
  initialRate: 0.1,    // Increase if too slow
  minRate: 0.0001,
  totalSteps: 1000
};
```

### 3. No Convergence

```typescript
// Reset and try different schedule
schedule.reset();
```

## Best Practices

1. **Initialize Once**: Create schedule instances in constructor, not in loops
2. **Advance Consistently**: Always call `advance()` after using a value
3. **Reset Appropriately**: Reset schedules when starting new training phases
4. **Monitor Progress**: Check `getProgress()` to track training
5. **Customize Carefully**: Test custom configurations before production use

## Migration Guide

### Migrating from Fixed Learning Rates

**Step 1**: Import schedule classes
```typescript
import { TDLambdaSchedule } from './schedules';
```

**Step 2**: Replace constants with schedule instances
```typescript
// Before
const lr = 0.01;

// After
const lrSchedule = new TDLambdaSchedule();
const lr = lrSchedule.getRate();
```

**Step 3**: Add schedule advancement
```typescript
// After using learning rate
lrSchedule.advance();
```

**Step 4**: Add reset if needed
```typescript
// When restarting training
lrSchedule.reset();
```

## API Reference

### Common Methods

All schedules implement:

- `getRate()` / `getValue()` / `getTemperature()` / etc.: Get current value
- `advance()`: Move to next step
- `reset()`: Reset to beginning
- `getProgress()`: Get progress (0 to 1)

### Properties

- `step`: Current step number
- `schedule`: Array of scheduled values

## Future Enhancements

Potential improvements:

1. **Dynamic Adjustment**: Adjust schedules based on online performance
2. **Multi-Phase Schedules**: Different schedules for different training phases
3. **Ensemble Schedules**: Combine multiple schedules
4. **Schedule Logging**: Track which schedule values were used

## Support

For integration issues:
1. Check generated schedule files in `src/core/schedules/`
2. Verify optimization results in `simulations/optimization/schedules/results/`
3. Run tests: `npm run test -- src/core/schedules/`
4. Check logs for schedule advancement
