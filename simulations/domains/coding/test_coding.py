"""
Test suite for coding domain simulations.

Tests all simulation modules to ensure they work correctly.
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code_generation import (
    POLLNCodeGenerator,
    CodeValidator,
    CodeTask,
    CodeType,
    Difficulty
)
from code_review import (
    POLLNCodeReviewer,
    CodeSample,
    IssueDetector,
    IssueType,
    Severity
)
from debugging_simulation import (
    POLLNDebugger,
    BugLocator,
    BugReport,
    BugType
)
from refactoring import (
    POLLNRefactoringAgent,
    CodeAnalyzer,
    RefactoringType
)
from code_metrics import (
    CodeMetricsAnalyzer,
    CyclomaticComplexityAnalyzer,
    MaintainabilityIndexAnalyzer
)


class TestCodeGeneration(unittest.TestCase):
    """Test code generation simulation"""

    def setUp(self):
        self.generator = POLLNCodeGenerator(
            temperature=0.3,
            checkpoints=15
        )

    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        self.assertEqual(self.generator.temperature, 0.3)
        self.assertEqual(self.generator.checkpoints, 15)
        self.assertIsNotNone(self.generator.validator)

    def test_generate_function(self):
        """Test function generation"""
        task = CodeTask(
            task_id="test_1",
            code_type=CodeType.FUNCTION,
            difficulty=Difficulty.EASY,
            description="Test function",
            requirements=["Return input"],
            test_cases=[]
        )

        result = self.generator.generate(task)

        self.assertIsNotNone(result)
        self.assertEqual(result.task_id, "test_1")
        self.assertIsInstance(result.generated_code, str)
        self.assertGreater(result.generation_time, 0)

    def test_validate_syntax(self):
        """Test syntax validation"""
        validator = CodeValidator()

        # Valid code
        valid_code = "def test(): return 1"
        ok, score = validator.validate_syntax(valid_code)
        self.assertTrue(ok)
        self.assertEqual(score, 1.0)

        # Invalid code
        invalid_code = "def test(: return 1"
        ok, score = validator.validate_syntax(invalid_code)
        self.assertFalse(ok)


class TestCodeReview(unittest.TestCase):
    """Test code review simulation"""

    def setUp(self):
        self.reviewer = POLLNCodeReviewer(
            model_size="100M",
            use_value_network=True
        )

    def test_reviewer_initialization(self):
        """Test reviewer initializes correctly"""
        self.assertEqual(self.reviewer.model_size, "100M")
        self.assertTrue(self.reviewer.use_value_network)
        self.assertIsNotNone(self.reviewer.detector)

    def test_detect_issues(self):
        """Test issue detection"""
        detector = IssueDetector()

        code = """
def test():
    password = "secret"
    eval(user_input)
    except:
        pass
"""

        issues = detector.detect_issues(code)

        # Should detect security issues
        security_issues = [i for i in issues if i.issue_type == IssueType.SECURITY]
        self.assertGreater(len(security_issues), 0)

        # Should detect bare except
        bug_issues = [i for i in issues if i.issue_type == IssueType.BUG]
        self.assertGreater(len(bug_issues), 0)

    def test_review_code_sample(self):
        """Test reviewing a code sample"""
        sample = CodeSample(
            sample_id="test_sample",
            file_path="test.py",
            code="def test(): return 1",
            language="python",
            injected_issues=[]
        )

        result = self.reviewer.review(sample)

        self.assertIsNotNone(result)
        self.assertEqual(result.file_path, "test.py")
        self.assertIsInstance(result.issues_found, list)


class TestDebugging(unittest.TestCase):
    """Test debugging simulation"""

    def setUp(self):
        self.debugger = POLLNDebugger(
            max_iterations=5,
            use_checkpoints=True
        )

    def test_debugger_initialization(self):
        """Test debugger initializes correctly"""
        self.assertEqual(self.debugger.max_iterations, 5)
        self.assertTrue(self.debugger.use_checkpoints)
        self.assertIsNotNone(self.debugger.locator)

    def test_locate_bug(self):
        """Test bug location"""
        locator = BugLocator()

        bug_report = BugReport(
            bug_id="test_bug",
            bug_type=BugType.RUNTIME,
            description="Test bug",
            error_message="IndexError: list index out of range",
            reproduction_steps=[],
            expected_behavior="",
            actual_behavior="",
            file_path="test.py",
            line_number=5
        )

        code = """
def test():
    data = []
    return data[0]
"""

        locations = locator.locate(code, bug_report, locator.strategies[0])

        self.assertIsInstance(locations, list)

    def test_debug_session(self):
        """Test debugging session"""
        bug_report = BugReport(
            bug_id="test_bug",
            bug_type=BugType.SYNTAX,
            description="Test bug",
            error_message="Syntax error",
            reproduction_steps=[],
            expected_behavior="",
            actual_behavior="",
            file_path="test.py",
            line_number=1
        )

        code = "# Test code\ndef test(): return 1"

        result = self.debugger.debug(code, bug_report)

        self.assertIsNotNone(result)
        self.assertEqual(result.bug_report.bug_id, "test_bug")
        self.assertLessEqual(result.total_iterations, 5)


class TestRefactoring(unittest.TestCase):
    """Test refactoring simulation"""

    def setUp(self):
        self.agent = POLLNRefactoringAgent(
            chunk_size=5,
            max_files=50
        )

    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.chunk_size, 5)
        self.assertEqual(self.agent.max_files, 50)
        self.assertIsNotNone(self.agent.analyzer)

    def test_analyze_file(self):
        """Test file analysis"""
        analyzer = CodeAnalyzer()

        code = """
def long_function():
    tmp = []
    for item in data:
        val = item * 2
        tmp.append(val)
    return tmp
"""

        opportunities = analyzer.analyze_file("test.py", code)

        self.assertIsInstance(opportunities, list)
        # Should detect some opportunities
        self.assertGreater(len(opportunities), 0)

    def test_refactor_file(self):
        """Test file refactoring"""
        code = """
def test():
    return 1
"""

        results, quality = self.agent.refactor_file("test.py", code)

        self.assertIsInstance(results, list)
        self.assertIsInstance(quality, float)


class TestCodeMetrics(unittest.TestCase):
    """Test code metrics"""

    def setUp(self):
        self.analyzer = CodeMetricsAnalyzer()

    def test_complexity_analyzer(self):
        """Test complexity analysis"""
        comp_analyzer = CyclomaticComplexityAnalyzer()

        # Simple code
        simple_code = "def test(): return 1"
        complexity = comp_analyzer.calculate(simple_code)
        self.assertEqual(complexity, 1)

        # Complex code
        complex_code = """
def test():
    if a:
        if b:
            if c:
                return 1
    return 0
"""
        complexity = comp_analyzer.calculate(complex_code)
        self.assertGreater(complexity, 1)

    def test_maintainability_analyzer(self):
        """Test maintainability analysis"""
        main_analyzer = MaintainabilityIndexAnalyzer()

        # Good code
        good_code = """
def well_named_function(input_data):
    \"\"\"Process input data efficiently.\"\"\"
    result = []
    for item in input_data:
        processed = item * 2
        result.append(processed)
    return result
"""

        maintainability = main_analyzer.calculate(good_code)
        self.assertGreater(maintainability, 0.5)

    def test_full_analysis(self):
        """Test complete code analysis"""
        code = """
def process(data):
    tmp = []
    for item in data:
        val = item * 2
        tmp.append(val)
    return tmp
"""

        test_code = """
def test_process():
    assert process([1, 2]) == [2, 4]
"""

        report = self.analyzer.analyze("test.py", code, test_code)

        self.assertIsNotNone(report)
        self.assertEqual(report.file_path, "test.py")
        self.assertIsInstance(report.metrics, list)
        self.assertIsInstance(report.overall_score, float)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_full_workflow(self):
        """Test complete coding workflow"""
        # This is a simplified integration test

        # 1. Generate code
        generator = POLLNCodeGenerator()
        task = CodeTask(
            task_id="integration_test",
            code_type=CodeType.FUNCTION,
            difficulty=Difficulty.EASY,
            description="Test",
            requirements=[],
            test_cases=[]
        )
        gen_result = generator.generate(task)
        self.assertIsNotNone(gen_result)

        # 2. Review generated code
        reviewer = POLLNCodeReviewer()
        sample = CodeSample(
            sample_id="integration_test",
            file_path="test.py",
            code=gen_result.generated_code,
            language="python",
            injected_issues=[]
        )
        review_result = reviewer.review(sample)
        self.assertIsNotNone(review_result)

        # 3. Analyze metrics
        analyzer = CodeMetricsAnalyzer()
        metrics_report = analyzer.analyze("test.py", gen_result.generated_code)
        self.assertIsNotNone(metrics_report)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
