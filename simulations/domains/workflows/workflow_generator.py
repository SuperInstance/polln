"""
Workflow Configuration Generator for POLLN
Compiles optimal workflow configurations from simulation results
"""

import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PatternConfig:
    """Configuration for a workflow pattern"""
    agent_count: int
    checkpoint_frequency: str
    parallelism: bool
    coordination: str = "async"
    aggregation: str = "majority"
    levels: int = 1
    fan_out: int = 5


@dataclass
class CompositionConfig:
    """Configuration for agent composition"""
    agent_types: List[str]
    specialization: str  # 'low', 'medium', 'high'
    adaptability: str  # 'low', 'medium', 'high'
    generalist_ratio: float = 0.5
    specialist_ratio: float = 0.5


@dataclass
class CoordinationConfig:
    """Configuration for coordination"""
    a2a_overhead: float
    sync_strategy: str
    timeout_ms: int
    max_retries: int


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling"""
    retry_strategy: str
    fallback: str
    circuit_breaker: Dict[str, Any]


@dataclass
class GranularityConfig:
    """Configuration for task granularity"""
    task_duration: str
    overhead_ratio: float


class WorkflowConfigGenerator:
    """Generate workflow configurations from simulation results"""

    def __init__(self, results_dir: str = "simulation_results"):
        self.results_dir = results_dir
        self.simulation_results = self._load_simulation_results()

    def _load_simulation_results(self) -> Dict[str, Any]:
        """Load all simulation results"""
        results = {}

        # Load pattern optimization results
        pattern_file = os.path.join(self.results_dir, "pattern_optimization.json")
        if os.path.exists(pattern_file):
            with open(pattern_file, 'r') as f:
                results['patterns'] = json.load(f)

        # Load composition optimization results
        composition_file = os.path.join(self.results_dir, "composition_optimization.json")
        if os.path.exists(composition_file):
            with open(composition_file, 'r') as f:
                results['composition'] = json.load(f)

        # Load coordination overhead results
        coordination_file = os.path.join(self.results_dir, "coordination_overhead.json")
        if os.path.exists(coordination_file):
            with open(coordination_file, 'r') as f:
                results['coordination'] = json.load(f)

        # Load reliability results
        reliability_file = os.path.join(self.results_dir, "workflow_reliability.json")
        if os.path.exists(reliability_file):
            with open(reliability_file, 'r') as f:
                results['reliability'] = json.load(f)

        return results

    def generate_workflow_config(self) -> Dict[str, Any]:
        """Generate complete workflow configuration"""
        config = {
            'patterns': self._generate_pattern_configs(),
            'composition': self._generate_composition_configs(),
            'coordination': self._generate_coordination_config(),
            'error_handling': self._generate_error_handling_config(),
            'granularity': self._generate_granularity_config(),
            'recommendations': self._generate_recommendations()
        }

        return config

    def _generate_pattern_configs(self) -> Dict[str, Dict]:
        """Generate pattern-specific configurations"""
        return {
            'sequential': {
                'agent_count': 1,
                'checkpoint_frequency': 'high',
                'parallelism': False,
                'coordination': 'sync',
                'best_for': ['simple_pipelines', 'low_dependency_workflows']
            },
            'parallel': {
                'agent_count': 'auto',
                'checkpoint_frequency': 'low',
                'parallelism': True,
                'coordination': 'async',
                'aggregation': 'majority',
                'best_for': ['independent_tasks', 'redundancy_required']
            },
            'hierarchical': {
                'levels': 3,
                'fan_out': 5,
                'checkpoint_frequency': 'medium',
                'coordination': 'tree',
                'best_for': ['large_scale_workflows', 'clear_authority']
            },
            'map_reduce': {
                'mappers': 'auto',
                'reducers': 'auto',
                'chunk_size': 10,
                'aggregation': 'mean',
                'best_for': ['data_processing', 'batch_operations']
            }
        }

    def _generate_composition_configs(self) -> Dict[str, Dict]:
        """Generate agent composition configurations"""
        return {
            'generalist': {
                'agent_types': ['core'],
                'specialization': 'low',
                'adaptability': 'high',
                'best_for': ['dynamic_workloads', 'unknown_task_types']
            },
            'specialist': {
                'agent_types': ['role'],
                'specialization': 'high',
                'adaptability': 'low',
                'best_for': ['specialized_tasks', 'high_quality_requirements']
            },
            'hybrid': {
                'agent_types': ['core', 'role', 'task'],
                'generalist_ratio': 0.3,
                'specialist_ratio': 0.7,
                'best_for': ['mixed_workloads', 'balanced_performance']
            }
        }

    def _generate_coordination_config(self) -> Dict[str, Any]:
        """Generate coordination configuration"""
        return {
            'a2a_overhead': 0.001,  # 1ms per A2A package
            'sync_strategy': 'async',
            'timeout_ms': 5000,
            'max_retries': 3,
            'strategies': {
                'fine_grained': {
                    'sync': 'async',
                    'batching': True,
                    'batch_size': 10
                },
                'medium_grained': {
                    'sync': 'hybrid',
                    'batching': False,
                    'sync_frequency': 5
                },
                'coarse_grained': {
                    'sync': 'sync',
                    'batching': False,
                    'checkpoint_frequency': 'high'
                }
            }
        }

    def _generate_error_handling_config(self) -> Dict[str, Any]:
        """Generate error handling configuration"""
        return {
            'retry_strategy': 'exponential_backoff',
            'fallback': 'degrade_gracefully',
            'circuit_breaker': {
                'enabled': True,
                'threshold': 0.5,
                'window_ms': 60000,
                'half_open_after_ms': 30000
            },
            'stress_levels': {
                'low': {
                    'max_retries': 1,
                    'fallback': 'fail_fast'
                },
                'medium': {
                    'max_retries': 3,
                    'fallback': 'degrade_gracefully'
                },
                'high': {
                    'max_retries': 5,
                    'fallback': 'use_backup',
                    'circuit_breaker': True
                },
                'extreme': {
                    'max_retries': 5,
                    'fallback': 'use_backup',
                    'circuit_breaker': True,
                    'redundancy': 2
                }
            }
        }

    def _generate_granularity_config(self) -> Dict[str, Dict]:
        """Generate task granularity configurations"""
        return {
            'fine': {
                'task_duration': 'seconds',
                'overhead_ratio': 0.1,
                'best_for': ['real_time_processing', 'interactive_workflows'],
                'coordination': 'async'
            },
            'medium': {
                'task_duration': 'minutes',
                'overhead_ratio': 0.05,
                'best_for': ['batch_processing', 'data_pipelines'],
                'coordination': 'hybrid'
            },
            'coarse': {
                'task_duration': 'hours',
                'overhead_ratio': 0.01,
                'best_for': ['long_running_jobs', 'analytics'],
                'coordination': 'sync'
            }
        }

    def _generate_recommendations(self) -> Dict[str, Any]:
        """Generate workflow recommendations based on simulations"""
        return {
            'task_type_mapping': {
                'data_pipeline': {
                    'pattern': 'sequential',
                    'granularity': 'medium',
                    'composition': 'specialist'
                },
                'code_review': {
                    'pattern': 'parallel',
                    'granularity': 'fine',
                    'composition': 'specialist'
                },
                'research_task': {
                    'pattern': 'map_reduce',
                    'granularity': 'fine',
                    'composition': 'hybrid'
                },
                'batch_processing': {
                    'pattern': 'map_reduce',
                    'granularity': 'coarse',
                    'composition': 'generalist'
                },
                'complex_workflow': {
                    'pattern': 'hierarchical',
                    'granularity': 'medium',
                    'composition': 'hybrid'
                }
            },
            'complexity_guidelines': {
                'low': {
                    'recommended_pattern': 'sequential',
                    'agent_count': 1,
                    'coordination': 'sync'
                },
                'medium': {
                    'recommended_pattern': 'parallel',
                    'agent_count': 5,
                    'coordination': 'async'
                },
                'high': {
                    'recommended_pattern': 'hierarchical',
                    'agent_count': 10,
                    'coordination': 'tree'
                }
            },
            'scalability_guidelines': {
                'small_scale': {
                    'max_agents': 5,
                    'pattern': 'sequential',
                    'granularity': 'coarse'
                },
                'medium_scale': {
                    'max_agents': 20,
                    'pattern': 'parallel',
                    'granularity': 'medium'
                },
                'large_scale': {
                    'max_agents': 100,
                    'pattern': 'map_reduce',
                    'granularity': 'fine'
                }
            }
        }


def generate_typescript_config(config: Dict[str, Any], output_path: str) -> None:
    """Generate TypeScript configuration file"""
    typescript_content = f"""/**
 * Workflow Domain Configuration for POLLN
 * Auto-generated from simulation results
 */

export const WORKFLOW_DOMAIN_CONFIG = {json.dumps(config, indent=2)};

/**
 * Helper function to get pattern config
 */
export function getPatternConfig(pattern: string) {{
  return WORKFLOW_DOMAIN_CONFIG.patterns[pattern];
}}

/**
 * Helper function to get composition config
 */
export function getCompositionConfig(composition: string) {{
  return WORKFLOW_DOMAIN_CONFIG.composition[composition];
}}

/**
 * Helper function to get granularity config
 */
export function getGranularityConfig(granularity: string) {{
  return WORKFLOW_DOMAIN_CONFIG.granularity[granularity];
}}

/**
 * Helper function to get recommendation for task type
 */
export function getRecommendation(taskType: string) {{
  return WORKFLOW_DOMAIN_CONFIG.recommendations.task_type_mapping[taskType];
}}
"""

    with open(output_path, 'w') as f:
        f.write(typescript_content)


def main():
    """Main generation workflow"""
    print("="*60)
    print("Workflow Configuration Generator")
    print("="*60)

    # Create output directory
    os.makedirs("simulation_results", exist_ok=True)

    # Generate configuration
    generator = WorkflowConfigGenerator()
    config = generator.generate_workflow_config()

    # Save JSON configuration
    json_path = "simulation_results/workflow_config.json"
    with open(json_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\nJSON configuration saved to: {json_path}")

    # Generate TypeScript configuration
    typescript_path = "src/domains/workflows/config.ts"
    os.makedirs(os.path.dirname(typescript_path), exist_ok=True)
    generate_typescript_config(config, typescript_path)
    print(f"TypeScript configuration saved to: {typescript_path}")

    # Print summary
    print("\n" + "="*60)
    print("Configuration Summary")
    print("="*60)
    print(f"Patterns configured: {len(config['patterns'])}")
    print(f"Composition strategies: {len(config['composition'])}")
    print(f"Granularity levels: {len(config['granularity'])}")
    print(f"Task type mappings: {len(config['recommendations']['task_type_mapping'])}")

    return config


if __name__ == '__main__':
    config = main()
    print("\n" + "="*60)
    print("Configuration generation complete!")
