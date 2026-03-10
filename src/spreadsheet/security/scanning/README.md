# POLLN Security Scanning System

**Enterprise-grade vulnerability scanning and security compliance for TypeScript applications**

---

## Overview

The Security Scanning System provides comprehensive vulnerability detection and security analysis for POLLN applications. It supports static analysis (SAST), dependency scanning, and container image scanning with automated risk assessment and remediation planning.

---

## Features

| Feature | Description |
|---------|-------------|
| **SAST Scanner** | Static analysis with ESLint integration and custom security rules |
| **Dependency Scanner** | npm audit and Snyk integration for known vulnerabilities |
| **Container Scanner** | Trivy-based Docker image scanning with Dockerfile analysis |
| **Vulnerability Tracker** | CVSS scoring, risk assessment, and remediation planning |
| **Security CLI** | Command-line interface for scans and reporting |

---

## Installation

```bash
# The security scanning system is included in POLLN
npm install @polln/security-scanning
```

---

## Quick Start

### CLI Usage

```bash
# Run a full security scan
npx polln-security scan

# Scan specific path
npx polln-security scan --path ./src

# Scan by type
npx polln-security scan --type sast
npx polln-security scan --type dependency
npx polln-security scan --type container

# Generate report
npx polln-security scan --format json --output report.json
```

### Programmatic Usage

```typescript
import { SASTScanner, DependencyScanner, ContainerScanner, VulnerabilityTracker } from '@polln/security-scanning';

// Initialize scanners
const sastScanner = new SASTScanner();
const dependencyScanner = new DependencyScanner();
const containerScanner = new ContainerScanner();
const tracker = new VulnerabilityTracker();

// Run scans
const sastResult = await sastScanner.scan('./src');
const depResult = await dependencyScanner.scan('./');
const containerResult = await containerScanner.scanImage('myapp:latest');

// Track vulnerabilities
for (const finding of sastResult.findings) {
  tracker.addOrUpdate({
    id: finding.id,
    type: 'sast',
    severity: finding.severity,
    title: finding.title,
    description: finding.description,
    detectedAt: new Date(),
    status: 'open'
  });
}

// Get remediation plan
const plan = tracker.getRemediationPlan();
```

---

## Scanners

### SAST Scanner (Static Application Security Testing)

Detects code-level security issues:

- `eval()` usage
- `innerHTML` / `dangerouslySetInnerHTML` XSS vectors
- `document.write()` injections
- Hardcoded credentials
- Insecure random number generation
- Weak cryptographic algorithms

```typescript
import { SASTScanner } from '@polln/security-scanning';

const scanner = new SASTScanner({
  enabledRules: [
    'no-eval',
    'no-inner-html',
    'no-document-write',
    'no-hardcoded-secrets'
  ]
});

const result = await scanner.scan('./src');
console.log(`Found ${result.findings.length} security issues`);
```

### Dependency Scanner

Scans npm dependencies for known vulnerabilities using:

- **npm audit** - Built-in vulnerability database
- **Snyk** - Commercial vulnerability intelligence (optional)

```typescript
import { DependencyScanner } from '@polln/security-scanning';

const scanner = new DependencyScanner({
  includeDevDependencies: true,
  useSnyk: true,
  snykToken: process.env.SNYK_TOKEN
});

const result = await scanner.scan('./');
for (const vuln of result.findings) {
  console.log(`${vuln.title}: ${vuln.recommendation}`);
}
```

### Container Scanner

Scans Docker images for vulnerabilities:

- **Trivy** - Comprehensive vulnerability scanner
- **Dockerfile analysis** - Security best practices

```typescript
import { ContainerScanner } from '@polln/security-scanning';

const scanner = new ContainerScanner({
  severity: 'CRITICAL,HIGH',
  timeout: 300000
});

// Scan Docker image
const imageResult = await scanner.scanImage('myapp:latest');

// Scan Dockerfile
const dockerfileResult = await scanner.scanDockerfile('./Dockerfile');
```

---

## Vulnerability Tracker

Track, prioritize, and plan remediation:

```typescript
import { VulnerabilityTracker } from '@polln/security-scanning';

const tracker = new VulnerabilityTracker();

// Add vulnerability
const tracked = tracker.addOrUpdate({
  id: 'VULN-001',
  type: 'dependency',
  severity: 'high',
  title: 'lodash vulnerable to prototype pollution',
  description: 'Versions < 4.17.21 are affected',
  detectedAt: new Date(),
  status: 'open'
});

// Get risk score (0-100)
console.log(`Risk Score: ${tracked.riskScore}`);

// Get remediation plan
const plan = tracker.getRemediationPlan();
console.log(`Critical: ${plan.critical.length}`);
console.log(`High: ${plan.high.length}`);
console.log(`Total Effort: ${plan.totalEstimatedHours}h`);
```

---

## Severity Levels

| Level | Description | Example |
|-------|-------------|---------|
| **CRITICAL** | Remote code execution, data breach | SQL injection, eval() on user input |
| **HIGH** | Significant security impact | XSS, authentication bypass |
| **MEDIUM** | Moderate security impact | CSRF, insecure configuration |
| **LOW** | Minor security issue | Information disclosure |
| **INFO** | Best practice recommendation | Missing security headers |

---

## OWASP Top 10 Coverage

| Category | Detection |
|----------|-----------|
| A01: Broken Access Control |  SAST rules |
| A02: Cryptographic Failures |  Weak algorithm detection |
| A03: Injection |  SQLi, XSS, eval() |
| A04: Insecure Design |  Security best practices |
| A05: Security Misconfiguration |  Config scanning |
| A06: Vulnerable Components |  Dependency scanning |
| A07: Authentication Failures |  Hardcoded credentials |
| A08: Data Integrity Failures |  Checksum validation |
| A09: Logging Failures |  Audit trail recommendations |
| A10: Server-Side Request Forgery |  URL validation checks |

---

## Configuration

### Environment Variables

```bash
# Snyk integration (optional)
SNYK_TOKEN=your-snyk-token

# Scan timeout
SCAN_TIMEOUT=300000

# Output format
SCAN_FORMAT=json
```

### Scanner Options

```typescript
// SAST Scanner
{
  enabledRules: string[];
  excludePatterns: string[];
  maxFileSize: number;
}

// Dependency Scanner
{
  includeDevDependencies: boolean;
  useSnyk: boolean;
  snykToken: string;
  timeout: number;
}

// Container Scanner
{
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'ALL';
  skipDirs: string[];
  timeout: number;
}
```

---

## CLI Reference

```bash
# Scan commands
npx polln-security scan                    # Run all scans
npx polln-security scan --type sast        # SAST only
npx polln-security scan --type dependency  # Dependencies only
npx polln-security scan --type container   # Container only

# Options
  --path <dir>         # Path to scan (default: .)
  --type <type>        # Scan type: all, sast, dependency, container
  --format <format>    # Output format: table, json, html
  --output <file>      # Write output to file
  --severity <level>   # Minimum severity to report

# Vulnerability management
npx polln-security vulnerabilities              # List all vulnerabilities
npx polln-security vulnerabilities --open       # Show only open issues
npx polln-security remediation                 # Get remediation plan
npx polln-security remediation --priority      # Prioritized by risk score

# Compliance
npx polln-security compliance                 # Check OWASP compliance
npx polln-security compliance --owasp         # OWASP Top 10

# Export/Import
npx polln-security export --format json        # Export findings
npx polln-security import --file scan.json     # Import findings

# Metrics
npx polln-security metrics                    # Show statistics
npx polln-security metrics --trend             # Show trends over time
```

---

## Examples

### Scan Before Deploy

```bash
# Pre-deployment security check
npx polln-security scan --severity critical,high
```

### CI/CD Integration

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npx polln-security scan --format json --output results.json
      - uses: actions/upload-artifact@v3
        with:
          name: security-results
          path: results.json
```

### Custom Security Rules

```typescript
import { SASTScanner } from '@polln/security-scanning';

const scanner = new SASTScanner({
  customRules: [
    {
      id: 'custom-001',
      pattern: /console\.log\(/,
      message: 'Remove console.log before production',
      severity: 'low'
    },
    {
      id: 'custom-002',
      pattern: /TODO.*security/,
      message: 'Security TODO found - address before release',
      severity: 'medium'
    }
  ]
});
```

---

## API Reference

### SASTScanner

```typescript
class SASTScanner {
  constructor(options?: SASTScannerOptions);
  scan(targetPath: string, options?: ScanOptions): Promise<ScanResult>;
  addCustomRule(rule: CustomRule): void;
  removeCustomRule(ruleId: string): void;
}
```

### DependencyScanner

```typescript
class DependencyScanner {
  constructor(options?: DependencyScannerOptions);
  scan(targetPath: string, options?: ScanOptions): Promise<ScanResult>;
  isSnykAvailable(): Promise<boolean>;
}
```

### ContainerScanner

```typescript
class ContainerScanner {
  constructor(options?: ContainerScannerOptions);
  scanImage(imageName: string, options?: ScanOptions): Promise<ScanResult>;
  scanDockerfile(dockerfilePath: string, options?: ScanOptions): Promise<ScanResult>;
  isTrivyAvailable(): Promise<boolean>;
}
```

### VulnerabilityTracker

```typescript
class VulnerabilityTracker {
  addOrUpdate(vulnerability: Vulnerability): TrackedVulnerability;
  remove(id: string): boolean;
  get(id: string): TrackedVulnerability | undefined;
  getAll(): TrackedVulnerability[];
  getRemediationPlan(): RemediationPlan;
  getStatistics(): TrackerStatistics;
}
```

---

## Best Practices

1. **Scan Regularly**: Run scans in CI/CD pipeline
2. **Fix Critical First**: Prioritize CRITICAL and HIGH severity issues
3. **Update Dependencies**: Keep packages up to date
4. **Review Dockerfiles**: Follow security best practices
5. **Track Progress**: Use vulnerability tracker to measure improvement
6. **Automate**: Integrate into deployment workflow

---

## License

MIT License - part of POLLN

---

**Repository:** https://github.com/SuperInstance/polln
**Package:** @polln/security-scanning
**Last Updated:** 2026-03-09
