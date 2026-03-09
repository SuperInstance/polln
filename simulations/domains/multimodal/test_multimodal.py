"""
Test suite for multi-modal simulations

Validates simulation components and generated configurations.
"""

import unittest
import numpy as np
import json
from pathlib import Path
import sys


class TestArchitectureSimulation(unittest.TestCase):
    """Test architecture simulation"""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).parent))
        from multimodal_architecture import (
            ArchitectureConfig, ArchitectureType, Modality,
            MockMultiModalEncoder, CrossModalFusion
        )
        self.ArchitectureConfig = ArchitectureConfig
        self.ArchitectureType = ArchitectureType
        self.Modality = Modality
        self.Encoder = MockMultiModalEncoder
        self.Fusion = CrossModalFusion

    def test_unified_encoder(self):
        """Test unified encoder"""
        config = self.ArchitectureConfig(
            name="test",
            architecture_type=self.ArchitectureType.UNIFIED,
            embedding_dim=768,
            encoder_type="transformer",
            fusion_strategy="attention",
            modalities=[self.Modality.TEXT, self.Modality.IMAGE]
        )
        encoder = self.Encoder(config)

        text_emb = encoder.encode(self.Modality.TEXT, np.random.randn(256))
        image_emb = encoder.encode(self.Modality.IMAGE, np.random.randn(256))

        self.assertEqual(len(text_emb), 768)
        self.assertEqual(len(image_emb), 768)

    def test_separate_encoder(self):
        """Test separate encoders"""
        config = self.ArchitectureConfig(
            name="test",
            architecture_type=self.ArchitectureType.SEPARATE,
            embedding_dim=768,
            encoder_type="modality_specific",
            fusion_strategy="attention",
            modalities=[self.Modality.TEXT, self.Modality.IMAGE]
        )
        encoder = self.Encoder(config)

        text_emb = encoder.encode(self.Modality.TEXT, np.random.randn(256))
        image_emb = encoder.encode(self.Modality.IMAGE, np.random.randn(256))

        self.assertEqual(len(text_emb), 768)
        self.assertEqual(len(image_emb), 768)

    def test_fusion(self):
        """Test fusion mechanisms"""
        config = self.ArchitectureConfig(
            name="test",
            architecture_type=self.ArchitectureType.UNIFIED,
            embedding_dim=768,
            encoder_type="transformer",
            fusion_strategy="attention",
            modalities=[self.Modality.TEXT, self.Modality.IMAGE]
        )
        fusion = self.Fusion(config)

        embeddings = {
            self.Modality.TEXT: np.random.randn(768),
            self.Modality.IMAGE: np.random.randn(768)
        }

        fused = fusion.fuse(embeddings)
        self.assertEqual(len(fused), 768)


class TestAttentionSimulation(unittest.TestCase):
    """Test attention simulation"""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).parent))
        from cross_modal_attention import (
            AttentionConfig, FusionStrategy,
            CrossModalAttention
        )
        self.AttentionConfig = AttentionConfig
        self.FusionStrategy = FusionStrategy
        self.Attention = CrossModalAttention

    def test_cross_attention(self):
        """Test cross-modal attention"""
        config = self.AttentionConfig(
            strategy=self.FusionStrategy.CO_ATTENTION,
            n_heads=8,
            dim_per_head=64
        )
        attention = self.Attention(config)

        embeddings = {
            'text': np.random.randn(768),
            'image': np.random.randn(512)
        }

        fused, importance = attention.compute_attention(
            'text', embeddings, embeddings
        )

        self.assertIsNotNone(fused)
        self.assertIn('text', importance)
        self.assertIn('image', importance)

    def test_early_fusion(self):
        """Test early fusion"""
        config = self.AttentionConfig(
            strategy=self.FusionStrategy.EARLY,
            n_heads=8,
            dim_per_head=64
        )
        attention = self.Attention(config)

        embeddings = {
            'text': np.random.randn(768),
            'image': np.random.randn(512)
        }

        fused, importance = attention.compute_attention(
            'text', embeddings, embeddings
        )

        self.assertIsNotNone(fused)
        self.assertEqual(len(importance), 2)


class TestEmbeddingSimulation(unittest.TestCase):
    """Test embedding simulation"""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).parent))
        from modality_embedding import (
            EmbeddingConfig, EmbeddingStrategy,
            ModalityEncoder, CrossModalRetriever
        )
        self.EmbeddingConfig = EmbeddingConfig
        self.EmbeddingStrategy = EmbeddingStrategy
        self.Encoder = ModalityEncoder
        self.Retriever = CrossModalRetriever

    def test_unified_embedding(self):
        """Test unified embedding"""
        config = self.EmbeddingConfig(
            strategy=self.EmbeddingStrategy.UNIFIED,
            embedding_dim=768
        )
        encoder = self.Encoder(config)

        text_emb = encoder.encode('text', np.random.randn(256))
        image_emb = encoder.encode('image', np.random.randn(256))

        self.assertEqual(len(text_emb), 768)
        self.assertEqual(len(image_emb), 768)

    def test_retrieval(self):
        """Test cross-modal retrieval"""
        config = self.EmbeddingConfig(
            strategy=self.EmbeddingStrategy.UNIFIED,
            embedding_dim=768
        )
        retriever = self.Retriever(config)

        query = np.random.randn(768)
        candidates = [np.random.randn(768) for _ in range(10)]

        results = retriever.retrieve(query, candidates, top_k=5)

        self.assertEqual(len(results), 5)
        self.assertIn(results[0], range(10))


class TestReasoningSimulation(unittest.TestCase):
    """Test reasoning simulation"""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).parent))
        from multimodal_reasoning import (
            ReasoningConfig, ReasoningTask,
            MultiModalReasoner
        )
        self.ReasoningConfig = ReasoningConfig
        self.ReasoningTask = ReasoningTask
        self.Reasoner = MultiModalReasoner

    def test_vqa_reasoning(self):
        """Test VQA reasoning"""
        config = self.ReasoningConfig(
            task=self.ReasoningTask.VQA,
            reasoning_steps=2
        )
        reasoner = self.Reasoner(config)

        inputs = {
            'image': np.random.randn(224, 224, 3),
            'text': np.random.randn(256)
        }

        answer, confidence, importance = reasoner.reason(inputs, "What is in the image?")

        self.assertIsNotNone(answer)
        self.assertGreater(confidence, 0)
        self.assertIn('text', importance)
        self.assertIn('image', importance)

    def test_multi_hop_reasoning(self):
        """Test multi-hop reasoning"""
        config = self.ReasoningConfig(
            task=self.ReasoningTask.MULTI_HOP,
            reasoning_steps=3
        )
        reasoner = self.Reasoner(config)

        inputs = {
            'text': np.random.randn(256),
            'image': np.random.randn(224, 224, 3),
            'audio': np.random.randn(16000)
        }

        answer, confidence, importance = reasoner.reason(inputs, "Why is this the case?")

        self.assertIsNotNone(answer)
        self.assertGreater(confidence, 0)


class TestGenerationSimulation(unittest.TestCase):
    """Test generation simulation"""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).parent))
        from generation_quality import (
            GenerationConfig, GenerationTask,
            MultiModalGenerator
        )
        self.GenerationConfig = GenerationConfig
        self.GenerationTask = GenerationTask
        self.Generator = MultiModalGenerator

    def test_image_captioning(self):
        """Test image captioning"""
        config = self.GenerationConfig(
            task=self.GenerationTask.IMAGE_CAPTIONING,
            temperature=0.8
        )
        generator = self.Generator(config)

        image = np.random.randn(224, 224, 3)
        caption, quality = generator.generate(image, 'image')

        self.assertIsNotNone(caption)
        self.assertGreater(quality, 0)
        self.assertLessEqual(quality, 1)

    def test_code_generation(self):
        """Test code generation"""
        config = self.GenerationConfig(
            task=self.GenerationTask.CODE_GENERATION,
            temperature=0.3
        )
        generator = self.Generator(config)

        text = np.random.randn(512)
        code, quality = generator.generate(text, 'text')

        self.assertIsNotNone(code)
        self.assertGreater(quality, 0)


class TestGeneratedConfig(unittest.TestCase):
    """Test generated configuration"""

    def test_config_exists(self):
        """Test that config file exists"""
        config_path = Path("src/domains/multimodal/config.ts")

        # Note: This test will fail until simulations are run
        # It's here to validate the output once generated
        if config_path.exists():
            content = config_path.read_text()
            self.assertIn("MULTIMODAL_DOMAIN_CONFIG", content)
            self.assertIn("architecture", content)
            self.assertIn("fusion", content)
            self.assertIn("agents", content)
            self.assertIn("generation", content)
        else:
            self.skipTest("Config not yet generated")


class TestResultsFiles(unittest.TestCase):
    """Test that result files are valid JSON"""

    def test_architecture_results(self):
        """Test architecture results"""
        results_path = Path("simulations/domains/multimodal/results/architecture_results.json")

        if results_path.exists():
            with open(results_path) as f:
                results = json.load(f)

            self.assertIsInstance(results, dict)
            # Check for expected modality combinations
            if results:
                first_key = list(results.keys())[0]
                self.assertIn('config', results[first_key])
                self.assertIn('metrics', results[first_key])
        else:
            self.skipTest("Results not yet generated")

    def test_attention_results(self):
        """Test attention results"""
        results_path = Path("simulations/domains/multimodal/results/attention_results.json")

        if results_path.exists():
            with open(results_path) as f:
                results = json.load(f)

            self.assertIsInstance(results, dict)
        else:
            self.skipTest("Results not yet generated")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestArchitectureSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestAttentionSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbeddingSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestReasoningSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerationSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratedConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestResultsFiles))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
