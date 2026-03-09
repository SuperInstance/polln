/**
 * POLLN Microbiome - Distributed Consensus System
 *
 * Phase 8: Distributed Systems - Milestone 1
 * Raft-based consensus for distributed microbiome coordination.
 * Enables multi-node deployment with strong consistency guarantees.
 *
 * @module microbiome/distributed
 */

import { v4 as uuidv4 } from 'uuid';

/**
 * Node identifier in the distributed system
 */
export type NodeId = string;

/**
 * Term number for leader election (monotonically increasing)
 */
export type Term = number;

/**
 * Log index
 */
export type LogIndex = number;

/**
 * Consensus algorithm types
 */
export enum ConsensusAlgorithm {
  /** Raft - Strong consistency, leader-based */
  RAFT = 'raft',
  /** Paxos - Fault-tolerant, leaderless */
  PAXOS = 'paxos',
  /** Epidemic - Gossip-based, eventual consistency */
  EPIDEMIC = 'epidemic',
  /** Hybrid - Combination of approaches */
  HYBRID = 'hybrid',
}

/**
 * Node state in Raft consensus
 */
export enum NodeState {
  /** Follower - Receives logs from leader */
  FOLLOWER = 'follower',
  /** Candidate - Campaigning for leadership */
  CANDIDATE = 'candidate',
  /** Leader - Handles all client requests */
  LEADER = 'leader',
}

/**
 * Log entry for consensus
 */
export interface LogEntry {
  /** Entry index */
  index: LogIndex;
  /** Term when entry was created */
  term: Term;
  /** Command to execute */
  command: StateChange;
  /** Entry has been committed */
  committed: boolean;
}

/**
 * State change command
 */
export interface StateChange {
  /** Change type */
  type: 'agent_introduce' | 'agent_cull' | 'colony_form' | 'resource_modify' | 'config_update';
  /** Target ID (if applicable) */
  targetId?: string;
  /** Change parameters */
  params: Record<string, any>;
  /** Timestamp */
  timestamp: number;
  /** Proposed by node */
  proposedBy: NodeId;
}

/**
 * Vote request from candidate
 */
export interface VoteRequest {
  /** Candidate's term */
  term: Term;
  /** Candidate ID */
  candidateId: NodeId;
  /** Index of candidate's last log entry */
  lastLogIndex: LogIndex;
  /** Term of candidate's last log entry */
  lastLogTerm: Term;
}

/**
 * Vote response
 */
export interface VoteResponse {
  /** Responder's current term */
  term: Term;
  /** Vote granted (true) or denied (false) */
  voteGranted: boolean;
  /** Responder node ID */
  nodeId: NodeId;
}

/**
 * Append entries request (heartbeat or log replication)
 */
export interface AppendEntriesRequest {
  /** Leader's term */
  term: Term;
  /** Leader ID */
  leaderId: NodeId;
  /** Index of log entry preceding new entries */
  prevLogIndex: LogIndex;
  /** Term of prevLogIndex entry */
  prevLogTerm: Term;
  /** Entries to append (empty for heartbeat) */
  entries: LogEntry[];
  /** Leader's commit index */
  leaderCommit: LogIndex;
}

/**
 * Append entries response
 */
export interface AppendEntriesResponse {
  /** Responder's current term */
  term: Term;
  /** Success (true) if append worked */
  success: boolean;
  /** Responder node ID */
  nodeId: NodeId;
  /** Reason for failure (if applicable) */
  reason?: string;
}

/**
 * Network partition event
 */
export interface Partition {
  /** Partition ID */
  id: string;
  /** Nodes in partition */
  nodes: Set<NodeId>;
  /** Detected timestamp */
  detectedAt: number;
  /** Estimated duration (ms) */
  estimatedDuration?: number;
}

/**
 * Recovery strategy for partitions
 */
export enum RecoveryStrategy {
  /** Wait for partition to heal */
  WAIT = 'wait',
  /** Form new cluster with majority */
  MAJORITY = 'majority',
  /** Merge with reconciliation */
  MERGE = 'merge',
  /** Rollback to last committed state */
  ROLLBACK = 'rollback',
}

/**
 * Proposal for consensus
 */
export interface Proposal {
  /** Proposal ID */
  id: string;
  /** State change being proposed */
  change: StateChange;
  /** Current term */
  term: Term;
  /** Proposed by node */
  proposedBy: NodeId;
  /** Votes received */
  votes: Map<NodeId, boolean>;
  /** Quorum needed */
  quorum: number;
  /** Timestamp */
  timestamp: number;
}

/**
 * Consensus result
 */
export interface ConsensusResult {
  /** Consensus achieved (true) or not (false) */
  achieved: boolean;
  /** Resulting state change (if achieved) */
  change?: StateChange;
  /** Term number */
  term: Term;
  /** Committed log index */
  commitIndex: LogIndex;
  /** Error message (if failed) */
  error?: string;
}

/**
 * Vote on a proposal
 */
export interface Vote {
  /** Proposal ID */
  proposalId: string;
  /** Voting node */
  nodeId: NodeId;
  /** Vote (true) or against (false) */
  approve: boolean;
  /** Term */
  term: Term;
  /** Rationale (optional) */
  rationale?: string;
}

/**
 * Distributed consensus configuration
 */
export interface DistributedConsensusConfig {
  /** Consensus algorithm to use */
  algorithm: ConsensusAlgorithm;
  /** Election timeout (ms) */
  electionTimeout: number;
  /** Heartbeat interval (ms) */
  heartbeatInterval: number;
  /** Log replication batch size */
  replicationBatchSize: number;
  /** Maximum log entries before compaction */
  maxLogSize: number;
  /** Enable network partition detection */
  enablePartitionDetection: boolean;
  /** Partition detection threshold (ms) */
  partitionThreshold: number;
  /** Quorum calculation strategy */
  quorumStrategy: 'majority' | 'supermajority' | 'unanimous';
}

/**
 * Node information in cluster
 */
export interface ClusterNode {
  /** Node ID */
  id: NodeId;
  /** Node address */
  address: string;
  /** Node state */
  state: NodeState;
  /** Current term */
  currentTerm: Term;
  /** Voted for (in current term) */
  votedFor: NodeId | null;
  /** Leader ID (if known) */
  leaderId: NodeId | null;
  /** Last heartbeat timestamp */
  lastHeartbeat: number;
  /** Is this node alive */
  isAlive: boolean;
}

/**
 * Distributed consensus statistics
 */
export interface ConsensusStats {
  /** Current leader */
  leaderId: NodeId | null;
  /** Current term */
  currentTerm: Term;
  /** Total nodes in cluster */
  totalNodes: number;
  /** Nodes alive */
  aliveNodes: number;
  /** Log entries */
  logEntries: number;
  /** Committed entries */
  committedEntries: number;
  /** Pending proposals */
  pendingProposals: number;
  /** Elections held */
  electionsHeld: number;
  /** Network partitions detected */
  partitionsDetected: number;
}

/**
 * Raft-based distributed consensus implementation
 */
export class DistributedConsensus {
  /** Local node ID */
  private nodeId: NodeId;
  /** Cluster nodes */
  private cluster: Map<NodeId, ClusterNode>;
  /** Replicated log */
  private log: LogEntry[];
  /** Commit index */
  private commitIndex: LogIndex;
  /** Last applied index */
  private lastApplied: LogIndex;
  /** Next index for each node (for replication) */
  private nextIndex: Map<NodeId, LogIndex>;
  /** Match index for each node */
  private matchIndex: Map<NodeId, LogIndex>;
  /** Current state */
  private state: NodeState;
  /** Current term */
  private currentTerm: Term;
  /** Voted for in current term */
  private votedFor: NodeId | null;
  /** Election timeout timer */
  private electionTimer: NodeJS.Timeout | null;
  /** Heartbeat timer */
  private heartbeatTimer: NodeJS.Timeout | null;
  /** Active proposals */
  private proposals: Map<string, Proposal>;
  /** Pending votes */
  private pendingVotes: Map<string, Vote>;
  /** Active partitions */
  private partitions: Map<string, Partition>;
  /** Configuration */
  private config: DistributedConsensusConfig;
  /** State change callbacks */
  private onCommitCallbacks: Set<(entry: LogEntry) => void>;
  /** Leader change callbacks */
  private onLeaderChangeCallbacks: Set<(leaderId: NodeId) => void>;
  /** Partition detection callbacks */
  private onPartitionCallbacks: Set<(partition: Partition) => void>;
  /** Election timeout randomized */
  private randomizedElectionTimeout: number;
  /** Last heartbeat received */
  private lastHeartbeatReceived: number;
  /** Statistics */
  private stats: ConsensusStats;

  /**
   * Create distributed consensus instance
   */
  constructor(nodeId: NodeId, clusterNodes: NodeId[], config: Partial<DistributedConsensusConfig> = {}) {
    this.nodeId = nodeId;
    this.cluster = new Map();
    this.log = [];
    this.commitIndex = 0;
    this.lastApplied = 0;
    this.nextIndex = new Map();
    this.matchIndex = new Map();
    this.state = NodeState.FOLLOWER;
    this.currentTerm = 0;
    this.votedFor = null;
    this.electionTimer = null;
    this.heartbeatTimer = null;
    this.proposals = new Map();
    this.pendingVotes = new Map();
    this.partitions = new Map();
    this.onCommitCallbacks = new Set();
    this.onLeaderChangeCallbacks = new Set();
    this.onPartitionCallbacks = new Set();
    this.lastHeartbeatReceived = Date.now();

    // Initialize cluster
    for (const id of clusterNodes) {
      this.cluster.set(id, {
        id,
        address: `${id}:8080`, // Default address
        state: NodeState.FOLLOWER,
        currentTerm: 0,
        votedFor: null,
        leaderId: null,
        lastHeartbeat: Date.now(),
        isAlive: id === nodeId, // Local node is alive
      });
      this.nextIndex.set(id, 1);
      this.matchIndex.set(id, 0);
    }

    // Configuration
    this.config = {
      algorithm: config.algorithm ?? ConsensusAlgorithm.RAFT,
      electionTimeout: config.electionTimeout ?? 5000,
      heartbeatInterval: config.heartbeatInterval ?? 1000,
      replicationBatchSize: config.replicationBatchSize ?? 10,
      maxLogSize: config.maxLogSize ?? 10000,
      enablePartitionDetection: config.enablePartitionDetection ?? true,
      partitionThreshold: config.partitionThreshold ?? 15000,
      quorumStrategy: config.quorumStrategy ?? 'majority',
    };

    // Randomize election timeout
    this.randomizedElectionTimeout = this.config.electionTimeout +
      Math.random() * this.config.electionTimeout;

    // Initialize statistics
    this.stats = {
      leaderId: null,
      currentTerm: 0,
      totalNodes: clusterNodes.length,
      aliveNodes: 1,
      logEntries: 0,
      committedEntries: 0,
      pendingProposals: 0,
      electionsHeld: 0,
      partitionsDetected: 0,
    };

    // Start election timer
    this.resetElectionTimer();
  }

  /**
   * Propose a state change
   */
  async proposeStateChange(change: StateChange): Promise<ConsensusResult> {
    // Only leader can propose
    if (this.state !== NodeState.LEADER) {
      return {
        achieved: false,
        term: this.currentTerm,
        commitIndex: this.commitIndex,
        error: 'Not leader',
      };
    }

    // Create log entry
    const entry: LogEntry = {
      index: this.log.length + 1,
      term: this.currentTerm,
      command: change,
      committed: false,
    };

    // Append to local log
    this.log.push(entry);
    this.stats.logEntries = this.log.length;

    // Replicate to followers
    await this.replicateLog(entry);

    // Wait for commit
    const committed = await this.waitForCommit(entry.index);

    if (committed) {
      return {
        achieved: true,
        change,
        term: this.currentTerm,
        commitIndex: entry.index,
      };
    }

    return {
      achieved: false,
      term: this.currentTerm,
      commitIndex: this.commitIndex,
      error: 'Failed to achieve consensus',
    };
  }

  /**
   * Vote on a proposed change
   */
  vote(change: StateChange, approve: boolean): Vote {
    const vote: Vote = {
      proposalId: uuidv4(),
      nodeId: this.nodeId,
      approve,
      term: this.currentTerm,
      rationale: approve ? 'Change aligns with ecosystem health' : 'Change conflicts with state',
    };

    this.pendingVotes.set(vote.proposalId, vote);

    return vote;
  }

  /**
   * Achieve consensus across proposals
   */
  achieveConsensus(proposals: Proposal[]): ConsensusResult {
    // Find proposals with quorum
    const quorumSize = this.calculateQuorum();

    for (const proposal of proposals) {
      let approvalCount = 0;
      for (const approved of Array.from(proposal.votes.values())) {
        if (approved) approvalCount++;
      }

      if (approvalCount >= quorumSize) {
        // Consensus achieved
        return {
          achieved: true,
          change: proposal.change,
          term: proposal.term,
          commitIndex: this.commitIndex + 1,
        };
      }
    }

    return {
      achieved: false,
      term: this.currentTerm,
      commitIndex: this.commitIndex,
      error: 'No proposal achieved quorum',
    };
  }

  /**
   * Elect a new leader
   */
  electLeader(): NodeId | null {
    // Start election if we're a follower
    if (this.state === NodeState.FOLLOWER) {
      this.startElection();
    }

    // Return current leader if known
    const localNode = this.cluster.get(this.nodeId);
    return localNode?.leaderId ?? null;
  }

  /**
   * Replicate log entry to followers
   */
  async replicateLog(entry: LogEntry): Promise<void> {
    if (this.state !== NodeState.LEADER) {
      return;
    }

    const nodes = Array.from(this.cluster.values()).filter(n => n.id !== this.nodeId && n.isAlive);

    for (const node of nodes) {
      const nextIdx = this.nextIndex.get(node.id) ?? 1;
      const prevLogEntry = this.log[nextIdx - 2] ?? null; // -2 because index is 1-based

      const request: AppendEntriesRequest = {
        term: this.currentTerm,
        leaderId: this.nodeId,
        prevLogIndex: prevLogEntry?.index ?? 0,
        prevLogTerm: prevLogEntry?.term ?? 0,
        entries: [entry],
        leaderCommit: this.commitIndex,
      };

      // Send to node (in real system, this would be RPC)
      // For now, simulate locally
      this.handleAppendEntries(request, node.id);
    }
  }

  /**
   * Handle network partition
   */
  handlePartition(partition: Partition): RecoveryStrategy {
    // Store partition
    this.partitions.set(partition.id, partition);
    this.stats.partitionsDetected = this.partitions.size;

    // Determine recovery strategy
    const majoritySize = Math.floor(this.cluster.size / 2) + 1;
    const partitionSize = partition.nodes.size;

    if (partitionSize >= majoritySize) {
      // Partition has majority - form new cluster
      return RecoveryStrategy.MAJORITY;
    } else if (partitionSize === 1) {
      // Single node - wait for partition to heal
      return RecoveryStrategy.WAIT;
    } else {
      // Minority partition - rollback to last committed
      return RecoveryStrategy.ROLLBACK;
    }
  }

  /**
   * Start leader election
   */
  private startElection(): void {
    this.state = NodeState.CANDIDATE;
    this.currentTerm++;
    this.votedFor = this.nodeId;
    this.stats.electionsHeld++;
    this.stats.currentTerm = this.currentTerm;

    // Update local node
    const localNode = this.cluster.get(this.nodeId);
    if (localNode) {
      localNode.state = NodeState.CANDIDATE;
      localNode.currentTerm = this.currentTerm;
      localNode.votedFor = this.nodeId;
    }

    // Request votes from other nodes
    const lastLogIndex = this.log.length;
    const lastLogTerm = this.log.length > 0 ? this.log[this.log.length - 1].term : 0;

    const request: VoteRequest = {
      term: this.currentTerm,
      candidateId: this.nodeId,
      lastLogIndex,
      lastLogTerm,
    };

    // Send vote requests to all nodes
    const nodes = Array.from(this.cluster.values()).filter(n => n.id !== this.nodeId);
    let votesGranted = 1; // Vote for self

    for (const node of nodes) {
      const response = this.handleVoteRequest(request, node.id);
      if (response.voteGranted) {
        votesGranted++;
      }
    }

    // Check if won election
    const quorumSize = this.calculateQuorum();
    if (votesGranted >= quorumSize) {
      this.becomeLeader();
    } else {
      // Lost election, go back to follower
      this.state = NodeState.FOLLOWER;
      this.resetElectionTimer();
    }
  }

  /**
   * Become leader
   */
  private becomeLeader(): void {
    this.state = NodeState.LEADER;
    this.stats.leaderId = this.nodeId;

    // Update local node
    const localNode = this.cluster.get(this.nodeId);
    if (localNode) {
      localNode.state = NodeState.LEADER;
      localNode.leaderId = this.nodeId;
    }

    // Initialize next and match index
    for (const nodeId of Array.from(this.cluster.keys())) {
      this.nextIndex.set(nodeId, this.log.length + 1);
      this.matchIndex.set(nodeId, 0);
    }

    // Notify callbacks
    for (const callback of Array.from(this.onLeaderChangeCallbacks)) {
      callback(this.nodeId);
    }

    // Start heartbeat
    this.startHeartbeat();
  }

  /**
   * Start heartbeat timer
   */
  private startHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    this.heartbeatTimer = setInterval(() => {
      if (this.state === NodeState.LEADER) {
        this.sendHeartbeat();
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * Send heartbeat to all followers
   */
  private sendHeartbeat(): void {
    const nodes = Array.from(this.cluster.values()).filter(n => n.id !== this.nodeId && n.isAlive);

    for (const node of nodes) {
      const prevLogEntry = this.log.length > 0 ? this.log[this.log.length - 1] : null;

      const request: AppendEntriesRequest = {
        term: this.currentTerm,
        leaderId: this.nodeId,
        prevLogIndex: prevLogEntry?.index ?? 0,
        prevLogTerm: prevLogEntry?.term ?? 0,
        entries: [], // Empty for heartbeat
        leaderCommit: this.commitIndex,
      };

      this.handleAppendEntries(request, node.id);
    }
  }

  /**
   * Handle vote request
   */
  handleVoteRequest(request: VoteRequest, fromNodeId: NodeId): VoteResponse {
    const response: VoteResponse = {
      term: this.currentTerm,
      voteGranted: false,
      nodeId: this.nodeId,
    };

    // If request term is lower, deny
    if (request.term < this.currentTerm) {
      return response;
    }

    // If request term is higher, update term and become follower
    if (request.term > this.currentTerm) {
      this.currentTerm = request.term;
      this.state = NodeState.FOLLOWER;
      this.votedFor = null;
      this.stats.currentTerm = this.currentTerm;
    }

    // Check if already voted
    if (this.votedFor === null || this.votedFor === request.candidateId) {
      // Check if candidate's log is at least as up-to-date
      const lastLogIndex = this.log.length;
      const lastLogTerm = this.log.length > 0 ? this.log[this.log.length - 1].term : 0;

      if (request.lastLogTerm > lastLogTerm ||
          (request.lastLogTerm === lastLogTerm && request.lastLogIndex >= lastLogIndex)) {
        this.votedFor = request.candidateId;
        response.voteGranted = true;
      }
    }

    return response;
  }

  /**
   * Handle append entries (heartbeat or log replication)
   */
  handleAppendEntries(request: AppendEntriesRequest, fromNodeId: NodeId): AppendEntriesResponse {
    const response: AppendEntriesResponse = {
      term: this.currentTerm,
      success: false,
      nodeId: this.nodeId,
    };

    // Update last heartbeat
    this.lastHeartbeatReceived = Date.now();

    // If request term is higher, update term and become follower
    if (request.term > this.currentTerm) {
      this.currentTerm = request.term;
      this.state = NodeState.FOLLOWER;
      this.votedFor = null;
      this.stats.currentTerm = this.currentTerm;
    }

    // Update leader
    const localNode = this.cluster.get(this.nodeId);
    if (localNode) {
      localNode.leaderId = request.leaderId;
      this.stats.leaderId = request.leaderId;
    }

    // If request term is lower, deny
    if (request.term < this.currentTerm) {
      response.reason = 'Term mismatch';
      return response;
    }

    // Check log consistency
    if (request.prevLogIndex > 0) {
      if (this.log.length < request.prevLogIndex) {
        response.reason = 'Log too short';
        return response;
      }

      const prevEntry = this.log[request.prevLogIndex - 1];
      if (!prevEntry || prevEntry.term !== request.prevLogTerm) {
        response.reason = 'Previous log term mismatch';
        return response;
      }
    }

    // Append new entries
    if (request.entries.length > 0) {
      // Check for existing conflicting entries
      for (let i = 0; i < request.entries.length; i++) {
        const entry = request.entries[i];
        const index = request.prevLogIndex + i + 1;

        if (this.log.length >= index) {
          const existing = this.log[index - 1];
          if (existing && existing.term !== entry.term) {
            // Conflict: truncate log from this point
            this.log = this.log.slice(0, index - 1);
            break;
          }
        }

        // Append entry
        if (this.log.length < index) {
          this.log.push(entry);
          this.stats.logEntries = this.log.length;
        }
      }
    }

    response.success = true;

    // Update commit index
    if (request.leaderCommit > this.commitIndex) {
      const oldCommitIndex = this.commitIndex;
      this.commitIndex = Math.min(request.leaderCommit, this.log.length);

      // Apply newly committed entries
      for (let i = oldCommitIndex; i < this.commitIndex; i++) {
        const entry = this.log[i];
        if (entry && !entry.committed) {
          entry.committed = true;
          this.stats.committedEntries++;
          this.notifyCommit(entry);
        }
      }
    }

    // Reset election timer
    this.resetElectionTimer();

    return response;
  }

  /**
   * Wait for entry to be committed
   */
  private async waitForCommit(index: LogIndex, timeout: number = 5000): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      if (this.commitIndex >= index) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return false;
  }

  /**
   * Calculate quorum size
   */
  private calculateQuorum(): number {
    const aliveNodes = Array.from(this.cluster.values()).filter(n => n.isAlive).length;

    switch (this.config.quorumStrategy) {
      case 'supermajority':
        return Math.floor(aliveNodes * 0.67) + 1;
      case 'unanimous':
        return aliveNodes;
      case 'majority':
      default:
        return Math.floor(aliveNodes / 2) + 1;
    }
  }

  /**
   * Reset election timer
   */
  private resetElectionTimer(): void {
    if (this.electionTimer) {
      clearTimeout(this.electionTimer);
    }

    // Randomize timeout to prevent split votes
    this.randomizedElectionTimeout = this.config.electionTimeout +
      Math.random() * this.config.electionTimeout;

    this.electionTimer = setTimeout(() => {
      // Check if should start election
      const timeSinceHeartbeat = Date.now() - this.lastHeartbeatReceived;
      if (timeSinceHeartbeat > this.randomizedElectionTimeout && this.state !== NodeState.LEADER) {
        this.startElection();
      }
    }, this.randomizedElectionTimeout);
  }

  /**
   * Notify commit callbacks
   */
  private notifyCommit(entry: LogEntry): void {
    for (const callback of Array.from(this.onCommitCallbacks)) {
      try {
        callback(entry);
      } catch (error) {
        console.error('Error in commit callback:', error);
      }
    }
  }

  /**
   * Register callback for committed entries
   */
  onCommit(callback: (entry: LogEntry) => void): void {
    this.onCommitCallbacks.add(callback);
  }

  /**
   * Register callback for leader changes
   */
  onLeaderChange(callback: (leaderId: NodeId) => void): void {
    this.onLeaderChangeCallbacks.add(callback);
  }

  /**
   * Register callback for partition detection
   */
  onPartition(callback: (partition: Partition) => void): void {
    this.onPartitionCallbacks.add(callback);
  }

  /**
   * Get current state
   */
  getState(): NodeState {
    return this.state;
  }

  /**
   * Get current leader
   */
  getLeader(): NodeId | null {
    return this.stats.leaderId;
  }

  /**
   * Get current term
   */
  getTerm(): Term {
    return this.currentTerm;
  }

  /**
   * Get log entries
   */
  getLog(): LogEntry[] {
    return [...this.log];
  }

  /**
   * Get cluster nodes
   */
  getCluster(): ClusterNode[] {
    return Array.from(this.cluster.values());
  }

  /**
   * Get statistics
   */
  getStats(): ConsensusStats {
    return { ...this.stats };
  }

  /**
   * Step down as leader
   */
  stepDown(): void {
    if (this.state === NodeState.LEADER) {
      this.state = NodeState.FOLLOWER;
      this.stats.leaderId = null;

      // Stop heartbeat
      if (this.heartbeatTimer) {
        clearInterval(this.heartbeatTimer);
        this.heartbeatTimer = null;
      }

      // Reset election timer
      this.resetElectionTimer();
    }
  }

  /**
   * Add node to cluster
   */
  addNode(nodeId: NodeId, address: string): void {
    this.cluster.set(nodeId, {
      id: nodeId,
      address,
      state: NodeState.FOLLOWER,
      currentTerm: 0,
      votedFor: null,
      leaderId: this.stats.leaderId,
      lastHeartbeat: Date.now(),
      isAlive: true,
    });

    this.nextIndex.set(nodeId, this.log.length + 1);
    this.matchIndex.set(nodeId, 0);
    this.stats.totalNodes = this.cluster.size;
    this.stats.aliveNodes = Array.from(this.cluster.values()).filter(n => n.isAlive).length;
  }

  /**
   * Remove node from cluster
   */
  removeNode(nodeId: NodeId): void {
    this.cluster.delete(nodeId);
    this.nextIndex.delete(nodeId);
    this.matchIndex.delete(nodeId);
    this.stats.totalNodes = this.cluster.size;
    this.stats.aliveNodes = Array.from(this.cluster.values()).filter(n => n.isAlive).length;
  }

  /**
   * Mark node as dead/alive
   */
  setNodeAlive(nodeId: NodeId, alive: boolean): void {
    const node = this.cluster.get(nodeId);
    if (node) {
      node.isAlive = alive;
      this.stats.aliveNodes = Array.from(this.cluster.values()).filter(n => n.isAlive).length;
    }
  }

  /**
   * Shutdown consensus
   */
  shutdown(): void {
    if (this.electionTimer) {
      clearTimeout(this.electionTimer);
      this.electionTimer = null;
    }

    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }

    this.state = NodeState.FOLLOWER;
  }

  /**
   * Compact log (remove committed entries)
   */
  compactLog(): void {
    if (this.log.length > this.config.maxLogSize) {
      // Keep only last N entries
      const keep = Math.floor(this.config.maxLogSize / 2);
      this.log = this.log.slice(-keep);

      // Update next and match indices
      for (const [nodeId, nextIdx] of Array.from(this.nextIndex.entries())) {
        this.nextIndex.set(nodeId, Math.max(nextIdx, this.log.length + 1));
      }

      this.stats.logEntries = this.log.length;
    }
  }

  /**
   * Create snapshot of current state
   */
  createSnapshot(): {
    term: Term;
    commitIndex: LogIndex;
    log: LogEntry[];
    state: NodeState;
    leaderId: NodeId | null;
  } {
    return {
      term: this.currentTerm,
      commitIndex: this.commitIndex,
      log: [...this.log],
      state: this.state,
      leaderId: this.stats.leaderId,
    };
  }

  /**
   * Restore from snapshot
   */
  restoreSnapshot(snapshot: {
    term: Term;
    commitIndex: LogIndex;
    log: LogEntry[];
    state: NodeState;
    leaderId: NodeId | null;
  }): void {
    this.currentTerm = snapshot.term;
    this.commitIndex = snapshot.commitIndex;
    this.log = [...snapshot.log];
    this.state = snapshot.state;
    this.stats.leaderId = snapshot.leaderId;
    this.stats.currentTerm = snapshot.term;
    this.stats.logEntries = this.log.length;
    this.stats.committedEntries = snapshot.commitIndex;
  }
}

/**
 * Create distributed consensus instance
 */
export function createDistributedConsensus(
  nodeId: NodeId,
  clusterNodes: NodeId[],
  config?: Partial<DistributedConsensusConfig>
): DistributedConsensus {
  return new DistributedConsensus(nodeId, clusterNodes, config);
}

/**
 * Helper function to calculate quorum for a given cluster size
 */
export function calculateQuorum(clusterSize: number, strategy: 'majority' | 'supermajority' | 'unanimous' = 'majority'): number {
  switch (strategy) {
    case 'supermajority':
      return Math.floor(clusterSize * 0.67) + 1;
    case 'unanimous':
      return clusterSize;
    case 'majority':
    default:
      return Math.floor(clusterSize / 2) + 1;
  }
}

/**
 * Helper function to detect network partition
 */
export function detectPartition(
  cluster: Map<NodeId, ClusterNode>,
  threshold: number
): Partition[] {
  const now = Date.now();
  const partitions: Partition[] = [];
  const partitionedNodes = new Set<NodeId>();

  for (const [nodeId, node] of Array.from(cluster.entries())) {
    if (!node.isAlive) {
      partitionedNodes.add(nodeId);
      continue;
    }

    const timeSinceHeartbeat = now - node.lastHeartbeat;
    if (timeSinceHeartbeat > threshold) {
      partitionedNodes.add(nodeId);
    }
  }

  if (partitionedNodes.size > 0) {
    partitions.push({
      id: uuidv4(),
      nodes: partitionedNodes,
      detectedAt: now,
    });
  }

  return partitions;
}

/**
 * Helper function to recover from partition
 */
export function recoverFromPartition(
  consensus: DistributedConsensus,
  partition: Partition,
  strategy: RecoveryStrategy
): void {
  switch (strategy) {
    case RecoveryStrategy.WAIT:
      // Just wait for partition to heal
      console.log(`Waiting for partition ${partition.id} to heal`);
      break;

    case RecoveryStrategy.MAJORITY:
      // Form new cluster with majority
      console.log(`Forming new cluster with majority from partition ${partition.id}`);
      const majoritySize = Math.floor(consensus.getCluster().length / 2) + 1;
      if (partition.nodes.size >= majoritySize) {
        // Trigger new election
        consensus.electLeader();
      }
      break;

    case RecoveryStrategy.MERGE:
      // Merge partitions with reconciliation
      console.log(`Merging partition ${partition.id} with reconciliation`);
      // In real system, would implement state reconciliation
      break;

    case RecoveryStrategy.ROLLBACK:
      // Rollback to last committed state
      console.log(`Rolling partition ${partition.id} to last committed state`);
      const snapshot = consensus.createSnapshot();
      consensus.restoreSnapshot(snapshot);
      break;
  }
}
