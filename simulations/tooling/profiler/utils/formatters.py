"""
Formatting Utilities
Helper functions for formatting profiling data.
"""

import math
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta


def format_duration(seconds: float, precision: int = 2) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds
        precision: Decimal places for seconds

    Returns:
        Formatted duration string (e.g., "1h 23m 45.67s")
    """
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f}ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.{precision}f}ms"
    elif seconds < 60:
        return f"{seconds:.{precision}f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.{precision}f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.{precision}f}s"


def format_bytes(bytes_value: int, precision: int = 2) -> str:
    """
    Format bytes in human-readable format.

    Args:
        bytes_value: Number of bytes
        precision: Decimal places

    Returns:
        Formatted bytes string (e.g., "1.23 MB")
    """
    if bytes_value == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = min(
        int(math.log(abs(bytes_value), 1024)),
        len(units) - 1
    )

    value = bytes_value / (1024 ** unit_index)
    return f"{value:.{precision}f} {units[unit_index]}"


def format_number(num: float, precision: int = 2) -> str:
    """
    Format number with thousands separator.

    Args:
        num: Number to format
        precision: Decimal places

    Returns:
        Formatted number string
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"


def format_percent(value: float, total: float, precision: int = 1) -> str:
    """
    Format value as percentage of total.

    Args:
        value: Numerator
        total: Denominator
        precision: Decimal places

    Returns:
        Percentage string
    """
    if total == 0:
        return "0.0%"

    percent = (value / total) * 100
    return f"{percent:.{precision}f}%"


def format_timestamp(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format Unix timestamp to datetime string.

    Args:
        timestamp: Unix timestamp
        format_str: strftime format string

    Returns:
        Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)


def format_metrics(
    metrics: Dict[str, Any],
    indent: int = 0,
    show_timestamps: bool = True
) -> str:
    """
    Format metrics dictionary for display.

    Args:
        metrics: Metrics dictionary
        indent: Indentation level
        show_timestamps: Whether to show timestamps

    Returns:
        Formatted multi-line string
    """
    lines = []
    prefix = "  " * indent

    for key, value in sorted(metrics.items()):
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_metrics(value, indent + 1, show_timestamps))
        elif isinstance(value, (int, float)):
            # Determine format based on key name
            if any(k in key.lower() for k in ['time', 'duration', 'latency']):
                lines.append(f"{prefix}{key}: {format_duration(value)}")
            elif any(k in key.lower() for k in ['bytes', 'memory', 'size']):
                lines.append(f"{prefix}{key}: {format_bytes(int(value))}")
            elif any(k in key.lower() for k in ['percent', 'rate', 'ratio']):
                lines.append(f"{prefix}{key}: {format_percent(value, 1) if value <= 100 else f'{value:.2f}'}")
            else:
                lines.append(f"{prefix}{key}: {format_number(value)}")
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: [{len(value)} items]")
        elif isinstance(value, str):
            lines.append(f"{prefix}{key}: {value}")
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)


def format_table(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
    reverse: bool = True,
    max_rows: Optional[int] = None
) -> str:
    """
    Format data as a table.

    Args:
        data: List of dictionaries with same keys
        columns: Column names (defaults to all keys from first item)
        sort_by: Column to sort by
        reverse: Sort descending
        max_rows: Maximum rows to display

    Returns:
        Formatted table string
    """
    if not data:
        return "No data"

    # Determine columns
    if columns is None:
        columns = list(data[0].keys())

    # Sort data
    if sort_by and sort_by in columns:
        data = sorted(
            data,
            key=lambda x: x.get(sort_by, 0),
            reverse=reverse
        )

    # Limit rows
    if max_rows:
        data = data[:max_rows]

    # Calculate column widths
    col_widths = {
        col: max(len(str(col)), max(len(str(row.get(col, ''))) for row in data))
        for col in columns
    }

    # Build header
    lines = []
    header = " | ".join(str(col).ljust(col_widths[col]) for col in columns)
    lines.append(header)
    lines.append("-" * len(header))

    # Build rows
    for row in data:
        line = " | ".join(
            str(row.get(col, '')).ljust(col_widths[col])
            for col in columns
        )
        lines.append(line)

    return "\n".join(lines)


def format_histogram(
    data: Dict[str, float],
    width: int = 50,
    char: str = "█"
) -> str:
    """
    Format histogram data as ASCII histogram.

    Args:
        data: Dictionary of label -> value
        width: Maximum width of bars
        char: Character for bars

    Returns:
        ASCII histogram string
    """
    if not data:
        return "No data"

    max_value = max(data.values())
    lines = []

    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((value / max_value) * width) if max_value > 0 else 0
        bar = char * bar_length

        # Format value
        if isinstance(value, float):
            value_str = f"{value:.2f}"
        else:
            value_str = str(value)

        lines.append(f"{label:20} {bar} {value_str}")

    return "\n".join(lines)


def format_progress(
    current: int,
    total: int,
    width: int = 40,
    prefix: str = "Progress"
) -> str:
    """
    Format progress bar.

    Args:
        current: Current progress
        total: Total value
        width: Bar width
        prefix: Label prefix

    Returns:
        Progress bar string
    """
    if total == 0:
        progress = 0
    else:
        progress = current / total

    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percent = progress * 100

    return f"{prefix}: [{bar}] {percent:.1f}% ({current}/{total})"


def format_speedup(
    baseline: float,
    optimized: float,
    precision: int = 2
) -> str:
    """
    Format speedup as "X times faster".

    Args:
        baseline: Baseline time
        optimized: Optimized time
        precision: Decimal places

    Returns:
        Speedup string
    """
    if optimized == 0:
        return "∞x faster"

    speedup = baseline / optimized
    if speedup > 1:
        return f"{speedup:.{precision}f}x faster"
    else:
        slowdown = optimized / baseline
        return f"{slowdown:.{precision}f}x slower"
