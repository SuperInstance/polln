"""
SuperInstance Research Platform - Verification Script
====================================================

Quick verification that all platform components are working correctly.
"""

import sys
from pathlib import Path

print("=" * 60)
print("SuperInstance Research Platform - Verification")
print("=" * 60)
print()

# Check Python version
print("1. Python Version")
python_version = sys.version_info
if python_version >= (3, 11):
    print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    print("   PASS: Python 3.11+ required")
else:
    print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    print("   WARNING: Python 3.11+ recommended")
print()

# Check required packages
print("2. Required Packages")
required_packages = {
    'fastapi': 'FastAPI',
    'uvicorn': 'Uvicorn',
    'pydantic': 'Pydantic',
    'numpy': 'NumPy',
    'asyncio': 'AsyncIO'
}

optional_packages = {
    'cupy': 'CuPy (GPU support)',
    'scipy': 'SciPy',
    'h5py': 'HDF5',
    'matplotlib': 'Matplotlib',
    'plotly': 'Plotly'
}

for package, name in required_packages.items():
    try:
        __import__(package)
        print(f"   PASS: {name}")
    except ImportError:
        print(f"   FAIL: {name} - Install with: pip install {package}")

for package, name in optional_packages.items():
    try:
        __import__(package)
        print(f"   INFO: {name} - Available")
    except ImportError:
        print(f"   INFO: {name} - Not installed (optional)")
print()

# Check platform files
print("3. Platform Files")
platform_dir = Path(__file__).parent
required_files = [
    'unified_platform.py',
    'web_interface.py',
    'requirements.txt',
    'README.md',
    'PLATFORM_ARCHITECTURE.md',
    'USER_GUIDE.md',
    'API_REFERENCE.md',
    'SUMMARY.md'
]

for filename in required_files:
    file_path = platform_dir / filename
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"   PASS: {filename} ({size:,} bytes)")
    else:
        print(f"   FAIL: {filename} - Missing")
print()

# Check data directories
print("4. Data Directories")
data_dir = platform_dir / 'data'
required_dirs = ['cache', 'results', 'experiments', 'logs']

for dirname in required_dirs:
    dir_path = data_dir / dirname
    if dir_path.exists():
        print(f"   PASS: {dirname}/")
    else:
        print(f"   INFO: {dirname}/ - Will be created automatically")
print()

# Check deployment configs
print("5. Deployment Configurations")
deployment_files = [
    'deployment/docker/Dockerfile',
    'deployment/docker/docker-compose.yml',
    'deployment/kubernetes/deployment.yaml'
]

for filepath in deployment_files:
    file_path = platform_dir / filepath
    if file_path.exists():
        print(f"   PASS: {filepath}")
    else:
        print(f"   FAIL: {filepath} - Missing")
print()

# Check examples
print("6. Examples")
example_files = [
    'examples/basic_usage.py',
    'examples/api_examples.sh'
]

for filepath in example_files:
    file_path = platform_dir / filepath
    if file_path.exists():
        print(f"   PASS: {filepath}")
    else:
        print(f"   FAIL: {filepath} - Missing")
print()

# Test imports
print("7. Module Imports")
try:
    sys.path.insert(0, str(platform_dir))
    from unified_platform import (
        SuperInstanceResearchPlatform,
        PlatformConfig,
        ExperimentConfig,
        create_platform,
        create_experiment
    )
    print("   PASS: Core platform imports")
except Exception as e:
    print(f"   FAIL: Core platform imports - {e}")

try:
    from unified_platform import (
        Backend,
        SimulationType,
        ValidationType,
        ExperimentStatus
    )
    print("   PASS: Enum imports")
except Exception as e:
    print(f"   FAIL: Enum imports - {e}")
print()

# Test basic functionality
print("8. Basic Functionality Test")
try:
    # Test platform creation
    config = PlatformConfig()
    platform = create_platform(config)
    print("   PASS: Platform creation")

    # Test experiment creation
    experiment = create_experiment(
        experiment_id="verify_001",
        name="Verification Test",
        simulation_type=SimulationType.GPU_ACCELERATED,
        parameters={"test": True}
    )
    print("   PASS: Experiment creation")

    # Test data layer
    exp_id = platform.data.register_experiment(experiment)
    if exp_id == "verify_001":
        print("   PASS: Experiment registration")

    loaded = platform.data.load_experiment(exp_id)
    if loaded and loaded.experiment_id == "verify_001":
        print("   PASS: Experiment loading")

    # Cleanup
    import asyncio
    asyncio.run(platform.shutdown())
    print("   PASS: Platform shutdown")

except Exception as e:
    print(f"   FAIL: Functionality test - {e}")
    import traceback
    traceback.print_exc()
print()

# Summary
print("=" * 60)
print("Verification Complete")
print("=" * 60)
print()
print("To start the platform:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Start server: python web_interface.py")
print("  3. Access API: http://localhost:8000/docs")
print()
print("For more information, see:")
print("  - README.md - Quick start guide")
print("  - USER_GUIDE.md - Comprehensive usage guide")
print("  - PLATFORM_ARCHITECTURE.md - System architecture")
print("  - API_REFERENCE.md - Complete API documentation")
print()
