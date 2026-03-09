# POLLN Debugging Tools

Comprehensive debugging toolkit for troubleshooting POLLN (Pattern-Organized Large Language Network) systems.

## Overview

This toolkit provides powerful debugging and diagnostic capabilities for POLLN colonies, including:

- **A2A Package Tracing** - Trace and inspect package flow through colonies
- **Agent State Inspection** - Deep dive into agent state, value networks, and synapses
- **Colony Health Diagnostics** - Detect deadlocks, resource exhaustion, communication failures
- **Value Network Debugging** - Analyze TD(λ) convergence, oscillation, and divergence
- **Issue Detection** - Automated detection of common problems
- **Replay Debugger** - Record and replay execution for step-by-step debugging
- **Diagnostic Reports** - Comprehensive HTML and JSON reports

## Installation

```bash
cd simulations/tooling/debug
pip install -r requirements.txt
```

## Quick Start

### 1. Run All Diagnostics

```bash
python diagnostic_generator.py <colony_id> <colony_data.json>
```

This generates:
- `diagnostic_report.html` - Visual HTML report
- `diagnostic_report.json` - Complete diagnostic data
- Individual JSON reports for each diagnostic tool

### 2. Trace A2A Packages

```bash
python a2a_tracer.py <colony_id> trace <packages_file.json>
python a2a_tracer.py <colony_id> visualize [chain_id]
python a2a_tracer.py <colony_id> report
```

### 3. Inspect Agents

```bash
python agent_inspector.py <colony_id> inspect <agents_file.json>
python agent_inspector.py <colony_id> summary <agent_id>
python agent_inspector.py <colony_id> report
```

### 4. Check Colony Health

```bash
python colony_diagnostics.py <colony_id> check <agents_file.json>
python colony_diagnostics.py <colony_id> summary
python colony_diagnostics.py <colony_id> deadlock
```

### 5. Debug Value Networks

```bash
python value_network_debugger.py <colony_id> load <value_data.json>
python value_network_debugger.py <colony_id> summary <agent_id>
python value_network_debugger.py <colony_id> converge <agent_id>
```

### 6. Detect Issues

```bash
python issue_detector.py <colony_id> check <colony_data.json>
python issue_detector.py <colony_id> summary
python issue_detector.py <colony_id> patterns
```

### 7. Replay Execution

```bash
python replay_debugger.py <colony_id> record
# ... run colony ...
python replay_debugger.py <colony_id> stop
python replay_debugger.py <colony_id> save
python replay_debugger.py <colony_id> load <recording_file.json>
python replay_debugger.py <colony_id> replay
python replay_debugger.py <colony_id> step
python replay_debugger.py <colony_id> bp "agent_id == 'agent-1'"
python replay_debugger.py <colony_id> continue
```

## Tool Reference

### A2A Tracer (`a2a_tracer.py`)

Traces A2A package flow through colonies.

**Features:**
- Real-time package flow tracing
- Causal chain reconstruction
- Lost package detection
- Delay analysis
- Serialization issue detection

**Key Methods:**
```python
from a2a_tracer import A2ATracer

tracer = A2ATracer(colony_id="my_colony")
tracer.trace_package(package_data, current_agent="agent-1", status="in_transit")
lost = tracer.find_lost_packages(timeout_seconds=60)
delays = tracer.analyze_delays()
tracer.save_trace_report()
```

### Agent Inspector (`agent_inspector.py`)

Inspects agent state, value networks, and synapses.

**Features:**
- Live agent state inspection
- Historical state replay
- Value network analysis
- Synapse health checks
- META tile tracking

**Key Methods:**
```python
from agent_inspector import AgentInspector

inspector = AgentInspector(colony_id="my_colony")
inspector.inspect_agent(agent_data)
inspector.inspect_value_network(agent_id, value_data)
inspector.inspect_synapse(source_id, target_id, synapse_data)
hung = inspector.detect_hung_agents()
issues = inspector.detect_value_convergence_issues()
```

### Colony Diagnostics (`colony_diagnostics.py`)

Performs comprehensive colony health checks.

**Features:**
- Deadlock detection (resource, communication, causal)
- Resource exhaustion detection
- Communication failure analysis
- Bottleneck identification
- Cascading failure prediction

**Key Methods:**
```python
from colony_diagnostics import ColonyDiagnostics

diagnostics = ColonyDiagnostics(colony_id="my_colony")
diagnostics.check_agent_health(agent_id, agent_data)
diagnostics.record_resource_usage(agent_id, resource_data)
deadlock = diagnostics.detect_deadlocks()
bottlenecks = diagnostics.analyze_bottlenecks()
cascade = diagnostics.predict_cascade_failures()
```

### Value Network Debugger (`value_network_debugger.py`)

Debugs TD(λ) value networks.

**Features:**
- Track value updates over time
- Analyze eligibility traces
- Detect convergence issues
- Identify oscillation patterns
- Detect divergence

**Key Methods:**
```python
from value_network_debugger import ValueNetworkDebugger

debugger = ValueNetworkDebugger(colony_id="my_colony")
debugger.record_update(agent_id, old_value, new_value, reward, td_error, ...)
debugger.record_eligibility_traces(agent_id, traces)
analysis = debugger.analyze_convergence(agent_id)
distribution = debugger.compute_value_distribution(agent_id)
```

### Issue Detector (`issue_detector.py`)

Automatically detects common issues.

**Features:**
- Memory leak detection
- Stuck agent detection
- Value function anomaly detection
- Communication failure detection
- Pattern recognition
- Trend analysis

**Key Methods:**
```python
from issue_detector import IssueDetector

detector = IssueDetector(colony_id="my_colony")
detector.run_all_checks(colony_data)
patterns = detector.detect_patterns()
trend = detector.analyze_trends(metric_name, current_value)
detector.save_issue_report()
```

### Replay Debugger (`replay_debugger.py`)

Records and replays colony execution.

**Features:**
- Record colony execution
- Replay step-by-step
- Forward/backward stepping
- Breakpoints with conditions
- State inspection at any point
- Variable evaluation

**Key Methods:**
```python
from replay_debugger import ReplayDebugger

debugger = ReplayDebugger(colony_id="my_colony")
debugger.start_recording()
debugger.record_event(event_type, agent_id, data, state_snapshot)
debugger.stop_recording()
debugger.save_recording()

# Replay
debugger.load_recording(filename)
debugger.start_replay()
debugger.step_forward()
debugger.jump_to(position)
debugger.set_breakpoint("agent_id == 'agent-1'")
debugger.continue_execution()
```

### Diagnostic Generator (`diagnostic_generator.py`)

Runs all diagnostics and generates comprehensive reports.

**Features:**
- Run all diagnostic tools
- Aggregate results
- Generate HTML report
- Provide recommendations

**Key Methods:**
```python
from diagnostic_generator import DiagnosticGenerator

generator = DiagnosticGenerator(colony_id="my_colony")
generator.load_colony_data(colony_data_file)
report = generator.generate_comprehensive_report()
generator.save_comprehensive_report()
generator.generate_html_report()
```

## Output Format

Diagnostic reports are generated in `reports/diagnostics/`:

```
reports/diagnostics/
├── a2a_trace.json             # A2A package traces
├── agent_states.json          # Agent state snapshots
├── colony_health.json         # Colony health report
├── value_network_debug.json   # Value network analysis
├── issues_detected.json       # Detected issues
├── diagnostic_report.json     # Comprehensive report
├── diagnostic_report.html     # Visual HTML report
└── replay_data.json           # Execution replay data
```

## Testing

Run the test suite:

```bash
python test_debug.py
```

## Data Format

### Colony Data Format

```json
{
  "agents": [
    {
      "id": "agent-1",
      "typeId": "TaskAgent",
      "status": "active",
      "lastActive": 1699123456.789,
      "valueFunction": 0.75,
      "successCount": 80,
      "failureCount": 20,
      "avgLatencyMs": 150,
      "stateSnapshot": {},
      "resources": {
        "cpuPercent": 45.0,
        "memoryMb": 350.0,
        "networkIoMb": 25.0,
        "activeConnections": 5,
        "queueDepth": 120
      },
      "valueNetwork": {
        "currentValue": 0.75,
        "valueHistory": [0.5, 0.6, 0.7, 0.75],
        "eligibilityTraces": {"action-1": 0.9},
        "learningRate": 0.1,
        "discountFactor": 0.99
      }
    }
  ],
  "a2a_packages": [
    {
      "id": "pkg-1",
      "timestamp": 1699123456.789,
      "senderId": "agent-1",
      "receiverId": "agent-2",
      "type": "request",
      "layer": "DELIBERATE",
      "privacyLevel": "PRIVATE",
      "parentIds": [],
      "causalChainId": "chain-1",
      "payload": {"data": "value"}
    }
  ],
  "communicationMatrix": {
    "agent-1_agent-2": 150,
    "agent-2_agent-1": 145
  }
}
```

## Common Debugging Workflows

### Workflow 1: Agent Not Responding

```bash
# 1. Check if agent is stuck
python agent_inspector.py my_colony inspect agents.json
python agent_inspector.py my_colony summary problem-agent

# 2. Check for deadlocks
python colony_diagnostics.py my_colony check agents.json
python colony_diagnostics.py my_colony deadlock

# 3. Check value network
python value_network_debugger.py my_colony load value_data.json
python value_network_debugger.py my_colony summary problem-agent
```

### Workflow 2: Memory Issues

```bash
# 1. Detect memory leaks
python issue_detector.py my_colony check colony_data.json

# 2. Check resource usage
python colony_diagnostics.py my_colony check agents.json

# 3. Generate full report
python diagnostic_generator.py my_colony colony_data.json
```

### Workflow 3: Performance Degradation

```bash
# 1. Check for bottlenecks
python colony_diagnostics.py my_colony check agents.json
python colony_diagnostics.py my_colony bottlenecks

# 2. Analyze value convergence
python value_network_debugger.py my_colony load value_data.json
python value_network_debugger.py my_colony converge agent-1

# 3. Check trends
python issue_detector.py my_colony patterns
```

### Workflow 4: Step-by-Step Debugging

```bash
# 1. Record execution
python replay_debugger.py my_colony record

# 2. Run colony (in another terminal)

# 3. Stop and save
python replay_debugger.py my_colony stop
python replay_debugger.py my_colony save

# 4. Replay and debug
python replay_debugger.py my_colony load replay_data.json
python replay_debugger.py my_colony replay
python replay_debugger.py my_colony bp "agent_id == 'problem-agent'"
python replay_debugger.py my_colony continue
```

## Contributing

When adding new debugging capabilities:

1. Create tool in `simulations/tooling/debug/`
2. Add tests to `test_debug.py`
3. Update documentation
4. Follow existing patterns

## License

MIT License - See LICENSE file for details.
