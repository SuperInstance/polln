/**
 * Sentiment Analysis Tile
 *
 * Example tile demonstrating the SMP tile interface:
 * - Discriminates: Classifies text sentiment (positive/negative/neutral)
 * - Confidence: Reports certainty based on text clarity
 * - Trace: Explains which words influenced the decision
 *
 * This is a reference implementation for building production tiles.
 */

import { Tile, Schema, Schemas, TileResult } from '../core/Tile';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Sentiment classification
 */
export type SentimentLabel = 'positive' | 'negative' | 'neutral';

/**
 * Sentiment analysis result
 */
export interface Sentiment {
  label: SentimentLabel;
  score: number; // -1.0 to 1.0
  confidence: number; // 0.0 to 1.0
  keywords: string[];
}

/**
 * Sentiment tile configuration
 */
export interface SentimentTileConfig {
  /** Minimum confidence to classify (default: 0.5) */
  minConfidence?: number;
  /** Include keyword extraction (default: true) */
  extractKeywords?: boolean;
  /** Custom positive words */
  positiveWords?: string[];
  /** Custom negative words */
  negativeWords?: string[];
}

// ============================================================================
// SENTIMENT TILE IMPLEMENTATION
// ============================================================================

/**
 * SentimentTile - Analyzes text sentiment
 *
 * A concrete tile implementation demonstrating:
 * - Lexicon-based sentiment analysis
 * - Confidence calculation from text clarity
 * - Keyword extraction for traceability
 *
 * @example
 * ```typescript
 * const sentimentTile = new SentimentTile({
 *   minConfidence: 0.6,
 *   extractKeywords: true,
 * });
 *
 * const result = await sentimentTile.execute("I absolutely love this product!");
 * // result.output = { label: 'positive', score: 0.85, confidence: 0.92, keywords: ['love', 'absolutely'] }
 * // result.zone = 'GREEN'
 * // result.trace = "Strong positive signals: 'love', 'absolutely'. No negative signals detected."
 * ```
 */
export class SentimentTile extends Tile<string, Sentiment> {
  private readonly config: Required<SentimentTileConfig>;

  // Default lexicons
  private static readonly DEFAULT_POSITIVE = [
    'love', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
    'awesome', 'outstanding', 'perfect', 'best', 'good', 'nice',
    'happy', 'pleased', 'satisfied', 'brilliant', 'superb', 'delightful',
    'absolutely', 'incredible', 'magnificent', 'terrific', 'positive',
  ];

  private static readonly DEFAULT_NEGATIVE = [
    'hate', 'terrible', 'awful', 'horrible', 'bad', 'worst', 'poor',
    'disappointing', 'frustrated', 'angry', 'sad', 'unhappy', 'disgusted',
    'annoying', 'dreadful', 'pathetic', 'useless', 'broken', 'negative',
    'never', 'waste', 'regret', 'horrible', 'disaster',
  ];

  private static readonly INTENSIFIERS = [
    'very', 'extremely', 'absolutely', 'completely', 'totally',
    'really', 'quite', 'rather', 'incredibly', 'exceptionally',
  ];

  private static readonly NEGATORS = [
    'not', "n't", 'never', 'no', 'none', 'neither', 'nobody', 'nothing',
  ];

  private readonly positiveWords: Set<string>;
  private readonly negativeWords: Set<string>;

  constructor(config: SentimentTileConfig = {}) {
    super(
      Schemas.string,
      {
        type: 'Sentiment',
        description: 'Sentiment analysis result',
        validate: (v: unknown): v is Sentiment => {
          if (typeof v !== 'object' || v === null) return false;
          const s = v as Sentiment;
          return (
            ['positive', 'negative', 'neutral'].includes(s.label) &&
            typeof s.score === 'number' &&
            typeof s.confidence === 'number' &&
            Array.isArray(s.keywords)
          );
        },
      },
      { id: config.minConfidence ? undefined : 'sentiment-tile' }
    );

    this.config = {
      minConfidence: config.minConfidence ?? 0.5,
      extractKeywords: config.extractKeywords ?? true,
      positiveWords: config.positiveWords ?? SentimentTile.DEFAULT_POSITIVE,
      negativeWords: config.negativeWords ?? SentimentTile.DEFAULT_NEGATIVE,
    };

    this.positiveWords = new Set(this.config.positiveWords);
    this.negativeWords = new Set(this.config.negativeWords);
  }

  /**
   * Discriminate: Analyze sentiment of input text
   */
  async discriminate(input: string): Promise<Sentiment> {
    const tokens = this.tokenize(input);
    const analysis = this.analyzeTokens(tokens);

    let label: SentimentLabel;
    if (analysis.score > 0.1) {
      label = 'positive';
    } else if (analysis.score < -0.1) {
      label = 'negative';
    } else {
      label = 'neutral';
    }

    return {
      label,
      score: analysis.score,
      confidence: analysis.confidence,
      keywords: analysis.keywords,
    };
  }

  /**
   * Confidence: Calculate certainty based on signal strength
   */
  async confidence(input: string): Promise<number> {
    const tokens = this.tokenize(input);
    const analysis = this.analyzeTokens(tokens);
    return analysis.confidence;
  }

  /**
   * Trace: Explain the sentiment decision
   */
  async trace(input: string): Promise<string> {
    const tokens = this.tokenize(input);
    const analysis = this.analyzeTokens(tokens);

    const parts: string[] = [];

    if (analysis.positiveCount > 0) {
      const words = analysis.keywords.filter(k =>
        this.positiveWords.has(k.toLowerCase())
      );
      parts.push(`Positive signals: ${words.map(w => `'${w}'`).join(', ')}`);
    }

    if (analysis.negativeCount > 0) {
      const words = analysis.keywords.filter(k =>
        this.negativeWords.has(k.toLowerCase())
      );
      parts.push(`Negative signals: ${words.map(w => `'${w}'`).join(', ')}`);
    }

    if (analysis.negationCount > 0) {
      parts.push(`Negations detected: ${analysis.negationCount}`);
    }

    if (analysis.intensifierCount > 0) {
      parts.push(`Intensifiers detected: ${analysis.intensifierCount}`);
    }

    if (parts.length === 0) {
      return 'No clear sentiment signals detected. Classified as neutral.';
    }

    const labelStr = analysis.score > 0.1 ? 'positive' :
                     analysis.score < -0.1 ? 'negative' : 'neutral';

    return `${parts.join('. ')}. Final classification: ${labelStr} (confidence: ${analysis.confidence.toFixed(2)})`;
  }

  // Private helpers

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\s']/g, ' ')
      .split(/\s+/)
      .filter(t => t.length > 0);
  }

  private analyzeTokens(tokens: string[]): {
    score: number;
    confidence: number;
    keywords: string[];
    positiveCount: number;
    negativeCount: number;
    negationCount: number;
    intensifierCount: number;
  } {
    let score = 0;
    let signalStrength = 0;
    const keywords: string[] = [];
    let positiveCount = 0;
    let negativeCount = 0;
    let negationCount = 0;
    let intensifierCount = 0;

    let negated = false;
    let intensified = 1;

    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i];
      const lowerToken = token.toLowerCase();

      // Check for negation
      if (SentimentTile.NEGATORS.includes(lowerToken)) {
        negated = true;
        negationCount++;
        continue;
      }

      // Check for intensifier
      if (SentimentTile.INTENSIFIERS.includes(lowerToken)) {
        intensified = 1.5;
        intensifierCount++;
        continue;
      }

      // Check sentiment words
      let wordScore = 0;
      if (this.positiveWords.has(lowerToken)) {
        wordScore = 0.5;
        positiveCount++;
        if (this.config.extractKeywords) keywords.push(token);
      } else if (this.negativeWords.has(lowerToken)) {
        wordScore = -0.5;
        negativeCount++;
        if (this.config.extractKeywords) keywords.push(token);
      }

      // Apply modifiers
      if (wordScore !== 0) {
        if (negated) {
          wordScore *= -0.5; // Negation flips and weakens
          negated = false;
        }
        wordScore *= intensified;
        intensified = 1;

        score += wordScore;
        signalStrength += Math.abs(wordScore);
      }
    }

    // Normalize score to [-1, 1]
    score = Math.max(-1, Math.min(1, score / Math.max(1, tokens.length / 4)));

    // Calculate confidence based on signal clarity
    let confidence = 0.5; // Base confidence

    if (signalStrength > 0) {
      // More signals = higher confidence
      confidence += Math.min(0.4, signalStrength * 0.2);
    }

    if (keywords.length > 0) {
      // Keywords found increases confidence
      confidence += Math.min(0.1, keywords.length * 0.02);
    }

    // Conflicting signals reduce confidence
    if (positiveCount > 0 && negativeCount > 0) {
      confidence -= 0.2;
    }

    confidence = Math.max(0.1, Math.min(1.0, confidence));

    return {
      score,
      confidence,
      keywords,
      positiveCount,
      negativeCount,
      negationCount,
      intensifierCount,
    };
  }
}

// ============================================================================
// EXPORT
// ============================================================================

export default SentimentTile;
