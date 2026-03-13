# Implementation: Distributed Consensus

**Paper:** 12 of 23
**Section:** 4 of 7
**Focus:** Protocol Specification and Reference Implementation

---

## 4.1 Protocol Specification

### 4.1.1 Protocol Phases

The SuperInstance Consensus Protocol operates in three phases per consensus round:

```
Phase 1: PROPOSE
  - Leader proposes value with origin chain
  - Propagates through hierarchy

Phase 2: VOTE
  - Nodes vote with confidence weights
  - Aggregators collect and summarize votes

Phase 3: COMMIT
  - Root aggregator broadcasts decision
  - Nodes verify and commit
```

### 4.1.2 State Machine

```
States: IDLE -> PROPOSING -> VOTING -> COMMITTED -> IDLE

Transitions:
  IDLE -> PROPOSING: Leader timeout or new proposal received
  PROPOSING -> VOTING: Proposal broadcast complete
  VOTING -> COMMITTED: Quorum reached
  COMMITTED -> IDLE: New round begins
```

### 4.1.3 Message Types

```typescript
// Core message types for consensus protocol

interface ProposalMessage {
  type: 'PROPOSAL';
  round: number;
  view: number;
  value: ConsensusValue;
  leader_signature: Signature;
}

interface VoteMessage {
  type: 'VOTE';
  round: number;
  view: number;
  value_hash: Hash;
  confidence: number;
  voter_id: NodeID;
  signature: Signature;
}

interface AggregateVoteMessage {
  type: 'AGGREGATE_VOTE';
  round: number;
  view: number;
  value_hash: Hash;
  total_confidence: number;
  vote_count: number;
  aggregator_id: NodeID;
  signatures: MerkleProof;
}

interface CommitMessage {
  type: 'COMMIT';
  round: number;
  view: number;
  value: ConsensusValue;
  quorum_proof: QuorumProof;
  root_signature: Signature;
}

interface ViewChangeMessage {
  type: 'VIEW_CHANGE';
  round: number;
  old_view: number;
  new_view: number;
  reason: 'TIMEOUT' | 'BYZANTINE_DETECTED';
  evidence: Evidence;
}
```

---

## 4.2 Reference Implementation

### 4.2.1 Core Data Structures

```typescript
// ============================================================
// SUPERINSTANCE CONSENSUS PROTOCOL - REFERENCE IMPLEMENTATION
// ============================================================

import { Hash, Signature, NodeID, OriginID } from './crypto';
import { OriginLink, ConfidenceCascade } from './origin-centric';

// ------------------------------------------------------------
// Core Types
// ------------------------------------------------------------

interface ConsensusConfig {
  n: number;              // Total nodes
  f: number;              // Max Byzantine nodes (n >= 3f + 1)
  k: number;              // Hierarchy levels (default: log n)
  timeout_propose: number;    // Proposal timeout (ms)
  timeout_vote: number;       // Vote timeout (ms)
  quorum_threshold: number;   // 2n/3
  confidence_threshold: number; // 2C/3
  thermal_decay: number;      // lambda for thermal load
}

interface ConsensusValue {
  value: any;
  origin_chain: OriginLink[];
  confidence: number;
  signatures: Map<NodeID, Signature>;
}

interface QuorumProof {
  value_hash: Hash;
  total_votes: number;
  total_confidence: number;
  merkle_root: Hash;
  signatures: Signature[];
}

// ------------------------------------------------------------
// Node Implementation
// ------------------------------------------------------------

class ConsensusNode {
  private id: NodeID;
  private config: ConsensusConfig;
  private state: 'IDLE' | 'PROPOSING' | 'VOTING' | 'COMMITTED';
  private round: number;
  private view: number;
  private role: 'LEADER' | 'FOLLOWER' | 'AGGREGATOR';
  private confidence_capacity: number;
  private thermal_load: number;

  private proposals: Map<Hash, ConsensusValue>;
  private votes: Map<Hash, Map<NodeID, VoteMessage>>;
  private commits: Set<Hash>;

  private hierarchy: HierarchicalNetwork;
  private cascade: ConfidenceCascade;

  constructor(id: NodeID, config: ConsensusConfig) {
    this.id = id;
    this.config = config;
    this.state = 'IDLE';
    this.round = 0;
    this.view = 0;
    this.role = this.determineRole();
    this.confidence_capacity = this.initializeConfidence();
    this.thermal_load = 0;

    this.proposals = new Map();
    this.votes = new Map();
    this.commits = new Set();

    this.hierarchy = new HierarchicalNetwork(config.n, config.k);
    this.cascade = new ConfidenceCascade();
  }

  // --------------------------------------------------------
  // Phase 1: Proposal
  // --------------------------------------------------------

  async propose(value: any, origin_chain: OriginLink[]): Promise<void> {
    if (this.role !== 'LEADER') {
      throw new Error('Only leaders can propose');
    }

    this.state = 'PROPOSING';

    // Calculate confidence from origin chain
    const confidence = this.cascade.computeConfidence(origin_chain);

    // Create consensus value
    const consensus_value: ConsensusValue = {
      value,
      origin_chain,
      confidence,
      signatures: new Map()
    };

    // Sign the proposal
    const signature = await this.sign(consensus_value);
    consensus_value.signatures.set(this.id, signature);

    // Create proposal message
    const proposal: ProposalMessage = {
      type: 'PROPOSAL',
      round: this.round,
      view: this.view,
      value: consensus_value,
      leader_signature: signature
    };

    // Broadcast to level-1 aggregators (hierarchical)
    await this.hierarchicalBroadcast(proposal);

    // Store proposal
    const value_hash = this.hash(consensus_value);
    this.proposals.set(value_hash, consensus_value);
  }

  async handleProposal(msg: ProposalMessage): Promise<void> {
    // Verify leader signature
    const leader_valid = await this.verifySignature(
      msg.leader_signature,
      msg.value,
      this.getLeader(msg.view)
    );

    if (!leader_valid) {
      this.reportByzantine(msg.leader_id, 'Invalid signature');
      return;
    }

    // Verify origin chain integrity
    const chain_valid = await this.verifyOriginChain(msg.value.origin_chain);
    if (!chain_valid) {
      this.reportByzantine(msg.leader_id, 'Invalid origin chain');
      return;
    }

    // Store proposal
    const value_hash = this.hash(msg.value);
    this.proposals.set(value_hash, msg.value);

    // Transition to voting
    this.state = 'VOTING';

    // Cast vote
    await this.vote(value_hash, msg.value.confidence);
  }

  // --------------------------------------------------------
  // Phase 2: Voting
  // --------------------------------------------------------

  async vote(value_hash: Hash, confidence: number): Promise<void> {
    // Apply thermal regulation
    const delay = this.computePropagationDelay(confidence);
    await this.sleep(delay);

    // Create vote message
    const vote: VoteMessage = {
      type: 'VOTE',
      round: this.round,
      view: this.view,
      value_hash,
      confidence,
      voter_id: this.id,
      signature: await this.sign({ value_hash, confidence })
    };

    // Send to aggregator (hierarchical)
    const aggregator = this.hierarchy.getAggregator(this.id);
    await this.sendToAggregator(aggregator, vote);

    // Update thermal load
    this.updateThermalLoad();
  }

  async handleVote(msg: VoteMessage): Promise<void> {
    // Verify signature
    const valid = await this.verifySignature(
      msg.signature,
      { value_hash: msg.value_hash, confidence: msg.confidence },
      msg.voter_id
    );

    if (!valid) {
      this.reportByzantine(msg.voter_id, 'Invalid vote signature');
      return;
    }

    // Store vote
    if (!this.votes.has(msg.value_hash)) {
      this.votes.set(msg.value_hash, new Map());
    }
    this.votes.get(msg.value_hash)!.set(msg.voter_id, msg);

    // Check if quorum reached (for aggregators)
    if (this.role === 'AGGREGATOR') {
      await this.aggregateAndForward(msg.value_hash);
    }
  }

  // --------------------------------------------------------
  // Hierarchical Aggregation
  // --------------------------------------------------------

  private async aggregateAndForward(value_hash: Hash): Promise<void> {
    const votes = this.votes.get(value_hash);
    if (!votes) return;

    // Check if we have enough votes to aggregate
    if (votes.size < this.config.quorum_threshold / this.config.k) {
      return; // Wait for more votes
    }

    // Aggregate votes
    const total_confidence = Array.from(votes.values())
      .reduce((sum, v) => sum + v.confidence * this.getNodeCapacity(v.voter_id), 0);

    const vote_count = votes.size;

    // Create Merkle proof of votes
    const signatures = Array.from(votes.values()).map(v => v.signature);
    const merkle_root = this.computeMerkleRoot(signatures);

    // Create aggregate message
    const aggregate: AggregateVoteMessage = {
      type: 'AGGREGATE_VOTE',
      round: this.round,
      view: this.view,
      value_hash,
      total_confidence,
      vote_count,
      aggregator_id: this.id,
      signatures: { merkle_root, count: signatures.length }
    };

    // Forward to next level
    const parent = this.hierarchy.getParent(this.id);
    if (parent) {
      await this.sendToAggregator(parent, aggregate);
    } else {
      // This is the root - check for commit
      await this.checkAndCommit(value_hash, aggregate);
    }
  }

  // --------------------------------------------------------
  // Phase 3: Commit
  // --------------------------------------------------------

  private async checkAndCommit(value_hash: Hash, aggregate: AggregateVoteMessage): Promise<void> {
    const proposal = this.proposals.get(value_hash);
    if (!proposal) return;

    // Check quorum
    const quorum_reached =
      aggregate.vote_count >= this.config.quorum_threshold &&
      aggregate.total_confidence >= this.config.confidence_threshold;

    if (!quorum_reached) {
      return; // Not enough support
    }

    // Create quorum proof
    const quorum_proof: QuorumProof = {
      value_hash,
      total_votes: aggregate.vote_count,
      total_confidence: aggregate.total_confidence,
      merkle_root: aggregate.signatures.merkle_root,
      signatures: [] // Would include necessary signatures for verification
    };

    // Create commit message
    const commit: CommitMessage = {
      type: 'COMMIT',
      round: this.round,
      view: this.view,
      value: proposal,
      quorum_proof,
      root_signature: await this.sign(quorum_proof)
    };

    // Broadcast commit to all nodes
    await this.hierarchicalBroadcast(commit);
  }

  async handleCommit(msg: CommitMessage): Promise<void> {
    // Verify root signature
    const valid = await this.verifySignature(
      msg.root_signature,
      msg.quorum_proof,
      this.getRootAggregator()
    );

    if (!valid) {
      this.reportByzantine(msg.root_id, 'Invalid commit signature');
      return;
    }

    // Verify quorum proof
    const quorum_valid =
      msg.quorum_proof.total_votes >= this.config.quorum_threshold &&
      msg.quorum_proof.total_confidence >= this.config.confidence_threshold;

    if (!quorum_valid) {
      this.reportByzantine(msg.root_id, 'Invalid quorum proof');
      return;
    }

    // Verify origin chain
    const chain_valid = await this.verifyOriginChain(msg.value.origin_chain);
    if (!chain_valid) {
      this.reportByzantine(msg.root_id, 'Invalid origin chain in commit');
      return;
    }

    // Commit the value
    this.state = 'COMMITTED';
    this.commits.add(this.hash(msg.value));

    // Persist to local storage
    await this.persistValue(msg.value);

    // Notify application layer
    this.emit('committed', msg.value);
  }

  // --------------------------------------------------------
  // View Change (Byzantine Recovery)
  // --------------------------------------------------------

  async handleViewChange(msg: ViewChangeMessage): Promise<void> {
    // Verify view change is valid
    if (msg.new_view <= msg.old_view) {
      return; // Invalid view change
    }

    // Verify evidence
    const evidence_valid = await this.verifyEvidence(msg.evidence);
    if (!evidence_valid) {
      return;
    }

    // Update view
    this.view = msg.new_view;

    // Reset state for new view
    this.state = 'IDLE';
    this.proposals.clear();
    this.votes.clear();

    // If new leader, propose previous value if any
    if (this.isLeaderForView(msg.new_view)) {
      // Would re-propose with new view
    }
  }

  // --------------------------------------------------------
  // Helper Methods
  // --------------------------------------------------------

  private computePropagationDelay(confidence: number): number {
    const base_delay = 10; // ms
    return base_delay * (1 / confidence) * (1 + this.thermal_load);
  }

  private updateThermalLoad(): void {
    const lambda = this.config.thermal_decay;
    const current_rate = 1; // Simplified: 1 message processed
    this.thermal_load = lambda * this.thermal_load + (1 - lambda) * current_rate;
  }

  private async verifyOriginChain(chain: OriginLink[]): Promise<boolean> {
    for (const link of chain) {
      // Verify signature
      const sig_valid = await this.verifySignature(
        link.signature,
        { origin_id: link.origin_id, transformation: link.transformation },
        link.creator_id
      );
      if (!sig_valid) return false;

      // Verify confidence cascade
      const expected_conf = this.cascade.apply(
        link.input_confidence,
        link.transformation
      );
      if (Math.abs(link.output_confidence - expected_conf) > 0.01) {
        return false;
      }
    }
    return true;
  }

  private async hierarchicalBroadcast(msg: any): Promise<void> {
    // Broadcast through hierarchy levels
    if (this.role === 'LEADER') {
      // Send to all level-1 aggregators
      const aggregators = this.hierarchy.getLevelAggregators(1);
      for (const agg of aggregators) {
        await this.send(agg, msg);
      }
    } else if (this.role === 'AGGREGATOR') {
      // Broadcast down to children
      const children = this.hierarchy.getChildren(this.id);
      for (const child of children) {
        await this.send(child, msg);
      }
    }
  }

  private async sign(data: any): Promise<Signature> {
    // Cryptographic signature (simplified)
    return crypto.sign(JSON.stringify(data), this.privateKey);
  }

  private async verifySignature(
    sig: Signature,
    data: any,
    signer: NodeID
  ): Promise<boolean> {
    const public_key = this.getPublicKey(signer);
    return crypto.verify(JSON.stringify(data), sig, public_key);
  }

  private hash(value: any): Hash {
    return crypto.hash(JSON.stringify(value));
  }

  private computeMerkleRoot(signatures: Signature[]): Hash {
    // Merkle tree root computation
    if (signatures.length === 0) return crypto.hash('');
    if (signatures.length === 1) return crypto.hash(signatures[0]);

    const mid = Math.floor(signatures.length / 2);
    const left = this.computeMerkleRoot(signatures.slice(0, mid));
    const right = this.computeMerkleRoot(signatures.slice(mid));
    return crypto.hash(left + right);
  }
}

// ------------------------------------------------------------
// Hierarchical Network
// ------------------------------------------------------------

class HierarchicalNetwork {
  private n: number;
  private k: number;
  private levels: Map<number, Set<NodeID>>;

  constructor(n: number, k: number) {
    this.n = n;
    this.k = k;
    this.levels = new Map();
    this.buildHierarchy();
  }

  private buildHierarchy(): void {
    // Level 0: All nodes
    this.levels.set(0, new Set(Array.from({ length: this.n }, (_, i) => i)));

    // Higher levels: Aggregators
    const fanout = Math.ceil(Math.pow(this.n, 1 / this.k));
    for (let level = 1; level <= this.k; level++) {
      const nodes_at_level = Math.ceil(this.n / Math.pow(fanout, level));
      this.levels.set(level, new Set(Array.from({ length: nodes_at_level }, (_, i) => i)));
    }
  }

  getAggregator(node_id: NodeID): NodeID {
    // Map node to its level-1 aggregator
    const level0_nodes = Array.from(this.levels.get(0)!);
    const index = level0_nodes.indexOf(node_id);
    const aggregators = Array.from(this.levels.get(1)!);
    return aggregators[index % aggregators.length];
  }

  getParent(node_id: NodeID): NodeID | null {
    // Get parent aggregator (null if root)
    for (let level = 1; level <= this.k; level++) {
      if (this.levels.get(level)?.has(node_id)) {
        if (level === this.k) return null; // Root
        const parents = Array.from(this.levels.get(level + 1)!);
        const index = Array.from(this.levels.get(level)!).indexOf(node_id);
        return parents[index % parents.length];
      }
    }
    return this.getAggregator(node_id);
  }

  getChildren(node_id: NodeID): NodeID[] {
    // Get children of aggregator
    for (let level = 1; level <= this.k; level++) {
      if (this.levels.get(level)?.has(node_id)) {
        if (level === 1) {
          // Return level-0 nodes assigned to this aggregator
          const aggregators = Array.from(this.levels.get(1)!);
          const my_index = aggregators.indexOf(node_id);
          const level0 = Array.from(this.levels.get(0)!);
          const per_agg = Math.ceil(this.n / aggregators.length);
          return level0.slice(my_index * per_agg, (my_index + 1) * per_agg);
        } else {
          // Return level-(level-1) aggregators
          const my_level = Array.from(this.levels.get(level)!);
          const child_level = Array.from(this.levels.get(level - 1)!);
          const my_index = my_level.indexOf(node_id);
          const per_parent = Math.ceil(child_level.length / my_level.length);
          return child_level.slice(my_index * per_parent, (my_index + 1) * per_parent);
        }
      }
    }
    return [];
  }

  getLevelAggregators(level: number): NodeID[] {
    return Array.from(this.levels.get(level) || []);
  }
}
```

---

## 4.3 Integration with SuperInstance

### 4.3.1 Origin-Centric Integration

```typescript
// Integration with Origin-Centric Architecture (Paper 1)

class OriginCentricConsensus extends ConsensusNode {
  private origin_store: OriginStore;

  async proposeWithOrigin(value: any, origin_ids: OriginID[]): Promise<void> {
    // Fetch origin chains
    const origin_chains = await Promise.all(
      origin_ids.map(id => this.origin_store.getOriginChain(id))
    );

    // Merge origin chains
    const merged_chain = this.mergeOriginChains(origin_chains);

    // Propose with merged chain
    await this.propose(value, merged_chain);
  }

  private mergeOriginChains(chains: OriginLink[][]): OriginLink[] {
    // Create consensus transformation
    const consensus_link: OriginLink = {
      origin_id: generateOriginID(),
      transformation: 'CONSENSUS_MERGE',
      input_confidence: Math.min(...chains.map(c => c[c.length - 1]?.output_confidence || 0)),
      output_confidence: 0, // Computed by cascade
      signature: null as any, // Filled during proposal
      creator_id: this.id
    };

    // Flatten and deduplicate
    const all_links = chains.flat();
    const unique_links = this.deduplicateLinks(all_links);

    return [...unique_links, consensus_link];
  }

  async commitWithProvenance(value: ConsensusValue): Promise<void> {
    // Store committed value in origin store
    const origin_id = generateOriginID();

    await this.origin_store.store({
      id: origin_id,
      value: value.value,
      origin_chain: value.origin_chain,
      confidence: value.confidence,
      timestamp: Date.now()
    });

    // Emit for downstream consumers
    this.emit('committed_with_origin', { origin_id, value });
  }
}
```

### 4.3.2 Confidence Cascade Integration

```typescript
// Integration with Confidence Cascade (Paper 3)

class ConfidenceAwareConsensus extends ConsensusNode {
  private cascade: ConfidenceCascadeManager;

  async voteWithCascade(value_hash: Hash, base_confidence: number): Promise<void> {
    // Apply confidence cascade
    const cascaded_confidence = this.cascade.applyCascade(
      base_confidence,
      this.getZone(value_hash)
    );

    // Vote with cascaded confidence
    await this.vote(value_hash, cascaded_confidence);
  }

  private getZone(value_hash: Hash): 'stable' | 'unstable' | 'novel' {
    // Determine zone based on value history
    const proposal = this.proposals.get(value_hash);
    if (!proposal) return 'novel';

    const confidence = proposal.confidence;
    if (confidence > 0.8) return 'stable';
    if (confidence > 0.5) return 'unstable';
    return 'novel';
  }
}
```

---

## 4.4 Performance Optimizations

### 4.4.1 Message Batching

```typescript
class BatchedConsensus extends ConsensusNode {
  private vote_batch: VoteMessage[] = [];
  private batch_timeout: number = 50; // ms
  private batch_size: number = 100;

  async handleVote(msg: VoteMessage): Promise<void> {
    this.vote_batch.push(msg);

    if (this.vote_batch.length >= this.batch_size) {
      await this.flushBatch();
    } else if (this.vote_batch.length === 1) {
      // Start timeout
      setTimeout(() => this.flushBatch(), this.batch_timeout);
    }
  }

  private async flushBatch(): Promise<void> {
    if (this.vote_batch.length === 0) return;

    // Aggregate batch
    const aggregated = this.aggregateVotes(this.vote_batch);

    // Forward as single message
    await this.aggregateAndForward(aggregated.value_hash);

    // Clear batch
    this.vote_batch = [];
  }
}
```

### 4.4.2 Signature Aggregation

```typescript
class SignatureAggregation {
  // BLS signature aggregation for efficient verification

  async aggregateSignatures(signatures: Signature[]): Promise<AggregatedSignature> {
    // BLS aggregation: sigma_agg = sum(sigma_i)
    const aggregated = bls.aggregate(signatures);
    return {
      signature: aggregated,
      public_keys: signatures.map((_, i) => this.getPublicKey(i))
    };
  }

  async verifyAggregated(
    agg_sig: AggregatedSignature,
    message: any
  ): Promise<boolean> {
    // BLS verification: e(sigma_agg, g2) = prod(e(H(m), pk_i))
    return bls.verifyAggregate(
      agg_sig.signature,
      message,
      agg_sig.public_keys
    );
  }
}
```

### 4.4.3 Speculative Execution

```typescript
class SpeculativeConsensus extends ConsensusNode {
  private speculative_commits: Map<Hash, ConsensusValue> = new Map();

  async handleProposal(msg: ProposalMessage): Promise<void> {
    await super.handleProposal(msg);

    // Speculatively execute value if high confidence
    if (msg.value.confidence > 0.9) {
      const value_hash = this.hash(msg.value);
      this.speculative_commits.set(value_hash, msg.value);

      // Execute optimistically
      this.emit('speculative_commit', msg.value);
    }
  }

  async handleCommit(msg: CommitMessage): Promise<void> {
    const value_hash = this.hash(msg.value);

    // Check if we speculated correctly
    if (this.speculative_commits.has(value_hash)) {
      // Speculation was correct - commit is free
      this.speculative_commits.delete(value_hash);
      this.emit('commit', msg.value);
    } else {
      // Speculation was wrong or not made
      await super.handleCommit(msg);
    }
  }
}
```

---

## 4.5 Configuration Parameters

```typescript
const DEFAULT_CONFIG: ConsensusConfig = {
  n: 100,                    // Network size
  f: 32,                     // Byzantine tolerance (n >= 3f + 1)
  k: 7,                      // Hierarchy levels (log_2(100) ~ 7)
  timeout_propose: 1000,     // 1 second
  timeout_vote: 500,         // 500 ms
  quorum_threshold: 67,      // ceil(2*100/3)
  confidence_threshold: 0.67, // 2/3 of total confidence
  thermal_decay: 0.9         // Thermal smoothing
};

const PRODUCTION_CONFIG: ConsensusConfig = {
  n: 10000,
  f: 3333,
  k: 14,                     // log_2(10000) ~ 14
  timeout_propose: 2000,
  timeout_vote: 1000,
  quorum_threshold: 6667,
  confidence_threshold: 0.67,
  thermal_decay: 0.95
};
```

---

## 4.6 Deployment Architecture

```
                    +-------------------+
                    |  Client Requests  |
                    +-------------------+
                            |
                            v
+------------------------------------------------------------------+
|                     Load Balancer                                 |
+------------------------------------------------------------------+
        |                    |                    |
        v                    v                    v
+---------------+   +---------------+   +---------------+
|   Node 0-99   |   |  Node 100-199 |   |  Node 200-299 |
|   (Region A)  |   |  (Region B)   |   |  (Region C)   |
+---------------+   +---------------+   +---------------+
        |                    |                    |
        v                    v                    v
+---------------+   +---------------+   +---------------+
| Aggregator L1 |   | Aggregator L1 |   | Aggregator L1 |
|   (Region A)  |   |  (Region B)   |   |  (Region C)   |
+---------------+   +---------------+   +---------------+
        \                    |                    /
         \                   |                   /
          \                  v                  /
           +-----------------------------------+
           |       Super Aggregator L2          |
           |      (Multi-Region Coordination)   |
           +-----------------------------------+
                            |
                            v
                   +----------------+
                   |  Root Agg. L3  |
                   |  (Final Commit)|
                   +----------------+
```

---

## 4.7 Monitoring and Observability

```typescript
interface ConsensusMetrics {
  // Performance
  throughput_tps: number;          // Transactions per second
  latency_p50_ms: number;          // Median latency
  latency_p99_ms: number;          // 99th percentile latency

  // Consensus health
  rounds_per_second: number;       // Consensus rounds completed
  commit_rate: number;             // Percentage of proposals committed
  view_change_rate: number;        // View changes per hour

  // Byzantine detection
  byzantine_detected: number;      // Byzantine nodes detected
  invalid_signatures: number;      // Invalid signatures seen
  origin_chain_violations: number; // Provenance violations

  // Network health
  message_queue_depth: number;     // Pending messages
  thermal_load_avg: number;        // Average thermal load
  hierarchy_efficiency: number;    // Actual vs optimal routing
}

class ConsensusMonitor {
  private metrics: ConsensusMetrics;

  collectMetrics(): ConsensusMetrics {
    return {
      throughput_tps: this.calculateThroughput(),
      latency_p50_ms: this.getPercentileLatency(50),
      latency_p99_ms: this.getPercentileLatency(99),
      rounds_per_second: this.roundsCompleted / this.elapsedTime,
      commit_rate: this.commits / this.proposals,
      view_change_rate: this.viewChanges / (this.elapsedTime / 3600000),
      byzantine_detected: this.byzantineCount,
      invalid_signatures: this.invalidSignatureCount,
      origin_chain_violations: this.provenanceViolationCount,
      message_queue_depth: this.messageQueue.size,
      thermal_load_avg: this.averageThermalLoad(),
      hierarchy_efficiency: this.actualMessages / this.optimalMessages
    };
  }
}
```

---

*Implementation: 2,800 words*
*Reference Implementation: TypeScript, ~1,200 lines*
