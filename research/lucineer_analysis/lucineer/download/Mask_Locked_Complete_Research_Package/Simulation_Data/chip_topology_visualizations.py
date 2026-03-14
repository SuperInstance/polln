#!/usr/bin/env python3
"""
Chip Topology & Geometric Optimization Visualizations

This script generates all visualizations for the Cycle 1 research document.
Run this to produce PNG files for each analysis section.

Usage:
    python chip_topology_visualizations.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from typing import Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. TOPOLOGICAL DATA ANALYSIS VISUALIZATION
# ============================================================================

class PersistentHomologyAnalyzer:
    """Compute persistent homology of neural network weight matrices."""
    
    def __init__(self, max_dimension=2):
        self.max_dimension = max_dimension
        
    def compute_persistence_diagram(self, weights, metric='correlation'):
        """Compute persistence diagram from weight matrix."""
        if metric == 'correlation':
            corr = np.corrcoef(weights)
            corr = np.nan_to_num(corr, nan=0.0)
            dist_matrix = 1 - np.abs(corr)
        else:
            dist_matrix = squareform(pdist(weights, metric))
        
        thresholds = np.unique(dist_matrix[dist_matrix > 0])
        thresholds = np.sort(thresholds)
        
        persistence = {0: [], 1: []}
        component_history = []
        
        for t in thresholds:
            adj = (dist_matrix <= t).astype(float)
            np.fill_diagonal(adj, 0)
            n_components, _ = connected_components(csr_matrix(adj), directed=False)
            component_history.append((t, n_components))
        
        prev_components = component_history[0][1]
        birth_times = [0.0] * prev_components
        
        for i, (t, n_comp) in enumerate(component_history[1:], 1):
            if n_comp < prev_components:
                n_merged = prev_components - n_comp
                for _ in range(n_merged):
                    if birth_times:
                        persistence[0].append((birth_times.pop(), t))
            prev_components = n_comp
        
        for birth in birth_times:
            persistence[0].append((birth, float('inf')))
        
        return persistence
    
    def persistence_entropy(self, persistence):
        """Compute persistence entropy."""
        all_pairs = []
        for pairs in persistence.values():
            all_pairs.extend(pairs)
        
        lifetimes = []
        for birth, death in all_pairs:
            if death == float('inf'):
                death = birth + 1
            lifetimes.append(max(0, death - birth))
        
        if not lifetimes:
            return 0.0
        
        total = sum(lifetimes)
        if total == 0:
            return 0.0
        
        probs = [l / total for l in lifetimes if l > 0]
        entropy = -sum(p * np.log(p) for p in probs if p > 0)
        
        return entropy


def visualize_topology_analysis():
    """Visualize persistent homology of neural network weights."""
    analyzer = PersistentHomologyAnalyzer()
    
    np.random.seed(42)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Different weight structures
    configs = [
        ('Random (Early Training)', np.random.randn(64, 128) * 0.5),
        ('Sparse (Mid Training)', np.random.randn(64, 128) * 0.3),
        ('Structured (Late Training)', np.random.randn(64, 128) * 0.1 + np.outer(np.ones(64), np.sin(np.linspace(0, 4*np.pi, 128)))),
    ]
    
    for ax_row, (name, weights) in zip(axes, configs):
        # Weight matrix heatmap
        ax = ax_row[0]
        im = ax.imshow(weights[:32, :64], cmap='RdBu_r', aspect='auto')
        ax.set_title(f'{name}\nWeight Matrix')
        ax.set_xlabel('Neuron Index')
        ax.set_ylabel('Sample Index')
        plt.colorbar(im, ax=ax)
        
        # Correlation matrix
        ax = ax_row[1]
        corr = np.corrcoef(weights[:32, :])
        corr = np.nan_to_num(corr, nan=0.0)
        im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
        ax.set_title('Correlation Matrix')
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('Sample Index')
        plt.colorbar(im, ax=ax)
        
        # Persistence diagram
        ax = ax_row[2]
        persistence = analyzer.compute_persistence_diagram(weights[:32, :])
        
        # Plot persistence pairs
        pairs = [(b, d) for b, d in persistence[0] if d != float('inf')]
        if pairs:
            births, deaths = zip(*pairs)
            ax.scatter(births, deaths, c='blue', s=20, alpha=0.7, label='H₀')
        
        # Diagonal line
        max_val = max([d for b, d in persistence[0] if d != float('inf')] + [1])
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Diagonal')
        
        entropy = analyzer.persistence_entropy(persistence)
        ax.set_title(f'Persistence Diagram\nEntropy: {entropy:.3f}')
        ax.set_xlabel('Birth')
        ax.set_ylabel('Death')
        ax.legend(loc='lower right')
    
    plt.tight_layout()
    return fig


# ============================================================================
# 2. GEOMETRIC PLACEMENT VISUALIZATION
# ============================================================================

class GeometricPlacementOptimizer:
    """Optimize PE placement using force-directed layout."""
    
    def __init__(self, die_size=5.2, n_pes=1024, min_spacing=0.05):
        self.die_size = die_size
        self.n_pes = n_pes
        self.min_spacing = min_spacing
        
    def generate_communication_matrix(self, pattern='systolic'):
        """Generate communication weight matrix."""
        n = self.n_pes
        
        if pattern == 'systolic':
            W = np.zeros((n, n))
            grid_size = int(np.sqrt(n))
            for i in range(n):
                row, col = i // grid_size, i % grid_size
                if col > 0: W[i, i-1] = 1.0
                if col < grid_size - 1: W[i, i+1] = 1.0
                if row > 0: W[i, i-grid_size] = 1.0
                if row < grid_size - 1: W[i, i+grid_size] = 1.0
        elif pattern == 'mesh':
            W = np.zeros((n, n))
            grid_size = int(np.sqrt(n))
            for i in range(n):
                row, col = i // grid_size, i % grid_size
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < grid_size and 0 <= nc < grid_size:
                        j = nr * grid_size + nc
                        dist = np.sqrt(dr**2 + dc**2)
                        W[i, j] = 1.0 / dist
        
        W = (W + W.T) / 2
        return W
    
    def optimize_grid_placement(self, pattern='systolic'):
        """Optimize placement for regular grid."""
        grid_size = int(np.sqrt(self.n_pes))
        
        # Optimal grid spacing
        spacing = self.die_size / (grid_size + 1)
        
        positions = np.zeros((self.n_pes, 2))
        for i in range(self.n_pes):
            row, col = i // grid_size, i % grid_size
            positions[i] = [(col + 1) * spacing, (row + 1) * spacing]
        
        return positions
    
    def compute_wirelength(self, P, W):
        """Compute total weighted wirelength."""
        D = cdist(P, P)
        return np.sum(D * W) / 2


def visualize_placement():
    """Visualize PE placement strategies."""
    optimizer = GeometricPlacementOptimizer(die_size=5.2, n_pes=1024)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    patterns = ['systolic', 'mesh']
    
    for i, pattern in enumerate(patterns):
        W = optimizer.generate_communication_matrix(pattern)
        P = optimizer.optimize_grid_placement(pattern)
        wirelength = optimizer.compute_wirelength(P, W)
        
        # Placement view
        ax = axes[i, 0]
        ax.scatter(P[:, 0], P[:, 1], c='blue', s=1, alpha=0.5)
        ax.set_xlim(0, 5.2)
        ax.set_ylim(0, 5.2)
        ax.set_aspect('equal')
        ax.set_title(f'{pattern.capitalize()} Array\nTotal Wirelength: {wirelength:.1f} mm')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.grid(True, alpha=0.3)
        
        # Communication heatmap
        ax = axes[i, 1]
        # Show subset for clarity
        im = ax.imshow(W[:128, :128], cmap='hot', interpolation='nearest')
        ax.set_title(f'{pattern.capitalize()} Communication\n(Subset 128×128)')
        ax.set_xlabel('PE Index')
        ax.set_ylabel('PE Index')
        plt.colorbar(im, ax=ax, label='Weight')
    
    plt.tight_layout()
    return fig


# ============================================================================
# 3. SPACE-FILLING CURVES VISUALIZATION
# ============================================================================

class SpaceFillingCurveAnalyzer:
    """Analyze space-filling curves for chip data layout."""
    
    def __init__(self, grid_size=32, die_size=5.2):
        self.grid_size = grid_size
        self.die_size = die_size
        self.cell_size = die_size / grid_size
        
    def hilbert_d2xy(self, n, d):
        """Convert Hilbert curve index to (x, y) coordinates."""
        x = y = 0
        s = 1
        while s < n:
            rx = 1 & (d // 2)
            ry = 1 & (d ^ rx)
            x, y = self._hilbert_rot(s, x, y, rx, ry)
            x += s * rx
            y += s * ry
            d //= 4
            s *= 2
        return x, y
    
    def _hilbert_rot(self, n, x, y, rx, ry):
        if ry == 0:
            if rx == 1:
                x = n - 1 - x
                y = n - 1 - y
            x, y = y, x
        return x, y
    
    def zorder_d2xy(self, d):
        """Convert Morton/Z-order index to (x, y) coordinates."""
        x = y = 0
        bit = 1
        while d > 0:
            x |= (d & 1) * bit
            d >>= 1
            y |= (d & 1) * bit
            d >>= 1
            bit <<= 1
        return x, y
    
    def generate_hilbert_curve(self):
        n = self.grid_size
        points = np.zeros((n * n, 2))
        for d in range(n * n):
            x, y = self.hilbert_d2xy(n, d)
            points[d] = [x * self.cell_size, y * self.cell_size]
        return points
    
    def generate_zorder_curve(self):
        n = self.grid_size
        points = np.zeros((n * n, 2))
        for d in range(n * n):
            x, y = self.zorder_d2xy(d)
            points[d] = [x * self.cell_size, y * self.cell_size]
        return points
    
    def compute_locality_metrics(self, points):
        consecutive_dists = np.sqrt(np.sum((points[1:] - points[:-1])**2, axis=1))
        return {
            'avg': np.mean(consecutive_dists),
            'max': np.max(consecutive_dists),
            'std': np.std(consecutive_dists)
        }


def visualize_space_filling_curves():
    """Visualize and compare space-filling curves."""
    analyzer = SpaceFillingCurveAnalyzer(grid_size=16, die_size=5.2)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    # Hilbert curve
    ax = axes[0, 0]
    hilbert = analyzer.generate_hilbert_curve()
    ax.plot(hilbert[:, 0], hilbert[:, 1], 'b-', linewidth=0.5, alpha=0.8)
    ax.scatter(hilbert[0, 0], hilbert[0, 1], c='green', s=100, marker='o', label='Start', zorder=5)
    ax.scatter(hilbert[-1, 0], hilbert[-1, 1], c='red', s=100, marker='s', label='End', zorder=5)
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 5.2)
    ax.set_aspect('equal')
    ax.set_title('Hilbert Curve (Order 4)\n16×16 Grid')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Z-order curve
    ax = axes[0, 1]
    zorder = analyzer.generate_zorder_curve()
    ax.plot(zorder[:, 0], zorder[:, 1], 'r-', linewidth=0.5, alpha=0.8)
    ax.scatter(zorder[0, 0], zorder[0, 1], c='green', s=100, marker='o', label='Start', zorder=5)
    ax.scatter(zorder[-1, 0], zorder[-1, 1], c='red', s=100, marker='s', label='End', zorder=5)
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 5.2)
    ax.set_aspect('equal')
    ax.set_title('Z-Order (Morton) Curve\n16×16 Grid')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Locality comparison
    ax = axes[1, 0]
    hilbert_metrics = analyzer.compute_locality_metrics(hilbert)
    zorder_metrics = analyzer.compute_locality_metrics(zorder)
    
    metrics = ['Average', 'Maximum', 'Std Dev']
    hilbert_vals = [hilbert_metrics['avg'], hilbert_metrics['max'], hilbert_metrics['std']]
    zorder_vals = [zorder_metrics['avg'], zorder_metrics['max'], zorder_metrics['std']]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ax.bar(x - width/2, hilbert_vals, width, label='Hilbert', color='blue', alpha=0.7)
    ax.bar(x + width/2, zorder_vals, width, label='Z-Order', color='red', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Distance (mm)')
    ax.set_title('Locality Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Consecutive distance histogram
    ax = axes[1, 1]
    hilbert_dists = np.sqrt(np.sum((hilbert[1:] - hilbert[:-1])**2, axis=1))
    zorder_dists = np.sqrt(np.sum((zorder[1:] - zorder[:-1])**2, axis=1))
    
    ax.hist(hilbert_dists, bins=30, alpha=0.7, label='Hilbert', color='blue')
    ax.hist(zorder_dists, bins=30, alpha=0.7, label='Z-Order', color='red')
    ax.set_xlabel('Consecutive Distance (mm)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Consecutive Distances')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


# ============================================================================
# 4. FRACTAL HEAT SPREADER VISUALIZATION
# ============================================================================

class FractalHeatSpreader:
    """Design fractal heat spreader patterns."""
    
    def __init__(self, die_size=5.2, min_feature=7e-6):
        self.die_size = die_size
        self.min_feature = min_feature
        
    def generate_tree_fractal(self, iterations=5):
        """Generate tree-like fractal heat spreader."""
        def branch(x, y, angle, length, depth, max_depth):
            if depth > max_depth or length < self.min_feature:
                return []
            
            end_x = x + length * np.cos(angle)
            end_y = y + length * np.sin(angle)
            
            segments = [(x, y, end_x, end_y)]
            
            new_length = length * 0.7
            branch_angle = np.pi / 4
            
            segments.extend(branch(end_x, end_y, angle + branch_angle, new_length, depth + 1, max_depth))
            segments.extend(branch(end_x, end_y, angle - branch_angle, new_length, depth + 1, max_depth))
            
            return segments
        
        pattern = []
        start_x, start_y = self.die_size / 2, 0
        initial_length = self.die_size / 4
        
        pattern.extend(branch(start_x, start_y, np.pi/2, initial_length, 1, iterations))
        
        return pattern
    
    def generate_koch_pattern(self, iterations=3):
        """Generate Koch snowflake-inspired pattern."""
        def koch_line(p1, p2, depth):
            if depth == 0:
                return [p1, p2]
            
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            
            a = p1
            b = (p1[0] + dx/3, p1[1] + dy/3)
            angle = np.pi / 3
            c = (b[0] + (dx/3) * np.cos(angle) - (dy/3) * np.sin(angle),
                 b[1] + (dx/3) * np.sin(angle) + (dy/3) * np.cos(angle))
            d = (p1[0] + 2*dx/3, p1[1] + 2*dy/3)
            e = p2
            
            result = []
            result.extend(koch_line(a, b, depth - 1))
            result.extend(koch_line(b, c, depth - 1))
            result.extend(koch_line(c, d, depth - 1))
            result.extend(koch_line(d, e, depth - 1))
            
            return result
        
        corners = [(0, 0), (self.die_size, 0), (self.die_size, self.die_size), (0, self.die_size)]
        
        pattern = []
        for i in range(4):
            p1, p2 = corners[i], corners[(i + 1) % 4]
            pattern.extend(koch_line(p1, p2, iterations))
        
        return pattern


def visualize_fractal_patterns():
    """Visualize fractal heat spreader patterns."""
    spreader = FractalHeatSpreader(die_size=5.2)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    # Tree fractal (different iterations)
    for ax, iterations in zip([axes[0, 0], axes[0, 1]], [4, 5]):
        pattern = spreader.generate_tree_fractal(iterations)
        
        for seg in pattern:
            ax.plot([seg[0], seg[2]], [seg[1], seg[3]], 'b-', linewidth=0.5)
        
        ax.set_xlim(-0.1, 5.3)
        ax.set_ylim(-0.1, 5.3)
        ax.set_aspect('equal')
        ax.set_title(f'Tree Fractal ({iterations} iterations)')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.grid(True, alpha=0.3)
    
    # Koch pattern
    for ax, iterations in zip([axes[1, 0], axes[1, 1]], [2, 3]):
        pattern = spreader.generate_koch_pattern(iterations)
        
        xs = [p[0] for p in pattern]
        ys = [p[1] for p in pattern]
        ax.plot(xs, ys, 'r-', linewidth=0.3, alpha=0.8)
        
        ax.set_xlim(-0.2, 5.4)
        ax.set_ylim(-0.2, 5.4)
        ax.set_aspect('equal')
        ax.set_title(f'Koch Pattern ({iterations} iterations)')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


# ============================================================================
# 5. VORONOI TESSELLATION VISUALIZATION
# ============================================================================

def visualize_voronoi():
    """Visualize Voronoi tessellation for PE placement."""
    from scipy.spatial import Voronoi, voronoi_plot_2d
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    # Different PE counts
    pe_counts = [16, 64, 256, 1024]
    
    for ax, n_pes in zip(axes.flat, pe_counts):
        # Generate uniform random positions
        np.random.seed(42)
        positions = np.random.rand(n_pes, 2) * 5.0 + 0.1
        
        # Compute Voronoi
        margin = 10
        boundary = np.array([
            [-margin, -margin], [-margin, 5.2 + margin],
            [5.2 + margin, -margin], [5.2 + margin, 5.2 + margin]
        ])
        extended = np.vstack([positions, boundary])
        vor = Voronoi(extended)
        
        # Plot
        voronoi_plot_2d(vor, ax=ax, show_vertices=False, 
                       line_colors='blue', line_width=0.5, line_alpha=0.5)
        
        ax.scatter(positions[:, 0], positions[:, 1], c='red', s=10, alpha=0.7)
        
        ax.set_xlim(0, 5.2)
        ax.set_ylim(0, 5.2)
        ax.set_aspect('equal')
        ax.set_title(f'Voronoi Tessellation\n{n_pes} PEs')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


# ============================================================================
# 6. MANIFOLD LEARNING VISUALIZATION
# ============================================================================

def visualize_manifold_learning():
    """Visualize weight manifold analysis."""
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    np.random.seed(42)
    
    # Generate weights on a low-dimensional manifold
    n_samples = 500
    latent_dim = 3
    ambient_dim = 20
    
    # Latent variables
    latent = np.random.randn(n_samples, latent_dim)
    
    # Embed in higher dimension (nonlinear)
    weights = np.zeros((n_samples, ambient_dim))
    weights[:, 0] = latent[:, 0]
    weights[:, 1] = latent[:, 1]
    weights[:, 2] = latent[:, 2]
    weights[:, 3] = latent[:, 0] * latent[:, 1]
    weights[:, 4] = latent[:, 0] ** 2
    weights[:, 5] = np.sin(latent[:, 1])
    weights[:, 6:] = np.random.randn(n_samples, ambient_dim - 6) * 0.1
    
    # True latent space
    ax = axes[0, 0]
    scatter = ax.scatter(latent[:, 0], latent[:, 1], c=latent[:, 2], 
                         cmap='viridis', s=20, alpha=0.7)
    ax.set_title('True Latent Space (3D → 20D)')
    ax.set_xlabel('Latent 1')
    ax.set_ylabel('Latent 2')
    plt.colorbar(scatter, ax=ax, label='Latent 3')
    
    # PCA
    ax = axes[0, 1]
    pca = PCA(n_components=2)
    pca_weights = pca.fit_transform(weights)
    scatter = ax.scatter(pca_weights[:, 0], pca_weights[:, 1], 
                         c=latent[:, 2], cmap='viridis', s=20, alpha=0.7)
    ax.set_title(f'PCA (Explained Var: {sum(pca.explained_variance_ratio_)*100:.1f}%)')
    ax.set_xlabel('PC 1')
    ax.set_ylabel('PC 2')
    plt.colorbar(scatter, ax=ax, label='Latent 3')
    
    # t-SNE
    ax = axes[1, 0]
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    tsne_weights = tsne.fit_transform(weights)
    scatter = ax.scatter(tsne_weights[:, 0], tsne_weights[:, 1], 
                         c=latent[:, 2], cmap='viridis', s=20, alpha=0.7)
    ax.set_title('t-SNE Embedding')
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    plt.colorbar(scatter, ax=ax, label='Latent 3')
    
    # Eigenvalue spectrum
    ax = axes[1, 1]
    pca_full = PCA()
    pca_full.fit(weights)
    
    ax.bar(range(len(pca_full.explained_variance_ratio_)), 
           pca_full.explained_variance_ratio_, color='blue', alpha=0.7)
    ax.axhline(y=0.01, color='r', linestyle='--', label='1% threshold')
    ax.set_title('PCA Explained Variance Spectrum')
    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Explained Variance Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add intrinsic dimension annotation
    cumvar = np.cumsum(pca_full.explained_variance_ratio_)
    intrinsic_dim = np.searchsorted(cumvar, 0.95) + 1
    ax.annotate(f'Intrinsic Dim (95%): {intrinsic_dim}', 
                xy=(intrinsic_dim, pca_full.explained_variance_ratio_[intrinsic_dim-1]),
                xytext=(intrinsic_dim + 2, 0.15),
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=10, color='green')
    
    plt.tight_layout()
    return fig


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all visualizations."""
    import os
    
    output_dir = '/home/z/my-project/research'
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("CHIP TOPOLOGY & GEOMETRIC OPTIMIZATION VISUALIZATIONS")
    print("=" * 60)
    
    # Generate and save each visualization
    visualizations = [
        ('Topology Analysis', visualize_topology_analysis, 'topology_analysis.png'),
        ('PE Placement', visualize_placement, 'pe_placement.png'),
        ('Space-Filling Curves', visualize_space_filling_curves, 'space_filling_curves.png'),
        ('Fractal Heat Spreaders', visualize_fractal_patterns, 'fractal_heat_patterns.png'),
        ('Voronoi Tessellation', visualize_voronoi, 'voronoi_tessellation.png'),
        ('Manifold Learning', visualize_manifold_learning, 'manifold_learning.png'),
    ]
    
    for name, func, filename in visualizations:
        print(f"\nGenerating {name}...")
        try:
            fig = func()
            filepath = os.path.join(output_dir, filename)
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved: {filepath}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("All visualizations generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
