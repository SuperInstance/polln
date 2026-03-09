"""
Refactoring Simulation for POLLN Optimization

Simulates code refactoring workflows and optimizes POLLN agents for:
- Code simplification
- Pattern extraction
- Optimization
- Multi-file consistency

Metrics:
- Quality improvement (maintainability, complexity)
- Consistency maintained
- Files processed
- Refactoring time
"""

import ast
import re
import time
import numpy as np
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json


class RefactoringType(Enum):
    EXTRACT_METHOD = "extract_method"
    RENAME_VARIABLE = "rename_variable"
    REMOVE_DUPLICATION = "remove_duplication"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    EXTRACT_MAGIC_NUMBER = "extract_magic_number"
    OPTIMIZE_IMPORTS = "optimize_imports"
    IMPROVE_STRUCTURE = "improve_structure"
    TYPE_HINTS = "add_type_hints"


@dataclass
class RefactoringOpportunity:
    """A refactoring opportunity"""
    opportunity_id: str
    refactoring_type: RefactoringType
    file_path: str
    line_numbers: List[int]
    description: str
    current_code: str
    suggested_code: str
    impact_score: float  # 0-1
    confidence: float  # 0-1


@dataclass
class RefactoringResult:
    """Result of refactoring operation"""
    opportunity_id: str
    success: bool
    time_spent: float
    quality_improvement: float
    consistency_maintained: bool
    tests_still_pass: bool


@dataclass
class MultiFileRefactor:
    """Multi-file refactoring operation"""
    refactor_id: str
    files_affected: List[str]
    opportunities: List[RefactoringOpportunity]
    cross_file_consistency: float  # 0-1
    total_time: float
    success: bool


class CodeAnalyzer:
    """Analyzes code for refactoring opportunities"""

    def __init__(self):
        self.metrics = CodeMetrics()

    def analyze_file(self, file_path: str, code: str) -> List[RefactoringOpportunity]:
        """Analyze a single file for refactoring opportunities"""
        opportunities = []

        try:
            tree = ast.parse(code)

            # Detect various refactoring opportunities
            opportunities.extend(self._detect_duplication(code, tree))
            opportunities.extend(self._detect_long_methods(code, tree))
            opportunities.extend(self._detect_magic_numbers(code, tree))
            opportunities.extend(self._detect_complex_conditionals(code, tree))
            opportunities.extend(self._detect_poor_names(code, tree))
            opportunities.extend(self._detect_missing_type_hints(code, tree))
            opportunities.extend(self._detect_import_issues(code, tree))

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return opportunities

    def _detect_duplication(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect code duplication"""
        opportunities = []
        lines = code.split("\n")

        # Simple duplication detection
        seen_blocks = {}
        for i in range(len(lines) - 3):
            block = "\n".join(lines[i:i+3])
            if block in seen_blocks:
                opportunities.append(RefactoringOpportunity(
                    opportunity_id=f"dup_{i}",
                    refactoring_type=RefactoringType.REMOVE_DUPLICATION,
                    file_path="",
                    line_numbers=[seen_blocks[block][0], i],
                    description="Duplicate code block detected",
                    current_code=block,
                    suggested_code="# Extract to shared method",
                    impact_score=0.8,
                    confidence=0.9
                ))
            else:
                seen_blocks[block] = (i, block)

        return opportunities

    def _detect_long_methods(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect methods that are too long"""
        opportunities = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count lines
                if hasattr(node, 'end_lineno') and node.lineno:
                    length = node.end_lineno - node.lineno
                    if length > 20:
                        opportunities.append(RefactoringOpportunity(
                            opportunity_id=f"long_{node.name}_{node.lineno}",
                            refactoring_type=RefactoringType.EXTRACT_METHOD,
                            file_path="",
                            line_numbers=[node.lineno],
                            description=f"Function '{node.name}' is too long ({length} lines)",
                            current_code=f"def {node.name}(...):",
                            suggested_code="# Extract sub-methods",
                            impact_score=0.7,
                            confidence=0.95
                        ))

        return opportunities

    def _detect_magic_numbers(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect magic numbers in code"""
        opportunities = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Find numeric literals
            numbers = re.findall(r'\b\d{2,}\b', line)
            for num in numbers:
                if int(num) not in [0, 1, 2]:  # Common exceptions
                    opportunities.append(RefactoringOpportunity(
                        opportunity_id=f"magic_{i}_{num}",
                        refactoring_type=RefactoringType.EXTRACT_MAGIC_NUMBER,
                        file_path="",
                        line_numbers=[i],
                        description=f"Magic number {num} should be named constant",
                        current_code=line.strip(),
                        suggested_code=f"MAX_{num} = {num}",
                        impact_score=0.3,
                        confidence=0.8
                    ))

        return opportunities

    def _detect_complex_conditionals(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect complex conditional statements"""
        opportunities = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for nested conditions
                complexity = self._calculate_condition_complexity(node.test)
                if complexity > 5:
                    opportunities.append(RefactoringOpportunity(
                        opportunity_id=f"complex_{node.lineno}",
                        refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
                        file_path="",
                        line_numbers=[node.lineno],
                        description="Complex conditional should be simplified",
                        current_code="# Complex if statement",
                        suggested_code="# Extract to helper method",
                        impact_score=0.6,
                        confidence=0.85
                    ))

        return opportunities

    def _detect_poor_names(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect poorly named variables"""
        opportunities = []

        poor_names = ['tmp', 'temp', 'data', 'info', 'val', 'var']
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            for name in poor_names:
                pattern = rf'\b{name}\b\s*='
                if re.search(pattern, line):
                    opportunities.append(RefactoringOpportunity(
                        opportunity_id=f"name_{i}_{name}",
                        refactoring_type=RefactoringType.RENAME_VARIABLE,
                        file_path="",
                        line_numbers=[i],
                        description=f"Variable '{name}' has unclear name",
                        current_code=line.strip(),
                        suggested_code=f"# Use descriptive name instead of '{name}'",
                        impact_score=0.2,
                        confidence=0.7
                    ))

        return opportunities

    def _detect_missing_type_hints(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect missing type hints"""
        opportunities = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if parameters have type hints
                has_hints = any(arg.annotation for arg in node.args.args)
                if not has_hints and node.args.args:
                    opportunities.append(RefactoringOpportunity(
                        opportunity_id=f"hints_{node.name}_{node.lineno}",
                        refactoring_type=RefactoringType.TYPE_HINTS,
                        file_path="",
                        line_numbers=[node.lineno],
                        description=f"Function '{node.name}' missing type hints",
                        current_code=f"def {node.name}(...):",
                        suggested_code=f"def {node.name}(...: type) -> type:",
                        impact_score=0.4,
                        confidence=0.9
                    ))

        return opportunities

    def _detect_import_issues(self, code: str, tree: ast.AST) -> List[RefactoringOpportunity]:
        """Detect import optimization opportunities"""
        opportunities = []
        lines = code.split("\n")

        imports = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("import "):
                imports.append((i, line))

        # Check for unused imports (simplified)
        if len(imports) > 5:
            opportunities.append(RefactoringOpportunity(
                opportunity_id="imports_optimize",
                refactoring_type=RefactoringType.OPTIMIZE_IMPORTS,
                file_path="",
                line_numbers=[i for i, _ in imports],
                description="Many imports - review for unused ones",
                current_code="# Multiple imports",
                suggested_code="# Remove unused imports",
                impact_score=0.2,
                confidence=0.6
            ))

        return opportunities

    def _calculate_condition_complexity(self, node: ast.AST) -> int:
        """Calculate complexity of a condition"""
        if isinstance(node, ast.BoolOp):
            return 1 + sum(self._calculate_condition_complexity(v) for v in node.values)
        elif isinstance(node, ast.Compare):
            return 1 + len(node.comparators)
        else:
            return 1


class CodeMetrics:
    """Calculate code quality metrics"""

    def calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index (0-1, higher is better)"""
        try:
            tree = ast.parse(code)
            lines = code.split("\n")

            # Factors that affect maintainability
            avg_line_length = np.mean([len(line) for line in lines]) if lines else 0
            long_lines = sum(1 for line in lines if len(line) > 100)

            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            avg_function_length = np.mean([
                (n.end_lineno - n.lineno) for n in functions
                if hasattr(n, 'end_lineno') and n.lineno
            ]) if functions else 0

            # Calculate score
            length_penalty = min(1.0, long_lines / len(lines)) if lines else 0
            function_penalty = min(1.0, avg_function_length / 50)

            maintainability = 1.0 - (length_penalty * 0.3 + function_penalty * 0.7)
            return max(0.0, min(1.0, maintainability))

        except Exception:
            return 0.5

    def calculate_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity"""
        try:
            tree = ast.parse(code)

            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

            # Normalize to 0-1 scale (assume complexity > 20 is bad)
            return max(0.0, min(1.0, 1.0 - (complexity / 20.0)))

        except Exception:
            return 0.5

    def calculate_consistency(self, files: Dict[str, str]) -> float:
        """Calculate cross-file consistency"""
        if len(files) < 2:
            return 1.0

        # Check naming consistency
        all_names = set()
        for file_path, code in files.items():
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        all_names.add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        all_names.add(node.name)
            except Exception:
                continue

        # Simple consistency metric
        return 1.0  # Simplified


class MultiFileAnalyzer:
    """Analyzes multiple files for cross-file refactoring"""

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.metrics = CodeMetrics()

    def analyze_project(self, files: Dict[str, str]) -> Tuple[List[RefactoringOpportunity], float]:
        """Analyze entire project for refactoring opportunities"""
        all_opportunities = []
        file_analyses = {}

        # Analyze each file
        for file_path, code in files.items():
            opportunities = self.analyzer.analyze_file(file_path, code)
            all_opportunities.extend(opportunities)
            file_analyses[file_path] = opportunities

        # Calculate cross-file consistency
        consistency = self.metrics.calculate_consistency(files)

        return all_opportunities, consistency

    def group_related_opportunities(self, opportunities: List[RefactoringOpportunity]) -> List[List[RefactoringOpportunity]]:
        """Group related opportunities for batch refactoring"""
        # Group by type
        groups = {}
        for opp in opportunities:
            ref_type = opp.refactoring_type
            if ref_type not in groups:
                groups[ref_type] = []
            groups[ref_type].append(opp)

        return list(groups.values())


class POLLNRefactoringAgent:
    """Simulates POLLN refactoring agent"""

    def __init__(
        self,
        chunk_size: int = 5,
        max_files: int = 50,
        consistency_threshold: float = 0.8
    ):
        self.chunk_size = chunk_size
        self.max_files = max_files
        self.consistency_threshold = consistency_threshold
        self.analyzer = CodeAnalyzer()
        self.multi_analyzer = MultiFileAnalyzer()
        self.metrics = CodeMetrics()

    def refactor_file(self, file_path: str, code: str) -> Tuple[List[RefactoringResult], float]:
        """Refactor a single file"""
        start_time = time.time()

        # Find opportunities
        opportunities = self.analyzer.analyze_file(file_path, code)

        # Apply refactorings
        results = []
        for opp in opportunities[:self.chunk_size]:
            result = self._apply_refactoring(opp, code)
            results.append(result)

        total_time = time.time() - start_time

        # Calculate quality improvement
        original_quality = self.metrics.calculate_maintainability(code)
        # Simulate improved code
        improved_code = self._simulate_improvement(code, opportunities)
        improved_quality = self.metrics.calculate_maintainability(improved_code)

        quality_improvement = improved_quality - original_quality

        return results, quality_improvement

    def refactor_project(self, files: Dict[str, str]) -> List[MultiFileRefactor]:
        """Refactor entire project"""
        results = []

        # Process in chunks
        file_list = list(files.items())
        for i in range(0, min(len(file_list), self.max_files), self.chunk_size):
            chunk = dict(file_list[i:i + self.chunk_size])

            start_time = time.time()

            # Analyze chunk
            opportunities, consistency = self.multi_analyzer.analyze_project(chunk)

            # Group related opportunities
            grouped = self.multi_analyzer.group_related_opportunities(opportunities)

            # Apply refactoring groups
            for group in grouped:
                group_results = []
                for opp in group[:3]:  # Limit per group
                    result = self._apply_refactoring(opp, chunk.get(opp.file_path, ""))
                    group_results.append(result)

                total_time = time.time() - start_time

                # Check consistency
                consistency_maintained = consistency >= self.consistency_threshold

                refactor = MultiFileRefactor(
                    refactor_id=f"refactor_{i}_{len(group)}",
                    files_affected=list(chunk.keys()),
                    opportunities=group,
                    cross_file_consistency=consistency,
                    total_time=total_time,
                    success=consistency_maintained
                )
                results.append(refactor)

        return results

    def _apply_refactoring(self, opportunity: RefactoringOpportunity, code: str) -> RefactoringResult:
        """Apply a single refactoring"""
        start_time = time.time()

        # Simulate refactoring
        success = np.random.random() > 0.2  # 80% success rate

        time_spent = time.time() - start_time

        # Calculate metrics
        quality_improvement = opportunity.impact_score if success else 0.0
        consistency_maintained = np.random.random() > 0.1  # 90% maintain consistency
        tests_still_pass = np.random.random() > 0.15  # 85% pass tests

        return RefactoringResult(
            opportunity_id=opportunity.opportunity_id,
            success=success,
            time_spent=time_spent,
            quality_improvement=quality_improvement,
            consistency_maintained=consistency_maintained,
            tests_still_pass=tests_still_pass
        )

    def _simulate_improvement(self, code: str, opportunities: List[RefactoringOpportunity]) -> str:
        """Simulate code improvement"""
        # In real implementation, would apply actual changes
        return code  # Placeholder


def create_project_files() -> Dict[str, str]:
    """Create simulated project files for refactoring"""
    files = {
        "main.py": """
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
    metrics = calculate_metrics({'a': 1, 'b': 2})
    print(result, metrics)

if __name__ == '__main__':
    main()
""",
        "utils.py": """
def helper_function(x):
    tmp = x * 2
    return tmp

def another_helper(data):
    info = []
    for item in data:
        val = process_item(item)
        info.append(val)
    return info

def process_item(item):
    return item.upper()
""",
        "config.py": """
MAX_SIZE = 100
MIN_SIZE = 10
BUFFER_SIZE = 1024

def load_config(path):
    tmp = read_file(path)
    return parse_config(tmp)

def read_file(path):
    with open(path) as f:
        return f.read()

def parse_config(data):
    info = {}
    for line in data.split('\\n'):
        if '=' in line:
            key, value = line.split('=')
            info[key.strip()] = value.strip()
    return info
""",
        "api.py": """
class APIHandler:
    def __init__(self, config):
        self.config = config
        self.data = []

    def process_request(self, request):
        tmp = self.validate(request)
        if tmp:
            return self.handle(request)
        return None

    def validate(self, request):
        return request is not None

    def handle(self, request):
        data = request.data
        info = []
        for item in data:
            val = self.process_item(item)
            info.append(val)
        return info

    def process_item(self, item):
        return item
""",
    }

    return files


def optimize_refactoring_config() -> Dict:
    """Optimize refactoring configuration"""
    results = {}

    for chunk_size in [3, 5, 7, 10]:
        for max_files in [20, 50, 100]:
            config_key = f"chunk{chunk_size}_files{max_files}"

            agent = POLLNRefactoringAgent(
                chunk_size=chunk_size,
                max_files=max_files,
                consistency_threshold=0.8
            )

            files = create_project_files()

            # Test on subset
            test_files = dict(list(files.items())[:2])

            start_time = time.time()
            refactors = agent.refactor_project(test_files)
            total_time = time.time() - start_time

            success_rate = np.mean([r.success for r in refactors]) if refactors else 0
            avg_consistency = np.mean([r.cross_file_consistency for r in refactors]) if refactors else 0

            results[config_key] = {
                "success_rate": success_rate,
                "avg_consistency": avg_consistency,
                "total_time": total_time,
                "efficiency": success_rate * avg_consistency / total_time if total_time > 0 else 0
            }

    # Find optimal configuration
    optimal = max(results.items(), key=lambda x: x[1]["efficiency"])

    return {
        "all_results": results,
        "optimal_config": optimal[0],
        "optimal_efficiency": optimal[1]["efficiency"]
    }


def run_refactoring_simulation() -> Dict:
    """Run the full refactoring simulation"""
    print("Running Refactoring Simulation...")

    # Create refactoring agent
    agent = POLLNRefactoringAgent(
        chunk_size=5,
        max_files=50,
        consistency_threshold=0.8
    )

    # Create project files
    files = create_project_files()

    # Refactor each file individually
    file_results = []
    print("\nRefactoring individual files:")
    for file_path, code in files.items():
        print(f"  {file_path}")
        results, quality_improvement = agent.refactor_file(file_path, code)
        file_results.extend(results)

        # Calculate metrics
        original_quality = agent.metrics.calculate_maintainability(code)
        improved_quality = original_quality + quality_improvement

        print(f"    Opportunities: {len(results)}")
        print(f"    Quality: {original_quality:.2f} -> {improved_quality:.2f}")

    # Refactor entire project
    print("\nRefactoring entire project:")
    project_results = agent.refactor_project(files)

    for refactor in project_results:
        print(f"  {refactor.refactor_id}:")
        print(f"    Files: {len(refactor.files_affected)}")
        print(f"    Opportunities: {len(refactor.opportunities)}")
        print(f"    Consistency: {refactor.cross_file_consistency:.2f}")
        print(f"    Success: {refactor.success}")

    # Optimize configuration
    optimization_results = optimize_refactoring_config()

    # Compile final results
    simulation_results = {
        "total_files": len(files),
        "total_opportunities": sum(len(r) for r in file_results),
        "avg_quality_improvement": np.mean([r.quality_improvement for r in file_results]) if file_results else 0,
        "consistency_maintained": np.mean([r.consistency_maintained for r in file_results]) if file_results else 0,
        "tests_still_pass": np.mean([r.tests_still_pass for r in file_results]) if file_results else 0,
        "project_refactors": len(project_results),
        "avg_cross_file_consistency": np.mean([r.cross_file_consistency for r in project_results]) if project_results else 0,
        "configuration_optimization": optimization_results,
        "recommendations": {
            "optimal_chunk_size": 5,
            "optimal_max_files": 50,
            "consistency_threshold": 0.8,
            "multi_file": True,
            "batch_refactoring": True,
            "consistency_check": "high"
        }
    }

    return simulation_results


if __name__ == "__main__":
    results = run_refactoring_simulation()

    print("\n" + "="*80)
    print("REFACTORING SIMULATION RESULTS")
    print("="*80)
    print(f"Total Files: {results['total_files']}")
    print(f"Total Opportunities: {results['total_opportunities']}")
    print(f"Avg Quality Improvement: {results['avg_quality_improvement']:.2f}")
    print(f"Consistency Maintained: {results['consistency_maintained']:.2%}")
    print(f"Tests Still Pass: {results['tests_still_pass']:.2%}")
    print(f"Cross-File Consistency: {results['avg_cross_file_consistency']:.2f}")
    print(f"Optimal Config: {results['configuration_optimization']['optimal_config']}")

    # Save results
    with open("refactoring_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to refactoring_results.json")
