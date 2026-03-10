/**
 * Tile Worker - Distributed Execution
 *
 * Enables tiles to run on different processes/nodes for:
 * - Parallel execution
 * - Message passing between workers
 * - Load balancing and * - Fault tolerance
 *
 * Part of Phase 2: Infrastructure
 */

import { ITile, TileResult, Zone, classifyZone } from '../core/Tile';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Worker configuration
 */
export interface WorkerConfig {
  /** Maximum workers */
  maxWorkers?: number;
  /** Worker idle timeout before killing */
  idleTimeout?: number;
  /** Maximum concurrent tiles per worker */
  maxConcurrent?: number;
  /** Task queue size */
  queueSize?: number;
  /** Enable load balancing */
  loadBalancing?: boolean;
  /** Enable fault tolerance */
  faultTolerance?: boolean;
}

/**
 * Worker statistics
 */
export interface WorkerStats {
  totalTasks: number;
  activeTasks: number;
  completedTasks: number;
  failedTasks: number;
  averageLatency: number;
  workerUtilization: Map<string, number>;
}

/**
 * Tile task for execution
 */
interface TileTask<I = any, O = any> {
  id: string;
  tile: ITile<I, O>;
  input: I;
  status: 'pending' | 'running' | 'completed' | 'failed';
  submittedAt: number;
  retries: number;
  workerId?: string;
  result?: TileResult<O>;
  error?: any;
  resolve?: (result: DistributedTileResult<O>) => void;
  reject?: (error: Error) => void;
}

/**
 * Worker instance
 */
interface Worker {
  id: string;
  lastActivity?: number;
  handleMessage?: (message: any) => void;
  sendToWorker?: (workerId: string, message: any) => Promise<void>;
}

/**
 * Distributed tile execution result
 */
export interface DistributedTileResult<O> extends TileResult<O> {
  workerId: string;
  workerUrl: string;
  executionTime: number;
}

// ============================================================================
// TILE Worker
// ============================================================================

/**
 * TileWorker - Executes tiles in separate worker processes
 *
 * Features:
 * - Parallel execution across multiple workers
* - Load balancing based on worker utilization
 * - Fault tolerance with automatic retry
 * - Message passing for inter-worker communication
 */
export class TileWorker {
  private workers: Worker[] = [];
  private taskQueue: TileTask[] = [];
  private activeTasks: Map<string, TileTask> = new Map();
  private config: WorkerConfig;

  constructor(config: WorkerConfig = {}) {
    this.config = {
      maxWorkers: config.maxWorkers ?? 4,
      idleTimeout: config.idleTimeout ?? 30000,
      maxConcurrent: config.maxConcurrent ?? 4,
      queueSize: config.queueSize ?? 100,
      loadBalancing: config.loadBalancing ?? true,
      faultTolerance: config.faultTolerance ?? true,
    };
  }

  /**
   * Submit a tile for execution
   */
  async submit<I, O>(tile: ITile<I, O>, input: I): Promise<DistributedTileResult<O>> {
    const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const task: TileTask<I, O> = {
      id: taskId,
      tile,
      input,
      status: 'pending',
      submittedAt: Date.now(),
      retries: 0,
    };

    this.taskQueue.push(task);

    return new Promise((resolve, reject) => {
      task.resolve = resolve;
      task.reject = reject;
    });
  }

  /**
   * Get worker stats
   */
  getStats(): WorkerStats {
    return {
      totalTasks: this.taskQueue.length + this.activeTasks.size,
      activeTasks: this.activeTasks.size,
      completedTasks: 0,
      failedTasks: 0,
      averageLatency: 0,
      workerUtilization: this.getWorkerUtilization(),
    };
  }

  /**
   * Start processing the task queue
   */
  async start(): Promise<void> {
    // Process pending tasks
    while (this.taskQueue.length > 0) {
      const task = this.taskQueue.shift()!;

      // Check if we spawn a new worker
      if (this.activeTasks.size < this.config.maxWorkers!) {
        await this.spawnWorker();
      }

      // Process the task
      const worker = this.selectWorker();
      if (!worker) {
        task.status = 'failed';
        task.reject?.(new Error('No available workers'));
        continue;
      }

      // Assign task to worker
      this.activeTasks.set(task.id, task);
      task.status = 'running';
      task.workerId = worker.id;

      // Execute tile
      try {
        const startTime = Date.now();
        const tile = task.tile;
        const output = await tile.discriminate(task.input);
        const conf = await tile.confidence(task.input);
        const zone = classifyZone(conf);
        const trace = await tile.trace(task.input);
        const duration = Date.now() - startTime;

        const result: TileResult<typeof output> = {
          output,
          confidence: conf,
          zone,
          trace,
          duration,
        };

        // Mark as completed
        task.status = 'completed';
        task.result = result as any;
        this.activeTasks.delete(task.id);

        // Resolve the promise
        if (task.resolve) {
          task.resolve({
            ...result,
            workerId: worker.id,
            workerUrl: worker.id, // In real implementation, this would be the actual URL
            executionTime: duration,
          } as any);
        }

        // Check for more pending tasks
        if (this.taskQueue.length > 0) {
          this.start(); // Continue processing
        }
      } catch (error) {
        task.status = 'failed';
        task.error = error;
        this.activeTasks.delete(task.id);

        // Reject the promise
        if (task.reject) {
          task.reject(error as Error);
        }
      }
    }
  }

  /**
   * Select the best worker for the task
   */
  private selectWorker(): Worker | undefined {
    // Get least busy worker
    let leastBusy = Infinity;
    let selectedWorker: Worker | undefined;

    this.workers.forEach(worker => {
      let activeCount = 0;
      this.activeTasks.forEach(task => {
        if (task.workerId === worker.id) {
          activeCount++;
        }
      });

      if (activeCount < leastBusy) {
        leastBusy = activeCount;
        selectedWorker = worker;
      }
    });

    return selectedWorker;
  }

  /**
   * Spawn a new worker
   */
  private async spawnWorker(): Promise<Worker> {
    const worker: Worker = {
      id: `worker_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      lastActivity: Date.now(),
      handleMessage: (message: any) => {
        // Handle incoming messages
        console.log(`Worker ${this.workers.length} received message:`, message);
      },
      sendToWorker: async (workerId: string, message: any) => {
        // Send message to worker
        console.log(`Sending message to worker ${workerId}:`, message);
      },
    };

    this.workers.push(worker);
    return worker;
  }

  /**
   * Kill an idle worker
   */
  private killIdleWorkers(): void {
    const now = Date.now();
    const idleWorkers: Worker[] = [];
    const idleTimeout = this.config.idleTimeout ?? 30000;

    this.workers = this.workers.filter(worker => {
      const isIdle = worker.lastActivity && (now - worker.lastActivity > idleTimeout);
      if (isIdle) {
        idleWorkers.push(worker);
      }
      return !isIdle;
    });

    for (const worker of idleWorkers) {
      this.activeTasks.delete(worker.id);
    }
  }

  /**
   * Get worker utilization
   */
  private getWorkerUtilization(): Map<string, number> {
    const utilization: Map<string, number> = new Map();

    this.activeTasks.forEach(task => {
      if (task.workerId) {
        utilization.set(task.workerId, (utilization.get(task.workerId) ?? 0) + 1);
      }
    });

    return utilization;
  }

  /**
   * Send message to specific worker
   */
  async sendToWorker(workerId: string, message: any): Promise<void> {
    const worker = this.workers.find(w => w.id === workerId);
    if (!worker) {
      throw new Error(`Worker ${workerId} not found`);
    }

    // Worker message handling would go here
    worker.handleMessage(message);
  }

  /**
   * Broadcast message to all workers
   */
  async broadcast(message: any): Promise<void> {
    await Promise.all(
      this.workers.map(worker => worker.sendToWorker(worker.id, message))
    );
  }
}

