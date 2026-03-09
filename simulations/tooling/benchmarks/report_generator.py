"""
Benchmark Report Generator

Generates comprehensive HTML reports with trends, comparisons,
and recommendations from benchmark results.
"""

import json
import base64
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import io


try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@dataclass
class ReportSection:
    """A section of the benchmark report"""
    title: str
    content: str
    charts: List[str]  # Base64 encoded chart images
    metrics: Dict[str, any]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BenchmarkReport:
    """Complete benchmark report"""
    title: str
    generated_at: str
    run_id: str
    commit_hash: str
    branch: str
    sections: List[ReportSection]
    executive_summary: str
    recommendations: List[str]
    overall_score: float  # 0-100

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "generated_at": self.generated_at,
            "run_id": self.run_id,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "sections": [s.to_dict() for s in self.sections],
            "executive_summary": self.executive_summary,
            "recommendations": self.recommendations,
            "overall_score": self.overall_score
        }


class ReportGenerator:
    """
    Generate comprehensive benchmark reports.

    Features:
    - HTML report generation
    - Interactive charts and visualizations
    - Executive summary
    - Detailed metrics breakdown
    - Performance recommendations
    - Historical comparisons
    - Multiple output formats (HTML, JSON, Markdown)
    """

    def __init__(
        self,
        current_dir: str = "reports/benchmarks/current",
        baseline_dir: str = "reports/benchmarks/baselines",
        history_dir: str = "reports/benchmarks/history",
        output_dir: str = "reports/benchmarks"
    ):
        self.current_dir = Path(current_dir)
        self.baseline_dir = Path(baseline_dir)
        self.history_dir = Path(history_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_benchmark_data(self, filepath: Path) -> Optional[Dict]:
        """Load benchmark data from JSON file"""

        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            return json.load(f)

    def generate_executive_summary(
        self,
        current_results: List[Dict],
        regression_results: Optional[Dict] = None
    ) -> str:
        """Generate executive summary of benchmark results"""

        lines = []

        # Overall status
        total_benchmarks = len(current_results)
        successful = sum(1 for r in current_results if r.get("success_rate", 1.0) > 0.9)

        lines.append(f"<p><strong>Executive Summary</strong></p>")
        lines.append(f"<ul>")
        lines.append(f"<li>Total benchmarks run: {total_benchmarks}</li>")
        lines.append(f"<li>Successful: {successful}/{total_benchmarks}</li>")

        # Check regressions
        if regression_results:
            regressions = regression_results.get("regressions", [])
            critical = sum(1 for r in regressions if r.get("severity") == "critical")
            high = sum(1 for r in regressions if r.get("severity") == "high")

            if critical > 0 or high > 0:
                lines.append(f"<li><span style='color: red;'>⚠️ Performance regressions detected: {critical + high}</span></li>")
            else:
                lines.append(f"<li><span style='color: green;'>✅ No critical regressions detected</span></li>")

        lines.append(f"</ul>")

        return "\n".join(lines)

    def generate_recommendations(
        self,
        current_results: List[Dict],
        regression_results: Optional[Dict] = None
    ) -> List[str]:
        """Generate performance recommendations"""

        recommendations = []

        # Analyze throughput
        throughputs = [r.get("throughput_ops", 0) for r in current_results if r.get("throughput_ops")]
        if throughputs:
            avg_throughput = sum(throughputs) / len(throughputs)
            if avg_throughput < 100:
                recommendations.append(
                    "Consider optimizing critical paths - average throughput is below 100 ops/sec"
                )

        # Analyze latency
        latencies = [r.get("p95_latency_ms", 0) for r in current_results if r.get("p95_latency_ms")]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            if avg_latency > 100:
                recommendations.append(
                    f"High latency detected (avg P95: {avg_latency:.2f}ms) - investigate slow operations"
                )

        # Analyze memory
        memories = [r.get("memory_mb", 0) for r in current_results if r.get("memory_mb")]
        if memories:
            max_memory = max(memories)
            if max_memory > 500:
                recommendations.append(
                    f"High memory usage detected (max: {max_memory:.2f}MB) - consider memory optimization"
                )

        # Regression-specific recommendations
        if regression_results:
            for regression in regression_results.get("regressions", []):
                if regression.get("severity") in ["critical", "high"]:
                    recommendations.append(regression.get("recommendation", ""))

        return recommendations

    def calculate_overall_score(
        self,
        current_results: List[Dict],
        regression_results: Optional[Dict] = None
    ) -> float:
        """Calculate overall performance score (0-100)"""

        if not current_results:
            return 0.0

        # Base score from success rate
        success_rates = [r.get("success_rate", 1.0) for r in current_results]
        base_score = (sum(success_rates) / len(success_rates)) * 100

        # Penalize for regressions
        penalty = 0.0
        if regression_results:
            for regression in regression_results.get("regressions", []):
                severity = regression.get("severity", "none")
                if severity == "critical":
                    penalty += 20
                elif severity == "high":
                    penalty += 10
                elif severity == "medium":
                    penalty += 5
                elif severity == "low":
                    penalty += 2

        return max(0.0, min(100.0, base_score - penalty))

    def generate_chart(
        self,
        data: Dict,
        chart_type: str = "bar"
    ) -> Optional[str]:
        """Generate chart and return as base64 encoded image"""

        if not HAS_MATPLOTLIB:
            return None

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "bar":
                names = list(data.keys())
                values = list(data.values())

                ax.bar(names, values)
                ax.set_ylabel('Value')
                ax.set_title('Benchmark Results')

            elif chart_type == "line":
                # For time series data
                for series_name, series_data in data.items():
                    timestamps = series_data.get("timestamps", [])
                    values = series_data.get("values", [])

                    dates = [datetime.fromtimestamp(ts) for ts in timestamps]
                    ax.plot(dates, values, marker='o', label=series_name)

                ax.set_ylabel('Value')
                ax.set_title('Performance Over Time')
                ax.legend()
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.xticks(rotation=45)

            plt.tight_layout()

            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()

            return img_base64

        except Exception as e:
            print(f"Error generating chart: {e}")
            return None

    def generate_html_report(
        self,
        current_file: str,
        baseline_file: Optional[str] = None,
        regression_file: Optional[str] = None
    ) -> BenchmarkReport:
        """Generate comprehensive HTML report"""

        # Load current results
        current_path = self.current_dir / current_file
        current_data = self.load_benchmark_data(current_path)

        if not current_data:
            raise FileNotFoundError(f"Current benchmark file not found: {current_path}")

        current_results = current_data.get("results", [])
        run_id = current_data.get("run_id", "unknown")
        commit_hash = current_data.get("commit_hash", "unknown")
        branch = current_data.get("branch", "main")

        # Load regression results if available
        regression_results = None
        if regression_file:
            regression_path = self.current_dir / regression_file
            regression_results = self.load_benchmark_data(regression_path)

        # Generate executive summary
        executive_summary = self.generate_executive_summary(
            current_results,
            regression_results
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(
            current_results,
            regression_results
        )

        # Calculate overall score
        overall_score = self.calculate_overall_score(
            current_results,
            regression_results
        )

        # Create sections
        sections = []

        # Section 1: Overview
        sections.append(ReportSection(
            title="Overview",
            content=f"""
            <p><strong>Run ID:</strong> {run_id}</p>
            <p><strong>Commit:</strong> {commit_hash}</p>
            <p><strong>Branch:</strong> {branch}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """,
            charts=[],
            metrics={"total_benchmarks": len(current_results)}
        ))

        # Section 2: Performance Metrics
        metrics_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        metrics_html += "<tr><th>Benchmark</th><th>Throughput</th><th>P95 Latency</th><th>Memory</th><th>Success Rate</th></tr>"

        for result in current_results:
            metrics_html += f"""
            <tr>
                <td>{result.get('name', 'unknown')}</td>
                <td>{result.get('throughput_ops', 0):.2f}</td>
                <td>{result.get('p95_latency_ms', 0):.2f}</td>
                <td>{result.get('memory_mb', 0):.2f}</td>
                <td>{result.get('success_rate', 0)*100:.1f}%</td>
            </tr>
            """

        metrics_html += "</table>"

        sections.append(ReportSection(
            title="Performance Metrics",
            content=metrics_html,
            charts=[],
            metrics={}
        ))

        # Section 3: Regressions (if available)
        if regression_results:
            regression_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            regression_html += "<tr><th>Metric</th><th>Baseline</th><th>Current</th><th>Change</th><th>Severity</th></tr>"

            for regression in regression_results.get("regressions", []):
                severity_color = {
                    "critical": "red",
                    "high": "orange",
                    "medium": "yellow",
                    "low": "blue"
                }.get(regression.get("severity", "none"), "black")

                regression_html += f"""
                <tr>
                    <td>{regression.get('metric_name', 'unknown')}</td>
                    <td>{regression.get('baseline_value', 0):.2f}</td>
                    <td>{regression.get('current_value', 0):.2f}</td>
                    <td>{regression.get('percent_change', 0):+.2f}%</td>
                    <td style='color: {severity_color};'>{regression.get('severity', 'none').upper()}</td>
                </tr>
                """

            regression_html += "</table>"

            sections.append(ReportSection(
                title="Performance Regressions",
                content=regression_html,
                charts=[],
                metrics={"regressions_detected": len(regression_results.get("regressions", []))}
            ))

        # Section 4: Recommendations
        recommendations_html = "<ul>"
        for rec in recommendations:
            recommendations_html += f"<li>{rec}</li>"
        recommendations_html += "</ul>"

        sections.append(ReportSection(
            title="Recommendations",
            content=recommendations_html,
            charts=[],
            metrics={}
        ))

        # Create report
        report = BenchmarkReport(
            title=f"POLLN Benchmark Report - {run_id}",
            generated_at=datetime.now().isoformat(),
            run_id=run_id,
            commit_hash=commit_hash,
            branch=branch,
            sections=sections,
            executive_summary=executive_summary,
            recommendations=recommendations,
            overall_score=overall_score
        )

        return report

    def save_html_report(self, report: BenchmarkReport, filename: str = None) -> Path:
        """Save report as HTML file"""

        if filename is None:
            filename = "benchmark_report.html"

        output_path = self.output_dir / filename

        # Generate HTML
        html = self._render_html_template(report)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path

    def _render_html_template(self, report: BenchmarkReport) -> str:
        """Render HTML template with report data"""

        # Score color
        score_color = "green" if report.overall_score >= 80 else "orange" if report.overall_score >= 60 else "red"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .score-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: {score_color};
        }}
        .section {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .recommendations {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .regression-critical {{ color: #e74c3c; font-weight: bold; }}
        .regression-high {{ color: #e67e22; font-weight: bold; }}
        .regression-medium {{ color: #f39c12; }}
        .regression-low {{ color: #3498db; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>

    <div class="score-box">
        <div>Overall Performance Score</div>
        <div class="score">{report.overall_score:.0f}/100</div>
    </div>

    <div class="section">
        {report.executive_summary}
    </div>

    <div class="meta">
        <p>Generated: {report.generated_at}</p>
        <p>Commit: {report.commit_hash}</p>
        <p>Branch: {report.branch}</p>
    </div>

    <h2>Report Sections</h2>
    """

        for section in report.sections:
            html += f"""
    <div class="section">
        <h2>{section.title}</h2>
        {section.content}
    </div>
            """

        html += f"""
    <div class="section recommendations">
        <h2>Recommendations</h2>
        <ul>
        """

        for rec in report.recommendations:
            html += f"<li>{rec}</li>"

        html += """
        </ul>
    </div>

    <footer>
        <p>Generated by POLLN Benchmark Suite</p>
    </footer>
</body>
</html>
        """

        return html

    def save_json_report(self, report: BenchmarkReport, filename: str = None) -> Path:
        """Save report as JSON file"""

        if filename is None:
            filename = "benchmark_report.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

        return output_path

    def save_markdown_report(self, report: BenchmarkReport, filename: str = None) -> Path:
        """Save report as Markdown file"""

        if filename is None:
            filename = "benchmark_report.md"

        output_path = self.output_dir / filename

        markdown = f"""# {report.title}

**Generated:** {report.generated_at}
**Commit:** {report.commit_hash}
**Branch:** {report.branch}

## Overall Performance Score: {report.overall_score:.0f}/100

{report.executive_summary}

"""

        for section in report.sections:
            markdown += f"## {section.title}\n\n{section.content}\n\n"

        markdown += "## Recommendations\n\n"
        for rec in report.recommendations:
            markdown += f"- {rec}\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return output_path


def main():
    """Main entry point for report generation"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Report Generator")
    parser.add_argument(
        "--current",
        default=None,
        help="Current benchmark results file"
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Baseline benchmark file for comparison"
    )
    parser.add_argument(
        "--regression",
        default="regression_report.json",
        help="Regression report file"
    )
    parser.add_argument(
        "--format",
        choices=["html", "json", "markdown", "all"],
        default="all",
        help="Report format (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports/benchmarks",
        help="Output directory for reports"
    )

    args = parser.parse_args()

    generator = ReportGenerator(output_dir=args.output_dir)

    # Find current benchmark file if not specified
    if args.current is None:
        current_dir = Path("reports/benchmarks/current")
        current_files = list(current_dir.glob("benchmark_run_*.json"))
        if not current_files:
            # Try benchmarks timestamp file
            current_files = list(current_dir.glob("benchmarks_*.json"))

        if not current_files:
            print("Error: No benchmark results found")
            exit(1)

        current_file = max(current_files, key=lambda p: p.stat().st_mtime).name
    else:
        current_file = args.current

    try:
        report = generator.generate_html_report(
            current_file=current_file,
            baseline_file=args.baseline,
            regression_file=args.regression
        )

        # Save in requested format(s)
        if args.format in ["html", "all"]:
            html_path = generator.save_html_report(report)
            print(f"HTML report: {html_path}")

        if args.format in ["json", "all"]:
            json_path = generator.save_json_report(report)
            print(f"JSON report: {json_path}")

        if args.format in ["markdown", "all"]:
            md_path = generator.save_markdown_report(report)
            print(f"Markdown report: {md_path}")

        print(f"\nOverall Score: {report.overall_score:.0f}/100")
        print(f"Recommendations: {len(report.recommendations)}")

    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
