#!/usr/bin/env python3
"""
Validate all simulation schemas across P24-P40.

Ensures all simulations run successfully and produce valid results.
This script is part of the CI/CD pipeline for SuperInstance papers.

Author: SuperInstance Research Team
Version: 1.0.0
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Add papers directory to path
repo_root = Path(__file__).parent.parent
papers_dir = repo_root / "papers"
sys.path.insert(0, str(papers_dir))

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class ValidationResult:
    """Result of validating a single schema."""
    paper_number: str
    paper_name: str
    status: str  # "success", "partial", "error"
    claims_validated: int = 0
    total_claims: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "paper_number": self.paper_number,
            "paper_name": self.paper_name,
            "status": self.status,
            "claims_validated": self.claims_validated,
            "total_claims": self.total_claims,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "details": self.details
        }


# =============================================================================
# Simulation Schema Registry
# =============================================================================

SIMULATION_SCHEMAS = [
    # Phase 2: High Priority (P24-P27)
    {
        "paper_number": "24",
        "paper_name": "24-self-play-mechanisms",
        "module_name": "simulation_schema",
        "priority": "high",
        "claims": [
            "claim_1_self_play_improvement",
            "claim_2_elo_correlation",
            "claim_3_novel_strategies",
            "claim_4_edge_case_discovery"
        ]
    },
    {
        "paper_number": "25",
        "paper_name": "25-hydraulic-intelligence",
        "module_name": "simulation_schema",
        "priority": "high",
        "claims": [
            "claim_1_pressure_activation",
            "claim_2_flow_conservation",
            "claim_3_emergence_detection",
            "claim_4_shannon_stability"
        ]
    },
    {
        "paper_number": "26",
        "paper_name": "26-value-networks",
        "module_name": "simulation_schema",
        "priority": "high",
        "claims": [
            "claim_1_value_correlation",
            "claim_2_uncertainty_calibration",
            "claim_3_value_guided_performance",
            "claim_4_dreaming_improvement"
        ]
    },
    {
        "paper_number": "27",
        "paper_name": "27-emergence-detection",
        "module_name": "simulation_schema",
        "priority": "high",
        "claims": [
            "claim_1_emergence_score_predicts",
            "claim_2_transfer_entropy_detection",
            "claim_3_composition_novelty",
            "claim_4_early_detection_enables"
        ]
    },

    # Phase 2: Medium Priority (P28-P30)
    {
        "paper_number": "28",
        "paper_name": "28-stigmergic-coordination",
        "module_name": "simulation_schema",
        "priority": "medium",
        "claims": [
            "claim_1_pheromone_efficiency",
            "claim_2_self_organization",
            "claim_3_scalability",
            "claim_4_fault_tolerance"
        ]
    },
    {
        "paper_number": "29",
        "paper_name": "29-competitive-coevolution",
        "module_name": "simulation_schema",
        "priority": "medium",
        "claims": [
            "claim_1_arms_race_improves",
            "claim_2_diversity_maintained",
            "claim_3_niches_formed",
            "claim_4_oscillation_dampens"
        ]
    },
    {
        "paper_number": "30",
        "paper_name": "30-granularity-analysis",
        "module_name": "simulation_schema",
        "priority": "medium",
        "claims": [
            "claim_1_optimal_complexity",
            "claim_2_granular_adaptation",
            "claim_3_efficiency_gain",
            "claim_4_cost_tradeoff"
        ]
    },

    # Phase 2: Extensions (P31-P40)
    {
        "paper_number": "31",
        "paper_name": "31-health-prediction",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_multidimensional_prediction",
            "claim_2_early_detection",
            "claim_3_intervention_efficacy"
        ]
    },
    {
        "paper_number": "32",
        "paper_name": "32-dreaming",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_overnight_optimization",
            "claim_2_consolidation_improves",
            "claim_3_dream_quality_correlates"
        ]
    },
    {
        "paper_number": "33",
        "paper_name": "33-lora-swarms",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_emergent_composition",
            "claim_2_efficient_coordination",
            "claim_3_scalable_integration"
        ]
    },
    {
        "paper_number": "34",
        "paper_name": "34-federated-learning",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_privacy_preserved",
            "claim_2_convergence_achieved",
            "claim_3_communication_efficient"
        ]
    },
    {
        "paper_number": "35",
        "paper_name": "35-guardian-angels",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_shadow_monitoring",
            "claim_2_anomaly_detection",
            "claim_3_automatic_recovery"
        ]
    },
    {
        "paper_number": "36",
        "paper_name": "36-time-travel-debug",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_replay_accurate",
            "claim_2_causal_traces",
            "claim_3_reverse_execution"
        ]
    },
    {
        "paper_number": "37",
        "paper_name": "37-energy-aware",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_thermodynamic_learning",
            "claim_2_energy_efficient",
            "claim_3_temperature_scaling"
        ]
    },
    {
        "paper_number": "38",
        "paper_name": "38-zk-proofs",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_capability_verified",
            "claim_2_privacy_preserved",
            "claim_3_proof_efficient"
        ]
    },
    {
        "paper_number": "39",
        "paper_name": "39-holographic-memory",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_distributed_storage",
            "claim_2_redundancy_tolerant",
            "claim_3_reconstruction_accurate"
        ]
    },
    {
        "paper_number": "40",
        "paper_name": "40-quantum-superposition",
        "module_name": "simulation_schema",
        "priority": "extension",
        "claims": [
            "claim_1_uncertain_state",
            "claim_2_superposition_advantage",
            "claim_3_collapse_correct"
        ]
    }
]


# =============================================================================
# Validation Functions
# =============================================================================

def validate_schema(paper_config: Dict) -> ValidationResult:
    """
    Validate a single simulation schema.

    Args:
        paper_config: Configuration for the paper to validate

    Returns:
        ValidationResult with validation outcome
    """
    start_time = time.time()
    paper_path = papers_dir / paper_config["paper_name"]
    module_name = paper_config["module_name"]

    logger.info(f"Validating {paper_config['paper_name']}...")

    try:
        # Check if paper directory exists
        if not paper_path.exists():
            return ValidationResult(
                paper_number=paper_config["paper_number"],
                paper_name=paper_config["paper_name"],
                status="error",
                error_message=f"Paper directory not found: {paper_path}",
                duration_seconds=time.time() - start_time
            )

        # Import module
        import importlib
        module_path = f"{paper_config['paper_name']}.{module_name}"

        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            return ValidationResult(
                paper_number=paper_config["paper_number"],
                paper_name=paper_config["paper_name"],
                status="error",
                error_message=f"Module not found: {module_path}",
                duration_seconds=time.time() - start_time
            )

        # Run validation
        results = {}

        # Check for run_validation function
        if hasattr(module, 'run_validation'):
            logger.info(f"  Running {module_path}.run_validation()")
            results = module.run_validation()

        # Check for run function (alternative)
        elif hasattr(module, 'run'):
            logger.info(f"  Running {module_path}.run()")
            results = module.run()

            # If run() returns a dict, check for validation summary
            if isinstance(results, dict):
                # Convert run() output to validation format
                results = normalize_run_output(results, paper_config["claims"])
        else:
            return ValidationResult(
                paper_number=paper_config["paper_number"],
                paper_name=paper_config["paper_name"],
                status="error",
                error_message="No run_validation() or run() function found",
                duration_seconds=time.time() - start_time
            )

        # Analyze results
        duration = time.time() - start_time

        if "summary" in results or results:
            claims_validated = 0
            total_claims = 0

            for claim_key in paper_config["claims"]:
                if claim_key in results:
                    total_claims += 1
                    claim_data = results[claim_key]

                    if isinstance(claim_data, dict):
                        if claim_data.get("validated", False):
                            claims_validated += 1

            # Determine status
            if claims_validated == total_claims and total_claims > 0:
                status = "success"
            elif claims_validated > 0:
                status = "partial"
            else:
                status = "error"

            return ValidationResult(
                paper_number=paper_config["paper_number"],
                paper_name=paper_config["paper_name"],
                status=status,
                claims_validated=claims_validated,
                total_claims=total_claims,
                duration_seconds=duration,
                details={"raw_results": results}
            )
        else:
            return ValidationResult(
                paper_number=paper_config["paper_number"],
                paper_name=paper_config["paper_name"],
                status="error",
                error_message="No validation results returned",
                duration_seconds=duration
            )

    except Exception as e:
        logger.error(f"  Error validating {paper_config['paper_name']}: {e}")
        return ValidationResult(
            paper_number=paper_config["paper_number"],
            paper_name=paper_config["paper_name"],
            status="error",
            error_message=str(e),
            duration_seconds=time.time() - start_time
        )


def normalize_run_output(output: Dict, expected_claims: List[str]) -> Dict:
    """
    Normalize output from run() function to validation format.

    Args:
        output: Raw output from run()
        expected_claims: List of expected claim keys

    Returns:
        Normalized validation results
    """
    normalized = {}

    # If output already has claim data, return as-is
    for claim_key in expected_claims:
        if claim_key in output:
            normalized[claim_key] = output[claim_key]

    # Add summary if not present
    if "summary" not in normalized:
        validated_count = sum(
            1 for v in normalized.values()
            if isinstance(v, dict) and v.get("validated", False)
        )
        normalized["summary"] = {
            "total_claims": len(expected_claims),
            "validated": validated_count
        }

    return normalized


# =============================================================================
# Summary Generation
# =============================================================================

def generate_summary_report(results: List[ValidationResult]) -> Dict[str, Any]:
    """
    Generate comprehensive summary report.

    Args:
        results: List of validation results

    Returns:
        Summary report dictionary
    """
    total = len(results)
    successful = sum(1 for r in results if r.status == "success")
    partial = sum(1 for r in results if r.status == "partial")
    errors = sum(1 for r in results if r.status == "error")

    total_duration = sum(r.duration_seconds for r in results)

    # Calculate success rate
    success_rate = (successful + partial) / total if total > 0 else 0.0

    # Count claims
    total_claims = sum(r.total_claims for r in results)
    total_validated = sum(r.claims_validated for r in results)

    # Group by priority
    by_priority = {
        "high": {"total": 0, "successful": 0, "partial": 0, "errors": 0},
        "medium": {"total": 0, "successful": 0, "partial": 0, "errors": 0},
        "extension": {"total": 0, "successful": 0, "partial": 0, "errors": 0}
    }

    for schema in SIMULATION_SCHEMAS:
        priority = schema["priority"]
        by_priority[priority]["total"] += 1

    for result in results:
        schema = next(
            (s for s in SIMULATION_SCHEMAS if s["paper_number"] == result.paper_number),
            None
        )
        if schema:
            priority = schema["priority"]
            if result.status == "success":
                by_priority[priority]["successful"] += 1
            elif result.status == "partial":
                by_priority[priority]["partial"] += 1
            elif result.status == "error":
                by_priority[priority]["errors"] += 1

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_schemas": total,
            "fully_validated": successful,
            "partially_validated": partial,
            "errors": errors,
            "success_rate": success_rate,
            "total_claims": total_claims,
            "claims_validated": total_validated,
            "claim_validation_rate": total_validated / total_claims if total_claims > 0 else 0.0,
            "total_duration_seconds": total_duration
        },
        "by_priority": by_priority,
        "detailed_results": [r.to_dict() for r in results]
    }


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Main execution function."""
    print("=" * 80)
    print("SuperInstance Simulation Schema Validation")
    print("=" * 80)
    print()

    results = []
    quick_mode = os.getenv("QUICK_VALIDATE", "false").lower() == "true"

    # Filter schemas based on mode
    schemas_to_validate = SIMULATION_SCHEMAS
    if quick_mode:
        logger.info("Quick mode: validating only high-priority schemas (P24-P27)")
        schemas_to_validate = [s for s in SIMULATION_SCHEMAS if s["priority"] == "high"]

    # Validate each schema
    for paper_config in schemas_to_validate:
        print(f"\nValidating {paper_config['paper_name']} (Priority: {paper_config['priority']})...")
        result = validate_schema(paper_config)
        results.append(result)

        # Print result
        status_icon = {
            "success": "[PASS]",
            "partial": "[PARTIAL]",
            "error": "[FAIL]"
        }.get(result.status, "[UNKNOWN]")

        print(f"  {status_icon} {result.status.upper()}")

        if result.status == "error":
            print(f"    Error: {result.error_message}")
        elif result.status in ["success", "partial"]:
            print(f"    Claims: {result.claims_validated}/{result.total_claims} validated")
            print(f"    Duration: {result.duration_seconds:.2f}s")

    # Generate and print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    summary = generate_summary_report(results)

    print(f"\nTotal schemas: {summary['summary']['total_schemas']}")
    print(f"  Fully validated: {summary['summary']['fully_validated']}")
    print(f"  Partially validated: {summary['summary']['partially_validated']}")
    print(f"  Errors: {summary['summary']['errors']}")

    print(f"\nClaims:")
    print(f"  Total: {summary['summary']['total_claims']}")
    print(f"  Validated: {summary['summary']['claims_validated']}")
    print(f"  Rate: {summary['summary']['claim_validation_rate']:.1%}")

    print(f"\nSuccess rate: {summary['summary']['success_rate']:.1%}")
    print(f"Total duration: {summary['summary']['total_duration_seconds']:.2f}s")

    # Priority breakdown
    print("\nBy Priority:")
    for priority, stats in summary["by_priority"].items():
        if stats["total"] > 0:
            print(f"  {priority.capitalize()}:")
            print(f"    Total: {stats['total']}")
            print(f"    Success: {stats['successful']}")
            print(f"    Partial: {stats['partial']}")
            print(f"    Errors: {stats['errors']}")

    # Determine exit code
    success_rate = summary['summary']['success_rate']
    if success_rate < 0.5:
        print(f"\nCRITICAL: Success rate {success_rate:.1%} below 50%")
        return 1
    elif success_rate < 0.8:
        print(f"\nWARNING: Success rate {success_rate:.1%} below 80%")
        return 0
    else:
        print(f"\nSUCCESS: Success rate {success_rate:.1%} meets threshold")
        return 0


if __name__ == "__main__":
    sys.exit(main())
