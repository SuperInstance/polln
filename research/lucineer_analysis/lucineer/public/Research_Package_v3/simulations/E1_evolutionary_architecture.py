"""
Simulation E1: Evolutionary Architecture Optimization
=====================================================
Uses genetic algorithms to find optimal PE array configurations

Paradigm: Treat chip architecture as evolving organism
Innovation: Discovers non-obvious architectures humans wouldn't design

Author: Innovation Simulation Agent
Date: 2026-03-08
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import random
from copy import deepcopy

# ============================================================================
# GENOME DEFINITION
# ============================================================================

@dataclass
class ChipGenome:
    """
    Genome encoding for chip architecture.
    Each gene represents a configurable parameter.
    """
    # PE Array Dimensions
    pe_rows: int  # 4-64
    pe_cols: int  # 4-64
    
    # Pipeline Configuration
    pipeline_depth: int  # 1-8
    
    # Memory Hierarchy
    weight_cache_kb: int  # 16-512
    kv_cache_kb: int  # 8-256
    
    # Compute Configuration
    mac_units_per_pe: int  # 1-4
    accumulator_bits: int  # 16-32
    
    # Data Flow
    weight_streaming: bool
    output_buffering: int  # 1-4
    
    def to_array(self) -> np.ndarray:
        """Convert genome to array for genetic operations"""
        return np.array([
            self.pe_rows,
            self.pe_cols,
            self.pipeline_depth,
            self.weight_cache_kb,
            self.kv_cache_kb,
            self.mac_units_per_pe,
            self.accumulator_bits,
            1 if self.weight_streaming else 0,
            self.output_buffering
        ])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'ChipGenome':
        """Create genome from array"""
        return cls(
            pe_rows=int(arr[0]),
            pe_cols=int(arr[1]),
            pipeline_depth=int(arr[2]),
            weight_cache_kb=int(arr[3]),
            kv_cache_kb=int(arr[4]),
            mac_units_per_pe=int(arr[5]),
            accumulator_bits=int(arr[6]),
            weight_streaming=bool(arr[7]),
            output_buffering=int(arr[8])
        )
    
    @classmethod
    def random(cls) -> 'ChipGenome':
        """Create random genome"""
        return cls(
            pe_rows=random.randint(4, 64),
            pe_cols=random.randint(4, 64),
            pipeline_depth=random.randint(1, 8),
            weight_cache_kb=random.choice([16, 32, 64, 128, 256, 512]),
            kv_cache_kb=random.choice([8, 16, 32, 64, 128, 256]),
            mac_units_per_pe=random.randint(1, 4),
            accumulator_bits=random.choice([16, 24, 32]),
            weight_streaming=random.choice([True, False]),
            output_buffering=random.randint(1, 4)
        )


# ============================================================================
# FITNESS FUNCTION
# ============================================================================

class FitnessEvaluator:
    """
    Evaluates chip architecture fitness.
    Multi-objective: maximize throughput, minimize power/area
    """
    
    # KV260 constraints (normalized)
    MAX_DSP = 1248
    MAX_BRAM_KB = 5000
    MAX_LUT_K = 117
    TARGET_POWER_W = 5.0
    TARGET_TOK_S = 20.0
    
    def evaluate(self, genome: ChipGenome) -> Dict[str, float]:
        """Calculate fitness metrics for genome"""
        
        # Resource estimation
        total_pes = genome.pe_rows * genome.pe_cols
        dsp_per_pe = genome.mac_units_per_pe * 2  # Ternary MAC needs 2 DSP
        total_dsp = total_pes * dsp_per_pe
        
        # BRAM estimation
        weight_bram = genome.weight_cache_kb / 36  # 36Kb BRAMs
        kv_bram = genome.kv_cache_kb / 36
        total_bram = weight_bram + kv_bram + total_pes * 0.5  # PE local storage
        
        # LUT estimation (control logic, accumulators)
        control_lut = total_pes * 100 / 1000  # K LUTs
        pipeline_lut = genome.pipeline_depth * total_pes * 50 / 1000
        total_lut = control_lut + pipeline_lut
        
        # Constraint violations
        dsp_violation = max(0, total_dsp - self.MAX_DSP) / self.MAX_DSP
        bram_violation = max(0, total_bram * 36 - self.MAX_BRAM_KB) / self.MAX_BRAM_KB
        lut_violation = max(0, total_lut - self.MAX_LUT_K) / self.MAX_LUT_K
        
        constraint_penalty = dsp_violation + bram_violation + lut_violation
        
        # Throughput estimation
        ops_per_cycle = total_pes * genome.mac_units_per_pe
        freq_mhz = 250 / (1 + genome.pipeline_depth * 0.1)  # Deeper pipeline, lower freq
        cycles_per_token = 2e9 / ops_per_cycle  # Approximate for 500M param model
        
        theoretical_tps = (freq_mhz * 1e6) / cycles_per_token
        
        # Derating factors
        utilization = 0.7 * (1 - min(constraint_penalty, 0.5))
        memory_factor = 0.8 if genome.weight_streaming else 0.6
        pipeline_efficiency = 0.9 ** genome.pipeline_depth
        
        realistic_tps = theoretical_tps * utilization * memory_factor * pipeline_efficiency
        
        # Power estimation
        dynamic_power = total_pes * genome.mac_units_per_pe * 0.01  # W per MAC unit
        memory_power = (genome.weight_cache_kb + genome.kv_cache_kb) * 0.001  # W per KB
        static_power = 0.8
        total_power = dynamic_power + memory_power + static_power
        
        # Area estimation (normalized to 1.0 = full chip)
        area = (total_dsp / self.MAX_DSP + total_bram * 36 / self.MAX_BRAM_KB + 
                total_lut / self.MAX_LUT_K) / 3
        
        # Multi-objective fitness
        throughput_score = min(realistic_tps / self.TARGET_TOK_S, 10)  # Cap at 10x
        power_score = self.TARGET_POWER_W / max(total_power, 0.1)  # Lower is better
        area_score = 1 / max(area, 0.1)  # Smaller is better
        
        # Weighted fitness (can be adjusted)
        weights = {
            "throughput": 0.5,
            "power": 0.3,
            "area": 0.2
        }
        
        fitness = (
            weights["throughput"] * throughput_score +
            weights["power"] * min(power_score, 2) +
            weights["area"] * min(area_score, 2)
        )
        
        # Apply constraint penalty
        fitness *= max(0, 1 - constraint_penalty * 10)
        
        return {
            "fitness": fitness,
            "throughput_tps": realistic_tps,
            "power_w": total_power,
            "area_normalized": area,
            "total_pes": total_pes,
            "dsp_used": total_dsp,
            "bram_used_kb": total_bram * 36,
            "lut_used_k": total_lut,
            "constraint_violation": constraint_penalty > 0,
            "constraint_penalty": constraint_penalty
        }


# ============================================================================
# GENETIC OPERATORS
# ============================================================================

class GeneticOperators:
    """Genetic operators for evolution"""
    
    @staticmethod
    def crossover(parent1: ChipGenome, parent2: ChipGenome) -> Tuple[ChipGenome, ChipGenome]:
        """Single-point crossover"""
        arr1 = parent1.to_array()
        arr2 = parent2.to_array()
        
        crossover_point = random.randint(1, len(arr1) - 1)
        
        child1_arr = np.concatenate([arr1[:crossover_point], arr2[crossover_point:]])
        child2_arr = np.concatenate([arr2[:crossover_point], arr1[crossover_point:]])
        
        return ChipGenome.from_array(child1_arr), ChipGenome.from_array(child2_arr)
    
    @staticmethod
    def mutate(genome: ChipGenome, mutation_rate: float = 0.1) -> ChipGenome:
        """Mutate genome with given probability"""
        arr = genome.to_array().astype(float)
        
        for i in range(len(arr)):
            if random.random() < mutation_rate:
                # Gaussian mutation
                arr[i] *= random.gauss(1.0, 0.2)
        
        # Clip to valid ranges
        arr[0] = np.clip(arr[0], 4, 64)  # pe_rows
        arr[1] = np.clip(arr[1], 4, 64)  # pe_cols
        arr[2] = np.clip(arr[2], 1, 8)   # pipeline_depth
        arr[3] = np.clip(arr[3], 16, 512)  # weight_cache
        arr[4] = np.clip(arr[4], 8, 256)   # kv_cache
        arr[5] = np.clip(arr[5], 1, 4)   # mac_units
        arr[6] = np.clip(arr[6], 16, 32)  # accumulator
        arr[8] = np.clip(arr[8], 1, 4)   # output_buffering
        
        # Boolean stays boolean
        arr[7] = 1 if arr[7] > 0.5 else 0
        
        return ChipGenome.from_array(arr.astype(int))


# ============================================================================
# EVOLUTIONARY ALGORITHM
# ============================================================================

class EvolutionaryOptimizer:
    """
    Main evolutionary optimization loop.
    Implements NSGA-II style multi-objective optimization.
    """
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.8,
        elitism_rate: float = 0.1
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate
        
        self.evaluator = FitnessEvaluator()
        self.operators = GeneticOperators()
        
        self.history = {
            "best_fitness": [],
            "avg_fitness": [],
            "best_genome": [],
            "pareto_frontier": []
        }
    
    def initialize_population(self) -> List[ChipGenome]:
        """Create initial random population"""
        return [ChipGenome.random() for _ in range(self.population_size)]
    
    def evaluate_population(self, population: List[ChipGenome]) -> List[Dict]:
        """Evaluate all genomes in population"""
        return [self.evaluator.evaluate(g) for g in population]
    
    def selection(
        self,
        population: List[ChipGenome],
        fitnesses: List[Dict]
    ) -> List[ChipGenome]:
        """Tournament selection"""
        selected = []
        n_elite = int(self.population_size * self.elitism_rate)
        
        # Elitism: keep best individuals
        sorted_indices = np.argsort([-f["fitness"] for f in fitnesses])
        elite = [population[i] for i in sorted_indices[:n_elite]]
        selected.extend(elite)
        
        # Tournament selection for rest
        while len(selected) < self.population_size:
            idx1, idx2 = random.sample(range(len(population)), 2)
            if fitnesses[idx1]["fitness"] > fitnesses[idx2]["fitness"]:
                selected.append(deepcopy(population[idx1]))
            else:
                selected.append(deepcopy(population[idx2]))
        
        return selected
    
    def evolve_population(self, population: List[ChipGenome]) -> List[ChipGenome]:
        """Apply genetic operators to create new population"""
        new_population = []
        
        while len(new_population) < self.population_size:
            # Select parents
            parent1, parent2 = random.sample(population, 2)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self.operators.crossover(parent1, parent2)
            else:
                child1, child2 = deepcopy(parent1), deepcopy(parent2)
            
            # Mutate
            child1 = self.operators.mutate(child1, self.mutation_rate)
            child2 = self.operators.mutate(child2, self.mutation_rate)
            
            new_population.extend([child1, child2])
        
        return new_population[:self.population_size]
    
    def run(self) -> Dict:
        """Run evolutionary optimization"""
        print("Starting Evolutionary Architecture Optimization...")
        print(f"Population: {self.population_size}, Generations: {self.generations}")
        
        # Initialize
        population = self.initialize_population()
        
        # Evolution loop
        for gen in range(self.generations):
            # Evaluate
            fitnesses = self.evaluate_population(population)
            
            # Record history
            best_fitness = max(f["fitness"] for f in fitnesses)
            avg_fitness = np.mean([f["fitness"] for f in fitnesses])
            best_idx = np.argmax([f["fitness"] for f in fitnesses])
            
            self.history["best_fitness"].append(best_fitness)
            self.history["avg_fitness"].append(avg_fitness)
            self.history["best_genome"].append(population[best_idx])
            
            # Progress
            if gen % 20 == 0:
                best = fitnesses[best_idx]
                print(f"  Gen {gen}: Best Fitness = {best_fitness:.3f}")
                print(f"    Throughput: {best['throughput_tps']:.1f} tok/s, Power: {best['power_w']:.2f}W")
            
            # Selection
            selected = self.selection(population, fitnesses)
            
            # Evolution
            population = self.evolve_population(selected)
        
        # Final evaluation
        final_fitnesses = self.evaluate_population(population)
        best_idx = np.argmax([f["fitness"] for f in final_fitnesses])
        best_genome = population[best_idx]
        best_fitness = final_fitnesses[best_idx]
        
        # Pareto frontier (simplified)
        pareto = []
        for i, (g, f) in enumerate(zip(population, final_fitnesses)):
            if f["constraint_penalty"] == 0:  # Feasible only
                dominated = False
                for j, (g2, f2) in enumerate(zip(population, final_fitnesses)):
                    if i != j and f2["constraint_penalty"] == 0:
                        if (f2["throughput_tps"] >= f["throughput_tps"] and 
                            f2["power_w"] <= f["power_w"] and
                            (f2["throughput_tps"] > f["throughput_tps"] or f2["power_w"] < f["power_w"])):
                            dominated = True
                            break
                if not dominated:
                    pareto.append({"genome": g, "fitness": f})
        
        results = {
            "best_genome": {
                "pe_rows": best_genome.pe_rows,
                "pe_cols": best_genome.pe_cols,
                "pipeline_depth": best_genome.pipeline_depth,
                "weight_cache_kb": best_genome.weight_cache_kb,
                "kv_cache_kb": best_genome.kv_cache_kb,
                "mac_units_per_pe": best_genome.mac_units_per_pe,
                "accumulator_bits": best_genome.accumulator_bits,
                "weight_streaming": best_genome.weight_streaming,
                "output_buffering": best_genome.output_buffering
            },
            "best_fitness": best_fitness,
            "history": {
                "best_fitness": self.history["best_fitness"],
                "avg_fitness": self.history["avg_fitness"]
            },
            "pareto_frontier": [
                {
                    "genome": {
                        "pe_rows": p["genome"].pe_rows,
                        "pe_cols": p["genome"].pe_cols,
                    },
                    "throughput_tps": p["fitness"]["throughput_tps"],
                    "power_w": p["fitness"]["power_w"]
                }
                for p in pareto[:10]  # Top 10
            ],
            "convergence_generation": np.argmax(self.history["best_fitness"]),
            "improvement": self.history["best_fitness"][-1] / max(self.history["best_fitness"][0], 0.001)
        }
        
        return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    # Initialize optimizer
    optimizer = EvolutionaryOptimizer(
        population_size=50,
        generations=100,
        mutation_rate=0.15,
        crossover_rate=0.8
    )
    
    # Run evolution
    results = optimizer.run()
    
    # Print results
    print("\n" + "=" * 60)
    print("EVOLUTIONARY ARCHITECTURE OPTIMIZATION RESULTS")
    print("=" * 60)
    
    print(f"\nBest Genome Found:")
    g = results["best_genome"]
    print(f"  PE Array: {g['pe_rows']}x{g['pe_cols']} = {g['pe_rows']*g['pe_cols']} PEs")
    print(f"  Pipeline Depth: {g['pipeline_depth']}")
    print(f"  Weight Cache: {g['weight_cache_kb']} KB")
    print(f"  KV Cache: {g['kv_cache_kb']} KB")
    print(f"  MAC Units/PE: {g['mac_units_per_pe']}")
    print(f"  Weight Streaming: {g['weight_streaming']}")
    
    print(f"\nBest Performance:")
    f = results["best_fitness"]
    print(f"  Throughput: {f['throughput_tps']:.1f} tok/s")
    print(f"  Power: {f['power_w']:.2f} W")
    print(f"  Area: {f['area_normalized']:.1%} of chip")
    print(f"  Fitness Score: {f['fitness']:.3f}")
    print(f"  Constraint Violation: {'No' if not f['constraint_violation'] else 'Yes'}")
    
    print(f"\nPareto Frontier (Trade-offs):")
    for i, p in enumerate(results["pareto_frontier"][:5]):
        print(f"  {i+1}. {p['genome']['pe_rows']}x{p['genome']['pe_cols']}: "
              f"{p['throughput_tps']:.1f} tok/s @ {p['power_w']:.2f}W")
    
    print(f"\nEvolution Statistics:")
    print(f"  Converged at Generation: {results['convergence_generation']}")
    print(f"  Improvement over initial: {results['improvement']:.1f}x")
    
    # Validation
    validation = {
        "target_tps": 20.0,
        "target_power_w": 5.0,
        "actual_tps": f['throughput_tps'],
        "actual_power_w": f['power_w'],
        "throughput_pass": f['throughput_tps'] >= 20.0,
        "power_pass": f['power_w'] <= 5.0,
        "overall_pass": f['throughput_tps'] >= 20.0 and f['power_w'] <= 5.0
    }
    
    print(f"\nValidation:")
    print(f"  Target: ≥20 tok/s @ ≤5W")
    print(f"  Result: {validation['actual_tps']:.1f} tok/s @ {validation['actual_power_w']:.2f}W")
    print(f"  STATUS: {'✅ PASS' if validation['overall_pass'] else '❌ FAIL'}")
    
    results["validation"] = validation
    
    # Save results
    with open("/home/z/my-project/download/simulations/E1_evolutionary_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to E1_evolutionary_results.json")
    
    return results


if __name__ == "__main__":
    results = main()
