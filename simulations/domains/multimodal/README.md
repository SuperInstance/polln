# Multi-Modal Simulation Suite

Comprehensive Python simulations for optimizing POLLN agents for multi-modal tasks (text, image, audio, code).

## Overview

This simulation suite tests and optimizes multi-modal architectures for POLLN agents, covering:

- **Architecture Design**: Unified encoders, separate encoders + fusion, mixture-of-experts
- **Cross-Modal Attention**: Early fusion, late fusion, hierarchical fusion, co-attention
- **Modality Embeddings**: Unified vs separate embedding spaces
- **Multi-Modal Reasoning**: VQA, chart understanding, code explanation, audio-visual reasoning
- **Generation Quality**: Image captioning, text-to-image, transcription, code generation

## Directory Structure

```
simulations/domains/multimodal/
├── README.md                          # This file
├── MULTIMODAL_GUIDE.md                # Detailed usage guide
├── ARCHITECTURE.md                    # Architecture patterns documentation
├── multimodal_architecture.py         # Architecture simulation
├── cross_modal_attention.py           # Attention optimization
├── modality_embedding.py              # Embedding optimization
├── multimodal_reasoning.py            # Reasoning simulation
├── generation_quality.py              # Generation quality simulation
├── multimodal_optimizer.py            # Configuration compiler
├── run_all.py                         # Master orchestrator
├── test_multimodal.py                 # Test suite
└── results/                           # Simulation results (generated)
    ├── architecture_results.json
    ├── attention_results.json
    ├── embedding_results.json
    ├── reasoning_results.json
    ├── generation_results.json
    └── optimal_params.json
```

## Quick Start

### 1. Run All Simulations

```bash
cd simulations/domains/multimodal
python run_all.py
```

This will:
1. Run all 5 simulations sequentially
2. Generate result JSON files in `results/`
3. Compile optimal configurations
4. Generate `src/domains/multimodal/config.ts`

### 2. Run Individual Simulations

```bash
# Architecture simulation
python multimodal_architecture.py

# Cross-modal attention optimization
python cross_modal_attention.py

# Modality embedding optimization
python modality_embedding.py

# Multi-modal reasoning simulation
python multimodal_reasoning.py

# Generation quality simulation
python generation_quality.py
```

### 3. Generate Configuration Only

If results already exist, just generate the config:

```bash
python multimodal_optimizer.py
```

### 4. Run Tests

```bash
python test_multimodal.py
```

## Simulation Components

### 1. Architecture Simulation (`multimodal_architecture.py`)

Tests different multi-modal architecture patterns:

**Architectures:**
- Unified Encoder: Single transformer for all modalities
- Separate Encoders: Modality-specific encoders with fusion
- Mixture-of-Experts: Dynamic expert routing

**Metrics:**
- Cross-modal alignment
- Generation quality
- Inference latency
- Memory usage
- Throughput

**Output:** `results/architecture_results.json`

### 2. Cross-Modal Attention (`cross_modal_attention.py`)

Optimizes fusion strategies:

**Strategies:**
- Early Fusion: Combine at input layer
- Late Fusion: Process separately, combine at output
- Hierarchical Fusion: Progressive multi-level fusion
- Co-Attention: Bidirectional attention between modalities
- Transformer Fusion: Multi-head cross-attention

**Metrics:**
- Fusion quality improvement
- Alignment score
- Attention entropy
- Computational cost (FLOPs)
- Memory usage
- Latency

**Output:** `results/attention_results.json`

### 3. Modality Embedding (`modality_embedding.py`)

Tests embedding space designs:

**Strategies:**
- Unified: All modalities in same space
- Separate: Modality-specific spaces
- Hybrid: Shared + modality-specific components
- Adversarial: Modality-invariant representations
- Contrastive: Align positive pairs

**Metrics:**
- Cross-modal retrieval accuracy
- Alignment between modalities
- Embedding quality (coherence, coverage)
- Transfer learning performance
- Downstream task performance

**Output:** `results/embedding_results.json`

### 4. Multi-Modal Reasoning (`multimodal_reasoning.py`)

Tests reasoning across modalities:

**Tasks:**
- Visual Question Answering (VQA)
- Chart Understanding
- Code Explanation
- Audio-Visual Reasoning
- Multi-Hop Reasoning

**Metrics:**
- Reasoning accuracy
- Cross-modal consistency
- Modality utilization
- Reasoning efficiency
- Confidence score

**Output:** `results/reasoning_results.json`

### 5. Generation Quality (`generation_quality.py`)

Tests generation across modalities:

**Tasks:**
- Image Captioning (image → text)
- Text-to-Image (text → image)
- Audio Transcription (audio → text)
- Text-to-Audio (text → audio)
- Code Generation (text → code)
- Code Explanation (code → text)

**Metrics:**
- Quality score
- Accuracy
- Fluency
- Alignment (input-output correspondence)
- Diversity
- Faithfulness

**Output:** `results/generation_results.json`

### 6. Configuration Optimizer (`multimodal_optimizer.py`)

Compiles all simulation results into optimal configurations:

**Features:**
- Loads all simulation results
- Compiles optimal configurations per modality set
- Generates TypeScript config file
- Provides helper functions for querying configs

**Output:** `src/domains/multimodal/config.ts`

## Generated Configuration

The optimizer generates a TypeScript configuration file with:

```typescript
export const MULTIMODAL_DOMAIN_CONFIG = {
  architecture: {
    unified: {...},
    separate: {...},
    mixtureOfExperts: {...}
  },
  fusion: {
    early: {...},
    late: {...},
    hierarchical: {...}
  },
  crossAttention: {
    heads: 12,
    dimPerHead: 64,
    ...
  },
  agents: {
    textAgent: {...},
    visionAgent: {...},
    audioAgent: {...},
    codeAgent: {...},
    universalAgent: {...}
  },
  generation: {
    text: {...},
    image: {...},
    audio: {...},
    code: {...}
  },
  ...
};
```

## Helper Functions

The generated config includes utility functions:

```typescript
// Get optimal agent for modality set
const agentConfig = getOptimalAgentConfig(['text', 'image']);

// Get optimal fusion strategy
const strategy = getOptimalFusionStrategy(3); // 3 modalities

// Get generation parameters
const params = getGenerationParams('image');
```

## Requirements

```bash
pip install numpy matplotlib scikit-learn
```

## Usage in POLLN

Once simulations are run and config is generated:

```typescript
import {
  MULTIMODAL_DOMAIN_CONFIG,
  getOptimalAgentConfig,
  getOptimalFusionStrategy,
  getGenerationParams
} from '@polln/multimodal';

// Get optimal agent for your modalities
const modalities: Modality[] = ['text', 'image'];
const agentConfig = getOptimalAgentConfig(modalities);

// Create agent with optimal config
const agent = new MultiModalAgent(agentConfig);
```

## Results Interpretation

### Architecture Selection

- **Unified Encoder**: Best for 2-3 modalities, low latency
- **Separate Encoders**: Best for 3+ modalities, higher accuracy
- **Mixture-of-Experts**: Best for complex modality combinations

### Fusion Strategy

- **Early Fusion**: Fastest, good for simple tasks
- **Late Fusion**: Better accuracy, good for complex tasks
- **Hierarchical Fusion**: Best for 3+ modalities

### Generation Parameters

- **Text**: Higher temperature (0.8) for creativity
- **Image**: Lower temperature (0.5), higher guidance (7.5)
- **Audio**: Medium temperature (0.7)
- **Code**: Low temperature (0.3) for precision

## Troubleshooting

### Simulations Fail to Run

1. Check Python version (3.8+ required)
2. Install dependencies: `pip install -r requirements.txt`
3. Check directory structure

### Config Not Generated

1. Ensure all simulations completed successfully
2. Check `results/` directory for JSON files
3. Run optimizer manually: `python multimodal_optimizer.py`

### Import Errors

```bash
# Make sure you're in the right directory
cd simulations/domains/multimodal

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Contributing

To add new simulations:

1. Create simulation file following existing patterns
2. Generate results JSON with consistent structure
3. Update `multimodal_optimizer.py` to load new results
4. Add tests to `test_multimodal.py`

## License

MIT License - See LICENSE file for details
