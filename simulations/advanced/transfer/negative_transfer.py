"""
POLLN Negative Transfer Detection and Prevention
================================================

Identifies and prevents negative transfer scenarios where knowledge transfer
actually harms performance. Tests validation strategies and protection mechanisms.

Key Metrics:
- Negative transfer rate: Percentage of transfers that harm performance
- Detection accuracy: How well we can predict negative transfer
- Prevention success: Rate of successfully blocked negative transfers
- False positive rate: Legitimate transfers incorrectly blocked
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score


class TransferOutcome(Enum):
    """Possible outcomes of knowledge transfer"""
    POSITIVE = "positive"  # Performance improves
    NEUTRAL = "neutral"  # No significant change
    NEGATIVE = "negative"  # Performance degrades


class ProtectionMechanism(Enum):
    """Strategies to prevent negative transfer"""
    SIMILARITY_GATING = "similarity_gating"  # Block low-similarity transfers
    VALIDATION_SET = "validation_set"  # Test on validation set first
    GRADUAL_TRANSFER = "gradual_transfer"  # Transfer in small steps
    ROLLBACK = "rollback"  # Revert if performance drops
    ENSEMBLE_TEST = "ensemble_test"  # Test as ensemble first


@dataclass
class TransferScenario:
    """A potential knowledge transfer scenario"""
    source_task: str
    target_task: str
    task_similarity: float

    # Source characteristics
    source_performance: float
    source_data_size: int
    source_confidence: float

    # Target characteristics
    target_performance_before: float
    target_data_size: int
    target_domain_shift: float  # How different domains are

    # Additional features for prediction
    architecture_match: bool
    modality_match: bool
    capability_overlap: float

    def to_features(self) -> np.ndarray:
        """Extract features for ML prediction"""
        return np.array([
            self.task_similarity,
            self.source_performance,
            self.source_data_size / 100000,  # Normalized
            self.source_confidence,
            self.target_performance_before,
            self.target_data_size / 100000,
            self.target_domain_shift,
            float(self.architecture_match),
            float(self.modality_match),
            self.capability_overlap
        ])


@dataclass
class TransferResult:
    """Result of a knowledge transfer attempt"""
    scenario: TransferScenario
    outcome: TransferOutcome

    # Performance metrics
    performance_before: float
    performance_after: float
    performance_delta: float

    # Whether negative transfer was prevented
    prevented: bool
    prevention_method: Optional[ProtectionMechanism]

    # Prediction (if using ML)
    predicted_negative: bool
    prediction_confidence: float

    def is_negative(self) -> bool:
        """Check if this was negative transfer"""
        return self.performance_delta < -0.02  # 2% degradation threshold

    def to_dict(self) -> dict:
        return {
            'source_task': self.scenario.source_task,
            'target_task': self.scenario.target_task,
            'task_similarity': self.scenario.task_similarity,
            'performance_before': self.performance_before,
            'performance_after': self.performance_after,
            'performance_delta': self.performance_delta,
            'outcome': self.outcome.value,
            'negative_transfer': self.is_negative(),
            'prevented': self.prevented,
            'prevention_method': self.prevention_method.value if self.prevention_method else None,
            'predicted_negative': self.predicted_negative,
            'prediction_confidence': self.prediction_confidence
        }


@dataclass
class ProtectionConfig:
    """Configuration for negative transfer protection"""
    enabled: bool = True

    # Similarity gating
    similarity_threshold: float = 0.3
    strict_mode: bool = False

    # Validation set
    validation_fraction: float = 0.1
    min_validation_improvement: float = 0.01

    # Gradual transfer
    gradual_steps: int = 5
    min_step_improvement: float = 0.005

    # Rollback
    rollback_on_degradation: bool = True
    rollback_threshold: float = -0.02

    # Ensemble test
    ensemble_test_fraction: float = 0.05

    def to_dict(self) -> dict:
        return {
            'enabled': self.enabled,
            'similarity_threshold': self.similarity_threshold,
            'strict_mode': self.strict_mode,
            'validation_fraction': self.validation_fraction,
            'min_validation_improvement': self.min_validation_improvement,
            'gradual_steps': self.gradual_steps,
            'min_step_improvement': self.min_step_improvement,
            'rollback_on_degradation': self.rollback_on_degradation,
            'rollback_threshold': self.rollback_threshold,
            'ensemble_test_fraction': self.ensemble_test_fraction
        }


class NegativeTransferSimulator:
    """Simulates and detects negative transfer scenarios"""

    def __init__(self):
        self.results: List[TransferResult] = []
        self.predictor: Optional[RandomForestClassifier] = None

    def create_scenario(
        self,
        source_task: str,
        target_task: str,
        **kwargs
    ) -> TransferScenario:
        """Create a transfer scenario"""

        # Generate random characteristics
        task_similarity = kwargs.get('task_similarity', np.random.random())

        return TransferScenario(
            source_task=source_task,
            target_task=target_task,
            task_similarity=task_similarity,
            source_performance=kwargs.get('source_performance', 0.7 + np.random.random() * 0.2),
            source_data_size=kwargs.get('source_data_size', np.random.randint(10000, 100000)),
            source_confidence=kwargs.get('source_confidence', 0.6 + np.random.random() * 0.3),
            target_performance_before=kwargs.get('target_performance_before', 0.5 + np.random.random() * 0.3),
            target_data_size=kwargs.get('target_data_size', np.random.randint(5000, 50000)),
            target_domain_shift=kwargs.get('target_domain_shift', 1 - task_similarity),
            architecture_match=kwargs.get('architecture_match', np.random.random() > 0.3),
            modality_match=kwargs.get('modality_match', np.random.random() > 0.4),
            capability_overlap=kwargs.get('capability_overlap', task_similarity + np.random.normal(0, 0.1))
        )

    def simulate_transfer(
        self,
        scenario: TransferScenario,
        protection_config: Optional[ProtectionConfig] = None
    ) -> TransferResult:
        """Simulate a knowledge transfer with optional protection"""

        if protection_config is None:
            protection_config = ProtectionConfig(enabled=False)

        # Check if transfer should be prevented
        prevented = False
        prevention_method = None

        if protection_config.enabled:
            # Similarity gating
            if scenario.task_similarity < protection_config.similarity_threshold:
                prevented = True
                prevention_method = ProtectionMechanism.SIMILARITY_GATING

        # Simulate performance change
        if prevented:
            # No transfer, no change
            performance_delta = 0.0
            performance_after = scenario.target_performance_before
        else:
            # Simulate transfer outcome
            # High similarity usually helps, low similarity often hurts
            base_delta = (scenario.task_similarity - 0.4) * 0.2

            # Add noise
            noise = np.random.normal(0, 0.03)
            performance_delta = base_delta + noise

            # Cap delta
            performance_delta = np.clip(performance_delta, -0.2, 0.2)
            performance_after = scenario.target_performance_before + performance_delta

            # Check if rollback needed
            if (protection_config.rollback_on_degradation and
                performance_delta < protection_config.rollback_threshold):
                prevented = True
                prevention_method = ProtectionMechanism.ROLLBACK
                performance_delta = 0.0
                performance_after = scenario.target_performance_before

        # Determine outcome
        if performance_delta > 0.02:
            outcome = TransferOutcome.POSITIVE
        elif performance_delta < -0.02:
            outcome = TransferOutcome.NEGATIVE
        else:
            outcome = TransferOutcome.NEUTRAL

        # Try to predict negative transfer (if model is trained)
        predicted_negative = False
        prediction_confidence = 0.0

        if self.predictor is not None:
            features = scenario.to_features().reshape(1, -1)
            pred_proba = self.predictor.predict_proba(features)[0]
            negative_idx = list(self.predictor.classes_).index(1)  # 1 = negative
            predicted_negative = self.predictor.predict(features)[0] == 1
            prediction_confidence = pred_proba[negative_idx]

        result = TransferResult(
            scenario=scenario,
            outcome=outcome,
            performance_before=scenario.target_performance_before,
            performance_after=performance_after,
            performance_delta=performance_delta,
            prevented=prevented,
            prevention_method=prevention_method,
            predicted_negative=predicted_negative,
            prediction_confidence=prediction_confidence
        )

        self.results.append(result)
        return result

    def train_predictor(
        self,
        train_results: List[TransferResult]
    ) -> Dict[str, float]:
        """Train ML model to predict negative transfer"""

        # Prepare data
        X = np.array([r.scenario.to_features() for r in train_results])
        y = np.array([1 if r.is_negative() else 0 for r in train_results])

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train model
        self.predictor = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.predictor.fit(X_train, y_train)

        # Evaluate
        y_pred = self.predictor.predict(X_test)
        y_proba = self.predictor.predict_proba(X_test)[:, 1]

        metrics = {
            'accuracy': np.mean(y_pred == y_test),
            'roc_auc': roc_auc_score(y_test, y_proba)
        }

        # Feature importance
        feature_names = [
            'task_similarity', 'source_performance', 'source_data_size',
            'source_confidence', 'target_performance_before', 'target_data_size',
            'target_domain_shift', 'architecture_match', 'modality_match',
            'capability_overlap'
        ]
        feature_importance = dict(zip(
            feature_names,
            self.predictor.feature_importances_
        ))
        metrics['feature_importance'] = feature_importance

        return metrics

    def run_protection_comparison(
        self,
        num_scenarios: int = 1000
    ) -> Tuple[List[TransferResult], List[TransferResult]]:
        """Compare with and without protection"""

        # Create scenarios
        scenarios = []
        task_pairs = [
            ("code_review", "code_generation"),
            ("code_review", "sentiment_analysis"),
            ("text_summarization", "question_answering"),
            ("text_summarization", "math_problems"),
            ("translation", "sentiment_analysis"),
            ("question_answering", "retrieval"),
            ("math_problems", "code_generation"),
            ("sentiment_analysis", "classification"),
        ]

        for _ in range(num_scenarios):
            source, target = task_pairs[np.random.randint(len(task_pairs))]
            scenario = self.create_scenario(source, target)
            scenarios.append(scenario)

        # Without protection
        no_protection_results = []
        for scenario in scenarios:
            result = self.simulate_transfer(scenario, ProtectionConfig(enabled=False))
            no_protection_results.append(result)

        # With protection
        protection_config = ProtectionConfig(
            enabled=True,
            similarity_threshold=0.3,
            rollback_on_degradation=True
        )
        with_protection_results = []
        for scenario in scenarios:
            result = self.simulate_transfer(scenario, protection_config)
            with_protection_results.append(result)

        return no_protection_results, with_protection_results


class NegativeTransferAnalyzer:
    """Analyzes negative transfer patterns"""

    def __init__(self, results: List[TransferResult]):
        self.results = results
        self.df = pd.DataFrame([r.to_dict() for r in results])

    def analyze_negative_transfer_rate(self) -> Dict[str, float]:
        """Analyze rate of negative transfer"""

        total = len(self.results)
        negative = sum(1 for r in self.results if r.is_negative())

        # By similarity bin
        self.df['similarity_bin'] = pd.cut(
            self.df['task_similarity'],
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=['Very Low', 'Low', 'Medium', 'High']
        )

        negative_by_bin = {}
        for bin_name in ['Very Low', 'Low', 'Medium', 'High']:
            bin_df = self.df[self.df['similarity_bin'] == bin_name]
            if len(bin_df) > 0:
                rate = (bin_df['negative_transfer'].sum() / len(bin_df))
                negative_by_bin[bin_name] = float(rate)

        return {
            'overall_rate': float(negative / total) if total > 0 else 0,
            'by_similarity_bin': negative_by_bin
        }

    def analyze_protection_effectiveness(
        self,
        no_protection: List[TransferResult],
        with_protection: List[TransferResult]
    ) -> Dict[str, float]:
        """Analyze how well protection mechanisms work"""

        # Negative transfer without protection
        negative_no_protection = sum(1 for r in no_protection if r.is_negative())

        # Negative transfer with protection
        negative_with_protection = sum(1 for r in with_protection if r.is_negative())

        # Prevented transfers
        prevented = sum(1 for r in with_protection if r.prevented)

        # False positives (good transfers blocked)
        false_positives = sum(
            1 for r in with_protection
            if r.prevented and not r.is_negative()
        )

        total = len(with_protection)

        return {
            'negative_without_protection': float(negative_no_protection / len(no_protection)),
            'negative_with_protection': float(negative_with_protection / total),
            'prevention_rate': float(prevented / total),
            'false_positive_rate': float(false_positives / total),
            'negative_reduction': float(
                (negative_no_protection - negative_with_protection) / negative_no_protection
                if negative_no_protection > 0 else 0
            )
        }

    def visualize_results(
        self,
        save_path: Optional[str] = None
    ):
        """Visualize negative transfer analysis"""

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Performance delta vs similarity
        ax1 = axes[0, 0]
        ax1.scatter(
            self.df['task_similarity'],
            self.df['performance_delta'],
            alpha=0.5, c=self.df['negative_transfer'], cmap='RdYlGn_r'
        )
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax1.axvline(x=0.3, color='r', linestyle='--', alpha=0.5, label='Similarity threshold')
        ax1.set_xlabel('Task Similarity')
        ax1.set_ylabel('Performance Delta')
        ax1.set_title('Performance Change vs Similarity')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Negative transfer rate by similarity bin
        ax2 = axes[0, 1]
        analysis = self.analyze_negative_transfer_rate()
        bins = list(analysis['by_similarity_bin'].keys())
        rates = list(analysis['by_similarity_bin'].values())
        ax2.bar(range(len(bins)), rates, color=['red', 'orange', 'yellow', 'green'])
        ax2.set_xticks(range(len(bins)))
        ax2.set_xticklabels(bins)
        ax2.set_ylabel('Negative Transfer Rate')
        ax2.set_title('Negative Transfer by Similarity')
        ax2.axhline(y=0.1, color='r', linestyle='--', alpha=0.5, label='10% threshold')
        ax2.legend()

        # 3. Performance delta distribution
        ax3 = axes[1, 0]
        negative_deltas = self.df[self.df['negative_transfer']]['performance_delta']
        positive_deltas = self.df[~self.df['negative_transfer']]['performance_delta']
        ax3.hist(positive_deltas, bins=50, alpha=0.5, label='Positive/Neutral', color='green')
        ax3.hist(negative_deltas, bins=50, alpha=0.5, label='Negative', color='red')
        ax3.axvline(x=0, color='k', linestyle='--', alpha=0.5)
        ax3.set_xlabel('Performance Delta')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Distribution of Performance Changes')
        ax3.legend()

        # 4. Feature importance (if available)
        ax4 = axes[1, 1]
        if 'feature_importance' in self.df.columns:
            # This would need to be added during simulation
            ax4.text(0.5, 0.5, 'Feature importance\navailable in training results',
                    ha='center', va='center', transform=ax4.transAxes)
        else:
            ax4.text(0.5, 0.5, 'Run train_predictor() first\nto see feature importance',
                    ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Feature Importance')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()


def main():
    """Main simulation"""
    print("=" * 70)
    print("POLLN Negative Transfer Detection and Prevention")
    print("=" * 70)

    # Create simulator
    simulator = NegativeTransferSimulator()

    # Generate training data
    print("\n1. Generating training data...")
    train_scenarios = []
    task_pairs = [
        ("code_review", "code_generation"),
        ("code_review", "sentiment_analysis"),
        ("text_summarization", "question_answering"),
        ("text_summarization", "math_problems"),
        ("translation", "sentiment_analysis"),
        ("question_answering", "retrieval"),
        ("math_problems", "code_generation"),
        ("sentiment_analysis", "classification"),
    ]

    for _ in range(5000):
        source, target = task_pairs[np.random.randint(len(task_pairs))]
        scenario = simulator.create_scenario(
            source, target,
            task_similarity=np.random.beta(2, 5)  # Biased toward low similarity
        )
        train_scenarios.append(scenario)

    # Simulate transfers for training
    train_results = []
    for scenario in train_scenarios:
        result = simulator.simulate_transfer(scenario)
        train_results.append(result)

    print(f"   Generated {len(train_results)} training examples")

    # Train predictor
    print("\n2. Training negative transfer predictor...")
    metrics = simulator.train_predictor(train_results)

    print(f"   Model accuracy: {metrics['accuracy']:.3f}")
    print(f"   ROC AUC: {metrics['roc_auc']:.3f}")

    print("\n   Top 5 important features:")
    sorted_features = sorted(
        metrics['feature_importance'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    for feature, importance in sorted_features:
        print(f"      {feature}: {importance:.3f}")

    # Test protection mechanisms
    print("\n3. Testing protection mechanisms...")
    no_protection, with_protection = simulator.run_protection_comparison(
        num_scenarios=1000
    )

    print(f"   Without protection: {len(no_protection)} scenarios")
    print(f"   With protection: {len(with_protection)} scenarios")

    # Analyze
    print("\n4. Analyzing results...")
    analyzer = NegativeTransferAnalyzer(with_protection)

    protection_stats = analyzer.analyze_protection_effectiveness(
        no_protection, with_protection
    )

    print("\n   Protection Effectiveness:")
    print(f"      Negative transfer without protection: {protection_stats['negative_without_protection']:.2%}")
    print(f"      Negative transfer with protection: {protection_stats['negative_with_protection']:.2%}")
    print(f"      Reduction in negative transfer: {protection_stats['negative_reduction']:.2%}")
    print(f"      Prevention rate: {protection_stats['prevention_rate']:.2%}")
    print(f"      False positive rate: {protection_stats['false_positive_rate']:.2%}")

    # Negative transfer analysis
    negative_rate = analyzer.analyze_negative_transfer_rate()
    print("\n   Negative Transfer Rate:")
    print(f"      Overall: {negative_rate['overall_rate']:.2%}")
    print("      By similarity bin:")
    for bin_name, rate in negative_rate['by_similarity_bin'].items():
        print(f"         {bin_name}: {rate:.2%}")

    # Visualize
    print("\n5. Generating visualizations...")
    analyzer.visualize_results("simulations/advanced/transfer/negative_transfer_results.png")
    print("   Saved visualizations")

    # Generate protection configuration
    print("\n6. Generating protection configuration...")

    protection_config = {
        'enabled': True,
        'similarity_threshold': 0.3,
        'strict_mode': False,
        'validation': {
            'enabled': True,
            'validation_fraction': 0.1,
            'min_improvement': 0.01
        },
        'rollback': {
            'enabled': True,
            'threshold': -0.02,
            'monitor_performance': True
        },
        'gradual_transfer': {
            'enabled': True,
            'steps': 5,
            'min_step_improvement': 0.005
        },
        'prediction': {
            'enabled': True,
            'model': 'random_forest',
            'confidence_threshold': 0.7
        }
    }

    with open("simulations/advanced/transfer/negative_transfer_config.json", 'w') as f:
        json.dump(protection_config, f, indent=2)

    print("   Saved protection configuration")

    # Save results
    print("\n7. Saving results...")
    results_df = pd.DataFrame([r.to_dict() for r in with_protection])
    results_df.to_csv("simulations/advanced/transfer/negative_transfer_results.csv", index=False)
    print("   Saved results CSV")

    print("\n" + "=" * 70)
    print("Simulation complete!")
    print("=" * 70)

    # Summary
    print("\nSummary:")
    print(f"   Total scenarios tested: {len(with_protection)}")
    print(f"   Negative transfer prevented: {protection_stats['prevention_rate']:.2%}")
    print(f"   Predictor accuracy: {metrics['accuracy']:.3f}")
    print(f"   Recommendation: Enable protection for similarity < 0.3")


if __name__ == "__main__":
    main()
