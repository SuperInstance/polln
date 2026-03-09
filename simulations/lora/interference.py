"""
Interference Detection for LoRA Composition

Validates when two LoRAs interfere with each other

Metrics:
- interference = corr(B_1×A_1, B_2×A_2)
- gradient_conflict = cos(g_1, g_2)
- performance_degradation = metrics(L_1 alone) - metrics(L_1 ⊕ L_2)

Key questions:
1. Can we predict interference from LoRA parameters?
2. Which expert pairs are compatible vs incompatible?
3. How does interference scale with rank overlap?
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
import json
from scipy.stats import pearsonr, spearmanr
from sklearn.cluster import KMeans
import seaborn as sns


@dataclass
class InterferenceMetrics:
    """Metrics for LoRA pair interference"""
    lora1_name: str
    lora2_name: str

    # Correlation-based metrics
    weight_correlation: float
    subspace_overlap: float

    # Gradient-based metrics
    gradient_conflict: float
    gradient_angle: float

    # Performance metrics
    performance_degradation: float
    combined_performance: float

    # Predictions
    predicted_compatibility: float
    actual_compatibility: float


class LoRAPair:
    """Represents a pair of LoRA adapters for interference analysis"""

    def __init__(
        self,
        B1: torch.Tensor,
        A1: torch.Tensor,
        B2: torch.Tensor,
        A2: torch.Tensor,
        name1: str = "LoRA_1",
        name2: str = "LoRA_2"
    ):
        self.B1, self.A1 = B1, A1
        self.B2, self.A2 = B2, A2
        self.name1, self.name2 = name1, name2

        self.dim = B1.shape[0]
        self.rank1 = A1.shape[0]
        self.rank2 = A2.shape[0]

    @property
    def delta_W1(self) -> torch.Tensor:
        """ΔW_1 = B_1 @ A_1"""
        return self.B1 @ self.A1

    @property
    def delta_W2(self) -> torch.Tensor:
        """ΔW_2 = B_2 @ A_2"""
        return self.B2 @ self.A2

    def combined_delta_W(self, weight1: float = 1.0, weight2: float = 1.0) -> torch.Tensor:
        """Combined ΔW = w_1 * B_1 @ A_1 + w_2 * B_2 @ A_2"""
        return weight1 * self.delta_W1 + weight2 * self.delta_W2


class InterferenceCalculator:
    """Calculate various interference metrics between LoRA pairs"""

    @staticmethod
    def weight_correlation(pair: LoRAPair) -> float:
        """
        Pearson correlation between weight matrices

        corr(B_1 @ A_1, B_2 @ A_2)
        """
        delta1 = pair.delta_W1.flatten().cpu().numpy()
        delta2 = pair.delta_W2.flatten().cpu().numpy()

        corr, _ = pearsonr(delta1, delta2)
        return corr

    @staticmethod
    def subspace_overlap(pair: LoRAPair, method: str = "principal") -> float:
        """
        Measure overlap between LoRA subspaces

        Methods:
        - principal: Overlap of principal subspaces (Grassmann distance)
        - volume: Volume overlap ratio
        - projection: Average projection score
        """
        if method == "principal":
            # Compute principal angles via SVD
            # Normalize matrices
            U1, _, _ = torch.linalg.svd(pair.delta_W1)
            U2, _, _ = torch.linalg.svd(pair.delta_W2)

            # Take top-r components
            r_min = min(pair.rank1, pair.rank2)
            U1_r = U1[:, :r_min]
            U2_r = U2[:, :r_min]

            # Projective metric: ||U1^T @ U2||_F / r
            projection = U1_r.T @ U2_r
            overlap = torch.norm(projection, 'fro').item() / r_min

            return overlap

        elif method == "projection":
            # Average projection score
            delta1 = pair.delta_W1
            delta2 = pair.delta_W2

            # Project delta2 onto delta1's subspace
            proj_score = torch.norm(delta2.T @ delta1, 'fro').item()
            norm_score = torch.norm(delta1, 'fro').item() * torch.norm(delta2, 'fro').item()

            return proj_score / (norm_score + 1e-8)

        else:
            raise ValueError(f"Unknown overlap method: {method}")

    @staticmethod
    def gradient_conflict(
        pair: LoRAPair,
        X: torch.Tensor,
        y: torch.Tensor,
        model: Optional[nn.Module] = None
    ) -> Tuple[float, float]:
        """
        Measure gradient conflict between LoRAs

        gradient_conflict = cos(g_1, g_2)
        gradient_angle = arccos(cos_angle)

        If model is None, uses simple quadratic loss
        """
        if model is None:
            # Simple quadratic loss: L = ||y - (W_base + w_1@B_1@A_1 + w_2@B_2@A_2) @ X||²
            def loss_fn(W):
                return torch.norm(y - W @ X, 'fro') ** 2

        # Compute gradients
        delta_W1 = pair.delta_W1
        delta_W2 = pair.delta_W2

        # Gradient w.r.t. weight for LoRA 1
        grad1 = torch.autograd.functional.jacobian(
            lambda w: loss_fn(w * delta_W1),
            torch.tensor(1.0)
        )

        # Gradient w.r.t. weight for LoRA 2
        grad2 = torch.autograd.functional.jacobian(
            lambda w: loss_fn(w * delta_W2),
            torch.tensor(1.0)
        )

        # Cosine similarity
        cos_angle = torch.cosine_similarity(grad1.unsqueeze(0), grad2.unsqueeze(0)).item()
        angle = np.arccos(np.clip(cos_angle, -1, 1))

        return cos_angle, angle

    @staticmethod
    def performance_degradation(
        pair: LoRAPair,
        X_test: torch.Tensor,
        y_test: torch.Tensor,
        W_base: torch.Tensor
    ) -> Tuple[float, float, float]:
        """
        Measure performance degradation when combining LoRAs

        Returns:
        - perf_lora1: Performance with LoRA 1 alone
        - perf_combined: Performance with combined LoRAs
        - degradation: perf_lora1 - perf_combined
        """
        # Performance with LoRA 1 alone
        W_lora1 = W_base + pair.delta_W1
        pred1 = X_test @ W_lora1.T
        perf_lora1 = -torch.mean((pred1 - y_test) ** 2).item()  # Negative MSE

        # Performance with combined LoRAs
        W_combined = W_base + pair.combined_delta_W(weight1=0.5, weight2=0.5)
        pred_combined = X_test @ W_combined.T
        perf_combined = -torch.mean((pred_combined - y_test) ** 2).item()

        degradation = perf_lora1 - perf_combined

        return perf_lora1, perf_combined, degradation


class InterferencePredictor:
    """
    Predict interference from LoRA parameters

    Can we predict interference before training?
    """

    def __init__(self):
        self.features = []
        self.labels = []

    def extract_features(self, pair: LoRAPair) -> Dict[str, float]:
        """
        Extract features that predict interference

        Features:
        - Rank ratio
        - Weight norm ratio
        - Subspace angle
        - Spectral similarity
        """
        # Rank features
        rank_ratio = min(pair.rank1, pair.rank2) / max(pair.rank1, pair.rank2)

        # Norm features
        norm1 = torch.norm(pair.delta_W1, 'fro').item()
        norm2 = torch.norm(pair.delta_W2, 'fro').item()
        norm_ratio = min(norm1, norm2) / (max(norm1, norm2) + 1e-8)

        # Spectral features
        _, S1, _ = torch.linalg.svd(pair.delta_W1)
        _, S2, _ = torch.linalg.svd(pair.delta_W2)

        # Top singular value ratio
        spectral_ratio = S1[0].item() / (S2[0].item() + 1e-8)

        # Spectral decay similarity
        decay_similarity = np.corrcoef(
            S1.cpu().numpy()[:10],
            S2.cpu().numpy()[:10]
        )[0, 1]

        # Subspace overlap
        calc = InterferenceCalculator()
        overlap = calc.subspace_overlap(pair, method="principal")

        return {
            "rank_ratio": rank_ratio,
            "norm_ratio": norm_ratio,
            "spectral_ratio": spectral_ratio,
            "decay_similarity": decay_similarity,
            "subspace_overlap": overlap
        }

    def train(
        self,
        pairs: List[LoRAPair],
        interference_scores: List[float]
    ):
        """
        Train interference prediction model

        Simple linear model: interference = w^T @ features
        """
        from sklearn.linear_model import Ridge

        # Extract features
        X = []
        for pair in pairs:
            features = self.extract_features(pair)
            X.append(list(features.values()))

        X = np.array(X)
        y = np.array(interference_scores)

        # Train model
        self.model = Ridge(alpha=1.0)
        self.model.fit(X, y)

        # Feature importance
        self.feature_names = list(features.keys())
        self.importance = dict(zip(
            self.feature_names,
            self.model.coef_
        ))

    def predict(self, pair: LoRAPair) -> float:
        """Predict interference for a LoRA pair"""
        features = self.extract_features(pair)
        X = np.array([list(features.values())])
        return self.model.predict(X)[0]


class InterferenceDetector:
    """
    Main class for detecting LoRA interference

    Workflow:
    1. Generate multiple LoRA pairs across domains
    2. Compute interference metrics
    3. Cluster compatible vs incompatible pairs
    4. Train predictor
    5. Validate predictions
    """

    def __init__(
        self,
        base_dim: int = 1024,
        ranks: List[int] = None,
        domains: List[str] = None
    ):
        self.base_dim = base_dim
        self.ranks = ranks or [8, 16, 32, 64]
        self.domains = domains or ["code", "writing", "analysis", "research"]

        # Results storage
        self.pairs: List[LoRAPair] = []
        self.metrics: List[InterferenceMetrics] = []

    def generate_lora_pairs(self, n_pairs_per_combination: int = 5) -> List[LoRAPair]:
        """Generate synthetic LoRA pairs for testing"""
        from .rank_analysis import SyntheticModelGenerator, LoRADecomposer

        pairs = []
        model_gen = SyntheticModelGenerator(self.base_dim)
        W_base = model_gen.generate_base_model()

        # Generate pairs across all domain combinations
        for i, domain1 in enumerate(self.domains):
            for j, domain2 in enumerate(self.domains):
                if i < j:  # Unique pairs only
                    for k in range(n_pairs_per_combination):
                        # Generate expert models
                        W_expert1 = model_gen.generate_expert_weights(
                            W_base, domain1, expertise_strength=0.3
                        )
                        W_expert2 = model_gen.generate_expert_weights(
                            W_base, domain2, expertise_strength=0.3
                        )

                        # Decompose into LoRAs
                        rank = np.random.choice(self.ranks)
                        decomposer = LoRADecomposer(rank)

                        B1, A1 = decomposer.decompose(W_base, W_expert1)
                        B2, A2 = decomposer.decompose(W_base, W_expert2)

                        pair = LoRAPair(
                            B1, A1, B2, A2,
                            name1=f"{domain1}_{k}",
                            name2=f"{domain2}_{k}"
                        )
                        pairs.append(pair)

        self.pairs = pairs
        return pairs

    def compute_all_metrics(
        self,
        n_samples: int = 1000
    ) -> List[InterferenceMetrics]:
        """
        Compute interference metrics for all pairs

        n_samples: Number of samples for gradient/performance tests
        """
        # Generate test data
        X_test = torch.randn(n_samples, self.base_dim)
        W_base = torch.randn(self.base_dim, self.base_dim) * 0.02
        y_test = X_test @ W_base.T + torch.randn(n_samples, self.base_dim) * 0.1

        metrics_list = []

        for pair in self.pairs:
            calc = InterferenceCalculator()

            # Correlation metrics
            weight_corr = calc.weight_correlation(pair)
            subspace_over = calc.subspace_overlap(pair)

            # Gradient conflict
            grad_conflict, grad_angle = calc.gradient_conflict(
                pair, X_test.T, y_test.T
            )

            # Performance degradation
            perf1, perf_combined, degradation = calc.performance_degradation(
                pair, X_test, y_test, W_base
            )

            # Predict compatibility (simple heuristic)
            # Compatible if: low subspace overlap, low gradient conflict
            predicted_compat = 1.0 - 0.5 * subspace_over - 0.5 * abs(grad_conflict)
            actual_compat = perf_combined / (perf1 + 1e-8)

            metrics = InterferenceMetrics(
                lora1_name=pair.name1,
                lora2_name=pair.name2,
                weight_correlation=weight_corr,
                subspace_overlap=subspace_over,
                gradient_conflict=grad_conflict,
                gradient_angle=grad_angle,
                performance_degradation=degradation,
                combined_performance=perf_combined,
                predicted_compatibility=predicted_compat,
                actual_compatibility=actual_compat
            )

            metrics_list.append(metrics)

        self.metrics = metrics_list
        return metrics_list

    def cluster_compatibility(
        self,
        n_clusters: int = 3
    ) -> Dict[str, List[str]]:
        """
        Cluster LoRA pairs by compatibility

        Returns clusters: {cluster_label: [pair_names]}
        """
        # Extract features for clustering
        features = []
        pair_names = []

        for m in self.metrics:
            feat = [
                m.weight_correlation,
                m.subspace_overlap,
                m.gradient_conflict,
                m.performance_degradation
            ]
            features.append(feat)
            pair_names.append(f"{m.lora1_name}+{m.lora2_name}")

        features = np.array(features)

        # Normalize
        features = (features - features.mean(0)) / (features.std(0) + 1e-8)

        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features)

        # Organize results
        clusters = {f"cluster_{i}": [] for i in range(n_clusters)}
        for name, label in zip(pair_names, labels):
            clusters[f"cluster_{label}"].append(name)

        return clusters

    def train_predictor(self) -> InterferencePredictor:
        """Train interference prediction model"""
        predictor = InterferencePredictor()

        # Prepare training data
        interference_scores = [
            1.0 - m.performance_degradation for m in self.metrics
        ]

        predictor.train(self.pairs, interference_scores)

        return predictor

    def visualize_interference_matrix(
        self,
        output_path: Optional[Path] = None
    ):
        """Visualize interference heatmap"""
        # Create matrix of pairwise interference
        n_pairs = len(self.pairs)
        interference_matrix = np.zeros((n_pairs, n_pairs))

        for i, m1 in enumerate(self.metrics):
            for j, m2 in enumerate(self.metrics):
                # Use subspace_overlap as interference metric
                if i == j:
                    interference_matrix[i, j] = 1.0
                else:
                    # Combine multiple metrics
                    interference = (
                        0.3 * abs(m1.weight_correlation) +
                        0.4 * m1.subspace_overlap +
                        0.3 * abs(m1.gradient_conflict)
                    )
                    interference_matrix[i, j] = interference

        # Plot
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            interference_matrix,
            cmap='RdYlGn_r',
            xticklabels=[m.lora1_name[:15] for m in self.metrics],
            yticklabels=[m.lora1_name[:15] for m in self.metrics],
            cbar_kws={'label': 'Interference Score'}
        )
        plt.title('LoRA Pair Interference Matrix', fontsize=16)
        plt.xlabel('LoRA Pairs', fontsize=12)
        plt.ylabel('LoRA Pairs', fontsize=12)
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

    def run_full_analysis(
        self,
        output_dir: Path = Path("./simulations/lora/results")
    ) -> Dict:
        """
        Run complete interference analysis

        Returns comprehensive results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("LoRA Interference Detection Analysis")
        print("=" * 60)

        # 1. Generate pairs
        print("\nGenerating LoRA pairs...")
        self.generate_lora_pairs(n_pairs_per_combination=3)
        print(f"  Generated {len(self.pairs)} pairs")

        # 2. Compute metrics
        print("\nComputing interference metrics...")
        self.compute_all_metrics()
        print(f"  Computed metrics for {len(self.metrics)} pairs")

        # 3. Cluster compatibility
        print("\nClustering compatible pairs...")
        clusters = self.cluster_compatibility(n_clusters=3)
        for cluster_name, pairs_in_cluster in clusters.items():
            print(f"  {cluster_name}: {len(pairs_in_cluster)} pairs")

        # 4. Train predictor
        print("\nTraining interference predictor...")
        predictor = self.train_predictor()
        print(f"  Feature importances:")
        for feat, imp in predictor.importance.items():
            print(f"    {feat}: {imp:.4f}")

        # 5. Visualize
        print("\nGenerating visualizations...")
        self.visualize_interference_matrix(
            output_dir / "interference_matrix.png"
        )
        print(f"  Saved: {output_dir / 'interference_matrix.png'}")

        # 6. Save results
        results = {
            "clusters": clusters,
            "feature_importance": predictor.importance,
            "metrics_summary": {
                "mean_weight_correlation": float(np.mean([
                    m.weight_correlation for m in self.metrics
                ])),
                "mean_subspace_overlap": float(np.mean([
                    m.subspace_overlap for m in self.metrics
                ])),
                "mean_gradient_conflict": float(np.mean([
                    m.gradient_conflict for m in self.metrics
                ])),
                "mean_performance_degradation": float(np.mean([
                    m.performance_degradation for m in self.metrics
                ])),
            },
            "detailed_metrics": [
                {
                    "pair": f"{m.lora1_name}+{m.lora2_name}",
                    "weight_correlation": m.weight_correlation,
                    "subspace_overlap": m.subspace_overlap,
                    "gradient_conflict": m.gradient_conflict,
                    "performance_degradation": m.performance_degradation,
                }
                for m in self.metrics
            ]
        }

        results_path = output_dir / "interference_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved results: {results_path}")

        return results


def main():
    """Run interference detection analysis"""
    detector = InterferenceDetector(
        base_dim=512,  # Smaller for testing
        ranks=[8, 16, 32],
        domains=["code", "writing", "analysis"]
    )

    results = detector.run_full_analysis()

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
