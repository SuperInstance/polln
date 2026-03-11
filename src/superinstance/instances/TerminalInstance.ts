/**
 * TerminalInstance - Implementation for command-line interface instances
 *
 * Represents terminal/shell interfaces that can execute commands,
 * manage processes, and handle standard I/O streams.
 */

import {
  BaseSuperInstance, InstanceType, InstanceState, InstanceCapability,
  CellPosition, InstanceConfiguration, InstancePermissions,
  InstanceMessage, InstanceMessageResponse, InstanceStatus, InstanceMetrics,
  Connection, ConnectionType, InstanceSnapshot, ValidationResult
} from '../types/base';

/**
 * ShellType - Types of shells/terminals
 */
export enum ShellType {
  BASH = 'bash',
  POWERSHELL = 'powershell',
  CMD = 'cmd',
  ZSH = 'zsh',
  FISH = 'fish',
  DOCKER = 'docker',
  SSH = 'ssh',
  CUSTOM = 'custom'
}

/**
 * TerminalMode - Terminal operation modes
 */
export enum TerminalMode {
  INTERACTIVE = 'interactive',  // Interactive shell
  BATCH = 'batch',              // Batch command execution
  SCRIPT = 'script',            // Script execution
  MONITOR = 'monitor'           // Process monitoring
}

/**
 * CommandResult - Result of command execution
 */
export interface CommandResult {
  exitCode: number;
  stdout: string;
  stderr: string;
  duration: number; // Execution time in milliseconds
  timestamp: number;
  command: string;
  pid?: number; // Process ID
}

/**
 * ProcessInfo - Information about a running process
 */
export interface ProcessInfo {
  pid: number;
  command: string;
  arguments: string[];
  workingDirectory: string;
  startTime: number;
  cpuUsage: number;
  memoryUsage: number;
  state: 'running' | 'stopped' | 'paused' | 'zombie';
  exitCode?: number;
}

/**
 * TerminalSession - Terminal session information
 */
export interface TerminalSession {
  id: string;
  shellType: ShellType;
  mode: TerminalMode;
  workingDirectory: string;
  environment: Record<string, string>;
  history: CommandHistoryEntry[];
  activeProcesses: ProcessInfo[];
  createdAt: number;
  lastActivity: number;
}

/**
 * CommandHistoryEntry - Entry in command history
 */
export interface CommandHistoryEntry {
  id: string;
  command: string;
  timestamp: number;
  result: CommandResult;
}

/**
 * TerminalConfig - Terminal configuration
 */
export interface TerminalConfig {
  shellType: ShellType;
  mode: TerminalMode;
  workingDirectory: string;
  environment: Record<string, string>;
  historySize: number; // Maximum history entries
  timeout: number; // Command timeout in milliseconds
  bufferSize: number; // Output buffer size in bytes
  autoComplete: boolean; // Enable auto-completion
  syntaxHighlighting: boolean; // Enable syntax highlighting
}

/**
 * StreamEvent - Event from terminal stream
 */
export interface StreamEvent {
  type: 'stdout' | 'stderr' | 'stdin' | 'exit' | 'error';
  data: string;
  timestamp: number;
  processId?: number;
}

/**
 * TerminalInstance - Interface for terminal instances
 */
export interface TerminalInstance {
  type: InstanceType.TERMINAL | InstanceType.SHELL | InstanceType.POWERSHELL | InstanceType.COMMAND_LINE;

  // Terminal-specific properties
  shellType: ShellType;
  terminalConfig: TerminalConfig;
  currentSession: TerminalSession;
  sessions: Map<string, TerminalSession>;

  // Command execution
  execute(command: string, args?: string[]): Promise<CommandResult>;
  executeScript(script: string, language?: string): Promise<CommandResult>;
  executeBatch(commands: string[]): Promise<CommandResult[]>;

  // Process management
  listProcesses(): Promise<ProcessInfo[]>;
  killProcess(pid: number, signal?: string): Promise<boolean>;
  pauseProcess(pid: number): Promise<boolean>;
  resumeProcess(pid: number): Promise<boolean>;

  // Session management
  createSession(config?: Partial<TerminalConfig>): Promise<string>;
  switchSession(sessionId: string): Promise<void>;
  closeSession(sessionId: string): Promise<void>;
  getSession(sessionId: string): TerminalSession | undefined;

  // Stream handling
  writeToStdin(data: string, processId?: number): Promise<void>;
  readStdout(processId?: number): Promise<string>;
  readStderr(processId?: number): Promise<string>;

  // History management
  getHistory(limit?: number): CommandHistoryEntry[];
  clearHistory(): void;
  searchHistory(query: string): CommandHistoryEntry[];

  // Monitoring
  getMetrics(): TerminalMetrics;
  getHealth(): { healthy: boolean; issues: string[] };
}

/**
 * TerminalMetrics - Terminal-specific metrics
 */
export interface TerminalMetrics {
  totalCommands: number;
  successfulCommands: number;
  failedCommands: number;
  averageExecutionTime: number;
  activeProcesses: number;
  totalSessions: number;
  memoryUsage: number;
  cpuUsage: number;
}

/**
 * ConcreteTerminalInstance - Implementation of TerminalInstance
 */
export class ConcreteTerminalInstance extends BaseSuperInstance implements TerminalInstance {
  type: InstanceType.TERMINAL | InstanceType.SHELL | InstanceType.POWERSHELL | InstanceType.COMMAND_LINE;
  shellType: ShellType;
  terminalConfig: TerminalConfig;
  currentSession: TerminalSession;
  sessions: Map<string, TerminalSession> = new Map();

  private connections: Map<string, Connection> = new Map();
  private children: SuperInstance[] = [];
  private parents: SuperInstance[] = [];
  private processes: Map<number, ProcessInfo> = new Map();
  private streamCallbacks: Map<string, (event: StreamEvent) => void> = new Map();
  private metrics: TerminalMetrics = {
    totalCommands: 0,
    successfulCommands: 0,
    failedCommands: 0,
    averageExecutionTime: 0,
    activeProcesses: 0,
    totalSessions: 0,
    memoryUsage: 0,
    cpuUsage: 0
  };
  private totalExecutionTime: number = 0;

  constructor(config: {
    id: string;
    name: string;
    description: string;
    cellPosition: CellPosition;
    spreadsheetId: string;
    shellType: ShellType;
    terminalConfig?: Partial<TerminalConfig>;
    configuration?: Partial<InstanceConfiguration>;
  }) {
    const instanceType = this.mapShellTypeToInstanceType(config.shellType);

    super({
      id: config.id,
      type: instanceType,
      name: config.name,
      description: config.description,
      cellPosition: config.cellPosition,
      spreadsheetId: config.spreadsheetId,
      configuration: config.configuration,
      capabilities: ['execute', 'computation', 'communication', 'network']
    });

    this.type = instanceType;
    this.shellType = config.shellType;
    this.terminalConfig = {
      shellType: config.shellType,
      mode: TerminalMode.INTERACTIVE,
      workingDirectory: process.cwd(),
      environment: { ...process.env },
      historySize: 1000,
      timeout: 30000,
      bufferSize: 1024 * 1024, // 1MB
      autoComplete: true,
      syntaxHighlighting: true,
      ...config.terminalConfig
    };

    // Create initial session
    this.currentSession = this.createSessionInternal('default');
    this.sessions.set(this.currentSession.id, this.currentSession);
    this.metrics.totalSessions = 1;
  }

  async initialize(config?: Partial<InstanceConfiguration>): Promise<void> {
    if (config) {
      this.configuration = { ...this.configuration, ...config };
    }

    const validation = this.validateConfiguration(this.configuration);
    if (!validation.valid) {
      throw new Error(`Configuration validation failed: ${validation.errors.map(e => e.message).join(', ')}`);
    }

    // Initialize terminal based on shell type
    await this.initializeTerminal();

    this.updateState(InstanceState.INITIALIZED);
  }

  async activate(): Promise<void> {
    if (this.state !== InstanceState.INITIALIZED && this.state !== InstanceState.IDLE) {
      throw new Error(`Cannot activate from state: ${this.state}`);
    }
    this.updateState(InstanceState.RUNNING);
  }

  async deactivate(): Promise<void> {
    if (this.state !== InstanceState.RUNNING && this.state !== InstanceState.PROCESSING) {
      throw new Error(`Cannot deactivate from state: ${this.state}`);
    }

    // Stop all processes
    await this.stopAllProcesses();

    this.updateState(InstanceState.IDLE);
  }

  async terminate(): Promise<void> {
    // Clean up connections
    this.connections.clear();
    this.children = [];
    this.parents = [];

    // Stop all processes
    await this.stopAllProcesses();

    // Clear sessions
    this.sessions.clear();
    this.processes.clear();
    this.streamCallbacks.clear();

    // Reset metrics
    this.metrics = {
      totalCommands: 0,
      successfulCommands: 0,
      failedCommands: 0,
      averageExecutionTime: 0,
      activeProcesses: 0,
      totalSessions: 0,
      memoryUsage: 0,
      cpuUsage: 0
    };
    this.totalExecutionTime = 0;

    this.updateState(InstanceState.TERMINATED);
  }

  async serialize(): Promise<InstanceSnapshot> {
    // Serialize sessions (excluding active processes)
    const sessionsData: Record<string, any> = {};
    for (const [id, session] of this.sessions) {
      sessionsData[id] = {
        ...session,
        activeProcesses: [] // Don't serialize active processes
      };
    }

    return {
      id: this.id,
      type: this.type,
      state: this.state,
      data: {
        shellType: this.shellType,
        terminalConfig: this.terminalConfig,
        currentSessionId: this.currentSession.id,
        sessions: sessionsData,
        metrics: this.metrics
      },
      configuration: this.configuration,
      timestamp: Date.now(),
      version: '1.0.0'
    };
  }

  async deserialize(snapshot: InstanceSnapshot): Promise<void> {
    if (![
      InstanceType.TERMINAL,
      InstanceType.SHELL,
      InstanceType.POWERSHELL,
      InstanceType.COMMAND_LINE
    ].includes(snapshot.type as any)) {
      throw new Error(`Cannot deserialize snapshot of type ${snapshot.type} into TerminalInstance`);
    }

    const data = snapshot.data;
    this.type = snapshot.type as any;
    this.shellType = data.shellType;
    this.terminalConfig = data.terminalConfig;
    this.metrics = data.metrics;

    // Restore sessions
    this.sessions.clear();
    for (const [id, sessionData] of Object.entries(data.sessions)) {
      this.sessions.set(id, sessionData as TerminalSession);
    }

    // Set current session
    if (data.currentSessionId && this.sessions.has(data.currentSessionId)) {
      this.currentSession = this.sessions.get(data.currentSessionId)!;
    } else if (this.sessions.size > 0) {
      this.currentSession = Array.from(this.sessions.values())[0];
    } else {
      this.currentSession = this.createSessionInternal('default');
      this.sessions.set(this.currentSession.id, this.currentSession);
    }

    this.configuration = snapshot.configuration;
    this.updateState(snapshot.state as InstanceState);
  }

  async sendMessage(message: InstanceMessage): Promise<InstanceMessageResponse> {
    try {
      await this.receiveMessage(message);
      return {
        messageId: message.id,
        status: 'success',
        payload: { received: true, timestamp: Date.now() }
      };
    } catch (error) {
      return {
        messageId: message.id,
        status: 'error',
        error: {
          code: 'MESSAGE_PROCESSING_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error',
          recoverable: true,
          context: { messageType: message.type }
        }
      };
    }
  }

  async receiveMessage(message: InstanceMessage): Promise<void> {
    switch (message.type) {
      case 'command':
        await this.handleCommandMessage(message);
        break;
      case 'data':
        await this.handleDataMessage(message);
        break;
      case 'query':
        await this.handleQueryMessage(message);
        break;
      default:
        console.warn(`Unhandled message type: ${message.type}`);
    }
  }

  async getStatus(): Promise<InstanceStatus> {
    const health = this.getHealth();
    return {
      state: this.state,
      health: health.healthy ? 'healthy' : 'unhealthy',
      uptime: Date.now() - this.createdAt,
      warnings: health.issues,
      lastError: undefined
    };
  }

  async getMetrics(): Promise<InstanceMetrics> {
    return {
      cpuUsage: this.metrics.cpuUsage,
      memoryUsage: this.metrics.memoryUsage,
      diskUsage: 0,
      networkIn: 0,
      networkOut: 0,
      requestCount: this.metrics.totalCommands,
      errorRate: this.metrics.failedCommands / Math.max(this.metrics.totalCommands, 1),
      latency: {
        p50: this.metrics.averageExecutionTime,
        p90: this.metrics.averageExecutionTime * 1.5,
        p95: this.metrics.averageExecutionTime * 2,
        p99: this.metrics.averageExecutionTime * 3,
        max: this.metrics.averageExecutionTime * 5
      }
    };
  }

  async getChildren(): Promise<SuperInstance[]> {
    return [...this.children];
  }

  async getParents(): Promise<SuperInstance[]> {
    return [...this.parents];
  }

  async getNeighbors(): Promise<SuperInstance[]> {
    // In a real implementation, this would query the spreadsheet for neighboring cells
    return [];
  }

  async connectTo(target: SuperInstance, connectionType: ConnectionType): Promise<Connection> {
    const connection: Connection = {
      id: `${this.id}-${target.id}-${Date.now()}`,
      source: this.id,
      target: target.id,
      type: connectionType,
      bandwidth: 1000, // 1 Gbps
      latency: 10, // 10ms
      reliability: 0.99,
      establishedAt: Date.now()
    };

    this.connections.set(connection.id, connection);
    return connection;
  }

  async disconnectFrom(target: SuperInstance): Promise<void> {
    for (const [id, connection] of this.connections) {
      if (connection.target === target.id) {
        this.connections.delete(id);
        break;
      }
    }
  }

  // TerminalInstance specific methods

  async execute(command: string, args?: string[]): Promise<CommandResult> {
    const startTime = Date.now();
    const fullCommand = args ? `${command} ${args.join(' ')}` : command;

    try {
      // Execute command based on shell type
      const result = await this.executeCommandInternal(fullCommand);

      // Update history
      this.addToHistory(fullCommand, result);

      // Update metrics
      this.updateMetrics(result, true);

      return result;
    } catch (error) {
      const errorResult: CommandResult = {
        exitCode: 1,
        stdout: '',
        stderr: error instanceof Error ? error.message : 'Unknown error',
        duration: Date.now() - startTime,
        timestamp: Date.now(),
        command: fullCommand
      };

      // Update history
      this.addToHistory(fullCommand, errorResult);

      // Update metrics
      this.updateMetrics(errorResult, false);

      throw error;
    }
  }

  async executeScript(script: string, language?: string): Promise<CommandResult> {
    const startTime = Date.now();

    try {
      // Determine script language
      const scriptLang = language || this.detectScriptLanguage(script);
      const tempFile = await this.createTempScript(script, scriptLang);

      // Execute script
      const command = this.getScriptCommand(scriptLang, tempFile);
      const result = await this.execute(command);

      // Clean up temp file
      await this.cleanupTempFile(tempFile);

      return result;
    } catch (error) {
      const errorResult: CommandResult = {
        exitCode: 1,
        stdout: '',
        stderr: error instanceof Error ? error.message : 'Unknown error',
        duration: Date.now() - startTime,
        timestamp: Date.now(),
        command: 'script'
      };

      this.updateMetrics(errorResult, false);
      throw error;
    }
  }

  async executeBatch(commands: string[]): Promise<CommandResult[]> {
    const results: CommandResult[] = [];

    for (const command of commands) {
      try {
        const result = await this.execute(command);
        results.push(result);
      } catch (error) {
        const errorResult: CommandResult = {
          exitCode: 1,
          stdout: '',
          stderr: error instanceof Error ? error.message : 'Unknown error',
          duration: 0,
          timestamp: Date.now(),
          command
        };
        results.push(errorResult);
      }
    }

    return results;
  }

  async listProcesses(): Promise<ProcessInfo[]> {
    return Array.from(this.processes.values());
  }

  async killProcess(pid: number, signal?: string): Promise<boolean> {
    const process = this.processes.get(pid);
    if (!process) {
      return false;
    }

    try {
      // In production, this would actually kill the process
      // For now, simulate it
      process.state = 'stopped';
      process.exitCode = 137; // SIGKILL exit code

      // Remove from active processes
      this.processes.delete(pid);

      // Update session
      this.currentSession.activeProcesses = this.currentSession.activeProcesses.filter(p => p.pid !== pid);

      // Update metrics
      this.metrics.activeProcesses = this.processes.size;

      // Emit exit event
      this.emitStreamEvent({
        type: 'exit',
        data: `Process ${pid} killed with signal ${signal || 'SIGKILL'}`,
        timestamp: Date.now(),
        processId: pid
      });

      return true;
    } catch (error) {
      console.error(`Failed to kill process ${pid}:`, error);
      return false;
    }
  }

  async pauseProcess(pid: number): Promise<boolean> {
    const process = this.processes.get(pid);
    if (!process || process.state !== 'running') {
      return false;
    }

    process.state = 'paused';
    return true;
  }

  async resumeProcess(pid: number): Promise<boolean> {
    const process = this.processes.get(pid);
    if (!process || process.state !== 'paused') {
      return false;
    }

    process.state = 'running';
    return true;
  }

  async createSession(config?: Partial<TerminalConfig>): Promise<string> {
    const sessionConfig = {
      ...this.terminalConfig,
      ...config
    };

    const session = this.createSessionInternal(`session-${Date.now()}`, sessionConfig);
    this.sessions.set(session.id, session);
    this.metrics.totalSessions = this.sessions.size;

    return session.id;
  }

  async switchSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    this.currentSession = session;
    this.currentSession.lastActivity = Date.now();
  }

  async closeSession(sessionId: string): Promise<void> {
    if (sessionId === this.currentSession.id) {
      throw new Error('Cannot close current session');
    }

    const session = this.sessions.get(sessionId);
    if (!session) {
      return;
    }

    // Kill all processes in session
    for (const process of session.activeProcesses) {
      await this.killProcess(process.pid);
    }

    // Remove session
    this.sessions.delete(sessionId);
    this.metrics.totalSessions = this.sessions.size;
  }

  getSession(sessionId: string): TerminalSession | undefined {
    return this.sessions.get(sessionId);
  }

  async writeToStdin(data: string, processId?: number): Promise<void> {
    if (processId) {
      const process = this.processes.get(processId);
      if (!process) {
        throw new Error(`Process ${processId} not found`);
      }

      // In production, this would write to the process stdin
      this.emitStreamEvent({
        type: 'stdin',
        data,
        timestamp: Date.now(),
        processId
      });
    } else {
      // Write to current session
      this.emitStreamEvent({
        type: 'stdin',
        data,
        timestamp: Date.now()
      });
    }
  }

  async readStdout(processId?: number): Promise<string> {
    // In production, this would read from process stdout
    // For now, return empty string
    return '';
  }

  async readStderr(processId?: number): Promise<string> {
    // In production, this would read from process stderr
    // For now, return empty string
    return '';
  }

  getHistory(limit?: number): CommandHistoryEntry[] {
    const history = this.currentSession.history;
    if (limit && limit > 0) {
      return history.slice(-limit);
    }
    return [...history];
  }

  clearHistory(): void {
    this.currentSession.history = [];
  }

  searchHistory(query: string): CommandHistoryEntry[] {
    const lowerQuery = query.toLowerCase();
    return this.currentSession.history.filter(entry =>
      entry.command.toLowerCase().includes(lowerQuery) ||
      entry.result.stdout.toLowerCase().includes(lowerQuery)
    );
  }

  getMetrics(): TerminalMetrics {
    return { ...this.metrics };
  }

  getHealth(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];

    // Check active processes
    if (this.metrics.activeProcesses > 100) {
      issues.push('Too many active processes');
    }

    // Check memory usage
    if (this.metrics.memoryUsage > 1024 * 1024 * 500) { // 500MB
      issues.push('High memory usage');
    }

    // Check CPU usage
    if (this.metrics.cpuUsage > 80) { // 80%
      issues.push('High CPU usage');
    }

    // Check error rate
    const errorRate = this.metrics.failedCommands / Math.max(this.metrics.totalCommands, 1);
    if (errorRate > 0.1) { // 10% error rate
      issues.push('High command failure rate');
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }

  // Private helper methods

  private mapShellTypeToInstanceType(shellType: ShellType): InstanceType {
    switch (shellType) {
      case ShellType.POWERSHELL:
        return InstanceType.POWERSHELL;
      case ShellType.BASH:
      case ShellType.ZSH:
      case ShellType.FISH:
        return InstanceType.SHELL;
      case ShellType.CMD:
        return InstanceType.COMMAND_LINE;
      default:
        return InstanceType.TERMINAL;
    }
  }

  private async initializeTerminal(): Promise<void> {
    // Initialize terminal based on shell type
    switch (this.shellType) {
      case ShellType.BASH:
      case ShellType.ZSH:
      case ShellType.FISH:
        // Unix-like shell initialization
        console.log(`Initializing ${this.shellType} terminal`);
        break;
      case ShellType.POWERSHELL:
        // PowerShell initialization
        console.log('Initializing PowerShell terminal');
        break;
      case ShellType.CMD:
        // CMD initialization
        console.log('Initializing CMD terminal');
        break;
      case ShellType.DOCKER:
        // Docker terminal initialization
        console.log('Initializing Docker terminal');
        break;
      case ShellType.SSH:
        // SSH terminal initialization
        console.log('Initializing SSH terminal');
        break;
    }
  }

  private async stopAllProcesses(): Promise<void> {
    const pids = Array.from(this.processes.keys());
    for (const pid of pids) {
      await this.killProcess(pid);
    }
  }

  private createSessionInternal(id: string, config?: TerminalConfig): TerminalSession {
    const sessionConfig = config || this.terminalConfig;

    return {
      id,
      shellType: sessionConfig.shellType,
      mode: sessionConfig.mode,
      workingDirectory: sessionConfig.workingDirectory,
      environment: { ...sessionConfig.environment },
      history: [],
      activeProcesses: [],
      createdAt: Date.now(),
      lastActivity: Date.now()
    };
  }

  private async executeCommandInternal(command: string): Promise<CommandResult> {
    const startTime = Date.now();

    // Simulate command execution
    // In production, this would use child_process or similar
    await new Promise(resolve => setTimeout(resolve, 100)); // Simulate execution time

    // Simulate different outcomes based on command
    let exitCode = 0;
    let stdout = '';
    let stderr = '';

    if (command.includes('error')) {
      exitCode = 1;
      stderr = 'Simulated error: Command failed';
    } else if (command.includes('sleep')) {
      stdout = 'Sleep command executed';
    } else {
      stdout = `Command executed successfully: ${command}`;
    }

    const duration = Date.now() - startTime;

    // Create process info if it's a long-running command
    if (command.includes('daemon') || command.includes('server')) {
      const pid = Date.now() % 10000;
      const processInfo: ProcessInfo = {
        pid,
        command: command.split(' ')[0],
        arguments: command.split(' ').slice(1),
        workingDirectory: this.currentSession.workingDirectory,
        startTime: Date.now(),
        cpuUsage: 0,
        memoryUsage: 0,
        state: 'running'
      };

      this.processes.set(pid, processInfo);
      this.currentSession.activeProcesses.push(processInfo);
      this.metrics.activeProcesses = this.processes.size;

      return {
        exitCode,
        stdout: `${stdout}\nProcess started with PID: ${pid}`,
        stderr,
        duration,
        timestamp: Date.now(),
        command,
        pid
      };
    }

    return {
      exitCode,
      stdout,
      stderr,
      duration,
      timestamp: Date.now(),
      command
    };
  }

  private detectScriptLanguage(script: string): string {
    // Simple language detection
    if (script.startsWith('#!/bin/bash') || script.includes('bash')) {
      return 'bash';
    } else if (script.startsWith('#!/usr/bin/env python') || script.includes('python')) {
      return 'python';
    } else if (script.startsWith('#!/usr/bin/env node') || script.includes('javascript')) {
      return 'javascript';
    } else if (script.startsWith('#!powershell') || script.includes('powershell')) {
      return 'powershell';
    } else {
      return 'bash'; // Default
    }
  }

  private async createTempScript(script: string, language: string): Promise<string> {
    // In production, create actual temp file
    // For now, return a simulated path
    const tempPath = `/tmp/script-${Date.now()}.${this.getScriptExtension(language)}`;
    console.log(`Created temp script at ${tempPath}`);
    return tempPath;
  }

  private getScriptExtension(language: string): string {
    switch (language.toLowerCase()) {
      case 'bash': return 'sh';
      case 'python': return 'py';
      case 'javascript': return 'js';
      case 'powershell': return 'ps1';
      default: return 'sh';
    }
  }

  private getScriptCommand(language: string, scriptPath: string): string {
    switch (language.toLowerCase()) {
      case 'bash': return `bash ${scriptPath}`;
      case 'python': return `python ${scriptPath}`;
      case 'javascript': return `node ${scriptPath}`;
      case 'powershell': return `powershell -File ${scriptPath}`;
      default: return `bash ${scriptPath}`;
    }
  }

  private async cleanupTempFile(path: string): Promise<void> {
    // In production, delete the temp file
    console.log(`Cleaned up temp file: ${path}`);
  }

  private addToHistory(command: string, result: CommandResult): void {
    const historyEntry: CommandHistoryEntry = {
      id: `cmd-${Date.now()}`,
      command,
      timestamp: Date.now(),
      result
    };

    this.currentSession.history.push(historyEntry);
    this.currentSession.lastActivity = Date.now();

    // Limit history size
    if (this.currentSession.history.length > this.terminalConfig.historySize) {
      this.currentSession.history = this.currentSession.history.slice(-this.terminalConfig.historySize);
    }
  }

  private updateMetrics(result: CommandResult, success: boolean): void {
    this.metrics.totalCommands++;
    this.totalExecutionTime += result.duration;

    if (success) {
      this.metrics.successfulCommands++;
    } else {
      this.metrics.failedCommands++;
    }

    this.metrics.averageExecutionTime = this.totalExecutionTime / this.metrics.totalCommands;

    // Update resource usage (simulated)
    this.metrics.memoryUsage = this.processes.size * 10; // 10MB per process
    this.metrics.cpuUsage = Math.min(this.processes.size * 5, 100); // 5% per process, max 100%
  }

  private emitStreamEvent(event: StreamEvent): void {
    // Call registered callbacks
    for (const callback of this.streamCallbacks.values()) {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in stream callback:', error);
      }
    }
  }

  private handleCommandMessage(message: InstanceMessage): void {
    const { payload } = message;

    if (payload && payload.command) {
      switch (payload.command) {
        case 'execute':
          if (payload.commandText) {
            this.execute(payload.commandText, payload.args);
          }
          break;
        case 'execute_script':
          if (payload.script) {
            this.executeScript(payload.script, payload.language);
          }
          break;
        case 'kill_process':
          if (payload.pid !== undefined) {
            this.killProcess(payload.pid, payload.signal);
          }
          break;
        case 'create_session':
          this.createSession(payload.config);
          break;
        case 'switch_session':
          if (payload.sessionId) {
            this.switchSession(payload.sessionId);
          }
          break;
      }
    }
  }

  private handleDataMessage(message: InstanceMessage): void {
    const { payload } = message;

    if (payload && payload.data && payload.type === 'stdin') {
      this.writeToStdin(payload.data, payload.processId);
    }
  }

  private handleQueryMessage(message: InstanceMessage): void {
    const { payload } = message;

    if (payload && payload.query) {
      switch (payload.query.type) {
        case 'history':
          const history = this.getHistory(payload.query.limit);
          // Send response back
          break;
        case 'processes':
          this.listProcesses();
          break;
        case 'sessions':
          // Return session list
          break;
      }
    }
  }
}