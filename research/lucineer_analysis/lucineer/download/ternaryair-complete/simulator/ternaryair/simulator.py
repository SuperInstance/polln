"""
TernaryAir Simulator - Working implementation

This is a simplified but functional simulator that demonstrates
ternary inference behavior. It shows:
1. Ternary weight encoding {-1, 0, +1}
2. RAU-style computation (add/subtract, no multiply)
3. OpenAI-compatible API
"""

import time
import hashlib
import random
from typing import Optional, List, Dict, Generator, Union
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    params: str
    layers: int
    dim: int
    vocab_size: int = 32000


# Available models
MODELS = {
    "debug-tiny": ModelConfig("debug-tiny", "125M", 6, 384, 8000),
    "tiny": ModelConfig("tiny", "500M", 12, 512, 16000),
    "small": ModelConfig("small", "1.5B", 18, 768, 32000),
    "medium": ModelConfig("medium", "3B", 24, 1024, 32000),
}


class TernaryWeights:
    """
    Simulated ternary weights.
    
    In real hardware, these are mask-locked in metal layers.
    Here we simulate them for software testing.
    """
    
    def __init__(self, rows: int, cols: int, seed: Optional[int] = None):
        self.rows = rows
        self.cols = cols
        if seed is not None:
            random.seed(seed)
        # Generate ternary weights: {-1, 0, +1}
        self._data = [
            [random.choice([-1, 0, 1]) for _ in range(cols)]
            for _ in range(rows)
        ]
        
        # Track stats
        self._nonzero = sum(1 for row in self._data for w in row if w != 0)
    
    def forward(self, inputs: List[float]) -> List[float]:
        """
        RAU forward pass.
        
        Traditional: output = input × weight
        Ternary: output = rotate(input, weight)
            +1: add input
             0: skip (add nothing)
            -1: subtract input
        """
        results = []
        for row in self._data:
            acc = 0.0
            for w, x in zip(row, inputs):
                if w == 1:
                    acc += x
                elif w == -1:
                    acc -= x
                # w == 0: no operation
            results.append(acc)
        return results
    
    @property
    def sparsity(self) -> float:
        """Fraction of zero weights"""
        total = self.rows * self.cols
        zeros = total - self._nonzero
        return zeros / total if total > 0 else 0


class Simulator:
    """
    TernaryAir inference simulator.
    
    Usage:
        sim = Simulator(model="tiny")
        response = sim.generate("Hello, world!")
        print(response)
    """
    
    def __init__(
        self,
        model: str = "tiny",
        seed: Optional[int] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize simulator.
        
        Args:
            model: Model size (debug-tiny, tiny, small, medium)
            seed: Random seed for reproducibility
            temperature: Sampling temperature
        """
        if model not in MODELS:
            print(f"Warning: Unknown model '{model}', using 'tiny'")
            model = "tiny"
        
        self.config = MODELS[model]
        self.seed = seed
        self.temperature = temperature
        
        # Initialize weights for each layer
        self._layers: Dict[str, TernaryWeights] = {}
        self._init_weights()
        
        # Performance tracking
        self._stats = {
            "tokens_generated": 0,
            "inference_time_ms": 0.0,
        }
    
    def _init_weights(self):
        """Initialize simulated ternary weights"""
        dim = self.config.dim
        for layer in range(self.config.layers):
            base_seed = layer * 1000 + (self.seed or 0)
            
            # Attention projections (simplified)
            self._layers[f"L{layer}_Q"] = TernaryWeights(dim, dim, base_seed)
            self._layers[f"L{layer}_K"] = TernaryWeights(dim, dim, base_seed + 1)
            self._layers[f"L{layer}_V"] = TernaryWeights(dim, dim, base_seed + 2)
            self._layers[f"L{layer}_O"] = TernaryWeights(dim, dim, base_seed + 3)
            
            # FFN (simplified)
            ffn_dim = dim * 4
            self._layers[f"L{layer}_FFN1"] = TernaryWeights(dim, ffn_dim, base_seed + 10)
            self._layers[f"L{layer}_FFN2"] = TernaryWeights(ffn_dim, dim, base_seed + 11)
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
        
        Returns:
            Generated text
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self.temperature
        
        # Tokenize (simplified)
        tokens = self._tokenize(prompt)
        
        # Generate new tokens
        generated = []
        for _ in range(max_tokens):
            # Simulate forward pass through layers
            hidden = self._forward(tokens)
            
            # Sample next token
            next_token = self._sample(hidden, temp)
            generated.append(next_token)
            tokens.append(next_token)
            
            # Check for end
            if random.random() < 0.02:
                break
        
        # Track stats
        elapsed = (time.time() - start_time) * 1000
        self._stats["tokens_generated"] += len(generated)
        self._stats["inference_time_ms"] += elapsed
        
        return self._detokenize(generated)
    
    def stream(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """Stream tokens as they're generated"""
        temp = temperature if temperature is not None else self.temperature
        tokens = self._tokenize(prompt)
        
        for _ in range(max_tokens):
            hidden = self._forward(tokens)
            next_token = self._sample(hidden, temp)
            tokens.append(next_token)
            
            # Simulate token latency
            time.sleep(0.01)
            
            yield self._detokenize([next_token])
            
            if random.random() < 0.02:
                break
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 100,
    ) -> str:
        """Multi-turn chat"""
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"[{role.upper()}]: {content}\n"
        prompt += "[ASSISTANT]:"
        return self.generate(prompt, max_tokens)
    
    def embed(self, text: str) -> List[float]:
        """Generate text embeddings"""
        # Simple hash-based embedding
        h = hashlib.sha256(text.encode()).digest()
        dim = self.config.dim
        embedding = []
        for i in range(dim):
            val = (h[i % 32] - 128) / 128.0
            embedding.append(val)
        return embedding
    
    def _tokenize(self, text: str) -> List[int]:
        """Simple tokenization"""
        # Word-based tokenization for demo
        words = text.lower().split()
        tokens = []
        for word in words:
            token = hash(word) % self.config.vocab_size
            tokens.append(token)
        return tokens
    
    def _detokenize(self, tokens: List[int]) -> str:
        """Convert tokens to text"""
        # Simple word bank for demo
        words = [
            "the", "ternary", "inference", "system", "processes", "data",
            "using", "weight", "values", "of", "negative", "one", "zero",
            "positive", "which", "eliminates", "multiplication", "and",
            "reduces", "power", "consumption", "significantly", "while",
            "maintaining", "reasonable", "accuracy", "for", "many", "tasks",
            "this", "approach", "is", "particularly", "suited", "to", "edge",
            "devices", "where", "efficiency", "matters", "most", "the",
            "rotation", "accumulate", "unit", "replaces", "expensive",
            "multipliers", "with", "simple", "sign", "manipulation",
            "achieving", "dramatic", "reductions", "in", "gate", "count"
        ]
        
        result = []
        for i, token in enumerate(tokens):
            word = words[token % len(words)]
            if i == 0:
                word = word.capitalize()
            result.append(word)
        
        return " ".join(result) + "."
    
    def _forward(self, tokens: List[int]) -> List[float]:
        """Simulate forward pass"""
        if self.seed is not None:
            random.seed(self.seed)
        
        # Create hidden state
        dim = self.config.dim
        hidden = [0.0] * dim
        
        for token in tokens:
            for i in range(dim):
                hidden[i] += (token % 100) / 100.0
        
        # Process through layers (simplified)
        for name, weights in self._layers.items():
            if "FFN" not in name:
                hidden = weights.forward(hidden)
        
        return hidden
    
    def _sample(self, hidden: List[float], temperature: float) -> int:
        """Sample next token from hidden state"""
        # Simplified sampling
        score = sum(hidden) / len(hidden)
        
        # Add temperature-controlled noise
        if temperature > 0:
            score += random.gauss(0, temperature)
        
        # Map to token
        token = int(abs(score) * 1000) % self.config.vocab_size
        return token
    
    def stats(self) -> Dict:
        """Get performance statistics"""
        avg_speed = (
            self._stats["tokens_generated"] / (self._stats["inference_time_ms"] / 1000)
            if self._stats["inference_time_ms"] > 0 else 0
        )
        
        # Calculate overall sparsity
        total_sparsity = sum(w.sparsity for w in self._layers.values()) / len(self._layers)
        
        return {
            "model": self.config.name,
            "params": self.config.params,
            "tokens_generated": self._stats["tokens_generated"],
            "inference_time_ms": self._stats["inference_time_ms"],
            "avg_tokens_per_second": avg_speed,
            "weight_sparsity": total_sparsity,
            "layers": len(self._layers),
        }


class TernaryAir:
    """
    Main TernaryAir interface.
    
    Provides OpenAI-compatible API over the simulator.
    """
    
    def __init__(self, model: str = "tiny", **kwargs):
        """
        Initialize TernaryAir.
        
        Args:
            model: Model size (tiny, small, medium)
            **kwargs: Additional simulator options
        """
        self._sim = Simulator(model=model, **kwargs)
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate text from prompt"""
        if stream:
            return self._sim.stream(prompt, max_tokens, temperature)
        return self._sim.generate(prompt, max_tokens, temperature)
    
    def stream(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """Stream tokens"""
        return self._sim.stream(prompt, max_tokens, temperature)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 100,
    ) -> str:
        """Chat interface"""
        return self._sim.chat(messages, max_tokens)
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings"""
        return self._sim.embed(text)


def create_device(model: str = "tiny") -> TernaryAir:
    """Factory function to create TernaryAir instance"""
    return TernaryAir(model=model)
