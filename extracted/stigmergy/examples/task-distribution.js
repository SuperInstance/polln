/**
 * Task Distribution Example
 *
 * This example shows how to use stigmergy for distributed task distribution
 * in a worker pool scenario.
 */

const { Stigmergy, PheromoneType, TrailFollower } = require('@superinstance/stigmergy');

// Create a distributed worker pool using stigmergy
class DistributedTaskPool {
  constructor() {
    this.stigmergy = new Stigmergy({
      maxPheromones: 500,
      defaultHalfLife: 30000, // 30 seconds
      evaporationInterval: 5000 // Clean up every 5 seconds
    });

    this.workers = new Map();
    this.tasks = new Map();
    this.completedTasks = 0;
  }

  // Submit a task for processing
  submitTask(task) {
    console.log(`Submitting task: ${task.id} (${task.type})`);
    this.tasks.set(task.id, task);

    // Signal that work is needed
    this.stigmergy.deposit(
      'system',
      PheromoneType.RECRUIT,
      { taskType: task.type },
      task.priority || 0.5,
      new Map([
        ['taskId', task.id],
        ['deadline', task.deadline || Date.now() + 60000],
        ['estimatedTime', task.estimatedTime || 10000]
      ])
    );
  }

  // Register a worker
  registerWorker(workerId, capabilities = ['data-processing', 'image-analysis']) {
    console.log(`Registering worker: ${workerId}`);

    const follower = new TrailFollower(this.stigmergy, workerId);
    this.workers.set(workerId, {
      follower,
      capabilities,
      currentTask: null,
      completed: 0
    });

    // Start worker loop
    this.startWorkerLoop(workerId);
  }

  // Worker finds and processes tasks
  startWorkerLoop(workerId) {
    const worker = this.workers.get(workerId);
    if (!worker) return;

    const interval = setInterval(() => {
      // If worker is busy, check if task is done
      if (worker.currentTask) {
        if (Date.now() > worker.currentTask.startTime + worker.currentTask.duration) {
          this.completeTask(workerId);
        }
        return;
      }

      // Look for available tasks
      for (const capability of worker.capabilities) {
        const result = worker.follower.followTrail(
          { taskType: capability },
          PheromoneType.RECRUIT
        );

        if (result.found) {
          const taskId = result.pheromone.metadata.get('taskId');
          const task = this.tasks.get(taskId);

          if (task && !task.assigned) {
            this.assignTask(workerId, task);
            break;
          }
        }
      }
    }, 1000);

    worker.interval = interval;
  }

  assignTask(workerId, task) {
    const worker = this.workers.get(workerId);
    if (!worker) return;

    console.log(`Worker ${workerId} assigned task ${task.id}`);
    task.assigned = true;
    task.assignedTo = workerId;
    task.startTime = Date.now();
    task.duration = task.estimatedTime || (Math.random() * 5000 + 2000);
    worker.currentTask = task;

    // Signal that we're working
    this.stigmergy.deposit(
      workerId,
      PheromoneType.NEST,
      { workerId },
      0.8,
      new Map([['status', 'busy'], ['task', task.id]])
    );
  }

  completeTask(workerId) {
    const worker = this.workers.get(workerId);
    if (!worker || !worker.currentTask) return;

    const task = worker.currentTask;
    console.log(`Worker ${workerId} completed task ${task.id}`);

    // Update stats
    this.completedTasks++;
    worker.completed++;
    this.tasks.delete(task.id);
    worker.currentTask = null;

    // Leave a success signal
    this.stigmergy.deposit(
      workerId,
      PheromoneType.RESOURCE,
      { taskType: task.type },
      0.9,
      new Map([
        ['completionTime', Date.now()],
        ['taskId', task.id],
        ['workerId', workerId]
      ])
    );

    // Worker available again
    this.stigmergy.deposit(
      workerId,
      PheromoneType.NEST,
      { workerId },
      1.0,
      new Map([['status', 'available']])
    );
  }

  // Monitor system status
  getStatus() {
    const stats = this.stigmergy.getStats();
    const availableWorkers = Array.from(this.workers.values())
      .filter(w => !w.currentTask).length;
    const busyWorkers = Array.from(this.workers.values())
      .filter(w => w.currentTask).length;

    return {
      pheromones: stats.activePheromones,
      pendingTasks: this.tasks.size,
      completedTasks: this.completedTasks,
      availableWorkers,
      busyWorkers,
      totalWorkers: this.workers.size
    };
  }

  shutdown() {
    console.log('Shutting down task pool...');
    this.workers.forEach(worker => {
      if (worker.interval) {
        clearInterval(worker.interval);
      }
    });
    this.stigmergy.shutdown();
  }
}

// Example usage
console.log('=== TASK DISTRIBUTION EXAMPLE ===\n');

const pool = new DistributedTaskPool();

// Register workers with different capabilities
pool.registerWorker('worker-1', ['data-processing']);
pool.registerWorker('worker-2', ['data-processing', 'image-analysis']);
pool.registerWorker('worker-3', ['image-analysis', 'video-processing']);

// Submit tasks
pool.submitTask({
  id: 'task-1',
  type: 'data-processing',
  priority: 0.8,
  estimatedTime: 3000
});

pool.submitTask({
  id: 'task-2',
  type: 'image-analysis',
  priority: 0.9,
  estimatedTime: 5000
});

pool.submitTask({
  id: 'task-3',
  type: 'data-processing',
  priority: 0.7,
  estimatedTime: 2000
});

pool.submitTask({
  id: 'task-4',
  type: 'video-processing',
  priority: 0.6,
  estimatedTime: 8000
});

// Monitor progress
const monitorInterval = setInterval(() => {
  const status = pool.getStatus();
  console.log(`\nStatus: ${status.pendingTasks} pending, ${status.completedTasks} completed, ${status.availableWorkers} available workers`);

  if (status.pendingTasks === 0) {
    console.log('\nAll tasks completed!');
    clearInterval(monitorInterval);
    pool.shutdown();
  }
}, 1000);