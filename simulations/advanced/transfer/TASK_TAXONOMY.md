# POLLN Task Taxonomy

## Overview

This document provides a comprehensive taxonomy of tasks supported by POLLN's transfer learning system. Tasks are categorized by domain, complexity, required capabilities, and transfer characteristics.

## Task Domains

### 1. Coding Tasks

#### Code Review
- **Description:** Review code for bugs, style issues, and improvements
- **Complexity:** 0.8 (high)
- **Capabilities:** syntax_analysis, pattern_matching, reasoning
- **Architecture:** decoder-only
- **Modalities:** text → text
- **Similar Tasks:** code_generation (0.85), bug_detection (0.75)

#### Code Generation
- **Description:** Generate code from natural language descriptions
- **Complexity:** 0.9 (very high)
- **Capabilities:** syntax_analysis, pattern_matching, generation
- **Architecture:** decoder-only
- **Modalities:** text → text
- **Similar Tasks:** code_review (0.85), bug_detection (0.70)

#### Bug Detection
- **Description:** Identify bugs in code snippets
- **Complexity:** 0.7 (medium-high)
- **Capabilities:** syntax_analysis, pattern_matching, classification
- **Architecture:** decoder-only
- **Modalities:** text → text
- **Similar Tasks:** code_review (0.75), code_generation (0.70)

### 2. NLP Tasks

#### Text Summarization
- **Description:** Generate concise summaries of long documents
- **Complexity:** 0.75 (medium-high)
- **Capabilities:** comprehension, generation, compression
- **Architecture:** encoder-decoder
- **Modalities:** text → text
- **Similar Tasks:** question_answering (0.65), translation (0.60)

#### Question Answering
- **Description:** Answer questions based on given context
- **Complexity:** 0.7 (medium-high)
- **Capabilities:** comprehension, reasoning, retrieval
- **Architecture:** encoder-decoder
- **Modalities:** text → text
- **Similar Tasks:** text_summarization (0.65), retrieval (0.60)

#### Sentiment Analysis
- **Description:** Classify text sentiment (positive/negative/neutral)
- **Complexity:** 0.4 (low-medium)
- **Capabilities:** comprehension, classification
- **Architecture:** encoder-only
- **Modalities:** text → label
- **Similar Tasks:** classification (0.90), text_summarization (0.45)

#### Translation
- **Description:** Translate text between languages
- **Complexity:** 0.7 (medium-high)
- **Capabilities:** comprehension, generation, alignment
- **Architecture:** encoder-decoder
- **Modalities:** text → text
- **Similar Tasks:** text_summarization (0.60), question_answering (0.55)

### 3. Reasoning Tasks

#### Math Word Problems
- **Description:** Solve mathematical word problems
- **Complexity:** 0.85 (high)
- **Capabilities:** comprehension, reasoning, calculation
- **Architecture:** decoder-only
- **Modalities:** text → text
- **Similar Tasks:** question_answering (0.55), reasoning (0.70)

#### Logical Reasoning
- **Description:** Solve logical puzzles and deductions
- **Complexity:** 0.8 (high)
- **Capabilities:** comprehension, reasoning, inference
- **Architecture:** decoder-only
- **Modalities:** text → text
- **Similar Tasks:** math_problems (0.70), question_answering (0.60)

### 4. Retrieval Tasks

#### Document Retrieval
- **Description:** Retrieve relevant documents from a corpus
- **Complexity:** 0.5 (medium)
- **Capabilities:** embedding, similarity, ranking
- **Architecture:** encoder-only
- **Modalities:** text → text
- **Similar Tasks:** question_answering (0.60), semantic_search (0.85)

#### Semantic Search
- **Description:** Find semantically similar documents
- **Complexity:** 0.6 (medium)
- **Capabilities:** embedding, similarity, ranking
- **Architecture:** encoder-only
- **Modalities:** text → text
- **Similar Tasks:** document_retrieval (0.85), question_answering (0.55)

### 5. Classification Tasks

#### Text Classification
- **Description:** Classify text into categories
- **Complexity:** 0.5 (medium)
- **Capabilities:** comprehension, classification
- **Architecture:** encoder-only
- **Modalities:** text → label
- **Similar Tasks:** sentiment_analysis (0.90), topic_classification (0.85)

#### Topic Classification
- **Description:** Classify documents by topic
- **Complexity:** 0.55 (medium)
- **Capabilities:** comprehension, classification, clustering
- **Architecture:** encoder-only
- **Modalities:** text → label
- **Similar Tasks:** text_classification (0.85), sentiment_analysis (0.75)

## Transfer Characteristics

### High Transferability (Similarity > 0.8)

Tasks within the same domain with significant overlap:

| Source Task | Target Task | Similarity | Expected Benefit |
|-------------|-------------|------------|------------------|
| code_review | code_generation | 0.85 | 5x speedup, 15% gain |
| code_review | bug_detection | 0.75 | 3x speedup, 10% gain |
| sentiment_analysis | text_classification | 0.90 | 5x speedup, 18% gain |
| document_retrieval | semantic_search | 0.85 | 5x speedup, 15% gain |
| translation_en_fr | translation_en_es | 0.95 | 6x speedup, 20% gain |

**Recommended Strategy:** LoRA (rank=8, 10 epochs, LR=0.001)

### Medium Transferability (Similarity 0.5-0.8)

Related tasks with partial overlap:

| Source Task | Target Task | Similarity | Expected Benefit |
|-------------|-------------|------------|------------------|
| text_summarization | question_answering | 0.65 | 2.5x speedup, 8% gain |
| math_problems | logical_reasoning | 0.70 | 3x speedup, 10% gain |
| question_answering | document_retrieval | 0.60 | 2x speedup, 6% gain |
| code_generation | code_review | 0.85 | 5x speedup, 15% gain |

**Recommended Strategy:** Full fine-tuning (frozen embeddings, 50 epochs, LR=0.0001)

### Low Transferability (Similarity 0.3-0.5)

Different domains with limited overlap:

| Source Task | Target Task | Similarity | Expected Benefit |
|-------------|-------------|------------|------------------|
| code_review | sentiment_analysis | 0.35 | 1.2x speedup, 2% gain |
| translation | math_problems | 0.30 | 1.1x speedup, 1% gain |
| retrieval | generation | 0.40 | 1.3x speedup, 3% gain |

**Recommended Strategy:** Selective fine-tuning (100 epochs, LR=0.0005)

### Not Recommended (Similarity < 0.3)

Very different tasks - train from scratch:

| Source Task | Target Task | Similarity | Recommendation |
|-------------|-------------|------------|----------------|
| sentiment_analysis | code_generation | 0.25 | Train from scratch |
| math_problems | translation | 0.20 | Train from scratch |
| retrieval | reasoning | 0.28 | Train from scratch |

**Recommendation:** Do not transfer (negative transfer risk >30%)

## Capability Clusters

### Cluster 1: Code & Syntax
- **Tasks:** code_review, code_generation, bug_detection
- **Core Capabilities:** syntax_analysis, pattern_matching
- **Transfer Potential:** Very high (>0.7)
- **Best Strategy:** LoRA

### Cluster 2: Language Understanding
- **Tasks:** text_summarization, question_answering, translation
- **Core Capabilities:** comprehension, reasoning
- **Transfer Potential:** High (0.5-0.7)
- **Best Strategy:** Full fine-tuning

### Cluster 3: Classification
- **Tasks:** sentiment_analysis, text_classification, topic_classification
- **Core Capabilities:** comprehension, classification
- **Transfer Potential:** Very high (>0.8)
- **Best Strategy:** LoRA

### Cluster 4: Reasoning
- **Tasks:** math_problems, logical_reasoning
- **Core Capabilities:** reasoning, calculation
- **Transfer Potential:** Medium (0.5-0.7)
- **Best Strategy:** Full fine-tuning

### Cluster 5: Retrieval
- **Tasks:** document_retrieval, semantic_search
- **Core Capabilities:** embedding, similarity
- **Transfer Potential:** Very high (>0.8)
- **Best Strategy:** LoRA

## Architecture Compatibility

### Decoder-Only Models
**Best for:** Generation, reasoning tasks
- code_review, code_generation, bug_detection
- math_problems, logical_reasoning
- text_summarization

**Transfer within architecture:** Very high (>0.7)

### Encoder-Decoder Models
**Best for:** Translation, complex NLP
- translation (all language pairs)
- text_summarization
- question_answering

**Transfer within architecture:** High (0.5-0.7)

### Encoder-Only Models
**Best for:** Classification, retrieval
- sentiment_analysis, text_classification
- document_retrieval, semantic_search

**Transfer within architecture:** Very high (>0.8)

### Cross-Architecture Transfer
**Generally low (<0.4):**
- decoder-only → encoder-only: 0.3-0.4
- encoder-only → decoder-only: 0.3-0.4
- encoder-decoder ↔ others: 0.35-0.45

## Modality Compatibility

### Same Modality (text → text)
**Transfer potential:** High (0.5-0.9)
- All coding tasks
- All NLP tasks
- All reasoning tasks

### Cross-Modality
**Transfer potential:** Low (<0.4)
- text → image: 0.2-0.3
- text → audio: 0.25-0.35
- image → text: 0.3-0.4

## Complexity Transfer

### Similar Complexity (diff < 0.2)
**Transfer potential:** High (0.6-0.9)
- Simple classification → Simple classification
- Medium reasoning → Medium reasoning

### Increasing Complexity
**Transfer potential:** Medium (0.4-0.6)
- Simple classification → Medium classification
- Medium reasoning → Complex reasoning

### Large Complexity Gap (diff > 0.4)
**Transfer potential:** Low (<0.4)
- Simple classification → Complex reasoning
- Medium retrieval → Complex generation

## Data Requirements

### Low Data (<10K examples)
**Best for:** Simple classification, retrieval
- sentiment_analysis
- document_retrieval
- text_classification

**Transfer benefit:** High (3-5x speedup)

### Medium Data (10K-100K examples)
**Best for:** Most NLP tasks
- text_summarization
- question_answering
- code_review

**Transfer benefit:** Medium (2-3x speedup)

### High Data (>100K examples)
**Best for:** Complex generation, translation
- code_generation
- translation
- math_problems

**Transfer benefit:** Low-Medium (1.5-2x speedup)

## Practical Guidelines

### Choosing Source Tasks

1. **Same domain preferred:** Choose source task in same domain
2. **Higher performance:** Source should outperform target baseline
3. **More data:** Source should have more training data
4. **Similar complexity:** Avoid large complexity gaps

### Sequence of Transfers

For best results, chain transfers by similarity:

```
Step 1: sentiment_analysis → text_classification (0.90 similarity)
Step 2: text_classification → topic_classification (0.85 similarity)
Step 3: topic_classification → document_retrieval (0.60 similarity)
```

### Multi-Source Transfer

Combine knowledge from multiple sources:

```
Target: code_generation
Sources:
  - code_review (0.85 similarity, 40% weight)
  - bug_detection (0.70 similarity, 35% weight)
  - text_summarization (0.45 similarity, 25% weight)
```

**Recommendation:** Weight by similarity × performance

## Task Templates

### Adding New Tasks

When adding new tasks to the taxonomy:

1. **Define characteristics:**
   - Domain, complexity, capabilities
   - Architecture, modalities
   - Data requirements

2. **Compute similarities:**
   - To tasks in same domain
   - To tasks with similar capabilities
   - To tasks with same architecture

3. **Determine transfer strategy:**
   - High similarity (>0.8): LoRA
   - Medium similarity (0.5-0.8): Full fine-tuning
   - Low similarity (0.3-0.5): Selective
   - Very low (<0.3): From scratch

4. **Validate empirically:**
   - Test transfer on held-out set
   - Monitor for negative transfer
   - Measure forgetting

### Example Task Definition

```typescript
const newTask = {
  id: 'code_optimization',
  name: 'Code Optimization',
  domain: 'coding',
  description: 'Optimize code for performance',
  required_capabilities: ['syntax_analysis', 'pattern_matching', 'reasoning'],
  architecture_pattern: 'decoder-only',
  input_modality: 'text',
  output_modality: 'text',
  complexity_score: 0.85,
  data_requirements: {
    dataset_size: 50000,
    diversity: 0.8
  }
};

// Find similar tasks
const similarTasks = findSimilarTasks(newTask, threshold=0.5);

// Best source: code_review (0.82 similarity)
// Recommended: LoRA transfer
```

---

**Last Updated:** 2026-03-07
**Version:** 1.0.0
