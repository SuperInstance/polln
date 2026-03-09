#!/usr/bin/env python3
"""
Issue Detector - Automated issue detection for POLLN colonies.

This tool detects common issues like memory leaks, stuck agents, wrong values,
and alerts to potential problems before they become critical.
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from collections import defaultdict
import time


@dataclass
class DetectedIssue:
    """A detected issue in the colony."""
    issue_id: str
    severity: str  # 'info', 'warning', 'critical'
    category: str
    agent_id: Optional[str]
    title: str
    description: str
    evidence: Dict[str, Any]
    timestamp: float
    suggested_fixes: List[str]
    related_issues: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IssuePattern:
    """A pattern of issues that suggest a systemic problem."""
    pattern_id: str
    pattern_name: str
    description: str
    matched_issues: List[str]
    confidence: float
    root_cause_hypothesis: str
    recommended_actions: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class HealthTrend:
    """Trend analysis of colony health."""
    metric_name: str
    current_value: float
    previous_value: float
    trend: str  # 'improving', 'declining', 'stable'
    rate_of_change: float
    predicted_value: float
    concern_level: str

    def to_dict(self) -> Dict:
        return asdict(self)


class IssueDetector:
    """
    Automated issue detection for POLLN colonies.

    Features:
    - Memory leak detection
    - Stuck agent detection
    - Value function anomaly detection
    - Communication failure detection
    - Resource exhaustion detection
    - Pattern recognition for systemic issues
    - Trend analysis
    - Predictive alerting
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Issue tracking
        self.detected_issues: Dict[str, DetectedIssue] = {}
        self.issue_patterns: Dict[str, IssuePattern] = {}
        self.health_trends: Dict[str, List[HealthTrend]] = defaultdict(list)

        # Historical data for trend analysis
        self.historical_metrics: Dict[str, List[float]] = defaultdict(list)

        # Detection configuration
        self.thresholds = {
            'memory_mb_warning': 500,
            'memory_mb_critical': 900,
            'cpu_percent_warning': 70,
            'cpu_percent_critical': 90,
            'queue_depth_warning': 500,
            'queue_depth_critical': 2000,
            'idle_time_warning': 300,
            'idle_time_critical': 600,
            'value_function_min': 0.1,
            'value_function_max': 0.9,
            'success_rate_min': 0.5
        }

        # Issue counters
        self.issue_counters = defaultdict(int)

    def check_memory_leaks(self, agent_data: Dict[str, Any]) -> Optional[DetectedIssue]:
        """
        Check for memory leaks in an agent.

        Args:
            agent_data: Dictionary containing agent state

        Returns:
            DetectedIssue if memory leak detected, None otherwise
        """
        agent_id = agent_data.get('id', 'unknown')
        memory_mb = agent_data.get('memoryMb', 0)

        # Check against thresholds
        if memory_mb > self.thresholds['memory_mb_critical']:
            return DetectedIssue(
                issue_id=f"memory_leak_{agent_id}_{int(time.time())}",
                severity='critical',
                category='memory',
                agent_id=agent_id,
                title=f"Critical memory leak detected in {agent_id}",
                description=f"Agent {agent_id} is using {memory_mb}MB of memory",
                evidence={
                    'memory_mb': memory_mb,
                    'threshold': self.thresholds['memory_mb_critical']
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "Restart the agent to free memory",
                    "Check for unbounded data structures",
                    "Review memory allocation patterns",
                    "Consider implementing memory limits"
                ],
                related_issues=[]
            )
        elif memory_mb > self.thresholds['memory_mb_warning']:
            return DetectedIssue(
                issue_id=f"memory_warning_{agent_id}_{int(time.time())}",
                severity='warning',
                category='memory',
                agent_id=agent_id,
                title=f"Memory usage warning for {agent_id}",
                description=f"Agent {agent_id} is using {memory_mb}MB of memory",
                evidence={
                    'memory_mb': memory_mb,
                    'threshold': self.thresholds['memory_mb_warning']
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "Monitor memory usage trend",
                    "Review recent memory allocations",
                    "Consider memory optimization"
                ],
                related_issues=[]
            )

        return None

    def check_stuck_agents(self, agent_data: Dict[str, Any]) -> Optional[DetectedIssue]:
        """
        Check for stuck or hung agents.

        Args:
            agent_data: Dictionary containing agent state

        Returns:
            DetectedIssue if agent is stuck, None otherwise
        """
        agent_id = agent_data.get('id', 'unknown')
        last_active = agent_data.get('lastActive', 0)
        idle_time = time.time() - last_active

        # Check against thresholds
        if idle_time > self.thresholds['idle_time_critical']:
            status = agent_data.get('status', 'unknown')
            if status in ['active', 'hibernating']:
                return DetectedIssue(
                    issue_id=f"stuck_agent_{agent_id}_{int(time.time())}",
                    severity='critical',
                    category='agent_hang',
                    agent_id=agent_id,
                    title=f"Agent {agent_id} appears to be stuck",
                    description=f"Agent {agent_id} has been idle for {idle_time:.0f} seconds but status is '{status}'",
                    evidence={
                        'idle_time': idle_time,
                        'last_active': last_active,
                        'status': status
                    },
                    timestamp=time.time(),
                    suggested_fixes=[
                        "Check agent logs for errors",
                        "Verify agent is not in deadlock",
                        "Consider restarting the agent",
                        "Check if agent has work to do"
                    ],
                    related_issues=[]
                )

        return None

    def check_value_anomalies(self, agent_data: Dict[str, Any]) -> Optional[DetectedIssue]:
        """
        Check for value function anomalies.

        Args:
            agent_data: Dictionary containing agent state

        Returns:
            DetectedIssue if anomaly detected, None otherwise
        """
        agent_id = agent_data.get('id', 'unknown')
        value_function = agent_data.get('valueFunction', 0.5)

        # Check for out-of-range values
        if value_function < self.thresholds['value_function_min']:
            return DetectedIssue(
                issue_id=f"value_low_{agent_id}_{int(time.time())}",
                severity='warning',
                category='value_function',
                agent_id=agent_id,
                title=f"Very low value function for {agent_id}",
                description=f"Agent {agent_id} has value function {value_function:.3f}",
                evidence={
                    'value_function': value_function,
                    'threshold': self.thresholds['value_function_min']
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "Review agent performance",
                    "Check reward function",
                    "Consider retraining agent",
                    "Verify agent is being used correctly"
                ],
                related_issues=[]
            )

        if value_function > self.thresholds['value_function_max']:
            return DetectedIssue(
                issue_id=f"value_high_{agent_id}_{int(time.time())}",
                severity='info',
                category='value_function',
                agent_id=agent_id,
                title=f"Unusually high value function for {agent_id}",
                description=f"Agent {agent_id} has value function {value_function:.3f}",
                evidence={
                    'value_function': value_function,
                    'threshold': self.thresholds['value_function_max']
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "Verify value function is correct",
                    "Check for reward hacking",
                    "Review learning rate"
                ],
                related_issues=[]
            )

        # Check for NaN or infinity
        if not isinstance(value_function, (int, float)) or value_function != value_function:
            return DetectedIssue(
                issue_id=f"value_corrupt_{agent_id}_{int(time.time())}",
                severity='critical',
                category='value_function',
                agent_id=agent_id,
                title=f"Corrupted value function in {agent_id}",
                description=f"Agent {agent_id} has corrupted value function: {value_function}",
                evidence={
                    'value_function': str(value_function),
                    'type': str(type(value_function))
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "CRITICAL: Restart agent immediately",
                    "Review value update logic",
                    "Add bounds checking to value function"
                ],
                related_issues=[]
            )

        return None

    def check_communication_failures(self, comm_matrix: Dict[str, int],
                                    sender_id: str, receiver_id: str) -> Optional[DetectedIssue]:
        """
        Check for communication failures between agents.

        Args:
            comm_matrix: Communication matrix
            sender_id: Sender agent ID
            receiver_id: Receiver agent ID

        Returns:
            DetectedIssue if communication failure detected, None otherwise
        """
        # Check for one-way communication (should be bidirectional)
        key1 = f"{sender_id}_{receiver_id}"
        key2 = f"{receiver_id}_{sender_id}"

        forward_count = comm_matrix.get(key1, 0) if isinstance(comm_matrix, dict) else 0
        backward_count = comm_matrix.get(key2, 0) if isinstance(comm_matrix, dict) else 0

        # If one direction has much more traffic than the other
        if forward_count > 10 and backward_count == 0:
            return DetectedIssue(
                issue_id=f"comm_failure_{key1}_{int(time.time())}",
                severity='warning',
                category='communication',
                agent_id=sender_id,
                title=f"Asymmetric communication detected",
                description=f"Agent {sender_id} sends to {receiver_id} but receives no responses",
                evidence={
                    'forward_count': forward_count,
                    'backward_count': backward_count
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "Check if receiver agent is processing messages",
                    "Verify receiver agent is not crashed",
                    "Check for message filtering issues"
                ],
                related_issues=[]
            )

        return None

    def check_resource_exhaustion(self, resource_data: Dict[str, Any]) -> Optional[DetectedIssue]:
        """
        Check for resource exhaustion.

        Args:
            resource_data: Dictionary containing resource metrics

        Returns:
            DetectedIssue if resource exhaustion detected, None otherwise
        """
        agent_id = resource_data.get('agentId', 'unknown')
        issues = []

        # CPU exhaustion
        cpu = resource_data.get('cpuPercent', 0)
        if cpu > self.thresholds['cpu_percent_critical']:
            issues.append({
                'resource': 'cpu',
                'value': cpu,
                'threshold': self.thresholds['cpu_percent_critical']
            })

        # Queue depth
        queue_depth = resource_data.get('queueDepth', 0)
        if queue_depth > self.thresholds['queue_depth_critical']:
            issues.append({
                'resource': 'queue',
                'value': queue_depth,
                'threshold': self.thresholds['queue_depth_critical']
            })

        if issues:
            return DetectedIssue(
                issue_id=f"resource_exhaustion_{agent_id}_{int(time.time())}",
                severity='critical',
                category='resources',
                agent_id=agent_id,
                title=f"Resource exhaustion in {agent_id}",
                description=f"Agent {agent_id} is exhausting resources",
                evidence={
                    'issues': issues
                },
                timestamp=time.time(),
                suggested_fixes=[
                    "Scale up agent resources",
                    "Redistribute load to other agents",
                    "Implement throttling",
                    "Clear backed-up queues"
                ],
                related_issues=[]
            )

        return None

    def detect_patterns(self) -> List[IssuePattern]:
        """
        Detect patterns of issues that suggest systemic problems.

        Returns:
            List of detected patterns
        """
        patterns = []

        # Group issues by category
        issues_by_category: Dict[str, List[DetectedIssue]] = defaultdict(list)
        for issue in self.detected_issues.values():
            issues_by_category[issue.category].append(issue)

        # Pattern: Multiple agents with memory leaks
        memory_issues = issues_by_category.get('memory', [])
        if len(memory_issues) >= 3:
            patterns.append(IssuePattern(
                pattern_id=f"systematic_memory_leak_{int(time.time())}",
                pattern_name="Systematic Memory Leak",
                description=f"{len(memory_issues)} agents showing memory leak patterns",
                matched_issues=[i.issue_id for i in memory_issues],
                confidence=0.8,
                root_cause_hypothesis="Common dependency or shared resource causing memory leaks",
                recommended_actions=[
                    "Review common dependencies across affected agents",
                    "Check for shared data structures",
                    "Implement memory monitoring at colony level"
                ]
            ))

        # Pattern: Multiple stuck agents
        stuck_issues = issues_by_category.get('agent_hang', [])
        if len(stuck_issues) >= 2:
            patterns.append(IssuePattern(
                pattern_id=f"systematic_agent_hang_{int(time.time())}",
                pattern_name="Systematic Agent Hang",
                description=f"{len(stuck_issues)} agents appear stuck",
                matched_issues=[i.issue_id for i in stuck_issues],
                confidence=0.7,
                root_cause_hypothesis="Possible deadlock or shared resource contention",
                recommended_actions=[
                    "Check for deadlock in communication graph",
                    "Review shared resource locks",
                    "Implement timeout mechanisms"
                ]
            ))

        # Pattern: Cascading value function decline
        value_issues = [i for i in issues_by_category.get('value_function', [])
                       if 'low' in i.title.lower()]
        if len(value_issues) >= 3:
            patterns.append(IssuePattern(
                pattern_id=f"cascading_value_decline_{int(time.time())}",
                pattern_name="Cascading Value Decline",
                description=f"{len(value_issues)} agents with declining value functions",
                matched_issues=[i.issue_id for i in value_issues],
                confidence=0.6,
                root_cause_hypothesis="Systemic issue affecting agent performance",
                recommended_actions=[
                    "Review reward function across colony",
                    "Check for environmental changes",
                    "Consider resetting value networks"
                ]
            ))

        return patterns

    def analyze_trends(self, metric_name: str, current_value: float) -> HealthTrend:
        """
        Analyze trends in colony health metrics.

        Args:
            metric_name: Name of the metric
            current_value: Current value of the metric

        Returns:
            HealthTrend: Trend analysis
        """
        # Store historical data
        self.historical_metrics[metric_name].append(current_value)

        # Keep only last 100 data points
        if len(self.historical_metrics[metric_name]) > 100:
            self.historical_metrics[metric_name].pop(0)

        history = self.historical_metrics[metric_name]

        if len(history) < 3:
            return HealthTrend(
                metric_name=metric_name,
                current_value=current_value,
                previous_value=current_value,
                trend='stable',
                rate_of_change=0.0,
                predicted_value=current_value,
                concern_level='info'
            )

        # Calculate trend
        previous_value = history[-2]
        rate_of_change = (current_value - previous_value) / max(1, abs(previous_value))

        # Determine trend direction
        if abs(rate_of_change) < 0.05:
            trend = 'stable'
        elif rate_of_change > 0:
            trend = 'improving' if metric_name in ['success_rate', 'value_function'] else 'declining'
        else:
            trend = 'declining' if metric_name in ['success_rate', 'value_function'] else 'improving'

        # Simple linear prediction
        if len(history) >= 5:
            changes = [history[i] - history[i-1] for i in range(1, len(history))]
            avg_change = sum(changes) / len(changes)
            predicted_value = current_value + avg_change
        else:
            predicted_value = current_value

        # Determine concern level
        concern_level = 'info'
        if trend == 'declining' and abs(rate_of_change) > 0.1:
            concern_level = 'warning'
        if trend == 'declining' and abs(rate_of_change) > 0.2:
            concern_level = 'critical'

        health_trend = HealthTrend(
            metric_name=metric_name,
            current_value=current_value,
            previous_value=previous_value,
            trend=trend,
            rate_of_change=rate_of_change,
            predicted_value=predicted_value,
            concern_level=concern_level
        )

        self.health_trends[metric_name].append(health_trend)

        return health_trend

    def run_all_checks(self, colony_data: Dict[str, Any]) -> List[DetectedIssue]:
        """
        Run all issue detection checks.

        Args:
            colony_data: Dictionary containing colony state

        Returns:
            List of detected issues
        """
        issues = []

        # Check each agent
        for agent_data in colony_data.get('agents', []):
            # Memory leak check
            memory_issue = self.check_memory_leaks(agent_data)
            if memory_issue:
                issues.append(memory_issue)

            # Stuck agent check
            stuck_issue = self.check_stuck_agents(agent_data)
            if stuck_issue:
                issues.append(stuck_issue)

            # Value anomaly check
            value_issue = self.check_value_anomalies(agent_data)
            if value_issue:
                issues.append(value_issue)

            # Resource exhaustion check
            if 'resources' in agent_data:
                resource_issue = self.check_resource_exhaustion(agent_data['resources'])
                if resource_issue:
                    issues.append(resource_issue)

            # Analyze trends
            if 'valueFunction' in agent_data:
                self.analyze_trends(f"value_function_{agent_data['id']}",
                                   agent_data['valueFunction'])

        # Check communication patterns
        comm_matrix = colony_data.get('communicationMatrix', {})
        for key, count in comm_matrix.items():
            # Parse key which might be "agent-1_agent-2" format
            parts = key.split('_')
            if len(parts) >= 2:
                sender = parts[0]
                receiver = parts[1]
                if count > 0:
                    comm_issue = self.check_communication_failures(comm_matrix, sender, receiver)
                    if comm_issue:
                        issues.append(comm_issue)

        # Store all issues
        for issue in issues:
            self.detected_issues[issue.issue_id] = issue

        # Detect patterns
        patterns = self.detect_patterns()
        for pattern in patterns:
            self.issue_patterns[pattern.pattern_id] = pattern

        return issues

    def generate_issue_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive issue report.

        Returns:
            Dictionary containing all issue data and analysis
        """
        # Detect patterns
        patterns = self.detect_patterns()

        # Categorize issues by severity
        critical_issues = [i for i in self.detected_issues.values() if i.severity == 'critical']
        warning_issues = [i for i in self.detected_issues.values() if i.severity == 'warning']
        info_issues = [i for i in self.detected_issues.values() if i.severity == 'info']

        # Count by category
        issues_by_category = defaultdict(int)
        for issue in self.detected_issues.values():
            issues_by_category[issue.category] += 1

        report = {
            'colony_id': self.colony_id,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(self.detected_issues),
                'critical_issues': len(critical_issues),
                'warning_issues': len(warning_issues),
                'info_issues': len(info_issues),
                'patterns_detected': len(patterns)
            },
            'issues_by_category': dict(issues_by_category),
            'detected_issues': {k: v.to_dict() for k, v in self.detected_issues.items()},
            'patterns': {k: v.to_dict() for k, v in self.issue_patterns.items()},
            'health_trends': {
                metric: [t.to_dict() for t in trends[-10:]]
                for metric, trends in self.health_trends.items()
            },
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        critical_count = sum(1 for i in self.detected_issues.values() if i.severity == 'critical')

        if critical_count > 0:
            recommendations.append(
                f"URGENT: Address {critical_count} critical issues immediately"
            )

        # Check for patterns
        if self.issue_patterns:
            recommendations.append(
                f"Address {len(self.issue_patterns)} systemic patterns affecting colony health"
            )

        # Check trends
        declining_metrics = [
            metric for metric, trends in self.health_trends.items()
            if trends and trends[-1].trend == 'declining'
        ]
        if declining_metrics:
            recommendations.append(
                f"Monitor {len(declining_metrics)} metrics showing declining trends"
            )

        return recommendations

    def save_issue_report(self, filename: str = "issues_detected.json") -> str:
        """
        Save issue report to file.

        Args:
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        report = self.generate_issue_report()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Issue report saved to: {output_path}")
        return str(output_path)

    def print_issue_summary(self) -> None:
        """Print a summary of detected issues."""
        critical = [i for i in self.detected_issues.values() if i.severity == 'critical']
        warnings = [i for i in self.detected_issues.values() if i.severity == 'warning']

        print(f"\n{'=' * 80}")
        print(f"Issue Detection Summary: {self.colony_id}")
        print(f"{'=' * 80}")
        print(f"Total Issues: {len(self.detected_issues)}")
        print(f"  Critical: {len(critical)}")
        print(f"  Warnings: {len(warnings)}")

        if self.issue_patterns:
            print(f"\nPatterns Detected: {len(self.issue_patterns)}")
            for pattern in self.issue_patterns.values():
                print(f"  - {pattern.pattern_name}: {pattern.description}")

        if critical:
            print(f"\nCritical Issues:")
            for issue in critical[:5]:  # Show first 5
                print(f"  - {issue.title}")
                if issue.suggested_fixes:
                    print(f"    Fix: {issue.suggested_fixes[0]}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python issue_detector.py <colony_id> [command]")
        print("\nCommands:")
        print("  check <colony_file>        - Run all issue detection checks")
        print("  report                     - Generate issue report")
        print("  summary                    - Print issue summary")
        print("  patterns                   - Detect issue patterns")
        sys.exit(1)

    colony_id = sys.argv[1]
    detector = IssueDetector(colony_id)

    if len(sys.argv) < 3:
        print("No command specified")
        sys.exit(1)

    command = sys.argv[2]

    if command == "check" and len(sys.argv) >= 4:
        # Load and check colony data
        colony_file = sys.argv[3]
        with open(colony_file, 'r') as f:
            colony_data = json.load(f)

        issues = detector.run_all_checks(colony_data)
        print(f"Detected {len(issues)} issues")

    elif command == "report":
        detector.save_issue_report()

    elif command == "summary":
        detector.print_issue_summary()

    elif command == "patterns":
        patterns = detector.detect_patterns()
        print(f"Detected {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"  - {pattern.pattern_name}")
            print(f"    {pattern.description}")
            print(f"    Confidence: {pattern.confidence:.1%}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
