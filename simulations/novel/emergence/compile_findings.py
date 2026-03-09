"""
Findings Compiler and Synthesizer

Compiles and synthesizes discoveries from multiple discovery campaigns
into comprehensive reports, papers, and documentation.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SynthesizedFindings:
    """Synthesized findings from multiple campaigns"""
    synthesis_id: str
    timestamp: str
    n_campaigns: int
    total_discoveries: int
    unique_phenomena: int
    high_novelty_phenomena: List[Dict]
    cross_campaign_patterns: List[str]
    theoretical_insights: List[str]
    practical_applications: List[str]
    publication_recommendations: List[str]


class FindingsCompiler:
    """
    Compiles and synthesizes findings from discovery campaigns

    Aggregates results from multiple runs, identifies cross-cutting patterns,
    and generates comprehensive reports.
    """

    def __init__(self, results_dir: str = "./discovery_results"):
        self.results_dir = Path(results_dir)
        self.campaigns = []
        self.phenomena = {}

    def load_campaigns(self) -> None:
        """Load all discovery campaigns from results directory"""
        logger.info(f"Loading campaigns from {self.results_dir}")

        # Find all campaign summaries
        campaign_files = list(self.results_dir.glob("**/campaign_summary.json"))

        for campaign_file in campaign_files:
            try:
                with open(campaign_file, 'r') as f:
                    campaign = json.load(f)

                self.campaigns.append({
                    "file": str(campaign_file),
                    "data": campaign
                })

                logger.info(f"  Loaded: {campaign_file}")

            except Exception as e:
                logger.warning(f"Could not load {campaign_file}: {e}")

        logger.info(f"Loaded {len(self.campaigns)} campaigns")

    def load_phenomena(self) -> None:
        """Load all phenomena from catalogs"""
        # Find all catalogs
        catalog_files = list(self.results_dir.glob("**/catalog/entries.json"))

        for catalog_file in catalog_files:
            try:
                with open(catalog_file, 'r') as f:
                    catalog = json.load(f)

                self.phenomena.update(catalog)

            except Exception as e:
                logger.warning(f"Could not load {catalog_file}: {e}")

        logger.info(f"Loaded {len(self.phenomena)} phenomena")

    def synthesize_findings(self) -> SynthesizedFindings:
        """Synthesize findings from all campaigns"""
        logger.info("Synthesizing findings...")

        # Count total discoveries
        total_discoveries = sum(
            c["data"].get("phenomena_cataloged", 0)
            for c in self.campaigns
        )

        # Extract high novelty phenomena
        high_novelty = []
        for pid, phenomenon in self.phenomena.items():
            if phenomenon.get("novelty_score", 0) > 0.8:
                high_novelty.append({
                    "id": pid,
                    "name": phenomenon.get("name", ""),
                    "short_name": phenomenon.get("short_name", ""),
                    "category": phenomenon.get("category", ""),
                    "novelty_score": phenomenon.get("novelty_score", 0),
                    "description": phenomenon.get("description", "")
                })

        # Sort by novelty
        high_novelty.sort(key=lambda x: x["novelty_score"], reverse=True)

        # Identify cross-cutting patterns
        cross_campaign_patterns = self._identify_cross_campaign_patterns()

        # Extract theoretical insights
        theoretical_insights = self._extract_theoretical_insights(high_novelty)

        # Identify practical applications
        practical_applications = self._identify_practical_applications(high_novelty)

        # Generate publication recommendations
        publication_recommendations = self._generate_publication_recommendations(
            high_novelty,
            theoretical_insights
        )

        synthesis = SynthesizedFindings(
            synthesis_id=f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            n_campaigns=len(self.campaigns),
            total_discoveries=total_discoveries,
            unique_phenomena=len(self.phenomena),
            high_novelty_phenomena=high_novelty[:20],  # Top 20
            cross_campaign_patterns=cross_campaign_patterns,
            theoretical_insights=theoretical_insights,
            practical_applications=practical_applications,
            publication_recommendations=publication_recommendations
        )

        logger.info(f"Synthesis complete: {synthesis.unique_phenomena} phenomena")

        return synthesis

    def _identify_cross_campaign_patterns(self) -> List[str]:
        """Identify patterns that appear across multiple campaigns"""
        patterns = []

        # Common categories
        category_counts = {}
        for phenomenon in self.phenomena.values():
            category = phenomenon.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        # Categories appearing in multiple campaigns
        for category, count in category_counts.items():
            if count >= 3:
                patterns.append(f"Repeated emergence of {category}-type phenomena")

        # High novelty patterns
        high_novelty_categories = set()
        for phenomenon in self.phenomena.values():
            if phenomenon.get("novelty_score", 0) > 0.8:
                high_novelty_categories.add(phenomenon.get("category", ""))

        if len(high_novelty_categories) > 2:
            patterns.append(f"High-novelty phenomena span {len(high_novelty_categories)} categories")

        return patterns

    def _extract_theoretical_insights(self, high_novelty: List[Dict]) -> List[str]:
        """Extract theoretical insights from high novelty phenomena"""
        insights = []

        # Look for common mechanisms
        mechanisms = {}
        for phenomenon_dict in high_novelty:
            pid = phenomenon_dict["id"]
            if pid in self.phenomena:
                mechanism = self.phenomena[pid].get("hypothesized_mechanism", "")
                if mechanism:
                    # Extract key terms
                    words = mechanism.lower().split()
                    for word in words:
                        if len(word) > 5:  # Significant words
                            mechanisms[word] = mechanisms.get(word, 0) + 1

        # Top mechanisms
        top_mechanisms = sorted(mechanisms.items(), key=lambda x: x[1], reverse=True)[:5]
        for word, count in top_mechanisms:
            if count >= 2:
                insights.append(f"Common mechanism: {word.capitalize()} (appears {count} times)")

        # Look for unique features
        for phenomenon_dict in high_novelty[:5]:
            pid = phenomenon_dict["id"]
            if pid in self.phenomena:
                features = self.phenomena[pid].get("features", {})
                unique_features = [f for f, v in features.items() if v > 0.8]
                if unique_features:
                    insights.append(
                        f"{phenomenon_dict['short_name']}: Unique features include {', '.join(unique_features[:3])}"
                    )

        return insights

    def _identify_practical_applications(self, high_novelty: List[Dict]) -> List[str]:
        """Identify practical applications of discoveries"""
        applications = []

        for phenomenon_dict in high_novelty[:10]:
            pid = phenomenon_dict["id"]
            if pid in self.phenomena:
                phenomenon_apps = self.phenomena[pid].get("practical_applications", [])
                applications.extend(phenomenon_apps)

        # Remove duplicates and limit
        unique_apps = list(set(applications))
        return unique_apps[:10]

    def _generate_publication_recommendations(self,
                                            high_novelty: List[Dict],
                                            insights: List[str]) -> List[str]:
        """Generate recommendations for publication"""
        recommendations = []

        if len(high_novelty) >= 5:
            recommendations.append(
                f"Sufficient high-novelty phenomena ({len(high_novelty)}) for a discovery paper"
            )

        if any("coordination" in p["category"].lower() for p in high_novelty):
            recommendations.append(
                "Coordination phenomena suggest potential paper on emergent collective behavior"
            )

        if any("phase_transition" in p["category"].lower() or "critical" in p["category"].lower()
               for p in high_novelty):
            recommendations.append(
                "Critical phenomena candidates for theoretical paper on phase transitions in multi-agent systems"
            )

        if len(insights) >= 3:
            recommendations.append(
                f"Rich theoretical insights ({len(insights)}) support a theoretical contributions paper"
            )

        # Check for universality classes
        categories = [p["category"] for p in high_novelty]
        if len(set(categories)) > 3:
            recommendations.append(
                "Diverse phenomena suggest potential paper on taxonomy of emergence"
            )

        return recommendations

    def generate_comprehensive_report(self, synthesis: SynthesizedFindings) -> str:
        """Generate comprehensive synthesis report"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE FINDINGS SYNTHESIS")
        report.append("=" * 80)
        report.append("")
        report.append(f"Synthesis ID: {synthesis.synthesis_id}")
        report.append(f"Timestamp: {synthesis.timestamp}")
        report.append("")

        # Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)
        report.append(f"Campaigns analyzed: {synthesis.n_campaigns}")
        report.append(f"Total discoveries: {synthesis.total_discoveries}")
        report.append(f"Unique phenomena: {synthesis.unique_phenomena}")
        report.append(f"High novelty phenomena: {len(synthesis.high_novelty_phenomena)}")
        report.append("")

        # Top discoveries
        report.append("TOP HIGH-NOVELTY DISCOVERIES")
        report.append("-" * 80)

        for i, phenomenon in enumerate(synthesis.high_novelty_phenomena[:10], 1):
            report.append(f"{i}. {phenomenon['name']}")
            report.append(f"   Short name: {phenomenon['short_name']}")
            report.append(f"   Category: {phenomenon['category']}")
            report.append(f"   Novelty: {phenomenon['novelty_score']:.3f}")
            report.append(f"   Description: {phenomenon['description'][:100]}...")
            report.append("")

        # Cross-cutting patterns
        if synthesis.cross_campaign_patterns:
            report.append("CROSS-CUTTING PATTERNS")
            report.append("-" * 80)
            for pattern in synthesis.cross_campaign_patterns:
                report.append(f"- {pattern}")
            report.append("")

        # Theoretical insights
        if synthesis.theoretical_insights:
            report.append("THEORETICAL INSIGHTS")
            report.append("-" * 80)
            for insight in synthesis.theoretical_insights[:10]:
                report.append(f"- {insight}")
            report.append("")

        # Practical applications
        if synthesis.practical_applications:
            report.append("PRACTICAL APPLICATIONS")
            report.append("-" * 80)
            for app in synthesis.practical_applications[:10]:
                report.append(f"- {app}")
            report.append("")

        # Publication recommendations
        if synthesis.publication_recommendations:
            report.append("PUBLICATION RECOMMENDATIONS")
            report.append("-" * 80)
            for i, rec in enumerate(synthesis.publication_recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")

        return "\n".join(report)

    def export_for_publication(self, synthesis: SynthesizedFindings, output_dir: str) -> None:
        """Export synthesized findings for publication"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate comprehensive report
        report = self.generate_comprehensive_report(synthesis)

        # Save main report
        report_file = output_path / "synthesis_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Saved synthesis report to {report_file}")

        # Save high novelty phenomena as JSON
        phenomena_file = output_path / "high_novelty_phenomena.json"
        with open(phenomena_file, 'w') as f:
            json.dump(synthesis.high_novelty_phenomena, f, indent=2)

        logger.info(f"Saved phenomena to {phenomena_file}")

        # Generate LaTeX table of phenomena
        latex_file = output_path / "phenomena_table.tex"
        latex_content = self._generate_latex_table(synthesis.high_novelty_phenomena)

        with open(latex_file, 'w') as f:
            f.write(latex_content)

        logger.info(f"Saved LaTeX table to {latex_file}")

    def _generate_latex_table(self, phenomena: List[Dict]) -> str:
        """Generate LaTeX table of phenomena"""
        latex = []
        latex.append("\\begin{table}[ht]")
        latex.append("\\centering")
        latex.append("\\caption{Discovered Emergent Phenomena}")
        latex.append("\\label{tab:phenomena}")
        latex.append("\\begin{tabular}{llcl}")
        latex.append("\\hline")
        latex.append("\\# & Phenomenon & Category & Novelty \\\\")
        latex.append("\\hline")

        for i, phenomenon in enumerate(phenomena[:20], 1):
            name = phenomenon.get("short_name", "").replace("_", "\\_")
            category = phenomenon.get("category", "").replace("_", "\\_")
            novelty = f"{phenomenon.get('novelty_score', 0):.2f}"

            latex.append(f"{i} & {name} & {category} & {novel} \\\\")

        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        return "\n".join(latex)


def main():
    """Main entry point for findings compilation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compile and synthesize findings from discovery campaigns"
    )

    parser.add_argument(
        "--results-dir",
        type=str,
        default="./discovery_results",
        help="Directory containing discovery campaign results"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./synthesis_results",
        help="Output directory for synthesized findings"
    )

    parser.add_argument(
        "--export",
        action="store_true",
        help="Export findings for publication"
    )

    args = parser.parse_args()

    # Create compiler
    compiler = FindingsCompiler(results_dir=args.results_dir)

    # Load data
    compiler.load_campaigns()
    compiler.load_phenomena()

    # Synthesize findings
    synthesis = compiler.synthesize_findings()

    # Generate report
    report = compiler.generate_comprehensive_report(synthesis)
    print(report)

    # Export if requested
    if args.export:
        compiler.export_for_publication(synthesis, args.output_dir)

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
