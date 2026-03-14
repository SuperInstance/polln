"""
Run all Phase 2 simulations and collect results
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Papers with simulation schemas
PAPERS_TO_VALIDATE = [
    ("P24", "papers/24-self-play-mechanisms/simulation_schema.py"),
    ("P25", "papers/25-hydraulic-intelligence/simulation_schema.py"),
    ("P26", "papers/26-value-networks/simulation_schema.py"),
    ("P27", "papers/27-emergence-detection/simulation_schema.py"),
    ("P28", "papers/28-stigmergic-coordination/simulation_schema.py"),
    ("P29", "papers/29-competitive-coevolution/simulation_schema.py"),
    ("P30", "papers/30-granularity-analysis/simulation_schema.py"),
    ("P31", "papers/31-health-prediction/simulation_schema.py"),
    ("P32", "papers/32-dreaming/simulation_schema.py"),
    ("P33", "papers/33-lora-swarms/simulation_schema.py"),
    ("P34", "papers/34-federated-learning/simulation_schema.py"),
    ("P35", "papers/35-guardian-angels/simulation_schema.py"),
    ("P36", "papers/36-time-travel-debug/simulation_schema.py"),
]

def run_simulation(paper_id, script_path):
    """Run a single simulation and capture output."""
    print(f"\n{'='*80}")
    print(f"Running {paper_id} simulation...")
    print(f"{'='*80}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout
        error = result.stderr

        # Parse output for key metrics
        lines = output.split('\n')

        results = {
            "paper_id": paper_id,
            "success": result.returncode == 0,
            "output": output,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

        # Extract validation claims
        for line in lines:
            if "VALIDATED" in line or "NOT VALIDATED" in line:
                print(line)

        # Extract summary if present
        for line in lines[-20:]:  # Check last 20 lines for summary
            if "Summary:" in line or "improvement:" in line or "correlation:" in line:
                print(line)

        return results

    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Simulation took too long")
        return {
            "paper_id": paper_id,
            "success": False,
            "error": "Timeout after 120 seconds",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return {
            "paper_id": paper_id,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def run_all_simulations():
    """Run all Phase 2 simulations."""
    print("\n" + "="*80)
    print("PHASE 2 SIMULATION SUITE")
    print("="*80)
    print(f"Total papers to validate: {len(PAPERS_TO_VALIDATE)}")
    print("Starting simulations...\n")

    all_results = []
    start_time = time.time()

    for i, (paper_id, script_path) in enumerate(PAPERS_TO_VALIDATE, 1):
        print(f"\n[{i}/{len(PAPERS_TO_VALIDATE)}] Processing {paper_id}...")

        # Check if file exists
        if not Path(script_path).exists():
            print(f"  [SKIP] File not found: {script_path}")
            continue

        result = run_simulation(paper_id, script_path)
        all_results.append(result)

        # Brief pause between simulations
        time.sleep(2)

    elapsed = time.time() - start_time

    # Summary
    print(f"\n{'='*80}")
    print("SIMULATION SUITE SUMMARY")
    print(f"{'='*80}")
    print(f"Total processed: {len(all_results)}")
    print(f"Successful: {sum(1 for r in all_results if r['success'])}")
    print(f"Failed: {sum(1 for r in all_results if not r['success'])}")
    print(f"Total time: {elapsed:.1f} seconds")

    # Save results
    output_file = f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    serializable_results = []
    for r in all_results:
        serializable = {
            "paper_id": r["paper_id"],
            "success": r["success"],
            "timestamp": r["timestamp"],
            "output_preview": r["output"][:500] if r["output"] else "",
            "error": r.get("error", "")
        }
        serializable_results.append(serializable)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total": len(all_results),
                "successful": sum(1 for r in all_results if r['success']),
                "failed": sum(1 for r in all_results if not r['success']),
                "elapsed_seconds": elapsed
            },
            "results": serializable_results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

    return all_results


if __name__ == "__main__":
    run_all_simulations()
