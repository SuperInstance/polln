# Installation Guide

This guide covers detailed installation instructions for the SuperInstance SDK on all supported platforms.

## System Requirements

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Any modern CPU | Multi-core for best experience |
| **RAM** | 2 GB | 4 GB or more |
| **USB** | USB 3.0 | USB 3.2 or USB4 |
| **OS Disk** | 100 MB free | 500 MB for examples |

### Software Requirements

| Software | Version |
|----------|---------|
| Python | 3.8, 3.9, 3.10, 3.11, or 3.12 |
| pip | Latest version |
| Operating System | See below |

### Operating System Support

| OS | Version | Architecture |
|----|---------|--------------|
| **Linux** | Ubuntu 20.04+, Debian 11+, Fedora 35+, RHEL 8+ | x86_64, ARM64 |
| **macOS** | 10.15 (Catalina) or later | x86_64, Apple Silicon |
| **Windows** | 10 or 11 | x86_64 |

## Installation Methods

### Method 1: pip (Recommended)

The simplest way to install the SDK:

```bash
pip install superinstance-sdk
```

### Method 2: pip with Virtual Environment

Using a virtual environment is recommended for development:

```bash
# Create virtual environment
python -m venv superinstance-env

# Activate it
# Linux/macOS:
source superinstance-env/bin/activate
# Windows:
superinstance-env\Scripts\activate

# Install SDK
pip install superinstance-sdk
```

### Method 3: From Source

For the latest development version or to contribute:

```bash
# Clone the repository
git clone https://github.com/superinstance-ai/superinstance-sdk.git
cd superinstance-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"
```

### Method 4: Specific Version

```bash
pip install superinstance-sdk==1.0.0
```

## Platform-Specific Instructions

### Linux

#### Ubuntu/Debian

```bash
# Update package lists
sudo apt-get update

# Install Python and pip if not already installed
sudo apt-get install python3 python3-pip python3-venv

# Install udev rules for device access
sudo cp /usr/local/lib/python3.X/dist-packages/superinstance/udev/99-superinstance.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to plugdev group (may be needed)
sudo usermod -a -G plugdev $USER

# Log out and back in for group changes to take effect
```

#### Fedora/RHEL

```bash
# Install Python
sudo dnf install python3 python3-pip

# For RHEL/CentOS, enable EPEL if needed
sudo dnf install epel-release
```

#### Linux USB Permissions

If you get "Permission denied" errors when accessing the device:

1. **Option A: Udev rules (recommended)**

Create `/etc/udev/rules.d/99-superinstance.rules`:

```
# SuperInstance AI Device
SUBSYSTEM=="usb", ATTR{idVendor}=="SUPER", ATTR{idProduct}=="0001", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="SUPER", ATTR{idProduct}=="0002", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="SUPER", ATTR{idProduct}=="0003", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="SUPER", ATTR{idProduct}=="0004", MODE="0666"
```

Then reload udev:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

2. **Option B: Run with sudo** (not recommended for development)

```bash
sudo python your_script.py
```

### macOS

#### Install via Homebrew (recommended for Python)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install SDK
pip3 install superinstance-sdk
```

#### macOS USB Permissions

macOS may prompt you to allow USB access. Click "Allow" when prompted.

If the device isn't detected:

1. Open **System Settings** > **Privacy & Security**
2. Check for any security prompts about the device
3. You may need to approve the device in **Security & Privacy** > **Privacy** > **USB Accessories**

### Windows

#### Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Install SDK:

```powershell
pip install superinstance-sdk
```

#### Windows USB Drivers

SuperInstance uses standard USB drivers that are included in Windows 10/11. No additional driver installation should be needed.

If the device isn't detected:

1. Open **Device Manager** (Win + X, then M)
2. Look for "SuperInstance" under "Universal Serial Bus devices"
3. If there's a yellow warning icon, right-click and select "Update driver"
4. Select "Search automatically for drivers"

#### Windows USB 3.0 Ports

Ensure you're using a USB 3.0+ port:

- USB 3.0 ports are usually **blue** inside
- USB 2.0 ports are usually **black** inside
- Check your computer's manual if unsure

## Verify Installation

### Quick Verification

```python
import superinstance
print(f"SDK Version: {superinstance.__version__}")
```

Expected output:
```
SDK Version: 1.0.0
```

### Device Detection Test

```python
from superinstance import Device

devices = Device.list_devices()
print(f"Found {len(devices)} SuperInstance device(s)")

for path in devices:
    print(f"  Device path: {path}")
```

### Full Connectivity Test

```python
from superinstance import Device

try:
    device = Device()
    info = device.info()
    
    print("✅ Device connected successfully!")
    print(f"   Type: {info.device_type.value}")
    print(f"   Serial: {info.serial_number}")
    print(f"   Firmware: {info.firmware_version}")
    print(f"   Cartridge: {info.cartridge_model}")
    print(f"   USB: {info.usb_speed}")
    
    device.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
```

## Development Installation

For contributors and those who want to work with the source code:

```bash
# Clone repository
git clone https://github.com/superinstance-ai/superinstance-sdk.git
cd superinstance-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode with all dependencies
pip install -e ".[dev,test,docs]"
```

### Development Dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Testing framework |
| `pytest-cov` | Coverage reporting |
| `black` | Code formatting |
| `isort` | Import sorting |
| `mypy` | Type checking |
| `flake8` | Linting |
| `sphinx` | Documentation |
| `pre-commit` | Git hooks |

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=superinstance

# Run specific test file
pytest tests/test_device.py -v
```

### Code Formatting

```bash
# Format code
black superinstance tests
isort superinstance tests

# Check formatting
black --check superinstance tests
isort --check superinstance tests

# Type check
mypy superinstance
```

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade superinstance-sdk
```

### Check Installed Version

```bash
pip show superinstance-sdk
```

Or in Python:

```python
import superinstance
print(superinstance.__version__)
```

### Upgrade from Pre-release

```bash
pip install --pre --upgrade superinstance-sdk
```

## Uninstallation

```bash
pip uninstall superinstance-sdk
```

To also remove configuration files:

```bash
# Linux/macOS
rm -rf ~/.superinstance/

# Windows
rmdir /s /q "%USERPROFILE%\.superinstance"
```

## Offline Installation

For environments without internet access:

### Download Wheels

On a machine with internet access:

```bash
# Download wheel and dependencies
pip download superinstance-sdk -d ./packages
```

### Transfer and Install

On the offline machine:

```bash
# Install from local packages
pip install --no-index --find-links=./packages superinstance-sdk
```

## Docker Installation

### Using Pre-built Image

```bash
docker pull superinstance/sdk:latest
```

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

# Install USB libraries
RUN apt-get update && apt-get install -y libusb-1.0-0 && rm -rf /var/lib/apt/lists/*

# Install SDK
RUN pip install superinstance-sdk

# Copy your application
COPY app.py /app/app.py
WORKDIR /app

# Run
CMD ["python", "app.py"]
```

### Docker Run with USB Access

```bash
docker run --device=/dev/bus/usb superinstance/sdk:latest python app.py
```

## Troubleshooting

### "Module 'superinstance' not found"

- Ensure Python environment is activated
- Reinstall: `pip install --force-reinstall superinstance-sdk`
- Check Python path: `python -c "import sys; print(sys.path)"`

### "Permission denied" on Linux

- Install udev rules (see Linux section)
- Or run with sudo (not recommended)

### Device not detected

1. Check USB cable is properly connected
2. Try a different USB port (prefer USB 3.0+)
3. Check device LED status
4. Run `Device.list_devices()` to check detection
5. Check OS USB permissions

### Import errors on Windows

- Install Visual C++ Redistributable:
  ```
  https://aka.ms/vs/17/release/vc_redist.x64.exe
  ```

### Slow installation

Use a mirror if pip is slow:

```bash
pip install -i https://pypi.org/simple/ superinstance-sdk
```

## Next Steps

- **[Getting Started](getting-started.md)**: Run your first inference
- **[API Reference](api-reference.md)**: Explore the SDK
- **[Examples](examples.md)**: See sample projects

---

Need help? Join our [Discord](https://discord.gg/superinstance) or check [Troubleshooting](troubleshooting.md).
