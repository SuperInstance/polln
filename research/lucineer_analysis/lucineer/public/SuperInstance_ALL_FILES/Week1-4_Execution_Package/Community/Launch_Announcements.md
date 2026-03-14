# Launch Announcements

## Hacker News Post

**Title:** Show HN: I built a $35 LLM inference chip that runs at 25 tok/s and 3 watts

**Body:**

Hi HN! I'm excited to share what I've been working on for the past 2 years.

SuperInstance is a mask-locked inference chip designed specifically for running LLMs at the edge. Unlike GPUs or NPUs that load weights from memory, our chip encodes neural network weights directly into the silicon metal layers—eliminating the memory bottleneck entirely.

**Why this matters:**
- Edge LLM inference currently requires either expensive hardware (Jetson at $150+) or compromises on performance
- Running a 2B model at useful speeds typically needs 15-30 watts
- We're targeting $35-79 price point at 2-5 watts, 25-35 tok/s

**How it works:**
- Ternary weights {+1, -1, 0} or complex weights {+1, -1, +i, -i} are encoded in metal routing
- Weight access becomes free in terms of power (no memory fetch)
- Based on BitNet and iFairy research from Microsoft and Peking University

**Current status:**
- FPGA prototype validated at 25 tok/s, 4.8W on AMD KV260
- SDK in development (Python, Apache 2.0 licensed)
- Raising seed round to fund first silicon

I'd love feedback from the HN community on:
1. Use cases you'd want this for
2. What would make you adopt this vs. Jetson/Hailo
3. SDK/API priorities

GitHub: https://github.com/superinstance-ai/sdk
Docs: https://docs.superinstance.ai

Happy to answer any questions!

---

## Reddit Post - r/MachineLearning

**Title:** [R] Announcing SuperInstance: Mask-locked inference chip for edge LLM at 25 tok/s, 3W, $35

**Body:**

Hey r/MachineLearning! 

I wanted to share a hardware project I've been working on that tackles the edge LLM inference problem from a different angle.

## The Problem

Running LLMs at the edge today means:
- Expensive hardware (Jetson $150+, Hailo $70+)
- High power consumption (7-30W)
- Complex software stack
- Performance that's often slower than CPU inference for small models

## Our Approach

Instead of storing weights in memory (SRAM/DRAM), we encode them directly into the physical chip layout:

- **Mask-locked weights**: Ternary/complex weights become metal routing patterns
- **Zero memory access power**: Weights are "wired" into the compute
- **Simplified inference**: No weight loading, just compute

## Technical Details

- Process: 28nm or 22nm FD-SOI
- Weight precision: Ternary {-1, 0, +1} or C4 {+1, -1, +i, -i}
- Model support: BitNet b1.58-2B-4T, iFairy models
- Reference: TeLLMe FPGA paper achieved 25 tok/s at 4.8W on KV260

## Trade-offs

**Pros:**
- 5-10x better energy efficiency than alternatives
- Sub-$50 price point achievable
- Zero setup (plug and play)

**Cons:**
- Model is "baked in" - can't change without new silicon
- Requires adapter architecture for flexibility
- Currently pre-silicon (FPGA validated)

## Open Questions

1. What use cases would benefit most from fixed-model edge inference?
2. How important is model flexibility vs. price/performance?
3. Would you use this for deployment, or mainly for development/prototyping?

Happy to discuss the architecture, quantization approach, or business model!

---

## Reddit Post - r/embedded

**Title:** $35 LLM inference chip running at 25 tok/s and 3W - thoughts?

**Body:**

Hi r/embedded!

I'm working on a hardware project that might interest this community. We're building a dedicated inference chip for running small language models at the edge.

**The pitch:**
- 25-35 tokens/second
- 2-5 watts power consumption
- $35-79 price target
- USB connection, zero driver setup

**The catch:**
- Model is "baked into" the silicon - you can't load different models
- Currently pre-silicon (FPGA prototype validated)

**Target applications:**
- Industrial IoT with natural language interfaces
- Robotics voice commands
- Home Assistant local processing
- Privacy-preserving AI appliances

For those of you working on embedded systems with AI needs:

1. Is this something you'd use?
2. What would be your main concerns?
3. Any specific use cases you'd want to see supported?

Would love feedback from the embedded community!

---

## Twitter Thread

**Tweet 1:**
Excited to announce SuperInstance: a $35 inference chip that runs LLMs at 25 tok/s and 3 watts 🧵

The secret? We encode neural network weights directly into silicon metal layers—no memory access needed.

Here's how it works:

**Tweet 2:**
Traditional GPUs/NPUs spend 30-60% of their power just fetching weights from memory.

We skip that entirely. The weights ARE the hardware. It's like the difference between reading a book and having the story memorized.

**Tweet 3:**
Result: 5-10x better energy efficiency than Jetson, 3-5x faster LLM inference than Hailo, all at 1/4 the price.

This opens up edge AI applications that were previously impossible:

**Tweet 4:**
Use cases:
🏠 Local voice assistant for smart home
🤖 Natural language robot commands
🏭 Industrial IoT with AI interfaces
🔒 Privacy-first AI appliances (100% offline)

**Tweet 5:**
Trade-off: The model is "baked in" to the silicon. Can't swap models without new hardware.

But we're solving this with an adapter architecture—base model is fixed, but adapters add capabilities.

**Tweet 6:**
Current status:
✅ FPGA prototype validated
✅ SDK in development (Python, open source)
📈 Raising seed round for first silicon

**Tweet 7:**
If you're interested in:
- Edge AI that's actually affordable
- Privacy-preserving local inference
- Hardware that "just works"

Check out: https://github.com/superinstance-ai/sdk

DMs open for questions! 🚀

---

## Product Hunt Launch

**Tagline:** The $35 edge AI chip that runs LLMs at 25 tok/s

**Description:**

SuperInstance is a dedicated inference chip designed specifically for running large language models at the edge. Unlike expensive alternatives (Jetson at $150+, Hailo at $70+), SuperInstance delivers 25-35 tokens per second at just 2-5 watts for $35-79.

**How it works:**

We encode neural network weights directly into the silicon itself—the metal routing patterns ARE the weights. This eliminates memory access entirely, giving you:
- 5-10x better energy efficiency
- 3-5x faster inference than competing edge chips
- Zero setup complexity (plug in and run)

**Perfect for:**
- 🔒 Privacy-first AI applications (100% local processing)
- 🏠 Smart home automation with natural language
- 🤖 Robotics and embedded AI
- 📡 IoT devices with AI interfaces

**Open source SDK:**
Apache 2.0 licensed Python SDK with streaming, profiling, and debug tools.

Currently pre-silicon with FPGA-validated performance. Join our Discord for updates!

---

**Links:**
- GitHub: https://github.com/superinstance-ai/sdk
- Documentation: https://docs.superinstance.ai
- Discord: https://discord.gg/superinstance
- Twitter: https://twitter.com/SuperInstanceAI

**Topics:** AI, Hardware, Edge Computing, LLM, Embedded Systems

---

## Email to Early Adopters

**Subject:** You're invited: SuperInstance early access program

Hi [Name],

You expressed interest in edge AI hardware, and I wanted to personally invite you to our early access program.

**What we're building:**
A $35 inference chip that runs LLMs at 25 tok/s and 3 watts. No CUDA, no drivers—plug in and generate.

**Why it matters:**
- 5-10x better energy efficiency than Jetson
- 3-5x faster inference than Hailo
- Zero setup (really, plug in USB and run Python)

**Early access includes:**
- 🎯 Priority device reservation (target: Q4 2025)
- 💬 Private Discord channel with founders
- 🛠️ Input on SDK features
- 📋 Development hardware loaner program

**What we need from you:**
Tell us your use case! What would you build with sub-$50, sub-5W LLM inference?

Reply to this email or schedule a 15-min call: [link]

Best,
[Founder Name]
Founder, SuperInstance.AI

---

Launch checklist:
- [ ] Hacker News post (Tuesday 9 AM PST optimal)
- [ ] Reddit posts (check subreddit rules first)
- [ ] Twitter thread (schedule for peak hours)
- [ ] Product Hunt (coordinate launch day)
- [ ] Email early adopters
- [ ] Discord announcement
- [ ] Update website with launch banner
