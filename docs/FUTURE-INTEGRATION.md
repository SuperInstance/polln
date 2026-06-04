# Future Integration: Polln

## Current State
A 945-file TypeScript monolithic colony intelligence with its own GPU engine, tile system, hydraulic metaphors, and Plinko stochastic decision layer. Visualizes PLATO tiles as interactive spreadsheet views with real-time updates. Too coupled to decompose, too rich to abandon.

## Integration Opportunities

### With ternary-cell
Every Polln concept maps to ternary-cell: Pollen → Payload, Bee → TernaryCell (Active state), Bot → BareMetalConstruct, Hive → CellGrid, Plinko decision → tick() cycle, Gumbel-Softmax → surprise-weighted energy redistribution, Pheromone → accumulated TernaryMessenger signals, Guardian → conservation law checker in GC phase. The Plinko layer's stochastic selection maintaining diversity through Gumbel-Softmax is exactly what the `surprise → vibe → gc` phases need — instead of greedy pruning, stochastic sampling maintains diversity.

### With ternary-spreadsheet
Polln's spreadsheet visualization is the frontend for ternary-spreadsheet. The real-time tile-to-spreadsheet rendering, interactive exploration, and multi-room views are exactly what the ternary-spreadsheet world model needs as a UI. Extract the visualization layer from Polln's monolith and connect it to ternary-cell's CellGrid via WebSocket.

### With room-as-codespace
Polln's Hive (the colony) maps to a room. Each Bee is a room-local agent, each Bot is a room-local skill. The Plinko decision layer becomes the room's GC strategy — how the room decides which agents to keep and which to prune.

## Dormant Ideas Now Unlockable
The monolithic coupling was the blocker. Now ternary-cell provides the decomposition target: extract each Polln concept as an independent ternary-cell strategy. The Plinko layer becomes a `CellGcStrategy` trait implementation. The Pheromone system becomes TernaryMessenger accumulation. The Guardian becomes conservation-law checking.

## Potential in Mature Systems
Polln becomes the reference implementation for stochastic room management. Its Plinko layer ensures no room becomes a monoculture — diversity is maintained through principled randomness rather than greedy optimization. Combined with strategy-ecology's Lotka-Volterra models, rooms have both stochastic and ecological diversity maintenance.

## Cross-Pollination Ideas
- **strategy-ecology**: Lotka-Volterra models complement Polln's Gumbel-Softmax for diversity
- **avoidance-cascade**: Balanced learning prevents the death spirals Polln's Pheromone system can cause
- **superinstance-spreadsheet**: Polln's visualization is the UI for the ternary spreadsheet

## Dependencies for Next Steps
- Extract Plinko layer as standalone ternary-cell GC strategy
- Bridge TypeScript visualization to Rust ternary-cell via WebSocket
- Define CellGcStrategy trait with Polln stochastic implementation
