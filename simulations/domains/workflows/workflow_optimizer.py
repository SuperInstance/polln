"""
Workflow Optimizer for POLLN
Uses ML to predict optimal workflow patterns and configurations
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict


class PatternType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    MAP_REDUCE = "map_reduce"


@dataclass
class WorkflowFeatures:
    """Features extracted from workflow"""
    num_tasks: int
    avg_task_duration: float
    task_duration_variance: float
    dependency_ratio: float  # edges / possible edges
    data_size_per_task: float
    complexity_score: float
    diversity_score: float
    criticality: float


@dataclass
class WorkflowExecution:
    """Historical workflow execution record"""
    features: WorkflowFeatures
    pattern: PatternType
    agent_count: int
    completion_time: float
    quality_score: float
    success: bool
    cost: float


class WorkflowFeatureExtractor:
    """Extract features from workflow descriptions"""

    def extract_features(self, workflow: Dict[str, Any]) -> WorkflowFeatures:
        """Extract features from workflow specification"""
        tasks = workflow.get('tasks', [])

        num_tasks = len(tasks)
        durations = [t.get('duration', 1.0) for t in tasks]
        avg_duration = np.mean(durations)
        duration_variance = np.var(durations)

        # Compute dependency ratio
        total_deps = sum(len(t.get('dependencies', [])) for t in tasks)
        max_deps = num_tasks * (num_tasks - 1) / 2
        dependency_ratio = total_deps / max_deps if max_deps > 0 else 0

        # Data size
        data_sizes = [t.get('data_size', 1.0) for t in tasks]
        avg_data_size = np.mean(data_sizes)

        # Complexity score (0-1)
        complexity = self._compute_complexity(tasks)

        # Diversity score (0-1)
        diversity = self._compute_diversity(tasks)

        # Criticality (0-1)
        criticality = workflow.get('criticality', 0.5)

        return WorkflowFeatures(
            num_tasks=num_tasks,
            avg_task_duration=avg_duration,
            task_duration_variance=duration_variance,
            dependency_ratio=dependency_ratio,
            data_size_per_task=avg_data_size,
            complexity_score=complexity,
            diversity_score=diversity,
            criticality=criticality
        )

    def _compute_complexity(self, tasks: List[Dict]) -> float:
        """Compute workflow complexity score"""
        factors = []

        # Number of tasks
        num_tasks = len(tasks)
        factors.append(min(num_tasks / 100, 1.0))

        # Dependency density
        total_deps = sum(len(t.get('dependencies', [])) for t in tasks)
        dep_density = total_deps / num_tasks if num_tasks > 0 else 0
        factors.append(min(dep_density / 5, 1.0))

        # Task type diversity
        task_types = set(t.get('type', 'default') for t in tasks)
        type_diversity = len(task_types) / 10
        factors.append(min(type_diversity, 1.0))

        return np.mean(factors)

    def _compute_diversity(self, tasks: List[Dict]) -> float:
        """Compute task diversity score"""
        if not tasks:
            return 0.0

        # Duration diversity
        durations = [t.get('duration', 1.0) for t in tasks]
        duration_cv = np.std(durations) / (np.mean(durations) + 1e-6)

        # Skill diversity
        all_skills = []
        for task in tasks:
            skills = task.get('skills', [])
            all_skills.extend(skills)

        unique_skills = len(set(all_skills))
        skill_diversity = unique_skills / 20 if all_skills else 0

        return min((duration_cv + skill_diversity) / 2, 1.0)


class WorkflowPredictor:
    """Predict optimal workflow configurations using ML"""

    def __init__(self):
        self.feature_extractor = WorkflowFeatureExtractor()
        self.historical_data: List[WorkflowExecution] = []
        self.pattern_performance = defaultdict(list)

    def add_execution(self, execution: WorkflowExecution):
        """Add historical execution record"""
        self.historical_data.append(execution)
        self.pattern_performance[execution.pattern].append(execution)

    def train(self, data: List[Dict]):
        """Train on historical data"""
        for record in data:
            features = self.feature_extractor.extract_features(record['workflow'])
            execution = WorkflowExecution(
                features=features,
                pattern=PatternType(record['pattern']),
                agent_count=record['agent_count'],
                completion_time=record['completion_time'],
                quality_score=record['quality_score'],
                success=record['success'],
                cost=record['cost']
            )
            self.add_execution(execution)

    def predict_pattern(self, workflow: Dict[str, Any]) -> Tuple[PatternType, float]:
        """Predict optimal pattern for workflow"""
        features = self.feature_extractor.extract_features(workflow)

        if not self.historical_data:
            # No historical data, use heuristics
            return self._heuristic_prediction(features)

        # Find similar historical workflows
        similar = self._find_similar(features, k=10)

        # Score patterns based on similar workflows
        pattern_scores = defaultdict(list)
        for execution in similar:
            # Compute similarity score
            similarity = self._compute_similarity(features, execution.features)
            performance = self._compute_performance_score(execution)
            pattern_scores[execution.pattern].append(similarity * performance)

        # Select best pattern
        best_pattern = max(
            pattern_scores.items(),
            key=lambda x: np.mean(x[1])
        )

        confidence = np.std(pattern_scores[best_pattern[0]]) if len(pattern_scores[best_pattern[0]]) > 1 else 0.5

        return best_pattern[0], confidence

    def predict_agent_count(self, workflow: Dict[str, Any], pattern: PatternType) -> int:
        """Predict optimal number of agents"""
        features = self.feature_extractor.extract_features(workflow)

        # Filter executions by pattern
        pattern_executions = [e for e in self.historical_data if e.pattern == pattern]

        if not pattern_executions:
            # Use heuristic
            return self._heuristic_agent_count(features, pattern)

        # Find similar executions
        similar = self._find_similar(features, k=5, filter_pattern=pattern)

        # Predict based on similar executions
        agent_counts = [e.agent_count for e in similar]
        return int(np.median(agent_counts))

    def _heuristic_prediction(self, features: WorkflowFeatures) -> Tuple[PatternType, float]:
        """Use heuristics to predict pattern"""
        if features.dependency_ratio > 0.7:
            # High dependencies, use sequential
            return PatternType.SEQUENTIAL, 0.7
        elif features.num_tasks > 50 and features.dependency_ratio < 0.3:
            # Many independent tasks, use map-reduce
            return PatternType.MAP_REDUCE, 0.8
        elif features.complexity_score > 0.7:
            # High complexity, use hierarchical
            return PatternType.HIERARCHICAL, 0.6
        else:
            # Default to parallel
            return PatternType.PARALLEL, 0.5

    def _heuristic_agent_count(self, features: WorkflowFeatures, pattern: PatternType) -> int:
        """Use heuristics to predict agent count"""
        base_count = max(2, min(20, int(features.num_tasks / 5)))

        if pattern == PatternType.SEQUENTIAL:
            return max(1, base_count // 2)
        elif pattern == PatternType.PARALLEL:
            return min(50, base_count * 2)
        elif pattern == PatternType.HIERARCHICAL:
            return base_count
        else:  # MAP_REDUCE
            return min(100, base_count * 3)

    def _find_similar(
        self,
        features: WorkflowFeatures,
        k: int = 5,
        filter_pattern: Optional[PatternType] = None
    ) -> List[WorkflowExecution]:
        """Find k most similar historical executions"""
        candidates = self.historical_data

        if filter_pattern:
            candidates = [e for e in candidates if e.pattern == filter_pattern]

        # Compute similarities
        similarities = []
        for execution in candidates:
            sim = self._compute_similarity(features, execution.features)
            similarities.append((sim, execution))

        # Sort and return top k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in similarities[:k]]

    def _compute_similarity(self, f1: WorkflowFeatures, f2: WorkflowFeatures) -> float:
        """Compute similarity between two feature vectors"""
        # Normalize features
        f1_vec = np.array([
            f1.num_tasks / 100,
            f1.avg_task_duration / 10,
            f1.task_duration_variance / 10,
            f1.dependency_ratio,
            f1.data_size_per_task / 100,
            f1.complexity_score,
            f1.diversity_score,
            f1.criticality
        ])

        f2_vec = np.array([
            f2.num_tasks / 100,
            f2.avg_task_duration / 10,
            f2.task_duration_variance / 10,
            f2.dependency_ratio,
            f2.data_size_per_task / 100,
            f2.complexity_score,
            f2.diversity_score,
            f2.criticality
        ])

        # Cosine similarity
        dot_product = np.dot(f1_vec, f2_vec)
        norm1 = np.linalg.norm(f1_vec)
        norm2 = np.linalg.norm(f2_vec)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _compute_performance_score(self, execution: WorkflowExecution) -> float:
        """Compute performance score for execution"""
        # Lower is better for time and cost, higher is better for quality
        time_score = 1.0 / (execution.completion_time + 1e-6)
        quality_score = execution.quality_score
        success_bonus = 1.5 if execution.success else 0.5

        return time_score * quality_score * success_bonus


class WorkflowOptimizer:
    """Main workflow optimization engine"""

    def __init__(self):
        self.predictor = WorkflowPredictor()
        self.feature_extractor = WorkflowFeatureExtractor()

    def optimize_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized workflow configuration"""
        # Extract features
        features = self.feature_extractor.extract_features(workflow)

        # Predict pattern and agent count
        pattern, confidence = self.predictor.predict_pattern(workflow)
        agent_count = self.predictor.predict_agent_count(workflow, pattern)

        # Generate configuration
        config = {
            'pattern': pattern.value,
            'agent_count': agent_count,
            'confidence': confidence,
            'features': {
                'num_tasks': features.num_tasks,
                'complexity': features.complexity_score,
                'diversity': features.diversity_score,
                'dependencies': features.dependency_ratio,
            },
            'parameters': self._generate_pattern_params(pattern, features),
            'expected_performance': self._estimate_performance(
                pattern, agent_count, features
            )
        }

        return config

    def _generate_pattern_params(self, pattern: PatternType, features: WorkflowFeatures) -> Dict:
        """Generate pattern-specific parameters"""
        if pattern == PatternType.SEQUENTIAL:
            return {
                'checkpoint_frequency': 'high',
                'error_handling': 'retry_immediate',
            }
        elif pattern == PatternType.PARALLEL:
            return {
                'aggregation': 'majority',
                'sync_strategy': 'async',
                'max_parallelism': features.num_tasks,
            }
        elif pattern == PatternType.HIERARCHICAL:
            return {
                'levels': 3,
                'fan_out': min(5, features.num_tasks // 3),
                'coordination': 'tree',
            }
        else:  # MAP_REDUCE
            return {
                'mappers': features.num_tasks // 10,
                'reducers': 3,
                'chunk_size': 10,
                'aggregation': 'mean',
            }

    def _estimate_performance(
        self,
        pattern: PatternType,
        agent_count: int,
        features: WorkflowFeatures
    ) -> Dict:
        """Estimate performance metrics"""
        # Simple estimation model
        base_time = features.num_tasks * features.avg_task_duration

        if pattern == PatternType.SEQUENTIAL:
            estimated_time = base_time
        elif pattern == PatternType.PARALLEL:
            estimated_time = base_time / min(agent_count, features.num_tasks)
        elif pattern == PatternType.HIERARCHICAL:
            estimated_time = base_time / np.log2(agent_count + 1)
        else:  # MAP_REDUCE
            estimated_time = (base_time / agent_count) * 1.5

        return {
            'estimated_time': estimated_time,
            'speedup': base_time / estimated_time,
            'estimated_quality': 0.9 - (features.complexity_score * 0.1),
            'estimated_cost': estimated_time * agent_count * 0.01,
        }


def generate_synthetic_training_data(n: int = 1000) -> List[Dict]:
    """Generate synthetic training data for the predictor"""
    data = []

    for _ in range(n):
        # Random workflow
        num_tasks = np.random.randint(5, 100)
        tasks = []
        for i in range(num_tasks):
            task = {
                'duration': np.random.uniform(0.5, 5.0),
                'dependencies': [],
                'data_size': np.random.uniform(0.1, 10.0),
                'type': np.random.choice(['compute', 'io', 'network']),
                'skills': np.random.choice(['analysis', 'processing', 'coordination'], np.random.randint(1, 3)).tolist()
            }
            tasks.append(task)

        # Add dependencies
        for i in range(1, num_tasks):
            if np.random.random() < 0.3:
                dep = np.random.randint(0, i)
                tasks[i]['dependencies'].append(dep)

        workflow = {'tasks': tasks, 'criticality': np.random.uniform(0.3, 0.9)}

        # Assign pattern and simulate
        feature_extractor = WorkflowFeatureExtractor()
        features = feature_extractor.extract_features(workflow)

        # Select pattern based on features
        if features.dependency_ratio > 0.6:
            pattern = PatternType.SEQUENTIAL.value
        elif features.num_tasks > 50:
            pattern = PatternType.MAP_REDUCE.value
        elif features.complexity_score > 0.7:
            pattern = PatternType.HIERARCHICAL.value
        else:
            pattern = PatternType.PARALLEL.value

        # Simulate execution
        agent_count = np.random.randint(2, 20)
        completion_time = num_tasks * 1.5 / agent_count
        quality_score = np.random.uniform(0.7, 0.95)
        success = np.random.random() < 0.9
        cost = completion_time * agent_count * 0.01

        data.append({
            'workflow': workflow,
            'pattern': pattern,
            'agent_count': agent_count,
            'completion_time': completion_time,
            'quality_score': quality_score,
            'success': success,
            'cost': cost
        })

    return data


def run_optimizer_demo():
    """Run workflow optimizer demo"""
    print("="*60)
    print("Workflow Optimizer Demo")
    print("="*60)

    # Generate training data
    print("\nGenerating synthetic training data...")
    training_data = generate_synthetic_training_data(500)

    # Train predictor
    print("Training predictor...")
    optimizer = WorkflowOptimizer()
    optimizer.predictor.train(training_data)

    # Test on sample workflows
    print("\n" + "="*60)
    print("Testing on sample workflows")
    print("="*60)

    test_workflows = [
        {
            'name': 'Data Pipeline',
            'tasks': [
                {'duration': 2.0, 'dependencies': [], 'data_size': 10},
                {'duration': 3.0, 'dependencies': [0], 'data_size': 8},
                {'duration': 1.0, 'dependencies': [1], 'data_size': 6},
                {'duration': 2.5, 'dependencies': [2], 'data_size': 4},
            ],
            'criticality': 0.8
        },
        {
            'name': 'Batch Processing',
            'tasks': [
                {'duration': 1.0, 'dependencies': [], 'data_size': 5, 'type': 'compute'}
                for _ in range(50)
            ],
            'criticality': 0.6
        },
        {
            'name': 'Complex Analysis',
            'tasks': [
                {'duration': 2.0, 'dependencies': [], 'data_size': 3, 'type': 'analysis'},
                {'duration': 1.5, 'dependencies': [0], 'data_size': 2, 'type': 'processing'},
                {'duration': 1.8, 'dependencies': [0], 'data_size': 2, 'type': 'processing'},
                {'duration': 2.2, 'dependencies': [0], 'data_size': 2, 'type': 'processing'},
                {'duration': 1.0, 'dependencies': [1, 2, 3], 'data_size': 1, 'type': 'validation'},
            ],
            'criticality': 0.9
        }
    ]

    results = {}
    for workflow in test_workflows:
        name = workflow.pop('name')
        print(f"\n{name}:")
        print(f"  Tasks: {len(workflow['tasks'])}")

        config = optimizer.optimize_workflow(workflow)

        print(f"  Recommended pattern: {config['pattern']}")
        print(f"  Agent count: {config['agent_count']}")
        print(f"  Confidence: {config['confidence']:.2f}")
        print(f"  Estimated time: {config['expected_performance']['estimated_time']:.2f}s")
        print(f"  Speedup: {config['expected_performance']['speedup']:.2f}x")

        results[name] = config

    return results


if __name__ == '__main__':
    results = run_optimizer_demo()

    # Save results
    import os
    os.makedirs('simulation_results', exist_ok=True)
    with open('simulation_results/workflow_optimizer.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("Optimizer demo complete!")
    print("Results saved to simulation_results/workflow_optimizer.json")
