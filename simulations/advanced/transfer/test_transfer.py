"""
POLLN Transfer Learning Tests
==============================

Comprehensive tests for transfer learning simulation modules.
Tests individual components and integration scenarios.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import json


# Import simulation modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from task_similarity import (
    Task, TaskDomain, SimilarityCalculator, TaskSimilarityMatrix,
    TransferEfficiencyPredictor, create_standard_task_set
)
from fine_tuning_strategies import (
    FineTuningMethod, FineTuningConfig, FineTuningResult,
    FineTuningSimulator, FineTuningOptimizer, create_standard_strategies
)
from succession_efficiency import (
    DistillationMethod, SuccessionConfig, KnowledgePacket,
    SuccessionResult, SuccessionSimulator, SuccessionAnalyzer
)
from cross_colony_transfer import (
    FederationMethod, ColonyKnowledge, FederationConfig,
    FederationResult, CrossColonySimulator, FederationAnalyzer
)
from negative_transfer import (
    TransferOutcome, ProtectionMechanism, TransferScenario,
    TransferResult, ProtectionConfig, NegativeTransferSimulator,
    NegativeTransferAnalyzer
)


# ============================================================================
# Task Similarity Tests
# ============================================================================

class TestTaskSimilarity:
    """Test task similarity computation"""

    def test_task_creation(self):
        """Test creating tasks"""
        task = Task(
            id="test_task",
            name="Test Task",
            domain=TaskDomain.REASONING,
            description="A test reasoning task",
            required_capabilities=["reasoning", "comprehension"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.7,
            data_requirements={"dataset_size": 10000, "diversity": 0.5}
        )

        assert task.id == "test_task"
        assert task.domain == TaskDomain.REASONING
        assert len(task.required_capabilities) == 2

    def test_semantic_similarity(self):
        """Test semantic similarity calculation"""
        calculator = SimilarityCalculator()

        task1 = Task(
            id="code_review",
            name="Code Review",
            domain=TaskDomain.CODING,
            description="Review code for bugs",
            required_capabilities=["syntax_analysis"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.7,
            data_requirements={}
        )

        task2 = Task(
            id="code_generation",
            name="Code Generation",
            domain=TaskDomain.CODING,
            description="Generate code from descriptions",
            required_capabilities=["generation"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.8,
            data_requirements={}
        )

        similarity = calculator.semantic_similarity(task1, task2)
        assert 0 <= similarity <= 1

    def test_capability_overlap(self):
        """Test capability overlap calculation"""
        calculator = SimilarityCalculator()

        task1 = Task(
            id="task1",
            name="Task 1",
            domain=TaskDomain.REASONING,
            description="Test",
            required_capabilities=["reasoning", "comprehension"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.5,
            data_requirements={}
        )

        task2 = Task(
            id="task2",
            name="Task 2",
            domain=TaskDomain.REASONING,
            description="Test",
            required_capabilities=["reasoning", "generation"],
            architecture_pattern="decoder-only",
            input_modality="text",
            output_modality="text",
            complexity_score=0.5,
            data_requirements={}
        )

        overlap = calculator.capability_overlap(task1, task2)
        # 1 common capability out of 3 total
        assert overlap == pytest.approx(1/3, rel=0.1)

    def test_similarity_matrix(self):
        """Test similarity matrix creation"""
        tasks = create_standard_task_set()
        matrix = TaskSimilarityMatrix(tasks)
        matrix.compute_all_similarities()

        assert matrix.similarity_matrix.shape == (len(tasks), len(tasks))

        # Check symmetry
        assert np.allclose(
            matrix.similarity_matrix,
            matrix.similarity_matrix.T,
            atol=1e-10
        )

        # Check diagonal is 1
        assert np.allclose(np.diag(matrix.similarity_matrix), 1.0)


# ============================================================================
# Fine-Tuning Strategy Tests
# ============================================================================

class TestFineTuningStrategies:
    """Test fine-tuning strategy optimization"""

    def test_strategy_creation(self):
        """Test creating fine-tuning configs"""
        config = FineTuningConfig(
            method=FineTuningMethod.LORA,
            learning_rate=0.001,
            epochs=50,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            rank=8,
            alpha=16
        )

        assert config.method == FineTuningMethod.LORA
        assert config.rank == 8
        assert config.alpha == 16

    def test_parameter_estimation(self):
        """Test trainable parameter estimation"""
        simulator = FineTuningSimulator(base_params=7_000_000_000)

        # LoRA should have far fewer params
        lora_config = FineTuningConfig(
            method=FineTuningMethod.LORA,
            learning_rate=0.001,
            epochs=50,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            rank=8,
            alpha=16
        )

        lora_params = simulator.estimate_trainable_params(lora_config)

        # Full fine-tuning
        full_config = FineTuningConfig(
            method=FineTuningMethod.FULL_FINETUNE,
            learning_rate=0.0001,
            epochs=50,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01
        )

        full_params = simulator.estimate_trainable_params(full_config)

        assert lora_params < full_params
        assert lora_params > 0

    def test_finetuning_simulation(self):
        """Test fine-tuning simulation"""
        simulator = FineTuningSimulator()

        config = FineTuningConfig(
            method=FineTuningMethod.LORA,
            learning_rate=0.001,
            epochs=50,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            rank=8,
            alpha=16
        )

        result = simulator.simulate_finetuning(
            config=config,
            task_similarity=0.8,
            source_performance=0.85
        )

        assert 0 <= result.target_performance <= 1
        assert 0 <= result.forgetting_ratio <= 1
        assert result.trainable_params > 0
        assert result.epochs_to_convergence > 0


# ============================================================================
# Succession Efficiency Tests
# ============================================================================

class TestSuccessionEfficiency:
    """Test knowledge succession protocol"""

    def test_knowledge_packet_creation(self):
        """Test creating knowledge packets"""
        patterns = {
            "pattern_1": np.random.randn(128),
            "pattern_2": np.random.randn(128)
        }
        values = {
            "pattern_1": 0.8,
            "pattern_2": 0.6
        }

        packet = KnowledgePacket(
            patterns=patterns,
            values=values,
            embeddings=np.random.randn(512),
            pattern_count=2,
            compression_ratio=1.0,
            source_performance=0.85
        )

        assert packet.pattern_count == 2
        assert packet.source_performance == 0.85

    def test_knowledge_compression(self):
        """Test knowledge compression"""
        simulator = SuccessionSimulator()

        # Create knowledge
        knowledge = simulator.create_teacher_knowledge(
            num_patterns=1000,
            teacher_performance=0.85
        )

        assert knowledge.pattern_count == 1000

        # Compress to 50%
        compressed = simulator.compress_knowledge(knowledge, 0.5)

        assert compressed.pattern_count == 500
        assert compressed.compression_ratio == 0.5

    def test_succession_simulation(self):
        """Test succession simulation"""
        simulator = SuccessionSimulator()

        config = SuccessionConfig(
            distillation_method=DistillationMethod.FEATURE_BASED,
            temperature=3.0,
            alpha=0.7,
            epochs=50
        )

        teacher_knowledge = simulator.create_teacher_knowledge(
            num_patterns=1000,
            teacher_performance=0.85
        )

        result = simulator.simulate_succession(
            config=config,
            teacher_knowledge=teacher_knowledge,
            student_initial_performance=0.3
        )

        assert result.knowledge_retention >= 0
        assert result.student_performance_after >= result.student_performance_before
        assert 0 <= result.pattern_preservation <= 1


# ============================================================================
# Cross-Colony Transfer Tests
# ============================================================================

class TestCrossColonyTransfer:
    """Test cross-colony knowledge transfer"""

    def test_colony_creation(self):
        """Test creating colonies"""
        simulator = CrossColonySimulator()

        colony = simulator.create_colony(
            colony_id="test_colony",
            task_specialization="code_review",
            base_performance=0.7
        )

        assert colony.colony_id == "test_colony"
        assert colony.task_specialization == "code_review"
        assert colony.performance >= 0.6  # Allow some noise

    def test_colony_similarity(self):
        """Test colony similarity computation"""
        simulator = CrossColonySimulator()

        colony1 = simulator.create_colony(
            colony_id="colony_1",
            task_specialization="code_review"
        )

        colony2 = simulator.create_colony(
            colony_id="colony_2",
            task_specialization="code_review"
        )

        similarity = simulator.compute_colony_similarity(colony1, colony2)

        assert 0 <= similarity <= 1
        # Same specialization should be similar
        assert similarity > 0.5

    def test_federation_simulation(self):
        """Test federation simulation"""
        simulator = CrossColonySimulator()

        colonies = []
        for i in range(3):
            colony = simulator.create_colony(
                colony_id=f"colony_{i}",
                task_specialization=["code_review", "sentiment_analysis", "math"][i]
            )
            colonies.append(colony)

        config = FederationConfig(
            method=FederationMethod.WEIGHTED_AVERAGING,
            min_colonies=2,
            weight_by_performance=True
        )

        result = simulator.simulate_federation(colonies, config)

        assert len(result.colony_performances_after) == len(colonies)
        assert result.knowledge_diversity >= 0


# ============================================================================
# Negative Transfer Tests
# ============================================================================

class TestNegativeTransfer:
    """Test negative transfer detection"""

    def test_scenario_creation(self):
        """Test creating transfer scenarios"""
        simulator = NegativeTransferSimulator()

        scenario = simulator.create_scenario(
            source_task="code_review",
            target_task="sentiment_analysis",
            task_similarity=0.3
        )

        assert scenario.source_task == "code_review"
        assert scenario.target_task == "sentiment_analysis"
        assert scenario.task_similarity == 0.3

    def test_negative_transfer_detection(self):
        """Test negative transfer detection"""
        simulator = NegativeTransferSimulator()

        # Low similarity scenario - likely negative
        scenario = simulator.create_scenario(
            source_task="code_review",
            target_task="sentiment_analysis",
            task_similarity=0.1
        )

        result = simulator.simulate_transfer(scenario)

        # Check that we can detect negative transfer
        if result.is_negative():
            assert result.performance_delta < 0

    def test_protection_mechanism(self):
        """Test protection mechanism"""
        simulator = NegativeTransferSimulator()

        scenario = simulator.create_scenario(
            source_task="code_review",
            target_task="sentiment_analysis",
            task_similarity=0.2  # Below threshold
        )

        protection_config = ProtectionConfig(
            enabled=True,
            similarity_threshold=0.3
        )

        result = simulator.simulate_transfer(scenario, protection_config)

        # Should be prevented
        assert result.prevented
        assert result.performance_delta == 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestTransferIntegration:
    """Integration tests for transfer learning system"""

    def test_end_to_end_pipeline(self):
        """Test complete transfer learning pipeline"""

        # 1. Create tasks
        tasks = create_standard_task_set()

        # 2. Compute similarity
        matrix = TaskSimilarityMatrix(tasks)
        matrix.compute_all_similarities()

        # 3. Get fine-tuning strategy
        strategies = create_standard_strategies()
        assert len(strategies) > 0

        # 4. Simulate succession
        succession_sim = SuccessionSimulator()
        knowledge = succession_sim.create_teacher_knowledge(1000, 0.85)

        config = SuccessionConfig(
            distillation_method=DistillationMethod.FEATURE_BASED,
            temperature=3.0,
            alpha=0.7
        )

        result = succession_sim.simulate_succession(config, knowledge)
        assert result.knowledge_retention > 0

    def test_file_generation(self):
        """Test that all output files can be generated"""

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Test that we can write JSON configs
            test_config = {"test": "value", "number": 42}

            config_file = tmppath / "test_config.json"
            with open(config_file, 'w') as f:
                json.dump(test_config, f)

            assert config_file.exists()

            # Test that we can write CSV results
            test_df = pd.DataFrame({
                'similarity': [0.1, 0.5, 0.9],
                'performance': [0.6, 0.7, 0.8]
            })

            csv_file = tmppath / "test_results.csv"
            test_df.to_csv(csv_file, index=False)

            assert csv_file.exists()


# ============================================================================
# Performance Tests
# ============================================================================

class TestTransferPerformance:
    """Performance benchmarks for transfer learning"""

    def test_similarity_matrix_performance(self):
        """Test similarity matrix computation performance"""
        import time

        tasks = create_standard_task_set()
        matrix = TaskSimilarityMatrix(tasks)

        start = time.time()
        matrix.compute_all_similarities()
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 5.0

    def test_batch_simulation_performance(self):
        """Test batch simulation performance"""
        import time

        simulator = FineTuningSimulator()

        strategies = create_standard_strategies()[:3]  # Test 3 strategies
        similarities = [0.3, 0.5, 0.7]

        start = time.time()
        for strategy in strategies:
            for similarity in similarities:
                simulator.simulate_finetuning(strategy, similarity)
        duration = time.time() - start

        # Should complete 9 simulations quickly
        assert duration < 10.0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
