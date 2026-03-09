# POLLN Spreadsheet Integration - UI Mockups & Visual Specifications

**Detailed visual descriptions for every critical screen and interaction**

---

## Table of Contents

1. [Cell State Mockups](#cell-state-mockups)
2. [Agent Inspector Screens](#agent-inspector-screens)
3. [Dialog Specifications](#dialog-specifications)
4. [Animation Specifications](#animation-specifications)
5. [Icon & Badge System](#icon--badge-system)
6. [Responsive Layouts](#responsive-layouts)
7. [Accessibility Specifications](#accessibility-specifications)

---

## Cell State Mockups

### State 1: Empty Agent Cell (Before First Run)

**Visual Description**:

```
┌────────────────────────────────────────────┐
│  🐝  Click to configure                    │
└────────────────────────────────────────────┘
```

**CSS Specifications**:
```css
.agent-cell-empty {
  border: 2px dashed #8B5CF6;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.03), rgba(139, 92, 246, 0.05));
  border-radius: 4px;
  position: relative;
  transition: all 200ms ease-out;
}

.agent-cell-empty::before {
  /* Bee icon in corner */
  content: "🐝";
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 12px;
  opacity: 0.3;
}

.agent-cell-empty:hover {
  border-color: #7C3AED;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.12));
  cursor: pointer;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
}
```

**Accessibility**:
- ARIA label: "Empty agent cell. Click to configure."
- Focus ring: 3px solid #8B5CF6 when focused via keyboard
- Keyboard: Enter/Space opens configuration

---

### State 2: Agent Cell Processing

**Visual Description**:

```
┌────────────────────────────────────────────┐
│  🐝  Analyzing 99 rows...          [⏳]     │
└────────────────────────────────────────────┘
```

**CSS Specifications**:
```css
.agent-cell-processing {
  border: 2px solid transparent;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

/* Animated border gradient */
.agent-cell-processing::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 4px;
  padding: 2px;
  background: linear-gradient(90deg, #8B5CF6, #3B82F6, #8B5CF6);
  background-size: 200% 100%;
  animation: borderFlow 2s linear infinite;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

@keyframes borderFlow {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

/* Bouncing bee icon */
.agent-cell-processing .agent-icon {
  animation: beeBounce 1s ease-in-out infinite;
}

@keyframes beeBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
```

**Accessibility**:
- ARIA live region: "polite" (announces updates but doesn't interrupt)
- ARIA label: "Agent processing. Analyzing 99 rows of data."
- Screen reader: "Busy" state announced every 5 seconds

---

### State 3: Agent Cell Ready (Success)

**Visual Description**:

```
┌────────────────────────────────────────────┐
│  ✓ Sales: +15.2% Q3              ⚡ Cache  │
└────────────────────────────────────────────┘
```

**CSS Specifications**:
```css
.agent-cell-ready {
  border: 2px solid #3B82F6;
  background: transparent;
  border-radius: 4px;
  position: relative;
  transition: all 150ms ease-out;
}

.agent-cell-ready::after {
  /* Checkmark icon */
  content: "✓";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 12px;
  color: #10B981;
  animation: checkmarkPop 300ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes checkmarkPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); opacity: 1; }
}

.agent-cell-ready:hover {
  border-color: #2563EB;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}
```

**Tooltip HTML**:
```html
<div class="agent-tooltip" role="tooltip">
  <div class="tooltip-header">
    <span class="tooltip-icon">🐝</span>
    <span class="tooltip-title">Sales Summary Agent</span>
  </div>
  <div class="tooltip-body">
    <div class="tooltip-row">
      <span class="tooltip-label">Agents:</span>
      <span class="tooltip-value">3 collaborating</span>
    </div>
    <div class="tooltip-row">
      <span class="tooltip-label">Last run:</span>
      <span class="tooltip-value">2 minutes ago</span>
    </div>
    <div class="tooltip-row">
      <span class="tooltip-label">Cache:</span>
      <span class="tooltip-value">⚡ Hit (saved 0.8s)</span>
    </div>
    <div class="tooltip-row">
      <span class="tooltip-label">Cost:</span>
      <span class="tooltip-value">Free (local)</span>
    </div>
  </div>
  <div class="tooltip-footer">
    <button>Double-click to inspect</button>
  </div>
</div>
```

---

### State 4: Agent Cell with Error

**Visual Description**:

```
┌────────────────────────────────────────────┐
│  ❌ Data format mismatch    [Fix it]       │
└────────────────────────────────────────────┘
```

**CSS Specifications**:
```css
.agent-cell-error {
  border: 2px solid #EF4444;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(239, 68, 68, 0.08));
  border-radius: 4px;
  position: relative;
}

.agent-cell-error::before {
  /* Pulsing red glow */
  content: "";
  position: absolute;
  inset: -4px;
  border-radius: 6px;
  background: rgba(239, 68, 68, 0.2);
  opacity: 0;
  animation: errorPulse 2s ease-in-out infinite;
  z-index: -1;
}

@keyframes errorPulse {
  0%, 100% { opacity: 0; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

/* Fix button in tooltip */
.tooltip-fix-button {
  background: #EF4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.tooltip-fix-button:hover {
  background: #DC2626;
  transform: scale(1.05);
}
```

**Accessibility**:
- ARIA alert: "Agent error. Data format mismatch."
- Focus management: Error cell receives focus automatically if caused by user action
- Keyboard: Enter opens troubleshooting panel

---

## Agent Inspector Screens

### Screen 1: Overview Tab (Default)

**Visual Description**:

```
┌─────────────────────────────────────────────────────────────────┐
│ Sales Summary Agent                                    [×] [⋮]  │
├─────────────────────────────────────────────────────────────────┤
│ [Overview] [Network] [Performance] [Settings]                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Result Summary                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │   Q3 sales increased by 15.2% compared to Q2           │   │
│  │                                                          │   │
│  │   Key findings:                                         │   │
│  │   • Strong performance in Western region (+23%)        │   │
│  │   • Category B showed highest growth (+18%)            │   │
│  │   • Overall trend: Positive momentum                   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📈 Performance Metrics                                         │
│  ┌───────────────────┬───────────────────┬─────────────────┐  │
│  │ Processed         │ 99 rows           │                 │  │
│  │ Runtime           │ 0.3 seconds       │ ⚡ Fast         │  │
│  │ Confidence        │ 87%               │ ✓ Reliable      │  │
│  │ Cache status      │ ⚡ Hit            │ Saved 0.8s      │  │
│  │ Cost              │ Free (local)      │ 💰              │  │
│  └───────────────────┴───────────────────┴─────────────────┘  │
│                                                                 │
│  🔄 Learning Progress                                          │
│  Success rate: 94% ▲ 12% improvement over 30 runs              │
│  ████████████████████████░░░░░░░                               │
│                                                                 │
│  What it learned:                                              │
│  ✓ Your data format (dates in Column A)                        │
│  ✓ Your preferred output style (concise)                       │
│  ✓ Seasonal patterns in your data                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [▶ Run Again]  [⚙️ Configure]  [📋 Copy]  [👥 Share]         │
└─────────────────────────────────────────────────────────────────┘
```

**Layout CSS**:
```css
.agent-inspector {
  width: 420px;
  min-width: 300px;
  max-width: 600px;
  height: 100vh;
  background: #FFFFFF;
  border-left: 1px solid #E5E7EB;
  display: flex;
  flex-direction: column;
  animation: slideInRight 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.inspector-header {
  height: 48px;
  padding: 0 16px;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #F9FAFB;
}

.inspector-tabs {
  height: 40px;
  padding: 0 16px;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  gap: 8px;
}

.tab-button {
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #6B7280;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.tab-button:hover {
  color: #374151;
  background: rgba(0, 0, 0, 0.04);
}

.tab-button.active {
  color: #8B5CF6;
  border-bottom-color: #8B5CF6;
}

.inspector-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.inspector-footer {
  height: 60px;
  padding: 12px 16px;
  border-top: 1px solid #E5E7EB;
  display: flex;
  gap: 8px;
  align-items: center;
}
```

---

### Screen 2: Network Tab (Agent Graph)

**Visual Description**:

```
┌─────────────────────────────────────────────────────────────────┐
│ Agent Network Visualization                                   [×]   │
├─────────────────────────────────────────────────────────────────┤
│ [Overview] [Network] [Performance] [Settings]                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Zoom In] [Zoom Out] [Fit to Screen] [Layout Options ▼]       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │    ┌─────────┐                                          │   │
│  │    │ Fetch   │                                          │   │
│  │    │  Data   │──┐ 3 packages/sec                       │   │
│  │    └─────────┘  │                                       │   │
│  │                 ▼                                       │   │
│  │          ┌─────────┐                                    │   │
│  │          │  Trend  │──▶ Success                         │   │
│  │          │Analyzer │     (87% confidence)               │   │
│  │          └─────────┘                                    │   │
│  │                 │                                       │   │
│  │                 ▼                                       │   │
│  │          ┌─────────┐                                    │   │
│  │          │ Format  │──▶ Done                            │   │
│  │          │ Output  │     (0.1s)                         │   │
│  │          └─────────┘                                    │   │
│  │                                                        │   │
│  │  Double-click any agent to inspect                    │   │
│  │  Drag to rearrange • Scroll to zoom                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Legend:                                                        │
│  📊 Data agents  🧠 Analysis agents  📝 Output agents          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Network Graph CSS**:
```css
.network-graph-container {
  width: 100%;
  height: 400px;
  background: #F9FAFB;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.network-node {
  position: absolute;
  width: 60px;
  height: 60px;
  background: #FFFFFF;
  border: 2px solid #8B5CF6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  cursor: pointer;
  transition: all 200ms ease-out;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.network-node:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
  z-index: 10;
}

.network-node.processing {
  animation: nodePulse 1s ease-in-out infinite;
}

@keyframes nodePulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(139, 92, 246, 0);
  }
}

.network-node.error {
  border-color: #EF4444;
  animation: nodeError 500ms ease-in-out;
}

@keyframes nodeError {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.network-edge {
  stroke: #8B5CF6;
  stroke-width: 2;
  fill: none;
  opacity: 0.6;
}

.network-edge.active {
  stroke-dasharray: 5, 5;
  animation: edgeFlow 1s linear infinite;
}

@keyframes edgeFlow {
  to {
    stroke-dashoffset: -10;
  }
}

.network-edge-label {
  position: absolute;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  color: #6B7280;
  pointer-events: none;
}
```

---

### Screen 3: Performance Tab (Analytics)

**Visual Description**:

```
┌─────────────────────────────────────────────────────────────────┐
│ Performance Analytics                                         [×]   │
├─────────────────────────────────────────────────────────────────┤
│ [Overview] [Network] [Performance] [Settings]                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Runtime Statistics                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Total runs: 234                                       │   │
│  │  Success rate: 94%                                     │   │
│  │  Average runtime: 0.3 seconds                          │   │
│  │  Last run: 2 minutes ago                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  💰 Cost Breakdown                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  Local runs:        232  ━━━━━━━━━━━  100% (Free)      │   │
│  │  API calls:           2  ━━           1% ($0.10)       │   │
│  │  Cache hits:        45  ━━━━━━━━━    19% (Saved $0.45) │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  💡 Optimization Suggestions                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Enable caching for Trend Analysis agent             │   │
│  │    Est. savings: 0.2s per run                          │   │
│  │    [Apply now]                                          │   │
│  │                                                           │   │
│  │  • Use local model instead of API for pattern detection│   │
│  │    Est. savings: $0.05 per run                         │   │
│  │    [Apply now]                                          │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📈 Performance Trend (Last 30 Runs)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Runtime (seconds)                                       │   │
│  │     1.0 │                                              │   │
│  │     0.8 │    ●●                                        │   │
│  │     0.6 │  ●    ●●                                     │   │
│  │     0.4 │●         ●●●                                 │   │
│  │     0.2 │             ●●●●●●●●●●                      │   │
│  │     0.0 └────────────────────────────────               │   │
│  │          Run 1    10    20    30                        │   │
│  │                                                          │   │
│  │  Getting faster! ▲ 40% improvement                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dialog Specifications

### Dialog 1: First Agent Creation (Onboarding)

**Visual Description**:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    🎉 Create Your First Agent                   │
│                                                                 │
│  Describe what you want to do in plain English:                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │  e.g., "Summarize the sales data in Column B"           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  I found some data nearby that might be relevant:              │
│  ○ Sheet1!A2:B100 (Sales data)                                 │
│  ○ Sheet2!C1:D50 (Customer reviews)                            │
│  ○ Manual selection...                                         │
│                                                                 │
│  [Cancel]  [Learn More]  [Create Agent ✨]                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**CSS**:
```css
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 200ms ease-out;
}

.dialog-container {
  width: 500px;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: dialogSlideIn 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dialogSlideIn {
  from {
    transform: scale(0.9) translateY(-20px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.dialog-textarea {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 2px solid #E5E7EB;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 150ms ease-out;
}

.dialog-textarea:focus {
  outline: none;
  border-color: #8B5CF6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.radio-option {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 2px solid #E5E7EB;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.radio-option:hover {
  border-color: #8B5CF6;
  background: rgba(139, 92, 246, 0.02);
}

.radio-option.selected {
  border-color: #8B5CF6;
  background: rgba(139, 92, 246, 0.05);
}

.dialog-primary-button {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.dialog-primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}
```

---

### Dialog 2: Cost Warning (First API Call)

**Visual Description**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  This task uses cloud AI (paid)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  This agent will call GPT-4 to analyze complex patterns.        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💰 Estimated cost: $0.05 per run                        │   │
│  │     You can run this ~200 times with $10 budget          │   │
│  │                                                          │   │
│  │  First run: $0.05                                       │   │
│  │  Subsequent runs: Free (cached) ⚡                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Run anyway]  [Use free/local option]                         │
│  ☐ Don't show this warning again                               │
│                                                                 │
│  💡 Tip: After first run, results are cached for free!         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Accessibility**:
- ARIA role: "alertdialog"
- Focus trap: Keep focus within dialog
- ESC key: Closes dialog
- Enter key: Activates "Run anyway" button

---

### Dialog 3: Agent Configuration (Settings)

**Visual Description**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Agent Configuration                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Name: [Sales Summary Agent_________________________]           │
│                                                                 │
│  ┌─ General ─┐ ┌─ Data ─┐ ┌─ Behavior ─┐ ┌─ Advanced ─┐       │
│                                                                 │
│  Temperature:                                                 │
│  More Creative ●━━━━━━━━● More Precise                         │
│                                                                 │
│  Learning Rate:                                                │
│  Fast Learning ●━━━━━━━━● Stable Results                       │
│                                                                 │
│  Error Handling:                                               │
│  [Retry automatically ▼]                                       │
│                                                                 │
│  Cache Results:    [✓] Enable caching                          │
│  Refresh Trigger:  [On data change ▼]                          │
│                                                                 │
│  ☐ Show advanced options                                       │
│                                                                 │
│  [Cancel]  [Reset to Defaults]  [Save Changes]                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Slider CSS**:
```css
.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.slider-label-left,
.slider-label-right {
  font-size: 12px;
  color: #6B7280;
  min-width: 100px;
}

.slider-input {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(90deg, #8B5CF6, #3B82F6);
  border-radius: 3px;
  outline: none;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: #FFFFFF;
  border: 3px solid #8B5CF6;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 150ms ease-out;
}

.slider-input::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider-value {
  min-width: 60px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #8B5CF6;
}
```

---

## Animation Specifications

### Animation 1: Agent Creation (Sparkle Effect)

**Visual Description**:
- Small sparkle particles appear around cell
- Cell border transforms from dashed to solid
- Bee icon fades in and bounces
- Total duration: 600ms

**CSS**:
```css
@keyframes sparkleAppear {
  0% {
    opacity: 0;
    transform: scale(0) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.2) rotate(180deg);
  }
  100% {
    opacity: 0;
    transform: scale(0.8) rotate(360deg);
  }
}

.sparkle-particle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: radial-gradient(circle, #8B5CF6, transparent);
  border-radius: 50%;
  animation: sparkleAppear 600ms ease-out forwards;
}

/* Generate 6 sparkle particles around the cell */
.agent-cell-creating .sparkle:nth-child(1) { top: -4px; left: 50%; animation-delay: 0ms; }
.agent-cell-creating .sparkle:nth-child(2) { top: 50%; right: -4px; animation-delay: 100ms; }
.agent-cell-creating .sparkle:nth-child(3) { bottom: -4px; left: 50%; animation-delay: 200ms; }
.agent-cell-creating .sparkle:nth-child(4) { top: 50%; left: -4px; animation-delay: 300ms; }
.agent-cell-creating .sparkle:nth-child(5) { top: 20%; right: 20%; animation-delay: 150ms; }
.agent-cell-creating .sparkle:nth-child(6) { bottom: 20%; left: 20%; animation-delay: 250ms; }
```

---

### Animation 2: Data Flow (Edge Animation)

**Visual Description**:
- Small dots flow along agent network edges
- Speed indicates data flow rate
- Color indicates status (purple = normal, red = error)

**CSS**:
```css
.network-edge {
  stroke: #8B5CF6;
  stroke-width: 2;
  fill: none;
  position: relative;
}

.network-edge::after {
  content: "";
  position: absolute;
  width: 6px;
  height: 6px;
  background: #8B5CF6;
  border-radius: 50%;
  animation: edgeFlow 1s linear infinite;
}

@keyframes edgeFlow {
  0% {
    offset-distance: 0%;
  }
  100% {
    offset-distance: 100%;
  }
}

/* Fast flow (high data rate) */
.network-edge.fast::after {
  animation-duration: 0.5s;
}

/* Slow flow (low data rate) */
.network-edge.slow::after {
  animation-duration: 2s;
}

/* Error flow */
.network-edge.error {
  stroke: #EF4444;
}

.network-edge.error::after {
  background: #EF4444;
}
```

---

### Animation 3: Success Checkmark (Completion)

**Visual Description**:
- Checkmark draws itself (SVG stroke animation)
- Subtle "pop" effect
- Confetti burst (optional, for first success)

**CSS**:
```css
.checkmark-container {
  width: 24px;
  height: 24px;
  animation: checkmarkPop 300ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes checkmarkPop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.checkmark-path {
  stroke: #10B981;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
  stroke-dasharray: 24;
  stroke-dashoffset: 24;
  animation: checkmarkDraw 300ms ease-out forwards;
}

@keyframes checkmarkDraw {
  to {
    stroke-dashoffset: 0;
  }
}

/* Confetti burst (for first success) */
.confetti {
  position: absolute;
  width: 8px;
  height: 8px;
  animation: confettiFall 1s ease-out forwards;
}

@keyframes confettiFall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100px) rotate(720deg);
    opacity: 0;
  }
}
```

---

## Icon & Badge System

### Badge Specifications

**Size**: 16px × 16px (small badges), 24px × 24px (large badges)

**Corner Radius**: 4px (small), 6px (large)

**Badge Types**:

```css
/* Cache hit badge */
.badge-cache {
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.badge-cache::before {
  content: "⚡";
}

/* Cost badge */
.badge-cost {
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.badge-cost::before {
  content: "💰";
}

/* Learning badge */
.badge-learning {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  animation: badgePulse 2s ease-in-out infinite;
}

.badge-learning::before {
  content: "🔄";
}

@keyframes badgePulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Privacy badge */
.badge-private {
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.badge-private::before {
  content: "🔒";
}

.badge-public {
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.badge-public::before {
  content: "🌐";
}
```

---

### Status Icons (SVG)

**Success Icon**:
```html
<svg class="status-icon status-icon-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path class="checkmark-path" d="M20 6L9 17l-5-5"/>
</svg>
```

**Error Icon**:
```html
<svg class="status-icon status-icon-error" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="12" cy="12" r="10"/>
  <line x1="15" y1="9" x2="9" y2="15"/>
  <line x1="9" y1="9" x2="15" y2="15"/>
</svg>
```

**Warning Icon**:
```html
<svg class="status-icon status-icon-warning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
  <line x1="12" y1="9" x2="12" y2="13"/>
  <line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>
```

**Processing Icon (Spinner)**:
```html
<svg class="status-icon status-icon-processing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <circle class="spinner-path" cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
</svg>
```

```css
.spinner-path {
  animation: spin 1s linear infinite;
  transform-origin: center;
}

@keyframes spin {
  to {
    stroke-dashoffset: 0;
    transform: rotate(360deg);
  }
}
```

---

## Responsive Layouts

### Mobile Adaptation (When spreadsheet viewed on mobile)

**Constraints**:
- Screen width: < 768px
- Touch interaction only
- Limited screen real estate

**Adaptations**:

1. **Agent Cell**:
   - Same visual treatment (border, icons)
   - Larger touch targets (min 44px × 44px)
   - Swipe to access actions (instead of hover)

2. **Agent Inspector**:
   - Full-screen overlay (instead of side panel)
   - Bottom sheet style (slides up from bottom)
   - Close button: Swipe down or tap outside

3. **Network Graph**:
   - Simplified view (show fewer nodes)
   - Pan/zoom with touch gestures
   - Tap node for details (instead of double-click)

**CSS**:
```css
@media (max-width: 768px) {
  .agent-inspector {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 80vh;
    border-radius: 16px 16px 0 0;
    animation: slideUp 300ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  @keyframes slideUp {
    from {
      transform: translateY(100%);
    }
    to {
      transform: translateY(0);
    }
  }

  .network-graph-container {
    touch-action: pan-x pan-y;
  }

  .network-node {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .inspector-footer {
    padding: 16px;
    gap: 12px;
  }

  .dialog-container {
    width: 90vw;
    max-width: 400px;
  }
}
```

---

## Accessibility Specifications

### Keyboard Navigation

**Tab Order**:
1. Spreadsheet cells (including agent cells)
2. Formula bar
3. Ribbon (Agent tab)
4. Agent Inspector (when open)

**Keyboard Shortcuts**:
- `Ctrl+Shift+A`: Insert new agent
- `Ctrl+Shift+I`: Open inspector for selected agent
- `Ctrl+Shift+R`: Run selected agent
- `Ctrl+Shift+C`: Open agent configuration
- `Escape`: Close inspector/dialog
- `F2`: Edit agent formula (focus formula bar)

**Focus Styles**:
```css
.agent-cell:focus,
.agent-cell:focus-visible {
  outline: 3px solid #8B5CF6;
  outline-offset: 2px;
  border-radius: 4px;
}

.agent-cell:focus:not(:focus-visible) {
  outline: none;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .agent-cell {
    border-width: 3px;
  }

  .agent-cell:focus {
    outline-width: 4px;
  }
}
```

---

### Screen Reader Support

**ARIA Labels**:
```html
<div
  class="agent-cell agent-cell-ready"
  role="button"
  tabindex="0"
  aria-label="Sales Summary Agent. Last ran 2 minutes ago. Double-click to inspect."
  aria-describedby="agent-cell-tooltip-1"
>
  Sales: +15.2% Q3
  <div id="agent-cell-tooltip-1" class="tooltip" role="tooltip" hidden>
    3 agents analyzed this. Cache hit. Free.
  </div>
</div>
```

**Live Regions** (for dynamic updates):
```html
<div
  class="agent-status"
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Processing... 87% complete
</div>
```

**Alerts** (for errors and warnings):
```html
<div
  class="agent-error"
  role="alert"
  aria-live="assertive"
>
  Data format error: Expected date in Column A, got text string
</div>
```

---

### Color Blindness Support

**Not relying on color alone**:
- Use icons + color for status indicators
- Use patterns (stripes, dots) for data visualization
- Provide labels for all color-coded elements

**Example**:
```html
<!-- Bad: Color only -->
<span style="color: red;">Error</span>

<!-- Good: Icon + label -->
<span style="color: red;">
  <span aria-hidden="true">❌</span>
  <span>Error</span>
</span>

<!-- Better: High contrast + pattern -->
<div class="error-badge" style="background: repeating-linear-gradient(45deg, #EF4444, #EF4444 5px, #DC2626 5px, #DC2626 10px); color: white; padding: 2px 6px; border-radius: 4px;">
  <span aria-hidden="true">❌</span>
  Error
</div>
```

---

### Reduced Motion Support

**Respect user's motion preferences**:
```css
@media (prefers-reduced-motion: reduce) {
  /* Disable all animations */
  .agent-cell,
  .network-node,
  .badge-learning,
  .status-icon-processing,
  .checkmark-path,
  .spinner-path {
    animation: none !important;
    transition: none !important;
  }

  /* Use static indicators instead */
  .agent-cell-processing::before {
    content: "Processing...";
    font-size: 10px;
    color: #8B5CF6;
  }

  .status-icon-processing {
    animation: none;
  }

  .status-icon-processing::after {
    content: "...";
  }
}
```

---

## Design Token System

### Colors (CSS Variables)

```css
:root {
  /* Primary - Agent Purple */
  --color-primary-50: #FAF5FF;
  --color-primary-100: #F3E8FF;
  --color-primary-200: #E9D5FF;
  --color-primary-300: #D8B4FE;
  --color-primary-400: #C084FC;
  --color-primary-500: #A855F7;
  --color-primary-600: #9333EA;
  --color-primary-700: #7E22CE;
  --color-primary-800: #6B21A8;
  --color-primary-900: #581C87;

  /* Secondary - Info Blue */
  --color-secondary-50: #EFF6FF;
  --color-secondary-100: #DBEAFE;
  --color-secondary-200: #BFDBFE;
  --color-secondary-300: #93C5FD;
  --color-secondary-400: #60A5FA;
  --color-secondary-500: #3B82F6;
  --color-secondary-600: #2563EB;
  --color-secondary-700: #1D4ED8;
  --color-secondary-800: #1E40AF;
  --color-secondary-900: #1E3A8A;

  /* Success Green */
  --color-success-50: #ECFDF5;
  --color-success-500: #10B981;
  --color-success-700: #047857;

  /* Warning Orange */
  --color-warning-50: #FFF7ED;
  --color-warning-500: #F59E0B;
  --color-warning-700: #B45309;

  /* Error Red */
  --color-error-50: #FEF2F2;
  --color-error-500: #EF4444;
  --color-error-700: #B91C1C;

  /* Neutral Grays */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;
}
```

### Typography (CSS Variables)

```css
:root {
  /* Font Families */
  --font-family-sans: 'Segoe UI', -apple-system, 'Helvetica Neue', sans-serif;
  --font-family-mono: 'Consolas', 'Monaco', 'Courier New', monospace;

  /* Font Sizes */
  --font-size-xs: 10px;
  --font-size-sm: 11px;
  --font-size-base: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
  --font-size-2xl: 24px;

  /* Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Line Heights */
  --line-height-tight: 1.3;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### Spacing (CSS Variables)

```css
:root {
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
}
```

### Border Radius (CSS Variables)

```css
:root {
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-full: 9999px;
}
```

### Shadows (CSS Variables)

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  /* Colored shadows for agent elements */
  --shadow-purple: 0 4px 12px rgba(139, 92, 246, 0.3);
  --shadow-blue: 0 4px 12px rgba(59, 130, 246, 0.3);
  --shadow-green: 0 4px 12px rgba(16, 185, 129, 0.3);
  --shadow-orange: 0 4px 12px rgba(245, 158, 11, 0.3);
  --shadow-red: 0 4px 12px rgba(239, 68, 68, 0.3);
}
```

---

## Implementation Guidelines

### Component Architecture

**Recommended structure**:

```typescript
// AgentCell component
interface AgentCellProps {
  agentId: string;
  formula: string;
  result: AgentResult;
  status: AgentStatus;
  onDoubleClick: () => void;
  onError: (error: AgentError) => void;
}

// AgentInspector component
interface AgentInspectorProps {
  agent: Agent;
  isOpen: boolean;
  activeTab: 'overview' | 'network' | 'performance' | 'settings';
  onClose: () => void;
  onTabChange: (tab: string) => void;
}

// NetworkGraph component
interface NetworkGraphProps {
  nodes: AgentNode[];
  edges: AgentEdge[];
  onNodeClick: (nodeId: string) => void;
  onNodeDoubleClick: (nodeId: string) => void;
  layout: 'force-directed' | 'hierarchical' | 'circular';
}
```

### Performance Considerations

1. **Lazy Loading**:
   - Load network graph visualization only when Network tab is opened
   - Lazy load historical performance data

2. **Virtualization**:
   - Use virtual scrolling for long lists (template library, cost history)
   - Only render visible nodes in network graph (for large networks)

3. **Debouncing**:
   - Debounce autocomplete suggestions (300ms)
   - Debounce cost calculations (500ms)

4. **Caching**:
   - Cache network graph layout calculations
   - Cache performance metrics (invalidated on agent run)

### Browser Compatibility

**Target Browsers**:
- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Excel Online: Latest (web assembly limitation)

**Polyfills Required**:
- `ResizeObserver` (for responsive layout)
- `IntersectionObserver` (for lazy loading)
- CSS Grid (if supporting older browsers)

---

*Document Version: 1.0*
*Last Updated: 2026-03-08*
*Author: Product Design Research Team*
*Status: Ready for Development*
