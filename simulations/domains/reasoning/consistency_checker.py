"""
POLLN Response Consistency Validation

Tests self-consistency, factual consistency, and temporal consistency
to optimize POLLN agents for consistent multi-turn dialogue and reasoning.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import json
from collections import defaultdict
import random


class ConsistencyType(Enum):
    """Types of consistency to check"""
    SELF_CONSISTENCY = "self_consistency"  # Internal consistency within response
    FACTUAL_CONSISTENCY = "factual_consistency"  # Consistency with known facts
    TEMPORAL_CONSISTENCY = "temporal_consistency"  # Consistency over time
    LOGICAL_CONSISTENCY = "logical_consistency"  # Logical coherence
    PERSONA_CONSISTENCY = "persona_consistency"  # Consistent persona/voice


@dataclass
class ConsistencyViolation:
    """Represents a consistency violation"""
    violation_type: str
    severity: str  # low, medium, high
    description: str
    location: str  # where in response
    confidence: float


@dataclass
class ConsistencyReport:
    """Report of consistency analysis"""
    overall_score: float
    violations: List[ConsistencyViolation]
    type_scores: Dict[str, float]
    recommendations: List[str]


@dataclass
class ConsistencyMetrics:
    """Metrics for consistency checking"""
    violation_rate: float
    detection_accuracy: float
    false_positive_rate: float
    avg_response_time: float
    consistency_score: float


class SelfConsistencyChecker:
    """
    Checks for internal consistency within responses.
    """

    def __init__(self):
        self.contradiction_patterns = [
            (r'always', r'never'),
            (r'all', r'none'),
            (r'every', r'no'),
            (r'certainly', r'uncertain'),
            (r'definitely', r'maybe')
        ]

    def check(self, response: str) -> List[ConsistencyViolation]:
        """Check for self-contradictions"""
        violations = []

        # Check for contradiction patterns
        for pattern1, pattern2 in self.contradiction_patterns:
            import re
            if re.search(pattern1, response, re.IGNORECASE) and \
               re.search(pattern2, response, re.IGNORECASE):
                violations.append(ConsistencyViolation(
                    violation_type='contradiction',
                    severity='medium',
                    description=f"Found contradicting patterns: {pattern1} vs {pattern2}",
                    location='response_body',
                    confidence=0.7
                ))

        # Check numerical consistency
        violations.extend(self._check_numerical_consistency(response))

        # Check entity consistency
        violations.extend(self._check_entity_consistency(response))

        return violations

    def _check_numerical_consistency(self, response: str) -> List[ConsistencyViolation]:
        """Check for numerical inconsistencies"""
        violations = []
        import re

        # Extract numbers with context
        numbers = re.findall(r'(\d+\.?\d*)\s*(\w+)?', response)

        # Check for duplicate numbers with different units
        number_contexts = defaultdict(list)
        for num, unit in numbers:
            if unit:
                number_contexts[unit].append(float(num))

        for unit, values in number_contexts.items():
            if len(set(values)) > 1:
                violations.append(ConsistencyViolation(
                    violation_type='numerical_inconsistency',
                    severity='low',
                    description=f"Multiple values for {unit}: {values}",
                    location='response_body',
                    confidence=0.6
                ))

        return violations

    def _check_entity_consistency(self, response: str) -> List[ConsistencyViolation]:
        """Check for entity reference consistency"""
        violations = []

        # Extract capitalized words (potential entities)
        import re
        entities = re.findall(r'\b([A-Z][a-z]+)\b', response)

        # Check if entity is referred to differently
        entity_variants = defaultdict(set)
        for entity in entities:
            entity_variants[entity.lower()].add(entity)

        for base_name, variants in entity_variants.items():
            if len(variants) > 1:
                violations.append(ConsistencyViolation(
                    violation_type='entity_naming_inconsistency',
                    severity='low',
                    description=f"Entity referred to as: {', '.join(variants)}",
                    location='response_body',
                    confidence=0.5
                ))

        return violations


class FactualConsistencyChecker:
    """
    Checks consistency with known facts.
    """

    def __init__(self):
        # Simulated knowledge base
        self.fact_database = {
            'earth_is_flat': False,
            'water_boils_at_100c': True,
            'speed_of_light': 299792458,
            'year': 2025,
            'pi_approx': 3.14159
        }

    def check(self, response: str) -> List[ConsistencyViolation]:
        """Check against known facts"""
        violations = []

        # Check for common misconceptions
        misconceptions = [
            (r'earth is flat', 'The Earth is not flat'),
            (r'water boils at \d+[^\d]', 'Water boils at 100°C at sea level'),
            (r'speed of light is \d+[^\d]', 'Speed of light is ~300,000 km/s')
        ]

        import re
        for pattern, correction in misconceptions:
            if re.search(pattern, response, re.IGNORECASE):
                violations.append(ConsistencyViolation(
                    violation_type='factual_inaccuracy',
                    severity='high',
                    description=f"Potential factual error: {correction}",
                    location='response_body',
                    confidence=0.8
                ))

        return violations


class TemporalConsistencyChecker:
    """
    Checks temporal consistency across conversation turns.
    """

    def __init__(self):
        self.conversation_history: List[Dict] = []

    def add_turn(self, speaker: str, content: str, timestamp: int):
        """Add a conversation turn"""
        self.conversation_history.append({
            'speaker': speaker,
            'content': content,
            'timestamp': timestamp
        })

    def check(self, current_response: str) -> List[ConsistencyViolation]:
        """Check for temporal inconsistencies"""
        violations = []

        if not self.conversation_history:
            return violations

        # Check against previous statements
        for turn in self.conversation_history[-5:]:  # Last 5 turns
            violations.extend(self._check_against_turn(
                current_response,
                turn
            ))

        # Check temporal references
        violations.extend(self._check_temporal_references(current_response))

        return violations

    def _check_against_turn(
        self,
        current: str,
        previous: Dict
    ) -> List[ConsistencyViolation]:
        """Check current response against previous turn"""
        violations = []

        # Check for direct contradictions
        if 'not' in current.lower() and previous['content'].lower() in current.lower():
            violations.append(ConsistencyViolation(
                violation_type='temporal_contradiction',
                severity='medium',
                description=f"Contradicts previous statement by {previous['speaker']}",
                location='response_body',
                confidence=0.6
            ))

        return violations

    def _check_temporal_references(self, response: str) -> List[ConsistencyViolation]:
        """Check temporal reference consistency"""
        violations = []

        # Check for conflicting temporal markers
        temporal_markers = ['yesterday', 'today', 'tomorrow', 'last week', 'next week']
        found_markers = [m for m in temporal_markers if m in response.lower()]

        if len(found_markers) > 2:
            violations.append(ConsistencyViolation(
                violation_type='temporal_confusion',
                severity='low',
                description=f"Multiple temporal references: {found_markers}",
                location='response_body',
                confidence=0.5
            ))

        return violations


class LogicalConsistencyChecker:
    """
    Checks logical coherence of responses.
    """

    def __init__(self):
        pass

    def check(self, response: str) -> List[ConsistencyViolation]:
        """Check for logical inconsistencies"""
        violations = []

        # Check for non-sequiturs
        violations.extend(self._check_sequitur(response))

        # Check for circular reasoning
        violations.extend(self._check_circular_reasoning(response))

        # Check for unsupported claims
        violations.extend(self._check_unsupported_claims(response))

        return violations

    def _check_sequitur(self, response: str) -> List[ConsistencyViolation]:
        """Check for non-sequiturs"""
        violations = []

        # Split into sentences
        sentences = response.split('.')

        # Check if conclusions follow from premises
        # (Simplified - just check for coherence markers)
        coherence_markers = ['therefore', 'thus', 'hence', 'consequently', 'so']

        for i, sentence in enumerate(sentences[:-1]):
            if any(marker in sentence.lower() for marker in coherence_markers):
                # Check if next sentence relates
                if not sentences[i+1].strip():
                    violations.append(ConsistencyViolation(
                        violation_type='non_sequitur',
                        severity='low',
                        description=f"Coherence marker but no follow-up",
                        location=f'sentence_{i}',
                        confidence=0.4
                    ))

        return violations

    def _check_circular_reasoning(self, response: str) -> List[ConsistencyViolation]:
        """Check for circular reasoning"""
        violations = []

        # Look for repetitive patterns
        words = response.lower().split()
        if len(words) > 20:
            # Check if first 5 words appear again at end
            start_phrase = ' '.join(words[:5])
            if start_phrase in ' '.join(words[-10:]):
                violations.append(ConsistencyViolation(
                    violation_type='circular_reasoning',
                    severity='medium',
                    description="Possible circular reasoning detected",
                    location='response_structure',
                    confidence=0.5
                ))

        return violations

    def _check_unsupported_claims(self, response: str) -> List[ConsistencyViolation]:
        """Check for unsupported claims"""
        violations = []

        # Look for definitive statements without support
        definitive_markers = ['definitely', 'certainly', 'undoubtedly', 'absolutely']

        import re
        for marker in definitive_markers:
            if re.search(rf'\b{marker}\b', response, re.IGNORECASE):
                # Check if followed by supporting evidence
                marker_idx = response.lower().find(marker)
                following_text = response[marker_idx:marker_idx+100]

                if not any(evidence in following_text.lower()
                          for evidence in ['because', 'since', 'due to', 'as']):
                    violations.append(ConsistencyViolation(
                        violation_type='unsupported_claim',
                        severity='low',
                        description=f"Definite statement without clear support",
                        location='response_body',
                        confidence=0.4
                    ))

        return violations


class PersonaConsistencyChecker:
    """
    Checks consistency of persona/voice throughout conversation.
    """

    def __init__(self, persona: Optional[Dict] = None):
        self.persona = persona or {
            'name': 'Assistant',
            'tone': 'helpful',
            'style': 'formal',
            'expertise': 'general'
        }
        self.response_history = []

    def check(self, response: str) -> List[ConsistencyViolation]:
        """Check for persona consistency"""
        violations = []

        # Check tone consistency
        violations.extend(self._check_tone_consistency(response))

        # Check style consistency
        violations.extend(self._check_style_consistency(response))

        # Update history
        self.response_history.append(response)

        return violations

    def _check_tone_consistency(self, response: str) -> List[ConsistencyViolation]:
        """Check if tone matches persona"""
        violations = []

        expected_tone = self.persona['tone']

        if expected_tone == 'helpful':
            helpful_markers = ['certainly', 'of course', 'happy to help', 'let me']
            if not any(marker in response.lower() for marker in helpful_markers):
                violations.append(ConsistencyViolation(
                    violation_type='tone_inconsistency',
                    severity='low',
                    description="Response doesn't match helpful persona",
                    location='response_tone',
                    confidence=0.3
                ))

        return violations

    def _check_style_consistency(self, response: str) -> List[ConsistencyViolation]:
        """Check if writing style is consistent"""
        violations = []

        if not self.response_history:
            return violations

        # Compare sentence length with history
        current_avg_len = np.mean([len(s.split()) for s in response.split('.')])

        historical_lengths = []
        for hist_response in self.response_history[-5:]:
            lengths = [len(s.split()) for s in hist_response.split('.')]
            historical_lengths.extend(lengths)

        historical_avg = np.mean(historical_lengths) if historical_lengths else current_avg_len

        # Check if current is very different
        if abs(current_avg_len - historical_avg) > historical_avg * 0.5:
            violations.append(ConsistencyViolation(
                violation_type='style_inconsistency',
                severity='low',
                description=f"Sentence length differs from historical average",
                location='response_style',
                confidence=0.4
            ))

        return violations


class ConsistencyValidator:
    """
    Main validator that combines all consistency checks.
    """

    def __init__(self, persona: Optional[Dict] = None):
        self.self_checker = SelfConsistencyChecker()
        self.factual_checker = FactualConsistencyChecker()
        self.temporal_checker = TemporalConsistencyChecker()
        self.logical_checker = LogicalConsistencyChecker()
        self.persona_checker = PersonaConsistencyChecker(persona)

    def validate_response(
        self,
        response: str,
        check_types: Optional[List[ConsistencyType]] = None
    ) -> ConsistencyReport:
        """Validate response across all consistency dimensions"""
        if check_types is None:
            check_types = list(ConsistencyType)

        all_violations = []
        type_scores = {}

        # Self-consistency
        if ConsistencyType.SELF_CONSISTENCY in check_types:
            violations = self.self_checker.check(response)
            all_violations.extend(violations)
            type_scores['self_consistency'] = self._calculate_type_score(violations)

        # Factual consistency
        if ConsistencyType.FACTUAL_CONSISTENCY in check_types:
            violations = self.factual_checker.check(response)
            all_violations.extend(violations)
            type_scores['factual_consistency'] = self._calculate_type_score(violations)

        # Temporal consistency
        if ConsistencyType.TEMPORAL_CONSISTENCY in check_types:
            violations = self.temporal_checker.check(response)
            all_violations.extend(violations)
            type_scores['temporal_consistency'] = self._calculate_type_score(violations)

        # Logical consistency
        if ConsistencyType.LOGICAL_CONSISTENCY in check_types:
            violations = self.logical_checker.check(response)
            all_violations.extend(violations)
            type_scores['logical_consistency'] = self._calculate_type_score(violations)

        # Persona consistency
        if ConsistencyType.PERSONA_CONSISTENCY in check_types:
            violations = self.persona_checker.check(response)
            all_violations.extend(violations)
            type_scores['persona_consistency'] = self._calculate_type_score(violations)

        # Calculate overall score
        overall_score = np.mean(list(type_scores.values())) if type_scores else 1.0

        # Generate recommendations
        recommendations = self._generate_recommendations(all_violations)

        return ConsistencyReport(
            overall_score=overall_score,
            violations=all_violations,
            type_scores=type_scores,
            recommendations=recommendations
        )

    def _calculate_type_score(self, violations: List[ConsistencyViolation]) -> float:
        """Calculate consistency score for a type (0-1)"""
        if not violations:
            return 1.0

        # Weight violations by severity and confidence
        severity_weights = {'low': 0.2, 'medium': 0.5, 'high': 1.0}
        penalty = sum(
            severity_weights[v.severity] * v.confidence
            for v in violations
        )

        return max(0.0, 1.0 - min(1.0, penalty / 2.0))

    def _generate_recommendations(
        self,
        violations: List[ConsistencyViolation]
    ) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        violation_types = set(v.violation_type for v in violations)

        if 'contradiction' in violation_types:
            recommendations.append("Review response for contradictory statements")

        if 'factual_inaccuracy' in violation_types:
            recommendations.append("Verify factual claims against knowledge base")

        if 'temporal_contradiction' in violation_types:
            recommendations.append("Ensure consistency with conversation history")

        if 'non_sequitur' in violation_types:
            recommendations.append("Improve logical flow between statements")

        if 'tone_inconsistency' in violation_types:
            recommendations.append("Maintain consistent tone aligned with persona")

        return recommendations


def run_consistency_simulation():
    """Run consistency validation simulation"""
    print("=" * 60)
    print("POLLN Consistency Validation Simulation")
    print("=" * 60)

    validator = ConsistencyValidator()

    # Test responses
    test_responses = [
        {
            'response': "The Earth is definitely flat. This is a known fact.",
            'expected_issues': ['factual_inaccuracy']
        },
        {
            'response': "I always help users, but sometimes I don't.",
            'expected_issues': ['contradiction']
        },
        {
            'response': "Therefore, the solution is clear. Additionally, perhaps maybe we could consider.",
            'expected_issues': ['non_sequitur']
        },
        {
            'response': "Certainly! I'd be happy to help with that. Let me explain step by step.",
            'expected_issues': []
        },
        {
            'response': "The answer is 42. The answer is definitely 43.",
            'expected_issues': ['contradiction', 'numerical_inconsistency']
        }
    ]

    results = []

    for i, test in enumerate(test_responses):
        print(f"\nTest {i+1}: {test['response'][:50]}...")

        report = validator.validate_response(test['response'])

        print(f"  Overall Score: {report.overall_score:.3f}")
        print(f"  Violations: {len(report.violations)}")

        for violation in report.violations:
            print(f"    - {violation.violation_type}: {violation.description}")

        # Store results
        results.append({
            'response': test['response'],
            'overall_score': report.overall_score,
            'type_scores': report.type_scores,
            'num_violations': len(report.violations),
            'violation_types': [v.violation_type for v in report.violations]
        })

    # Test temporal consistency
    print("\n" + "=" * 60)
    print("Temporal Consistency Test")
    print("=" * 60)

    validator.temporal_checker.add_turn("User", "What's the capital of France?", 0)
    validator.temporal_checker.add_turn("Assistant", "The capital of France is Paris.", 1)
    validator.temporal_checker.add_turn("User", "Are you sure?", 2)

    response = "Actually, the capital of France is London."
    report = validator.validate_response(response)

    print(f"\nResponse: {response}")
    print(f"Overall Score: {report.overall_score:.3f}")
    print(f"Violations: {len(report.violations)}")

    # Calculate metrics
    print("\n" + "=" * 60)
    print("Consistency Metrics")
    print("=" * 60)

    total_tests = len(results)
    tests_with_violations = sum(1 for r in results if r['num_violations'] > 0)
    violation_rate = tests_with_violations / total_tests if total_tests > 0 else 0

    avg_score = np.mean([r['overall_score'] for r in results])

    print(f"\nTotal Tests: {total_tests}")
    print(f"Tests with Violations: {tests_with_violations}")
    print(f"Violation Rate: {violation_rate:.3f}")
    print(f"Average Score: {avg_score:.3f}")

    # Compile optimal configuration
    optimal_config = {
        'consistency_checks': {
            'self_consistency': {
                'enabled': True,
                'severity_threshold': 'medium'
            },
            'factual_consistency': {
                'enabled': True,
                'knowledge_base': True,
                'confidence_threshold': 0.7
            },
            'temporal_consistency': {
                'enabled': True,
                'history_window': 5,
                'severity_threshold': 'medium'
            },
            'logical_consistency': {
                'enabled': True,
                'check_circular_reasoning': True,
                'check_non_sequitur': True
            },
            'persona_consistency': {
                'enabled': True,
                'tone_checking': True,
                'style_checking': True
            }
        },
        'performance': {
            'expected_violation_rate': violation_rate,
            'expected_score': avg_score,
            'detection_confidence': 0.7
        },
        'optimization': {
            'auto_correction': True,
            'violation_filters': ['low'],  # Only show medium+ severity
            'max_violations_per_response': 10
        }
    }

    # Save results
    with open('simulations/domains/reasoning/consistency_results.json', 'w') as f:
        json.dump({
            'test_results': results,
            'metrics': {
                'violation_rate': violation_rate,
                'average_score': avg_score
            },
            'optimal_config': optimal_config
        }, f, indent=2)

    print("\nResults saved to consistency_results.json")

    return optimal_config


if __name__ == '__main__':
    run_consistency_simulation()
