# Mathematical Framework

## 2.1 Formal Definitions

### Definition D1 (Rate Function)

The **instantaneous rate function** $r(t)$ is defined as:

$$r(t) = \lim_{\Delta t \to 0} \frac{x(t + \Delta t) - x(t)}{\Delta t} = \frac{dx}{dt}$$

**Discrete Approximation**: For sampled systems:

$$r[n] = \frac{x[n] - x[n-1]}{\Delta t}$$

**Property**: Rate captures velocity of change, not magnitude of state.

### Definition D2 (Rate Deadband)

A **rate deadband** $\mathcal{D}$ is a triple-threshold system:

$$\mathcal{D} = (\epsilon_1, \epsilon_2, \epsilon_3)$$

Where:
- $\epsilon_1$: Stable zone threshold (green)
- $\epsilon_2$: Monitored zone threshold (yellow)
- $\epsilon_3$: Critical zone threshold (red)

**Zone Classification**:

$$Z(r) = \begin{cases}
\text{STABLE} & |r| < \epsilon_1 \\
\text{MONITORED} & \epsilon_1 \leq |r| < \epsilon_2 \\
\text{CRITICAL} & |r| \geq \epsilon_2
\end{cases}$$

### Definition D3 (Integrated Rate)

The **integrated rate** $I(t)$ predicts future state:

$$I(t) = x_0 + \int_{t_0}^t r(\tau) d\tau$$

**Discrete Form**:

$$I[n] = x[0] + \sum_{k=1}^{n} r[k] \cdot \Delta t$$

**Property**: Integration smooths noise through averaging.

### Definition D4 (Rate Anomaly Score)

The **anomaly score** $A(t)$ combines rate magnitude and persistence:

$$A(t) = \int_{t-\tau}^{t} |r(\tau)| \cdot w(\tau) d\tau$$

Where $w(\tau)$ is a decay weight function, typically $w(\tau) = e^{-\lambda(t-\tau)}$.

---

## 2.2 Theorems and Proofs

### Theorem T1 (Early Detection)

**Statement**: Rate-based monitoring detects anomalies in $O(1/\epsilon)$ time, compared to $O(1/\delta)$ for state-based monitoring, where $\epsilon$ is rate threshold and $\delta$ is state deviation threshold.

**Proof**:

*Lemma L1.1*: Rate changes before state accumulates.

*Proof of L1.1*: Consider state evolution $x(t) = x_0 + \int r(\tau) d\tau$. For state to change by $\delta$, rate must first be non-zero. If $r(t) \geq \epsilon$, then after time $\tau = \delta/\epsilon$, state changes by $\delta$. Rate is detected at $t$, state at $t + \tau$. $\square$

*Lemma L1.2*: Rate detection time is independent of state magnitude.

*Proof of L1.2*: By Definition D1, $r(t)$ depends only on local derivative. Large states can have zero rate; small states can have large rate. Detection depends on $\epsilon$, not $\delta$. $\square$

*Main Proof*: By L1.1, rate is detected $\tau = \delta/\epsilon$ before state deviation. By L1.2, this advantage is independent of state magnitude. Therefore, rate-based detection is $O(\delta/\epsilon)$ faster than state-based. $\square$

### Theorem T2 (False Positive Reduction)

**Statement**: Rate integration reduces false positives by factor of $\sqrt{n}$ where $n$ is noise samples.

**Proof**:

*Lemma L2.1*: Integration is a low-pass filter.

*Proof of L2.1*: The integral $I = \int r dt$ has transfer function $H(s) = 1/s$. For high-frequency noise $s \to \infty$, $|H(s)| \to 0$. Integration attenuates high-frequency noise. $\square$

*Lemma L2.2*: Noise variance reduces by factor $n$ after integration.

*Proof of L2.2*: For independent noise samples $\{\epsilon_1, ..., \epsilon_n\}$ with variance $\sigma^2$, the integral variance is:
$$\text{Var}\left(\sum \epsilon_i\right) = n \cdot \sigma^2 / n^2 = \sigma^2/n$$
$\square$

*Main Proof*: By L2.1, integration filters high-frequency noise. By L2.2, variance reduces by $n$. False positives, which are noise-induced, reduce by $\sqrt{n}$. $\square$

### Theorem T3 (Computational Efficiency)

**Statement**: Rate-based monitoring requires O(1) storage per metric, compared to O(n) for time-series state monitoring.

**Proof**:

*Lemma L3.1*: Rate computation requires only current and previous sample.

*Proof of L3.1*: By Definition D1 (discrete), $r[n] = (x[n] - x[n-1])/\Delta t$. Only $x[n]$ and $x[n-1]$ needed. $\square$

*Lemma L3.2*: Integration requires O(1) accumulator.

*Proof of L3.2*: By Definition D3 (discrete), $I[n] = I[n-1] + r[n] \cdot \Delta t$. Single accumulator suffices. $\square$

*Main Proof*: By L3.1, rate needs 2 samples. By L3.2, integration needs 1 accumulator. Total storage: O(1). State monitoring needs full history: O(n). $\square$

---

## 2.3 Mathematical Properties

### Property P1: Causality

Rate at time $t$ predicts state at time $t + \tau$:

$$r(t) > \epsilon \Rightarrow x(t + \tau) > x(t) + \epsilon \cdot \tau$$

This is the foundation of predictive monitoring.

### Property P2: Composition

Rates compose through summation:

$$r_{combined} = \sum_i w_i \cdot r_i$$

Where $w_i$ are weights. This enables multi-metric rate tracking.

### Property P3: Stability

Bounded rates guarantee bounded states:

$$|r(t)| \leq M \forall t \Rightarrow |x(t) - x(0)| \leq M \cdot t$$

This enables stability analysis from rate information alone.

---

## 2.4 Complexity Analysis

| Operation | State-Based | Rate-Based | Improvement |
|-----------|-------------|------------|-------------|
| Anomaly Detection | O(n) history | O(1) current | O(n) |
| False Positive Filter | O(n log n) | O(1) integration | O(n log n) |
| Storage | O(n) samples | O(1) accumulator | O(n) |
| Prediction | O(n) model | O(1) extrapolation | O(n) |
| Alert Latency | O(1/δ) | O(1/ε) | O(δ/ε) |

Where $n$ = sample history size, $\delta$ = state threshold, $\epsilon$ = rate threshold.

---

## 2.5 Summary

The mathematical framework establishes that:

1. **Early Detection** is achievable through rate-first thinking (T1)
2. **Noise Reduction** comes naturally from integration (T2)
3. **Computational Efficiency** is guaranteed by O(1) storage (T3)

These properties form the theoretical foundation for building rate-based monitoring systems that outperform traditional state-based approaches.

---

*Part of the SuperInstance Mathematical Framework*
