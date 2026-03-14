#!/bin/bash
# SuperInstance.AI Mask-Locked Inference Chip
# One-Click Simulation Runner
#
# Usage: ./run.sh [command] [options]
#
# Commands:
#   sim         Run simulation (verilator/icarus/cocotb)
#   synth       Run synthesis (kv260/de10nano)
#   test        Run tests
#   clean       Clean build artifacts
#   wave        Open waveform viewer
#   status      Show project status
#   help        Show this help
#
# Author: VP Manufacturing, SuperInstance.AI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  SuperInstance.AI Mask-Locked Inference Chip              ${NC}"
    echo -e "${BLUE}  FPGA Simulation & Synthesis Environment                  ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

# Check for required tools
check_tools() {
    local tools_ok=true
    
    echo -e "\n${YELLOW}Checking tools...${NC}\n"
    
    # Check Verilator
    if command -v verilator &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Verilator: $(verilator --version | head -1)"
    else
        echo -e "  ${RED}✗${NC} Verilator: NOT INSTALLED (apt install verilator)"
        tools_ok=false
    fi
    
    # Check Icarus Verilog
    if command -v iverilog &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Icarus Verilog: $(iverilog -V | head -1)"
    else
        echo -e "  ${RED}✗${NC} Icarus Verilog: NOT INSTALLED (apt install iverilog)"
        tools_ok=false
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        local py_ver=$(python3 --version)
        echo -e "  ${GREEN}✓${NC} Python: $py_ver"
    else
        echo -e "  ${RED}✗${NC} Python: NOT INSTALLED"
        tools_ok=false
    fi
    
    # Check cocotb
    if python3 -c "import cocotb" 2>/dev/null; then
        local cocotb_ver=$(python3 -c "import cocotb; print(cocotb.__version__)")
        echo -e "  ${GREEN}✓${NC} Cocotb: $cocotb_ver"
    else
        echo -e "  ${YELLOW}?${NC} Cocotb: NOT INSTALLED (pip install cocotb)"
    fi
    
    echo ""
    
    if [ "$tools_ok" = false ]; then
        echo -e "${YELLOW}Some tools missing. Run setup:${NC}"
        echo -e "  python3 scripts/setup_environment.py"
        return 1
    fi
    
    return 0
}

# Run Verilator simulation
run_verilator() {
    echo -e "\n${GREEN}Running Verilator simulation...${NC}\n"
    
    mkdir -p build/verilator waves
    
    # Build
    echo -e "${YELLOW}Building with Verilator...${NC}"
    verilator --cc --exe --build --timing --trace \
        --top-module superinstance_inference_engine \
        -Mdir build/verilator/obj_dir \
        +define+SIMULATION \
        rtl/*.sv \
        verification/verilator_main.cpp \
        -o superinstance_sim
    
    # Run
    echo -e "${YELLOW}Running simulation...${NC}"
    ./build/verilator/obj_dir/superinstance_sim
    
    echo -e "\n${GREEN}Simulation complete!${NC}"
    echo -e "Waveforms: ${BLUE}waves/superinstance.vcd${NC}"
}

# Run Icarus Verilog simulation
run_icarus() {
    echo -e "\n${GREEN}Running Icarus Verilog simulation...${NC}\n"
    
    mkdir -p build/icarus waves
    
    # Compile
    echo -e "${YELLOW}Compiling with Icarus Verilog...${NC}"
    iverilog -g2012 \
        -o build/icarus/tb_superinstance.vvp \
        -D SIMULATION \
        rtl/*.sv \
        verification/tb_superinstance.sv
    
    # Run
    echo -e "${YELLOW}Running simulation...${NC}"
    vvp build/icarus/tb_superinstance.vvp -lxt2
    
    echo -e "\n${GREEN}Simulation complete!${NC}"
    echo -e "Waveforms: ${BLUE}waves/tb_superinstance.vcd${NC}"
}

# Run tests
run_tests() {
    echo -e "\n${GREEN}Running tests...${NC}\n"
    
    # Check for cocotb
    if ! python3 -c "import cocotb" 2>/dev/null; then
        echo -e "${YELLOW}Installing cocotb...${NC}"
        pip install cocotb cocotb-test
    fi
    
    # Run pytest
    pytest verification/ -v --tb=short
}

# Run synthesis
run_synth() {
    local target=${1:-kv260}
    
    echo -e "\n${GREEN}Running synthesis for ${target}...${NC}\n"
    
    case $target in
        kv260)
            if ! command -v vivado &> /dev/null; then
                echo -e "${RED}ERROR: Vivado not found. Install from Xilinx website.${NC}"
                exit 1
            fi
            vivado -mode batch -source synthesis/xilinx/run_synth.tcl
            ;;
        de10nano)
            if ! command -v quartus_sh &> /dev/null; then
                echo -e "${RED}ERROR: Quartus not found. Install from Intel website.${NC}"
                exit 1
            fi
            echo -e "${YELLOW}Quartus synthesis coming soon...${NC}"
            ;;
        *)
            echo -e "${RED}Unknown target: $target${NC}"
            echo -e "Supported targets: kv260, de10nano"
            exit 1
            ;;
    esac
}

# Open waveform viewer
open_wave() {
    if [ -f waves/superinstance.vcd ]; then
        gtkwave waves/superinstance.vcd &
    elif [ -f waves/tb_superinstance.vcd ]; then
        gtkwave waves/tb_superinstance.vcd &
    else
        echo -e "${YELLOW}No wave files found. Run simulation first.${NC}"
    fi
}

# Clean build artifacts
clean() {
    echo -e "\n${YELLOW}Cleaning build artifacts...${NC}\n"
    rm -rf build waves *.log *.vcd
    echo -e "${GREEN}Clean complete!${NC}"
}

# Show status
show_status() {
    header
    check_tools
    
    echo -e "${YELLOW}Project Structure:${NC}\n"
    echo "  rtl/               - RTL source files"
    echo "  verification/      - Test benches"
    echo "  synthesis/         - Synthesis scripts"
    echo "  scripts/           - Utility scripts"
    echo "  build/             - Build output"
    echo "  waves/             - Waveform files"
    
    echo -e "\n${YELLOW}RTL Files:${NC}\n"
    ls -la rtl/*.sv 2>/dev/null || echo "  No RTL files found"
    
    echo -e "\n${YELLOW}Build Status:${NC}\n"
    if [ -d "build" ]; then
        ls -la build/ 2>/dev/null
    else
        echo "  No build directory (run 'sim' or 'synth')"
    fi
}

# Help
show_help() {
    header
    echo -e "\n${YELLOW}Usage:${NC} ./run.sh [command] [options]\n"
    echo "Commands:"
    echo "  sim verilator    Run Verilator simulation (fast)"
    echo "  sim icarus       Run Icarus Verilog simulation"
    echo "  synth kv260      Synthesize for Xilinx KV260"
    echo "  synth de10nano   Synthesize for DE10-Nano"
    echo "  test             Run Python tests"
    echo "  wave             Open GTKWave"
    echo "  clean            Remove build artifacts"
    echo "  status           Show project status"
    echo "  help             Show this help"
    echo ""
    echo "Examples:"
    echo "  ./run.sh sim                  # Quick Verilator simulation"
    echo "  ./run.sh sim icarus           # Full waveform simulation"
    echo "  ./run.sh synth kv260          # Build for KV260"
    echo ""
}

# Main
case "${1:-help}" in
    sim)
        header
        check_tools || exit 1
        case "${2:-verilator}" in
            verilator) run_verilator ;;
            icarus) run_icarus ;;
            *) echo -e "${RED}Unknown simulator: $2${NC}"; exit 1 ;;
        esac
        ;;
    synth)
        header
        run_synth ${2:-kv260}
        ;;
    test)
        header
        run_tests
        ;;
    wave)
        open_wave
        ;;
    clean)
        clean
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
