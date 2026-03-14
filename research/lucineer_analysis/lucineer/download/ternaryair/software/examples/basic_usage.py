"""
Example: Basic usage of TernaryAir SDK
"""

from ternaryair import TernaryAir, Simulator, Config

def basic_generation():
    """Basic text generation example."""
    print("=== Basic Generation ===")
    
    # Use simulator (no hardware needed)
    device = TernaryAir(backend=Simulator())
    
    # Simple generation
    response = device.generate("Hello, world!")
    print(f"Prompt: Hello, world!")
    print(f"Response: {response}")
    print()


def streaming_generation():
    """Streaming generation example."""
    print("=== Streaming Generation ===")
    
    device = TernaryAir(backend=Simulator())
    
    print("Prompt: Tell me about AI")
    print("Response: ", end="", flush=True)
    
    for token in device.stream("Tell me about AI", max_tokens=50):
        print(token, end="", flush=True)
    
    print("\n")


def batch_generation():
    """Batch generation example."""
    print("=== Batch Generation ===")
    
    device = TernaryAir(backend=Simulator())
    
    prompts = [
        "What is machine learning?",
        "What is deep learning?",
        "What is natural language processing?",
    ]
    
    responses = device.batch_generate(prompts, max_tokens=30)
    
    for prompt, response in zip(prompts, responses):
        print(f"Q: {prompt}")
        print(f"A: {response}")
        print("-" * 40)


def conversation_mode():
    """Conversation mode example."""
    print("=== Conversation Mode ===")
    
    device = TernaryAir(backend=Simulator())
    
    with device.conversation() as chat:
        # First message
        response1 = chat.send("My name is Alice.")
        print(f"User: My name is Alice.")
        print(f"AI: {response1}")
        
        # Second message - device should remember the name
        response2 = chat.send("What's my name?")
        print(f"User: What's my name?")
        print(f"AI: {response2}")
    
    # Context is lost after conversation ends
    print("\n(After conversation ends, context is lost)")
    print()


def custom_configuration():
    """Custom configuration example."""
    print("=== Custom Configuration ===")
    
    # Create custom config
    config = Config(
        max_tokens=100,
        temperature=0.8,
        top_p=0.95,
        top_k=50,
    )
    
    device = TernaryAir(config=config, backend=Simulator())
    
    response = device.generate("Write a haiku about programming:")
    print(f"Response: {response}")
    print()


def deterministic_mode():
    """Deterministic generation example."""
    print("=== Deterministic Mode ===")
    
    config = Config.deterministic()
    device = TernaryAir(config=config, backend=Simulator())
    
    # Same prompt should give same response
    prompt = "What is 2+2?"
    
    response1 = device.generate(prompt)
    response2 = device.generate(prompt)
    
    print(f"Prompt: {prompt}")
    print(f"Response 1: {response1}")
    print(f"Response 2: {response2}")
    print(f"Same response: {response1 == response2}")
    print()


def device_info():
    """Device information example."""
    print("=== Device Information ===")
    
    device = TernaryAir(backend=Simulator())
    
    info = device.info
    status = device.status
    
    print(f"Model: {info.model}")
    print(f"Firmware: {info.firmware_version}")
    print(f"Serial: {info.serial_number}")
    print(f"Memory: {info.memory_mb} MB")
    print(f"Max Context: {info.max_tokens} tokens")
    print()
    print(f"Status: {'Ready' if status.is_ready else 'Busy'}")
    print(f"Temperature: {status.temperature_c:.1f}°C")
    print(f"Power: {status.power_w:.1f}W")
    print()


def context_manager():
    """Context manager example."""
    print("=== Context Manager ===")
    
    # Device automatically disconnects when done
    with TernaryAir(backend=Simulator()) as device:
        response = device.generate("Hello!")
        print(f"Response: {response}")
    
    print("Device disconnected automatically")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("TernaryAir SDK Examples")
    print("=" * 60)
    print()
    
    basic_generation()
    streaming_generation()
    batch_generation()
    conversation_mode()
    custom_configuration()
    deterministic_mode()
    device_info()
    context_manager()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)
