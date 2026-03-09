/**
 * POLLN Coding Domain
 *
 * Optimized configurations and task definitions for software development tasks.
 *
 * @module domains/coding
 */

export { CODING_DOMAIN_CONFIG } from './config';
export { CODE_QUALITY_VALUE_CONFIG } from './value-network-config';
export { CODING_TASKS } from './tasks';

// Re-export types
export type { TaskDefinition } from '../../core/types';
export type { ValueNetworkConfig } from '../../core/types';

/**
 * Get coding domain configuration
 */
export function getCodingDomainConfig() {
  return CODING_DOMAIN_CONFIG;
}

/**
 * Get code quality value network configuration
 */
export function getCodeQualityValueConfig() {
  return CODE_QUALITY_VALUE_CONFIG;
}

/**
 * Get task definition by name
 */
export function getTask(taskName: string) {
  return CODING_TASKS[taskName];
}

/**
 * Get all task definitions
 */
export function getAllTasks() {
  return CODING_TASKS;
}

/**
 * Get code generation tasks
 */
export function getCodeGenerationTasks() {
  return Object.entries(CODING_TASKS)
    .filter(([_, task]) => task.expertise === 'code_generation')
    .reduce((acc, [name, task]) => ({ ...acc, [name]: task }), {});
}

/**
 * Get code review tasks
 */
export function getCodeReviewTasks() {
  return Object.entries(CODING_TASKS)
    .filter(([_, task]) => task.expertise === 'code_review')
    .reduce((acc, [name, task]) => ({ ...acc, [name]: task }), {});
}

/**
 * Get debugging tasks
 */
export function getDebuggingTasks() {
  return Object.entries(CODING_TASKS)
    .filter(([_, task]) => task.expertise === 'debugging')
    .reduce((acc, [name, task]) => ({ ...acc, [name]: task }), {});
}

/**
 * Get refactoring tasks
 */
export function getRefactoringTasks() {
  return Object.entries(CODING_TASKS)
    .filter(([_, task]) => task.expertise === 'refactoring')
    .reduce((acc, [name, task]) => ({ ...acc, [name]: task }), {});
}
