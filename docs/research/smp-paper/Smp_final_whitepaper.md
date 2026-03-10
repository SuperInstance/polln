# Seed-Model-Prompt Programming: LLMs to Swarms, SMPbots Peek on Schrödinger's Cat

**A White Paper on Deconstructing LLMs into inspectable, trainable spreadsheet components**

---

## Quick Summary

SMP (Seed + Model + Prompt) Programming breaks giant AI models into tiny pieces that live in spreadsheet cells. Each piece is visible, improvable, and can learn on its own. It's like taking apart a Swiss watch to see exactly how each gear works—then putting it back together better than before.

**The breakthrough**: You can see inside the black box. It glass box.

---

## Table of Contents

1. [The Hook](#chapter-1-the-hook) - Why this matters NOW
2. [The SMP Idea](#chapter-2-the-idea) - What it is and how it works
3. [The Breakthroughs](#chapter-3-breakthroughs) - What you can do now
4. [How It Works](#chapter-4-how-it-works) - Under the hood
5. [Examples](#chapter-5-examples) - Real-world scenarios
6. [The Science](#chapter-6-science) - Why it works
7. [Future Directions](#chapter-7-future) - Where it's going
8. [Appendix: Technical Details](#appendix-technical-details)

---

## Chapter 1: The Hook

<!-- INCLUDE: chapter-1-the-hook.md -->
## The Fifty Years of Building Mystery Boxes

<!-- INCLUDE: chapter-2-the-idea.md -->
## The The Breakthroughs

<!-- INCLUDE: chapter-3-breakthroughs.md -->
##   How It works

<!-- INCLUDE: chapter-4-how-it-works.md -->
##   Examples

<!-- INCLUDE: chapter-5-examples.md -->
##   The Science

<!-- INCLUDE: chapter-6-science.md -->
##   Future Directions

<!-- INCLUDE: chapter-7-future.md -->

---

## Appendix A: Technical Details

### The Tile Architecture

**Minimum Viable Tile (MVT)**:
- Discriminates: Binary decision
- Inspectable: Shows reasoning trace
- Trainable: Learns from examples
- Composable: Well-defined I/O schema

### Key Theorems

1. **Universal Approximation**: Any LLM can be approximated by tile composition
2. **Observability-Improvement Bound**: Tile changes have bounded impact
3. **SSTL Convergence**: Tiles converge to teacher performance

### Implementation Status
- Core POLLN: 821+ tests passing
- KV-Cache System: Complete
- GPU/CPU routing: Validated
- Spreadsheet UI: In development

---

## Get Started

```
# Install
npm install

# Run examples
npm run smp-examples

# Build a tile
npm run build-tile --name my-analyzer --data A1:A100
```

---

**Paper Version**: 1.0
**Last Updated**: 2026-03-09
**Authors**: POLLN Research Team
**Repository**: https://github.com/SuperInstance/polln
**License**: MIT
