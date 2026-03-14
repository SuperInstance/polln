"""
Network Flow Diagrams for Transformer Inference
================================================

This module generates visual representations of the flow network model.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def draw_transformer_flow_network():
    """Draw the transformer layer flow network."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(-1, 15)
    ax.set_ylim(-2, 4)
    ax.axis('off')
    ax.set_title('Transformer Inference as Flow Network\n(Min-Cut Identifies Bottleneck)', fontsize=14, fontweight='bold')
    
    # Node positions
    nodes = {
        'source': (0, 1),
        'attn_0': (2, 2),
        'ffn_0': (4, 2),
        'attn_1': (6, 2),
        'ffn_1': (8, 2),
        'attn_n': (10, 2),
        'ffn_n': (12, 2),
        'sink': (14, 1),
    }
    
    # Draw nodes
    node_style = dict(boxstyle='round,pad=0.3', facecolor='lightblue', edgecolor='navy', linewidth=2)
    attn_style = dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='orange', linewidth=2)
    ffn_style = dict(boxstyle='round,pad=0.3', facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
    sink_style = dict(boxstyle='round,pad=0.3', facecolor='lightcoral', edgecolor='darkred', linewidth=2)
    
    ax.text(nodes['source'][0], nodes['source'][1], 'Source\n(Input)', ha='center', va='center', 
            fontsize=10, fontweight='bold', bbox=node_style)
    ax.text(nodes['sink'][0], nodes['sink'][1], 'Sink\n(Output)', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=sink_style)
    
    # Layer nodes
    ax.text(nodes['attn_0'][0], nodes['attn_0'][1], 'Attn\nLayer 0', ha='center', va='center',
            fontsize=9, bbox=attn_style)
    ax.text(nodes['ffn_0'][0], nodes['ffn_0'][1], 'FFN\nLayer 0', ha='center', va='center',
            fontsize=9, bbox=ffn_style)
    ax.text(nodes['attn_1'][0], nodes['attn_1'][1], 'Attn\nLayer 1', ha='center', va='center',
            fontsize=9, bbox=attn_style)
    ax.text(nodes['ffn_1'][0], nodes['ffn_1'][1], 'FFN\nLayer 1', ha='center', va='center',
            fontsize=9, bbox=ffn_style)
    ax.text(7, 2, '...', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(nodes['attn_n'][0], nodes['attn_n'][1], 'Attn\nLayer L-1', ha='center', va='center',
            fontsize=9, bbox=attn_style)
    ax.text(nodes['ffn_n'][0], nodes['ffn_n'][1], 'FFN\nLayer L-1', ha='center', va='center',
            fontsize=9, bbox=ffn_style)
    
    # Draw edges with capacity labels
    edge_style = dict(arrowstyle='->', color='black', lw=2, mutation_scale=15)
    cut_style = dict(arrowstyle='->', color='red', lw=3, mutation_scale=15)
    
    # Edges
    edges = [
        ('source', 'attn_0', 'c₀', False),
        ('attn_0', 'ffn_0', 'c₁*', True),  # Min-cut edge
        ('ffn_0', 'attn_1', 'c₂', False),
        ('attn_1', 'ffn_1', 'c₁*', True),  # Min-cut edge
        ('ffn_1', 'attn_n', 'c₃', False),
        ('attn_n', 'ffn_n', 'c₁*', True),  # Min-cut edge
        ('ffn_n', 'sink', 'c₄', False),
    ]
    
    for src, dst, cap, is_cut in edges:
        x1, y1 = nodes[src]
        x2, y2 = nodes[dst]
        style = cut_style if is_cut else edge_style
        ax.annotate('', xy=(x2-0.4, y2), xytext=(x1+0.4, y1),
                   arrowprops=style)
        mid_x = (x1 + x2) / 2
        mid_y = y1 + 0.4
        color = 'red' if is_cut else 'black'
        ax.text(mid_x, mid_y, cap, ha='center', va='bottom', fontsize=10, 
               color=color, fontweight='bold' if is_cut else 'normal')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='lightblue', edgecolor='navy', label='Source/Sink Nodes'),
        mpatches.Patch(facecolor='lightyellow', edgecolor='orange', label='Attention Nodes'),
        mpatches.Patch(facecolor='lightgreen', edgecolor='darkgreen', label='FFN Nodes'),
        plt.Line2D([0], [0], color='red', lw=3, label='Min-Cut Edges (Bottleneck)'),
        plt.Line2D([0], [0], color='black', lw=2, label='Regular Edges'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=9)
    
    # Add equations
    ax.text(7, -0.5, r'$\text{Max Flow} = \text{Min Cut} = c_1^*$', ha='center', va='top',
           fontsize=12, fontweight='bold', 
           bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))
    ax.text(7, -1.2, r'Throughput limited by bottleneck layer capacity', ha='center', va='top',
           fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/flow_network_diagram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: flow_network_diagram.png")


def draw_queueing_model():
    """Draw the queueing model for each layer."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.set_xlim(-1, 15)
    ax.set_ylim(-1, 4)
    ax.axis('off')
    ax.set_title('Queueing Model: Each Layer as M/M/1 Queue', fontsize=14, fontweight='bold')
    
    # Draw three queueing stations
    stations = [
        (2, 'Attention\nQueue', 'λ', 'μ_attn'),
        (7, 'FFN\nQueue', 'λ', 'μ_ffn'),
        (12, 'Output\nQueue', 'λ', 'μ_out'),
    ]
    
    for x, label, arrival, service in stations:
        # Queue rectangle
        queue_rect = FancyBboxPatch((x-1.5, 0.5), 3, 1.5, 
                                     boxstyle='round,pad=0.1',
                                     facecolor='lightyellow', edgecolor='orange', linewidth=2)
        ax.add_patch(queue_rect)
        
        # Server circle
        server_circle = plt.Circle((x, 3), 0.5, facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
        ax.add_patch(server_circle)
        
        # Labels
        ax.text(x, 1.25, label, ha='center', va='center', fontsize=10, fontweight='bold')
        ax.text(x, 3, 'Server', ha='center', va='center', fontsize=8)
        
        # Arrival arrow
        ax.annotate('', xy=(x-0.5, 1.5), xytext=(x-2.5, 1.5),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        ax.text(x-2.5, 1.8, f'Arrival: {arrival}', fontsize=9, color='blue')
        
        # Service arrow (exit)
        ax.annotate('', xy=(x+2.5, 3), xytext=(x+0.7, 3),
                   arrowprops=dict(arrowstyle='->', color='green', lw=2))
        ax.text(x+1.5, 3.3, f'Service: {service}', fontsize=9, color='green')
        
        # Queue to server arrow
        ax.annotate('', xy=(x, 2.5), xytext=(x, 1.8),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Connecting arrows
    ax.annotate('', xy=(5.5, 1.25), xytext=(3.5, 1.25),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax.annotate('', xy=(10.5, 1.25), xytext=(8.5, 1.25),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Equations
    eq_box = dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9)
    ax.text(7, -0.5, r'Utilization: $\rho = \frac{\lambda}{\mu}$', ha='center', fontsize=11, bbox=eq_box)
    ax.text(7, -0.9, r'Queue Time: $W_q = \frac{\rho}{\mu(1-\rho)}$', ha='center', fontsize=11, bbox=eq_box)
    ax.text(7, -1.3, r'System Time: $W = \frac{1}{\mu - \lambda}$', ha='center', fontsize=11, bbox=eq_box)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/queueing_model_diagram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: queueing_model_diagram.png")


def draw_kv_cache_flow():
    """Draw KV cache as flow storage."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 9)
    ax.axis('off')
    ax.set_title('KV Cache as Flow Storage (Reservoir Model)', fontsize=14, fontweight='bold')
    
    # Reservoir (cache)
    reservoir = FancyBboxPatch((3, 1), 6, 4, boxstyle='round,pad=0.2',
                                facecolor='lightblue', edgecolor='navy', linewidth=2)
    ax.add_patch(reservoir)
    ax.text(6, 3, 'KV Cache\nReservoir', ha='center', va='center', 
           fontsize=14, fontweight='bold')
    
    # Water level indicator
    ax.plot([3.2, 3.2], [1.2, 3.5], 'b-', lw=2)
    ax.plot([3.0, 3.4], [3.5, 3.5], 'b-', lw=2)
    ax.text(2.8, 2.5, 'S(t)', ha='right', va='center', fontsize=11)
    
    # Inflow arrow
    ax.annotate('', xy=(5, 5.2), xytext=(5, 7),
               arrowprops=dict(arrowstyle='->', color='green', lw=3))
    ax.text(5, 7.3, r'$f_{in}$: Tokens Generated', ha='center', fontsize=11, color='green')
    
    # Outflow arrow
    ax.annotate('', xy=(5, 0.8), xytext=(5, 0.2),
               arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(5, -0.1, r'$f_{out}$: Tokens Evicted', ha='center', fontsize=11, color='red')
    
    # Read arrow (hit)
    ax.annotate('', xy=(11, 3), xytext=(9.2, 3),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.text(11.5, 3, r'Cache Read (Hit)', ha='left', va='center', fontsize=10, color='blue')
    
    # Storage equation
    eq_box = dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9)
    ax.text(10, 7, r'$\frac{dS}{dt} = f_{in} - f_{out}$', ha='center', fontsize=12, bbox=eq_box)
    ax.text(10, 6.3, r'Equilibrium: $\frac{dS}{dt} = 0$', ha='center', fontsize=11, bbox=eq_box)
    ax.text(10, 5.6, r'Hit Rate: $P_{hit} = 1 - (W/C)^\alpha$', ha='center', fontsize=11, bbox=eq_box)
    
    # Capacity line
    ax.plot([3, 9], [4.7, 4.7], 'r--', lw=2)
    ax.text(9.2, 4.7, 'Capacity C', ha='left', va='center', fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/kv_cache_flow_diagram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: kv_cache_flow_diagram.png")


def draw_parallelism_models():
    """Draw parallelism models."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Pipeline Parallelism
    ax = axes[0]
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 6)
    ax.axis('off')
    ax.set_title('Pipeline Parallelism', fontsize=12, fontweight='bold')
    
    # Devices
    for i, (y, label) in enumerate([(4, 'Device 0\n(Layers 0-3)'), (2, 'Device 1\n(Layers 4-7)'), (0, 'Device 2\n(Layers 8-11)')]):
        device = FancyBboxPatch((0.5, y-0.3), 3, 0.6, boxstyle='round,pad=0.1',
                                 facecolor='lightblue', edgecolor='navy', linewidth=2)
        ax.add_patch(device)
        ax.text(2, y, label, ha='center', va='center', fontsize=8)
        
        # Microbatches flowing through
        for mb in range(3):
            ax.add_patch(plt.Circle((4 + mb * 2, y), 0.2, facecolor='orange', edgecolor='darkorange'))
            ax.text(4 + mb * 2, y + 0.5, f'mb{mb}', ha='center', fontsize=7)
    
    # Arrows showing flow
    ax.annotate('', xy=(3.5, 4), xytext=(3.5, 2.3), arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax.annotate('', xy=(3.5, 2), xytext=(3.5, 0.3), arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Bubble indicator
    ax.text(10, 4, 'Bubble', ha='center', va='center', fontsize=9, color='red')
    ax.text(10, 2, 'Processing', ha='center', va='center', fontsize=9, color='green')
    
    ax.text(5, -0.7, r'$Speedup = P(1 - \frac{P-1}{P+m-1})$', ha='center', fontsize=10)
    
    # Data Parallelism
    ax = axes[1]
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 6)
    ax.axis('off')
    ax.set_title('Data Parallelism', fontsize=12, fontweight='bold')
    
    # Workers with model replicas
    for i, y in enumerate([4, 2, 0]):
        # Model replica
        model = FancyBboxPatch((0.5, y-0.4), 3, 0.8, boxstyle='round,pad=0.1',
                                facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
        ax.add_patch(model)
        ax.text(2, y, f'Worker {i}\n(Full Model)', ha='center', va='center', fontsize=8)
        
        # Data batch
        ax.add_patch(FancyBboxPatch((5, y-0.3), 2, 0.6, boxstyle='round,pad=0.1',
                                     facecolor='lightyellow', edgecolor='orange', linewidth=1))
        ax.text(6, y, f'Batch {i}', ha='center', va='center', fontsize=8)
    
    # All-reduce
    ax.add_patch(FancyBboxPatch((8, 1), 2, 3, boxstyle='round,pad=0.1',
                                 facecolor='lightcoral', edgecolor='darkred', linewidth=2))
    ax.text(9, 2.5, 'All-Reduce\n(Gradients)', ha='center', va='center', fontsize=8)
    
    # Arrows
    for y in [4, 2, 0]:
        ax.annotate('', xy=(8, y+0.3), xytext=(7, y+0.3), arrowprops=dict(arrowstyle='->', color='black', lw=1))
    
    ax.text(5, -0.7, r'$Speedup = \frac{D}{1 + D \cdot T_{comm}/T_1}$', ha='center', fontsize=10)
    
    # Tensor Parallelism
    ax = axes[2]
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 6)
    ax.axis('off')
    ax.set_title('Tensor Parallelism', fontsize=12, fontweight='bold')
    
    # Sharded model across workers
    for i, y in enumerate([4, 2, 0]):
        shard = FancyBboxPatch((0.5, y-0.4), 3, 0.8, boxstyle='round,pad=0.1',
                                facecolor='lightyellow', edgecolor='orange', linewidth=2)
        ax.add_patch(shard)
        ax.text(2, y, f'Worker {i}\n(Shard {i})', ha='center', va='center', fontsize=8)
    
    # Inter-worker communication
    for y1, y2 in [(4, 2), (2, 0)]:
        ax.annotate('', xy=(2, y2 + 0.5), xytext=(2, y1 - 0.5),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    
    # Input/Output
    ax.text(6, 2, 'Input\nToken', ha='center', va='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))
    ax.annotate('', xy=(3.5, 2), xytext=(5.5, 2), arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))
    
    ax.text(9, 2, 'Output\nLogits', ha='center', va='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))
    
    ax.text(5, -0.7, r'$Speedup = \frac{T}{1 + \alpha(T-1)}$', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/parallelism_diagrams.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: parallelism_diagrams.png")


def draw_reliability_model():
    """Draw reliability model."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(-1, 15)
    ax.set_ylim(-1, 9)
    ax.axis('off')
    ax.set_title('Reliability Block Diagram for Inference System', fontsize=14, fontweight='bold')
    
    # Series system of components
    components = [
        (1, 'Input\nLayer', 'lightblue'),
        (3, 'Attn\nL0', 'lightyellow'),
        (4.5, 'FFN\nL0', 'lightgreen'),
        (6, 'Attn\nL1', 'lightyellow'),
        (7.5, 'FFN\nL1', 'lightgreen'),
        (9, '...', 'white'),
        (10.5, 'Attn\nLn', 'lightyellow'),
        (12, 'FFN\nLn', 'lightgreen'),
        (14, 'Output\nLayer', 'lightcoral'),
    ]
    
    for x, label, color in components:
        if color != 'white':
            comp = FancyBboxPatch((x-0.5, 3.5), 1, 1.5, boxstyle='round,pad=0.1',
                                   facecolor=color, edgecolor='gray', linewidth=2)
            ax.add_patch(comp)
        ax.text(x, 4.25, label, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Series connection
    for i in range(len(components) - 1):
        x1 = components[i][0] + 0.5
        x2 = components[i+1][0] - 0.5
        ax.plot([x1, x2], [4.25, 4.25], 'k-', lw=2)
    
    # Input/output arrows
    ax.annotate('', xy=(0.5, 4.25), xytext=(-0.5, 4.25),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.annotate('', xy=(15, 4.25), xytext=(14.5, 4.25),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    
    # TMR for critical components
    ax.text(7.5, 7, 'Triple Modular Redundancy (TMR) for Critical Layers', ha='center', fontsize=11, fontweight='bold')
    
    # Draw TMR structure
    for i, y in enumerate([6.5, 5.5, 4.5]):
        ax.add_patch(plt.Circle((5, y), 0.3, facecolor='lightyellow', edgecolor='orange', linewidth=1))
        ax.text(5, y, 'C', ha='center', va='center', fontsize=8)
    ax.text(5.8, 5.5, 'Voter', ha='left', va='center', fontsize=9)
    ax.add_patch(FancyBboxPatch((6.2, 5.2), 0.8, 0.6, boxstyle='round,pad=0.05',
                                 facecolor='lightgreen', edgecolor='darkgreen', linewidth=1))
    
    # Connect to voter
    for y in [6.5, 5.5, 4.5]:
        ax.plot([5.3, 6.2], [y, 5.5], 'k-', lw=1)
    
    # Equations
    eq_box = dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9)
    ax.text(3, 1.5, r'Series: $R_{system} = \prod_i R_i$', ha='center', fontsize=11, bbox=eq_box)
    ax.text(7.5, 1.5, r'TMR: $R_{TMR} = 3R^2 - 2R^3$', ha='center', fontsize=11, bbox=eq_box)
    ax.text(12, 1.5, r'MTBF $= \frac{1}{\sum_i \lambda_i}$', ha='center', fontsize=11, bbox=eq_box)
    
    ax.text(7.5, 0.5, r'Availability $= \frac{MTBF}{MTBF + MTTR}$', ha='center', fontsize=12, fontweight='bold', bbox=eq_box)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/reliability_diagram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: reliability_diagram.png")


def draw_scheduling_gantt():
    """Draw Gantt chart for scheduling."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_title('Layer Execution Scheduling (Johnson\'s Rule)', fontsize=14, fontweight='bold')
    
    # Define layer jobs
    layers = list(range(6))
    attn_times = [0.5, 0.7, 0.3, 0.6, 0.4, 0.5]
    ffn_times = [0.8, 0.4, 0.9, 0.5, 0.7, 0.6]
    
    # Johnson's rule ordering
    # Sort: if attn < ffn, put first; else put last
    jobs = list(zip(layers, attn_times, ffn_times))
    front = []
    back = []
    while jobs:
        min_job = min(jobs, key=lambda x: min(x[1], x[2]))
        jobs.remove(min_job)
        if min_job[1] <= min_job[2]:
            front.append(min_job)
        else:
            back.append(min_job)
    ordered = front + back[::-1]
    
    # Draw Gantt chart
    colors_attn = plt.cm.Blues(np.linspace(0.4, 0.8, 6))
    colors_ffn = plt.cm.Greens(np.linspace(0.4, 0.8, 6))
    
    y_pos = 6
    attn_end = 0
    
    for i, (layer, attn_t, ffn_t) in enumerate(ordered):
        # Attention
        ax.barh(y_pos, attn_t, left=attn_end, height=0.6, color=colors_attn[layer], 
               edgecolor='navy', linewidth=1)
        ax.text(attn_end + attn_t/2, y_pos, f'L{layer}\nAttn', ha='center', va='center', fontsize=8)
        
        # FFN
        ffn_start = max(attn_end + attn_t, (i+1) * 0.1 if i == 0 else ffn_start + ffn_times[ordered[i-1][0]])
        ax.barh(y_pos - 0.8, ffn_t, left=attn_end + attn_t, height=0.6, color=colors_ffn[layer],
               edgecolor='darkgreen', linewidth=1)
        ax.text(attn_end + attn_t + ffn_t/2, y_pos - 0.8, f'L{layer}\nFFN', ha='center', va='center', fontsize=8)
        
        attn_end += attn_t
    
    # Add annotations
    ax.axhline(y=6.3, color='black', lw=1, linestyle='--', alpha=0.3)
    ax.axhline(y=5.5, color='black', lw=1, linestyle='--', alpha=0.3)
    
    ax.text(0, 7.5, 'Machine 1: Attention', fontsize=10, fontweight='bold')
    ax.text(0, 4.7, 'Machine 2: FFN', fontsize=10, fontweight='bold')
    
    # Makespan annotation
    makespan = sum(t[1] for t in ordered) + ordered[-1][2]
    ax.annotate('', xy=(makespan, 4.5), xytext=(makespan, 6.3),
               arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(makespan + 0.2, 5.4, f'Makespan\n= {makespan:.2f}', fontsize=10, color='red')
    
    # Legend
    ax.text(8, 3, 'Johnson\'s Rule:', fontsize=11, fontweight='bold')
    ax.text(8, 2.5, '1. Find min(attn_i, ffn_i)', fontsize=9)
    ax.text(8, 2, '2. If min is attn, schedule first', fontsize=9)
    ax.text(8, 1.5, '3. If min is ffn, schedule last', fontsize=9)
    ax.text(8, 1, '4. Repeat for remaining jobs', fontsize=9)
    
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/scheduling_gantt.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: scheduling_gantt.png")


if __name__ == "__main__":
    print("Generating network flow diagrams...")
    draw_transformer_flow_network()
    draw_queueing_model()
    draw_kv_cache_flow()
    draw_parallelism_models()
    draw_reliability_model()
    draw_scheduling_gantt()
    print("\nAll diagrams generated successfully!")
