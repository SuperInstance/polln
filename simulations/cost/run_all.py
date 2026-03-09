"""
Master Orchestrator: Run All Cost Simulations

This script orchestrates all cost simulations and generates a comprehensive report.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CostSimulationOrchestrator:
    """Orchestrates all cost simulations"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or 'simulations/cost')
        self.simulations = [
            'token_cost_analysis',
            'compute_efficiency',
            'dynamic_scaling',
            'break_even_analysis',
        ]
        self.results = {}

    def run_simulation(self, name: str) -> bool:
        """Run a single simulation"""
        print(f"\n{'=' * 80}")
        print(f"Running: {name}")
        print(f"{'=' * 80}")

        try:
            script_path = self.output_dir / f'{name}.py'
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                print(f"✓ {name} completed successfully")
                self.results[name] = {'status': 'success', 'output': result.stdout}
                return True
            else:
                print(f"✗ {name} failed")
                print(result.stderr)
                self.results[name] = {'status': 'failed', 'error': result.stderr}
                return False

        except subprocess.TimeoutExpired:
            print(f"✗ {name} timed out")
            self.results[name] = {'status': 'timeout'}
            return False
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            self.results[name] = {'status': 'error', 'error': str(e)}
            return False

    def run_all(self) -> Dict[str, bool]:
        """Run all simulations"""
        print("\n" + "=" * 80)
        print("COST SIMULATION ORCHESTRATOR")
        print("=" * 80)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Simulations to run: {len(self.simulations)}")

        results = {}
        for sim in self.simulations:
            results[sim] = self.run_simulation(sim)

        return results

    def collect_results(self) -> Dict:
        """Collect all simulation results"""
        collected = {}

        for sim in self.simulations:
            json_path = self.output_dir / f'{sim}_results.json'
            if json_path.exists():
                try:
                    with open(json_path, 'r') as f:
                        collected[sim] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {json_path}: {e}")
                    collected[sim] = None
            else:
                print(f"Warning: {json_path} not found")
                collected[sim] = None

        return collected

    def generate_summary_report(self, collected_results: Dict) -> str:
        """Generate summary report from all simulations"""
        report = []
        report.append("=" * 80)
        report.append("POLLN COST EFFICIENCY SIMULATION SUMMARY")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)

        # H1: Token Cost Reduction
        if collected_results.get('token_cost_analysis'):
            tca = collected_results['token_cost_analysis']
            avg_savings = np.mean([
                tca[complexity]['polln']['cost_per_request'] /
                tca[complexity]['gpt-4']['cost_per_request']
                for complexity in ['simple', 'medium', 'complex', 'very_complex']
            ]) * 100

            report.append(f"H1 (Token Cost Reduction): {100 - avg_savings:.1f}% savings vs GPT-4")
            report.append(f"  Target: 80% reduction")
            report.append(f"  Status: {'✓ PROVEN' if avg_savings <= 20 else '✗ NOT PROVEN'}")
        else:
            report.append("H1 (Token Cost Reduction): No data available")

        # H2: Compute Efficiency
        if collected_results.get('compute_efficiency'):
            ce = collected_results['compute_efficiency']['comparison']
            quality = ce['polln']['quality'] * 100
            cost = ce['comparison']['cost_for_quality_percent']

            report.append(f"\nH2 (Compute Efficiency): {quality:.1f}% quality at {cost:.1f}% compute cost")
            report.append(f"  Target: 90% quality at 10% compute")
            report.append(f"  Status: {'✓ PROVEN' if quality >= 90 and cost <= 10 else '✗ NOT PROVEN'}")
        else:
            report.append("\nH2 (Compute Efficiency): No data available")

        # H3: Dynamic Scaling
        if collected_results.get('dynamic_scaling'):
            ds = collected_results['dynamic_scaling']['results']
            avg_savings = np.mean([
                ds[pattern]['savings']['percent']
                for pattern in ds.keys()
            ])

            report.append(f"\nH3 (Dynamic Scaling): {avg_savings:.1f}% cost reduction")
            report.append(f"  Target: 60% reduction")
            report.append(f"  Status: {'✓ PROVEN' if avg_savings >= 60 else '✗ NOT PROVEN'}")
        else:
            report.append("\nH3 (Dynamic Scaling): No data available")

        # H4: Break-Even Analysis
        if collected_results.get('break_even_analysis'):
            be = collected_results['break_even_analysis']['analysis']
            min_requests = be['minimum_requests_90_day']

            report.append(f"\nH4 (Break-Even): Cost-effective at {min_requests}+ requests/day")
            report.append(f"  Target: 100 requests/day")
            report.append(f"  Status: {'✓ PROVEN' if min_requests <= 100 else '✗ NOT PROVEN'}")
        else:
            report.append("\nH4 (Break-Even): No data available")

        # Overall Verdict
        report.append("\n\nOVERALL VERDICT")
        report.append("-" * 80)
        all_proven = all([
            collected_results.get('token_cost_analysis') and (
                100 - np.mean([
                    collected_results['token_cost_analysis'][c]['polln']['cost_per_request'] /
                    collected_results['token_cost_analysis'][c]['gpt-4']['cost_per_request']
                    for c in ['simple', 'medium', 'complex', 'very_complex']
                ]) * 100
            ) >= 80,
            collected_results.get('compute_efficiency') and (
                collected_results['compute_efficiency']['comparison']['polln']['quality'] >= 0.9 and
                collected_results['compute_efficiency']['comparison']['comparison']['cost_for_quality_percent'] <= 10
            ),
            collected_results.get('dynamic_scaling') and np.mean([
                collected_results['dynamic_scaling']['results'][p]['savings']['percent']
                for p in collected_results['dynamic_scaling']['results'].keys()
            ]) >= 60,
            collected_results.get('break_even_analysis') and
            collected_results['break_even_analysis']['analysis']['minimum_requests_90_day'] <= 100,
        ])

        if all_proven:
            report.append("✓ ALL HYPOTHESES PROVEN")
            report.append("\nPOLLN achieves 5-10x cost reduction compared to monolithic LLMs")
            report.append("while maintaining competitive quality across all metrics.")
        else:
            report.append("✗ SOME HYPOTHESES NOT PROVEN")
            report.append("\nFurther optimization may be needed to achieve all targets.")

        # Detailed Results
        report.append("\n\nDETAILED RESULTS")
        report.append("-" * 80)

        for sim in self.simulations:
            report.append(f"\n{sim.replace('_', ' ').title()}:")
            if self.results.get(sim):
                status = self.results[sim]['status']
                report.append(f"  Status: {status.upper()}")
            if collected_results.get(sim):
                report.append(f"  Data: Available")

        report.append("\n\nFILES GENERATED")
        report.append("-" * 80)

        output_files = []
        for sim in self.simulations:
            output_files.extend([
                f"{sim}_report.txt",
                f"{sim}_results.json",
                f"{sim}_comparison.png",
            ])

        for f in sorted(output_files):
            path = self.output_dir / f
            if path.exists():
                report.append(f"  ✓ {f}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def generate_interactive_calculator(self) -> str:
        """Generate HTML-based cost calculator"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POLLN Cost Calculator</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2E7D32;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #fafafa;
        }
        .card h3 {
            margin-top: 0;
            color: #333;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        button {
            background: #2E7D32;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
        }
        button:hover {
            background: #1B5E20;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #E8F5E9;
            border-radius: 8px;
            border-left: 4px solid #2E7D32;
        }
        .results h2 {
            margin-top: 0;
            color: #2E7D32;
        }
        .result-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }
        .result-row:last-child {
            border-bottom: none;
        }
        .result-label {
            font-weight: 500;
            color: #555;
        }
        .result-value {
            font-weight: 600;
            color: #333;
        }
        .savings {
            color: #2E7D32;
        }
        .loss {
            color: #C62828;
        }
        .chart {
            margin-top: 30px;
            height: 300px;
            background: white;
            border-radius: 8px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>POLLN Cost Calculator</h1>
        <p class="subtitle">Compare costs between POLLN and monolithic LLM approaches</p>

        <div class="grid">
            <div class="card">
                <h3>Workload Parameters</h3>
                <label for="requests_per_day">Requests per Day</label>
                <input type="number" id="requests_per_day" value="100" min="1" max="10000">

                <label for="request_complexity">Request Complexity</label>
                <select id="request_complexity">
                    <option value="simple">Simple (500 input, 200 output tokens)</option>
                    <option value="medium" selected>Medium (2000 input, 800 output tokens)</option>
                    <option value="complex">Complex (5000 input, 2000 output tokens)</option>
                    <option value="very_complex">Very Complex (10000 input, 4000 output tokens)</option>
                </select>

                <label for="duration">Duration (days)</label>
                <input type="number" id="duration" value="90" min="1" max="365">
            </div>

            <div class="card">
                <h3>POLLN Configuration</h3>
                <label for="num_agents">Number of Agents</label>
                <input type="number" id="num_agents" value="100" min="10" max="1000">

                <label for="agent_size">Agent Size</label>
                <select id="agent_size">
                    <option value="tiny" selected>Tiny (10M parameters)</option>
                    <option value="small">Small (100M parameters)</option>
                    <option value="medium">Medium (1B parameters)</option>
                </select>

                <label for="checkpoint_efficiency">Checkpoint Efficiency (%)</label>
                <input type="range" id="checkpoint_efficiency" value="70" min="30" max="90">
                <span id="checkpoint_value">70%</span>
            </div>

            <div class="card">
                <h3>Comparison Model</h3>
                <label for="base_model">Base Model</label>
                <select id="base_model">
                    <option value="gpt-4" selected>GPT-4 ($0.03/1K in, $0.06/1K out)</option>
                    <option value="claude-opus">Claude Opus ($0.015/1K in, $0.075/1K out)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo ($0.0005/1K in, $0.0015/1K out)</option>
                </select>

                <label for="auto_scale">Enable Auto-scaling</label>
                <input type="checkbox" id="auto_scale" checked>
            </div>
        </div>

        <button onclick="calculate()">Calculate Costs</button>

        <div class="results" id="results" style="display: none;">
            <h2>Cost Comparison</h2>
            <div id="comparison_results"></div>
        </div>

        <div class="chart" id="chart" style="display: none;">
            <canvas id="costChart"></canvas>
        </div>
    </div>

    <script>
        // Update checkpoint efficiency display
        document.getElementById('checkpoint_efficiency').addEventListener('input', function(e) {
            document.getElementById('checkpoint_value').textContent = e.target.value + '%';
        });

        function calculate() {
            // Get input values
            const requestsPerDay = parseInt(document.getElementById('requests_per_day').value);
            const complexity = document.getElementById('request_complexity').value;
            const duration = parseInt(document.getElementById('duration').value);
            const numAgents = parseInt(document.getElementById('num_agents').value);
            const agentSize = document.getElementById('agent_size').value;
            const checkpointEfficiency = parseInt(document.getElementById('checkpoint_efficiency').value) / 100;
            const baseModel = document.getElementById('base_model').value;
            const autoScale = document.getElementById('auto_scale').checked;

            // Token profiles
            const tokenProfiles = {
                simple: { input: 500, output: 200 },
                medium: { input: 2000, output: 800 },
                complex: { input: 5000, output: 2000 },
                very_complex: { input: 10000, output: 4000 }
            };

            const profile = tokenProfiles[complexity];

            // Model pricing
            const pricing = {
                'gpt-4': { input: 0.03, output: 0.06 },
                'claude-opus': { input: 0.015, output: 0.075 },
                'gpt-3.5-turbo': { input: 0.0005, output: 0.0015 }
            };

            const modelPrice = pricing[baseModel];

            // Calculate monolithic cost
            const monolithicCostPerRequest =
                ((profile.input / 1000) * modelPrice.input +
                 (profile.output / 1000) * modelPrice.output);
            const totalMonolithicCost = monolithicCostPerRequest * requestsPerDay * duration;

            // Calculate POLLN cost
            const pollnTokenCostPerRequest =
                ((profile.input * checkpointEfficiency / 1000) * 0.0001 +
                 (profile.output * checkpointEfficiency / 1000) * 0.0002);
            const pollnComputeCostPerRequest = 0.001;
            const pollnCostPerRequest = pollnTokenCostPerRequest + pollnComputeCostPerRequest;

            // Apply auto-scaling discount
            const scalingDiscount = autoScale ? 0.6 : 1.0;
            const totalPollnCost = pollnCostPerRequest * requestsPerDay * duration * scalingDiscount;

            // Add fixed costs
            const pollnFixedCosts = 8000; // One-time setup
            const amortizedFixedCosts = duration <= 30 ? pollnFixedCosts : pollnFixedCosts / (duration / 30);
            const totalPollnCostWithFixed = totalPollnCost + amortizedFixedCosts;

            // Calculate savings
            const savings = totalMonolithicCost - totalPollnCostWithFixed;
            const savingsPercent = (savings / totalMonolithicCost) * 100;

            // Display results
            const resultsDiv = document.getElementById('comparison_results');
            resultsDiv.innerHTML = `
                <div class="result-row">
                    <span class="result-label">Total Requests:</span>
                    <span class="result-value">${(requestsPerDay * duration).toLocaleString()}</span>
                </div>
                <div class="result-row">
                    <span class="result-label">Monolithic LLM (${baseModel}):</span>
                    <span class="result-value">$${totalMonolithicCost.toFixed(2)}</span>
                </div>
                <div class="result-row">
                    <span class="result-label">POLLN (${numAgents}×${agentSize}):</span>
                    <span class="result-value">$${totalPollnCostWithFixed.toFixed(2)}</span>
                </div>
                <div class="result-row">
                    <span class="result-label">Cost Savings:</span>
                    <span class="result-value ${savings > 0 ? 'savings' : 'loss'}">
                        $${savings.toFixed(2)} (${savingsPercent.toFixed(1)}%)
                    </span>
                </div>
                <div class="result-row">
                    <span class="result-label">Break-Even:</span>
                    <span class="result-value">${calculateBreakEven(requestsPerDay, monolithicCostPerRequest, pollnCostPerRequest * scalingDiscount, pollnFixedCosts)} days</span>
                </div>
            `;

            document.getElementById('results').style.display = 'block';

            // Draw chart
            drawChart(totalMonolithicCost, totalPollnCostWithFixed);
        }

        function calculateBreakEven(requestsPerDay, monolithicCost, pollnCost, fixedCosts) {
            let cumulativeMonolithic = 0;
            let cumulativePolln = fixedCosts;

            for (let day = 1; day <= 365; day++) {
                cumulativeMonolithic += monolithicCost * requestsPerDay;
                cumulativePolln += pollnCost * requestsPerDay;

                if (cumulativePolln <= cumulativeMonolithic) {
                    return day;
                }
            }

            return '>365';
        }

        function drawChart(monolithicCost, pollnCost) {
            const chartDiv = document.getElementById('chart');
            chartDiv.style.display = 'block';

            const canvas = document.getElementById('costChart');
            const ctx = canvas.getContext('2d');

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw simple bar chart
            const maxCost = Math.max(monolithicCost, pollnCost);
            const scale = 250 / maxCost;

            ctx.fillStyle = '#C62828';
            ctx.fillRect(50, 50, monolithicCost * scale, 50);
            ctx.fillStyle = '#333';
            ctx.fillText(`Monolithic: $${monolithicCost.toFixed(2)}`, 50 + monolithicCost * scale + 10, 80);

            ctx.fillStyle = '#2E7D32';
            ctx.fillRect(50, 120, pollnCost * scale, 50);
            ctx.fillStyle = '#333';
            ctx.fillText(`POLLN: $${pollnCost.toFixed(2)}`, 50 + pollnCost * scale + 10, 150);
        }
    </script>
</body>
</html>
        """

        calculator_path = self.output_dir / 'cost_calculator.html'
        with open(calculator_path, 'w') as f:
            f.write(html)

        return str(calculator_path)

    def save_summary_report(self, report: str):
        """Save summary report to file"""
        report_path = self.output_dir / 'COST_ANALYSIS_SUMMARY.txt'
        with open(report_path, 'w') as f:
            f.write(report)

        return report_path


def main():
    """Run all cost simulations"""
    import numpy as np  # Import for summary report

    orchestrator = CostSimulationOrchestrator()

    # Run all simulations
    results = orchestrator.run_all()

    # Collect results
    collected_results = orchestrator.collect_results()

    # Generate summary report
    summary_report = orchestrator.generate_summary_report(collected_results)
    print("\n" + summary_report)

    # Save summary report
    report_path = orchestrator.save_summary_report(summary_report)
    print(f"\n✓ Summary report saved to: {report_path}")

    # Generate interactive calculator
    calculator_path = orchestrator.generate_interactive_calculator()
    print(f"✓ Interactive calculator saved to: {calculator_path}")

    # Print status
    print("\n" + "=" * 80)
    print("SIMULATION STATUS")
    print("=" * 80)
    for sim, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{sim}: {status}")

    # Print file list
    print("\n" + "=" * 80)
    print("GENERATED FILES")
    print("=" * 80)
    output_files = list(orchestrator.output_dir.glob('*'))
    for f in sorted(output_files):
        if f.is_file():
            print(f"  {f.name}")


if __name__ == '__main__':
    main()
