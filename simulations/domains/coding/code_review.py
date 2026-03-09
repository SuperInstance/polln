"""
Code Review Simulation for POLLN Optimization

Simulates code review workflows and optimizes POLLN agents for:
- Bug detection
- Security analysis
- Style checking
- Performance analysis

Metrics:
- Precision (correct bugs flagged / total flagged)
- Recall (correct bugs flagged / total bugs)
- F1 score
- False positive rate
"""

import re
import ast
import time
import numpy as np
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json


class IssueType(Enum):
    BUG = "bug"
    SECURITY = "security"
    STYLE = "style"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CodeIssue:
    """A code issue found during review"""
    issue_id: str
    issue_type: IssueType
    severity: Severity
    line_number: int
    message: str
    suggestion: str
    confidence: float  # 0-1


@dataclass
class ReviewResult:
    """Result of code review"""
    file_path: str
    issues_found: List[CodeIssue]
    review_time: float
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


@dataclass
class CodeSample:
    """A code sample for review"""
    sample_id: str
    file_path: str
    code: str
    language: str
    injected_issues: List[CodeIssue]  # Ground truth issues


class IssueDetector:
    """Detects various types of code issues"""

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[IssueType, List[Dict]]:
        """Load regex patterns for issue detection"""
        return {
            IssueType.BUG: [
                {
                    "pattern": r"== None",
                    "message": "Use 'is None' instead of '== None'",
                    "severity": Severity.LOW,
                    "confidence": 0.9
                },
                {
                    "pattern": r"except\s*:",
                    "message": "Bare except clause - should specify exception type",
                    "severity": Severity.HIGH,
                    "confidence": 0.95
                },
                {
                    "pattern": r"import\s+\*",
                    "message": "Wildcard import - can pollute namespace",
                    "severity": Severity.MEDIUM,
                    "confidence": 0.85
                },
                {
                    "pattern": r"\.append\(.*\)\[0\]",
                    "message": "Appending then accessing index 0 - use list initialization",
                    "severity": Severity.LOW,
                    "confidence": 0.7
                },
            ],
            IssueType.SECURITY: [
                {
                    "pattern": r"eval\s*\(",
                    "message": "Use of eval() is dangerous - can execute arbitrary code",
                    "severity": Severity.CRITICAL,
                    "confidence": 0.95
                },
                {
                    "pattern": r"exec\s*\(",
                    "message": "Use of exec() is dangerous - can execute arbitrary code",
                    "severity": Severity.CRITICAL,
                    "confidence": 0.95
                },
                {
                    "pattern": r"password\s*=.*['\"]",
                    "message": "Hardcoded password detected",
                    "severity": Severity.CRITICAL,
                    "confidence": 0.9
                },
                {
                    "pattern": r"api_key\s*=.*['\"]",
                    "message": "Hardcoded API key detected",
                    "severity": Severity.HIGH,
                    "confidence": 0.9
                },
                {
                    "pattern": r"random\.random\s*\(",
                    "message": "Use secrets module for cryptographic randomness",
                    "severity": Severity.MEDIUM,
                    "confidence": 0.7
                },
            ],
            IssueType.STYLE: [
                {
                    "pattern": r"\b[A-Z]{2,}\b",
                    "message": "Consider using lowercase for variable names",
                    "severity": Severity.INFO,
                    "confidence": 0.6
                },
                {
                    "pattern": r"def\s+\w+\s*\(\s*\w+\s*:\s*\)\s*:",
                    "message": "Empty type hints - consider removing",
                    "severity": Severity.INFO,
                    "confidence": 0.5
                },
                {
                    "pattern": r"#\s*TODO",
                    "message": "TODO comment found - consider creating issue",
                    "severity": Severity.INFO,
                    "confidence": 0.8
                },
            ],
            IssueType.PERFORMANCE: [
                {
                    "pattern": r"for\s+\w+\s+in\s+range\(len\(",
                    "message": "Use enumerate() instead of range(len())",
                    "severity": Severity.MEDIUM,
                    "confidence": 0.85
                },
                {
                    "pattern": r"\.strip\(\)\.lower\(\)",
                    "message": "Consider chaining methods efficiently",
                    "severity": Severity.LOW,
                    "confidence": 0.6
                },
                {
                    "pattern": r"list\s*\(\s*.*\.keys\(\)\s*\)",
                    "message": "Unnecessary list() call on keys()",
                    "severity": Severity.LOW,
                    "confidence": 0.7
                },
                {
                    "pattern": r"for\s+\w+\s+in\s+\w+\s*:\s*\n\s*\w+\.append\(",
                    "message": "Use list comprehension instead of loop with append",
                    "severity": Severity.MEDIUM,
                    "confidence": 0.8
                },
            ],
            IssueType.MAINTAINABILITY: [
                {
                    "pattern": r"def\s+\w+\([^)]{100,}",
                    "message": "Function has too many parameters",
                    "severity": Severity.MEDIUM,
                    "confidence": 0.9
                },
                {
                    "pattern": r"class\s+\w+:.{500,}",
                    "message": "Class is very long - consider splitting",
                    "severity": Severity.MEDIUM,
                    "confidence": 0.7
                },
                {
                    "pattern": r"if\s+.{100,}:",
                    "message": "Complex condition - consider extracting",
                    "severity": Severity.LOW,
                    "confidence": 0.6
                },
            ],
        }

    def detect_issues(self, code: str) -> List[CodeIssue]:
        """Detect issues in code"""
        issues = []
        lines = code.split("\n")

        for issue_type, patterns in self.patterns.items():
            for pattern_dict in patterns:
                pattern = pattern_dict["pattern"]
                message = pattern_dict["message"]
                severity = pattern_dict["severity"]
                confidence = pattern_dict["confidence"]

                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        issue = CodeIssue(
                            issue_id=f"{issue_type.value}_{line_num}",
                            issue_type=issue_type,
                            severity=severity,
                            line_number=line_num,
                            message=message,
                            suggestion=self._get_suggestion(issue_type, pattern),
                            confidence=confidence
                        )
                        issues.append(issue)

        return issues

    def _get_suggestion(self, issue_type: IssueType, pattern: str) -> str:
        """Get a suggestion for fixing the issue"""
        suggestions = {
            "== None": "Use 'is None' instead",
            "except:": "Specify exception type, e.g., 'except Exception:'",
            "import *": "Import specific modules instead",
            "eval(": "Use ast.literal_eval() or a safer alternative",
            "exec(": "Avoid exec() - refactor code",
            "for .* in range(len(": "Use 'for i, item in enumerate(items):' instead",
        }

        for key, suggestion in suggestions.items():
            if key in pattern:
                return suggestion

        return "Review and fix this issue"


class ValueNetwork:
    """Predicts code quality using learned value function"""

    def __init__(self):
        self.weights = {
            "bug_count": 2.0,
            "security_count": 5.0,
            "style_count": 0.5,
            "performance_count": 1.0,
            "maintainability_count": 1.5,
        }

    def predict_quality(self, issues: List[CodeIssue]) -> float:
        """Predict overall code quality (0-1, higher is better)"""
        # Count issues by type
        counts = {}
        for issue_type in IssueType:
            type_issues = [i for i in issues if i.issue_type == issue_type]
            counts[issue_type] = len(type_issues)

        # Calculate penalty score
        penalty = 0.0
        for issue_type, count in counts.items():
            weight = self.weights.get(issue_type, 1.0)
            penalty += weight * count

        # Convert to quality score (0-1)
        # Use exponential decay
        quality = np.exp(-penalty / 10.0)

        return quality

    def predict_issue_severity(self, issue: CodeIssue) -> float:
        """Predict the severity score of an issue"""
        base_scores = {
            Severity.CRITICAL: 1.0,
            Severity.HIGH: 0.8,
            Severity.MEDIUM: 0.5,
            Severity.LOW: 0.3,
            Severity.INFO: 0.1,
        }

        base = base_scores.get(issue.severity, 0.5)
        adjusted = base * issue.confidence

        return adjusted


class POLLNCodeReviewer:
    """Simulates POLLN code review with value network"""

    def __init__(
        self,
        model_size: str = "100M",
        expertise: str = "code_review",
        use_value_network: bool = True
    ):
        self.model_size = model_size
        self.expertise = expertise
        self.use_value_network = use_value_network
        self.detector = IssueDetector()
        self.value_network = ValueNetwork() if use_value_network else None

    def review(self, sample: CodeSample) -> ReviewResult:
        """Review a code sample"""
        start_time = time.time()

        # Detect issues
        issues_found = self.detector.detect_issues(sample.code)

        # Use value network to prioritize issues
        if self.value_network:
            issues_found = self._prioritize_issues(issues_found)

        review_time = time.time() - start_time

        # Calculate metrics against ground truth
        true_positives, false_positives, false_negatives = self._calculate_metrics(
            issues_found, sample.injected_issues
        )

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return ReviewResult(
            file_path=sample.file_path,
            issues_found=issues_found,
            review_time=review_time,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            precision=precision,
            recall=recall,
            f1=f1
        )

    def _prioritize_issues(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Prioritize issues using value network"""
        # Calculate priority score for each issue
        for issue in issues:
            issue.priority_score = self.value_network.predict_issue_severity(issue)

        # Sort by priority
        issues.sort(key=lambda i: i.priority_score, reverse=True)

        # Filter out low-priority issues
        threshold = 0.3
        return [i for i in issues if i.priority_score >= threshold]

    def _calculate_metrics(
        self,
        found_issues: List[CodeIssue],
        injected_issues: List[CodeIssue]
    ) -> Tuple[int, int, int]:
        """Calculate true positives, false positives, false negatives"""

        # For simplicity, match by line number and issue type
        found_set = {(i.line_number, i.issue_type) for i in found_issues}
        injected_set = {(i.line_number, i.issue_type) for i in injected_issues}

        true_positives = len(found_set & injected_set)
        false_positives = len(found_set - injected_set)
        false_negatives = len(injected_set - found_set)

        return true_positives, false_positives, false_negatives


# Add priority_score to CodeIssue
CodeIssue.priority_score = 0.0


def create_code_samples() -> List[CodeSample]:
    """Create code samples with injected issues for testing"""
    samples = [
        CodeSample(
            sample_id="review_1",
            file_path="example1.py",
            code="""
def process_data(data):
    result = []
    for i in range(len(data)):
        result.append(data[i] * 2)
    return result

def check_value(value):
    if value == None:
        return False
    return True

def execute_code(code_str):
    try:
        eval(code_str)
    except:
        pass
""",
            language="python",
            injected_issues=[
                CodeIssue("bug_1", IssueType.BUG, Severity.LOW, 6, "Use 'is None'", "", 1.0),
                CodeIssue("bug_2", IssueType.BUG, Severity.HIGH, 11, "Bare except", "", 1.0),
                CodeIssue("perf_1", IssueType.PERFORMANCE, Severity.MEDIUM, 3, "Use enumerate", "", 1.0),
                CodeIssue("sec_1", IssueType.SECURITY, Severity.CRITICAL, 13, "eval() usage", "", 1.0),
            ]
        ),
        CodeSample(
            sample_id="review_2",
            file_path="example2.py",
            code="""
import os
from api_utils import *

API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"

def authenticate(username, password):
    if password == PASSWORD:
        return True
    return False

def process_request(request):
    data = request.data
    for i in range(len(data)):
        print(data[i])

def random_token():
    import random
    return random.random()
""",
            language="python",
            injected_issues=[
                CodeIssue("sec_1", IssueType.SECURITY, Severity.CRITICAL, 4, "Hardcoded API key", "", 1.0),
                CodeIssue("sec_2", IssueType.SECURITY, Severity.CRITICAL, 5, "Hardcoded password", "", 1.0),
                CodeIssue("sec_3", IssueType.SECURITY, Severity.HIGH, 2, "Wildcard import", "", 1.0),
                CodeIssue("perf_1", IssueType.PERFORMANCE, Severity.MEDIUM, 12, "Use enumerate", "", 1.0),
                CodeIssue("sec_4", IssueType.SECURITY, Severity.MEDIUM, 17, "Use secrets", "", 1.0),
            ]
        ),
        CodeSample(
            sample_id="review_3",
            file_path="example3.py",
            code="""
class DataProcessor:
    def __init__(self, config, source, destination, format, encoding, compression, retry, timeout):
        self.config = config
        self.source = source
        self.destination = destination
        self.format = format
        self.encoding = encoding
        self.compression = compression
        self.retry = retry
        self.timeout = timeout

    def process(self, data):
        result = []
        for item in data:
            if item is not None and item != "" and len(item) > 0:
                processed = self._transform(item)
                result.append(processed)
        return result

    def _transform(self, item):
        # TODO: Implement proper transformation
        return item.upper()
""",
            language="python",
            injected_issues=[
                CodeIssue("maint_1", IssueType.MAINTAINABILITY, Severity.MEDIUM, 2, "Too many parameters", "", 1.0),
                CodeIssue("style_1", IssueType.STYLE, Severity.INFO, 17, "TODO comment", "", 1.0),
            ]
        ),
    ]

    return samples


def optimize_review_configuration() -> Dict:
    """Optimize review agent configuration"""
    results = {}

    for model_size in ["50M", "100M", "200M"]:
        for use_value_network in [True, False]:
            config_key = f"{model_size}_vn{use_value_network}"

            reviewer = POLLNCodeReviewer(
                model_size=model_size,
                use_value_network=use_value_network
            )

            samples = create_code_samples()
            config_results = []

            for sample in samples:
                result = reviewer.review(sample)
                config_results.append(result)

            avg_precision = np.mean([r.precision for r in config_results])
            avg_recall = np.mean([r.recall for r in config_results])
            avg_f1 = np.mean([r.f1 for r in config_results])
            avg_time = np.mean([r.review_time for r in config_results])

            results[config_key] = {
                "precision": avg_precision,
                "recall": avg_recall,
                "f1": avg_f1,
                "avg_time": avg_time,
                "efficiency": avg_f1 / avg_time if avg_time > 0 else 0
            }

    # Find optimal configuration
    optimal = max(results.items(), key=lambda x: x[1]["f1"])

    return {
        "all_results": results,
        "optimal_config": optimal[0],
        "optimal_f1": optimal[1]["f1"]
    }


def run_code_review_simulation() -> Dict:
    """Run the full code review simulation"""
    print("Running Code Review Simulation...")

    # Create reviewer
    reviewer = POLLNCodeReviewer(
        model_size="100M",
        expertise="code_review",
        use_value_network=True
    )

    # Create test samples
    samples = create_code_samples()

    # Review all samples
    results = []
    for sample in samples:
        print(f"\nReviewing sample: {sample.sample_id}")
        result = reviewer.review(sample)
        results.append(result)

        print(f"  Issues found: {len(result.issues_found)}")
        print(f"  True positives: {result.true_positives}")
        print(f"  False positives: {result.false_positives}")
        print(f"  False negatives: {result.false_negatives}")
        print(f"  Precision: {result.precision:.2f}")
        print(f"  Recall: {result.recall:.2f}")
        print(f"  F1: {result.f1:.2f}")

    # Optimize configuration
    optimization_results = optimize_review_configuration()

    # Compile final results
    simulation_results = {
        "total_samples": len(samples),
        "avg_precision": np.mean([r.precision for r in results]),
        "avg_recall": np.mean([r.recall for r in results]),
        "avg_f1": np.mean([r.f1 for r in results]),
        "avg_review_time": np.mean([r.review_time for r in results]),
        "avg_issues_found": np.mean([len(r.issues_found) for r in results]),
        "configuration_optimization": optimization_results,
        "recommendations": {
            "optimal_model_size": "100M",
            "use_value_network": True,
            "value_function": "code_quality",
            "min_confidence_threshold": 0.3,
            "max_issues_per_review": 50,
            "priority_filtering": True
        }
    }

    return simulation_results


if __name__ == "__main__":
    results = run_code_review_simulation()

    print("\n" + "="*80)
    print("CODE REVIEW SIMULATION RESULTS")
    print("="*80)
    print(f"Total Samples: {results['total_samples']}")
    print(f"Avg Precision: {results['avg_precision']:.2f}")
    print(f"Avg Recall: {results['avg_recall']:.2f}")
    print(f"Avg F1: {results['avg_f1']:.2f}")
    print(f"Avg Review Time: {results['avg_review_time']:.2f}s")
    print(f"Optimal Config: {results['configuration_optimization']['optimal_config']}")

    # Save results
    with open("code_review_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to code_review_results.json")
