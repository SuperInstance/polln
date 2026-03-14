"""
Command-line interface for TernaryAir.
"""

import argparse
import sys
from typing import Optional

from ternaryair import TernaryAir, Simulator, __version__


def cmd_chat(args: argparse.Namespace) -> None:
    """Interactive chat mode."""
    print("TernaryAir Chat (type 'exit' to quit)")
    print("-" * 40)
    
    device = TernaryAir(backend=Simulator() if args.simulator else None)
    
    with device.conversation() as chat:
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ('exit', 'quit', 'q'):
                    print("Goodbye!")
                    break
                if not user_input:
                    continue
                
                print("\nTernaryAir: ", end="", flush=True)
                if args.stream:
                    for token in device.stream(user_input, max_tokens=args.max_tokens):
                        print(token, end="", flush=True)
                    print()
                else:
                    response = chat.send(user_input, max_tokens=args.max_tokens)
                    print(response)
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


def cmd_complete(args: argparse.Namespace) -> None:
    """Single completion mode."""
    device = TernaryAir(backend=Simulator() if args.simulator else None)
    
    if args.stream:
        for token in device.stream(args.prompt, max_tokens=args.max_tokens):
            print(token, end="", flush=True)
        print()
    else:
        response = device.generate(args.prompt, max_tokens=args.max_tokens)
        print(response)


def cmd_stream(args: argparse.Namespace) -> None:
    """Stream mode."""
    device = TernaryAir(backend=Simulator() if args.simulator else None)
    
    for token in device.stream(args.prompt, max_tokens=args.max_tokens):
        print(token, end="", flush=True)
    print()


def cmd_info(args: argparse.Namespace) -> None:
    """Show device info."""
    device = TernaryAir(backend=Simulator() if args.simulator else None)
    
    info = device.info
    status = device.status
    
    print("Device Information")
    print("-" * 40)
    print(f"Model:            {info.model}")
    print(f"Firmware:         {info.firmware_version}")
    print(f"Serial:           {info.serial_number}")
    print(f"Memory:           {info.memory_mb} MB")
    print(f"Max Context:      {info.max_tokens} tokens")
    print()
    print("Status")
    print("-" * 40)
    print(f"Ready:            {status.is_ready}")
    print(f"Temperature:      {status.temperature_c:.1f}°C")
    print(f"Power:            {status.power_w:.1f}W")
    print(f"Tokens Generated: {status.tokens_generated}")
    print(f"Inferences:       {status.inference_count}")
    print(f"Uptime:           {status.uptime_s:.1f}s")


def cmd_batch(args: argparse.Namespace) -> None:
    """Batch processing mode."""
    device = TernaryAir(backend=Simulator() if args.simulator else None)
    
    # Read prompts from file
    with open(args.input, 'r') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    print(f"Processing {len(prompts)} prompts...")
    
    results = device.batch_generate(prompts, max_tokens=args.max_tokens)
    
    # Write results to output file
    with open(args.output, 'w') as f:
        for prompt, result in zip(prompts, results):
            f.write(f"Prompt: {prompt}\n")
            f.write(f"Response: {result}\n")
            f.write("-" * 40 + "\n")
    
    print(f"Results written to {args.output}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="ternaryair",
        description="TernaryAir - Open Source Air-Gapped Inference Hardware",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--simulator", action="store_true", help="Use software simulator")
    parser.add_argument("--max-tokens", type=int, default=256, help="Maximum tokens to generate")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Interactive chat mode")
    chat_parser.add_argument("--stream", action="store_true", help="Stream output")
    chat_parser.set_defaults(func=cmd_chat)
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Single completion")
    complete_parser.add_argument("prompt", help="Input prompt")
    complete_parser.add_argument("--stream", action="store_true", help="Stream output")
    complete_parser.set_defaults(func=cmd_complete)
    
    # Stream command
    stream_parser = subparsers.add_parser("stream", help="Stream generation")
    stream_parser.add_argument("prompt", help="Input prompt")
    stream_parser.set_defaults(func=cmd_stream)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show device info")
    info_parser.set_defaults(func=cmd_info)
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch processing")
    batch_parser.add_argument("input", help="Input file with prompts")
    batch_parser.add_argument("output", help="Output file for results")
    batch_parser.set_defaults(func=cmd_batch)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()
