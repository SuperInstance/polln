"""
Emergence Taxonomy System

Classifies and categorizes emergent phenomena into a structured taxonomy.
Identifies similarities between phenomena and assesses novelty based on
existing classifications.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


@dataclass
class TaxonomyNode:
    """Node in emergence taxonomy"""
    node_id: str
    name: str
    description: str
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    phenomena_ids: List[str] = field(default_factory=list)
    features: Dict[str, float] = field(default_factory=dict)
    signatures: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Phenomenon:
    """Emergent phenomenon classified in taxonomy"""
    phenomenon_id: str
    name: str
    description: str
    taxonomy_path: List[str]  # Path from root to leaf
    features: Dict[str, float]
    computational_signature: Dict[str, Any]
    mechanism_hypotheses: List[str]
    similar_phenomena: List[str] = field(default_factory=list)
    novelty_score: float = 0.0
    universality_class: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UniversalityClass:
    """Universality class (phenomena sharing same critical exponents/behavior)"""
    class_id: str
    name: str
    description: str
    critical_exponents: Dict[str, float]
    scaling_laws: List[str]
    phenomena: List[str]
    representative_systems: List[str]


class EmergenceTaxonomy:
    """
    Comprehensive taxonomy of emergent phenomena

    Classifies phenomena into hierarchical categories, identifies
    universality classes, and assesses novelty.
    """

    def __init__(self, output_dir: str = "./taxonomy_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.taxonomy_tree: Dict[str, TaxonomyNode] = {}
        self.phenomena: Dict[str, Phenomenon] = {}
        self.universality_classes: Dict[str, UniversalityClass] = {}

        # Initialize with standard taxonomy
        self._initialize_base_taxonomy()

    def _initialize_base_taxonomy(self):
        """Initialize base taxonomy structure for emergence"""
        # Root
        root = TaxonomyNode(
            node_id="root",
            name="Emergent Phenomena",
            description="Root of all emergent phenomena"
        )
        self.taxonomy_tree["root"] = root

        # Major categories
        categories = [
            ("collective", "Collective Behavior", "Coordinated behavior of multiple agents"),
            ("structural", "Structural Emergence", "Emergence of organized structure"),
            ("functional", "Functional Emergence", "Emergence of new functionalities"),
            ("computational", "Computational Emergence", "Emergence of computational capabilities"),
            ("temporal", "Temporal Emergence", "Emergent temporal patterns and dynamics")
        ]

        for cat_id, name, desc in categories:
            node = TaxonomyNode(
                node_id=cat_id,
                name=name,
                description=desc,
                parent_id="root"
            )
            self.taxonomy_tree[cat_id] = node
            root.children_ids.append(cat_id)

        # Collective behavior subcategories
        collective_subcats = [
            ("synchronization", "Synchronization", "Coordinated timing or state"),
            ("coordination", "Coordination", "Coherent action without central control"),
            ("consensus", "Consensus", "Agreement among agents"),
            ("flocking", "Flocking", "Coordinated movement"),
            ("swarming", "Swarming", "Collective decision making")
        ]

        for sub_id, name, desc in collective_subcats:
            node = TaxonomyNode(
                node_id=f"collective.{sub_id}",
                name=name,
                description=desc,
                parent_id="collective"
            )
            self.taxonomy_tree[node.node_id] = node
            self.taxonomy_tree["collective"].children_ids.append(node.node_id)

        # Structural emergence subcategories
        structural_subcats = [
            ("network", "Network Formation", "Emergence of network structure"),
            ("pattern", "Pattern Formation", "Spatiotemporal patterns"),
            ("hierarchy", "Hierarchy", "Emergent hierarchical organization"),
            ("modularity", "Modularity", "Emergence of modules or compartments")
        ]

        for sub_id, name, desc in structural_subcats:
            node = TaxonomyNode(
                node_id=f"structural.{sub_id}",
                name=name,
                description=desc,
                parent_id="structural"
            )
            self.taxonomy_tree[node.node_id] = node
            self.taxonomy_tree["structural"].children_ids.append(node.node_id)

        # Add more subcategories for other major categories...
        phase_node = TaxonomyNode(
            node_id="temporal.phase_transition",
            name="Phase Transition",
            description="Sharp transition between regimes",
            parent_id="temporal"
        )
        self.taxonomy_tree[phase_node.node_id] = phase_node
        self.taxonomy_tree["temporal"].children_ids.append(phase_node.node_id)

        criticality_node = TaxonomyNode(
            node_id="temporal.criticality",
            name="Criticality",
            description="Operation at critical point",
            parent_id="temporal"
        )
        self.taxonomy_tree[criticality_node.node_id] = criticality_node
        self.taxonomy_tree["temporal"].children_ids.append(criticality_node.node_id)

    def classify_phenomenon(self,
                           phenomenon_data: Dict[str, Any],
                           phenomenon_id: Optional[str] = None) -> Phenomenon:
        """
        Classify a phenomenon into the taxonomy

        Args:
            phenomenon_data: Data about the phenomenon
            phenomenon_id: Optional ID for the phenomenon

        Returns:
            Classified phenomenon object
        """
        if phenomenon_id is None:
            phenomenon_id = f"phenomenon_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"🏷️  Classifying phenomenon {phenomenon_id}...")

        # Extract features
        features = self._extract_classification_features(phenomenon_data)

        # Find best matching taxon
        taxonomy_path = self._find_taxonomic_path(features, phenomenon_data)

        # Create phenomenon object
        phenomenon = Phenomenon(
            phenomenon_id=phenomenon_id,
            name=phenomenon_data.get("name", "Unnamed Phenomenon"),
            description=phenomenon_data.get("description", ""),
            taxonomy_path=taxonomy_path,
            features=features,
            computational_signature=phenomenon_data.get("signature", {}),
            mechanism_hypotheses=phenomenon_data.get("mechanisms", []),
            novelty_score=0.0,  # Will be computed
            metadata=phenomenon_data.get("metadata", {})
        )

        # Add to taxonomy
        leaf_node_id = taxonomy_path[-1]
        if leaf_node_id in self.taxonomy_tree:
            self.taxonomy_tree[leaf_node_id].phenomena_ids.append(phenomenon_id)

        self.phenomena[phenomenon_id] = phenomenon

        # Compute novelty
        phenomenon.novelty_score = self._compute_novelty_score(phenomenon)

        # Find similar phenomena
        phenomenon.similar_phenomena = self._find_similar_phenomena(phenomenon)

        # Check for universality class
        phenomenon.universality_class = self._check_universality_class(phenomenon)

        print(f"  ✅ Classified as: {' -> '.join([self.taxonomy_tree[n].name for n in taxonomy_path])}")
        print(f"  📊 Novelty score: {phenomenon.novelty_score:.3f}")

        # Save
        self._save_taxonomy()

        return phenomenon

    def _extract_classification_features(self, phenomenon_data: Dict) -> Dict[str, float]:
        """Extract features for classification"""
        features = {}

        # Temporal features
        features["temporal"] = self._has_characteristic(phenomenon_data, [
            "oscillation", "cycle", "period", "phase", "transition", "dynamics"
        ])

        # Spatial features
        features["spatial"] = self._has_characteristic(phenomenon_data, [
            "pattern", "wave", "front", "cluster", "gradient", "position"
        ])

        # Network features
        features["network"] = self._has_characteristic(phenomenon_data, [
            "connection", "link", "graph", "topology", "path", "component"
        ])

        # Collective features
        features["collective"] = self._has_characteristic(phenomenon_data, [
            "coordination", "synchronization", "consensus", "flocking", "swarm", "together"
        ])

        # Information features
        features["informational"] = self._has_characteristic(phenomenon_data, [
            "information", "entropy", "communication", "signal", "message"
        ])

        # Critical features
        features["critical"] = self._has_characteristic(phenomenon_data, [
            "critical", "threshold", "transition", "bifurcation", "tipping"
        ])

        # Self-organization
        features["self_organized"] = self._has_characteristic(phenomenon_data, [
            "self-organize", "spontaneous", "autonomous", "decentralized"
        ])

        # Add metric features if available
        if "metrics" in phenomenon_data:
            metrics = phenomenon_data["metrics"]
            features["coordination_level"] = metrics.get("coordination", 0.0)
            features["synchronization_level"] = metrics.get("synchronization", 0.0)
            features["complexity"] = metrics.get("complexity", 0.0)
            features["criticality"] = metrics.get("criticality", 0.0)

        return features

    def _has_characteristic(self, data: Dict, keywords: List[str]) -> float:
        """Check if data has characteristic keywords"""
        text = str(data).lower()
        score = sum(1 for kw in keywords if kw.lower() in text) / len(keywords)
        return score

    def _find_taxonomic_path(self, features: Dict[str, float],
                            phenomenon_data: Dict) -> List[str]:
        """Find best matching path through taxonomy"""
        # Start at root
        current_node = "root"
        path = [current_node]

        # Greedy descent through taxonomy
        while True:
            children = self.taxonomy_tree[current_node].children_ids

            if not children:
                break

            # Score each child
            scores = []
            for child_id in children:
                child_node = self.taxonomy_tree[child_id]
                score = self._compute_node_match(features, phenomenon_data, child_node)
                scores.append((child_id, score))

            # Select best child if score is above threshold
            best_child, best_score = max(scores, key=lambda x: x[1])

            if best_score > 0.3:  # Threshold for classification
                path.append(best_child)
                current_node = best_child
            else:
                break

        return path

    def _compute_node_match(self, features: Dict[str, float],
                           phenomenon_data: Dict,
                           node: TaxonomyNode) -> float:
        """Compute match score between phenomenon and taxonomy node"""
        # Keyword matching
        node_text = (node.name + " " + node.description).lower()
        phenomenon_text = str(phenomenon_data).lower()

        # Extract keywords from node
        keywords = re.findall(r'\b\w+\b', node_text)
        keyword_score = sum(1 for kw in keywords if kw in phenomenon_text) / max(1, len(keywords))

        # Feature matching
        feature_score = 0.0
        if "collective" in node.name.lower():
            feature_score += features.get("collective", 0.0)
        if "temporal" in node.name.lower() or "phase" in node.name.lower():
            feature_score += features.get("temporal", 0.0)
        if "structural" in node.name.lower() or "network" in node.name.lower():
            feature_score += features.get("network", 0.0) + features.get("spatial", 0.0)
        if "critical" in node.name.lower():
            feature_score += features.get("critical", 0.0)

        # Combine scores
        combined_score = 0.5 * keyword_score + 0.5 * feature_score

        return combined_score

    def _compute_novelty_score(self, phenomenon: Phenomenon) -> float:
        """Compute novelty score based on similarity to existing phenomena"""
        if len(self.phenomena) == 0:
            return 1.0

        # Find most similar existing phenomenon
        max_similarity = 0.0

        for other_id, other in self.phenomena.items():
            if other_id == phenomenon.phenomenon_id:
                continue

            similarity = self._compute_phenomenon_similarity(phenomenon, other)
            max_similarity = max(max_similarity, similarity)

        # Novelty is inverse of maximum similarity
        novelty = 1.0 - max_similarity
        return novelty

    def _compute_phenomenon_similarity(self, p1: Phenomenon, p2: Phenomenon) -> float:
        """Compute similarity between two phenomena"""
        # Feature similarity
        features1 = np.array(list(p1.features.values()))
        features2 = np.array(list(p2.features.values()))

        # Pad to same length
        if len(features1) != len(features2):
            max_len = max(len(features1), len(features2))
            features1 = np.pad(features1, (0, max_len - len(features1)))
            features2 = np.pad(features2, (0, max_len - len(features2)))

        feature_sim = 1.0 - (np.abs(features1 - features2).mean() / (features1.mean() + features2.mean() + 1e-6))

        # Taxonomic path similarity
        path1_set = set(p1.taxonomy_path)
        path2_set = set(p2.taxonomy_path)
        path_sim = len(path1_set & path2_set) / len(path1_set | path2_set)

        # Combined similarity
        combined_sim = 0.6 * feature_sim + 0.4 * path_sim

        return combined_sim

    def _find_similar_phenomena(self, phenomenon: Phenomenon,
                               n_similar: int = 5) -> List[str]:
        """Find most similar phenomena"""
        similarities = []

        for other_id, other in self.phenomena.items():
            if other_id == phenomenon.phenomenon_id:
                continue

            sim = self._compute_phenomenon_similarity(phenomenon, other)
            similarities.append((other_id, sim))

        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [pid for pid, _ in similarities[:n_similar]]

    def _check_universality_class(self, phenomenon: Phenomenon) -> Optional[str]:
        """Check if phenomenon belongs to known universality class"""
        # This would compare critical exponents, scaling laws
        # For now, return None
        return None

    def identify_universality_class(self,
                                   phenomena: List[Phenomenon],
                                   class_name: str) -> UniversalityClass:
        """
        Identify a new universality class from phenomena

        Args:
            phenomena: List of phenomena sharing universal behavior
            class_name: Name for the universality class

        Returns:
            UniversalityClass object
        """
        print(f"🔬 Identifying universality class: {class_name}")

        class_id = f"universality_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Extract common properties
        # In practice, would fit critical exponents
        critical_exponents = {
            "beta": 0.33,  # Example
            "gamma": 1.24,
            "nu": 0.63
        }

        scaling_laws = [
            "Order parameter ~ (T - Tc)^beta",
            "Correlation length ~ |T - Tc|^-nu",
            "Susceptibility ~ |T - Tc|^-gamma"
        ]

        uni_class = UniversalityClass(
            class_id=class_id,
            name=class_name,
            description=f"Universality class identified in POLLN",
            critical_exponents=critical_exponents,
            scaling_laws=scaling_laws,
            phenomena=[p.phenomenon_id for p in phenomena],
            representative_systems=["POLLN"]
        )

        self.universality_classes[class_id] = uni_class

        # Link phenomena to class
        for p in phenomena:
            p.universality_class = class_id

        return uni_class

    def generate_taxonomy_report(self) -> str:
        """Generate comprehensive taxonomy report"""
        report = []
        report.append("=" * 80)
        report.append("EMERGENCE TAXONOMY REPORT")
        report.append("=" * 80)
        report.append("")

        # Statistics
        report.append("STATISTICS")
        report.append("-" * 80)
        report.append(f"Total phenomena classified: {len(self.phenomena)}")
        report.append(f"Total taxonomy nodes: {len(self.taxonomy_tree)}")
        report.append(f"Universality classes: {len(self.universality_classes)}")
        report.append("")

        # Taxonomy tree
        report.append("TAXONOMY STRUCTURE")
        report.append("-" * 80)
        self._print_tree(self.taxonomy_tree["root"], report, prefix="")
        report.append("")

        # Phenomena by category
        report.append("PHENOMENA BY CATEGORY")
        report.append("-" * 80)

        category_counts = {}
        for phenomenon in self.phenomena.values():
            if phenomenon.taxonomy_path:
                category = self.taxonomy_tree[phenomenon.taxonomy_path[1]].name  # Skip root
                category_counts[category] = category_counts.get(category, 0) + 1

        for category, count in sorted(category_counts.items()):
            report.append(f"{category}: {count}")

        report.append("")

        # Novel phenomena
        report.append("MOST NOVEL PHENOMENA")
        report.append("-" * 80)

        novel_sorted = sorted(self.phenomena.values(),
                             key=lambda p: p.novelty_score,
                             reverse=True)

        for i, phenomenon in enumerate(novel_sorted[:10]):
            report.append(f"{i+1}. {phenomenon.name}")
            report.append(f"   Novelty: {phenomenon.novelty_score:.3f}")
            report.append(f"   Category: {' -> '.join([self.taxonomy_tree[n].name for n in phenomenon.taxonomy_path])}")
            report.append("")

        return "\n".join(report)

    def _print_tree(self, node: TaxonomyNode, report: List[str], prefix: str = ""):
        """Recursively print taxonomy tree"""
        report.append(f"{prefix}{node.name} ({len(node.phenomena_ids)} phenomena)")

        for i, child_id in enumerate(node.children_ids):
            child = self.taxonomy_tree[child_id]
            is_last = (i == len(node.children_ids) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            connector = "└── " if is_last else "├── "
            self._print_tree(child, report, prefix + connector)

    def _save_taxonomy(self) -> None:
        """Save taxonomy to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save phenomena
        phenomena_file = self.output_dir / f"phenomena_{timestamp}.json"
        phenomena_data = {}
        for pid, phenomenon in self.phenomena.items():
            phenomena_data[pid] = {
                "phenomenon_id": phenomenon.phenomenon_id,
                "name": phenomenon.name,
                "description": phenomenon.description,
                "taxonomy_path": phenomenon.taxonomy_path,
                "features": phenomenon.features,
                "computational_signature": phenomenon.computational_signature,
                "novelty_score": phenomenon.novelty_score,
                "universality_class": phenomenon.universality_class,
                "similar_phenomena": phenomenon.similar_phenomena
            }

        with open(phenomena_file, 'w') as f:
            json.dump(phenomena_data, f, indent=2, default=str)

        # Save taxonomy structure
        taxonomy_file = self.output_dir / f"taxonomy_{timestamp}.json"
        taxonomy_data = {}
        for nid, node in self.taxonomy_tree.items():
            taxonomy_data[nid] = {
                "node_id": node.node_id,
                "name": node.name,
                "description": node.description,
                "parent_id": node.parent_id,
                "children_ids": node.children_ids,
                "phenomena_ids": node.phenomena_ids
            }

        with open(taxonomy_file, 'w') as f:
            json.dump(taxonomy_data, f, indent=2)

        print(f"  💾 Taxonomy saved to {taxonomy_file}")


if __name__ == "__main__":
    # Test taxonomy
    print("Testing Emergence Taxonomy")

    taxonomy = EmergenceTaxonomy(output_dir="./test_taxonomy_results")

    # Test classification
    test_phenomenon = {
        "name": "Sudden Synchronization",
        "description": "Agents suddenly synchronize their decisions when density exceeds threshold",
        "metrics": {
            "coordination": 0.95,
            "synchronization": 0.92,
            "criticality": 0.88
        },
        "signature": {
            "type": "phase_transition",
            "threshold": 0.73
        }
    }

    phenomenon = taxonomy.classify_phenomenon(test_phenomenon)

    # Generate report
    report = taxonomy.generate_taxonomy_report()
    print("\n" + report)
