"""
Task Distribution Design for Meta-Learning

Designs task distributions for meta-training and meta-testing.
Key challenge: Balance diversity and similarity for optimal generalization.

Components:
1. Task Families: Groups of related tasks
2. Meta-Training Tasks: Tasks for learning initialization
3. Meta-Test Tasks: Tasks for evaluating generalization
4. In-Distribution vs Out-of-Distribution: Generalization analysis
"""

import numpy as np
import torch
from typing import List, Dict, Tuple, Callable, Any, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pickle


@dataclass
class TaskDistributionConfig:
    """Task distribution configuration"""
    num_families: int = 4            # Number of task families
    tasks_per_family: int = 25       # Tasks per family

    # Meta-training/test split
    meta_train_ratio: float = 0.8    # 80% for training
    meta_test_ratio: float = 0.2     # 20% for testing

    # Task diversity
    diversity_metric: str = 'entropy'  # entropy, coverage, cluster
    min_distance: float = 0.1        # Minimum task distance

    # Sampling strategy
    sampling_strategy: str = 'uniform'  # uniform, weighted, curriculum
    curriculum_order: str = 'easy_to_hard'  # easy_to_hard, hard_to_easy, random


class Task:
    """
    Represents a single task for meta-learning

    A task consists of:
    - Support set: Examples for adaptation
    - Query set: Examples for evaluation
    - Task metadata: Family, difficulty, features
    """

    def __init__(
        self,
        task_id: int,
        family: str,
        support_x: torch.Tensor,
        support_y: torch.Tensor,
        query_x: torch.Tensor,
        query_y: torch.Tensor,
        difficulty: float = 0.5,
        features: Optional[np.ndarray] = None
    ):
        self.task_id = task_id
        self.family = family
        self.support_x = support_x
        self.support_y = support_y
        self.query_x = query_x
        self.query_y = query_y
        self.difficulty = difficulty
        self.features = features or self._extract_features()

    def _extract_features(self) -> np.ndarray:
        """Extract task features for diversity analysis"""
        # Combine support and query statistics
        all_x = torch.cat([self.support_x, self.query_x], dim=0)

        features = []
        features.append(all_x.mean(dim=0).cpu().numpy())
        features.append(all_x.std(dim=0).cpu().numpy())
        features.append(self.support_y.mean().cpu().numpy().reshape(1))
        features.append(self.support_y.std().cpu().numpy().reshape(1))

        return np.concatenate(features)

    def to_dict(self) -> Dict[str, torch.Tensor]:
        """Convert to dictionary format"""
        return {
            'support_x': self.support_x,
            'support_y': self.support_y,
            'query_x': self.query_x,
            'query_y': self.query_y
        }


class TaskFamily:
    """
    Represents a family of related tasks

    Task families share structure but differ in specifics.
    Examples:
    - Reasoning: Logic puzzles, math problems, causal inference
    - Coding: Bug fixing, code completion, refactoring
    - Dialogue: Question answering, chitchat, instruction following
    - Creative: Story writing, poetry, roleplay
    """

    def __init__(
        self,
        name: str,
        base_params: Dict[str, Any],
        variation_range: float = 0.2
    ):
        self.name = name
        self.base_params = base_params
        self.variation_range = variation_range
        self.tasks: List[Task] = []

    def generate_tasks(
        self,
        num_tasks: int,
        k_shot: int = 5,
        num_query: int = 15,
        state_dim: int = 128
    ) -> List[Task]:
        """Generate tasks from this family"""
        tasks = []

        for i in range(num_tasks):
            # Sample task-specific parameters
            task_params = self._sample_task_params()

            # Generate data
            support_x = self._generate_data(k_shot * 5, state_dim, task_params)
            support_y = self._generate_labels(support_x, task_params)
            query_x = self._generate_data(num_query, state_dim, task_params)
            query_y = self._generate_labels(query_x, task_params)

            # Compute difficulty
            difficulty = self._compute_difficulty(task_params)

            task = Task(
                task_id=len(self.tasks),
                family=self.name,
                support_x=support_x,
                support_y=support_y,
                query_x=query_x,
                query_y=query_y,
                difficulty=difficulty
            )

            self.tasks.append(task)
            tasks.append(task)

        return tasks

    def _sample_task_params(self) -> Dict[str, Any]:
        """Sample parameters for a specific task"""
        params = {}
        for key, value in self.base_params.items():
            if isinstance(value, (int, float)):
                # Add noise within variation range
                noise = np.random.uniform(-self.variation_range, self.variation_range)
                params[key] = value * (1 + noise)
            else:
                params[key] = value
        return params

    def _generate_data(
        self,
        num_samples: int,
        state_dim: int,
        params: Dict[str, Any]
    ) -> torch.Tensor:
        """Generate input data for task"""
        # Base distribution with task-specific shift
        base = torch.randn(num_samples, state_dim)
        shift = torch.randn(state_dim) * params.get('shift_scale', 0.1)
        return base + shift

    def _generate_labels(
        self,
        x: torch.Tensor,
        params: Dict[str, Any]
    ) -> torch.Tensor:
        """Generate labels for task"""
        # Task-specific labeling function
        scale = params.get('label_scale', 1.0)
        noise = params.get('noise_level', 0.1)
        return x.mean(dim=1) * scale + torch.randn(x.size(0)) * noise

    def _compute_difficulty(self, params: Dict[str, Any]) -> float:
        """Compute task difficulty (0-1 scale)"""
        # Higher noise and shift = harder
        noise_difficulty = params.get('noise_level', 0.1) * 5
        shift_difficulty = params.get('shift_scale', 0.1) * 2
        difficulty = min(1.0, noise_difficulty + shift_difficulty)
        return difficulty


class TaskDistribution:
    """
    Manages task distribution for meta-learning

    Responsibilities:
    1. Create diverse task families
    2. Split into meta-train/meta-test
    3. Sample tasks for training
    4. Measure diversity and coverage
    """

    def __init__(self, config: TaskDistributionConfig):
        self.config = config
        self.families: Dict[str, TaskFamily] = {}
        self.all_tasks: List[Task] = []
        self.meta_train_tasks: List[Task] = []
        self.meta_test_tasks: List[Task] = []

        # Diversity metrics
        self.diversity_score = 0.0
        self.coverage_score = 0.0

    def create_families(self) -> None:
        """Create task families"""
        print(f"Creating {self.config.num_families} task families...")

        family_configs = {
            'reasoning': {
                'shift_scale': 0.05,
                'label_scale': 1.0,
                'noise_level': 0.05
            },
            'coding': {
                'shift_scale': 0.15,
                'label_scale': 1.5,
                'noise_level': 0.1
            },
            'dialogue': {
                'shift_scale': 0.1,
                'label_scale': 0.8,
                'noise_level': 0.15
            },
            'creative': {
                'shift_scale': 0.2,
                'label_scale': 2.0,
                'noise_level': 0.2
            }
        }

        for family_name, base_params in family_configs.items():
            family = TaskFamily(family_name, base_params)
            tasks = family.generate_tasks(
                num_tasks=self.config.tasks_per_family,
                k_shot=5,
                num_query=15
            )
            self.families[family_name] = family
            self.all_tasks.extend(tasks)

        print(f"Generated {len(self.all_tasks)} tasks total")

    def split_train_test(self) -> None:
        """Split tasks into meta-train and meta-test"""
        # Stratified split by family
        for family_name, family in self.families.items():
            family_tasks = family.tasks
            n_train = int(len(family_tasks) * self.config.meta_train_ratio)

            # Shuffle and split
            indices = np.random.permutation(len(family_tasks))
            train_indices = indices[:n_train]
            test_indices = indices[n_train:]

            for idx in train_indices:
                self.meta_train_tasks.append(family_tasks[idx])
            for idx in test_indices:
                self.meta_test_tasks.append(family_tasks[idx])

        print(f"Meta-train: {len(self.meta_train_tasks)} tasks")
        print(f"Meta-test: {len(self.meta_test_tasks)} tasks")

    def compute_diversity(self) -> Dict[str, float]:
        """Compute task diversity metrics"""
        # Extract features
        features = np.array([task.features for task in self.all_tasks])

        # 1. Entropy-based diversity
        # Normalize features
        features_norm = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)

        # Compute pairwise distances
        from scipy.spatial.distance import pdist
        distances = pdist(features_norm, metric='euclidean')

        # Diversity = spread of distances
        diversity = distances.std() / (distances.mean() + 1e-8)
        self.diversity_score = diversity

        # 2. Coverage: how well tasks span the space
        # Use clustering to measure coverage
        n_clusters = min(10, len(self.all_tasks))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features_norm)

        # Coverage = ratio of filled clusters
        coverage = len(np.unique(labels)) / n_clusters
        self.coverage_score = coverage

        return {
            'diversity': diversity,
            'coverage': coverage,
            'avg_distance': distances.mean(),
            'distance_std': distances.std()
        }

    def sample_tasks(
        self,
        batch_size: int,
        split: str = 'train',
        strategy: str = 'uniform'
    ) -> List[Task]:
        """
        Sample tasks for meta-learning

        Args:
            batch_size: Number of tasks to sample
            split: 'train' or 'test'
            strategy: Sampling strategy

        Returns:
            List of sampled tasks
        """
        tasks = self.meta_train_tasks if split == 'train' else self.meta_test_tasks

        if strategy == 'uniform':
            # Uniform random sampling
            indices = np.random.choice(len(tasks), size=batch_size, replace=True)
        elif strategy == 'weighted':
            # Weight by difficulty (harder tasks more likely)
            difficulties = np.array([t.difficulty for t in tasks])
            probs = difficulties / difficulties.sum()
            indices = np.random.choice(len(tasks), size=batch_size, replace=True, p=probs)
        elif strategy == 'curriculum':
            # Curriculum learning: easier to harder
            sorted_tasks = sorted(tasks, key=lambda t: t.difficulty)
            # Sample from easier portion initially
            easy_threshold = np.percentile([t.difficulty for t in tasks], 50)
            easy_tasks = [t for t in tasks if t.difficulty < easy_threshold]
            indices = np.random.choice(len(easy_tasks), size=batch_size, replace=True)
            tasks = easy_tasks
        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")

        return [tasks[i] for i in indices]

    def analyze_generalization(self) -> Dict[str, Any]:
        """
        Analyze in-distribution vs out-of-distribution generalization

        Tests:
        1. IID performance: Same family, train vs test
        2. OOD performance: Different family
        3. Transfer distance: How far can we transfer?
        """
        results = {
            'iid_performance': {},
            'ood_performance': {},
            'transfer_analysis': {}
        }

        # In-distribution: same family
        for family_name in self.families.keys():
            train_tasks = [t for t in self.meta_train_tasks if t.family == family_name]
            test_tasks = [t for t in self.meta_test_tasks if t.family == family_name]

            if train_tasks and test_tasks:
                # Compute task similarity
                train_features = np.array([t.features for t in train_tasks])
                test_features = np.array([t.features for t in test_tasks])

                # Average distance
                from scipy.spatial.distance import cdist
                distances = cdist(train_features, test_features, metric='euclidean')
                avg_distance = distances.mean()

                results['iid_performance'][family_name] = avg_distance

        # Out-of-distribution: different family
        family_names = list(self.families.keys())
        for i, family1 in enumerate(family_names):
            for family2 in family_names[i+1:]:
                train_tasks = [t for t in self.meta_train_tasks if t.family == family1]
                test_tasks = [t for t in self.meta_test_tasks if t.family == family2]

                if train_tasks and test_tasks:
                    train_features = np.array([t.features for t in train_tasks])
                    test_features = np.array([t.features for t in test_tasks])

                    from scipy.spatial.distance import cdist
                    distances = cdist(train_features, test_features, metric='euclidean')
                    avg_distance = distances.mean()

                    key = f"{family1}_to_{family2}"
                    results['ood_performance'][key] = avg_distance

        return results

    def visualize_distribution(self) -> None:
        """Visualize task distribution"""
        # Extract features
        features = np.array([task.features for task in self.all_tasks])

        # PCA for visualization
        pca = PCA(n_components=2)
        features_2d = pca.fit_transform(features)

        # Plot by family
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # By family
        for family_name in self.families.keys():
            family_tasks = [t for t in self.all_tasks if t.family == family_name]
            family_features = np.array([t.features for t in family_tasks])
            family_2d = pca.transform(family_features)

            ax1.scatter(family_2d[:, 0], family_2d[:, 1],
                       label=family_name, alpha=0.6, s=50)

        ax1.set_xlabel('PC1')
        ax1.set_ylabel('PC2')
        ax1.set_title('Task Distribution by Family')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # By difficulty
        difficulties = [task.difficulty for task in self.all_tasks]
        scatter = ax2.scatter(features_2d[:, 0], features_2d[:, 1],
                             c=difficulties, cmap='RdYlGn_r',
                             alpha=0.6, s=50)
        ax2.set_xlabel('PC1')
        ax2.set_ylabel('PC2')
        ax2.set_title('Task Distribution by Difficulty')
        plt.colorbar(scatter, ax=ax2, label='Difficulty')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('simulations/advanced/metalearning/task_distribution.png', dpi=150)
        plt.close()

        print("Saved task distribution visualization to task_distribution.png")

    def save(self, path: str) -> None:
        """Save task distribution"""
        with open(path, 'wb') as f:
            pickle.dump({
                'families': self.families,
                'all_tasks': self.all_tasks,
                'meta_train_tasks': self.meta_train_tasks,
                'meta_test_tasks': self.meta_test_tasks,
                'config': self.config,
                'diversity_score': self.diversity_score,
                'coverage_score': self.coverage_score
            }, f)

        print(f"Saved task distribution to {path}")

    @classmethod
    def load(cls, path: str) -> 'TaskDistribution':
        """Load task distribution"""
        with open(path, 'rb') as f:
            data = pickle.load(f)

        distribution = cls(data['config'])
        distribution.families = data['families']
        distribution.all_tasks = data['all_tasks']
        distribution.meta_train_tasks = data['meta_train_tasks']
        distribution.meta_test_tasks = data['meta_test_tasks']
        distribution.diversity_score = data['diversity_score']
        distribution.coverage_score = data['coverage_score']

        return distribution


def optimize_task_diversity():
    """
    Optimize task diversity for meta-learning

    Tests:
    1. How many task families?
    2. How diverse should tasks be?
    3. What's the optimal split?
    """
    print("\n" + "=" * 60)
    print("Optimizing Task Diversity")
    print("=" * 60)

    results = []

    # Test different numbers of families
    for num_families in [2, 4, 6, 8]:
        config = TaskDistributionConfig(
            num_families=num_families,
            tasks_per_family=25
        )

        distribution = TaskDistribution(config)
        distribution.create_families()
        distribution.split_train_test()

        diversity_metrics = distribution.compute_diversity()
        generalization = distribution.analyze_generalization()

        results.append({
            'num_families': num_families,
            'diversity': diversity_metrics['diversity'],
            'coverage': diversity_metrics['coverage'],
            'iid_distance': np.mean(list(generalization['iid_performance'].values())),
            'ood_distance': np.mean(list(generalization['ood_performance'].values()))
        })

        print(f"\nFamilies: {num_families}")
        print(f"  Diversity: {diversity_metrics['diversity']:.4f}")
        print(f"  Coverage: {diversity_metrics['coverage']:.4f}")

    # Find optimal
    optimal = max(results, key=lambda r: r['diversity'] * r['coverage'])

    print(f"\nOptimal Configuration:")
    print(f"  Num Families: {optimal['num_families']}")
    print(f"  Diversity Score: {optimal['diversity']:.4f}")
    print(f"  Coverage Score: {optimal['coverage']:.4f}")

    return optimal


def create_task_distribution() -> TaskDistribution:
    """Create and save task distribution"""
    print("\n" + "=" * 60)
    print("Creating Task Distribution")
    print("=" * 60)

    config = TaskDistributionConfig(
        num_families=4,
        tasks_per_family=25,
        meta_train_ratio=0.8,
        sampling_strategy='uniform'
    )

    distribution = TaskDistribution(config)
    distribution.create_families()
    distribution.split_train_test()

    # Analyze
    diversity = distribution.compute_diversity()
    print(f"\nDiversity Metrics:")
    print(f"  Diversity: {diversity['diversity']:.4f}")
    print(f"  Coverage: {diversity['coverage']:.4f}")

    # Visualize
    distribution.visualize_distribution()

    # Generalization analysis
    generalization = distribution.analyze_generalization()
    print(f"\nGeneralization Analysis:")
    print(f"  Avg IID Distance: {np.mean(list(generalization['iid_performance'].values())):.4f}")
    print(f"  Avg OOD Distance: {np.mean(list(generalization['ood_performance'].values())):.4f}")

    # Save
    Path('simulations/advanced/metalearning').mkdir(parents=True, exist_ok=True)
    distribution.save('simulations/advanced/metalearning/task_distribution.pkl')

    return distribution


def generate_task_config() -> Dict[str, Any]:
    """Generate task configuration for meta-learning"""
    print("\n" + "=" * 60)
    print("Generating Task Configuration")
    print("=" * 60)

    config = {
        'task_distribution': {
            'num_families': 4,
            'families': ['reasoning', 'coding', 'dialogue', 'creative'],
            'tasks_per_family': 25,
            'total_tasks': 100
        },
        'meta_train': {
            'num_tasks': 80,
            'split_ratio': 0.8,
            'sampling_strategy': 'uniform'
        },
        'meta_test': {
            'num_tasks': 20,
            'split_ratio': 0.2,
            'includes_ood': True
        },
        'diversity': {
            'target_diversity': 0.5,
            'target_coverage': 0.8,
            'min_task_distance': 0.1
        },
        'sampling': {
            'strategy': 'uniform',
            'alternatives': ['weighted', 'curriculum'],
            'batch_size': 32
        },
        'generalization': {
            'iid_performance': 'high',
            'ood_performance': 'medium',
            'transfer_capability': 'family_to_family'
        }
    }

    print("\nTask Configuration:")
    import json
    print(json.dumps(config, indent=2))

    # Save config
    with open('simulations/advanced/metalearning/task_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    return config


def main():
    """Main execution"""
    print("=" * 60)
    print("Task Distribution Design for Meta-Learning")
    print("=" * 60)

    Path('simulations/advanced/metalearning').mkdir(parents=True, exist_ok=True)

    # 1. Optimize task diversity
    print("\n1. Optimizing Task Diversity")
    print("-" * 60)
    optimal_diversity = optimize_task_diversity()

    # 2. Create task distribution
    print("\n2. Creating Task Distribution")
    print("-" * 60)
    distribution = create_task_distribution()

    # 3. Generate configuration
    print("\n3. Generating Configuration")
    print("-" * 60)
    config = generate_task_config()

    print("\n" + "=" * 60)
    print("Task distribution design complete!")
    print("=" * 60)

    return {
        'optimal_diversity': optimal_diversity,
        'distribution': distribution,
        'config': config
    }


if __name__ == '__main__':
    main()
