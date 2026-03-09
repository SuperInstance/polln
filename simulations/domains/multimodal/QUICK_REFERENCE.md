# Multi-Modal Simulation Quick Reference

Quick reference for running and using multi-modal simulations.

## Command Summary

```bash
# Run all simulations
cd simulations/domains/multimodal
python run_all.py

# Run individual simulations
python multimodal_architecture.py      # Test architectures
python cross_modal_attention.py        # Optimize fusion
python modality_embedding.py           # Test embeddings
python multimodal_reasoning.py         # Test reasoning
python generation_quality.py           # Test generation

# Generate config from existing results
python multimodal_optimizer.py

# Run tests
python test_multimodal.py
```

## File Locations

```
polln/
├── simulations/domains/multimodal/     # Simulations
│   ├── *.py                            # Simulation scripts
│   ├── results/                        # Generated results
│   └── *.md                            # Documentation
└── src/domains/multimodal/             # Generated config
    ├── index.ts                        # Exports
    └── config.ts                       # Configuration (generated)
```

## Common Tasks

### Re-run Simulations After Code Changes

```bash
cd simulations/domains/multimodal
rm -rf results/*  # Clear old results
python run_all.py
```

### Update Configuration After Changes

```bash
cd simulations/domains/multimodal
python multimodal_optimizer.py
```

### Add New Modality

1. Update simulation files with new modality
2. Re-run simulations
3. Regenerate config

### Debug Simulation Issues

```bash
# Run single simulation with output
python multimodal_architecture.py 2>&1 | tee debug.log

# Check results
cat results/architecture_results.json | python -m json.tool
```

## Result Files

| File | Description |
|------|-------------|
| `architecture_results.json` | Architecture benchmark results |
| `attention_results.json` | Fusion strategy results |
| `embedding_results.json` | Embedding optimization results |
| `reasoning_results.json` | Reasoning task results |
| `generation_results.json` | Generation quality results |
| `optimal_params.json` | Optimal parameters per modality |

## Key Metrics

### Architecture Metrics

- `cross_modal_alignment`: Embedding alignment (0-1, higher is better)
- `generation_quality`: Output quality (0-1)
- `inference_latency_ms`: Processing time (ms)
- `memory_mb`: Memory usage (MB)

### Attention Metrics

- `fusion_quality`: Fusion improvement (0-1)
- `alignment_score`: Cross-modal alignment (0-1)
- `attention_entropy`: Attention diversity (0-3)
- `computation_flops`: Computational cost

### Embedding Metrics

- `retrieval_accuracy`: Cross-modal retrieval (0-1)
- `alignment_score`: Embedding alignment (0-1)
- `embedding_quality`: Coherence and coverage (0-1)
- `transfer_score`: Transfer learning (0-1)

### Reasoning Metrics

- `accuracy`: Answer correctness (0-1)
- `cross_modal_consistency`: Consistency (0-1)
- `modality_utilization`: Per-modality usage (0-1)
- `reasoning_efficiency`: Steps to solution (0-1)

### Generation Metrics

- `quality_score`: Overall quality (0-1)
- `accuracy`: Factual correctness (0-1)
- `fluency`: Naturalness (0-1)
- `alignment`: Input-output match (0-1)
- `diversity`: Output variety (0-1)

## Troubleshooting

### Simulation Fails

**Check**:
1. Python version (3.8+)
2. Dependencies installed
3. Working directory correct

**Fix**:
```bash
pip install numpy matplotlib scikit-learn
cd simulations/domains/multimodal
```

### No Results Generated

**Check**:
1. Simulation ran successfully
2. No errors in output
3. Results directory exists

**Fix**:
```bash
mkdir -p results
python run_all.py
```

### Config Not Updated

**Check**:
1. Results exist
2. Optimizer ran successfully
3. Write permissions on src/

**Fix**:
```bash
python multimodal_optimizer.py
```

## Performance Tips

### Faster Simulations

- Reduce `n_trials` in simulation files
- Run fewer architecture combinations
- Use smaller `embedding_dim`

### Better Results

- Increase `n_trials`
- Test more configurations
- Run multiple times and average

### Lower Memory

- Use unified encoder
- Reduce `embedding_dim`
- Use early fusion

## Integration

### Import in POLLN

```typescript
import {
  MULTIMODAL_DOMAIN_CONFIG,
  getOptimalAgentConfig
} from '@polln/multimodal';

// Use configuration
const config = getOptimalAgentConfig(['text', 'image']);
```

### Extend for Custom Tasks

1. Add new simulation file
2. Generate results JSON
3. Update optimizer to load results
4. Regenerate config

### Custom Modalities

1. Add modality to `Modality` enum
2. Update all simulation files
3. Re-run all simulations
4. Regenerate config

## Further Reading

- `README.md` - Full documentation
- `MULTIMODAL_GUIDE.md` - Detailed guide
- `ARCHITECTURE.md` - Architecture patterns
