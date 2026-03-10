# POLLN Incident Response System

**Automated incident detection, escalation, and response orchestration**

---

## Overview

The POLLN Incident Response System provides comprehensive incident management with automated detection, intelligent escalation, runbook execution, and multi-channel notifications.

---

## Features

| Feature | Description |
|---------|-------------|
| **Incident Detector** | Rule-based anomaly detection and threshold monitoring |
| **Incident Manager** | Complete incident lifecycle management |
| **Escalation Engine** | Automated multi-level escalation |
| **Runbook Engine** | Automated incident response execution |
| **Notification System** | Multi-channel notifications (Email, Slack, SMS, PagerDuty) |
| **Metrics** | MTTD, MTTR, and trend analysis |

---

## Installation

```bash
# Incident response is included in POLLN
npm install @polln/incidents
```

---

## Quick Start

### Detect and Manage Incidents

```typescript
import {
  IncidentDetector,
  IncidentManager,
  EscalationEngine,
  RunbookEngine,
  NotificationSystem
} from '@polln/incidents';

// Initialize components
const detector = new IncidentDetector();
const manager = new IncidentManager();
const escalation = new EscalationEngine();
const runbooks = new RunbookEngine();
const notifications = new NotificationSystem();

// Add detection rule
detector.addRule({
  id: 'high-error-rate',
  name: 'High Error Rate',
  type: IncidentType.PERFORMANCE,
  severity: IncidentSeverity.HIGH,
  conditions: [{
    metric: 'error_rate',
    operator: 'gte',
    value: 0.05
  }],
  thresholds: [{
    metric: 'error_rate',
    warning: 0.01,
    critical: 0.05
  }]
});

// Process monitoring data
const results = await detector.processData([
  { metric: 'error_rate', value: 0.06, timestamp: new Date(), source: 'api' }
]);

// Create incident for detected issues
for (const result of results) {
  if (result.detected && result.incident) {
    const incident = manager.createIncident(result.incident);
    await escalation.processIncident(incident);
  }
}
```

---

## Incident Detection

### Define Detection Rules

```typescript
import { IncidentDetector } from '@polln/incidents';

const detector = new IncidentDetector({
  enabled: true,
  interval: 30000,
  cooldownPeriod: 300000
});

// Add rule with multiple thresholds
detector.addRule({
  id: 'memory-usage',
  name: 'High Memory Usage',
  type: IncidentType.PERFORMANCE,
  severity: IncidentSeverity.HIGH,
  enabled: true,
  conditions: [
    {
      metric: 'memory_usage',
      operator: 'gte',
      value: 0.9
    }
  ],
  thresholds: [
    {
      metric: 'memory_usage',
      warning: 0.7,
      critical: 0.9
    }
  ]
});
```

### Process Monitoring Data

```typescript
const monitoringData: MonitoringData[] = [
  {
    metric: 'response_time',
    value: 5000,
    timestamp: new Date(),
    source: 'api-server',
    metadata: { endpoint: '/api/users' }
  },
  {
    metric: 'error_rate',
    value: 0.02,
    timestamp: new Date(),
    source: 'api-server'
  }
];

const detections = await detector.processData(monitoringData);

for (const detection of detections) {
  if (detection.detected) {
    console.log(`Incident detected: ${detection.incident?.title}`);
    console.log(`Confidence: ${detection.confidence}`);
  }
}
```

---

## Incident Management

### Create Incident

```typescript
import { IncidentManager } from '@polln/incidents';

const manager = new IncidentManager({
  maxIncidents: 1000,
  retentionDays: 90,
  autoAssign: false
});

const incident = manager.createIncident({
  type: IncidentType.SECURITY,
  severity: IncidentSeverity.CRITICAL,
  status: IncidentStatus.DETECTED,
  title: 'SQL Injection Detected',
  description: 'Potential SQL injection in login form',
  detectedAt: new Date(),
  createdBy: 'security-scanner',
  tags: ['security', 'sql-injection', 'critical'],
  impact: {
    score: 95,
    affectedSystems: ['api-server', 'database'],
    businessCritical: true
  }
});
```

### Update Incident

```typescript
// Update status
manager.updateIncident(
  incident.id,
  { status: IncidentStatus.INVESTIGATING },
  'security-analyst'
);

// Add action
manager.addAction(
  incident.id,
  'investigation',
  'security-analyst',
  {
    success: true,
    message: 'Confirmed SQL injection vulnerability',
    duration: 1200
  }
);

// Resolve incident
manager.resolveIncident(
  incident.id,
  'Patched input validation. No evidence of exploitation.',
  'security-analyst'
);

// Close incident
manager.closeIncident(incident.id, 'security-analyst');
```

### Query Incidents

```typescript
// Get by ID
const incident = manager.getIncident(incidentId);

// Query with filters
const openIncidents = manager.queryIncidents({
  statuses: [IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING],
  severities: [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
  dateRange: { start: new Date(Date.now() - 86400000), end: new Date() }
});

// Get statistics
const stats = manager.getStatistics();
console.log(`
  Total: ${stats.total}
  Unassigned: ${stats.unassigned}
  MTTD: ${stats.mttd.toFixed(0)} minutes
  MTTR: ${stats.mttr.toFixed(0)} minutes
  Trend: ${stats.trend}
`);
```

---

## Escalation Engine

### Define Escalation Rules

```typescript
import { EscalationEngine } from '@polln/incidents';

const escalation = new EscalationEngine({
  enabled: true,
  defaultEscalationDelay: 15,
  maxEscalationLevels: 3,
  requireApproval: true
});

// Add escalation rule
escalation.addRule({
  id: 'security-escalation',
  name: 'Security Incident Escalation',
  type: IncidentType.SECURITY,
  severity: IncidentSeverity.CRITICAL,
  autoEscalate: false,
  steps: [
    {
      level: 1,
      delay: 15, // minutes
      recipients: ['security-team@company.com'],
      message: 'Critical security incident requires attention',
      actions: ['notify', 'create-ticket'],
      conditions: [
        {
          status: [IncidentStatus.DETECTED],
          timeElapsed: 15,
          noActionFor: 10
        }
      ]
    },
    {
      level: 2,
      delay: 30,
      recipients: ['cto@company.com', 'security-lead@company.com'],
      message: 'Security incident escalated to Level 2',
      actions: ['notify', 'page-oncall'],
      conditions: [
        {
          status: [IncidentStatus.INVESTIGATING],
          timeElapsed: 30,
          noActionFor: 20
        }
      ]
    }
  ]
});
```

### Process Escalation

```typescript
// Check for escalations
const results = await escalation.processIncident(incident);

for (const result of results) {
  if (result.escalated) {
    console.log(`Escalated to level ${result.level}`);
    console.log(`Reason: ${result.reason}`);
  }
}

// Get escalation level
const level = escalation.getEscalationLevel(incident.id);

// Reset escalation
escalation.resetEscalation(incident.id);
```

---

## Runbook Engine

### Define Runbooks

```typescript
import { RunbookEngine, DefaultRunbooks } from '@polln/incidents';

const engine = new RunbookEngine({
  timeout: 300000,
  maxRetries: 3,
  allowManualApproval: true,
  requireApprovalFor: ['destructive', 'production-change']
});

// Use predefined runbook
engine.registerRunbook(DefaultRunbooks.securityIncident());

// Or create custom runbook
engine.registerRunbook({
  id: 'database-recovery',
  name: 'Database Recovery Runbook',
  description: 'Automated database recovery procedures',
  incidentTypes: [IncidentType.AVAILABILITY],
  severities: [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
  steps: [
    {
      id: 'check-status',
      name: 'Check Database Status',
      type: 'command',
      config: {
        command: 'pg_isready -h localhost -p 5432'
      },
      requiresApproval: false,
      continueOnFailure: true
    },
    {
      id: 'restart-db',
      name: 'Restart Database',
      type: 'command',
      config: {
        command: 'systemctl restart postgresql'
      },
      requiresApproval: true,
      continueOnFailure: false,
      retries: 2,
      retryOnFailure: true
    },
    {
      id: 'verify',
      name: 'Verify Connectivity',
      type: 'http-request',
      config: {
        url: 'http://localhost:5432/health',
        method: 'GET'
      },
      requiresApproval: false,
      continueOnFailure: false
    }
  ]
});
```

### Execute Runbooks

```typescript
// Execute runbook for incident
const execution = await engine.executeRunbook(
  incident,
  'database-recovery',
  { databaseHost: 'localhost' }
);

console.log(`Execution ID: ${execution.id}`);
console.log(`Status: ${execution.status}`);

// Get execution results
for (const step of execution.steps) {
  console.log(`${step.name}: ${step.status}`);
  if (step.error) {
    console.log(`  Error: ${step.error}`);
  }
}
```

---

## Notification System

### Configure Channels

```typescript
import { NotificationSystem } from '@polln/incidents';

const notifications = new NotificationSystem({
  enabled: true,
  defaultChannels: ['email', 'slack'],
  rateLimits: {
    email: { maxPerMinute: 10, maxPerHour: 100 },
    slack: { maxPerMinute: 20, maxPerHour: 500 }
  }
});

// Configure email
notifications.configureEmail({
  host: 'smtp.company.com',
  port: 587,
  secure: false,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  },
  from: 'noreply@company.com'
});

// Configure Slack
notifications.configureSlack({
  webhookUrl: process.env.SLACK_WEBHOOK_URL,
  defaultChannel: '#incidents',
  username: 'Incident Bot',
  iconEmoji: ':warning:'
});

// Configure SMS (Twilio)
notifications.configureSMS({
  provider: 'twilio',
  accountSid: process.env.TWILIO_ACCOUNT_SID,
  authToken: process.env.TWILIO_AUTH_TOKEN,
  fromNumber: '+1234567890'
});
```

### Send Notifications

```typescript
// Notify for incident
const results = await notifications.notify(
  incident,
  ['email', 'slack', 'sms'],
  'Custom notification message'
);

for (const result of results) {
  if (result.success) {
    console.log(`Sent via ${result.channel}`);
  } else {
    console.error(`Failed: ${result.error}`);
  }
}

// Send manual notification
await notifications.sendEmail([
  'oncall@company.com'
], 'Critical incident detected', '<p>Details...</p>');
```

---

## Statistics and Metrics

### Incident Statistics

```typescript
const stats = manager.getStatistics();

console.log(`
  Total Incidents: ${stats.total}

  By Status:
    Detected: ${stats.byStatus.detected}
    Investigating: ${stats.byStatus.investigating}
    Resolved: ${stats.byStatus.resolved}

  By Severity:
    Critical: ${stats.bySeverity.critical}
    High: ${stats.bySeverity.high}
    Medium: ${stats.bySeverity.medium}

  Performance:
    MTTD: ${stats.mttd.toFixed(0)} min
    MTTR: ${stats.mttr.toFixed(0)} min

  Trend: ${stats.trend}

  Recent Activity:
    Last 24h: ${stats.recentActivity.last24h}
    Last 7d: ${stats.recentActivity.last7d}
    Last 30d: ${stats.recentActivity.last30d}
`);
```

### Detector Statistics

```typescript
const detectorStats = detector.getStatistics();

console.log(`
  Total Rules: ${detectorStats.totalRules}
  Active Rules: ${detectorStats.activeRules}
  Total Incidents: ${detectorStats.totalIncidents}
  Active Incidents: ${detectorStats.activeIncidents}
`);
```

### Escalation Statistics

```typescript
const escalationStats = escalation.getStatistics();

console.log(`
  Total Escalations: ${escalationStats.totalEscalations}
  Incidents Escalated: ${escalationStats.incidentsEscalated}
  Average Level: ${escalationStats.averageLevel.toFixed(1)}
  Max Level: ${escalationStats.maxLevel}
`);
```

---

## Environment Variables

```bash
# Email Configuration
EMAIL_HOST=smtp.company.com
EMAIL_PORT=587
EMAIL_USER=noreply@company.com
EMAIL_PASS=your-password

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token

# PagerDuty Configuration
PAGERDUTY_API_KEY=your-api-key
PAGERDUTY_INTEGRATION_KEY=your-integration-key

# Webhook Configuration
INCIDENT_WEBHOOK_URL=https://your-server.com/webhook
```

---

## Best Practices

1. **Define Clear Rules**: Make detection rules specific and actionable
2. **Set Appropriate Thresholds**: Balance sensitivity and false positives
3. **Document Runbooks**: Keep runbooks up to date with clear steps
4. **Test Notifications**: Verify notification channels work correctly
5. **Review Escalations**: Regularly review and update escalation paths
6. **Track Metrics**: Monitor MTTD and MTTR for improvement
7. **Post-Incident Review**: Conduct post-mortems after major incidents

---

## License

MIT License - part of POLLN

---

**Repository:** https://github.com/SuperInstance/polln
**Package:** @polln/incidents
**Last Updated:** 2026-03-09
