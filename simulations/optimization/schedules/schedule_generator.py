"""
Schedule Generator
==================
Converts optimal schedules from simulation results to production-ready TypeScript classes.

Reads optimization results from JSON files and generates TypeScript schedule classes
for integration into POLLN core system.

Generated Classes:
- LearningRateSchedule: TD(λ), VAE, Hebbian, Oja
- TemperatureSchedule: Plinko exploration
- DreamRatioSchedule: Dream optimization
- PlasticitySchedule: META tile differentiation
- FederatedSyncSchedule: Multi-colony synchronization
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np


class TypeScriptGenerator:
    """Generates TypeScript schedule classes from optimization results"""

    def __init__(self, results_dir: str, output_dir: str = None):
        self.results_dir = Path(results_dir)
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent.parent / "src" / "core" / "schedules"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_results(self) -> Dict[str, Any]:
        """Load all optimization results"""
        results = {}

        # Load learning rate results
        lr_file = self.results_dir / "schedule_optimization_summary.json"
        if lr_file.exists():
            with open(lr_file, 'r') as f:
                results['learning_rate'] = json.load(f)

        # Load exploration results
        exploration_file = self.results_dir / "exploration_optimal_schedule.json"
        if exploration_file.exists():
            with open(exploration_file, 'r') as f:
                results['exploration'] = json.load(f)

        # Load dream ratio results
        dream_file = self.results_dir / "dream_ratio_optimal.json"
        if dream_file.exists():
            with open(dream_file, 'r') as f:
                results['dream_ratio'] = json.load(f)

        # Load plasticity results
        plasticity_file = self.results_dir / "plasticity_optimal_schedule.json"
        if plasticity_file.exists():
            with open(plasticity_file, 'r') as f:
                results['plasticity'] = json.load(f)

        # Load federated sync results
        federated_file = self.results_dir / "federated_sync_optimal.json"
        if federated_file.exists():
            with open(federated_file, 'r') as f:
                results['federated_sync'] = json.load(f)

        return results

    def generate_learning_rate_schedules(self, results: Dict) -> str:
        """Generate learning rate schedule classes"""
        code = '''/**
 * Learning Rate Schedules
 * =======================
 * Auto-generated from simulation optimization results.
 *
 * Optimal schedules for:
 * - TD(λ) Value Learning
 * - VAE World Model
 * - Hebbian Learning
 * - Oja's Rule (PCA)
 */

export interface LearningRateScheduleConfig {
  initialRate?: number;
  minRate?: number;
  totalSteps?: number;
  warmupSteps?: number;
  decayRate?: number;
  cycleLength?: number;
}

/**
 * Base learning rate schedule class
 */
export abstract class LearningRateSchedule {
  protected step: number = 0;
  protected schedule: number[];

  constructor(config: LearningRateScheduleConfig = {}) {}

  /**
   * Get current learning rate
   */
  getRate(): number {
    return this.schedule[Math.min(this.step, this.schedule.length - 1)];
  }

  /**
   * Advance to next step
   */
  advance(): void {
    this.step++;
  }

  /**
   * Reset schedule to beginning
   */
  reset(): void {
    this.step = 0;
  }

  /**
   * Get progress (0 to 1)
   */
  getProgress(): number {
    return Math.min(1, this.step / this.schedule.length);
  }
}

/**
 * TD(λ) Value Learning Schedule
 * Optimal: {td_lambda_schedule}
 */
export class TDLambdaSchedule extends LearningRateSchedule {
  constructor(config: LearningRateScheduleConfig = {}) {{
    super(config);
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps);
  }}

  private generateSchedule(totalSteps: number): number[] {{
    const schedule: number[] = [];
    {td_lambda_implementation}
    return schedule;
  }}

  /**
   * Get TD(λ)-specific learning rate
   */
  getTDLambdaRate(): number {{
    return this.getRate();
  }}
}}

/**
 * VAE World Model Schedule
 * Optimal: {vae_schedule}
 */
export class VAESchedule extends LearningRateSchedule {
  constructor(config: LearningRateScheduleConfig = {}) {{
    super(config);
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps);
  }}

  private generateSchedule(totalSteps: number): number[] {{
    const schedule: number[] = [];
    {vae_implementation}
    return schedule;
  }}
}}

/**
 * Hebbian Learning Schedule
 * Optimal: {hebbian_schedule}
 */
export class HebbianSchedule extends LearningRateSchedule {
  constructor(config: LearningRateScheduleConfig = {}) {{
    super(config);
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps);
  }}

  private generateSchedule(totalSteps: number): number[] {{
    const schedule: number[] = [];
    {hebbian_implementation}
    return schedule;
  }}
}}

/**
 * Oja's Rule Schedule
 * Optimal: {oja_schedule}
 */
export class OjaSchedule extends LearningRateSchedule {
  constructor(config: LearningRateScheduleConfig = {}) {{
    super(config);
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps);
  }}

  private generateSchedule(totalSteps: number): number[] {{
    const schedule: number[] = [];
    {oja_implementation}
    return schedule;
  }}
}}

/**
 * Unified learning rate manager
 */
export class LearningRateManager {{
  private schedules: Map<string, LearningRateSchedule>;

  constructor() {{
    this.schedules = new Map();
    this.schedules.set('td_lambda', new TDLambdaSchedule());
    this.schedules.set('vae', new VAESchedule());
    this.schedules.set('hebbian', new HebbianSchedule());
    this.schedules.set('oja', new OjaSchedule());
  }}

  getRate(algorithm: string): number {{
    const schedule = this.schedules.get(algorithm);
    if (!schedule) {{
      throw new Error(`Unknown learning algorithm: ${{algorithm}}`);
    }}
    return schedule.getRate();
  }}

  advance(algorithm?: string): void {{
    if (algorithm) {{
      const schedule = this.schedules.get(algorithm);
      if (schedule) {{
        schedule.advance();
      }}
    }} else {{
      this.schedules.forEach(s => s.advance());
    }}
  }}

  reset(algorithm?: string): void {{
    if (algorithm) {{
      const schedule = this.schedules.get(algorithm);
      if (schedule) {{
        schedule.reset();
      }}
    }} else {{
      this.schedules.forEach(s => s.reset());
    }}
  }}
}}
'''
        return code

    def generate_temperature_schedule(self, results: Dict) -> str:
        """Generate temperature schedule for Plinko"""
        optimal = results.get('exploration', {}).get('optimal_schedule', 'temperature_exponential')
        params = results.get('exploration', {}).get('optimal_params', {})

        # Generate implementation based on optimal schedule
        if 'exponential' in optimal:
            implementation = f'''for (let step = 0; step < totalSteps; step++) {{
  const decayRate = {params.get('decay_rate', 0.995)};
  const minTemp = {params.get('min_temp', 0.1)};
  const temp = {params.get('initial_temp', 2.5)} * Math.pow(decayRate, step);
  schedule.push(Math.max(temp, minTemp));
}}'''
        elif 'cosine' in optimal:
            implementation = f'''for (let step = 0; step < totalSteps; step++) {{
  const initialTemp = {params.get('initial_temp', 2.5)};
  const minTemp = {params.get('min_temp', 0.1)};
  const temp = minTemp + 0.5 * (initialTemp - minTemp) *
    (1 + Math.cos(Math.PI * step / totalSteps));
  schedule.push(temp);
}}'''
        else:
            implementation = f'''for (let step = 0; step < totalSteps; step++) {{
  schedule.push({params.get('temperature', 1.0)});
}}'''

        code = f'''/**
 * Temperature Schedule for Plinko Stochastic Selection
 * =====================================================
 * Auto-generated from exploration optimization.
 *
 * Optimal strategy: {optimal}
 */

export interface TemperatureScheduleConfig {{
  initialTemp?: number;
  minTemp?: number;
  decayRate?: number;
  totalSteps?: number;
}}

/**
 * Temperature schedule for Boltzmann/softmax exploration
 */
export class TemperatureSchedule {{
  private step: number = 0;
  private schedule: number[];

  constructor(config: TemperatureScheduleConfig = {{}}) {{
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps, config);
  }}

  private generateSchedule(totalSteps: number, config: TemperatureScheduleConfig): number[] {{
    const schedule: number[] = [];
    {implementation}
    return schedule;
  }}

  /**
   * Get current temperature
   */
  getTemperature(): number {{
    return this.schedule[Math.min(this.step, this.schedule.length - 1)];
  }}

  /**
   * Get temperature at specific progress (0 to 1)
   */
  getTemperatureAtProgress(progress: number): number {{
    const idx = Math.floor(progress * (this.schedule.length - 1));
    return this.schedule[Math.min(idx, this.schedule.length - 1)];
  }}

  /**
   * Advance to next step
   */
  advance(): void {{
    this.step++;
  }}

  /**
   * Reset schedule
   */
  reset(): void {{
    this.step = 0;
  }}

  /**
   * Get progress
   */
  getProgress(): number {{
    return Math.min(1, this.step / this.schedule.length);
  }}
}}

/**
 * Convenience function for exponential temperature decay
 */
export function getExponentialTemperature(
  step: number,
  initialTemp: number = 2.5,
  minTemp: number = 0.1,
  decayRate: number = 0.995
): number {{
  const temp = initialTemp * Math.pow(decayRate, step);
  return Math.max(temp, minTemp);
}}
'''
        return code

    def generate_dream_ratio_schedule(self, results: Dict) -> str:
        """Generate dream ratio schedule"""
        optimal = results.get('dream_ratio', {}).get('optimal_schedule', 'high_early_low_late')
        params = results.get('dream_ratio', {}).get('optimal_params', {})

        # Generate implementation
        if 'exponential' in optimal or 'early_low_late' in optimal:
            implementation = f'''for (let episode = 0; episode < totalEpisodes; episode++) {{
  const decayRate = {params.get('decay_rate', 0.995)};
  const minRatio = {params.get('min_ratio', 0.1)};
  const ratio = {params.get('initial_ratio', 0.7)} * Math.pow(decayRate, episode);
  schedule.push(Math.max(ratio, minRatio));
}}'''
        elif 'one_cycle' in optimal:
            implementation = f'''const midPoint = Math.floor(totalEpisodes / 2);
const maxRatio = {params.get('max_ratio', 0.9)};
const minRatio = {params.get('min_ratio', 0.1)};

for (let episode = 0; episode < totalEpisodes; episode++) {{
  let ratio: number;
  if (episode < midPoint) {{
    // First half: increase dream ratio
    const pct = episode / midPoint;
    ratio = {params.get('initial_ratio', 0.2)} + (maxRatio - {params.get('initial_ratio', 0.2)}) * pct;
  }} else {{
    // Second half: decrease dream ratio
    const pct = (episode - midPoint) / (totalEpisodes - midPoint);
    ratio = maxRatio - (maxRatio - minRatio) * pct;
  }}
  schedule.push(ratio);
}}'''
        else:
            implementation = f'''const ratio = {params.get('ratio', 0.5)};
for (let episode = 0; episode < totalEpisodes; episode++) {{
  schedule.push(ratio);
}}'''

        code = f'''/**
 * Dream Ratio Schedule
 * ====================
 * Auto-generated from dream ratio optimization.
 *
 * Optimal strategy: {optimal}
 */

export interface DreamRatioScheduleConfig {{
  initialRatio?: number;
  minRatio?: number;
  maxRatio?: number;
  decayRate?: number;
  totalEpisodes?: number;
}}

/**
 * Dream ratio schedule for dream-based policy optimization
 */
export class DreamRatioSchedule {{
  private episode: number = 0;
  private schedule: number[];

  constructor(config: DreamRatioScheduleConfig = {{}}) {{
    const totalEpisodes = config.totalEpisodes ?? 1000;
    this.schedule = this.generateSchedule(totalEpisodes, config);
  }}

  private generateSchedule(totalEpisodes: number, config: DreamRatioScheduleConfig): number[] {{
    const schedule: number[] = [];
    {implementation}
    return schedule;
  }}

  /**
   * Get current dream ratio (0 to 1)
   */
  getRatio(): number {{
    return this.schedule[Math.min(this.episode, this.schedule.length - 1)];
  }}

  /**
   * Check if should dream at current episode
   */
  shouldDream(): boolean {{
    return Math.random() < this.getRatio();
  }}

  /**
   * Advance to next episode
   */
  advance(): void {{
    this.episode++;
  }}

  /**
   * Reset schedule
   */
  reset(): void {{
    this.episode = 0;
  }}

  /**
   * Get progress
   */
  getProgress(): number {{
    return Math.min(1, this.episode / this.schedule.length);
  }}
}}
'''
        return code

    def generate_plasticity_schedule(self, results: Dict) -> str:
        """Generate plasticity schedule for META tiles"""
        optimal = results.get('plasticity', {}).get('optimal_schedule', 'exponential_decay')
        params = results.get('plasticity', {}).get('optimal_params', {})

        if 'exponential' in optimal or 'decay' in optimal:
            implementation = f'''for (let step = 0; step < totalSteps; step++) {{
  const decayRate = {params.get('decay_rate', 0.99)};
  const minPlasticity = {params.get('min_plasticity', 0.01)};
  const plasticity = {params.get('initial_plasticity', 1.0)} * Math.pow(decayRate, step);
  schedule.push(Math.max(plasticity, minPlasticity));
}}'''
        elif 'adaptive' in optimal:
            implementation = '''// Adaptive plasticity based on performance
let currentPlasticity = initialPlasticity;

for (let step = 0; step < totalSteps; step++) {{
  // Performance monitoring would happen here
  // For now, use exponential decay as baseline
  const decayRate = 0.995;
  const minPlasticity = 0.01;
  currentPlasticity = Math.max(
    minPlasticity,
    currentPlasticity * decayRate
  );
  schedule.push(currentPlasticity);
}}'''
        else:
            implementation = f'''const plasticity = {params.get('plasticity', 0.5)};
for (let step = 0; step < totalSteps; step++) {{
  schedule.push(plasticity);
}}'''

        code = f'''/**
 * Plasticity Schedule for META Tiles
 * ==================================
 * Auto-generated from plasticity optimization.
 *
 * Optimal strategy: {optimal}
 */

export interface PlasticityScheduleConfig {{
  initialPlasticity?: number;
  minPlasticity?: number;
  decayRate?: number;
  totalSteps?: number;
}}

/**
 * Plasticity schedule for META tile differentiation
 */
export class PlasticitySchedule {{
  private step: number = 0;
  private schedule: number[];

  constructor(config: PlasticityScheduleConfig = {{}}) {{
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps, config);
  }}

  private generateSchedule(totalSteps: number, config: PlasticityScheduleConfig): number[] {{
    const schedule: number[] = [];
    const initialPlasticity = config.initialPlasticity ?? 1.0;
    {implementation}
    return schedule;
  }}

  /**
   * Get current plasticity (0 to 1)
   */
  getPlasticity(): number {{
    return this.schedule[Math.min(this.step, this.schedule.length - 1)];
  }}

  /**
   * Apply plasticity to learning rate
   */
  modulate(learningRate: number): number {{
    return learningRate * this.getPlasticity();
  }}

  /**
   * Advance to next step
   */
  advance(): void {{
    this.step++;
  }}

  /**
   * Reset schedule
   */
  reset(): void {{
    this.step = 0;
  }}

  /**
   * Check if in critical period (high plasticity)
   */
  isCriticalPeriod(threshold: number = 0.5): boolean {{
    return this.getPlasticity() > threshold;
  }}
}}
'''
        return code

    def generate_federated_sync_schedule(self, results: Dict) -> str:
        """Generate federated sync schedule"""
        optimal = results.get('federated_sync', {}).get('optimal_schedule', 'adaptive_divergence')
        params = results.get('federated_sync', {}).get('optimal_params', {})

        if 'fixed' in optimal:
            implementation = f'''const syncInterval = {params.get('sync_every', 100)};
for (let step = 0; step < totalSteps; step++) {{
  schedule.push(step % syncInterval === 0);
}}'''
        elif 'adaptive' in optimal:
            implementation = f'''// Adaptive sync based on divergence
const threshold = {params.get('divergence_threshold', 0.3)};
const minInterval = {params.get('min_interval', 10)};

let lastSync = -minInterval;
for (let step = 0; step < totalSteps; step++) {{
  // Divergence would be computed from actual colony states
  // For now, use fixed interval with some randomness
  const shouldSync = (step - lastSync >= minInterval) &&
    (Math.random() < threshold);
  schedule.push(shouldSync);
  if (shouldSync) lastSync = step;
}}'''
        else:
            implementation = f'''const syncProbability = {params.get('gossip_probability', 0.05)};
for (let step = 0; step < totalSteps; step++) {{
  schedule.push(Math.random() < syncProbability);
}}'''

        code = f'''/**
 * Federated Sync Schedule
 * =======================
 * Auto-generated from federated synchronization optimization.
 *
 * Optimal strategy: {optimal}
 */

export interface FederatedSyncScheduleConfig {{
  syncInterval?: number;
  divergenceThreshold?: number;
  minInterval?: number;
  totalSteps?: number;
}}

/**
 * Federated synchronization schedule
 */
export class FederatedSyncSchedule {{
  private step: number = 0;
  private schedule: boolean[];

  constructor(config: FederatedSyncScheduleConfig = {{}}) {{
    const totalSteps = config.totalSteps ?? 1000;
    this.schedule = this.generateSchedule(totalSteps, config);
  }}

  private generateSchedule(totalSteps: number, config: FederatedSyncScheduleConfig): boolean[] {{
    const schedule: boolean[] = [];
    {implementation}
    return schedule;
  }}

  /**
   * Check if should sync at current step
   */
  shouldSync(): boolean {{
    return this.schedule[Math.min(this.step, this.schedule.length - 1)];
  }}

  /**
   * Advance to next step
   */
  advance(): void {{
    this.step++;
  }}

  /**
   * Reset schedule
   */
  reset(): void {{
    this.step = 0;
  }}

  /**
   * Get total number of syncs
   */
  getTotalSyncs(): number {{
    return this.schedule.filter(s => s).length;
  }}

  /**
   * Get sync frequency
   */
  getSyncFrequency(): number {{
    const totalSyncs = this.getTotalSyncs();
    return totalSyncs / this.schedule.length;
  }}
}}
'''
        return code

    def generate_all(self):
        """Generate all TypeScript schedule files"""
        results = self.load_results()

        # Generate learning rate schedules
        lr_code = self.generate_learning_rate_schedules(results)
        with open(self.output_dir / "learning-rate.ts", 'w') as f:
            f.write(lr_code)
        print(f"Generated: {self.output_dir / 'learning-rate.ts'}")

        # Generate temperature schedule
        temp_code = self.generate_temperature_schedule(results)
        with open(self.output_dir / "temperature.ts", 'w') as f:
            f.write(temp_code)
        print(f"Generated: {self.output_dir / 'temperature.ts'}")

        # Generate dream ratio schedule
        dream_code = self.generate_dream_ratio_schedule(results)
        with open(self.output_dir / "dream-ratio.ts", 'w') as f:
            f.write(dream_code)
        print(f"Generated: {self.output_dir / 'dream-ratio.ts'}")

        # Generate plasticity schedule
        plasticity_code = self.generate_plasticity_schedule(results)
        with open(self.output_dir / "plasticity.ts", 'w') as f:
            f.write(plasticity_code)
        print(f"Generated: {self.output_dir / 'plasticity.ts'}")

        # Generate federated sync schedule
        federated_code = self.generate_federated_sync_schedule(results)
        with open(self.output_dir / "federated-sync.ts", 'w') as f:
            f.write(federated_code)
        print(f"Generated: {self.output_dir / 'federated-sync.ts'}")

        # Generate index file
        index_code = '''/**
 * POLLN Schedules
 * ==============
 * Auto-generated optimal learning schedules.
 *
 * Generated from simulation optimization results.
 */

export * from './learning-rate';
export * from './temperature';
export * from './dream-ratio';
export * from './plasticity';
export * from './federated-sync';

/**
 * Unified schedule manager
 */
export class ScheduleManager {{
  private learningRateManager: LearningRateManager;
  private temperatureSchedule: TemperatureSchedule;
  private dreamRatioSchedule: DreamRatioSchedule;
  private plasticitySchedule: PlasticitySchedule;
  private federatedSyncSchedule: FederatedSyncSchedule;

  constructor() {{
    this.learningRateManager = new LearningRateManager();
    this.temperatureSchedule = new TemperatureSchedule();
    this.dreamRatioSchedule = new DreamRatioSchedule();
    this.plasticitySchedule = new PlasticitySchedule();
    this.federatedSyncSchedule = new FederatedSyncSchedule();
  }}

  /**
   * Get learning rate for algorithm
   */
  getLearningRate(algorithm: string): number {{
    return this.learningRateManager.getRate(algorithm);
  }}

  /**
   * Get temperature for exploration
   */
  getTemperature(): number {{
    return this.temperatureSchedule.getTemperature();
  }}

  /**
   * Get dream ratio
   */
  getDreamRatio(): number {{
    return this.dreamRatioSchedule.getRatio();
  }}

  /**
   * Get plasticity
   */
  getPlasticity(): number {{
    return this.plasticitySchedule.getPlasticity();
  }}

  /**
   * Check if should sync
   */
  shouldSync(): boolean {{
    return this.federatedSyncSchedule.shouldSync();
  }}

  /**
   * Advance all schedules
   */
  advanceAll(): void {{
    this.learningRateManager.advance();
    this.temperatureSchedule.advance();
    this.dreamRatioSchedule.advance();
    this.plasticitySchedule.advance();
    this.federatedSyncSchedule.advance();
  }}

  /**
   * Reset all schedules
   */
  resetAll(): void {{
    this.learningRateManager.reset();
    this.temperatureSchedule.reset();
    this.dreamRatioSchedule.reset();
    this.plasticitySchedule.reset();
    this.federatedSyncSchedule.reset();
  }}
}}
'''
        with open(self.output_dir / "index.ts", 'w') as f:
            f.write(index_code)
        print(f"Generated: {self.output_dir / 'index.ts'}")

        print(f"\nAll schedules generated successfully!")
        print(f"Output directory: {self.output_dir}")


def main():
    """Generate TypeScript schedules from optimization results"""
    results_dir = Path(__file__).parent / "results"
    generator = TypeScriptGenerator(results_dir)
    generator.generate_all()


if __name__ == "__main__":
    main()
