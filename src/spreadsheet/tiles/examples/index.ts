/**
 * SMP Tile Examples
 *
 * Reference implementations demonstrating tile patterns:
 * - SentimentTile: Text classification with lexicon-based analysis
 * - FraudDetectionTile: Multi-factor risk analysis
 *
 * These examples show how to build production-ready tiles that:
 * - Implement discriminate(), confidence(), and trace()
 * - Use the three-zone confidence model
 * - Provide explainable decisions
 */

export { SentimentTile, Sentiment, SentimentLabel, SentimentTileConfig } from './SentimentTile';
export {
  FraudDetectionTile,
  FraudDetection,
  FraudRiskLevel,
  RiskFactor,
  Transaction,
  FraudTileConfig,
} from './FraudDetectionTile';
