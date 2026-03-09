/**
 * Multi-modal Domain Configuration for POLLN
 *
 * This is a placeholder configuration. Run the simulations to generate
 * optimal configurations based on empirical testing.
 *
 * To generate optimal configuration:
 * ```bash
 * cd simulations/domains/multimodal
 * python run_all.py
 * ```
 */

export const MULTIMODAL_DOMAIN_CONFIG = {
  // Architecture patterns
  architecture: {
    unified: {
      encoder: 'transformer',
      embeddingDim: 768,
      modalityTokens: ['text', 'image', 'audio', 'code'],
      parameters: {
        n_heads: 12,
        n_layers: 6,
        dropout: 0.1
      }
    },
    separate: {
      textEncoder: 'transformer',
      imageEncoder: 'vision_transformer',
      audioEncoder: 'wav2vec',
      codeEncoder: 'codebert',
      fusion: 'cross_attention',
      embeddingDim: 768
    },
    mixtureOfExperts: {
      experts: 8,
      gating: 'learned',
      topK: 2,
      loadBalancing: true
    }
  },

  // Fusion strategies
  fusion: {
    early: {
      concatEmbeddings: true,
      fusionLayer: 'input',
      useCase: ['text+image', 'text+audio']
    },
    late: {
      unimodalProcessing: true,
      fusionLayer: 'output',
      aggregation: 'attention',
      useCase: ['3+modalities', 'complex_reasoning']
    },
    hierarchical: {
      levels: 3,
      fusionPerLevel: true,
      progressiveIntegration: true,
      useCase: ['universal_agent', 'all_modalities']
    }
  },

  // Cross-modal attention
  crossAttention: {
    heads: 12,
    dimPerHead: 64,
    dropout: 0.1,
    temperature: 1.0,
    nLayers: 2
  },

  // Agent composition for multi-modal
  agents: {
    textAgent: {
      type: 'role',
      modalities: ['text'],
      modelSize: '100M',
      architecture: 'unified',
      useCases: ['text_generation', 'summarization', 'qa']
    },
    visionAgent: {
      type: 'role',
      modalities: ['text', 'image'],
      modelSize: '200M',
      architecture: 'separate',
      fusion: 'early',
      crossAttention: true,
      useCases: ['vqa', 'image_captioning', 'visual_reasoning']
    },
    audioAgent: {
      type: 'role',
      modalities: ['text', 'audio'],
      modelSize: '200M',
      architecture: 'separate',
      fusion: 'early',
      useCases: ['transcription', 'text_to_speech', 'audio_analysis']
    },
    codeAgent: {
      type: 'role',
      modalities: ['text', 'code'],
      modelSize: '100M',
      architecture: 'unified',
      useCases: ['code_generation', 'code_explanation', 'debugging']
    },
    universalAgent: {
      type: 'core',
      modalities: ['text', 'image', 'audio', 'code'],
      modelSize: '500M',
      architecture: 'separate',
      fusion: 'hierarchical',
      crossAttention: true,
      reasoning: {
        steps: 3,
        useChainOfThought: true,
        useVerification: true
      },
      useCases: ['multimodal_reasoning', 'complex_tasks', 'universal_assistant']
    }
  },

  // Generation parameters per modality
  generation: {
    text: {
      temperature: 0.8,
      topP: 0.9,
      repetitionPenalty: 1.0
    },
    image: {
      temperature: 0.5,
      guidance: 7.5,
      steps: 50
    },
    audio: {
      temperature: 0.7,
      topP: 0.95
    },
    code: {
      temperature: 0.3,
      topP: 0.95,
      repetitionPenalty: 1.1
    }
  },

  // Embedding configuration
  embeddings: {
    strategy: 'hybrid',
    embeddingDim: 768,
    sharedDim: 256,
    modalityDim: 512,
    temperature: 0.07,
    normalization: true,
    modalityEncoders: {
      text: 'transformer',
      image: 'vision_transformer',
      audio: 'wav2vec',
      code: 'codebert'
    }
  },

  // Reasoning configuration
  reasoning: {
    defaultSteps: 3,
    useCrossAttention: true,
    useChainOfThought: true,
    useVerification: true,
    temperature: 0.7,
    taskSpecific: {
      visual_question_answering: {
        steps: 2,
        focus: 'visual'
      },
      chart_understanding: {
        steps: 3,
        focus: 'quantitative'
      },
      code_explanation: {
        steps: 3,
        focus: 'structural'
      },
      multi_hop_reasoning: {
        steps: 5,
        useChainOfThought: true,
        useVerification: true
      }
    }
  }
};

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
export function getOptimalAgentConfig(modalities: Modality[]): any {
  const modalityKey = modalities.sort().join('+');

  // Direct matches
  if (modalities.length === 1 && modalities[0] === 'text') {
    return MULTIMODAL_DOMAIN_CONFIG.agents.textAgent;
  }
  if (modalities.includes('image') && !modalities.includes('audio') && !modalities.includes('code')) {
    return MULTIMODAL_DOMAIN_CONFIG.agents.visionAgent;
  }
  if (modalities.includes('audio') && !modalities.includes('image') && !modalities.includes('code')) {
    return MULTIMODAL_DOMAIN_CONFIG.agents.audioAgent;
  }
  if (modalities.includes('code') && !modalities.includes('image') && !modalities.includes('audio')) {
    return MULTIMODAL_DOMAIN_CONFIG.agents.codeAgent;
  }

  // Default to universal for complex combinations
  return MULTIMODAL_DOMAIN_CONFIG.agents.universalAgent;
}

/**
 * Get optimal fusion strategy for modality count
 */
export function getOptimalFusionStrategy(nModalities: number): FusionStrategy {
  if (nModalities <= 2) {
    return 'early';
  } else if (nModalities === 3) {
    return 'late';
  } else {
    return 'hierarchical';
  }
}

/**
 * Get generation parameters for modality
 */
export function getGenerationParams(modality: Modality): any {
  return MULTIMODAL_DOMAIN_CONFIG.generation[modality] || MULTIMODAL_DOMAIN_CONFIG.generation.text;
}
