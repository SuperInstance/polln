#!/usr/bin/env python3
"""
Diagnostic Generator - Generate comprehensive diagnostic reports for POLLN colonies.

This tool runs all diagnostics and generates a comprehensive HTML report
with all findings, recommendations, and actionable insights.
"""

import json
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

# Import our debug tools
from a2a_tracer import A2ATracer
from agent_inspector import AgentInspector
from colony_diagnostics import ColonyDiagnostics
from value_network_debugger import ValueNetworkDebugger
from issue_detector import IssueDetector


class DiagnosticGenerator:
    """
    Generate comprehensive diagnostic reports.

    Features:
    - Run all diagnostic tools
    - Aggregate results
    - Generate HTML report
    - Create JSON reports
    - Provide actionable recommendations
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize diagnostic tools
        self.a2a_tracer = A2ATracer(colony_id, output_dir)
        self.agent_inspector = AgentInspector(colony_id, output_dir)
        self.colony_diagnostics = ColonyDiagnostics(colony_id, output_dir)
        self.value_network_debugger = ValueNetworkDebugger(colony_id, output_dir)
        self.issue_detector = IssueDetector(colony_id, output_dir)

        # Data storage
        self.colony_data: Optional[Dict[str, Any]] = None

    def load_colony_data(self, data_file: str) -> None:
        """
        Load colony data from file.

        Args:
            data_file: Path to colony data JSON file
        """
        with open(data_file, 'r') as f:
            self.colony_data = json.load(f)

        print(f"Loaded colony data from: {data_file}")

    def run_all_diagnostics(self) -> Dict[str, Any]:
        """
        Run all diagnostic tools.

        Returns:
            Dictionary containing all diagnostic results
        """
        if self.colony_data is None:
            raise ValueError("No colony data loaded. Call load_colony_data() first.")

        print("Running all diagnostics...")

        # Run A2A tracing
        print("  - A2A package tracing...")
        for pkg_data in self.colony_data.get('a2a_packages', []):
            self.a2a_tracer.trace_package(
                pkg_data,
                current_agent=pkg_data.get('currentAgent', 'unknown'),
                status=pkg_data.get('status', 'in_transit')
            )

        # Run agent inspection
        print("  - Agent state inspection...")
        for agent_data in self.colony_data.get('agents', []):
            self.agent_inspector.inspect_agent(agent_data)

            # Load value network data if available
            if 'valueNetwork' in agent_data:
                vn_data = agent_data['valueNetwork']
                agent_id = agent_data['id']

                # Record value history
                if 'valueHistory' in vn_data:
                    self.value_network_debugger.value_history[agent_id] = vn_data['valueHistory']

                # Record eligibility traces
                if 'eligibilityTraces' in vn_data:
                    self.value_network_debugger.record_eligibility_traces(
                        agent_id,
                        vn_data['eligibilityTraces']
                    )

                # Store learning parameters
                self.value_network_debugger.learning_params[agent_id] = {
                    'learning_rate': vn_data.get('learningRate', 0.1),
                    'lambda': 0.9  # Default TD(λ) parameter
                }

        # Run colony diagnostics
        print("  - Colony health diagnostics...")
        for agent_data in self.colony_data.get('agents', []):
            self.colony_diagnostics.check_agent_health(agent_data['id'], agent_data)

            if 'resources' in agent_data:
                self.colony_diagnostics.record_resource_usage(
                    agent_data['id'],
                    agent_data['resources']
                )

        # Run issue detection
        print("  - Issue detection...")
        self.issue_detector.run_all_checks(self.colony_data)

        # Generate individual reports
        print("  - Generating individual reports...")
        a2a_report = self.a2a_tracer.generate_trace_report()
        agent_report = self.agent_inspector.generate_inspection_report()
        colony_report = self.colony_diagnostics.generate_health_report()
        value_report = self.value_network_debugger.generate_debug_report()
        issue_report = self.issue_detector.generate_issue_report()

        print("Diagnostics complete!")

        return {
            'a2a_tracing': a2a_report,
            'agent_inspection': agent_report,
            'colony_diagnostics': colony_report,
            'value_network_debug': value_report,
            'issue_detection': issue_report
        }

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive diagnostic report.

        Returns:
            Dictionary containing all diagnostic data
        """
        diagnostics = self.run_all_diagnostics()

        # Calculate overall health score
        colony_health = diagnostics['colony_diagnostics']['health_score']
        critical_issues = diagnostics['issue_detection']['summary']['critical_issues']

        overall_health = colony_health
        if critical_issues > 0:
            overall_health = max(0, overall_health - 0.2 * critical_issues)

        # Aggregate recommendations
        all_recommendations = []

        # From colony diagnostics
        all_recommendations.extend(diagnostics['colony_diagnostics'].get('recommendations', []))

        # From issue detection
        all_recommendations.extend(diagnostics['issue_detection'].get('recommendations', []))

        # From value network issues
        for issue in diagnostics['value_network_debug'].get('issues', []):
            if issue.get('severity') == 'critical':
                all_recommendations.append(issue.get('recommendation', ''))

        # Deduplicate recommendations
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        report = {
            'colony_id': self.colony_id,
            'generated_at': datetime.now().isoformat(),
            'overall_health_score': overall_health,
            'overall_status': self._get_status_from_score(overall_health),
            'summary': {
                'total_agents': diagnostics['agent_inspection']['summary']['total_agents'],
                'critical_issues': critical_issues,
                'warning_issues': diagnostics['issue_detection']['summary']['warning_issues'],
                'deadlocked': diagnostics['colony_diagnostics']['summary']['deadlocked'],
                'cascade_risk': diagnostics['colony_diagnostics']['summary']['cascade_risk']
            },
            'diagnostics': diagnostics,
            'recommendations': unique_recommendations[:10]  # Top 10
        }

        return report

    def _get_status_from_score(self, score: float) -> str:
        """Get status string from health score."""
        if score >= 0.8:
            return 'healthy'
        elif score >= 0.6:
            return 'warning'
        else:
            return 'critical'

    def save_comprehensive_report(self, filename: str = "diagnostic_report.json") -> str:
        """
        Save comprehensive report to JSON file.

        Args:
            filename: Name of output file

        Returns:
            Path to saved file
        """
        report = self.generate_comprehensive_report()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Comprehensive report saved to: {output_path}")
        return str(output_path)

    def generate_html_report(self, filename: str = "diagnostic_report.html") -> str:
        """
        Generate HTML diagnostic report.

        Args:
            filename: Name of output HTML file

        Returns:
            Path to saved file
        """
        report = self.generate_comprehensive_report()

        html_content = self._render_html_report(report)

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML report saved to: {output_path}")
        return str(output_path)

    def _render_html_report(self, report: Dict[str, Any]) -> str:
        """Render HTML report from diagnostic data."""

        overall_health = report['overall_health_score']
        overall_status = report['overall_status']

        # Determine color scheme
        if overall_status == 'healthy':
            status_color = '#28a745'
            status_bg = '#d4edda'
        elif overall_status == 'warning':
            status_color = '#ffc107'
            status_bg = '#fff3cd'
        else:
            status_color = '#dc3545'
            status_bg = '#f8d7da'

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POLLN Diagnostic Report - {self.colony_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .timestamp {{
            color: #6c757d;
            font-size: 0.9em;
        }}

        .health-score {{
            display: flex;
            align-items: center;
            margin-top: 20px;
        }}

        .score-circle {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: {status_bg};
            border: 4px solid {status_color};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            font-weight: bold;
            color: {status_color};
            margin-right: 20px;
        }}

        .score-text {{
            flex: 1;
        }}

        .score-text h2 {{
            color: {status_color};
            margin-bottom: 5px;
        }}

        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .section h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .summary-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}

        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #495057;
        }}

        .summary-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .issue-list {{
            list-style: none;
        }}

        .issue-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #6c757d;
        }}

        .issue-item.critical {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}

        .issue-item.warning {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}

        .issue-item.info {{
            background: #d1ecf1;
            border-left-color: #17a2b8;
        }}

        .recommendation-list {{
            list-style: none;
        }}

        .recommendation-item {{
            padding: 12px;
            margin-bottom: 8px;
            background: #e7f3ff;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}

        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        .table th,
        .table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}

        .table th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badge.critical {{
            background: #dc3545;
            color: white;
        }}

        .badge.warning {{
            background: #ffc107;
            color: #212529;
        }}

        .badge.success {{
            background: #28a745;
            color: white;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 POLLN Diagnostic Report</h1>
            <p class="timestamp">Colony: {self.colony_id} | Generated: {report['generated_at']}</p>

            <div class="health-score">
                <div class="score-circle">
                    {int(overall_health * 100)}%
                </div>
                <div class="score-text">
                    <h2>{overall_status.upper()}</h2>
                    <p>Overall colony health based on comprehensive diagnostics</p>
                </div>
            </div>
        </header>

        <div class="section">
            <h2>📊 Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="value">{report['summary']['total_agents']}</div>
                    <div class="label">Total Agents</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #dc3545;">{report['summary']['critical_issues']}</div>
                    <div class="label">Critical Issues</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #ffc107;">{report['summary']['warning_issues']}</div>
                    <div class="label">Warning Issues</div>
                </div>
                <div class="summary-card">
                    <div class="value">{'⚠️' if report['summary']['deadlocked'] else '✓'}</div>
                    <div class="label">Deadlocked</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>⚠️ Detected Issues</h2>
            <ul class="issue-list">
"""

        # Add issues
        issues = report['diagnostics']['issue_detection']['detected_issues']
        for issue_id, issue in list(issues.items())[:10]:  # Show top 10
            html += f"""
                <li class="issue-item {issue['severity']}">
                    <strong>{issue.get('title', 'Unknown Issue')}</strong>
                    <p>{issue.get('description', '')}</p>
                    <p><strong>Agent:</strong> {issue.get('agent_id', 'N/A')}</p>
                </li>
            """

        if not issues:
            html += """
                <li class="issue-item info">
                    <strong>No issues detected!</strong>
                    <p>The colony appears to be functioning normally.</p>
                </li>
            """

        html += """
            </ul>
        </div>

        <div class="section">
            <h2>💡 Recommendations</h2>
            <ul class="recommendation-list">
"""

        # Add recommendations
        for i, rec in enumerate(report['recommendations'][:10], 1):
            html += f"""
                <li class="recommendation-item">
                    <strong>{i}.</strong> {rec}
                </li>
            """

        html += """
            </ul>
        </div>

        <div class="section">
            <h2>🔬 Detailed Diagnostics</h2>
            <p>Individual diagnostic reports have been generated:</p>
            <ul>
                <li><strong>A2A Tracing:</strong> a2a_trace.json</li>
                <li><strong>Agent Inspection:</strong> agent_states.json</li>
                <li><strong>Colony Diagnostics:</strong> colony_health.json</li>
                <li><strong>Value Network Debug:</strong> value_network_debug.json</li>
                <li><strong>Issue Detection:</strong> issues_detected.json</li>
            </ul>
        </div>
    </div>

    <footer>
        <p>Generated by POLLN Diagnostic Tool | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
"""

        return html


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python diagnostic_generator.py <colony_id> <colony_data_file> [command]")
        print("\nCommands:")
        print("  report                    - Generate all diagnostic reports")
        print("  html                      - Generate HTML report")
        print("  json                      - Generate JSON report")
        sys.exit(1)

    colony_id = sys.argv[1]
    data_file = sys.argv[2]
    command = sys.argv[3] if len(sys.argv) >= 4 else "report"

    generator = DiagnosticGenerator(colony_id)
    generator.load_colony_data(data_file)

    if command == "report" or command == "html":
        generator.generate_html_report()

    if command == "report" or command == "json":
        generator.save_comprehensive_report()


if __name__ == "__main__":
    main()
