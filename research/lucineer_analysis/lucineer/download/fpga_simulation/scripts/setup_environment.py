#!/usr/bin/env python3
"""
SuperInstance.AI Mask-Locked Inference Chip
FPGA Simulation Environment Setup Script

This script installs all dependencies and sets up the simulation environment.

Usage:
    python3 scripts/setup_environment.py [--sim-only] [--synth-only]

Requirements:
    - Linux (Ubuntu 22.04 recommended) or macOS
    - Python 3.8+
    - 8GB+ RAM recommended

Author: VP Manufacturing, SuperInstance.AI
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
import argparse
import shutil

# Color output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_step(text):
    print(f"{Colors.BLUE}[STEP]{Colors.ENDC} {text}")

def print_success(text):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {text}")

def print_error(text):
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {text}")

def run_command(cmd, check=True, capture=False):
    """Run shell command with error handling"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True, "", ""
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def check_os():
    """Check operating system compatibility"""
    system = platform.system()
    if system == "Linux":
        distro = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("NAME="):
                        distro = line.split("=")[1].strip('"')
                        break
        except:
            pass
        print_success(f"Detected: {distro} (Linux)")
        return "linux"
    elif system == "Darwin":
        print_success(f"Detected: macOS")
        return "macos"
    else:
        print_warning(f"Untested OS: {system}")
        return "other"

def install_linux_packages():
    """Install required Linux packages"""
    print_header("Installing Linux System Packages")
    
    packages = [
        "build-essential",
        "clang",
        "verilator",
        "iverilog",
        "gtkwave",
        "python3-dev",
        "python3-pip",
        "git",
        "cmake",
        "ninja-build",
    ]
    
    print_step("Updating package lists...")
    run_command("sudo apt update")
    
    print_step(f"Installing: {', '.join(packages)}")
    run_command(f"sudo apt install -y {' '.join(packages)}")
    
    print_success("System packages installed")

def install_macos_packages():
    """Install required macOS packages via Homebrew"""
    print_header("Installing macOS System Packages")
    
    # Check for Homebrew
    if not shutil.which("brew"):
        print_error("Homebrew not found. Please install from https://brew.sh")
        sys.exit(1)
    
    packages = [
        "verilator",
        "icarus-verilog",
        "gtkwave",
        "cmake",
        "ninja",
    ]
    
    print_step(f"Installing: {', '.join(packages)}")
    run_command(f"brew install {' '.join(packages)}")
    
    print_success("System packages installed")

def install_python_packages():
    """Install Python packages"""
    print_header("Installing Python Packages")
    
    packages = [
        "cocotb",
        "cocotb-test",
        "numpy",
        "pytest",
        "pyyaml",
        "matplotlib",
    ]
    
    print_step(f"Installing: {', '.join(packages)}")
    run_command(f"pip install {' '.join(packages)}")
    
    print_success("Python packages installed")

def setup_workspace():
    """Set up workspace directories"""
    print_header("Setting Up Workspace")
    
    directories = [
        "build",
        "build/verilator",
        "build/icarus",
        "build/vivado",
        "build/quartus",
        "waves",
        "logs",
        "results",
    ]
    
    for d in directories:
        Path(d).mkdir(parents=True, exist_ok=True)
        print_step(f"Created: {d}/")
    
    print_success("Workspace ready")

def verify_installation():
    """Verify all tools are installed correctly"""
    print_header("Verifying Installation")
    
    tools = {
        "Verilator": "verilator --version",
        "Icarus Verilog": "iverilog -V | head -1",
        "GTKWave": "gtkwave --version",
        "Python": f"python3 --version",
        "pip": "pip --version",
    }
    
    all_ok = True
    for name, cmd in tools.items():
        success, stdout, stderr = run_command(cmd, check=False, capture=True)
        if success:
            version = stdout.split('\n')[0] if stdout else "OK"
            print_success(f"{name}: {version}")
        else:
            print_warning(f"{name}: NOT INSTALLED")
            all_ok = False
    
    # Check cocotb
    success, _, _ = run_command("python3 -c 'import cocotb; print(cocotb.__version__)'", check=False, capture=True)
    if success:
        print_success("cocotb: installed")
    else:
        print_warning("cocotb: NOT INSTALLED")
    
    return all_ok

def create_run_script():
    """Create convenience run script"""
    print_header("Creating Run Scripts")
    
    run_script = '''#!/bin/bash
# SuperInstance.AI Quick Run Script

case "$1" in
    sim)
        make sim SIM=${2:-verilator}
        ;;
    synth)
        make synth TARGET=${2:-kv260}
        ;;
    wave)
        gtkwave waves/*.vcd &
        ;;
    clean)
        make clean
        ;;
    test)
        pytest verification/ -v
        ;;
    *)
        echo "Usage: $0 {sim|synth|wave|clean|test}"
        echo ""
        echo "  sim    - Run simulation (verilator|icarus|vivado)"
        echo "  synth  - Run synthesis (kv260|de10nano)"
        echo "  wave   - Open waveform viewer"
        echo "  clean  - Clean build artifacts"
        echo "  test   - Run Python tests"
        ;;
esac
'''
    
    with open("run.sh", "w") as f:
        f.write(run_script)
    
    run_command("chmod +x run.sh")
    print_success("Created: run.sh")

def print_next_steps():
    """Print next steps for user"""
    print_header("Setup Complete! Next Steps")
    
    print("""
    1. Run simulation:
       ./run.sh sim verilator    # Fast development simulation
       ./run.sh sim icarus       # Waveform debugging
    
    2. View waveforms:
       ./run.sh wave
    
    3. Synthesize for FPGA:
       ./run.sh synth kv260      # Xilinx KV260 (recommended)
    
    4. Run Python tests:
       ./run.sh test
    
    5. Clean build artifacts:
       ./run.sh clean
    
    Documentation:
       - RTL: rtl/README.md
       - Verification: verification/README.md
       - Synthesis: synthesis/README.md
    """)

def main():
    parser = argparse.ArgumentParser(description="Setup FPGA simulation environment")
    parser.add_argument("--sim-only", action="store_true", help="Only install simulation tools")
    parser.add_argument("--synth-only", action="store_true", help="Only install synthesis tools")
    parser.add_argument("--skip-system", action="store_true", help="Skip system package installation")
    args = parser.parse_args()
    
    print_header("SuperInstance.AI FPGA Environment Setup")
    
    # Detect OS
    os_type = check_os()
    
    # Install system packages
    if not args.skip_system:
        if os_type == "linux":
            install_linux_packages()
        elif os_type == "macos":
            install_macos_packages()
        else:
            print_warning("Skipping system package installation (unknown OS)")
    
    # Install Python packages
    install_python_packages()
    
    # Setup workspace
    setup_workspace()
    
    # Create run script
    create_run_script()
    
    # Verify installation
    all_ok = verify_installation()
    
    # Print next steps
    print_next_steps()
    
    if all_ok:
        print_success("All tools installed successfully!")
        return 0
    else:
        print_warning("Some tools not installed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
