# SuperInstance
## Investor Pitch Deck Content

**"The Nintendo of AI"**

---

## Slide 1: Title/Hook

### Slide Title
**SuperInstance: Physical AI Cartridges**

### Key Message
AI you can hold in your hand—insert cartridge, get intelligence.

### Supporting Content
- Logo placeholder: SuperInstance wordmark with cartridge icon
- Tagline: "The Nintendo of AI"
- $500K Seed Round
- Confidential

### Speaker Notes
"Imagine if every AI model was a physical thing you could buy, swap, and collect. That's SuperInstance. We're building the first physical AI cartridges—embedding neural networks directly into silicon that you insert like a game cartridge. No cloud. No drivers. No setup. Just intelligence on demand."

---

## Slide 2: Problem

### Slide Title
**Edge AI is Broken**

### Key Message
You can have cheap, easy, or fast—pick one.

### Supporting Content
| Solution | Price | Speed | Power | Setup |
|----------|-------|-------|-------|-------|
| Jetson Orin | $250 | 20 tok/s | 15W | Days |
| Hailo-10H | $90 | 5 tok/s | 5W | Hours |
| Cloud APIs | $$/month | Latency | Always-on | Complex |

**The gap**: No affordable, plug-and-play LLM inference at the edge.

**The market**: 70M Raspberry Pis, 500K robotics developers, millions of IoT devices—waiting for intelligence that doesn't require a cloud connection.

### Speaker Notes
"Today, edge AI forces developers into impossible choices. NVIDIA's Jetson costs $250, needs 15 watts, and requires a CUDA expert to set up. Hailo's new accelerator is cheaper but delivers only 5 tokens per second—slower than a CPU. Cloud APIs create recurring costs and privacy nightmares. There's a massive gap: sub-$100, plug-and-play, fast local inference. That gap is where SuperInstance lives."

---

## Slide 3: Solution (Cartridge Architecture)

### Slide Title
**Introducing the Physical AI Cartridge**

### Key Message
Neural networks encoded in silicon—insert, run, swap.

### Supporting Content
**How it works**:
1. Model weights encoded into metal layers during chip manufacture
2. Zero memory access latency—infinite bandwidth to compute
3. No drivers, no software stack, no configuration
4. Physical swap to change models—like loading a game

**The cartridge advantage**:
- Different cartridges for different AI tasks
- Collectible, tradeable intelligence
- Deterministic performance guaranteed
- No software compatibility issues

### Speaker Notes
"Here's our core invention. Traditional AI chips load models from memory—creating a bottleneck. We encode weights directly into the chip's metal layers during manufacturing. The model IS the hardware. This means zero access latency, zero memory bandwidth constraints, and zero setup. When you want a different model, you swap cartridges. It's like the Nintendo model—physical, collectible, instant. This hasn't been done at the edge before."

---

## Slide 4: Market Opportunity

### Slide Title
**$69 Billion Edge AI Market**

### Key Message
The sub-$100, sub-5W segment is wide open.

### Supporting Content
**Market sizing**:
- Edge AI chips: $26B (2025) → $69B (2030) at 17% CAGR
- Sub-$100 segment: ~$8B with no dominant player
- LLM-capable edge: New category, first-mover advantage

**Target segments**:
| Segment | Volume | Need |
|---------|--------|------|
| Maker/Hobbyist | 300K units/year | Privacy, simplicity, price |
| Industrial IoT | 100K units/year | Offline, deterministic, power |
| Education | 80K units/year | Hands-on AI, curriculum |
| Robotics | 50K units/year | Real-time, battery-powered |

**Why now**: Taalas raised $219M validating mask-locked architecture. They target data center. We own edge.

### Speaker Notes
"The edge AI market is growing at 17% annually to nearly $70 billion by 2030. But look at the sub-$100 segment—that's an $8 billion opportunity with no dominant player. Hailo captures makers but fails on LLM performance. NVIDIA owns development but is too expensive and complex for production edge. We're targeting four segments: makers who want privacy, industrial users who need offline operation, educators who need affordable hardware, and robotics developers who need battery-efficient intelligence. The window is open because Taalas, the only other company doing mask-locked inference, raised $219M for data center chips. They're not competing for edge. That's our 18-month moat."

---

## Slide 5: Product Demo/Technology

### Slide Title
**How We Achieve 5x Performance**

### Key Message
Mask-locked weights + ternary inference = orders of magnitude efficiency.

### Supporting Content
**Technical breakthroughs**:

| Innovation | Impact |
|------------|--------|
| Mask-locked weights | 0 pJ weight access (vs. 10+ pJ for SRAM) |
| Ternary inference | 95% gate reduction vs. FP16 |
| On-chip KV cache | Eliminates memory bandwidth bottleneck |
| iFairy arithmetic | Multiplication-free inference |

**Result**:
- 80-150 tokens/second
- 2-3 watts power consumption
- $35 unit economics
- 50x tokens/watt vs. Jetson

**Benchmark**:
```
SuperInstance:  100 tok/s @ 2W  = 50 tok/W
Hailo-10H:       5 tok/s @ 5W  =  1 tok/W
Jetson Nano:    20 tok/s @ 15W =  1.3 tok/W
```

### Speaker Notes
"Let me explain why we achieve 5x the performance at 1/3 the power. First, mask-locked weights. In a traditional chip, accessing weights from memory costs 10+ picojoules per bit. Our weights are encoded in metal—they're always present at the compute unit. Zero access energy. Second, we use ternary inference—weights are -1, 0, or +1. This eliminates 95% of the multiplication hardware. Third, we keep the KV cache entirely on-chip, removing the memory bandwidth bottleneck that kills LLM performance on edge chips. The result: 100 tokens per second at 2 watts. That's 50 tokens per watt versus 1 token per watt for our competitors. This is a step-function improvement."

---

## Slide 6: Business Model

### Slide Title
**Hardware + Platform**

### Key Message
Sell cartridges, build ecosystem, capture recurring value.

### Supporting Content
**Revenue streams**:

| Stream | Model | Year 3 Target |
|--------|-------|---------------|
| Cartridge sales | $35-89 ASP | $17.5M (200K units) |
| IP licensing | $2-5/device royalty | $5M |
| Platform services | SaaS for fleet mgmt | $1M |

**Unit economics**:
- COGS: $5-19 (config dependent)
- Gross margin: 61-85%
- Break-even: 167K units

**The platform play**:
- Multiple cartridges = multiple revenue per customer
- Software updates via physical refresh
- Enterprise fleet management subscriptions

### Speaker Notes
"We're a hardware company with platform economics. Cartridges sell at $35-89 with 60-80% gross margins. But the real value comes from the cartridge model itself—customers buy multiple cartridges for different tasks, and we capture recurring revenue when they upgrade models. Enterprise customers will pay for fleet management software. By Year 3, we project $17.5 million in cartridge revenue and $6 million in high-margin platform revenue. Break-even happens at 167,000 units—achievable in our second year of production."

---

## Slide 7: Go-to-Market

### Slide Title
**Community-First Launch**

### Key Message
Makers first, then enterprise, then global scale.

### Supporting Content
**Phase 1: Early Adopters (Month 1-12)**
- Target: 50 beta customers
- Channels: Hacker News, r/LocalLLaMA, maker forums
- Message: "First LLM cartridge under $100"
- Price: $49 beta program

**Phase 2: Volume (Month 13-24)**
- Target: 1,000+ customers
- Channels: DigiKey, Mouser, ODM partnerships
- Message: "Production-ready edge LLM"
- Price: $69-89 retail

**Phase 3: Global (Month 25+)**
- Target: 10,000+ customers
- India/China: $35 pricing for volume
- Enterprise: Direct sales, fleet pricing
- Developer ecosystem: SDK, custom cartridges

### Speaker Notes
"We're launching community-first because our earliest adopters are makers and developers who hang out on Reddit and Hacker News. They'll spread the word if the product works. Phase 1 is a $49 beta program targeting 50 customers who'll become advocates. Phase 2 expands to distributors like DigiKey and Mouser. Phase 3 is global scale—we've designed unit economics to support $35 pricing in India and China where volume justifies thinner margins. The cartridge model means we can offer region-specific models without software localization."

---

## Slide 8: Competitive Landscape

### Slide Title
**Clear Water in a Crowded Market**

### Key Message
We're the only ones doing mask-locked inference at the edge.

### Supporting Content
**Competitive matrix**:

| Player | Price | Speed | Power | Model Flex | Threat |
|--------|-------|-------|-------|------------|--------|
| **SuperInstance** | $35-89 | 100 tok/s | 2W | Cartridge | — |
| Hailo-10H | $90 | 5 tok/s | 5W | Programmable | Medium |
| Jetson Nano | $250 | 20 tok/s | 15W | Flexible | Low |
| Coral TPU | $60 | N/A | 2W | CNN only | None |
| Taalas | $$$ | 17000 tok/s | 200W+ | Fixed | None (different market) |

**Taalas analysis**:
- $219M raised for data center mask-locked chips
- Zero edge signals detected (job postings, announcements)
- 18-24 month window before potential pivot

**Our moat**: First-mover + patents + cartridge ecosystem

### Speaker Notes
"Let's be clear about competition. Hailo is our nearest competitor, but their LLM performance is 20x slower than ours—they're optimized for vision, not language. Jetson is too expensive and complex for production edge. Coral is end-of-life. The only company with similar technology is Taalas, who just raised $219M. But they're focused on 200-watt data center chips, not 2-watt edge devices. Our analysis shows zero signals of an edge pivot—no job postings for mobile engineers, no edge-related announcements. We have an 18-24 month window to establish the cartridge category before they could respond."

---

## Slide 9: Traction/Roadmap

### Slide Title
**Four Gates to Production**

### Key Message
Systematic de-risking before committing to silicon.

### Supporting Content
**Gate 0: FPGA Prototype (Month 1-3)**
- Target: 25 tok/s on KV260
- Budget: $50K
- Risk: Technical feasibility

**Gate 1: Architecture Freeze (Month 4-6)**
- Target: Patents filed, 15 LOIs
- Budget: $100K
- Risk: Market validation

**Gate 2: MPW Tapeout (Month 7-12)**
- Target: First silicon, 50 pilot customers
- Budget: $150K
- Risk: Silicon execution

**Gate 3: Production (Month 13-18)**
- Target: 10K units, first revenue
- Budget: $2-3M (Series A)
- Risk: Scale execution

**Current status**: Gate 0 initiated, architecture validated in simulation

### Speaker Notes
"Semiconductor startups fail when they commit to silicon too early. We've designed a four-gate process to systematically de-risk. Gate 0 is FPGA prototyping—we'll validate our arithmetic at 25 tokens per second on a Xilinx board. Gate 1 freezes the architecture, files patents, and secures customer LOIs. Gate 2 is our first silicon via MPW—20-40 units for pilot customers. Gate 3 is full production with Series A funding. We're asking for seed funding to complete Gates 0 and 1. That's $500K to prove the technology and validate the market before we ask for the $3M needed for silicon."

---

## Slide 10: Team

### Slide Title
**Building the Team**

### Key Message
Semiconductor experience + AI expertise + community building.

### Supporting Content
**Current team**:
- Founder: [Background in AI/semiconductor]

**Open roles (Seed funding enables)**:
| Role | Priority | Status |
|------|----------|--------|
| Architecture Lead | CRITICAL | Recruiting |
| ML Engineer | HIGH | Identified candidates |
| RTL Designer | HIGH | Open |

**Advisors needed**:
- Semiconductor veteran (ex-Apple/NVIDIA/Qualcomm)
- Edge AI ecosystem (ex-Hailo/Coral)
- Academic collaboration (Peking University iFairy team)

**Incubator**: Silicon Catalyst application in progress

### Speaker Notes
"I'm the founder, and I'm building this team deliberately. We need an architecture lead with silicon tapeout experience—this is our critical hire. ML engineer for model quantization and optimization. RTL designer for implementation. What we don't need is a large team—we're designing a fixed-function chip, not a general-purpose processor. Three senior engineers can execute this. We're also applying to Silicon Catalyst, the premier semiconductor incubator, which provides access to EDA tools, foundry relationships, and mentorship."

---

## Slide 11: Financials

### Slide Title
**Path to $35M Revenue**

### Key Message
Conservative projections, realistic ramp.

### Supporting Content
**5-Year Model**:

| Year | Units | Revenue | Gross Profit | Net Income |
|------|-------|---------|--------------|------------|
| 1 | 5K | $175K | $140K | ($650K) |
| 2 | 50K | $1.75M | $1.4M | ($500K) |
| 3 | 200K | $7M | $5.6M | $3M |
| 4 | 500K | $17.5M | $14M | $10M |
| 5 | 1M | $35M | $28M | $22M |

**Key assumptions**:
- ASP: $35 average (declines over time)
- Gross margin: 70%+ throughout
- Operating expenses scale with revenue

**Funding history**:
- Pre-seed: $150K (architecture)
- Seed: $500K (this round)
- Series A: $3M (Month 7-18)

### Speaker Notes
"Here's our financial model. Year 1 is pre-revenue—we're shipping 5,000 units to early adopters and pilot customers. Year 2 scales to 50,000 units as we hit production. Year 3 is when volume kicks in at 200,000 units and we turn profitable. By Year 5, we're at a million units and $35 million in revenue with $22 million net income. These are conservative projections—we've assumed price erosion and haven't baked in platform revenue upside. The key is that we hit profitability with Series A funding; we don't need Series B to survive."

---

## Slide 12: The Ask

### Slide Title
**$500K Seed Round**

### Key Message
Fund the de-risking, then we talk silicon.

### Supporting Content
**Use of funds**:

| Category | Amount | Purpose |
|----------|--------|---------|
| Architecture Lead | $150K | 6-month salary |
| ML Engineer | $100K | 6-month salary |
| FPGA Prototype | $50K | Hardware, consultants |
| Patent Filing | $50K | 5 provisionals |
| Runway Buffer | $150K | Contingency |

**Milestones for Series A**:
- ✓ FPGA prototype at 25+ tok/s
- ✓ 15 customer LOIs
- ✓ 5 patents filed
- ✓ Architecture frozen

**Investor profile**: Hardware-focused VCs, semiconductor incubators, strategic corporate investors

**Expected outcomes**:
- Bear case: $50M acquisition (8.6x return)
- Base case: $150M acquisition (26x return)
- Bull case: $400M acquisition (70x return)

### Speaker Notes
"We're raising $500K to complete Gates 0 and 1. This funds an architecture lead, an ML engineer, FPGA prototyping, and patent filing. The milestones for Series A are clear: working FPGA prototype, customer LOIs, patents filed, and architecture frozen. At that point, the technical risk is de-risked, and we're ready to commit to silicon. Our ideal investor understands hardware cycles, has patience for semiconductor timelines, and can add value through foundry relationships or customer introductions. The exit range is $50 to $400 million based on comparable transactions. At the base case, this seed round returns 26x. The question isn't whether mask-locked inference works—Taalas proved that. The question is who captures the edge. We intend to."

---

## Appendix Slides (Optional)

### A1: Technical Deep-Dive
- iFairy arithmetic details
- KV cache architecture
- Systolic array design

### A2: Patent Strategy
- 5 provisional patents
- Coverage: architecture, cartridge, swarm, on-chip KV

### A3: Taalas Analysis
- Full competitive intelligence report
- Edge pivot probability: 15-25%

### A4: Customer Personas
- Maker/Hobbyist (45%)
- Professional Developer (30%)
- Enterprise R&D (15%)
- Education (10%)

---

*Document Version: 1.0*
*Date: March 2026*
*Classification: Confidential - Investor Materials*
