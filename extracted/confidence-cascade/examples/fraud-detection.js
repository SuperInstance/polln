/**
 * Fraud Detection Example
 *
 * This example shows how to use confidence cascades for fraud detection
 * in a payment processing system.
 */

const {
  createConfidence,
  parallelCascade,
  sequentialCascade,
  conditionalCascade
} = require('@superinstance/confidence-cascade');

// Simulate fraud detection signals
function simulateFraudDetection(transaction) {
  console.log('Processing transaction:', transaction);

  // Step 1: Sequential cascade for basic checks
  const basicChecks = sequentialCascade([
    createConfidence(transaction.isValidFormat ? 0.95 : 0.10, 'format_validation'),
    createConfidence(transaction.hasValidInputs ? 0.90 : 0.20, 'input_validation'),
    createConfidence(transaction.isNotDuplicate ? 0.85 : 0.15, 'duplicate_check')
  ]);

  console.log(`Basic checks confidence: ${basicChecks.confidence.value} (${basicChecks.confidence.zone})`);

  // Step 2: Parallel cascade for ML and rule-based checks
  const mlAndRules = parallelCascade([
    { confidence: createConfidence(transaction.mlScore, 'ml_model'), weight: 0.6 },
    { confidence: createConfidence(transaction.rulesScore, 'rules_engine'), weight: 0.4 }
  ]);

  console.log(`ML/Rules confidence: ${mlAndRules.confidence.value} (${mlAndRules.confidence.zone})`);

  // Step 3: Conditional cascade based on transaction amount
  const amountBasedChecks = conditionalCascade([
    {
      confidence: createConfidence(0.92, 'basic_amount_checks'),
      predicate: transaction.amount < 1000,
      description: 'low_amount_flow'
    },
    {
      confidence: createConfidence(0.85, 'enhanced_amount_checks'),
      predicate: transaction.amount >= 1000 && transaction.amount < 10000,
      description: 'medium_amount_flow'
    },
    {
      confidence: createConfidence(0.95, 'manual_review_checks'),
      predicate: transaction.amount >= 10000,
      description: 'high_amount_flow'
    }
  ]);

  console.log(`Amount-based checks: ${amountBasedChecks.confidence.value} (${amountBasedChecks.confidence.zone})`);

  // Final decision cascade
  const finalDecision = parallelCascade([
    { confidence: basicChecks.confidence, weight: 0.2 },
    { confidence: mlAndRules.confidence, weight: 0.5 },
    { confidence: amountBasedChecks.confidence, weight: 0.3 }
  ]);

  console.log(`\nFinal decision confidence: ${finalDecision.confidence.value} (${finalDecision.confidence.zone})`);

  if (finalDecision.escalationTriggered) {
    console.log(`ESCALATION: ${finalDecision.escalationLevel}`);

    switch (finalDecision.escalationLevel) {
      case 'ALERT':
      case 'CRITICAL':
        console.log('ACTION: Block transaction and flag for manual review');
        return false;
      case 'WARNING':
        console.log('ACTION: Request additional verification');
        return 'additional_verification';
      default:
        console.log('ACTION: Log warning and continue');
        return true;
    }
  }

  console.log('ACTION: Approve transaction');
  return true;
}

// Example usage
console.log('=== FRAUD DETECTION EXAMPLE ===\n');

// Normal transaction
const normalTransaction = {
  id: 'txn_123',
  amount: 150,
  mlScore: 0.88,
  rulesScore: 0.92,
  isValidFormat: true,
  hasValidInputs: true,
  isNotDuplicate: true
};

console.log('Testing normal transaction...');
simulateFraudDetection(normalTransaction);

console.log('\n---\n');

// Suspicious transaction
const suspiciousTransaction = {
  id: 'txn_456',
  amount: 50000,
  mlScore: 0.45,
  rulesScore: 0.20,
  isValidFormat: true,
  hasValidInputs: false,
  isNotDuplicate: true
};

console.log('Testing suspicious transaction...');
simulateFraudDetection(suspiciousTransaction);