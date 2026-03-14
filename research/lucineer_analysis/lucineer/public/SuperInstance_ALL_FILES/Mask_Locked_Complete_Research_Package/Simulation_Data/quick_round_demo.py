#!/usr/bin/env python3
"""
Quick 12-Round Framework Demo
Shows the orchestration working across multiple rounds
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

DEEPSEEK_API_KEY = "sk-2c32887fc62b4016b6ff03f982968b76"
NVIDIA_API_KEY = "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"

OUTPUT_BASE = "/home/z/my-project/research/twelve_round_framework"
Path(OUTPUT_BASE).mkdir(parents=True, exist_ok=True)
Path(f"{OUTPUT_BASE}/rtl").mkdir(exist_ok=True)
Path(f"{OUTPUT_BASE}/reports").mkdir(exist_ok=True)

def deepseek_chat(prompt, model="deepseek-coder", max_tokens=1000):
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.2},
        timeout=60
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Error: {response.status_code}"

def nvidia_chat(prompt, model="meta/llama-3.1-70b-instruct", max_tokens=1000):
    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.2},
        timeout=60
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Error: {response.status_code}"

print("=" * 60)
print("12-ROUND HARDWARE DEVELOPMENT FRAMEWORK DEMO")
print("Multi-Model Orchestration: DeepSeek + NVIDIA NIM")
print("=" * 60)

results = {}

# Round 1: RTL Generation
print("\n--- ROUND 1: RTL Generation (deepseek-coder) ---")
rtl_prompt = """Write synthesizable Verilog for a ternary MAC unit:
- 8-bit activation input
- 2-bit ternary weight (-1,0,+1)
- 24-bit accumulator
- Clock gating
- Pipeline: 2 stages
Output ONLY Verilog code, no explanation."""

rtl_result = deepseek_chat(rtl_prompt, "deepseek-coder", 2000)
print(f"Generated {len(rtl_result)} chars")

# Extract and save code
if "```verilog" in rtl_result:
    code = rtl_result.split("```verilog")[1].split("```")[0].strip()
elif "```" in rtl_result:
    code = rtl_result.split("```")[1].split("```")[0].strip()
else:
    code = rtl_result

with open(f"{OUTPUT_BASE}/rtl/ternary_mac.v", 'w') as f:
    f.write(code)
print(f"Saved: {OUTPUT_BASE}/rtl/ternary_mac.v")
results["round1"] = {"model": "deepseek-coder", "status": "completed", "output": "rtl/ternary_mac.v"}

# Round 3: Stochastic Reasoning
print("\n--- ROUND 3: Stochastic Reasoning (deepseek-reasoner) ---")
stochastic_prompt = """For a 32x32 PE array chip, analyze defect tolerance stochastically:
- Defect rate: 10^-8 per transistor
- Each PE: ~50K transistors
- Total: 1024 PEs

Calculate:
1. Expected defects per die (Poisson)
2. Probability of zero defects
3. Optimal redundancy (1-spare, 2-spare)
4. Yield improvement with redundancy

Provide quantitative analysis with formulas."""

stochastic_result = deepseek_chat(stochastic_prompt, "deepseek-reasoner", 2000)
print(f"Generated {len(stochastic_result)} chars")

with open(f"{OUTPUT_BASE}/reports/stochastic_analysis.md", 'w') as f:
    f.write(stochastic_result)
print(f"Saved: {OUTPUT_BASE}/reports/stochastic_analysis.md")
results["round3"] = {"model": "deepseek-reasoner", "status": "completed", "output": "reports/stochastic_analysis.md"}

# Round 4: Power Analysis
print("\n--- ROUND 4: Power Analysis (deepseek-reasoner) ---")
power_prompt = """Analyze power for ternary inference chip:
- 1024 PEs at 1GHz
- Current estimate: 8.85W
- Target: 5W

Provide:
1. Power breakdown (switching, leakage, clock, memory)
2. 5 specific optimization techniques with % reduction
3. Recommended power budget allocation

Be quantitative and specific."""

power_result = deepseek_chat(power_prompt, "deepseek-reasoner", 2000)
print(f"Generated {len(power_result)} chars")

with open(f"{OUTPUT_BASE}/reports/power_analysis.md", 'w') as f:
    f.write(power_result)
print(f"Saved: {OUTPUT_BASE}/reports/power_analysis.md")
results["round4"] = {"model": "deepseek-reasoner", "status": "completed", "output": "reports/power_analysis.md"}

# Round 7: Testbench (NVIDIA)
print("\n--- ROUND 7: Testbench Generation (nvidia/llama-3.1-70b) ---")
tb_prompt = """Write a SystemVerilog testbench for ternary MAC unit:
- Clock/reset generation
- 10 test cases (ternary operations)
- Coverage collection
- Assertions
- Self-checking

Output ONLY SystemVerilog code."""

tb_result = nvidia_chat(tb_prompt, "meta/llama-3.1-70b-instruct", 2000)
print(f"Generated {len(tb_result)} chars")

if "```systemverilog" in tb_result:
    code = tb_result.split("```systemverilog")[1].split("```")[0].strip()
elif "```" in tb_result:
    code = tb_result.split("```")[1].split("```")[0].strip()
else:
    code = tb_result

with open(f"{OUTPUT_BASE}/rtl/tb_ternary_mac.sv", 'w') as f:
    f.write(code)
print(f"Saved: {OUTPUT_BASE}/rtl/tb_ternary_mac.sv")
results["round7"] = {"model": "nvidia/llama-3.1-70b", "status": "completed", "output": "rtl/tb_ternary_mac.sv"}

# Save execution log
execution_log = {
    "timestamp": datetime.now().isoformat(),
    "rounds_executed": len(results),
    "results": results
}

with open(f"{OUTPUT_BASE}/execution_log.json", 'w') as f:
    json.dump(execution_log, f, indent=2)

print("\n" + "=" * 60)
print(f"DEMO COMPLETE: {len(results)} rounds executed")
print(f"Output directory: {OUTPUT_BASE}")
print("=" * 60)
