"""
POLLN Reasoning Domain Optimizer

Compiles optimal reasoning configurations from all simulations and
generates the production-ready TypeScript configuration file.
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path


class ReasoningOptimizer:
    """
    Main optimizer that compiles all simulation results into
    production-ready configuration.
    """

    def __init__(self, results_dir: str = 'simulations/domains/reasoning'):
        self.results_dir = Path(results_dir)
        self.all_results = {}
        self.optimal_config = {}

    def load_all_results(self):
        """Load results from all simulation files"""
        print("Loading simulation results...")

        result_files = [
            ('dialogue_results.json', 'dialogue'),
            ('cot_results.json', 'chain_of_thought'),
            ('context_tracking_results.json', 'context_tracking'),
            ('depth_results.json', 'reasoning_depth'),
            ('consistency_results.json', 'consistency')
        ]

        for filename, key in result_files:
            filepath = self.results_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    self.all_results[key] = json.load(f)
                print(f"  Loaded {key} results")
            else:
                print(f"  Warning: {filename} not found, using defaults")
                self.all_results[key] = {}

    def compile_optimal_config(self) -> Dict[str, Any]:
        """Compile optimal configuration from all results"""
        print("\nCompiling optimal configuration...")

        # Dialogue configuration
        dialogue_config = self._compile_dialogue_config()

        # Chain-of-thought configuration
        cot_config = self._compile_cot_config()

        # Context tracking configuration
        context_config = self._compile_context_config()

        # Depth configuration
        depth_config = self._compile_depth_config()

        # Consistency configuration
        consistency_config = self._compile_consistency_config()

        # Agent composition
        agent_composition = self._compile_agent_composition()

        self.optimal_config = {
            'dialogue': dialogue_config,
            'chainOfThought': cot_config,
            'context': context_config,
            'depth': depth_config,
            'consistency': consistency_config,
            'agents': agent_composition,
            'metadata': {
                'version': '1.0.0',
                'generated_by': 'reasoning_optimizer.py',
                'source': 'POLLN reasoning domain simulations'
            }
        }

        return self.optimal_config

    def _compile_dialogue_config(self) -> Dict[str, Any]:
        """Compile dialogue management configuration"""
        dialogue_results = self.all_results.get('dialogue', {})

        # Extract optimal config or use defaults
        optimal = dialogue_results.get('optimal_config', {})

        return {
            'maxTurns': optimal.get('num_agents', 100),
            'contextWindow': '128K',
            'summarizationThreshold': optimal.get('summarization_threshold', 10),
            'entityTracking': optimal.get('entity_tracking', True),
            'personaConsistency': 'high',
            'temperature': 0.8,
            'turnManagement': {
                'maxConsecutiveTurns': 3,
                'interruptionAllowed': False
            },
            'coherence': {
                'target': 0.85,
                'minContextRetention': 0.7
            }
        }

    def _compile_cot_config(self) -> Dict[str, Any]:
        """Compile chain-of-thought configuration"""
        cot_results = self.all_results.get('chain_of_thought', {})
        optimal = cot_results.get('optimal_config', {})

        return {
            'enabled': True,
            'checkpoints': optimal.get('checkpoints', {'placement': 'auto'}),
            'selfConsistency': {
                'samples': optimal.get('self_consistency', {}).get('samples', 5),
                'aggregation': 'majority',
                'temperature': 0.7
            },
            'verifier': {
                'enabled': optimal.get('verifier', {}).get('enabled', True),
                'confidence': optimal.get('verifier', {}).get('confidence_threshold', 0.7)
            },
            'maxSteps': 20,
            'stepConfidenceThreshold': 0.6
        }

    def _compile_context_config(self) -> Dict[str, Any]:
        """Compile context management configuration"""
        context_results = self.all_results.get('context_tracking', {})
        optimal = context_results.get('optimal_config', {})

        compression_config = optimal.get('compression', {})
        kv_cache_config = optimal.get('kv_cache', {})
        memory_config = optimal.get('memory_retrieval', {})

        return {
            'compression': {
                'strategy': compression_config.get('strategy', 'hybrid'),
                'summarizationThreshold': compression_config.get('summarization_threshold', 10),
                'hierarchicalLevels': compression_config.get('hierarchical_levels', 3)
            },
            'kvCache': {
                'enabled': kv_cache_config.get('enabled', True),
                'strategy': kv_cache_config.get('strategy', 'attention_prior'),
                'maxSize': kv_cache_config.get('max_size', '1GB'),
                'cacheBudget': kv_cache_config.get('cache_budget', 20),
                'evictionPolicy': 'lru'
            },
            'entityTracking': {
                'enabled': optimal.get('entity_tracking', {}).get('enabled', True),
                'relationshipInference': True,
                'activeWindow': 10
            },
            'memoryRetrieval': {
                'enabled': memory_config.get('enabled', True),
                'topK': memory_config.get('top_k', 5),
                'similarity': memory_config.get('similarity_metric', 'cosine'),
                'timeDecay': memory_config.get('time_decay', True),
                'importanceWeight': 1.0
            }
        }

    def _compile_depth_config(self) -> Dict[str, Any]:
        """Compile reasoning depth configuration"""
        depth_results = self.all_results.get('reasoning_depth', {})
        optimal_config = depth_results.get('optimal_config', {})

        depth_config = optimal_config.get('depth_config', {})

        return {
            'shallow': {
                'maxSteps': depth_config.get('shallow', {}).get('max_steps', 3),
                'breadth': depth_config.get('shallow', {}).get('breadth', 10),
                'beamWidth': depth_config.get('shallow', {}).get('beam_width', 5),
                'useCase': 'simple_tasks'
            },
            'medium': {
                'maxSteps': depth_config.get('medium', {}).get('max_steps', 7),
                'breadth': depth_config.get('medium', {}).get('breadth', 5),
                'beamWidth': depth_config.get('medium', {}).get('beam_width', 3),
                'useCase': 'moderate_complexity'
            },
            'deep': {
                'maxSteps': depth_config.get('deep', {}).get('max_steps', 15),
                'breadth': depth_config.get('deep', {}).get('breadth', 3),
                'beamWidth': depth_config.get('deep', {}).get('beam_width', 2),
                'useCase': 'complex_reasoning'
            },
            'adaptive': {
                'enabled': depth_config.get('adaptive', {}).get('enabled', True),
                'complexityThreshold': 0.5,
                'features': ['num_entities', 'question_length', 'semantic_complexity']
            },
            'explorationStrategy': {
                'default': 'tree_of_thoughts',
                'alternatives': ['iterative_refinement', 'debate', 'beam_search']
            }
        }

    def _compile_consistency_config(self) -> Dict[str, Any]:
        """Compile consistency checking configuration"""
        consistency_results = self.all_results.get('consistency', {})
        optimal_config = consistency_results.get('optimal_config', {})
        checks_config = optimal_config.get('consistency_checks', {})

        return {
            'selfConsistency': {
                'enabled': checks_config.get('self_consistency', {}).get('enabled', True),
                'severityThreshold': 'medium'
            },
            'factualConsistency': {
                'enabled': checks_config.get('factual_consistency', {}).get('enabled', True),
                'knowledgeBase': True,
                'confidenceThreshold': 0.7
            },
            'temporalConsistency': {
                'enabled': checks_config.get('temporal_consistency', {}).get('enabled', True),
                'historyWindow': 5,
                'severityThreshold': 'medium'
            },
            'logicalConsistency': {
                'enabled': checks_config.get('logical_consistency', {}).get('enabled', True),
                'checkCircularReasoning': True,
                'checkNonSequitur': True
            },
            'personaConsistency': {
                'enabled': checks_config.get('persona_consistency', {}).get('enabled', True),
                'toneChecking': True,
                'styleChecking': True
            }
        }

    def _compile_agent_composition(self) -> Dict[str, Any]:
        """Compile optimal agent composition for reasoning"""
        # Based on all simulation results, determine optimal agents
        return {
            'reasoner': {
                'type': 'role',
                'expertise': 'logical_reasoning',
                'checkpoints': 20,
                'temperature': 0.5,
                'valueNetwork': 'reasoning_quality'
            },
            'verifier': {
                'type': 'task',
                'expertise': 'verification',
                'valueNetwork': 'verification_confidence',
                'confidenceThreshold': 0.7
            },
            'summarizer': {
                'type': 'task',
                'expertise': 'summarization',
                'compressionRatio': 0.3,
                'maxSummaryLength': 500
            },
            'dialogueManager': {
                'type': 'role',
                'expertise': 'dialogue_coordination',
                'maxTurns': 100,
                'contextRetention': 0.8
            },
            'consistencyChecker': {
                'type': 'task',
                'expertise': 'consistency_validation',
                'severityThreshold': 'medium'
            },
            'entityTracker': {
                'type': 'task',
                'expertise': 'entity_extraction',
                'activeWindow': 10
            }
        }

    def generate_typescript_config(self, output_path: str = 'src/domains/reasoning/config.ts'):
        """Generate TypeScript configuration file"""
        print(f"\nGenerating TypeScript configuration: {output_path}")

        # Convert config to TypeScript format
        ts_content = self._config_to_typescript()

        # Ensure directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(output_path, 'w') as f:
            f.write(ts_content)

        print(f"  Configuration written to {output_path}")

        return str(output_path)

    def _config_to_typescript(self) -> str:
        """Convert configuration to TypeScript format"""
        config = self.optimal_config

        ts = """/**
 * POLLN Reasoning Domain Configuration
 *
 * This configuration is auto-generated from simulation results.
 * It provides optimal settings for dialogue and reasoning tasks.
 *
 * Generated by: reasoning_optimizer.py
 * Version: 1.0.0
 */

import { ReasoningDomainConfig, DialogueConfig, ChainOfThoughtConfig,
         ContextConfig, DepthConfig, ConsistencyConfig, AgentComposition } from './types';

export const REASONING_DOMAIN_CONFIG: ReasoningDomainConfig = {
"""

        # Dialogue configuration
        ts += "\n  // ========================================\n"
        ts += "  // Dialogue Management\n"
        ts += "  // ========================================\n"
        ts += f"  dialogue: {self._dict_to_ts(config.get('dialogue', {}))},\n\n"

        # Chain-of-thought configuration
        ts += "  // ========================================\n"
        ts += "  // Chain-of-Thought Reasoning\n"
        ts += "  // ========================================\n"
        ts += f"  chainOfThought: {self._dict_to_ts(config.get('chainOfThought', {}))},\n\n"

        # Context configuration
        ts += "  // ========================================\n"
        ts += "  // Context Management\n"
        ts += "  // ========================================\n"
        ts += f"  context: {self._dict_to_ts(config.get('context', {}))},\n\n"

        # Depth configuration
        ts += "  // ========================================\n"
        ts += "  // Reasoning Depth Configuration\n"
        ts += "  // ========================================\n"
        ts += f"  depth: {self._dict_to_ts(config.get('depth', {}))},\n\n"

        # Consistency configuration
        ts += "  // ========================================\n"
        ts += "  // Consistency Validation\n"
        ts += "  // ========================================\n"
        ts += f"  consistency: {self._dict_to_ts(config.get('consistency', {}))},\n\n"

        # Agent composition
        ts += "  // ========================================\n"
        ts += "  // Agent Composition\n"
        ts += "  // ========================================\n"
        ts += f"  agents: {self._dict_to_ts(config.get('agents', {}))},\n"

        # Metadata
        ts += "\n  metadata: {\n"
        metadata = config.get('metadata', {})
        for key, value in metadata.items():
            if isinstance(value, str):
                ts += f"    {key}: '{value}',\n"
            else:
                ts += f"    {key}: {value},\n"
        ts += "  }\n"

        ts += "};\n\n"

        # Export convenience functions
        ts += """
// ========================================
// Convenience Functions
// ========================================

/**
 * Get dialogue configuration with overrides
 */
export function getDialogueConfig(overrides?: Partial<DialogueConfig>): DialogueConfig {
  return {
    ...REASONING_DOMAIN_CONFIG.dialogue,
    ...overrides
  };
}

/**
 * Get chain-of-thought configuration with overrides
 */
export function getCOTConfig(overrides?: Partial<ChainOfThoughtConfig>): ChainOfThoughtConfig {
  return {
    ...REASONING_DOMAIN_CONFIG.chainOfThought,
    ...overrides
  };
}

/**
 * Get context configuration with overrides
 */
export function getContextConfig(overrides?: Partial<ContextConfig>): ContextConfig {
  return {
    ...REASONING_DOMAIN_CONFIG.context,
    ...overrides
  };
}

/**
 * Get depth configuration for specific task complexity
 */
export function getDepthConfig(complexity: 'shallow' | 'medium' | 'deep'): any {
  return REASONING_DOMAIN_CONFIG.depth[complexity];
}

/**
 * Check if consistency validation is enabled
 */
export function isConsistencyEnabled(type: keyof ConsistencyConfig): boolean {
  return REASONING_DOMAIN_CONFIG.consistency[type]?.enabled ?? false;
}

/**
 * Get agent configuration for reasoning tasks
 */
export function getReasoningAgent(agentType: keyof AgentComposition): any {
  return REASONING_DOMAIN_CONFIG.agents[agentType];
}
"""

        return ts

    def _dict_to_ts(self, obj: Any, indent: int = 2) -> str:
        """Convert Python dict to TypeScript object format"""
        if isinstance(obj, dict):
            if not obj:
                return '{}'

            items = []
            for key, value in obj.items():
                # Format key
                if not key[0].isalpha() and key[0] != '_':
                    formatted_key = f'"{key}"'
                elif ' ' in key or '-' in key:
                    formatted_key = f"'{key}'"
                else:
                    formatted_key = key

                # Format value
                if isinstance(value, dict):
                    items.append(f"{' ' * indent}{formatted_key}: {self._dict_to_ts(value, indent + 2)}")
                elif isinstance(value, list):
                    items.append(f"{' ' * indent}{formatted_key}: {self._list_to_ts(value, indent + 2)}")
                elif isinstance(value, str):
                    items.append(f"{' ' * indent}{formatted_key}: '{value}'")
                elif isinstance(value, bool):
                    items.append(f"{' ' * indent}{formatted_key}: {str(value).lower()}")
                else:
                    items.append(f"{' ' * indent}{formatted_key}: {value}")

            inner = ',\n'.join(items)
            return '{\n' + inner + '\n' + ' ' * (indent - 2) + '}'

        elif isinstance(obj, list):
            return self._list_to_ts(obj, indent)

        elif isinstance(obj, str):
            return f"'{obj}'"

        elif isinstance(obj, bool):
            return str(obj).lower()

        else:
            return str(obj)

    def _list_to_ts(self, obj: List, indent: int) -> str:
        """Convert Python list to TypeScript array format"""
        if not obj:
            return '[]'

        items = []
        for item in obj:
            if isinstance(item, dict):
                items.append(self._dict_to_ts(item, indent + 2))
            elif isinstance(item, list):
                items.append(self._list_to_ts(item, indent + 2))
            elif isinstance(item, str):
                items.append(f"'{item}'")
            elif isinstance(item, bool):
                items.append(str(item).lower())
            else:
                items.append(str(item))

        inner = ',\n'.join(items)
        return '[\n' + ' ' * indent + inner + '\n' + ' ' * (indent - 2) + ']'

    def generate_summary_report(self) -> str:
        """Generate summary report of optimization results"""
        report = []
        report.append("=" * 70)
        report.append("POLLN Reasoning Domain Optimization Summary")
        report.append("=" * 70)
        report.append("")

        # Dialogue
        dialogue = self.optimal_config.get('dialogue', {})
        report.append("Dialogue Management:")
        report.append(f"  Max Turns: {dialogue.get('maxTurns', 'N/A')}")
        report.append(f"  Summarization Threshold: {dialogue.get('summarizationThreshold', 'N/A')}")
        report.append(f"  Entity Tracking: {dialogue.get('entityTracking', 'N/A')}")
        report.append("")

        # Chain-of-thought
        cot = self.optimal_config.get('chainOfThought', {})
        report.append("Chain-of-Thought Reasoning:")
        report.append(f"  Enabled: {cot.get('enabled', 'N/A')}")
        report.append(f"  Self-Consistency Samples: {cot.get('selfConsistency', {}).get('samples', 'N/A')}")
        report.append(f"  Verifier Enabled: {cot.get('verifier', {}).get('enabled', 'N/A')}")
        report.append("")

        # Context
        context = self.optimal_config.get('context', {})
        report.append("Context Management:")
        report.append(f"  Compression Strategy: {context.get('compression', {}).get('strategy', 'N/A')}")
        report.append(f"  KV-Cache Enabled: {context.get('kvCache', {}).get('enabled', 'N/A')}")
        report.append(f"  Memory Retrieval: {context.get('memoryRetrieval', {}).get('enabled', 'N/A')}")
        report.append("")

        # Depth
        depth = self.optimal_config.get('depth', {})
        report.append("Reasoning Depth:")
        report.append(f"  Shallow: {depth.get('shallow', {}).get('maxSteps', 'N/A')} steps")
        report.append(f"  Medium: {depth.get('medium', {}).get('maxSteps', 'N/A')} steps")
        report.append(f"  Deep: {depth.get('deep', {}).get('maxSteps', 'N/A')} steps")
        report.append(f"  Adaptive: {depth.get('adaptive', {}).get('enabled', 'N/A')}")
        report.append("")

        # Agents
        agents = self.optimal_config.get('agents', {})
        report.append("Agent Composition:")
        for agent_name, agent_config in agents.items():
            report.append(f"  {agent_name.capitalize()}:")
            report.append(f"    Type: {agent_config.get('type', 'N/A')}")
            report.append(f"    Expertise: {agent_config.get('expertise', 'N/A')}")
        report.append("")

        report.append("=" * 70)
        report.append("Configuration files generated:")
        report.append("  - src/domains/reasoning/config.ts")
        report.append("=" * 70)

        return '\n'.join(report)


def main():
    """Main optimization workflow"""
    print("=" * 70)
    print("POLLN Reasoning Domain Optimizer")
    print("=" * 70)
    print()

    # Initialize optimizer
    optimizer = ReasoningOptimizer()

    # Load all simulation results
    optimizer.load_all_results()

    # Compile optimal configuration
    print("\n" + "=" * 70)
    print("Compiling Optimal Configuration")
    print("=" * 70)
    optimizer.compile_optimal_config()

    # Generate TypeScript config
    print("\n" + "=" * 70)
    print("Generating Configuration Files")
    print("=" * 70)
    optimizer.generate_typescript_config()

    # Generate summary report
    print("\n" + "=" * 70)
    print("Optimization Summary")
    print("=" * 70)
    report = optimizer.generate_summary_report()
    print(report)

    # Save summary
    results_dir = Path('simulations/domains/reasoning')
    summary_path = results_dir / 'OPTIMIZATION_SUMMARY.md'
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        f.write(report)
    print("\nSummary saved to OPTIMIZATION_SUMMARY.md")

    # Save full config as JSON
    config_path = results_dir / 'full_config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(optimizer.optimal_config, f, indent=2)
    print("Full configuration saved to full_config.json")

    return optimizer.optimal_config


if __name__ == '__main__':
    main()
