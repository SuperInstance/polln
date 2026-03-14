# SuperInstance.AI Mask-Locked Inference Chip
# Timing Constraints for Xilinx KV260
#
# Target: 200MHz operation (5ns period)
#
# Author: VP Manufacturing, SuperInstance.AI

# -----------------------------------------------------------------------------
# Clock Definitions
# -----------------------------------------------------------------------------

# Primary clock (200MHz target)
create_clock -period 5.000 -name sys_clk [get_ports clk]

# Memory interface clock (166MHz for LPDDR4)
create_clock -period 6.000 -name mem_clk [get_ports mem_clk]

# Generated clocks for internal use
create_generated_clock -name clk_div2 -master_clock sys_clk \
    -divide_by 2 [get_pins -hierarchical *clk_div_reg*/Q]

# -----------------------------------------------------------------------------
# Clock Groups
# -----------------------------------------------------------------------------

# System and memory clocks are asynchronous
set_clock_groups -asynchronous -group [get_clocks sys_clk] -group [get_clocks mem_clk]

# -----------------------------------------------------------------------------
# Input/Output Delays
# -----------------------------------------------------------------------------

# Activation input bus (sync to sys_clk)
set_input_delay -clock sys_clk -max 1.0 [get_ports activation*]
set_input_delay -clock sys_clk -min 0.1 [get_ports activation*]

# Weight interface (combinatorial from ROM)
set_input_delay -clock sys_clk -max 0.5 [get_ports weight*]
set_input_delay -clock sys_clk -min 0.0 [get_ports weight*]

# Output delays
set_output_delay -clock sys_clk -max 1.5 [get_ports result*]
set_output_delay -clock sys_clk -min 0.1 [get_ports result*]

# -----------------------------------------------------------------------------
# False Paths
# -----------------------------------------------------------------------------

# Reset path (async)
set_false_path -from [get_ports rst_n]

# Configuration inputs (not timing critical)
set_false_path -from [get_ports config_*]

# -----------------------------------------------------------------------------
# Multicycle Paths
# -----------------------------------------------------------------------------

# Accumulator update (can take 2 cycles)
set_multicycle_path -setup 2 -from [get_cells -hierarchical *accumulator_reg*] \
    -to [get_cells -hierarchical *accumulator_reg*]

# -----------------------------------------------------------------------------
# Max Delay Constraints
# -----------------------------------------------------------------------------

# RAU rotation logic must complete in 1 cycle
set_max_delay -from [get_cells -hierarchical *rotation_logic*] \
    -to [get_cells -hierarchical *accumulator*] 4.0

# -----------------------------------------------------------------------------
# Timing Exceptions for Mask-Locked Weights
# -----------------------------------------------------------------------------

# Weight ROM access is combinational (via pattern = immediate value)
# No timing path for weight access
set_false_path -from [get_cells -hierarchical *weight_rom*] \
    -through [get_nets -hierarchical *weight*]

# -----------------------------------------------------------------------------
# Power Optimization
# -----------------------------------------------------------------------------

# Enable clock gating for inactive RAUs
set_power_optimization_enable true

# Activity file for power analysis
set_switching_activity -toggle_rate 0.1 [get_cells -hierarchical *rau_*]
