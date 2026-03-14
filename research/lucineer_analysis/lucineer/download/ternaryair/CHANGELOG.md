# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-08

### Added
- Initial open source release
- Complete RTL implementation in SystemVerilog
  - `top_level.sv`: Main inference engine (286 lines)
  - `synaptic_array.sv`: PE array implementation (150 lines)
  - `rau.sv`: Rotation-Accumulate Unit (169 lines)
  - `weight_rom.sv`: Mask-locked weight storage (109 lines)
  - `kv_cache.sv`: Key-value attention cache (100 lines)
- Python SDK (`ternaryair` package)
  - Hardware device interface
  - Software simulator backend
  - Streaming and batch inference
  - OpenAI-compatible API
- Model conversion tools
  - FP16 to ternary quantization
  - BitNet model support
  - GDSII ROM generation script
- Documentation
  - Multi-level Learning Center (5 levels)
  - Visual communication guide
  - API reference
  - Architecture deep dive
- FPGA support
  - Pre-built bitstreams for PYNQ-Z2, Arty A7
  - Build scripts and constraints
- CI/CD pipeline
  - RTL simulation tests
  - Python package tests
  - Code quality checks

### Security
- Mask-locked weight ROM design
- Air-gapped architecture by design
- No network interface capability
- No persistent storage

## [0.9.0] - 2026-02-15

### Added
- Beta release for testing
- Core RAU implementation validated
- FPGA prototype on PYNQ-Z2
- Basic SDK functionality

## [0.1.0] - 2025-11-01

### Added
- Initial concept and architecture design
- RAU mathematical foundation
- Ternary weight encoding scheme
