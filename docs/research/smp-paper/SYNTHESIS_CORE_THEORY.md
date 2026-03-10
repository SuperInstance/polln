# SMP Core Theory: What's Actually Under the Hood

**A no-nonsense guide to Seed-Model-Prompt Programming**

---

## What SMP Actually Is

SMP breaks giant AI models into tiny pieces called "tiles" that live in spreadsheet cells. Each tile does one job, tells you how confident it is, and explains its reasoning. You can inspect every decision, fix specific pieces without retraining everything, and prove the whole system works before you ship it.

Think of it like a fishing boat. Traditional AI is one big black box engine—you push the throttle and hope it goes. SMP is a dozen visible gears and pulleys. When one sticks, you see exactly which one and fix it. When you want more speed, you upgrade the transmission gear without touching the steering.

**The breakthrough**: Glass box AI. You can see inside.

---

## The Tile Model: What Makes a Tile

Every tile is five things:

```
T = (I, O, f, c, τ)
```

**In plain English:**

- **I (Input)**: What it takes—like "a sentence" or "a number"
- **O (Output)**: What it spits out—like "sentiment score" or "rounded value"
- **f (function)**: The actual work it does—converts input to output
- **c (confidence)**: How sure it is—from 0.0 (guessing) to 1.0 (certain)
- **τ (trace)**: The explanation—why it made that decision

**Minimum Viable Tile**: A binary decision maker.

```typescript
// Example: Is this email spam?
{
  input: "email text",
  output: "spam | not spam",
  confidence: 0.87,
  trace: "Found 'FREE MONEY' + urgency markers"
}
```

Every tile is:
- **Visible**: You can see what it did
- **Testable**: You can check if it works
- **Fixable**: You can improve it without touching the rest

---

## Confidence Flow: Why Multiplication Matters

Confidence isn't a score—it's currency. It flows through your tile chain.

### Sequential Tiles: Confidence MULTIPLIES

When tiles work in sequence (A → B → C), confidence multiplies:

```
Chain confidence = 0.90 × 0.80 × 0.95 = 0.684
```

**Why multiplication?** Think of it like a pipeline. If pipe A leaks 10% and pipe B leaks 20%, you don't lose 30% total. You lose 10%, then 20% of what's left. Same with confidence.

**The implication**: Long chains naturally degrade confidence. This is a feature, not a bug. It tells you when your pipeline is getting too long.

### Parallel Tiles: Confidence AVERAGES

When tiles work side-by-side, confidence averages:

```
Parallel confidence = (0.90 + 0.80) / 2 = 0.85
```

Weight each tile by how much you trust it.

### The Three-Zone Model

We split confidence into three zones:

| Zone | Range | Action |
|------|-------|--------|
| GREEN | 0.90 - 1.00 | Auto-proceed |
| YELLOW | 0.75 - 0.89 | Human review needed |
| RED | 0.00 - 0.74 | Stop and fix |

**Zone composition is monotonic**: It can only get worse (GREEN → YELLOW → RED), never better. If any tile in your chain goes RED, the whole system stops.

This is like a circuit breaker. When confidence drops, the system automatically knows to involve a human.

---

## The Composition Paradox: Why Safe Tiles Don't Always Compose Safely

Here's the tricky part: Two safe tiles can combine into something unsafe.

### The Counterexample

```
Tile A: Round to 2 decimals (safe for display)
Tile B: Multiply by 100 (safe for currency)

Input: 3.14159

A → B: 3.14159 → 3.14 → 314
B → A: 3.14159 → 314.159 → 314.16

Difference: 0.16
```

Both tiles are individually safe. But composed in different orders, they give different answers. In accounting, that 0.16 discrepancy matters.

### The Solution: Constraint Strengthening

Each tile has constraints—rules about what inputs it accepts.

**The theorem**: When you compose tiles, constraints naturally STRENGTHEN:

```
Constraints(A ; B) ⊆ Constraints(A) ∩ Constraints(B)
```

Each tile can only RESTRICT the valid input space, never expand it.

**What this means**: Safety IS compositional, but only if you track constraints explicitly. You need to know what each tile requires and guarantee the previous tile provides it.

---

## Formal Guarantees: What We Can Prove

Tiles aren't just convenient—they're mathematically rigorous. They form a **category**, which means we can prove things about them.

### 1. Associativity

Order of grouping doesn't matter:

```
(A ; B) ; C = A ; (B ; C)
```

You can group tiles however you want and get the same result.

### 2. Identity

Every type has an "identity tile" that does nothing:

```
id ; A = A = A ; id
```

Like multiplying by 1 or adding 0.

### 3. Distributivity

Parallel and sequential composition play nice:

```
(A ; B) || (C ; D) = (A || C) ; (B || D)
```

This lets us optimize—rearrange tiles for speed without changing behavior.

### 4. Type Safety

If tiles compose without type errors, they'll run without type errors. Guaranteed at compile time.

### 5. Zone Monotonicity

Confidence zones can only degrade, never improve:

```
zone(A ; B) is "worse than or equal to" zone(A) and zone(B)
```

This means the system gets more conservative as complexity increases.

---

## Why This Matters

Traditional AI: "We tested it and it seems to work."

SMP: "We proved it works and here's exactly why."

The difference is trust. Would you rather fly in a plane that was tested a hundred times, or one that was mathematically proven safe?

---

## Quick Reference

### Tile = (I, O, f, c, τ)

- **I**: Input type
- **O**: Output type
- **f**: What it does
- **c**: How confident it is [0, 1]
- **τ**: Why it did it

### Composition Rules

- **Sequential** (A ; B): Output of A feeds into B. Confidence multiplies.
- **Parallel** (A || B): Both run independently. Confidence averages.

### Three Zones

- **GREEN** [0.90, 1.00]: Auto-proceed
- **YELLOW** [0.75, 0.90): Human review
- **RED** [0.00, 0.75): Stop and fix

### Safety

- Safe tiles don't always compose safely
- Track constraints explicitly
- Constraints strengthen during composition

### Formal Guarantees

- Associative: Grouping doesn't matter
- Identity: Do-nothing tiles exist
- Distributive: Parallel and sequential interact predictably
- Type safe: Compile-time guarantees
- Zone monotonic: Confidence degrades with complexity

---

**That's the core. Everything else—stigmergy, memory, cross-modal tiles—builds on these foundations.**

---

*POLLN Research Team | 2026-03-10*
*MIT License | https://github.com/SuperInstance/polln*
