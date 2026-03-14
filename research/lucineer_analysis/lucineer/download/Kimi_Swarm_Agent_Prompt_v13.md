# Kimi Swarm Agent Assignment Prompt
## Mask-Locked Inference Chip MVP v13.0 — Complementary Research Brief

**Purpose**: This document provides a comprehensive prompt for Kimi swarm agents to conduct parallel research that maximally complements the v13.0 document. It leverages Kimi's unique strengths in long-context reasoning, web browsing, and multi-language research.

---

## PART 1: UNDERSTANDING THE ASSIGNMENT

You are a swarm of specialized research agents working on the Mask-Locked Inference Chip project. Your role is to **complement, not duplicate** the work already done in v13.0. 

**What v13.0 Already Contains:**
- Validation status checklist (7/11 items validated)
- Taalas competitive analysis ($219M raised, data center focus)
- Memory pricing crisis documentation ($10-12 LPDDR4)
- 4 customer personas with specs
- 7/8 global research claims verified
- Complete deal terms structure
- Gate 0 specification (8-10 weeks)
- Architecture decision framework

**What v13.0 NEEDS (Your Assignment):**
The following research gaps require your unique capabilities. Each agent should tackle one area independently, then synthesize findings.

---

## PART 2: SWARM AGENT ASSIGNMENTS

### AGENT 1: Technical Deep-Dive — BitNet & Ternary Inference

**Your Unique Value**: Kimi can process entire research papers and technical documentation in context.

**Assignment**: 
Conduct a comprehensive technical analysis of BitNet b1.58-2B-4T and ternary inference feasibility.

**Specific Tasks**:
1. **BitNet Model Verification**:
   - Access HuggingFace: https://huggingface.co/microsoft/bitnet-b1.58-2B-4T
   - Verify: Model exists, parameter count, license (MIT?), download stats
   - Check: Are there known issues, bugs, or limitations reported?
   - Find: Any papers citing this model since April 2025

2. **Ternary Inference Hardware Research**:
   - Search for: "ternary neural network hardware implementation 2025 2026"
   - Search for: "1.58 bit inference chip" 
   - Search for: "BitNet hardware accelerator"
   - Find: Any startups, research groups, or products implementing ternary inference

3. **SPICE Simulation Standards**:
   - What is the industry standard for noise margin in ternary logic?
   - Find papers on "ternary logic noise margin CMOS"
   - Is 50mV a reasonable threshold? What's the correct threshold?

4. **Output Format**:
```
BITNET_MODEL_STATUS:
- Exists: [YES/NO]
- Parameters: [actual count]
- License: [type]
- Known Issues: [list]
- Citations: [count and key papers]

TERNARY_HARDWARE_LANDSCAPE:
- Competitors: [list any]
- Research Groups: [list]
- Feasibility Assessment: [1-10 score with rationale]

SPICE_SIMULATION_STANDARDS:
- Recommended Noise Margin: [value with source]
- Industry Precedent: [cite]
```

---

### AGENT 2: Chinese Language Deep Research — Native Sources

**Your Unique Value**: Kimi has exceptional Chinese language understanding and can access Chinese academic sources that Western search misses.

**Assignment**:
Conduct native Chinese language research on the two verified Chinese claims and find NEW relevant research.

**Specific Tasks**:

1. **Fairy ±i Complex-Valued LLM Deep-Dive**:
   - Search CNKI (知网), Chinese arXiv mirrors
   - Keywords: 复数值大语言模型, Fairy ±i, 加法推理, 2比特量化
   - Find: Full paper, authors, contact information
   - Find: Any hardware implementation attempts
   - Find: GitHub repos, code, demos

2. **CNT TPU (Peking University) Deep-Dive**:
   - Search: 北京大學 碳纳米管 张量处理器
   - Find: Full paper, research group, timeline to commercialization
   - Find: Any patents filed

3. **NEW Chinese AI Chip Research**:
   - Search: 边缘AI芯片 2026 (edge AI chip 2026)
   - Search: 神经网络推理加速器 (neural network inference accelerator)
   - Search: 昆仑, 寒武纪, 地平线 new product announcements
   - Find: Any Chinese startups working on LLM inference chips for edge

4. **Chinese Memory/Supply Chain Intelligence**:
   - Search: 长鑫存储 LPDDR4 (Changxin LPDDR4)
   - Find: Current production capacity, pricing, export status
   - Find: Alternative Chinese memory suppliers

5. **Output Format**:
```
FAIRY_PMI_RESEARCH:
- Full Paper URL: [link]
- Authors: [names and emails if available]
- Hardware Implications: [detailed analysis]
- Code/Demo: [links]

CNT_TPU_RESEARCH:
- Research Group: [names]
- Timeline: [estimated]
- Patents: [numbers]

NEW_CHINESE_AI_CHIPS:
- [list startups/products with details]

CHINESE_MEMORY_INTELLIGENCE:
- Changxin Status: [current situation]
- Alternative Suppliers: [list]
```

---

### AGENT 3: Japanese & Korean Language Research

**Your Unique Value**: Native language access to Japanese and Korean research sources.

**Assignment**:
Deep dive into Japanese and Korean edge AI and memory research.

**Specific Tasks**:

1. **Japanese Edge AI Semiconductor Project**:
   - Search: 次世代エッジAI半導体 (next-generation edge AI semiconductor)
   - Search: NEDO AIチップ 2026
   - Find: Project timeline, participants, budget, target specifications
   - Find: Any relation to local LLM inference

2. **MN-Core (Preferred Networks) Investigation**:
   - Search: MN-Core 推論 (MN-Core inference)
   - Find: Is there an edge variant planned?
   - Find: Any LLM inference benchmarks?

3. **Korean 2T1C DRAM Deep-Dive**:
   - Search: KAIST HPIC Lab contact information
   - Search: 2T1C DRAM 상용화 (2T1C DRAM commercialization)
   - Search: KAIST ADC-free MAC
   - Find: Professor names, email contacts
   - Find: Timeline to commercial availability
   - Find: Any startup spin-offs

4. **Korean Memory Industry Update**:
   - Search: SK 하이닉스 LPDDR4 2026
   - Search: 삼성 LPDDR5 가격
   - Find: Current supply situation, allocation status
   - Find: Price forecasts

5. **Output Format**:
```
JAPANESE_EDGE_AI_PROJECT:
- Timeline: [dates]
- Participants: [companies/universities]
- Target Specs: [if available]
- Threat Assessment: [low/medium/high]

MN_CORE_STATUS:
- Edge Variant: [yes/no/planned]
- LLM Benchmarks: [if available]

KOREAN_2T1C_RESEARCH:
- Key Contacts: [names, emails]
- Commercialization Timeline: [estimate]
- Spin-offs: [list]

KOREAN_MEMORY_STATUS:
- SK Hynix: [situation]
- Samsung: [situation]
```

---

### AGENT 4: Real-Time Competitive Intelligence

**Your Unique Value**: Kimi can browse the web for real-time updates that static research files cannot capture.

**Assignment**:
Conduct comprehensive competitive intelligence gathering with focus on VERY RECENT developments.

**Specific Tasks**:

1. **Taalas Deep Monitoring**:
   - Search: "Taalas AI chip" last 30 days
   - Search: "Taalas edge" or "Taalas mobile" or "Taalas low power"
   - Search: Taalas job postings for "mobile", "embedded", "edge"
   - Search: Taalas investor updates
   - Find: ANY indication of edge/mobile strategy

2. **Hailo Competitive Update**:
   - Search: "Hailo-15H" launch status
   - Search: "Hailo LLM" benchmarks 2026
   - Search: Hailo press releases 2026
   - Find: Any new products, partnerships, performance claims

3. **New Entrants Search**:
   - Search: "edge LLM chip startup 2026"
   - Search: "LLM inference accelerator $100"
   - Search: "BitNet hardware" startup
   - Find: Any new competitors, funding announcements

4. **Raspberry Pi AI Strategy**:
   - Search: "Raspberry Pi AI" announcements 2026
   - Search: "Pi 6" rumors or announcements
   - Find: Any indication of Pi Foundation building own AI silicon

5. **Memory Market Real-Time**:
   - Search: "LPDDR4 price" February 2026
   - Search: "memory shortage" 2026
   - Find: Current spot prices, availability

6. **Output Format**:
```
TAALAS_MONITORING:
- Recent News: [list with dates]
- Edge Signals: [any found]
- Job Postings: [relevant ones]

HAILO_UPDATE:
- New Products: [list]
- LLM Claims: [any]
- Partnerships: [any]

NEW_ENTRANTS:
- [list startups with funding, product descriptions]

PI_FOUNDATION:
- AI Strategy: [latest]
- Pi 6 Rumors: [any]

MEMORY_REALTIME:
- Current LPDDR4 Price: [with source]
- Availability: [status]
```

---

### AGENT 5: Investor & Acquisition Intelligence

**Your Unique Value**: Kimi can cross-reference investor portfolios and acquisition patterns.

**Assignment**:
Build comprehensive investor and acquisition intelligence for fundraising and exit strategy.

**Specific Tasks**:

1. **Qualcomm Acquisition Pattern Analysis**:
   - Research: Qualcomm acquisitions 2020-2026
   - Find: Average deal size, multiples, integration patterns
   - Find: Key decision-makers, M&A team structure
   - Find: Recent Alphawave ($2.4B) deal structure

2. **Edge AI Investor Identification**:
   - Search: "edge AI" venture capital investments 2025-2026
   - Find: VCs who have invested in edge AI chips
   - Cross-reference: Which have mobile/embedded portfolio focus?
   - Find: Check size preferences ($150K-500K seed)

3. **Hardware Startup Exit Analysis**:
   - Search: Semiconductor startup exits 2024-2026
   - Filter: Edge AI, inference chips, sub-$100M exits
   - Find: Valuation multiples, time to exit, key value drivers

4. **Taalas Investor Intelligence**:
   - Search: Taalas investors, funding rounds
   - Find: Who invested? Any edge-focused VCs?
   - Implication: If Taalas pivots to edge, what resources do they have?

5. **Output Format**:
```
QUALCOMM_ACQUISITION_PATTERN:
- Recent Deals: [list with valuations]
- Decision Makers: [names/titles]
- Alphawave Structure: [breakdown]

EDGE_AI_INVESTORS:
- Tier 1 (Best Fit): [list with rationale]
- Tier 2 (Good Fit): [list]
- Contact Strategy: [recommended approach]

HARDWARE_EXIT_DATA:
- Exits 2024-2026: [list with multiples]
- Key Value Drivers: [ranked]

TAALAS_INVESTORS:
- Investor List: [names]
- Edge Focus: [yes/no for each]
```

---

### AGENT 6: Customer Validation Research

**Your Unique Value**: Kimi can browse forums, reviews, and community discussions to extract genuine user sentiment.

**Assignment**:
Conduct deep customer validation research from actual user discussions.

**Specific Tasks**:

1. **Hailo User Sentiment Analysis**:
   - Browse: Reddit r/raspberry_pi, r/LocalLLaMA for Hailo-10H discussions
   - Browse: Hailo community forums
   - Find: Specific complaints about LLM performance
   - Find: What users wish Hailo could do better
   - Extract: Direct quotes with usernames for credibility

2. **Jetson vs Hailo vs Coral Comparison Research**:
   - Find: Head-to-head comparisons posted by users
   - Find: Why users chose one over another
   - Find: Regret points ("I wish I had chosen...")

3. **BitNet User Community**:
   - Browse: r/LocalLLaMA for BitNet discussions
   - Find: What are users doing with BitNet models?
   - Find: Hardware setups being used
   - Find: Performance complaints/wishes

4. **Educational AI Hardware Research**:
   - Search: University AI courses using edge hardware
   - Find: Course syllabi mentioning LLMs, edge AI
   - Find: Budget constraints per student
   - Find: What hardware are universities actually buying?

5. **Output Format**:
```
HAILO_USER_SENTIMENT:
- Common Complaints: [list with quotes]
- Wishlist Features: [list]
- Performance Reality: [actual vs claimed]

COMPARISON_RESEARCH:
- User Preferences: [summarized]
- Key Decision Factors: [ranked]

BITNET_COMMUNITY:
- Use Cases: [list]
- Hardware Setups: [list]
- Wishes: [list]

EDUCATION_RESEARCH:
- University Examples: [list]
- Budget Per Student: [typical]
- Current Hardware: [what's being used]
```

---

### AGENT 7: Technical Paper Deep-Read

**Your Unique Value**: Kimi can process entire academic papers and extract actionable technical insights.

**Assignment**:
Deep-read the key technical papers and extract hardware-relevant insights.

**Specific Tasks**:

1. **BitNet b1.58 Paper Analysis**:
   - Find and read: "The Era of 1-bit LLMs" paper from Microsoft
   - Extract: Hardware requirements, memory bandwidth calculations
   - Extract: Any mention of FPGA implementation
   - Extract: Performance per watt metrics

2. **2T1C DRAM Paper Analysis**:
   - Find and read: "Dual-mode 2T1C DRAM Process-In-Memory Architecture"
   - Extract: Cell size, power consumption, operating frequency
   - Extract: Compatibility with standard CMOS logic process
   - Extract: Any limitations or requirements

3. **Fairy ±i Complex-Valued LLM Paper Analysis**:
   - Find and read: Full paper on complex-valued LLM
   - Extract: How does addition-only inference work?
   - Extract: Hardware simplification potential (quantified)
   - Extract: Quality comparison vs standard quantization

4. **TeLLMe FPGA BitNet Paper Analysis**:
   - Find and read: TeLLMe paper on BitNet FPGA implementation
   - Extract: Actual performance achieved
   - Extract: Resource utilization (LUTs, BRAM)
   - Extract: Lessons learned for our FPGA demo

5. **Output Format**:
```
BITNET_PAPER:
- Hardware Requirements: [detailed]
- FPGA Implementation: [any mentioned]
- Power Efficiency: [metrics]

2T1C_PAPER:
- Cell Size: [value]
- Power: [value]
- Process Compatibility: [assessment]
- Limitations: [list]

FAIRY_PAPER:
- Addition-Only Mechanism: [explanation]
- Hardware Simplification: [quantified %]
- Quality Tradeoff: [comparison]

TELLME_PAPER:
- FPGA Performance: [tok/s]
- Resource Utilization: [details]
- Key Learnings: [list]
```

---

## PART 3: SYNTHESIS INSTRUCTIONS

After completing individual assignments, synthesize your findings into a single report:

### Synthesis Structure:

```
# Kimi Swarm Research Report
## Mask-Locked Inference Chip MVP v13.0 Complementary Research

### Executive Summary
[2-3 paragraph summary of most critical findings]

### Section 1: Technical Verification
[Agent 1 + Agent 7 combined findings]
- BitNet model status
- Ternary hardware landscape
- Paper insights

### Section 2: Asian Research Deep-Dive
[Agent 2 + Agent 3 combined findings]
- Chinese AI chip landscape
- Japanese projects
- Korean 2T1C contacts

### Section 3: Competitive Intelligence
[Agent 4 findings]
- Taalas monitoring
- Hailo update
- New entrants

### Section 4: Investor & Exit Intelligence
[Agent 5 findings]
- Investor targets
- Exit precedents
- Acquisition patterns

### Section 5: Customer Intelligence
[Agent 6 findings]
- User sentiment
- Wishlist features
- Educational market

### Section 6: Critical Actions Identified
[What should the founder do next based on findings?]
1. [Action item with priority]
2. [Action item with priority]
...

### Section 7: Red Flags / Concerns
[What negative findings should be escalated?]

### Appendix: Source Links
[All URLs for verification]
```

---

## PART 4: WHAT NOT TO DO

**Do NOT**:
1. Regurgitate information already in v13.0
2. Provide generic analysis — be specific with URLs, names, numbers
3. Speculate without sources
4. Skip the Chinese/Japanese/Korean native language research
5. Forget to check DATES — only 2025-2026 information is relevant

**DO**:
1. Provide direct URLs for every claim
2. Include specific names, emails, contacts where possible
3. Quote actual user sentiment with attribution
4. Cross-reference findings across agents
5. Prioritize actionable intelligence over general information

---

## PART 5: SUCCESS CRITERIA

Your research will be evaluated on:

1. **Novelty**: Does it find information NOT in v13.0? (40%)
2. **Actionability**: Can the founder take immediate action? (30%)
3. **Specificity**: Are there names, numbers, URLs? (20%)
4. **Timeliness**: Is it current (2025-2026)? (10%)

**Target**: Generate at least 10 specific action items and 5 specific contacts/introductions that advance the project.

---

## ATTACHED DOCUMENTS

Review these documents for context (not to duplicate):

1. `/home/z/my-project/download/Mask_Locked_Chip_MVP_v13_Validated.pdf` - Current version
2. `/home/z/my-project/download/v13_user_market_research.json` - User personas
3. `/home/z/my-project/download/v13_multilang_verification.json` - Research verification
4. `/home/z/my-project/download/v13_memory_pricing.json` - Memory pricing
5. `/home/z/my-project/download/v13_competitive_customer.json` - Competitive analysis

---

**BEGIN RESEARCH NOW. Report back in structured format.**
