# Translation Quality Standards
## Ensuring Accuracy, Consistency, and Cultural Authenticity

**Applicable to:** All language specialist agents
**Reference:** `LANGUAGE_SPECIALIST_ONBOARDING.md`
**Last Updated:** 2026-03-13

---

## 🎯 Quality Dimensions

### 1. Mathematical Accuracy (Non-negotiable)
- **Equations & proofs:** 100% faithful to original
- **Variable names:** Preserved exactly
- **Mathematical notation:** LaTeX unchanged
- **Logical structure:** Preserved even if sentence structure changes

### 2. Conceptual Fidelity
- **Core ideas:** Faithfully conveyed
- **Theoretical framework:** Maintained
- **Pedagogical intent:** Preserved
- **Abstract concepts:** Accurately rendered

### 3. Linguistic Quality
- **Native fluency:** Reads like original academic writing
- **Grammar & syntax:** Flawless in target language
- **Academic style:** Appropriate for target language academia
- **Readability:** Clear and accessible to target audience

### 4. Cultural Adaptation
- **Examples & metaphors:** Culturally appropriate
- **Historical references:** Contextualized for target culture
- **Academic conventions:** Follow target language standards
- **Cultural sensitivity:** Respectful and appropriate

### 5. Consistency
- **Terminology:** Consistent across all papers
- **Style:** Uniform within and across translations
- **Notation:** Consistent with mathematical standards
- **Formatting:** Follows repository conventions

---

## 📋 Quality Checklist

### Pre-Translation
- [ ] **Source analysis:** Understand paper's mathematical content
- [ ] **Terminology research:** Check existing translations of key terms
- [ ] **Cultural assessment:** Identify adaptation needs
- [ ] **Style planning:** Decide on academic register

### During Translation
- [ ] **Mathematical verification:** Each equation checked
- [ ] **Terminology consistency:** Use established terms
- [ ] **Cultural adaptation:** Examples replaced appropriately
- [ ] **Readability check:** Native speaker would understand

### Post-Translation
- [ ] **Self-review:** Read entire translation for flow
- [ ] **Mathematical audit:** Verify all equations
- [ ] **Terminology audit:** Check consistency
- [ ] **Cultural review:** Ensure adaptations work

### Documentation
- [ ] **Translation notes:** All decisions documented
- [ ] **Research notes:** Language-specific insights recorded
- [ ] **Quality self-assessment:** Score against metrics
- [ ] **A2A preparation:** Insights ready for synthesis

---

## 🧮 Mathematical Accuracy Standards

### Equation Preservation
```
Original: $E = mc^2$
✅ Correct: $E = mc^2$
❌ Incorrect: $E = m \times c^2$ (changed notation)
❌ Incorrect: Energy equals mass times speed of light squared (verbalized)
```

### Proof Structure
- **Step-by-step preservation:** Each logical step maintained
- **Theorem statements:** Exactly equivalent
- **Lemma references:** Preserved with correct numbering
- **Mathematical symbols:** Unicode/LaTeX preserved exactly

### Variable Naming
- **Single-letter variables:** Preserved (x, y, z, etc.)
- **Greek letters:** Preserved (α, β, γ, etc.)
- **Subscripts/superscripts:** Preserved exactly
- **Special notation:** Preserved (vectors, matrices, etc.)

---

## 🌐 Cultural Adaptation Guidelines

### When to Adapt Examples
```
✅ ADAPT:
- Culture-specific references (American sports, local landmarks)
- Historical examples unknown in target culture
- Pop culture references
- Education system examples

✅ PRESERVE:
- Universal mathematical examples (prime numbers, geometry)
- Historical mathematical figures (Euclid, Newton)
- Standard scientific examples (planetary motion, chemical reactions)
```

### Adaptation Methodology
1. **Identify core pedagogical purpose** of example
2. **Find culturally equivalent example** in target culture
3. **Ensure mathematical validity** is preserved
4. **Document adaptation** in translation notes
5. **Maintain similar complexity level**

### Sensitive Topics
- **Religion:** Neutral or omit if potentially problematic
- **Politics:** Avoid contemporary political references
- **Historical conflicts:** Handle with extreme care
- **Cultural stereotypes:** Avoid entirely

---

## 📚 Terminology Management

### Existing Terminology
1. **Research first:** Check if term already has accepted translation
2. **Academic consensus:** Use most common academic translation
3. **Field-specific:** Consider mathematical vs. general usage
4. **Historical usage:** Respect established translations

### New Terminology Creation
When no existing translation:
1. **Literal translation:** If works mathematically and linguistically
2. **Descriptive translation:** Explain concept in target language
3. **Loanword:** Use English term with explanation
4. **New coinage:** Create new term with clear definition

### Terminology Database
- **Maintain shared file:** `terminology_[language].md`
- **Cross-reference:** Link to other language terminology
- **Update regularly:** As new terms are created
- **Community review:** Open for other agents to suggest improvements

---

## 🔍 Quality Assessment Metrics

### Quantitative Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Mathematical errors** | 0 | Manual review of equations |
| **Terminology consistency** | 95%+ | Term usage across paper |
| **Readability score** | 4/5+ | Self-assessment |
| **Cultural appropriateness** | 5/5 | Cultural review checklist |
| **A2A insights** | 2+ per paper | Count of novel insights |

### Qualitative Assessment
1. **Would a native academic understand?** Yes/No/With difficulty
2. **Does it feel like original research?** Yes/No/Somewhat
3. **Cultural authenticity?** Authentic/Forced/Inappropriate
4. **Mathematical clarity?** Clear/Confusing/Ambiguous

### Peer Review Process
1. **Self-assessment** using checklist
2. **Cross-language review** by another language specialist
3. **Mathematical verification** by A2A synthesis agent
4. **Final approval** by orchestrator

---

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Over-literalism
```
Problem: Word-for-word translation that loses meaning
Solution: Translate meaning, not words. Focus on conceptual equivalence.
```

### Pitfall 2: Cultural Blindness
```
Problem: Keeping culture-specific examples that don't work
Solution: Research target culture, find equivalent examples.
```

### Pitfall 3: Inconsistent Terminology
```
Problem: Using different terms for same concept
Solution: Maintain terminology database, review consistently.
```

### Pitfall 4: Mathematical Corruption
```
Problem: Accidentally changing equations or proofs
Solution: Triple-check all mathematics, use LaTeX preservation.
```

### Pitfall 5: Academic Style Mismatch
```
Problem: Wrong register for target language academia
Solution: Study target language academic papers, emulate style.
```

---

## 📝 Documentation Requirements

### Translation Notes Must Include
1. **Key terminology decisions** with rationale
2. **Cultural adaptations** made and why
3. **Challenges encountered** and solutions
4. **Alternative translations considered**
5. **Areas needing review** or uncertain

### Quality Self-Assessment Report
```
# Quality Self-Assessment: P[N] - [Language]
**Translator:** [Agent ID]
**Date:** YYYY-MM-DD

## Accuracy Assessment
- Mathematical correctness: [1-5]
- Conceptual fidelity: [1-5]
- Terminology consistency: [1-5]

## Readability Assessment
- Native fluency: [1-5]
- Academic style: [1-5]
- Clarity: [1-5]

## Cultural Assessment
- Example appropriateness: [1-5]
- Cultural sensitivity: [1-5]
- Adaptation quality: [1-5]

## Overall Score: [X]/[Y]
**Areas for improvement:** [List]
**Ready for A2A synthesis:** Yes/No
```

---

## 🔄 Continuous Improvement

### Feedback Loop
1. **A2A synthesis feedback:** Insights from cross-language discussion
2. **Peer review feedback:** From other language specialists
3. **Orchestrator feedback:** Quality assessment
4. **Self-reflection:** After completion of each paper

### Quality Tracking
- **Maintain quality metrics** over time
- **Identify patterns** in errors or challenges
- **Share best practices** across language teams
- **Update standards** based on experience

### Community Review
- **Regular cross-language review sessions**
- **Terminology harmonization meetings**
- **Cultural adaptation workshops**
- **Quality calibration exercises**

---

## 🏆 Excellence Recognition

### Quality Tiers
- **Bronze:** Meets all accuracy standards
- **Silver:** Bronze + excellent readability
- **Gold:** Silver + exceptional cultural adaptation
- **Platinum:** Gold + breakthrough insights for A2A

### Recognition Criteria
- **Mathematical perfection:** Zero errors
- **Linguistic excellence:** Native-level writing
- **Cultural mastery:** Authentic adaptation
- **Innovative insights:** Contributions to A2A synthesis

### Continuous Learning
- **Study exemplary translations**
- **Participate in review processes**
- **Share challenges and solutions**
- **Contribute to terminology development**

---

*"Quality is never an accident; it is always the result of intelligent effort." - John Ruskin*
*Our intelligent effort ensures mathematical truth transcends language barriers.*

**Reference:** Use these standards for all translations, update based on experience.