"""
Tests for POLLN Benchmark System

Unit tests for benchmark suite, regression detection, and trend tracking.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from benchmark_suite import BenchmarkSuite, BenchmarkResult, BenchmarkConfig
    from regression_detector import RegressionDetector, RegressionSeverity
    from trend_tracker import TrendTracker, DataPoint
    from baseline_manager import BaselineManager, Baseline, BaselineStatus
    from benchmark_runner import BenchmarkRunner, BenchmarkJob
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    IMPORTS_AVAILABLE = False


class TestBenchmarkSuite(unittest.TestCase):
    """Tests for BenchmarkSuite"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Imports not available")

        self.temp_dir = tempfile.mkdtemp()
        self.suite = BenchmarkSuite(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_benchmark_result_creation(self):
        """Test BenchmarkResult dataclass"""
        result = BenchmarkResult(
            name="test_benchmark",
            operation="test_operation",
            iterations=100,
            total_time=1.0,
            avg_latency_ms=10.0,
            min_latency_ms=5.0,
            max_latency_ms=20.0,
            p50_latency_ms=10.0,
            p95_latency_ms=15.0,
            p99_latency_ms=18.0,
            throughput_ops=100.0,
            memory_mb=50.0,
            cpu_percent=25.0,
            success_rate=1.0,
            metadata={}
        )

        self.assertEqual(result.name, "test_benchmark")
        self.assertEqual(result.throughput_ops, 100.0)
        self.assertTrue(result.to_dict())

    def test_benchmark_config_defaults(self):
        """Test BenchmarkConfig default values"""
        config = BenchmarkConfig(name="test")

        self.assertEqual(config.name, "test")
        self.assertEqual(config.warmup_iterations, 10)
        self.assertEqual(config.benchmark_iterations, 100)

    @patch('benchmark_suite.psutil.Process')
    def test_agent_creation_benchmark(self, mock_process):
        """Test agent creation benchmark"""
        mock_proc = Mock()
        mock_proc.memory_info.return_value.rss = 1024 * 1024 * 100  # 100MB
        mock_proc.cpu_percent.return_value = 25.0
        mock_process.return_value = mock_proc

        result = self.suite.benchmark_agent_creation()

        self.assertIsNotNone(result)
        self.assertEqual(result.name, "agent_creation")
        self.assertGreater(result.throughput_ops, 0)

    def test_save_results(self):
        """Test saving benchmark results to JSON"""
        # Add a mock result
        result = BenchmarkResult(
            name="test",
            operation="test",
            iterations=10,
            total_time=1.0,
            avg_latency_ms=10.0,
            min_latency_ms=5.0,
            max_latency_ms=20.0,
            p50_latency_ms=10.0,
            p95_latency_ms=15.0,
            p99_latency_ms=18.0,
            throughput_ops=10.0,
            memory_mb=10.0,
            cpu_percent=10.0,
            success_rate=1.0,
            metadata={}
        )
        self.suite.results.append(result)

        output_path = self.suite.save_results("test_results.json")

        self.assertTrue(output_path.exists())
        with open(output_path, 'r') as f:
            data = json.load(f)
            self.assertIn("results", data)
            self.assertEqual(len(data["results"]), 1)


class TestRegressionDetector(unittest.TestCase):
    """Tests for RegressionDetector"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Imports not available")

        self.temp_dir = tempfile.mkdtemp()
        self.baseline_dir = Path(self.temp_dir) / "baselines"
        self.current_dir = Path(self.temp_dir) / "current"
        self.baseline_dir.mkdir()
        self.current_dir.mkdir()

        # Create baseline file
        self.baseline_data = {
            "timestamp": time.time(),
            "results": [
                {
                    "name": "test_benchmark",
                    "avg_latency_ms": 100.0,
                    "p95_latency_ms": 150.0,
                    "p99_latency_ms": 180.0,
                    "throughput_ops": 1000.0,
                    "memory_mb": 100.0
                }
            ]
        }

        with open(self.baseline_dir / "baseline.json", 'w') as f:
            json.dump(self.baseline_data, f)

        self.detector = RegressionDetector(
            baseline_dir=str(self.baseline_dir),
            current_dir=str(self.current_dir)
        )

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_severity_determination(self):
        """Test regression severity determination"""
        # Critical regression (>50%)
        severity = self.detector.determine_severity(60.0)
        self.assertEqual(severity, RegressionSeverity.CRITICAL)

        # High regression (20-50%)
        severity = self.detector.determine_severity(30.0)
        self.assertEqual(severity, RegressionSeverity.HIGH)

        # Medium regression (10-20%)
        severity = self.detector.determine_severity(15.0)
        self.assertEqual(severity, RegressionSeverity.MEDIUM)

        # Low regression (5-10%)
        severity = self.detector.determine_severity(7.0)
        self.assertEqual(severity, RegressionSeverity.LOW)

        # No regression (<5%)
        severity = self.detector.determine_severity(3.0)
        self.assertEqual(severity, RegressionSeverity.NONE)

    def test_metric_comparison(self):
        """Test metric comparison logic"""
        # Latency comparison (lower is better)
        comp = self.detector.compare_metric(100.0, 120.0, "latency", True)
        self.assertTrue(comp["is_regression"])
        self.assertEqual(comp["percent_change"], 20.0)

        # Throughput comparison (higher is better)
        comp = self.detector.compare_metric(1000.0, 800.0, "throughput", False)
        self.assertTrue(comp["is_regression"])
        self.assertEqual(comp["percent_change"], 20.0)

    def test_regression_detection(self):
        """Test regression detection"""
        # Create current results with regression
        current_data = {
            "timestamp": time.time(),
            "results": [
                {
                    "name": "test_benchmark",
                    "avg_latency_ms": 130.0,  # 30% increase - regression
                    "p95_latency_ms": 195.0,  # 30% increase
                    "p99_latency_ms": 234.0,  # 30% increase
                    "throughput_ops": 700.0,  # 30% decrease - regression
                    "memory_mb": 100.0
                }
            ]
        }

        with open(self.current_dir / "current.json", 'w') as f:
            json.dump(current_data, f)

        result = self.detector.check_regressions(
            baseline_file="baseline.json",
            current_file="current.json"
        )

        self.assertIsNotNone(result)
        self.assertGreater(len(result.regressions), 0)
        self.assertIn("HIGH", [r.severity.value for r in result.regressions])


class TestTrendTracker(unittest.TestCase):
    """Tests for TrendTracker"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Imports not available")

        self.temp_dir = tempfile.mkdtemp()
        self.history_dir = Path(self.temp_dir) / "history"
        self.history_dir.mkdir()

        self.tracker = TrendTracker(history_dir=str(self.history_dir))

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_data_point_creation(self):
        """Test DataPoint creation"""
        point = DataPoint(
            timestamp=time.time(),
            commit_hash="abc123",
            branch="main",
            value=100.0,
            metadata={}
        )

        self.assertEqual(point.commit_hash, "abc123")
        self.assertEqual(point.value, 100.0)
        self.assertTrue(point.to_dict())

    def test_add_data_point(self):
        """Test adding data points to time series"""
        self.tracker._add_data_point(
            "test_metric",
            time.time(),
            "abc123",
            "main",
            {"avg_latency_ms": 100.0}
        )

        self.assertIn("test_metric_avg_latency", self.tracker.time_series)
        self.assertEqual(len(self.tracker.time_series["test_metric_avg_latency"]), 1)

    def test_anomaly_detection(self):
        """Test anomaly detection in time series"""
        # Create data points with one anomaly
        points = [
            DataPoint(time.time() - i, f"commit{i}", "main", 100.0, {})
            for i in range(10)
        ]
        # Add anomaly
        points.append(DataPoint(time.time() - 10, "commit_anomaly", "main", 200.0, {}))

        anomalies = self.tracker._detect_anomalies(points)

        # Should detect the outlier
        self.assertGreater(len(anomalies), 0)


class TestBaselineManager(unittest.TestCase):
    """Tests for BaselineManager"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Imports not available")

        self.temp_dir = tempfile.mkdtemp()
        self.baseline_dir = Path(self.temp_dir) / "baselines"
        self.current_dir = Path(self.temp_dir) / "current"
        self.baseline_dir.mkdir()
        self.current_dir.mkdir()

        self.manager = BaselineManager(
            baseline_dir=str(self.baseline_dir),
            current_dir=str(self.current_dir)
        )

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_baseline(self):
        """Test creating a baseline"""
        # Create current results file
        current_data = {
            "run_id": "test_run",
            "timestamp": time.time(),
            "results": [
                {
                    "name": "test",
                    "avg_latency_ms": 100.0
                }
            ]
        }

        with open(self.current_dir / "results.json", 'w') as f:
            json.dump(current_data, f)

        baseline = self.manager.create_baseline(
            name="test_baseline",
            results_file="results.json",
            description="Test baseline"
        )

        self.assertIsNotNone(baseline)
        self.assertEqual(baseline.name, "test_baseline")
        self.assertEqual(baseline.status, BaselineStatus.ACTIVE)

    def test_get_baseline(self):
        """Test retrieving a baseline"""
        # Create baseline
        current_data = {
            "run_id": "test_run",
            "timestamp": time.time(),
            "results": []
        }

        with open(self.current_dir / "results.json", 'w') as f:
            json.dump(current_data, f)

        self.manager.create_baseline(
            name="test_baseline",
            results_file="results.json"
        )

        # Retrieve it
        baseline = self.manager.get_baseline("test_baseline")
        self.assertIsNotNone(baseline)
        self.assertEqual(baseline.name, "test_baseline")

    def test_set_active_baseline(self):
        """Test setting active baseline"""
        # Create two baselines
        current_data = {
            "run_id": "test_run",
            "timestamp": time.time(),
            "results": []
        }

        with open(self.current_dir / "results.json", 'w') as f:
            json.dump(current_data, f)

        self.manager.create_baseline(
            name="baseline1",
            results_file="results.json"
        )

        with open(self.current_dir / "results2.json", 'w') as f:
            json.dump(current_data, f)

        self.manager.create_baseline(
            name="baseline2",
            results_file="results2.json"
        )

        # Set baseline2 as active
        self.manager.set_active_baseline("baseline2")

        baseline1 = self.manager.get_baseline("baseline1")
        baseline2 = self.manager.get_baseline("baseline2")

        self.assertEqual(baseline1.status, BaselineStatus.ARCHIVED)
        self.assertEqual(baseline2.status, BaselineStatus.ACTIVE)


class TestBenchmarkRunner(unittest.TestCase):
    """Tests for BenchmarkRunner"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Imports not available")

        self.temp_dir = tempfile.mkdtemp()
        self.runner = BenchmarkRunner(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_default_jobs(self):
        """Test creating default benchmark jobs"""
        jobs = self.runner.create_default_jobs(scale="small")

        self.assertGreater(len(jobs), 0)

        # Check that all categories are represented
        categories = set(job.category for job in jobs)
        self.assertIn("agents", categories)
        self.assertIn("colony", categories)
        self.assertIn("learning", categories)
        self.assertIn("kv_cache", categories)

    def test_cache_key_generation(self):
        """Test cache key generation"""
        job = BenchmarkJob(
            name="test",
            category="agents",
            scale="small",
            script="test.py",
            args={"param": "value"}
        )

        key1 = self.runner.get_cache_key(job)
        key2 = self.runner.get_cache_key(job)

        self.assertEqual(key1, key2)

        # Different job should have different key
        job2 = BenchmarkJob(
            name="test2",
            category="agents",
            scale="small",
            script="test.py",
            args={}
        )

        key3 = self.runner.get_cache_key(job2)
        self.assertNotEqual(key1, key3)

    def test_run_id_generation(self):
        """Test unique run ID generation"""
        run_id1 = self.runner.generate_run_id()
        time.sleep(0.01)  # Small delay
        run_id2 = self.runner.generate_run_id()

        self.assertNotEqual(run_id1, run_id2)
        self.assertTrue(run_id1.startswith("run_"))
        self.assertTrue(run_id2.startswith("run_"))


class TestIntegration(unittest.TestCase):
    """Integration tests for the benchmark system"""

    def setUp(self):
        """Set up test fixtures"""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Imports not available")

        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_benchmark_workflow(self):
        """Test complete benchmark workflow"""
        # This is a simplified integration test
        output_dir = Path(self.temp_dir) / "output"
        output_dir.mkdir()

        suite = BenchmarkSuite(output_dir=str(output_dir))

        # Run a simple benchmark
        result = suite.benchmark_agent_creation()

        self.assertIsNotNone(result)
        self.assertGreater(result.throughput_ops, 0)

        # Save results
        result_file = suite.save_results()
        self.assertTrue(result_file.exists())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    if IMPORTS_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestBenchmarkSuite))
        suite.addTests(loader.loadTestsFromTestCase(TestRegressionDetector))
        suite.addTests(loader.loadTestsFromTestCase(TestTrendTracker))
        suite.addTests(loader.loadTestsFromTestCase(TestBaselineManager))
        suite.addTests(loader.loadTestsFromTestCase(TestBenchmarkRunner))
        suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run_tests()
