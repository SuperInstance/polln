#!/usr/bin/env python3
"""
Replay Debugger - Record and replay colony execution for step-by-step debugging.

This tool records colony execution for later replay, allowing step-through
execution, state inspection at any point, forward/backward stepping, and breakpoints.
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from collections import defaultdict
import time
import pickle


@dataclass
class ExecutionEvent:
    """A single event in colony execution."""
    event_id: str
    timestamp: float
    event_type: str  # 'agent_spawn', 'agent_kill', 'a2a_send', 'a2a_receive', 'state_change'
    agent_id: Optional[str]
    data: Dict[str, Any]
    state_snapshot: Optional[Dict[str, Any]]  # Colony state after this event

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Breakpoint:
    """A breakpoint for debugging."""
    breakpoint_id: str
    condition: str  # e.g., "agent_id == 'agent-1'"
    event_type: Optional[str]
    enabled: bool
    hit_count: int

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ReplayState:
    """State of the replay debugger."""
    current_position: int
    total_events: int
    current_agent_states: Dict[str, Any]
    current_a2a_packages: List[Dict[str, Any]]
    breakpoints: Dict[str, Breakpoint]
    variables: Dict[str, Any]  # User-defined variables for debugging

    def to_dict(self) -> Dict:
        return asdict(self)


class ReplayDebugger:
    """
    Record and replay colony execution for debugging.

    Features:
    - Record colony execution events
    - Replay execution step-by-step
    - Inspect state at any point
    - Forward and backward stepping
    - Set breakpoints with conditions
    - Inspect variables and expressions
    - Export/import replay sessions
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Execution recording
        self.events: List[ExecutionEvent] = []
        self.recording_start_time: Optional[float] = None
        self.is_recording = False

        # Replay state
        self.replay_state = ReplayState(
            current_position=0,
            total_events=0,
            current_agent_states={},
            current_a2a_packages=[],
            breakpoints={},
            variables={}
        )

        # State snapshots for fast seeking
        self.state_snapshots: Dict[int, Dict[str, Any]] = {}

    def start_recording(self) -> None:
        """Start recording colony execution."""
        self.is_recording = True
        self.recording_start_time = time.time()
        self.events = []
        print(f"Started recording colony {self.colony_id}")

    def stop_recording(self) -> None:
        """Stop recording colony execution."""
        self.is_recording = False
        print(f"Stopped recording. Captured {len(self.events)} events")

    def record_event(self, event_type: str, agent_id: Optional[str],
                    data: Dict[str, Any],
                    state_snapshot: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an execution event.

        Args:
            event_type: Type of event
            agent_id: Associated agent ID
            data: Event-specific data
            state_snapshot: Optional colony state snapshot after event
        """
        if not self.is_recording:
            return

        event = ExecutionEvent(
            event_id=f"event_{len(self.events)}",
            timestamp=time.time() - (self.recording_start_time or time.time()),
            event_type=event_type,
            agent_id=agent_id,
            data=data,
            state_snapshot=state_snapshot
        )

        self.events.append(event)

        # Save state snapshot periodically for fast seeking
        if len(self.events) % 100 == 0 and state_snapshot:
            self.state_snapshots[len(self.events) - 1] = state_snapshot

    def save_recording(self, filename: Optional[str] = None) -> str:
        """
        Save recording to file.

        Args:
            filename: Optional filename (defaults to replay_data.json)

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"replay_data_{self.colony_id}_{int(time.time())}.json"

        output_path = self.output_dir / filename

        recording_data = {
            'colony_id': self.colony_id,
            'recording_start_time': self.recording_start_time,
            'events': [e.to_dict() for e in self.events],
            'state_snapshots': self.state_snapshots
        }

        with open(output_path, 'w') as f:
            json.dump(recording_data, f, indent=2)

        print(f"Recording saved to: {output_path}")
        return str(output_path)

    def load_recording(self, filename: str) -> None:
        """
        Load recording from file.

        Args:
            filename: Path to recording file
        """
        with open(filename, 'r') as f:
            recording_data = json.load(f)

        self.colony_id = recording_data['colony_id']
        self.recording_start_time = recording_data['recording_start_time']
        self.events = [ExecutionEvent(**e) for e in recording_data['events']]
        self.state_snapshots = recording_data.get('state_snapshots', {})

        # Initialize replay state
        self.replay_state.total_events = len(self.events)
        self.replay_state.current_position = 0

        print(f"Loaded recording with {len(self.events)} events")

    def start_replay(self) -> None:
        """Start replay session."""
        self.replay_state.current_position = 0
        self.replay_state.total_events = len(self.events)
        print(f"Starting replay of {len(self.events)} events")

    def step_forward(self, count: int = 1) -> Optional[ExecutionEvent]:
        """
        Step forward in execution.

        Args:
            count: Number of steps to move forward

        Returns:
            The event at the new position, or None if at end
        """
        new_position = self.replay_state.current_position + count

        if new_position >= self.replay_state.total_events:
            print("Already at end of recording")
            return None

        self.replay_state.current_position = new_position
        event = self.events[new_position]

        # Update current state
        if event.state_snapshot:
            self._update_replay_state(event.state_snapshot)

        return event

    def step_backward(self, count: int = 1) -> Optional[ExecutionEvent]:
        """
        Step backward in execution.

        Args:
            count: Number of steps to move backward

        Returns:
            The event at the new position, or None if at beginning
        """
        new_position = self.replay_state.current_position - count

        if new_position < 0:
            print("Already at beginning of recording")
            return None

        self.replay_state.current_position = new_position
        event = self.events[new_position]

        # Update current state
        if event.state_snapshot:
            self._update_replay_state(event.state_snapshot)

        return event

    def jump_to(self, position: int) -> Optional[ExecutionEvent]:
        """
        Jump to a specific position in execution.

        Args:
            position: Position to jump to

        Returns:
            The event at the new position, or None if invalid
        """
        if position < 0 or position >= self.replay_state.total_events:
            print(f"Invalid position: {position}")
            return None

        # Find nearest state snapshot
        snapshot_position = max(
            [p for p in self.state_snapshots.keys() if p <= position],
            default=-1
        )

        # Load snapshot if available
        if snapshot_position >= 0:
            self._update_replay_state(self.state_snapshots[snapshot_position])
            # Replay events from snapshot to target
            for i in range(snapshot_position + 1, position + 1):
                if self.events[i].state_snapshot:
                    self._update_replay_state(self.events[i].state_snapshot)
        else:
            # No snapshot, replay from beginning
            for i in range(position + 1):
                if self.events[i].state_snapshot:
                    self._update_replay_state(self.events[i].state_snapshot)

        self.replay_state.current_position = position
        return self.events[position]

    def set_breakpoint(self, condition: str,
                      event_type: Optional[str] = None) -> Breakpoint:
        """
        Set a breakpoint.

        Args:
            condition: Python expression that evaluates to True to break
            event_type: Optional event type filter

        Returns:
            The created breakpoint
        """
        breakpoint_id = f"bp_{len(self.replay_state.breakpoints)}"
        breakpoint = Breakpoint(
            breakpoint_id=breakpoint_id,
            condition=condition,
            event_type=event_type,
            enabled=True,
            hit_count=0
        )

        self.replay_state.breakpoints[breakpoint_id] = breakpoint
        print(f"Breakpoint set: {breakpoint_id} - {condition}")
        return breakpoint

    def check_breakpoints(self, event: ExecutionEvent) -> bool:
        """
        Check if any breakpoints should trigger.

        Args:
            event: Current event

        Returns:
            True if a breakpoint triggered
        """
        for bp in self.replay_state.breakpoints.values():
            if not bp.enabled:
                continue

            if bp.event_type and bp.event_type != event.event_type:
                continue

            try:
                # Build evaluation context
                context = {
                    'event': event,
                    'agent_id': event.agent_id,
                    'event_type': event.event_type,
                    'data': event.data,
                    **self.replay_state.variables
                }

                if eval(bp.condition, {}, context):
                    bp.hit_count += 1
                    print(f"Breakpoint hit: {bp.breakpoint_id}")
                    print(f"  Condition: {bp.condition}")
                    print(f"  Event: {event.event_type} at position {self.replay_state.current_position}")
                    return True
            except Exception as e:
                print(f"Error evaluating breakpoint condition: {e}")

        return False

    def continue_execution(self) -> Optional[ExecutionEvent]:
        """
        Continue execution until next breakpoint or end.

        Returns:
            The event where breakpoint triggered, or None if at end
        """
        while self.replay_state.current_position < self.replay_state.total_events:
            event = self.step_forward()
            if event is None:
                return None

            if self.check_breakpoints(event):
                return event

        return None

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current colony state during replay.

        Returns:
            Dictionary containing current state
        """
        return {
            'position': self.replay_state.current_position,
            'total_events': self.replay_state.total_events,
            'agent_states': self.replay_state.current_agent_states,
            'a2a_packages': self.replay_state.current_a2a_packages,
            'variables': self.replay_state.variables
        }

    def inspect_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Inspect an agent's current state during replay.

        Args:
            agent_id: Agent ID to inspect

        Returns:
            Agent state dictionary, or None if agent not found
        """
        return self.replay_state.current_agent_states.get(agent_id)

    def evaluate_expression(self, expression: str) -> Any:
        """
        Evaluate a Python expression in the replay context.

        Args:
            expression: Python expression to evaluate

        Returns:
            Result of evaluation
        """
        context = {
            'state': self.replay_state,
            'agents': self.replay_state.current_agent_states,
            'packages': self.replay_state.current_a2a_packages,
            'position': self.replay_state.current_position,
            **self.replay_state.variables
        }

        try:
            return eval(expression, {}, context)
        except Exception as e:
            return f"Error: {e}"

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set a debugging variable.

        Args:
            name: Variable name
            value: Variable value
        """
        self.replay_state.variables[name] = value
        print(f"Set variable: {name} = {value}")

    def print_event_info(self, event: ExecutionEvent) -> None:
        """Print information about an event."""
        print(f"\n{'=' * 80}")
        print(f"Event {self.replay_state.current_position}: {event.event_type}")
        print(f"{'=' * 80}")
        print(f"Timestamp: {event.timestamp:.3f}s")
        print(f"Agent: {event.agent_id}")
        print(f"Data: {json.dumps(event.data, indent=2)}")

    def print_replay_summary(self) -> None:
        """Print summary of current replay state."""
        event = self.events[self.replay_state.current_position] if self.events else None

        print(f"\n{'=' * 80}")
        print(f"Replay Summary")
        print(f"{'=' * 80}")
        print(f"Position: {self.replay_state.current_position} / {self.replay_state.total_events}")
        print(f"Progress: {self.replay_state.current_position / max(1, self.replay_state.total_events) * 100:.1f}%")

        if event:
            print(f"Current Event: {event.event_type}")
            print(f"Agent: {event.agent_id}")

        print(f"\nAgents: {len(self.replay_state.current_agent_states)}")
        print(f"A2A Packages: {len(self.replay_state.current_a2a_packages)}")
        print(f"Breakpoints: {len(self.replay_state.breakpoints)}")
        print(f"Variables: {len(self.replay_state.variables)}")

    def export_session(self, filename: Optional[str] = None) -> str:
        """
        Export current replay session.

        Args:
            filename: Optional filename

        Returns:
            Path to exported session
        """
        if filename is None:
            filename = f"replay_session_{self.colony_id}_{int(time.time())}.json"

        output_path = self.output_dir / filename

        session_data = {
            'colony_id': self.colony_id,
            'replay_state': self.replay_state.to_dict(),
            'current_event': self.events[self.replay_state.current_position].to_dict()
            if self.events and self.replay_state.current_position < len(self.events)
            else None
        }

        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)

        print(f"Session exported to: {output_path}")
        return str(output_path)

    def _update_replay_state(self, state_snapshot: Dict[str, Any]) -> None:
        """Update replay state from snapshot."""
        self.replay_state.current_agent_states = state_snapshot.get('agents', {})
        self.replay_state.current_a2a_packages = state_snapshot.get('a2a_packages', [])


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python replay_debugger.py <colony_id> [command]")
        print("\nCommands:")
        print("  record                    - Start recording")
        print("  stop                      - Stop recording")
        print("  save [filename]           - Save recording")
        print("  load <filename>           - Load recording")
        print("  replay                    - Start replay")
        print("  step [count]              - Step forward")
        print("  back [count]              - Step backward")
        print("  jump <position>           - Jump to position")
        print("  bp <condition> [type]     - Set breakpoint")
        print("  continue                  - Continue to breakpoint")
        print("  state                     - Show current state")
        print("  inspect <agent_id>        - Inspect agent")
        print("  eval <expression>         - Evaluate expression")
        print("  set <name> <value>        - Set variable")
        print("  export [filename]         - Export session")
        sys.exit(1)

    colony_id = sys.argv[1]
    debugger = ReplayDebugger(colony_id)

    if len(sys.argv) < 3:
        print("No command specified")
        sys.exit(1)

    command = sys.argv[2]

    if command == "record":
        debugger.start_recording()
        print("Recording... (Ctrl+C to stop)")

    elif command == "stop":
        debugger.stop_recording()

    elif command == "save":
        filename = sys.argv[3] if len(sys.argv) >= 4 else None
        debugger.save_recording(filename)

    elif command == "load" and len(sys.argv) >= 4:
        debugger.load_recording(sys.argv[3])

    elif command == "replay":
        debugger.start_replay()

    elif command == "step":
        count = int(sys.argv[3]) if len(sys.argv) >= 4 else 1
        event = debugger.step_forward(count)
        if event:
            debugger.print_event_info(event)

    elif command == "back":
        count = int(sys.argv[3]) if len(sys.argv) >= 4 else 1
        event = debugger.step_backward(count)
        if event:
            debugger.print_event_info(event)

    elif command == "jump" and len(sys.argv) >= 4:
        event = debugger.jump_to(int(sys.argv[3]))
        if event:
            debugger.print_event_info(event)

    elif command == "bp" and len(sys.argv) >= 4:
        event_type = sys.argv[4] if len(sys.argv) >= 5 else None
        debugger.set_breakpoint(sys.argv[3], event_type)

    elif command == "continue":
        event = debugger.continue_execution()
        if event:
            debugger.print_event_info(event)

    elif command == "state":
        debugger.print_replay_summary()

    elif command == "inspect" and len(sys.argv) >= 4:
        agent_state = debugger.inspect_agent(sys.argv[3])
        if agent_state:
            print(json.dumps(agent_state, indent=2))
        else:
            print("Agent not found")

    elif command == "eval" and len(sys.argv) >= 4:
        result = debugger.evaluate_expression(sys.argv[3])
        print(f"Result: {result}")

    elif command == "set" and len(sys.argv) >= 4:
        value = sys.argv[4] if len(sys.argv) >= 5 else None
        # Try to parse as JSON, fall back to string
        try:
            value = json.loads(value)
        except:
            pass
        debugger.set_variable(sys.argv[3], value)

    elif command == "export":
        filename = sys.argv[3] if len(sys.argv) >= 4 else None
        debugger.export_session(filename)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
