"""
Flame Graph Generator
Generate interactive flame graphs for CPU, memory, and A2A flow visualization.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import statistics


@dataclass
class FlameGraphNode:
    """A node in the flame graph tree."""
    name: str
    value: float
    children: List['FlameGraphNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StackFrame:
    """A single stack frame sample."""
    name: str
    timestamp: float
    duration: float
    depth: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class FlameGraphGenerator:
    """
    Generate interactive flame graphs for POLLN profiling data.

    Creates:
    - CPU flame graphs (showing where CPU time is spent)
    - Memory flame graphs (showing memory allocations)
    - A2A flow graphs (showing communication patterns)

    Generates interactive HTML with zoom, filter, and search capabilities.

    Usage:
        generator = FlameGraphGenerator()

        # CPU flame graph
        cpu_html = generator.generate_cpu_flame_graph(profile_data, output_path)

        # Memory flame graph
        mem_html = generator.generate_memory_flame_graph(memory_data, output_path)

        # A2A flow graph
        a2a_html = generator.generate_a2a_flow_graph(a2a_data, output_path)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the flame graph generator.

        Args:
            output_dir: Directory to save generated graphs
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_cpu_flame_graph(
        self,
        profile_data: Dict[str, Any],
        output_path: Optional[str] = None,
        title: str = "CPU Flame Graph"
    ) -> str:
        """
        Generate CPU flame graph from profiling data.

        Args:
            profile_data: Profiling data with function calls and timings
            output_path: Output HTML file path
            title: Graph title

        Returns:
            Path to generated HTML file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"flame_graph_cpu_{timestamp}.html")

        # Build flame graph tree
        root = self._build_cpu_tree(profile_data)

        # Generate HTML
        html = self._generate_flame_graph_html(
            root, title, "cpu", profile_data
        )

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def generate_memory_flame_graph(
        self,
        memory_data: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        title: str = "Memory Flame Graph"
    ) -> str:
        """
        Generate memory flame graph from allocation data.

        Args:
            memory_data: Memory allocation snapshots
            output_path: Output HTML file path
            title: Graph title

        Returns:
            Path to generated HTML file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"flame_graph_memory_{timestamp}.html")

        # Build memory tree
        root = self._build_memory_tree(memory_data)

        # Generate HTML
        html = self._generate_flame_graph_html(
            root, title, "memory", memory_data
        )

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def generate_a2a_flow_graph(
        self,
        a2a_data: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        title: str = "A2A Communication Flow"
    ) -> str:
        """
        Generate A2A communication flow graph.

        Args:
            a2a_data: A2A package flow data
            output_path: Output HTML file path
            title: Graph title

        Returns:
            Path to generated HTML file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"flow_graph_a2a_{timestamp}.html")

        # Build flow tree
        root = self._build_a2a_tree(a2a_data)

        # Generate HTML
        html = self._generate_flow_graph_html(
            root, title, a2a_data
        )

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def _build_cpu_tree(self, profile_data: Dict[str, Any]) -> FlameGraphNode:
        """Build CPU flame graph tree from profiling data."""
        root = FlameGraphNode(name="root", value=0)

        # Extract hotspots from profile data
        hotspots = profile_data.get('hotspots', [])

        for hotspot in hotspots:
            func_name = hotspot.get('function', 'unknown')
            total_time = hotspot.get('total_time', 0)
            cumulative_time = hotspot.get('cumulative_time', 0)

            # Create node for this function
            node = FlameGraphNode(
                name=func_name,
                value=total_time,
                metadata={
                    'calls': hotspot.get('calls', 0),
                    'per_call': hotspot.get('per_call', 0),
                    'cumulative': cumulative_time,
                }
            )

            root.children.append(node)
            root.value += total_time

        # Sort by value (descending)
        root.children.sort(key=lambda x: x.value, reverse=True)

        return root

    def _build_memory_tree(self, memory_data: List[Dict[str, Any]]) -> FlameGraphNode:
        """Build memory flame graph tree from allocation data."""
        root = FlameGraphNode(name="root", value=0)

        for allocation in memory_data:
            trace = allocation.get('trace', 'unknown')
            size = allocation.get('size_bytes', 0)
            count = allocation.get('count', 1)

            # Parse trace to get function name
            # Trace format: "file.py:123: function_name"
            parts = trace.split(':')
            if len(parts) >= 3:
                func_name = parts[-1].strip()
            else:
                func_name = trace

            node = FlameGraphNode(
                name=func_name,
                value=size,
                metadata={
                    'count': count,
                    'average': size / count if count > 0 else 0,
                    'trace': trace,
                }
            )

            root.children.append(node)
            root.value += size

        # Sort by value (descending)
        root.children.sort(key=lambda x: x.value, reverse=True)

        return root

    def _build_a2a_tree(self, a2a_data: List[Dict[str, Any]]) -> FlameGraphNode:
        """Build A2A flow tree from communication data."""
        # Group by sender
        senders: Dict[str, List[Dict]] = {}
        total_bytes = 0

        for package in a2a_data:
            sender = package.get('senderId', 'unknown')
            if sender not in senders:
                senders[sender] = []
            senders[sender].append(package)
            total_bytes += package.get('size', 0)

        # Build tree
        root = FlameGraphNode(name="root", value=total_bytes)

        for sender, packages in senders.items():
            sender_bytes = sum(p.get('size', 0) for p in packages)

            # Group by receiver for this sender
            receivers: Dict[str, List[Dict]] = {}
            for pkg in packages:
                receiver = pkg.get('receiverId', 'unknown')
                if receiver not in receivers:
                    receivers[receiver] = []
                receivers[receiver].append(pkg)

            sender_node = FlameGraphNode(
                name=f"Sender: {sender}",
                value=sender_bytes,
                metadata={
                    'package_count': len(packages),
                }
            )

            for receiver, recv_packages in receivers.items():
                recv_bytes = sum(p.get('size', 0) for p in recv_packages)

                recv_node = FlameGraphNode(
                    name=f"Receiver: {receiver}",
                    value=recv_bytes,
                    metadata={
                        'package_count': len(recv_packages),
                    }
                )

                sender_node.children.append(recv_node)

            root.children.append(sender_node)

        # Sort by value
        root.children.sort(key=lambda x: x.value, reverse=True)
        for child in root.children:
            child.children.sort(key=lambda x: x.value, reverse=True)

        return root

    def _generate_flame_graph_html(
        self,
        root: FlameGraphNode,
        title: str,
        graph_type: str,
        data: Any
    ) -> str:
        """Generate interactive flame graph HTML."""
        # Convert tree to JSON for JavaScript
        tree_json = json.dumps(self._node_to_dict(root))

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .info {{
            color: #666;
            margin-bottom: 20px;
        }}
        #chart {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .tooltip {{
            position: absolute;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1000;
        }}
        .controls {{
            margin-bottom: 15px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .controls input {{
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }}
        .controls button {{
            padding: 5px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }}
        .controls button:hover {{
            background-color: #45a049;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="info">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

    <div class="controls">
        <input type="text" id="search" placeholder="Search functions..." onkeyup="filterGraph()">
        <button onclick="resetZoom()">Reset Zoom</button>
        <button onclick="exportData()">Export Data</button>
    </div>

    <div id="chart"></div>
    <div id="tooltip" class="tooltip"></div>

    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script>
        const treeData = {tree_json};
        let currentRoot = treeData;

        function renderChart(root) {{
            const chart = d3.select("#chart");
            chart.selectAll("*").remove();

            const width = chart.node().getBoundingClientRect().width || 1200;
            const height = 600;

            const svg = chart.append("svg")
                .attr("width", width)
                .attr("height", height);

            const hierarchy = d3.hierarchy(root)
                .sum(d => d.value)
                .sort((a, b) => b.value - a.value);

            const rootX = d3.treemap()
                .size([width, height])
                .padding(2)
                .round(true)(hierarchy);

            const color = d3.scaleOrdinal(d3.schemeCategory10);

            const cell = svg.selectAll("g")
                .data(rootX.leaves())
                .join("g")
                .attr("transform", d => `translate(${{d.x0}},${{d.y0}})`);

            cell.append("rect")
                .attr("width", d => d.x1 - d.x0)
                .attr("height", d => d.y1 - d.y0)
                .attr("fill", d => {{
                    while (d.depth > 1) d = d.parent;
                    return color(d.data.name);
                }})
                .attr("stroke", "white")
                .attr("stroke-width", 1)
                .style("cursor", "pointer")
                .on("mouseover", function(event, d) {{
                    showTooltip(event, d);
                }})
                .on("mouseout", hideTooltip)
                .on("click", function(event, d) {{
                    zoomToNode(d);
                }});

            cell.append("text")
                .attr("x", 4)
                .attr("y", 14)
                .text(d => d.data.name)
                .attr("font-size", "11px")
                .attr("fill", "white")
                .style("opacity", d => {{
                    const width = d.x1 - d.x0;
                    return width > 50 ? 1 : 0;
                }})
                .each(function(d) {{
                    const width = d.x1 - d.x0;
                    const text = d3.select(this);
                    if (width > 50 && width < 100) {{
                        const textWidth = text.node().getComputedTextLength();
                        if (textWidth > width - 8) {{
                            text.text(d.data.name.substring(0, Math.floor((width - 8) / 6)) + "...");
                        }}
                    }}
                }});
        }}

        function showTooltip(event, d) {{
            const tooltip = d3.select("#tooltip");
            const metadata = d.data.metadata || {{}};

            let content = `<strong>${{d.data.name}}</strong><br>`;
            content += `Value: ${formatValue(d.value)}<br>`;

            if (metadata.calls !== undefined) {{
                content += `Calls: ${{metadata.calls}}<br>`;
                content += `Per Call: ${{metadata.per_call}}<br>`;
            }}
            if (metadata.count !== undefined) {{
                content += `Count: ${{metadata.count}}<br>`;
                content += `Average: ${{formatValue(metadata.average)}}<br>`;
            }}
            if (metadata.package_count !== undefined) {{
                content += `Packages: ${{metadata.package_count}}<br>`;
            }}

            tooltip
                .html(content)
                .style("opacity", 1)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}

        function hideTooltip() {{
            d3.select("#tooltip").style("opacity", 0);
        }}

        function formatValue(value) {{
            if (typeof value === 'number') {{
                if (value > 1024 * 1024 * 1024) {{
                    return (value / (1024 * 1024 * 1024)).toFixed(2) + " GB";
                }} else if (value > 1024 * 1024) {{
                    return (value / (1024 * 1024)).toFixed(2) + " MB";
                }} else if (value > 1024) {{
                    return (value / 1024).toFixed(2) + " KB";
                }} else {{
                    return value.toFixed(2);
                }}
            }}
            return value;
        }}

        function zoomToNode(d) {{
            currentRoot = d;
            renderChart(d);
        }}

        function resetZoom() {{
            currentRoot = treeData;
            renderChart(treeData);
        }}

        function filterGraph() {{
            const searchTerm = document.getElementById("search").value.toLowerCase();
            // Implement search filtering
            if (searchTerm === "") {{
                renderChart(currentRoot);
            }} else {{
                const filtered = filterTree(currentRoot, searchTerm);
                if (filtered) {{
                    renderChart(filtered);
                }}
            }}
        }}

        function filterTree(node, term) {{
            if (node.name.toLowerCase().includes(term)) {{
                return node;
            }}
            if (node.children) {{
                const filteredChildren = node.children
                    .map(child => filterTree(child, term))
                    .filter(child => child !== null);

                if (filteredChildren.length > 0) {{
                    return {{
                        ...node,
                        children: filteredChildren
                    }};
                }}
            }}
            return null;
        }}

        function exportData() {{
            const dataStr = JSON.stringify(currentRoot, null, 2);
            const blob = new Blob([dataStr], {{type: "application/json"}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "{graph_type}_flame_graph_data.json";
            a.click();
            URL.revokeObjectURL(url);
        }}

        // Initial render
        renderChart(treeData);
    </script>
</body>
</html>
        """

        return html

    def _generate_flow_graph_html(
        self,
        root: FlameGraphNode,
        title: str,
        data: Any
    ) -> str:
        """Generate A2A flow graph HTML (similar to flame graph but for flow)."""
        # Reuse flame graph HTML with different title
        return self._generate_flame_graph_html(root, title, "a2a", data)

    def _node_to_dict(self, node: FlameGraphNode) -> Dict[str, Any]:
        """Convert FlameGraphNode to dictionary for JSON serialization."""
        return {
            'name': node.name,
            'value': node.value,
            'children': [self._node_to_dict(child) for child in node.children],
            'metadata': node.metadata,
        }

    def generate_comparison_graph(
        self,
        profiles: List[Dict[str, Any]],
        labels: List[str],
        output_path: Optional[str] = None,
        title: str = "Performance Comparison"
    ) -> str:
        """
        Generate side-by-side comparison flame graph.

        Args:
            profiles: List of profile data to compare
            labels: Labels for each profile
            output_path: Output HTML file path
            title: Graph title

        Returns:
            Path to generated HTML file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"comparison_flame_graph_{timestamp}.html")

        # Build trees for each profile
        trees = [self._build_cpu_tree(p) for p in profiles]

        # Generate comparison HTML
        html = self._generate_comparison_html(
            trees, labels, title
        )

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def _generate_comparison_html(
        self,
        trees: List[FlameGraphNode],
        labels: List[str],
        title: str
    ) -> str:
        """Generate side-by-side comparison HTML."""
        trees_json = json.dumps([self._node_to_dict(t) for t in trees])
        labels_json = json.dumps(labels)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        .container {{
            display: grid;
            grid-template-columns: repeat({len(trees)}, 1fr);
            gap: 20px;
            margin-top: 20px;
        }}
        .chart {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 15px;
        }}
        .chart h2 {{
            font-size: 16px;
            color: #333;
            margin-top: 0;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="container" id="container"></div>

    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script>
        const trees = {trees_json};
        const labels = {labels_json};

        function renderChart(treeData, containerId, label) {{
            const container = d3.select(containerId);
            const width = container.node().getBoundingClientRect().width || 400;
            const height = 400;

            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height);

            const hierarchy = d3.hierarchy(treeData)
                .sum(d => d.value)
                .sort((a, b) => b.value - a.value);

            const rootX = d3.treemap()
                .size([width, height])
                .padding(2)
                .round(true)(hierarchy);

            const color = d3.scaleOrdinal(d3.schemeCategory10);

            const cell = svg.selectAll("g")
                .data(rootX.leaves())
                .join("g")
                .attr("transform", d => `translate(${{d.x0}},${{d.y0}})`);

            cell.append("rect")
                .attr("width", d => d.x1 - d.x0)
                .attr("height", d => d.y1 - d.y0)
                .attr("fill", d => {{
                    while (d.depth > 1) d = d.parent;
                    return color(d.data.name);
                }})
                .attr("stroke", "white")
                .attr("stroke-width", 1);

            cell.append("text")
                .attr("x", 4)
                .attr("y", 14)
                .text(d => d.data.name)
                .attr("font-size", "10px")
                .attr("fill", "white")
                .style("opacity", d => (d.x1 - d.x0) > 40 ? 1 : 0);
        }}

        const containerDiv = document.getElementById("container");

        trees.forEach((treeData, i) => {{
            const chartDiv = document.createElement("div");
            chartDiv.className = "chart";

            const title = document.createElement("h2");
            title.textContent = labels[i];
            chartDiv.appendChild(title);

            const chartContainer = document.createElement("div");
            chartContainer.id = `chart-${{i}}`;
            chartDiv.appendChild(chartContainer);

            containerDiv.appendChild(chartDiv);

            renderChart(treeData, `#chart-${{i}}`, labels[i]);
        }});
    </script>
</body>
</html>
        """

        return html
