# POLLN Spreadsheet Integration - Technical Architecture

**Version:** 1.0
**Date:** 2026-03-08
**Status:** Design Document

---

## Executive Summary

This document defines the technical architecture for integrating POLLN (Pattern-Organized Large Language Network) with spreadsheet platforms (Excel, Google Sheets, Airtable). The integration enables spreadsheet users to create intelligent agent networks using familiar formula syntax like `=AGENT(...)` while leveraging POLLN's distributed intelligence capabilities.

**Key Innovation:** Transform spreadsheet cells into living agents that learn, communicate, and optimize through emergent behavior—making AI as accessible as `=SUM()`.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Integration Architecture](#2-integration-architecture)
3. [Platform-Specific Integration Points](#3-platform-specific-integration-points)
4. [Data Models](#4-data-models)
5. [Cell-to-Agent Binding](#5-cell-to-agent-binding)
6. [State Management & Persistence](#6-state-management--persistence)
7. [Communication Protocols](#7-communication-protocols)
8. [Performance Optimization](#8-performance-optimization)
9. [Security Model](#9-security-model)
10. [Deployment Models](#10-deployment-models)
11. [API Design](#11-api-design)
12. [MVP Roadmap](#12-mvp-roadmap)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Spreadsheet Platform                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │   A1    │  │   A2    │  │   B1    │  │   B2    │  Cells    │
│  │=AGENT()│  │=AGENT()│  │=AGENT()│  │=AGENT()│           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       │            │            │            │                   │
│  ┌────▼────────────▼────────────▼────────────▼────┐            │
│  │         Spreadsheet Integration Layer           │            │
│  │  • Custom Functions / Add-in Runtime           │            │
│  │  • POLLN Bridge (Platform-Specific)            │            │
│  │  • Event Handler & Dependency Tracker          │            │
│  └────────────────────┬───────────────────────────┘            │
└───────────────────────┼───────────────────────────────────────┘
                        │ WebSocket / HTTP
┌───────────────────────▼───────────────────────────────────────┐
│                    POLLN Runtime Server                       │
│  ┌────────────────────────────────────────────────────┐      │
│  │            Spreadsheet Colony Manager              │      │
│  │  • Cell-Agent Registry                            │      │
│  │  • Dependency Graph Manager                       │      │
│  │  • Evaluation Scheduler                           │      │
│  └────────────────┬───────────────────────────────────┘      │
│                   │                                           │
│  ┌────────────────▼───────────────────────────────────┐      │
│  │              POLLN Core System                     │      │
│  │  • Colony (Agent Network)                         │      │
│  │  • BaseAgent Implementations                      │      │
│  │  • PlinkoLayer (Decision Making)                  │      │
│  │  • A2A Communication System                       │      │
│  │  • Learning Systems (Hebbian, TD-λ, Dreaming)     │      │
│  └────────────────┬───────────────────────────────────┘      │
│                   │                                           │
│  ┌────────────────▼───────────────────────────────────┐      │
│  │              State Persistence                      │      │
│  │  • Spreadsheet Metadata Store                     │      │
│  │  • Agent State Database                          │      │
│  │  • Network Cache (Redis/LMCache)                  │      │
│  └────────────────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────────┐
│                    External Services                          │
│  • LLM APIs (OpenAI, Anthropic, etc.)                        │
│  • KV-Cache Backends (LMCache)                               │
│  • Federated Learning Services                               │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

1. **Non-Invasive Integration:** Works within existing spreadsheet constraints and APIs
2. **Lazy Evaluation:** Agents activate only when their cells require recalculation
3. **Dependency Awareness:** Respects spreadsheet dependency chains and circular reference rules
4. **State Isolation:** Agent state persists independently of spreadsheet session
5. **Platform Agnostic:** Core POLLN logic remains platform-independent
6. **Performance First:** Sub-second latency for typical agent operations
7. **Incremental Adoption:** Users can start with simple agents and scale to complex networks

---

## 2. Integration Architecture

### 2.1 Integration Pattern Comparison

| Aspect | Excel Add-in | Google Sheets Apps Script | Airtable Scripting |
|--------|--------------|--------------------------|-------------------|
| **Runtime** | JavaScript in browser/desktop | JavaScript on Google servers | JavaScript in browser |
| **Custom Functions** | Office.js API | `@customfunction` JSDoc | Script extensions |
| **Persistence** | Document-bound | Script-bound | Base-bound |
| **Networking** | Full fetch/XHR | UrlFetchService | fetch API |
| **State Storage** | Custom XML part | PropertiesService | base settings |
| **Real-time** | WebSocket possible | Limited | WebSocket possible |
| **Performance** | Best (desktop) | Good (server) | Variable (browser) |
| **Distribution** | AppSource / Sideloading | Marketplace / Script link | Marketplace |
| **Sandbox** | Strict (iframe) | Strict (V8 runtime) | Moderate (browser) |

### 2.2 Hybrid Architecture Strategy

Given platform constraints, we use a **three-tier architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Spreadsheet Client (Platform-Specific)              │
│ • Custom function wrapper                                   │
│ • Cell metadata storage                                     │
│ • Lightweight event handling                                │
│ • UI for agent inspection                                   │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS/WSS
┌────────────────▼────────────────────────────────────────────┐
│ Tier 2: POLLN Runtime Service (Platform-Agnostic)           │
│ • Agent lifecycle management                                │
│ • Colony coordination                                       │
│ • A2A message routing                                       │
│ • Learning optimization                                     │
└────────────────┬────────────────────────────────────────────┘
                 │ Persistence Layer
┌────────────────▼────────────────────────────────────────────┐
│ Tier 3: State & Model Storage                               │
│ • Agent configurations                                      │
│ • Learned weights & synapses                                │
│ • Execution history                                         │
│ • KV-cache anchors (LMCache)                                │
└─────────────────────────────────────────────────────────────┘
```

**Why Hybrid?**

1. **Browser constraints:** Spreadsheet runtimes have memory/CPU limits unsuitable for complex agent networks
2. **Persistence:** Agent state must survive spreadsheet sessions
3. **Collaboration:** Multiple users can share agents without conflicts
4. **Performance:** Heavy computation (LLM calls, learning) happens server-side
5. **Scalability:** Server can cache and optimize across many spreadsheets

---

## 3. Platform-Specific Integration Points

### 3.1 Excel (Office.js)

#### 3.1.1 Custom Function Implementation

```typescript
// functions.ts
/**
 * Creates or invokes a POLLN agent in this cell
 * @customfunction
 * @param {string} agentType Type of agent to create
 * @param {string|string[]} inputTopics Topics this agent responds to
 * @param {any[]} [args] Additional arguments for agent configuration
 * @returns {string} Agent ID or result
 * @customfunction
 */
function AGENT(agentType: string, inputTopics: string | string[], args?: any[]): string {
  // Delegate to POLLN runtime
  return POLLNBridge.invokeAgent(agentType, inputTopics, args);
}

/**
 * Creates a communication link between two agents
 * @customfunction
 * @param {string} fromAgent Source agent ID
 * @param {string} toAgent Target agent ID
 * @param {number} [weight=0.5] Initial synaptic weight
 * @returns {string} Connection ID
 * @customfunction
 */
function CONNECT(fromAgent: string, toAgent: string, weight?: number): string {
  return POLLNBridge.connectAgents(fromAgent, toAgent, weight);
}

/**
 * Triggers learning/reinforcement for an agent
 * @customfunction
 * @param {string} agentId Agent to reinforce
 * @param {number} reward Reward signal (-1 to 1)
 * @returns {boolean} Success status
 * @customfunction
 */
function REINFORCE(agentId: string, reward: number): boolean {
  return POLLNBridge.reinforceAgent(agentId, reward);
}
```

#### 3.1.2 POLLN Bridge for Excel

```typescript
// excel-bridge.ts
class ExcelPOLLNBridge {
  private runtimeUrl: string;
  private spreadsheetId: string;
  private cellAgentMap: Map<string, string>; // cell -> agentId

  constructor(runtimeUrl: string, spreadsheetId: string) {
    this.runtimeUrl = runtimeUrl;
    this.spreadsheetId = spreadsheetId;
    this.cellAgentMap = new Map();

    // Load existing mappings from document settings
    this.loadMappings();
  }

  async invokeAgent(
    agentType: string,
    inputTopics: string | string[],
    args?: any[]
  ): Promise<string> {
    const cellAddress = await this.getCurrentCell();

    // Check if agent already exists for this cell
    const existingAgentId = this.cellAgentMap.get(cellAddress);

    const payload = {
      spreadsheetId: this.spreadsheetId,
      cellAddress,
      agentType,
      inputTopics: Array.isArray(inputTopics) ? inputTopics : [inputTopics],
      args: args || [],
      existingAgentId: existingAgentId || undefined
    };

    // Call POLLN runtime
    const response = await fetch(`${this.runtimeUrl}/api/agent/invoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    // Store mapping if new agent
    if (result.agentId && !existingAgentId) {
      this.cellAgentMap.set(cellAddress, result.agentId);
      await this.saveMappings();
    }

    return result.value || result.agentId;
  }

  async connectAgents(
    fromAgent: string,
    toAgent: string,
    weight: number = 0.5
  ): Promise<string> {
    const response = await fetch(`${this.runtimeUrl}/api/agent/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spreadsheetId: this.spreadsheetId,
        fromAgent,
        toAgent,
        weight
      })
    });

    return (await response.json()).connectionId;
  }

  private async getCurrentCell(): Promise<string> {
    return new Promise((resolve) => {
      Excel.run(async (context) => {
        const range = context.workbook.getActiveCell();
        range.load("address");
        await context.sync();
        resolve(range.address);
      });
    });
  }

  private async loadMappings(): Promise<void> {
    // Load from CustomXmlPart or document settings
    Excel.run(async (context) => {
      const xmlParts = context.workbook.customXmlParts;
      const pollnPart = xmlParts.getItemOrNullObject("{POLLN-MAPPING-ID}");
      await context.sync();

      if (!pollnPart.isNull) {
        const xml = pollnPart.getXml();
        await context.sync();
        // Parse XML and populate cellAgentMap
      }
    });
  }

  private async saveMappings(): Promise<void> {
    // Save to CustomXmlPart
    Excel.run(async (context) => {
      const xmlParts = context.workbook.customXmlParts;
      const xml = this.serializeMappings();
      xmlParts.add(xml);
      await context.sync();
    });
  }

  private serializeMappings(): string {
    const obj = Object.fromEntries(this.cellAgentMap);
    return `<?xml version="1.0"?><polln><mappings>${JSON.stringify(obj)}</mappings></polln>`;
  }
}
```

#### 3.1.3 Task Pane for Agent Inspection

```typescript
// task-pane.ts
class AgentInspector {
  private runtimeUrl: string;
  private selectedAgentId: string | null = null;

  constructor(runtimeUrl: string) {
    this.runtimeUrl = runtimeUrl;
    this.setupUI();
  }

  async inspectAgent(agentId: string): Promise<void> {
    this.selectedAgentId = agentId;

    const response = await fetch(`${this.runtimeUrl}/api/agent/${agentId}`);
    const agent = await response.json();

    this.renderAgentDetails(agent);
  }

  private renderAgentDetails(agent: AgentState): void {
    const container = document.getElementById('agent-details');

    container.innerHTML = `
      <h3>Agent: ${agent.id}</h3>
      <div class="agent-stats">
        <div class="stat">
          <span class="label">Type:</span>
          <span class="value">${agent.typeId}</span>
        </div>
        <div class="stat">
          <span class="label">Status:</span>
          <span class="value ${agent.status}">${agent.status}</span>
        </div>
        <div class="stat">
          <span class="label">Success Rate:</span>
          <span class="value">${(agent.successRate * 100).toFixed(1)}%</span>
        </div>
        <div class="stat">
          <span class="label">Value Function:</span>
          <span class="value">${agent.valueFunction.toFixed(3)}</span>
        </div>
        <div class="stat">
          <span class="label">Executions:</span>
          <span class="value">${agent.executionCount}</span>
        </div>
      </div>

      <div class="agent-connections">
        <h4>Connections</h4>
        <button id="view-connections">View Network</button>
      </div>

      <div class="agent-history">
        <h4>Recent Activity</h4>
        <div id="activity-log"></div>
      </div>
    `;

    this.loadActivityLog(agent.id);
  }
}
```

### 3.2 Google Sheets (Apps Script)

#### 3.2.1 Custom Functions

```javascript
// Code.gs
/**
 * Creates or invokes a POLLN agent
 * @param {string} agentType Type of agent
 * @param {string} inputTopics Comma-separated topics
 * @return {string} Agent ID or result
 * @customfunction
 */
function AGENT(agentType, inputTopics) {
  const bridge = new SheetsPOLLNBridge();
  return bridge.invokeAgent(agentType, inputTopics);
}

/**
 * Connects two agents with a synaptic link
 * @param {string} fromAgent Source agent ID
 * @param {string} toAgent Target agent ID
 * @param {number} weight Synaptic weight (0-1)
 * @return {string} Connection ID
 * @customfunction
 */
function CONNECT(fromAgent, toAgent, weight) {
  const bridge = new SheetsPOLLNBridge();
  return bridge.connectAgents(fromAgent, toAgent, weight);
}

/**
 * Reinforces an agent with reward signal
 * @param {string} agentId Agent to reinforce
 * @param {number} reward Reward value (-1 to 1)
 * @return {boolean} Success
 * @customfunction
 */
function REINFORCE(agentId, reward) {
  const bridge = new SheetsPOLLNBridge();
  return bridge.reinforceAgent(agentId, reward);
}

/**
 * Shows agent inspector sidebar
 * @param {string} agentId Agent to inspect
 * @return {string} Confirmation message
 * @customfunction
 */
function INSPECT(agentId) {
  const bridge = new SheetsPOLLNBridge();
  bridge.showInspector(agentId);
  return "Opening inspector...";
}
```

#### 3.2.2 POLLN Bridge for Sheets

```javascript
// sheets-bridge.js
class SheetsPOLLNBridge {
  constructor() {
    this.runtimeUrl = this.getRuntimeUrl();
    this.spreadsheetId = SpreadsheetApp.getActiveSpreadsheet().getId();
    this.properties = PropertiesService.getDocumentProperties();
    this.cache = CacheService.getDocumentCache();
  }

  invokeAgent(agentType, inputTopics) {
    const cell = this.getCurrentCell();
    const cacheKey = `agent_${cell}`;

    // Check cache for existing agent
    let agentId = this.cache.get(cacheKey);

    const payload = {
      spreadsheetId: this.spreadsheetId,
      cellAddress: cell,
      agentType: agentType,
      inputTopics: inputTopics.split(',').map(t => t.trim()),
      existingAgentId: agentId || undefined
    };

    try {
      const response = UrlFetchApp.fetch(`${this.runtimeUrl}/api/agent/invoke`, {
        method: 'POST',
        contentType: 'application/json',
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });

      const result = JSON.parse(response.getContentText());

      // Cache the agent ID
      if (result.agentId) {
        this.cache.put(cacheKey, result.agentId, 21600); // 6 hours
      }

      return result.value || result.agentId;

    } catch (e) {
      return `#ERROR: ${e.message}`;
    }
  }

  connectAgents(fromAgent, toAgent, weight) {
    const payload = {
      spreadsheetId: this.spreadsheetId,
      fromAgent: fromAgent,
      toAgent: toAgent,
      weight: weight || 0.5
    };

    const response = UrlFetchApp.fetch(`${this.runtimeUrl}/api/agent/connect`, {
      method: 'POST',
      contentType: 'application/json',
      payload: JSON.stringify(payload)
    });

    const result = JSON.parse(response.getContentText());
    return result.connectionId;
  }

  reinforceAgent(agentId, reward) {
    const payload = {
      spreadsheetId: this.spreadsheetId,
      agentId: agentId,
      reward: reward
    };

    const response = UrlFetchApp.fetch(`${this.runtimeUrl}/api/agent/reinforce`, {
      method: 'POST',
      contentType: 'application/json',
      payload: JSON.stringify(payload)
    });

    const result = JSON.parse(response.getContentText());
    return result.success;
  }

  showInspector(agentId) {
    const html = HtmlService.createHtmlOutput(`
      <script>
        const agentId = "${agentId}";
        const runtimeUrl = "${this.runtimeUrl}";

        async function loadAgent() {
          const response = await fetch(`${runtimeUrl}/api/agent/\${agentId}`);
          const agent = await response.json();

          document.getElementById('agent-info').innerHTML = `
            <h3>Agent: \${agent.id}</h3>
            <p>Type: \${agent.typeId}</p>
            <p>Status: \${agent.status}</p>
            <p>Success Rate: \${(agent.successRate * 100).toFixed(1)}%</p>
            <p>Value: \${agent.valueFunction.toFixed(3)}</p>
          `;
        }

        loadAgent();
      </script>
      <div id="agent-info">Loading...</div>
    `)
      .setTitle('Agent Inspector')
      .setWidth(300);

    SpreadsheetApp.getUi().showSidebar(html);
  }

  getCurrentCell() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const cell = sheet.getActiveCell();
    return `${sheet.getSheetName()}!${cell.getA1Notation()}`;
  }

  getRuntimeUrl() {
    // Store runtime URL in script properties
    const props = PropertiesService.getScriptProperties();
    return props.getProperty('POLLN_RUNTIME_URL') || 'http://localhost:3000';
  }
}
```

#### 3.2.3 Menu Installation

```javascript
// Create menu when spreadsheet opens
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('POLLN')
    .addItem('Configure Runtime', 'showConfigDialog')
    .addItem('View Colony Status', 'showColonyStatus')
    .addItem('Inspect Agent', 'showInspectorDialog')
    .addSeparator()
    .addItem('Help', 'showHelp')
    .addToUi();
}

function showConfigDialog() {
  const html = HtmlService.createHtmlOutput(`
    <h3>POLLN Configuration</h3>
    <label>Runtime URL:</label>
    <input type="text" id="runtimeUrl" placeholder="http://localhost:3000" />
    <button onclick="saveConfig()">Save</button>
    <script>
      function saveConfig() {
        const url = document.getElementById('runtimeUrl').value;
        google.script.run.saveRuntimeUrl(url);
        google.script.host.close();
      }
    </script>
  `);

  SpreadsheetApp.getUi().showModalDialog(html, 'Configure POLLN');
}

function saveRuntimeUrl(url) {
  PropertiesService.getScriptProperties().setProperty('POLLN_RUNTIME_URL', url);
}
```

### 3.3 Airtable (Scripting)

#### 3.3.1 Script Extension

```javascript
// Airtable Script Extension
const POLLN_RUNTIME_URL = 'https://api.polln.io';

// Main function exposed to UI
async function createAgentField() {
    const table = base.getTable(cursor.activeTableId);
    const view = table.getView(cursor.viewId);

    // Let user select field to attach agent to
    const field = await input.fieldAsync('Select field to attach agent', table);

    // Get agent configuration
    const config = await input.tableAsync(
        'Enter agent configuration',
        {
            agentType: { type: FieldType.SingleLineText },
            inputTopics: { type: FieldType.MultipleCollaborators },
            initialState: { type: FieldType.SingleLineText }
        }
    );

    // Create formula field that invokes agent
    await table.createFieldAsync({
        name: `${field.name}_AGENT`,
        type: FieldType.Formula,
        formula: `AGENT('${config.agentType}', '${config.inputTopics}', {field: '${field.name}'})`
    });

    alert(`Agent field created for ${field.name}`);
}

// Custom function (via automation)
async function AGENT(agentType, inputTopics, options) {
    const recordId = options?.recordId;
    const tableId = options?.tableId;

    const payload = {
        baseId: base.id,
        tableId: tableId,
        recordId: recordId,
        agentType: agentType,
        inputTopics: inputTopics.split(','),
        context: options
    };

    const response = await remoteFetchAsync(`${POLLN_RUNTIME_URL}/api/agent/invoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const result = await response.json();
    return result.value || result.agentId;
}
```

---

## 4. Data Models

### 4.1 Cell-Agent Binding Model

```typescript
/**
 * Represents the binding between a spreadsheet cell and an agent
 */
interface CellAgentBinding {
  // Identification
  id: string;                      // Unique binding ID
  spreadsheetId: string;           // Platform's spreadsheet identifier
  cellAddress: string;             // Platform-specific cell reference
  agentId: string;                 // POLLN agent ID

  // Binding configuration
  agentType: string;               // Type of agent to create/use
  inputTopics: string[];           // Topics this agent responds to
  outputTopic: string;             // Topic this agent publishes to

  // Cell references
  dependencies: CellReference[];   // Cells this agent reads from
  dependents: CellReference[];     // Cells that read this agent's output

  // Configuration
  config: AgentCellConfig;         // Cell-specific configuration

  // State tracking
  createdAt: number;
  lastActivated: number;
  activationCount: number;

  // Lifecycle
  status: 'active' | 'inactive' | 'error' | 'orphaned';
}

/**
 * Configuration for an agent in a cell
 */
interface AgentCellConfig {
  // Lifecycle
  persistent: boolean;             // Keep agent active between recalculation
  lazy: boolean;                   // Only activate when explicitly called

  // Learning
  learningEnabled: boolean;        // Allow agent to learn from cell interactions
  reinforcement: {
    enabled: boolean;
    autoReinforce: boolean;        // Auto-reinforce based on cell edits
    rewardSignal?: string;         // Formula for calculating reward
  };

  // LLM integration
  llmConfig?: {
    provider: string;
    model: string;
    maxTokens?: number;
    temperature?: number;
  };

  // Output formatting
  outputFormat: 'raw' | 'json' | 'table' | 'chart';

  // Error handling
  onError: 'error' | 'fallback' | 'retry';
  fallbackValue?: any;

  // Performance
  timeoutMs: number;
  cacheEnabled: boolean;
  cacheTTLSec: number;
}

/**
 * Reference to another cell
 */
interface CellReference {
  sheet: string;
  cell: string;
  agentId?: string;                // If cell contains an agent
  referenceType: 'read' | 'write';
}
```

### 4.2 Spreadsheet Colony Model

```typescript
/**
 * A colony representing all agents in a spreadsheet
 */
interface SpreadsheetColony {
  // Identification
  id: string;                      // Colony ID = spreadsheet ID
  spreadsheetId: string;
  platform: 'excel' | 'sheets' | 'airtable';

  // Colony configuration
  config: ColonyConfig;

  // Agent registry
  agents: Map<string, SpreadsheetAgent>;  // agentId -> agent
  bindings: Map<string, CellAgentBinding>; // cell -> binding

  // Dependency graph
  dependencyGraph: DependencyGraph;

  // Colony state
  state: ColonyState;

  // Statistics
  stats: ColonyStats;
}

/**
 * An agent that exists in a spreadsheet context
 */
interface SpreadsheetAgent extends AgentState {
  // Spreadsheet context
  spreadsheetId: string;
  cellAddress: string;

  // Cell-specific overrides
  cellConfig: AgentCellConfig;

  // Network connections
  connections: AgentConnection[];

  // Learning data
  learningHistory: LearningEvent[];

  // Performance tracking
  cellStats: {
    avgRecalcTime: number;
    recalcCount: number;
    errorCount: number;
    lastRecalc: number;
  };
}

/**
 * Connection between two spreadsheet agents
 */
interface AgentConnection {
  id: string;
  fromAgentId: string;
  toAgentId: string;

  // Synaptic properties
  weight: number;
  learningRate: number;

  // Connection metadata
  viaCell?: string;                // If connection is mediated by a cell
  formula?: string;                // CONNECT formula that created this

  // Statistics
  activationCount: number;
  lastActivated: number;
}

/**
 * Dependency graph for tracking cell relationships
 */
interface DependencyGraph {
  nodes: Map<string, DependencyNode>;
  edges: DependencyEdge[];

  // Graph metrics
  cycles: string[][];              // Detected circular dependencies
  levels: Map<string, number>;     // Topological levels for evaluation order
}

interface DependencyNode {
  id: string;                      // Cell address
  agentId?: string;
  hasAgent: boolean;

  // Dependencies
  dependsOn: string[];             // Cells this node reads from
  dependedOnBy: string[];          // Cells that read this node

  // Evaluation
  evaluationOrder: number;
  isCircular: boolean;
}

interface DependencyEdge {
  from: string;                    // From cell
  to: string;                      // To cell
  type: 'data' | 'agent';
  indirect: boolean;
}
```

### 4.3 State Storage Model

```typescript
/**
 * Complete state for a spreadsheet's POLLN integration
 */
interface SpreadsheetState {
  // Versioning
  version: number;
  lastModified: number;

  // Colony
  colony: SpreadsheetColony;

  // Mappings
  cellMappings: Record<string, string>;  // cell -> agentId

  // Cache
  agentCache: Record<string, CachedAgentResult>;

  // Metadata
  metadata: {
    spreadsheetName: string;
    platformVersion: string;
    pollnVersion: string;
    author: string;
    description?: string;
  };
}

/**
 * Cached agent result for performance
 */
interface CachedAgentResult {
  value: any;
  timestamp: number;
  hash: string;                    // Hash of inputs
  expiresAt: number;
}
```

---

## 5. Cell-to-Agent Binding

### 5.1 Binding Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Binding Lifecycle                         │
└─────────────────────────────────────────────────────────────┘

User enters: =AGENT("analyzer", "sales")
                    │
                    ▼
        ┌───────────────────────┐
        │  1. Parse Formula     │
        │  - Extract agentType  │
        │  - Extract inputTopics│
        │  - Extract args       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  2. Check Binding     │
        │  - Does cell have     │
        │    existing agent?    │
        └───────────┬───────────┘
                    │
           ┌────────┴────────┐
           │                 │
        Yes│                 │No
           │                 │
           ▼                 ▼
    ┌───────────┐    ┌──────────────────┐
    │ Load      │    │ Create New Agent │
    │ Existing  │    │ - Generate ID    │
    │ Agent     │    │ - Initialize     │
    └─────┬─────┘    │ - Register       │
          │          └────────┬─────────┘
          │                   │
          └────────┬──────────┘
                   │
                   ▼
        ┌───────────────────────┐
        │  3. Resolve Inputs    │
        │  - Read referenced    │
        │    cells              │
        │  - Build context      │
        └───────────┬───────────┘
                   │
                   ▼
        ┌───────────────────────┐
        │  4. Invoke Agent      │
        │  - Send to runtime    │
        │  - Execute            │
        └───────────┬───────────┘
                   │
                   ▼
        ┌───────────────────────┐
        │  5. Cache Result      │
        │  - Store in cell      │
        │    metadata           │
        │  - Update binding     │
        └───────────┬───────────┘
                   │
                   ▼
        ┌───────────────────────┐
        │  6. Return Value      │
        │  - Display in cell    │
        └───────────────────────┘
```

### 5.2 Binding Resolution

```typescript
/**
 * Resolves and creates cell-agent bindings
 */
class BindingResolver {
  private colony: SpreadsheetColony;
  private runtime: POLLNRuntime;

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
  }

  /**
   * Resolves a cell to an agent, creating if necessary
   */
  async resolveCell(
    cellAddress: string,
    agentType: string,
    inputTopics: string[],
    args?: any[]
  ): Promise<string> {
    // Check for existing binding
    const existingBinding = this.colony.bindings.get(cellAddress);

    if (existingBinding) {
      // Validate binding matches
      if (existingBinding.agentType === agentType) {
        return this.invokeExisting(existingBinding, args);
      } else {
        // Agent type changed, deprecate old binding
        await this.deprecateBinding(existingBinding);
      }
    }

    // Create new binding
    const binding = await this.createBinding(
      cellAddress,
      agentType,
      inputTopics,
      args
    );

    // Register binding
    this.colony.bindings.set(cellAddress, binding);

    // Invoke agent
    return await this.invokeAgent(binding, args);
  }

  /**
   * Creates a new cell-agent binding
   */
  private async createBinding(
    cellAddress: string,
    agentType: string,
    inputTopics: string[],
    args?: any[]
  ): Promise<CellAgentBinding> {
    // Create agent via runtime
    const agent = await this.runtime.createAgent({
      type: agentType,
      inputTopics: inputTopics,
      outputTopic: this.generateOutputTopic(cellAddress),
      config: this.extractConfig(args)
    });

    // Create binding
    const binding: CellAgentBinding = {
      id: this.generateBindingId(),
      spreadsheetId: this.colony.spreadsheetId,
      cellAddress: cellAddress,
      agentId: agent.id,
      agentType: agentType,
      inputTopics: inputTopics,
      outputTopic: agent.config.outputTopic,
      dependencies: await this.resolveDependencies(cellAddress),
      dependents: [],
      config: this.extractConfig(args),
      createdAt: Date.now(),
      lastActivated: Date.now(),
      activationCount: 0,
      status: 'active'
    };

    // Update dependency graph
    this.updateDependencyGraph(binding);

    return binding;
  }

  /**
   * Invokes an existing binding
   */
  private async invokeExisting(
    binding: CellAgentBinding,
    args?: any[]
  ): Promise<string> {
    // Check if binding is still valid
    if (binding.status !== 'active') {
      throw new Error(`Binding ${binding.id} is not active`);
    }

    return await this.invokeAgent(binding, args);
  }

  /**
   * Invokes the agent for a binding
   */
  private async invokeAgent(
    binding: CellAgentBinding,
    args?: any[]
  ): Promise<string> {
    // Resolve input values from dependencies
    const inputs = await this.resolveInputs(binding);

    // Invoke agent via runtime
    const result = await this.runtime.invokeAgent({
      agentId: binding.agentId,
      inputs: inputs,
      context: {
        cellAddress: binding.cellAddress,
        spreadsheetId: binding.spreadsheetId,
        args: args || []
      }
    });

    // Update binding stats
    binding.lastActivated = Date.now();
    binding.activationCount++;

    // Cache result
    await this.cacheResult(binding, result);

    return result.value;
  }

  /**
   * Resolves input values from cell dependencies
   */
  private async resolveInputs(binding: CellAgentBinding): Promise<Record<string, any>> {
    const inputs: Record<string, any> = {};

    for (const dep of binding.dependencies) {
      if (dep.agentId) {
        // Dependency is an agent cell
        const depBinding = this.colony.bindings.get(dep.referenceType);
        if (depBinding) {
          inputs[dep.sheet + '!' + dep.cell] = await this.getCachedResult(depBinding);
        }
      } else {
        // Dependency is a regular cell
        inputs[dep.sheet + '!' + dep.cell] = await this.readCellValue(dep);
      }
    }

    return inputs;
  }

  /**
   * Updates the dependency graph with a new binding
   */
  private updateDependencyGraph(binding: CellAgentBinding): void {
    const graph = this.colony.dependencyGraph;

    // Create node for this cell
    const node: DependencyNode = {
      id: binding.cellAddress,
      agentId: binding.agentId,
      hasAgent: true,
      dependsOn: binding.dependencies.map(d => d.sheet + '!' + d.cell),
      dependedOnBy: [],
      evaluationOrder: 0,
      isCircular: false
    };

    graph.nodes.set(binding.cellAddress, node);

    // Update edges
    for (const dep of binding.dependencies) {
      const depId = dep.sheet + '!' + dep.cell;

      graph.edges.push({
        from: depId,
        to: binding.cellAddress,
        type: 'agent',
        indirect: false
      });

      // Update dependent's list
      const depNode = graph.nodes.get(depId);
      if (depNode) {
        depNode.dependedOnBy.push(binding.cellAddress);
      }
    }

    // Detect cycles
    this.detectCycles();

    // Calculate evaluation order
    this.calculateEvaluationOrder();
  }

  /**
   * Detects circular dependencies
   */
  private detectCycles(): void {
    const graph = this.colony.dependencyGraph;
    const visited = new Set<string>();
    const recStack = new Set<string>();
    const cycles: string[][] = [];

    const dfs = (nodeId: string, path: string[]): void => {
      visited.add(nodeId);
      recStack.add(nodeId);
      path.push(nodeId);

      const node = graph.nodes.get(nodeId);
      if (node) {
        for (const depId of node.dependsOn) {
          if (!visited.has(depId)) {
            dfs(depId, [...path]);
          } else if (recStack.has(depId)) {
            // Found a cycle
            const cycleStart = path.indexOf(depId);
            cycles.push(path.slice(cycleStart));
          }
        }
      }

      recStack.delete(nodeId);
    };

    for (const nodeId of graph.nodes.keys()) {
      if (!visited.has(nodeId)) {
        dfs(nodeId, []);
      }
    }

    graph.cycles = cycles;

    // Mark circular nodes
    for (const cycle of cycles) {
      for (const nodeId of cycle) {
        const node = graph.nodes.get(nodeId);
        if (node) {
          node.isCircular = true;
        }
      }
    }
  }

  /**
   * Calculates topological evaluation order
   */
  private calculateEvaluationOrder(): void {
    const graph = this.colony.dependencyGraph;
    const inDegree = new Map<string, number>();
    const order: string[] = [];

    // Calculate in-degrees
    for (const nodeId of graph.nodes.keys()) {
      inDegree.set(nodeId, 0);
    }

    for (const edge of graph.edges) {
      inDegree.set(edge.to, (inDegree.get(edge.to) || 0) + 1);
    }

    // Kahn's algorithm
    const queue: string[] = [];
    for (const [nodeId, degree] of inDegree) {
      if (degree === 0) {
        queue.push(nodeId);
      }
    }

    while (queue.length > 0) {
      const nodeId = queue.shift()!;
      order.push(nodeId);

      const node = graph.nodes.get(nodeId);
      if (node) {
        for (const depId of node.dependedOnBy) {
          inDegree.set(depId, inDegree.get(depId)! - 1);
          if (inDegree.get(depId) === 0) {
            queue.push(depId);
          }
        }
      }
    }

    // Assign order numbers
    order.forEach((nodeId, index) => {
      const node = graph.nodes.get(nodeId);
      if (node) {
        node.evaluationOrder = index;
      }
    });
  }

  private generateBindingId(): string {
    return `binding_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateOutputTopic(cellAddress: string): string {
    return `cell:${cellAddress}`;
  }

  private extractConfig(args?: any[]): AgentCellConfig {
    // Extract configuration from function arguments
    return {
      persistent: true,
      lazy: false,
      learningEnabled: true,
      reinforcement: {
        enabled: true,
        autoReinforce: false
      },
      outputFormat: 'raw',
      onError: 'error',
      timeoutMs: 5000,
      cacheEnabled: true,
      cacheTTLSec: 300
    };
  }

  private async resolveDependencies(cellAddress: string): Promise<CellReference[]> {
    // Parse formula to find referenced cells
    // This is platform-specific
    return [];
  }

  private async deprecateBinding(binding: CellAgentBinding): Promise<void> {
    binding.status = 'inactive';
    // Optionally shutdown agent
  }

  private async getCachedResult(binding: CellAgentBinding): Promise<any> {
    // Return cached result for this binding
    return null;
  }

  private async readCellValue(ref: CellReference): Promise<any> {
    // Read value from referenced cell
    return null;
  }

  private async cacheResult(binding: CellAgentBinding, result: any): Promise<void> {
    // Cache the result
  }
}
```

### 5.3 Dependency Propagation

```typescript
/**
 * Manages dependency propagation in agent networks
 */
class DependencyPropagator {
  private colony: SpreadsheetColony;
  private runtime: POLLNRuntime;

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
  }

  /**
   * Propagates changes through the dependency graph
   */
  async propagateChange(changedCell: string): Promise<string[]> {
    const graph = this.colony.dependencyGraph;
    const node = graph.nodes.get(changedCell);

    if (!node) {
      return [];
    }

    // Find all affected cells (transitive dependents)
    const affected = this.findAffectedCells(changedCell);

    // Invalidate cache for affected cells
    for (const cellId of affected) {
      await this.invalidateCache(cellId);
    }

    // Trigger recalculation for affected agents
    const recalculated: string[] = [];
    for (const cellId of affected) {
      const binding = this.colony.bindings.get(cellId);
      if (binding && binding.status === 'active') {
        await this.recalculateAgent(binding);
        recalculated.push(cellId);
      }
    }

    return recalculated;
  }

  /**
   * Finds all cells affected by a change (transitive closure)
   */
  private findAffectedCells(startCell: string): string[] {
    const affected: string[] = [];
    const visited = new Set<string>();
    const queue: string[] = [startCell];

    while (queue.length > 0) {
      const cellId = queue.shift()!;

      if (visited.has(cellId)) {
        continue;
      }

      visited.add(cellId);

      const node = this.colony.dependencyGraph.nodes.get(cellId);
      if (node) {
        for (const depId of node.dependedOnBy) {
          if (!visited.has(depId)) {
            queue.push(depId);
            affected.push(depId);
          }
        }
      }
    }

    return affected;
  }

  /**
   * Invalidates cached result for a cell
   */
  private async invalidateCache(cellId: string): Promise<void> {
    // Remove from cache
    const binding = this.colony.bindings.get(cellId);
    if (binding) {
      // Clear cache entry
    }
  }

  /**
   * Recalculates an agent
   */
  private async recalculateAgent(binding: CellAgentBinding): Promise<void> {
    // Trigger agent recalculation
    await this.runtime.invokeAgent({
      agentId: binding.agentId,
      inputs: {},
      context: {
        cellAddress: binding.cellAddress,
        spreadsheetId: binding.spreadsheetId,
        recalculate: true
      }
    });
  }
}
```

---

## 6. State Management & Persistence

### 6.1 Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layers                             │
└─────────────────────────────────────────────────────────────┘

Layer 1: Spreadsheet (Platform Storage)
├─ Excel: CustomXmlPart
├─ Sheets: PropertiesService
└─ Airtable: Base settings
  Purpose: Cell-agent mappings, quick lookup

Layer 2: POLLN Runtime (Server Storage)
├─ Redis/PostgreSQL: Active agent states
├─ LMCache: KV-cache anchors
└─ File System: Persistent agent configurations
  Purpose: Runtime state, learning data

Layer 3: External Services
├─ Federated Learning: Model updates
├─ Meadow: Community patterns
└─ KV-Cache Backends: Distributed cache
  Purpose: Cross-spreadsheet optimization
```

### 6.2 State Synchronization

```typescript
/**
 * Manages state synchronization between spreadsheet and runtime
 */
class StateManager {
  private spreadsheetId: string;
  private platform: SpreadsheetPlatform;
  private runtime: POLLNRuntime;
  private syncInterval: number = 60000; // 1 minute

  constructor(
    spreadsheetId: string,
    platform: SpreadsheetPlatform,
    runtime: POLLNRuntime
  ) {
    this.spreadsheetId = spreadsheetId;
    this.platform = platform;
    this.runtime = runtime;
  }

  /**
   * Loads complete state for a spreadsheet
   */
  async loadState(): Promise<SpreadsheetState> {
    // Try loading from platform storage first
    const platformState = await this.loadFromPlatform();

    if (platformState) {
      // Validate and merge with runtime state
      return await this.mergeWithRuntime(platformState);
    }

    // No existing state, create new
    return await this.initializeState();
  }

  /**
   * Saves state to platform storage
   */
  async saveState(state: SpreadsheetState): Promise<void> {
    const serialized = this.serializeState(state);
    await this.platform.storeMetadata(this.spreadsheetId, serialized);
  }

  /**
   * Syncs state with runtime
   */
  async syncWithRuntime(): Promise<void> {
    const state = await this.loadState();

    // Send to runtime for validation/merge
    const runtimeState = await this.runtime.syncSpreadsheetState(state);

    // Update local state
    await this.mergeState(runtimeState);

    // Save to platform
    await this.saveState(runtimeState);
  }

  /**
   * Loads state from platform storage
   */
  private async loadFromPlatform(): Promise<SpreadsheetState | null> {
    const data = await this.platform.loadMetadata(this.spreadsheetId);

    if (!data) {
      return null;
    }

    return this.deserializeState(data);
  }

  /**
   * Initializes new state for a spreadsheet
   */
  private async initializeState(): Promise<SpreadsheetState> {
    return {
      version: 1,
      lastModified: Date.now(),
      colony: {
        id: this.spreadsheetId,
        spreadsheetId: this.spreadsheetId,
        platform: this.platform.type,
        config: await this.getDefaultColonyConfig(),
        agents: new Map(),
        bindings: new Map(),
        dependencyGraph: {
          nodes: new Map(),
          edges: [],
          cycles: [],
          levels: new Map()
        },
        state: 'initialized',
        stats: {
          totalAgents: 0,
          activeAgents: 0,
          shannonDiversity: 0,
          avgValueFunction: 0,
          totalExecutions: 0
        }
      },
      cellMappings: {},
      agentCache: {},
      metadata: {
        spreadsheetName: await this.platform.getSpreadsheetName(),
        platformVersion: await this.platform.getVersion(),
        pollnVersion: '1.0.0',
        author: '',
        description: ''
      }
    };
  }

  /**
   * Merges platform state with runtime state
   */
  private async mergeWithRuntime(
    platformState: SpreadsheetState
  ): Promise<SpreadsheetState> {
    // Get runtime state
    const runtimeState = await this.runtime.getSpreadsheetState(this.spreadsheetId);

    if (!runtimeState) {
      // Runtime doesn't know about this spreadsheet
      await this.runtime.registerSpreadsheet(platformState);
      return platformState;
    }

    // Merge states, preferring runtime for active agents
    return this.mergeStates(platformState, runtimeState);
  }

  /**
   * Merges two states
   */
  private mergeStates(
    platformState: SpreadsheetState,
    runtimeState: SpreadsheetState
  ): SpreadsheetState {
    // Use runtime's colony state (more up-to-date)
    // Use platform's metadata (user-defined)
    return {
      ...platformState,
      colony: runtimeState.colony,
      lastModified: Math.max(
        platformState.lastModified,
        runtimeState.lastModified
      )
    };
  }

  /**
   * Serializes state for storage
   */
  private serializeState(state: SpreadsheetState): string {
    return JSON.stringify({
      version: state.version,
      lastModified: state.lastModified,
      colony: {
        ...state.colony,
        agents: Array.from(state.colony.agents.entries()),
        bindings: Array.from(state.colony.bindings.entries()),
        dependencyGraph: {
          nodes: Array.from(state.colony.dependencyGraph.nodes.entries()),
          edges: state.colony.dependencyGraph.edges,
          cycles: state.colony.dependencyGraph.cycles,
          levels: Array.from(state.colony.dependencyGraph.levels.entries())
        }
      },
      cellMappings: state.cellMappings,
      metadata: state.metadata
    });
  }

  /**
   * Deserializes state from storage
   */
  private deserializeState(data: string): SpreadsheetState {
    const parsed = JSON.parse(data);

    return {
      ...parsed,
      colony: {
        ...parsed.colony,
        agents: new Map(parsed.colony.agents),
        bindings: new Map(parsed.colony.bindings),
        dependencyGraph: {
          nodes: new Map(parsed.colony.dependencyGraph.nodes),
          edges: parsed.colony.dependencyGraph.edges,
          cycles: parsed.colony.dependencyGraph.cycles,
          levels: new Map(parsed.colony.dependencyGraph.levels)
        }
      }
    };
  }

  private async getDefaultColonyConfig(): Promise<any> {
    return {
      // Default colony configuration
    };
  }

  private async mergeState(state: SpreadsheetState): Promise<void> {
    // Merge state into local storage
  }
}
```

### 6.3 Collaboration Support

```typescript
/**
 * Manages collaborative spreadsheet scenarios
 */
class CollaborationManager {
  private spreadsheetId: string;
  private runtime: POLLNRuntime;
  private userId: string;

  constructor(spreadsheetId: string, runtime: POLLNRuntime, userId: string) {
    this.spreadsheetId = spreadsheetId;
    this.runtime = runtime;
    this.userId = userId;
  }

  /**
   * Acquires lock for editing an agent
   */
  async acquireLock(agentId: string): Promise<LockHandle> {
    const response = await this.runtime.acquireLock({
      spreadsheetId: this.spreadsheetId,
      agentId: agentId,
      userId: this.userId,
      ttl: 30000 // 30 seconds
    });

    return {
      agentId: agentId,
      lockId: response.lockId,
      acquiredAt: Date.now(),
      expiresAt: Date.now() + 30000
    };
  }

  /**
   * Releases lock for an agent
   */
  async releaseLock(lock: LockHandle): Promise<void> {
    await this.runtime.releaseLock({
      spreadsheetId: this.spreadsheetId,
      agentId: lock.agentId,
      lockId: lock.lockId,
      userId: this.userId
    });
  }

  /**
   * Subscribes to agent updates from other users
   */
  async subscribeToUpdates(
    agentIds: string[],
    callback: (update: AgentUpdate) => void
  ): Promise<SubscriptionHandle> {
    return await this.runtime.subscribeToAgentUpdates({
      spreadsheetId: this.spreadsheetId,
      agentIds: agentIds,
      userId: this.userId,
      callback: callback
    });
  }
}

interface LockHandle {
  agentId: string;
  lockId: string;
  acquiredAt: number;
  expiresAt: number;
}

interface SubscriptionHandle {
  subscriptionId: string;
  unsubscribe: () => void;
}

interface AgentUpdate {
  agentId: string;
  userId: string;
  timestamp: number;
  changes: Record<string, any>;
}
```

---

## 7. Communication Protocols

### 7.1 Inter-Cell Messaging

```typescript
/**
 * Message passing between agents in different cells
 */
interface CellMessage {
  id: string;
  timestamp: number;

  // Source/destination
  fromCell: string;
  toCell: string;
  fromAgent: string;
  toAgent: string;

  // Content
  type: string;
  payload: any;

  // Routing
  routing: MessageRouting;

  // Context
  spreadsheetId: string;
  correlationId?: string;
}

interface MessageRouting {
  direct: boolean;              // Direct or via runtime
  viaCells?: string[];          // Intermediate cells
  priority: 'low' | 'normal' | 'high';
  ttl?: number;                // Time to live
}

/**
 * Router for inter-cell messages
 */
class CellMessageRouter {
  private colony: SpreadsheetColony;
  private runtime: POLLNRuntime;

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
  }

  /**
   * Routes a message from one cell to another
   */
  async routeMessage(message: CellMessage): Promise<void> {
    // Check if destination is local (same spreadsheet)
    const destBinding = this.colony.bindings.get(message.toCell);

    if (destBinding) {
      // Local routing
      await this.routeLocally(message, destBinding);
    } else {
      // Remote routing (via runtime)
      await this.routeRemotely(message);
    }
  }

  /**
   * Routes message within same spreadsheet
   */
  private async routeLocally(
    message: CellMessage,
    destBinding: CellAgentBinding
  ): Promise<void> {
    const agent = this.colony.agents.get(destBinding.agentId);

    if (agent && agent.status === 'active') {
      // Deliver message to agent
      await this.runtime.deliverToAgent({
        agentId: destBinding.agentId,
        message: {
          type: message.type,
          payload: message.payload,
          fromCell: message.fromCell,
          fromAgent: message.fromAgent
        }
      });
    }
  }

  /**
   * Routes message via runtime
   */
  private async routeRemotely(message: CellMessage): Promise<void> {
    await this.runtime.routeMessage(message);
  }

  /**
   * Broadcasts message to all connected cells
   */
  async broadcast(
    fromCell: string,
    messageType: string,
    payload: any
  ): Promise<void> {
    const fromBinding = this.colony.bindings.get(fromCell);

    if (!fromBinding) {
      return;
    }

    // Find all connected cells
    const connectedCells = this.findConnectedCells(fromCell);

    // Send to each
    for (const toCell of connectedCells) {
      const message: CellMessage = {
        id: this.generateMessageId(),
        timestamp: Date.now(),
        fromCell: fromCell,
        toCell: toCell,
        fromAgent: fromBinding.agentId,
        toAgent: this.colony.bindings.get(toCell)?.agentId || '',
        type: messageType,
        payload: payload,
        routing: {
          direct: true,
          priority: 'normal'
        },
        spreadsheetId: this.colony.spreadsheetId
      };

      await this.routeMessage(message);
    }
  }

  /**
   * Finds all cells connected to a given cell
   */
  private findConnectedCells(cellId: string): string[] {
    const connected: string[] = [];
    const node = this.colony.dependencyGraph.nodes.get(cellId);

    if (node) {
      // Add all dependents
      for (const depId of node.dependedOnBy) {
        connected.push(depId);
      }

      // Add all dependencies (for bidirectional communication)
      for (const depId of node.dependsOn) {
        connected.push(depId);
      }
    }

    return connected;
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

### 7.2 Event Propagation

```typescript
/**
 * Events in the spreadsheet agent network
 */
type SpreadsheetEventType =
  | 'agent:created'
  | 'agent:activated'
  | 'agent:deactivated'
  | 'agent:updated'
  | 'agent:error'
  | 'connection:created'
  | 'connection:removed'
  | 'cell:changed'
  | 'dependency:invalidated'
  | 'colony:synced';

interface SpreadsheetEvent {
  id: string;
  type: SpreadsheetEventType;
  timestamp: number;

  // Source
  source: {
    spreadsheetId: string;
    cell?: string;
    agentId?: string;
    userId?: string;
  };

  // Data
  data: Record<string, any>;

  // Propagation
  propagation: {
    broadcast: boolean;
    targetCells?: string[];
    targetAgents?: string[];
  };
}

/**
 * Event bus for spreadsheet events
 */
class SpreadsheetEventBus {
  private colony: SpreadsheetColony;
  private runtime: POLLNRuntime;
  private listeners: Map<SpreadsheetEventType, Set<EventListener>>;

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
    this.listeners = new Map();
  }

  /**
   * Emits an event
   */
  async emit(event: SpreadsheetEvent): Promise<void> {
    // Local listeners
    const typeListeners = this.listeners.get(event.type);
    if (typeListeners) {
      for (const listener of typeListeners) {
        await listener(event);
      }
    }

    // Propagate to affected cells
    if (event.propagation.targetCells) {
      await this.propagateToCells(event);
    }

    // Send to runtime for persistence/broadcast
    await this.runtime.recordEvent(event);
  }

  /**
   * Subscribes to events
   */
  on(eventType: SpreadsheetEventType, listener: EventListener): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }

    this.listeners.get(eventType)!.add(listener);
  }

  /**
   * Unsubscribes from events
   */
  off(eventType: SpreadsheetEventType, listener: EventListener): void {
    const typeListeners = this.listeners.get(eventType);
    if (typeListeners) {
      typeListeners.delete(listener);
    }
  }

  /**
   * Propagates event to target cells
   */
  private async propagateToCells(event: SpreadsheetEvent): Promise<void> {
    if (!event.propagation.targetCells) {
      return;
    }

    for (const cellId of event.propagation.targetCells) {
      const binding = this.colony.bindings.get(cellId);

      if (binding && binding.status === 'active') {
        await this.runtime.notifyAgent({
          agentId: binding.agentId,
          event: {
            type: event.type,
            data: event.data
          }
        });
      }
    }
  }
}

type EventListener = (event: SpreadsheetEvent) => void | Promise<void>;
```

---

## 8. Performance Optimization

### 8.1 Caching Strategy

```typescript
/**
 * Multi-level caching for agent results
 */
class AgentCacheManager {
  private colony: SpreadsheetColony;

  // Cache levels
  private l1Cache: Map<string, CacheEntry>;  // In-memory (current session)
  private l2Cache: Map<string, CacheEntry>;  // Platform storage (cross-session)
  private runtime: POLLNRuntime;              // L3 cache (server)

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
    this.l1Cache = new Map();
    this.l2Cache = new Map();
  }

  /**
   * Gets cached result for an agent
   */
  async get(cellId: string, inputHash: string): Promise<any | null> {
    const cacheKey = `${cellId}:${inputHash}`;

    // L1: In-memory cache
    const l1Entry = this.l1Cache.get(cacheKey);
    if (l1Entry && !this.isExpired(l1Entry)) {
      return l1Entry.value;
    }

    // L2: Platform cache
    const l2Entry = this.l2Cache.get(cacheKey);
    if (l2Entry && !this.isExpired(l2Entry)) {
      // Promote to L1
      this.l1Cache.set(cacheKey, l2Entry);
      return l2Entry.value;
    }

    // L3: Runtime cache
    const l3Value = await this.runtime.getCachedResult(
      this.colony.spreadsheetId,
      cellId,
      inputHash
    );

    if (l3Value !== null) {
      // Cache in L1 and L2
      const entry: CacheEntry = {
        key: cacheKey,
        value: l3Value,
        timestamp: Date.now(),
        ttl: 300000 // 5 minutes
      };

      this.l1Cache.set(cacheKey, entry);
      this.l2Cache.set(cacheKey, entry);

      return l3Value;
    }

    return null;
  }

  /**
   * Sets cached result for an agent
   */
  async set(cellId: string, inputHash: string, value: any, ttl?: number): Promise<void> {
    const cacheKey = `${cellId}:${inputHash}`;
    const entry: CacheEntry = {
      key: cacheKey,
      value: value,
      timestamp: Date.now(),
      ttl: ttl || 300000 // Default 5 minutes
    };

    // L1 cache
    this.l1Cache.set(cacheKey, entry);

    // L2 cache
    this.l2Cache.set(cacheKey, entry);
    await this.persistL2Cache();

    // L3 cache
    await this.runtime.setCachedResult(
      this.colony.spreadsheetId,
      cellId,
      inputHash,
      value,
      ttl
    );
  }

  /**
   * Invalidates cache for a cell
   */
  async invalidate(cellId: string): Promise<void> {
    // Invalidate all entries for this cell
    for (const [key, entry] of this.l1Cache) {
      if (key.startsWith(cellId + ':')) {
        this.l1Cache.delete(key);
      }
    }

    for (const [key, entry] of this.l2Cache) {
      if (key.startsWith(cellId + ':')) {
        this.l2Cache.delete(key);
      }
    }

    await this.persistL2Cache();

    await this.runtime.invalidateCache(
      this.colony.spreadsheetId,
      cellId
    );
  }

  /**
   * Clears all caches
   */
  async clear(): Promise<void> {
    this.l1Cache.clear();
    this.l2Cache.clear();
    await this.persistL2Cache();

    await this.runtime.clearCache(this.colony.spreadsheetId);
  }

  /**
   * Checks if cache entry is expired
   */
  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > entry.ttl;
  }

  /**
   * Persists L2 cache to platform storage
   */
  private async persistL2Cache(): Promise<void> {
    // Serialize and store to platform
    const serialized = Array.from(this.l2Cache.entries());
    // ... store to platform storage
  }
}

interface CacheEntry {
  key: string;
  value: any;
  timestamp: number;
  ttl: number;
}
```

### 8.2 Lazy Evaluation

```typescript
/**
 * Lazy evaluation for spreadsheet agents
 */
class LazyEvaluationManager {
  private colony: SpreadsheetColony;
  private runtime: POLLNRuntime;

  // Evaluation queue
  private evaluationQueue: EvaluationTask[];
  private evaluating: boolean = false;

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
    this.evaluationQueue = [];
  }

  /**
   * Requests evaluation of a cell (may be deferred)
   */
  async requestEvaluation(
    cellId: string,
    priority: 'immediate' | 'normal' | 'deferred' = 'normal'
  ): Promise<any> {
    const binding = this.colony.bindings.get(cellId);

    if (!binding) {
      throw new Error(`No binding found for cell ${cellId}`);
    }

    // Check if agent is configured for lazy evaluation
    if (binding.config.lazy && priority !== 'immediate') {
      return this.queueEvaluation(cellId, priority);
    }

    // Immediate evaluation
    return await this.evaluateNow(binding);
  }

  /**
   * Evaluates an agent immediately
   */
  private async evaluateNow(binding: CellAgentBinding): Promise<any> {
    const agent = this.colony.agents.get(binding.agentId);

    if (!agent) {
      throw new Error(`Agent ${binding.agentId} not found`);
    }

    // Check cache first
    const cacheKey = this.generateCacheKey(binding);
    const cached = await this.runtime.getCachedResult(
      this.colony.spreadsheetId,
      binding.cellAddress,
      cacheKey
    );

    if (cached !== null) {
      return cached;
    }

    // Evaluate agent
    const result = await this.runtime.invokeAgent({
      agentId: binding.agentId,
      inputs: {},
      context: {
        cellAddress: binding.cellAddress,
        spreadsheetId: binding.spreadsheetId
      }
    });

    // Cache result
    await this.runtime.setCachedResult(
      this.colony.spreadsheetId,
      binding.cellAddress,
      cacheKey,
      result.value
    );

    return result.value;
  }

  /**
   * Queues evaluation for later
   */
  private async queueEvaluation(
    cellId: string,
    priority: 'normal' | 'deferred'
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      const task: EvaluationTask = {
        cellId: cellId,
        priority: priority,
        resolve: resolve,
        reject: reject,
        timestamp: Date.now()
      };

      this.evaluationQueue.push(task);

      // Start evaluation if not already running
      if (!this.evaluating) {
        this.processQueue();
      }
    });
  }

  /**
   * Processes evaluation queue
   */
  private async processQueue(): Promise<void> {
    this.evaluating = true;

    try {
      while (this.evaluationQueue.length > 0) {
        // Sort by priority and timestamp
        this.evaluationQueue.sort((a, b) => {
          if (a.priority === 'normal' && b.priority === 'deferred') {
            return -1;
          }
          if (a.priority === 'deferred' && b.priority === 'normal') {
            return 1;
          }
          return a.timestamp - b.timestamp;
        });

        const task = this.evaluationQueue.shift()!;
        const binding = this.colony.bindings.get(task.cellId);

        if (binding) {
          try {
            const result = await this.evaluateNow(binding);
            task.resolve(result);
          } catch (error) {
            task.reject(error);
          }
        }
      }
    } finally {
      this.evaluating = false;
    }
  }

  private generateCacheKey(binding: CellAgentBinding): string {
    // Generate hash based on inputs
    return `hash_${binding.cellAddress}_${Date.now()}`;
  }
}

interface EvaluationTask {
  cellId: string;
  priority: 'normal' | 'deferred';
  resolve: (value: any) => void;
  reject: (error: Error) => void;
  timestamp: number;
}
```

### 8.3 Batch Processing

```typescript
/**
 * Batch processing for multiple agent evaluations
 */
class BatchProcessor {
  private colony: SpreadsheetColony;
  private runtime: POLLNRuntime;

  constructor(colony: SpreadsheetColony, runtime: POLLNRuntime) {
    this.colony = colony;
    this.runtime = runtime;
  }

  /**
   * Evaluates multiple cells in batch
   */
  async evaluateBatch(cellIds: string[]): Promise<Map<string, any>> {
    const results = new Map<string, any>();

    // Group by dependency level for parallel evaluation
    const levels = this.groupByEvaluationLevel(cellIds);

    // Process each level
    for (const [level, cells] of levels) {
      const levelResults = await this.evaluateLevel(cells);

      for (const [cellId, result] of levelResults) {
        results.set(cellId, result);
      }
    }

    return results;
  }

  /**
   * Groups cells by evaluation level
   */
  private groupByEvaluationLevel(
    cellIds: string[]
  ): Map<number, string[]> {
    const levels = new Map<number, string[]>();

    for (const cellId of cellIds) {
      const node = this.colony.dependencyGraph.nodes.get(cellId);

      if (node) {
        const level = node.evaluationOrder;

        if (!levels.has(level)) {
          levels.set(level, []);
        }

        levels.get(level)!.push(cellId);
      }
    }

    return levels;
  }

  /**
   * Evaluates all cells at a given level in parallel
   */
  private async evaluateLevel(cellIds: string[]): Promise<Map<string, any>> {
    const results = new Map<string, any>();

    // Evaluate in parallel
    const evaluations = cellIds.map(async (cellId) => {
      const binding = this.colony.bindings.get(cellId);

      if (binding) {
        const result = await this.runtime.invokeAgent({
          agentId: binding.agentId,
          inputs: {},
          context: {
            cellAddress: binding.cellAddress,
            spreadsheetId: binding.spreadsheetId
          }
        });

        return { cellId, value: result.value };
      }

      return { cellId, value: null };
    });

    const values = await Promise.all(evaluations);

    for (const { cellId, value } of values) {
      results.set(cellId, value);
    }

    return results;
  }
}
```

---

## 9. Security Model

### 9.1 Sandboxing

```typescript
/**
 * Sandbox configuration for agent execution
 */
interface SandboxConfig {
  // Resource limits
  maxMemoryMB: number;
  maxCpuTimeMs: number;
  maxNetworkRequests: number;

  // Network restrictions
  allowedDomains: string[];
  blockedDomains: string[];

  // Data access
  canReadCells: boolean;
  canWriteCells: boolean;
  canAccessExternal: boolean;

  // LLM restrictions
  allowedLLMProviders: string[];
  maxTokensPerRequest: number;

  // Isolation
  isolated: boolean;              // Run in separate process/worker
  persistentState: boolean;       // Allow state persistence
}

/**
 * Sandbox enforcement
 */
class AgentSandbox {
  private config: SandboxConfig;
  private runtime: POLLNRuntime;

  constructor(config: SandboxConfig, runtime: POLLNRuntime) {
    this.config = config;
    this.runtime = runtime;
  }

  /**
   * Validates agent action against sandbox rules
   */
  async validateAction(
    agentId: string,
    action: AgentAction
  ): Promise<SandboxResult> {
    const violations: string[] = [];

    // Check resource usage
    const usage = await this.getRuntimeUsage(agentId);
    if (usage.memoryMB > this.config.maxMemoryMB) {
      violations.push(`Memory limit exceeded: ${usage.memoryMB}MB > ${this.config.maxMemoryMB}MB`);
    }
    if (usage.cpuTimeMs > this.config.maxCpuTimeMs) {
      violations.push(`CPU time limit exceeded: ${usage.cpuTimeMs}ms > ${this.config.maxCpuTimeMs}ms`);
    }

    // Check network access
    if (action.type === 'network_request') {
      if (!this.config.canAccessExternal) {
        violations.push('External network access not allowed');
      }

      const url = new URL(action.url);
      if (this.config.blockedDomains.includes(url.hostname)) {
        violations.push(`Domain ${url.hostname} is blocked`);
      }

      if (this.config.allowedDomains.length > 0 &&
          !this.config.allowedDomains.includes(url.hostname)) {
        violations.push(`Domain ${url.hostname} is not in allowed list`);
      }
    }

    // Check cell access
    if (action.type === 'cell_read' && !this.config.canReadCells) {
      violations.push('Cell reading not allowed');
    }
    if (action.type === 'cell_write' && !this.config.canWriteCells) {
      violations.push('Cell writing not allowed');
    }

    // Check LLM usage
    if (action.type === 'llm_request') {
      if (!this.config.allowedLLMProviders.includes(action.provider)) {
        violations.push(`LLM provider ${action.provider} not allowed`);
      }
      if (action.tokens > this.config.maxTokensPerRequest) {
        violations.push(`Token limit exceeded: ${action.tokens} > ${this.config.maxTokensPerRequest}`);
      }
    }

    return {
      allowed: violations.length === 0,
      violations: violations
    };
  }

  private async getRuntimeUsage(agentId: string): Promise<RuntimeUsage> {
    return await this.runtime.getAgentUsage(agentId);
  }
}

interface AgentAction {
  type: 'network_request' | 'cell_read' | 'cell_write' | 'llm_request';
  [key: string]: any;
}

interface SandboxResult {
  allowed: boolean;
  violations: string[];
}

interface RuntimeUsage {
  memoryMB: number;
  cpuTimeMs: number;
  networkRequestCount: number;
}
```

### 9.2 Permissions

```typescript
/**
 * Permission system for spreadsheet agents
 */
enum Permission {
  // Cell access
  READ_OWN_CELLS = 'read_own_cells',
  READ_ALL_CELLS = 'read_all_cells',
  WRITE_OWN_CELLS = 'write_own_cells',
  WRITE_ALL_CELLS = 'write_all_cells',

  // Agent operations
  CREATE_AGENTS = 'create_agents',
  MODIFY_OWN_AGENTS = 'modify_own_agents',
  MODIFY_ALL_AGENTS = 'modify_all_agents',
  DELETE_OWN_AGENTS = 'delete_own_agents',
  DELETE_ALL_AGENTS = 'delete_all_agents',

  // Network access
  NETWORK_ACCESS = 'network_access',
  LLM_ACCESS = 'llm_access',

  // Learning
  ENABLE_LEARNING = 'enable_learning',
  ENABLE_REINFORCEMENT = 'enable_reinforcement',

  // Collaboration
  SHARE_AGENTS = 'share_agents',
  IMPORT_AGENTS = 'import_agents'
}

/**
 * Permission context
 */
interface PermissionContext {
  userId: string;
  spreadsheetId: string;
  role: 'owner' | 'editor' | 'viewer' | 'collaborator';
  permissions: Set<Permission>;
}

/**
 * Permission manager
 */
class PermissionManager {
  private runtime: POLLNRuntime;

  constructor(runtime: POLLNRuntime) {
    this.runtime = runtime;
  }

  /**
   * Checks if a user has a permission
   */
  async hasPermission(
    context: PermissionContext,
    permission: Permission
  ): Promise<boolean> {
    // Owner has all permissions
    if (context.role === 'owner') {
      return true;
    }

    // Check explicit permission
    if (context.permissions.has(permission)) {
      return true;
    }

    // Check role-based permissions
    return this.getRolePermissions(context.role).has(permission);
  }

  /**
   * Gets permissions for a role
   */
  private getRolePermissions(role: string): Set<Permission> {
    switch (role) {
      case 'editor':
        return new Set([
          Permission.READ_ALL_CELLS,
          Permission.WRITE_ALL_CELLS,
          Permission.CREATE_AGENTS,
          Permission.MODIFY_OWN_AGENTS,
          Permission.DELETE_OWN_AGENTS,
          Permission.NETWORK_ACCESS,
          Permission.LLM_ACCESS,
          Permission.ENABLE_LEARNING,
          Permission.ENABLE_REINFORCEMENT
        ]);

      case 'viewer':
        return new Set([
          Permission.READ_ALL_CELLS
        ]);

      case 'collaborator':
        return new Set([
          Permission.READ_ALL_CELLS,
          Permission.WRITE_OWN_CELLS,
          Permission.CREATE_AGENTS,
          Permission.MODIFY_OWN_AGENTS,
          Permission.DELETE_OWN_AGENTS,
          Permission.SHARE_AGENTS
        ]);

      default:
        return new Set();
    }
  }

  /**
   * Grants a permission to a user
   */
  async grantPermission(
    spreadsheetId: string,
    userId: string,
    permission: Permission
  ): Promise<void> {
    await this.runtime.grantPermission({
      spreadsheetId: spreadsheetId,
      userId: userId,
      permission: permission
    });
  }

  /**
   * Revokes a permission from a user
   */
  async revokePermission(
    spreadsheetId: string,
    userId: string,
    permission: Permission
  ): Promise<void> {
    await this.runtime.revokePermission({
      spreadsheetId: spreadsheetId,
      userId: userId,
      permission: permission
    });
  }
}
```

### 9.3 Data Isolation

```typescript
/**
 * Data isolation between spreadsheets and users
 */
class DataIsolationManager {
  private runtime: POLLNRuntime;

  constructor(runtime: POLLNRuntime) {
    this.runtime = runtime;
  }

  /**
   * Ensures data isolation for an agent
   */
  async isolateAgentData(
    agentId: string,
    spreadsheetId: string,
    userId: string
  ): Promise<void> {
    // Create isolated namespace
    const namespace = this.generateNamespace(spreadsheetId, userId);

    // Move agent data to isolated namespace
    await this.runtime.isolateAgentData({
      agentId: agentId,
      namespace: namespace
    });
  }

  /**
   * Generates isolated namespace
   */
  private generateNamespace(spreadsheetId: string, userId: string): string {
    return `${spreadsheetId}:${userId}`;
  }

  /**
   * Checks if data access is allowed
   */
  async checkDataAccess(
    agentId: string,
    targetAgentId: string,
    context: PermissionContext
  ): Promise<boolean> {
    // Check if agents are in same spreadsheet
    const agentSpreadsheet = await this.runtime.getAgentSpreadsheet(agentId);
    const targetSpreadsheet = await this.runtime.getAgentSpreadsheet(targetAgentId);

    if (agentSpreadsheet !== targetSpreadsheet) {
      // Cross-spreadsheet access requires special permission
      return await this.hasPermission(context, Permission.IMPORT_AGENTS);
    }

    // Same spreadsheet, check ownership
    const agentOwner = await this.runtime.getAgentOwner(agentId);
    const targetOwner = await this.runtime.getAgentOwner(targetAgentId);

    if (agentOwner === targetOwner) {
      return true; // Same owner can access
    }

    // Different owners in same spreadsheet
    return await this.hasPermission(context, Permission.MODIFY_ALL_AGENTS);
  }

  private async hasPermission(
    context: PermissionContext,
    permission: Permission
  ): Promise<boolean> {
    // Delegate to permission manager
    return true;
  }
}
```

---

## 10. Deployment Models

### 10.1 Deployment Architectures

```
┌─────────────────────────────────────────────────────────────┐
│                   Deployment Option 1: Cloud                │
└─────────────────────────────────────────────────────────────┘

Spreadsheet ──HTTPS──▶ Cloud POLLN Runtime
                            │
                            ▼
                     Managed Services
                     - PostgreSQL
                     - Redis
                     - LMCache
                     - LLM APIs

Pros: Scalable, managed, easy updates
Cons: Latency, ongoing costs

┌─────────────────────────────────────────────────────────────┐
│                Deployment Option 2: On-Premise              │
└─────────────────────────────────────────────────────────────┘

Spreadsheet ──HTTPS──▶ On-Premise POLLN Runtime
                            │
                            ▼
                     Local Infrastructure
                     - PostgreSQL
                     - Redis
                     - Local LLM

Pros: Low latency, data control, no API costs
Cons: Maintenance, scaling limits

┌─────────────────────────────────────────────────────────────┐
│               Deployment Option 3: Hybrid                   │
└─────────────────────────────────────────────────────────────┘

Spreadsheet ──HTTPS──▶ Local POLLN Runtime ──▶ Cloud Backup
                            │                      │
                            ▼                      ▼
                     Local Cache           Cloud Sync
                     - LMCache             - Federated Learning
                     - Local LLM           - Meadow

Pros: Best of both worlds
Cons: Complex setup, sync overhead
```

### 10.2 Runtime Service Deployment

```yaml
# docker-compose.yml for POLLN Runtime
version: '3.8'

services:
  polln-runtime:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/polln
      - REDIS_URL=redis://redis:6379
      - LMCACHE_BACKEND=redis
    depends_on:
      - db
      - redis
      - lmcache
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=polln
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  lmcache:
    image: lmcache/lmcache-server:latest
    ports:
      - "50051:50051"
    environment:
      - BACKEND=redis
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - polln-runtime
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 10.3 Distribution Models

#### Excel Add-in Distribution

```xml
<!-- manifest.xml -->
<OfficeApp xmlns="http://schemas.microsoft.com/office/appforoffice/1.1"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:type="TaskPaneApp">
  <Id>YOUR-GUID-HERE</Id>
  <Version>1.0.0.0</Version>
  <ProviderName>Your Company</ProviderName>
  <DefaultLocale>en-US</DefaultLocale>
  <DisplayName DefaultValue="POLLN Agents" />
  <Description DefaultValue="Intelligent agents in your spreadsheet" />
  <IconUrl DefaultValue="https://example.com/icon.png" />

  <AppDomains>
    <AppDomain>https://api.polln.io</AppDomain>
  </AppDomains>

  <Hosts>
    <Host Name="Workbook" />
  </Hosts>

  <Requirements>
    <Sets DefaultMinVersion="1.1">
      <Set Name="ExcelApi" MinVersion="1.10" />
    </Sets>
  </Requirements>

  <DefaultSettings>
    <SourceLocation DefaultValue="https://example.com/task-pane.html" />
  </DefaultSettings>

  <Permissions>ReadWriteDocument</Permissions>

  <VersionOverrides xmlns="http://schemas.microsoft.com/office/taskpaneappversionoverrides"
                    xsi:type="VersionOverridesV1_0">
    <!-- Custom Functions -->
    <VersionOverrides xmlns="http://schemas.microsoft.com/office/excelversionoverrides"
                      xsi:type="VersionOverridesV1_0">
      <WebExtensionProvider>
        <Runtime>
          <Override type="JavaScript" resid="Runtime.Url" />
        </Runtime>
      </WebExtensionProvider>
    </VersionOverrides>
  </VersionOverrides>
</OfficeApp>
```

#### Google Sheets Distribution

```javascript
// Apps Script project structure
├── Code.gs                    // Main functions
├── appsscript.json            // Project manifest
├── POLLNBridge.js             // Runtime bridge
├── config.js                  // Configuration
└── README.md                  // Documentation

// appsscript.json
{
  "timeZone": "America/New_York",
  "dependencies": {
    "enabledAdvancedServices": [
      {
        "userSymbol": "Sheets",
        "serviceId": "sheets",
        "version": "v4"
      }
    ]
  },
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "webapp": {
    "executeAs": "USER_ACCESSING",
    "access": "ANYONE"
  }
}
```

---

## 11. API Design

### 11.1 Spreadsheet-Facing API

```typescript
/**
 * Core spreadsheet API for POLLN
 */
interface SpreadsheetAPI {
  // Agent management
  createAgent(config: AgentConfig): Promise<string>;
  getAgent(agentId: string): Promise<SpreadsheetAgent>;
  updateAgent(agentId: string, config: Partial<AgentConfig>): Promise<void>;
  deleteAgent(agentId: string): Promise<void>;

  // Agent invocation
  invokeAgent(request: InvokeAgentRequest): Promise<InvokeAgentResponse>;
  invokeBatch(requests: InvokeAgentRequest[]): Promise<InvokeAgentResponse[]>;

  // Connections
  connectAgents(from: string, to: string, weight?: number): Promise<string>;
  disconnectAgents(connectionId: string): Promise<void>;
  getConnections(agentId: string): Promise<AgentConnection[]>;

  // Learning
  reinforceAgent(agentId: string, reward: number): Promise<void>;
  getAgentLearning(agentId: string): Promise<LearningEvent[]>;

  // Colony
  getColonyStats(spreadsheetId: string): Promise<ColonyStats>;
  syncColony(spreadsheetId: string): Promise<SpreadsheetColony>;

  // Inspection
  inspectAgent(agentId: string): Promise<AgentInspection>;
  traceExecution(agentId: string): Promise<ExecutionTrace>;

  // Cache
  getCachedResult(spreadsheetId: string, cell: string, hash: string): Promise<any>;
  setCachedResult(spreadsheetId: string, cell: string, hash: string, value: any, ttl?: number): Promise<void>;
  invalidateCache(spreadsheetId: string, cell?: string): Promise<void>;
}

interface InvokeAgentRequest {
  agentId: string;
  inputs: Record<string, any>;
  context: {
    cellAddress: string;
    spreadsheetId: string;
    recalculate?: boolean;
    args?: any[];
  };
}

interface InvokeAgentResponse {
  value: any;
  agentId: string;
  executionTime: number;
  cached: boolean;
  error?: string;
}

interface AgentInspection {
  agent: SpreadsheetAgent;
  connections: AgentConnection[];
  recentActivity: ActivityEntry[];
  learningProgress: LearningProgress;
  performanceMetrics: PerformanceMetrics;
}

interface ExecutionTrace {
  traceId: string;
  agentId: string;
  steps: TraceStep[];
  totalDuration: number;
  a2aPackages: string[];
}

interface TraceStep {
  stepId: string;
  type: 'input' | 'processing' | 'output' | 'error';
  timestamp: number;
  duration: number;
  data: any;
}
```

### 11.2 Runtime API

```typescript
/**
 * POLLN Runtime API for spreadsheet integration
 */
class POLLNRuntime {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  /**
   * Invokes an agent
   */
  async invokeAgent(request: InvokeAgentRequest): Promise<InvokeAgentResponse> {
    const response = await fetch(`${this.baseUrl}/api/spreadsheet/agent/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`Runtime error: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Creates a new agent
   */
  async createAgent(config: AgentConfig): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/spreadsheet/agent/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(config)
    });

    const result = await response.json();
    return result.agentId;
  }

  /**
   * Gets agent state
   */
  async getAgent(agentId: string): Promise<SpreadsheetAgent> {
    const response = await fetch(`${this.baseUrl}/api/spreadsheet/agent/${agentId}`, {
      headers: {
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      }
    });

    return await response.json();
  }

  /**
   * Connects two agents
   */
  async connectAgents(
    fromAgent: string,
    toAgent: string,
    weight: number
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/spreadsheet/agent/connect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify({
        fromAgent,
        toAgent,
        weight
      })
    });

    const result = await response.json();
    return result.connectionId;
  }

  /**
   * Gets cached result
   */
  async getCachedResult(
    spreadsheetId: string,
    cell: string,
    hash: string
  ): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/spreadsheet/cache/get?spreadsheet=${spreadsheetId}&cell=${cell}&hash=${hash}`,
      {
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      }
    );

    if (response.status === 404) {
      return null;
    }

    const result = await response.json();
    return result.value;
  }

  /**
   * Sets cached result
   */
  async setCachedResult(
    spreadsheetId: string,
    cell: string,
    hash: string,
    value: any,
    ttl?: number
  ): Promise<void> {
    await fetch(`${this.baseUrl}/api/spreadsheet/cache/set`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify({
        spreadsheetId,
        cell,
        hash,
        value,
        ttl
      })
    });
  }

  /**
   * Syncs spreadsheet state
   */
  async syncSpreadsheetState(state: SpreadsheetState): Promise<SpreadsheetState> {
    const response = await fetch(`${this.baseUrl}/api/spreadsheet/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(state)
    });

    return await response.json();
  }

  /**
   * Gets spreadsheet state
   */
  async getSpreadsheetState(spreadsheetId: string): Promise<SpreadsheetState | null> {
    const response = await fetch(
      `${this.baseUrl}/api/spreadsheet/${spreadsheetId}/state`,
      {
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      }
    );

    if (response.status === 404) {
      return null;
    }

    return await response.json();
  }

  /**
   * Registers a spreadsheet
   */
  async registerSpreadsheet(state: SpreadsheetState): Promise<void> {
    await fetch(`${this.baseUrl}/api/spreadsheet/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(state)
    });
  }

  /**
   * Records an event
   */
  async recordEvent(event: SpreadsheetEvent): Promise<void> {
    await fetch(`${this.baseUrl}/api/spreadsheet/event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(event)
    });
  }

  /**
   * Acquires lock
   */
  async acquireLock(request: LockRequest): Promise<LockResponse> {
    const response = await fetch(`${this.baseUrl}/api/spreadsheet/lock/acquire`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(request)
    });

    return await response.json();
  }

  /**
   * Releases lock
   */
  async releaseLock(request: LockReleaseRequest): Promise<void> {
    await fetch(`${this.baseUrl}/api/spreadsheet/lock/release`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify(request)
    });
  }

  /**
   * Subscribes to agent updates
   */
  async subscribeToAgentUpdates(
    request: SubscriptionRequest
  ): Promise<SubscriptionHandle> {
    // Implementation depends on WebSocket support
    throw new Error('Not implemented');
  }

  /**
   * Gets colony stats
   */
  async getColonyStats(spreadsheetId: string): Promise<ColonyStats> {
    const response = await fetch(
      `${this.baseUrl}/api/spreadsheet/${spreadsheetId}/stats`,
      {
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      }
    );

    return await response.json();
  }

  /**
   * Inspects agent
   */
  async inspectAgent(agentId: string): Promise<AgentInspection> {
    const response = await fetch(
      `${this.baseUrl}/api/spreadsheet/agent/${agentId}/inspect`,
      {
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      }
    );

    return await response.json();
  }

  /**
   * Traces execution
   */
  async traceExecution(agentId: string): Promise<ExecutionTrace> {
    const response = await fetch(
      `${this.baseUrl}/api/spreadsheet/agent/${agentId}/trace`,
      {
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      }
    );

    return await response.json();
  }

  /**
   * Invalidates cache
   */
  async invalidateCache(spreadsheetId: string, cell?: string): Promise<void> {
    const url = cell
      ? `${this.baseUrl}/api/spreadsheet/${spreadsheetId}/cache/${cell}`
      : `${this.baseUrl}/api/spreadsheet/${spreadsheetId}/cache`;

    await fetch(url, {
      method: 'DELETE',
      headers: {
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      }
    });
  }

  /**
   * Clears cache
   */
  async clearCache(spreadsheetId: string): Promise<void> {
    await fetch(`${this.baseUrl}/api/spreadsheet/${spreadsheetId}/cache`, {
      method: 'DELETE',
      headers: {
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      }
    });
  }

  /**
   * Reinforces agent
   */
  async reinforceAgent(agentId: string, reward: number): Promise<void> {
    await fetch(`${this.baseUrl}/api/spreadsheet/agent/${agentId}/reinforce`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
      },
      body: JSON.stringify({ reward })
    });
  }

  /**
   * Gets agent usage
   */
  async getAgentUsage(agentId: string): Promise<RuntimeUsage> {
    const response = await fetch(
      `${this.baseUrl}/api/spreadsheet/agent/${agentId}/usage`,
      {
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      }
    );

    return await response.json();
  }
}

interface LockRequest {
  spreadsheetId: string;
  agentId: string;
  userId: string;
  ttl: number;
}

interface LockResponse {
  lockId: string;
  acquiredAt: number;
  expiresAt: number;
}

interface LockReleaseRequest {
  spreadsheetId: string;
  agentId: string;
  lockId: string;
  userId: string;
}

interface SubscriptionRequest {
  spreadsheetId: string;
  agentIds: string[];
  userId: string;
  callback?: (update: AgentUpdate) => void;
}
```

---

## 12. MVP Roadmap

### Phase 1: Core Integration (Weeks 1-4)

**Week 1: Excel Foundation**
- Excel custom function implementation
- Basic POLLN bridge for Excel
- Cell-agent binding storage (CustomXmlPart)
- Simple agent invocation

**Week 2: Google Sheets Foundation**
- Google Sheets custom functions
- POLLN bridge for Apps Script
- PropertiesService storage
- Menu and UI setup

**Week 3: Runtime Service**
- Basic runtime API endpoints
- Agent creation and invocation
- Simple cache layer
- Error handling

**Week 4: Testing & Documentation**
- Unit tests for bridges
- Integration tests
- User documentation
- Example spreadsheets

### Phase 2: Agent Networks (Weeks 5-8)

**Week 5: Dependency Tracking**
- Dependency graph implementation
- Cell reference resolution
- Circular dependency detection
- Evaluation order calculation

**Week 6: Inter-Agent Communication**
- A2A package system for spreadsheets
- Message routing between cells
- Event propagation
- Network visualization

**Week 7: State Management**
- State persistence
- Sync mechanisms
- Conflict resolution
- Version control

**Week 8: Performance**
- Caching strategy
- Lazy evaluation
- Batch processing
- Performance testing

### Phase 3: Learning & Optimization (Weeks 9-12)

**Week 9: Learning Integration**
- Hebbian learning for spreadsheet agents
- TD(λ) value functions
- Reward mechanisms
- Learning visualization

**Week 10: Knowledge Distillation**
- LLM observation mode
- Pattern extraction
- Agent creation from examples
- Template library

**Week 11: Advanced Features**
- Dreaming for overnight optimization
- Federated learning across spreadsheets
- Meadow integration
- KV-cache optimization

**Week 12: Polish & Launch**
- Performance optimization
- Security hardening
- User testing
- Launch preparation

### Success Metrics

- **Performance**: < 500ms average agent invocation
- **Reliability**: > 99.9% uptime
- **Adoption**: 100+ active spreadsheets in first month
- **Satisfaction**: > 4.5/5 user rating
- **Learning**: Measurable improvement in agent performance over time

---

## Appendix A: Configuration Examples

### A.1 Agent Configuration

```typescript
// Simple data processor
const dataProcessorConfig: AgentCellConfig = {
  persistent: true,
  lazy: false,
  learningEnabled: true,
  reinforcement: {
    enabled: true,
    autoReinforce: false
  },
  outputFormat: 'raw',
  onError: 'fallback',
  fallbackValue: '#ERROR',
  timeoutMs: 5000,
  cacheEnabled: true,
  cacheTTLSec: 300
};

// Complex analyst agent
const analystConfig: AgentCellConfig = {
  persistent: true,
  lazy: true,
  learningEnabled: true,
  reinforcement: {
    enabled: true,
    autoReinforce: true,
    rewardSignal: 'IF(ISNUMBER(SEARCH("increase", @)), 0.1, -0.1)'
  },
  llmConfig: {
    provider: 'openai',
    model: 'gpt-4',
    maxTokens: 1000,
    temperature: 0.7
  },
  outputFormat: 'json',
  onError: 'retry',
  timeoutMs: 30000,
  cacheEnabled: true,
  cacheTTLSec: 600
};
```

### A.2 Colony Configuration

```typescript
const colonyConfig: ColonyConfig = {
  maxAgents: 100,
  maxConnections: 500,
  learningRate: 0.01,
  explorationRate: 0.3,
  safetyEnabled: true,
  loggingEnabled: true,
  performanceTracking: true
};
```

---

## Appendix B: Error Handling

### B.1 Error Types

```typescript
enum SpreadsheetErrorCode {
  // Agent errors
  AGENT_NOT_FOUND = 'AGENT_NOT_FOUND',
  AGENT_CREATION_FAILED = 'AGENT_CREATION_FAILED',
  AGENT_EXECUTION_FAILED = 'AGENT_EXECUTION_FAILED',
  AGENT_TIMEOUT = 'AGENT_TIMEOUT',

  // Dependency errors
  CIRCULAR_DEPENDENCY = 'CIRCULAR_DEPENDENCY',
  MISSING_DEPENDENCY = 'MISSING_DEPENDENCY',
  INVALID_CELL_REFERENCE = 'INVALID_CELL_REFERENCE',

  // Cache errors
  CACHE_MISS = 'CACHE_MISS',
  CACHE_ERROR = 'CACHE_ERROR',

  // Runtime errors
  RUNTIME_UNAVAILABLE = 'RUNTIME_UNAVAILABLE',
  RUNTIME_ERROR = 'RUNTIME_ERROR',

  // Permission errors
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',

  // Resource errors
  RESOURCE_LIMIT_EXCEEDED = 'RESOURCE_LIMIT_EXCEEDED',
  QUOTA_EXCEEDED = 'QUOTA_EXCEEDED'
}

class SpreadsheetError extends Error {
  constructor(
    public code: SpreadsheetErrorCode,
    message: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'SpreadsheetError';
  }
}
```

---

## Appendix C: Security Considerations

### C.1 Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Malicious agent code | High | Sandboxing, code signing, review process |
| Data exfiltration | High | Network restrictions, data encryption |
| Resource exhaustion | Medium | Rate limiting, resource quotas |
| Privilege escalation | High | Permission checks, audit logging |
| Cross-sheet attacks | Medium | Namespace isolation, access controls |
| LLM injection | Medium | Prompt sanitization, output validation |

### C.2 Security Best Practices

1. **Principle of Least Privilege**: Agents only get permissions they need
2. **Defense in Depth**: Multiple layers of security controls
3. **Audit Logging**: All agent actions logged for review
4. **Regular Updates**: Security patches applied promptly
5. **User Education**: Clear documentation of security features
6. **Incident Response**: Process for handling security incidents

---

## Conclusion

This architecture provides a comprehensive foundation for integrating POLLN with spreadsheet platforms. The design balances:

- **Usability**: Simple formula-based interface
- **Power**: Full agent network capabilities
- **Performance**: Sub-second response times
- **Scalability**: Support for thousands of agents per spreadsheet
- **Security**: Robust sandboxing and permission model
- **Extensibility**: Platform-agnostic core with platform-specific adapters

The phased MVP approach ensures early value delivery while building toward the full vision of democratizing distributed AI through spreadsheets.

---

**Document Version**: 1.0
**Last Updated**: 2026-03-08
**Maintained By**: POLLN Architecture Team
