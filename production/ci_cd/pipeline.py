#!/usr/bin/env python3
"""
SuperInstance CI/CD Pipeline Orchestrator

Comprehensive pipeline for:
- Multi-stage testing (unit, integration, simulation validation)
- Docker image building and pushing
- Kubernetes deployment with health checks
- Monitoring and alerting setup
- Rollback capabilities

Author: DevOps Team
Version: 1.0.0
"""

import os
import sys
import subprocess
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import asyncio
import aiohttp
from datetime import datetime

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Pipeline Configuration
# =============================================================================

class Environment(Enum):
    """Deployment environments."""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    project_name: str = "superinstance"
    registry: str = "registry.example.com"
    docker_context: str = "."
    kubernetes_context: str = "k8s-context"
    python_versions: List[str] = field(default_factory=lambda: ["3.10", "3.11"])
    node_versions: List[str] = field(default_factory=lambda: ["18.x", "20.x"])
    gpu_enabled: bool = True
    test_timeout_minutes: int = 30
    build_timeout_minutes: int = 45
    deploy_timeout_minutes: int = 30

    # Thresholds
    code_coverage_threshold: float = 80.0
    lint_threshold: int = 10
    security_scan_threshold: str = "HIGH"

    # Monitoring
    prometheus_url: str = "http://prometheus:9090"
    grafana_url: str = "http://grafana:3000"
    alertmanager_url: str = "http://alertmanager:9093"

    # Rollback
    rollback_on_failure: bool = True
    rollback_timeout_seconds: int = 300


# =============================================================================
# Test Results
# =============================================================================

@dataclass
class TestResult:
    """Result of a test stage."""
    stage_name: str
    success: bool
    duration_seconds: float
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage_name": self.stage_name,
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "details": self.details,
            "errors": self.errors
        }


# =============================================================================
# Pipeline Stages
# =============================================================================

class PipelineStage:
    """Base class for pipeline stages."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.result: Optional[TestResult] = None

    async def execute(self) -> TestResult:
        """Execute the stage. Override in subclasses."""
        raise NotImplementedError

    def _run_command(
        self,
        command: List[str],
        timeout_seconds: int = 300,
        cwd: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """Run shell command."""
        try:
            logger.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=cwd or self.config.docker_context
            )

            success = result.returncode == 0
            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"Command error: {e}")
            return False, "", str(e)


class LintStage(PipelineStage):
    """Code quality and linting stage."""

    async def execute(self) -> TestResult:
        """Run linting checks."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Running linting checks...")

        # Python linting
        python_success, python_stdout, python_stderr = self._run_command([
            "python", "-m", "black", "--check", "src/", "tests/"
        ], timeout_seconds=120)

        if not python_success:
            errors.append(f"Black formatting issues:\n{python_stderr}")
            details["black"] = "failed"
        else:
            details["black"] = "passed"

        # Type checking
        mypy_success, mypy_stdout, mypy_stderr = self._run_command([
            "python", "-m", "mypy", "src/"
        ], timeout_seconds=120)

        if not mypy_success:
            errors.append(f"Type checking issues:\n{mypy_stderr}")
            details["mypy"] = "failed"
        else:
            details["mypy"] = "passed"

        # Security linting
        pylint_success, pylint_stdout, pylint_stderr = self._run_command([
            "python", "-m", "pylint", "src/", "--fail-under=8"
        ], timeout_seconds=180)

        if not pylint_success:
            errors.append(f"Pylint issues:\n{pylint_stderr}")
            details["pylint"] = "failed"
        else:
            details["pylint"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="lint",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class UnitTestStage(PipelineStage):
    """Unit testing stage."""

    async def execute(self) -> TestResult:
        """Run unit tests."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Running unit tests...")

        # Python tests
        python_success, python_stdout, python_stderr = self._run_command([
            "python", "-m", "pytest",
            "tests/unit/",
            "-v",
            "--cov=src/",
            "--cov-report=xml",
            "--cov-report=term-missing",
            f"--cov-fail-under={self.config.code_coverage_threshold}"
        ], timeout_seconds=self.config.test_timeout_minutes * 60)

        if not python_success:
            errors.append(f"Python unit tests failed:\n{python_stderr}")
            details["python_tests"] = "failed"
        else:
            details["python_tests"] = "passed"

        # Node.js tests
        node_success, node_stdout, node_stderr = self._run_command([
            "npm", "test", "--", "--coverage"
        ], timeout_seconds=self.config.test_timeout_minutes * 60)

        if not node_success:
            errors.append(f"Node.js tests failed:\n{node_stderr}")
            details["node_tests"] = "failed"
        else:
            details["node_tests"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="unit_tests",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class IntegrationTestStage(PipelineStage):
    """Integration testing stage."""

    async def execute(self) -> TestResult:
        """Run integration tests."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Running integration tests...")

        # Start test environment
        logger.info("Starting test environment...")
        self._run_command([
            "docker-compose", "-f", "docker-compose.test.yml", "up", "-d"
        ], timeout_seconds=300)

        # Wait for services to be ready
        time.sleep(10)

        # Run integration tests
        test_success, test_stdout, test_stderr = self._run_command([
            "python", "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short"
        ], timeout_seconds=self.config.test_timeout_minutes * 60)

        if not test_success:
            errors.append(f"Integration tests failed:\n{test_stderr}")
            details["integration_tests"] = "failed"
        else:
            details["integration_tests"] = "passed"

        # Cleanup
        logger.info("Stopping test environment...")
        self._run_command([
            "docker-compose", "-f", "docker-compose.test.yml", "down"
        ], timeout_seconds=120)

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="integration_tests",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class SimulationValidationStage(PipelineStage):
    """Simulation schema validation stage."""

    async def execute(self) -> TestResult:
        """Validate all simulation schemas."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Validating simulation schemas...")

        # Run validation script
        validation_success, validation_stdout, validation_stderr = self._run_command([
            "python", "scripts/validate_all_schemas.py"
        ], timeout_seconds=self.config.test_timeout_minutes * 60)

        # Parse results
        if validation_success:
            try:
                results = json.loads(validation_stdout)
                details["validation_results"] = results

                # Check if success rate meets threshold
                success_rate = results.get("success_rate", 0.0)
                if success_rate < 0.8:
                    errors.append(f"Validation success rate {success_rate:.1%} below 80%")
                    details["validation_status"] = "below_threshold"
                else:
                    details["validation_status"] = "passed"

            except json.JSONDecodeError:
                errors.append("Failed to parse validation results")
                details["validation_status"] = "parse_error"
        else:
            errors.append(f"Validation script failed:\n{validation_stderr}")
            details["validation_status"] = "failed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="simulation_validation",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class SecurityScanStage(PipelineStage):
    """Security scanning stage."""

    async def execute(self) -> TestResult:
        """Run security scans."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Running security scans...")

        # Dependency vulnerability scan
        dep_success, dep_stdout, dep_stderr = self._run_command([
            "python", "-m", "safety", "check", "--json"
        ], timeout_seconds=120)

        if not dep_success:
            errors.append(f"Dependency vulnerabilities found:\n{dep_stderr}")
            details["dependency_scan"] = "vulnerabilities_found"
        else:
            details["dependency_scan"] = "passed"

        # Container image scan
        image_success, image_stdout, image_stderr = self._run_command([
            "trivy", "image", "--severity", self.config.security_scan_threshold,
            "--format", "json", f"{self.config.project_name}:test"
        ], timeout_seconds=180)

        if not image_success:
            errors.append(f"Container security issues:\n{image_stderr}")
            details["container_scan"] = "issues_found"
        else:
            details["container_scan"] = "passed"

        # SAST scan
        sast_success, sast_stdout, sast_stderr = self._run_command([
            "bandit", "-r", "src/", "-f", "json"
        ], timeout_seconds=120)

        if not sast_success:
            errors.append(f"SAST issues found:\n{sast_stderr}")
            details["sast_scan"] = "issues_found"
        else:
            details["sast_scan"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="security_scan",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class BuildStage(PipelineStage):
    """Docker image build stage."""

    async def execute(self) -> TestResult:
        """Build Docker images."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Building Docker images...")

        # Build images
        build_success, build_stdout, build_stderr = self._run_command([
            "docker-compose", "-f", "docker-compose.prod.yml", "build"
        ], timeout_seconds=self.config.build_timeout_minutes * 60)

        if not build_success:
            errors.append(f"Docker build failed:\n{build_stderr}")
            self.result = TestResult(
                stage_name="build",
                success=False,
                duration_seconds=time.time() - start_time,
                details=details,
                errors=errors
            )
            return self.result

        details["docker_build"] = "passed"

        # Tag images for registry
        tag_success, tag_stdout, tag_stderr = self._run_command([
            "docker", "tag",
            f"{self.config.project_name}:latest",
            f"{self.config.registry}/{self.config.project_name}:latest"
        ], timeout_seconds=60)

        if not tag_success:
            errors.append(f"Docker tag failed:\n{tag_stderr}")
            details["docker_tag"] = "failed"
        else:
            details["docker_tag"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="build",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class PushStage(PipelineStage):
    """Docker image push stage."""

    async def execute(self) -> TestResult:
        """Push Docker images to registry."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info("Pushing Docker images...")

        # Login to registry
        login_success, login_stdout, login_stderr = self._run_command([
            "docker", "login", self.config.registry,
            "-u", os.getenv("REGISTRY_USERNAME", ""),
            "-p", os.getenv("REGISTRY_PASSWORD", "")
        ], timeout_seconds=60)

        if not login_success:
            errors.append(f"Docker login failed:\n{login_stderr}")
            details["docker_login"] = "failed"

        # Push images
        push_success, push_stdout, push_stderr = self._run_command([
            "docker", "push",
            f"{self.config.registry}/{self.config.project_name}:latest"
        ], timeout_seconds=self.config.build_timeout_minutes * 60)

        if not push_success:
            errors.append(f"Docker push failed:\n{push_stderr}")
            details["docker_push"] = "failed"
        else:
            details["docker_push"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name="push",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


class DeployStage(PipelineStage):
    """Kubernetes deployment stage."""

    def __init__(self, config: PipelineConfig, environment: Environment):
        super().__init__(config)
        self.environment = environment
        self.deployment_name = f"{self.config.project_name}-{environment.value}"

    async def execute(self) -> TestResult:
        """Deploy to Kubernetes."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info(f"Deploying to {self.environment.value}...")

        # Apply Kubernetes manifests
        manifest_path = f"k8s/superinstance/{self.environment.value}/"

        apply_success, apply_stdout, apply_stderr = self._run_command([
            "kubectl", "apply", "-f", manifest_path,
            "--context", self.config.kubernetes_context
        ], timeout_seconds=180)

        if not apply_success:
            errors.append(f"Kubernetes apply failed:\n{apply_stderr}")
            details["kubernetes_apply"] = "failed"

        # Wait for rollout
        rollout_success, rollout_stdout, rollout_stderr = self._run_command([
            "kubectl", "rollout", "status",
            f"deployment/{self.deployment_name}",
            "--context", self.config.kubernetes_context,
            f"--timeout={self.config.deploy_timeout_minutes}m"
        ], timeout_seconds=self.config.deploy_timeout_minutes * 60)

        if not rollout_success:
            errors.append(f"Rollout failed:\n{rollout_stderr}")
            details["rollout_status"] = "failed"
        else:
            details["rollout_status"] = "passed"

        # Verify deployment
        verify_success = await self._verify_deployment()

        if not verify_success:
            errors.append("Deployment verification failed")
            details["verification"] = "failed"
        else:
            details["verification"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name=f"deploy_{self.environment.value}",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result

    async def _verify_deployment(self) -> bool:
        """Verify deployment health."""
        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            try:
                # Check pod status
                success, stdout, stderr = self._run_command([
                    "kubectl", "get", "pods",
                    "-l", f"app={self.config.project_name},env={self.environment.value}",
                    "--context", self.config.kubernetes_context,
                    "-o", "json"
                ], timeout_seconds=30)

                if success:
                    pods = json.loads(stdout)
                    running_pods = [
                        pod for pod in pods.get("items", [])
                        if pod.get("status", {}).get("phase") == "Running"
                    ]

                    if len(running_pods) > 0:
                        logger.info(f"Deployment verified: {len(running_pods)} pods running")
                        return True

                attempt += 1
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Verification error: {e}")
                attempt += 1
                await asyncio.sleep(10)

        return False


class RollbackStage(PipelineStage):
    """Rollback stage."""

    def __init__(self, config: PipelineConfig, environment: Environment):
        super().__init__(config)
        self.environment = environment
        self.deployment_name = f"{self.config.project_name}-{environment.value}"

    async def execute(self) -> TestResult:
        """Rollback deployment."""
        start_time = time.time()
        errors = []
        details = {}

        logger.info(f"Rolling back {self.environment.value} deployment...")

        # Rollback to previous revision
        rollback_success, rollback_stdout, rollback_stderr = self._run_command([
            "kubectl", "rollout", "undo",
            f"deployment/{self.deployment_name}",
            "--context", self.config.kubernetes_context
        ], timeout_seconds=180)

        if not rollback_success:
            errors.append(f"Rollback failed:\n{rollback_stderr}")
            details["rollback"] = "failed"
        else:
            details["rollback"] = "passed"

        # Wait for rollback
        wait_success, wait_stdout, wait_stderr = self._run_command([
            "kubectl", "rollout", "status",
            f"deployment/{self.deployment_name}",
            "--context", self.config.kubernetes_context,
            f"--timeout={self.config.deploy_timeout_minutes}m"
        ], timeout_seconds=self.config.deploy_timeout_minutes * 60)

        if not wait_success:
            errors.append(f"Rollout status check failed:\n{wait_stderr}")
            details["rollback_rollout"] = "failed"
        else:
            details["rollback_rollout"] = "passed"

        duration = time.time() - start_time
        success = len(errors) == 0

        self.result = TestResult(
            stage_name=f"rollback_{self.environment.value}",
            success=success,
            duration_seconds=duration,
            details=details,
            errors=errors
        )

        return self.result


# =============================================================================
# Pipeline Orchestrator
# =============================================================================

class PipelineOrchestrator:
    """Main pipeline orchestrator."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.status = DeploymentStatus.PENDING

    async def run_pipeline(
        self,
        environment: Environment,
        skip_tests: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete pipeline.

        Args:
            environment: Target deployment environment
            skip_tests: Skip test stages (for emergency deploys)

        Returns:
            Pipeline execution summary
        """
        start_time = time.time()
        self.status = DeploymentStatus.RUNNING

        logger.info(f"Starting SuperInstance CI/CD Pipeline for {environment.value}")
        logger.info(f"Configuration: {self.config}")

        try:
            # Stage 1: Lint
            logger.info("\n" + "="*80)
            logger.info("STAGE 1: Lint")
            logger.info("="*80)

            lint_stage = LintStage(self.config)
            lint_result = await lint_stage.execute()
            self.results.append(lint_result)

            if not lint_result.success:
                logger.error("Lint stage failed. Stopping pipeline.")
                await self._handle_failure(environment)
                return self._generate_summary(False, time.time() - start_time)

            # Stage 2: Unit Tests
            logger.info("\n" + "="*80)
            logger.info("STAGE 2: Unit Tests")
            logger.info("="*80)

            if not skip_tests:
                unit_test_stage = UnitTestStage(self.config)
                unit_result = await unit_test_stage.execute()
                self.results.append(unit_result)

                if not unit_result.success:
                    logger.error("Unit test stage failed. Stopping pipeline.")
                    await self._handle_failure(environment)
                    return self._generate_summary(False, time.time() - start_time)
            else:
                logger.warning("Skipping unit tests")

            # Stage 3: Integration Tests
            logger.info("\n" + "="*80)
            logger.info("STAGE 3: Integration Tests")
            logger.info("="*80)

            if not skip_tests:
                integration_stage = IntegrationTestStage(self.config)
                integration_result = await integration_stage.execute()
                self.results.append(integration_result)

                if not integration_result.success:
                    logger.error("Integration test stage failed. Stopping pipeline.")
                    await self._handle_failure(environment)
                    return self._generate_summary(False, time.time() - start_time)
            else:
                logger.warning("Skipping integration tests")

            # Stage 4: Simulation Validation
            logger.info("\n" + "="*80)
            logger.info("STAGE 4: Simulation Validation")
            logger.info("="*80)

            if not skip_tests:
                sim_stage = SimulationValidationStage(self.config)
                sim_result = await sim_stage.execute()
                self.results.append(sim_result)

                if not sim_result.success:
                    logger.error("Simulation validation failed. Stopping pipeline.")
                    await self._handle_failure(environment)
                    return self._generate_summary(False, time.time() - start_time)
            else:
                logger.warning("Skipping simulation validation")

            # Stage 5: Security Scan
            logger.info("\n" + "="*80)
            logger.info("STAGE 5: Security Scan")
            logger.info("="*80)

            security_stage = SecurityScanStage(self.config)
            security_result = await security_stage.execute()
            self.results.append(security_result)

            if not security_result.success:
                logger.error("Security scan failed. Stopping pipeline.")
                await self._handle_failure(environment)
                return self._generate_summary(False, time.time() - start_time)

            # Stage 6: Build
            logger.info("\n" + "="*80)
            logger.info("STAGE 6: Build")
            logger.info("="*80)

            build_stage = BuildStage(self.config)
            build_result = await build_stage.execute()
            self.results.append(build_result)

            if not build_result.success:
                logger.error("Build stage failed. Stopping pipeline.")
                return self._generate_summary(False, time.time() - start_time)

            # Stage 7: Push
            logger.info("\n" + "="*80)
            logger.info("STAGE 7: Push")
            logger.info("="*80)

            push_stage = PushStage(self.config)
            push_result = await push_stage.execute()
            self.results.append(push_result)

            if not push_result.success:
                logger.error("Push stage failed. Stopping pipeline.")
                return self._generate_summary(False, time.time() - start_time)

            # Stage 8: Deploy
            logger.info("\n" + "="*80)
            logger.info(f"STAGE 8: Deploy to {environment.value}")
            logger.info("="*80)

            deploy_stage = DeployStage(self.config, environment)
            deploy_result = await deploy_stage.execute()
            self.results.append(deploy_result)

            if not deploy_result.success:
                logger.error(f"Deploy to {environment.value} failed.")
                await self._handle_failure(environment)
                return self._generate_summary(False, time.time() - start_time)

            # Success!
            self.status = DeploymentStatus.SUCCESS
            logger.info("\n" + "="*80)
            logger.info("PIPELINE SUCCESSFUL")
            logger.info("="*80)

            return self._generate_summary(True, time.time() - start_time)

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            await self._handle_failure(environment)
            return self._generate_summary(False, time.time() - start_time)

    async def _handle_failure(self, environment: Environment):
        """Handle pipeline failure with rollback."""
        if self.config.rollback_on_failure:
            self.status = DeploymentStatus.ROLLING_BACK
            logger.warning("Initiating rollback...")

            rollback_stage = RollbackStage(self.config, environment)
            rollback_result = await rollback_stage.execute()
            self.results.append(rollback_result)

            if rollback_result.success:
                self.status = DeploymentStatus.ROLLED_BACK
                logger.info("Rollback successful")
            else:
                logger.error("Rollback failed")
        else:
            self.status = DeploymentStatus.FAILED

    def _generate_summary(self, success: bool, total_duration: float) -> Dict[str, Any]:
        """Generate pipeline execution summary."""
        summary = {
            "status": self.status.value,
            "success": success,
            "total_duration_seconds": total_duration,
            "stages": [result.to_dict() for result in self.results],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Print summary
        print("\n" + "="*80)
        print("PIPELINE SUMMARY")
        print("="*80)
        print(f"Status: {summary['status'].upper()}")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"\nStages:")
        for result in self.results:
            status_icon = "[PASS]" if result.success else "[FAIL]"
            print(f"  {status_icon} {result.stage_name}: {result.duration_seconds:.2f}s")

        return summary


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperInstance CI/CD Pipeline")
    parser.add_argument(
        "--environment",
        type=str,
        choices=["dev", "staging", "production"],
        default="dev",
        help="Deployment environment"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test stages (emergency deploys only)"
    )

    args = parser.parse_args()

    # Load configuration
    config = PipelineConfig(
        registry=os.getenv("DOCKER_REGISTRY", "registry.example.com"),
        kubernetes_context=os.getenv("K8S_CONTEXT", "minikube")
    )

    # Create orchestrator
    orchestrator = PipelineOrchestrator(config)

    # Run pipeline
    environment = Environment[args.environment.upper()]
    summary = await orchestrator.run_pipeline(
        environment=environment,
        skip_tests=args.skip_tests
    )

    # Exit with appropriate code
    sys.exit(0 if summary["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
