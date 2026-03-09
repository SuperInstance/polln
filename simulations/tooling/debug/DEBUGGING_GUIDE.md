# POLLN Debugging Guide

Comprehensive guide to debugging POLLN systems using the debugging toolkit.

## Table of Contents

1. [Debugging Philosophy](#debugging-philosophy)
2. [Common Issues and Solutions](#common-issues-and-solutions)
3. [Diagnostic Workflows](#diagnostic-workflows)
4. [Tool-Specific Guides](#tool-specific-guides)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Debugging Philosophy

### Emergent Behavior

POLLN colonies exhibit emergent behavior - intelligence emerges from the interactions between agents, not from any single agent. This means:

- **Debug the system, not just components**
- **Look for patterns, not isolated events**
- **Consider network effects**
- **Trace causal chains**

### Subsumption Architecture

The layered architecture (SAFETY → REFLEX → HABITUAL → DELIBERATE) means:

- **Lower layers always win**
- **Check safety constraints first**
- **Layer conflicts cause unexpected behavior**
- **Debug from bottom up**

### Memory as Structure

POLLN doesn't store facts - it stores stronger connections:

- **Debug connection weights, not data**
- **Look for synaptic patterns**
- **Track Hebbian learning**
- **Monitor value function evolution**

## Common Issues and Solutions

### Issue: Agent Not Responding

**Symptoms:**
- Agent appears stuck
- No A2A packages sent/received
- High queue depth

**Diagnosis:**
```bash
# Check agent status
python agent_inspector.py <colony_id> inspect agents.json
python agent_inspector.py <colony_id> summary <agent_id>

# Check for deadlocks
python colony_diagnostics.py <colony_id> deadlock

# Check if agent is waiting
python replay_debugger.py <colony_id> load recording.json
python replay_debugger.py <colony_id> jump_to <position>
python replay_debugger.py <colony_id> eval "agents['<agent_id>']"
```

**Solutions:**
1. **Deadlock**: Break waiting cycle
2. **Resource exhaustion**: Scale up resources
3. **Stuck processing**: Restart agent
4. **No work**: Check input topics

### Issue: Poor Performance

**Symptoms:**
- Low success rate
- High latency
- Declining value function

**Diagnosis:**
```bash
# Check performance metrics
python agent_inspector.py <colony_id> inspect agents.json
python colony_diagnostics.py <colony_id> check agents.json

# Analyze value network
python value_network_debugger.py <colony_id> load value_data.json
python value_network_debugger.py <colony_id> converge <agent_id>

# Check for bottlenecks
python colony_diagnostics.py <colony_id> bottlenecks
```

**Solutions:**
1. **Low value function**: Retrain agent
2. **Oscillation**: Reduce learning rate
3. **Divergence**: Check reward function
4. **Bottleneck**: Scale up or redistribute

### Issue: Memory Leaks

**Symptoms:**
- Memory usage growing
- Agents being killed
- System slowdown

**Diagnosis:**
```bash
# Detect memory leaks
python issue_detector.py <colony_id> check colony_data.json

# Check resource usage
python colony_diagnostics.py <colony_id> check agents.json

# Monitor over time
python issue_detector.py <colony_id> check colony_data.json
# Wait 5 minutes
python issue_detector.py <colony_id> check colony_data.json
```

**Solutions:**
1. **Unbounded growth**: Add limits to data structures
2. **Cache not clearing**: Implement LRU eviction
3. **Reference cycles**: Break circular references
4. **Large payloads**: Implement streaming

### Issue: Communication Failures

**Symptoms:**
- Packages not delivered
- Asymmetric communication
- High network errors

**Diagnosis:**
```bash
# Trace A2A packages
python a2a_tracer.py <colony_id> trace packages.json
python a2a_tracer.py <colony_id> visualize

# Check communication patterns
python colony_diagnostics.py <colony_id> check agents.json

# Look for one-way communication
python issue_detector.py <colony_id> check colony_data.json
```

**Solutions:**
1. **Receiver not processing**: Check receiver status
2. **Network issues**: Verify connectivity
3. **Serialization errors**: Check payload format
4. **Queue full**: Increase queue size

### Issue: Value Network Problems

**Symptoms:**
- Oscillating values
- Diverging values
- Slow convergence

**Diagnosis:**
```bash
# Analyze value network
python value_network_debugger.py <colony_id> load value_data.json
python value_network_debugger.py <colony_id> converge <agent_id>
python value_network_debugger.py <colony_id> summary <agent_id>

# Check for patterns
python value_network_debugger.py <colony_id> report
```

**Solutions:**
1. **Oscillation**: Reduce learning rate
2. **Divergence**: Check reward scale
3. **Slow convergence**: Increase learning rate
4. **Local optima**: Add exploration

## Diagnostic Workflows

### Workflow 1: Initial Diagnosis

When something goes wrong:

```bash
# 1. Run comprehensive diagnostics
python diagnostic_generator.py <colony_id> colony_data.json

# 2. Review HTML report
open reports/diagnostics/diagnostic_report.html

# 3. Check critical issues first
python issue_detector.py <colony_id> summary

# 4. Dive into specific tools based on findings
```

### Workflow 2: Performance Debugging

For performance issues:

```bash
# 1. Check colony health
python colony_diagnostics.py <colony_id> check agents.json
python colony_diagnostics.py <colony_id> bottlenecks

# 2. Analyze value networks
python value_network_debugger.py <colony_id> load value_data.json
for agent in agent_ids:
    python value_network_debugger.py <colony_id> converge $agent

# 3. Check communication patterns
python a2a_tracer.py <colony_id> trace packages.json
python a2a_tracer.py <colony_id> visualize

# 4. Identify trends
python issue_detector.py <colony_id> patterns
```

### Workflow 3: Step-by-Step Debugging

For complex issues:

```bash
# 1. Record execution
python replay_debugger.py <colony_id> record

# 2. Run colony until issue occurs

# 3. Stop recording
python replay_debugger.py <colony_id> stop
python replay_debugger.py <colony_id> save

# 4. Replay with breakpoints
python replay_debugger.py <colony_id> load recording.json
python replay_debugger.py <colony_id> replay
python replay_debugger.py <colony_id> bp "agent_id == 'problem-agent'"
python replay_debugger.py <colony_id> continue

# 5. Inspect state at breakpoint
python replay_debugger.py <colony_id> inspect problem-agent
python replay_debugger.py <colony_id> eval "agents['problem-agent']['valueFunction']"
```

### Workflow 4: Preventive Monitoring

For ongoing health:

```bash
# 1. Set up periodic checks
while true; do
    python colony_diagnostics.py <colony_id> check agents.json
    python issue_detector.py <colony_id> check colony_data.json
    sleep 300  # Every 5 minutes
done

# 2. Generate daily reports
python diagnostic_generator.py <colony_id> colony_data.json
mv reports/diagnostics/diagnostic_report.html \
   reports/diagnostics/reports/diagnostic_report_$(date +%Y%m%d).html
```

## Tool-Specific Guides

### A2A Tracer

**Use when:**
- Packages are getting lost
- Communication is slow
- Need to trace causal chains

**Key features:**
- Package flow visualization
- Causal chain analysis
- Delay statistics
- Serialization checks

**Pro tips:**
- Filter by causal chain to focus on specific workflows
- Look for packages stuck in 'in_transit' status
- Check parent_ids to understand package lineage
- Use visualize to see the big picture

### Agent Inspector

**Use when:**
- Agent behavior is wrong
- Need to understand agent state
- Checking agent health

**Key features:**
- State snapshot inspection
- Value network analysis
- Synapse health checks
- META tile tracking

**Pro tips:**
- Check value_function trend over time
- Look for agents with low success rates
- Monitor synapse weights for learning
- Track META tile differentiation

### Colony Diagnostics

**Use when:**
- Colony performance is poor
- Suspect deadlocks
- Resource issues

**Key features:**
- Deadlock detection
- Resource monitoring
- Bottleneck analysis
- Cascade prediction

**Pro tips:**
- Check health_score for overall colony health
- Look for overloaded agents
- Monitor queue depths
- Check cascade risk before scaling

### Value Network Debugger

**Use when:**
- Agent performance declining
- Value function acting strange
- Learning issues

**Key features:**
- Convergence analysis
- Oscillation detection
- Divergence detection
- Trend analysis

**Pro tips:**
- Monitor stability_score for convergence
- Check for oscillation with high frequency
- Look for divergence (values going to infinity)
- Track value distribution over time

### Issue Detector

**Use when:**
- Preventive monitoring
- Finding systemic issues
- Automated health checks

**Key features:**
- Memory leak detection
- Stuck agent detection
- Value anomaly detection
- Pattern recognition

**Pro tips:**
- Run periodically to catch issues early
- Look for patterns indicating systemic problems
- Check trends for early warning signs
- Focus on critical issues first

### Replay Debugger

**Use when:**
- Complex, intermittent issues
- Need to understand execution flow
- Step-by-step analysis

**Key features:**
- Execution recording
- Step-by-step replay
- Breakpoints
- State inspection

**Pro tips:**
- Record early and often
- Use descriptive breakpoints
- Check state at key decision points
- Export sessions for sharing

## Best Practices

### 1. Start Broad, Then Narrow

1. Run comprehensive diagnostics first
2. Identify the problem area
3. Use specific tools to dive deeper
4. Focus on the most critical issues

### 2. Trace Causal Chains

POLLN is all about causality:

- Always trace causal chains
- Understand parent relationships
- Check for cycles
- Verify causal integrity

### 3. Monitor Trends

Single data points are misleading:

- Track metrics over time
- Look for trends, not snapshots
- Compare to baselines
- Watch for sudden changes

### 4. Check Assumptions

Common incorrect assumptions:

- Agent is active → Check status and lastActive
- Package delivered → Verify receiver got it
- Value is correct → Check for NaN/Infinity
- No deadlocks → Run deadlock detection

### 5. Use Multiple Tools

No single tool gives the full picture:

- Combine tools for comprehensive view
- Cross-validate findings
- Look for consistent patterns
- Triangulate issues

### 6. Document Findings

For complex issues:

- Save diagnostic reports
- Record replay sessions
- Document hypotheses
- Track resolutions

## Troubleshooting

### Tool Not Working

**Problem:** Tool crashes or gives errors

**Solutions:**
1. Check data format matches expected schema
2. Verify colony_id is correct
3. Ensure output directory exists
4. Check Python version (3.8+)
5. Install missing dependencies

### No Issues Found

**Problem:** Tools show no issues but colony is failing

**Solutions:**
1. Check if data is current
2. Verify data completeness
3. Look for edge cases
4. Check thresholds are appropriate
5. Manual code inspection may be needed

### Too Many Issues

**Problem:** Overwhelming number of issues detected

**Solutions:**
1. Focus on critical issues first
2. Look for patterns (use issue_detector patterns)
3. Check for systemic problems
4. Address root causes
5. Fix issues in priority order

### Performance Impact

**Problem:** Debugging tools slowing down colony

**Solutions:**
1. Use sampling instead of full data
2. Run diagnostics on separate system
3. Schedule during low-traffic periods
4. Use replay debugger on recordings
5. Enable/disable specific checks

## Getting Help

If you're stuck:

1. Check this guide first
2. Review tool-specific documentation
3. Run comprehensive diagnostics
4. Export diagnostic report
5. Share report with team

## Appendix

### Data Schemas

See `README.md` for detailed data format specifications.

### Threshold Configuration

Default thresholds can be modified in each tool:

- **Memory:** 500MB (warning), 900MB (critical)
- **CPU:** 70% (warning), 90% (critical)
- **Queue Depth:** 500 (warning), 2000 (critical)
- **Idle Time:** 300s (warning), 600s (critical)

### Exit Codes

- **0:** Success
- **1:** Error
- **2:** Invalid arguments
- **3:** File not found
- **4:** Data format error

---

For more information, see the main README or open an issue on GitHub.
