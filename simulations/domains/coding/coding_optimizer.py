"""
Coding Domain Optimizer

Compiles optimal coding configurations from simulation results and generates
TypeScript configuration files for the POLLN system.
"""

import json
import os
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """Result from a simulation"""
    simulation_name: str
    metrics: Dict
    recommendations: Dict


class CodingDomainOptimizer:
    """Optimizes POLLN for coding domain"""

    def __init__(self):
        self.results: List[OptimizationResult] = []

    def load_simulation_results(self, results_dir: str = ".") -> None:
        """Load all simulation result files"""
        import glob

        result_files = glob.glob(os.path.join(results_dir, "*_results.json"))

        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                sim_name = os.path.basename(file_path).replace("_results.json", "")
                self.results.append(OptimizationResult(
                    simulation_name=sim_name,
                    metrics=data,
                    recommendations=data.get("recommendations", {})
                ))

                print(f"Loaded results from: {sim_name}")

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def compile_optimal_config(self) -> Dict:
        """Compile optimal configuration from all simulations"""
        config = {
            "domain": "coding",
            "version": "1.0.0",
            "generated": "2026-03-07",

            # Code generation configuration
            "generation": {},

            # Agent configurations
            "agents": {},

            # Value network
            "valueFunction": {},

            # Refactoring
            "refactoring": {},

            # Debugging
            "debugging": {},

            # Code review
            "codeReview": {},
        }

        # Compile from each simulation
        for result in self.results:
            sim_name = result.simulation_name

            if sim_name == "code_generation":
                config["generation"] = self._compile_generation_config(result)
            elif sim_name == "code_review":
                config["codeReview"] = self._compile_review_config(result)
            elif sim_name == "debugging":
                config["debugging"] = self._compile_debugging_config(result)
            elif sim_name == "refactoring":
                config["refactoring"] = self._compile_refactoring_config(result)

        # Compile agent configurations
        config["agents"] = self._compile_agent_configs(config)

        # Compile value network
        config["valueFunction"] = self._compile_value_network_config()

        return config

    def _compile_generation_config(self, result: OptimizationResult) -> Dict:
        """Compile code generation configuration"""
        recs = result.recommendations

        checkpoint_opt = result.metrics.get("checkpoint_optimization", {})
        optimal_checkpoints = checkpoint_opt.get("optimal_checkpoints", 15)

        return {
            "temperature": recs.get("optimal_temperature", 0.3),
            "topP": 0.9,
            "frequencyPenalty": 0.1,
            "stopTokens": ["```", "\n\n"],
            "maxTokens": 2000,
            "checkpoints": optimal_checkpoints,
            "modelSize": recs.get("optimal_model_size", "100M"),
            "useValueNetwork": recs.get("use_value_network", True),
        }

    def _compile_review_config(self, result: OptimizationResult) -> Dict:
        """Compile code review configuration"""
        recs = result.recommendations

        config_opt = result.metrics.get("configuration_optimization", {})
        optimal_config = config_opt.get("optimal_config", "100M_vnTrue")

        # Parse optimal config
        model_size = optimal_config.split("_")[0] if "_" in optimal_config else "100M"
        use_value_network = "vnTrue" in optimal_config

        return {
            "modelSize": model_size,
            "useValueNetwork": use_value_network,
            "valueFunction": "code_quality",
            "minConfidenceThreshold": recs.get("min_confidence_threshold", 0.3),
            "maxIssuesPerReview": recs.get("max_issues_per_review", 50),
            "priorityFiltering": recs.get("priority_filtering", True),
        }

    def _compile_debugging_config(self, result: OptimizationResult) -> Dict:
        """Compile debugging configuration"""
        recs = result.recommendations

        workflow_opt = result.metrics.get("workflow_optimization", {})
        optimal_config = workflow_opt.get("optimal_config", "iter5_cp5")

        # Parse optimal config
        parts = optimal_config.split("_")
        max_iterations = int(parts[0].replace("iter", "")) if len(parts) > 0 else 5
        checkpoint_freq = int(parts[1].replace("cp", "")) if len(parts) > 1 else 5

        return {
            "maxIterations": max_iterations,
            "checkpointFrequency": checkpoint_freq,
            "useIterativeReasoning": recs.get("use_iterative_reasoning", True),
            "strategySequence": recs.get("strategy_sequence", [
                "incremental",
                "hypothesis_testing",
                "symbolic_execution",
                "binary_search"
            ]),
            "fixValidation": recs.get("fix_validation", True),
            "earlyTerminationThreshold": recs.get("early_termination_threshold", 0.8),
        }

    def _compile_refactoring_config(self, result: OptimizationResult) -> Dict:
        """Compile refactoring configuration"""
        recs = result.recommendations

        config_opt = result.metrics.get("configuration_optimization", {})
        optimal_config = config_opt.get("optimal_config", "chunk5_files50")

        # Parse optimal config
        parts = optimal_config.split("_")
        chunk_size = int(parts[0].replace("chunk", "")) if len(parts) > 0 else 5
        max_files = int(parts[1].replace("files", "")) if len(parts) > 1 else 50

        return {
            "multiFile": recs.get("multi_file", True),
            "consistency": recs.get("consistency_check", "high"),
            "maxFiles": max_files,
            "chunkSize": chunk_size,
            "batchRefactoring": recs.get("batch_refactoring", True),
            "consistencyThreshold": 0.8,
        }

    def _compile_agent_configs(self, config: Dict) -> Dict:
        """Compile agent configurations"""
        return {
            "generator": {
                "type": "role",
                "expertise": "code_generation",
                "modelSize": config["generation"]["modelSize"],
                "checkpoints": config["generation"]["checkpoints"],
                "temperature": config["generation"]["temperature"],
            },
            "reviewer": {
                "type": "role",
                "expertise": "code_review",
                "modelSize": config["codeReview"]["modelSize"],
                "useValueNetwork": config["codeReview"]["useValueNetwork"],
                "valueNetwork": "code_quality",
                "minConfidence": config["codeReview"]["minConfidenceThreshold"],
            },
            "debugger": {
                "type": "task",
                "expertise": "debugging",
                "iterative": config["debugging"]["useIterativeReasoning"],
                "maxIterations": config["debugging"]["maxIterations"],
                "checkpointFrequency": config["debugging"]["checkpointFrequency"],
            },
            "refactorer": {
                "type": "role",
                "expertise": "refactoring",
                "multiFile": config["refactoring"]["multiFile"],
                "maxFiles": config["refactoring"]["maxFiles"],
                "chunkSize": config["refactoring"]["chunkSize"],
                "consistencyThreshold": config["refactoring"]["consistencyThreshold"],
            },
        }

    def _compile_value_network_config(self) -> Dict:
        """Compile value network configuration"""
        return {
            "features": [
                "syntactic_correctness",
                "semantic_correctness",
                "test_coverage",
                "complexity",
                "maintainability",
                "security_score"
            ],
            "weights": {
                "correctness": 0.5,
                "test_pass_rate": 0.3,
                "maintainability": 0.1,
                "security": 0.1
            },
            "network": {
                "inputSize": 6,
                "hiddenLayers": [64, 32, 16],
                "outputSize": 1,
                "activation": "relu",
                "outputActivation": "sigmoid"
            },
            "training": {
                "lossFunction": "mse",
                "optimizer": "adam",
                "learningRate": 0.001,
                "batchSize": 32,
                "epochs": 100
            },
            "tdLambda": {
                "lambda": 0.9,
                "gamma": 0.99
            }
        }

    def generate_typescript_config(self, output_path: str) -> None:
        """Generate TypeScript configuration file"""
        config = self.compile_optimal_config()

        ts_content = self._dict_to_typescript(config, "CODING_DOMAIN_CONFIG")

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(ts_content)

        print(f"Generated TypeScript config: {output_path}")

    def _dict_to_typescript(self, data: dict, var_name: str, indent: int = 0) -> str:
        """Convert dict to TypeScript syntax"""
        tabs = "  " * indent
        lines = []

        lines.append(f"{tabs}export const {var_name} = {{")

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{tabs}  {key}: {{")
                lines.append(self._dict_to_typescript(value, "", indent + 2))
                lines.append(f"{tabs}  }},")
            elif isinstance(value, list):
                ts_list = json.dumps(value)
                lines.append(f"{tabs}  {key}: {ts_list},")
            elif isinstance(value, str):
                lines.append(f'{tabs}  {key}: "{value}",')
            elif isinstance(value, bool):
                lines.append(f"{tabs}  {key}: {str(value).lower()},")
            else:
                lines.append(f"{tabs}  {key}: {value},")

        lines.append(f"{tabs}}};")

        return "\n".join(lines)


def generate_complete_config():
    """Generate complete coding domain configuration"""
    print("Coding Domain Optimizer")
    print("="*80)

    optimizer = CodingDomainOptimizer()

    # Load simulation results
    print("\nLoading simulation results...")
    optimizer.load_simulation_results()

    if not optimizer.results:
        print("No simulation results found. Using default configurations.")

        # Add default results
        optimizer.results = [
            OptimizationResult("code_generation", {}, {
                "optimal_temperature": 0.3,
                "optimal_checkpoints": 15,
                "optimal_model_size": "100M",
            }),
            OptimizationResult("code_review", {}, {
                "optimal_model_size": "100M",
                "use_value_network": True,
            }),
            OptimizationResult("debugging", {}, {
                "max_iterations": 5,
                "checkpoint_frequency": 5,
            }),
            OptimizationResult("refactoring", {}, {
                "chunk_size": 5,
                "max_files": 50,
            }),
        ]

    # Compile optimal configuration
    print("\nCompiling optimal configuration...")
    config = optimizer.compile_optimal_config()

    print("\nOptimal Configuration:")
    print(json.dumps(config, indent=2))

    # Generate TypeScript file
    output_path = "src/domains/coding/config.ts"
    print(f"\nGenerating TypeScript configuration: {output_path}")
    optimizer.generate_typescript_config(output_path)

    # Generate additional configuration files
    print("\nGenerating additional configuration files...")

    # Value network config
    value_config_path = "src/domains/coding/value-network-config.ts"
    os.makedirs(os.path.dirname(value_config_path), exist_ok=True)

    with open(value_config_path, 'w') as f:
        f.write(generate_value_network_ts_config())

    print(f"  Generated: {value_config_path}")

    # Task definitions
    tasks_config_path = "src/domains/coding/tasks.ts"
    with open(tasks_config_path, 'w') as f:
        f.write(generate_tasks_ts_config())

    print(f"  Generated: {tasks_config_path}")

    print("\n" + "="*80)
    print("Configuration generation complete!")
    print("="*80)


def generate_value_network_ts_config() -> str:
    """Generate value network TypeScript configuration"""
    return """
import { ValueNetworkConfig } from '../../core/types';

export const CODE_QUALITY_VALUE_CONFIG: ValueNetworkConfig = {
  // Input features for value network
  features: [
    'syntactic_correctness',
    'semantic_correctness',
    'test_coverage',
    'complexity',
    'maintainability',
    'security_score'
  ],

  // Reward function weights
  rewardWeights: {
    correctness: 0.5,
    test_pass_rate: 0.3,
    maintainability: 0.1,
    security: 0.1
  },

  // Network architecture
  network: {
    inputSize: 6,
    hiddenLayers: [64, 32, 16],
    outputSize: 1,
    activation: 'relu',
    outputActivation: 'sigmoid'
  },

  // Training parameters
  training: {
    lossFunction: 'mse',
    optimizer: 'adam',
    learningRate: 0.001,
    batchSize: 32,
    epochs: 100
  },

  // TD(lambda) parameters
  tdLambda: {
    lambda: 0.9,
    gamma: 0.99
  },

  // Quality thresholds
  thresholds: {
    excellent: 0.9,
    good: 0.7,
    acceptable: 0.5,
    poor: 0.3
  }
};
"""


def generate_tasks_ts_config() -> str:
    """Generate task definitions TypeScript configuration"""
    return """
import { TaskDefinition } from '../../core/types';

export const CODING_TASKS: Record<string, TaskDefinition> = {
  // Code generation tasks
  generate_function: {
    name: 'generate_function',
    description: 'Generate a function from specification',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 15,
    maxTokens: 2000,
  },

  generate_class: {
    name: 'generate_class',
    description: 'Generate a class from specification',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 15,
    maxTokens: 3000,
  },

  generate_api: {
    name: 'generate_api',
    description: 'Generate API endpoint implementation',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 20,
    maxTokens: 2500,
  },

  // Code review tasks
  review_code: {
    name: 'review_code',
    description: 'Review code for bugs and issues',
    agentType: 'role',
    expertise: 'code_review',
    useValueNetwork: true,
    valueNetwork: 'code_quality',
  },

  detect_bugs: {
    name: 'detect_bugs',
    description: 'Detect bugs in code',
    agentType: 'task',
    expertise: 'code_review',
    temperature: 0.2,
  },

  // Debugging tasks
  debug_issue: {
    name: 'debug_issue',
    description: 'Debug and fix a reported issue',
    agentType: 'task',
    expertise: 'debugging',
    iterative: true,
    maxIterations: 5,
    checkpointFrequency: 5,
  },

  localize_bug: {
    name: 'localize_bug',
    description: 'Locate the source of a bug',
    agentType: 'task',
    expertise: 'debugging',
    temperature: 0.4,
  },

  // Refactoring tasks
  refactor_file: {
    name: 'refactor_file',
    description: 'Refactor a single file',
    agentType: 'role',
    expertise: 'refactoring',
    multiFile: false,
  },

  refactor_project: {
    name: 'refactor_project',
    description: 'Refactor multiple files maintaining consistency',
    agentType: 'role',
    expertise: 'refactoring',
    multiFile: true,
    maxFiles: 50,
    chunkSize: 5,
    consistencyThreshold: 0.8,
  },

  extract_method: {
    name: 'extract_method',
    description: 'Extract a method from code',
    agentType: 'task',
    expertise: 'refactoring',
    temperature: 0.2,
  },
};
"""


if __name__ == "__main__":
    generate_complete_config()
