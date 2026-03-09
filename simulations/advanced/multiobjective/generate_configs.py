"""
Generate Tiered Configuration Files

Creates production-ready configuration files for different tiers
from Pareto-optimized configurations.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import shutil


class ConfigGenerator:
    """Generate tiered configuration files."""

    def __init__(self, source_dir: str = None, output_dir: str = None):
        self.source_dir = Path(source_dir) if source_dir else \
            Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'
        self.output_dir = Path(output_dir) if output_dir else self.source_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_all_tiers(self) -> Dict[str, Dict]:
        """Load all tier configurations."""
        all_tiers = {}

        json_files = [
            'accuracy_cost_tiers.json',
            'speed_quality_tiers.json',
            'robustness_efficiency_tiers.json',
            'scalability_complexity_tiers.json'
        ]

        for filename in json_files:
            filepath = self.source_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    category = filename.replace('_tiers.json', '')
                    all_tiers[category] = data
                    print(f"Loaded {len(data)} tiers from {category}")

        return all_tiers

    def generate_tier_index(self, all_tiers: Dict[str, Dict]) -> str:
        """Generate master index of all tiers."""
        index = {
            'version': '1.0.0',
            'generated_at': str(Path(__file__).stat().st_mtime),
            'categories': list(all_tiers.keys()),
            'total_tiers': sum(len(v) for v in all_tiers.values()),
            'tiers': {}
        }

        for category, tiers in all_tiers.items():
            for tier_name, config in tiers.items():
                full_name = f"{category}_{tier_name}"
                index['tiers'][full_name] = {
                    'category': category,
                    'tier': tier_name,
                    'description': self._get_tier_description(category, tier_name),
                    'config': config
                }

        return index

    def _get_tier_description(self, category: str, tier: str) -> str:
        """Get human-readable description for tier."""
        descriptions = {
            'accuracy_cost': {
                'BUDGET': 'Maximum cost efficiency with acceptable quality',
                'STANDARD': 'Balanced performance and cost',
                'PERFORMANCE': 'High quality with moderate cost',
                'PREMIUM': 'Maximum quality regardless of cost',
                'MAXIMUM': 'Best possible accuracy'
            },
            'speed_quality': {
                'REALTIME': 'Sub-100ms latency for real-time applications',
                'INTERACTIVE': '100-500ms for interactive experiences',
                'FAST': '500-1000ms for responsive applications',
                'STANDARD': '1-2 second latency',
                'BATCH': 'High throughput for batch processing'
            },
            'robustness_efficiency': {
                'BASIC': '99% availability, minimal overhead',
                'HIGH': '99.9% availability with redundancy',
                'CRITICAL': '99.99% availability with full fault tolerance',
                'EXTREME': 'Maximum availability with disaster recovery'
            },
            'scalability_complexity': {
                'SMALL': '10-100 agents, simple topology',
                'MEDIUM': '100-500 agents, balanced complexity',
                'LARGE': '500-1000 agents, scaled infrastructure',
                'XLARGE': '1000+ agents, distributed system'
            }
        }

        return descriptions.get(category, {}).get(tier, f'{category} - {tier}')

    def generate_scenario_configs(self, all_tiers: Dict[str, Dict]) -> Dict[str, Dict]:
        """Generate scenario-based recommended configurations."""
        scenarios = {
            'production': {
                'description': 'High-availability production deployment',
                'primary_category': 'robustness_efficiency',
                'primary_tier': 'HIGH',
                'secondary': {
                    'speed_quality': 'INTERACTIVE',
                    'scalability_complexity': 'MEDIUM'
                }
            },
            'development': {
                'description': 'Development and testing environment',
                'primary_category': 'accuracy_cost',
                'primary_tier': 'BUDGET',
                'secondary': {
                    'speed_quality': 'STANDARD',
                    'robustness_efficiency': 'BASIC'
                }
            },
            'edge': {
                'description': 'Edge deployment with limited resources',
                'primary_category': 'speed_quality',
                'primary_tier': 'REALTIME',
                'secondary': {
                    'accuracy_cost': 'BUDGET',
                    'scalability_complexity': 'SMALL'
                }
            },
            'research': {
                'description': 'Research with maximum quality',
                'primary_category': 'accuracy_cost',
                'primary_tier': 'MAXIMUM',
                'secondary': {
                    'speed_quality': 'BATCH',
                    'robustness_efficiency': 'HIGH'
                }
            },
            'realtime': {
                'description': 'Real-time applications',
                'primary_category': 'speed_quality',
                'primary_tier': 'REALTIME',
                'secondary': {
                    'robustness_efficiency': 'HIGH',
                    'scalability_complexity': 'MEDIUM'
                }
            },
            'batch': {
                'description': 'High-throughput batch processing',
                'primary_category': 'scalability_complexity',
                'primary_tier': 'LARGE',
                'secondary': {
                    'speed_quality': 'BATCH',
                    'accuracy_cost': 'STANDARD'
                }
            }
        }

        scenario_configs = {}

        for scenario_name, scenario_config in scenarios.items():
            # Get primary config
            primary = all_tiers.get(scenario_config['primary_category'], {}).get(
                scenario_config['primary_tier'], {}
            )

            # Merge secondary configs
            merged = primary.copy()
            for category, tier in scenario_config['secondary'].items():
                secondary = all_tiers.get(category, {}).get(tier, {})
                merged.update(secondary)

            scenario_configs[scenario_name] = {
                'description': scenario_config['description'],
                'config': merged
            }

        return scenario_configs

    def generate_quick_reference(self, all_tiers: Dict[str, Dict]) -> str:
        """Generate quick reference guide."""
        lines = []
        lines.append("# POLLN Configuration Tiers - Quick Reference\n")
        lines.append("## Accuracy vs Cost Tiers\n")
        lines.append("| Tier | Description | Use Case |\n")
        lines.append("|------|-------------|----------|\n")

        accuracy_cost = all_tiers.get('accuracy_cost', {})
        for tier in ['BUDGET', 'STANDARD', 'PERFORMANCE', 'PREMIUM', 'MAXIMUM']:
            if tier in accuracy_cost:
                config = accuracy_cost[tier]
                desc = self._get_tier_description('accuracy_cost', tier)
                use_case = self._infer_use_case(config)
                lines.append(f"| {tier} | {desc} | {use_case} |\n")

        lines.append("\n## Speed vs Quality Tiers\n")
        lines.append("| Tier | Latency | Use Case |\n")
        lines.append("|------|---------|----------|\n")

        speed_quality = all_tiers.get('speed_quality', {})
        for tier in ['REALTIME', 'INTERACTIVE', 'FAST', 'STANDARD', 'BATCH']:
            if tier in speed_quality:
                config = speed_quality[tier]
                latency = config.get('expected_latency_ms', 'N/A')
                use_case = self._infer_use_case(config)
                lines.append(f"| {tier} | {latency}ms | {use_case} |\n")

        lines.append("\n## Robustness vs Efficiency Tiers\n")
        lines.append("| Tier | Availability | Use Case |\n")
        lines.append("|------|--------------|----------|\n")

        robustness = all_tiers.get('robustness_efficiency', {})
        for tier in ['BASIC', 'HIGH', 'CRITICAL', 'EXTREME']:
            if tier in robustness:
                config = robustness[tier]
                availability = config.get('expected_availability', 'N/A')
                use_case = self._infer_use_case(config)
                lines.append(f"| {tier} | {availability} | {use_case} |\n")

        lines.append("\n## Scalability vs Complexity Tiers\n")
        lines.append("| Tier | Colony Size | Use Case |\n")
        lines.append("|------|-------------|----------|\n")

        scalability = all_tiers.get('scalability_complexity', {})
        for tier in ['SMALL', 'MEDIUM', 'LARGE', 'XLARGE']:
            if tier in scalability:
                config = scalability[tier]
                size = config.get('colony_size', 'N/A')
                use_case = self._infer_use_case(config)
                lines.append(f"| {tier} | {size} | {use_case} |\n")

        return ''.join(lines)

    def _infer_use_case(self, config: Dict) -> str:
        """Infer use case from configuration."""
        latency = config.get('expected_latency_ms', 0)
        availability = config.get('expected_availability', '0%')

        if isinstance(availability, str):
            availability = float(availability.rstrip('%'))

        if latency < 100:
            return "Real-time systems"
        elif latency < 500:
            return "Interactive apps"
        elif availability > 99.9:
            return "Critical production"
        elif availability > 99.0:
            return "Production"
        else:
            return "Development/testing"

    def generate_typescript_definitions(self, all_tiers: Dict[str, Dict]) -> str:
        """Generate TypeScript type definitions."""
        lines = []

        lines.append("/**")
        lines.append(" * POLLN Configuration Tier Definitions")
        lines.append(" * Auto-generated from Pareto-optimized configurations")
        lines.append(" */")
        lines.append("")
        lines.append("export interface PollnConfig {")
        lines.append("  // Model parameters")
        lines.append("  modelSize?: string;")
        lines.append("  checkpointFrequency?: number;")
        lines.append("  cacheSize?: string;")
        lines.append("  kvCacheSize?: string;")
        lines.append("")
        lines.append("  // Inference parameters")
        lines.append("  batchSize?: number;")
        lines.append("  compressionLevel?: number;")
        lines.append("  temperature?: number;")
        lines.append("  topP?: number;")
        lines.append("  maxTokens?: number;")
        lines.append("")
        lines.append("  // Reliability parameters")
        lines.append("  replicationFactor?: number;")
        lines.append("  monitoringLevel?: number;")
        lines.append("  backupEnabled?: boolean;")
        lines.append("  healthCheckIntervalSec?: number;")
        lines.append("")
        lines.append("  // Scalability parameters")
        lines.append("  colonySize?: number;")
        lines.append("  topologyDepth?: number;")
        lines.append("  agentTypes?: number;")
        lines.append("  decentralizationLevel?: number;")
        lines.append("  horizontalScaling?: boolean;")
        lines.append("  autoScaling?: boolean;")
        lines.append("")
        lines.append("  // Target objective")
        lines.append("  target: string;")
        lines.append("}")
        lines.append("")
        lines.append("export type ConfigTier =")
        lines.append("  | 'BUDGET' | 'STANDARD' | 'PERFORMANCE' | 'PREMIUM' | 'MAXIMUM'")
        lines.append("  | 'REALTIME' | 'INTERACTIVE' | 'FAST' | 'BATCH'")
        lines.append("  | 'BASIC' | 'HIGH' | 'CRITICAL' | 'EXTREME'")
        lines.append("  | 'SMALL' | 'MEDIUM' | 'LARGE' | 'XLARGE';")
        lines.append("")
        lines.append("export interface ConfigCategory {")
        lines.append("  name: string;")
        lines.append("  description: string;")
        lines.append("  tiers: Record<ConfigTier, PollnConfig>;")
        lines.append("}")
        lines.append("")

        # Generate category interfaces
        for category, tiers in all_tiers.items():
            category_name = category.replace('_', ' ').title().replace(' ', '')
            lines.append(f"export const {category_name}Tiers: Record<ConfigTier, PollnConfig> = {{")

            for tier_name, config in tiers.items():
                lines.append(f"  {tier_name}: {{")

                for key, value in config.items():
                    ts_key = self._to_camel_case(key)
                    if isinstance(value, str):
                        lines.append(f"    {ts_key}: '{value}',")
                    elif isinstance(value, bool):
                        lines.append(f"    {ts_key}: {str(value).lower()},")
                    elif isinstance(value, (int, float)):
                        lines.append(f"    {ts_key}: {value},")
                    else:
                        lines.append(f"    {ts_key}: {value},")

                lines.append("  },")
                lines.append("")

            lines.append("};")
            lines.append("")

        lines.append("export const AllConfigTiers: Record<string, PollnConfig> = {")
        lines.append("  ...AccuracyCostTiers,")
        lines.append("  ...SpeedQualityTiers,")
        lines.append("  ...RobustnessEfficiencyTiers,")
        lines.append("  ...ScalabilityComplexityTiers,")
        lines.append("};")
        lines.append("")

        return ''.join(lines)

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def generate_all(self):
        """Generate all configuration files."""
        print("=" * 70)
        print("GENERATING TIERED CONFIGURATION FILES")
        print("=" * 70)

        # Load all tiers
        all_tiers = self.load_all_tiers()

        if not all_tiers:
            print("Error: No tier configurations found!")
            print(f"Looking in: {self.source_dir}")
            return

        # Generate master index
        print("\nGenerating master index...")
        index = self.generate_tier_index(all_tiers)
        index_path = self.output_dir / 'index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        print(f"✓ Generated: {index_path}")

        # Generate scenario configs
        print("\nGenerating scenario configurations...")
        scenario_configs = self.generate_scenario_configs(all_tiers)
        scenarios_path = self.output_dir / 'scenarios.json'
        with open(scenarios_path, 'w') as f:
            json.dump(scenario_configs, f, indent=2)
        print(f"✓ Generated: {scenarios_path}")

        # Generate quick reference
        print("\nGenerating quick reference guide...")
        quick_ref = self.generate_quick_reference(all_tiers)
        ref_path = self.output_dir / 'QUICK_REFERENCE.md'
        with open(ref_path, 'w') as f:
            f.write(quick_ref)
        print(f"✓ Generated: {ref_path}")

        # Generate TypeScript definitions
        print("\nGenerating TypeScript definitions...")
        ts_defs = self.generate_typescript_definitions(all_tiers)
        ts_path = self.output_dir / 'types.ts'
        with open(ts_path, 'w') as f:
            f.write(ts_defs)
        print(f"✓ Generated: {ts_path}")

        # Copy to src/core/config if path exists
        core_config_dir = Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config'
        if core_config_dir.exists():
            print(f"\nCopying to {core_config_dir}...")
            for file in ['index.json', 'scenarios.json', 'types.ts', 'QUICK_REFERENCE.md']:
                src = self.output_dir / file
                dst = core_config_dir / file
                if src.exists():
                    shutil.copy(src, dst)
                    print(f"  ✓ Copied {file}")

        print("\n" + "=" * 70)
        print("CONFIGURATION GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nGenerated files in {self.output_dir}:")
        print("  - index.json: Master index of all tiers")
        print("  - scenarios.json: Scenario-based recommended configs")
        print("  - QUICK_REFERENCE.md: Quick reference guide")
        print("  - types.ts: TypeScript type definitions")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate tiered configuration files')
    parser.add_argument('--source-dir', type=str,
                       help='Source directory for tier JSON files')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for generated files')

    args = parser.parse_args()

    generator = ConfigGenerator(
        source_dir=args.source_dir,
        output_dir=args.output_dir
    )
    generator.generate_all()


if __name__ == '__main__':
    main()
