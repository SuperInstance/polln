# TernaryAir UX Playtest Report
## Multi-Persona Simulation Results & Iterative Improvements

**Simulation Date:** March 2026  
**Package Version:** 1.0.0  
**Test Duration:** 60 minutes (simulated)

---

## Executive Summary

| Persona | Would Proceed | Key Blocker | Time to Confusion |
|---------|---------------|-------------|-------------------|
| Sarah (Non-technical) | ❌ No | "What do I DO with this?" | 2 minutes |
| Wei (Hardware Engineer) | ❌ No | "RTL is incomplete stubs" | 5 minutes |
| Marcus (Python Developer) | ⚠️ Maybe | "pip install doesn't exist" | 3 minutes |
| Dr. Priya (AI Researcher) | ❌ No | "No citations, no benchmarks" | 4 minutes |
| Jake (Startup Founder) | ❌ No | "Can't buy it, can't test it" | 2 minutes |
| Alex (Student) | ❌ No | "Where do I start?" | 1 minute |

**Overall Verdict:** The package is **website content masquerading as a product**. Every persona hit a wall within 5 minutes.

---

## Detailed Persona Reports

### 1. SARAH - Non-Technical Healthcare User

**Persona:** Healthcare administrator, privacy-conscious, HIPAA compliance needs

#### What She Expected
A downloadable app or a physical device she could buy.

#### What She Found
- Source code files (.sv, .tsx) she couldn't open
- No README.txt explaining what to do
- Python code snippets requiring programming knowledge
- No way to actually USE the product

#### Specific Pain Points

| Issue | Quote |
|-------|-------|
| Confusing download | "I expected an app, got blueprints" |
| Missing README | "WHERE DO I START??" |
| Technical jargon | "What is RTL? What is pip?" |
| No purchase option | "Where do I buy the $99 device?" |
| Compliance gap | "I need HIPAA docs to show my compliance officer" |

#### Recommendations from Sarah

1. **Add START_HERE.txt** at package root
2. **Clarify product status** - Is this shipping? Concept? Prototype?
3. **Create a desktop demo app** (even just simulator with GUI)
4. **Add healthcare compliance section**
5. **Remove code from "For Users" page entirely**

---

### 2. WEI - Hardware Engineer

**Persona:** 8 years digital design, FPGA experience, skeptical of claims

#### Technical Assessment

| Component | Status | Issue |
|-----------|--------|-------|
| RAU | Partial | Not novel, standard ternary MAC |
| Synaptic Array | Broken | Combinatorial 768-input adder tree won't close timing |
| Weight ROM | Stub | Behavioral model, not synthesizable |
| KV Cache | Impossible | Claims 768MB SRAM on 120mm² die |
| Top Level | Incomplete | References non-existent modules |
| Testbenches | Missing | ZERO verification code |

#### Critical Technical Gaps

```
Missing Modules (referenced but don't exist):
- embedding_rom.sv
- attention.sv
- feedforward.sv
- layer_norm.sv
- softmax.sv
- tokenizer.sv
- Any testbench
```

#### Performance Claims Analysis

| Claim | Reality Check |
|-------|---------------|
| 768MB SRAM | Physically impossible on 120mm² at 28nm |
| 100+ tok/s | No timing analysis, adder tree is timing disaster |
| 3-5W | Unsubstantiated without power analysis |
| 90% gate reduction | Roughly accurate but not novel |

#### Wei's Recommendations

1. **Add synthesizable RTL** - Not behavioral stubs
2. **Include testbenches** - Even 50% coverage would be something
3. **Fix adder tree** - Needs 4-6 stage pipeline
4. **Realistic memory claims** - 768MB needs off-chip DRAM
5. **Post-synthesis reports** - Show LUT/BRAM counts
6. **One complete layer** - Demonstrate real synthesis

---

### 3. MARCUS - Python Developer

**Persona:** 5 years Python, uses OpenAI API, wants local AI

#### Developer Experience Issues

```bash
# What the docs say:
$ pip install ternaryair

# What actually happens:
ERROR: Could not find a version that satisfies the requirement ternaryair
```

**Critical Gap:** The package doesn't exist on PyPI. All code examples fail.

#### Missing for Real Integration

| Need | Status |
|------|--------|
| PyPI package | ❌ Doesn't exist |
| Simulator implementation | ❌ Only stubs shown |
| Error handling examples | ❌ Missing |
| Async support | ❌ Not documented |
| Type hints | ❌ Not shown |
| Real model weights | ❌ No download |
| LangChain integration | ❌ Only mentioned |

#### Comparison to Alternatives (Marcus's View)

| Feature | TernaryAir | Ollama | OpenAI |
|---------|------------|--------|--------|
| Installable now | ❌ No | ✅ Yes | ✅ Yes |
| Working code | ❌ No | ✅ Yes | ✅ Yes |
| Documentation | ⚠️ Stub | ✅ Complete | ✅ Complete |
| Cost | $99 (device) | Free | Pay per use |

**Marcus's Verdict:** "I can't evaluate this because there's nothing to run. I'll stick with Ollama."

---

### 4. DR. PRIYA - AI Researcher

**Persona:** PhD in ML, publishes at NeurIPS, studies quantization

#### Academic Concerns

| Claim | Citation Needed | Status |
|-------|-----------------|--------|
| 90% gate reduction | Comparative study | ❌ Missing |
| 85% power reduction | Power analysis | ❌ Missing |
| Accuracy at ternary | Benchmark results | ❌ Missing |
| BitNet b1.58 baseline | arXiv:2402.17764 | ✅ Can cite |
| iFairy comparison | arXiv:2508.05571 | ⚠️ Mentioned |

#### Reproducibility Issues

```
Questions a researcher would ask:
1. What model is actually running? (BitNet? Custom?)
2. What's the accuracy on standard benchmarks? (MMLU, GSM8K?)
3. How was quantization done? (QAT? PTQ?)
4. What's the perplexity degradation?
5. Where's the model card?
```

#### Missing for Academic Credibility

- No paper or technical report
- No benchmark comparisons
- No accuracy degradation analysis
- No model weights/checkpoints
- No training methodology

---

### 5. JAKE - Startup Founder

**Persona:** Runs AI SaaS, $50K/month OpenAI bill, evaluating alternatives

#### Business Decision Blockers

| Question | Answer Needed | Found |
|----------|---------------|-------|
| When can I buy it? | Shipping date | ❌ Not found |
| Can I test before buying? | Demo/trial | ❌ No working demo |
| Who's behind this? | Company/team | ⚠️ One person mentioned |
| What's support like? | SLA, community | ❌ Not addressed |
| What's the upgrade path? | New models | ❌ Not clear |

#### ROI Analysis (What Jake Would Calculate)

```
Current: $50K/month OpenAI = $600K/year

TernaryAir scenario:
- Hardware cost: $99 × N devices
- But: Can I actually buy it? NO
- But: Will it work? CAN'T TEST
- But: Support? UNKNOWN

Decision: Cannot evaluate ROI without product availability
```

#### Competitive Comparison (Jake's View)

| Option | Price | Available | Performance |
|--------|-------|-----------|-------------|
| TernaryAir | $99 | ❌ No | Unknown |
| Hailo-10H | $70 | ✅ Yes | 9 tok/s |
| Jetson Orin | $250 | ✅ Yes | 30 tok/s |
| Continue OpenAI | $600K/yr | ✅ Yes | Reliable |

---

### 6. ALEX - Student Learner

**Persona:** Junior CS major, curious about AI hardware, limited budget

#### Learning Experience Issues

| What Alex Needed | What Was Found |
|------------------|----------------|
| Step-by-step introduction | Technical jargon immediately |
| "Start here" guide | No clear entry point |
| Interactive demo | Nothing runnable |
| Explained concepts | Assumed knowledge |
| Projects to try | No tutorials |

#### Terms That Needed Explanation

- "Ternary" - mentioned but not explained for beginners
- "Mask-locked" - used throughout, never explained
- "RAU" - acronym not expanded initially
- "Via encoding" - visual shown but not explained
- "Systolic array" - used without context

---

## Consolidated Issues by Category

### 🔴 Critical (Blocks All Users)

1. **No working product** - Nothing can be installed/run
2. **Missing PyPI package** - `pip install ternaryair` fails
3. **No README** - Package has no entry point
4. **Product status unclear** - Is this shipping? Concept? Prototype?

### 🟠 High (Blocks Technical Users)

5. **RTL is incomplete** - Missing modules, won't synthesize
6. **Zero verification** - No testbenches
7. **Impossible memory claims** - 768MB SRAM on 120mm² is physically impossible
8. **Timing analysis missing** - Adder tree won't close timing

### 🟡 Medium (Reduces Trust)

9. **No citations** - Academic claims unsubstantiated
10. **No benchmarks** - Performance claims unproven
11. **No comparison** - Why this vs Hailo, Jetson, Ollama?
12. **Compliance missing** - No HIPAA documentation

### 🟢 Low (Polish Items)

13. **Jargon in beginner sections** - "For Users" page has technical terms
14. **Missing video demos** - Visual explanation would help
15. **No community links** - Discord, forum, etc.

---

## Iteration 1 Improvements (Priority Order)

### Phase 1: Existence Proof (Week 1)

1. **Create actual PyPI package**
   ```bash
   # This must work:
   pip install ternaryair
   python -c "from ternaryair import Simulator; print('OK')"
   ```

2. **Add README.md to package root**
   ```markdown
   # TernaryAir
   
   **Status:** Early development. Not yet shipping.
   
   This package contains:
   - RTL source code (SystemVerilog)
   - Website source (Next.js)
   - Documentation
   
   ## Quick Test
   pip install ternaryair
   python -m ternaryair.demo
   ```

3. **Create working simulator**
   ```python
   # This must actually work:
   from ternaryair import Simulator
   sim = Simulator()
   print(sim.generate("Hello"))  # Returns actual output
   ```

### Phase 2: Credibility (Week 2)

4. **Add one complete RTL module with testbench**
   ```systemverilog
   // rau_complete.sv - synthesizable
   // tb_rau.sv - testbench with coverage
   ```

5. **Add benchmark results table**
   | Model | MMLU | GSM8K | HumanEval |
   |-------|------|-------|-----------|
   | FP16 Baseline | 63.4% | 77.7% | 67.0% |
   | TernaryAir | XX% | XX% | XX% |

6. **Clarify memory architecture**
   - Update claims to realistic numbers
   - Or document off-chip DRAM requirement

### Phase 3: Trust (Week 3)

7. **Add comparison page**
   - Honest comparison vs Hailo, Jetson, Ollama
   - Acknowledge where competitors are ahead
   - Highlight where TernaryAir wins

8. **Add technical paper/report**
   - Even 4-page arXiv preprint
   - Cite BitNet, iFairy, ternary networks

9. **Create demo video**
   - 5-minute walkthrough
   - Show actual simulation running

### Phase 4: Adoption (Week 4)

10. **Developer quickstart that works**
    ```bash
    # 30-second test:
    pip install ternaryair
    ternaryair demo
    # Opens browser with working demo
    ```

11. **LangChain integration example**
12. **Docker container for easy testing**

---

## Revised Package Structure

```
ternaryair-complete-v2/
├── README.md                    # NEW: Entry point
├── START_HERE.txt               # NEW: One-page guide
├── STATUS.md                    # NEW: Product status
│
├── simulator/                   # NEW: Working Python package
│   ├── ternaryair/
│   │   ├── __init__.py
│   │   ├── simulator.py         # Actually works
│   │   └── demo.py
│   └── setup.py
│
├── rtl/
│   ├── rau.sv                   # Updated with testbench
│   ├── tb_rau.sv                # NEW
│   └── SYNTHESIS_STATUS.md      # NEW: What synthesizes
│
├── docs/
│   ├── BENCHMARKS.md            # NEW
│   ├── COMPARISON.md            # NEW
│   └── CITATIONS.md             # NEW
│
├── website/                     # Renamed from src/app
│   └── (existing files)
│
└── demos/
    ├── quick_start.ipynb        # NEW
    └── video_walkthrough.mp4    # NEW
```

---

## Key Metrics to Track

| Metric | Current | Target (v2) |
|--------|---------|-------------|
| Time to first success | ∞ (broken) | < 30 seconds |
| pip install works | ❌ No | ✅ Yes |
| RTL synthesizes | ❌ No | ⚠️ Partial |
| Simulator works | ❌ No | ✅ Yes |
| Documentation accuracy | Low | High |
| Trust score (1-10) | 2 | 6 |

---

## Conclusion

The current package is **beautiful marketing materials with nothing behind them**. Every persona tested hit a wall because there's no working code, no installable package, and no way to actually evaluate the claims.

**The single most important fix:** Make `pip install ternaryair` work and return meaningful output. Without this, no one can take this seriously.

**Secondary fixes:** Complete one RTL module with testbench, add realistic benchmarks, and clarify product status/timeline.

---

*Report generated from multi-persona UX simulation*  
*Next step: Implement Phase 1 improvements and re-test*
