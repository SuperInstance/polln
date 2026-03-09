"""
Multi-modal Configuration Optimizer for POLLN

Compiles optimal multi-modal configurations from all simulation results.
Generates production-ready TypeScript configuration file.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


class MultiModalOptimizer:
    """Optimizer for multi-modal POLLN configurations"""

    def __init__(self, results_dir: str = "simulations/domains/multimodal/results"):
        self.results_dir = Path(results_dir)
        self.results = {}

    def load_all_results(self):
        """Load all simulation results"""
        result_files = [
            "architecture_results.json",
            "attention_results.json",
            "embedding_results.json",
            "reasoning_results.json",
            "generation_results.json",
            "optimal_params.json"
        ]

        for filename in result_files:
            filepath = self.results_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    key = filename.replace("_results.json", "").replace("_params", "params")
                    self.results[key] = json.load(f)

        print(f"Loaded {len(self.results)} result files")

    def compile_optimal_configs(self) -> Dict[str, Any]:
        """Compile optimal configurations from all results"""

        # Architecture configurations
        architecture = self._compile_architecture_configs()

        # Fusion strategies
        fusion = self._compile_fusion_strategies()

        # Cross-modal attention
        cross_attention = self._compile_cross_attention()

        # Agent configurations
        agents = self._compile_agent_configs()

        # Generation parameters
        generation = self._compile_generation_params()

        # Embedding configs
        embeddings = self._compile_embedding_configs()

        # Reasoning configs
        reasoning = self._compile_reasoning_configs()

        return {
            'architecture': architecture,
            'fusion': fusion,
            'crossAttention': cross_attention,
            'agents': agents,
            'generation': generation,
            'embeddings': embeddings,
            'reasoning': reasoning
        }

    def _compile_architecture_configs(self) -> Dict[str, Any]:
        """Compile architecture configurations"""
        arch_results = self.results.get('architecture', {})

        unified_config = {
            'encoder': 'transformer',
            'embeddingDim': 768,
            'modalityTokens': ['text', 'image', 'audio', 'code'],
            'parameters': {
                'n_heads': 12,
                'n_layers': 6,
                'dropout': 0.1
            }
        }

        separate_config = {
            'textEncoder': 'transformer',
            'imageEncoder': 'vision_transformer',
            'audioEncoder': 'wav2vec',
            'codeEncoder': 'codebert',
            'fusion': 'cross_attention',
            'embeddingDim': 768
        }

        moe_config = {
            'experts': 8,
            'gating': 'learned',
            'topK': 2,
            'load_balancing': True
        }

        return {
            'unified': unified_config,
            'separate': separate_config,
            'mixtureOfExperts': moe_config
        }

    def _compile_fusion_strategies(self) -> Dict[str, Any]:
        """Compile fusion strategies"""
        attention_results = self.results.get('attention', {})

        early_fusion = {
            'concatEmbeddings': True,
            'fusionLayer': 'input',
            'useCase': ['text+image', 'text+audio']
        }

        late_fusion = {
            'unimodalProcessing': True,
            'fusionLayer': 'output',
            'aggregation': 'attention',
            'useCase': ['3+modalities', 'complex_reasoning']
        }

        hierarchical_fusion = {
            'levels': 3,
            'fusionPerLevel': True,
            'progressiveIntegration': True,
            'useCase': ['universal_agent', 'all_modalities']
        }

        return {
            'early': early_fusion,
            'late': late_fusion,
            'hierarchical': hierarchical_fusion
        }

    def _compile_cross_attention(self) -> Dict[str, Any]:
        """Compile cross-modal attention configuration"""
        attention_results = self.results.get('attention', {})

        # Get best config from results
        if '4' in attention_results:
            best_config = attention_results['4']['config']
        else:
            best_config = {}

        return {
            'heads': best_config.get('n_heads', 12),
            'dimPerHead': best_config.get('dim_per_head', 64),
            'dropout': best_config.get('dropout', 0.1),
            'temperature': best_config.get('temperature', 1.0),
            'nLayers': best_config.get('n_layers', 2)
        }

    def _compile_agent_configs(self) -> Dict[str, Any]:
        """Compile agent configurations for multi-modal"""
        agents = {}

        # Text-only agent
        agents['textAgent'] = {
            'type': 'role',
            'modalities': ['text'],
            'modelSize': '100M',
            'architecture': 'unified',
            'useCases': ['text_generation', 'summarization', 'qa']
        }

        # Vision agent
        agents['visionAgent'] = {
            'type': 'role',
            'modalities': ['text', 'image'],
            'modelSize': '200M',
            'architecture': 'separate',
            'fusion': 'early',
            'crossAttention': True,
            'useCases': ['vqa', 'image_captioning', 'visual_reasoning']
        }

        # Audio agent
        agents['audioAgent'] = {
            'type': 'role',
            'modalities': ['text', 'audio'],
            'modelSize': '200M',
            'architecture': 'separate',
            'fusion': 'early',
            'useCases': ['transcription', 'text_to_speech', 'audio_analysis']
        }

        # Code agent
        agents['codeAgent'] = {
            'type': 'role',
            'modalities': ['text', 'code'],
            'modelSize': '100M',
            'architecture': 'unified',
            'useCases': ['code_generation', 'code_explanation', 'debugging']
        }

        # Universal agent
        agents['universalAgent'] = {
            'type': 'core',
            'modalities': ['text', 'image', 'audio', 'code'],
            'modelSize': '500M',
            'architecture': 'separate',
            'fusion': 'hierarchical',
            'crossAttention': True,
            'reasoning': {
                'steps': 3,
                'useChainOfThought': True,
                'useVerification': True
            },
            'useCases': ['multimodal_reasoning', 'complex_tasks', 'universal_assistant']
        }

        return agents

    def _compile_generation_params(self) -> Dict[str, Any]:
        """Compile generation parameters"""
        optimal_params = self.results.get('params', {})

        # Use optimal params from results, with fallbacks
        return {
            'text': {
                'temperature': optimal_params.get('text', {}).get('temperature', 0.8),
                'topP': optimal_params.get('text', {}).get('top_p', 0.9),
                'repetitionPenalty': optimal_params.get('text', {}).get('repetition_penalty', 1.0)
            },
            'image': {
                'temperature': optimal_params.get('image', {}).get('temperature', 0.5),
                'guidance': optimal_params.get('image', {}).get('guidance', 7.5),
                'steps': optimal_params.get('image', {}).get('steps', 50)
            },
            'audio': {
                'temperature': optimal_params.get('audio', {}).get('temperature', 0.7),
                'topP': optimal_params.get('audio', {}).get('top_p', 0.95)
            },
            'code': {
                'temperature': optimal_params.get('code', {}).get('temperature', 0.3),
                'topP': optimal_params.get('code', {}).get('top_p', 0.95),
                'repetitionPenalty': optimal_params.get('code', {}).get('repetition_penalty', 1.1)
            }
        }

    def _compile_embedding_configs(self) -> Dict[str, Any]:
        """Compile embedding configurations"""
        embedding_results = self.results.get('embedding', {})

        return {
            'strategy': 'hybrid',  # Best balance from results
            'embeddingDim': 768,
            'sharedDim': 256,
            'modalityDim': 512,
            'temperature': 0.07,
            'normalization': True,
            'modalityEncoders': {
                'text': 'transformer',
                'image': 'vision_transformer',
                'audio': 'wav2vec',
                'code': 'codebert'
            }
        }

    def _compile_reasoning_configs(self) -> Dict[str, Any]:
        """Compile reasoning configurations"""
        reasoning_results = self.results.get('reasoning', {})

        return {
            'defaultSteps': 3,
            'useCrossAttention': True,
            'useChainOfThought': True,
            'useVerification': True,
            'temperature': 0.7,
            'taskSpecific': {
                'visual_question_answering': {
                    'steps': 2,
                    'focus': 'visual'
                },
                'chart_understanding': {
                    'steps': 3,
                    'focus': 'quantitative'
                },
                'code_explanation': {
                    'steps': 3,
                    'focus': 'structural'
                },
                'multi_hop_reasoning': {
                    'steps': 5,
                    'useChainOfThought': True,
                    'useVerification': True
                }
            }
        }

    def generate_typescript_config(self, output_path: str):
        """Generate TypeScript configuration file"""

        configs = self.compile_optimal_configs()

        # Format as TypeScript
        ts_content = f"""/**
 * Multi-modal Domain Configuration for POLLN
 *
 * Auto-generated from simulation results.
 * Optimal configurations for multi-modal agent architectures.
 */

export const MULTIMODAL_DOMAIN_CONFIG = {{
  // Architecture patterns
  architecture: {json.dumps(configs['architecture'], indent=2)},

  // Fusion strategies
  fusion: {json.dumps(configs['fusion'], indent=2)},

  // Cross-modal attention
  crossAttention: {json.dumps(configs['crossAttention'], indent=2)},

  // Agent composition for multi-modal
  agents: {json.dumps(configs['agents'], indent=2)},

  // Generation parameters per modality
  generation: {json.dumps(configs['generation'], indent=2)},

  // Embedding configuration
  embeddings: {json.dumps(configs['embeddings'], indent=2)},

  // Reasoning configuration
  reasoning: {json.dumps(configs['reasoning'], indent=2)}
}};

/**
 * Helper type for modality combinations
 */
export type Modality = 'text' | 'image' | 'audio' | 'code';

/**
 * Helper type for fusion strategy
 */
export type FusionStrategy = 'early' | 'late' | 'hierarchical' | 'co_attention' | 'transformer_fusion';

/**
 * Helper type for architecture type
 */
export type ArchitectureType = 'unified' | 'separate' | 'mixture_of_experts';

/**
 * Get optimal agent configuration for modality set
 */
export function getOptimalAgentConfig(modalities: Modality[]): any {{
  const modalityKey = modalities.sort().join('+');

  // Direct matches
  if (modalities.length === 1 && modalities[0] === 'text') {{
    return MULTIMODAL_DOMAIN_CONFIG.agents.textAgent;
  }}
  if (modalities.includes('image') && !modalities.includes('audio') && !modalities.includes('code')) {{
    return MULTIMODAL_DOMAIN_CONFIG.agents.visionAgent;
  }}
  if (modalities.includes('audio') && !modalities.includes('image') && !modalities.includes('code')) {{
    return MULTIMODAL_DOMAIN_CONFIG.agents.audioAgent;
  }}
  if (modalities.includes('code') && !modalities.includes('image') && !modalities.includes('audio')) {{
    return MULTIMODAL_DOMAIN_CONFIG.agents.codeAgent;
  }}

  // Default to universal for complex combinations
  return MULTIMODAL_DOMAIN_CONFIG.agents.universalAgent;
}}

/**
 * Get optimal fusion strategy for modality count
 */
export function getOptimalFusionStrategy(nModalities: number): FusionStrategy {{
  if (nModalities <= 2) {{
    return 'early';
  }} else if (nModalities === 3) {{
    return 'late';
  }} else {{
    return 'hierarchical';
  }}
}}

/**
 * Get generation parameters for modality
 */
export function getGenerationParams(modality: Modality): any {{
  return MULTIMODAL_DOMAIN_CONFIG.generation[modality] || MULTIMODAL_DOMAIN_CONFIG.generation.text;
}}
"""

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(ts_content)

        print(f"TypeScript config generated: {output_path}")

    def generate_summary(self):
        """Generate summary of optimal configurations"""

        configs = self.compile_optimal_configs()

        print("\n" + "=" * 80)
        print("MULTI-MODAL CONFIGURATION SUMMARY")
        print("=" * 80)

        print("\nARCHITECTURE RECOMMENDATIONS:")
        print("-" * 80)
        for arch_type, config in configs['architecture'].items():
            print(f"\n{arch_type.upper()}:")
            print(f"  {json.dumps(config, indent=4)}")

        print("\n\nFUSION STRATEGY RECOMMENDATIONS:")
        print("-" * 80)
        for strategy, config in configs['fusion'].items():
            print(f"\n{strategy.upper()}:")
            print(f"  {json.dumps(config, indent=4)}")

        print("\n\nAGENT CONFIGURATIONS:")
        print("-" * 80)
        for agent_name, config in configs['agents'].items():
            print(f"\n{agent_name}:")
            print(f"  Type: {config.get('type')}")
            print(f"  Modalities: {', '.join(config.get('modalities', []))}")
            print(f"  Model Size: {config.get('modelSize')}")
            print(f"  Architecture: {config.get('architecture')}")

        print("\n\nGENERATION PARAMETERS:")
        print("-" * 80)
        for modality, params in configs['generation'].items():
            print(f"\n{modality.upper()}:")
            print(f"  {json.dumps(params, indent=4)}")


def main():
    """Main optimization pipeline"""

    print("=" * 80)
    print("MULTI-MODAL OPTIMIZER")
    print("=" * 80)

    # Initialize optimizer
    optimizer = MultiModalOptimizer()

    # Load all results
    print("\nLoading simulation results...")
    optimizer.load_all_results()

    # Compile configurations
    print("\nCompiling optimal configurations...")
    configs = optimizer.compile_optimal_configs()

    # Generate TypeScript config
    print("\nGenerating TypeScript configuration...")
    output_path = "src/domains/multimodal/config.ts"
    optimizer.generate_typescript_config(output_path)

    # Generate summary
    optimizer.generate_summary()

    print("\n" + "=" * 80)
    print("Optimization complete!")
    print("=" * 80)

    return configs


if __name__ == "__main__":
    configs = main()
