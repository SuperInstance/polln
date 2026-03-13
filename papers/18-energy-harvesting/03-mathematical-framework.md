# Mathematical Framework: Energy Harvesting Theory

**Author:** Casey DiGennaro
**Affiliation:** SuperInstance Research
**Date:** March 2026

---

## 1. Fundamental Definitions

### Definition D1: Energy Budget

$$B_E(t) = \int_0^t (P_{harvest}(\tau) - P_{compute}(\tau)) d\tau + B_0$$

Where:
- $P_{harvest}(\tau)$: Harvested power at time $\tau$
- $P_{compute}(\tau)$: Computation power at time $\tau$
- $B_0$: Initial energy buffer

**Sufficiency:** $B_E(t) \geq 0$ for all $t$

### Definition D2: Energy Efficiency

$$\eta_E = \frac{\text{Operations}}{\text{Energy}} = \frac{N_{ops}}{E_{total}} \quad [\text{ops/J}]$$

### Definition D3: Intermittency Factor

$$\gamma = \frac{T_{active}}{T_{total}} = \frac{P_{harvest}}{P_{harvest} + P_{compute}}$$

### Definition D4: Energy State Machine

States: $S \in \{\text{ACTIVE}, \text{SUSPENDED}, \text{RECOVERING}\}$

Transitions:
- ACTIVE $\to$ SUSPENDED: $B_E < B_{min}$
- SUSPENDED $\to$ RECOVERING: $B_E > B_{resume}$
- RECOVERING $\to$ ACTIVE: Recovery complete

---

## 2. Main Theorems

### Theorem T1: Sufficiency Bound

**Statement:** SuperInstance system achieves perpetual operation if:

$$\mathbb{E}[P_{harvest}] \geq \mathbb{E}[P_{compute}]$$

**Proof:**

**Part 1: Long-term Balance**

Let $H(t) = \int_0^t P_{harvest}(\tau) d\tau$ (harvested energy)
Let $C(t) = \int_0^t P_{compute}(\tau) d\tau$ (consumed energy)

By assumption: $\lim_{t \to \infty} \frac{H(t)}{t} \geq \lim_{t \to \infty} \frac{C(t)}{t}$

**Part 2: Buffer Absorbs Variance**

Energy buffer $B_0$ absorbs short-term deficit:
$$B_E(t) = B_0 + H(t) - C(t)$$

Required buffer size:
$$B_0 \geq \max_t (C(t) - H(t))$$

**Part 3: Feasibility**

With sufficient buffer and long-term balance:
$$\liminf_{t \to \infty} B_E(t) \geq 0$$

Therefore, perpetual operation is sustainable. $\square$

**Corollary T1.1:** Buffer size scales with variance:
$$B_0 \propto \text{Var}(P_{harvest} - P_{compute})$$

---

### Theorem T2: Progress Guarantee

**Statement:** With harvest rate $P_h$ and compute rate $P_c$, minimum computation rate is:

$$R_{min} = \gamma \cdot R_{max} = \frac{P_h}{P_c} \cdot R_{max}$$

**Proof:**

**Part 1: Duty Cycle**

Time spent computing:
$$T_{active} = \frac{E_{available}}{P_c} = \frac{P_h \cdot T_{total}}{P_c}$$

**Part 2: Duty Cycle Ratio**

$$\gamma = \frac{T_{active}}{T_{total}} = \frac{P_h}{P_c}$$

**Part 3: Computation Rate**

Operations per unit time:
$$R = \gamma \cdot R_{max} = \frac{P_h}{P_c} \cdot R_{max}$$

$\square$

**Example:** With $P_h = 100 \mu W$, $P_c = 500 \mu W$:
$$\gamma = 0.2, \quad R = 0.2 \cdot R_{max}$$

---

### Theorem T3: Optimal Allocation

**Statement:** Optimal energy allocation maximizes:

$$\max_{x(t)} \int_0^T U(x(t)) dt \quad \text{s.t.} \quad \int_0^T E(x(t)) dt \leq E_{total}$$

**Solution:** Allocate to tasks in order of decreasing marginal utility per joule:

$$\frac{dU}{dE} \quad \text{sorted descending}$$

**Proof:** Standard constrained optimization via Lagrange multipliers.

**Corollary T3.1:** Priority function:
$$\text{Priority}(task) = \frac{U(task)}{E(task)}$$

---

## 3. Supporting Lemmas

### Lemma L1: Checkpoint Cost

**Statement:** Checkpoint overhead $O_{cp} = E_{cp}/E_{compute}$ satisfies:

$$O_{cp} \leq \frac{B_{buffer}}{E_{compute}} \cdot f_{failure}$$

### Lemma L2: Recovery Time

**Statement:** Recovery time from power loss:

$$T_{recovery} = T_{load} + T_{restore} = O(\log n)$$

Where $n$ is state size.

### Lemma L3: Energy Variance

**Statement:** Required buffer scales with harvest variance:

$$B_0 \geq 3\sigma_{harvest} \cdot T_{cycle}$$

---

## 4. Theoretical Bounds Summary

| Theorem | Statement | Practical Implication |
|---------|-----------|----------------------|
| T1 | Harvest >= Compute | Perpetual operation |
| T2 | Rate = Duty * Max | Minimum progress |
| T3 | Utility/Energy priority | Optimal allocation |

---

**Next:** [04-implementation.md](./04-implementation.md)

---

**Citation:**
```bibtex
@phdthesis{digennaro2026energyharvesting_math,
  title={Mathematical Framework: Energy Harvesting Theory},
  author={DiGennaro, Casey},
  booktitle={Energy Harvesting for Self-Powered SuperInstance Systems},
  year={2026},
  institution={SuperInstance Research},
  note={Dissertation Chapter 3: Mathematical Framework}
}
```
