# TernaryAir FPGA Prototyping Guide

This guide explains how to build and deploy TernaryAir on FPGA development boards.

## Supported Boards

| Board | FPGA | Status | Notes |
|-------|------|--------|-------|
| PYNQ-Z2 | Zynq-7020 | ✅ Tested | Primary development board |
| Arty A7 | Artix-7 | ✅ Tested | Requires USB-UART bridge |
| ZCU104 | Zynq UltraScale+ | ⚠️ Beta | Higher performance |

## Quick Start

### Prerequisites

- Xilinx Vivado 2022.1 or later
- Digilent board support files
- USB cable for programming

### Build from Source

```bash
cd hardware/fpga

# Build bitstream for PYNQ-Z2
make bitstream BOARD=pynq-z2

# Program the FPGA
make program BOARD=pynq-z2
```

### Use Pre-built Bitstream

```bash
# Download pre-built bitstream
make download-prebuilt BOARD=pynq-z2

# Program the FPGA
make program BOARD=pynq-z2
```

## Resource Utilization

### PYNQ-Z2 (Zynq-7020)

| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUT | 45,230 | 53,200 | 85% |
| FF | 38,450 | 106,400 | 36% |
| BRAM | 98 | 140 | 70% |
| DSP | 12 | 220 | 5% |

### Timing

- Target: 100 MHz
- Achieved: 105 MHz (positive slack)
- First token latency: <50ms

## Pin Assignments

### PYNQ-Z2

| Signal | Pin | Description |
|--------|-----|-------------|
| clk | H16 | 125 MHz clock |
| rst_n | D19 | Button 0 (active low) |
| usb_tx | W15 | UART TX to USB |
| usb_rx | T11 | UART RX from USB |
| led[0] | R14 | Status LED |
| led[1] | P14 | Activity LED |

### Arty A7

| Signal | Pin | Description |
|--------|-----|-------------|
| clk | E3 | 100 MHz clock |
| rst_n | C2 | Button 0 |
| usb_tx | D10 | UART TX |
| usb_rx | A9 | UART RX |

## Testing

### Self-Test

```python
from ternaryair import TernaryAir

# Connect to FPGA
device = TernaryAir(device="/dev/ttyUSB1")  # Adjust port

# Run self-test
result = device.self_test()
print(f"Self-test: {'PASS' if result else 'FAIL'}")

# Test inference
response = device.generate("Hello")
print(f"Response: {response}")
```

### Performance Test

```bash
cd tests/hardware
python benchmark.py --port /dev/ttyUSB1 --tokens 1000
```

## Troubleshooting

### Bitstream Won't Load

1. Check USB cable connection
2. Verify JTAG mode is selected
3. Try `vivado -mode batch -source program.tcl`

### No Response from Device

1. Check UART connection
2. Verify baud rate (115200)
3. Check power LED
4. Try pressing reset button

### Poor Performance

1. Verify timing closure in Vivado
2. Check for cooling issues
3. Ensure stable power supply

## Building Custom Configurations

```tcl
# custom_build.tcl
set_param board.repoPaths [list "path/to/board/files"]

create_project ternaryair ./build -part xc7z020clg400-1
set_property board_part xilinx.com:pynq-z2:part0:1.0

# Add RTL sources
add_files [glob ../rtl/*.sv]

# Set top module
set_property top top_level [current_fileset]

# Run synthesis
launch_runs synth_1
wait_on_run synth_1

# Run implementation
launch_runs impl_1
wait_on_run impl_1

# Generate bitstream
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1
```

## Next Steps

- Connect sensors for edge AI applications
- Integrate with your application via Python SDK
- Deploy to production with custom PCB
