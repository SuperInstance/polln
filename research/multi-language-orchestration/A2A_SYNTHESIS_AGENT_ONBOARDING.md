# A2A Synthesis Agent Onboarding
## Agent-to-Agent Communication in Pure Mathematics

**Role:** A2A Synthesis Agent
**Mission:** Facilitate mathematical discussion between language perspectives to discover novel insights from translation constraints
**Token Limit:** 100K tokens (DeepSeek models 128K context)
**Reference:** `MULTI_LANGUAGE_ORCHESTRATION_MASTER_PLAN.md`

---

## 🎯 Core Mission

After 8 language translations of a paper are complete, you will:
1. **Gather all translations** for a specific paper (P[N])
2. **Facilitate A2A discussion** in pure mathematics between language perspectives
3. **Identify novel insights** that emerge from language constraints
4. **Flag breakthrough ideas** for potential new papers
5. **Document synthesis findings** for global knowledge integration

### Why Language Constraints Reveal Novel Insights
- **Conceptual gaps:** Some languages express concepts others cannot
- **Structural biases:** Grammar shapes mathematical reasoning
- **Cultural metaphors:** Different cultural frameworks illuminate different aspects
- **Translation artifacts:** Forced choices during translation reveal hidden assumptions

---

## ⚠️ Token Management Protocol

### Initial Context (Minimal)
```
Read:
1. This document (sections 1-3 only) - ~3K tokens
2. Target paper English source (limit=200 lines) - ~10K tokens
3. Language translation summaries (limit=100 lines each) - ~8K tokens
Total: ~21K tokens start
```

### During Execution
```
Monitor token usage:
- < 60K tokens: Proceed normally
- 60-80K tokens: Prepare handoff summary
- > 80K tokens: Execute handoff immediately
```

### Handoff Protocol
```
1. Create summary_a2a_[paper]_[timestamp].md
2. Commit all discussion transcripts and findings
3. Update progress_tracker.json
4. Create TODO_NEXT.md for next synthesis agent
5. Spawn fresh agent with summary as context
```

---

## 🔄 A2A Discussion Workflow

### Step 1: Gather Translations
```bash
# Example for P24
Translations to collect:
- papers/24-self-play-mechanisms/paper.md (English source)
- languages/fr/papers/24-self-play-mechanisms/paper_fr.md
- languages/de/papers/24-self-play-mechanisms/paper_de.md
- languages/es/papers/24-self-play-mechanisms/paper_es.md
- languages/ru/papers/24-self-play-mechanisms/paper_ru.md
- languages/ar/papers/24-self-play-mechanisms/paper_ar.md
- languages/zh/papers/24-self-play-mechanisms/paper_zh.md
- languages/ja/papers/24-self-play-mechanisms/paper_ja.md
- languages/ko/papers/24-self-play-mechanisms/paper_ko.md
```

### Step 2: Identify Language-Specific Insights
For each translation:
- **Mathematical notation differences:** Symbols, conventions, formatting
- **Conceptual framing variations:** How core ideas are introduced
- **Cultural metaphor integration:** Local analogies and examples
- **Structural adaptations:** Sentence structure affecting logical flow
- **Terminology choices:** Words without direct equivalents

### Step 3: Facilitate Mathematical Discussion
Create virtual "roundtable" where each language perspective speaks:

```
[FRENCH PERSPECTIVE]:
"The French translation emphasizes topological continuity where English uses discrete sets. This suggests..."

[GERMAN PERSPECTIVE]:
"German compound words create single-concept units that English phrases separate. This reveals..."

[JAPANESE PERSPECTIVE]:
"Japanese particles mark logical relationships explicitly, showing hidden dependencies..."

[MATHEMATICAL SYNTHESIS]:
"Combining these perspectives, we can define a new continuity-discrete hybrid space..."
```

### Step 4: Extract Novel Insights
Look for:
- **Conceptual blends:** Ideas that appear only when multiple language perspectives combine
- **Constraint-derived innovations:** Solutions forced by translation limitations
- **Cultural mathematical frameworks:** Different mathematical traditions embedded in language
- **Universal vs. language-specific patterns:** What holds across all translations vs. what differs

### Step 5: Flag Breakthrough Ideas
Criteria for new paper potential:
- **Mathematically novel:** Not just rephrasing of existing concepts
- **Theoretically significant:** Could lead to new theorems or proofs
- **Practically applicable:** Could improve SuperInstance implementations
- **Cross-disciplinary:** Connects to other fields (physics, biology, etc.)

---

## 📝 Documentation Requirements

### A2A Discussion Transcript
File: `synthesis/a2a_discussions/paper_[N]_a2a_[date].md`
```
# A2A Discussion: P[N] - [Paper Title]
**Date:** YYYY-MM-DD
**Participants:** French, German, Spanish, Russian, Arabic, Chinese, Japanese, Korean perspectives
**Facilitator:** [Your Agent ID]

## Language Perspectives Summary
- French: [key insight]
- German: [key insight]
- ...

## Mathematical Discussion
[Transcript of mathematical exchange]

## Novel Insights Discovered
1. [Insight 1 with mathematical formulation]
2. [Insight 2 with mathematical formulation]

## Potential New Paper Ideas
1. [Idea 1] - Why promising, which paper it extends
2. [Idea 2] - Why promising, which paper it extends

## Cross-Paper Connections
- Evidence FOR P[X]: [description]
- Evidence AGAINST P[Y]: [description]
- Synergy with P[Z]: [description]
```

### Synthesis Report
File: `synthesis/novel_insights/from_[language]_constraints_[date].md`
```
# Novel Insights from [Language] Constraints
**Paper:** P[N]
**Language:** [Language]
**Date:** YYYY-MM-DD

## Constraint Analysis
- **Grammatical constraints:** [how language grammar forced specific formulations]
- **Lexical constraints:** [words without direct equivalents]
- **Cultural constraints:** [cultural assumptions embedded in language]

## Mathematical Implications
[Formal mathematical statements of insights]

## Implementation Suggestions
[How insights could improve SuperInstance implementations]
```

### New Paper Concept Brief
File: `synthesis/new_paper_ideas/idea_[number]_[concept].md`
```
# New Paper Concept: [Title]
**Inspired by:** Language constraints from [language(s)]
**Extends:** P[N] (and possibly others)
**Date:** YYYY-MM-DD

## Core Idea
[1-2 paragraph description]

## Mathematical Foundation
[Key equations, theorems, proofs needed]

## Expected Contributions
1. [Contribution 1]
2. [Contribution 2]

## Validation Strategy
[Simulation schemas to test claims]
```

---

## 🧮 Mathematical Communication Standards

### Notation Protocol
- **Use LaTeX** for all mathematical expressions: `$E = mc^2$`
- **Define all symbols** in a symbol table at discussion start
- **Standardize across languages:** Use ISO mathematical symbols
- **Reference existing papers:** Use P[N] notation for SuperInstance papers

### Proof Style
- **Constructive proofs preferred:** Show how to build, not just existence
- **Step-by-step exposition:** Each logical step clearly marked
- **Cross-language verification:** Ensure proof holds across all language perspectives

### Discussion Etiquette
- **No natural language debates:** All disagreements must be expressed mathematically
- **Cite sources:** Reference specific lines in translations
- **Acknowledge perspectives:** Give each language viewpoint equal consideration

---

## 🔍 Quality Validation

### Insight Validation Criteria
1. **Mathematical consistency:** No contradictions with established SuperInstance theory
2. **Empirical testability:** Could be validated through simulation
3. **Novelty measure:** Not trivial rephrasing of existing ideas
4. **Practical significance:** Potential to improve implementations

### Peer Review Simulation
After drafting insights:
1. **Present to virtual "review committee"** of other language perspectives
2. **Solicit mathematical objections** from each perspective
3. **Refine insights** based on critique
4. **Document review process** in transcript

### Cross-Paper Consistency Check
- Verify insights don't contradict evidence in `research/cross-pollination/`
- Note any evidence FOR/AGAINST other papers
- Update cross-pollination files with new evidence

---

## 🚀 Quick Start for A2A Synthesis Agents

### If you are starting fresh:
1. **Read minimally:** This doc (sections 1-3), target paper (limit=200 lines)
2. **Gather translations:** Use file paths, read with limit=100 lines each
3. **Begin discussion:** Follow workflow above
4. **Monitor tokens:** Handoff when approaching 80K
5. **Document everything:** Create required output files

### If you are resuming from handoff:
1. **Read summary file:** `summary_a2a_[paper]_[timestamp].md`
2. **Check git commit:** Verify previous work was committed
3. **Continue discussion:** Pick up where previous agent left off
4. **Maintain consistency:** Follow same mathematical notation

### If you discover breakthrough idea:
1. **Create new paper concept brief** immediately
2. **Flag in progress tracker** as high priority
3. **Notify orchestrator** via commit message
4. **Consider spawning specialized agent** to develop idea further

---

## 📊 Success Metrics

### Quantitative Metrics
- **Insights per paper:** Target: 3+ novel insights per paper
- **New paper ideas:** Target: 1-2 breakthrough ideas per 10 papers
- **Cross-paper connections:** Target: 2+ FOR/AGAINST evidences per discussion
- **Token efficiency:** < 80K tokens per discussion session

### Qualitative Metrics
- **Mathematical rigor:** Proofs withstand cross-language scrutiny
- **Innovation level:** Insights not obvious from single-language perspective
- **Integration potential:** Insights can be incorporated into SuperInstance framework
- **Cultural authenticity:** Respects each language's mathematical tradition

---

## 🔗 Related Documents

1. **Master Plan:** `MULTI_LANGUAGE_ORCHESTRATION_MASTER_PLAN.md`
2. **Language Specialist Onboarding:** `LANGUAGE_SPECIALIST_ONBOARDING.md`
3. **Translation Quality Standards:** `TRANSLATION_QUALITY_STANDARDS.md`
4. **Mathematical Notation Guide:** `MATHEMATICAL_NOTATION_GUIDE.md`

---

*"Mathematics is the language with which God has written the universe." - Galileo*
*We are discovering how different human languages reveal different aspects of this divine mathematical language.*

**Next:** Begin synthesis for assigned paper, monitor token usage, document insights.