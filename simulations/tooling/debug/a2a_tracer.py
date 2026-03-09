#!/usr/bin/env python3
"""
A2A Package Tracer - Trace and inspect A2A package flow through POLLN colonies.

This tool traces A2A packages as they flow through the colony, inspecting their
contents, causal chains, timestamps, and debugging issues like lost packages,
delays, and serialization problems.
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from collections import defaultdict
import hashlib


@dataclass
class A2APackageEvent:
    """An event in the lifecycle of an A2A package."""
    event_id: str
    package_id: str
    timestamp: float
    event_type: str  # 'created', 'sent', 'received', 'processed', 'dropped'
    agent_id: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class A2APackageSnapshot:
    """Snapshot of an A2A package at a point in time."""
    id: str
    timestamp: float
    sender_id: str
    receiver_id: Optional[str]
    type: str
    layer: str
    privacy_level: str
    parent_ids: List[str]
    causal_chain_id: str
    payload_hash: str
    payload_size: int
    current_agent: Optional[str]
    status: str  # 'in_transit', 'delivered', 'processed', 'dropped', 'stuck'

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CausalChainAnalysis:
    """Analysis of a causal chain."""
    chain_id: str
    depth: int
    branch_count: int
    total_packages: int
    root_package_id: str
    leaf_package_ids: List[str]
    cycle_detected: bool
    orphan_packages: List[str]
    avg_branching_factor: float

    def to_dict(self) -> Dict:
        return asdict(self)


class A2ATracer:
    """
    Trace and analyze A2A package flow through POLLN colonies.

    Features:
    - Real-time package flow tracing
    - Causal chain reconstruction and analysis
    - Lost package detection
    - Delay analysis
    - Serialization issue detection
    - Trace visualization
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Package tracking
        self.packages: Dict[str, A2APackageSnapshot] = {}
        self.events: List[A2APackageEvent] = []
        self.causal_chains: Dict[str, Set[str]] = defaultdict(set)  # chain_id -> package_ids

        # Analysis caches
        self.causal_chain_cache: Dict[str, CausalChainAnalysis] = {}
        self.lost_packages: Set[str] = set()
        self.stuck_packages: Set[str] = set()

    def record_event(self, event: A2APackageEvent) -> None:
        """Record a package event."""
        self.events.append(event)
        print(f"[{datetime.fromtimestamp(event.timestamp).isoformat()}] "
              f"{event.event_type.upper()}: {event.package_id} "
              f"({event.agent_id})")

    def trace_package(self, package_data: Dict[str, Any], current_agent: str,
                     status: str = 'in_transit') -> A2APackageSnapshot:
        """
        Trace an A2A package through the colony.

        Args:
            package_data: Dictionary containing package fields (id, timestamp, senderId, etc.)
            current_agent: ID of the agent currently handling the package
            status: Current status of the package

        Returns:
            A2APackageSnapshot: Snapshot of the package state
        """
        package_id = package_data.get('id', 'unknown')

        # Calculate payload hash for integrity checking
        payload = json.dumps(package_data.get('payload', {}), sort_keys=True)
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()

        snapshot = A2APackageSnapshot(
            id=package_id,
            timestamp=package_data.get('timestamp', 0),
            sender_id=package_data.get('senderId', 'unknown'),
            receiver_id=package_data.get('receiverId'),
            type=package_data.get('type', 'unknown'),
            layer=package_data.get('layer', 'UNKNOWN'),
            privacy_level=package_data.get('privacyLevel', 'PRIVATE'),
            parent_ids=package_data.get('parentIds', []),
            causal_chain_id=package_data.get('causalChainId', package_id),
            payload_hash=payload_hash,
            payload_size=len(payload.encode()),
            current_agent=current_agent,
            status=status
        )

        # Store snapshot
        self.packages[package_id] = snapshot

        # Track causal chain
        chain_id = snapshot.causal_chain_id
        self.causal_chains[chain_id].add(package_id)

        # Record event
        event = A2APackageEvent(
            event_id=f"{package_id}_{snapshot.timestamp}_{status}",
            package_id=package_id,
            timestamp=snapshot.timestamp,
            event_type=status,
            agent_id=current_agent,
            details={
                'layer': snapshot.layer,
                'type': snapshot.type,
                'parent_count': len(snapshot.parent_ids)
            }
        )
        self.record_event(event)

        return snapshot

    def find_lost_packages(self, timeout_seconds: float = 60.0) -> List[str]:
        """
        Find packages that are stuck or lost.

        Args:
            timeout_seconds: Time threshold for considering a package lost

        Returns:
            List of lost package IDs
        """
        current_time = datetime.now().timestamp()
        lost = []

        for package_id, snapshot in self.packages.items():
            if snapshot.status in ['in_transit', 'stuck']:
                age = current_time - snapshot.timestamp
                if age > timeout_seconds:
                    lost.append(package_id)
                    self.lost_packages.add(package_id)

        return lost

    def analyze_delays(self) -> Dict[str, Any]:
        """
        Analyze package delays through the colony.

        Returns:
            Dictionary with delay statistics
        """
        chain_delays: Dict[str, List[float]] = defaultdict(list)

        # Group events by causal chain
        for chain_id in self.causal_chains:
            chain_events = [e for e in self.events
                          if any(p_id in self.causal_chains[chain_id] for p_id in [e.package_id])]

            # Calculate delays between events
            sorted_events = sorted(chain_events, key=lambda e: e.timestamp)
            for i in range(1, len(sorted_events)):
                delay = sorted_events[i].timestamp - sorted_events[i-1].timestamp
                chain_delays[chain_id].append(delay)

        # Compute statistics
        stats = {}
        for chain_id, delays in chain_delays.items():
            if delays:
                stats[chain_id] = {
                    'avg_delay': sum(delays) / len(delays),
                    'min_delay': min(delays),
                    'max_delay': max(delays),
                    'total_delay': sum(delays),
                    'hop_count': len(delays)
                }

        return stats

    def detect_serialization_issues(self) -> List[Dict[str, Any]]:
        """
        Detect potential serialization issues.

        Returns:
            List of detected issues
        """
        issues = []

        for package_id, snapshot in self.packages.items():
            # Check for suspicious payload sizes
            if snapshot.payload_size == 0:
                issues.append({
                    'type': 'empty_payload',
                    'package_id': package_id,
                    'severity': 'warning',
                    'message': f'Package {package_id} has empty payload'
                })

            # Check for oversized payloads
            if snapshot.payload_size > 10_000_000:  # 10MB
                issues.append({
                    'type': 'oversized_payload',
                    'package_id': package_id,
                    'severity': 'warning',
                    'message': f'Package {package_id} has oversized payload: {snapshot.payload_size} bytes'
                })

        return issues

    def analyze_causal_chain(self, chain_id: str) -> CausalChainAnalysis:
        """
        Analyze a causal chain.

        Args:
            chain_id: ID of the causal chain to analyze

        Returns:
            CausalChainAnalysis: Analysis results
        """
        if chain_id in self.causal_chain_cache:
            return self.causal_chain_cache[chain_id]

        package_ids = self.causal_chains.get(chain_id, set())
        packages = [self.packages[pid] for pid in package_ids if pid in self.packages]

        if not packages:
            return CausalChainAnalysis(
                chain_id=chain_id,
                depth=0,
                branch_count=0,
                total_packages=0,
                root_package_id='',
                leaf_package_ids=[],
                cycle_detected=False,
                orphan_packages=[],
                avg_branching_factor=0.0
            )

        # Find root (no parents) and leaves (no children)
        all_ids = set(package_ids)
        parent_ids = set()
        for pkg in packages:
            parent_ids.update(pkg.parent_ids)

        root_ids = all_ids - parent_ids
        root_package_id = list(root_ids)[0] if root_ids else package_ids[0]

        # Find leaves (packages that are not parents of any other package)
        child_ids = set()
        for pkg in packages:
            child_ids.update(pkg.parent_ids)

        leaf_ids = all_ids - child_ids

        # Detect cycles
        cycle_detected = self._detect_cycles(chain_id)

        # Find orphan packages
        orphan_packages = [pid for pid in package_ids
                          if pid not in self.packages]

        # Calculate branching factor
        branch_count = len(package_ids) - len(root_ids)
        avg_branching = branch_count / len(package_ids) if package_ids else 0

        analysis = CausalChainAnalysis(
            chain_id=chain_id,
            depth=len(packages),  # Simplified depth calculation
            branch_count=branch_count,
            total_packages=len(package_ids),
            root_package_id=root_package_id,
            leaf_package_ids=list(leaf_ids),
            cycle_detected=cycle_detected,
            orphan_packages=orphan_packages,
            avg_branching_factor=avg_branching
        )

        self.causal_chain_cache[chain_id] = analysis
        return analysis

    def _detect_cycles(self, chain_id: str) -> bool:
        """Detect cycles in a causal chain using DFS."""
        package_ids = self.causal_chains.get(chain_id, set())
        visited = set()
        rec_stack = set()

        def dfs(pkg_id: str) -> bool:
            visited.add(pkg_id)
            rec_stack.add(pkg_id)

            if pkg_id in self.packages:
                for parent_id in self.packages[pkg_id].parent_ids:
                    if parent_id not in visited:
                        if dfs(parent_id):
                            return True
                    elif parent_id in rec_stack:
                        return True

            rec_stack.remove(pkg_id)
            return False

        return any(dfs(pid) for pid in package_ids if pid not in visited)

    def generate_trace_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive trace report.

        Returns:
            Dictionary containing all trace data and analysis
        """
        # Analyze all causal chains
        chain_analyses = {}
        for chain_id in self.causal_chains:
            chain_analyses[chain_id] = self.analyze_causal_chain(chain_id).to_dict()

        # Get delay statistics
        delay_stats = self.analyze_delays()

        # Detect serialization issues
        serialization_issues = self.detect_serialization_issues()

        # Find lost packages
        lost_packages = list(self.lost_packages)

        report = {
            'colony_id': self.colony_id,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_packages': len(self.packages),
                'total_events': len(self.events),
                'causal_chains': len(self.causal_chains),
                'lost_packages': len(lost_packages),
                'serialization_issues': len(serialization_issues)
            },
            'packages': {pid: pkg.to_dict() for pid, pkg in self.packages.items()},
            'events': [e.to_dict() for e in self.events],
            'causal_chain_analyses': chain_analyses,
            'delay_statistics': delay_stats,
            'lost_packages': lost_packages,
            'serialization_issues': serialization_issues
        }

        return report

    def save_trace_report(self, filename: str = "a2a_trace.json") -> str:
        """
        Save trace report to file.

        Args:
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        report = self.generate_trace_report()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Trace report saved to: {output_path}")
        return str(output_path)

    def visualize_flow(self, chain_id: Optional[str] = None) -> str:
        """
        Generate a simple text-based visualization of package flow.

        Args:
            chain_id: Optional causal chain ID to visualize

        Returns:
            String representation of the flow
        """
        if chain_id:
            package_ids = self.causal_chains.get(chain_id, set())
            packages = [self.packages[pid] for pid in package_ids if pid in self.packages]
        else:
            packages = list(self.packages.values())

        # Sort by timestamp
        packages = sorted(packages, key=lambda p: p.timestamp)

        lines = []
        lines.append("=" * 80)
        lines.append("A2A Package Flow Visualization")
        lines.append("=" * 80)

        for pkg in packages:
            lines.append(f"\n[{datetime.fromtimestamp(pkg.timestamp).isoformat()}]")
            lines.append(f"  Package: {pkg.id}")
            lines.append(f"  Type: {pkg.type} | Layer: {pkg.layer}")
            lines.append(f"  From: {pkg.sender_id} -> To: {pkg.receiver_id or 'Unknown'}")
            lines.append(f"  Current Agent: {pkg.current_agent}")
            lines.append(f"  Status: {pkg.status}")
            lines.append(f"  Parents: {len(pkg.parent_ids)} | Chain: {pkg.causal_chain_id}")

        return "\n".join(lines)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python a2a_tracer.py <colony_id> [command]")
        print("\nCommands:")
        print("  trace <package_file>     - Trace packages from JSON file")
        print("  report                    - Generate trace report")
        print("  visualize [chain_id]      - Visualize package flow")
        sys.exit(1)

    colony_id = sys.argv[1]
    tracer = A2ATracer(colony_id)

    if len(sys.argv) < 3:
        print("No command specified")
        sys.exit(1)

    command = sys.argv[2]

    if command == "trace" and len(sys.argv) >= 4:
        # Load and trace packages from file
        package_file = sys.argv[3]
        with open(package_file, 'r') as f:
            packages = json.load(f)

        for pkg_data in packages:
            tracer.trace_package(pkg_data, current_agent=pkg_data.get('currentAgent', 'unknown'),
                                status=pkg_data.get('status', 'in_transit'))

        print(f"Traced {len(packages)} packages")

    elif command == "report":
        tracer.save_trace_report()

    elif command == "visualize":
        chain_id = sys.argv[3] if len(sys.argv) >= 4 else None
        print(tracer.visualize_flow(chain_id))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
