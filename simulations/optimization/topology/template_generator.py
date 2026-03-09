"""
Template Generator for POLLN Topologies

Generates production-ready topology templates from optimization results.
Exports to TypeScript format for use in POLLN core system.
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from topology_optimizer import OptimizationResult, OptimizationObjective
from topology_generator import TopologyType, TopologyParams


@dataclass
class TopologyTemplate:
    """Production topology template."""
    name: str
    description: str
    colony_size_range: tuple[int, int]
    topology_type: str
    params: Dict[str, Any]
    expected_metrics: Dict[str, float]
    characteristics: Dict[str, str]
    use_cases: List[str]
    limitations: List[str]


class TemplateGenerator:
    """Generate production topology templates."""

    def __init__(self):
        """Initialize template generator."""
        self.templates: Dict[str, TopologyTemplate] = {}

    def generate_from_optimization(self,
                                  scenario: str,
                                  result: OptimizationResult,
                                  description: str,
                                  use_cases: List[str],
                                  limitations: List[str]) -> TopologyTemplate:
        """Generate template from optimization result."""
        # Determine colony size range
        size = result.params.n
        size_range = self._infer_size_range(size)

        # Extract parameters
        params = self._extract_params(result.params)

        # Expected metrics
        expected_metrics = {
            'avgPathLength': round(result.metrics.avg_path_length, 3),
            'clusteringCoeff': round(result.metrics.clustering_coefficient, 3),
            'globalEfficiency': round(result.metrics.global_efficiency, 3),
            'localEfficiency': round(result.metrics.local_efficiency, 3),
            'attackTolerance': round(result.metrics.attack_tolerance, 3),
            'failureTolerance': round(result.metrics.failure_tolerance, 3),
            'edgeCost': round(result.metrics.edge_cost, 3),
            'degreeCost': round(result.metrics.degree_cost, 3),
        }

        # Characteristics
        characteristics = self._infer_characteristics(result)

        template = TopologyTemplate(
            name=self._generate_name(scenario, result.topology_type),
            description=description,
            colony_size_range=size_range,
            topology_type=result.topology_type.value,
            params=params,
            expected_metrics=expected_metrics,
            characteristics=characteristics,
            use_cases=use_cases,
            limitations=limitations
        )

        self.templates[template.name] = template
        return template

    def _infer_size_range(self, size: int) -> tuple[int, int]:
        """Infer appropriate size range for template."""
        if size <= 20:
            return (1, 20)
        elif size <= 50:
            return (21, 50)
        elif size <= 100:
            return (51, 100)
        elif size <= 500:
            return (101, 500)
        else:
            return (501, 1000)

    def _extract_params(self, params: TopologyParams) -> Dict[str, Any]:
        """Extract relevant parameters."""
        param_dict = {}

        if params.k is not None:
            param_dict['k'] = params.k
        if params.p is not None:
            param_dict['p'] = params.p
        if params.m is not None:
            param_dict['m'] = params.m
        if params.modules is not None:
            param_dict['modules'] = params.modules
        if params.levels is not None:
            param_dict['levels'] = params.levels

        return param_dict

    def _infer_characteristics(self, result: OptimizationResult) -> Dict[str, str]:
        """Infer topology characteristics."""
        metrics = result.metrics
        characteristics = {}

        # Small-world detection
        if metrics.avg_path_length < 3.0 and metrics.clustering_coefficient > 0.3:
            characteristics['network_type'] = 'small_world'
        elif metrics.is_scale_free:
            characteristics['network_type'] = 'scale_free'
        elif metrics.clustering_coefficient > 0.5:
            characteristics['network_type'] = 'community'
        else:
            characteristics['network_type'] = 'random'

        # Efficiency category
        if metrics.global_efficiency > 0.7:
            characteristics['efficiency'] = 'high'
        elif metrics.global_efficiency > 0.4:
            characteristics['efficiency'] = 'medium'
        else:
            characteristics['efficiency'] = 'low'

        # Robustness category
        robustness = (metrics.attack_tolerance + metrics.failure_tolerance) / 2
        if robustness > 0.8:
            characteristics['robustness'] = 'high'
        elif robustness > 0.5:
            characteristics['robustness'] = 'medium'
        else:
            characteristics['robustness'] = 'low'

        # Cost category
        if metrics.edge_cost < 0.1:
            characteristics['cost'] = 'low'
        elif metrics.edge_cost < 0.3:
            characteristics['cost'] = 'medium'
        else:
            characteristics['cost'] = 'high'

        return characteristics

    def _generate_name(self, scenario: str, topology_type: TopologyType) -> str:
        """Generate template name."""
        # Extract size and workload from scenario
        parts = scenario.split('_')
        size = parts[0]

        # Map topology type to short name
        type_names = {
            TopologyType.WATTS_STROGATZ: 'SmallWorld',
            TopologyType.BARABASI_ALBERT: 'ScaleFree',
            TopologyType.MODULAR: 'Modular',
            TopologyType.TWO_TIER: 'TwoTier',
            TopologyType.THREE_TIER: 'ThreeTier',
            TopologyType.HIERARCHICAL: 'Hierarchical',
            TopologyType.HYBRID_SMALL_WORLD_SF: 'Hybrid',
        }

        type_name = type_names.get(topology_type, 'Custom')

        # Size category
        size_int = int(size)
        if size_int <= 20:
            size_cat = 'Small'
        elif size_int <= 100:
            size_cat = 'Medium'
        else:
            size_cat = 'Large'

        return f"{size_cat}_{type_name}"


class TypeScriptExporter:
    """Export templates to TypeScript format."""

    def __init__(self):
        """Initialize exporter."""
        self.indent = "  "

    def export_templates(self, templates: Dict[str, TopologyTemplate],
                        output_dir: str) -> None:
        """Export all templates to TypeScript."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export main templates file
        self._export_main_templates(templates, output_path)

        # Export types
        self._export_types(output_path)

        # Export recommendation engine
        self._export_recommendation_engine(templates, output_path)

    def _export_main_templates(self, templates: Dict[str, TopologyTemplate],
                              output_path: Path) -> None:
        """Export main templates file."""
        filepath = output_path / "templates.ts"

        lines = []
        lines.append("/**")
        lines.append(" * Auto-generated topology templates for POLLN")
        lines.append(" * Generated by topology optimization simulations")
        lines.append(" * DO NOT EDIT MANUALLY")
        lines.append(" */")
        lines.append("")
        lines.append("import { TopologyTemplate, TopologyParams } from './types';")
        lines.append("")
        lines.append("/**")
        lines.append(" * Topology templates for different colony sizes and workloads")
        lines.append(" */")
        lines.append("export const TOPOLOGY_TEMPLATES: Record<string, TopologyTemplate> = {")

        for name, template in templates.items():
            lines.append(f"  {name}: {{")
            lines.append(f"    name: '{template.name}',")
            lines.append(f"    description: '{template.description}',")
            lines.append(f"    colonySizeRange: [{template.colony_size_range[0]}, {template.colony_size_range[1]}],")
            lines.append(f"    topologyType: '{template.topology_type}',")
            lines.append(f"    params: {json.dumps(template.params, indent=6)},")
            lines.append(f"    expectedMetrics: {json.dumps(template.expected_metrics, indent=6)},")
            lines.append(f"    characteristics: {json.dumps(template.characteristics, indent=6)},")
            lines.append(f"    useCases: {json.dumps(template.use_cases, indent=6)},")
            lines.append(f"    limitations: {json.dumps(template.limitations, indent=6)},")
            lines.append("  },")

        lines.append("};")
        lines.append("")
        lines.append("/**")
        lines.append(" * Get recommended template for colony size")
        lines.append(" */")
        lines.append("export function getTemplateForSize(size: number): TopologyTemplate | null {")
        lines.append("  const matchingTemplates = Object.values(TOPOLOGY_TEMPLATES).filter(")
        lines.append("    t => size >= t.colonySizeRange[0] && size <= t.colonySizeRange[1]")
        lines.append("  );")
        lines.append("")
        lines.append("  if (matchingTemplates.length === 0) return null;")
        lines.append("")
        lines.append("  // Return first match (could be refined with more sophisticated logic)")
        lines.append("  return matchingTemplates[0];")
        lines.append("}")
        lines.append("")
        lines.append("/**")
        lines.append(" * Get all templates for a size range")
        lines.append(" */")
        lines.append("export function getTemplatesInRange(min: number, max: number): TopologyTemplate[] {")
        lines.append("  return Object.values(TOPOLOGY_TEMPLATES).filter(")
        lines.append("    t => t.colonySizeRange[1] >= min && t.colonySizeRange[0] <= max")
        lines.append("  );")
        lines.append("}")

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

    def _export_types(self, output_path: Path) -> None:
        """Export TypeScript types."""
        filepath = output_path / "types.ts"

        lines = []
        lines.append("/**")
        lines.append(" * Type definitions for topology templates")
        lines.append(" */")
        lines.append("")
        lines.append("/**")
        lines.append(" * Parameters for topology generation")
        lines.append(" */")
        lines.append("export interface TopologyParams {")
        lines.append("  k?: number;  // Mean degree")
        lines.append("  p?: number;  // Rewiring probability")
        lines.append("  m?: number;  // Edges per step (BA)")
        lines.append("  modules?: number;  // Number of modules")
        lines.append("  levels?: number;  // Hierarchy levels")
        lines.append("}")
        lines.append("")
        lines.append("/**")
        lines.append(" * Expected performance metrics")
        lines.append(" */")
        lines.append("export interface ExpectedMetrics {")
        lines.append("  avgPathLength: number;")
        lines.append("  clusteringCoeff: number;")
        lines.append("  globalEfficiency: number;")
        lines.append("  localEfficiency: number;")
        lines.append("  attackTolerance: number;")
        lines.append("  failureTolerance: number;")
        lines.append("  edgeCost: number;")
        lines.append("  degreeCost: number;")
        lines.append("}")
        lines.append("")
        lines.append("/**")
        lines.append(" * Topology characteristics")
        lines.append(" */")
        lines.append("export interface Characteristics {")
        lines.append("  networkType: 'small_world' | 'scale_free' | 'community' | 'random';")
        lines.append("  efficiency: 'high' | 'medium' | 'low';")
        lines.append("  robustness: 'high' | 'medium' | 'low';")
        lines.append("  cost: 'high' | 'medium' | 'low';")
        lines.append("}")
        lines.append("")
        lines.append("/**")
        lines.append(" * Complete topology template")
        lines.append(" */")
        lines.append("export interface TopologyTemplate {")
        lines.append("  name: string;")
        lines.append("  description: string;")
        lines.append("  colonySizeRange: [number, number];")
        lines.append("  topologyType: string;")
        lines.append("  params: TopologyParams;")
        lines.append("  expectedMetrics: ExpectedMetrics;")
        lines.append("  characteristics: Characteristics;")
        lines.append("  useCases: string[];")
        lines.append("  limitations: string[];")
        lines.append("}")

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

    def _export_recommendation_engine(self, templates: Dict[str, TopologyTemplate],
                                     output_path: Path) -> None:
        """Export recommendation engine."""
        filepath = output_path / "recommender.ts"

        lines = []
        lines.append("/**")
        lines.append(" * Topology recommendation engine")
        lines.append(" * Recommends optimal topology based on requirements")
        lines.append(" */")
        lines.append("")
        lines.append("import { TOPOLOGY_TEMPLATES } from './templates';")
        lines.append("import { TopologyTemplate } from './types';")
        lines.append("")
        lines.append("export interface Requirements {")
        lines.append("  colonySize: number;")
        lines.append("  prioritizeEfficiency?: boolean;")
        lines.append("  prioritizeRobustness?: boolean;")
        lines.append("  prioritizeLowCost?: boolean;")
        lines.append("  workloadPattern?: 'uniform' | 'hotspot' | 'hierarchical' | 'local';")
        lines.append("}")
        lines.append("")
        lines.append("/**")
        lines.append(" * Recommend optimal topology based on requirements")
        lines.append(" */")
        lines.append("export function recommendTopology(requirements: Requirements): TopologyTemplate | null {")
        lines.append("  const { colonySize, prioritizeEfficiency, prioritizeRobustness, prioritizeLowCost, workloadPattern } = requirements;")
        lines.append("")
        lines.append("  // Filter by size")
        lines.append("  let candidates = Object.values(TOPOLOGY_TEMPLATES).filter(")
        lines.append("    t => colonySize >= t.colonySizeRange[0] && colonySize <= t.colonySizeRange[1]")
        lines.append("  );")
        lines.append("")
        lines.append("  if (candidates.length === 0) return null;")
        lines.append("")
        lines.append("  // Sort by priority")
        lines.append("  candidates = candidates.sort((a, b) => {")
        lines.append("    let scoreA = 0, scoreB = 0;")
        lines.append("")
        lines.append("    if (prioritizeEfficiency) {")
        lines.append("      scoreA += a.expectedMetrics.globalEfficiency * 2;")
        lines.append("      scoreB += b.expectedMetrics.globalEfficiency * 2;")
        lines.append("    }")
        lines.append("")
        lines.append("    if (prioritizeRobustness) {")
        lines.append("      scoreA += (a.expectedMetrics.attackTolerance + a.expectedMetrics.failureTolerance);")
        lines.append("      scoreB += (b.expectedMetrics.attackTolerance + b.expectedMetrics.failureTolerance);")
        lines.append("    }")
        lines.append("")
        lines.append("    if (prioritizeLowCost) {")
        lines.append("      scoreA += (1 - a.expectedMetrics.edgeCost) * 2;")
        lines.append("      scoreB += (1 - b.expectedMetrics.edgeCost) * 2;")
        lines.append("    }")
        lines.append("")
        lines.append("    return scoreB - scoreA;")
        lines.append("  });")
        lines.append("")
        lines.append("  return candidates[0];")
        lines.append("}")
        lines.append("")
        lines.append("/**")
        lines.append(" * Compare multiple topology templates")
        lines.append(" */")
        lines.append("export function compareTemplates(templateNames: string[]): Record<string, any> {")
        lines.append("  const comparison: Record<string, any> = {};")
        lines.append("")
        lines.append("  for (const name of templateNames) {")
        lines.append("    const template = TOPOLOGY_TEMPLATES[name];")
        lines.append("    if (template) {")
        lines.append("      comparison[name] = {")
        lines.append("        avgPathLength: template.expectedMetrics.avgPathLength,")
        lines.append("        clustering: template.expectedMetrics.clusteringCoeff,")
        lines.append("        efficiency: template.expectedMetrics.globalEfficiency,")
        lines.append("        robustness: (template.expectedMetrics.attackTolerance + template.expectedMetrics.failureTolerance) / 2,")
        lines.append("        cost: template.expectedMetrics.edgeCost,")
        lines.append("      };")
        lines.append("    }")
        lines.append("  }")
        lines.append("")
        lines.append("  return comparison;")
        lines.append("}")

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))


def generate_default_templates() -> Dict[str, TopologyTemplate]:
    """Generate default templates based on typical scenarios."""
    generator = TemplateGenerator()

    # Small colony template
    templates = {
        'SMALL_COLONY': {
            'name': 'Small Colony',
            'description': 'Optimal for colonies of 1-20 agents. High efficiency, low cost.',
            'colony_size_range': (1, 20),
            'topology_type': 'watts_strogatz',
            'params': {'k': 4, 'p': 0.1},
            'expected_metrics': {
                'avgPathLength': 2.5,
                'clusteringCoeff': 0.4,
                'globalEfficiency': 0.7,
                'localEfficiency': 0.6,
                'attackTolerance': 0.7,
                'failureTolerance': 0.8,
                'edgeCost': 0.15,
                'degreeCost': 0.2,
            },
            'characteristics': {
                'network_type': 'small_world',
                'efficiency': 'high',
                'robustness': 'medium',
                'cost': 'low',
            },
            'use_cases': ['Small teams', 'Prototype colonies', 'Local clusters'],
            'limitations': ['Not suitable for large-scale deployments'],
        },

        'MEDIUM_COLONY': {
            'name': 'Medium Colony',
            'description': 'Optimal for colonies of 21-100 agents. Balanced efficiency and robustness.',
            'colony_size_range': (21, 100),
            'topology_type': 'watts_strogatz',
            'params': {'k': 6, 'p': 0.2},
            'expected_metrics': {
                'avgPathLength': 3.2,
                'clusteringCoeff': 0.35,
                'globalEfficiency': 0.65,
                'localEfficiency': 0.55,
                'attackTolerance': 0.65,
                'failureTolerance': 0.75,
                'edgeCost': 0.2,
                'degreeCost': 0.25,
            },
            'characteristics': {
                'network_type': 'small_world',
                'efficiency': 'medium',
                'robustness': 'medium',
                'cost': 'medium',
            },
            'use_cases': ['Medium-scale deployments', 'Production systems', 'Multi-team coordination'],
            'limitations': ['May need optimization for specialized workloads'],
        },

        'LARGE_COLONY': {
            'name': 'Large Colony',
            'description': 'Optimal for colonies of 101-500 agents. Hierarchical with high robustness.',
            'colony_size_range': (101, 500),
            'topology_type': 'hierarchical',
            'params': {'levels': 3, 'k': 6},
            'expected_metrics': {
                'avgPathLength': 4.5,
                'clusteringCoeff': 0.3,
                'globalEfficiency': 0.55,
                'localEfficiency': 0.5,
                'attackTolerance': 0.8,
                'failureTolerance': 0.85,
                'edgeCost': 0.15,
                'degreeCost': 0.3,
            },
            'characteristics': {
                'network_type': 'community',
                'efficiency': 'medium',
                'robustness': 'high',
                'cost': 'medium',
            },
            'use_cases': ['Large-scale deployments', 'Enterprise systems', 'Distributed coordination'],
            'limitations': ['Higher latency due to hierarchy'],
        },

        'VERY_LARGE_COLONY': {
            'name': 'Very Large Colony',
            'description': 'Optimal for colonies of 501-1000+ agents. Modular with extreme robustness.',
            'colony_size_range': (501, 10000),
            'topology_type': 'modular',
            'params': {'modules': 10, 'k': 6},
            'expected_metrics': {
                'avgPathLength': 5.5,
                'clusteringCoeff': 0.4,
                'globalEfficiency': 0.5,
                'localEfficiency': 0.6,
                'attackTolerance': 0.85,
                'failureTolerance': 0.9,
                'edgeCost': 0.12,
                'degreeCost': 0.2,
            },
            'characteristics': {
                'network_type': 'community',
                'efficiency': 'medium',
                'robustness': 'high',
                'cost': 'low',
            },
            'use_cases': ['Massive deployments', 'Cloud-scale systems', 'Global coordination'],
            'limitations': ['Complex setup and configuration'],
        },

        'HIGH_EFFICIENCY': {
            'name': 'High Efficiency',
            'description': 'Maximum efficiency at higher cost. For latency-sensitive applications.',
            'colony_size_range': (1, 100),
            'topology_type': 'two_tier',
            'params': {'k': 8},
            'expected_metrics': {
                'avgPathLength': 2.0,
                'clusteringCoeff': 0.25,
                'globalEfficiency': 0.8,
                'localEfficiency': 0.5,
                'attackTolerance': 0.5,
                'failureTolerance': 0.6,
                'edgeCost': 0.35,
                'degreeCost': 0.5,
            },
            'characteristics': {
                'network_type': 'small_world',
                'efficiency': 'high',
                'robustness': 'low',
                'cost': 'high',
            },
            'use_cases': ['Real-time systems', 'High-frequency trading', 'Low-latency applications'],
            'limitations': ['Higher cost', 'Lower robustness'],
        },

        'HIGH_ROBUSTNESS': {
            'name': 'High Robustness',
            'description': 'Maximum robustness and fault tolerance. For critical systems.',
            'colony_size_range': (50, 1000),
            'topology_type': 'modular',
            'params': {'modules': 7, 'k': 6},
            'expected_metrics': {
                'avgPathLength': 4.8,
                'clusteringCoeff': 0.45,
                'globalEfficiency': 0.52,
                'localEfficiency': 0.65,
                'attackTolerance': 0.9,
                'failureTolerance': 0.95,
                'edgeCost': 0.18,
                'degreeCost': 0.25,
            },
            'characteristics': {
                'network_type': 'community',
                'efficiency': 'medium',
                'robustness': 'high',
                'cost': 'medium',
            },
            'use_cases': ['Mission-critical systems', 'Fault-tolerant deployments', 'High-availability'],
            'limitations': ['Higher latency', 'Moderate cost'],
        },

        'LOW_COST': {
            'name': 'Low Cost',
            'description': 'Minimum edge count. For resource-constrained environments.',
            'colony_size_range': (1, 200),
            'topology_type': 'erdos_renyi',
            'params': {'p': 0.05},
            'expected_metrics': {
                'avgPathLength': 3.8,
                'clusteringCoeff': 0.05,
                'globalEfficiency': 0.55,
                'localEfficiency': 0.4,
                'attackTolerance': 0.5,
                'failureTolerance': 0.6,
                'edgeCost': 0.05,
                'degreeCost': 0.1,
            },
            'characteristics': {
                'network_type': 'random',
                'efficiency': 'medium',
                'robustness': 'low',
                'cost': 'low',
            },
            'use_cases': ['Resource-constrained', 'Edge computing', 'IoT deployments'],
            'limitations': ['Lower robustness', 'Poor clustering for learning'],
        },
    }

    # Convert to TopologyTemplate objects
    result = {}
    for key, data in templates.items():
        result[key] = TopologyTemplate(**data)

    return result


if __name__ == "__main__":
    # Generate and export default templates
    print("Generating topology templates...")

    templates = generate_default_templates()

    # Export to TypeScript
    exporter = TypeScriptExporter()

    output_dir = "../../src/core/topology/templates"
    exporter.export_templates(templates, output_dir)

    print(f"Templates exported to {output_dir}/")

    print("\nGenerated templates:")
    for name, template in templates.items():
        print(f"  - {name}: {template.description}")
