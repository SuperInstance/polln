#!/usr/bin/env python3
"""
SuperInstance SDK - Hello World Example

This example demonstrates the basic usage of the SuperInstance SDK
for running LLM inference on SuperInstance mask-locked hardware.

Usage:
    # With physical device:
    python hello_world.py

    # With simulation mode (no hardware required):
    SUPERINSTANCE_SIMULATE=1 python hello_world.py
"""

import os
import sys

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from superinstance import Device, GenerationConfig


def basic_inference():
    """Basic inference example - the simplest way to generate text."""
    print("=" * 60)
    print("Example 1: Basic Inference")
    print("=" * 60)

    # Auto-detect and connect to device
    # This finds the first available SuperInstance device
    device = Device()

    print(f"Connected to: {device.info()}")

    # Load model from inserted cartridge
    model = device.load_cartridge()
    print(f"Loaded model: {model.name} v{model.version}")
    print()

    # Generate text
    prompt = "Hello, I am"
    print(f"Prompt: {prompt}")

    result = model.generate(prompt)

    print(f"Response: {result.text}")
    print()
    print(f"Generated {result.generated_tokens} tokens in {result.total_time_ms:.0f}ms")
    print(f"Speed: {result.tokens_per_second:.1f} tokens/second")
    print(f"Energy used: {result.energy_millijoules:.1f} mJ")

    # Clean up
    device.close()


def streaming_example():
    """Streaming generation example - tokens appear in real-time."""
    print("\n" + "=" * 60)
    print("Example 2: Streaming Output")
    print("=" * 60)

    with Device() as device:
        model = device.load_cartridge()

        prompt = "Write a short story about a robot:"
        print(f"Prompt: {prompt}")
        print("Response: ", end="", flush=True)

        # Stream tokens as they're generated
        for token in model.generate_stream(prompt):
            print(token, end="", flush=True)

        print()  # Newline after streaming


def chat_example():
    """Chat-style conversation example."""
    print("\n" + "=" * 60)
    print("Example 3: Chat Conversation")
    print("=" * 60)

    with Device() as device:
        model = device.load_cartridge()

        # Build conversation history
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant running on SuperInstance hardware."},
            {"role": "user", "content": "What is machine learning?"},
        ]

        print("User: What is machine learning?")
        response = model.chat(messages)

        print(f"Assistant: {response.text}")

        # Continue conversation
        messages.append({"role": "assistant", "content": response.text})
        messages.append({"role": "user", "content": "Can you give me a simple example?"})

        print("\nUser: Can you give me a simple example?")
        response = model.chat(messages)
        print(f"Assistant: {response.text}")


def generation_config_example():
    """Generation configuration examples."""
    print("\n" + "=" * 60)
    print("Example 4: Generation Configuration")
    print("=" * 60)

    with Device() as device:
        model = device.load_cartridge()

        prompt = "Once upon a time"

        # Deterministic generation (temperature=0)
        print("\n--- Deterministic (temperature=0) ---")
        config = GenerationConfig(temperature=0, max_tokens=50)
        result1 = model.generate(prompt, config)
        result2 = model.generate(prompt, config)
        print(f"Run 1: {result1.text[:80]}...")
        print(f"Run 2: {result2.text[:80]}...")
        print(f"Same result: {result1.text == result2.text}")

        # Creative generation (high temperature)
        print("\n--- Creative (temperature=1.2) ---")
        config = GenerationConfig(temperature=1.2, top_p=0.95, max_tokens=50)
        for i in range(3):
            result = model.generate(prompt, config)
            print(f"Run {i+1}: {result.text[:80]}...")

        # With stop sequences
        print("\n--- With stop sequences ---")
        config = GenerationConfig(
            temperature=0.5,
            stop_sequences=["\n\n", "The End"],
            max_tokens=200
        )
        result = model.generate("Tell me a story:", config)
        print(f"Response: {result.text}")
        print(f"Finish reason: {result.finish_reason}")


def device_info_example():
    """Device information and monitoring example."""
    print("\n" + "=" * 60)
    print("Example 5: Device Information")
    print("=" * 60)

    # List all available devices
    devices = Device.list_devices()
    print(f"Found {len(devices)} device(s):")
    for path in devices:
        print(f"  - {path}")

    print()

    # Connect and get detailed info
    with Device() as device:
        info = device.info()

        print(f"Device Type: {info.device_type.value}")
        print(f"Serial Number: {info.serial_number}")
        print(f"Firmware Version: {info.firmware_version}")
        print(f"USB Speed: {info.usb_speed}")
        print()

        if info.cartridge_inserted:
            print(f"Cartridge: {info.cartridge_model} v{info.cartridge_version}")
        else:
            print("No cartridge inserted")

        print()
        print(f"Temperature: {info.temperature_celsius:.1f}°C")
        print(f"Power: {info.power_watts:.1f}W")
        print(f"Uptime: {info.uptime_seconds}s")
        print(f"Total Inferences: {info.total_inferences}")
        print(f"Total Tokens Generated: {info.total_tokens_generated}")


def error_handling_example():
    """Error handling example."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    from superinstance import (
        DeviceNotFoundError,
        DeviceBusyError,
        NoCartridgeError,
        ContextLengthExceededError,
    )

    try:
        # This will fail if no device and no simulation mode
        device = Device()
        model = device.load_cartridge()

        # Try to generate with extremely long prompt
        very_long_prompt = "word " * 10000  # Way over context limit

        try:
            model.generate(very_long_prompt)
        except ContextLengthExceededError as e:
            print(f"Context limit exceeded: {e.message}")
            print(f"  Tokens in prompt: {e.tokens}")
            print(f"  Max allowed: {e.max_tokens}")

        device.close()

    except DeviceNotFoundError:
        print("No device found!")
        print("Set SUPERINSTANCE_SIMULATE=1 for demo mode.")

    except NoCartridgeError:
        print("No cartridge inserted!")
        print("Please insert a model module.")


def main():
    """Run all examples."""
    print("SuperInstance SDK - Hello World Examples")
    print("=" * 60)

    # Check for simulation mode
    simulate = os.environ.get("SUPERINSTANCE_SIMULATE", "0") == "1"
    if simulate:
        print("Running in SIMULATION mode (no hardware required)")
        print()
    else:
        print("Running with physical device")
        print("Set SUPERINSTANCE_SIMULATE=1 for simulation mode")
        print()

    try:
        basic_inference()
        streaming_example()
        chat_example()
        generation_config_example()
        device_info_example()
        error_handling_example()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nTo run without hardware, use:")
        print("  SUPERINSTANCE_SIMULATE=1 python hello_world.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
