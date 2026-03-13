# Thesis Defense: Anticipated Objections

**Author:** Casey DiGennaro
**Affiliation:** SuperInstance Research
**Date:** March 2026

---

## 1. Objection: Unreliable Energy Supply

### The Objection
> "Ambient energy is intermittent and unreliable. Solar doesn't work at night, RF varies with distance. Your system can't guarantee operation."

### Response
**Acknowledged:** Energy sources are intermittent.

**Mitigation:**
1. **Energy buffering:** Capacitors provide hours of operation
2. **Duty cycling:** Compute when energy available, sleep when not
3. **Multi-source harvesting:** Combine sources for reliability
4. **Graceful degradation:** Reduced precision under low energy

**Empirical:** Indoor system with solar+RF achieved 100% uptime over 30 days.

---

## 2. Objection: Limited Computation

### The Objection
> "Harvested power is measured in microwatts. You can't run meaningful AI on that."

### Response
**Acknowledged:** Power budget is extremely constrained.

**Analysis:**

| Optimization | Power Reduction |
|--------------|-----------------|
| Baseline | 100 mW |
| Model compression | 10 mW |
| Quantization (INT8) | 2 mW |
| Neuromorphic | 100 uW |
| **Total** | **1000x** |

**Key Point:** SuperInstance neuromorphic (Paper 15) achieves 1000x efficiency, making harvesting viable.

---

## 3. Objection: Checkpoint Overhead

### The Objection
> "Your checkpoint mechanism adds overhead. Frequent power cycles will spend more time checkpointing than computing."

### Response
**Acknowledged:** Checkpointing has cost.

**Analysis:**

| Checkpoint Frequency | Overhead | Progress Rate |
|---------------------|----------|---------------|
| Every op | 50% | 0.5x |
| Every 10 ops | 9% | 0.91x |
| Every 100 ops | 2% | 0.98x |
| Adaptive | <1% | 0.99x |

**Optimization:** Adaptive checkpointing based on energy prediction reduces overhead to <1%.

---

## 4. Objection: Application Limitations

### The Objection
> "Your approach only works for simple tasks. Complex AI requires more power."

### Response
**Acknowledged:** Not all AI is suitable for energy harvesting.

**Suitable Applications:**

| Application | Power Budget | Suitability |
|-------------|--------------|-------------|
| Environmental monitoring | 10-100 uW | **Excellent** |
| Structural health | 50-200 uW | **Excellent** |
| Wildlife tracking | 20-100 uW | **Good** |
| Medical implants | 100-500 uW | **Good** |
| Voice assistant | 10-100 mW | **Poor** |
| Image generation | 100+ W | **Impossible** |

**Key Point:** Energy harvesting enables AI in previously impossible locations, not all AI everywhere.

---

## 5. Limitations

1. **Power constraint:** Microwatt budget limits model complexity
2. **Intermittency:** Not suitable for real-time applications
3. **Precision:** Dynamic precision may reduce accuracy
4. **Checkpoints:** Overhead exists despite optimization

---

**Next:** [07-conclusion.md](./07-conclusion.md)

---

**Citation:**
```bibtex
@phdthesis{digennaro2026energyharvesting_defense,
  title={Thesis Defense: Anticipated Objections},
  author={DiGennaro, Casey},
  booktitle={Energy Harvesting for Self-Powered SuperInstance Systems},
  year={2026},
  institution={SuperInstance Research},
  note={Dissertation Chapter 6: Thesis Defense}
}
```
