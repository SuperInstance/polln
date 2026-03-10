/**
 * Fraud Detection Tile
 *
 * Example tile for financial transaction analysis:
 * - Discriminates: Classifies transactions as legitimate/suspicious/fraudulent
 * - Confidence: Reports certainty based on risk factors
 * - Trace: Explains which factors contributed to the decision
 *
 * Demonstrates multi-factor confidence composition.
 */

import { Tile, Schema, Schemas, Zone } from '../core/Tile';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Fraud risk level
 */
export type FraudRiskLevel = 'legitimate' | 'suspicious' | 'fraudulent';

/**
 * Transaction data
 */
export interface Transaction {
  id: string;
  amount: number;
  currency: string;
  timestamp: Date;
  merchant: {
    id: string;
    category: string;
    country: string;
  };
  user: {
    id: string;
    accountAge: number; // days
    averageTransactionAmount: number;
    transactionCount: number;
    country: string;
  };
  device?: {
    id: string;
    type: string;
    knownDevice: boolean;
  };
  location?: {
    latitude: number;
    longitude: number;
    country: string;
  };
}

/**
 * Fraud detection result
 */
export interface FraudDetection {
  riskLevel: FraudRiskLevel;
  riskScore: number; // 0.0 to 1.0
  confidence: number; // 0.0 to 1.0
  riskFactors: RiskFactor[];
  recommendation: 'approve' | 'review' | 'decline';
}

/**
 * Individual risk factor
 */
export interface RiskFactor {
  name: string;
  severity: 'low' | 'medium' | 'high';
  weight: number;
  description: string;
}

/**
 * Fraud tile configuration
 */
export interface FraudTileConfig {
  /** Threshold for suspicious (default: 0.3) */
  suspiciousThreshold?: number;
  /** Threshold for fraudulent (default: 0.7) */
  fraudulentThreshold?: number;
  /** Minimum confidence for auto-decision (default: 0.8) */
  autoDecisionConfidence?: number;
  /** High-risk countries */
  highRiskCountries?: string[];
  /** High-risk merchant categories */
  highRiskCategories?: string[];
}

// ============================================================================
// FRAUD DETECTION TILE IMPLEMENTATION
// ============================================================================

/**
 * FraudDetectionTile - Analyzes transactions for fraud risk
 *
 * A production-style tile demonstrating:
 * - Multi-factor risk analysis
 * - Weighted confidence composition
 * - Zone-based recommendations
 *
 * @example
 * ```typescript
 * const fraudTile = new FraudDetectionTile({
 *   suspiciousThreshold: 0.3,
 *   fraudulentThreshold: 0.7,
 * });
 *
 * const transaction: Transaction = {
 *   id: 'txn_123',
 *   amount: 5000,
 *   // ...
 * };
 *
 * const result = await fraudTile.execute(transaction);
 * // result.zone = 'YELLOW' -> needs review
 * // result.output.riskFactors -> list of flagged factors
 * ```
 */
export class FraudDetectionTile extends Tile<Transaction, FraudDetection> {
  private readonly config: Required<FraudTileConfig>;

  private static readonly DEFAULT_HIGH_RISK_COUNTRIES = [
    'XX', 'YY', 'ZZ', // Placeholder ISO codes
  ];

  private static readonly DEFAULT_HIGH_RISK_CATEGORIES = [
    'gambling',
    'cryptocurrency',
    'money_transfer',
    'adult_content',
  ];

  constructor(config: FraudTileConfig = {}) {
    super(
      {
        type: 'Transaction',
        description: 'Financial transaction for fraud analysis',
        validate: (v: unknown): v is Transaction => {
          if (typeof v !== 'object' || v === null) return false;
          const t = v as Transaction;
          return (
            typeof t.id === 'string' &&
            typeof t.amount === 'number' &&
            t.merchant !== undefined &&
            t.user !== undefined
          );
        },
      },
      {
        type: 'FraudDetection',
        description: 'Fraud detection result',
        validate: (v: unknown): v is FraudDetection => {
          if (typeof v !== 'object' || v === null) return false;
          const f = v as FraudDetection;
          return (
            ['legitimate', 'suspicious', 'fraudulent'].includes(f.riskLevel) &&
            typeof f.riskScore === 'number' &&
            typeof f.confidence === 'number' &&
            Array.isArray(f.riskFactors)
          );
        },
      },
      { id: 'fraud-detection-tile' }
    );

    this.config = {
      suspiciousThreshold: config.suspiciousThreshold ?? 0.3,
      fraudulentThreshold: config.fraudulentThreshold ?? 0.7,
      autoDecisionConfidence: config.autoDecisionConfidence ?? 0.8,
      highRiskCountries: config.highRiskCountries ?? FraudDetectionTile.DEFAULT_HIGH_RISK_COUNTRIES,
      highRiskCategories: config.highRiskCategories ?? FraudDetectionTile.DEFAULT_HIGH_RISK_CATEGORIES,
    };
  }

  /**
   * Discriminate: Analyze transaction for fraud risk
   */
  async discriminate(input: Transaction): Promise<FraudDetection> {
    const riskFactors = this.analyzeRiskFactors(input);
    const riskScore = this.calculateRiskScore(riskFactors);
    const confidence = this.calculateConfidence(riskFactors, input);

    let riskLevel: FraudRiskLevel;
    if (riskScore >= this.config.fraudulentThreshold) {
      riskLevel = 'fraudulent';
    } else if (riskScore >= this.config.suspiciousThreshold) {
      riskLevel = 'suspicious';
    } else {
      riskLevel = 'legitimate';
    }

    const recommendation = this.getRecommendation(riskLevel, confidence);

    return {
      riskLevel,
      riskScore,
      confidence,
      riskFactors,
      recommendation,
    };
  }

  /**
   * Confidence: Calculate certainty of fraud assessment
   */
  async confidence(input: Transaction): Promise<number> {
    const riskFactors = this.analyzeRiskFactors(input);
    return this.calculateConfidence(riskFactors, input);
  }

  /**
   * Trace: Explain the fraud detection decision
   */
  async trace(input: Transaction): Promise<string> {
    const riskFactors = this.analyzeRiskFactors(input);
    const riskScore = this.calculateRiskScore(riskFactors);

    const lines: string[] = [
      `Transaction ${input.id} ($${input.amount.toFixed(2)})`,
      `Risk Score: ${(riskScore * 100).toFixed(1)}%`,
      '',
      'Risk Factors:',
    ];

    if (riskFactors.length === 0) {
      lines.push('  No significant risk factors detected');
    } else {
      for (const factor of riskFactors) {
        lines.push(`  - ${factor.name}: ${factor.severity.toUpperCase()} (${(factor.weight * 100).toFixed(0)}%)`);
        lines.push(`    ${factor.description}`);
      }
    }

    const zone = this.classifyZone(riskScore);
    lines.push('');
    lines.push(`Final Assessment: ${zone} zone`);
    lines.push(`Confidence: ${(await this.confidence(input) * 100).toFixed(1)}%`);

    return lines.join('\n');
  }

  // Private helpers

  private analyzeRiskFactors(txn: Transaction): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Amount anomaly
    const amountRatio = txn.amount / Math.max(1, txn.user.averageTransactionAmount);
    if (amountRatio > 10) {
      factors.push({
        name: 'Amount Anomaly',
        severity: 'high',
        weight: 0.25,
        description: `Transaction ${amountRatio.toFixed(1)}x user's average`,
      });
    } else if (amountRatio > 5) {
      factors.push({
        name: 'Amount Anomaly',
        severity: 'medium',
        weight: 0.15,
        description: `Transaction ${amountRatio.toFixed(1)}x user's average`,
      });
    } else if (amountRatio > 2) {
      factors.push({
        name: 'Amount Anomaly',
        severity: 'low',
        weight: 0.05,
        description: `Transaction ${amountRatio.toFixed(1)}x user's average`,
      });
    }

    // Country mismatch
    if (txn.location && txn.location.country !== txn.user.country) {
      factors.push({
        name: 'Country Mismatch',
        severity: 'medium',
        weight: 0.20,
        description: `Transaction in ${txn.location.country}, user in ${txn.user.country}`,
      });
    }

    // High-risk country
    const txnCountry = txn.location?.country ?? txn.merchant.country;
    if (txnCountry && this.config.highRiskCountries.includes(txnCountry)) {
      factors.push({
        name: 'High-Risk Country',
        severity: 'high',
        weight: 0.30,
        description: `Transaction involves ${txnCountry}`,
      });
    }

    // High-risk merchant category
    if (this.config.highRiskCategories.includes(txn.merchant.category)) {
      factors.push({
        name: 'High-Risk Category',
        severity: 'medium',
        weight: 0.15,
        description: `Merchant category: ${txn.merchant.category}`,
      });
    }

    // New account
    if (txn.user.accountAge < 7) {
      factors.push({
        name: 'New Account',
        severity: 'medium',
        weight: 0.15,
        description: `Account age: ${txn.user.accountAge} days`,
      });
    }

    // Unknown device
    if (txn.device && !txn.device.knownDevice) {
      factors.push({
        name: 'Unknown Device',
        severity: 'low',
        weight: 0.10,
        description: `Device not previously used by account`,
      });
    }

    // Low transaction history
    if (txn.user.transactionCount < 5) {
      factors.push({
        name: 'Low Activity',
        severity: 'low',
        weight: 0.05,
        description: `Only ${txn.user.transactionCount} transactions`,
      });
    }

    return factors;
  }

  private calculateRiskScore(factors: RiskFactor[]): number {
    if (factors.length === 0) return 0;

    // Sum weighted factors
    const totalWeight = factors.reduce((sum, f) => sum + f.weight, 0);

    // Cap at 1.0
    return Math.min(1.0, totalWeight);
  }

  private calculateConfidence(factors: RiskFactor[], txn: Transaction): number {
    // Base confidence
    let confidence = 0.6;

    // More data points = higher confidence
    if (txn.device) confidence += 0.05;
    if (txn.location) confidence += 0.05;

    // User history improves confidence
    if (txn.user.transactionCount > 10) confidence += 0.1;
    if (txn.user.accountAge > 30) confidence += 0.1;

    // Multiple risk factors reduce confidence (complexity)
    if (factors.length > 3) confidence -= 0.1;

    // High-severity factors increase confidence (clear signal)
    const highSeverityCount = factors.filter(f => f.severity === 'high').length;
    if (highSeverityCount > 0) confidence += 0.1;

    return Math.max(0.3, Math.min(0.95, confidence));
  }

  private getRecommendation(
    riskLevel: FraudRiskLevel,
    confidence: number
  ): 'approve' | 'review' | 'decline' {
    if (riskLevel === 'fraudulent') {
      return 'decline';
    }

    if (riskLevel === 'suspicious') {
      return 'review';
    }

    // Legitimate - check confidence for auto-approval
    if (confidence >= this.config.autoDecisionConfidence) {
      return 'approve';
    }

    return 'review';
  }

  private classifyZone(riskScore: number): Zone {
    if (riskScore >= this.config.fraudulentThreshold) {
      return 'RED';
    }
    if (riskScore >= this.config.suspiciousThreshold) {
      return 'YELLOW';
    }
    return 'GREEN';
  }
}

// ============================================================================
// EXPORT
// ============================================================================

export default FraudDetectionTile;
