#!/usr/bin/env python3
"""
Generate Testbenches using NVIDIA NIM
AI-generated verification for mask-locked inference chip
"""

import requests
import json
import os

NVIDIA_API_KEY = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

def nvidia_chat(prompt, max_tokens=2048, temp=0.2):
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temp
    }
    
    try:
        response = requests.post(
            f"{NVIDIA_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def extract_code(text):
    """Extract code from markdown"""
    if "```systemverilog" in text:
        return text.split("```systemverilog")[1].split("```")[0].strip()
    elif "```verilog" in text:
        return text.split("```verilog")[1].split("```")[0].strip()
    elif "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text

output_dir = "/home/z/my-project/research/nvidia_enhanced_rtl"
os.makedirs(output_dir, exist_ok=True)

print("=" * 50)
print("Generating AI Testbenches with NVIDIA NIM")
print("=" * 50)

# 1. RAU Testbench
print("\n1. RAU Testbench...")
tb_rau = nvidia_chat("""Write a comprehensive SystemVerilog testbench for the RAU (Rotation-Accumulate Unit):

Module interface:
- 8-bit activation input
- 2-bit ternary weight {-1, 0, +1} encoded as 2'b00=+1, 2'b01=-1, 2'b10=0
- 24-bit accumulator output
- Valid/ready handshaking
- Clock and reset

Test scenarios:
1. Basic ternary operations: (+1)*a, (-1)*a, 0*a
2. Accumulation sequence with saturation
3. Pipeline behavior verification
4. Back-to-back transactions
5. Idle cycles between operations
6. Reset behavior
7. Maximum accumulator value
8. Minimum accumulator value (negative saturation)

Include:
- Clock generation
- Task/function for stimulus
- Coverage collection
- Assertions for protocol checking
- Self-checking scoreboard

Output only SystemVerilog code.""", max_tokens=3000)

if "Error" not in tb_rau:
    with open(f"{output_dir}/tb_rau.sv", 'w') as f:
        f.write(extract_code(tb_rau))
    print("   ✓ Saved tb_rau.sv")
else:
    print(f"   ✗ {tb_rau}")

# 2. PE Array Testbench
print("\n2. PE Array Testbench...")
tb_pe = nvidia_chat("""Write a SystemVerilog testbench for a 4x4 PE array (subset of 32x32):

Each PE has:
- North, South, East, West data ports
- Ternary weight input
- Partial sum input/output
- Valid/ready handshaking

Test scenarios:
1. Systolic data flow (weight-stationary)
2. Neighbor-to-neighbor communication
3. Full array computation
4. Power gating modes
5. Sleep/wake transitions
6. Defect bypass testing

Include:
- UVM-style testbench structure (if familiar)
- Or clean module-based testbench
- Waveform dumping commands
- Coverage for activation patterns

Output only SystemVerilog code.""", max_tokens=3000)

if "Error" not in tb_pe:
    with open(f"{output_dir}/tb_pe_array.sv", 'w') as f:
        f.write(extract_code(tb_pe))
    print("   ✓ Saved tb_pe_array.sv")
else:
    print(f"   ✗ {tb_pe}")

# 3. Weight ROM Testbench
print("\n3. Weight ROM Testbench...")
tb_rom = nvidia_chat("""Write a SystemVerilog testbench for mask-locked weight ROM:

Features:
- 512 ternary weights packed 4 per byte
- Single-cycle read
- Address input, data output

Test scenarios:
1. Sequential read of all addresses
2. Random access patterns
3. ECC check (if implemented)
4. Power-up initialization
5. Defect detection patterns

Include:
- Expected data generation
- CRC/checksum verification
- Timing checks

Output only SystemVerilog code.""", max_tokens=2500)

if "Error" not in tb_rom:
    with open(f"{output_dir}/tb_weight_rom.sv", 'w') as f:
        f.write(extract_code(tb_rom))
    print("   ✓ Saved tb_weight_rom.sv")
else:
    print(f"   ✗ {tb_rom}")

# 4. KV Cache Testbench
print("\n4. KV Cache Testbench...")
tb_kv = nvidia_chat("""Write a SystemVerilog testbench for KV cache:

Features:
- 32KB, 256 entries × 128 bytes
- Circular buffer for streaming
- 128-bit data path
- Power-gated banks

Test scenarios:
1. Sequential write and read
2. Circular buffer wrap-around
3. Bank switching
4. Power gating while retaining data
5. Concurrent read/write
6. Full/empty conditions
7. Stress test with random patterns

Include:
- Memory model reference
- Latency measurement
- Bandwidth calculation

Output only SystemVerilog code.""", max_tokens=3000)

if "Error" not in tb_kv:
    with open(f"{output_dir}/tb_kv_cache.sv", 'w') as f:
        f.write(extract_code(tb_kv))
    print("   ✓ Saved tb_kv_cache.sv")
else:
    print(f"   ✗ {tb_kv}")

# 5. Python Co-Simulation Script
print("\n5. Python Co-Simulation Script...")
py_cosim = nvidia_chat("""Write a Python co-simulation script using cocotb for RAU verification:

Features:
- Connect to Verilog RAU module
- Drive stimuli from Python
- Python model for reference
- Automated comparison
- Coverage collection
- UVM-like test sequences

Include:
- Model of RAU in Python
- Test cases as coroutines
- Scoreboard for comparison
- Coverage database generation

Output only Python code.""", max_tokens=3000)

if "Error" not in py_cosim:
    with open(f"{output_dir}/cosim_rau.py", 'w') as f:
        f.write(extract_code(py_cosim))
    print("   ✓ Saved cosim_rau.py")
else:
    print(f"   ✗ {py_cosim}")

# 6. Power Analysis Script
print("\n6. Power Analysis Script...")
power_script = nvidia_chat("""Write a Python script for power analysis of ternary PE array:

Features:
- Activity factor estimation
- Switching power calculation
- Leakage estimation for 28nm
- Power breakdown by component
- Clock tree power
- Memory power (SRAM, ROM)

Inputs:
- Array size, frequency, voltage
- Activity patterns
- Technology parameters

Outputs:
- Total power
- Power by component
- Efficiency metrics (tok/s/W)

Include:
- Visualization (matplotlib)
- Sensitivity analysis
- Optimization suggestions

Output only Python code.""", max_tokens=2500)

if "Error" not in power_script:
    with open(f"{output_dir}/power_analysis.py", 'w') as f:
        f.write(extract_code(power_script))
    print("   ✓ Saved power_analysis.py")
else:
    print(f"   ✗ {power_script}")

print("\n" + "=" * 50)
print("Testbench generation complete!")
print(f"Output: {output_dir}")
print("=" * 50)
