"""
POLLN Task Similarity Modeling
==============================

Measures and models task similarity to predict transfer learning efficiency.
Provides similarity thresholds for beneficial knowledge transfer.

Key Metrics:
- Semantic similarity: Embedding-based task description similarity
- Structural similarity: Architecture and computational graph similarity
- Capability overlap: Shared skills and required operations
- Transfer efficiency: Performance gain from transfer vs from scratch
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import seaborn as sns


class TaskDomain(Enum):
    """High-level task categories"""
    REASONING = "reasoning"
    GENERATION = "generation"
    CLASSIFICATION = "classification"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    CODING = "coding"
    MATH = "math"
    RETRIEVAL = "retrieval"


@dataclass
class Task:
    """Represents a task with its characteristics"""
    id: str
    name: str
    domain: TaskDomain
    description: str
    required_capabilities: List[str]
    architecture_pattern: str  # e.g., "decoder-only", "encoder-decoder"
    input_modality: str  # e.g., "text", "image", "audio"
    output_modality: str
    complexity_score: float  # 0-1
    data_requirements: Dict[str, float]  # dataset_size, diversity, etc.

    # For similarity computation
    embedding: Optional[np.ndarray] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain.value,
            'description': self.description,
            'required_capabilities': self.required_capabilities,
            'architecture_pattern': self.architecture_pattern,
            'input_modality': self.input_modality,
            'output_modality': self.output_modality,
            'complexity_score': self.complexity_score,
            'data_requirements': self.data_requirements
        }


class SimilarityCalculator:
    """Computes multi-dimensional task similarity"""

    def __init__(self):
        self.semantic_weight = 0.4
        self.structural_weight = 0.3
        self.capability_weight = 0.3

    def semantic_similarity(self, task1: Task, task2: Task) -> float:
        """Semantic similarity using TF-IDF on descriptions"""
        descriptions = [task1.description, task2.description]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)

    def structural_similarity(self, task1: Task, task2: Task) -> float:
        """Structural similarity based on architecture and modalities"""
        score = 0.0

        # Architecture pattern match
        if task1.architecture_pattern == task2.architecture_pattern:
            score += 0.4

        # Input modality match
        if task1.input_modality == task2.input_modality:
            score += 0.3

        # Output modality match
        if task1.output_modality == task2.output_modality:
            score += 0.3

        return score

    def capability_overlap(self, task1: Task, task2: Task) -> float:
        """Jaccard similarity of required capabilities"""
        caps1 = set(task1.required_capabilities)
        caps2 = set(task2.required_capabilities)

        if len(caps1) == 0 and len(caps2) == 0:
            return 1.0

        intersection = len(caps1 & caps2)
        union = len(caps1 | caps2)

        return intersection / union if union > 0 else 0.0

    def complexity_similarity(self, task1: Task, task2: Task) -> float:
        """Similarity in complexity (inverse of difference)"""
        diff = abs(task1.complexity_score - task2.complexity_score)
        return 1.0 - diff

    def overall_similarity(self, task1: Task, task2: Task) -> float:
        """Weighted combination of all similarity metrics"""
        sem = self.semantic_similarity(task1, task2)
        struct = self.structural_similarity(task1, task2)
        cap = self.capability_overlap(task1, task2)
        comp = self.complexity_similarity(task1, task2)

        # Overall similarity (weights sum to 1.0)
        similarity = (
            self.semantic_weight * sem +
            self.structural_weight * struct +
            self.capability_weight * cap +
            0.0 * comp  # Complexity is secondary
        )

        return float(similarity)


class TaskSimilarityMatrix:
    """Maintains and analyzes task similarity relationships"""

    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
        self.task_index = {task.id: i for i, task in enumerate(tasks)}
        self.similarity_matrix = np.zeros((len(tasks), len(tasks)))
        self.calculator = SimilarityCalculator()

    def compute_all_similarities(self):
        """Compute pairwise similarities for all tasks"""
        n = len(self.tasks)
        for i in range(n):
            for j in range(i, n):
                sim = self.calculator.overall_similarity(self.tasks[i], self.tasks[j])
                self.similarity_matrix[i][j] = sim
                self.similarity_matrix[j][i] = sim  # Symmetric

    def get_similarity(self, task1_id: str, task2_id: str) -> float:
        """Get similarity between two tasks"""
        i = self.task_index[task1_id]
        j = self.task_index[task2_id]
        return float(self.similarity_matrix[i][j])

    def find_similar_tasks(self, task_id: str, threshold: float = 0.5,
                          top_k: Optional[int] = None) -> List[Tuple[str, float]]:
        """Find tasks similar to the given task"""
        i = self.task_index[task_id]
        similarities = []

        for j, task in enumerate(self.tasks):
            if j != i:
                sim = float(self.similarity_matrix[i][j])
                if sim >= threshold:
                    similarities.append((task.id, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        if top_k:
            similarities = similarities[:top_k]

        return similarities

    def get_similarity_stats(self) -> Dict[str, float]:
        """Get statistics about similarity distribution"""
        # Get upper triangle (excluding diagonal)
        upper_tri = self.similarity_matrix[np.triu_indices_from(self.similarity_matrix, k=1)]

        return {
            'mean': float(np.mean(upper_tri)),
            'std': float(np.std(upper_tri)),
            'min': float(np.min(upper_tri)),
            'max': float(np.max(upper_tri)),
            'median': float(np.median(upper_tri))
        }

    def visualize(self, save_path: Optional[str] = None):
        """Visualize similarity matrix as heatmap"""
        plt.figure(figsize=(12, 10))

        task_names = [task.name for task in self.tasks]
        sns.heatmap(
            self.similarity_matrix,
            xticklabels=task_names,
            yticklabels=task_names,
            cmap='viridis',
            annot=True,
            fmt='.2f',
            cbar_kws={'label': 'Similarity'}
        )
        plt.title('Task Similarity Matrix')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

    def save(self, filepath: str):
        """Save similarity matrix to file"""
        data = {
            'tasks': [task.to_dict() for task in self.tasks],
            'similarity_matrix': self.similarity_matrix.tolist()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


class TransferEfficiencyPredictor:
    """Predicts transfer learning efficiency based on task similarity"""

    def __init__(self):
        # These thresholds will be learned from simulation data
        self.high_threshold = 0.8
        self.medium_threshold = 0.5
        self.low_threshold = 0.3

        # Efficiency models (will be fitted)
        self.efficiency_model = None

    def predict_transfer_benefit(self, similarity: float) -> Dict[str, float]:
        """Predict transfer learning benefits based on similarity"""

        if similarity >= self.high_threshold:
            # High similarity: large transfer benefit
            return {
                'expected_speedup': 5.0,  # 5x faster training
                'expected_performance_gain': 0.15,  # 15% better final accuracy
                'catastrophic_forgetting_risk': 0.05,  # Low risk
                'transfer_recommendation': 'full_transfer'
            }
        elif similarity >= self.medium_threshold:
            # Medium similarity: moderate transfer benefit
            return {
                'expected_speedup': 2.5,
                'expected_performance_gain': 0.08,
                'catastrophic_forgetting_risk': 0.15,
                'transfer_recommendation': 'selective_transfer'
            }
        elif similarity >= self.low_threshold:
            # Low similarity: minimal transfer benefit
            return {
                'expected_speedup': 1.2,
                'expected_performance_gain': 0.02,
                'catastrophic_forgetting_risk': 0.40,
                'transfer_recommendation': 'cautious_transfer'
            }
        else:
            # Very low similarity: negative transfer likely
            return {
                'expected_speedup': 0.8,  # Actually slower
                'expected_performance_gain': -0.05,  # Performance loss
                'catastrophic_forgetting_risk': 0.70,
                'transfer_recommendation': 'no_transfer'
            }

    def estimate_sample_efficiency(self, similarity: float,
                                   base_samples: int) -> Dict[str, float]:
        """Estimate how many samples are saved by transfer learning"""
        benefit = self.predict_transfer_benefit(similarity)
        speedup = benefit['expected_speedup']

        return {
            'samples_without_transfer': base_samples,
            'samples_with_transfer': int(base_samples / speedup),
            'samples_saved': int(base_samples - base_samples / speedup),
            'efficiency_ratio': speedup
        }


def create_standard_task_set() -> List[Task]:
    """Create a standard set of POLLN tasks for similarity analysis"""

    tasks = [
        Task(
            id="code_review",
            name="Code Review",
            domain=TaskDomain.CODING,
            description="Review code for bugs, style issues, and improvements",
            required_capabilities=["syntax_analysis", "pattern_matching", "reasoning"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.8,
            data_requirements={"dataset_size": 10000, "diversity": 0.7}
        ),
        Task(
            id="code_generation",
            name="Code Generation",
            domain=TaskDomain.CODING,
            description="Generate code from natural language descriptions",
            required_capabilities=["syntax_analysis", "pattern_matching", "generation"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.9,
            data_requirements={"dataset_size": 50000, "diversity": 0.9}
        ),
        Task(
            id="bug_detection",
            name="Bug Detection",
            domain=TaskDomain.CODING,
            description="Identify bugs in code snippets",
            required_capabilities=["syntax_analysis", "pattern_matching", "classification"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.7,
            data_requirements={"dataset_size": 20000, "diversity": 0.6}
        ),
        Task(
            id="text_summarization",
            name="Text Summarization",
            domain=TaskDomain.SUMMARIZATION,
            description="Generate concise summaries of long documents",
            required_capabilities=["comprehension", "generation", "compression"],
            architecture_pattern="encoder-decoder",
            input_modality="text",
            output_modality="text",
            complexity_score=0.75,
            data_requirements={"dataset_size": 100000, "diversity": 0.8}
        ),
        Task(
            id="question_answering",
            name="Question Answering",
            domain=TaskDomain.REASONING,
            description="Answer questions based on given context",
            required_capabilities=["comprehension", "reasoning", "retrieval"],
            architecture_pattern="encoder-decoder",
            input_modality="text",
            output_modality="text",
            complexity_score=0.7,
            data_requirements={"dataset_size": 80000, "diversity": 0.75}
        ),
        Task(
            id="math_word_problems",
            name="Math Word Problems",
            domain=TaskDomain.MATH,
            description="Solve mathematical word problems",
            required_capabilities=["comprehension", "reasoning", "calculation"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.85,
            data_requirements={"dataset_size": 30000, "diversity": 0.5}
        ),
        Task(
            id="sentiment_analysis",
            name="Sentiment Analysis",
            domain=TaskDomain.CLASSIFICATION,
            description="Classify text sentiment (positive/negative/neutral)",
            required_capabilities=["comprehension", "classification"],
            architecture_pattern="encoder-only",
            input_modality="text",
            output_modality="label",
            complexity_score=0.4,
            data_requirements={"dataset_size": 50000, "diversity": 0.6}
        ),
        Task(
            id="translation_en_fr",
            name="English-French Translation",
            domain=TaskDomain.TRANSLATION,
            description="Translate English text to French",
            required_capabilities=["comprehension", "generation", "alignment"],
            architecture_pattern="encoder-decoder",
            input_modality="text",
            output_modality="text",
            complexity_score=0.7,
            data_requirements={"dataset_size": 1000000, "diversity": 0.95}
        ),
        Task(
            id="translation_en_es",
            name="English-Spanish Translation",
            domain=TaskDomain.TRANSLATION,
            description="Translate English text to Spanish",
            required_capabilities=["comprehension", "generation", "alignment"],
            architecture_pattern="encoder-decoder",
            input_modality="text",
            output_modality="text",
            complexity_score=0.7,
            data_requirements={"dataset_size": 1000000, "diversity": 0.95}
        ),
        Task(
            id="document_retrieval",
            name="Document Retrieval",
            domain=TaskDomain.RETRIEVAL,
            description="Retrieve relevant documents from a corpus",
            required_capabilities=["embedding", "similarity", "ranking"],
            architecture_pattern="encoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.5,
            data_requirements={"dataset_size": 100000, "diversity": 0.8}
        ),
    ]

    return tasks


def main():
    """Main simulation"""
    print("=" * 70)
    print("POLLN Task Similarity Modeling")
    print("=" * 70)

    # Create task set
    print("\n1. Creating standard task set...")
    tasks = create_standard_task_set()
    print(f"   Created {len(tasks)} tasks")

    # Compute similarity matrix
    print("\n2. Computing task similarity matrix...")
    matrix = TaskSimilarityMatrix(tasks)
    matrix.compute_all_similarities()
    print("   Similarity matrix computed")

    # Get statistics
    print("\n3. Similarity statistics:")
    stats = matrix.get_similarity_stats()
    for key, value in stats.items():
        print(f"   {key}: {value:.4f}")

    # Find similar tasks for each task
    print("\n4. Finding similar tasks (threshold >= 0.6):")
    for task in tasks:
        similar = matrix.find_similar_tasks(task.id, threshold=0.6, top_k=3)
        if similar:
            print(f"\n   {task.name}:")
            for sim_id, sim_score in similar:
                sim_task = next(t for t in tasks if t.id == sim_id)
                print(f"      - {sim_task.name}: {sim_score:.3f}")

    # Predict transfer benefits
    print("\n5. Transfer efficiency predictions:")
    predictor = TransferEfficiencyPredictor()

    test_similarities = [0.9, 0.7, 0.5, 0.3, 0.1]
    for sim in test_similarities:
        benefit = predictor.predict_transfer_benefit(sim)
        print(f"\n   Similarity {sim:.1f}:")
        print(f"      Recommendation: {benefit['transfer_recommendation']}")
        print(f"      Expected speedup: {benefit['expected_speedup']:.1f}x")
        print(f"      Performance gain: {benefit['expected_performance_gain']:.2%}")
        print(f"      Forgetting risk: {benefit['catastrophic_forgetting_risk']:.2%}")

    # Sample efficiency estimation
    print("\n6. Sample efficiency estimation (base: 10,000 samples):")
    for sim in [0.8, 0.6, 0.4]:
        efficiency = predictor.estimate_sample_efficiency(sim, 10000)
        print(f"\n   Similarity {sim:.1f}:")
        print(f"      Without transfer: {efficiency['samples_without_transfer']:,} samples")
        print(f"      With transfer: {efficiency['samples_with_transfer']:,} samples")
        print(f"      Saved: {efficiency['samples_saved']:,} samples ({efficiency['efficiency_ratio']:.1f}x)")

    # Save results
    print("\n7. Saving results...")
    matrix.save("simulations/advanced/transfer/task_similarity_matrix.json")
    print("   Saved similarity matrix")

    # Generate recommendations
    print("\n8. Transfer recommendations:")
    print("\n   Fine-tuning strategy by similarity level:")
    print("      - High (>= 0.8): LoRA with low learning rate")
    print("      - Medium (0.5 - 0.8): Full fine-tuning with frozen embeddings")
    print("      - Low (0.3 - 0.5): Selective layer fine-tuning")
    print("      - Very low (< 0.3): Train from scratch")

    print("\n" + "=" * 70)
    print("Simulation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
