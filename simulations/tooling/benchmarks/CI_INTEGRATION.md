# CI/CD Integration Guide

Guide for integrating POLLN benchmark system into CI/CD pipelines.

## Overview

The POLLN benchmark system provides seamless integration with CI/CD platforms:

- **GitHub Actions** - Full support with PR comments
- **Travis CI** - Basic support
- **CircleCI** - Basic support
- **GitLab CI** - Basic support
- **Jenkins** - Manual integration

---

## GitHub Actions

### Basic Setup

1. **Create workflow file**: `.github/workflows/benchmarks.yml`

```yaml
name: Benchmarks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install numpy scipy matplotlib psutil
          npm install
          npm run build

      - name: Run benchmarks
        run: |
          python simulations/tooling/benchmarks/benchmark_ci.py \
            --scale small \
            --fail-on-regression
```

### Advanced Configuration

```yaml
name: Benchmarks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:      # Manual trigger

jobs:
  # PR benchmarks (fast)
  pr-benchmarks:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install numpy scipy matplotlib psutil
          npm install
          npm run build

      - name: Run benchmarks
        run: |
          python simulations/tooling/benchmarks/benchmark_ci.py \
            --scale small

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: pr-benchmark-results
          path: reports/benchmarks/current/
          retention-days: 7

  # Main branch benchmarks (full)
  main-benchmarks:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install numpy scipy matplotlib psutil
          npm install
          npm run build

      - name: Run benchmarks
        run: |
          python simulations/tooling/benchmarks/benchmark_runner.py \
            --scale medium

      - name: Check regressions
        run: |
          python simulations/tooling/benchmarks/regression_detector.py

      - name: Generate report
        run: |
          python simulations/tooling/benchmarks/report_generator.py

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: main-benchmark-results
          path: reports/benchmarks/
          retention-days: 90

      - name: Update baseline
        run: |
          python simulations/tooling/benchmarks/baseline_manager.py update \
            --results reports/benchmarks/current/benchmarks_*.json

  # Nightly benchmarks (large scale)
  nightly-benchmarks:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install numpy scipy matplotlib psutil
          npm install
          npm run build

      - name: Run large-scale benchmarks
        run: |
          python simulations/tooling/benchmarks/benchmark_runner.py \
            --scale large

      - name: Trend analysis
        run: |
          python simulations/tooling/benchmarks/trend_tracker.py \
            --visualize

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: nightly-benchmark-results
          path: |
            reports/benchmarks/current/
            reports/benchmarks/trends/
          retention-days: 90
```

### PR Comment Integration

The system automatically posts PR comments with results:

```python
# In benchmark_ci.py
def post_pr_comment(self, comment: str):
    """Post comment to PR using GitHub CLI"""
    pr_number = os.environ["PR_NUMBER"]
    subprocess.run([
        "gh", "pr", "comment", str(pr_number),
        "--body", comment
    ])
```

### Status Checks

Configure status checks in branch protection:

1. Go to Repository Settings → Branches
2. Add rule for `main` branch
3. Require status check: `Benchmarks`
4. Mark as required before merging

---

## Travis CI

### Configuration

```yaml
# .travis.yml
language: python
python:
  - "3.10"

install:
  - pip install numpy scipy matplotlib psutil
  - npm install
  - npm run build

script:
  - python simulations/tooling/benchmarks/benchmark_ci.py

after_success:
  - python simulations/tooling/benchmarks/regression_detector.py

notifications:
  email:
    on_success: change
    on_failure: always
```

---

## CircleCI

### Configuration

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  benchmarks:
    docker:
      - image: cimg/python:3.10

    steps:
      - checkout

      - run:
          name: Install dependencies
          command: |
            pip install numpy scipy matplotlib psutil
            npm install
            npm run build

      - run:
          name: Run benchmarks
          command: |
            python simulations/tooling/benchmarks/benchmark_ci.py

      - store_artifacts:
          path: reports/benchmarks/

workflows:
  benchmark-workflow:
    jobs:
      - benchmarks
```

---

## GitLab CI

### Configuration

```yaml
# .gitlab-ci.yml
stages:
  - benchmark

benchmark:
  stage: benchmark
  image: python:3.10
  script:
    - pip install numpy scipy matplotlib psutil
    - npm install
    - npm run build
    - python simulations/tooling/benchmarks/benchmark_ci.py
  artifacts:
    paths:
      - reports/benchmarks/
    expire_in: 30 days
  only:
    - main
    - merge_requests
```

---

## Jenkins

### Pipeline Script

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'pip install numpy scipy matplotlib psutil'
                sh 'npm install'
                sh 'npm run build'
            }
        }

        stage('Benchmarks') {
            steps {
                sh '''
                    python simulations/tooling/benchmarks/benchmark_runner.py \
                    --scale small
                '''
            }
        }

        stage('Regression Check') {
            steps {
                sh '''
                    python simulations/tooling/benchmarks/regression_detector.py
                '''
            }
        }

        stage('Report') {
            steps {
                sh '''
                    python simulations/tooling/benchmarks/report_generator.py
                '''
            }
            publishHTML([
                reportDir: 'reports/benchmarks',
                reportFiles: 'benchmark_report.html',
                reportName: 'Benchmark Report'
            ])
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/benchmarks/**/*'
        }
        failure {
            emailext(
                subject: "Benchmarks Failed: ${env.JOB_NAME}",
                body: "Check console output for details.",
                to: "team@example.com"
            )
        }
    }
}
```

---

## Docker Integration

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install numpy scipy matplotlib psutil

# Install POLLN
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npm run build

# Copy benchmark tools
COPY simulations/ simulations/

# Run benchmarks
CMD ["python", "simulations/tooling/benchmarks/benchmark_ci.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  benchmarks:
    build: .
    volumes:
      - ./reports:/app/reports
      - ./.git:/app/.git
    environment:
      - SCALE=small
      - FAIL_ON_REGRESSION=true
```

---

## Kubernetes Integration

### CronJob for Nightly Benchmarks

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: polln-benchmarks
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: benchmarks
            image: polln-benchmarks:latest
            command:
            - python
            - simulations/tooling/benchmarks/benchmark_runner.py
            - --scale
            - medium
            volumeMounts:
            - name: results
              mountPath: /app/reports
          volumes:
          - name: results
            persistentVolumeClaim:
              claimName: benchmark-results
          restartPolicy: OnFailure
```

---

## Monitoring and Alerting

### Slack Notifications

```yaml
# In GitHub Actions
- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Benchmarks failed! Check logs for details.'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications

```yaml
# In GitHub Actions
- name: Send email on failure
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.example.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "Benchmarks Failed"
    body: "Benchmarks failed. Check GitHub Actions for details."
    to: team@example.com
```

---

## Best Practices

### 1. Benchmark Frequency

| Event | Scale | Frequency |
|-------|-------|-----------|
| PR | Small | Every PR |
| Push to main | Medium | Every commit |
| Nightly | Large | Daily |
| Weekly | All scales | Weekly |

### 2. Baseline Management

- Update baseline monthly or after major improvements
- Keep 3-5 historical baselines
- Archive old baselines instead of deleting

### 3. Failure Handling

```yaml
# Don't fail CI on low-severity regressions
- name: Check regressions
  id: regressions
  continue-on-error: true
  run: |
    python simulations/tooling/benchmarks/regression_detector.py

- name: Post warning comment
  if: steps.regressions.outcome == 'failure'
  run: |
    # Post warning but don't fail
    echo "Performance regression detected"
```

### 4. Caching

```yaml
# Cache benchmark results
- name: Cache benchmark results
  uses: actions/cache@v3
  with:
    path: reports/benchmarks/cache
    key: ${{ runner.os }}-benchmarks-${{ hashFiles('**/*.ts') }}
```

---

## Troubleshooting

### CI Fails Locally

1. Check environment differences
2. Verify all dependencies installed
3. Check for platform-specific code
4. Use Docker for consistency

### Intermittent Failures

1. Increase benchmark iterations
2. Use sequential execution
3. Check for resource contention
4. Add retry logic

### Slow CI Pipelines

1. Use smaller scale for PR checks
2. Parallelize benchmark execution
3. Cache dependencies
4. Use self-hosted runners

---

## Advanced Features

### Custom Metrics

```python
# Add custom metric collection
def benchmark_with_custom_metrics():
    result = benchmark_suite.benchmark_agent_creation()

    # Add custom metrics
    custom_metrics = {
        "custom_throughput": calculate_custom_metric(),
        "custom_latency": measure_custom_latency()
    }

    result.metrics.update(custom_metrics)
    return result
```

### Comparative Benchmarks

```bash
# Compare against multiple baselines
python simulations/tooling/benchmarks/regression_detector.py \
    --baseline baseline_v1.json \
    --baseline baseline_v2.json
```

### Historical Analysis

```python
# Analyze performance over time
from trend_tracker import TrendTracker

tracker = TrendTracker()
report = tracker.generate_report()

# Generate visualizations
tracker.visualize_trends(report.trends.keys())
```

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Travis CI Documentation](https://docs.travis-ci.com/)
- [CircleCI Documentation](https://circleci.com/docs/)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
