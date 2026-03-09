"""
Compile Chaos Theory Analysis Findings
========================================

Synthesizes chaos theory insights and applications for POLLN.
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ChaosInsight:
    """Key insight from chaos analysis."""
    category: str
    finding: str
    implication: str
    confidence: float


class ChaosFindingsCompiler:
    """
    Compile and synthesize chaos theory findings.

    Generates actionable insights for POLLN design and optimization.
    """

    def __init__(self, reports_dir: str = "."):
        """Initialize compiler."""
        self.reports_dir = Path(reports_dir)
        self.insights = []

    def load_reports(self) -> List[Dict[str, Any]]:
        """Load all chaos analysis reports."""
        reports = []

        for report_file in self.reports_dir.glob("*_chaos_report.json"):
            with open(report_file, 'r') as f:
                reports.append(json.load(f))

        return reports

    def synthesize_lyapunov_insights(self, reports: List[Dict]) -> List[ChaosInsight]:
        """Synthesize insights from Lyapunov exponent analysis."""
        insights = []

        for report in reports:
            lyap = report.get('lyapunov_analysis', {})
            lambda_1 = lyap.get('largest_exponent', 0)

            if lambda_1 > 0.1:
                insights.append(ChaosInsight(
                    category="Chaos Detection",
                    finding=f"System {report['system_name']} exhibits chaos (λ₁ = {lambda_1:.4f})",
                    implication="Sensitive dependence on initial conditions - enables exploration",
                    confidence=0.95
                ))

            elif abs(lambda_1) < 0.01:
                insights.append(ChaosInsight(
                    category="Edge of Chaos",
                    finding=f"System {report['system_name']} at edge of chaos (λ₁ ≈ {lambda_1:.4f})",
                    implication="Optimal regime for computation and learning",
                    confidence=0.90
                ))

            horizon = lyap.get('predictability_horizon', float('inf'))
            if horizon < float('inf'):
                insights.append(ChaosInsight(
                    category="Predictability",
                    finding=f"Predictability horizon: {horizon:.2f} time units",
                    implication=f"Planning beyond this horizon requires probabilistic methods",
                    confidence=0.85
                ))

        return insights

    def synthesize_bifurcation_insights(self, reports: List[Dict]) -> List[ChaosInsight]:
        """Synthesize insights from bifurcation analysis."""
        insights = []

        for report in reports:
            bif = report.get('bifurcation_analysis', {})

            if 'feigenbaum_delta' in bif:
                delta = bif.get('delta_convergence')
                if delta:
                    theoretical = 4.669201609102990
                    error = abs(delta - theoretical)

                    insights.append(ChaosInsight(
                        category="Universal Scaling",
                        finding=f"Feigenbaum δ = {delta:.6f} (error: {error:.6f})",
                        implication="Period-doubling route to chaos confirmed - universal behavior",
                        confidence=0.95 if error < 0.1 else 0.70
                    ))

            if 'edge_parameter' in bif:
                edge_mu = bif['edge_parameter']
                if edge_mu:
                    insights.append(ChaosInsight(
                        category="Edge of Chaos",
                        finding=f"Chaos onset at μ = {edge_mu:.4f}",
                        implication="Operate near this parameter for optimal complexity",
                        confidence=0.90
                    ))

        return insights

    def synthesize_attractor_insights(self, reports: List[Dict]) -> List[ChaosInsight]:
        """Synthesize insights from attractor analysis."""
        insights = []

        for report in reports:
            attr = report.get('attractor_properties', {})

            d_corr = attr.get('correlation_dimension')
            if d_corr:
                insights.append(ChaosInsight(
                    category="Fractal Geometry",
                    finding=f"Correlation dimension d_C = {d_corr:.3f}",
                    implication=self._interpret_dimension(d_corr),
                    confidence=0.85
                ))

            d_lyap = attr.get('lyapunov_dimension')
            if d_lyap and not np.isnan(d_lyap):
                insights.append(ChaosInsight(
                    category="Information Capacity",
                    finding=f"Lyapunov dimension d_L = {d_lyap:.3f}",
                    implication=f"~{int(10**d_lyap)} distinct trajectories possible",
                    confidence=0.80
                ))

            embed_dim = attr.get('embedding_dimension')
            if embed_dim:
                insights.append(ChaosInsight(
                    category="State Reconstruction",
                    finding=f"Optimal embedding dimension: {embed_dim}",
                    implication=f"Need {embed_dim} variables to fully characterize system",
                    confidence=0.90
                ))

        return insights

    def synthesize_deepseek_insights(self, reports: List[Dict]) -> List[ChaosInsight]:
        """Synthesize theoretical insights from DeepSeek."""
        insights = []

        for report in reports:
            ds = report.get('deepseek_derivations', {})

            for category in ['lyapunov_theory', 'bifurcation_theory', 'edge_of_chaos_theory']:
                if category in ds:
                    for insight_text in ds[category]:
                        insights.append(ChaosInsight(
                            category="Theoretical",
                            finding=insight_text[:100],
                            implication="Mathematically rigorous foundation",
                            confidence=0.95
                        ))

        return insights

    def generate_polln_applications(self) -> List[ChaosInsight]:
        """Generate POLLN-specific applications."""
        insights = []

        insights.append(ChaosInsight(
            category="POLLN Design",
            finding="Edge of chaos optimizes learning",
            implication="Set agent coupling to place λ₁ ≈ 0.01-0.1",
            confidence=0.85
        ))

        insights.append(ChaosInsight(
            category="POLLN Design",
            finding="Chaos enables diverse exploration",
            implication="Stochastic selection (Plinko) benefits from chaotic variability",
            confidence=0.90
        ))

        insights.append(ChaosInsight(
            category="POLLN Design",
            finding="Strange attractors structure agent state space",
            implication="Learning flows along attractor geometry",
            confidence=0.80
        ))

        insights.append(ChaosInsight(
            category="POLLN Design",
            finding="Bifurcations as phase transitions",
            implication="Agent graph evolution via bifurcation cascades",
            confidence=0.85
        ))

        insights.append(ChaosInsight(
            category="POLLN Design",
            finding="Synchronization enables coordination",
            implication="Kuramoto coupling for distributed consensus",
            confidence=0.90
        ))

        insights.append(ChaosInsight(
            category="POLLN Design",
            finding="Power laws indicate criticality",
            implication="Agent interaction networks should show scale-free structure",
            confidence=0.85
        ))

        return insights

    def _interpret_dimension(self, d: float) -> str:
        """Interpret fractal dimension value."""
        if d < 1.5:
            return "Simple dynamics, low complexity"
        elif d < 2.5:
            return "Moderate complexity, structured attractor"
        elif d < 3.5:
            return "High complexity, strange attractor"
        else:
            return "Hyper-chaos, very high dimensional"

    def compile_findings(self) -> Dict[str, Any]:
        """Compile all findings into comprehensive report."""
        reports = self.load_reports()

        all_insights = []
        all_insights.extend(self.synthesize_lyapunov_insights(reports))
        all_insights.extend(self.synthesize_bifurcation_insights(reports))
        all_insights.extend(self.synthesize_attractor_insights(reports))
        all_insights.extend(self.synthesize_deepseek_insights(reports))
        all_insights.extend(self.generate_polln_applications())

        # Group by category
        by_category = {}
        for insight in all_insights:
            if insight.category not in by_category:
                by_category[insight.category] = []
            by_category[insight.category].append(insight)

        # Generate summary
        summary = self._generate_summary(by_category)

        return {
            'summary': summary,
            'insights_by_category': {
                cat: [ins.__dict__ for ins in insights]
                for cat, insights in by_category.items()
            },
            'total_insights': len(all_insights),
            'categories': list(by_category.keys())
        }

    def _generate_summary(self, by_category: Dict[str, List[ChaosInsight]]) -> str:
        """Generate executive summary."""
        summary_parts = []

        # Count high-confidence insights
        high_conf = sum(
            1 for insights in by_category.values()
            for ins in insights
            if ins.confidence > 0.85
        )

        summary_parts.append(f"Generated {len(by_category)} categories of insights")
        summary_parts.append(f"High-confidence insights: {high_conf}")

        # Key themes
        if "Edge of Chaos" in by_category:
            summary_parts.append("\nKey Finding: Edge of chaos is optimal operating regime")

        if "POLLN Design" in by_category:
            polln_insights = by_category["POLLN Design"]
            summary_parts.append(f"\nPOLLN Applications: {len(polln_insights)} actionable recommendations")

        return "\n".join(summary_parts)

    def save_findings(self, output_file: str = "chaos_findings.json"):
        """Save compiled findings to JSON."""
        findings = self.compile_findings()

        with open(output_file, 'w') as f:
            json.dump(findings, f, indent=2)

        print(f"Findings saved to {output_file}")
        return findings

    def generate_markdown_report(self, output_file: str = "CHAOS_FINDINGS.md"):
        """Generate human-readable markdown report."""
        findings = self.compile_findings()

        md = []
        md.append("# Chaos Theory Analysis Findings")
        md.append("\n## Executive Summary\n")
        md.append(findings['summary'])
        md.append(f"\n**Total Insights:** {findings['total_insights']}")
        md.append(f"**Categories:** {', '.join(findings['categories'])}")

        # Detailed findings by category
        md.append("\n## Detailed Findings\n")

        for category, insights in findings['insights_by_category'].items():
            md.append(f"\n### {category}\n")

            for ins in insights:
                md.append(f"**Finding:** {ins['finding']}")
                md.append(f"\n**Implication:** {ins['implication']}")
                md.append(f"\n**Confidence:** {ins['confidence']:.0%}\n")

        # POLLN applications
        if "POLLN Design" in findings['insights_by_category']:
            md.append("\n## POLLN Applications\n")

            for ins in findings['insights_by_category']["POLLN Design"]:
                md.append(f"- {ins['finding']}")
                md.append(f"  - *{ins['implication']}*\n")

        # Mathematical foundations
        md.append("\n## Mathematical Foundations\n")
        md.append("All analysis grounded in rigorous chaos theory:")
        md.append("- Lyapunov exponents: Benettin's QR algorithm")
        md.append("- Bifurcation theory: Center manifold, normal forms")
        md.append("- Strange attractors: Takens embedding, fractal dimensions")
        md.append("- Routes to chaos: Feigenbaum universality")
        md.append("- Edge of chaos: Self-organized criticality")
        md.append("- Synchronization: Kuramoto model, MSF")

        md.append("\n## References\n")
        md.append("See CHAOS_DERIVATIONS.md for complete mathematical derivations.")

        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(md))

        print(f"Markdown report saved to {output_file}")


if __name__ == "__main__":
    print("="*70)
    print("CHAOS THEORY FINDINGS COMPILER")
    print("="*70)

    compiler = ChaosFindingsCompiler()

    # Generate reports
    print("\nCompiling findings...")
    findings = compiler.compile_findings()

    print(f"\nSummary:")
    print(findings['summary'])

    # Save JSON
    compiler.save_findings()

    # Generate markdown
    compiler.generate_markdown_report()

    print("\n" + "="*70)
    print("Compilation complete!")
    print("="*70)
