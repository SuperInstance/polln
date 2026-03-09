#!/usr/bin/env python3
"""
Colony Diagnostics - Comprehensive health diagnostics for POLLN colonies.

This tool performs health checks on POLLN colonies, detecting deadlocks,
resource exhaustion, communication failures, unhealthy agents, bottlenecks,
and cascading failures.
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple
from pathlib import Path
from collections import defaultdict
import time


@dataclass
class HealthMetric:
    """A health metric for the colony."""
    name: str
    value: float
    threshold: float
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    recommendation: Optional[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DeadlockDetection:
    """Results of deadlock detection."""
    is_deadlocked: bool
    deadlock_cycle: List[str]  # Agent IDs involved in deadlock
    deadlock_type: str  # 'resource', 'communication', 'causal'
    severity: str
    description: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ResourceUsage:
    """Resource usage statistics."""
    agent_id: str
    cpu_percent: float
    memory_mb: float
    network_io_mb: float
    active_connections: int
    queue_depth: int

    # Health indicators
    cpu_status: str
    memory_status: str
    network_status: str
    queue_status: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BottleneckAnalysis:
    """Analysis of colony bottlenecks."""
    bottlenecks: List[Dict[str, Any]]
    throughput: float
    avg_latency: float
    p95_latency: float
    p99_latency: float
    overloaded_agents: List[str]
    underutilized_agents: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CascadeFailureReport:
    """Report on potential cascading failures."""
    at_risk_agents: List[str]
    failure_probability: float
    propagation_path: List[str]
    triggers: List[str]
    mitigation_actions: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class ColonyDiagnostics:
    """
    Comprehensive colony health diagnostics.

    Features:
    - Deadlock detection (resource, communication, causal)
    - Resource exhaustion detection
    - Communication failure analysis
    - Agent health monitoring
    - Bottleneck identification
    - Cascading failure prediction
    - Performance metrics
    - Health recommendations
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Health tracking
        self.health_metrics: List[HealthMetric] = []
        self.resource_usage: Dict[str, ResourceUsage] = {}
        self.communication_matrix: Dict[Tuple[str, str], int] = defaultdict(int)
        self.agent_errors: Dict[str, List[Dict]] = defaultdict(list)

        # Analysis caches
        self.deadlock_cache: Optional[DeadlockDetection] = None
        self.bottleneck_cache: Optional[BottleneckAnalysis] = None
        self.cascade_cache: Optional[CascadeFailureReport] = None

        # Thresholds
        self.cpu_threshold = 80.0  # percent
        self.memory_threshold = 90.0  # percent
        self.queue_threshold = 1000  # items
        self.latency_threshold = 5000  # ms

    def check_agent_health(self, agent_id: str, agent_data: Dict[str, Any]) -> List[HealthMetric]:
        """
        Check the health of a single agent.

        Args:
            agent_id: Agent ID
            agent_data: Dictionary containing agent state

        Returns:
            List of health metrics
        """
        metrics = []

        # Check status
        status = agent_data.get('status', 'unknown')
        if status == 'error':
            metrics.append(HealthMetric(
                name=f"{agent_id}_status",
                value=0,
                threshold=1,
                status='critical',
                message=f"Agent {agent_id} is in error state",
                recommendation="Check agent logs and restart if necessary"
            ))

        # Check value function
        value_function = agent_data.get('valueFunction', 0.5)
        if value_function < 0.2:
            metrics.append(HealthMetric(
                name=f"{agent_id}_value_function",
                value=value_function,
                threshold=0.2,
                status='critical',
                message=f"Agent {agent_id} has very low value function: {value_function:.3f}",
                recommendation="Review agent performance and consider retraining"
            ))
        elif value_function < 0.4:
            metrics.append(HealthMetric(
                name=f"{agent_id}_value_function",
                value=value_function,
                threshold=0.4,
                status='warning',
                message=f"Agent {agent_id} has declining value function: {value_function:.3f}",
                recommendation="Monitor agent performance closely"
            ))

        # Check success rate
        success_count = agent_data.get('successCount', 0)
        failure_count = agent_data.get('failureCount', 0)
        total = success_count + failure_count
        if total > 10:
            success_rate = success_count / total
            if success_rate < 0.5:
                metrics.append(HealthMetric(
                    name=f"{agent_id}_success_rate",
                    value=success_rate,
                    threshold=0.5,
                    status='critical',
                    message=f"Agent {agent_id} has low success rate: {success_rate:.1%}",
                    recommendation="Review agent behavior and update training data"
                ))

        # Check activity
        last_active = agent_data.get('lastActive', 0)
        idle_time = time.time() - last_active
        if idle_time > 600:  # 10 minutes
            metrics.append(HealthMetric(
                name=f"{agent_id}_activity",
                value=idle_time,
                threshold=600,
                status='warning',
                message=f"Agent {agent_id} has been idle for {idle_time:.0f} seconds",
                recommendation="Check if agent is stuck or has no work"
            ))

        self.health_metrics.extend(metrics)
        return metrics

    def record_resource_usage(self, agent_id: str, resource_data: Dict[str, Any]) -> ResourceUsage:
        """
        Record resource usage for an agent.

        Args:
            agent_id: Agent ID
            resource_data: Dictionary containing resource metrics

        Returns:
            ResourceUsage: Resource usage snapshot
        """
        cpu = resource_data.get('cpuPercent', 0)
        memory_mb = resource_data.get('memoryMb', 0)
        network_io = resource_data.get('networkIoMb', 0)
        connections = resource_data.get('activeConnections', 0)
        queue_depth = resource_data.get('queueDepth', 0)

        # Determine status based on thresholds
        cpu_status = 'critical' if cpu > 90 else ('warning' if cpu > self.cpu_threshold else 'healthy')
        memory_status = 'critical' if memory_mb > 900 else ('warning' if memory_mb > 700 else 'healthy')
        network_status = 'warning' if network_io > 100 else 'healthy'
        queue_status = 'critical' if queue_depth > 2000 else ('warning' if queue_depth > self.queue_threshold else 'healthy')

        usage = ResourceUsage(
            agent_id=agent_id,
            cpu_percent=cpu,
            memory_mb=memory_mb,
            network_io_mb=network_io,
            active_connections=connections,
            queue_depth=queue_depth,
            cpu_status=cpu_status,
            memory_status=memory_status,
            network_status=network_status,
            queue_status=queue_status
        )

        self.resource_usage[agent_id] = usage
        return usage

    def record_communication(self, sender_id: str, receiver_id: str) -> None:
        """Record a communication event between agents."""
        self.communication_matrix[(sender_id, receiver_id)] += 1

    def record_error(self, agent_id: str, error_data: Dict[str, Any]) -> None:
        """Record an error for an agent."""
        self.agent_errors[agent_id].append({
            'timestamp': time.time(),
            **error_data
        })

    def detect_deadlocks(self) -> DeadlockDetection:
        """
        Detect deadlocks in the colony.

        Returns:
            DeadlockDetection: Results of deadlock detection
        """
        if self.deadlock_cache:
            return self.deadlock_cache

        # Check for resource deadlock (agents waiting on each other)
        waiting_graph = self._build_waiting_graph()
        resource_cycle = self._find_cycle(waiting_graph)

        # Check for communication deadlock
        comm_cycle = self._check_communication_deadlock()

        # Determine deadlock type and severity
        if resource_cycle:
            detection = DeadlockDetection(
                is_deadlocked=True,
                deadlock_cycle=resource_cycle,
                deadlock_type='resource',
                severity='critical',
                description=f"Resource deadlock detected involving {len(resource_cycle)} agents"
            )
        elif comm_cycle:
            detection = DeadlockDetection(
                is_deadlocked=True,
                deadlock_cycle=comm_cycle,
                deadlock_type='communication',
                severity='critical',
                description=f"Communication deadlock detected involving {len(comm_cycle)} agents"
            )
        else:
            detection = DeadlockDetection(
                is_deadlocked=False,
                deadlock_cycle=[],
                deadlock_type='none',
                severity='none',
                description="No deadlocks detected"
            )

        self.deadlock_cache = detection
        return detection

    def analyze_bottlenecks(self) -> BottleneckAnalysis:
        """
        Analyze colony bottlenecks.

        Returns:
            BottleneckAnalysis: Bottleneck analysis results
        """
        if self.bottleneck_cache:
            return self.bottleneck_cache

        bottlenecks = []
        overloaded = []
        underutilized = []

        # Check each agent for bottlenecks
        for agent_id, usage in self.resource_usage.items():
            # CPU bottleneck
            if usage.cpu_percent > 90:
                bottlenecks.append({
                    'agent_id': agent_id,
                    'type': 'cpu',
                    'severity': 'critical',
                    'value': usage.cpu_percent,
                    'message': f"Agent {agent_id} is CPU overloaded"
                })
                overloaded.append(agent_id)
            elif usage.cpu_percent < 10:
                underutilized.append(agent_id)

            # Memory bottleneck
            if usage.memory_mb > 900:
                bottlenecks.append({
                    'agent_id': agent_id,
                    'type': 'memory',
                    'severity': 'critical',
                    'value': usage.memory_mb,
                    'message': f"Agent {agent_id} is memory exhausted"
                })
                overloaded.append(agent_id)

            # Queue bottleneck
            if usage.queue_depth > 2000:
                bottlenecks.append({
                    'agent_id': agent_id,
                    'type': 'queue',
                    'severity': 'critical',
                    'value': usage.queue_depth,
                    'message': f"Agent {agent_id} has excessive queue depth"
                })
                overloaded.append(agent_id)

        # Calculate throughput and latency
        total_messages = sum(self.communication_matrix.values())
        total_pairs = len(self.communication_matrix)
        throughput = total_messages / max(1, total_pairs)

        # Estimate latency based on queue depths
        avg_queue = sum(u.queue_depth for u in self.resource_usage.values()) / max(1, len(self.resource_usage))
        avg_latency = avg_queue * 0.1  # Rough estimate
        p95_latency = avg_latency * 1.5
        p99_latency = avg_latency * 2.0

        analysis = BottleneckAnalysis(
            bottlenecks=bottlenecks,
            throughput=throughput,
            avg_latency=avg_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            overloaded_agents=overloaded,
            underutilized_agents=underutilized
        )

        self.bottleneck_cache = analysis
        return analysis

    def predict_cascade_failures(self) -> CascadeFailureReport:
        """
        Predict potential cascading failures.

        Returns:
            CascadeFailureReport: Cascade failure analysis
        """
        if self.cascade_cache:
            return self.cascade_cache

        at_risk = []
        triggers = []
        propagation_path = []

        # Find agents with critical issues
        for agent_id, usage in self.resource_usage.items():
            if usage.cpu_status == 'critical' or usage.memory_status == 'critical':
                at_risk.append(agent_id)

        # Find agents with low success rates
        for metric in self.health_metrics:
            if metric.status == 'critical' and 'success_rate' in metric.name:
                agent_id = metric.name.split('_')[0]
                if agent_id not in at_risk:
                    at_risk.append(agent_id)
                    triggers.append(f"Low success rate for {agent_id}")

        # Build propagation path based on communication graph
        if at_risk:
            # Find downstream agents that depend on at-risk agents
            for (sender, receiver), count in self.communication_matrix.items():
                if sender in at_risk and receiver not in at_risk and count > 10:
                    propagation_path.append(receiver)

        # Calculate failure probability
        failure_prob = min(1.0, len(at_risk) * 0.2)

        # Generate mitigation actions
        mitigations = []
        if at_risk:
            mitigations.append("Scale up critical agents")
            mitigations.append("Enable circuit breakers for overloaded agents")
            mitigations.append("Redirect traffic from failed agents")

        report = CascadeFailureReport(
            at_risk_agents=at_risk,
            failure_probability=failure_prob,
            propagation_path=propagation_path,
            triggers=triggers,
            mitigation_actions=mitigations
        )

        self.cascade_cache = report
        return report

    def _build_waiting_graph(self) -> Dict[str, List[str]]:
        """Build a graph of agents waiting on each other."""
        graph = defaultdict(list)

        for agent_id, usage in self.resource_usage.items():
            # If agent has high queue depth, it's waiting on something
            if usage.queue_depth > self.queue_threshold:
                # Find who it might be waiting on based on communication patterns
                for (sender, receiver), count in self.communication_matrix.items():
                    if receiver == agent_id and count > 0:
                        graph[agent_id].append(sender)

        return graph

    def _find_cycle(self, graph: Dict[str, List[str]]) -> List[str]:
        """Find cycles in a directed graph using DFS."""
        visited = set()
        rec_stack = set()
        cycle = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle.extend(path[cycle_start:])
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if dfs(node, []):
                    break

        return cycle

    def _check_communication_deadlock(self) -> List[str]:
        """Check for communication deadlocks."""
        # Look for communication patterns that suggest deadlock
        # e.g., A waiting for B, B waiting for A

        comm_graph = defaultdict(list)

        for (sender, receiver), count in self.communication_matrix.items():
            if count > 0:
                comm_graph[sender].append(receiver)

        # Check for 2-cycles (simplest deadlock pattern)
        for sender, receivers in comm_graph.items():
            for receiver in receivers:
                if sender in comm_graph.get(receiver, []):
                    return [sender, receiver]

        return []

    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive health report.

        Returns:
            Dictionary containing all health data and analysis
        """
        deadlock = self.detect_deadlocks()
        bottlenecks = self.analyze_bottlenecks()
        cascade = self.predict_cascade_failures()

        # Calculate overall health score
        critical_metrics = sum(1 for m in self.health_metrics if m.status == 'critical')
        warning_metrics = sum(1 for m in self.health_metrics if m.status == 'warning')
        total_metrics = len(self.health_metrics)

        if total_metrics > 0:
            health_score = 1.0 - (critical_metrics * 0.5 + warning_metrics * 0.2) / total_metrics
        else:
            health_score = 1.0

        overall_status = 'healthy'
        if deadlock.is_deadlocked or critical_metrics > 0:
            overall_status = 'critical'
        elif warning_metrics > 0 or cascade.failure_probability > 0.5:
            overall_status = 'warning'

        report = {
            'colony_id': self.colony_id,
            'generated_at': datetime.now().isoformat(),
            'overall_status': overall_status,
            'health_score': health_score,
            'summary': {
                'total_agents': len(self.resource_usage),
                'total_metrics': total_metrics,
                'critical_issues': critical_metrics,
                'warning_issues': warning_metrics,
                'deadlocked': deadlock.is_deadlocked,
                'bottlenecks': len(bottlenecks.bottlenecks),
                'cascade_risk': cascade.failure_probability
            },
            'health_metrics': [m.to_dict() for m in self.health_metrics],
            'resource_usage': {k: v.to_dict() for k, v in self.resource_usage.items()},
            'deadlock_detection': deadlock.to_dict(),
            'bottleneck_analysis': bottlenecks.to_dict(),
            'cascade_failure_prediction': cascade.to_dict(),
            'communication_summary': {
                'total_messages': sum(self.communication_matrix.values()),
                'active_pairs': len(self.communication_matrix),
                'top_pairs': [
                    {'from': k[0], 'to': k[1], 'count': v}
                    for k, v in sorted(self.communication_matrix.items(),
                                      key=lambda x: x[1], reverse=True)[:10]
                ]
            },
            'error_summary': {
                'total_errors': sum(len(errors) for errors in self.agent_errors.values()),
                'agents_with_errors': len(self.agent_errors),
                'recent_errors': [
                    error for errors in self.agent_errors.values()
                    for error in errors[-5:]
                ]
            },
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on diagnostics."""
        recommendations = []

        deadlock = self.deadlock_cache or self.detect_deadlocks()
        bottlenecks = self.bottleneck_cache or self.analyze_bottlenecks()
        cascade = self.cascade_cache or self.predict_cascade_failures()

        if deadlock.is_deadlocked:
            recommendations.append(
                f"URGENT: Break deadlock involving {len(deadlock.deadlock_cycle)} agents. "
                f"Consider restarting agents in reverse dependency order."
            )

        if bottlenecks.bottlenecks:
            recommendations.append(
                f"Address {len(bottlenecks.bottlenecks)} bottlenecks. "
                f"Scale up overloaded agents or redistribute load."
            )

        if cascade.failure_probability > 0.5:
            recommendations.append(
                f"HIGH RISK: Cascade failure probability is {cascade.failure_probability:.1%}. "
                f"Implement circuit breakers and redundancy for at-risk agents."
            )

        if bottlenecks.underutilized_agents:
            recommendations.append(
                f"Consider consolidating or shutting down {len(bottlenecks.underutilized_agents)} "
                f"underutilized agents to optimize resource usage."
            )

        return recommendations

    def save_health_report(self, filename: str = "colony_health.json") -> str:
        """
        Save health report to file.

        Args:
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        report = self.generate_health_report()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Health report saved to: {output_path}")
        return str(output_path)

    def print_health_summary(self) -> None:
        """Print a summary of colony health."""
        report = self.generate_health_report()

        print(f"\n{'=' * 80}")
        print(f"Colony Health Report: {self.colony_id}")
        print(f"{'=' * 80}")
        print(f"Overall Status: {report['overall_status'].upper()}")
        print(f"Health Score: {report['health_score']:.1%}")
        print(f"\nSummary:")
        print(f"  Total Agents: {report['summary']['total_agents']}")
        print(f"  Critical Issues: {report['summary']['critical_issues']}")
        print(f"  Warning Issues: {report['summary']['warning_issues']}")
        print(f"  Deadlocked: {report['summary']['deadlocked']}")
        print(f"  Bottlenecks: {report['summary']['bottlenecks']}")
        print(f"  Cascade Risk: {report['summary']['cascade_risk']:.1%}")

        if report['recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python colony_diagnostics.py <colony_id> [command]")
        print("\nCommands:")
        print("  check <agent_file>         - Run health checks on agents")
        print("  report                     - Generate health report")
        print("  summary                    - Print health summary")
        print("  deadlock                   - Detect deadlocks")
        print("  bottlenecks                - Analyze bottlenecks")
        sys.exit(1)

    colony_id = sys.argv[1]
    diagnostics = ColonyDiagnostics(colony_id)

    if len(sys.argv) < 3:
        print("No command specified")
        sys.exit(1)

    command = sys.argv[2]

    if command == "check" and len(sys.argv) >= 4:
        # Load and check agents from file
        agent_file = sys.argv[3]
        with open(agent_file, 'r') as f:
            agents = json.load(f)

        for agent_data in agents:
            agent_id = agent_data.get('id', 'unknown')
            diagnostics.check_agent_health(agent_id, agent_data)

            # Record resource usage if available
            if 'resources' in agent_data:
                diagnostics.record_resource_usage(agent_id, agent_data['resources'])

        print(f"Checked {len(agents)} agents")

    elif command == "report":
        diagnostics.save_health_report()

    elif command == "summary":
        diagnostics.print_health_summary()

    elif command == "deadlock":
        deadlock = diagnostics.detect_deadlocks()
        print(f"Deadlock detected: {deadlock.is_deadlocked}")
        if deadlock.is_deadlocked:
            print(f"Type: {deadlock.deadlock_type}")
            print(f"Cycle: {' -> '.join(deadlock.deadlock_cycle)}")
            print(f"Severity: {deadlock.severity}")

    elif command == "bottlenecks":
        bottlenecks = diagnostics.analyze_bottlenecks()
        print(f"Bottlenecks found: {len(bottlenecks.bottlenecks)}")
        for b in bottlenecks.bottlenecks:
            print(f"  - {b['agent_id']}: {b['type']} ({b['severity']})")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
