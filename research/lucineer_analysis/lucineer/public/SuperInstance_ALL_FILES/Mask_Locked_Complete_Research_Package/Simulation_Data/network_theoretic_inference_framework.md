# Network-Theoretic Framework for Inference Data Flow

## Abstract

This document develops a rigorous network-theoretic framework for analyzing transformer inference, modeling the data flow through layers as a flow network. We apply max-flow min-cut theory, queueing theory, scheduling theory, and reliability analysis to derive fundamental bounds on throughput, latency, and fault tolerance in large-scale inference systems.

---

## 1. Inference as Flow Network

### 1.1 Graph Representation of Transformer Layers

A transformer with $L$ layers is modeled as a directed acyclic graph $G = (V, E)$ where:

**Vertices (Processing Nodes):**
$$V = \{s, v_0^{attn}, v_0^{ffn}, v_1^{attn}, v_1^{ffn}, \ldots, v_{L-1}^{attn}, v_{L-1}^{ffn}, t\}$$

Where:
- $s$ = source (input tokens)
- $v_\ell^{attn}$ = attention node at layer $\ell$
- $v_\ell^{ffn}$ = feed-forward network node at layer $\ell$
- $t$ = sink (output logits)

**Edges (Data Movement):**
$$E = E_{input} \cup E_{layer} \cup E_{output}$$

With:
- $E_{input} = \{(s, v_0^{attn})\}$ — input embedding edge
- $E_{layer} = \{(v_\ell^{attn}, v_\ell^{ffn})\}_{\ell=0}^{L-1} \cup \{(v_\ell^{ffn}, v_{\ell+1}^{attn})\}_{\ell=0}^{L-2}$
- $E_{output} = \{(v_{L-1}^{ffn}, t)\}$ — output projection edge

### 1.2 Edge Capacities (Bandwidth Model)

Each edge $e \in E$ has capacity $c(e)$ representing maximum token throughput:

$$c(e) = \begin{cases}
\frac{B_{mem}}{d_{model} \cdot \text{sizeof}(float)} & \text{memory bandwidth limited} \\
\frac{F_{compute}}{2d_{model}^2} & \text{compute limited (attention)} \\
\frac{F_{compute}}{2d_{model} \cdot d_{ffn}} & \text{compute limited (FFN)}
\end{cases}$$

Where:
- $B_{mem}$ = memory bandwidth (GB/s)
- $F_{compute}$ = compute throughput (FLOPS)
- $d_{model}$ = model dimension
- $d_{ffn}$ = FFN hidden dimension (typically $4d_{model}$)

### 1.3 Flow Definition

Let $f: E \rightarrow \mathbb{R}^+$ be a flow function satisfying:

**Capacity Constraint:**
$$\forall e \in E: 0 \leq f(e) \leq c(e)$$

**Flow Conservation:**
$$\forall v \in V \setminus \{s, t\}: \sum_{e \in \delta^-(v)} f(e) = \sum_{e \in \delta^+(v)} f(e)$$

Where $\delta^-(v)$ and $\delta^+(v)$ are incoming and outgoing edges of $v$.

**Throughput (Flow Value):**
$$|f| = \sum_{e \in \delta^+(s)} f(e) = \sum_{e \in \delta^-(t)} f(e)$$

### 1.4 Max-Flow for Transformer Inference

**Theorem 1.1 (Max-Flow Bound):** The maximum throughput of a transformer inference system equals the value of the maximum flow in the layer graph:

$$\text{Throughput}_{max} = \max_f |f|$$

**Computation via Ford-Fulkerson:**

```
Algorithm: Transformer Max-Flow
Input: Layer graph G = (V, E), capacities c
Output: Maximum throughput θ_max

1. Initialize f(e) ← 0 for all e ∈ E
2. while ∃ augmenting path P from s to t in residual graph G_f:
3.     c_P ← min{c_f(e) : e ∈ P}  // bottleneck capacity
4.     for e ∈ P:
5.         if e is forward: f(e) ← f(e) + c_P
6.         else: f(e) ← f(e) - c_P
7. return |f|
```

### 1.5 Min-Cut and Bottleneck Identification

**Definition (Cut):** A cut $(S, T)$ partitions $V$ with $s \in S$ and $t \in T$.

**Cut Capacity:**
$$c(S, T) = \sum_{e \in E: \text{tail}(e) \in S, \text{head}(e) \in T} c(e)$$

**Theorem 1.2 (Max-Flow Min-Cut):** 
$$\max_f |f| = \min_{(S,T)} c(S, T)$$

**Bottleneck Layer Identification:**

The bottleneck layer(s) are determined by the min-cut:

$$\ell^* = \arg\min_\ell \left( c(v_\ell^{attn}, v_\ell^{ffn}) \text{ or } c(v_\ell^{ffn}, v_{\ell+1}^{attn}) \right)$$

**Practical Implication:** To increase throughput, focus optimization on the min-cut edges.

---

## 2. Data Movement Equations

### 2.1 Flow Conservation at Each Layer

For each layer $\ell$, we have two conservation equations:

**Attention Node Conservation:**
$$f(s, v_0^{attn}) = f(v_0^{attn}, v_0^{ffn}) \quad \text{(first layer)}$$
$$f(v_{\ell-1}^{ffn}, v_\ell^{attn}) = f(v_\ell^{attn}, v_\ell^{ffn}) \quad \text{(intermediate layers)}$$

**FFN Node Conservation:**
$$f(v_\ell^{attn}, v_\ell^{ffn}) = f(v_\ell^{ffn}, v_{\ell+1}^{attn}) \quad \text{(intermediate layers)}$$
$$f(v_{L-1}^{attn}, v_{L-1}^{ffn}) = f(v_{L-1}^{ffn}, t) \quad \text{(last layer)}$$

### 2.2 Processing Rate Equations

**Attention Processing Rate:**
$$\mu_\ell^{attn} = \frac{F_\ell}{2n_{heads} \cdot d_{head} \cdot d_{model} \cdot (seq + cache)}$$

Where:
- $F_\ell$ = FLOPS allocated to layer $\ell$
- $n_{heads}$ = number of attention heads
- $d_{head}$ = dimension per head
- $seq$ = sequence length
- $cache$ = KV cache length

**FFN Processing Rate:**
$$\mu_\ell^{ffn} = \frac{F_\ell}{2 \cdot d_{model} \cdot d_{ffn}}$$

**Combined Layer Rate:**
$$\mu_\ell = \left( \frac{1}{\mu_\ell^{attn}} + \frac{1}{\mu_\ell^{ffn}} \right)^{-1} = \frac{\mu_\ell^{attn} \cdot \mu_\ell^{ffn}}{\mu_\ell^{attn} + \mu_\ell^{ffn}}$$

### 2.3 Edge Bandwidth Constraints

**Memory Bandwidth Constraint:**
$$f(e) \leq \min\left( \frac{B_{HBM}}{M_{layer}}, \frac{B_{PCIe}}{M_{param}} \right)$$

Where:
- $M_{layer}$ = memory transferred per layer per token
- $M_{param}$ = parameter size per layer
- $B_{HBM}$ = high-bandwidth memory rate
- $B_{PCIe}$ = inter-device bandwidth

**Compute-Bound vs Memory-Bound Regime:**

$$\text{Regime} = \begin{cases}
\text{Compute-bound} & \text{if } \frac{\text{FLOPs}}{\text{Bytes}} > \frac{F_{peak}}{B_{peak}} \\
\text{Memory-bound} & \text{otherwise}
\end{cases}$$

The arithmetic intensity threshold:
$$I^* = \frac{F_{peak}}{B_{peak}}$$

### 2.4 Queueing Delays at Each Stage

Each processing node is modeled as an M/M/1 queue:

**Arrival Rate:** $\lambda = |f|$ (tokens/second)

**Service Rate:** $\mu = \mu_\ell^{op}$ where $op \in \{attn, ffn\}$

**Utilization:** $\rho = \frac{\lambda}{\mu}$

**Queueing Delay:**
$$W_q = \frac{\rho}{\mu(1-\rho)} = \frac{\lambda}{\mu(\mu - \lambda)}$$

**System Time (Including Service):**
$$W = \frac{1}{\mu - \lambda}$$

**End-to-End Latency:**
$$L_{e2e} = \sum_{\ell=0}^{L-1} \left( W_\ell^{attn} + W_\ell^{ffn} \right) + W_{embed} + W_{output}$$

### 2.5 Multi-Server Queueing (Batch Processing)

For batch size $b$ processed in parallel, each node becomes an M/M/c queue:

**Erlang-C Formula:**
$$C(c, \rho) = \frac{\frac{(c\rho)^c}{c!} \cdot \frac{1}{1-\rho}}{\sum_{k=0}^{c-1} \frac{(c\rho)^k}{k!} + \frac{(c\rho)^c}{c!} \cdot \frac{1}{1-\rho}}$$

**Average Queueing Time:**
$$W_q^{batch} = \frac{C(c, \rho)}{c\mu - \lambda}$$

---

## 3. KV Cache as Flow Storage

### 3.1 Cache as Reservoir in Flow Network

The KV cache is modeled as a storage reservoir between generation steps:

$$S_{KV}(t) = S_{KV}(0) + \int_0^t \left( f_{in}(\tau) - f_{out}(\tau) \right) d\tau$$

Where:
- $S_{KV}(t)$ = cache size at time $t$
- $f_{in}$ = tokens being added to cache
- $f_{out}$ = tokens evicted (usually 0 for autoregressive)

### 3.2 Cache Hit/Miss Probabilities

For a cache with capacity $C$ and working set $W$:

**Cache Hit Probability (LRU Model):**
$$P_{hit} = 1 - \left(\frac{W}{C}\right)^\alpha$$

Where $\alpha$ is the locality parameter.

**Working Set Size:**
$$W(t) = |\{tokens \ referenced \ in \ [t-\tau, t]\}|$$

**Stack Distance Distribution:**
$$P(\text{stack distance} = d) = \frac{1}{Z} \cdot d^{-\beta}$$

For $\beta \approx 1$ (Zipf-like access pattern typical in language).

### 3.3 Flow-Based Cache Analysis

**Effective Throughput with Cache:**
$$\lambda_{eff} = \lambda \cdot P_{hit} + \lambda \cdot (1-P_{hit}) \cdot r_{miss}$$

Where $r_{miss} < 1$ is the slowdown factor on cache miss.

**Cache-Adjusted Processing Rate:**
$$\mu_\ell^{attn, cached} = \mu_\ell^{attn} \cdot \left( P_{hit} + (1-P_{hit}) \cdot \frac{1}{\gamma} \right)^{-1}$$

Where $\gamma$ is the compute amplification on miss.

### 3.4 Working Set Modeling

**Temporal Locality Model:**
$$P(\text{reuse at time } t) = \frac{1}{t^\beta} \cdot e^{-\lambda t}$$

**Working Set Growth (Autoregressive):**
$$W(n) = \sum_{i=0}^{n} P(\text{token}_i \text{ referenced}) \cdot \mathbf{1}_{cache}$$

**Critical Working Set Size (Thrashing Threshold):**
$$W^* = C \cdot (1 - \rho_{threshold})$$

Where $\rho_{threshold}$ is the maximum acceptable cache miss rate.

### 3.5 Streaming Cache Equations

For streaming inference with cache eviction policy:

**Optimal Eviction Age:**
$$\tau_{evict}^* = \arg\max_\tau \int_0^\tau P(\text{reuse}|age=t) dt - \frac{C_{evict}}{C_{store}}$$

**Cache Pressure:**
$$P_{cache} = \frac{\sum_{\ell} S_{KV}^\ell(t)}{C_{total}}$$

**Flow Equilibrium Condition:**
$$\frac{dS_{KV}}{dt} = \lambda_{generate} - \lambda_{evict} = 0$$

At equilibrium, cache size is stable.

---

## 4. Parallelism Analysis

### 4.1 Pipeline Parallelism as Flow

Pipeline parallelism divides layers across $P$ devices:

$$G_{pipeline} = (V_P, E_P)$$

Where:
$$V_P = \{s\} \cup \{D_0, D_1, \ldots, D_{P-1}\} \cup \{t\}$$

And each device $D_p$ contains layers in range $[\ell_p^{start}, \ell_p^{end}]$.

**Pipeline Flow Constraints:**

$$f(D_p, D_{p+1}) = \min\left( \mu_{D_p}, \mu_{D_{p+1}}, B_{inter} \right)$$

**Pipeline Bubble:**
$$B_{bubble} = \frac{P - 1}{P + m - 1}$$

Where $m$ is the number of micro-batches.

**Effective Throughput:**
$$\lambda_{pipeline} = \lambda_{ideal} \cdot (1 - B_{bubble}) = \frac{\lambda_{max}}{P} \cdot \frac{m}{P + m - 1}$$

### 4.2 Data Parallelism Graph

Data parallelism replicates the model across $D$ devices:

$$G_{dataparallel} = \{G_0, G_1, \ldots, G_{D-1}\}$$

With synchronization edges forming an all-reduce:

$$E_{sync} = \{(G_d, G_{d'}) : d \neq d'\}$$

**Synchronization Overhead:**
$$T_{sync} = \frac{M_{model}}{B_{allreduce}} \cdot \log_2 D$$

For ring all-reduce.

**Speedup with Synchronization:**
$$S(D) = \frac{T_1}{\frac{T_1}{D} + T_{sync}} = \frac{D}{1 + D \cdot \frac{T_{sync}}{T_1}}$$

### 4.3 Synchronization Points

Critical synchronization occurs at:

1. **Pipeline stage boundaries:** After each device
2. **Gradient accumulation steps:** Every $k$ micro-batches
3. **All-reduce operations:** After each layer batch

**Synchronization Flow Chart:**

```
Input → [Stage 0] → sync → [Stage 1] → sync → ... → [Stage P-1] → Output
           ↓                      ↓                           ↓
        AllReduce            AllReduce                   AllReduce
           ↓                      ↓                           ↓
        Barrier               Barrier                     Barrier
```

### 4.4 Extended Amdahl's Law

**Classical Amdahl:**
$$S(p) = \frac{1}{(1-f) + \frac{f}{p}}$$

**Extended for Communication Overhead:**
$$S_{extended}(p) = \frac{1}{(1-f) + \frac{f}{p} + \alpha \cdot p^\beta}$$

Where:
- $f$ = parallelizable fraction
- $\alpha$ = communication coefficient
- $\beta$ = communication scaling exponent ($\approx 0.5$ for log-scaling)

**Extended for Memory Constraints:**
$$S_{memory}(p) = \min\left( S_{extended}(p), \frac{M_{total}}{M_{model} + M_{activation}} \right)$$

**Optimal Parallelism Degree:**
$$p^* = \arg\max_p S_{extended}(p)$$

Found by solving:
$$\frac{dS}{dp} = 0 \implies p^* = \sqrt{\frac{f}{\alpha \beta}}$$

---

## 5. Reliability Analysis

### 5.1 Network Reliability with Defective Components

**Reliability Block Diagram:**

The inference system is a series-parallel system:

$$R_{system} = R_{input} \cdot \prod_{\ell=0}^{L-1} R_\ell^{attn} \cdot R_\ell^{ffn} \cdot R_{output}$$

**Component Reliability (Exponential Model):**
$$R_\ell(t) = e^{-\lambda_\ell t}$$

Where $\lambda_\ell$ is the failure rate of layer $\ell$.

**Mean Time Between Failures (MTBF):**
$$MTBF = \frac{1}{\sum_{\ell} \lambda_\ell} = \frac{1}{\Lambda_{total}}$$

### 5.2 Graceful Degradation

**Degraded Mode Flow:**

When component $v$ fails, flow reroutes through backup:

$$f'(e) = \begin{cases}
f(e) + f(v_{failed}) & \text{if } e \in \text{backup path} \\
0 & \text{if } e \in \text{failed path}
\end{cases}$$

**Capacity Reduction Factor:**
$$\gamma_{degraded} = \frac{c(G')}{c(G)} = 1 - \frac{c(v_{failed})}{c(G)}$$

**Quality-Adjusted Throughput:**
$$\lambda_{degraded} = \gamma_{degraded} \cdot \lambda_{nominal} \cdot Q_{degraded}$$

Where $Q_{degraded} \leq 1$ represents quality loss.

### 5.3 Fault Tolerance via Redundancy

**N-Modular Redundancy (NMR):**

With $N$ parallel replicas and majority voting:

$$R_{NMR} = \sum_{k=\lceil N/2 \rceil}^{N} \binom{N}{k} R^k (1-R)^{N-k}$$

For TMR (Triple Modular Redundancy):
$$R_{TMR} = 3R^2 - 2R^3$$

**Active Replication:**

All $N$ replicas process all requests:
$$R_{active} = 1 - (1-R)^N$$

**Selective Replication for Critical Layers:**

Replicate only layers in the min-cut:

$$R_{selective} = \prod_{\ell \notin MC} R_\ell \cdot \prod_{\ell \in MC} (1-(1-R_\ell)^{n_\ell})$$

### 5.4 Mean Time to Failure Analysis

**State Transition Model:**

States: $\{S_0, S_1, \ldots, S_F\}$ where $S_k$ = $k$ components failed, $S_F$ = system failure.

**Transition Rates:**
$$\lambda_k = (N-k)\lambda \quad \text{(failure rate in state k)}$$
$$\mu_k = k\mu \quad \text{(repair rate in state k)}$$

**Steady-State Availability:**
$$A = \frac{\sum_{k=0}^{F-1} \frac{\lambda^k}{\mu^k \cdot k!}}{\sum_{k=0}^{F} \frac{\lambda^k}{\mu^k \cdot k!}}$$

**MTTR (Mean Time To Repair):**
$$MTTR = \frac{1}{\mu}$$

**Availability:**
$$A = \frac{MTBF}{MTBF + MTTR}$$

---

## 6. Scheduling Theory

### 6.1 Layer Execution as Job Scheduling

Each layer execution is a job $J_\ell = (r_\ell, p_\ell, d_\ell)$ with:
- $r_\ell$ = release time (when inputs available)
- $p_\ell$ = processing time
- $d_\ell$ = deadline (for real-time inference)

**Scheduling Objectives:**
1. **Minimize Makespan:** $C_{max} = \max_\ell C_\ell$
2. **Minimize Latency:** $L = C_{last} - r_{first}$
3. **Maximize Throughput:** $\lambda = \frac{N}{C_{max}}$

### 6.2 Johnson's Rule for Two-Machine Flow Shop

For attention → FFN as a two-stage flow shop:

**Johnson's Algorithm:**

```
1. Find minimum processing time among all jobs
2. If min is on Machine 1 (attention):
   - Schedule job first available
3. If min is on Machine 2 (FFN):
   - Schedule job last available
4. Remove job from list and repeat
```

**Optimal Sequence:**
$$\pi^* = \arg\min_\pi \max_{k=1,\ldots,L} \left( \sum_{\ell=1}^{k} p_\ell^{attn} + \sum_{\ell=k}^{L} p_\ell^{ffn} \right)$$

**Makespan:**
$$C_{max}^* = \max_{k} \left( \sum_{\ell=1}^{k} p_\ell^{attn} + \sum_{\ell=k}^{L} p_\ell^{ffn} \right)$$

### 6.3 Optimal Sequence for Inference

**Prefill Phase Scheduling:**

During prefill, all prompt tokens can be processed in parallel:

$$\pi_{prefill}: \text{Process all layers for all tokens in parallel}$$

**Decode Phase Scheduling:**

During decode, tokens are generated sequentially:

$$\pi_{decode}: \text{Process one token through all layers, then next token}$$

**Speculative Decoding Scheduling:**

With speculation factor $k$ (generate $k$ candidates):

$$\pi_{spec} = \text{Parallel verification of } k \text{ candidates}$$

**Expected Speedup:**
$$S_{spec} = \frac{1}{(1-P_{accept}) + \frac{P_{accept}}{k}}$$

### 6.4 Latency Minimization Equations

**First Token Latency (Time to First Token):**
$$L_{TTFT} = \sum_{\ell=0}^{L-1} \left( p_\ell^{attn} \cdot \frac{n_{prompt}}{b_{attn}} + p_\ell^{ffn} \cdot \frac{n_{prompt}}{b_{ffn}} \right)$$

Where $b_{attn}, b_{ffn}$ are batch sizes for attention and FFN.

**Inter-Token Latency:**
$$L_{ITL} = \sum_{\ell=0}^{L-1} \left( p_\ell^{attn} + p_\ell^{ffn} \right)$$

**Total Latency for $N$ Output Tokens:**
$$L_{total} = L_{TTFT} + N \cdot L_{ITL}$$

**Optimization Problem:**
$$\min_{b, \pi} L_{total} \quad \text{s.t.} \quad M(b) \leq M_{max}, \quad \lambda \geq \lambda_{min}$$

**KKT Conditions:**
$$\frac{\partial L_{total}}{\partial b} = \mu \frac{\partial M}{\partial b}$$
$$\frac{\partial L_{total}}{\partial \pi} = 0$$

### 6.5 Priority Scheduling for Mixed Workloads

**Weighted Fair Queueing:**

For multiple inference streams with weights $w_i$:

$$V_i(t) = \int_0^t \frac{w_i}{\sum_j w_j} \cdot \mu(\tau) d\tau$$

**Virtual Finish Time:**
$$F_i^k = \max(A_i^k, F_i^{k-1}) + \frac{L_i^k}{w_i}$$

Where $A_i^k$ is arrival time and $L_i^k$ is processing time.

**Delay Bound:**
$$D_i \leq \frac{L_{max}}{w_i} \cdot \sum_j w_j$$

---

## 7. Integrated Network Model

### 7.1 Complete Flow Network Equations

**System State:**
$$\mathbf{x}(t) = [q_0^{attn}(t), q_0^{ffn}(t), \ldots, q_{L-1}^{attn}(t), q_{L-1}^{ffn}(t), S_{KV}(t)]$$

**Dynamics:**
$$\frac{d\mathbf{x}}{dt} = \mathbf{A}\mathbf{x} + \mathbf{B}\mathbf{u}$$

Where:
- $\mathbf{A}$ encodes flow conservation
- $\mathbf{B}\mathbf{u}$ represents external input rate

**Stability Condition:**
$$\lambda < \min_\ell \mu_\ell \quad \text{(throughput less than bottleneck service rate)}$$

### 7.2 Performance Bounds

**Throughput Bound:**
$$\lambda_{max} = \min_{cut} c(S,T) = \text{min-cut capacity}$$

**Latency Bound:**
$$L_{min} = \sum_{\ell=0}^{L-1} \frac{1}{\mu_\ell} \quad \text{(zero queueing delay)}$$

**Latency-Throughput Tradeoff:**
$$L(\lambda) = L_{min} + \frac{\lambda}{\mu_{min}(\mu_{min} - \lambda)}$$

Where $\mu_{min} = \min_\ell \mu_\ell$ is the bottleneck service rate.

### 7.3 Optimal Resource Allocation

**Problem:**
$$\max_{F_0, \ldots, F_{L-1}} \lambda \quad \text{s.t.} \quad \sum_\ell F_\ell \leq F_{total}$$

**Solution (Water-Filling):**
$$F_\ell^* = F_{total} \cdot \frac{w_\ell}{\sum_j w_j}$$

Where $w_\ell$ is the compute weight of layer $\ell$.

**Equalized Layer Times:**
$$\frac{p_0}{F_0} = \frac{p_1}{F_1} = \cdots = \frac{p_{L-1}}{F_{L-1}}$$

---

## 8. Summary of Key Results

### 8.1 Fundamental Theorems

| Theorem | Statement | Implication |
|---------|-----------|-------------|
| Max-Flow Min-Cut | $\max |f| = \min c(S,T)$ | Throughput determined by bottleneck |
| Little's Law | $N = \lambda W$ | Average occupancy = rate × time |
| Jackson Network | Product-form solution | Closed-form queueing analysis |
| Burke's Theorem | Departure = Poisson | Pipeline stages decouple |

### 8.2 Key Equations

**Throughput:**
$$\lambda^* = \min_{\ell, op} \frac{F_\ell^{op}}{T_\ell^{op}}$$

**Latency:**
$$L = L_{TTFT} + N_{tokens} \cdot L_{ITL}$$

**Reliability:**
$$R(t) = e^{-\Lambda t}, \quad \Lambda = \sum_\ell \lambda_\ell$$

**Speedup:**
$$S(p) = \frac{p}{1 + \alpha p^\beta}$$

### 8.3 Design Guidelines

1. **Identify min-cut:** Focus optimization on bottleneck layers
2. **Balance layer times:** Equalize processing time across layers
3. **Cache optimization:** Working set must fit in cache
4. **Parallelism degree:** Optimize $p^*$ from extended Amdahl
5. **Redundancy:** Replicate min-cut components for reliability

---

## Appendix A: Notation Reference

| Symbol | Meaning |
|--------|---------|
| $G = (V, E)$ | Layer graph |
| $f(e)$ | Flow on edge $e$ |
| $c(e)$ | Capacity of edge $e$ |
| $\lambda$ | Arrival/throughput rate |
| $\mu$ | Service rate |
| $\rho$ | Utilization |
| $L$ | Latency |
| $R$ | Reliability |
| $MTBF$ | Mean time between failures |
| $p_\ell$ | Processing time at layer $\ell$ |
| $S_{KV}$ | KV cache size |

## Appendix B: Python Implementation

```python
import numpy as np
from scipy.optimize import linprog, minimize
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class LayerConfig:
    d_model: int
    d_ffn: int
    n_heads: int
    d_head: int
    seq_len: int
    cache_len: int

@dataclass
class HardwareConfig:
    flops: float  # Peak FLOPS
    hbm_bw: float  # HBM bandwidth GB/s
    pcie_bw: float  # PCIe bandwidth GB/s
    memory: float  # Total memory GB

class TransformerFlowNetwork:
    """
    Flow network model for transformer inference.
    """
    
    def __init__(self, layers: List[LayerConfig], hw: HardwareConfig):
        self.layers = layers
        self.hw = hw
        self.n_layers = len(layers)
        
    def attention_flops(self, layer: LayerConfig) -> float:
        """FLOPs per token for attention."""
        return 2 * layer.n_heads * layer.d_head * layer.d_model * (layer.seq_len + layer.cache_len)
    
    def ffn_flops(self, layer: LayerConfig) -> float:
        """FLOPs per token for FFN."""
        return 2 * layer.d_model * layer.d_ffn
    
    def attention_memory(self, layer: LayerConfig) -> float:
        """Memory bytes transferred per token for attention."""
        # Q, K, V projections + output projection + KV cache read
        param_bytes = 4 * layer.d_model * layer.d_model * 4  # float32
        cache_bytes = 2 * layer.d_model * layer.cache_len * 4
        return param_bytes + cache_bytes
    
    def ffn_memory(self, layer: LayerConfig) -> float:
        """Memory bytes transferred per token for FFN."""
        return 2 * layer.d_model * layer.d_ffn * 4  # float32
    
    def compute_capacity(self, layer_idx: int, op: str) -> float:
        """Compute capacity (tokens/sec) for a layer operation."""
        layer = self.layers[layer_idx]
        if op == 'attn':
            flops = self.attention_flops(layer)
        else:
            flops = self.ffn_flops(layer)
        return self.hw.flops / flops
    
    def memory_capacity(self, layer_idx: int, op: str) -> float:
        """Memory capacity (tokens/sec) for a layer operation."""
        layer = self.layers[layer_idx]
        if op == 'attn':
            mem = self.attention_memory(layer)
        else:
            mem = self.ffn_memory(layer)
        return self.hw.hbm_bw * 1e9 / mem  # Convert GB/s to bytes/s
    
    def edge_capacity(self, layer_idx: int, op: str) -> float:
        """Effective capacity considering compute and memory bounds."""
        c_compute = self.compute_capacity(layer_idx, op)
        c_memory = self.memory_capacity(layer_idx, op)
        return min(c_compute, c_memory)
    
    def max_flow(self) -> Tuple[float, List[Tuple[int, str, float]]]:
        """
        Compute max flow using min-cut identification.
        Returns (throughput, bottleneck_edges).
        """
        # Build capacity list
        capacities = []
        for i, layer in enumerate(self.layers):
            capacities.append((i, 'attn', self.edge_capacity(i, 'attn')))
            capacities.append((i, 'ffn', self.edge_capacity(i, 'ffn')))
        
        # Min-cut is minimum capacity
        min_cap = min(capacities, key=lambda x: x[2])
        min_cut_value = min_cap[2]
        
        # All edges with min capacity form the cut
        bottlenecks = [c for c in capacities if np.isclose(c[2], min_cut_value)]
        
        return min_cut_value, bottlenecks
    
    def latency(self, throughput: float) -> float:
        """Compute end-to-end latency using queueing model."""
        total_latency = 0.0
        
        for i, layer in enumerate(self.layers):
            for op in ['attn', 'ffn']:
                mu = self.edge_capacity(i, op)
                rho = throughput / mu
                
                if rho >= 1:
                    return float('inf')  # Unstable
                
                # M/M/1 queueing delay
                W = 1.0 / (mu - throughput)
                total_latency += W
        
        return total_latency
    
    def optimal_throughput(self, target_latency: float = None) -> float:
        """Find optimal throughput subject to latency constraint."""
        max_throughput, _ = self.max_flow()
        
        if target_latency is None:
            return max_throughput
        
        # Binary search for throughput meeting latency constraint
        lo, hi = 0, max_throughput
        for _ in range(50):
            mid = (lo + hi) / 2
            if self.latency(mid) <= target_latency:
                lo = mid
            else:
                hi = mid
        
        return lo

class KVCacheModel:
    """
    KV cache analysis using flow storage model.
    """
    
    def __init__(self, cache_size: int, n_layers: int, d_model: int):
        self.C = cache_size  # Total cache capacity (tokens)
        self.n_layers = n_layers
        self.d_model = d_model
        self.per_layer_cache = cache_size // n_layers
    
    def working_set(self, seq_len: int) -> int:
        """Working set size for sequence length."""
        return seq_len
    
    def hit_rate(self, working_set: int, alpha: float = 0.8) -> float:
        """
        Cache hit rate using LRU model.
        alpha: locality parameter
        """
        if working_set <= self.C:
            return 1.0
        return 1.0 - (working_set / self.C) ** alpha
    
    def effective_throughput(self, raw_throughput: float, seq_len: int) -> float:
        """Throughput adjusted for cache effects."""
        ws = self.working_set(seq_len)
        hr = self.hit_rate(ws)
        # Miss penalty: need to recompute KV
        miss_penalty = 10.0  # Cycles to recompute vs read
        return raw_throughput * (hr + (1 - hr) / miss_penalty)

class ReliabilityModel:
    """
    Reliability analysis for inference systems.
    """
    
    def __init__(self, n_layers: int, failure_rate_per_layer: float, 
                 repair_rate: float = 1/3600):
        self.n_layers = n_layers
        self.lambda_layer = failure_rate_per_layer
        self.mu = repair_rate
    
    def system_reliability(self, time: float) -> float:
        """System reliability at time t (series system)."""
        R_layer = np.exp(-self.lambda_layer * time)
        return R_layer ** self.n_layers
    
    def mtbf(self) -> float:
        """Mean time between failures."""
        return 1.0 / (self.n_layers * self.lambda_layer)
    
    def availability(self) -> float:
        """System availability."""
        mtbf = self.mtbf()
        mttr = 1.0 / self.mu
        return mtbf / (mtbf + mttr)
    
    def tmr_reliability(self, time: float, critical_layers: List[int]) -> float:
        """
        Reliability with TMR on critical layers.
        """
        R = 1.0
        for i in range(self.n_layers):
            R_layer = np.exp(-self.lambda_layer * time)
            if i in critical_layers:
                # TMR: R_tmr = 3R^2 - 2R^3
                R_layer = 3 * R_layer**2 - 2 * R_layer**3
            R *= R_layer
        return R

class SchedulingOptimizer:
    """
    Optimal scheduling for layer execution.
    """
    
    def __init__(self, processing_times: List[Tuple[float, float]]):
        """
        processing_times: List of (attn_time, ffn_time) per layer
        """
        self.times = processing_times
        self.n = len(processing_times)
    
    def johnson_sequence(self) -> List[int]:
        """
        Johnson's rule for two-machine flow shop.
        Returns optimal sequence of layer indices.
        """
        # Create jobs with (attn_time, ffn_time)
        jobs = list(range(self.n))
        front = []
        back = []
        
        remaining = jobs.copy()
        
        while remaining:
            # Find minimum across all remaining jobs
            min_val = float('inf')
            min_job = None
            min_machine = None
            
            for j in remaining:
                attn, ffn = self.times[j]
                if attn < min_val:
                    min_val = attn
                    min_job = j
                    min_machine = 1
                if ffn < min_val:
                    min_val = ffn
                    min_job = j
                    min_machine = 2
            
            remaining.remove(min_job)
            
            if min_machine == 1:
                front.append(min_job)
            else:
                back.append(min_job)
        
        return front + back[::-1]
    
    def makespan(self, sequence: List[int]) -> float:
        """Compute makespan for given sequence."""
        attn_complete = 0.0
        ffn_complete = 0.0
        
        for j in sequence:
            attn_t, ffn_t = self.times[j]
            attn_complete += attn_t
            ffn_complete = max(ffn_complete, attn_complete) + ffn_t
        
        return ffn_complete
    
    def optimal_makespan(self) -> float:
        """Optimal makespan using Johnson's sequence."""
        seq = self.johnson_sequence()
        return self.makespan(seq)

# Example usage
def demo():
    # Layer configuration for a 12-layer transformer
    layers = [LayerConfig(
        d_model=768,
        d_ffn=3072,
        n_heads=12,
        d_head=64,
        seq_len=512,
        cache_len=1024
    ) for _ in range(12)]
    
    # Hardware configuration (A100-like)
    hw = HardwareConfig(
        flops=312e12,  # 312 TFLOPS
        hbm_bw=2039,   # 2 TB/s
        pcie_bw=64,    # 64 GB/s
        memory=80      # 80 GB
    )
    
    # Create flow network
    flow_net = TransformerFlowNetwork(layers, hw)
    
    # Compute max flow (throughput)
    max_throughput, bottlenecks = flow_net.max_flow()
    print(f"Max throughput: {max_throughput:.2f} tokens/sec")
    print(f"Bottleneck edges: {bottlenecks}")
    
    # Compute latency at 50% utilization
    throughput = 0.5 * max_throughput
    latency = flow_net.latency(throughput)
    print(f"Latency at 50% throughput: {latency*1000:.2f} ms")
    
    # KV cache analysis
    kv_cache = KVCacheModel(cache_size=100000, n_layers=12, d_model=768)
    hit_rate = kv_cache.hit_rate(working_set=50000)
    print(f"Cache hit rate: {hit_rate:.2%}")
    
    # Reliability analysis
    reliability = ReliabilityModel(n_layers=12, failure_rate_per_layer=1e-6)
    print(f"MTBF: {reliability.mtbf()/3600:.2f} hours")
    print(f"Availability: {reliability.availability():.4f}")
    
    # Scheduling optimization
    times = [(0.001, 0.002) for _ in range(12)]  # 1ms attn, 2ms ffn per layer
    scheduler = SchedulingOptimizer(times)
    opt_seq = scheduler.johnson_sequence()
    opt_makespan = scheduler.optimal_makespan()
    print(f"Optimal makespan: {opt_makespan*1000:.2f} ms")

if __name__ == "__main__":
    demo()
```

---

## References

1. Ford, L. R., & Fulkerson, D. R. (1956). Maximal flow through a network. *Canadian Journal of Mathematics*.

2. Kleinrock, L. (1975). *Queueing Systems, Volume 1: Theory*. Wiley.

3. Johnson, S. M. (1954). Optimal two- and three-stage production schedules. *Naval Research Logistics Quarterly*.

4. Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. *AFIPS Conference*.

5. Papadimitriou, C. H., & Steiglitz, K. (1998). *Combinatorial Optimization: Algorithms and Complexity*. Dover.

6. Trivedi, K. S. (2001). *Probability and Statistics with Reliability, Queuing, and Computer Science Applications*. Wiley.
