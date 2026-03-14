# Changelog

All notable changes to SuperInstance.AI SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Rust language bindings (experimental)
- JavaScript/Node.js SDK (experimental)
- GPIO API for Maker Edition devices
- ROS2 integration package
- LangChain integration examples

### Changed
- Improved streaming performance for long generations
- Enhanced error messages with actionable suggestions

### Fixed
- Edge case in token counting for multilingual text

---

## [1.0.0] - 2026-03-15

### Added
- Initial stable release of SuperInstance SDK
- **Device API**: Auto-detection and management of SuperInstance hardware
  - `Device()` for auto-detection
  - `Device.list_devices()` for listing available devices
  - `Device.info()` for device metadata and status
  - `Device.load_cartridge()` for loading pre-installed models
  - `Device.load_model()` for custom model loading (PRO/Maker)
- **Model API**: Text generation and chat capabilities
  - `model.generate()` for complete response generation
  - `model.generate_stream()` for real-time token streaming
  - `model.chat()` for multi-turn conversations
  - `model.chat_stream()` for streaming chat
  - `model.tokenize()` and `model.detokenize()` for token manipulation
- **GenerationConfig**: Comprehensive generation parameter control
  - Temperature, top_p, top_k sampling parameters
  - Stop sequences and stop tokens
  - Repetition, frequency, and presence penalties
  - Seed for reproducible outputs
  - Max tokens and echo options
- **Profiler API**: Performance and energy measurement
  - `Profiler` context manager for profiling sessions
  - Layer-by-layer performance breakdown
  - Energy consumption measurement
  - Memory bandwidth and compute utilization metrics
- **Error Handling**: Comprehensive exception hierarchy
  - `DeviceNotFoundError`, `DeviceBusyError`, `DeviceConnectionError`
  - `NoCartridgeError`, `CartridgeReadError`
  - `ContextLengthExceededError`, `GenerationError`
  - Clear error messages with suggested fixes
- **Cross-platform support**: Linux, macOS, Windows 10/11
- **Documentation**: Complete API reference and examples

### Security
- Cryptographic verification of firmware updates
- Encrypted USB communication channels
- Secure boot for firmware integrity

---

## [0.3.0] - 2026-02-01

### Added
- Profiler API for performance measurement
- Energy consumption tracking
- Device health monitoring (temperature, power)
- Multi-device support with device indexing

### Changed
- **BREAKING**: Renamed `Model.generate_streaming()` to `Model.generate_stream()`
- Improved streaming latency by 15%
- Reduced memory footprint by 20%

### Fixed
- Device detection on Windows with multiple USB devices
- Token counting for Unicode text
- Race condition in concurrent device access

---

## [0.2.0] - 2026-01-15

### Added
- Chat API with multi-turn conversation support
- `GenerationConfig` class for generation parameters
- Stop sequences for controlled generation
- Seed parameter for reproducible outputs
- Tokenization API (`tokenize`, `detokenize`, `count_tokens`)

### Changed
- **BREAKING**: `Model.generate()` now returns `GenerationResult` object instead of string
  - Access text via `result.text`
  - Use `str(result)` for backward compatibility
- Improved error messages with context

### Fixed
- Context length validation before generation
- Memory leak in long-running sessions

---

## [0.1.0] - 2025-12-01

### Added
- Initial alpha release
- Basic device detection and connection
- Simple text generation
- Streaming output support
- Python 3.8+ support

### Known Issues
- Device detection may fail on some Linux systems without udev rules
- Streaming can have occasional stuttering on high-latency USB hubs
- Temperature readings may be inaccurate during first 30 seconds

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|-------------|--------------|
| 1.0.0 | 2026-03-15 | First stable release |
| 0.3.0 | 2026-02-01 | Profiler, energy tracking |
| 0.2.0 | 2026-01-15 | Chat API, GenerationConfig |
| 0.1.0 | 2025-12-01 | Alpha release |

---

## Upgrading Guide

### From 0.3.x to 1.0.0

No breaking changes. Simply upgrade:

```bash
pip install --upgrade superinstance-sdk
```

### From 0.2.x to 0.3.0

No breaking changes. The `Profiler` API is new and optional.

### From 0.1.x to 0.2.0

**Breaking Change**: `Model.generate()` now returns a `GenerationResult` object.

**Before (0.1.x):**
```python
text = model.generate("Hello")
```

**After (0.2.0+):**
```python
result = model.generate("Hello")
text = result.text
# Or simply:
text = str(model.generate("Hello"))
```

---

## Release Schedule

We follow a regular release schedule:

- **Patch releases** (1.0.x): As needed for bug fixes and minor improvements
- **Minor releases** (1.x.0): Monthly with new features
- **Major releases** (x.0.0): Annually with significant changes

Release candidates (RC) are published 1 week before minor/major releases for community testing.

---

## Deprecation Policy

Features are deprecated following this timeline:

1. **Announcement**: Deprecated in release N
2. **Warning**: Runtime deprecation warnings in releases N through N+2
3. **Removal**: Feature removed in release N+3 (minimum 3 months)

All deprecations are documented in release notes and migration guides.

---

For detailed release notes, see [GitHub Releases](https://github.com/superinstance-ai/superinstance-sdk/releases).
