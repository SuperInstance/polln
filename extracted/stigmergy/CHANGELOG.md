# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-11

### Added
- Initial release of Stigmergy
- Bio-inspired coordination via pheromone-based indirect communication
- Five standard pheromone types (PATHWAY, RESOURCE, DANGER, NEST, RECRUIT)
- Position-based detection with multiple formats (coordinates, topics, hash-based)
- Automatic pheromone evaporation with configurable half-life
- Reinforcement mechanism for trail following
- Event-driven architecture for monitoring
- TrailFollower helper class for agent implementation

### Features
- Configurable detection radius and reinforcement rates
- Real-time pheromone lifecycle management
- Comprehensive test suite with >95% coverage
- Full TypeScript support with detailed types
- Performance optimized with O(1) deposits
- Memory efficient with automatic cleanup