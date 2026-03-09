/**
 * Coding Domain Task Definitions
 *
 * Predefined task configurations for common software development workflows.
 *
 * Generated: 2026-03-07
 * Source: Python simulations in simulations/domains/coding/
 */

import { TaskDefinition } from '../../core/types';

export const CODING_TASKS: Record<string, TaskDefinition> = {
  // ============================================================================
  // CODE GENERATION TASKS
  // ============================================================================

  generate_function: {
    name: 'generate_function',
    description: 'Generate a function from specification',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 15,
    maxTokens: 2000,
    useValueNetwork: true,
  },

  generate_class: {
    name: 'generate_class',
    description: 'Generate a class from specification',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 15,
    maxTokens: 3000,
    useValueNetwork: true,
  },

  generate_api: {
    name: 'generate_api',
    description: 'Generate API endpoint implementation',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 20,
    maxTokens: 2500,
    useValueNetwork: true,
  },

  generate_module: {
    name: 'generate_module',
    description: 'Generate a complete module with multiple functions',
    agentType: 'role',
    expertise: 'code_generation',
    temperature: 0.3,
    checkpoints: 25,
    maxTokens: 4000,
    useValueNetwork: true,
  },

  generate_tests: {
    name: 'generate_tests',
    description: 'Generate unit tests for existing code',
    agentType: 'task',
    expertise: 'code_generation',
    temperature: 0.2,
    checkpoints: 10,
    maxTokens: 2000,
    useValueNetwork: true,
  },

  // ============================================================================
  // CODE REVIEW TASKS
  // ============================================================================

  review_code: {
    name: 'review_code',
    description: 'Review code for bugs and issues',
    agentType: 'role',
    expertise: 'code_review',
    useValueNetwork: true,
    valueNetwork: 'code_quality',
    minConfidence: 0.3,
    maxIssues: 50,
  },

  detect_bugs: {
    name: 'detect_bugs',
    description: 'Detect bugs in code',
    agentType: 'task',
    expertise: 'code_review',
    temperature: 0.2,
    useValueNetwork: true,
  },

  security_review: {
    name: 'security_review',
    description: 'Review code for security vulnerabilities',
    agentType: 'task',
    expertise: 'code_review',
    temperature: 0.1,
    useValueNetwork: true,
    focus: ['security'],
  },

  performance_review: {
    name: 'performance_review',
    description: 'Review code for performance issues',
    agentType: 'task',
    expertise: 'code_review',
    temperature: 0.2,
    useValueNetwork: true,
    focus: ['performance'],
  },

  style_check: {
    name: 'style_check',
    description: 'Check code for style violations',
    agentType: 'task',
    expertise: 'code_review',
    temperature: 0.1,
    useValueNetwork: false,
    focus: ['style'],
  },

  // ============================================================================
  // DEBUGGING TASKS
  // ============================================================================

  debug_issue: {
    name: 'debug_issue',
    description: 'Debug and fix a reported issue',
    agentType: 'task',
    expertise: 'debugging',
    iterative: true,
    maxIterations: 5,
    checkpointFrequency: 5,
    useValueNetwork: true,
  },

  localize_bug: {
    name: 'localize_bug',
    description: 'Locate the source of a bug',
    agentType: 'task',
    expertise: 'debugging',
    temperature: 0.4,
    useValueNetwork: true,
  },

  generate_fix: {
    name: 'generate_fix',
    description: 'Generate a fix for a known bug',
    agentType: 'task',
    expertise: 'debugging',
    temperature: 0.3,
    checkpoints: 10,
    useValueNetwork: true,
  },

  validate_fix: {
    name: 'validate_fix',
    description: 'Validate that a fix resolves the issue',
    agentType: 'task',
    expertise: 'debugging',
    temperature: 0.1,
    useValueNetwork: false,
  },

  // ============================================================================
  // REFACTORING TASKS
  // ============================================================================

  refactor_file: {
    name: 'refactor_file',
    description: 'Refactor a single file',
    agentType: 'role',
    expertise: 'refactoring',
    multiFile: false,
    useValueNetwork: true,
  },

  refactor_project: {
    name: 'refactor_project',
    description: 'Refactor multiple files maintaining consistency',
    agentType: 'role',
    expertise: 'refactoring',
    multiFile: true,
    maxFiles: 50,
    chunkSize: 5,
    consistencyThreshold: 0.8,
    useValueNetwork: true,
  },

  extract_method: {
    name: 'extract_method',
    description: 'Extract a method from code',
    agentType: 'task',
    expertise: 'refactoring',
    temperature: 0.2,
    useValueNetwork: true,
  },

  rename_variable: {
    name: 'rename_variable',
    description: 'Rename variables to improve clarity',
    agentType: 'task',
    expertise: 'refactoring',
    temperature: 0.1,
    useValueNetwork: true,
  },

  simplify_code: {
    name: 'simplify_code',
    description: 'Simplify complex code structures',
    agentType: 'task',
    expertise: 'refactoring',
    temperature: 0.3,
    useValueNetwork: true,
  },

  remove_duplication: {
    name: 'remove_duplication',
    description: 'Remove duplicate code',
    agentType: 'task',
    expertise: 'refactoring',
    temperature: 0.2,
    useValueNetwork: true,
  },

  add_type_hints: {
    name: 'add_type_hints',
    description: 'Add type hints to improve code clarity',
    agentType: 'task',
    expertise: 'refactoring',
    temperature: 0.1,
    useValueNetwork: false,
  },

  // ============================================================================
  // WORKFLOW TASKS
  // ============================================================================

  implement_feature: {
    name: 'implement_feature',
    description: 'Implement a new feature from requirements',
    agentType: 'workflow',
    expertise: 'code_generation',
    workflow: [
      'generate_function',
      'generate_tests',
      'review_code',
      'refactor_file',
    ],
    useValueNetwork: true,
  },

  fix_bug: {
    name: 'fix_bug',
    description: 'Fix a bug from bug report',
    agentType: 'workflow',
    expertise: 'debugging',
    workflow: [
      'localize_bug',
      'generate_fix',
      'validate_fix',
      'generate_tests',
    ],
    useValueNetwork: true,
  },

  improve_code: {
    name: 'improve_code',
    description: 'Improve code quality through refactoring',
    agentType: 'workflow',
    expertise: 'refactoring',
    workflow: [
      'review_code',
      'refactor_file',
      'generate_tests',
      'review_code',
    ],
    useValueNetwork: true,
  },

  code_review_workflow: {
    name: 'code_review_workflow',
    description: 'Complete code review workflow',
    agentType: 'workflow',
    expertise: 'code_review',
    workflow: [
      'review_code',
      'detect_bugs',
      'security_review',
      'performance_review',
    ],
    useValueNetwork: true,
  },
};

export default CODING_TASKS;
