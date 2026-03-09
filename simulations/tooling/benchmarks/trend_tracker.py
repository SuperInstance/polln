"""
Performance Trend Tracker

Tracks performance metrics over time (commits, branches) to identify
trends, anomalies, and predict future performance.
"""

import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from scipy import stats
    from scipy.signal import savgol_filter
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@dataclass
class DataPoint:
    """Single data point in time series"""
    timestamp: float
    commit_hash: str
    branch: str
    value: float
    metadata: Dict

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrendAnalysis:
    """Analysis of a metric trend"""
    metric_name: str
    slope: float  # Rate of change per day
    correlation: float  # Correlation coefficient
    is_significant: bool  # Statistically significant trend
    trend_direction: str  # "improving", "degrading", "stable"
    confidence: float  # Confidence in trend
    predictions: Dict[str, float]  # Future predictions
    anomalies: List[Dict]  # Detected anomalies

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrendReport:
    """Complete trend report for all metrics"""
    generated_at: str
    time_range: Dict[str, str]
    total_commits: int
    metrics_analyzed: int
    trends: Dict[str, TrendAnalysis]
    summary: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["trends"] = {
            k: v.to_dict() for k, v in self.trends.items()
        }
        return data


class TrendTracker:
    """
    Track performance trends over time.

    Features:
    - Time series analysis of metrics
    - Trend detection (improving/degrading/stable)
    - Anomaly detection (statistical outliers)
    - Future performance prediction
    - Visualization with trend lines
    - Multiple branch tracking
    """

    def __init__(
        self,
        history_dir: str = "reports/benchmarks/history",
        min_data_points: int = 5
    ):
        self.history_dir = Path(history_dir)
        self.min_data_points = min_data_points
        self.time_series: Dict[str, List[DataPoint]] = defaultdict(list)

    def load_historical_data(self) -> Dict[str, List[DataPoint]]:
        """Load all historical benchmark data"""

        if not self.history_dir.exists():
            print(f"Warning: History directory not found: {self.history_dir}")
            return {}

        # Load all JSON files in history directory
        for filepath in self.history_dir.glob("**/*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                timestamp = data.get("timestamp", time.time())
                commit_hash = data.get("commit_hash", "unknown")
                branch = data.get("branch", "main")

                for result in data.get("results", []):
                    name = result.get("name", "unknown")
                    self._add_data_point(name, timestamp, commit_hash, branch, result)

            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        return self.time_series

    def _add_data_point(
        self,
        metric_name: str,
        timestamp: float,
        commit_hash: str,
        branch: str,
        result: Dict
    ):
        """Add a data point to time series"""

        # Extract key metrics
        key_metrics = [
            ("avg_latency_ms", "avg_latency"),
            ("p95_latency_ms", "p95_latency"),
            ("p99_latency_ms", "p99_latency"),
            ("throughput_ops", "throughput"),
            ("memory_mb", "memory")
        ]

        for metric_key, metric_suffix in key_metrics:
            if metric_key in result:
                full_name = f"{metric_name}_{metric_suffix}"
                point = DataPoint(
                    timestamp=timestamp,
                    commit_hash=commit_hash,
                    branch=branch,
                    value=result[metric_key],
                    metadata=result
                )
                self.time_series[full_name].append(point)

    def analyze_trend(
        self,
        metric_name: str,
        branch: str = "all"
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric"""

        # Get data points
        points = self.time_series.get(metric_name, [])

        if branch != "all":
            points = [p for p in points if p.branch == branch]

        if len(points) < self.min_data_points:
            return None

        # Sort by timestamp
        points = sorted(points, key=lambda p: p.timestamp)

        # Extract values and timestamps
        values = np.array([p.value for p in points])
        timestamps = np.array([p.timestamp for p in points])

        # Convert timestamps to days from start
        days = (timestamps - timestamps[0]) / 86400

        # Linear regression to find trend
        if HAS_SCIPY:
            slope, intercept, correlation, p_value, std_err = stats.linregress(days, values)
            is_significant = p_value < 0.05
        else:
            # Simple linear regression
            n = len(days)
            slope = (n * np.sum(days * values) - np.sum(days) * np.sum(values)) / \
                    (n * np.sum(days**2) - (np.sum(days))**2)
            intercept = (np.sum(values) - slope * np.sum(days)) / n
            correlation = np.corrcoef(days, values)[0, 1]
            is_significant = abs(correlation) > 0.5

        # Determine trend direction
        # For latency/memory: positive slope = degrading
        # For throughput: positive slope = improving
        if "throughput" in metric_name:
            if slope > 0.01:
                direction = "improving"
            elif slope < -0.01:
                direction = "degrading"
            else:
                direction = "stable"
        else:
            if slope < -0.01:
                direction = "improving"
            elif slope > 0.01:
                direction = "degrading"
            else:
                direction = "stable"

        # Calculate confidence (based on correlation strength)
        confidence = min(abs(correlation), 1.0)

        # Predict future values (1, 7, 30 days out)
        last_day = days[-1]
        predictions = {}
        for days_out in [1, 7, 30]:
            future_day = last_day + days_out
            predicted_value = slope * future_day + intercept
            predictions[f"{days_out}day"] = float(predicted_value)

        # Detect anomalies (statistical outliers)
        anomalies = self._detect_anomalies(points)

        return TrendAnalysis(
            metric_name=metric_name,
            slope=float(slope),
            correlation=float(correlation),
            is_significant=is_significant,
            trend_direction=direction,
            confidence=float(confidence),
            predictions=predictions,
            anomalies=anomalies
        )

    def _detect_anomalies(
        self,
        points: List[DataPoint],
        threshold: float = 2.5
    ) -> List[Dict]:
        """Detect statistical anomalies in time series"""

        values = np.array([p.value for p in points])

        # Use median and MAD (median absolute deviation) for robustness
        median = np.median(values)
        mad = np.median(np.abs(values - median))

        if mad == 0:
            mad = np.std(values)  # Fall back to std if MAD is 0

        # Z-score using MAD
        z_scores = 0.6745 * (values - median) / mad

        # Find anomalies
        anomalies = []
        for i, (point, z_score) in enumerate(zip(points, z_scores)):
            if abs(z_score) > threshold:
                anomalies.append({
                    "timestamp": point.timestamp,
                    "commit_hash": point.commit_hash,
                    "value": point.value,
                    "z_score": float(z_score),
                    "expected": float(median),
                    "deviation": float(point.value - median)
                })

        return anomalies

    def generate_report(
        self,
        metrics: Optional[List[str]] = None,
        branch: str = "all"
    ) -> TrendReport:
        """Generate comprehensive trend report"""

        # Load historical data
        self.load_historical_data()

        # Analyze trends
        trends = {}
        metric_names = metrics if metrics else list(self.time_series.keys())

        for metric_name in metric_names:
            analysis = self.analyze_trend(metric_name, branch)
            if analysis:
                trends[metric_name] = analysis

        # Calculate time range
        all_points = []
        for points in self.time_series.values():
            all_points.extend(points)

        if all_points:
            timestamps = [p.timestamp for p in all_points]
            time_range = {
                "start": datetime.fromtimestamp(min(timestamps)).isoformat(),
                "end": datetime.fromtimestamp(max(timestamps)).isoformat()
            }
        else:
            time_range = {"start": "unknown", "end": "unknown"}

        # Generate summary
        summary = self._generate_summary(trends)

        return TrendReport(
            generated_at=datetime.now().isoformat(),
            time_range=time_range,
            total_commits=len(set(p.commit_hash for p in all_points)),
            metrics_analyzed=len(trends),
            trends=trends,
            summary=summary
        )

    def _generate_summary(self, trends: Dict[str, TrendAnalysis]) -> str:
        """Generate human-readable summary"""

        lines = []
        lines.append("Performance Trend Summary")
        lines.append("=" * 50)

        # Count trends by direction
        improving = sum(1 for t in trends.values() if t.trend_direction == "improving")
        degrading = sum(1 for t in trends.values() if t.trend_direction == "degrading")
        stable = sum(1 for t in trends.values() if t.trend_direction == "stable")

        lines.append(f"✅ Improving: {improving} metric(s)")
        lines.append(f"⚠️  Degrading: {degrading} metric(s)")
        lines.append(f"➡️  Stable: {stable} metric(s)")

        # Count anomalies
        total_anomalies = sum(len(t.anomalies) for t in trends.values())
        if total_anomalies > 0:
            lines.append(f"\n⚡ {total_anomalies} anomaly/ies detected")

        return "\n".join(lines)

    def visualize_trends(
        self,
        metric_names: List[str],
        output_dir: str = "reports/benchmarks/trends",
        branch: str = "all"
    ):
        """Generate trend visualizations"""

        if not HAS_MATPLOTLIB:
            print("Warning: matplotlib not available, skipping visualization")
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for metric_name in metric_names:
            analysis = self.analyze_trend(metric_name, branch)
            if not analysis:
                continue

            points = self.time_series.get(metric_name, [])
            if branch != "all":
                points = [p for p in points if p.branch == branch]

            points = sorted(points, key=lambda p: p.timestamp)

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))

            # Extract data
            timestamps = [datetime.fromtimestamp(p.timestamp) for p in points]
            values = [p.value for p in points]

            # Plot data points
            ax.plot(timestamps, values, 'o-', label=metric_name, alpha=0.6)

            # Plot trend line
            if HAS_SCIPY and len(points) >= 3:
                # Smooth trend line using Savitzky-Golay filter
                if len(points) >= 7:
                    window = min(7, len(points) if len(points) % 2 == 1 else len(points) - 1)
                    smoothed = savgol_filter(values, window, 2)
                    ax.plot(timestamps, smoothed, '--', label='Trend', linewidth=2, color='red')

            # Mark anomalies
            if analysis.anomalies:
                anomaly_timestamps = []
                anomaly_values = []
                for anomaly in analysis.anomalies:
                    point = next(
                        (p for p in points if p.timestamp == anomaly["timestamp"]),
                        None
                    )
                    if point:
                        anomaly_timestamps.append(datetime.fromtimestamp(point.timestamp))
                        anomaly_values.append(point.value)

                ax.scatter(
                    anomaly_timestamps,
                    anomaly_values,
                    color='red',
                    s=100,
                    zorder=5,
                    label='Anomalies',
                    marker='x'
                )

            # Formatting
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.set_title(f'Performance Trend: {metric_name}', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)

            # Add trend info
            trend_text = (
                f"Trend: {analysis.trend_direction}\n"
                f"Slope: {analysis.slope:.4f}/day\n"
                f"Correlation: {analysis.correlation:.3f}\n"
                f"Confidence: {analysis.confidence*100:.0f}%"
            )
            ax.text(0.02, 0.98, trend_text,
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            plt.tight_layout()

            # Save figure
            filename = f"{metric_name.replace('/', '_')}_trend.png"
            filepath = output_path / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"Saved: {filepath}")

    def save_report(self, report: TrendReport, filename: str = "trend_report.json") -> Path:
        """Save trend report to JSON"""

        output_path = Path("reports/benchmarks/current") / filename

        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

        return output_path

    def print_report(self, report: TrendReport):
        """Print trend report to console"""

        print(f"\n{'='*80}")
        print(f"PERFORMANCE TREND REPORT")
        print(f"{'='*80}\n")

        print(f"Generated: {report.generated_at}")
        print(f"Time Range: {report.time_range['start']} to {report.time_range['end']}")
        print(f"Total Commits: {report.total_commits}")
        print(f"Metrics Analyzed: {report.metrics_analyzed}")

        print(f"\n{report.summary}\n")

        # Print individual trends
        print("DETAILED TRENDS:")
        print("-" * 80)

        for metric_name, analysis in report.trends.items():
            direction_emoji = {
                "improving": "✅",
                "degrading": "⚠️",
                "stable": "➡️"
            }

            emoji = direction_emoji.get(analysis.trend_direction, "❓")

            print(f"\n{emoji} {metric_name}")
            print(f"   Direction: {analysis.trend_direction}")
            print(f"   Slope: {analysis.slope:.6f} per day")
            print(f"   Correlation: {analysis.correlation:.3f}")
            print(f"   Confidence: {analysis.confidence*100:.0f}%")
            print(f"   Significant: {analysis.is_significant}")

            print("   Predictions:")
            for period, value in analysis.predictions.items():
                print(f"     {period}: {value:.2f}")

            if analysis.anomalies:
                print(f"   Anomalies: {len(analysis.anomalies)}")
                for anomaly in analysis.anomalies[:3]:  # Show first 3
                    print(f"     - {anomaly['commit_hash'][:8]}: "
                          f"{anomaly['value']:.2f} (z={anomaly['z_score']:.2f})")

        print(f"\n{'='*80}\n")


def main():
    """Main entry point for trend tracking"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Trend Tracker")
    parser.add_argument(
        "--history-dir",
        default="reports/benchmarks/history",
        help="Historical benchmark data directory"
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=None,
        help="Specific metrics to analyze (default: all)"
    )
    parser.add_argument(
        "--branch",
        default="all",
        help="Branch to analyze (default: all)"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate trend visualizations"
    )
    parser.add_argument(
        "--output",
        default="reports/benchmarks/current/trend_report.json",
        help="Output file for report"
    )

    args = parser.parse_args()

    tracker = TrendTracker(history_dir=args.history_dir)

    report = tracker.generate_report(metrics=args.metrics, branch=args.branch)

    tracker.print_report(report)
    tracker.save_report(report, args.output)

    print(f"Report saved to: {args.output}")

    if args.visualize:
        metrics_to_viz = args.metrics if args.metrics else list(report.trends.keys())
        tracker.visualize_trends(metrics_to_viz)
        print(f"Visualizations saved to: reports/benchmarks/trends/")


if __name__ == "__main__":
    main()
