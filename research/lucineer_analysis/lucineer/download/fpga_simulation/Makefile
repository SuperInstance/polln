# SuperInstance.AI Mask-Locked Inference Chip
# FPGA Simulation and Synthesis Makefile
#
# Supported simulators:
#   - Verilator (fastest for development, open source)
#   - Icarus Verilog (good waveform viewing, open source)
#   - Vivado (Xilinx synthesis and simulation)
#   - Quartus (Intel synthesis)
#
# Usage:
#   make sim                    # Run Verilator simulation (default)
#   make sim SIM=icarus         # Run Icarus Verilog simulation
#   make synth TARGET=kv260     # Synthesize for Xilinx KV260
#   make synth TARGET=de10nano  # Synthesize for Intel DE10-Nano
#   make clean                  # Clean build artifacts
#
# Author: VP Manufacturing, SuperInstance.AI

#------------------------------------------------------------------------------
# Configuration
#------------------------------------------------------------------------------

SIM ?= verilator
TARGET ?= kv260

# Paths
RTL_DIR = rtl
VERIF_DIR = verification
SYNTH_DIR = synthesis
BUILD_DIR = build
WAVE_DIR = waves

# Source files
RTL_SOURCES = $(wildcard $(RTL_DIR)/*.sv) $(wildcard $(RTL_DIR)/*.v)
TB_SOURCES = $(wildcard $(VERIF_DIR)/*.sv) $(wildcard $(VERIF_DIR)/*.v)

# Top module
TOP_MODULE = superinstance_inference_engine
TB_MODULE = tb_superinstance

# Clock period (ns)
CLK_PERIOD = 10

# Simulation time (ns)
SIM_TIME = 100000

#------------------------------------------------------------------------------
# Verilator
#------------------------------------------------------------------------------

VERILATOR_ROOT ?= $(shell which verilator 2>/dev/null | xargs dirname 2>/dev/null)
VERILATOR = verilator

VERILATOR_FLAGS = \
	-Wall \
	--cc \
	--exe \
	--build \
	--timing \
	--trace \
	--top-module $(TOP_MODULE) \
	+define+SIMULATION \
	+define+DEBUG \
	-Wno-fatal \
	--error-limit 100

VERILATOR_BUILD = $(BUILD_DIR)/verilator
VERILATOR_OBJ = $(VERILATOR_BUILD)/obj_dir/V$(TOP_MODULE)

verilator-check:
	@if [ -z "$(VERILATOR_ROOT)" ]; then \
		echo "ERROR: Verilator not found. Install with:"; \
		echo "  Ubuntu: sudo apt install verilator"; \
		echo "  macOS:  brew install verilator"; \
		exit 1; \
	fi

verilator-build: verilator-check
	@mkdir -p $(VERILATOR_BUILD)
	$(VERILATOR) $(VERILATOR_FLAGS) \
		-Mdir $(VERILATOR_BUILD)/obj_dir \
		-o $(VERILATOR_OBJ) \
		$(RTL_SOURCES) \
		$(VERIF_DIR)/verilator_main.cpp

verilator-run: verilator-build
	@mkdir -p $(WAVE_DIR)
	$(VERILATOR_OBJ) +verilator+rand+reset+1 \
		-l $(WAVE_DIR)/simulation.log \
		+MAX_SIM_TIME=$(SIM_TIME)

#------------------------------------------------------------------------------
# Icarus Verilog
#------------------------------------------------------------------------------

ICARUS_BUILD = $(BUILD_DIR)/icarus
ICARUS_VVP = $(ICARUS_BUILD)/$(TB_MODULE).vvp
ICARUS_VCD = $(WAVE_DIR)/$(TB_MODULE).vcd

icarus-check:
	@if ! command -v iverilog >/dev/null 2>&1; then \
		echo "ERROR: Icarus Verilog not found. Install with:"; \
		echo "  Ubuntu: sudo apt install iverilog"; \
		echo "  macOS:  brew install icarus-verilog"; \
		exit 1; \
	fi

icarus-build: icarus-check
	@mkdir -p $(ICARUS_BUILD) $(WAVE_DIR)
	iverilog -g2012 \
		-o $(ICARUS_VVP) \
		-D SIMULATION \
		-D DEBUG \
		-I $(RTL_DIR) \
		$(RTL_SOURCES) \
		$(TB_SOURCES)

icarus-run: icarus-build
	vvp $(ICARUS_VVP) -l $(WAVE_DIR)/icarus.log
	@echo "Wave file: $(ICARUS_VCD)"
	@echo "View with: gtkwave $(ICARUS_VCD)"

#------------------------------------------------------------------------------
# Cocotb Tests
#------------------------------------------------------------------------------

COCOTB_BUILD = $(BUILD_DIR)/cocotb

cocotb-check:
	@if ! python3 -c "import cocotb" 2>/dev/null; then \
		echo "ERROR: Cocotb not found. Install with:"; \
		echo "  pip install cocotb cocotb-test"; \
		exit 1; \
	fi

cocotb-test: cocotb-check icarus-build
	@mkdir -p $(COCOTB_BUILD)
	cd $(COCOTB_BUILD) && \
	MODULE=test_rau \
	TOPLEVEL=$(TOP_MODULE) \
	TOPLEVEL_LANG=verilog \
	VERILOG_SOURCES="$(realpath $(RTL_SOURCES))" \
	GPI_EXTRA=pycleantools \
	python3 $(realpath $(VERIF_DIR)/test_rau.py)

#------------------------------------------------------------------------------
# Vivado (Xilinx)
#------------------------------------------------------------------------------

VIVADO = vivado
VIVADO_BUILD = $(BUILD_DIR)/vivado
VIVADO_PROJECT = $(VIVADO_BUILD)/superinstance.xpr

# Xilinx board part numbers
XILINX_BOARDS = \
	kv260=xilinx.com:kv260:part0:1.0 \
	zedboard=xilinx.com:zed:part0:1.0 \
	zybo=digilentinc.com:zybo:part0:1.0 \
	pynq=digilentinc.com:pynq-z1:part0:1.1

vivado-check:
	@if ! command -v $(VIVADO) >/dev/null 2>&1; then \
		echo "ERROR: Vivado not found. Install from Xilinx website."; \
		exit 1; \
	fi

vivado-project: vivado-check
	@mkdir -p $(VIVADO_BUILD)
	$(VIVADO) -mode batch -source scripts/create_vivado_project.tcl \
		-tclargs $(VIVADO_BUILD) $(RTL_DIR) $(TOP_MODULE)

vivado-synth: vivado-project
	$(VIVADO) -mode batch -source scripts/run_synth.tcl \
		-tclargs $(VIVADO_BUILD) $(TOP_MODULE) $(TARGET)

vivado-impl: vivado-synth
	$(VIVADO) -mode batch -source scripts/run_impl.tcl \
		-tclargs $(VIVADO_BUILD) $(TOP_MODULE)

vivado-bitstream: vivado-impl
	$(VIVADO) -mode batch -source scripts/generate_bitstream.tcl \
		-tclargs $(VIVADO_BUILD) $(TOP_MODULE)
	@echo "Bitstream: $(VIVADO_BUILD)/$(TOP_MODULE).bit"

#------------------------------------------------------------------------------
# Quartus (Intel/Altera)
#------------------------------------------------------------------------------

QUARTUS = quartus_sh
QUARTUS_BUILD = $(BUILD_DIR)/quartus

# Intel board part numbers
INTEL_BOARDS = \
	de10nano=DE10-Nano \
	cyclone10gx=C10GX \
	arria10=Arria10

quartus-check:
	@if ! command -v $(QUARTUS) >/dev/null 2>&1; then \
		echo "ERROR: Quartus not found. Install from Intel website."; \
		exit 1; \
	fi

quartus-project: quartus-check
	@mkdir -p $(QUARTUS_BUILD)
	$(QUARTUS) --flow compile superinstance \
		--source $(RTL_DIR) \
		--top $(TOP_MODULE)

quartus-synth: quartus-project
	cd $(QUARTUS_BUILD) && quartus_map superinstance

quartus-fit: quartus-synth
	cd $(QUARTUS_BUILD) && quartus_fit superinstance

quartus-asm: quartus-fit
	cd $(QUARTUS_BUILD) && quartus_asm superinstance

quartus-bitstream: quartus-asm
	@echo "Bitstream: $(QUARTUS_BUILD)/output_files/superinstance.sof"

#------------------------------------------------------------------------------
# Synthesis Targets
#------------------------------------------------------------------------------

ifeq ($(TARGET),kv260)
synth: vivado-bitstream
else ifeq ($(TARGET),de10nano)
synth: quartus-bitstream
else
synth:
	@echo "Unknown target: $(TARGET)"
	@echo "Supported: kv260, zedboard, zybo, pynq, de10nano"
	@exit 1
endif

#------------------------------------------------------------------------------
# Simulation Targets
#------------------------------------------------------------------------------

ifeq ($(SIM),verilator)
sim: verilator-run
else ifeq ($(SIM),icarus)
sim: icarus-run
else ifeq ($(SIM),cocotb)
sim: cocotb-test
else ifeq ($(SIM),vivado)
sim: vivado-project
	$(VIVADO) -mode gui $(VIVADO_PROJECT)
else
sim:
	@echo "Unknown simulator: $(SIM)"
	@echo "Supported: verilator, icarus, cocotb, vivado"
	@exit 1
endif

#------------------------------------------------------------------------------
# Utilities
#------------------------------------------------------------------------------

wave:
	gtkwave $(WAVE_DIR)/*.vcd &

lint:
	$(VERILATOR) --lint-only -Wall $(RTL_SOURCES)

format:
	verilog-format --inplace $(RTL_SOURCES) $(TB_SOURCES)

clean:
	rm -rf $(BUILD_DIR) $(WAVE_DIR)
	rm -f *.log *.vcd *.wdb

help:
	@echo "SuperInstance.AI FPGA Simulation Makefile"
	@echo ""
	@echo "Simulation:"
	@echo "  make sim                    # Run Verilator (default)"
	@echo "  make sim SIM=icarus         # Run Icarus Verilog"
	@echo "  make sim SIM=cocotb         # Run cocotb tests"
	@echo "  make sim SIM=vivado         # Open Vivado GUI"
	@echo ""
	@echo "Synthesis:"
	@echo "  make synth TARGET=kv260     # Synthesize for Xilinx KV260"
	@echo "  make synth TARGET=de10nano  # Synthesize for DE10-Nano"
	@echo ""
	@echo "Utilities:"
	@echo "  make lint                   # Run linting"
	@echo "  make wave                   # Open GTKWave"
	@echo "  make clean                  # Clean build artifacts"

.PHONY: all sim synth clean help lint format wave \
        verilator-build verilator-run \
        icarus-build icarus-run \
        cocotb-test \
        vivado-project vivado-synth vivado-impl vivado-bitstream \
        quartus-project quartus-synth quartus-fit quartus-asm quartus-bitstream

all: sim
