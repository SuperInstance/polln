"""
Pattern Discovery Toolkit for Emergent Phenomena

Uses machine learning to automatically identify and characterize patterns
in high-dimensional simulation data. Clusters behaviors, detects anomalies,
and extracts computational signatures of emergence.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime

# ML imports
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy.spatial.distance import pdist, squareform
from scipy import stats
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')


@dataclass
class Pattern:
    """Discovered pattern"""
    pattern_id: str
    pattern_type: str  # cluster, anomaly, trend, cycle, etc.
    description: str
    features: Dict[str, float]
    instances: List[int]  # Indices of data points exhibiting this pattern
    signature: Dict[str, Any]  # Computational signature
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehaviorCluster:
    """Cluster of similar behaviors"""
    cluster_id: int
    size: int
    centroid: np.ndarray
    behavior_signature: Dict[str, float]
    parameter_profile: Dict[str, Tuple[float, float]]  # (mean, std)
    emergence_metrics: Dict[str, float]
    stability: float  # How consistent the cluster is
    novelty_score: float  # How novel this behavior is


class PatternDiscoveryEngine:
    """
    Advanced pattern discovery for emergent phenomena

    Automatically identifies patterns, clusters behaviors, detects anomalies,
    and extracts computational signatures from high-dimensional simulation data.
    """

    def __init__(self, output_dir: str = "./pattern_discovery_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.discovered_patterns = []
        self.behavior_clusters = []
        self.anomalies = []

        # Preprocessing
        self.scaler = StandardScaler()
        self.is_fitted = False

    def discover_patterns(self,
                         simulation_data: List[Dict[str, Any]],
                         methods: Optional[List[str]] = None) -> List[Pattern]:
        """
        Discover patterns in simulation data

        Args:
            simulation_data: List of simulation results with configs and metrics
            methods: Discovery methods to use (cluster, anomaly, trend, cycle, all)

        Returns:
            List of discovered patterns
        """
        print(f"🔍 Discovering patterns in {len(simulation_data)} simulations")

        if methods is None:
            methods = ["cluster", "anomaly", "trend", "cycle"]

        # Extract feature matrix
        features, feature_names, configs_list = self._extract_features(simulation_data)

        # Normalize features
        features_normalized = self.scaler.fit_transform(features)
        self.is_fitted = True

        patterns = []

        # Apply different discovery methods
        if "cluster" in methods:
            cluster_patterns = self._discover_clusters(features_normalized, feature_names, configs_list)
            patterns.extend(cluster_patterns)

        if "anomaly" in methods:
            anomaly_patterns = self._discover_anomalies(features_normalized, feature_names, configs_list)
            patterns.extend(anomaly_patterns)

        if "trend" in methods:
            trend_patterns = self._discover_trends(features_normalized, feature_names, configs_list)
            patterns.extend(trend_patterns)

        if "cycle" in methods:
            cycle_patterns = self._discover_cycles(features_normalized, feature_names, configs_list)
            patterns.extend(cycle_patterns)

        self.discovered_patterns = patterns

        # Save patterns
        self._save_patterns(patterns)

        return patterns

    def _extract_features(self, simulation_data: List[Dict]) -> Tuple[np.ndarray, List[str], List[Dict]]:
        """Extract feature matrix from simulation data"""
        features_list = []
        configs_list = []

        for sim in simulation_data:
            # Extract metrics
            feature_dict = {}
            if "metrics" in sim:
                feature_dict.update(sim["metrics"])

            # Extract config features
            if "config" in sim:
                config = sim["config"]
                for key, value in config.items():
                    if isinstance(value, (int, float)):
                        feature_dict[f"config_{key}"] = value

            # Extract derived features
            if "raw_result" in sim:
                derived = self._compute_derived_features(sim["raw_result"])
                feature_dict.update(derived)

            features_list.append(feature_dict)
            configs_list.append(sim.get("config", {}))

        # Convert to matrix
        feature_names = sorted(set().union(*[f.keys() for f in features_list]))
        features = np.array([[f.get(name, 0.0) for name in feature_names]
                            for f in features_list])

        return features, feature_names, configs_list

    def _compute_derived_features(self, raw_result: Dict) -> Dict[str, float]:
        """Compute derived features from raw simulation results"""
        derived = {}

        # Example: ratios, interactions
        if "agent_behavior" in raw_result:
            ab = raw_result["agent_behavior"]
            if "coordination" in ab and "specialization" in ab:
                derived["coordination_specialization_ratio"] = (
                    ab["coordination"] / (ab["specialization"] + 1e-6)
                )

        if "collective_dynamics" in raw_result:
            cd = raw_result["collective_dynamics"]
            if "synchronization" in cd and "criticality" in cd:
                derived["sync_criticality_product"] = cd["synchronization"] * cd["criticality"]

        if "information_flow" in raw_result:
            info = raw_result["information_flow"]
            if "entropy" in info and "mutual_information" in info:
                derived["info_integration"] = info["entropy"] * info["mutual_information"]

        return derived

    def _discover_clusters(self, features: np.ndarray, feature_names: List[str],
                          configs_list: List[Dict]) -> List[Pattern]:
        """Discover behavioral clusters using multiple clustering algorithms"""
        print("  🔄 Discovering behavioral clusters...")
        patterns = []

        # Try different clustering algorithms
        clustering_methods = [
            ("dbscan", DBSCAN(eps=0.5, min_samples=5)),
            ("hierarchical", AgglomerativeClustering(n_clusters=5, linkage='ward')),
            ("kmeans", KMeans(n_clusters=5, random_state=42, n_init=10))
        ]

        for method_name, clustering in clustering_methods:
            try:
                # Fit clustering
                if method_name == "dbscan":
                    # DBSCAN doesn't need predict
                    clusters = clustering.fit_predict(features)
                else:
                    clusters = clustering.fit_predict(features)

                # Analyze each cluster
                unique_clusters = np.unique(clusters)
                unique_clusters = unique_clusters[unique_clusters >= 0]  # Remove noise for DBSCAN

                for cluster_id in unique_clusters:
                    cluster_mask = clusters == cluster_id
                    cluster_indices = np.where(cluster_mask)[0]

                    if len(cluster_indices) < 3:  # Skip tiny clusters
                        continue

                    # Extract cluster characteristics
                    cluster_features = features[cluster_mask]
                    cluster_centroid = cluster_features.mean(axis=0)

                    # Parameter profile
                    cluster_configs = [configs_list[i] for i in cluster_indices]
                    param_profile = self._compute_parameter_profile(cluster_configs)

                    # Emergence metrics
                    emergence_metrics = self._compute_cluster_emergence_metrics(cluster_features, feature_names)

                    # Stability (inverse of variance within cluster)
                    stability = 1.0 / (1.0 + cluster_features.std(axis=0).mean())

                    # Create pattern
                    pattern = Pattern(
                        pattern_id=f"cluster_{method_name}_{cluster_id}",
                        pattern_type="behavioral_cluster",
                        description=f"Cluster of {len(cluster_indices)} similar behaviors",
                        features=dict(zip(feature_names, cluster_centroid)),
                        instances=cluster_indices.tolist(),
                        signature={
                            "centroid": cluster_centroid.tolist(),
                            "param_profile": param_profile,
                            "emergence_metrics": emergence_metrics,
                            "stability": stability
                        },
                        confidence=stability,
                        metadata={
                            "method": method_name,
                            "size": len(cluster_indices),
                            "cluster_id": cluster_id
                        }
                    )

                    patterns.append(pattern)
                    self.behavior_clusters.append(BehaviorCluster(
                        cluster_id=cluster_id,
                        size=len(cluster_indices),
                        centroid=cluster_centroid,
                        behavior_signature=dict(zip(feature_names, cluster_centroid)),
                        parameter_profile=param_profile,
                        emergence_metrics=emergence_metrics,
                        stability=stability,
                        novelty_score=0.0  # To be computed
                    ))

                    print(f"    📊 Cluster {cluster_id} ({method_name}): {len(cluster_indices)} instances")

            except Exception as e:
                print(f"    ⚠️  {method_name} clustering failed: {e}")
                continue

        return patterns

    def _discover_anomalies(self, features: np.ndarray, feature_names: List[str],
                           configs_list: List[Dict]) -> List[Pattern]:
        """Discover anomalous behaviors"""
        print("  🎯 Discovering anomalies...")
        patterns = []

        # Try different anomaly detection methods
        anomaly_methods = [
            ("isolation_forest", IsolationForest(contamination=0.1, random_state=42)),
            ("lof", LocalOutlierFactor(n_neighbors=20, contamination=0.1))
        ]

        for method_name, detector in anomaly_methods:
            try:
                # Fit detector
                if method_name == "lof":
                    # LOF doesn't have fit_predict for new data
                    predictions = detector.fit_predict(features)
                else:
                    predictions = detector.fit_predict(features)

                # Anomalies are labeled -1
                anomaly_mask = predictions == -1
                anomaly_indices = np.where(anomaly_mask)[0]

                if len(anomaly_indices) == 0:
                    continue

                print(f"    🚨 {method_name}: {len(anomaly_indices)} anomalies found")

                # Analyze anomalies
                for idx in anomaly_indices:
                    anomaly_features = features[idx]
                    anomaly_config = configs_list[idx]

                    # Compute anomaly score (distance from nearest neighbors)
                    distances = np.linalg.norm(features - anomaly_features, axis=1)
                    distances = np.sort(distances)[1:6]  # 5 nearest neighbors (excluding self)
                    anomaly_score = distances.mean()

                    pattern = Pattern(
                        pattern_id=f"anomaly_{method_name}_{idx}",
                        pattern_type="anomaly",
                        description=f"Anomalous behavior at index {idx}",
                        features=dict(zip(feature_names, anomaly_features)),
                        instances=[idx],
                        signature={
                            "anomaly_score": anomaly_score,
                            "nearest_neighbor_distance": distances[0],
                            "config": anomaly_config
                        },
                        confidence=min(1.0, anomaly_score),
                        metadata={
                            "method": method_name,
                            "index": idx
                        }
                    )

                    patterns.append(pattern)
                    self.anomalies.append(pattern)

            except Exception as e:
                print(f"    ⚠️  {method_name} anomaly detection failed: {e}")
                continue

        return patterns

    def _discover_trends(self, features: np.ndarray, feature_names: List[str],
                        configs_list: List[Dict]) -> List[Pattern]:
        """Discover trends and relationships"""
        print("  📈 Discovering trends...")
        patterns = []

        # Find correlations between features
        n_features = features.shape[1]
        correlation_matrix = np.corrcoef(features.T)

        # Find strong correlations
        strong_corr_threshold = 0.7
        for i in range(n_features):
            for j in range(i+1, n_features):
                corr = correlation_matrix[i, j]
                if abs(corr) > strong_corr_threshold:
                    pattern = Pattern(
                        pattern_id=f"trend_correlation_{i}_{j}",
                        pattern_type="correlation",
                        description=f"Strong {'positive' if corr > 0 else 'negative'} correlation between {feature_names[i]} and {feature_names[j]}",
                        features={"correlation": corr},
                        instances=[],
                        signature={"feature1": feature_names[i], "feature2": feature_names[j], "correlation": corr},
                        confidence=abs(corr)
                    )
                    patterns.append(pattern)

        # Find monotonic trends (if data has temporal or parameter ordering)
        # This would require ordered data, which we don't have
        # Skip for now

        return patterns

    def _discover_cycles(self, features: np.ndarray, feature_names: List[str],
                        configs_list: List[Dict]) -> List[Pattern]:
        """Discover cyclical patterns"""
        print("  🔄 Discovering cycles...")
        patterns = []

        # Look for periodicity in features (if ordered)
        # This would require time-series data
        # Skip for now

        return patterns

    def _compute_parameter_profile(self, configs: List[Dict]) -> Dict[str, Tuple[float, float]]:
        """Compute parameter profile for a cluster"""
        if not configs:
            return {}

        param_profile = {}
        for param in configs[0].keys():
            values = [c.get(param, 0.0) for c in configs if param in c]
            if values:
                param_profile[param] = (float(np.mean(values)), float(np.std(values)))

        return param_profile

    def _compute_cluster_emergence_metrics(self, cluster_features: np.ndarray,
                                          feature_names: List[str]) -> Dict[str, float]:
        """Compute emergence metrics for a cluster"""
        metrics = {}

        # Cluster coherence (inverse of within-cluster variance)
        metrics["coherence"] = 1.0 / (1.0 + cluster_features.std(axis=0).mean())

        # Cluster separation (distance from global centroid)
        # This would require global centroid, skip for now

        return metrics

    def reduce_dimensions(self,
                        features: np.ndarray,
                        method: str = "umap",
                        n_components: int = 2) -> np.ndarray:
        """
        Dimensionality reduction for visualization

        Args:
            features: High-dimensional feature matrix
            method: Reduction method (pca, tsne, umap)
            n_components: Number of components

        Returns:
            Low-dimensional embedding
        """
        print(f"  📉 Reducing dimensions using {method.upper()}...")

        if method == "pca":
            reducer = PCA(n_components=n_components, random_state=42)
            embedding = reducer.fit_transform(features)
            explained_variance = reducer.explained_variance_ratio_.sum()
            print(f"    Explained variance: {explained_variance:.2%}")

        elif method == "tsne":
            reducer = TSNE(n_components=n_components, random_state=42, perplexity=min(30, len(features)//4))
            embedding = reducer.fit_transform(features)

        elif method == "umap":
            reducer = umap.UMAP(n_components=n_components, random_state=42)
            embedding = reducer.fit_transform(features)

        else:
            raise ValueError(f"Unknown reduction method: {method}")

        return embedding

    def compute_phase_space(self,
                          simulation_data: List[Dict[str, Any]],
                          metrics: List[str]) -> Dict[str, Any]:
        """
        Construct phase space for analyzing system dynamics

        Args:
            simulation_data: Simulation results
            metrics: Metrics to use as phase space dimensions

        Returns:
            Phase space analysis results
        """
        print("  🌀 Computing phase space...")

        # Extract trajectories
        trajectories = []
        for sim in simulation_data:
            if "metrics" in sim:
                point = [sim["metrics"].get(m, 0.0) for m in metrics]
                trajectories.append(point)

        trajectories = np.array(trajectories)

        # Compute phase space properties
        phase_space = {
            "dimensions": metrics,
            "n_points": len(trajectories),
            "bounds": {m: (trajectories[:, i].min(), trajectories[:, i].max())
                      for i, m in enumerate(metrics)},
            "centroids": trajectories.mean(axis=0).tolist(),
            "covariance": np.cov(trajectories.T).tolist()
        }

        # Detect attractors (dense regions)
        try:
            from sklearn.cluster import DBSCAN
            clustering = DBSCAN(eps=0.3, min_samples=5).fit(trajectories)
            n_attractors = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
            phase_space["n_attractors"] = n_attractors
        except:
            phase_space["n_attractors"] = 0

        return phase_space

    def detect_critical_transitions(self,
                                   simulation_data: List[Dict[str, Any]],
                                   metric: str) -> List[Dict[str, Any]]:
        """
        Detect critical phase transitions in time series data

        Args:
            simulation_data: Time-series simulation results
            metric: Metric to analyze for transitions

        Returns:
            List of detected transitions
        """
        print(f"  ⚡ Detecting critical transitions in {metric}...")

        # Extract time series
        time_series = []
        for sim in simulation_data:
            if "metrics" in sim and metric in sim["metrics"]:
                time_series.append(sim["metrics"][metric])

        if len(time_series) < 10:
            return []

        time_series = np.array(time_series)

        # Detect transitions using variance change detection
        transitions = []
        window_size = max(5, len(time_series) // 10)

        for i in range(window_size, len(time_series) - window_size):
            window_before = time_series[i-window_size:i]
            window_after = time_series[i:i+window_size]

            var_before = window_before.var()
            var_after = window_after.var()

            # Significant variance change indicates potential transition
            if abs(var_after - var_before) / (var_before + 1e-6) > 0.5:
                transitions.append({
                    "index": i,
                    "value": time_series[i],
                    "variance_change": var_after - var_before,
                    "type": "increase" if var_after > var_before else "decrease"
                })

        # Merge nearby transitions
        if transitions:
            merged = [transitions[0]]
            for t in transitions[1:]:
                if t["index"] - merged[-1]["index"] > window_size:
                    merged.append(t)
            transitions = merged

        print(f"    Found {len(transitions)} potential transitions")

        return transitions

    def compute_information_theoretic_measures(self,
                                              simulation_data: List[Dict[str, Any]],
                                              metrics: List[str]) -> Dict[str, float]:
        """
        Compute information-theoretic measures of emergence

        Args:
            simulation_data: Simulation results
            metrics: Metrics to analyze

        Returns:
            Information measures (entropy, mutual info, etc.)
        """
        print("  ℹ️  Computing information-theoretic measures...")

        # Extract joint distribution
        data_matrix = []
        for sim in simulation_data:
            if "metrics" in sim:
                row = [sim["metrics"].get(m, 0.0) for m in metrics]
                data_matrix.append(row)

        data_matrix = np.array(data_matrix)

        # Discretize for entropy computation
        n_bins = 10
        from scipy.stats import entropy as scipy_entropy

        measures = {}

        # Individual entropies
        for i, metric in enumerate(metrics):
            hist, _ = np.histogram(data_matrix[:, i], bins=n_bins, density=True)
            hist = hist + 1e-10  # Avoid log(0)
            measures[f"{metric}_entropy"] = scipy_entropy(hist)

        # Mutual information between metric pairs
        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i < j:
                    # Compute mutual information
                    hist_2d, _, _ = np.histogram2d(data_matrix[:, i], data_matrix[:, j], bins=n_bins)
                    pxy = hist_2d / hist_2d.sum()
                    px = pxy.sum(axis=1)
                    py = pxy.sum(axis=0)

                    mi = 0.0
                    for ix in range(n_bins):
                        for iy in range(n_bins):
                            if pxy[ix, iy] > 0:
                                mi += pxy[ix, iy] * np.log(pxy[ix, iy] / (px[ix] * py[iy] + 1e-10))

                    measures[f"{metric1}_{metric2}_mutual_info"] = mi

        return measures

    def _save_patterns(self, patterns: List[Pattern]) -> None:
        """Save discovered patterns to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"patterns_{timestamp}.json"

        # Convert to serializable format
        patterns_data = []
        for p in patterns:
            pattern_dict = {
                "pattern_id": p.pattern_id,
                "pattern_type": p.pattern_type,
                "description": p.description,
                "features": p.features,
                "instances": p.instances,
                "signature": p.signature,
                "confidence": p.confidence,
                "metadata": p.metadata
            }
            patterns_data.append(pattern_dict)

        with open(filename, 'w') as f:
            json.dump(patterns_data, f, indent=2, default=str)

        print(f"  💾 Patterns saved to {filename}")

    def generate_report(self) -> str:
        """Generate comprehensive pattern discovery report"""
        report = []
        report.append("=" * 80)
        report.append("PATTERN DISCOVERY REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total patterns discovered: {len(self.discovered_patterns)}")
        report.append(f"Behavioral clusters: {len(self.behavior_clusters)}")
        report.append(f"Anomalies: {len(self.anomalies)}")
        report.append("")

        # Pattern types
        pattern_types = {}
        for p in self.discovered_patterns:
            pattern_types[p.pattern_type] = pattern_types.get(p.pattern_type, 0) + 1

        report.append("PATTERN TYPES")
        report.append("-" * 80)
        for ptype, count in pattern_types.items():
            report.append(f"  {ptype}: {count}")
        report.append("")

        # Top clusters by stability
        if self.behavior_clusters:
            report.append("MOST STABLE BEHAVIORAL CLUSTERS")
            report.append("-" * 80)
            top_clusters = sorted(self.behavior_clusters, key=lambda x: x.stability, reverse=True)[:5]
            for cluster in top_clusters:
                report.append(f"  Cluster {cluster.cluster_id}:")
                report.append(f"    Size: {cluster.size}")
                report.append(f"    Stability: {cluster.stability:.3f}")
                report.append(f"    Emergence metrics: {cluster.emergence_metrics}")
            report.append("")

        # High-confidence anomalies
        if self.anomalies:
            report.append("HIGH-CONFIDENCE ANOMALIES")
            report.append("-" * 80)
            top_anomalies = sorted(self.anomalies, key=lambda x: x.confidence, reverse=True)[:5]
            for anomaly in top_anomalies:
                report.append(f"  {anomaly.pattern_id}:")
                report.append(f"    Confidence: {anomaly.confidence:.3f}")
                report.append(f"    Description: {anomaly.description}")
            report.append("")

        return "\n".join(report)


if __name__ == "__main__":
    # Test with mock data
    print("Testing Pattern Discovery Engine")

    # Generate mock simulation data
    n_simulations = 100
    mock_data = []
    for i in range(n_simulations):
        sim = {
            "config": {
                "temperature": np.random.uniform(0.1, 2.0),
                "learning_rate": np.random.uniform(0.001, 0.1),
                "n_agents": np.random.randint(10, 100)
            },
            "metrics": {
                "collective_intelligence": np.random.random(),
                "criticality": np.random.random(),
                "information_integration": np.random.random()
            }
        }
        mock_data.append(sim)

    # Create engine and discover patterns
    engine = PatternDiscoveryEngine(output_dir="./test_pattern_results")
    patterns = engine.discover_patterns(mock_data, methods=["cluster", "anomaly"])

    # Generate report
    report = engine.generate_report()
    print("\n" + report)
