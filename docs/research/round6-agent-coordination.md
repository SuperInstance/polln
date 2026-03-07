# POLLN Research Round 6: Agent Coordination Patterns

**Pattern-Organized Large Language Network**
**Research Agent:** Coordination Architect
**Date:** 2026-03-06
**Status:** COMPLETE

---

## Executive Summary

This document presents a comprehensive analysis of **agent coordination patterns** extracted from four historical multi-agent projects: `agent-grid`, `multibot`, `SwarmOrchestration`, and `agentz`. The research identifies **six novel coordination patterns** that can enhance POLLN's existing architecture, particularly in the areas of task allocation, consensus mechanisms, leader election, conflict resolution, and communication protocols.

Each pattern includes:
- Conceptual overview with architecture diagrams
- Code snippets from historical projects
- Novelty and applicability assessment
- Integration strategies with existing POLLN components (BaseAgent, Colony, A2APackage, PlinkoLayer)

---

## Table of Contents

1. [Hierarchical Master-Worker Coordination](#1-hierarchical-master-worker-coordination)
2. [Priority-Based Task Queuing](#2-priority-based-task-queuing)
3. [File-Based Asynchronous Communication](#3-file-based-asynchronous-communication)
4. [Merge Coordination with Conflict Resolution](#4-merge-coordination-with-conflict-resolution)
5. [Agent Registry and Discovery](#5-agent-registry-and-discovery)
6. [Consensus Through Weighted Voting](#6-consensus-through-weighted-voting)

---

## 1. Hierarchical Master-Worker Coordination

### 1.1 Concept Overview

**Pattern**: A centralized orchestrator (Master) manages multiple worker instances, delegating tasks and monitoring progress. Workers operate independently in isolated environments (Git worktrees) while the Master maintains global coordination.

**Key Characteristics**:
- Centralized control plane with distributed execution
- Isolated worker environments for parallel work
- Lifecycle management (spawn, pause, resume, terminate)
- Progress monitoring and failure recovery

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│            HIERARCHICAL MASTER-WORKER PATTERN                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MASTER (Orchestrator):                                        │
│  ┌─────────────────────────────────────────────────┐           │
│  │ • Task decomposition                           │           │
│  │ • Worker lifecycle management                  │           │
│  │ • Progress monitoring                          │           │
│  │ • Merge coordination                           │           │
│  │ • Resource allocation                          │           │
│  └─────────────────────────────────────────────────┘           │
│                     │                                          │
│         ┌───────────┼───────────┐                              │
│         ▼           ▼           ▼                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Worker 1 │ │ Worker 2 │ │ Worker N │                       │
│  │ Sonnet   │ │ Haiku    │ │ Opus     │                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
│         │           │           │                              │
│         ▼           ▼           ▼                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Worktree │ │ Worktree │ │ Worktree │                       │
│  │ Branch 1 │ │ Branch 2 │ │ Branch N │                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
│                                                                 │
│  COMMUNICATION:                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Master ←→ Worker Communication                 │           │
│  │ • Task assignment                              │           │
│  │ • Progress updates                              │           │
│  │ • Questions and answers                         │           │
│  │ • Heartbeat monitoring                          │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Historical Implementation

**Source**: `multibot/orchestrator-master/orchestrator_master.py`

**Key Components**:

```python
class OrchestratorMaster:
    """Main orchestrator class managing all system components."""

    def __init__(self):
        # Core components
        self.worker_manager = WorkerManager()
        self.task_queue = TaskQueue()
        self.communication = CommunicationHub()
        self.repo_manager = RepositoryManager()
        self.monitoring = MonitoringDashboard()

        # Enhanced components
        self.worker_lifecycle = WorkerLifecycleManager()
        self.message_queue = MessageQueueManager()
        self.master_communication = MasterCommunicationHandler(self.message_queue)
        self.priority_handler = PriorityTimeoutHandler(self.message_queue)
```

**Worker Lifecycle Management**:

```python
@mcp.tool()
async def spawn_worker(request: SpawnWorkerRequest) -> Dict[str, Any]:
    """Spawn a new worker instance with enhanced lifecycle management."""
    try:
        # Check safety constraints
        active_count = len(orchestrator.worker_lifecycle.active_workers)
        if not check_safety("worker_limits", active_workers=active_count):
            raise Exception("Worker limit reached or resource constraints exceeded")

        # Spawn the worker with enhanced lifecycle
        result = await orchestrator.worker_lifecycle.spawn_worker(
            worker_id=request.worker_id,
            model=request.model,
            task_name=request.task_name,
            base_branch=request.base_branch
        )

        # Register worker in communication hub
        await orchestrator.communication.register_worker(request.worker_id)

        # Update monitoring
        orchestrator.monitoring.add_worker_terminal(
            request.worker_id,
            f"Worker-{request.worker_id}-{request.task_name}"
        )

        return {
            "status": "success",
            "worker_id": request.worker_id,
            "details": result
        }
```

**Task Assignment**:

```python
@mcp.tool()
async def assign_task(request: AssignTaskRequest) -> Dict[str, Any]:
    """Assign a task to a specific worker."""
    try:
        task_id = await orchestrator.task_queue.assign_task(
            worker_id=request.worker_id,
            task_description=request.task_description,
            context=request.context,
            priority=request.priority
        )

        # Update worker's current task
        await orchestrator.worker_lifecycle.update_worker_task(
            request.worker_id,
            task_id,
            request.task_description
        )

        # Send task assignment via enhanced communication system
        success = await orchestrator.master_communication.send_task_assignment(
            worker_id=request.worker_id,
            task_id=task_id,
            description=request.task_description,
            context={"context_list": request.context, "additional_info": {}},
            priority=request.priority,
            timeout_seconds=3600
        )

        return {
            "status": "success",
            "task_id": task_id,
            "worker_id": request.worker_id
        }
```

### 1.3 Integration with POLLN

**Applicability**: HIGH

**Integration Points**:

1. **Colony as Master**: Extend `Colony` class to act as hierarchical coordinator
2. **BaseAgent as Worker**: Workers inherit from `BaseAgent` with lifecycle management
3. **A2A Package for Tasks**: Task assignments transmitted as A2A packages
4. **PlinkoLayer for Selection**: Master uses Plinko to select workers for tasks

**Implementation Strategy**:

```typescript
/**
 * POLLN Hierarchical Coordinator
 * Extends Colony to provide master-worker coordination
 */
export class HierarchicalColony extends Colony {
  private workers: Map<string, WorkerAgent> = new Map();
  private taskQueue: PriorityQueue<Task>;
  private lifecycleManager: WorkerLifecycleManager;

  /**
   * Spawn a new worker agent
   */
  async spawnWorker(config: WorkerConfig): Promise<string> {
    const workerId = uuidv4();

    // Create worker with isolated context
    const worker = new WorkerAgent({
      id: workerId,
      colonyId: this.id,
      ...config
    });

    // Initialize worker
    await worker.initialize();

    // Register worker
    this.workers.set(workerId, worker);
    this.registerAgent(worker.config);

    // Send spawn notification as A2A package
    const spawnPackage: A2APackage<WorkerSpawnEvent> = {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.id,
      receiverId: workerId,
      type: 'WORKER_SPAWN',
      payload: {
        workerId,
        config,
        spawnedAt: Date.now()
      },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.COLONY,
      layer: SubsumptionLayer.REFLEX
    };

    await this.emit('a2a_package', spawnPackage);

    return workerId;
  }

  /**
   * Assign task to worker
   */
  async assignTask(
    workerId: string,
    task: Task
  ): Promise<TaskAssignment> {
    const worker = this.workers.get(workerId);
    if (!worker) {
      throw new Error(`Worker ${workerId} not found`);
    }

    // Create task assignment A2A package
    const assignmentPackage: A2APackage<TaskAssignment> = {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.id,
      receiverId: workerId,
      type: 'TASK_ASSIGNMENT',
      payload: {
        taskId: task.id,
        description: task.description,
        context: task.context,
        priority: task.priority,
        assignedAt: Date.now()
      },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.PRIVATE,
      layer: SubsumptionLayer.DELIBERATE
    };

    // Send to worker
    await worker.receiveTask(assignmentPackage);

    return assignmentPackage.payload;
  }

  /**
   * Monitor worker progress
   */
  async monitorWorker(workerId: string): Promise<WorkerStatus> {
    const worker = this.workers.get(workerId);
    if (!worker) {
      throw new Error(`Worker ${workerId} not found`);
    }

    return worker.getStatus();
  }
}
```

### 1.4 Novelty Assessment

**Novelty**: 6/10

**Justification**:
- Master-worker pattern is well-established in distributed systems
- Novel aspects: Git worktree isolation, model-tiered workers (Opus/Sonnet/Haiku)
- Integration with A2A packages adds traceability
- Plinko-based worker selection introduces stochastic element

**Unique Contributions**:
- Model-specific worker allocation (Opus for complex tasks, Haiku for simple)
- Worktree-based isolation prevents conflicts
- Lifecycle management with pause/resume capabilities

---

## 2. Priority-Based Task Queuing

### 2.1 Concept Overview

**Pattern**: Tasks are queued with priority levels and assigned to workers based on availability, capability matching, and priority ordering.

**Key Characteristics**:
- Priority queue with heapq implementation
- Dependency resolution (tasks can depend on other tasks)
- Worker-task affinity matching
- Automatic reassignment on worker failure
- Retry mechanism with exponential backoff

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│                PRIORITY-BASED TASK QUEUING                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TASK SUBMISSION:                                              │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Task Queue                                      │           │
│  │ • Priority ordering (heapq)                     │           │
│  │ • Dependency tracking                           │           │
│  │ • Worker assignment                             │           │
│  │ • State persistence                             │           │
│  └─────────────────────────────────────────────────┘           │
│                     │                                          │
│                     ▼                                          │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Priority Queue:                                 │           │
│  │ [(9, timestamp, task_id_high),                  │           │
│  │  (7, timestamp, task_id_medium),                │           │
│  │  (5, timestamp, task_id_normal),                │           │
│  │  (3, timestamp, task_id_low)]                   │           │
│  └─────────────────────────────────────────────────┘           │
│                     │                                          │
│                     ▼                                          │
│  WORKER ASSIGNMENT:                                             │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Assignment Logic:                               │           │
│  │ 1. Check dependencies satisfied                 │           │
│  │ 2. Match worker capabilities                    │           │
│  │ 3. Assign highest priority available task       │           │
│  │ 4. Handle worker failures gracefully            │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  TASK LIFECYCLE:                                               │
│  PENDING → ASSIGNED → IN_PROGRESS → COMPLETED/FAILED           │
│     │          │           │                │                  │
│     │          ▼           ▼                ▼                  │
│     │    (reassign)   (timeout)      (retry)                  │
│     │          │           │                │                  │
│     └──────────┴───────────┴────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Historical Implementation

**Source**: `multibot/orchestrator-master/task_queue.py`

**Task Data Structure**:

```python
@dataclass
class Task:
    """Task data structure."""
    task_id: str
    description: str
    context: List[str]
    priority: int
    created_at: datetime
    assigned_worker: Optional[str] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = None
    estimated_duration: Optional[int] = None  # seconds
    actual_duration: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
```

**Priority Queue Implementation**:

```python
class TaskQueue:
    """Manages task queue with priority scheduling and dependency resolution."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.priority_queue: List[tuple] = []  # (priority, created_time, task_id)
        self.worker_assignments: Dict[str, List[str]] = {}  # worker_id -> [task_ids]
        self.state_dir = Path("/tmp/multibot/tasks")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def assign_task(
        self,
        worker_id: str,
        task_description: str,
        context: List[str] = None,
        priority: int = TaskPriority.NORMAL.value,
        dependencies: List[str] = None,
        estimated_duration: Optional[int] = None
    ) -> str:
        """Assign a new task to a worker."""
        async with self._lock:
            task_id = str(uuid.uuid4())

            task = Task(
                task_id=task_id,
                description=task_description,
                context=context or [],
                priority=priority,
                created_at=datetime.now(),
                dependencies=dependencies or [],
                estimated_duration=estimated_duration
            )

            # Check dependencies
            if not await self._check_dependencies(task.dependencies):
                raise ValueError(f"Unresolved dependencies: {task.dependencies}")

            # Assign to worker
            task.assigned_worker = worker_id
            task.assigned_at = datetime.now()
            task.status = TaskStatus.ASSIGNED

            # Store task
            self.tasks[task_id] = task

            # Update worker assignments
            if worker_id not in self.worker_assignments:
                self.worker_assignments[worker_id] = []
            self.worker_assignments[worker_id].append(task_id)

            # Add to priority queue
            heapq.heappush(
                self.priority_queue,
                (-priority, task.created_at.timestamp(), task_id)
            )

            # Save state
            await self._save_task_state(task_id)

            logger.info(f"Task {task_id} assigned to worker {worker_id}")
            return task_id
```

**Dependency Resolution**:

```python
async def _check_dependencies(self, dependencies: List[str]) -> bool:
    """Check if all dependencies are satisfied."""
    if not dependencies:
        return True

    for dep_id in dependencies:
        if dep_id not in self.tasks:
            return False
        if self.tasks[dep_id].status != TaskStatus.COMPLETED:
            return False

    return True
```

**Task Reassignment on Failure**:

```python
async def reassign_orphaned_tasks(self, task_ids: List[str]) -> List[str]:
    """Reassign tasks that were orphaned due to worker termination."""
    reassigned = []

    async with self._lock:
        for task_id in task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                    # Reset task for reassignment
                    task.status = TaskStatus.PENDING
                    task.assigned_worker = None
                    task.assigned_at = None
                    task.started_at = None

                    # Add back to priority queue
                    heapq.heappush(
                        self.priority_queue,
                        (-task.priority, task.created_at.timestamp(), task_id)
                    )

                    await self._save_task_state(task_id)
                    reassigned.append(task_id)

    logger.info(f"Reassigned {len(reassigned)} orphaned tasks")
    return reassigned
```

### 2.3 Integration with POLLN

**Applicability**: HIGH

**Integration Points**:

1. **A2A Package Tasks**: Tasks are A2A packages with priority metadata
2. **PlinkoLayer for Selection**: Priority influences Plinko selection probabilities
3. **Colony Task Distribution**: Colony manages task queue across agents
4. **Resource Allocation**: High-priority tasks get more resources

**Implementation Strategy**:

```typescript
/**
 * POLLN Priority Task Queue
 * Integrates with A2A packages and Plinko selection
 */
export class PriorityTaskQueue {
  private tasks: Map<string, QueuedTask> = new Map();
  private priorityQueue: MinPriorityQueue<QueuedTask>;
  private colony: Colony;

  constructor(colony: Colony) {
    this.colony = colony;
    this.priorityQueue = new MinPriorityQueue({
      priority: (task) => -task.priority // Negative for max-heap
    });
  }

  /**
   * Enqueue task as A2A package
   */
  async enqueue(
    description: string,
    context: string[],
    priority: number = 5,
    dependencies: string[] = []
  ): Promise<string> {
    const taskId = uuidv4();

    const task: QueuedTask = {
      id: taskId,
      description,
      context,
      priority,
      dependencies,
      status: 'pending',
      createdAt: Date.now(),
      causalChain: []
    };

    // Check dependencies
    for (const depId of dependencies) {
      const depTask = this.tasks.get(depId);
      if (!depTask || depTask.status !== 'completed') {
        throw new Error(`Dependency ${depId} not satisfied`);
      }
    }

    // Store task
    this.tasks.set(taskId, task);
    this.priorityQueue.enqueue(task);

    return taskId;
  }

  /**
   * Assign task to agent using Plinko selection
   */
  async assignToAgent(taskId: string): Promise<string> {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    // Get eligible agents (based on capabilities)
    const eligibleAgents = this.getEligibleAgents(task);

    // Use Plinko layer to select agent
    const plinkoDecision = await this.colony.plinkoLayer.decide({
      context: {
        task,
        eligibleAgents: eligibleAgents.map(a => a.id)
      },
      proposals: eligibleAgents.map(agent => ({
        agentId: agent.id,
        confidence: agent.valueFunction,
        bid: task.priority * agent.valueFunction
      }))
    });

    const selectedAgentId = plinkoDecision.selectedAgentId;
    if (!selectedAgentId) {
      throw new Error('No agent selected by Plinko layer');
    }

    // Create task assignment A2A package
    const assignmentPackage: A2APackage<TaskAssignment> = {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.colony.id,
      receiverId: selectedAgentId,
      type: 'TASK_ASSIGNMENT',
      payload: {
        taskId,
        description: task.description,
        context: task.context,
        priority: task.priority
      },
      parentIds: task.causalChain,
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.PRIVATE,
      layer: SubsumptionLayer.DELIBERATE
    };

    // Update task status
    task.status = 'assigned';
    task.assignedAgent = selectedAgentId;
    task.assignedAt = Date.now();

    return selectedAgentId;
  }

  /**
   * Get eligible agents for task
   */
  private getEligibleAgents(task: QueuedTask): AgentState[] {
    const allAgents = this.colony.getAllAgents();

    return allAgents.filter(agent => {
      // Agent must be active
      if (agent.status !== 'active') return false;

      // Agent must have required capabilities
      const agentConfig = this.colony.getAgentConfig(agent.id);
      if (!agentConfig) return false;

      // Check capability match
      const hasCapabilities = task.context.some(ctx =>
        agentConfig.inputTopics.some(topic => topic.includes(ctx))
      );

      return hasCapabilities;
    });
  }
}
```

### 2.4 Novelty Assessment

**Novelty**: 5/10

**Justification**:
- Priority queues are standard in distributed systems
- Novel integration with Plinko for stochastic selection
- A2A package traceability adds auditability
- Dependency resolution with causal chains

**Unique Contributions**:
- Plinko-based agent selection introduces stochastic element
- Causal chain tracking in task dependencies
- Integration with agent value functions for bidding

---

## 3. File-Based Asynchronous Communication

### 3.1 Concept Overview

**Pattern**: Agents communicate asynchronously through file-based message queues, with each agent having dedicated inbox/outbox directories.

**Key Characteristics**:
- File-based message persistence
- Inbox/outbox per agent
- Message type enumeration
- Pending question tracking
- Heartbeat monitoring

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│           FILE-BASED ASYNCHRONOUS COMMUNICATION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  COMMUNICATION DIRECTORY STRUCTURE:                             │
│  /tmp/multibot/communication/                                   │
│  ├── master/                                                    │
│  │   ├── inbox/        (receives from workers)                 │
│  │   └── outbox/       (sends to workers)                      │
│  └── workers/                                                   │
│      ├── worker-1/                                              │
│      │   ├── inbox/     (receives from master)                  │
│      │   ├── outbox/    (sends to master)                      │
│      │   └── archive/   (processed messages)                   │
│      └── worker-2/                                              │
│          ├── inbox/                                             │
│          ├── outbox/                                            │
│          └── archive/                                           │
│                                                                 │
│  MESSAGE FLOW:                                                  │
│  ┌─────────────────────────────────────────────────┐           │
│  │ 1. Master writes to worker-1/inbox/message.json │           │
│  │ 2. Worker-1 reads from inbox                     │           │
│  │ 3. Worker-1 processes message                    │           │
│  │ 4. Worker-1 writes response to outbox/response.json│       │
│  │ 5. Master reads from worker-1/outbox              │           │
│  │ 6. Master moves processed message to archive      │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  MESSAGE TYPES:                                                 │
│  • TASK_ASSIGNMENT    • TASK_UPDATE                            │
│  • TASK_COMPLETE      • QUESTION                                │
│  • ANSWER             • HEARTBEAT                               │
│  • TERMINATE          • BROADCAST                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Historical Implementation

**Source**: `multibot/orchestrator-master/communication.py`

**Message Data Structure**:

```python
@dataclass
class Message:
    """Message data structure."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    priority: int = 5

class MessageType(Enum):
    """Message type enumeration."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    QUESTION = "question"
    ANSWER = "answer"
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"
    HEARTBEAT = "heartbeat"
    TERMINATE = "terminate"
    PAUSE = "pause"
    RESUME = "resume"
    BROADCAST = "broadcast"
    MESSAGE = "message"
```

**Communication Hub**:

```python
class CommunicationHub:
    """Manages communication between Master and Workers."""

    def __init__(self):
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.pending_questions: Dict[str, Message] = {}
        self.message_history: Dict[str, List[Message]] = {}

        # Communication directories
        self.comm_dir = Path("/tmp/multibot/communication")
        self.master_inbox = self.comm_dir / "master" / "inbox"
        self.master_outbox = self.comm_dir / "master" / "outbox"

        # Create directories
        self.comm_dir.mkdir(parents=True, exist_ok=True)
        self.master_inbox.mkdir(parents=True, exist_ok=True)
        self.master_outbox.mkdir(parents=True, exist_ok=True)

    async def register_worker(self, worker_id: str, capabilities: List[str] = None) -> bool:
        """Register a worker for communication."""
        # Create worker communication directories
        worker_inbox = self.comm_dir / "workers" / worker_id / "inbox"
        worker_outbox = self.comm_dir / "workers" / worker_id / "outbox"
        worker_inbox.mkdir(parents=True, exist_ok=True)
        worker_outbox.mkdir(parents=True, exist_ok=True)

        # Register worker
        self.workers[worker_id] = {
            "registered_at": datetime.now(),
            "last_seen": datetime.now(),
            "capabilities": capabilities or [],
            "inbox_path": worker_inbox,
            "outbox_path": worker_outbox,
            "status": "active"
        }

        return True
```

**Sending Messages**:

```python
async def send_to_worker(self, worker_id: str, payload: Dict[str, Any]) -> str:
    """Send a message to a specific worker."""
    if worker_id not in self.workers:
        raise ValueError(f"Worker {worker_id} not registered")

    worker = self.workers[worker_id]
    if worker["status"] != "active":
        raise ValueError(f"Worker {worker_id} is not active")

    # Create message
    message_id = str(uuid.uuid4())
    message = Message(
        message_id=message_id,
        sender_id="master",
        recipient_id=worker_id,
        message_type=MessageType(payload.get("type", MessageType.MESSAGE.value)),
        payload=payload,
        timestamp=datetime.now(),
        priority=payload.get("priority", 5)
    )

    # Write to worker's inbox
    message_file = worker["inbox_path"] / f"{message_id}.json"
    try:
        with open(message_file, "w") as f:
            json.dump(message.to_dict(), f, indent=2)

        # Add to message history
        self.message_history[worker_id].append(message)

        logger.debug(f"Sent message {message_id} to worker {worker_id}")
        return message_id

    except Exception as e:
        logger.error(f"Failed to send message to worker {worker_id}: {str(e)}")
        raise
```

**Question-Answer Pattern**:

```python
async def ask_worker_question(
    self,
    worker_id: str,
    question: str,
    context: Dict[str, Any] = None,
    timeout: int = 300
) -> Optional[Dict[str, Any]]:
    """Ask a question to a worker and wait for response."""
    question_id = str(uuid.uuid4())

    question_payload = {
        "type": MessageType.QUESTION.value,
        "question_id": question_id,
        "question": question,
        "context": context or {},
        "reply_required": True
    }

    # Send question
    await self.send_to_worker(worker_id, question_payload)

    # Create pending question entry
    question_msg = Message(
        message_id=question_id,
        sender_id="master",
        recipient_id=worker_id,
        message_type=MessageType.QUESTION,
        payload=question_payload,
        timestamp=datetime.now(),
        expires_at=datetime.now() + timedelta(seconds=timeout)
    )

    self.pending_questions[question_id] = question_msg

    # Wait for response
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < timeout:
        # Check if answer received
        if question_id not in self.pending_questions:
            # Answer was processed and removed
            break

        await asyncio.sleep(1)

    # Check if we got an answer
    for message in reversed(self.message_history.get(worker_id, [])):
        if (message.message_type == MessageType.ANSWER and
            message.reply_to == question_id):
            return message.payload

    # Timeout - remove pending question
    if question_id in self.pending_questions:
        del self.pending_questions[question_id]

    logger.warning(f"Question {question_id} to worker {worker_id} timed out")
    return None
```

### 3.3 Integration with POLLN

**Applicability**: MEDIUM

**Integration Points**:

1. **A2A Package as Message**: A2A packages naturally map to communication messages
2. **Privacy Levels**: Message visibility controlled by privacy levels
3. **Subsumption Layers**: Message priority maps to subsumption hierarchy
4. **Causal Chains**: Message reply_to field enables causal tracking

**Implementation Strategy**:

```typescript
/**
 * POLLN Asynchronous Communication Layer
 * Extends A2A packages with file-based persistence
 */
export class AsyncCommunicationLayer {
  private colony: Colony;
  private commDir: string;
  private pendingQuestions: Map<string, A2APackage> = new Map();
  private messageHistory: Map<string, A2APackage[]> = new Map();

  constructor(colony: Colony, commDir: string = '/tmp/polln/communication') {
    this.colony = colony;
    this.commDir = commDir;

    // Create directories
    this.ensureDirectories();
  }

  /**
   * Send A2A package to agent
   */
  async sendToAgent(
    senderId: string,
    receiverId: string,
    package: A2APackage
  ): Promise<void> {
    // Set sender/receiver
    package.senderId = senderId;
    package.receiverId = receiverId;
    package.timestamp = Date.now();

    // Write to agent's inbox
    const inboxPath = path.join(
      this.commDir,
      'agents',
      receiverId,
      'inbox',
      `${package.id}.json`
    );

    await fs.writeFile(inboxPath, JSON.stringify(package, null, 2));

    // Add to history
    if (!this.messageHistory.has(receiverId)) {
      this.messageHistory.set(receiverId, []);
    }
    this.messageHistory.get(receiverId)!.push(package);
  }

  /**
   * Receive messages for agent
   */
  async receiveForAgent(agentId: string): Promise<A2APackage[]> {
    const inboxPath = path.join(this.commDir, 'agents', agentId, 'inbox');
    const archivePath = path.join(this.commDir, 'agents', agentId, 'archive');

    const messages: A2APackage[] = [];

    // Read all messages from inbox
    const files = await fs.readdir(inboxPath);
    for (const file of files) {
      if (file.endsWith('.json')) {
        const filePath = path.join(inboxPath, file);
        const content = await fs.readFile(filePath, 'utf-8');
        const pkg = JSON.parse(content) as A2APackage;

        messages.push(pkg);

        // Archive processed message
        const archiveFilePath = path.join(archivePath, file);
        await fs.rename(filePath, archiveFilePath);
      }
    }

    return messages;
  }

  /**
   * Ask agent a question (question-answer pattern)
   */
  async askAgent(
    senderId: string,
    receiverId: string,
    question: string,
    context: Record<string, unknown> = {},
    timeout: number = 300000 // 5 minutes
  ): Promise<A2APackage | null> {
    const questionId = uuidv4();

    // Create question A2A package
    const questionPackage: A2APackage<QuestionPayload> = {
      id: questionId,
      timestamp: Date.now(),
      senderId,
      receiverId,
      type: 'QUESTION',
      payload: {
        question,
        context,
        replyRequired: true
      },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.PRIVATE,
      layer: SubsumptionLayer.DELIBERATE
    };

    // Send question
    await this.sendToAgent(senderId, receiverId, questionPackage);

    // Track pending question
    this.pendingQuestions.set(questionId, questionPackage);

    // Wait for answer
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      // Check if answer received
      const messages = await this.receiveForAgent(senderId);
      const answer = messages.find(m =>
        m.type === 'ANSWER' &&
        m.replyTo === questionId
      );

      if (answer) {
        this.pendingQuestions.delete(questionId);
        return answer;
      }

      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Timeout
    this.pendingQuestions.delete(questionId);
    return null;
  }

  /**
   * Ensure communication directories exist
   */
  private async ensureDirectories(): Promise<void> {
    const dirs = [
      path.join(this.commDir, 'agents'),
      path.join(this.commDir, 'colony')
    ];

    for (const dir of dirs) {
      await fs.mkdir(dir, { recursive: true });
    }

    // Create directories for each agent
    for (const agent of this.colony.getAllAgents()) {
      const agentDir = path.join(this.commDir, 'agents', agent.id);
      await fs.mkdir(path.join(agentDir, 'inbox'), { recursive: true });
      await fs.mkdir(path.join(agentDir, 'outbox'), { recursive: true });
      await fs.mkdir(path.join(agentDir, 'archive'), { recursive: true });
    }
  }
}
```

### 3.4 Novelty Assessment

**Novelty**: 4/10

**Justification**:
- File-based messaging is a classic pattern
- Novel aspects: Question-answer pattern with timeout, message history tracking
- Integration with A2A packages adds structure

**Unique Contributions**:
- A2A packages as unified message format
- Privacy level enforcement
- Causal chain tracking through reply_to field

---

## 4. Merge Coordination with Conflict Resolution

### 4.1 Concept Overview

**Pattern**: When multiple workers modify shared resources in parallel, a merge coordinator detects conflicts, resolves them automatically when possible, and assigns resolution tasks for complex conflicts.

**Key Characteristics**:
- Conflict detection (file-level, dependency-level, interface-level)
- Automatic resolution for simple conflicts
- Manual resolution assignment for complex conflicts
- Dependency-ordered merge strategy
- Topological sorting for merge ordering

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│            MERGE COORDINATION WITH CONFLICT RESOLUTION           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PARALLEL WORK:                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Worker 1    │  │ Worker 2    │  │ Worker 3    │            │
│  │ Branch A    │  │ Branch B    │  │ Branch C    │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────┐               │
│  │         Shared Resource Modifications        │               │
│  └─────────────────────────────────────────────┘               │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────┐               │
│  │        Merge Coordinator                   │               │
│  │  1. Conflict Detection                     │               │
│  │  2. Conflict Analysis                      │               │
│  │  3. Resolution Strategy                    │               │
│  │  4. Merge Execution                         │               │
│  └─────────────────────────────────────────────┘               │
│                           │                                     │
│           ┌───────────────┼───────────────┐                     │
│           ▼               ▼               ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Auto      │  │   Assign    │  │    Merge    │            │
│  │  Resolve    │  │  to Worker  │  │  Execution  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  CONFLICT TYPES:                                               │
│  • File Conflict (multiple workers edit same file)             │
│  • Dependency Conflict (incompatible dependencies)              │
│  • Interface Conflict (breaking API changes)                   │
│  • Import Conflict (circular or missing imports)               │
│                                                                 │
│  MERGE STRATEGIES:                                             │
│  • Sequential (merge one at a time by priority)                │
│  • Dependency-Ordered (topological sort)                       │
│  • Parallel-Safe (merge non-conflicting in parallel)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Historical Implementation

**Source**: `multibot/orchestrator-master/merge_coordination.py`

**Conflict Data Structures**:

```python
class ConflictType(Enum):
    """Types of merge conflicts."""
    FILE_CONFLICT = "file_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    TYPE_CONFLICT = "type_conflict"
    IMPORT_CONFLICT = "import_conflict"
    INTERFACE_BREAKING = "interface_breaking"

@dataclass
class MergeConflict:
    """Represents a merge conflict that needs resolution."""
    conflict_id: str
    conflict_type: ConflictType
    files_involved: List[str]
    workers_involved: List[str]
    description: str
    severity: str  # "low", "medium", "high", "critical"
    auto_resolvable: bool
    resolution_strategy: Optional[str] = None
    assigned_worker: Optional[str] = None

@dataclass
class WorkerBranch:
    """Represents a worker's branch with their completed work."""
    worker_id: str
    branch_name: str
    task_ids: List[str]
    files_modified: List[str]
    test_status: str  # "passed", "failed", "not_run"
    dependencies: List[str]  # Other branches this depends on
    merge_priority: int  # Lower number = higher priority
```

**Conflict Analyzer**:

```python
class ConflictAnalyzer:
    """Analyzes potential conflicts between worker branches."""

    async def analyze_conflicts(self, branches: List[WorkerBranch]) -> List[MergeConflict]:
        """Analyze potential conflicts between branches."""
        conflicts = []

        # Check file-level conflicts
        file_conflicts = await self._check_file_conflicts(branches)
        conflicts.extend(file_conflicts)

        # Check dependency conflicts
        dep_conflicts = await self._check_dependency_conflicts(branches)
        conflicts.extend(dep_conflicts)

        # Check interface conflicts
        interface_conflicts = await self._check_interface_conflicts(branches)
        conflicts.extend(interface_conflicts)

        return conflicts

    async def _check_file_conflicts(self, branches: List[WorkerBranch]) -> List[MergeConflict]:
        """Check for files modified by multiple workers."""
        conflicts = []
        file_to_workers = {}

        # Map files to workers who modified them
        for branch in branches:
            for file_path in branch.files_modified:
                if file_path not in file_to_workers:
                    file_to_workers[file_path] = []
                file_to_workers[file_path].append(branch.worker_id)

        # Find files modified by multiple workers
        for file_path, workers in file_to_workers.items():
            if len(workers) > 1:
                conflict = MergeConflict(
                    conflict_id=f"file_conflict_{len(conflicts)}",
                    conflict_type=ConflictType.FILE_CONFLICT,
                    files_involved=[file_path],
                    workers_involved=workers,
                    description=f"File {file_path} modified by multiple workers: {', '.join(workers)}",
                    severity="medium",
                    auto_resolvable=await self._is_auto_resolvable_file_conflict(file_path, workers)
                )
                conflicts.append(conflict)

        return conflicts

    async def _is_auto_resolvable_file_conflict(self, file_path: str, workers: List[str]) -> bool:
        """Determine if a file conflict can be automatically resolved."""
        # Simple heuristics - can be enhanced
        file_ext = os.path.splitext(file_path)[1]

        # JSON files are often auto-resolvable if they're configuration
        if file_ext == '.json':
            return True

        # Documentation files are usually auto-resolvable
        if file_path.endswith(('.md', '.txt', '.rst')):
            return True

        # Code files require more analysis
        return False
```

**Merge Strategies**:

```python
class MergeStrategy:
    """Implements different merge strategies."""

    async def _sequential_merge(self, branches: List[WorkerBranch], conflicts: List[MergeConflict]) -> MergeReport:
        """Merge branches sequentially by priority."""
        # Sort branches by merge priority
        sorted_branches = sorted(branches, key=lambda b: b.merge_priority)

        for branch in sorted_branches:
            logger.info(f"Merging branch {branch.branch_name} from worker {branch.worker_id}")

            # Pre-merge checks
            await self._run_pre_merge_checks(branch, merge_report)

            # Perform merge
            merge_success = await self._perform_git_merge(branch)

            if merge_success:
                merge_report.branches_merged.append(branch.branch_name)

                # Post-merge tests
                test_results = await self._run_post_merge_tests(branch)
                merge_report.test_results[branch.branch_name] = test_results

                if not test_results.get("passed", False):
                    logger.warning(f"Tests failed after merging {branch.branch_name}")
                    # Could trigger conflict resolution here
            else:
                logger.error(f"Failed to merge branch {branch.branch_name}")
                merge_report.status = MergeStatus.FAILED
                break

        return merge_report

    async def _dependency_ordered_merge(self, branches: List[WorkerBranch], conflicts: List[MergeConflict]) -> MergeReport:
        """Merge branches in dependency order."""
        # Build dependency graph and topologically sort
        sorted_branches = await self._topological_sort_branches(branches)
        return await self._sequential_merge(sorted_branches, conflicts)

    async def _topological_sort_branches(self, branches: List[WorkerBranch]) -> List[WorkerBranch]:
        """Sort branches in dependency order."""
        # Simple topological sort based on dependencies
        sorted_branches = []
        remaining = branches.copy()

        while remaining:
            # Find branches with no unresolved dependencies
            ready = []
            for branch in remaining:
                deps_satisfied = all(
                    dep in [b.worker_id for b in sorted_branches]
                    for dep in branch.dependencies
                )
                if deps_satisfied:
                    ready.append(branch)

            if not ready:
                # Circular dependency or error - fall back to priority order
                ready = [min(remaining, key=lambda b: b.merge_priority)]

            # Add ready branches to sorted list
            sorted_branches.extend(ready)
            for branch in ready:
                remaining.remove(branch)

        return sorted_branches
```

**Conflict Resolver**:

```python
class ConflictResolver:
    """Resolves merge conflicts automatically or assigns them to workers."""

    async def resolve_conflict(self, conflict: MergeConflict, task_orchestrator) -> bool:
        """Attempt to resolve a conflict automatically or assign to worker."""
        logger.info(f"Resolving conflict {conflict.conflict_id}: {conflict.description}")

        if conflict.auto_resolvable and conflict.conflict_type in self.auto_resolvers:
            # Try automatic resolution
            success = await self.auto_resolvers[conflict.conflict_type](conflict)
            if success:
                logger.info(f"Automatically resolved conflict {conflict.conflict_id}")
                return True

        # Assign to appropriate worker for manual resolution
        await self._assign_conflict_to_worker(conflict, task_orchestrator)
        return False

    async def _assign_conflict_to_worker(self, conflict: MergeConflict, task_orchestrator):
        """Assign conflict resolution to an appropriate worker."""
        # Determine best worker for this type of conflict
        if conflict.severity in ["high", "critical"]:
            preferred_model = "opus"
        elif conflict.severity == "medium":
            preferred_model = "sonnet"
        else:
            preferred_model = "haiku"

        # Create conflict resolution task
        resolution_task = {
            "task_id": f"resolve_{conflict.conflict_id}",
            "title": f"Resolve {conflict.conflict_type.value}",
            "description": f"Resolve conflict: {conflict.description}",
            "type": "conflict_resolution",
            "priority": 9,  # High priority
            "preferred_model": preferred_model,
            "files_involved": conflict.files_involved,
            "context": {
                "conflict_type": conflict.conflict_type.value,
                "workers_involved": conflict.workers_involved,
                "severity": conflict.severity
            }
        }

        logger.info(f"Assigned conflict {conflict.conflict_id} to worker with {preferred_model} model")
```

### 4.3 Integration with POLLN

**Applicability**: HIGH

**Integration Points**:

1. **A2A Package Conflicts**: Conflicts are A2A packages with conflict metadata
2. **PlinkoLayer for Resolver Selection**: Use Plinko to select agents for conflict resolution
3. **Consensus for Resolution**: Multiple agents vote on conflict resolution strategy
4. **Colony Merge**: Colony manages merge coordination across agent groups

**Implementation Strategy**:

```typescript
/**
 * POLLN Merge Coordinator
 * Coordinates parallel work with conflict resolution
 */
export class PollnMergeCoordinator {
  private colony: Colony;

  constructor(colony: Colony) {
    this.colony = colony;
  }

  /**
   * Coordinate merge phase for parallel agent work
   */
  async coordinateMerge(
    agentWork: AgentWork[]
  ): Promise<MergeReport> {
    // Analyze conflicts
    const conflicts = await this.analyzeConflicts(agentWork);

    // Resolve auto-resolvable conflicts
    const resolved: MergeConflict[] = [];
    const unresolved: MergeConflict[] = [];

    for (const conflict of conflicts) {
      if (conflict.autoResolvable) {
        const success = await this.autoResolve(conflict);
        if (success) {
          resolved.push(conflict);
        } else {
          unresolved.push(conflict);
        }
      } else {
        unresolved.push(conflict);
      }
    }

    // Assign unresolved conflicts to agents
    for (const conflict of unresolved) {
      await this.assignConflictResolution(conflict);
    }

    // Execute merge strategy
    const mergeStrategy = this.selectMergeStrategy(agentWork);
    const mergeReport = await this.executeMerge(agentWork, mergeStrategy);

    return {
      conflictsDetected: conflicts.length,
      conflictsResolved: resolved.length,
      conflictsRemaining: unresolved.length,
      mergeReport
    };
  }

  /**
   * Analyze potential conflicts
   */
  private async analyzeConflicts(agentWork: AgentWork[]): Promise<MergeConflict[]> {
    const conflicts: MergeConflict[] = [];

    // Check for shared resource modifications
    const resourceToAgents = new Map<string, string[]>();

    for (const work of agentWork) {
      for (const resource of work.modifiedResources) {
        if (!resourceToAgents.has(resource)) {
          resourceToAgents.set(resource, []);
        }
        resourceToAgents.get(resource)!.push(work.agentId);
      }
    }

    // Find conflicts
    for (const [resource, agents] of resourceToAgents) {
      if (agents.length > 1) {
        conflicts.push({
          id: uuidv4(),
          type: 'resource_conflict',
          resource,
          agentsInvolved: agents,
          severity: 'medium',
          autoResolvable: await this.isAutoResolvable(resource),
          description: `Resource ${resource} modified by multiple agents: ${agents.join(', ')}`
        });
      }
    }

    return conflicts;
  }

  /**
   * Assign conflict resolution to agent
   */
  private async assignConflictResolution(conflict: MergeConflict): Promise<void> {
    // Select agents based on capabilities
    const eligibleAgents = this.colony.getActiveAgents().filter(agent => {
      const config = this.colony.getAgentConfig(agent.id);
      return config?.modelFamily === 'opus' || config?.modelFamily === 'sonnet';
    });

    // Use Plinko to select resolver
    const plinkoDecision = await this.colony.plinkoLayer.decide({
      context: {
        conflict,
        eligibleAgents: eligibleAgents.map(a => a.id)
      },
      proposals: eligibleAgents.map(agent => ({
        agentId: agent.id,
        confidence: agent.valueFunction,
        bid: conflict.severity === 'high' ? agent.valueFunction * 2 : agent.valueFunction
      }))
    });

    const selectedAgentId = plinkoDecision.selectedAgentId;
    if (!selectedAgentId) {
      throw new Error('No agent selected for conflict resolution');
    }

    // Create conflict resolution A2A package
    const resolutionPackage: A2APackage<ConflictResolutionTask> = {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.colony.id,
      receiverId: selectedAgentId,
      type: 'CONFLICT_RESOLUTION',
      payload: {
        conflictId: conflict.id,
        conflict,
        resolutionRequired: true
      },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.COLONY,
      layer: SubsumptionLayer.DELIBERATE
    };

    // Send to agent
    // (In real implementation, this would be sent via communication layer)
  }

  /**
   * Check if conflict is auto-resolvable
   */
  private async isAutoResolvable(resource: string): Promise<boolean> {
    // Check resource type
    const ext = path.extname(resource);

    // Configuration files are often auto-resolvable
    if (ext === '.json' || ext === '.yaml' || ext === '.yml') {
      return true;
    }

    // Documentation files are usually auto-resolvable
    if (ext === '.md' || ext === '.txt') {
      return true;
    }

    return false;
  }
}
```

### 4.4 Novelty Assessment

**Novelty**: 7/10

**Justification**:
- Merge coordination is common in version control
- Novel aspects: Model-tiered resolution (Opus for critical, Haiku for simple)
- Plinko-based resolver selection
- Integration with A2A packages for conflict tracking

**Unique Contributions**:
- Multi-agent conflict resolution with voting
- Automatic severity assessment
- Stigmergic conflict resolution (pheromone markers for conflict zones)

---

## 5. Agent Registry and Discovery

### 5.1 Concept Overview

**Pattern**: A centralized registry maintains agent metadata, capabilities, and status, enabling dynamic discovery and selection of agents for tasks.

**Key Characteristics**:
- Dynamic agent registration/deregistration
- Capability-based discovery
- Heartbeat monitoring for health detection
- Load tracking for task assignment
- Status tracking (starting, idle, busy, draining, offline)

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│                 AGENT REGISTRY AND DISCOVERY                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AGENT REGISTRATION:                                            │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Agent Registry                                  │           │
│  │ • Agent ID                                       │           │
│  │ • Name & Version                                 │           │
│  │ • Capabilities (list)                            │           │
│  │ • Status (starting/idle/busy/etc)               │           │
│  │ • Last Heartbeat                                 │           │
│  │ • Current Task                                   │           │
│  │ • Performance Metrics                            │           │
│  │ • Metadata (hostname, pid, startTime)           │           │
│  └─────────────────────────────────────────────────┘           │
│                     │                                          │
│                     ▼                                          │
│  DISCOVERY MECHANISMS:                                         │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Query by Capabilities                            │           │
│  │ • Find agents supporting [task-type]             │           │
│  │ • Filter by status (active/idle)                │           │
│  │ • Sort by performance/success-rate               │           │
│  │ • Limit to N results                             │           │
│  └─────────────────────────────────────────────────┘           │
│                     │                                          │
│                     ▼                                          │
│  ┌─────────────────────────────────────────────────┐           │
│  │ Heartbeat Monitoring                             │           │
│  │ • Agents send heartbeat every N seconds          │           │
│  │ • Registry updates last_heartbeat                │           │
│  │ • Agents timeout → marked offline               │           │
│  │ • Automatic re-registration on reconnect         │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  LOAD TRACKING:                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │ • maxConcurrentTasks per agent                   │           │
│  │ • Current task count                             │           │
│  │ • Load percentage (current/max)                  │           │
│  │ • Tasks completed/failed                         │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Historical Implementation

**Source**: `SwarmOrchestration/src/types/agent.ts`

**Agent Types**:

```typescript
export interface Agent {
  id: string;
  name: string;
  version: string;
  capabilities: string[];
  status: AgentStatus;
  lastHeartbeat: Date;
  currentTask?: string;
  tasksCompleted: number;
  tasksFailed: number;
  metadata: AgentMetadata;
}

export type AgentStatus = 'starting' | 'idle' | 'busy' | 'draining' | 'offline';

export interface AgentMetadata {
  hostname: string;
  pid: number;
  startTime: Date;
  maxConcurrentTasks: number;
  supportedTaskTypes: string[];
}

export interface AgentHeartbeat {
  agentId: string;
  timestamp: Date;
  status: AgentStatus;
  currentTask?: string;
  load?: number;
}

export interface AgentCapabilities {
  taskTypes: string[];
  maxConcurrentTasks: number;
  priority?: number;
}
```

**Registry Implementation** (Conceptual):

```typescript
class AgentRegistry {
  private agents: Map<string, Agent> = new Map();
  private heartbeatTimeout: number = 30000; // 30 seconds

  /**
   * Register agent
   */
  register(agent: Agent): void {
    this.agents.set(agent.id, agent);
    this.emit('agent_registered', agent);
  }

  /**
   * Unregister agent
   */
  unregister(agentId: string): void {
    const agent = this.agents.get(agentId);
    if (agent) {
      this.agents.delete(agentId);
      this.emit('agent_unregistered', agent);
    }
  }

  /**
   * Update heartbeat
   */
  updateHeartbeat(heartbeat: AgentHeartbeat): void {
    const agent = this.agents.get(heartbeat.agentId);
    if (agent) {
      agent.lastHeartbeat = heartbeat.timestamp;
      agent.status = heartbeat.status;
      agent.currentTask = heartbeat.currentTask;
      this.agents.set(heartbeat.agentId, agent);
    }
  }

  /**
   * Discover agents by capabilities
   */
  discover(capabilities: string[]): Agent[] {
    return Array.from(this.agents.values()).filter(agent => {
      // Agent must have at least one required capability
      return capabilities.some(cap =>
        agent.capabilities.includes(cap)
      );
    });
  }

  /**
   * Get available agents
   */
  getAvailable(): Agent[] {
    const now = new Date();
    return Array.from(this.agents.values()).filter(agent => {
      // Agent must be idle and have recent heartbeat
      return agent.status === 'idle' &&
        (now.getTime() - agent.lastHeartbeat.getTime()) < this.heartbeatTimeout;
    });
  }

  /**
   * Check for timed out agents
   */
  checkTimeouts(): void {
    const now = new Date();
    for (const [agentId, agent] of this.agents) {
      if ((now.getTime() - agent.lastHeartbeat.getTime()) > this.heartbeatTimeout) {
        agent.status = 'offline';
        this.emit('agent_timeout', agent);
      }
    }
  }
}
```

### 5.3 Integration with POLLN

**Applicability**: HIGH

**Integration Points**:

1. **Colony as Registry**: Extend Colony to act as agent registry
2. **BaseAgent Registration**: Agents self-register on initialization
3. **Capability Matching**: Match SPORE input/output topics
4. **Plinko Discovery**: Use Plinko for stochastic agent selection

**Implementation Strategy**:

```typescript
/**
 * POLLN Agent Registry
 * Extends Colony with discovery and registration
 */
export class AgentRegistry extends Colony {
  private heartbeats: Map<string, number> = new Map();
  private heartbeatTimeout: number = 30000; // 30 seconds

  /**
   * Register agent with capability discovery
   */
  registerAgentWithCapabilities(config: AgentConfig): AgentState {
    const state = super.registerAgent(config);

    // Register capabilities
    const capabilities = this.extractCapabilities(config);
    state.capabilities = capabilities;

    // Initialize heartbeat
    this.heartbeats.set(config.id, Date.now());

    this.emit('agent_registered', {
      agentId: config.id,
      state,
      capabilities
    });

    return state;
  }

  /**
   * Extract capabilities from agent config
   */
  private extractCapabilities(config: AgentConfig): string[] {
    const capabilities: string[] = [];

    // Add input topics as capabilities
    for (const topic of config.inputTopics) {
      capabilities.push(topic);
    }

    // Add model family as capability
    capabilities.push(`model:${config.modelFamily}`);

    // Add category as capability
    capabilities.push(`category:${config.categoryId}`);

    return capabilities;
  }

  /**
   * Discover agents by capability
   */
  discoverByCapabilities(requiredCapabilities: string[]): AgentState[] {
    const allAgents = this.getAllAgents();

    return allAgents.filter(agent => {
      const agentConfig = this.getAgentConfig(agent.id);
      if (!agentConfig) return false;

      const agentCapabilities = this.extractCapabilities(agentConfig);

      // Agent must have all required capabilities
      return requiredCapabilities.every(cap =>
        agentCapabilities.includes(cap)
      );
    });
  }

  /**
   * Update agent heartbeat
   */
  updateHeartbeat(agentId: string): void {
    this.heartbeats.set(agentId, Date.now());

    // Update agent status
    const agent = this.getAgent(agentId);
    if (agent && agent.status === 'offline') {
      this.activateAgent(agentId);
    }
  }

  /**
   * Check for timed out agents
   */
  checkTimeouts(): string[] {
    const now = Date.now();
    const timedOut: string[] = [];

    for (const [agentId, lastHeartbeat] of this.heartbeats) {
      if (now - lastHeartbeat > this.heartbeatTimeout) {
        this.deactivateAgent(agentId);
        timedOut.push(agentId);
      }
    }

    return timedOut;
  }

  /**
   * Get best agent for task using Plinko
   */
  async selectAgentForTask(task: Task): Promise<string | null> {
    // Discover capable agents
    const capableAgents = this.discoverByCapabilities(task.requiredCapabilities);

    if (capableAgents.length === 0) {
      return null;
    }

    // Use Plinko to select agent
    const plinkoDecision = await this.plinkoLayer.decide({
      context: {
        task,
        capableAgents: capableAgents.map(a => a.id)
      },
      proposals: capableAgents.map(agent => ({
        agentId: agent.id,
        confidence: agent.valueFunction,
        bid: agent.valueFunction * (1 / (capableAgents.indexOf(agent) + 1))
      }))
    });

    return plinkoDecision.selectedAgentId || null;
  }
}
```

### 5.4 Novelty Assessment

**Novelty**: 5/10

**Justification**:
- Service discovery is a well-established pattern
- Novel aspects: SPORE-based capability matching, Plinko-based selection
- Integration with A2A packages for registration

**Unique Contributions**:
- Capability matching based on SPORE input/output topics
- Stigmergic discovery (agents leave "trails" for capabilities)
- Value-function-based bidding for agent selection

---

## 6. Consensus Through Weighted Voting

### 6.1 Concept Overview

**Pattern**: Agents vote on decisions, with votes weighted by their value function (success rate), enabling collective intelligence and conflict resolution.

**Key Characteristics**:
- Weighted voting based on agent performance
- Multiple consensus types (full, fast path, emergency)
- Quorum requirements
- Decision time tracking
- Vote traceability

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│              CONSENSUS THROUGH WEIGHTED VOTING                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CONSENSUS TYPES:                                               │
│  ┌─────────────────────────────────────────────────┐           │
│  │ WEIGHTED_VOTING  | Agents vote, weighted by    │           │
│  │                 | value function (success)     │           │
│  │ FAST_PATH        | Single agent can decide     │           │
│  │                 | if confidence > threshold    │           │
│  │ EMERGENCY        | Safety-critical, requires   │           │
│  │                 | unanimous agreement          │           │
│  │ FULL_CONSENSUS   | All agents must agree      │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  VOTING PROCESS:                                               │
│  ┌─────────────────────────────────────────────────┐           │
│  │ 1. Proposal submitted                           │           │
│  │ 2. Agents evaluate proposal                     │           │
│  │ 3. Agents cast votes (yes/no)                   │           │
│  │ 4. Votes weighted by value function             │           │
│  │ 5. Tally votes                                   │           │
│  │ 6. Check quorum                                  │           │
│  │ 7. Return result                                 │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  WEIGHT CALCULATION:                                           │
│  weight = value_function * success_rate                         │
│                                                                 │
│  value_function ∈ [0, 1]                                       │
│  success_rate = success_count / (success_count + failure_count) │
│                                                                 │
│  QUORUM REQUIREMENTS:                                           │
│  • Simple majority: > 50% of weighted votes                    │
│  • Supermajority: > 66% of weighted votes                      │
│  • Unanimous: 100% agreement                                   │
│  • Quorum reached: Minimum participation met                    │
│                                                                 │
│  EXAMPLE:                                                       │
│  Proposal: "Merge branch feature-x into main"                   │
│                                                                 │
│  Agent A (value=0.9, success=95%):  weight=0.855 → YES        │
│  Agent B (value=0.7, success=85%):  weight=0.595 → YES        │
│  Agent C (value=0.5, success=70%):  weight=0.350 → NO         │
│  Agent D (value=0.3, success=60%):  weight=0.180 → YES        │
│                                                                 │
│  Total weight: 1.98                                             │
│  Votes for: 0.855 + 0.595 + 0.180 = 1.63 (82%)               │
│  Result: PASS (supermajority)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Historical Implementation

**Source**: `POLLN src/core/types.ts` (ConsensusVote, ConsensusResult)

**Consensus Types**:

```typescript
export enum ConsensusType {
  WEIGHTED_VOTING = 'WEIGHTED_VOTING',
  FAST_PATH = 'FAST_PATH',
  EMERGENCY = 'EMERGENCY',
  FULL_CONSENSUS = 'FULL_CONSENSUS'
}

export interface ConsensusVote {
  agentId: string;
  vote: boolean;
  weight: number;
  timestamp: number;
}

export interface ConsensusResult {
  type: ConsensusType;
  passed: boolean;
  votesFor: number;
  votesAgainst: number;
  totalWeight: number;
  quorumReached: boolean;
  decisionTime: number;
}
```

**Consensus Implementation** (Conceptual):

```typescript
class ConsensusManager {
  private colony: Colony;

  constructor(colony: Colony) {
    this.colony = colony;
  }

  /**
   * Achieve consensus on proposal
   */
  async achieveConsensus(
    proposal: Proposal,
    consensusType: ConsensusType = ConsensusType.WEIGHTED_VOTING
  ): Promise<ConsensusResult> {
    const startTime = Date.now();
    const votes: ConsensusVote[] = [];

    // Get active agents
    const activeAgents = this.colony.getActiveAgents();

    // Collect votes
    for (const agent of activeAgents) {
      const vote = await this.requestVote(agent, proposal);
      votes.push(vote);
    }

    // Calculate weighted totals
    const votesFor = votes
      .filter(v => v.vote)
      .reduce((sum, v) => sum + v.weight, 0);

    const votesAgainst = votes
      .filter(v => !v.vote)
      .reduce((sum, v) => sum + v.weight, 0);

    const totalWeight = votesFor + votesAgainst;

    // Check quorum
    const quorumReached = totalWeight >= this.calculateQuorumThreshold();

    // Determine result
    let passed = false;
    switch (consensusType) {
      case ConsensusType.WEIGHTED_VOTING:
        passed = votesFor > totalWeight * 0.5; // Simple majority
        break;
      case ConsensusType.FULL_CONSENSUS:
        passed = votesAgainst === 0; // Unanimous
        break;
      case ConsensusType.EMERGENCY:
        passed = votesFor === totalWeight && quorumReached; // All must agree
        break;
      case ConsensusType.FAST_PATH:
        // Single agent can decide if confident
        passed = votes.some(v => v.vote && v.weight > 0.9);
        break;
    }

    return {
      type: consensusType,
      passed,
      votesFor,
      votesAgainst,
      totalWeight,
      quorumReached,
      decisionTime: Date.now() - startTime
    };
  }

  /**
   * Request vote from agent
   */
  private async requestVote(
    agent: AgentState,
    proposal: Proposal
  ): Promise<ConsensusVote> {
    // Calculate weight based on value function and success rate
    const successRate = agent.successCount /
      (agent.successCount + agent.failureCount);
    const weight = agent.valueFunction * successRate;

    // Request vote (in real implementation, this would be A2A)
    const vote = await this.evaluateProposal(agent, proposal);

    return {
      agentId: agent.id,
      vote,
      weight,
      timestamp: Date.now()
    };
  }

  /**
   * Evaluate proposal (placeholder)
   */
  private async evaluateProposal(
    agent: AgentState,
    proposal: Proposal
  ): Promise<boolean> {
    // In real implementation, this would send A2A package to agent
    // and wait for response
    return true;
  }

  /**
   * Calculate quorum threshold
   */
  private calculateQuorumThreshold(): number {
    const activeAgents = this.colony.getActiveAgents();
    const totalValue = activeAgents.reduce(
      (sum, a) => sum + a.valueFunction,
      0
    );
    return totalValue * 0.5; // 50% participation required
  }
}
```

### 6.3 Integration with POLLN

**Applicability**: HIGH

**Integration Points**:

1. **PlinkoLayer as Fast Path**: Plinko provides fast-path decision making
2. **A2A Package Voting**: Votes are A2A packages with causal chain
3. **Colony Consensus**: Colony manages consensus across agents
4. **Value Function Weighting**: Agent performance influences vote weight

**Implementation Strategy**:

```typescript
/**
 * POLLN Consensus Manager
 * Integrates with Plinko and A2A packages
 */
export class PollnConsensusManager {
  private colony: Colony;
  private plinkoLayer: PlinkoLayer;

  constructor(colony: Colony, plinkoLayer: PlinkoLayer) {
    this.colony = colony;
    this.plinkoLayer = plinkoLayer;
  }

  /**
   * Achieve consensus on decision
   */
  async achieveConsensus(
    proposal: Proposal,
    consensusType: ConsensusType
  ): Promise<ConsensusResult> {
    // Try fast path first
    if (consensusType === ConsensusType.FAST_PATH) {
      const fastPathResult = await this.tryFastPath(proposal);
      if (fastPathResult) {
        return fastPathResult;
      }
    }

    // Fall back to weighted voting
    return this.weightedVoting(proposal);
  }

  /**
   * Try fast path (Plinko-based)
   */
  private async tryFastPath(proposal: Proposal): Promise<ConsensusResult | null> {
    const startTime = Date.now();

    // Use Plinko to make decision
    const plinkoDecision = await this.plinkoLayer.decide({
      context: {
        proposal,
        consensusType: ConsensusType.FAST_PATH
      },
      proposals: await this.generateProposals(proposal)
    });

    // Check if confident enough
    if (plinkoDecision.selectedConfidence && plinkoDecision.selectedConfidence > 0.9) {
      return {
        type: ConsensusType.FAST_PATH,
        passed: plinkoDecision.outcome === 'success',
        votesFor: plinkoDecision.selectedConfidence,
        votesAgainst: 1 - plinkoDecision.selectedConfidence,
        totalWeight: 1.0,
        quorumReached: true,
        decisionTime: Date.now() - startTime
      };
    }

    return null;
  }

  /**
   * Weighted voting consensus
   */
  private async weightedVoting(proposal: Proposal): Promise<ConsensusResult> {
    const startTime = Date.now();
    const votes: ConsensusVote[] = [];

    // Create voting A2A package
    const votingPackage: A2APackage<VotingRequest> = {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.colony.id,
      receiverId: 'broadcast',
      type: 'CONSENSUS_VOTE_REQUEST',
      payload: {
        proposal,
        consensusType: ConsensusType.WEIGHTED_VOTING
      },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.COLONY,
      layer: SubsumptionLayer.DELIBERATE
    };

    // Broadcast to active agents
    const activeAgents = this.colony.getActiveAgents();
    for (const agent of activeAgents) {
      const vote = await this.requestAgentVote(agent, proposal);
      votes.push(vote);
    }

    // Calculate results
    const votesFor = votes
      .filter(v => v.vote)
      .reduce((sum, v) => sum + v.weight, 0);

    const votesAgainst = votes
      .filter(v => !v.vote)
      .reduce((sum, v) => sum + v.weight, 0);

    const totalWeight = votesFor + votesAgainst;

    return {
      type: ConsensusType.WEIGHTED_VOTING,
      passed: votesFor > votesAgainst,
      votesFor,
      votesAgainst,
      totalWeight,
      quorumReached: totalWeight > 0,
      decisionTime: Date.now() - startTime
    };
  }

  /**
   * Request vote from agent
   */
  private async requestAgentVote(
    agent: AgentState,
    proposal: Proposal
  ): Promise<ConsensusVote> {
    // Calculate weight
    const successRate = agent.successCount /
      (agent.successCount + agent.failureCount);
    const weight = agent.valueFunction * successRate;

    // Send voting request A2A package
    const votingPackage: A2APackage<VotingRequest> = {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.colony.id,
      receiverId: agent.id,
      type: 'CONSENSUS_VOTE_REQUEST',
      payload: {
        proposal,
        consensusType: ConsensusType.WEIGHTED_VOTING
      },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: PrivacyLevel.PRIVATE,
      layer: SubsumptionLayer.DELIBERATE
    };

    // In real implementation, send and wait for response
    // For now, simulate vote
    const vote = agent.valueFunction > 0.5;

    return {
      agentId: agent.id,
      vote,
      weight,
      timestamp: Date.now()
    };
  }

  /**
   * Generate proposals for Plinko
   */
  private async generateProposals(proposal: Proposal): Promise<Proposal[]> {
    const activeAgents = this.colony.getActiveAgents();

    return activeAgents.map(agent => ({
      agentId: agent.id,
      confidence: agent.valueFunction,
      bid: agent.valueFunction,
      explanation: `Agent ${agent.id} vote on proposal`
    }));
  }
}
```

### 6.4 Novelty Assessment

**Novelty**: 7/10

**Justification**:
- Weighted voting is common in distributed systems
- Novel aspects: Value function based weighting, Plinko fast-path
- Integration with A2A packages for vote traceability

**Unique Contributions**:
- Dynamic weight based on real-time performance
- Fast-path optimization using Plinko
- Causal chain tracking for auditability

---

## Summary and Recommendations

### Pattern Comparison

| Pattern | Complexity | Novelty | Applicability | Priority |
|---------|-----------|---------|--------------|----------|
| **Hierarchical Master-Worker** | Medium | 6/10 | HIGH | HIGH |
| **Priority-Based Task Queuing** | Medium | 5/10 | HIGH | HIGH |
| **File-Based Async Communication** | Low | 4/10 | MEDIUM | LOW |
| **Merge Coordination** | High | 7/10 | HIGH | HIGH |
| **Agent Registry & Discovery** | Low | 5/10 | HIGH | MEDIUM |
| **Weighted Voting Consensus** | Medium | 7/10 | HIGH | MEDIUM |

### Integration Roadmap

#### Phase 1: High Priority (Weeks 1-4)
1. **Hierarchical Master-Worker**: Extend Colony for lifecycle management
2. **Priority-Based Task Queuing**: Implement task queue with Plinko selection
3. **Merge Coordination**: Add conflict detection and resolution

#### Phase 2: Medium Priority (Weeks 5-8)
4. **Agent Registry & Discovery**: Capability-based discovery with SPORE
5. **Weighted Voting Consensus**: Consensus with value function weighting

#### Phase 3: Optional (Weeks 9-10)
6. **File-Based Async Communication**: If persistence needed beyond A2A

### Key Integration Points

All patterns integrate with existing POLLN components:

- **BaseAgent**: All agents inherit from BaseAgent
- **Colony**: Colony acts as registry and coordinator
- **A2A Package**: Communication and state tracking
- **PlinkoLayer**: Stochastic selection and decision making
- **Value Function**: Performance-based weighting and prioritization

### Novel Contributions

This research identifies several novel aspects that can strengthen POLLN:

1. **Model-Tiered Workers**: Opus/Sonnet/Haiku hierarchy for task complexity matching
2. **Plinko-Based Selection**: Stochastic agent selection replacing deterministic routing
3. **A2A Traceability**: All coordination decisions tracked in causal chains
4. **Value Function Weighting**: Dynamic weighting based on real-time performance
5. **Stigmergic Discovery**: Capability discovery through virtual pheromones

---

**Document Status:** COMPLETE
**Next Steps:** Begin Phase 1 implementation
**Review Date:** After Phase 1 completion

---

*Research Agent:* Coordination Architect
*Date:* 2026-03-06
*Version:* 1.0.0
*Repository:* https://github.com/SuperInstance/POLLN
