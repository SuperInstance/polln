"""
Code-Specific Metrics for POLLN Optimization

Implements code quality metrics and reward functions for:
- Cyclomatic complexity
- Maintainability index
- Test coverage
- Code smell detection
- Security score

These metrics are used to train value networks for code quality prediction.
"""

import ast
import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    COVERAGE = "coverage"
    SECURITY = "security"
    QUALITY = "quality"


@dataclass
class CodeMetric:
    """A code quality metric"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    normalized_value: float  # 0-1, higher is better
    weight: float  # Importance in overall score


@dataclass
class MetricReport:
    """Report of all metrics for a codebase"""
    file_path: str
    metrics: List[CodeMetric]
    overall_score: float
    issues_found: List[str]
    recommendations: List[str]


class CyclomaticComplexityAnalyzer:
    """Calculates cyclomatic complexity"""

    def calculate(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        try:
            tree = ast.parse(code)

            complexity = 1  # Base complexity

            for node in ast.walk(tree):
                if isinstance(node, (
                    ast.If, ast.While, ast.For,
                    ast.ExceptHandler, ast.With,
                    ast.BoolOp
                )):
                    complexity += 1
                elif isinstance(node, ast.ListComp) or isinstance(node, ast.DictComp):
                    complexity += 1

            return complexity

        except Exception:
            return 1

    def normalize(self, complexity: int) -> float:
        """Normalize complexity to 0-1 scale"""
        # Complexity > 20 is considered bad
        return max(0.0, min(1.0, 1.0 - (complexity / 20.0)))

    def get_function_complexity(self, code: str) -> Dict[str, int]:
        """Get complexity per function"""
        try:
            tree = ast.parse(code)
            complexities = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_complexity = 1  # Base complexity

                    # Count decision points
                    for child in ast.walk(node):
                        if isinstance(child, (
                            ast.If, ast.While, ast.For,
                            ast.ExceptHandler, ast.BoolOp
                        )):
                            func_complexity += 1

                    complexities[node.name] = func_complexity

            return complexities

        except Exception:
            return {}


class MaintainabilityIndexAnalyzer:
    """Calculates maintainability index"""

    def calculate(self, code: str) -> float:
        """Calculate maintainability index (0-1, higher is better)"""
        try:
            tree = ast.parse(code)
            lines = code.split("\n")

            # Factors affecting maintainability
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
            code_lines = total_lines - blank_lines - comment_lines

            # Average line length
            line_lengths = [len(line) for line in lines if line.strip()]
            avg_line_length = np.mean(line_lengths) if line_lengths else 0
            long_lines = sum(1 for length in line_lengths if length > 100)

            # Function metrics
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            avg_function_length = 0
            if functions:
                function_lengths = [
                    (n.end_lineno - n.lineno)
                    for n in functions
                    if hasattr(n, 'end_lineno') and n.lineno
                ]
                avg_function_length = np.mean(function_lengths) if function_lengths else 0

            # Calculate maintainability score
            # Higher is better
            length_penalty = min(1.0, long_lines / total_lines) if total_lines > 0 else 0
            function_penalty = min(1.0, avg_function_length / 50)
            line_length_penalty = min(1.0, avg_line_length / 100)

            maintainability = 1.0 - (
                length_penalty * 0.3 +
                function_penalty * 0.4 +
                line_length_penalty * 0.3
            )

            return max(0.0, min(1.0, maintainability))

        except Exception:
            return 0.5


class TestCoverageAnalyzer:
    """Estimates test coverage"""

    def estimate_coverage(self, code: str, test_code: Optional[str] = None) -> float:
        """Estimate test coverage (0-1)"""
        if not test_code:
            return 0.0

        try:
            tree = ast.parse(code)
            test_tree = ast.parse(test_code)

            # Get functions in main code
            functions = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    for method in ast.walk(node):
                        if isinstance(method, ast.FunctionDef):
                            functions.add(f"{node.name}.{method.name}")

            # Get functions called in tests
            tested_functions = set()
            for node in ast.walk(test_tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        tested_functions.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        tested_functions.add(node.func.attr)

            if not functions:
                return 0.0

            coverage = len(tested_functions & functions) / len(functions)
            return coverage

        except Exception:
            return 0.0


class SecurityAnalyzer:
    """Analyzes code for security issues"""

    def analyze(self, code: str) -> Tuple[float, List[str]]:
        """Analyze security and return score and issues"""
        issues = []
        score = 1.0

        lines = code.split("\n")

        # Check for security issues
        for i, line in enumerate(lines, 1):
            # Dangerous functions
            if "eval(" in line:
                issues.append(f"Line {i}: Use of eval() is dangerous")
                score -= 0.3
            if "exec(" in line:
                issues.append(f"Line {i}: Use of exec() is dangerous")
                score -= 0.3

            # Hardcoded secrets
            if re.search(r'password\s*=\s*["\']', line, re.IGNORECASE):
                issues.append(f"Line {i}: Hardcoded password detected")
                score -= 0.2
            if re.search(r'api[_-]?key\s*=\s*["\']', line, re.IGNORECASE):
                issues.append(f"Line {i}: Hardcoded API key detected")
                score -= 0.2
            if re.search(r'secret\s*=\s*["\']', line, re.IGNORECASE):
                issues.append(f"Line {i}: Hardcoded secret detected")
                score -= 0.15

            # SQL injection risk
            if re.search(r'f["\'].*SELECT.*{', line, re.IGNORECASE):
                issues.append(f"Line {i}: Potential SQL injection")
                score -= 0.15

            # Weak random
            if "random.random()" in line or "random.choice(" in line:
                issues.append(f"Line {i}: Use secrets module for cryptography")
                score -= 0.05

        return max(0.0, score), issues


class CodeSmellDetector:
    """Detects code smells"""

    def detect(self, code: str) -> List[str]:
        """Detect code smells"""
        smells = []

        try:
            tree = ast.parse(code)
            lines = code.split("\n")

            # Long functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'end_lineno') and node.lineno:
                        length = node.end_lineno - node.lineno
                        if length > 30:
                            smells.append(f"Function '{node.name}' is too long ({length} lines)")

            # Long parameter list
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 5:
                        smells.append(f"Function '{node.name}' has too many parameters ({len(node.args.args)})")

            # Duplicate code
            seen_blocks = {}
            for i in range(len(lines) - 3):
                block = "\n".join(lines[i:i+3])
                if block in seen_blocks:
                    smells.append(f"Duplicate code block at lines {seen_blocks[block][0]} and {i+1}")
                else:
                    seen_blocks[block] = (i, block)

            # Poor naming
            poor_names = ['tmp', 'temp', 'data', 'info', 'val', 'var']
            for i, line in enumerate(lines, 1):
                for name in poor_names:
                    if re.search(rf'\b{name}\s*=', line):
                        smells.append(f"Line {i}: Variable '{name}' has unclear name")

        except Exception:
            pass

        return smells


class RewardFunction:
    """Reward functions for code quality"""

    def __init__(self):
        self.weights = {
            "correctness": 0.5,
            "test_pass_rate": 0.3,
            "maintainability": 0.1,
            "security": 0.1
        }

    def calculate_reward(self, metrics: List[CodeMetric]) -> float:
        """Calculate overall reward from metrics"""
        reward = 0.0

        for metric in metrics:
            category = metric.metric_type.value
            if category in self.weights:
                reward += metric.normalized_value * self.weights[category]

        return reward

    def calculate_td_target(
        self,
        current_reward: float,
        future_value: float,
        gamma: float = 0.99
    ) -> float:
        """Calculate TD(lambda) target for value network training"""
        return current_reward + gamma * future_value

    def create_feature_vector(self, code: str) -> np.ndarray:
        """Create feature vector for value network input"""
        analyzers = {
            "complexity": CyclomaticComplexityAnalyzer(),
            "maintainability": MaintainabilityIndexAnalyzer(),
            "security": SecurityAnalyzer(),
        }

        features = []

        # Complexity
        complexity = analyzers["complexity"].calculate(code)
        features.append(analyzers["complexity"].normalize(complexity))

        # Maintainability
        maintainability = analyzers["maintainability"].calculate(code)
        features.append(maintainability)

        # Security
        security_score, _ = analyzers["security"].analyze(code)
        features.append(security_score)

        # Code length
        lines = len(code.split("\n"))
        features.append(min(1.0, lines / 500))

        # Comment ratio
        comment_lines = sum(1 for line in code.split("\n") if line.strip().startswith("#"))
        comment_ratio = comment_lines / lines if lines > 0 else 0
        features.append(comment_ratio)

        return np.array(features)


class CodeMetricsAnalyzer:
    """Main analyzer combining all metrics"""

    def __init__(self):
        self.complexity_analyzer = CyclomaticComplexityAnalyzer()
        self.maintainability_analyzer = MaintainabilityIndexAnalyzer()
        self.coverage_analyzer = TestCoverageAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.smell_detector = CodeSmellDetector()
        self.reward_function = RewardFunction()

    def analyze(self, file_path: str, code: str, test_code: Optional[str] = None) -> MetricReport:
        """Analyze code and generate comprehensive report"""
        metrics = []
        issues = []
        recommendations = []

        # Calculate complexity
        complexity = self.complexity_analyzer.calculate(code)
        metrics.append(CodeMetric(
            metric_id="complexity",
            metric_type=MetricType.COMPLEXITY,
            name="Cyclomatic Complexity",
            value=complexity,
            normalized_value=self.complexity_analyzer.normalize(complexity),
            weight=0.2
        ))

        # Calculate maintainability
        maintainability = self.maintainability_analyzer.calculate(code)
        metrics.append(CodeMetric(
            metric_id="maintainability",
            metric_type=MetricType.MAINTAINABILITY,
            name="Maintainability Index",
            value=maintainability,
            normalized_value=maintainability,
            weight=0.3
        ))

        # Estimate coverage
        coverage = self.coverage_analyzer.estimate_coverage(code, test_code)
        metrics.append(CodeMetric(
            metric_id="coverage",
            metric_type=MetricType.COVERAGE,
            name="Test Coverage",
            value=coverage,
            normalized_value=coverage,
            weight=0.3
        ))

        # Analyze security
        security_score, security_issues = self.security_analyzer.analyze(code)
        metrics.append(CodeMetric(
            metric_id="security",
            metric_type=MetricType.SECURITY,
            name="Security Score",
            value=security_score,
            normalized_value=security_score,
            weight=0.2
        ))
        issues.extend(security_issues)

        # Detect code smells
        smells = self.smell_detector.detect(code)
        issues.extend(smells)

        # Generate recommendations
        if complexity > 15:
            recommendations.append("Consider breaking down complex functions")
        if maintainability < 0.5:
            recommendations.append("Improve code structure and documentation")
        if coverage < 0.5:
            recommendations.append("Increase test coverage")
        if security_score < 0.7:
            recommendations.append("Address security vulnerabilities")

        # Calculate overall score
        overall_score = self.reward_function.calculate_reward(metrics)

        return MetricReport(
            file_path=file_path,
            metrics=metrics,
            overall_score=overall_score,
            issues_found=issues,
            recommendations=recommendations
        )

    def create_value_network_config(self) -> Dict:
        """Create value network configuration for code quality"""
        return {
            "input_features": [
                "complexity_score",
                "maintainability_score",
                "security_score",
                "coverage_score",
                "code_length",
                "comment_ratio",
                "function_count",
                "class_count"
            ],
            "output": "predicted_quality",
            "loss_function": "mse",
            "optimizer": "adam",
            "learning_rate": 0.001,
            "hidden_layers": [64, 32, 16],
            "activation": "relu",
            "reward_weights": {
                "correctness": 0.5,
                "test_pass_rate": 0.3,
                "maintainability": 0.1,
                "security": 0.1
            },
            "discount_factor": 0.99,
            "td_lambda": 0.9
        }


def generate_quality_value_network_config() -> str:
    """Generate TypeScript configuration for value network"""
    config = """
export const CODE_QUALITY_VALUE_CONFIG = {
  // Input features for value network
  features: [
    'complexity_score',
    'maintainability_score',
    'security_score',
    'coverage_score',
    'code_length',
    'comment_ratio',
    'function_count',
    'class_count'
  ],

  // Reward function weights
  rewardWeights: {
    correctness: 0.5,
    test_pass_rate: 0.3,
    maintainability: 0.1,
    security: 0.1
  },

  // Network architecture
  network: {
    inputSize: 8,
    hiddenLayers: [64, 32, 16],
    outputSize: 1,
    activation: 'relu',
    outputActivation: 'sigmoid'
  },

  // Training parameters
  training: {
    lossFunction: 'mse',
    optimizer: 'adam',
    learningRate: 0.001,
    batchSize: 32,
    epochs: 100
  },

  // TD(lambda) parameters
  tdLambda: {
    lambda: 0.9,
    gamma: 0.99
  },

  // Quality thresholds
  thresholds: {
    excellent: 0.9,
    good: 0.7,
    acceptable: 0.5,
    poor: 0.3
  }
};
"""

    return config


if __name__ == "__main__":
    # Test the analyzers
    sample_code = """
def process_data(data):
    tmp = []
    for item in data:
        val = item * 2
        tmp.append(val)
    return tmp

def calculate_metrics(metrics):
    info = {}
    for key, value in metrics.items():
        info[key] = value * 100
    return info

def main():
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    print(result)

if __name__ == '__main__':
    main()
"""

    test_code = """
def test_process_data():
    data = [1, 2, 3]
    result = process_data(data)
    assert result == [2, 4, 6]
"""

    analyzer = CodeMetricsAnalyzer()
    report = analyzer.analyze("example.py", sample_code, test_code)

    print("="*80)
    print("CODE METRICS REPORT")
    print("="*80)
    print(f"Overall Score: {report.overall_score:.2f}")
    print("\nMetrics:")
    for metric in report.metrics:
        print(f"  {metric.name}: {metric.value:.2f} (normalized: {metric.normalized_value:.2f})")

    print("\nIssues Found:")
    for issue in report.issues_found:
        print(f"  - {issue}")

    print("\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")

    print("\n" + "="*80)
    print("VALUE NETWORK CONFIG")
    print("="*80)
    print(generate_quality_value_network_config())
